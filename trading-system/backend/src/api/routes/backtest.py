from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from src.backtesting.backtesting_engine_mode import BacktestingEngine
from src.backtesting import backtest_results
import traceback

router = APIRouter()

class BacktestRequest(BaseModel):
    model_id: str
    tickers: Optional[List[str]] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    transaction_cost_bps: float = 1.0
    slippage_bps: float = 0.0

@router.post("/backtest/run")
def run_backtest(req: BacktestRequest):
    try:
        engine = BacktestingEngine(transaction_cost_bps=req.transaction_cost_bps, slippage_bps=req.slippage_bps)
        result = engine.run_persistent(
            model_id=req.model_id,
            tickers=req.tickers,
            start_date=req.start_date,
            end_date=req.end_date
        )
        return {"success": True, "result": result.to_dict(), "run_id": result.params.get("run_id")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/backtest/list")
def list_backtests(model_id: Optional[str] = Query(None), limit: int = Query(20)):
    return backtest_results.list_backtest_results(limit=limit, model_id=model_id)

@router.get("/backtest/{run_id}")
def get_backtest(run_id: str):
    result = backtest_results.load_backtest_result(run_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return result
