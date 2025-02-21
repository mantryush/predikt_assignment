from src.fetch_futures_list import fetch_futures_list
from src.fetch_future_details import fetch_futures_details
import polars as pl
import os

# Set the number of futures to scrape (Change to 3, 5, or any number)
NUM_FUTURES_TO_FETCH = 5  

if __name__ == "__main__":
    print("[INFO] Fetching Futures Listings...")
    fetch_futures_list()

    print(f"[INFO] Fetching Details for the First {NUM_FUTURES_TO_FETCH} Futures...")
    futures_df = pl.read_csv("marketwatch_futures/futures_list.csv").to_dicts()

    # Fetch only the first `NUM_FUTURES_TO_FETCH` futures
    fetch_futures_details(futures_df[:NUM_FUTURES_TO_FETCH])
