from fastapi import APIRouter, HTTPException, Query
from src.utils.duckdb_helpers import read_table

router = APIRouter()

@router.get("/data/table")
def get_table_data(
    table: str = Query(..., regex="^(raw|cleaned|features)$"),
    ticker: str = Query(...)
):
    df = read_table(table)
    if df is None or df.empty:
        return []
    # Always include 'Date' column if present
    cols = [c for c in df.columns if c.startswith(f"{ticker}_")]
    if "Date" in df.columns:
        cols = ["Date"] + cols
    if not cols or all(col not in df.columns for col in cols):
        return []
    result = df[cols].dropna().to_dict(orient="records")
    return result
