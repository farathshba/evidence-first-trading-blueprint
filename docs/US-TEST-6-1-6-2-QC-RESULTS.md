# US Test 6.1/6.2 QuantConnect Re-Confirmation: VERDICT
## VOID-BY-DATA-QUALITY (owner decision 25 Nov 2026)

Per docs/US-QC-RECONFIRM-6-1-6-2-SPEC.md (PR #66) the Day-1 Stage-1 PASS of
27 Nov (23 Nov run, PRs #63-#65) required one survivorship-free QC confirmation
run per arm/cost. This document records what happened and closes the gate.

## Run history (all runs, in order)

| Run | Config | Result | Status |
|---|---|---|---|
| R1 attempt 1 | arm A, 0.35%/side | crash (MethodBinding, on_data) | apparatus fixed (PR #68) |
| R1 attempt 2 | arm A, 0.35%/side, QC default ADJUSTED data | trades=6681, EV +38.58% | VOID (wrong data convention) |
| ABEV probe 1 (dump) | probe ABEV | exposed dividend-adjusted prices; 12-year holds | diagnosis |
| R1 attempt 3 | arm A, 0.35%/side, SPLIT_ADJUSTED | trades=5794, EV +32.01%, 12/12 yrs | VOID (see audit) |
| ABEV probe 2 (dump) | probe ABEV, SPLIT_ADJUSTED | engine parity CONFIRMED vs frozen script (real prices, rows match local reference) | engine cleared |
| R1 audit run | arm A, 0.35%/side, TOP-50 winners audit | top-50 = 30.7% of net PnL; winners mix real and provable artifacts | evidence below |

## Why the +32% is not a believable reading

Engine parity was proven: ABEV single-symbol probe (25 Nov) reproduced the
frozen local engine trade-for-trade at real split-adjusted prices (entries
e.g. 2014-10-08 = 6.93 matching the local reference exactly, same duplicate
counts). The inflated EV therefore comes from the wider point-in-time UNIVERSE
combined with data contamination.

TOP-50 winners audit, externally verified 25 Nov:
- REAL megawins (point-in-time universe effect, absent from Day-1's
  present-day snapshot): UMC 2.17 -> 19.07 (Barchart: 19.88 on 2026-08-31);
  SQ 9.20 -> 86.96 (real Block history).
- FANTASY / artifact wins: WW 0.78 -> 16.38 (+1,996%): WeightWatchers filed
  Ch.11 2025, old shares cancelled, Nasdaq delisted (Sept 2025); QC stitched
  the series across the share cancellation. TNK 9.83 -> 88.20: Tsakos renamed
  to TEN; real price ~30-45, QC old series ~2x inflated (ADR/ratio artifact).
  STM exit 51.34, TTMI exit 124.73, VSLR exit 43.08 also exceed verifiable
  real levels.
- Top-50 rows carry 30.7% of total net PnL; EV excl. top-1% is still +21.5%,
  i.e. the fat mid tail shares the same long-hold + artifact character.

Additional structural finding (registered caution, non-binding): the 6.1
mechanics are NOT short-hold in practice. Local frozen-engine check on
Day-1 data: median holding time ~440 days, mean ~877, most winners exit at
window-end. The class behaves as trend-follow-and-hold on $1-10 microcaps,
with edge concentrated in the right tail (Day-1: EV excl. best-100 trades =
+0.31%, below the +0.60% bar).

## Verdict (owner decision 25 Nov 2026)

1. The QC re-confirmation is VOID-BY-DATA-QUALITY: three registered-run
   attempts were each contaminated by QC free-tier data defects (default
   ADJUSTED normalization; factor-file errors QC itself flags; bankrupt-share
   stitching; ADR-ratio/ticker-change artifacts). The bars were never read as
   PASS or FAIL on clean data, so per the spec this is neither a QC PASS nor
   a QC FAIL.
2. Consequences: Day-1 Stage-1 PASS stays UNCONFIRMED. No adoption, no
   paper venue (Longbridge or Plus500), no live capital, no rulebook changes.
   Tier-6 6.3/6.4/6.5 remain gated. 2 Nov 2026 deployments unaffected.
3. The class 6.1/6.2 is PARKED. Reopening requires BOTH: (a) explicit owner go,
   and (b) a registered clean survivorship-free data source (e.g. Norgate or
   Sharadar) replacing QC free tier; no third free-data attempt.
4. Standing evidence-first lesson registered: for microcap trap-heavy classes,
   free daily point-in-time data (QC free tier) is not evidentiary grade;
   audit trade-level winners against external reality BEFORE reading bars.

Provenance: QC runs by owner on quantconnect.com (LEAN v2.5.0.0.18288,
2014-01-01..2026-08-28, split-adjusted daily, universe US$0.90-10.50 superset
with frozen $1-10 + US$3M dvol entry filters); engine port
scripts/qc/Main.py (PRs #67, #68, #69, #70) validated trade-for-trade against
the frozen local script (154/154 identical both arms, ABAT/ABEO/ABEV).
