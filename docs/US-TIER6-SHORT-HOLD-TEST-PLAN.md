# US Tier 6 — Short-Hold Folklore Test Plan (Tori Trades Break & Retest)

**Status:** REGISTERED (bars frozen below BEFORE any code). No bars may change after the first run. One registered run per test, no gate-widening (4.2 precedent).
**Owner decisions locked 22 Nov 2026:** market = US microcaps (frozen 4.5 universe), sequence = daily Stage 1 first, intraday only if Stage 1 passes.

---

## Source being tested

- **Video:** "Give Me 33 Minutes and You'll Never Place a Dumb Trade Again" — Tori Trades (Victoria Duke), youtube.com/watch?v=zai2jojP1hY
- **Strategy as taught:** trendline break-and-retest with top-down multi-timeframe analysis; entry on retest + candle-close confirmation; stop at the opposing trendline; exit either on opposing-trendline violation (trailed) or at a support/resistance take-profit
- **Taught on:** E-mini / Micro Dow Jones futures (intraday-to-swing holds). We test the *decodable core* on the US microcap universe, so friction is harsher here than in her venue — that gap is itself part of the test.
- **Third-party decode cross-checked:** app.faketrades.in/s/give-me-33-minutes... (same-rule backtest on Indian data: +0.31R expectancy, 36% win rate, negative in 4/9 years, maxDD −21%) — used to sanity-check the mechanical translation only; NOT evidence for adoption.

**Standing verdicts this plan must respect:** breakout class tombstoned both markets (3.1b, 5.2, 4.7b — breakout strictly underperformed nearness on the same scan); Brooks EMA-pullback and RSI family dead on both markets; friction wall (~0.9% round trip on SGX; 35bps/side model on US) governs all short-hold structures. **Registered prediction: FAIL for every test in this plan.** A pass would be as suspicious as 5.1 — QC/AlgoSeek survivorship-free confirmation is mandatory before any Stage-1 pass is believed (three prior Yahoo-snapshot inversions: 5.1, 5.3, and the 5.1-QC sanity fail).

---

## Mechanical translation (frozen before any run)

The video is deliberately subjective ("capture as many touch points as possible", "wiggle room", redraw when pierced). To make it testable, every subjective choice is replaced by a fixed rule. These definitions are FROZEN.

### Trendline construction (per symbol, per timeframe)
- **Pivots:** swing highs/lows via fractal window W=5 bars on each side (5.4-registered style).
- **Down-trendline** = line through the two most recent consecutive lower swing highs; extend right. **Up-trendline** = mirror on swing lows.
- **Touch validity:** bar high/low within ±0.25 × ATR(14) of the line counts as a touch. A line needs ≥ 2 anchor points to exist.
- **No-intersection rule (her core rule):** if any bar's body CLOSE crosses the line between anchors, the line is invalidated and rebuilt from the next valid pair. *Body-close, not wick* — this is the frozen operationalization of her "price can't pierce, but incorporate wick within buffer" instruction. "Wiggle room" is NOT tested (advanced topic, deliberately excluded, registered as out of scope).

### Top-down filter
- Multi-timeframe MTHLY→W→D hierarchy as in video is replaced by the frozen two-level gate already validated on this universe: **SPY > SMA200 AND universe breadth ≥ 0.50**, evaluated with 1-bar lag (shift(1) look-ahead idiom, per execution_sim lesson). Her "top-down trend bias" maps onto the regime gate; nothing new is invented.

### Test 6.1 — Break & Retest, DAILY (Stage 1, Mac/Yahoo)
**Trigger sequence (all three required, per transcript):**
1. **Break:** daily close crosses the active trendline (close beyond line, evaluated with lag).
2. **Pullback & retest:** within N=10 bars after the break, price returns and touches the broken line from the other side (touch rule above).
3. **Candle closure:** the retest bar CLOSES on the far side of the line (i.e., does not close back through). Entry next bar open.
- **Direction:** long-only execution per owner rule; short-side examples in the video are mapped to the long mirror (up-trendline break → long on retest).
- **Stop/exit (her Option A):** opposing trendline redrawn steeper at entry (anchored on the retest swing and prior pivot, same construction rules); position closed at the next daily close violating that line. No fixed stop, no target — matches her "no set take-profit, trail the trend" mode.
- **Holds:** short by construction (days to weeks) — this is the friction-wall exposure.
- **Run:** 2014-01 → 2026-10, 0.35%/side primary, 0.55% stress, frozen 4.5 universe (US$1–10, dvol ≥ US$3M), survivorship caveat flagged on Yahoo snapshot.

### Test 6.2 — Exit head-to-head (paired, ZERO new bars consumed — 4.7b precedent)
Same trades as 6.1. Arm A = opposing-trendline exit (6.1 as run). Arm B = her Option B: S/R take-profit placed at the most recent confirmed swing high BEFORE the entry bar (frozen: most recent pivot high with ≥ 3 touches within 0.25×ATR in the prior 60 bars; if none qualifies, top of the retest swing), nudged 0.25×ATR below the level (her "bump it a few ticks"). Same stop, whichever exit hits first closes the trade. **Key bar: Arm B EV − Arm A EV ≥ +0.30pp** for the S/R exit to be considered an improvement. Prediction: no separation (FAIL registered).

### Test 6.3 — Intraday 15m break & retest (ONLY IF 6.1 clears Stage 1 bars)
- Same frozen rules on 15-minute bars, 1h-bars lines for the bias (video's own 1h example), same/day-or-so holds, force-close EOD (intraday-scaled, 5.4-style).
- **Data route:** LEAN CLI local minute data (owner-decided route for 5.4–5.6; docs/RUNBOOK-5-4-5-6-LEAN-CLI.md applies — single-ticker download test first, IBKR 1-min bulk as fallback). Universe cap and segment splits pre-registered in-apparatus before the run, per 5.4–5.6 precedent.
- If 6.1 fails Stage 1, 6.3 is VOID-by-precedent: no intraday upgrade of a dead signal (registered now so it cannot be argued later).

---

## Frozen bars (all tests)

| Bar | Threshold |
|---|---|
| EV/trade (net, 0.35%/side) | > +0.60% |
| Positive years | ≥ 6/13 |
| Trade count | ≥ 150 (else VOID-by-feasibility) |
| OOS (walk-forward, 2022–26) | EV ≥ +0.60% AND ≥ 4/5 positive years |
| Stress @ 0.55%/side | EV > 0 (passes-at-0.35-dies-at-0.55 = FAIL; 4.6 lesson) |
| Two-stage guardrail | Stage 1 full-period → Stage 2 walk-forward, pre-registered bars only |
| Confirmation bar | Any Stage 1 PASS triggers mandatory QC/AlgoSeek survivorship-free re-run before adoption (5.1/5.3 inversion precedent); maxDD reported (informational, 5.3 miss lesson) |

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
4. Any surviving candidate → two-stage walk-forward → QC confirmation → adoption-bar comparison vs 4.5 → owner decision

**2 Nov live/paper deployments are unaffected by anything in this plan until every bar above reads.**
