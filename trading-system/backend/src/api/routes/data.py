from fastapi import APIRouter
from src.utils.duckdb_helpers import read_table
from typing import Any

router = APIRouter()

@router.get("/data/available")
def get_available_data() -> Any:
    try:
        df = read_table("features_tidy")
        if df is None or df.empty:
            return []
        tickers = sorted(set(df["Ticker"]))
        results = []
        for ticker in tickers:
            dft = df[df["Ticker"] == ticker]
            start_date = dft["Date"].min()
            end_date = dft["Date"].max()
            row_count = len(dft)
            results.append({
                "ticker": ticker,
                "start_date": str(start_date),
                "end_date": str(end_date),
                "row_count": row_count,
            })
        return results
    except Exception as e:
        return []
