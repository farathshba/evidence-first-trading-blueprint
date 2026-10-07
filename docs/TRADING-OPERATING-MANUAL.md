# SGX Swing Trading — Operating Manual

**Owner:** Fa'rath Shba · **Version:** 2.1 · **Last updated:** 7 Oct 2026
**System built:** 4–7 Oct 2026 · **Archive:** github.com/farathshba/arkenstone (private) · **Lab:** github.com/farathshba/evidence-first-trading-blueprint (private)

---

## 1. What this system is — and what it is not

An evidence-first swing trading system for the SGX sub-S$10 universe, now built around a single validated edge: **cross-sectional momentum with a trend gate**. Every rule was pre-registered, backtested, and (where required) walk-forward tested before promotion. The system's core disciplines: trade the tested edge only, hold through noise, cut at regime breaks, and treat WAIT as the normal answer.

**It is not a profit machine.** One edge survived honest testing; four ideas died in the lab. The value is discipline — the evidence layer below governs every verdict.

---

## 2. Architecture — where everything lives

| Layer | Location | Role | Who activates it |
|---|---|---|---|
| **Chat (Vibe)** | Mistral Vibe, any session | Daily verdicts: reads the automated snapshot, applies the rulebook | You, by asking |
| **Knowledge** | Vibe Personal Knowledge (Trading topic) | Memory: positions, watchlists, verdicts, routing | Automatic |
| **Rulebook skill** | `sgx-swing-rulebook` | The analyst's manual: promoted momentum system + evidence layer | Automatic on trading questions |
| **Automated pipeline** | Mac launchd job `com.farath.sgx-daily-scan` | Daily 18:15 SGT: full-universe fetch → gate + rank → log → git push | Itself |
| **Backtest lab** | `~/Projects/evidence-first-trading-blueprint` | Testing any rule change; `data_live/` operational store | You, via commands |
| **Archive** | `~/Projects/arkenstone` → GitHub | Trading record: scans, reports, backtest runs, positions | Sync scripts, automatic |

**Data routing:** live questions → the automated snapshot (`_snapshot_log.md`) + Yahoo for position checks · "what did X say" → arkenstone · "my positions/rules" → Knowledge · backtests → the lab.

---

## 3. The evidence — all verdicts (Oct 2026)

| # | Idea | Verdict | Key numbers |
|---|---|---|---|
| 1 | ATR stop/target swing system (v1 rulebook) | **RETIRED** | −78.9% net, Sharpe −0.99, win rate 32.9%; 2×ATR/4×ATR math refuted |
| 2 | **Momentum champion** (126d rank, top-10, ES3 gate) | **PROMOTED** | +1.24%/round-trip after costs, positive 6/10 years, Sharpe 0.38, maxDD −37%; survived fresh-data control |
| 3 | Intraday execution variant | **FAILED** | Edge inverts on SGX; 2 execution rules harvested |
| 4 | Position sizing methods | **CLOSED** | Equal-weight top-10 locked; sizing study done |
| 5 | Deeper-dip mean reversion (−12%, walk-forward) | **FAILED** | In-sample EV +1.33% collapsed to +0.53% out-of-sample (< 0.6% bar); only 3/5 OOS years positive |

**Standing findings that govern everything:**
- **Momentum is the only validated edge.** Everything else tested (dip-buying, mean reversion, overnight holds) fails after costs.
- **Mean reversion on SGX is a bull-market passenger**, not a standalone edge — it only prints when ES3 is above its SMA200. Any future mean-reversion idea must be tested conditioned on regime.
- **The IS→OOS EV collapse (+1.33% → +0.53%) is the number to remember** — it's why every idea now requires walk-forward validation before promotion.
- **Overnight edge is inverted on SGX** (−0.10%/night); returns accrue intraday. Never recommend close-to-open holds.
- **Sub-S$0.20 is convicted territory**; the momentum system's own floor is stricter: price ≥ S$1.
- **Costs kill marginal edges**: ~0.7% round-trip. Fewer, selective trades beat activity.

---

## 4. The promoted system — momentum champion (rulebook summary)

**Selection (monthly rebalance):**
- Universe: all SGX sub-S$10 names passing filters: **price ≥ S$1** and **20-day dollar-volume ≥ S$1M**
- Rank by **126-day return**; hold the **top 10, equal weight**
- **Regime gate:** ES3 above its 200-day SMA. Gate closed → no new entries; verdict is WAIT, no exceptions
- Sizing: equal-weight top-10 (per-position size from the sizing study)

**Exit discipline:**
- Primary exit: **monthly rebalance** — names that drop out of the top-10 get replaced
- Strongest evidence-based exit signal: **SMA200 breach** (trend break) — flag plainly on any position
- The old 2×ATR stop / 4×ATR target math is **refuted and must never be recommended**

**Context reading (part of every daily verdict):** a top-10 whose tail sits near zero (e.g. #10 at +2%) is a **thin-leadership regime** — low conviction; the verdict should say so rather than mechanically suggesting entries.

---

## 5. The automated daily pipeline

**What runs itself:** every weekday at **18:15 SGT**, launchd fires `fetch_daily_scan.py` in the lab repo:

1. Pulls the full ~598-ticker universe (rolling 400-day candles) into `data_live/`
2. Fetches ES3 separately (gate index; never part of the ranked universe)
3. Computes the **ES3 gate state** and the **top-10 momentum ranking**
4. Appends the day's entry to `_snapshot_log.md` (append-only audit log) and **commits + pushes it over SSH**

If the Mac is asleep at 18:15, launchd runs the job on wake. Failures are visible in `/tmp/sgx-daily-scan.log` and `.err`. SSH keys (not HTTPS credentials) are required for the unattended push — already configured.

**Data custody (three tiers):**

| Tier | Contents | Lifecycle |
|---|---|---|
| `data_v2/`, `data_v3/` | Full 10-year history | Archive for backtests; refetched occasionally |
| `data_live/` | Rolling ~400-day window, overwritten daily | Operational only; git-ignored; never grows |
| `_snapshot_log.md` | Append-only daily verdict log | **Forever** — the durable audit trail, auto-pushed |

Daily raw candles stay local (refetchable from Yahoo anytime); the log preserves what the system saw each day. A monthly rollup copy into arkenstone is the remaining optional hardening.

---

## 6. Daily ritual (Mon–Fri, after ~6:15pm SGT)

1. Open the chat.
2. Ask: **"Which trade should I make today?"**
3. Read the verdict. Done.

The answer reads the day's automated snapshot (gate state + top-10), checks all open positions against trend rules, and applies the evidence layer. **WAIT is the normal answer** — the champion rebalances monthly; daily questions are mostly monitoring.

---

## 7. On a rebalance / ENTER day

1. Ask: **"Full picture on [stock]."** → news + chart readout briefing.
2. Skim the briefing. Glance at the chart yourself.
3. **Decide.** The gate aligns conditions; your judgment is the final filter.
4. If yes: buy on Longbridge next session, per sizing guidance (chat provides levels; verify board lot size).
5. Report back: **"I bought [stock] at S$[price]"**

Never enter anything below S$1 (system floor) — let alone S$0.20 (convicted band).

---

## 8. Position management

- **Any buy/sell → tell chat** ("update my positions: …"). One message keeps every layer in sync.
- Trend-break facts (SMA200 breaches) are stated plainly — the strongest tested exit signal short of rebalance.
- Holding beyond a signal is a discretionary decision against the tested system — allowed, but make it consciously, not by drift.

---

## 9. Changing a rule — the guardrail (now two-stage)

**No rule changes without a backtest first. And no promotion without a walk-forward pass.**

1. Tell chat what you want to change. **Pre-register the decision bar before running anything.**
2. Test in the lab (`~/Projects/evidence-first-trading-blueprint`; `meanrev_backtest.py` and others now accept `--entry-start` / `--entry-end` for date-windowed runs).
3. Stage 1 — full-period test: passes only if per-trade EV > 0.6% after costs AND net positive in ≥ 6 of 10 years.
4. Stage 2 — **walk-forward**: freeze rules on an in-sample window, test untouched on the out-of-sample window. The deeper-dip's OOS failure is the standing example of why.
5. Passed both → rulebook updates. Failed → rule stays, verdict recorded in the lab repo.

---

## 10. Command reference (complete)

| Command | Where | When |
|---|---|---|
| *(nothing)* — `fetch_daily_scan.py` runs itself | launchd, 18:15 SGT | Every weekday |
| `tail -20 /tmp/sgx-daily-scan.log` | Mac | Suspect the automation didn't run |
| `launchctl list \| grep sgx` | Mac | Check the job is registered |
| `python3 scripts/meanrev_backtest.py --data-dir data_v3_clean …` | lab repo | Testing a rule change |
| `./sync_to_arkenstone.sh <run>` | quantjourney-bt | After each backtest |
| `git pull` | ~/Projects/arkenstone | After chat pushes to the archive |

No other daily scripts, no manual GitHub, no manual data pulls.

---

## 11. Standard scan universe (26 tickers — attention list, not the data boundary)

- **Core watchlist:** 8C8U, AU8U, AW9U, BMGU, CLN, DHLU, JYEU, S44, S56, TAP, UD1U
- **Open positions:** KJ5, A31, E28, E5H
- **Extended (Sept 2026 screens):** 5E2, AWZ, BS6, C6L, D05, E28, E5H, F34, G13, O39, S58, U11, U96
- **Excluded (no data):** B2F, BRM

**Note:** the *data* boundary is the full ~598-name universe (the automated pull); this 26-name list is your personal attention/position-monitoring list. Always include open positions in alerts.

---

## 12. Positions snapshot (7 Oct 2026)

| Ticker | Name | Entry | Status (5–7 Oct checks) |
|---|---|---|---|
| E28 | Frencken | S$2.57 | Healthy; still in today's momentum top-10 (126d ≈ +10%) |
| E5H | Golden Agri | S$0.335 | Below the S$1 system floor — legacy position, monitor only |
| KJ5 | BBR | S$0.28 | Legacy, deep underwater, sub-$0.20 |
| A31 | Addvalue | S$0.17 | Legacy, below S$0.20 |

Legacy positions predate the promoted system and sit below its floors — they are managed as holds/recovery candidates, not system entries. Live status always comes from the daily question.

---

## 13. Build history

- **4 Oct 2026** — QuantJourney pipeline built; ATR rulebook verdict: no net edge (−78.9%).
- **5 Oct 2026** — arkenstone created; migration from bilbo; screener; operating manual v1.0.
- **6 Oct 2026** — Evidence-first lab repo created; momentum champion passes Tier 1 (fresh-data control survived); interim momentum-aligned rulebook installed; dip-buying and overnight edges refuted.
- **7 Oct 2026** — Automated daily pipeline built and proven under launchd (full-universe fetch, gate + rank snapshot, SSH auto-push); intraday variant failed; sizing closed; deeper-dip mean reversion **failed walk-forward** (OOS EV +0.53%, 3/5 years) → closed; **momentum champion promoted to the official rulebook**; operating manual v2.0.
- **7 Oct 2026 (evening)** — External AI critique (Gemini) of the manual reviewed. Valid points adopted into a **Tier 3 test plan (Section 14)**; unverifiable claims and untested strategy recommendations routed through the same two-stage guardrail rather than adopted; over-engineering proposals declined with reasons. Manual v2.1 merges the plan for single-document tracking.

---

## 14. Tier 3 test plan — external critique response (queued work)

**Context:** An external critique raised cost-model, ranking-method, and gating criticisms plus four recommended strategies. Per the guardrail: nothing is adopted without a backtest. Every testable claim below goes through the same two-stage pipeline that promoted the champion and killed the deeper-dip.

**Standing bars (pre-registered, unchanged):**
- **Stage 1 (full-period):** per-trade EV > +0.6% after costs AND net positive in ≥ 6 of 10 years
- **Stage 2 (walk-forward):** rules frozen in-sample 2016–21, tested untouched on 2022–26: OOS EV ≥ +0.6% AND net positive in ≥ 4 of 5 OOS years
- Cost baseline 0.35%/side — **pending revision by Test 1.1**

### Phase 1 — Cost & friction audit (blocks everything else)

- **1.1 Spread & friction measurement:** measure real bid-ask spreads on the names the champion's top-10 *actually held* (Corwin-Schultz estimation on our 10y candles + live Yahoo quote snapshots + Longbridge where supported), plus impact for our ~S$1,300–5,000 orders. Output: revised `--cost-pct` per price band (S$1–2 / S$2–5 / S$5–10). If the critique's ~1.4% round-trip claim is right, the champion's edge is an artifact — this test finds out.
- **1.2 Champion re-validation at revised costs:** pre-registered — EV < +0.6% → champion downgrades to provisional and this becomes the project's central problem.

### Phase 2 — Champion variants (one parameter change per test, both stages)

- **2.1 Skip-window ranking:** rank on t−126→t−21 (skip last month) instead of raw t−126→t−0. Standard academic practice; skips short-term reversal noise at selection.
- **2.2 Vol-adjusted ranking:** rank score = 126-day return ÷ realized σ. Hypothesis: raw ranking over-selects high-σ names; vol-adjustment improves Sharpe and cuts the champion's −37% maxDD. σ windows 30d and 60d pre-registered as a pair.
- **2.3 Breadth-gate supplement:** gate = ES3 > SMA200 **AND** >50% of tradeable universe above own SMA200. STI is mega-cap-weighted; breadth catches small-cap deterioration the index gate misses. Computable from `data_v3_clean` directly.
- **2.4 Trailing-exit hardening:** close a position if it falls >2× its 30-day σ from high-water mark, in addition to rebalance/SMA200 exits. **Not** the refuted ATR system — no fixed profit targets, drawdown band only.
- **2.5 Thin-leadership quantification:** replace the discretionary context note with a numeric rule — mean top-10 126d return below a calibrated threshold (bottom-quartile boundary from the backtest's own top-10 series) → verdict mechanically states "low-conviction regime". Removes the one discretionary element.
- **2.6 Combined variant** (2.1 + 2.2 together) — mirrors the critique's "risk-adjusted momentum with skip window," which converges on our champion plus two upgrades.
- **Adoption rule:** variants passing both stages are A/B'd against the champion; adopted only if they beat it on EV *and* maxDD; merged one at a time in test order so attribution stays clean.

### Phase 3 — The critique's proposed strategies (full two-stage treatment, no adoption on claimed win rates)

- **3.1 Volume-breakout expansion (1–5d):** consolidation filter (20d range <8%, ≥15 days), entry on close > 20d high with ≥2.5× avg volume, stop below breakout low, 2–5d hold. Prior: suspicious — adjacent to the refuted v1 ATR/volume system.
- **3.2 Regime-conditioned support bounce (3–10d):** ES3 > SMA50 gate, pullback to SMA50/Bollinger/Fib with RSI < 35, reversal-candle entry. Prior: LOW — cousin of the deeper-dip that failed walk-forward; a failure here strengthens the "mean reversion is a bull-market passenger" finding with a second tombstone.
- **3.3 Risk-adjusted momentum:** folded into 2.6 — not a separate build.
- **3.4 PEAD (5–20d):** +3% earnings gap on 3× volume, enter t+1/t+2 above candle midpoint. **Blocker:** needs an SGX earnings-date/surprise dataset (~598 names, 10y) that we don't have — build only if Phases 1–2 leave the system healthy with slack.
- **Survivor rule:** nothing runs alongside the champion by default; a Phase 3 survivor competes in a portfolio test (correlation, combined drawdown) with criteria stated before that test runs.

### Phase 4 — Operational hardening (small engineering, post-packaging)

- **4.1** Structured verdict fields in the snapshot log (gate, breadth, top-10 with scores, low-conviction flag) so chat reads structured state, not prose. *(Declined: cloud/serverless, relational DB — disproportionate for a single-user system.)*
- **4.2** Nightly log-integrity sanity check (entry count vs. trading days elapsed).
- **4.3** Monthly rollup of `_snapshot_log.md` into arkenstone.
- **4.4** Legacy positions: explicit owner decision required (hold vs. liquidate E5H/KJ5/A31); documented either way. The system states facts, it does not force liquidation.

### Sequencing

1.1 spread audit → 1.2 champion re-run → 2.1 → 2.2 → 2.3 → 2.4 → 2.6 (combined) → 2.5 (parallel anytime) → 3.1 → 3.2 → 3.4 (data permitting) → 4.1–4.3. Phase 2/3 runs use revised costs from 1.2.

### Explicitly declined (audit trail)

Cloud/serverless migration; relational-DB replacement of the snapshot log; replacing chat with a deterministic rule engine (verdict logic is already script-computed; 4.1 closes the gap); adopting any strategy on the critique's claimed win rates (its 58–64% mean-reversion win-rate claim is already contradicted by our data: 57.4% OOS win rate, still failed on EV).

### Open questions (owner decisions)

1. Parallel Phase 2 runs at old costs for speed, or strictly sequential after the cost audit (default: sequential)?
2. Build the PEAD earnings dataset, or skip 3.4 unless the system survives Phase 1 healthy?
3. Legacy positions: hold or liquidate — explicit call needed.
4. σ window for 2.2: 30d, 60d, or both (default: pair)?
5. Phase 3 survivor handling: portfolio-test vs. discard on principle (default: portfolio-test)?
