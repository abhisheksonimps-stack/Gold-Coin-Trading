# Multi-Strategy Trading System — Gold + BTC

Two independently-validated daily strategies with automated signals to Telegram, running free on GitHub Actions.

> ⚠️ **Not financial advice.** Research/education tool. Trading involves risk of loss. It signals; **you decide and execute.** No auto-execution by design.

---

## The two strategies

### 1. Gold (XAU/USD) — regime-adaptive, stop/target
- ADX≥20 → breakout (2-close confirmation); ADX<20 → RSI mean-reversion
- Volatility filter (skip top 15% vol) + conviction 2× sizing on strong EMA-aligned trends
- Stop 1.5×ATR, target 1.5R, ~7 trades/yr
- **Validated:** +0.48R/trade, PF ~2.2, ~59% win, out-of-sample + forward + flip tested
- Signals: **ENTER / WAIT / ARM / STAND ASIDE**

### 2. BTC (Bitcoin) — majority-trend, long/cash
- Three signals: close>150-SMA · MACD(8,21)>signal · 30-day momentum>0
- LONG when ≥2 of 3 bullish, else CASH. Long-only, no leverage.
- **Validated:** full-sample Sharpe ~2.0, maxDD ~−55% (vs buy&hold −83%); out-of-sample (2023-26) DD −31% vs −53%. **Robust to parameter changes** (not overfit — unlike a single 5/100 crossover).
- Signals: **HOLD BTC / MOVE TO CASH** (+ optional 2.5×ATR emergency stop)

**Why two?** Gold and BTC are largely uncorrelated → genuine diversification. Each edge is small but real; the big historical CAGR on BTC rides its non-repeatable run — the durable value is **drawdown reduction + Sharpe**, not the headline return.

---

## Honest limits (read these)
- Real returns will be lower than backtest (slippage, emotions).
- BTC drawdown is still ~−55% — brutal. Size small; consider 50–70% allocation even when long.
- Edges are market-specific: this gold model did NOT transfer to silver/oil/equities; most "amazing" patterns (breakout/triangle/dip-buy) FAILED out-of-sample. These two survived rigorous testing — that's the whole point.
- One out-of-sample split is not walk-forward. Keep validating live.

---

## Setup (~15 min)
1. Push this repo to your GitHub.
2. Telegram: message **@BotFather** → `/newbot` → copy token. Get your chat id via `https://api.telegram.org/bot<TOKEN>/getUpdates`.
3. Repo → **Settings → Secrets → Actions**: add `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`.
4. **Actions** tab → enable → **Run workflow** to test. You'll get both signals each run.

## Run locally
```bash
pip install -r requirements.txt
# fetch: npx dukascopy-node -i xauusd -from 2012-01-01 -to 2026-07-06 -t d1 -f csv
python run_backtest.py gold data/xauusd-d1.csv
python run_backtest.py btc  data/btcusd-d1.csv
python daily.py gold data/xauusd-d1.csv --risk 500 --always
python daily.py btc  data/btcusd-d1.csv --always
```
> Note: Dukascopy's BTC daily is gappy. For BTC use continuous data (investing.com / Binance / CryptoDataDownload BTCUSDT 1d) and save as `data/btcusd-d1.csv`.

## Structure
```
strategy/core.py   # gold regime-adaptive engine
strategy/btc.py    # BTC majority-trend model
strategy/data.py   # CSV loader (Dukascopy + generic)
run_backtest.py    # backtest either strategy
run_signal.py      # gold today's signal
daily.py           # orchestrator: gold|btc -> Telegram
notify/telegram.py # Telegram sender
docs/TRADING_PLAN.md
.github/workflows/  # daily automation (both strategies)
```

## Roadmap
- [ ] Trade journal auto-logging (append signals to CSV)
- [ ] Weekly performance summary to Telegram
- [ ] Portfolio view: combined gold+BTC equity, correlation, risk budget
- [ ] Paper-trading tracker: live signals vs backtest expectation
