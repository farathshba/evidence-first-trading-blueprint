# Evidence-First Trading Blueprint

**Backtest your trading strategy before you risk a single dollar.**

A beginner-friendly, copy-paste guide to building an evidence-first trading
system on your own computer: download ~10 years of prices for an entire
market (free), screen it daily in 2 seconds, backtest your strategy honestly
in 2 minutes, and build the daily routine and guardrails around whatever the
evidence says.

Written after a real experiment: an ATR + volume swing strategy that looked
great on a 3-year window (+14%) and on live trades (49% win rate) lost 79%
over a full 10-year backtest. This process caught that before it cost real
money. The numbers are real; the method is what you replicate.

Educational material only. Not financial advice.

## What you will build

tickers.txt -> fetch_universe.py -> data/*.csv -> screen_universe.py -> daily ENTER list
                                                -> backtest_swing.py  -> honest verdict

Time: 2-3 hours once, then 5 minutes a day. Cost: zero. Privacy: all local.

## Step 0 - Install the tools (once)

Python:
- macOS: brew install python (or python.org installer). Verify: python3 --version
- Windows: python.org/downloads installer, CHECK "Add python.exe to PATH". Verify: py --version
- Linux: sudo apt install python3 python3-venv python3-pip. Verify: python3 --version

Git: macOS: brew install git - Windows: git-scm.com/download/win - Linux: sudo apt install git

Get the project + environment:

macOS / Linux:
  git clone https://github.com/farathshba/evidence-first-trading-blueprint.git
  cd evidence-first-trading-blueprint
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt

Windows (PowerShell):
  git clone https://github.com/farathshba/evidence-first-trading-blueprint.git
  cd evidence-first-trading-blueprint
  py -m venv .venv
  .venv\Scripts\activate
  py -m pip install -r requirements.txt

Windows notes: if activate is blocked, run
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned once, then retry.
Re-run the activate line at the start of every session.

## Step 1 - Define your market universe

Open tickers.txt in any text editor. One Yahoo Finance ticker per line.
SGX ends in .SI, Indonesia .JK, Australia .AX, US has no suffix.
Lines starting with # are ignored. Aim for 50-600 tickers, one market at a time.

## Step 2 - Download the data (~30 min, unattended)

macOS / Linux: python3 scripts/fetch_universe.py
Windows:       py scripts\fetch_universe.py

Downloads ~10 years of daily OHLCV per ticker into data/ (one CSV each) and
writes data/_manifest.csv. Re-run any time to refresh.
Success looks like: Done: 598 downloaded, 12 failed.

## Step 3 - Screen the whole universe (2 seconds)

macOS / Linux: python3 scripts/screen_universe.py
Windows:       py scripts\screen_universe.py

Judges every stock against 5 conditions: price > SMA200 (trend), price >
SMA20 (momentum), volume >= 1.5x its 20-day average (confirmation), ATR(14)
< 15% of price (volatility filter), avg volume > 500K/day (liquidity).
Prints ENTER (all 5) and NEAR-MISSES (4/5).

Two rules: (1) a stale ENTER is a lead, not a signal - re-verify live before
acting; (2) near-misses are your watchlist. Edit the constants at the top of
the script to match YOUR rules.

## Step 4 - Backtest honestly (~2 minutes)

Simulates the strategy as a portfolio: fixed-fraction sizing (2% of NAV),
capped concurrent positions (60), percentage costs both sides (0.15%/side),
exits at 2xATR stop / 4xATR target (stop checked before target: conservative).

macOS / Linux: python3 scripts/backtest_swing.py
Windows:       py scripts\backtest_swing.py

Flags: --capital 100000 --risk-pct 2.0 --max-positions 60 --cost-pct 0.15
--vol-spike 1.5 --stop-atr 2.0 --tp-atr 4.0

The four traps (each corrupted an early run of the real experiment):
1. Window luck. 3 years showed +14%; 10 years showed -79%. Test full history.
2. Fake costs. Set --cost-pct to your broker's real fee before trusting totals.
3. No cash discipline. Without the cap and fixed sizing, backtests produce
   fantasy results (real run: 12,100% turnover before the fix).
4. Small samples. 65 live trades at 49% felt like proof; 5,573 backtested
   trades said 32.9%. A big honest sample beats a small hopeful one.

Reading the verdict: net return, Sharpe, drawdown, win rate vs required,
stop:target ratio vs the 2:1 a random walk predicts, per-price-band damage
(the real experiment's cheapest band: 44% of trades, 28% wins, ALL the net
loss - convicted, excluded from live trading), per-year consistency.
If the verdict says "no edge" - you just saved the money you would have lost.

## Step 5 - Change a rule the right way

Pre-register the decision rule BEFORE testing. The real bar: a variant
passes only if per-trade EV > 0.6% after costs AND net P&L positive in
>= 6 of 10 years. Then walk-forward validate before going live.
Test variants with flags, e.g.: python3 scripts/backtest_swing.py --vol-spike 2.0
Log every result, including failures.

## Step 6 - Build the operating system around the verdict

- Daily (after close): screen, check positions vs stops/targets, act only on
  fresh verified signals. WAIT is the normal answer (1-2 trades/month).
- On an ENTER: read the news, look at the chart, decide with your own
  judgment. Execute with a bracket order: stop entry - 2xATR, target + 4xATR.
- Standing rules: stops are non-negotiable - exclude convicted price bands -
  judge liquidity in dollars/day, not shares.
- The guardrail: no rule changes without a backtest first. Step 5, always.
- Archive privately: private git repo with backtests/, verdicts, position
  snapshots. Never make it public.

## Troubleshooting

pip not found (macOS/Linux): use python3 -m pip install ...
py not found (Windows): reinstall Python WITH "Add to PATH", reopen PowerShell
PowerShell blocks activate: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
Many tickers fail: Yahoo throttles free requests; wait an hour and re-run
No module named pandas: venv not active - re-run the activate line

## FAQ

My own strategy? Edit constants in screen_universe.py and flags in
backtest_swing.py. The process IS the blueprint; the ATR rules are the example.
Crypto/forex? Anything with a Yahoo ticker (e.g. BTC-USD) works.
Why daily bars? Free, and enough to answer the only question that matters:
does an edge exist at all?

## Repo map

README.md, requirements.txt, tickers.txt (edit me!),
scripts/fetch_universe.py, screen_universe.py, backtest_swing.py, LICENSE (MIT)
