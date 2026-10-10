# PHASE-US-1 RUNBOOK — US Sub-US$10 Expansion Track (v1.0)

**Status:** PRE-PROJECT — decision recorded 10 Oct 2026. No US capital deploys until every gate in this document is passed.
**Companion docs:** `docs/TIER-3-TEST-PLAN.md` (SGX evidence base), `docs/PHASE-4-RUNBOOK.md` (SGX live deployment — unaffected by this track).
**Standing rule:** the US track is a separate lab. It must NEVER touch the SGX champion deployment (first live rebalance 2 Nov 2026), its capital, or its rebalance schedule.

---

## 0. Decision record (10 Oct 2026)

- Owner considered closing ALL SGX holdings and pivoting to US markets. Rejected after evidence review.
- **SGX side (UNCHANGED):** all holdings kept (E28 = rulebook HOLD, in momentum top-10). The three legacy liquidation decisions (E5H, KJ5, A31) stand as previously decided. Champion 2.3 deploys S$5,000 at the 2 Nov 2026 rebalance per `docs/PHASE-4-RUNBOOK.md`.
- **US side (NEW):** owner wants a validated US sub-US$10 swing system. Path: research → pre-registered backtests → paper trading (weeks-to-months) → live capital, only if every gate passes. Zero capital commits before Phase 3.
- **Broker (deferred):** zero-commission brokers monetize via FX spread (moomoo ~0.2–0.5%, Tiger ~0.15%, Webull conversion spread); IBKR near-zero FX (~0.002%) with tiered per-share pricing. Decision deferred until Phase 3 — instrument choice follows evidence, not marketing.

## 1. Why the SGX results do NOT transfer automatically

Two findings from the SGX lab bound this project, one in each direction:

1. **Friction wall (SGX-specific):** every short-hold family died because SGX round-trip friction ≈ 0.9%. US friction on liquid small caps is materially lower (cent-level spreads; effective round trip plausibly <0.3% incl. fees). Lower friction means the SAME bars are easier to clear — so a US PASS is not cheap, and the tombstoned families cannot be "revived" without a fresh pre-registration (their sub-friction verdicts were cost-relative, not absolute).
2. **Validated edge (hypothesis, not fact):** 126d momentum + gates survived SGX. Whether it survives US sub-US$10 is an open empirical question — the US small-cap regime, shorting pressure, and sector rotation differ. It gets tested, not assumed.

Standing constraints that DO transfer unchanged: long-only; pre-registration before any run; two-stage guardrail; verdicts logged in repo issues; no adoption on claimed win rates (including Reddit/YouTube/vendor claims — the strategy hunt of 10 Oct found zero families not already in the test plan).

## 2. Universe definition (Phase 0)

- **Universe:** US-listed common stocks, price US$1–10, **20-day dollar-volume ≥ US$3M** (higher than SGX's S$1M — US data includes true trash at the bottom; floor is a pre-registered parameter, tunable in Stage 1 sensitivity only if pre-registered).
- **Exclusions (pre-registered):** OTC/pink sheets, ADRs, SPACs pre-deal, leveraged ETFs, unit trusts, tickers flagged delisted.
- **Data source:** yfinance daily (same engine as SGX lab; loader lessons already paid: MultiIndex columns, tz-aware indices, lowercase headers, `n/a` handling). Fallback: Stooq.
- **Survivorship care (mandatory — new risk class):** US delistings are frequent and silently removed from yfinance. The universe snapshot must be point-in-time honest: today's fetch defines TODAY's candidates for paper trading; for the historical backtest, accept the known survivorship caveat explicitly in the verdict OR source a delisting-aware list before Stage 1 is considered final. This is pre-registered as the #1 validity threat.
- **Sector data note:** if sector classification is ever needed, Yahoo's US coverage is excellent (the 58% SGX coverage problem was SGX-specific).

## 3. Backtest spec (Phase 1) — replicate champion spec, US-localized

- **Selection:** top-10 by 126-day return, equal weight, monthly rebalance (first trading day of month).
- **Gates:** SPY (or SPY-proxy) > SMA200 regime gate; breadth ≥ 50% of universe above SMA200. Both required for entries; either closed → flat.
- **Costs:** 0.35%/side baseline (US friction measured assumption, to be re-based on live paper fills), stress at 0.55%/side.
- **Lookback requirement:** ≥260 trading days of history per name.
- **Bars (Stage 1, full sample 2016–2026):** EV/trade > +0.6% after costs AND ≥ 6/10 positive years. **Stage 2 (walk-forward):** freeze IS 2016–21, untouched OOS 2022–26: OOS EV ≥ +0.6% AND ≥ 4/5 positive years.
- **VOID conditions:** <150 trades in Stage 1; survivorship contamination demonstrably >2pp of EV (audit pre-registered); data coverage <90% of universe.
- **Challengers:** tombstoned SGX families may be re-tested ONLY with fresh pre-registration (each is a new Test 4.x). Priority order if the champion replicates: none — protect the replication first. If the champion FAILS: document the failure mode before any challenger work.

## 4. Paper trading (Phase 2)

- **Duration:** minimum 8 weeks, target 3 months (owner decision: weeks-to-months; this document sets the floor).
- **Execution:** paper account (Webull/moomoo paper, or manual ledger against daily closes — decided at Phase 2 entry).
- **Pass gate to Phase 3:** ≥10 simulated fills; mean realized cost/side ≤ 0.55%; tracking error vs backtest replay ≤ 10pp/quarter; all rulebook verdicts followed without exception (behavioral gate, same as SGX Phase 4).
- **Kill/park:** any behavioral breach (undocumented discretionary trade) → restart the clock.

## 5. Live capital (Phase 3)

- Only after Phases 0–2 pass. Capital sizing: same maxDD-based logic as SGX (size to documented drawdown vs tolerance).
- Broker: IBKR (near-zero FX) unless live paper fills show an alternative is materially cheaper at actual position sizes.
- Ramp and kill criteria: mirror SGX Phase 4 runbook (behavioral, never P&L).

## 6. Governance

- All pre-registrations land on `main` via PR BEFORE any run (standing constitution).
- Verdicts logged in `docs/TIER-3-TEST-PLAN.md` style — new doc `docs/US-TEST-PLAN.md` once Test 4.1 is pre-registered.
- Solo-maintainer rules, branch protection, and CODEOWNERS discipline apply to this track identically.
- The SGX repo's evidence, snapshot pipeline, and rebalance records remain the source of truth for SGX; the US track adds its own scripts under `scripts/us/` and results under `results/us/`.

## 7. What "done" looks like (any branch)

- **PASS:** a US system that cleared Stage 1 + Stage 2 + paper gates, deployed at sized capital, with its own runbook — and the SGX champion untouched.
- **FAIL:** documented evidence that the champion does not replicate on US sub-US$10 (or fails Stage 2) — a real finding, recorded, and SGX remains the sole live system.
- **PARK:** any gate VOID — data inadequate (survivorship, coverage) — revive only when the data condition is met, with fresh pre-registration.

---
*Prepared 10 Oct 2026. This document is the pre-project commitment record. Amend only via PR.*
