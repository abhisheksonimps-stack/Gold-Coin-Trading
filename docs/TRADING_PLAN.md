# Mera Gold Trading Plan
### Regime-adaptive strategy | Capital ₹50,000 | 1% risk per trade

> Yeh plan ek data-validated strategy par bana hai (2012–2026, out-of-sample + forward tested).
> Yeh financial advice nahi — mera apna trading framework hai. Sirf woh paisa lagaunga jo poori tarah kho sakta hoon.

---

## 0. Sabse pehle — reality jise main accept karta hoon

- Yeh strategy **~7 trades/saal** deti hai. Zyadatar din **koi trade nahi**. Yeh sahi hai, boredom bug nahi.
- Backtest par ~+3–5R/saal, ~59% win rate, ~40% trades HAARTI hain. **4–5 consecutive losses normal hain.**
- Backtest ≠ live. Real slippage + emotions se mera actual return backtest se **kam** hoga.
- Pehle 6–12 mahine ka goal **PROFIT nahi — DISCIPLINE hai.** Kya main plan follow kar paata hoon?
- Yeh mera FD/emergency/rent ka paisa NAHI hai. Yeh alag "risk capital" hai.

---

## 1. Account & instrument

| Item | Value |
|---|---|
| Trading capital | ₹50,000 (risk capital, alag) |
| Instrument | MCX **Gold Petal** (1 gram lot) — chhota, isliye chhota risk |
| Timeframe | **Daily** candles (signal daily close par) |
| Risk per trade | **1%** = ₹500 (≈ 1 Petal lot @ 1.5×ATR stop) |
| Position size | Normal: **1 lot** · Strong trend (conviction): **max 2 lots** |

> **₹20-30k par mat shuru karo** proper 1% ke liye — 1 lot hi 1.4–2.1% risk ho jaata hai.
> Ya to ₹50k tak save karo, ya tab tak **paper trade** karo.

---

## 2. Entry rules (roz market close ke baad check)

**Step 1 — Regime pehchano (ADX-14):**
- ADX ≥ 20 → **TREND regime** → breakout playbook
- ADX < 20 → **RANGE regime** → mean-reversion playbook

**Step 2 — TREND regime (breakout):**
- LONG: price 60-din ke high ke upar band ho **AUR +DI > −DI**
- SHORT: price 60-din ke low ke neeche band ho **AUR −DI > +DI**
- **Confirmation ZAROORI:** agle din bhi close usi taraf ho (fakeout-trap se bachne ke liye). Ek hi close = WAIT karo.

**Step 3 — RANGE regime (mean-reversion):**
- LONG: RSI-14 < 25 (oversold)
- SHORT: RSI-14 > 75 (overbought)

**Step 4 — Volatility filter (SABSE ZAROORI):**
- Agar ATR/price apne pichhle history ke **top 15%** mein hai → **TRADE MAT KARO**, chahe signal ho.
- Yeh whipsaw/news-spike se bachaata hai. Isne backtest mein drawdown 40% kam kiya.

**Step 5 — Conviction sizing (optional, aggressive):**
- Sirf tab 2 lots: TREND + ADX > 35 + price 50-EMA aur 200-EMA ke sahi taraf aligned.
- Fake trend guard: agar EMAs align nahi → 1 lot hi.

---

## 3. Exit rules (entry ke saath hi set karo — negotiable nahi)

| | Value |
|---|---|
| Stop loss | Entry se **1.5 × ATR** door (yeh = 1R) |
| Take profit | Entry se **1.5 × ATR × 1.5 = 2.25 × ATR** door (yeh = 1.5R) |
| Entry timing | Signal wale din ke agle din ke **open** par (market order) |

- Stop aur target **entry se pehle** decide, order ke saath lagao. **Kabhi stop peeche mat khiskaao** trade ke against.
- Target hit → nikal jao. Stop hit → nikal jao. **Beech mein manually interfere mat karo.**

---

## 4. Risk circuit-breakers (ye mujhe blow-up se bachaayenge)

1. **Per trade:** max 1% (₹500). Conviction par max 2% (₹1,000). Kabhi zyada nahi.
2. **Ek waqt mein:** max 2 open positions. Total open risk ≤ 3% account.
3. **Monthly stop:** agar mahine mein account −6% gir jaye → **us mahine trading BAND.** Review karo, next month se.
4. **Losing streak:** 5 consecutive losses → 1 hafta break, journal review. (Streak normal hai, par break emotions reset karta hai.)
5. **No revenge trading:** loss ke baad size double karke "wapas paane" ki koshish = account killer. Kabhi nahi.
6. **No news gambling:** NFP/CPI/Fed ke din naya trade nahi (vol filter waise bhi rok dega).

---

## 5. Daily routine (~15 min/din)

1. Market close ke baad: ADX, DI, RSI, 60-din high/low, ATR, volatility rank check karo (ya signal script chalao).
2. Verdict nikaalo: **ENTER / WAIT / ARM / STAND ASIDE.**
3. ENTER ho to: entry, stop, target, lot size likho → order lagao.
4. **Journal mein entry karo** (neeche template).
5. Screen band karo. Bar-bar mat dekho. Daily strategy hai, intraday nahi.

---

## 6. Trading journal (har trade — yeh meri #1 seekhne ki tool hai)

| Date | Signal (regime/dir) | Entry | Stop | Target | Lots | Result (R) | Maine plan follow kiya? (Y/N) | Note |
|---|---|---|---|---|---|---|---|---|

> Sabse important column: **"plan follow kiya?"** — profit/loss se zyada yeh matter karta hai.
> Loss with discipline = achha trade. Profit with rule-break = bura trade (luck tha).

---

## 7. Review schedule

- **Weekly:** journal padho — kya main rules follow kar raha hoon?
- **Monthly:** actual results vs backtest expectation. Win rate, avg R, drawdown.
- **Quarterly:** kya edge zinda hai? Kya main psychologically consistent hoon? Size badhaana hai ya nahi?

**Size sirf tab badhao jab:** 6+ mahine consistent discipline + actual results backtest ke aas-paas.

---

## 8. Realistic expectations (jhoot nahi)

- ₹50,000 @ 1% risk → backtest par **~₹1,500–2,500/saal** (3–5%). **FD se kam.**
- Yeh chhoti income hai — kyunki capital chhota hai. Income = return% × capital.
- **Full-time career = chhota edge + bada capital + multiple strategies + years.** Yeh phase 1 hai.
- Agla step (baad mein): 2-3 aur validated strategies banao (alag markets/styles) → diversify → tab income smooth hoti hai.

---

## 9. Kab ruk jaana / rethink karna

- 6 mahine baad agar main **rules follow nahi kar pa raha** (journal mein bahut "N") → problem strategy nahi, discipline hai. Woh fix karo.
- Agar actual results backtest se **bahut** kharaab (jaise expR negative rehta 30+ trades tak) → edge shayad live mein kaam nahi kar raha, ya execution/cost issue hai. Rethink.
- Agar trading tension/neend/paisa-pressure de rahi hai → capital kam karo ya break lo. Health > trading.

---

### Ek line jo main roz yaad rakhunga:
> "Mera kaam paisa kamana nahi — mera kaam plan follow karna hai. Paisa uska by-product hai."
