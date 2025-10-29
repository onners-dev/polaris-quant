import os
import duckdb
import pandas as pd
import xgboost as xgb
import joblib
import json
from datetime import datetime
from typing import Dict, List, Optional
from src.utils.json_safe import clean_for_json


DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/database.duckdb"))
MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../models/artifacts"))
REGISTRY_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../models/registry.json"))
os.makedirs(MODEL_DIR, exist_ok=True)

def fetch_tidy_features(
    tickers: Optional[List[str]] = None,
    target_col: str = "Return_1d"
) -> pd.DataFrame:
    with duckdb.connect(DB_PATH) as con:
        df = con.execute(f"SELECT * FROM features_tidy").fetchdf()
    if tickers:
        df = df[df["Ticker"].isin(tickers)]
    df = df.dropna(subset=[target_col])
    return df

def prep_data(df: pd.DataFrame, target_col: str):
    y = df[target_col]
    X = df.drop(columns=["Date", "Ticker", target_col])
    # One-hot encode Ticker if multi-ticker
    if "Ticker" in df and len(df["Ticker"].unique()) > 1:
        X = pd.get_dummies(X, columns=[], prefix="", prefix_sep="")
    cutoff = int(len(X) * 0.8)
    X_train, X_val = X.iloc[:cutoff], X.iloc[cutoff:]
    y_train, y_val = y.iloc[:cutoff], y.iloc[cutoff:]
    return X_train, X_val, y_train, y_val

def train_and_save(
    tickers: Optional[List[str]] = None,
    target_col: str = "Return_1d"
) -> Dict:
    df = fetch_tidy_features(tickers, target_col)
    if df.empty:
        raise ValueError("No features found for training")
    X_train, X_val, y_train, y_val = prep_data(df, target_col)
    model = xgb.XGBRegressor(n_estimators=100, max_depth=3)
    model.set_params(eval_metric="rmse")
    try:
        model.fit(
            X_train,
            y_train,
            eval_set=[(X_val, y_val)],
            early_stopping_rounds=10,
            verbose=False
        )
    except TypeError:  # Early stopping not supported in your XGBoost version
        model.fit(
            X_train,
            y_train,
            eval_set=[(X_val, y_val)],
            verbose=False
        )
    val_score = model.score(X_val, y_val)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_type = "single" if tickers and len(tickers) == 1 else "multi"
    mid = (
        f"{'_'.join(tickers) if tickers else 'ALL'}_xgb_{target_col}_{ts}"
        if model_type == "multi"
        else f"{tickers[0]}_xgb_{target_col}_{ts}"
    )
    model_path = os.path.join(MODEL_DIR, f"{mid}.joblib")
    joblib.dump(model, model_path)
    meta = {
        "model_id": mid,
        "model_type": model_type,
        "tickers": tickers if tickers else "ALL",
        "target": target_col,
        "val_score": float(val_score),
        "trained_at": datetime.now().isoformat(),
        "model_path": model_path,
        "params": model.get_params(),
    }
    meta = clean_for_json(meta) 
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
    # Multi-ticker example
    print(train_and_save(tickers=["AAPL", "MSFT"]))
    # Single-ticker example
    # print(train_and_save(tickers=["AAPL"]))
    # Universal (all tickers)
    # print(train_and_save())
