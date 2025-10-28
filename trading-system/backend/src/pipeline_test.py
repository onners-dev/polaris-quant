from src.utils.duckdb_helpers import read_table, write_table
from src.ingestion.yahoo_ingest import ingest_yahoo
from src.validation.validate_data import run_full_validation, basic_cleaning
from src.features.feature_engineering import compute_all_ticker_features

TICKERS = ["AAPL", "MSFT"]
START = "2023-01-01"
END = "2023-06-1"

print("Step 1: Ingest Yahoo data")
ingest_yahoo(TICKERS, START, END)

df = read_table("raw")
if df is None or df.empty:
    print("[FAIL] DuckDB 'raw' table is empty after ingestion.")
    exit(1)
print("[OK] Data ingested to DuckDB table 'raw'.")

print("Step 2: Validate & Clean")
results = run_full_validation(df, [], [])
print("[OK] Validation results:", results)
cleaned_df = basic_cleaning(df)
write_table(cleaned_df, "cleaned")
print("[OK] Cleaned data saved to DuckDB table 'cleaned'.")

print("Step 3: Feature Engineering")
print("DEBUG columns before feature engineering:", list(cleaned_df.columns))

features_df = compute_all_ticker_features(cleaned_df)
write_table(features_df, "features")
print("[OK] Features data saved to DuckDB table 'features'.")

print("\nPipeline run completed successfully!")
