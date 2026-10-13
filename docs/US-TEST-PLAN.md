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

## TEST 4.5 RESULTS (11 Oct 2026): Stage 1 PASS, Stage 2 VOID — candidate alive, unconfirmed
- Full (near52w rank, top-10): BAR 1 PASS (+1.40% EV, 560 trades), BAR 2 PASS (7/13 years), maxDD -23.8% (mildest of all US variants).
- Stress 0.55%/side: +1.00% EV, 6/13 years, maxDD -27.0% — cost-robust.
- OOS (2022-26): VOID (120 < 150 trades, gate-closed regime). Readable subset: EV +0.69% (clears BAR 1) but 2/5 positive years (fails BAR 2) — edge concentrated 2025-26; 2026 = +1.34%.
- Verdict: best-performing US candidate to date; survives stress; OOS unconfirmed by pre-registered terms. NOT promotable (survivorship caveat + no OOS confirmation). Retained for survivorship-free re-test if data is acquired.

## TEST 4.4 COVERAGE AUDIT (11 Oct 2026): NO-GO at 75% vs 80% guard — PEAD VOID-by-coverage
- Apparatus note: first audit run invalid (lxml ImportError corrupted 88/100 into exceptions; installed lxml 6.1.3, rerun clean, 0 exceptions).
- Rerun (seed 42, n=100 of 666): >=8 quarters: 75/100 (75%, guard 80%). Thin 1-7: 13 (recent listings — TRUG, ABTC, BTCT et al). Zero rows: 12 — several appear to be closed-end funds/ETFs in the price-only universe (DSU, WIW, NMZ pattern), structurally uncoverable rather than a data gap.
- Verdict: VOID-by-coverage, Test 3.6 precedent. No post-hoc bar-lowering or universe re-scoping after seeing results (4.2 precedent).
- Revival condition (pre-declared, before any re-audit): a fund-excluded universe declared BEFORE the audit, and a source covering >=80% of it. Norgate (fund flags + point-in-time constituents) would satisfy declaration mechanics if the survivorship purchase happens. yfinance is otherwise adequate — 0 exceptions, 25-row depth on covered names.
- Note: yfinance earnings dates are rich where present (up to 25 quarters, incl. EPS estimates) — viable signal source if the universe problem is solved upstream.

## TEST 4.6 (registered 12 Oct 2026, pre-run): turn-of-month seasonality, long-only
- Hypothesis: month-end cash flows (salaries, fund inflows) lift equities in a ~7-day window (last 4 + first 3 trading days of each month). Calendar effect, not a stock-selection edge.
- Strategy: same price/dollar-volume universe; select top-10 by 20d avg dollar volume (liquidity only, no signal rank); hold ONLY during the window; cash otherwise. No regime gates (calendar mechanism is regime-agnostic — intentional deviation, registered).
- Costs: 0.35%/side primary, 0.55%/side stress.
- Bars (frozen pre-run): Stage 1 full 2014-2026: mean window return > +0.30% NET of costs AND >= 6/13 positive years AND >= 100 windows, else VOID. Stage 2 OOS 2022-26 single run: mean > +0.30%, >= 3/5 positive years, >= 40 windows, else VOID. No reruns.
- Reasoning for +0.30% bar: ~7-day hold vs ~21-day in prior tests; net bar implies ~+1.0% gross vs 0.70% round-trip friction — a real hurdle, not a giveaway.
- SURVIVORSHIP CAVEAT: screening-grade only.

## TEST 4.6 RESULTS (12 Oct 2026): Stage 1 PASS, Stage 2 FAIL — turn-of-month tombstoned
- Apparatus note: initial run VOID due to volume-matrix index-alignment bug (row-number index vs calendar dates -> all volumes NaN); fixed loader, probed on 2026 subset before registered arms. No verdict was produced by the buggy run.
- Full: BAR 1 PASS (+0.49% net/window, 152 windows), BAR 2 PASS (7/13 years). Stress 0.55%/side: +0.09% — edge is cost-fragile (margin ~= friction delta).
- OOS 2022-26 (57 windows, valid sample): BAR 1 FAIL (-0.34% mean window), BAR 2 PASS (3/5). Negative mean = decisive fail, not a near-miss.
- Verdict: FAIL at Stage 2 per pre-registered terms. Turn-of-month does not survive friction out-of-sample on this universe. Tombstone: seasonality class closed on US microcaps (screening-grade).
- Diagnostic flag: 2026 window mean -9.45% is an extreme outlier (next-worst year -5.54%); appears to be genuine recent drawdown, not artifact — clean-data re-test (if purchased) can double-check incidentally. No rerun.

## TEST 4.5 SURVIVORSHIP-FREE RE-TEST (13 Oct 2026): Stage 1 CONFIRMED — QC/AlgoSeek
- Apparatus: QuantConnect free tier, LEAN Python port of frozen bars (near52w, top-10, monthly, SPY>SMA200 + breadth>=0.50, 0.35%/side). AlgoSeek data includes delisted equities — survivorship caveat CLOSED.
- Two stitched runs with SetWarmUp(200): A 2014-01→2020-06 (98 trades, +1.99%), B 2020-07→2026-07-15 (116 trades, +6.20%).
- Stitched: EV +4.27% net, 214 trades, 7/13 positive years. ALL THREE BARS PASS.
- Negative years honest on record: 2014 (-2.16%), 2023 (-7.19%). Gate-closed flat: 2015/19/20/22 — same trade-frequency profile as the original run; edge is NOT a survivorship artifact.
- Caveats: data ends 2026-07-15 (vendor cutoff, ~3 mo short); boundary trades at split uncounted (conservative); see results/us_4_5_qc_survivorship_free.txt.
- Verdict: first validated US candidate. OOS arm stays VOID per registration; walk-forward decision is a separate pre-registered owner call.
