# Tier 3 Test Plan — External Critique Response

**Status:** Queued · **Created:** 7 Oct 2026 · **Owner:** Fa'rath Shba
**Companion doc:** `docs/TRADING-OPERATING-MANUAL.md` (v2.1) · **Archive copy:** arkenstone `docs/TRADING-OPERATING-MANUAL.md` §14

**Context:** An external AI critique of the Operating Manual raised cost-model, ranking-method, and gating criticisms plus four recommended strategies. Per the guardrail: **nothing is adopted without a backtest.** Every testable claim goes through the same two-stage pipeline that promoted the momentum champion and killed the deeper-dip.

---

## Standing decision bars (pre-registered, unchanged)

- **Stage 1 (full-period):** per-trade EV > +0.6% after costs AND net positive in >= 6 of 10 years
- **Stage 2 (walk-forward):** rules frozen in-sample 2016-21, tested untouched on 2022-26: OOS EV >= +0.6% AND net positive in >= 4 of 5 OOS years
- Cost baseline 0.35%/side — **pending revision by Test 1.1**
- Pre-register hypothesis and bar BEFORE each run. No post-hoc rationalization.

---

## Phase 1 — Cost & friction audit (blocks everything else)

### 1.1 Spread & friction measurement
Measure real bid-ask spreads on the names the champion's top-10 *actually held*:
1. Corwin-Schultz high-low spread estimation on our 10y daily candles (historical baseline)
2. Live Yahoo quote snapshots (bid/ask fields) over several sessions
3. Longbridge quote data where supported
4. Impact estimate for ~S$1,300-5,000 orders vs. each name's dollar-volume

**Output:** revised `--cost-pct` per price band (S$1-2 / S$2-5 / S$5-10) + spread table.
**Pre-registered decision:** if revised round-trip friction is ~1.4% (critique's claim), the champion's +1.24% EV may be an artifact — Test 1.2 decides.

### 1.2 Champion re-validation at revised costs
One run with revised `--cost-pct`. **Pre-registered:** EV < +0.6% -> champion downgrades to provisional; this becomes the project's central problem.

### 1.3 Sizing-integrity audit (Reddit critique, 8 Oct 2026)
Forensic check on the champion's backtest, not a new strategy run:
- Verify position sizing is period-invariant: no equity-curve dependence, no implicit caps that bite only in bad years
- Examine the >10-candidates slot tie-break for hidden state-dependence (does which-10-gets-picked change behavior in crowded markets?)
- Method: code audit + assertion test (same inputs -> identical sizing regardless of period)

### 1.4 Edge-stability decomposition (Reddit critique, 8 Oct 2026)
- Champion win rate and EV decomposed by year and by half
- Profit-concentration analysis: what % of total profit came from the top-N trades?
- Distinguishes "consistently thin edge" from "carried by two big years"
- Must run BEFORE Phase 2 variants — its output determines how variant results are interpreted


---

## Phase 2 — Champion variants (one parameter change per test, both stages)

- **2.1 Skip-window ranking:** rank on t-126 -> t-21 (skip last month) vs. raw t-126 -> t-0. Standard academic practice; skips short-term reversal noise at selection.
- **2.2 Vol-adjusted ranking:** rank score = 126-day return / realized sigma (30d and 60d windows pre-registered as a pair). Hypothesis: raw ranking over-selects high-sigma names; vol-adjustment cuts the champion's -37% maxDD.
- **2.3 Breadth-gate supplement:** gate = ES3 > SMA200 **AND** >50% of tradeable universe above own SMA200. Computable from `data_v3_clean` directly.
- **2.4 Trailing-exit hardening:** close if position falls >2x its 30-day sigma from high-water mark, in addition to rebalance/SMA200 exits. NOT the refuted ATR system — no fixed profit targets, drawdown band only.
- **2.5 Thin-leadership quantification:** numeric rule — mean top-10 126d return below calibrated bottom-quartile threshold -> verdict mechanically states "low-conviction regime". Removes the one discretionary element.
- **2.6 Combined variant** (2.1 + 2.2 together) — mirrors the critique's "risk-adjusted momentum with skip window."

**Adoption rule:** variants passing both stages are A/B'd against the champion; adopted only if they beat it on EV *and* maxDD; merged one at a time in test order so attribution stays clean.

---

## Phase 3 — The critique's proposed strategies (full two-stage treatment, no adoption on claimed win rates)

- **3.1 Volume-breakout expansion (1-5d):** consolidation filter (20d range <8%, >=15 days), entry on close > 20d high with >=2.5x avg volume, stop below breakout low, 2-5d hold. Prior: suspicious — adjacent to the refuted v1 ATR/volume system.
- **3.2 Regime-conditioned support bounce (3-10d):** ES3 > SMA50 gate, pullback to SMA50/Bollinger/Fib with RSI < 35, reversal-candle entry. Prior: LOW — cousin of the deeper-dip that failed walk-forward (OOS EV +0.53%); a failure here is a second tombstone for SGX mean reversion.
- **3.3 Risk-adjusted momentum:** folded into 2.6 — not a separate build. (The critique's "fundamentally different approach" converges on our champion plus two upgrades — itself an informative outcome.)
- **3.4 PEAD (5-20d):** +3% earnings gap on 3x volume, enter t+1/t+2 above candle midpoint, exit on 10/20 SMA cross or 20 days. **Decision (owner, 7 Oct 2026):** build the SGX earnings-date/surprise dataset NOW — data collection runs parallel with Phase 1; the backtest itself waits for revised costs.
- **Survivor rule:** nothing runs alongside the champion by default; a survivor competes in a portfolio test (correlation, combined drawdown) with pre-registered portfolio-level criteria.

---

## Phase 4 — Operational hardening (small engineering, post-packaging)

- **4.1** Structured verdict fields in the snapshot log (gate, breadth, top-10 with scores, low-conviction flag) so chat reads structured state, not prose.
- **4.2** Nightly log-integrity sanity check (entry count vs. trading days elapsed).
- **4.3** Monthly rollup of `_snapshot_log.md` into arkenstone.
- **4.4** Legacy positions: explicit owner decision (hold vs. liquidate E5H/KJ5/A31), documented either way. The system states facts, it does not force liquidation.

---

## Sequencing

1.1 spread audit -> 1.2 champion re-run -> 1.3 sizing audit -> 1.4 edge decomposition -> 2.1 -> 2.2 -> 2.3 -> 2.4 -> 2.6 -> 2.5 (parallel anytime) -> 3.1 -> 3.2 -> 3.4 (data permitting) -> 4.1-4.3. Phase 2/3 runs use revised costs from 1.2.

---

## Explicitly declined (audit trail)

Cloud/serverless migration; relational-DB replacement of the snapshot log; replacing chat with a deterministic rule engine (verdict logic is already script-computed; 4.1 closes the gap); adopting any strategy on the critique's claimed win rates (its 58-64% mean-reversion win-rate claim is contradicted by our own data: 57.4% OOS win rate, still failed on EV).

---

## Owner decisions (recorded 7 Oct 2026 — plan is LOCKED)

1. **Sequencing:** strictly sequential — cost audit (1.1 -> 1.2) before any Phase 2 runs.
2. **PEAD (3.4):** build the SGX earnings-date dataset NOW (data collection runs parallel with Phase 1; the backtest itself waits for revised costs).
3. **Legacy positions:** LIQUIDATE all three (E5H, KJ5, A31) — off-system holdings exit the portfolio.
4. **Sigma window for 2.2:** both 30d and 60d, pre-registered as a pair.
5. **Phase 3 survivor:** portfolio-test against the champion.

---

## Verdict log (fill as tests complete)

| Test | Stage 1 | Stage 2 | Verdict | Date | Notes |
|---|---|---|---|---|---|
| 1.1 Spread audit | — | — | SPREADS HIGHER THAN MODELED | 8 Oct 2026 | CS effective spread median 0.60% on 66 held names (band: 0.63% sub-S$2, 0.48% above). Modeled 0.35%/side too low; Gemini 1.4% rt claim not confirmed. Honest range: 0.85-1.20% rt. 1.2 tests worst case. |
| 1.2 Champion @ revised costs | PASS | pending (Phase 2) | CHAMPION SURVIVES | 8 Oct 2026 | Worst-case 1.20% rt: EV +0.74%, 6/10 yrs. Mid-case 0.90% rt: EV +1.04%, 6/10 yrs. Gemini friction-artifact claim refuted by measurement. New default cost: 0.45%/side. Caveat: thin margin; edge remains regime-dependent per 1.4. |
| 1.3 Sizing-integrity audit | PASS | — | PASS | 8 Oct 2026 | stake P&L-blind, runs deterministic, tie-break stateless; quirks documented; silent gate-off bug fixed (fails closed) |
| 1.4 Edge-stability decomposition | — | — | CONCENTRATED/FRAGILE | 8 Oct 2026 | Top-1 trade = 43% of net profit; top-10 = 229.7% (other 312 net negative); 2022-24 all losing years; all profit from 2025-H2/2026-H1 regime. Edge is regime-dependent, not distributed. |
| 2.1 Skip window | FAIL | FAIL | REJECTED | 8 Oct 2026 | Stage 1: ~5/10 yrs positive (< 6 bar); 2021 flips +6,991 -> -13,333. IS EV collapses to +0.28%; OOS EV +1.25% but 2/5 yrs (< 4 bar). Finding: SGX small-cap momentum lacks short-term reversal noise; the fresh-month return IS part of the edge. Raw 126d window confirmed correct. |
| 2.2 Vol-adjusted (30d/60d) | FAIL | FAIL | REJECTED | 8 Oct 2026 | 30d: EV +0.92% but 5/10 yrs; OOS +0.32% (< bar); 2026 flips negative. 60d: EV +0.42% (< bar); OOS -0.23%. maxDD improved slightly (30d: -33.8% vs -37.6%) but edge destroyed. Finding: high-sigma names ARE the SGX momentum edge; vol-adjustment filters out the payers. |
| 2.3 Breadth gate | PASS | FAIL (year-count) | REJECTED — STRONGEST KNOWN VARIANT | 8 Oct 2026 | Stage 1: EV +2.30%, 6/10 yrs, maxDD -31.1%. OOS: EV +3.26% but 2/5 yrs (< 4 bar — a bar the incumbent also fails). Strict dominance vs champion on all metrics (EV, maxDD, Sharpe, win rate, 2022-24 bleed halved). Concentration improved but not healed: top-5 share 102% (vs 146%); still carried by 2025-H2/2026-H1. Owner decision: HOLD THE BAR — finish Phase 2 before any succession. |
| 2.4 Trailing exit | FAIL | FAIL | REJECTED | 8 Oct 2026 | 15% trailing stop: Stage 1 EV +0.26% (< bar), maxDD unchanged (-36.5%); OOS +0.14%, IS +0.16%. Trades 322->361 (stop->rebuy cost churn); added a 2020 loss. Finding: the edge lives in drawdown-surviving winners; every hold-side overlay tested (skip, vol-adj, trail) filters out the profit source. Hold-through-the-noise edge. |
| 2.5 Thin-leadership threshold | NULL | — | NULL — NO TESTABLE SIGNAL | 8 Oct 2026 | 10% floor never bound (byte-identical to champion); 20% floor bound ~1 month (323 trades, EV +1.03%). Finding: SGX always has a >=20% 126d leader at month-end — thin-leadership months do not exist on this universe. Variant untestable as specified; speculative leadership is perpetual (bull and bleed years alike). |
| 2.6 Combined (2.1+2.2) | — | — | CANCELLED | 8 Oct 2026 | Both components rejected individually; combining rejected variants is moot. A breadth+trail combo is dominated by breadth alone (2.4). |
| 3.1 Volume breakout | — | — | pending | | |
| 3.2 Support bounce | — | — | pending | | |
| 3.4 PEAD | — | — | pending | | |


## PHASE 2 — COMPLETE (8 Oct 2026)
Champion 5, challengers 0: 2.1 skip-window REJECTED; 2.2 vol-adjust REJECTED (both windows); 2.4 trailing exit REJECTED; 2.5 thin-leadership NULL (never binds on SGX); 2.6 CANCELLED (components rejected). Findings: SGX small-cap momentum is a hold-through-the-noise edge — the fresh-month return is signal, high-sigma names are the payers, drawdown-surviving winners carry the edge, and speculative leadership is perpetual.

## CHAMPION SUCCESSION — AMENDMENT (8 Oct 2026)
**Decision (owner):** Test 2.3 (breadth gate, >=50% of universe above own SMA200) is ADOPTED as champion, effective immediately.

**Amended rule (documented post-hoc, with reasoning):** The Stage 2 OOS year-count bar (>=4/5 positive years) is waived for succession ONLY where ALL hold:
  (a) strict dominance vs incumbent on EV, maxDD, Sharpe, and 2022-24 bleed,
  (b) improved profit concentration (top-5 share: 102% vs 146%),
  (c) Stage 1 passed honestly (6/10 years, same terms as incumbent's promotion),
  (d) the incumbent itself fails the bar in the same window.
Rationale: a bar that rejects every system in the tested class — including the incumbent — measures the window, not the variant. The OOS EV bar (>0.6%) is NOT waived and remains binding: 2.3 passes it at +3.26%.

**New champion config:** momentum_backtest.py --breadth 50 --cost-pct 0.45 (data_v3_clean; all other params unchanged: 126d lookback, top-10, min price S$1, min dvol S$1M, ES3>SMA200 regime gate).
**Champion metrics (10y, honest costs):** +59.0% total, Sharpe 0.46, maxDD -31.1%, EV +2.30%/trade, 43.1% win rate, 218 round-trips.
**Standing caveats carried forward:** edge remains regime-dependent (2025-H2/2026-H1 carry it); worst-case-cost sensitivity NOT yet re-run on 2.3; 1.3 sizing-integrity audit was run on the OLD champion's log — rerun on 2.3's log before live deployment.

**Pre-deployment TODOs (gate live capital):**
1. Re-run worst-case cost test (0.60%/side) on 2.3.
2. Re-run 1.3 sizing-integrity audit on 2.3's trade log.
3. Live-quote spread cross-check on 2.3's held names.

## PRE-DEPLOYMENT AUDITS (8 Oct 2026, evening)
1. **Worst-case cost (0.60%/side): PASS.** EV +1.99% (> 0.6 bar), 6/10 positive years, maxDD -31.9%, Sharpe 0.44. Cost sensitivity: 0.35% -> +2.50% EV; 0.45% -> +2.30%; 0.60% -> +1.99%. The worst case at nearly double the OLD champion's mid-case EV (+1.04%). Succession stands unconditionally on costs — no asterisk.
2. **Sizing integrity on 2.3 log: PASS.** Stake P&L-blind; byte-identical reruns; documented quirks deterministic.
3. **Live spread cross-check: PENDING** — requires market hours (SGX 09:00-17:30 SGT).

## PRE-DEPLOYMENT AUDIT 3 — LIVE SPREAD CHECK (9 Oct 2026, ~10:15 SGT, market open)
Basket (champion top-10, live quotes): PCT 0.14%, 558 0.18%, EB5 0.11%, BS6 0.10%, E28 0.20%, HSHD 0.21%, CC3 0.45%, OV8 0.17%, P8Z 0.25%, S58 0.14% (half-spreads).
Median half-spread 0.17%, mean 0.19% vs assumed 0.45%/side: >2x headroom on the basket. VERDICT: PASS — all three pre-deployment gates clear; champion cleared for live capital.
Footnotes: CC3 exactly at 0.45% and thin live volume today (~S$109k) — watch on live fills; quotes are 10-min delayed (indicative, not depth-checked). ES3_SI data file has capitalized headers inconsistent with the rest of data_v3_clean — normalize in a future tidy commit.

## TEST 3.1 — VOLUME BREAKOUT: VERDICT & DIAGNOSTIC (9 Oct 2026)
**STAGE 1: FAIL** — 26 round-trips, EV -0.28%, win rate 42.3%, 1/5 positive years. IS (2016-21): ZERO triggers. OOS identical to full period (all trades post-2022).
**Diagnostics (same day):**
- Adjustment concern cleared: median adjclose/close ratio 1.000 across 395 books; 1 book materially adjusted (0.317). close=adjclose design does not distort breakout logic here.
- Signal anatomy: breakout condition fires 300-500x/yr through 2024, then 1314 (2025) / 1432 (2026) — breakouts are 3-4x more common in the current regime. Consolidation <8% over 20d is the binding filter: intersection with breakout+volume is ~0-26 triggers/yr.
**Finding:** as pre-registered, the strategy is nearly untestable on this universe (26 trades in 10 years, 2/3 in the current bull regime, EV negative). FAIL stands on the measured trades, but this is WEAK evidence against the breakout class — the spec, not the class, strangled the sample. Optional pre-registered sensitivity (3.1b): loosen consolidation to 15% to test the class with an adequate sample; any 3.1b result requires full re-registration and cannot promote on this run's evidence. Class-level tombstone remains premature.

## TEST 3.1b — CLASS PROBE (15% consolidation): BREAKOUT CLASS TOMBSTONED (9 Oct 2026)
Adequate sample: 102 round-trips across 11 years, EV -0.83%/trade, win rate 37.3%, 4/11 positive years. STAGE 1: FAIL.
Key anatomy: 2026 — the champion's best regime, with 1,432 breakout fires — is the breakout's WORST year (-59.81% summed, 41 trades). SGX small-caps that break 20d highs on 2.5x volume mean-revert, not follow through. The class is anti-correlated with the champion's edge: breakout buys the exact event momentum is positioned opposite.
CLASS VERDICT: short-hold volume breakout on SGX small caps is structurally negative after realistic costs — consistent with the v1 refutation, now with adequate sample. Not a promotion candidate, not a diversification candidate. 3.1 CLOSED (class tombstone).

## TEST 3.2 — SUPPORT BOUNCE: FAIL (9 Oct 2026)
**STAGE 1: FAIL** — 52 round-trips, EV -1.39%/trade, win rate 21.2% (catastrophic vs ~45% random baseline), 1/3 positive years. Zero triggers pre-2024; 48/52 trades in 2026 — the conjunction (RSI<35 + bullish candle + support proximity + ES3>SMA50 gate) essentially never co-fires outside the current choppy-hot regime. IS window: NO TRADES.
**Evidence now converging across three tests:** deeper-dip failed walk-forward (+0.53% OOS); breakout loses because names mean-revert (3.1b); buying the dips also loses at 21% win rate (this test). Convergent finding: SGX small-cap short-hold moves — in EITHER direction — are too small to clear ~0.9% round-trip friction. The champion's month-scale hold is not incidental; it is what lets fat-tailed winners amortize the friction. Mean-reversion class tombstone: SECOND, now with convergent (though regime-clustered) evidence. Caveat: 48/52 trades in one year limits class-level confidence; the tombstone is directional, not decisive.

## TEST 3.4-PROXY — POST-GAP DRIFT: FAIL (real but sub-friction) (9 Oct 2026)
**STAGE 1: FAIL** — 56 round-trips, EV +0.23%/trade, 42.9% win rate, 5/10 positive years. IS (2016-21): 16 trades, EV -3.53%. OOS (2022-26): 40 trades, EV +1.73%, 3/5 positive years.
**Anatomy — distinct from 3.1/3.2 failures:** full-period EV is near zero, not negative: post-gap drift on SGX small caps is REAL but TOO SMALL to clear ~0.9% round-trip friction. IS/OOS sign flip: drift only pays in the post-2022 regime (echoing the champion's regime-dependence; small samples, n=16/n=40, so directional only). Unlike breakout, 2026 is roughly flat — not anti-correlated with the champion.
**Consequences:** (1) NO class tombstone — the effect exists; the friction kills it. (2) True-3.4 (announcements dataset) is NOT obviously dead: label purification could concentrate drift, but it would be building from a +0.23% raw base — weak foundation for a multi-week engineering block. Owner decision pending. (3) Strengthens the Phase 3 synthesis: the only short-hold mechanism with theoretical support (information diffusion) is present but sub-cost; every short-hold class tested has been defeated by the same ~0.9% friction wall.

## PHASE 3 — COMPLETE (9 Oct 2026)
Champion 1, challengers 0. 3.1 breakout: FAIL (class tombstone via 3.1b probe — EV -0.83%, anti-correlated with champion). 3.2 support bounce: FAIL (second mean-reversion tombstone, 21% win rate). 3.4-proxy post-gap drift: FAIL on bars but effect real and sub-friction (+0.23% EV, OOS-only; no tombstone). 3.3 remains folded into 2.6 (cancelled with its components). 3.4-true (announcements dataset): PARKED — owner decision 9 Oct 2026 rationale: proxy ceiling measured at +0.23% raw with regime flip; purification must ~3x the effect to clear the bar. Revisit only on regime change.
PHASE 3 SYNTHESIS (the phase's real finding): every short-hold class tested — breakout, dip-buy, event-drift — is defeated by the same ~0.9% round-trip friction wall. The champion's edge is not just momentum; it is the only tested structure that amortizes SGX small-cap friction. This explains the system rather than merely validating it, and it is the standing answer to "why not something else."
Tier 3 state: Phases 1-3 complete; Phase 2 succession adopted (2.3 breadth gate, all pre-deployment gates PASS); Phase 4 (operational hardening) remains, pending deployment sizing decision.

## PHASE 3 — COMPLETE (9 Oct 2026)
Champion 1, challengers 0. 3.1 breakout: FAIL (class tombstone via 3.1b probe — EV -0.83%, anti-correlated with champion). 3.2 support bounce: FAIL (second mean-reversion tombstone, 21% win rate). 3.4-proxy post-gap drift: FAIL on bars but effect real and sub-friction (+0.23% EV, OOS-only; no tombstone). 3.3 remains folded into 2.6 (cancelled with its components). 3.4-true (announcements dataset): PARKED — owner decision 9 Oct 2026 rationale: proxy ceiling measured at +0.23% raw with regime flip; purification must ~3x the effect to clear the bar. Revisit only on regime change.
PHASE 3 SYNTHESIS (the phase's real finding): every short-hold class tested — breakout, dip-buy, event-drift — is defeated by the same ~0.9% round-trip friction wall. The champion's edge is not just momentum; it is the only tested structure that amortizes SGX small-cap friction. This explains the system rather than merely validating it, and it is the standing answer to "why not something else."
Tier 3 state: Phases 1-3 complete; Phase 2 succession adopted (2.3 breadth gate, all pre-deployment gates PASS); Phase 4 (operational hardening) remains, pending deployment sizing decision.
