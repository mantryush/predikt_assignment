import os

def save_data(df, filename):
    """Saves data to CSV, JSON, and Parquet formats."""
    df.write_csv(filename + ".csv")
    df.write_json(filename + ".json")
    df.write_parquet(filename + ".parquet")
