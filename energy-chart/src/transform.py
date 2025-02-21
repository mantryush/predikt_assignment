import polars as pl

def convert_unix_timestamp(df):
    """Converts UNIX timestamps to datetime format."""
    return df.with_columns(pl.from_epoch(pl.col("Timestamp"), time_unit="s").alias("Timestamp"))

def aggregate_monthly(df):
    """Groups data by month and calculates average."""
    df = df.with_columns(df["Timestamp"].dt.truncate("1mo").dt.strftime("%Y-%m").alias("Month"))
    return df.group_by("Month").agg(pl.col("Price (EUR/MWh)").mean())
