from fastapi import APIRouter, HTTPException
from src.features.feature_engineering import compute_all_ticker_features
from src.features.tidy_feature_engineering import wide_to_tidy_features
from src.utils.duckdb_helpers import read_table, write_table
router = APIRouter()

@router.post("/data/features")
def generate_features():
    try:
        df = read_table("cleaned")
        feats = compute_all_ticker_features(df)
        write_table(feats, "features")
        
        # Also save tidy features
        tidy = wide_to_tidy_features(feats)
        write_table(tidy, "features_tidy")
        return {"success": True, "row_count": len(tidy)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
