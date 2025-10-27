import os
import pandas as pd
import numpy as np
from src.utils.pandas_helpers import flatten_columns

CLEANED_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/cleaned"))
FEATURES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/features"))
os.makedirs(FEATURES_DIR, exist_ok=True)

def add_returns(df: pd.DataFrame) -> pd.DataFrame:
    df["Return_1d"] = df["Close"].pct_change()
    df["Return_5d"] = df["Close"].pct_change(5)
    df["Return_21d"] = df["Close"].pct_change(21)
    return df

def add_moving_averages(df: pd.DataFrame) -> pd.DataFrame:
    df["SMA_5"] = df["Close"].rolling(5).mean()
    df["SMA_20"] = df["Close"].rolling(20).mean()
    df["EMA_12"] = df["Close"].ewm(span=12, adjust=False).mean()
    df["EMA_26"] = df["Close"].ewm(span=26, adjust=False).mean()
    return df

def add_volatility(df: pd.DataFrame) -> pd.DataFrame:
    df["Volatility_10"] = df["Return_1d"].rolling(10).std()
    df["Volatility_21"] = df["Return_1d"].rolling(21).std()
    return df

def add_rolling_extremes(df: pd.DataFrame) -> pd.DataFrame:
    df["Rolling_Max_20"] = df["High"].rolling(20).max()
    df["Rolling_Min_20"] = df["Low"].rolling(20).min()
    return df

def add_rsi(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()
    rs = avg_gain / (avg_loss + 1e-10)
    df["RSI_14"] = 100 - (100 / (1 + rs))
    return df

def add_bollinger_bands(df: pd.DataFrame, window: int = 20, num_std: float = 2.0) -> pd.DataFrame:
    sma = df["Close"].rolling(window).mean()
    std = df["Close"].rolling(window).std()
    df["BB_upper"] = sma + num_std * std
    df["BB_lower"] = sma - num_std * std
    df["BB_bandwidth"] = (df["BB_upper"] - df["BB_lower"]) / sma
    return df

def add_momentum(df: pd.DataFrame, window: int = 10) -> pd.DataFrame:
    df["Momentum_10"] = df["Close"] - df["Close"].shift(window)
    return df

def add_macd(df: pd.DataFrame) -> pd.DataFrame:
    ema12 = df["Close"].ewm(span=12, adjust=False).mean()
    ema26 = df["Close"].ewm(span=26, adjust=False).mean()
    df["MACD"] = ema12 - ema26
    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    return df

def add_volume_features(df: pd.DataFrame) -> pd.DataFrame:
    df["Volume_Change"] = df["Volume"].pct_change()
    df["Volume_Zscore"] = (df["Volume"] - df["Volume"].rolling(20).mean()) / (df["Volume"].rolling(20).std() + 1e-10)
    return df

def compute_features(df: pd.DataFrame) -> pd.DataFrame:
    df = add_returns(df)
    df = add_moving_averages(df)
    df = add_volatility(df)
    df = add_rolling_extremes(df)
    df = add_rsi(df)
    df = add_bollinger_bands(df)
    df = add_momentum(df)
    df = add_macd(df)
    df = add_volume_features(df)
    return df

def compute_all_ticker_features(df: pd.DataFrame) -> pd.DataFrame:
    df = flatten_columns(df)
    tickers = sorted(set(col.split("_")[0] for col in df.columns if "_" in col))
    features_by_ticker = []
    for ticker in tickers:
        ticker_cols = [col for col in df.columns if col.startswith(f"{ticker}_")]
        df_ticker = df[ticker_cols].copy()
        df_ticker.columns = [col[len(ticker)+1:] for col in ticker_cols]
        feats = compute_features(df_ticker)
        feats = feats.add_prefix(f"{ticker}_")
        features_by_ticker.append(feats)
    if features_by_ticker:
        features_df = pd.concat(features_by_ticker, axis=1)
    else:
        features_df = compute_features(df)
    return features_df

if __name__ == "__main__":
    for fname in os.listdir(CLEANED_DIR):
        if fname.endswith(".parquet"):
            input_path = os.path.join(CLEANED_DIR, fname)
            output_path = os.path.join(FEATURES_DIR, fname)
            df = pd.read_parquet(input_path)
            feats_df = compute_all_ticker_features(df)
            feats_df.to_parquet(output_path)
            print(f"Engineered features saved to {output_path}")
