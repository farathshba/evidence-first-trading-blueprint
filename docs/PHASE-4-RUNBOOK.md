# PHASE 4 — OPERATIONAL RUNBOOK (champion: 2.3 breadth-gate momentum)

## 1. Monthly rebalance procedure
Run on the first trading day of each month, after SGX close (17:30 SGT), act next morning.

1. Refresh data_v3_clean (same pipeline as backtest — no ad-hoc data sources).
2. Compute signals exactly as scripts/momentum_backtest.py does:
   - Universe filters: price >= S$1, 20d dollar volume >= S$1M
   - Rank by 126d momentum; target top 10
   - BREADTH GATE (champion 2.3): trade only if >= 50% of universe books are above their SMA200; if gate fails, go flat and stand aside
   - REGIME GATE: ES3 > SMA200 required for entries
3. Diff target vs current holdings. Sells first, then buys (frees capital).
4. Whole-share floor sizing: stake = cash / max(new buys, 1) — same formula as the audited backtest (Test 1.3).

## 2. Order execution
- Time window: 09:30–11:00 SGT (avoid 09:00 open auction churn and lunch thinning; rebalance day has no urgency — monthly horizon).
- Order type: limit at bid (buys) / ask (sells) at time of placement; walk the price by one tick if unfilled after 15 min; max 3 walks, then reassess next day. Never market orders on SGX small caps.
- One name per 10-minute slot to avoid self-attention in thin books.

## 3. Fill-quality log (per order)
Log in results/fills_log.csv: date, ticker, side, intended px, fill px, size, realized cost % vs 0.45% assumption, notes.
RAMP CRITERION (from sizing decision): mean realized cost/side within [0.20%, 0.70%] over the first 3 months. Outside that band = live behavior deviates from documented = investigate before ramping.

## 4. Monthly monitoring (vs documented behavior)
- Portfolio drawdown vs -31% documented maxDD: within range = normal; a NEW low beyond -31% does not auto-kill (backtest can understate) but triggers a written review.
- Win rate: documented 41.7%; below ~30% over 20+ trades = investigate.
- Positive months: 6/10 years positive means red months are EXPECTED — a red month is never itself a signal.
- Tracking: portfolio return vs backtest replay of the same period (re-run champion config on actuals each quarter).

## 5. Kill criteria (pre-registered)
System is killed — capital withdrawn, post-mortem written — on any of:
1. STRUCTURAL: fill costs persistently > 0.70%/side over 20+ orders (the friction wall moves; the edge dies with it).
2. LOGICAL: strategy definition cannot be executed as backtested (data feed dies, universe rules unenforceable, broker constraint).
3. BEHAVIORAL: live tracking error vs backtest replay > 10 percentage points over a full quarter (system is not the system we tested).
NOT kill criteria: losing months, losing quarters, drawdown within documented range, media narratives, boredom.

## 6. Records discipline
Every rebalance: commit the signal diff and fills to the repo the same day. The live record is the continuation of the test plan — an evidence-first system is run the way it was built.
