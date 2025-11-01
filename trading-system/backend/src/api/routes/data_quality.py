from fastapi import APIRouter
from typing import List, Dict, Any
import duckdb
import pandas as pd
import numpy as np
from src.utils.duckdb_helpers import get_con

router = APIRouter()

@router.get("/data/quality")
def get_data_quality():
    with get_con() as con:
        df = con.execute("SELECT * FROM cleaned").df()

    # Identify tickers & features
    cols = list(df.columns)
    features = [c for c in cols if c != "Date" and "_" in c]
    # Group by ticker
    ticker_info = {}
    for feat in features:
        try:
            ticker, field = feat.split("_", 1)
        except:
            continue
        if ticker not in ticker_info:
            ticker_info[ticker] = {}
        ser = df[feat]
        missing = ser.isnull().mean()
        last_valid = df.loc[ser.notnull(), "Date"].max() if ser.notnull().any() else None
        outliers = 0
        if pd.api.types.is_numeric_dtype(ser):
            z = np.abs((ser - ser.mean()) / (ser.std(ddof=0) + 1e-12))
            outliers = int((z > 5).sum())
        ticker_info[ticker][field] = {
            "percent_missing": round(float(missing) * 100, 2),
            "last_valid_date": str(last_valid) if last_valid is not None else None,
            "outlier_count": int(outliers)
        }

    # Find staleness for each ticker (latest overall date in cleaned data)
    last_date = df["Date"].max() if "Date" in df else None
    ticker_last_date = {
        ticker: max(
            (info[f]["last_valid_date"] for f in info if info[f]["last_valid_date"]),
            default=None
        )
        for ticker, info in ticker_info.items()
    }

    # Warning evaluation
    alerts = []
    for ticker, last in ticker_last_date.items():
        if last is None or (last_date and last < str(last_date)):
            alerts.append(f"Data for {ticker} is stale. Last value: {last}. Cleaned table last: {last_date}")

    # Any high missingness?
    for ticker, info in ticker_info.items():
        for feat, vals in info.items():
            if vals["percent_missing"] > 10:
                alerts.append(f"High missingness for {ticker} {feat}: {vals['percent_missing']}%")
            if vals["outlier_count"] > 10:
                alerts.append(f"Many outliers for {ticker} {feat}: {vals['outlier_count']}")
    
    return {
        "last_date": str(last_date),
        "data": ticker_info,
        "last_per_ticker": ticker_last_date,
        "alerts": alerts
    }
