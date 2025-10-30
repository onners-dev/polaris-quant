from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from src.backtesting.backtesting_engine import BacktestingEngine

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
        result = engine.run(
            model_id=req.model_id,
            tickers=req.tickers,
            start_date=req.start_date,
            end_date=req.end_date,
        )
        return {"success": True, "result": result.to_dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
