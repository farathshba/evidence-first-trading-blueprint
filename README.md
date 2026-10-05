# Evidence-First Trading Blueprint

**Backtest your strategy before you risk a dollar.**

A complete, generic blueprint for building an evidence-first swing trading system:
a local backtest pipeline, an honest validation process, a verdict-driven operating
routine, and the guardrails that keep you from trading on gut feel.

Written after a real experiment: an ATR + volume swing strategy that looked great on
a 3-year window (+14%) and on live trades (49% win rate) **lost 79% over a full
10-year backtest**. The process below is what caught that before it cost real money.

> Educational material only. Not financial advice.

## The 8 phases

**Phase 0 — Adopt the principles.** Rules before money · negative results are wins ·
pre-register your decision rule before testing · the backtest is the authority.

**Phase 1 — Build a local backtest pipeline.** Any local backtester (QuantJourney,
backtrader, vectorbt). Fetch your own universe (~600 tickers, 10y daily OHLCV, one
CSV per ticker) from free sources. Data stays local; a manifest records freshness.

**Phase 2 — Encode the strategy as code.** Example gate: Close > SMA200, Close >
SMA20, volume >= 1.5x its 20-day average, ATR(14) < 15% of price, avg volume >
500K/day. Exit: stop at entry - 2xATR, target at entry + 4xATR. Swap in your own.

**Phase 3 — Validate honestly (the four traps).**
1. Window luck — test full history, not a flattering window (+14% in 3y hid -79% in 10y)
2. Placeholder costs — use percentage costs, then your broker's real fees
3. Cash discipline — cap concurrent positions; size entries (e.g., 2% of NAV)
4. Small-sample live trades — 65 trades at 49% felt like proof; 5,573 trades said 32.9%

**Phase 4 — Read the verdict honestly.** Real case study (anonymized, 10y, ~600 stocks,
5,573 trades, 0.15%/side): net -78.9%, Sharpe -0.99 · win rate 32.9% vs ~40% required ·
stop:target exits 67:33 ≈ the 2:1 a random walk predicts · cheapest price band = 44% of
trades, 28% wins, all the net damage · costs ate 35-40 points. Check your own verdict
for: full-history P&L, Sharpe, win rate vs required, exit ratio vs random-walk,
per-band breakdown, cost attribution, per-year consistency.

**Phase 5 — Pre-register the rule-change decision rule.** Example: a variant passes
only if per-trade EV > 0.6% after costs AND positive net P&L in >= 6 of 10 years.
Then walk-forward validate. If it fails, the rule stays.

**Phase 6 — Build the operating system around the verdict.** Daily: one question to
your AI assistant after the close ("which trade should I make today?") — watchlist
scanned, positions checked vs stops, verdicts citing the evidence. WAIT is the normal
answer (expect 1-2 trades/month). On an ENTER: full briefing, review it yourself,
decide, execute with a bracket order. Report every position change. Weekly 5-minute
review. Standing rules: stops are non-negotiable; convicted bands excluded; liquidity
judged in dollars.

**Phase 7 — Screen the full universe.** `scripts/screen_universe.py` runs your 5
conditions over the entire local universe in seconds. Rules: a stale ENTER is a lead,
not a signal — live-verify before acting; near-misses (4/5) are the watchlist generator.

**Phase 8 — Archive everything.** Private archive repo: `backtests/<run>-<date>/`,
`strategies/`, `positions/`, `docs/`, plus a 10-line sync script. **Keep it private —
it contains your positions.**

## The single most important habit

**No rule changes without a backtest first.** Not after a losing streak, not after a
lucky trade. Run the variant, hold it to the pre-registered bar.

## Repo contents

- README.md — this blueprint
- scripts/screen_universe.py — generic multi-ticker screener (edit the constants)
- LICENSE — MIT
