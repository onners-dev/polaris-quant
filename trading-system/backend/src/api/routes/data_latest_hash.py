from fastapi import APIRouter, Query
from typing import List, Optional
import duckdb
import pandas as pd
from src.utils.data_hash import hash_dataframe, hash_series
from src.utils.duckdb_helpers import get_con

router = APIRouter()

@router.get("/data/latest-hash")
def latest_data_hash(
    tickers: Optional[List[str]] = Query(None),
    target: str = "Return_1d"
):
    with get_con() as con:
        df = con.execute("SELECT * FROM features_tidy").df()
    if tickers:
        df = df[df["Ticker"].isin(tickers)]
    if target in df.columns:
        df = df.dropna(subset=[target])
    cols = [c for c in df.columns if c not in ("Date", "Ticker", target)]
    features_hash = hash_dataframe(df[cols])
    target_hash = hash_series(df[target]) if target in df.columns else None
    last_date = str(df["Date"].max()) if "Date" in df.columns else None
    return {
        "features_hash": features_hash,
        "target_hash": target_hash,
        "last_date": last_date,
        "row_count": len(df)
    }
