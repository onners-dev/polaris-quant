from src.utils.duckdb_helpers import read_table, write_table
from validate_data import run_full_validation, basic_cleaning

REQUIRED_COLUMNS = ["Open", "High", "Low", "Close", "Volume"]
OUTLIER_COLUMNS = ["Open", "High", "Low", "Close", "Volume"]

df = read_table("raw")  # this now includes all tickers!

try:
    results = run_full_validation(df, REQUIRED_COLUMNS, OUTLIER_COLUMNS)
    print(f"Validation results for DuckDB raw: {results}")
    cleaned = basic_cleaning(df)
    write_table(cleaned, "cleaned")  # this saves all tickers at once
    print("Cleaned data written to DuckDB 'cleaned' table")
except Exception as e:
    print(f"Validation failed: {e}")
