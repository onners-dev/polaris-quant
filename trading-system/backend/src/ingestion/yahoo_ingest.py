import time
import os
from typing import List, Optional
import yfinance as yf
import pandas as pd

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
                show_errors=False,
            )
            if not df.empty:
                return df
            else:
                return None
        except Exception:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_BACKOFF * (2**attempt))
            else:
                return None

def save_raw_data(df: pd.DataFrame, file_path: str) -> None:
    df.to_parquet(file_path)

def ingest_yahoo(
    tickers: List[str],
    start: str,
    end: str,
    interval: str = "1d",
) -> None:
    df = fetch_yahoo_data(tickers, start, end, interval)
    if df is not None:
        raw_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../data/raw")
        )
        os.makedirs(raw_dir, exist_ok=True)
        tickers_string = "_".join(sorted(tickers))
        filename = f"{tickers_string}_{start}_{end}_{interval}.parquet"
        output_path = os.path.join(raw_dir, filename)
        save_raw_data(df, output_path)

