#!/usr/bin/env python3
"""
run_signal.py — today's trade signal from a CSV (regime, levels, ENTER/WAIT/ARM/STAND ASIDE).

Usage:
    python run_signal.py data/xauusd-d1.csv
    python run_signal.py data/xauusd-d1.csv --risk 500
"""
import argparse
import numpy as np
from strategy.data import load_csv
from strategy.core import (add_indicators, LOOKBACK, ADX_TREND_MIN, ADX_STRONG,
                           RSI_LOW, RSI_HIGH, STOP_ATR_MULT, TARGET_RR, VOL_SKIP_PCTILE)


def build_plan(df, risk_dollars=None):
    d = add_indicators(df)
    r, pr = d.iloc[-1], d.iloc[-2]
    px, a, risk = r.close, r.atr, r.atr * STOP_ATR_MULT
    trending = r.adx >= ADX_TREND_MIN
    up = r.pdi > r.mdi
    high_vol = (not np.isnan(r.volpct)) and (r.volpct > VOL_SKIP_PCTILE)
    action, direction, entry, reason = "STAND ASIDE", None, None, ""

    if trending:
        res_t, res_y = d.iloc[-1].hi, d.iloc[-2].hi
        sup_t, sup_y = d.iloc[-1].lo, d.iloc[-2].lo
        if up:
            direction = "LONG"
            confirmed = (pr.close > res_y) and (px > res_y)
            entry = res_y if confirmed else res_t
            if confirmed: action, reason = "ENTER", "trend up + breakout confirmed (2 closes above 60d high)"
            elif px > res_t: action, reason = "WAIT 1 DAY", "closed above 60d high today - need 2nd close to confirm"
            else: action, reason = "ARM", f"trend up; arm long if daily close breaks above {res_t:,.0f}"
        else:
            direction = "SHORT"
            confirmed = (pr.close < sup_y) and (px < sup_y)
            entry = sup_y if confirmed else sup_t
            if confirmed: action, reason = "ENTER", "trend down + breakdown confirmed (2 closes below 60d low)"
            elif px < sup_t: action, reason = "WAIT 1 DAY", "closed below 60d low today - need 2nd close to confirm"
            else: action, reason = "ARM", f"trend down; arm short if daily close breaks below {sup_t:,.0f}"
    else:
        if r.rsi < RSI_LOW: direction, entry, action, reason = "LONG", px, "ENTER", f"range + RSI {r.rsi:.0f} oversold - fade the dip"
        elif r.rsi > RSI_HIGH: direction, entry, action, reason = "SHORT", px, "ENTER", f"range + RSI {r.rsi:.0f} overbought - fade the rip"
        else: reason = f"range-bound, RSI {r.rsi:.0f} neutral - no edge"

    if high_vol and action in ("ENTER", "WAIT 1 DAY"):
        action, reason = "STAND ASIDE", f"volatility in top {(1-VOL_SKIP_PCTILE)*100:.0f}% - whipsaw risk, skip"

    # conviction sizing suggestion
    size = "1x"
    if action == "ENTER" and trending and r.adx > ADX_STRONG:
        aligned = (direction == "LONG" and px > r.ema50 > r.ema200) or (direction == "SHORT" and px < r.ema50 < r.ema200)
        if aligned: size = "2x (strong trend, EMA-aligned)"

    plan = dict(date=str(r.datetime.date()), price=px, atr=a, adx=r.adx, rsi=r.rsi,
                regime="TREND" if trending else "RANGE", high_vol=high_vol, volpct=r.volpct,
                action=action, direction=direction, reason=reason, size=size,
                ema50=r.ema50, ema200=r.ema200, hi=r.hi, lo=r.lo)
    if direction and entry is not None and action != "STAND ASIDE":
        d0 = 1 if direction == "LONG" else -1
        plan.update(entry=entry, stop=entry - d0 * risk, target=entry + d0 * TARGET_RR * risk, risk_per_unit=risk)
        if risk_dollars: plan["position_units"] = risk_dollars / risk
    return plan


def fmt(p):
    L = ["=" * 60, f"  GOLD DAILY SIGNAL   ({p['date']})", "=" * 60,
         f"  Price {p['price']:,.0f}   ATR {p['atr']:,.0f}   ADX {p['adx']:.0f}   RSI {p['rsi']:.0f}",
         f"  Regime: {p['regime']}   60d range: {p['lo']:,.0f} <-> {p['hi']:,.0f}",
         f"  Volatility rank: {p['volpct']*100:.0f}th pctile" + ("  << HIGH, filter active" if p['high_vol'] else ""),
         "-" * 60]
    verdict = {"ENTER": ">>> ENTER TODAY", "WAIT 1 DAY": "... WAIT (confirm tomorrow)",
               "ARM": "~ ARM (set alert)", "STAND ASIDE": "--- STAND ASIDE (no trade)"}[p["action"]]
    L.append(f"  {verdict}")
    if p.get("entry") is not None and p["action"] != "STAND ASIDE":
        L += [f"  Direction : {p['direction']}   |   Size: {p['size']}",
              f"  Entry     : {p['entry']:,.0f}",
              f"  Stop      : {p['stop']:,.0f}   (risk {p['risk_per_unit']:,.0f}/unit = 1R)",
              f"  Target    : {p['target']:,.0f}   (1.5R)"]
        if "position_units" in p: L.append(f"  Size      : {p['position_units']:.2f} units")
    L += [f"  Why       : {p['reason']}", "-" * 60,
          "  Data tool, not financial advice. ~59% win rate, not every trade.", "=" * 60]
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--risk", type=float, default=None)
    a = ap.parse_args()
    df = load_csv(a.csv)
    if len(df) < 220:
        raise SystemExit("Need ~220+ daily bars.")
    print(fmt(build_plan(df, a.risk)))


if __name__ == "__main__":
    main()
