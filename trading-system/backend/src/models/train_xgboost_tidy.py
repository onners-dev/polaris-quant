import os
import duckdb
import pandas as pd
import xgboost as xgb
import joblib
import numpy as np
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

class ModelTrainer:
    def __init__(
        self,
        tickers: Optional[List[str]] = None,
        target_col: str = "Return_1d",
        model_params: Optional[Dict[str, Any]] = None,
        seed: Optional[int] = 42,
    ):
        self.tickers = tickers
        self.target_col = target_col
        self.model_params = model_params or {"n_estimators": 100, "max_depth": 3}
        self.seed = seed
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

    def prepare_data(self, df: pd.DataFrame):
        y = df[self.target_col]
        X = df.drop(columns=["Date", "Ticker", self.target_col])
        dates = df["Date"]
        N = len(X)
        n_test = int(np.ceil(0.2 * N))
        n_val = int(np.ceil(0.2 * N))
        idx_train = slice(0, N - n_val - n_test)
        idx_val = slice(N - n_val - n_test, N - n_test)
        idx_test = slice(N - n_test, N)
        return {
            "X_train": X.iloc[idx_train],
            "y_train": y.iloc[idx_train],
            "dates_train": dates.iloc[idx_train],
            "X_val": X.iloc[idx_val],
            "y_val": y.iloc[idx_val],
            "dates_val": dates.iloc[idx_val],
            "X_test": X.iloc[idx_test],
            "y_test": y.iloc[idx_test],
            "dates_test": dates.iloc[idx_test]
        }

    def train(self, X_train, y_train, X_val, y_val):
        params = {**self.model_params, "random_state": self.seed, "eval_metric": "rmse"}
        self.model = xgb.XGBRegressor(**params)
        try:
            self.model.fit(
                X_train,
                y_train,
                eval_set=[(X_val, y_val)],
                early_stopping_rounds=10,
                verbose=False,
            )
        except TypeError:
            self.model.fit(
                X_train,
                y_train,
                eval_set=[(X_val, y_val)],
                verbose=False,
            )

    def save_artifacts(self, meta):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_type = "single" if self.tickers and len(self.tickers) == 1 else "multi"
        base_name = (
            f"{'_'.join(self.tickers) if self.tickers else 'ALL'}_xgb_{self.target_col}"
        )
        unique_part = meta["features_hash_train"][:8]
        model_id = f"{base_name}_{unique_part}_{ts}"
        model_path = os.path.join(MODEL_DIR, f"{model_id}.joblib")
        joblib.dump(self.model, model_path)
        meta["model_id"] = model_id
        meta["model_type"] = model_type
        meta["model_path"] = model_path
        meta["feature_importances"] = self.model.feature_importances_.tolist()
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
        splits = self.prepare_data(df)
        # Compute hashes for splits
        hash_dict = {
            "features_hash_train": hash_dataframe(splits["X_train"]),
            "features_hash_val": hash_dataframe(splits["X_val"]),
            "features_hash_test": hash_dataframe(splits["X_test"]),
            "target_hash_train": hash_series(splits["y_train"]),
            "target_hash_val": hash_series(splits["y_val"]),
            "target_hash_test": hash_series(splits["y_test"]),
        }
        self.feature_names = list(splits["X_train"].columns)
        self.train(splits["X_train"], splits["y_train"], splits["X_val"], splits["y_val"])
        # Metrics on each split
        preds_val = self.model.predict(splits["X_val"])
        preds_test = self.model.predict(splits["X_test"])
        val_metrics = {
            "val_rmse": rmse(splits["y_val"], preds_val),
            "val_sharpe": sharpe_ratio(splits["y_val"]),
            "val_drawdown": max_drawdown(splits["y_val"]),
        }
        test_metrics = {
            "test_rmse": rmse(splits["y_test"], preds_test),
            "test_sharpe": sharpe_ratio(splits["y_test"]),
            "test_drawdown": max_drawdown(splits["y_test"]),
        }
        split_ranges = {
            "train_dates": [str(splits["dates_train"].min()), str(splits["dates_train"].max())],
            "validation_dates": [str(splits["dates_val"].min()), str(splits["dates_val"].max())],
            "test_dates": [str(splits["dates_test"].min()), str(splits["dates_test"].max())],
        }
        meta = {
            "tickers": self.tickers if self.tickers else "ALL",
            "target": self.target_col,
            "trained_at": datetime.now().isoformat(),
            "features": self.feature_names,
            "params": clean_for_json(self.model.get_params()),
            "seed": self.seed,
            **hash_dict,
            **split_ranges,
            **val_metrics,
            **test_metrics
        }
        meta = self.save_artifacts(meta)
        self.registry_meta = clean_for_json(meta)
        self.update_registry()
        self.write_predictions()
        return meta

if __name__ == "__main__":
    import numpy as np
    trainer = ModelTrainer(tickers=["AAPL", "MSFT"], target_col="Return_1d")
    meta = trainer.run()
    print(json.dumps(meta, indent=2))
