from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from src.backtesting.walkforward_engine import walk_forward_backtest

router = APIRouter()

class WalkForwardRequest(BaseModel):
    model_id: str
    tickers: Optional[List[str]] = None
    full_start: str
    full_end: str
    window_train: int
    window_test: int
    stride: Optional[int] = None
    transaction_cost_bps: float = 1.0
    slippage_bps: float = 0.0

@router.post("/backtest/walkforward")
def run_walkforward(req: WalkForwardRequest):
    try:
        res = walk_forward_backtest(
            model_id=req.model_id,
            tickers=req.tickers,
            full_start=req.full_start,
            full_end=req.full_end,
            window_train=req.window_train,
            window_test=req.window_test,
            stride=req.stride,
            transaction_cost_bps=req.transaction_cost_bps,
            slippage_bps=req.slippage_bps
        )
        # Summarize per-window and aggregate stats
        split_metrics = [r["metrics"] for r in res.runs]
        summary = res.summarize()
        return {
            "success": True,
            "splits": res.runs,
            "summary": summary,
            "params": res.params
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
