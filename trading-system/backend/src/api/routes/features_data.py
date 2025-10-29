from fastapi import APIRouter, HTTPException, Query
from src.utils.duckdb_helpers import read_table
from typing import Any

router = APIRouter()

@router.get("/data/features")
def get_features_for_ticker(ticker: str = Query(...)) -> Any:
    df = read_table("features")
    if df is None or df.empty:
        return []
    # Always include 'Date' if present
    cols = [c for c in df.columns if c.startswith(f"{ticker}_")]
    if "Date" in df.columns:
        cols = ["Date"] + cols
    if not cols or all(col not in df.columns for col in cols):
        return []
    result = df[cols].dropna().to_dict(orient="records")
    return result
