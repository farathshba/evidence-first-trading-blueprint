# US Test 5.2 — Pre-Registration & Run Procedure (17 Oct 2026)

Restates the frozen registration from docs/US-TIER5-TEST-PLAN.md (16 Oct) verbatim.
No new parameters, no bar changes. One run, no gate-widening (4.2 precedent).

## Hypothesis

On the SAME 4.5 scan (consolidation near 52w-high, building volume), the
breakout entry trigger (fresh daily close > 252-day high) UNDERPERFORMS the
nearness entry. Prediction: fails the beat-baseline bar. Either result is
informative — PASS would confirm the 3.1b breakout tombstone on US data;
a beat would be a genuine surprise requiring QC confirmation.

## Rule (frozen)

Identical to 4.5 except the entry trigger:
- Universe: US$1–10, 20d dollar-volume >= $3M, common equities, >= 260
  trading days history.
- Gates: SPY > SMA200 AND breadth >= 0.50 (candidates above SMA200).
- Selection: long-only, top-10 by nearness-to-52w-high, monthly rebalance —
  UNCHANGED for candidate ranking.
- ENTRY DIFFERENCE: a candidate is entered only on a daily close strictly
  above its 252-day high (fresh breakout) instead of entering on nearness
  rank alone. Positions failing the breakout condition are not taken that
  month (no substitute fill).
- Hold/rebalance logic unchanged from 4.5.
- Costs: 0.35%/side.

## Frozen bars (registered 16 Oct, read ONCE after the run, no reruns)

1. EV/trade net @ 0.35%/side > +0.60%
2. Positive years >= 6/13
3. Trades >= 150 (else VOID)
4. KEY BAR: EV/trade must beat the unconditioned 4.5 baseline EV on the
   SAME window by >= +0.30pp — else no adoption.

## Apparatus

Mac lab, Yahoo daily data (screening-grade caveat noted). Single run.

QC follow-up: NOT required if FAIL (tombstone stands — cheap negative).
If Stage 1 PASSES, treat the Yahoo number with elevated suspicion (5.1
lesson: Stage 1 edge inverted on survivorship-free data) before spending
QC compute; QC confirmation is REQUIRED before any adoption regardless.

## Sanity expectations (non-bar diagnostics, do not gate)

- Trade count will likely be LOWER than 4.5 (breakout condition is
  restrictive vs nearness). If trades < 150 -> VOID as registered.
- 5.1 lesson applied: if Run A-style calibration vs any prior 4.5 rerun
  diverges, note it but bars are read as-is on the single run.

## Verdict options: PASS / FAIL / VOID
