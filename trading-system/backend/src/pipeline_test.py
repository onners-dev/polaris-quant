import os
import pandas as pd

from src.ingestion.yahoo_ingest import ingest_yahoo
from src.validation.validate_data import run_full_validation, basic_cleaning
from src.features.feature_engineering import compute_all_ticker_features

TICKERS = ["AAPL", "MSFT"]
START = "2023-01-01"
END = "2023-03-31"
RAW_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/raw"))
CLEANED_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/cleaned"))
FEATURES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/features"))

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(CLEANED_DIR, exist_ok=True)
os.makedirs(FEATURES_DIR, exist_ok=True)

raw_fname = f"{'_'.join(sorted(TICKERS))}_{START}_{END}_1d.parquet"
raw_path = os.path.join(RAW_DIR, raw_fname)
cleaned_path = os.path.join(CLEANED_DIR, raw_fname)
features_path = os.path.join(FEATURES_DIR, raw_fname)

print("Step 1: Ingest Yahoo data")
ingest_yahoo(TICKERS, START, END, raw_dir=RAW_DIR)

if not os.path.exists(raw_path):
    print(f"[FAIL] Ingestion did not produce expected {raw_path}")
    exit(1)
print(f"[OK] Data ingested to {raw_path}")

print("Step 2: Validate & Clean")
df = pd.read_parquet(raw_path)
if isinstance(df.columns, pd.MultiIndex):
    df.columns = ['_'.join([str(c) for c in col if str(c) != '']) for col in df.columns.values]

results = run_full_validation(df, [], [])
print("[OK] Validation results:", results)
cleaned_df = basic_cleaning(df)

# Flatten again in case Parquet roundtrip restored MultiIndex
if isinstance(cleaned_df.columns, pd.MultiIndex):
    cleaned_df.columns = ['_'.join([str(c) for c in col if str(c) != '']) for col in cleaned_df.columns.values]

cleaned_df.to_parquet(cleaned_path)
print(f"[OK] Cleaned data saved to {cleaned_path}")

print("Step 3: Feature Engineering")
features_df = compute_all_ticker_features(cleaned_df)
features_df.to_parquet(features_path)
print(f"[OK] Features data saved to {features_path}")

print("\nPipeline run completed successfully!")
