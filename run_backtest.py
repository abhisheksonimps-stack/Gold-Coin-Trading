#!/usr/bin/env python3
"""
run_backtest.py — backtest either strategy on a CSV.

Usage:
    python run_backtest.py gold data/xauusd-d1.csv
    python run_backtest.py btc  data/btcusd-d1.csv
"""
import argparse, pandas as pd
from strategy.data import load_csv, validate


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("strategy", choices=["gold", "btc"])
    ap.add_argument("csv")
    ap.add_argument("--no-conviction", action="store_true")
    a = ap.parse_args()
    df = load_csv(a.csv); v = validate(df)
    print(f"Data: {v['rows']} bars {v['start']} -> {v['end']}\n")

    if a.strategy == "gold":
        from strategy.core import backtest, stats
        t = backtest(df, conviction=not a.no_conviction); s = stats(t)
        print("GOLD (regime-adaptive)")
        for k, val in s.items():
            print(f"  {k:16s}: {val:.3f}" if isinstance(val, float) else f"  {k:16s}: {val}")
    else:
        from strategy.btc import backtest
        s = backtest(df)
        print("BTC (majority-trend long/cash)")
        print(f"  CAGR           : {s['cagr']*100:.1f}%")
        print(f"  Sharpe         : {s['sharpe']:.2f}")
        print(f"  Max drawdown   : {s['max_drawdown']*100:.1f}%")
        print(f"  Time in market : {s['time_in_market']*100:.0f}%")
        print(f"  Final multiple : {s['final_multiple']:.0f}x")


if __name__ == "__main__":
    main()
