import pandas as pd
import numpy as np
from src.utils.pandas_helpers import flatten_columns
from src.utils.duckdb_helpers import read_table, write_table

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
    # Long-term realized annualized
    df["Volatility_126"] = df["Return_1d"].rolling(126).std() * np.sqrt(252)
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
    df["BB_bandwidth"] = (df["BB_upper"] - df["BB_lower"]) / (sma + 1e-10)
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

def add_cross_sectional_features(feats: pd.DataFrame, date_colname: str = "Date") -> pd.DataFrame:
    if date_colname not in feats.columns:
        return feats
    # Create cross-sectional z-score and rank for each numeric feature per date
    num_feats = feats.select_dtypes(include=[np.number]).columns
    out = feats.copy()
    for feat in num_feats:
        # If all rows NaN, skip
        if out[feat].notnull().sum() < 2:
            continue
        zname = f"{feat}_zscore"
        rankname = f"{feat}_rank"
        out[zname] = out.groupby(date_colname)[feat].transform(lambda x: (x - x.mean()) / (x.std(ddof=0) + 1e-8))
        out[rankname] = out.groupby(date_colname)[feat].rank(pct=True)
    return out

def add_advanced_features(df: pd.DataFrame) -> pd.DataFrame:
    # Example: Moving average of returns
    df["MeanReturn21_5"] = df["Return_5d"].rolling(21).mean()
    df["MeanReturn21_1"] = df["Return_1d"].rolling(21).mean()
    # Rolling correlation with market: placeholder for extension with market col
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
    df = add_advanced_features(df)
    return df

def compute_all_ticker_features(df: pd.DataFrame) -> pd.DataFrame:
    df = flatten_columns(df)
    tickers = sorted(set(col.split("_")[0] for col in df.columns if "_" in col))
    features_by_ticker = []
    date_col = df["Date"] if "Date" in df.columns else None
    for ticker in tickers:
        ticker_cols = [col for col in df.columns if col.startswith(f"{ticker}_")]
        df_ticker = df[ticker_cols].copy()
        df_ticker.columns = [col[len(ticker)+1:] for col in ticker_cols]
        feats = compute_features(df_ticker)
        if date_col is not None:
            feats = feats.copy()
            feats["Date"] = date_col.values
        # Add cross-sectional features (per date) for this ticker
        feats = add_cross_sectional_features(feats, date_colname="Date")
        feats = feats.add_prefix(f"{ticker}_")
        features_by_ticker.append(feats)
    if features_by_ticker:
        features_df = features_by_ticker[0]
        for df_other in features_by_ticker[1:]:
            features_df = features_df.merge(df_other, on=f"{tickers[0]}_Date", how="outer")
        # Fix columns: ensure only one Date in leftmost
        date_col_name = f"{tickers[0]}_Date"
        cols = list(features_df.columns)
        if date_col_name in cols:
            cols = [date_col_name] + [c for c in cols if c != date_col_name]
            features_df = features_df[cols]
        features_df = features_df.rename(columns={date_col_name: "Date"})
    else:
        expected = {"Open", "High", "Low", "Close", "Volume"}
        if expected.issubset(set(df.columns)):
            features_df = compute_features(df)
            if "Date" in df.columns:
                features_df.insert(0, "Date", df["Date"].values)
            features_df = add_cross_sectional_features(features_df, date_colname="Date")
        else:
            raise ValueError("No ticker columns found, and single-ticker expected columns not in dataframe.")
    return features_df

if __name__ == "__main__":
    df = read_table("cleaned")
    feats_df = compute_all_ticker_features(df)
    write_table(feats_df, "features")
    print("Engineered features written to DuckDB table 'features'")
