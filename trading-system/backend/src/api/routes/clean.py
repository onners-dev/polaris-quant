from fastapi import APIRouter, HTTPException
from src.utils.duckdb_helpers import read_table, write_table
from src.validation.validate_data import run_full_validation, basic_cleaning

router = APIRouter()

def jsonify(obj):
    import numpy as np
    if isinstance(obj, dict):
        return {k: jsonify(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [jsonify(x) for x in obj]
    elif isinstance(obj, (np.integer,)):
        return int(obj)
    elif isinstance(obj, (np.floating,)):
        return float(obj)
    elif isinstance(obj, (np.ndarray,)):
        return obj.tolist()
    else:
        return obj

@router.post("/data/clean")
def clean_data():
    try:
        df = read_table("raw")
        if df is None or df.empty:
            raise HTTPException(status_code=400, detail="No raw data found.")
        results = run_full_validation(df, [], [])
        cleaned = basic_cleaning(df)
        write_table(cleaned, "cleaned")
        payload = {
            "success": True,
            "validation": jsonify(results),
            "row_count": int(len(cleaned))
        }
        return payload
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
