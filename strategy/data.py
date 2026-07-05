"""strategy/data.py — load and clean price CSVs (Dukascopy or generic OHLC)."""
from __future__ import annotations
import pandas as pd


def load_csv(path: str, resample_daily: bool = True) -> pd.DataFrame:
    """
    Accepts Dukascopy (`timestamp` in ms) or generic (`datetime`/`date`) OHLC CSVs.
    Returns a clean daily OHLC frame with a `datetime` column.
    """
    df = pd.read_csv(path)
    cols = {c.lower(): c for c in df.columns}
    if "timestamp" in cols:
        df["datetime"] = pd.to_datetime(df[cols["timestamp"]], unit="ms", utc=True)
    elif "datetime" in cols:
        df["datetime"] = pd.to_datetime(df[cols["datetime"]], utc=True)
    elif "date" in cols:
        df["datetime"] = pd.to_datetime(df[cols["date"]], utc=True)
    else:
        raise ValueError("CSV needs a 'timestamp', 'datetime', or 'date' column.")
    df["datetime"] = df["datetime"].dt.tz_localize(None)
    df = df.rename(columns={
        cols.get("open", "open"): "open", cols.get("high", "high"): "high",
        cols.get("low", "low"): "low", cols.get("close", "close"): "close",
    })
    df = df.sort_values("datetime").drop_duplicates("datetime")
    # drop non-trading filler bars (flat high==low==close)
    df = df[~((df["high"] == df["low"]) & (df["low"] == df["close"]))]
    out = df[["datetime", "open", "high", "low", "close"]].reset_index(drop=True)
    if resample_daily:
        d = (out.set_index("datetime").resample("1D")
             .agg(open=("open", "first"), high=("high", "max"),
                  low=("low", "min"), close=("close", "last")).dropna().reset_index())
        return d
    return out


def validate(df: pd.DataFrame) -> dict:
    bad = ((df["high"] < df["low"]) | (df["close"] > df["high"] + 0.01) |
           (df["close"] < df["low"] - 0.01)).sum()
    return dict(rows=len(df), start=str(df["datetime"].min().date()),
                end=str(df["datetime"].max().date()),
                nulls=int(df[["open", "high", "low", "close"]].isna().sum().sum()),
                bad_ohlc=int(bad))
