# US Tier 6 — Short-Hold Folklore Test Plan (Break & Retest + VWAP/9EMA)

**Status:** REGISTERED (bars frozen below BEFORE any code). No bars may change after the first run. One registered run per test, no gate-widening (4.2 precedent).
**Owner decisions locked 22 Nov 2026:** market = US microcaps (frozen 4.5 universe), sequence = daily Stage 1 first, intraday only if Stage 1 passes.

---

## Sources being tested

- **Video 1:** "Give Me 33 Minutes and You\'ll Never Place a Dumb Trade Again" — Tori Trades (Victoria Duke), youtube.com/watch?v=zai2jojP1hY
- **Video 2:** "These are the only two trading indicators I use..." (VWAP + 9 EMA day-trade setup; Simply Options Academy marketing video), transcript pasted 22 Nov 2026. Tests 6.1–6.3 decode Video 1; Test 6.4 decodes Video 2.
- **Video 3:** "One strategy I use every single day..." (Opening Range Breakout, 15/5/1-minute drill) — triaged 22 Nov 2026 as **class already registered (Test 5.4)**, see Source triage log below. No new Tier 6 test consumed.
- **Video 4:** Harry Sharp interview (IQ Capital) — "story / zone / strat" intraday scalping — triaged 22 Nov 2026 as **breakout/retest family (already registered) + SMC-wrapper exclusions**; two decodable novel elements flagged for owner decision, see Source triage log. No new Tier 6 test consumed.
- **Taught on:** index futures / day trading venues. We test the *decodable core* on the US microcap universe, so friction is harsher here than in the source venue — that gap is itself part of the test.
- **Third-party decode cross-checked:** app.faketrades.in/s/give-me-33-minutes... (same-rule backtest on Indian data: +0.31R expectancy, 36% win rate, negative in 4/9 years, maxDD −21%) — used to sanity-check the mechanical translation only; NOT evidence for adoption.

**Standing verdicts this plan must respect:** breakout class tombstoned both markets (3.1b, 5.2, 4.7b — breakout strictly underperformed nearness on the same scan); Brooks EMA-pullback and RSI family dead on both markets; **VWAP reclaim already eliminated in the 16 Oct US research sweep; EMA-crossover family dead via Test 3.5 (1,683 trades, gross ≈ +0.05% — no edge even before friction)**; friction wall (~0.9% round trip on SGX; 35bps/side model on US) governs all short-hold structures. **Registered prediction: FAIL for every test in this plan.** A pass would be as suspicious as 5.1 — QC/AlgoSeek survivorship-free confirmation is mandatory before any Stage-1 pass is believed (three prior Yahoo-snapshot inversions: 5.1, 5.3, and the 5.1-QC sanity fail).

---
## Mechanical translation (frozen before any run)

Videos 1–2 are deliberately subjective ("capture as many touch points as possible", "wiggle room", "pressure in the wicks", fair value gaps, liquidity areas, fib targets). To make them testable, every decodable claim is replaced by a fixed rule; every undecodable claim is registered as out of scope. These definitions are FROZEN.

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
- **Stop:** below signal-side swing = min(zswing_low, min(VWAP, EMA9) − 0.25×ATR), evaluated on entry bar; exit on stop touch (intraday touch, not close — day-trade convention).
- **Target:** prior session swing high (the video's "low of some sort", mirrored); whichever of target / stop / 15:55-ET-flat hits first closes the trade. One position at a time per symbol.
- **Run window:** 2016-01 → 2026-07 (LEAN-local/AlgoSeek-equivalent minute data window), 0.35%/side + 0.55% stress, frozen 4.5 universe with the 5.4–5.6 registered in-apparatus caps (universe cap, segment splits, truncation-at-cap rule declared BEFORE the run).
- **Compute:** LEAN CLI local route per docs/RUNBOOK-5-4-5-6-LEAN-CLI.md; runs only after the 5.4 single-ticker download plumbing check passes; IBKR 1-min bulk fallback if the QC download fails.

---

## Source triage log

**Video 3 (transcript pasted 22 Nov 2026): "one strategy I use every single day..." — Opening Range Breakout (15/5/1-minute drill, first-2-hours focus).**
- **Triage verdict: CLASS ALREADY REGISTERED — no new test consumed.** The decodable core is Test 5.4 (laboratory registration PR #36, superseded by arkenstone PR #9 / lab repo 5.4–5.6 registration): 15-minute opening range, close-confirmed break, gap-up only, ≤2% width filter, same-day exit, QC/LEAN minute route, predicted FAIL (tombstone-completion). The video's 5-minute-close confirmation and 15-minute range high/low marking match 5.4's frozen definition line for line. Registering a near-duplicate 6.5 would violate the one-run / no-class-duplication discipline.
- **Two deltas vs the frozen 5.4 registration, flagged for owner decision BEFORE the 5.4 run (its registration is already frozen; amending mechanics is the owner\'s call, not an agent default):**
  1. **Retest entry:** the video enters on the pullback to the broken range level (1-minute rejection at the level), whereas 5.4 as registered enters on the confirmed close beyond the range. Note: 4.7b found breakout-entry strictly worse than nearness on the daily 52w scan — a retest-entry arm is a legitimate paired-arm option if the owner pre-registers it now.
  2. **Fixed 1:2 take-profit:** the video targets a fixed 2R; 5.4 exits at day-end logic. A fixed-R target is cheap to add as a paired exit arm pre-run.
- **Excluded as untestable folklore (SMC-class):** "sellers/buyers stepping in" wick reads, "price acceptance" narrative, mental-stop / hold-if-structure-unviolated management (only hard stops are testable), unspecified "key technical levels" higher-timeframe targets, low-of-day-plus-continuation discretionary targets.
- **If owner declines both deltas:** Video 3 = source confirmation only; 5.4 runs exactly as registered.

**Video 4 (transcript pasted 22 Nov 2026): Harry Sharp interview (IQ Capital) — "story / zone / strat" intraday NQ scalping.**
- **Triage verdict: CLASS ALREADY REGISTERED (breakout/retest family) + SMC-wrapper exclusions — no new Tier 6 test for the entry.**
  - **Entry machinery = same family as 6.1 / 6.4 / the 5.4 retest-arm option:** intraday range/structure on 5m/15m, close above the range high (close-confirmed, level-invalidation-on-close matches the 5.4 convention), pullback/bottom-wick retest, buy-stop at the breakout candle high, stop below the breakout candle, ~1:1 target, session window (NY open, ~1 hour). A duplicate 6.5 would burn minute-data compute on a predicted-FAIL class already queued — declined per one-run / no-class-duplication discipline.
  - **Excluded as SMC-class untestable folklore:** "liquidity grabs" / "rubber band spring" narrative, "clean zone" vs "messy zone" judgment (explicitly experience-based), wick-quality reads ("nipple wick" — the trader himself refuses to put a number on it), discretionary profit-taking ("when it moves fast, close"), fundamental "story" bias, "staircase" market-structure marking, order-flow/gamma references he himself says are unneeded.
- **Two decodable novel elements, flagged for OWNER DECISION (not registered without owner go):**
  1. **Two-candle bias filter:** previous daily close bullish AND previous 4h close bullish → session-bullish bias (bearish/bearish → bearish; mixed → stand aside or fade at 4h/daily resistance). A **cheap, mechanically clean session-continuation signal** not covered by any existing registration. Test shape if owner approves: intraday bars (LEAN CLI route) or a daily-proxy variant measuring next-session return conditional on the two closes; long-only mirror; bars frozen BEFORE any run. NOTE: this would be a *bias/probe* test (does the filter carry predictive payload?), NOT a strategy test — its bars must be pre-registered accordingly (e.g., conditional next-session return vs unconditional, significance-style bars), and per the guardrail any LATER use of it as a filter on a live strategy is itself a rule change requiring the two-stage process.
  2. **Body-close S/R convention:** levels marked on candle CLOSE prices (bodies), invalidated only by a close beyond on the timeframe where the level formed (a 5m close does not break a 15m level). Decodable and free — folded into any future level-marking apparatus as the default convention if owner approves (note: consistent with the body-close/no-intersection choice already frozen in 6.1 — a confirmation, not a change).
- **Claimed track record (70%+ win rate at ~1:1, live-streamed for 3 years):** noted as claimed, unverifiable in this framework; per standing rule, no strategy is adopted on claimed win rates.

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
5. Any surviving candidate → two-stage walk-forward → QC confirmation → adoption-bar comparison vs 4.5 → owner decision

**2 Nov live/paper deployments are unaffected by anything in this plan until every bar above reads.**
