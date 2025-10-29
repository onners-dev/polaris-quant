from fastapi import APIRouter
from src.utils.duckdb_helpers import read_table
from typing import Any

router = APIRouter()

@router.get("/data/available")
def get_available_data() -> Any:
    try:
        df = read_table("raw")
        if df is None or df.empty:
            return []

        # Infer tickers from columns
        cols = [c for c in df.columns if "_" in c and c.endswith("Close")]
        tickers = [c.split("_")[0] for c in cols]
        unique_tickers = sorted(set(tickers))

        # Identify the correct date column (commonly "Date" or similar)
        # Let's auto-detect and fall back to index
        date_col = None
        for possible in ["date", "Date", "DATE"]:
            if possible in df.columns:
                date_col = possible
                break

        results = []
        for ticker in unique_tickers:
            col = f"{ticker}_Close"
            if col not in df.columns:
                continue
            series = df[col].dropna()
            if series.empty:
                continue

            if date_col:
                # Use the date column for dates
                valid_dates = df.loc[series.index, date_col]
                start_date = valid_dates.min()
                end_date = valid_dates.max()
            else:
                # Fallback: try to use index if it's a DatetimeIndex
                if hasattr(df.index, "min") and hasattr(df.index, "max"):
                    start_date = df.index[series.index.min()]
                    end_date = df.index[series.index.max()]
                else:
                    start_date = series.index.min()
                    end_date = series.index.max()

            results.append({
                "ticker": ticker,
                "start_date": str(start_date),
                "end_date": str(end_date),
                "row_count": int(len(series)),
            })
        return results
    except Exception as e:
        return {"error": str(e)}

