import os
import duckdb
import pandas as pd
import numpy as np
import joblib
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from src.utils.json_safe import clean_for_json
from src.utils.duckdb_helpers import append_table
from src.utils.data_hash import hash_dataframe, hash_series
from src.utils.metrics import rmse, sharpe_ratio, max_drawdown

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/database.duckdb"))
MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../models/artifacts"))
REGISTRY_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../models/registry.json"))
os.makedirs(MODEL_DIR, exist_ok=True)

try:
    import lightgbm as lgb
    HAS_LGB = True
except ImportError:
    HAS_LGB = False

import xgboost as xgb

PARAM_GRID = [
    {"max_depth": 3, "learning_rate": 0.1, "n_estimators": 100},
    {"max_depth": 4, "learning_rate": 0.05, "n_estimators": 150},
    {"max_depth": 5, "learning_rate": 0.03, "n_estimators": 200},
]

def walkforward_split(X, n_folds: int=3, val_size: float=0.2, test_size: float=0.2):
    n = len(X)
    fold_sizes = []
    min_train = int(n * 0.2)
    for i in range(n_folds):
        train_end = min_train + i * int((n - min_train) / n_folds)
        val_end = train_end + int(n * val_size)
        test_end = val_end + int(n * test_size)
        if test_end > n:
            break
        fold_sizes.append({"train": slice(0, train_end),
                           "val": slice(train_end, val_end),
                           "test": slice(val_end, test_end)})
    return fold_sizes

class ModelTrainer:
    def __init__(
        self,
        tickers: Optional[List[str]] = None,
        target_col: str = "Return_1d",
        model_params: Optional[Dict[str, Any]] = None,
        search_params: Optional[List[Dict[str, Any]]] = None,
        use_lightgbm: bool = False,
        seed: Optional[int] = 42,
        n_cv: int = 3,
    ):
        self.tickers = tickers
        self.target_col = target_col
        self.model_params = model_params or {"n_estimators": 100, "max_depth": 3}
        self.search_params = search_params or PARAM_GRID
        self.use_lightgbm = use_lightgbm and HAS_LGB
        self.seed = seed
        self.n_cv = n_cv
        self.model = None
        self.feature_names = None
        self.registry_meta = None

    def fetch_features(self) -> pd.DataFrame:
        with duckdb.connect(DB_PATH) as con:
            df = con.execute(f"SELECT * FROM features_tidy").fetchdf()
        if self.tickers:
            df = df[df["Ticker"].isin(self.tickers)]
        df = df.dropna(subset=[self.target_col])
        return df

    def get_model(self, params: Dict[str, Any]):
        params = dict(params, random_state=self.seed)
        if self.use_lightgbm:
            return lgb.LGBMRegressor(**params)
        return xgb.XGBRegressor(**params, eval_metric="rmse")

    def rolling_cv_metrics(self, X, y, dates):
        folds = walkforward_split(X, n_folds=self.n_cv)
        results = []
        importances = []
        best_score = 1e10
        best_model = None
        best_params = None
        best_metrics = []
        for cfg in self.search_params:
            fold_metrics = []
            fold_imports = []
            for fold in folds:
                model = self.get_model(cfg)
                X_train, y_train = X.iloc[fold["train"]], y.iloc[fold["train"]]
                X_val, y_val = X.iloc[fold["val"]], y.iloc[fold["val"]]
                X_test, y_test = X.iloc[fold["test"]], y.iloc[fold["test"]]
                # Safe fit for early_stopping_rounds depending on version
                try:
                    model.fit(
                        X_train,
                        y_train,
                        eval_set=[(X_val, y_val)],
                        early_stopping_rounds=10,
                        verbose=False
                    )
                except TypeError:
                    try:
                        model.fit(
                            X_train,
                            y_train,
                            eval_set=[(X_val, y_val)],
                            verbose=False
                        )
                    except Exception:
                        model.fit(X_train, y_train)
                preds_val = model.predict(X_val)
                preds_test = model.predict(X_test)
                fold_result = {
                    "params": clean_for_json(model.get_params()),
                    "val_rmse": rmse(y_val, preds_val),
                    "val_sharpe": sharpe_ratio(y_val),
                    "val_drawdown": max_drawdown(y_val),
                    "test_rmse": rmse(y_test, preds_test),
                    "test_sharpe": sharpe_ratio(y_test),
                    "test_drawdown": max_drawdown(y_test),
                }
                imports = model.feature_importances_.tolist() if hasattr(model, "feature_importances_") else []
                fold_metrics.append(fold_result)
                fold_imports.append(imports)
            mean_val_rmse = float(np.mean([m["val_rmse"] for m in fold_metrics])) if fold_metrics else 1e10
            if mean_val_rmse < best_score:
                best_score = mean_val_rmse
                best_model = model
                best_params = cfg
                best_metrics = fold_metrics
            results.append({"cfg": cfg, "metrics": fold_metrics, "importances": fold_imports})
        return results, best_model, best_params, best_metrics

    def save_artifacts(self, meta):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_type = "single" if self.tickers and len(self.tickers) == 1 else "multi"
        tickers_s = self.tickers if self.tickers else "ALL"
        base_name = f"{'_'.join(tickers_s) if isinstance(tickers_s, list) else tickers_s}_model_{self.target_col}"
        model_id = f"{base_name}_{meta['features_hash_train'][:8]}_{ts}"
        model_path = os.path.join(MODEL_DIR, f"{model_id}.joblib")
        joblib.dump(self.model, model_path)
        meta["model_id"] = model_id
        meta["model_type"] = model_type
        meta["model_path"] = model_path
        meta["feature_importances"] = self.model.feature_importances_.tolist() if hasattr(self.model, "feature_importances_") else []
        return meta

    def update_registry(self):
        reg = []
        if os.path.exists(REGISTRY_PATH):
            with open(REGISTRY_PATH, "r") as f:
                try:
                    reg = json.load(f)
                except Exception:
                    reg = []
        reg.append(self.registry_meta)
        os.makedirs(os.path.dirname(REGISTRY_PATH), exist_ok=True)
        with open(REGISTRY_PATH, "w") as f:
            json.dump(reg, f, indent=2)

    def write_predictions(self):
        df = self.fetch_features()
        if df.empty or self.model is None or self.registry_meta is None:
            return
        with duckdb.connect(DB_PATH) as con:
            con.execute("DELETE FROM predictions WHERE model_id = ?", [self.registry_meta["model_id"]])
        X_pred = df.drop(columns=["Date", "Ticker", self.target_col])
        preds = self.model.predict(X_pred)
        out_df = pd.DataFrame({
            "model_id": self.registry_meta["model_id"],
            "Date": df["Date"],
            "Ticker": df["Ticker"],
            "Prediction": preds,
            "Return_1d": df[self.target_col],
        })
        append_table(out_df, "predictions")

    def run(self):
        df = self.fetch_features()
        if df.empty:
            raise ValueError("No features found for training")
        y = df[self.target_col]
        X = df.drop(columns=["Date", "Ticker", self.target_col])
        dates = df["Date"]
        self.feature_names = list(X.columns)
        cv_results, best_model, best_params, best_metrics = self.rolling_cv_metrics(X, y, dates)
        self.model = best_model
        self.model_params = best_params

        # Compute leaderboard summary metrics for best run
        test_sharpes = [m.get("test_sharpe", 0) for m in best_metrics]
        test_rmses = [m.get("test_rmse", 0) for m in best_metrics]
        test_drawdowns = [m.get("test_drawdown", 0) for m in best_metrics]

        hash_dict = {
            "features_hash_train": hash_dataframe(X),
            "target_hash_train": hash_series(y)
        }
        ts = datetime.now().isoformat()
        meta = {
            "tickers": self.tickers if self.tickers else "ALL",
            "target": self.target_col,
            "trained_at": ts,
            "features": self.feature_names,
            "params": clean_for_json(best_params),
            "seed": self.seed,
            "cv_results": cv_results,
            "test_sharpe": float(np.mean(test_sharpes)) if test_sharpes else None,
            "test_rmse": float(np.mean(test_rmses)) if test_rmses else None,
            "test_drawdown": float(np.mean(test_drawdowns)) if test_drawdowns else None,
            **hash_dict,
        }
        meta = self.save_artifacts(meta)
        self.registry_meta = clean_for_json(meta)
        self.update_registry()
        self.write_predictions()
        return meta

if __name__ == "__main__":
    trainer = ModelTrainer(tickers=["AAPL", "MSFT"], target_col="Return_1d", use_lightgbm=False)
    meta = trainer.run()
    print(json.dumps(meta, indent=2))
