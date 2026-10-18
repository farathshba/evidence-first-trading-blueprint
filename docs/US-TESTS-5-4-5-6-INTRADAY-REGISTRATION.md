# US Tests 5.4–5.6 — Intraday Folklore Registration (18 Oct 2026)

Separate registration per the Tier 5 plan condition ("bars frozen in a separate
registration before any minute-data run"). Purpose: TOMBSTONE COMPLETION, not
edge-hunting. Prediction (registered): all three FAIL — friction wall (Tier 3
synthesis, SGX; US track record: STREV/PEAD/TOM/breakout/mean-rev all dead or
sub-friction). One run each. Bars read once. No gate-widening (4.2 precedent).

## Feasibility & compute budget (the blocker this registration must clear)

- Apparatus: QuantConnect free tier, AlgoSeek minute data (survivorship-free), 2016-01-01
  to 2026-06-30 (minute-era coverage; NOT identical to 4.5's 2014 start — registered as-is).
- Free-tier limit: 10,000 orders/backtest. Intraday churn blows this: naive ORB on the
  full US$1-10 universe could exceed 50K orders/year.
- REGISTERED COMPUTE CONTROL (frozen now, part of the test — not a tuning knob):
  - Universe per test day: US$1-10, dvol >= US$3M, >= 260d history, tradable that day
    (no halt). Candidates = top 20 by previous-day dollar volume.
  - Max new entries/day: 3; max simultaneous positions: 3.
  - Window SPLIT into two runs per test (2016-2020, 2021-2026), stitched with the same
    boundary-conservative rule as 4.5 (boundary positions uncounted, noted).
  - Per-run order estimate ~7K-15K. If a run hits the 10K cap before its window ends,
    the run is TRUNCATED at the cap and bars are read on the completed subsample
    (registered truncation rule — no re-run with different knobs).
- If truncation leaves < 100 trades: declare VOID-by-feasibility and tombstone as
  "untestable on free tier" (same class as SMC). Registered outcome class.

## Cost model (registered)

0.35%/side primary PLUS mandatory 0.55%/side stress (intraday microcaps gap through
stops; 4.6 lesson — edge = friction delta must be shown). A test that passes at 0.35%
and dies at 0.55% logs FAIL (intraday claims must survive stress).

## Frozen bars (all three tests, read once per test)

1. EV/trade net @ 0.35%/side > +0.30% (intraday scale; the daily-hold 0.60% bar is not
   portable — registered lower, still above friction-adjusted zero)
2. Trades >= 100 (per test, across stitched runs)
3. Positive years >= 5/10
4. Stress: EV @ 0.55%/side > 0%
5. KEY: FAIL here is a CLASS TOMBSTONE for the intraday community-favorite set.
   No re-tests without a new pre-registered hypothesis.

## Test 5.4 — Opening Range Breakout (ORB)
- 15-minute opening range (09:30-09:45 ET). Long entry on first 5-min bar CLOSE above
  range high + 0.1% (no gap-through entries without close confirmation).
- Stop: range low. Exit: stop or session close (time stop). No pyramiding, no shorts.
- Filter: only take breakout if range width <= 2% of price (one value, no sweep).

## Test 5.5 — ACD (A-up pivot, simplified mechanical proxy)
- A-up = opening range high * (1 + A_multiple); A_multiple = 0.5 * previous 5-day
  average daily range / price. Long entry on 5-min close above A-up.
- Stop: A-up - 1x previous 5-day ADR. Exit: stop or session close.
- Filter: skip days with opening gap > 3% vs prior close (registered).

## Test 5.6 — Brooks 2-leg pullback proxy (intraday)
- 20-period EMA on 15-min bars trending (price above EMA20, EMA20 rising >= 6 bars).
  Entry: two consecutive 15-min closes below EMA20, then first close back above.
- Stop: pullback low. Exit: stop, 2x reward target, or session close.
- Registered as PROXY (Brooks' method is discretionary); results speak to the
  mechanical version only. Expected: FAIL.

## Execution order

5.4 -> 5.5 -> 5.6. If 5.4 and 5.5 both FAIL on friction (not trade count), 5.6 may run
on a shorter window (2021-2026) if compute-bound — registered flexibility, declared
BEFORE any run.

## Provenance
Tier 5 plan (PR #30), Tier 3 friction synthesis (issue #3), 4.6 stress lesson (PR #26),
arkenstone research triage (PR #1) where ORB/ACD/Brooks were first parked.
