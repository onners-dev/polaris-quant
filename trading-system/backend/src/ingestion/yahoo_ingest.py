import time
from typing import List, Optional
import yfinance as yf
import pandas as pd
from src.utils.duckdb_helpers import write_table

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
            print(f"[DEBUG] yfinance returned {'empty' if df.empty else 'non-empty'} dataframe")
            print(f"[DEBUG] DataFrame shape: {df.shape}")
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
    raw_dir = None,  # Ignored for DuckDB-only
) -> None:
    df = fetch_yahoo_data(tickers, start, end, interval)
    if df is not None:
        write_table(df, "raw")
        print(f"[DEBUG] Data written to DuckDB 'raw' table")
    else:
        print("[DEBUG] fetch_yahoo_data returned None")
