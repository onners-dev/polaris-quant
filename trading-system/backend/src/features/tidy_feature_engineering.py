import pandas as pd
from src.utils.pandas_helpers import flatten_columns
from src.utils.duckdb_helpers import read_table, write_table

def wide_to_tidy_features(df: pd.DataFrame) -> pd.DataFrame:
    df = flatten_columns(df)
    tickers = sorted(set(col.split("_")[0] for col in df.columns if "_" in col))
    all_records = []
    for ticker in tickers:
        ticker_cols = [col for col in df.columns if col.startswith(f"{ticker}_")]
        if not ticker_cols:
            continue
        sub = df[["Date"] + ticker_cols].copy()
        sub.columns = ["Date"] + [col[len(ticker)+1:] for col in ticker_cols]
        sub["Ticker"] = ticker
        all_records.append(sub)
    tidy = pd.concat(all_records, axis=0, ignore_index=True)
    cols = ["Date", "Ticker"] + [c for c in tidy.columns if c not in ("Date", "Ticker")]
    tidy = tidy[cols]
    return tidy

if __name__ == "__main__":
    # Use the output of your wide feature pipeline
    df = read_table("features")
    tidy = wide_to_tidy_features(df)
    write_table(tidy, "features_tidy")
    print("Tidy features written to DuckDB 'features_tidy'")
