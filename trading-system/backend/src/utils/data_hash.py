import pandas as pd
import hashlib

def hash_dataframe(df: pd.DataFrame) -> str:
    values = pd.util.hash_pandas_object(df, index=True).values
    return hashlib.sha256(values).hexdigest()

def hash_series(s: pd.Series) -> str:
    values = pd.util.hash_pandas_object(s, index=True).values
    return hashlib.sha256(values).hexdigest()
