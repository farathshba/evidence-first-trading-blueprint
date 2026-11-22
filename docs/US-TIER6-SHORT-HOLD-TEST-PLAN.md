# US Tier 6 — Short-Hold Folklore Test Plan (Break & Retest + VWAP/9EMA + Bias Probe)

**Status:** REGISTERED (bars frozen below BEFORE any code). No bars may change after the first run. One registered run per test, no gate-widening (4.2 precedent).
**Owner decisions locked 22 Nov 2026:** market = US microcaps (frozen 4.5 universe), sequence = daily Stage 1 first, intraday only if Stage 1 passes. **Owner decisions (same day): 6.5 bias probe REGISTERED; 5.4 amended pre-run with both paired arms (body-close S/R convention stays per-test, NOT made default).** **Batch status: source series CLOSED 22 Nov at 5 videos; no further 6.x registrations without new owner go.**

---

## Sources being tested

- **Video 1:** "Give Me 33 Minutes and You\'ll Never Place a Dumb Trade Again" — Tori Trades (Victoria Duke), youtube.com/watch?v=zai2jojP1hY
- **Video 2:** "These are the only two trading indicators I use..." (VWAP + 9 EMA day-trade setup; Simply Options Academy marketing video), transcript pasted 22 Nov 2026. Tests 6.1–6.3 decode Video 1; Test 6.4 decodes Video 2.
- **Video 3:** "One strategy I use every single day..." (Opening Range Breakout, 15/5/1-minute drill) — triaged 22 Nov 2026 as **class already registered (Test 5.4)**. Owner decision: 5.4 amended pre-run with both paired arms (retest entry + fixed 1:2 target) — see amendment doc.
- **Video 4:** Harry Sharp interview (IQ Capital) — "story / zone / strat" intraday scalping — triaged 22 Nov 2026 as **breakout/retest family (already registered) + SMC-wrapper exclusions**. Owner decision: the two-candle bias filter REGISTERED as Test 6.5 (probe only); body-close S/R convention stays per-test.
- **Video 5:** "Only two indicators I have ever used" — 20 SMA + 200 SMA — triaged 22 Nov 2026 as **FULLY COVERED** (200-MA regime logic = the system\'s own validated gate; all entry cores map to existing tombstones). No new test; batch CLOSED.
- **Taught on:** index futures / day trading venues. We test the *decodable core* on the US microcap universe, so friction is harsher here than in the source venue — that gap is itself part of the test.
- **Third-party decode cross-checked:** app.faketrades.in/s/give-me-33-minutes... (same-rule backtest on Indian data: +0.31R expectancy, 36% win rate, negative in 4/9 years, maxDD −21%) — used to sanity-check the mechanical translation only; NOT evidence for adoption.

**Standing verdicts this plan must respect:** breakout class tombstoned both markets (3.1b, 5.2, 4.7b — breakout strictly underperformed nearness on the same scan); Brooks EMA-pullback and RSI family dead on both markets; **VWAP reclaim already eliminated in the 16 Oct US research sweep; EMA-crossover family dead via Test 3.5 (1,683 trades, gross ≈ +0.05% — no edge even before friction)**; friction wall (~0.9% round trip on SGX; 35bps/side model on US) governs all short-hold structures. **Registered prediction: FAIL for every strategy test in this plan; the 6.5 probe is predicted to show sub-friction or no payload.** A pass would be as suspicious as 5.1 — QC/AlgoSeek survivorship-free confirmation is mandatory before any Stage-1 pass is believed (three prior Yahoo-snapshot inversions: 5.1, 5.3, and the 5.1-QC sanity fail).

---
## Mechanical translation (frozen before any run)

Videos are deliberately subjective ("capture as many touch points as possible", "wiggle room", "pressure in the wicks", fair value gaps, liquidity areas, fib targets, "liquidity grabs", "clean zones"). To make them testable, every decodable claim is replaced by a fixed rule; every undecodable claim is registered as out of scope. These definitions are FROZEN.

### Trendline construction (per symbol, per timeframe, Tests 6.1–6.3)
- **Pivots:** swing highs/lows via fractal window W=5 bars on each side (5.4-registered style).
- **Down-trendline** = line through the two most recent consecutive lower swing highs; extend right. **Up-trendline** = mirror on swing lows.
- **Touch validity:** bar high/low within ±0.25 × ATR(14) of the line counts as a touch. A line needs ≥ 2 anchor points to exist.
- **No-intersection rule (her core rule):** if any bar's body CLOSE crosses the line between anchors, the line is invalidated and rebuilt from the next valid pair. *Body-close, not wick* — this is the frozen operationalization of her "price can\'t pierce, but incorporate wick within buffer" instruction. "Wiggle room" is NOT tested (advanced topic, deliberately excluded, registered as out of scope).

### Top-down filter (Tests 6.1–6.4)
- The video hierarchies (MTF top-down / "above VWAP = trade up") are replaced by the frozen two-level gate already validated on this universe: **SPY > SMA200 AND universe breadth ≥ 0.50**, evaluated with 1-bar lag (shift(1) look-ahead idiom, per execution_sim lesson). Nothing new is invented.

### Test 6.1 — Break & Retest, DAILY (Stage 1, Mac/Yahoo; Video 1)
**Trigger sequence (all three required, per transcript):**
1. **Break:** daily close crosses the active trendline (close beyond line, evaluated with lag).
2. **Pullback & retest:** within N=10 bars after the break, price returns and touches the broken line from the other side (touch rule above).
3. **Candle closure:** the retest bar CLOSES on the far side of the line (i.e., does not close back through). Entry next bar open.
- **Direction:** long-only execution per owner rule; short-side examples in the video are mapped to the long mirror.
- **Stop/exit (her Option A):** opposing trendline redrawn steeper at entry (anchored on the retest swing and prior pivot, same construction rules); position closed at the next daily close violating that line. No fixed stop, no target — matches her "no set take-profit, trail the trend" mode.
- **Holds:** short by construction (days to weeks) — this is the friction-wall exposure.
- **Run:** 2014-01 → 2026-10, 0.35%/side primary, 0.55% stress, frozen 4.5 universe (US$1–10, dvol ≥ US$3M), survivorship caveat flagged on Yahoo snapshot.

### Test 6.2 — Exit head-to-head (paired, ZERO new bars consumed — 4.7b precedent; Video 1)
Same trades as 6.1. Arm A = opposing-trendline exit (6.1 as run). Arm B = her Option B: S/R take-profit placed at the most recent confirmed swing high BEFORE the entry bar (frozen: most recent pivot high with ≥ 3 touches within 0.25×ATR in the prior 60 bars; if none qualifies, top of the retest swing), nudged 0.25×ATR below the level (her "bump it a few ticks"). Same stop, whichever exit hits first closes the trade. **Key bar: Arm B EV − Arm A EV ≥ +0.30pp** for the S/R exit to be considered an improvement. Prediction: no separation (FAIL registered).

### Test 6.3 — Intraday 15m break & retest (ONLY IF 6.1 clears Stage 1 bars; Video 1)
- Same frozen rules on 15-minute bars, 1h-bars lines for the bias (video's own 1h example), same/day-or-so holds, force-close EOD (intraday-scaled, 5.4-style).
- **Data route:** LEAN CLI local minute data (owner-decided route for 5.4–5.6; docs/RUNBOOK-5-4-5-6-LEAN-CLI.md applies — single-ticker download test first, IBKR 1-min bulk as fallback). Universe cap and segment splits pre-registered in-apparatus before the run, per 5.4–5.6 precedent.
- If 6.1 fails Stage 1, 6.3 is VOID-by-precedent: no intraday upgrade of a dead signal (registered now so it cannot be argued later).

### Test 6.4 — VWAP + 9 EMA day-trade setup (LEAN CLI minute route, queued behind 5.4 plumbing; Video 2)
**Class status / prior:** VWAP reclaim was eliminated in the 16 Oct US research sweep; EMA-crossover entries died with Test 3.5 (gross ≈ +0.05%, no edge before friction). This test is registered as **tombstone-completion**: the decodable core is tested once mechanically; the undecodable narrative (wick "pressure", fair value gaps, "liquidity/demand" zone targeting, fib 50% targets) is OUT OF SCOPE — registered as SMC-class untestable folklore, identical to the 3.6/SMC exclusions. Prediction: FAIL.

**Frozen rules (long-only mirror, per owner rule):**
- **Bars:** 15-minute, session-anchored indicators; force-flat at 15:55 ET (day-trade hold constraint from the video).
- **Indicators:** standard session VWAP (no bands/anchors, exactly as the video insists); EMA(9) on 15m bars.
- **Regime rule (video rule 1):** only longs, only when price is above session VWAP at signal time.
- **Proximity gate (video rule 2):** |EMA9 − VWAP| ≤ 0.25 × ATR(14, 15m) on the signal bar ("trade only when they\'re close together").
- **Entry A (break-retest continuation):** price crosses above VWAP, then pulls back and touches the VWAP/EMA zone from above within N=6 bars; confirmation bar closes above the prior bar high with a body ≥ 0.75×ATR(14, 15m) (the video's "momentum/engulfing" proxy); entry next bar open.
- **Entry B (level rejection):** price sells down INTO the VWAP/EMA zone from above in an above-VWAP session; rejection proxy = lower wick ≥ 50% of bar range on ≥ 2 consecutive bars at the zone; then a bar closes above EMA9; entry on the next bar taking out the prior bar high. Entry next bar open.
- **Stop:** below signal-side swing = min(swing_low, min(VWAP, EMA9) − 0.25×ATR), evaluated on entry bar; exit on stop touch (intraday touch, not close — day-trade convention).
- **Target:** prior session swing high; whichever of target / stop / 15:55-ET-flat hits first closes the trade. One position at a time per symbol.
- **Run window:** 2016-01 → 2026-07 (LEAN-local/AlgoSeek-equivalent minute data window), 0.35%/side + 0.55% stress, frozen 4.5 universe with the 5.4–5.6 registered in-apparatus caps (universe cap, segment splits, truncation-at-cap rule declared BEFORE the run).
- **Compute:** LEAN CLI local route per docs/RUNBOOK-5-4-5-6-LEAN-CLI.md; runs only after the 5.4 single-ticker download plumbing check passes; IBKR 1-min bulk fallback if the QC download fails.

### Test 6.5 — Two-candle session bias probe (Harry Sharp, Video 4) — PROBE ONLY, not a strategy test (owner decision 22 Nov 2026)
**Source:** Video 4 — "story/bias" step: previous daily close AND previous 4h close (the last completed 4h candle before the session) in the same direction → session bias in that direction; mixed → stand aside. Long-only mirror per owner rule: only the bullish confluence (both closes up) is probed for long payload; bearish confluence is reported informationally.

**Class status / purpose:** Not covered by any existing registration. This is a *predictive-payload probe* — does the two-candle confluence carry information about the next session? — NOT a tradable strategy. **Any later use of it as a filter on a live strategy is a rule change requiring the full two-stage guardrail.** Registered prediction: NO TRADABLE EDGE — any payload found is expected to be sub-friction, consistent with every short-hold finding to date (and note the overnight-hold inversion: SGX overnight edge is inverted, −0.10%/night — tight multi-hour windows on microcaps have the same exposure).

**Frozen rules (long-only mirror):**
- **Condition C(t):** daily candle of t−1 closes up AND the last completed 4h candle before the session open (09:30 ET) closes up. Sessions not meeting C are excluded from the conditional arm; the unconditional mean is computed across ALL sessions.
- **Measurement variable:** next-session return of the frozen 4.5 universe, equal-weighted — close(09:30)→close(15:55) equal-weight universe return on day t (session return, not close-to-close, to isolate the session window he claims the bias governs).
- **Data:** 4h and intraday session returns require the LEAN CLI minute route — queued behind the 5.4 single-ticker plumbing check, same as 6.4; run window 2016-01→2026-07 or the longest window the minute data supports, declared in-apparatus BEFORE the run.
- **One run. No gate-widening. No re-runs.**

**Frozen probe bars (all required for the probe to "read positive"):**
| Bar | Threshold |
|---|---|
| Conditioned mean session return − unconditional mean | ≥ +0.10pp |
| Observations (sessions meeting C) | ≥ 500 (else VOID-by-feasibility) |
| Consistency | positive delta in BOTH halves of the window (split at midpoint) |
| Statistical | block-bootstrap 95% CI of the delta (30-day blocks) excludes 0 |
| Friction context | report: does the delta survive 2×0.35%/side costs if traded naively? (expected NO — informational but mandatory in the verdict) |

**If the probe reads positive:** it does NOT enter the live system; it is queued as a candidate filter-condition arm on a future registered test (which must then clear the two-stage guardrail with the filter on). If negative: bias-filter class tombstoned; Video 4 fully closed.


---

## Source triage log

**Video 3 (Opening Range Breakout, 15/5/1-minute drill):** CLASS ALREADY REGISTERED (Test 5.4) — no Tier 6 test consumed. **Owner decision 22 Nov: BOTH paired arms (retest entry + fixed 1:2 target) pre-registered into 5.4 before its first run** (docs/US-TEST-5-4-RUN-AMENDMENT.md). One-run discipline preserved. Excluded (SMC-class): wick reads, mental stops, discretionary targets. Registered prediction: FAIL.

**Video 4 (Harry Sharp, "story / zone / strat"):** Entry machinery = breakout/retest family (covered); SMC layers excluded (liquidity-grab narrative, clean/messy zones, "nipple wick" explicitly experience-based, discretionary fast-move exits, fundamental "story", staircases, gamma). **Owner decisions 22 Nov: two-candle bias filter REGISTERED as Test 6.5 (probe only); body-close S/R convention NOT made default (stays per-test — consistent with 6.1\'s frozen body-close rule where used).** Claimed 70%+ win rate at ~1:1: noted as claimed only; standing rule — no adoption on claimed win rates.

**Video 5 (transcript pasted 22 Nov 2026): "Only two indicators I have ever used" — 20 SMA + 200 SMA (day/swing trading; Schwab account, ~$500k/9mo claimed).**
- **Triage verdict: FULLY COVERED — no new test consumed.** Every decodable element maps to an existing registration or tombstone:
  - **200-MA floor/ceiling regime logic = the system\'s own already-validated gate** (SPY > SMA200 in the 4.5 gates / ES3 > SMA200 on SGX). Not folklore — this half of the video is already evidence-cleared and live. Convergence worth noting: a claimed six-figure day trader\'s "bias layer" reduces to the champion\'s regime gate.
  - **20-MA pullback / touch-and-bounce entries** = EMA-pullback class, tombstoned both markets (Brooks EMA-pullback, 16 Oct sweep; EMA family dead via Test 3.5, gross ≈ +0.05%).
  - **"Extension" mean-reversion reversals** = mean reversion, tombstoned (SGX support-bounce 21% win rate; deeper-dip walk-forward fail; US STREV 4.3).
  - **"Squeeze play"** (flat 200 + rising 20 crossing, oscillation, breakout) = breakout class, tombstoned (3.1b, 5.2, 4.7b); the trader himself says it suits swing trading on daily/weekly.
- **Excluded as untestable:** discretionary "respect" reads across 2m→daily timeframes with no frozen entry/exit/stops/targets/hold rules anywhere in the video; claimed brokerage P&L (noted as claimed only; standing rule — no adoption on claimed results).
- **BATCH NOTE (final): Tier 6 video series CLOSED 22 Nov at 5 sources.** Series synthesis mirrors the Tier 3 / US finding from the popular-media direction: every video\'s decodable core reduces to (a) the regime gate the system already uses, (b) a short-hold class the friction wall kills, or (c) untestable SMC-style narrative. Novel decodable yield from the entire series: ONE probe (6.5) and two pre-registered 5.4 arms. The "why not something else" answer now has popular-media coverage in addition to backtest coverage: same classes, same wall. No further 6.x registrations without new owner go.


---

## Frozen bars

**Daily-scaled tests (6.1, 6.2):**

| Bar | Threshold |
|---|---|
| EV/trade (net, 0.35%/side) | > +0.60% |
| Positive years | ≥ 6/13 |
| Trade count | ≥ 150 (else VOID-by-feasibility) |
| OOS (walk-forward, 2022–26) | EV ≥ +0.60% AND ≥ 4/5 positive years |
| Stress @ 0.55%/side | EV > 0 (passes-at-0.35-dies-at-0.55 = FAIL; 4.6 lesson) |
| Two-stage guardrail | Stage 1 full-period → Stage 2 walk-forward, pre-registered bars only |
| Confirmation bar | Any Stage 1 PASS triggers mandatory QC/AlgoSeek survivorship-free re-run before adoption (5.1/5.3 inversion precedent); maxDD reported (informational, 5.3 miss lesson) |

**Intraday-scaled tests (6.3, 6.4)** — per the frozen 5.4–5.6 registration precedent:

| Bar | Threshold |
|---|---|
| EV/trade (net, 0.35%/side) | > +0.60% |
| Positive years | ≥ 6/10 |
| Trade count | ≥ 500 (else VOID-by-feasibility) |
| Stress @ 0.55%/side | EV > 0 (mandatory) |

**Probe (6.5):** bars frozen in the 6.5 section above. Probe results NEVER enter the live system directly.

**Adoption bar (only after all above):** beats the live 4.5 champion regime-gated baseline EV by ≥ +0.30pp on the matched universe, else no adoption even on a pass.

## Kill / tombstone criteria
- Any test failing Stage 1 → class tombstone logged with verdict doc + PR, no gate variants, no re-runs (one-run discipline).
- Any Stage 1 pass that inverts on QC data → tombstone + Yahoo-snapshot signature logged as 4th occurrence.
- Kill criteria are structural only — never P&L-based.

## Apparatus guardrails (standing lessons, binding)
- Verify fetched/generated file content is non-empty before pushing (18 Oct incident).
- shift(1) on all signal columns; no same-bar close-entry look-ahead (5.2 off-by-one lesson).
- Probe scripts before verdicts (known-good-ticker probe; index-alignment probe — 4.4/4.6 lessons).
- Deterministic rerun check: identical numbers required on repeat run (5.3 Mac check).
- Costs applied offline at −2×0.35%/trade from fills unless venue fees are implemented.
- Provenance: yahoo=delayed-snapshot (survivorship caveat flagged), qc-algoseek=cached, lean-local=cached; Contract-1 5-key on every number in any results doc.

## Execution order
1. 6.1 daily Stage 1 (Mac/Yahoo) → single bar reading → verdict doc + PR
2. 6.2 paired exit head-to-head (consumes no new bars) → verdict doc + PR
3. 6.3 intraday ONLY on 6.1 Stage 1 pass → LEAN CLI route → verdict doc + PR
4. 6.4 VWAP/9EMA intraday → LEAN CLI route, AFTER 5.4-minute-data plumbing is validated (single AAPL-download test per RUNBOOK-5-4-5-6) → single bar reading → verdict doc + PR
5. 6.5 bias probe → LEAN CLI route, same data batch as 6.4 → single bar reading → verdict doc + PR (probe verdict; no adoption regardless)
6. Any surviving candidate → two-stage walk-forward → QC confirmation → adoption-bar comparison vs 4.5 → owner decision

**Source series CLOSED 22 Nov 2026 (5 videos). No further 6.x registrations without new owner go.**
**2 Nov live/paper deployments are unaffected by anything in this plan until every bar above reads.**
