import os
import duckdb
import pandas as pd

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/database.duckdb"))

def get_con() -> duckdb.DuckDBPyConnection:
    return duckdb.connect(DB_PATH)

def write_table(df: pd.DataFrame, table: str, mode: str = "overwrite") -> None:
    with get_con() as con:
        if mode == "overwrite":
            con.execute(f"DROP TABLE IF EXISTS {table}")
        con.execute(f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM df")

def append_table(df: pd.DataFrame, table: str) -> None:
    with get_con() as con:
        con.execute(f"INSERT INTO {table} SELECT * FROM df")

def read_table(table: str) -> pd.DataFrame:
    with get_con() as con:
        return con.execute(f"SELECT * FROM {table}").df()

def run_query(query: str) -> pd.DataFrame:
    with get_con() as con:
        return con.execute(query).df()

def ensure_predictions_table():
    ddl = """
    CREATE TABLE IF NOT EXISTS predictions (
        model_id VARCHAR,
        Date VARCHAR,
        Ticker VARCHAR,
        Prediction DOUBLE,
        Return_1d DOUBLE
    );
    """
    with get_con() as con:
        con.execute(ddl)
