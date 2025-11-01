# This file does not write the backtesting to the database
import os
import duckdb
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Callable, Any
from datetime import datetime
from src.utils.duckdb_helpers import ensure_predictions_table, get_con

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/database.duckdb"))

class BacktestResult:
    def __init__(self, equity_curve: pd.Series, trades: pd.DataFrame, metrics: Dict[str, float], params: Dict[str, Any]):
        self.equity_curve = equity_curve
        self.trades = trades
        self.metrics = metrics
        self.params = params

    def to_dict(self):
        return {
            "equity_curve": self.equity_curve.to_dict(),
            "trades": self.trades.to_dict(orient="records"),
            "metrics": self.metrics,
            "params": self.params,
        }

class BacktestingEngine:
    def __init__(
        self,
        db_path: Optional[str] = None,
        transaction_cost_bps: float = 1.0,
        slippage_bps: float = 0.0,
        initial_capital: float = 1_000_000,
        position_sizer: Optional[Callable] = None,
    ):
        self.db_path = db_path or DB_PATH
        self.transaction_cost_bps = transaction_cost_bps
        self.slippage_bps = slippage_bps
        self.initial_capital = initial_capital
        self.position_sizer = position_sizer or self.default_position_sizer

    def load_predictions(self, model_id: str) -> pd.DataFrame:
        ensure_predictions_table()
        with get_con() as con:
            preds = con.execute("SELECT * FROM predictions WHERE model_id = ?", [model_id]).df()
        return preds

    def run(
        self,
        model_id: str,
        tickers: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        position_sizer: Optional[Callable] = None,
        cost_bps: Optional[float] = None,
        slippage_bps: Optional[float] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> 'BacktestResult':
        preds = self.load_predictions(model_id)
        if tickers:
            preds = preds[preds["Ticker"].isin(tickers)]
        if start_date:
            preds = preds[preds["Date"] >= start_date]
        if end_date:
            preds = preds[preds["Date"] <= end_date]
        preds = preds.sort_values(["Date", "Ticker"])

        if preds.empty:
            raise ValueError(f"No prediction data found for model_id='{model_id}'. Cannot run backtest.")

        preds["Signal"] = np.where(preds["Prediction"] > 0, 1, np.where(preds["Prediction"] < 0, -1, 0))

        signals = preds.pivot(index="Date", columns="Ticker", values="Signal").fillna(0)
        position_sizer_fn = position_sizer or self.position_sizer
        weights = signals.apply(position_sizer_fn, axis=1, result_type="expand")

        returns = preds.pivot(index="Date", columns="Ticker", values="Return_1d").fillna(0)
        weights = weights.reindex_like(returns).fillna(0)

        gross_returns = (weights.shift().fillna(0) * returns).sum(axis=1)
        cost = (weights.diff().abs().sum(axis=1)) * ((cost_bps or self.transaction_cost_bps) / 10000.0)
        slippage = weights.diff().abs().sum(axis=1) * ((slippage_bps or self.slippage_bps) / 10000.0)
        net_returns = gross_returns - cost - slippage

        equity_curve = (1 + net_returns).cumprod() * self.initial_capital

        trade_list = []
        for date, row in weights.diff().iterrows():
            for ticker, change in row.items():
                if abs(change) > 1e-5:
                    trade_list.append({
                        "Date": date,
                        "Ticker": ticker,
                        "Change": change,
                        "WeightAfter": weights.at[date, ticker]
                    })
        trades = pd.DataFrame(trade_list)

        metrics = self.compute_metrics(equity_curve, net_returns)
        result = BacktestResult(equity_curve, trades, metrics, params or {})
        return result

    @staticmethod
    def default_position_sizer(signals: pd.Series) -> pd.Series:
        n = (signals != 0).sum()
        return signals / n if n > 0 else signals

    @staticmethod
    def compute_metrics(equity: pd.Series, returns: pd.Series) -> Dict[str, float]:
        if equity.empty or returns.empty:
            return {
                "total_return": 0.0,
                "sharpe": 0.0,
                "max_drawdown": 0.0,
                "cagr": 0.0,
                "volatility": 0.0,
            }
        daily = returns
        total_return = equity.iloc[-1] / equity.iloc[0] - 1
        sharpe = daily.mean() / (daily.std(ddof=0) + 1e-8) * (252 ** 0.5)
        drawdown = 1 - equity / equity.cummax()
        max_dd = drawdown.max()
        cagr = (equity.iloc[-1] / equity.iloc[0]) ** (252 / len(equity)) - 1 if len(equity) > 1 else 0.0
        volatility = daily.std(ddof=0) * (252 ** 0.5)
        return {
            "total_return": float(total_return),
            "sharpe": float(sharpe),
            "max_drawdown": float(max_dd),
            "cagr": float(cagr),
            "volatility": float(volatility),
        }
