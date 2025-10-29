import os
import duckdb
import pandas as pd
import xgboost as xgb
import joblib
import json
from datetime import datetime
from typing import Dict

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/database.duckdb"))
MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../models/artifacts"))
REGISTRY_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../models/registry.json"))
os.makedirs(MODEL_DIR, exist_ok=True)

def fetch_features(ticker: str, target_col: str) -> pd.DataFrame:
    with duckdb.connect(DB_PATH) as con:
        df = con.execute(f"SELECT * FROM features").fetchdf()
    needed = [c for c in df.columns if c.startswith(f"{ticker}_")] + ["Date"]
    needed = list(sorted(set(needed)))
    df = df[needed]
    df = df.dropna(subset=[f"{ticker}_{target_col}"])
    return df

def prep_data(df: pd.DataFrame, ticker: str, target_col: str):
    y = df[f"{ticker}_{target_col}"]
    X = df.drop(columns=["Date", f"{ticker}_{target_col}"])
    cutoff = int(len(X) * 0.8)
    X_train, X_val = X.iloc[:cutoff], X.iloc[cutoff:]
    y_train, y_val = y.iloc[:cutoff], y.iloc[cutoff:]
    return X_train, X_val, y_train, y_val

def train_and_save(ticker: str, target_col: str = "Return_1d") -> Dict:
    df = fetch_features(ticker, target_col)
    if df.empty:
        raise ValueError("No features found for training")
    X_train, X_val, y_train, y_val = prep_data(df, ticker, target_col)
    model = xgb.XGBRegressor(n_estimators=100, max_depth=3)
    model.set_params(eval_metric="rmse")
    # Try using early stopping if available, otherwise skip
    try:
        model.fit(
            X_train,
            y_train,
            eval_set=[(X_val, y_val)],
            early_stopping_rounds=10,
            verbose=False
        )
    except TypeError:
        model.fit(
            X_train,
            y_train,
            eval_set=[(X_val, y_val)],
            verbose=False
        )
    val_score = model.score(X_val, y_val)
    fname = f"{ticker}_xgb_{target_col}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.joblib"
    model_path = os.path.join(MODEL_DIR, fname)
    joblib.dump(model, model_path)
    meta = {
        "model_id": fname.replace(".joblib",""),
        "ticker": ticker,
        "target": target_col,
        "val_score": float(val_score),
        "trained_at": datetime.now().isoformat(),
        "model_path": model_path,
        "params": model.get_params(),
    }
    reg = []
    if os.path.exists(REGISTRY_PATH):
        with open(REGISTRY_PATH, "r") as f:
            try:
                reg = json.load(f)
            except:
                reg = []
    reg.append(meta)
    with open(REGISTRY_PATH, "w") as f:
        json.dump(reg, f, indent=2)
    return meta

if __name__ == "__main__":
    # Example usage
    print(train_and_save("AAPL"))
