import duckdb
import pandas as pd
import numpy as np
import uuid
from datetime import datetime, timedelta
from src.backtesting.backtesting_engine import BacktestingEngine

DB_PATH = "trading-system/data/database.duckdb"
MODEL_ID = "UNITTEST_XGB_" + str(uuid.uuid4())

def create_test_predictions(db_path=DB_PATH, model_id=MODEL_ID, days=30, tickers=["AAPL", "MSFT"]):
    now = datetime.now()
    data = []
    for i in range(days):
        day = (now - timedelta(days=days - i)).strftime('%Y-%m-%d')
        for ticker in tickers:
            pred = np.random.normal(0, 0.01)
            ret = pred + np.random.normal(0, 0.01)
            data.append({
                "Date": day,
                "Ticker": ticker,
                "Prediction": pred,
                "Return_1d": ret,
                "model_id": model_id
            })
    df = pd.DataFrame(data)
    con = duckdb.connect(db_path)
    con.execute("CREATE TABLE IF NOT EXISTS predictions (Date DATE, Ticker VARCHAR, Prediction DOUBLE, Return_1d DOUBLE, model_id VARCHAR)")
    con.execute("DELETE FROM predictions WHERE model_id = ?", [model_id])
    con.execute("INSERT INTO predictions SELECT * FROM df")
    con.close()
    return model_id

if __name__ == "__main__":
    model_id = create_test_predictions()
    engine = BacktestingEngine(db_path=DB_PATH)
    result = engine.run(model_id=model_id)
    print("Equity curve (tail):", result.equity_curve.tail())
    print("Trade sample:", result.trades.head())
    print("Metrics:", result.metrics)
