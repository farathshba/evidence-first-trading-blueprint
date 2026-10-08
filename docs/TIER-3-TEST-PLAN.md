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
| 2.4 Trailing exit | — | — | pending | | |
| 2.5 Thin-leadership threshold | — | — | pending | | |
| 2.6 Combined (2.1+2.2) | — | — | pending | | |
| 3.1 Volume breakout | — | — | pending | | |
| 3.2 Support bounce | — | — | pending | | |
| 3.4 PEAD | — | — | pending | | |
