#Uses the basic backtesting engine but also persists the results to the database
import uuid
from datetime import datetime
from .backtest_results import save_backtest_result
from .backtesting_engine import BacktestingEngine as BaseBacktestingEngine

class BacktestingEngine(BaseBacktestingEngine):
    def run_persistent(
        self,
        model_id: str,
        tickers = None,
        start_date = None,
        end_date = None,
        position_sizer = None,
        cost_bps = None,
        slippage_bps = None,
        params = None,
    ):
        result = super().run(
            model_id=model_id,
            tickers=tickers,
            start_date=start_date,
            end_date=end_date,
            position_sizer=position_sizer,
            cost_bps=cost_bps,
            slippage_bps=slippage_bps,
            params=params,
        )
        run_id = f"{model_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        save_backtest_result(
            run_id=run_id,
            model_id=model_id,
            params=params or {},
            start_date=start_date,
            end_date=end_date,
            metrics=result.metrics,
            equity_curve=result.equity_curve.to_dict(),
            trades=result.trades.to_dict(orient="records"),
        )
        result.params["run_id"] = run_id
        return result
