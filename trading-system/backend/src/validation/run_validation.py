import os
import pandas as pd
from validate_data import run_full_validation, basic_cleaning

RAW_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/raw"))
CLEANED_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/cleaned"))
os.makedirs(CLEANED_DIR, exist_ok=True)

REQUIRED_COLUMNS = ["Open", "High", "Low", "Close", "Volume"]
OUTLIER_COLUMNS = ["Open", "High", "Low", "Close", "Volume"]

for fname in os.listdir(RAW_DIR):
    if fname.endswith(".parquet"):
        input_path = os.path.join(RAW_DIR, fname)
        output_path = os.path.join(CLEANED_DIR, fname)
        print(f"Processing {fname}...")

        df = pd.read_parquet(input_path)
        try:
            results = run_full_validation(df, REQUIRED_COLUMNS, OUTLIER_COLUMNS)
            print(f"Validation results for {fname}: {results}")

            cleaned = basic_cleaning(df)
            cleaned.to_parquet(output_path)

            print(f"Saved cleaned data to {output_path}")
        except Exception as e:
            print(f"Validation failed for {fname}: {e}")
