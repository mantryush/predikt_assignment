from config import COUNTRIES, END_DATE, CHUNK_SIZE
from ingestion import fetch_data
from transform import convert_unix_timestamp, aggregate_monthly
from storage import save_data
import polars as pl
from datetime import datetime, timedelta

def find_earliest_available_date(bzn):
    """Find the earliest available data by checking from today and moving back one year if no data is found."""
    step = timedelta(days=365)
    test_date = datetime.utcnow()
    last_valid_date = None  # Store last valid data year

    while test_date.year > 2000:  # Ensure we check all the way back
        start_test = test_date.strftime("%Y-%m-%dT00:00Z")
        end_test = (test_date + step).strftime("%Y-%m-%dT00:00Z")
        url = f"https://api.energy-charts.info/price?bzn={bzn}&start={start_test}&end={end_test}"
        data = fetch_data(url)

        if data and data.get("price"):
            last_valid_date = start_test  # Store latest valid year
            print(f"Data available from {start_test} for {bzn}. Continuing search for earlier data...")
        else:
            break  # Stop searching once no more data is found

        test_date -= step  # Move back one year
    
    if last_valid_date:
        print(f"Earliest confirmed data for {bzn}: {last_valid_date}")
        return last_valid_date
    
    print(f"No data found before {test_date.strftime('%Y-%m-%d')} for {bzn}.")
    return "2008-01-01T00:00Z"  # Default safe assumption

def fetch_spot_price(bzn, country_name):
    print(f"[INFO] Starting data fetch for {country_name} ({bzn})")
    start_date = find_earliest_available_date(bzn)
    all_data = []
    
    start = datetime.strptime(start_date, "%Y-%m-%dT%H:%MZ")
    end = datetime.strptime(END_DATE, "%Y-%m-%dT%H:%MZ")
    
    while start < end:
        next_end = min(start + timedelta(days=CHUNK_SIZE), end)
        url = f"https://api.energy-charts.info/price?bzn={bzn}&start={start.strftime('%Y-%m-%dT%H:%MZ')}&end={next_end.strftime('%Y-%m-%dT%H:%MZ')}"
        print(f"[INFO] Fetching data from {start.strftime('%Y-%m-%d')} to {next_end.strftime('%Y-%m-%d')} for {country_name}")
        data = fetch_data(url)

        if data and data.get("price"):
            print(f"[SUCCESS] Data retrieved for {country_name} ({start.strftime('%Y-%m-%d')} - {next_end.strftime('%Y-%m-%d')})")
            chunk_df = pl.DataFrame({"Timestamp": data["unix_seconds"], "Price (EUR/MWh)": data["price"]})
            all_data.append(chunk_df)
        else:
            print(f"[WARNING] No data available for {country_name} in this range ({start.strftime('%Y-%m-%d')} - {next_end.strftime('%Y-%m-%d')})")

        start = next_end
    
    if all_data:
        print(f"[INFO] Processing data for {country_name} ({bzn})")
        df = pl.concat(all_data)
        df = convert_unix_timestamp(df)
        monthly_avg = aggregate_monthly(df).drop_nulls()

        print(f"[INFO] Saving data for {country_name} ({bzn})")
        save_data(df, f"data/spot_prices_{country_name}")
        save_data(monthly_avg, f"data/monthly_avg_spot_prices_{country_name}")
        print(f"[SUCCESS] Data saved successfully for {country_name} ({bzn})")
    else:
        print(f"[ERROR] No data was fetched for {country_name} ({bzn}). Skipping save operation.")

if __name__ == "__main__":
    for bzn, country_name in COUNTRIES.items():
        fetch_spot_price(bzn, country_name)
