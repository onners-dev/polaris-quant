import os
import duckdb
import json
from datetime import datetime
from typing import Dict, Any, Optional

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/database.duckdb"))

def ensure_backtest_table():
    ddl = """
    CREATE TABLE IF NOT EXISTS backtest_results (
        run_id VARCHAR PRIMARY KEY,
        model_id VARCHAR,
        params JSON,
        start_date DATE,
        end_date DATE,
        created_at TIMESTAMP,
        metrics JSON,
        equity_curve JSON,
        trades JSON
    );
    """
    with duckdb.connect(DB_PATH) as con:
        con.execute(ddl)

def save_backtest_result(run_id: str, model_id: str, params: Dict[str, Any], start_date: str, end_date: str,
                         metrics: Dict[str, Any], equity_curve: Dict, trades: Dict):
    ensure_backtest_table()
    record = {
        "run_id": run_id,
        "model_id": model_id,
        "params": json.dumps(params),
        "start_date": start_date,
        "end_date": end_date,
        "created_at": datetime.now().isoformat(),
        "metrics": json.dumps(metrics),
        "equity_curve": json.dumps(equity_curve),
        "trades": json.dumps(trades),
    }
    with duckdb.connect(DB_PATH) as con:
        cols = ','.join(record.keys())
        vals = ','.join(['?']*len(record))
        sql = f"INSERT INTO backtest_results ({cols}) VALUES ({vals})"
        con.execute(sql, list(record.values()))

def load_backtest_result(run_id: str) -> Optional[Dict[str, Any]]:
    ensure_backtest_table()
    with duckdb.connect(DB_PATH) as con:
        res = con.execute("SELECT * FROM backtest_results WHERE run_id = ?", [run_id]).fetchone()
        if res is None:
            return None
        colnames = [desc[0] for desc in con.description]
        record = dict(zip(colnames, res))
        # Parse JSON fields
        record["params"] = json.loads(record["params"])
        record["metrics"] = json.loads(record["metrics"])
        record["equity_curve"] = json.loads(record["equity_curve"])
        record["trades"] = json.loads(record["trades"])
        return record

def list_backtest_results(limit: int = 20, model_id: Optional[str] = None) -> list:
    ensure_backtest_table()
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
    results["metrics"] = results["metrics"].apply(lambda m: json.loads(m) if isinstance(m, str) else (m or {}))
    return results.to_dict(orient="records")
