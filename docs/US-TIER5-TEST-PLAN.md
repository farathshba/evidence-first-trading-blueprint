# US Test Batch Tier 5 — Registration Plan (16 Oct 2026)

Pre-registration plan for the next US test batch. Goal (owner, 16 Oct): produce a thoroughly
tested US strategy that can become a US trading skill — per the standing rule, any skill
proposing trade rules must pass the two-stage guardrail or it is not created.

Baseline: Test 4.5 (52w-high nearness momentum) — Stage 1 CONFIRMED on survivorship-free
QC/AlgoSeek data (EV +4.27%, 214 trades, 7/13 years, PR #28 lab repo). Forward paper OOS
registered (Longbridge, first rebalance 2 Nov 2026). All tests below refine or challenge
that base. Frozen bars BEFORE code. One run each. No gate-widening reruns (4.2 precedent).

## TEST 5.1 — Volatility-conditioned champion (from Humbled Trader Tip 2, triaged 16 Oct)
- Hypothesis: conditioning the 4.5 universe by volatility/range improves EV/trade.
- Rule: identical to 4.5 except eligibility adds ADR filter: 20-day mean of
  (high-low)/close >= 4.0% (registered parameter, one value, no sweep).
- Universe: US$1-10, dvol >= US$3M, SPY>SMA200 + breadth>=0.50 gates, top-10, monthly.
- Bars (Stage 1): EV > +0.60%/trade at 0.35%/side AND >= 6/13 positive years AND >= 150 trades
  (else VOID) AND [key bar] must BEAT the unconditioned 4.5 baseline EV on the same window
  by >= +0.30pp — else no adoption (a filter that doesn't clearly help is complexity).
- Apparatus: Mac lab, Yahoo daily (screening-grade caveat noted), then survivorship-free
  QC confirmation ONLY if Stage 1 passes.
- Verdict options: PASS / FAIL / VOID.

## TEST 5.2 — Breakout-trigger vs nearness-trigger (forum "break and hold", 4.7b)
- Hypothesis: on the SAME scan (consolidation near 52w-high, building volume), the breakout
  entry trigger underperforms the nearness entry — confirming the 3.1b breakout tombstone on US data.
- Rule: 4.5 scan, but entry only on daily close > 252-day high (fresh breakout) instead of
  nearness rank. Hold/rebalance unchanged.
- Bars: same as 5.1 incl. the "beat baseline" comparison (inverted expectation: we PREDICT
  it fails to beat nearness; either result is informative).
- Apparatus: Mac lab, Yahoo daily. No QC follow-up needed if FAIL (tombstone stands).

## TEST 5.3 — RSI divergence + Fibonacci golden pocket (folklore audit, daily)
- Fully mechanical translation: trend filter 50EMA>200SMA; pullback into 38.2-61.8% zone of
  90-day swing leg; 14-day RSI regular divergence; reversal candle close in zone. Long-only.
- Bars: EV > +0.60% net at 0.35%/side AND >= 6/13 positive years AND >= 150 trades else VOID.
- Expected: FAIL (mean-reversion family killed 3x). Run for record completeness.

## TESTS 5.4-5.6 — Intraday folklore audit (ORB, ACD, Brooks 2-leg proxy) — PARKED
- Require QC minute data; heavy runs. Registered as intent only; bars to be frozen in a
  separate registration before any minute-data run (budget/feasibility check first).
- Expected: FAIL across the board (friction wall). Not edge-hunting; tombstone-completion.

## Status (18 Oct 2026)
- 5.1 ADR-conditioned champion: DONE — VOID-pending-debug / NOT CONFIRMED (QC v5, key bar
  fails inverted by 1.62pp; Stage 1 edge = survivorship artifact; tombstoned; PR #32,
  docs/US-TEST-5-1-QC-VERDICT.md). Unconditioned 4.5 stays the registered paper variant.
- 5.2 breakout-trigger: REGISTERED + pre-registration restated (PR #33,
  docs/US-TEST-5-2-REGISTRATION.md) — ready to run on Mac lab. If Yahoo Stage 1 PASS,
  elevated suspicion applies before QC compute (5.1 lesson).
- 5.3 RSI+Fib: queued after 5.2.
- 5.4-5.6: REGISTERED separately (PR #36, docs/US-TESTS-5-4-5-6-INTRADAY-REGISTRATION.md)
  — frozen bars + compute budget; awaits owner go on QC minute-data compute.
- Parallel (2 Nov deadline): US paper trade-ledger spec v1.0 REGISTERED
  (PR #34, docs/US-TRADE-LEDGER-SPEC.md) — schema, provenance contract, slippage validation,
  audit bars frozen BEFORE deployment.

## Order of execution
1. ~~Test 5.1~~ DONE: VOID/not confirmed (17 Oct)
2. Test 5.2 (closes the breakout-vs-nearness gap)
3. Test 5.3 (cheapest folklore tombstone)
4. Tests 5.4-5.6 only if owner wants intraday record completeness.

## Skill path (the end goal)
Any variant that passes Stage 1 + survivorship-free confirmation + (for live authority) the
forward paper OOS, earns a US rulebook skill (sgx-swing-rulebook pattern: ENTER/WAIT authority,
frozen rules, Phase-4-style runbook). Until then: context-only. A skill that fails any stage
is not created — same standard that deleted ema-9-20-rsi-atr-trading and trade-sector.

Provenance: docs/US-TEST-PLAN.md (Tier 4 verdicts), PR #28 (4.5 confirmation),
arkenstone strategies/us-smallcap-research-triage-oct-2026.md (source triage).
