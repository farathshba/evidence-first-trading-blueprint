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

## TEST 4.2 (registered 11 Oct 2026, pre-run): OOS gate widening
- Motivation: 4.1 OOS VOID (120 < 150 trades, gate closed 45/57 months). Hypothesis: champion edge persists OOS when gate widening lifts OOS trades >= 150.
- Widening rule (frozen): breadth gate threshold relaxed from top-decile (0.90) to top-quartile (0.75) of listed names. Chosen a priori from 4.1 diagnostics; NO variant search on OOS.
- IS guard: IS (2014-21) run under widened gate must hold EV >= +0.60% with >= 150 trades, else apparatus void — widening may not buy trade count with signal quality.
- OOS bars (single run, no iterations): EV > +0.60%, >= 150 trades, >= 3/5 positive OOS years.
- VOID floor: OOS < 150 trades under widened gate -> FINAL VOID, US champion retired from further testing.
- Costs: 0.35%/side primary; 0.55%/side stress run on the same frozen gate.
- Sequence: IS run first (guard), then OOS run once, then stress. No edits between runs.

### TEST 4.2 AMENDMENT (pre-run, same day): threshold correction
- Registration error caught pre-run: actual gate is breadth >= 0.50 (line: breadth.loc[d] < 0.5), not top-decile. Widening rule corrected to: 0.50 -> 0.40. No other terms changed. Recorded for audit honesty.

## TEST 4.2 RESULTS (11 Oct 2026): OOS FAIL — champion retired from US testing
- IS guard (breadth 0.40, 2014-21): PASS — EV +2.91%, 640 trades, 64/95 months in market.
- OOS (2022-26, breadth 0.40): FAIL — EV -0.14% (bar: > +0.60%), 340 trades (VOID floor cleared — genuine verdict), 2/5 positive years (bar: >= 3/5), maxDD -52.1%.
- Stress full-sample (0.55%/side, breadth 0.40): +1.46% EV but maxDD -60.1% — untradeable tail.
- Final verdict: US microcap champion edge is IN-SAMPLE ONLY; does not persist out-of-sample at gate 0.50 or 0.40. RETIRED from US testing per pre-registered terms. No further gate variants.
- Remaining honest caveats: survivorship bias inflates all figures (today-only universe); true OOS edge is <= the (already negative) numbers above.

## TEST 4.3 (registered 11 Oct 2026, pre-run): short-term reversal, long-only
- Motivation: strongest documented microcap anomaly (STREV ~2.04%/mo in microcaps, t=10.28); long-only leg = buying 21-day losers. SGX mean-reversion tombstones do NOT transfer automatically — US spread structure differs; this is an empirical question.
- Strategy: universe unchanged (US$1-10, dvol >= US$3M); rank by 21-day return; buy BOTTOM 10 equal-weight; monthly rebalance; regime gates unchanged (SPY>SMA200, breadth>=0.50).
- Primary costs 0.35%/side; stress 0.55%/side.
- Stage 1 (full 2014-2026): EV > +0.60%/trade AND >= 6/13 positive years. VOID floor: < 150 trades.
- Stage 2 (walk-forward): IS 2014-21 then untouched OOS 2022-26; OOS EV > +0.60% AND >= 3/5 positive OOS years. VOID floor: OOS < 150 trades -> VOID, no gate-widening reruns (4.2 precedent).
- SURVIVORSHIP CAVEAT: screening-grade only; any Stage 2 pass requires re-run on survivorship-free data before promotion consideration.
- Single OOS run, no edits between arms. Bars before runs.

## TEST 4.3 RESULTS (11 Oct 2026): Stage 1 FAIL — reversal tombstoned on US microcaps
- Full (21d losers, bottom-10): BAR 1 PASS (+1.01% EV, 560 trades) but BAR 2 FAIL (4/13 positive years — EV is 2016+2021 only; 8 negative years). Stress 0.55%/side: +0.61%, marginal. maxDD -42%.
- OOS arm (2022-26): VOID (120 < 150 trades); readable subset EV -2.33%, 1/5 positive years, worst year 2024 (-2.43%) = momentum champion best regime. Anti-correlation with momentum, consistent with SGX breakout tombstone.
- Verdict: FAIL at Stage 1. No Stage 2 per registration. Short-term reversal does NOT survive long-only after 0.35%/side with regime gates. Tombstone: mean-reversion class fails on US microcaps (third market-wide tombstone after SGX 3.2/3.4).
- Note: IS arm not run separately (Stage 1 failure ends test); full-sample year table covers the record.

## TEST 4.5 (registered 11 Oct 2026, pre-run): 52-week-high momentum (George-Hwang), long-only
- Motivation: distinct mechanism from the failed 126d return rank (anchoring nearness-to-52w-high vs trend). Literature: profits in 18/20 international markets, strongest in small stocks; counterpoint: Barroso-Wang find it subsumed by standard momentum in small caps. Last momentum-family US candidate.
- Strategy: universe/gates/rebalance unchanged; rank = A / A.rolling(252).max() (nearness to 52-week high); buy TOP 10; monthly rebalance.
- Costs: 0.35%/side primary, 0.55%/side stress.
- Stage 1 (full 2014-2026): EV > +0.60%/trade AND >= 6/13 positive years, >= 150 trades else VOID.
- Stage 2 (walk-forward): OOS 2022-26 single run: EV > +0.60%, >= 3/5 positive years, >= 150 trades else VOID. No gate-widening reruns (4.2 precedent).
- SURVIVORSHIP CAVEAT: screening-grade only. Bars before runs.
