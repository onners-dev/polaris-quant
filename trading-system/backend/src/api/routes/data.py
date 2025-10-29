from fastapi import APIRouter
from src.utils.duckdb_helpers import read_table
from typing import Any, Dict

router = APIRouter()

def get_ticker_info(table: str) -> Dict[str, Dict]:
    res = {}
    try:
        df = read_table(table)
        if df is not None and not df.empty:
            if table == "features_tidy":
                ticker_col, date_col = "Ticker", "Date"
            else:
                # infer tickers from wide format
                cols = [c for c in df.columns if "_" in c and c.endswith("Close")]
                tickers = sorted(set(c.split("_")[0] for c in cols))
                ticker_col, date_col = None, "Date"
            tickers = (
                sorted(set(df[ticker_col])) if ticker_col else tickers
            )
            for ticker in tickers:
                if ticker_col:
                    dft = df[df[ticker_col] == ticker]
                else:
                    dft = df[[date_col, f"{ticker}_Close"]].dropna(subset=[f"{ticker}_Close"])
                if not dft.empty:
                    res[ticker] = {
                        "start_date": str(dft[date_col].min()),
                        "end_date": str(dft[date_col].max()),
                        "row_count": len(dft),
                    }
    except Exception:
        pass
    return res

@router.get("/data/available")
def get_available_data() -> Any:
    # Gather from all tables
    raw = get_ticker_info("raw")
    cleaned = get_ticker_info("cleaned")
    features = get_ticker_info("features_tidy")

    all_tickers = set(raw) | set(cleaned) | set(features)
    results = []
    for ticker in sorted(all_tickers):
        results.append({
            "ticker": ticker,
            "raw": raw.get(ticker),
            "cleaned": cleaned.get(ticker),
            "features": features.get(ticker),
        })
    return results
