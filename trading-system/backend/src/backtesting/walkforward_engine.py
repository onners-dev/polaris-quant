import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any
from datetime import datetime
from src.backtesting.backtesting_engine import BacktestingEngine
from src.backtesting.backtest_results import save_backtest_result

class WalkForwardResult:
    def __init__(self, runs: List[dict], params: dict):
        self.runs = runs
        self.params = params

    def summarize(self):
        dfs = [pd.DataFrame([r["metrics"]]) for r in self.runs if "metrics" in r]
        if dfs:
            summary = pd.concat(dfs).mean(numeric_only=True).to_dict()
        else:
            summary = {}
        return summary

def walk_forward_backtest(
    model_id: str,
    tickers: Optional[List[str]],
    full_start: str,
    full_end: str,
    window_train: int,
    window_test: int,
    stride: int = None,
    transaction_cost_bps: float = 1.0,
    slippage_bps: float = 0.0
) -> WalkForwardResult:
    stride = stride or window_test
    engine = BacktestingEngine(transaction_cost_bps=transaction_cost_bps, slippage_bps=slippage_bps)
    # Load all preds for model/tickers/date range
    preds = engine.load_predictions(model_id)
    if tickers:
        preds = preds[preds["Ticker"].isin(tickers)]
    preds = preds[(preds["Date"] >= full_start) & (preds["Date"] <= full_end)]
    preds = preds.sort_values(["Date", "Ticker"])
    unique_dates = pd.Series(preds["Date"].unique()).sort_values()
    runs = []
    i = 0
    while i + window_train + window_test <= len(unique_dates):
        train_start = unique_dates.iloc[i]
        train_end = unique_dates.iloc[i + window_train - 1]
        test_start = unique_dates.iloc[i + window_train]
        test_end = unique_dates.iloc[i + window_train + window_test - 1]
        # Define test slice
        test_mask = (preds["Date"] >= test_start) & (preds["Date"] <= test_end)
        test_preds = preds[test_mask].copy()
        if test_preds.empty:
            i += stride
            continue
        result = engine.run(
            model_id=model_id,
            tickers=tickers,
            start_date=str(test_start),
            end_date=str(test_end),
            params={"window_train": window_train, "window_test": window_test,
                    "train_period": (str(train_start), str(train_end)), "test_period": (str(test_start), str(test_end))}
        )
        run_id = f"{model_id}_WF_{str(test_start)}_{str(test_end)}"
        save_backtest_result(
            run_id=run_id,
            model_id=model_id,
            params={
                "window_train": window_train,
                "window_test": window_test,
                "train_period": (str(train_start), str(train_end)),
                "test_period": (str(test_start), str(test_end))
            },
            start_date=str(test_start),
            end_date=str(test_end),
            metrics=result.metrics,
            equity_curve=result.equity_curve.to_dict(),
            trades=result.trades.to_dict(orient="records"),
        )
        runs.append({
            "run_id": run_id,
            "train_period": (str(train_start), str(train_end)),
            "test_period": (str(test_start), str(test_end)),
            "metrics": result.metrics,
            "equity_curve": result.equity_curve.to_dict(),
            "params": result.params
        })
        i += stride
    return WalkForwardResult(runs=runs, params={"model_id": model_id, "window_train": window_train, "window_test": window_test})

