from fastapi import APIRouter, HTTPException
from typing import Optional
from src.backtesting.backtest_results import load_backtest_result, list_backtest_results

router = APIRouter()

@router.get("/backtest/{run_id}")
def get_backtest_result(run_id: str):
    res = load_backtest_result(run_id)
    if res is None:
        raise HTTPException(status_code=404, detail="Backtest result not found")
    return res

@router.get("/backtest/list")
def list_backtests(limit: int = 20, model_id: Optional[str] = None):
    return list_backtest_results(limit=limit, model_id=model_id)
