import time
from typing import List, Optional, Dict, Any
import yfinance as yf
import pandas as pd
from src.utils.duckdb_helpers import write_table
from src.utils.pandas_helpers import flatten_columns

MAX_RETRIES = 3
RETRY_BACKOFF = 5

def fetch_yahoo_data(
    tickers: List[str],
    start: str,
    end: str,
    interval: str = "1d",
) -> Optional[pd.DataFrame]:
    for attempt in range(MAX_RETRIES):
        try:
            df = yf.download(
                tickers=" ".join(tickers),
                start=start,
                end=end,
                interval=interval,
                group_by="ticker",
                auto_adjust=False,
                threads=True,
                progress=False,
            )
            if not df.empty:
                return df
            else:
                return None
        except Exception as e:
            print(f"[DEBUG] Exception during yfinance fetch: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BACKOFF * (2**attempt))
            else:
                return None

def ingest_yahoo(
    tickers: List[str],
    start: str,
    end: str,
    interval: str = "1d",
    raw_dir=None,
) -> Dict[str, Any]:
    df = fetch_yahoo_data(tickers, start, end, interval)
    if df is not None and not df.empty:
        df = df.reset_index()
        df = flatten_columns(df)
        write_table(df, "raw")
        min_date = str(df["Date"].min()) if "Date" in df.columns else None
        max_date = str(df["Date"].max()) if "Date" in df.columns else None
        summary = {
            "success": True,
            "tickers": tickers,
            "row_count": int(len(df)),
            "start_date": min_date,
            "end_date": max_date,
        }
        print(f"[INFO] Data written to DuckDB 'raw' table: {summary}")
        return summary
    else:
        error_msg = "No data available from Yahoo Finance for the given parameters."
        print(f"[INFO] {error_msg}")
        return {"success": False, "error": error_msg}


if __name__ == "__main__":
    # Example for CLI/manual test use only
    TICKERS = ["AAPL", "MSFT"]
    START = "2023-01-01"
    END = "2023-06-01"
    result = ingest_yahoo(TICKERS, START, END)
    print(result)
