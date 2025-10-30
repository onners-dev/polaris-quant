from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from src.backtesting.backtest_results import load_backtest_result
import duckdb
import os

router = APIRouter()
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../data/database.duckdb"))

@router.get("/backtest/{run_id}")
def get_backtest_result(run_id: str):
    res = load_backtest_result(run_id)
    if res is None:
        raise HTTPException(status_code=404, detail="Backtest result not found")
    return res

@router.get("/backtest/list")
def list_backtests(limit: int = 20, model_id: Optional[str] = None):
    with duckdb.connect(DB_PATH) as con:
        if model_id:
            results = con.execute(
                "SELECT run_id, model_id, created_at, start_date, end_date, metrics FROM backtest_results WHERE model_id = ? ORDER BY created_at DESC LIMIT ?",
                [model_id, limit]
            ).fetchdf()
        else:
            results = con.execute(
                "SELECT run_id, model_id, created_at, start_date, end_date, metrics FROM backtest_results ORDER BY created_at DESC LIMIT ?",
                [limit]
            ).fetchdf()
    if results.empty:
        return []
    results["metrics"] = results["metrics"].apply(lambda m: m if isinstance(m, dict) else {})
    return results.to_dict(orient="records")
