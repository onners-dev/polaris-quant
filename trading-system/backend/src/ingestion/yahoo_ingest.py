import time
from typing import List, Optional, Dict, Any
import yfinance as yf
import pandas as pd
from src.utils.duckdb_helpers import write_table, read_table
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

def get_existing_dates_for_ticker(ticker: str) -> set:
    try:
        raw_df = read_table("raw")
        if "Date" not in raw_df.columns or f"{ticker}_Close" not in raw_df.columns:
            return set()
        # Use only dates where at least price data exists for ticker
        return set(raw_df.loc[~raw_df[f"{ticker}_Close"].isna(), "Date"])
    except Exception:
        return set()

def smart_append_raw(new_df):
    try:
        old = read_table("raw")
    except Exception:
        old = None
    if old is not None and not old.empty:
        combined = pd.concat([old, new_df], ignore_index=True)
        # "Date" + all ticker columns (since these are wide-form)
        subset_cols = ["Date"] + [col for col in new_df.columns if col != "Date"]
        combined = combined.drop_duplicates(subset=subset_cols, keep="last")
    else:
        combined = new_df
    write_table(combined, "raw")

def ingest_yahoo(
    tickers: List[str],
    start: str,
    end: str,
    interval: str = "1d",
    raw_dir=None,
) -> Dict[str, Any]:
    to_download = []
    # Check existing data for each ticker, only download missing dates
    for ticker in tickers:
        have_dates = get_existing_dates_for_ticker(ticker)
        # If no dates, or new date range, add to download
        if not have_dates:
            to_download.append(ticker)
        else:
            # If at least one date is missing in requested range, add to download
            req_dates = pd.date_range(start, end).strftime("%Y-%m-%d")
            if not set(req_dates).issubset(have_dates):
                to_download.append(ticker)
    if not to_download:
        return {"success": True, "tickers": [], "row_count": 0, "msg": "All tickers/dates already present"}
    df = fetch_yahoo_data(to_download, start, end, interval)
    if df is not None and not df.empty:
        df = df.reset_index()
        df = flatten_columns(df)
        smart_append_raw(df)
        min_date = str(df["Date"].min()) if "Date" in df.columns else None
        max_date = str(df["Date"].max()) if "Date" in df.columns else None
        summary = {
            "success": True,
            "tickers": to_download,
            "row_count": int(len(df)),
            "start_date": min_date,
            "end_date": max_date,
        }
        print(f"[INFO] Data written to DuckDB 'raw' table (smart append): {summary}")
        return summary
    else:
        error_msg = "No new data downloaded, all requested data already present or download failed."
        print(f"[INFO] {error_msg}")
        return {"success": False, "error": error_msg}


if __name__ == "__main__":
    TICKERS = ["AAPL", "MSFT"]
    START = "2023-01-01"
    END = "2023-06-01"
    result = ingest_yahoo(TICKERS, START, END)
    print(result)
