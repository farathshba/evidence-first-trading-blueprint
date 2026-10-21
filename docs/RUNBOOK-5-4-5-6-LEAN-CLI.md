# RUNBOOK — 5.4-5.6 INTRADAY TESTS, LEAN CLI LOCAL ROUTE (owner decision 21 Oct)

QC free tier is not viable for minute data (~200M points at ~1k pts/s = ~55h/test).
Registered decision: run locally on the Mac. Data must come from ONE of these routes:

## Route A (preferred): QuantConnect data via LEAN CLI
1. `pip install lean` then `lean login` (your QC account)
2. Test download capability:
   `lean data download --dataset "US Equities" --data-type Trade --resolution Minute --ticker AAPL --start 2016-01-01 --end 2026-07-15`
3. If permitted by your plan: script the bulk download for the union of frozen-universe
   tickers (Step 2 of the test script prints this list), convert to CSV, place in
   `data_us_minute/<TICKER>.csv` with columns: datetime,open,high,low,close,volume (ET).
   If the download is blocked on your tier -> Route B or C.

## Route B: IBKR historical 1-minute data (your IBKR account)
- 1-min bars available back to ~2016; pace-limited (~6 months/request).
- A bulk fetcher over the universe list spread over a few days of background downloads.
- Same CSV format into `data_us_minute/`.

## Route C: QC paid tier (cloud, no local setup)
- Reverses the compute wall (paid nodes are not throttled like free).
- Only if A and B both fail.

## Test execution (all three tests)
- `python scripts/us_5_4_orb.py --minute-dir data_us_minute --daily-dir data_us`
- 5.5/5.6 scripts follow the same pattern once 5.4 plumbing is validated.
- ONE registered run each. Bars frozen in arkenstone PR #9. Verdicts from the
  stitched summary lines only.

## Apparatus notes
- Universe: frozen 4.5 daily universe computed from daily data (US$1-10, 20d dvol>=3M,
  >=260 daily rows) — minute data only needed for eligible ticker-days.
- All timestamps US/Eastern (NYSE session 09:30-16:00).
- Costs 0.35%/side applied in ledger. Long-only. Same-day exits. No gates (audits the setup).
