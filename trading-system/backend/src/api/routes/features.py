from fastapi import APIRouter, HTTPException
from src.utils.duckdb_helpers import read_table, write_table
from src.features.feature_engineering import compute_all_ticker_features

router = APIRouter()

@router.post("/data/features")
def generate_features():
    try:
        df = read_table("cleaned")
        if df is None or df.empty:
            raise HTTPException(status_code=400, detail="No cleaned data found.")
        feats = compute_all_ticker_features(df)
        write_table(feats, "features")
        return {"success": True, "row_count": len(feats)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
