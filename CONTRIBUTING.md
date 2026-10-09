# Contributing to the Evidence-First Trading Blueprint

This repo runs a live trading system. Its core asset is not the code — it is the
evidence trail. Contributions are welcome, but they follow the discipline, not
the vibe.

## The constitution (non-negotiable)

1. **Pre-register before you run.** Every backtest gets its rules, costs, and
   pass/fail bars written down BEFORE results exist. Post-hoc bars don't count.
2. **Two-stage guardrail for ANY rule change:**
   - Stage 1 (full period): EV > +0.6%/trade after costs AND positive in >= 6/10 years
   - Stage 2 (walk-forward): freeze in-sample 2016-21, test untouched 2022-26 —
     OOS EV >= +0.6% AND positive in >= 4/5 years
3. **Costs are always modeled** (0.45%/side default, 0.60% for stress). No
   zero-friction results are accepted. See "The friction wall" in the README.
4. **Failed strategies get tombstones, not retries.** If a class failed with an
   adequate sample, it is dead. Read the README before proposing anything.
5. **Verdicts live in docs/TIER-3-TEST-PLAN.md and issue #3.** Log your result
   the same day you get it, with the anatomy (year-by-year, win rate, sample
   size), not just the verdict.

## How to propose a strategy or rule change

1. Open an issue first. State: the hypothesis, the mechanism (WHY should this
   work on SGX?), the exact spec (entry/exit/universe/costs), and the bars.
2. Wait for spec agreement before coding. This is deliberate — the repo's
   biggest failures came from specs that made strategies untestable.
3. Write the backtest as a standalone script (see scripts/ for the pattern:
   argparse flags for every parameter, --entry-start/--entry-end for
   walk-forward, trades CSV to results/).
4. Run full period + IS + OOS. Report ALL THREE, including the ugly ones.
5. Log the verdict honestly. Negative results with adequate samples are the
   repo's most valuable commits.

## What NOT to do

- Don't propose re-tests of tombstoned classes (breakout, mean reversion) with
  the same mechanism — the tombstones are the evidence.
- Don't tune parameters on the OOS window. Ever.
- Don't report EV without sample size and year-by-year breakdown.
- Don't touch the live champion config without the full two-stage guardrail.
- Don't submit claimed win rates from elsewhere as evidence. Everything gets
  re-tested here, on this universe, with these costs.

## Data

`data_v3_clean/` — ~395 SGX daily books (Yahoo-sourced, dividend-adjusted via
adjclose). One CSV per ticker: date,open,high,low,close,adj close,volume.
Refresh policy and universe filters are in scripts/momentum_backtest.py.

## Questions?

Read docs/TIER-3-TEST-PLAN.md top to bottom — it documents every decision and
every refutation. Then open an issue.
