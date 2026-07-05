#!/usr/bin/env python3
"""
daily.py — automation entry point (multi-strategy).
Runs the requested strategy on its CSV and sends the signal to Telegram.

Usage:
    python daily.py gold data/xauusd-d1.csv --risk 500 --always
    python daily.py btc  data/btcusd-d1.csv --always
"""
import argparse
from strategy.data import load_csv
from notify.telegram import send


# ---------------- GOLD (regime-adaptive, stop/target trade) ----------------
def gold_message(csv, risk, always):
    from run_signal import build_plan
    df = load_csv(csv)
    if len(df) < 220:
        send("⚠️ Gold: not enough data bars for today's signal.")
        return None
    p = build_plan(df, risk)
    emoji = {"ENTER": "\U0001F7E2", "WAIT 1 DAY": "\U0001F7E1",
             "ARM": "\U0001F535", "STAND ASIDE": "\u26AA"}[p["action"]]
    L = [f"<b>{emoji} GOLD SIGNAL — {p['date']}</b>",
         f"Price <b>{p['price']:,.0f}</b> · ATR {p['atr']:,.0f} · ADX {p['adx']:.0f} · RSI {p['rsi']:.0f}",
         f"Regime: <b>{p['regime']}</b> · 60d {p['lo']:,.0f}–{p['hi']:,.0f}",
         f"Vol rank: {p['volpct']*100:.0f}%" + (" ⚠️ HIGH" if p["high_vol"] else ""), "———"]
    verdict = {"ENTER": "✅ <b>ENTER TODAY</b>", "WAIT 1 DAY": "⏳ <b>WAIT</b> (confirm tomorrow)",
               "ARM": "🎯 <b>ARM</b> (set alert)", "STAND ASIDE": "🚫 <b>STAND ASIDE</b>"}[p["action"]]
    L.append(verdict)
    if p.get("entry") is not None and p["action"] != "STAND ASIDE":
        L += [f"Direction: <b>{p['direction']}</b> · Size: {p['size']}",
              f"Entry: <b>{p['entry']:,.0f}</b>",
              f"Stop: {p['stop']:,.0f} · Target: {p['target']:,.0f} (1.5R)"]
        if "position_units" in p:
            L.append(f"Position: {p['position_units']:.2f} units")
    L += [f"<i>{p['reason']}</i>", "———", "Not advice · follow your plan"]
    actionable = p["action"] in ("ENTER", "WAIT 1 DAY")
    return "\n".join(L), actionable


# ---------------- BTC (majority-trend long/cash model) ----------------
def btc_message(csv, always):
    from strategy.btc import build_plan
    df = load_csv(csv)
    if len(df) < 200:
        send("⚠️ BTC: not enough data bars for today's signal.")
        return None
    p = build_plan(df)
    hold = p["action"] == "HOLD BTC"
    emoji = "\U0001F7E2" if hold else "\u26AA"
    chk = lambda b: "✅" if b else "❌"
    L = [f"<b>{emoji} BTC SIGNAL — {p['date']}</b>",
         f"Price <b>{p['price']:,.0f}</b> · ATR {p['atr']:,.0f}",
         f"Signals ({p['score']}/3 bullish):",
         f"  {chk(p['s_trend'])} Trend: close vs 150-SMA ({p['sma150']:,.0f})",
         f"  {chk(p['s_macd'])} MACD(8,21) vs signal",
         f"  {chk(p['s_mom'])} 30-day momentum ({p['mom30']*100:+.1f}%)", "———",
         ("🟢 <b>HOLD BTC</b> (2+ signals bullish)" if hold else "⚪ <b>MOVE TO CASH</b> (fewer than 2 bullish)")]
    if hold and p.get("emergency_stop"):
        L.append(f"Emergency stop idea: ~{p['emergency_stop']:,.0f} (2.5×ATR)")
    L += ["———", "Long/cash trend model · no leverage · not advice"]
    # BTC changes state rarely; treat a state that is HOLD or a fresh flip as actionable
    return "\n".join(L), True  # always relevant (position status), workflow --always controls spam


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("strategy", choices=["gold", "btc"])
    ap.add_argument("csv")
    ap.add_argument("--risk", type=float, default=None)
    ap.add_argument("--always", action="store_true")
    a = ap.parse_args()

    if a.strategy == "gold":
        res = gold_message(a.csv, a.risk, a.always)
    else:
        res = btc_message(a.csv, a.always)
    if res is None:
        return
    msg, actionable = res
    if actionable or a.always:
        send(msg)
    else:
        print(f"No ping ({a.strategy}). Use --always for daily heartbeat.")
    print(msg)


if __name__ == "__main__":
    main()
