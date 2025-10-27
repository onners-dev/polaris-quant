import pandas as pd
from typing import List, Dict, Any
from src.utils.pandas_helpers import flatten_columns

def get_tickers_from_columns(df: pd.DataFrame) -> List[str]:
    tickers = set()
    for col in df.columns:
        if "_" in col:
            tickers.add(col.split("_")[0])
    return sorted(tickers)

def required_columns_for_tickers(tickers: List[str], base_cols: List[str]) -> List[str]:
    return [f"{ticker}_{col}" for ticker in tickers for col in base_cols]

def validate_schema(df: pd.DataFrame, required_columns: List[str]) -> bool:
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return True

def detect_missing_data(df: pd.DataFrame) -> Dict[str, int]:
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    return missing.to_dict()

def detect_duplicates(df: pd.DataFrame, subset: List[str] = None) -> int:
    if subset:
        return df.duplicated(subset=subset).sum()
    return df.duplicated().sum()

def detect_outliers(df: pd.DataFrame, columns: List[str], z_thresh: float = 5.0) -> Dict[str, int]:
    outlier_counts = {}
    for col in columns:
        if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
            zscores = (df[col] - df[col].mean()) / df[col].std(ddof=0)
            outlier_counts[col] = int((zscores.abs() > z_thresh).sum())
    return outlier_counts

def basic_cleaning(df: pd.DataFrame) -> pd.DataFrame:
    df = flatten_columns(df)
    df = df.copy()
    df = df.drop_duplicates()
    df = df.ffill().bfill()
    return df

def run_full_validation(
    df: pd.DataFrame, 
    required_columns: List[str], 
    outlier_columns: List[str]
) -> Dict[str, Any]:
    df = flatten_columns(df)
    if any("_" in col for col in df.columns):
        tickers = get_tickers_from_columns(df)
        base_cols = ["Open", "High", "Low", "Close", "Volume"]
        required_columns = required_columns_for_tickers(tickers, base_cols)
        outlier_columns = required_columns.copy()
    results = {}
    validate_schema(df, required_columns)
    results["missing_data"] = detect_missing_data(df)
    results["duplicate_rows"] = detect_duplicates(df)
    results["outliers"] = detect_outliers(df, outlier_columns)
    return results
