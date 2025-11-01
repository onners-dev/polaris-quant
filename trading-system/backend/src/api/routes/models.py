from fastapi import APIRouter, HTTPException, Query
import os
import json
from typing import List, Optional, Union
from src.utils.json_safe import clean_for_json

REGISTRY_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../models/registry.json"))

router = APIRouter()

@router.get("/models/list")
def list_models(
    ticker: Optional[str] = Query(None, description="Filter for models containing this ticker (case insensitive)")
):
    if not os.path.exists(REGISTRY_PATH):
        return []
    with open(REGISTRY_PATH, "r") as f:
        try:
            reg = json.load(f)
        except Exception:
            return []
    if ticker:
        ticker_upper = ticker.upper()
        def match(model):
            model_tickers = model.get("tickers")
            if isinstance(model_tickers, list):
                return any(t.upper() == ticker_upper for t in model_tickers)
            elif isinstance(model_tickers, str):
                return model_tickers.upper() == ticker_upper
            return False
        reg = [m for m in reg if match(m)]
    reg_clean = [clean_for_json(m) for m in reg]
    return reg_clean

@router.get("/models/{model_id}")
def get_model(model_id: str):
    if not os.path.exists(REGISTRY_PATH):
        raise HTTPException(status_code=404, detail="Registry not found")
    with open(REGISTRY_PATH, "r") as f:
        try:
            reg = json.load(f)
        except Exception:
            raise HTTPException(status_code=500, detail="Failed to parse registry")
    model = next((m for m in reg if m.get("model_id") == model_id), None)
    if model is None:
        raise HTTPException(status_code=404, detail="Model not found")
    return clean_for_json(model)
