import cloudscraper
from bs4 import BeautifulSoup
import polars as pl
import os
import time

# Constants
BASE_URL = "https://www.marketwatch.com/tools/markets/futures"
OUTPUT_DIR = "marketwatch_futures"
os.makedirs(OUTPUT_DIR, exist_ok=True)  # Ensure the output directory exists

# Headers to mimic a real browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Referer": "https://www.google.com/",
    "Connection": "keep-alive",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "max-age=0",
}


def fetch_page(url, retries=3):
    """Fetch a page and return a BeautifulSoup object."""
    scraper = cloudscraper.create_scraper()

    for attempt in range(retries):
        response = scraper.get(url, headers=HEADERS)
        if response.status_code == 200:
            return BeautifulSoup(response.content, "html.parser")
        else:
            print(f"[INFO] Attempt {attempt + 1}: Failed to fetch {url} - Status {response.status_code}")
            time.sleep(2)  # Wait before retrying

    print(f"[ERROR] Skipping {url} after {retries} failed attempts.")
    return None


def extract_futures_data(soup, page_num):
    """Extract futures listings from a page."""
    table = soup.find("table", {"class": "table table-condensed"})
    if not table:
        print("[ERROR] Table not found! The page structure may have changed.")
        return []

    rows = []
    for row in table.find("tbody").find_all("tr"):
        try:
            cells = row.find_all("td")
            if cells:
                name = cells[0].text.strip()
                link = cells[0].find("a")["href"] if cells[0].find("a") else ""
                exchange = cells[1].text.strip()
                country = cells[2].text.strip()
                sector = cells[3].text.strip() if len(cells) > 3 else ""

                # Ensure link is absolute URL
                full_link = f"https://www.marketwatch.com{link}" if link and link.startswith("/") else link

                rows.append((page_num, name, full_link, exchange, country, sector))
        except Exception as e:
            print(f"[ERROR] Failed to extract row: {e}")

    return rows


def fetch_futures_list():
    """Fetch all futures listings from MarketWatch."""
    all_futures_data = []
    total_pages = 35  # Known number of pages

    for page_num in range(1, total_pages + 1):
        page_url = f"{BASE_URL}/{page_num}" if page_num > 1 else BASE_URL
        print(f"[INFO] Scraping page {page_num}/{total_pages}: {page_url}")
        soup = fetch_page(page_url)

        if soup:
            futures_data = extract_futures_data(soup, page_num)
            all_futures_data.extend(futures_data)

        time.sleep(1)  # Avoid rate limits

    # Convert to Polars DataFrame and remove duplicates
    df = pl.DataFrame(
        all_futures_data,
        schema=["Page", "Name", "Link", "Exchange", "Country", "Sector"]
    )
    df = df.unique()  # Remove duplicates

    # Sort by Page (original order) and Name
    df = df.sort(["Page", "Name"])

    # Save the cleaned data
    df.write_csv(os.path.join(OUTPUT_DIR, "futures_list.csv"))
    df.write_parquet(os.path.join(OUTPUT_DIR, "futures_list.parquet"))

    print(f"[SUCCESS] Successfully saved {len(df)} unique futures listings.")
    return df


