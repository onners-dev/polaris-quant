import pandas as pd
from typing import List, Dict, Any


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
        if pd.api.types.is_numeric_dtype(df[col]):
            zscores = (df[col] - df[col].mean()) / df[col].std(ddof=0)
            outlier_counts[col] = int((zscores.abs() > z_thresh).sum())
    return outlier_counts


def basic_cleaning(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.drop_duplicates()
    df = df.fillna(method="ffill").fillna(method="bfill")
    return df


def run_full_validation(
    df: pd.DataFrame, 
    required_columns: List[str], 
    outlier_columns: List[str]
) -> Dict[str, Any]:
    results = {}
    validate_schema(df, required_columns)
    results["missing_data"] = detect_missing_data(df)
    results["duplicate_rows"] = detect_duplicates(df)
    results["outliers"] = detect_outliers(df, outlier_columns)
    return results
