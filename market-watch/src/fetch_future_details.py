import cloudscraper
from bs4 import BeautifulSoup
import polars as pl
import os
import time
from datetime import datetime
import pytz
import re

# Setup CloudScraper
scraper = cloudscraper.create_scraper()

# Headers to mimic a real browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Referer": "https://www.google.com/",
    "Connection": "keep-alive",
}

# Directory to save data
OUTPUT_DIR = "marketwatch_futures_details"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Timezone mappings for MarketWatch
TIMEZONE_MAPPING = {
    "CEST": "Europe/Berlin",   # Central European Summer Time (GMT+2)
    "CET": "Europe/Berlin",    # Central European Time (GMT+1)
    "EST": "America/New_York", # Eastern Standard Time (GMT-5)
    "EDT": "America/New_York", # Eastern Daylight Time (GMT-4)
    "CST": "America/Chicago",  # Central Standard Time (GMT-6)
    "CDT": "America/Chicago",  # Central Daylight Time (GMT-5)
    "GMT": "GMT",              # GMT (no conversion needed)
}

def fetch_page(url):
    """Fetch the page content using Cloudscraper with headers."""
    response = scraper.get(url, headers=HEADERS)

    if response.status_code == 200:
        return BeautifulSoup(response.content, "html.parser")
    else:
        print(f"[ERROR] Failed to fetch {url} - Status Code: {response.status_code}")
        return None

def convert_to_utc(timestamp_str):
    """Convert a MarketWatch timestamp to UTC in ISO 8601 format with microseconds."""
    if not timestamp_str or "N/A" in timestamp_str:
        return "N/A"

    try:
        # Extract timezone from the string
        parts = timestamp_str.split()
        timezone_abbr = parts[-1]  # Last part of the string is the timezone
        tz_name = TIMEZONE_MAPPING.get(timezone_abbr, "UTC")

        # Normalize 'a.m.'/'p.m.' to 'AM'/'PM' (to match Python's strptime format)
        timestamp_normalized = re.sub(r'(\d{1,2}):(\d{2})\s([ap])\.m\.', r'\1:\2 \3M', " ".join(parts[:-1]))

        # Parse datetime string
        local_time = datetime.strptime(timestamp_normalized, "%b %d, %Y %I:%M %p")

        # Localize and convert to UTC
        local_tz = pytz.timezone(tz_name)
        local_dt = local_tz.localize(local_time)
        utc_dt = local_dt.astimezone(pytz.utc)

        # Format as ISO 8601 with microseconds
        return utc_dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    except Exception as e:
        print(f"[ERROR] Failed to parse timestamp: {timestamp_str} - {e}")
        return "N/A"
    
def extract_futures_data(soup):
    """Extract relevant futures data from the HTML soup."""
    data = {}

    # Extract Futures Name
    name_elem = soup.select_one("span.company__ticker")
    market_elem = soup.select_one("span.company__market")
    data["Futures Name"] = f"{name_elem.text.strip()} ({market_elem.text.strip()})" if name_elem and market_elem else "N/A"

    # Extract Price
    price_elem = soup.select_one("bg-quote[field='Last']")
    data["Price"] = price_elem.text.strip() if price_elem else "N/A"

    # Extract Change (€ and %)
    change_point_elem = soup.select_one("bg-quote[field='change']")
    change_percent_elem = soup.select_one("bg-quote[field='percentchange']")
    data["Change (€)"] = change_point_elem.text.strip() if change_point_elem else "N/A"
    data["Change (%)"] = change_percent_elem.text.strip() if change_percent_elem else "N/A"

    # Extract Open Price
    open_price_elem = soup.find("small", string="Open")
    open_price_value = open_price_elem.find_next("span", class_="primary") if open_price_elem else None
    data["Open Price"] = open_price_value.text.strip() if open_price_value else "N/A"

    # Extract Open Interest
    open_interest_elem = soup.find("small", string="Open Interest")
    open_interest_value = open_interest_elem.find_next("span", class_="primary") if open_interest_elem else None
    data["Open Interest"] = open_interest_value.text.strip() if open_interest_value else "N/A"

    # Extract Settlement Price
    settlement_elem = soup.find("th", string=lambda text: text and "Settlement Price" in text)
    settlement_value = settlement_elem.find_next("td") if settlement_elem else None
    data["Settlement Price"] = settlement_value.text.strip() if settlement_value else "N/A"

    # Extract Day Range
    day_range_elem = soup.find("small", string="Day Range")
    day_range_value = day_range_elem.find_next("span", class_="primary") if day_range_elem else None
    data["Day Range"] = day_range_value.text.strip() if day_range_value else "N/A"

    # Extract 52-Week Range
    week_52_elem = soup.find("small", string="52 Week Range")
    week_52_value = week_52_elem.find_next("span", class_="primary") if week_52_elem else None
    data["52-Week Range"] = week_52_value.text.strip() if week_52_value else "N/A"

    # Extract Volume & 65-Day Average Volume
    volume_elem = soup.select_one(".range--volume .primary")
    avg_volume_elem = soup.select_one(".range--volume .secondary")
    data["Volume"] = volume_elem.text.strip() if volume_elem else "N/A"
    data["65-Day Avg Volume"] = avg_volume_elem.text.strip() if avg_volume_elem else "N/A"

    # Extract Last Updated timestamp
    timestamp_elem = soup.select_one("span.timestamp__time")
    timestamp_raw = timestamp_elem.text.replace("Last Updated: ", "").strip() if timestamp_elem else "N/A"
    data["Last Updated"] = convert_to_utc(timestamp_raw)

    # Extract Performance Metrics (5-day, 1-month, 3-month, YTD, 1-year)
    performance_table = soup.find("div", class_="element element--table performance")
    if performance_table:
        rows = performance_table.find_all("tr", class_="table__row")
        performance_data = {
            "5 Day": "N/A",
            "1 Month": "N/A",
            "3 Month": "N/A",
            "YTD": "N/A",
            "1 Year": "N/A"
        }
        for row in rows:
            period_elem = row.find("td", class_="table__cell")  # e.g., "5 Day", "1 Month"
            value_elem = row.find("li", class_="content__item value ignore-color")

            if period_elem and value_elem:
                period = period_elem.text.strip()
                value = value_elem.text.strip()
                performance_data[period] = value  # Store in the dictionary
        
        # Ensure all performance fields exist in `data`
        for period, value in performance_data.items():
            data[f"Performance {period}"] = value

    return data


def save_data(data, filename):
    """Save the extracted data to CSV and Parquet using Polars."""
    df = pl.DataFrame([data])

    # Save as CSV
    df.write_csv(os.path.join(OUTPUT_DIR, f"{filename}.csv"))

    # Save as Parquet
    df.write_parquet(os.path.join(OUTPUT_DIR, f"{filename}.parquet"))

    print(f"[SUCCESS] Data saved: {filename}")


def fetch_futures_details(futures_list):
    """Fetch details for all futures."""
    all_data = []

    for future in futures_list:
        url = future["Link"]
        print(f"[INFO] Scraping: {url}")
        soup = fetch_page(url)
        if soup:
            data = extract_futures_data(soup)
            data["Futures Name"] = future["Name"]
            all_data.append(data)
        time.sleep(1)  # Avoid rate limits

    df = pl.DataFrame(all_data)
    df.write_csv(os.path.join(OUTPUT_DIR, "futures_details.csv"))
    df.write_parquet(os.path.join(OUTPUT_DIR, "futures_details.parquet"))

    print(f"[SUCCESS] Successfully saved {len(df)} futures details.")
    return df
