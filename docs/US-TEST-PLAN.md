# US TEST PLAN — Tier 4 expansion track (per docs/PHASE-US-1-RUNBOOK.md)

## TEST 4.1 — US sub-US$10 champion replication — PRE-REGISTERED 10 Oct 2026, before any run
- Subject: does the SGX champion spec (126d momentum, top-10, monthly rebalance, regime + breadth gates) replicate on a US sub-US$10 universe? Prior: OPEN — SGX evidence does not transfer in either direction (US friction lower; regime differs).
- Universe: US exchange-listed (Nasdaq screener, no OTC), price US$1-10, 20d dollar-volume >= US$3M, >=260d history. Snapshot = today (SURVIVORSHIP CAVEAT pre-registered as validity threat #1; Stage 1 final only after caveat quantified or delisting-aware list sourced).
- Gates: SPY > SMA200 AND breadth >= 50% of universe above SMA200. Either closed -> flat.
- Costs: 0.35%/side baseline, stress 0.55%/side. Long-only.
- Bars (Stage 1, 2016-2026): EV/trade > +0.6% after costs AND >= 6/10 positive years.
- Stage 2 (walk-forward): freeze IS 2016-21, untouched OOS 2022-26: OOS EV >= +0.6% AND >= 4/5 positive years.
- VOID: <150 trades Stage 1; data coverage <90%; survivorship contamination demonstrably >2pp of EV.
- Phase 0a tool: scripts/us_universe_fetch.py (sha256 02391c9f..730e54; compile-gated; diagnostics at every stage).

## TEST 4.1 RUN 1 (10 Oct 2026): VOID — pre-registered trade-count guard fired (120 < 150)
- Output: EV +12.86% (exploratory only, NOT a verdict), 12/129 months in market, 3/11 positive years, VOID declared before any bar evaluated.
- Autopsy found apparatus bug: breadth denominator counted unlisted-at-date tickers as "below SMA200" (NaN > NaN = False), mechanically closing gates 2016-2019. Fixed point-in-time (denominator = tickers with 200d history at date).
- Second cause: fetch started 2016-01, consuming 2016 in lookbacks. Refetch at 2014-01.
- EV inflation note: survivorship-only universe + 12 cherry months; the +12.86% is not evidence of edge under any bar.
- Rerun authorized under the SAME pre-registration (apparatus fix, not a spec change). Bars unchanged.

## TEST 4.1 RUN 2 (10 Oct 2026, post-fix): IS PASS / OOS VOID / stress PASS
- Full: EV +4.24%, 560 trades, BAR 1 PASS, BAR 2 PASS on letter (6/13 positive years — concentration caveat: edge lives in 2016/2020/2021/2024/2025; regime-dependent, not all-weather). 56/153 months in market. maxDD -25.9% monthly equity.
- IS (2014-21): PASS — EV +4.36%, 440 trades.
- Stress (0.55%/side): PASS — EV +3.84%. Edge survives realistic microcap fills.
- OOS (2022-26): VOID — 120 < 150 trades (genuine; gate-closed regime, not apparatus). No out-of-sample confirmation exists.
- Apparatus: ZeroDivision guard added (commit 579dc30) after 2014 start exposed empty-breadth dates; breadth point-in-time fix from PR #22 confirmed working (56 vs 12 months in market).
- Standing verdict: in-sample US microcap edge exists at conservative costs; replication NOT demonstrated out-of-sample. Next: pre-register Test 4.2 or accept VOID as final. Bars before runs, as always.
