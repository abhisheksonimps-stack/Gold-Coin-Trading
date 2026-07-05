"""
strategy/core.py — the validated gold strategy, one place.

Regime-adaptive:
  ADX >= 20  -> TREND  -> breakout (with 2-close confirmation)
  ADX <  20  -> RANGE  -> mean-reversion (RSI extremes)
Filters:
  - volatility filter: skip entries when ATR/price is in the top 15% historically
  - conviction sizing: 2x size when trend is strong (ADX>35) AND EMA-aligned
Risk:
  - stop = 1.5 x ATR, target = 1.5R, entry at next bar open

Validated 2012–2026 on daily XAU/USD:
  expR ~+0.48R/trade, PF ~2.2, ~59% win, maxDD ~-4R, ~7 trades/yr.
  Edge is GOLD- and DAILY-specific — it did NOT transfer to hourly, equities, silver, or oil.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

# ---- locked parameters (robust to small changes; do not casually re-tune) ----
LOOKBACK = 60
ADX_TREND_MIN = 20
ADX_STRONG = 35
RSI_LOW, RSI_HIGH = 25, 75
STOP_ATR_MULT = 1.5
TARGET_RR = 1.5
VOL_SKIP_PCTILE = 0.85
COST = 0.50  # round-trip in price units


def atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    h, l, c = df["high"], df["low"], df["close"]
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    return tr.rolling(n).mean()


def adx(df: pd.DataFrame, n: int = 14):
    h, l, c = df["high"], df["low"], df["close"]
    up, dn = h.diff(), -l.diff()
    plus = np.where((up > dn) & (up > 0), up, 0.0)
    minus = np.where((dn > up) & (dn > 0), dn, 0.0)
    tr = pd.concat([h - l, (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1).max(axis=1)
    a = tr.rolling(n).mean()
    pdi = 100 * pd.Series(plus, index=df.index).rolling(n).mean() / a
    mdi = 100 * pd.Series(minus, index=df.index).rolling(n).mean() / a
    dx = 100 * (pdi - mdi).abs() / (pdi + mdi).replace(0, np.nan)
    return dx.rolling(n).mean(), pdi, mdi


def rsi(s: pd.Series, n: int = 14) -> pd.Series:
    d = s.diff()
    up = d.clip(lower=0).rolling(n).mean()
    dn = (-d.clip(upper=0)).rolling(n).mean()
    return 100 - 100 / (1 + up / dn.replace(0, np.nan))


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["atr"] = atr(d)
    d["adx"], d["pdi"], d["mdi"] = adx(d)
    d["rsi"] = rsi(d["close"])
    d["ema50"] = d["close"].ewm(span=50, adjust=False).mean()
    d["ema200"] = d["close"].ewm(span=200, adjust=False).mean()
    d["hi"] = d["high"].rolling(LOOKBACK).max().shift(1)
    d["lo"] = d["low"].rolling(LOOKBACK).min().shift(1)
    volr = d["atr"] / d["close"]
    d["volpct"] = volr.expanding(200).apply(lambda s: (s.iloc[-1] > s).mean(), raw=False)
    return d


def backtest(df: pd.DataFrame, conviction: bool = True, cost: float = COST) -> pd.DataFrame:
    """Event-loop backtest. Returns a DataFrame of trades with R multiples."""
    d = add_indicators(df).reset_index(drop=True)
    A = d["atr"].values
    ADX, PDI, MDI = d["adx"].values, d["pdi"].values, d["mdi"].values
    RSI = d["rsi"].values
    E50, E200 = d["ema50"].values, d["ema200"].values
    VP = d["volpct"].values
    O, H, L, C = d["open"].values, d["high"].values, d["low"].values, d["close"].values
    n = len(d)
    trades = []
    i = max(LOOKBACK, 30)
    while i < n - 1:
        if np.isnan(ADX[i]) or not (A[i] > 0):
            i += 1
            continue
        direction, ei, regime = 0, i, "trend"
        if ADX[i] >= ADX_TREND_MIN:
            hi = H[i - LOOKBACK:i].max()
            lo = L[i - LOOKBACK:i].min()
            if C[i] > hi and PDI[i] > MDI[i]:
                direction = 1
                if i + 1 < n and C[i + 1] > hi:
                    ei = i + 1
                else:
                    i += 1
                    continue
            elif C[i] < lo and MDI[i] > PDI[i]:
                direction = -1
                if i + 1 < n and C[i + 1] < lo:
                    ei = i + 1
                else:
                    i += 1
                    continue
        else:
            regime = "range"
            if RSI[i] < RSI_LOW:
                direction = 1
            elif RSI[i] > RSI_HIGH:
                direction = -1
        if direction == 0 or ei + 1 >= n:
            i += 1
            continue
        if not np.isnan(VP[ei]) and VP[ei] > VOL_SKIP_PCTILE:
            i = ei + 1
            continue
        entry = O[ei + 1]
        risk = A[ei] * STOP_ATR_MULT
        strong = regime == "trend" and ADX[ei] > ADX_STRONG
        if strong and conviction:
            strong = (direction > 0 and C[ei] > E50[ei] > E200[ei]) or (
                direction < 0 and C[ei] < E50[ei] < E200[ei]
            )
        size = 2.0 if (strong and conviction) else 1.0
        sl = entry - direction * risk
        tp = entry + direction * TARGET_RR * risk
        ex, j = None, ei + 1
        while j < n:
            if direction > 0:
                hit_sl, hit_tp = L[j] <= sl, H[j] >= tp
            else:
                hit_sl, hit_tp = H[j] >= sl, L[j] <= tp
            if hit_sl:
                ex = sl
            elif hit_tp:
                ex = tp
            if ex is not None:
                break
            j += 1
        if ex is None:
            ex, j = C[-1], n - 1
        R = size * (direction * (ex - entry) - cost) / risk
        trades.append(
            dict(entry_date=d["datetime"].iloc[ei + 1], exit_date=d["datetime"].iloc[j],
                 direction=int(direction), regime=regime, size=size, R=R)
        )
        i = j + 1
    return pd.DataFrame(trades)


def stats(trades: pd.DataFrame) -> dict:
    if len(trades) == 0:
        return dict(n=0)
    R = trades["R"].values
    wins, losses = R[R > 0].sum(), -R[R < 0].sum()
    eq = np.cumsum(np.sort(R)[::-1] * 0 + R)  # keep order
    eq = np.cumsum(trades.sort_values("exit_date")["R"].values)
    mdd = (eq - np.maximum.accumulate(eq)).min()
    return dict(
        n=len(R), win_rate=float((R > 0).mean()), expectancy_R=float(R.mean()),
        profit_factor=float(wins / losses) if losses > 0 else float("inf"),
        total_R=float(R.sum()), max_drawdown_R=float(mdd),
    )
