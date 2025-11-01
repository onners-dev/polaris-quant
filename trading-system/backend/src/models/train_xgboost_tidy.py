import os
import duckdb
import pandas as pd
import xgboost as xgb
import joblib
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from src.utils.json_safe import clean_for_json
from src.utils.duckdb_helpers import append_table

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/database.duckdb"))
MODEL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../models/artifacts"))
REGISTRY_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../models/registry.json"))
os.makedirs(MODEL_DIR, exist_ok=True)

def feature_data_hash(df: pd.DataFrame) -> str:
    hash_obj = hashlib.sha256(pd.util.hash_pandas_object(df, index=True).values)
    return hash_obj.hexdigest()

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
        self.val_score = None
        self.data_hash = None
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
        if "Ticker" in df and len(df["Ticker"].unique()) > 1:
            pass
        self.feature_names = list(X.columns)
        self.data_hash = feature_data_hash(X)
        cutoff = int(len(X) * 0.8)
        return X.iloc[:cutoff], X.iloc[cutoff:], y.iloc[:cutoff], y.iloc[cutoff:]

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
        self.val_score = float(self.model.score(X_val, y_val))

    def save_artifacts(self):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_type = "single" if self.tickers and len(self.tickers) == 1 else "multi"
        base_name = (
            f"{'_'.join(self.tickers) if self.tickers else 'ALL'}_xgb_{self.target_col}"
        )
        unique_part = self.data_hash[:8]
        model_id = f"{base_name}_{unique_part}_{ts}"
        model_path = os.path.join(MODEL_DIR, f"{model_id}.joblib")
        joblib.dump(self.model, model_path)

        meta = {
            "model_id": model_id,
            "model_type": model_type,
            "tickers": self.tickers if self.tickers else "ALL",
            "target": self.target_col,
            "trained_at": datetime.now().isoformat(),
            "val_score": self.val_score,
            "model_path": model_path,
            "features": self.feature_names,
            "data_hash": self.data_hash,
            "feature_importances": self.model.feature_importances_.tolist(),
            "params": clean_for_json(self.model.get_params()),
            "seed": self.seed,
        }
        meta = clean_for_json(meta)
        self.registry_meta = meta
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
        import duckdb
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
        
        from src.utils.duckdb_helpers import append_table
        append_table(out_df, "predictions")

    def run(self):
        df = self.fetch_features()
        if df.empty:
            raise ValueError("No features found for training")
        X_train, X_val, y_train, y_val = self.prepare_data(df)
        self.train(X_train, y_train, X_val, y_val)
        meta = self.save_artifacts()
        self.update_registry()
        self.write_predictions()  # <-- AUTOMATIC prediction write
        return meta

if __name__ == "__main__":
    trainer = ModelTrainer(tickers=["AAPL", "MSFT"], target_col="Return_1d")
    meta = trainer.run()
    print(json.dumps(meta, indent=2))
