# Project Status — Evidence-First Trading Blueprint
**Last updated:** 7 Oct 2026 · **Current phase:** Tier 3 (validation-hardening) · **System:** Operating Manual v2.1 (arkenstone docs/)

## Where we are
Build phase COMPLETE. One promoted system (momentum champion: 126d rank, top-10 EW, ES3 SMA200 gate, monthly rebalance) backed by 5 tested verdicts; daily pipeline fully automated (launchd 18:15 SGT -> fetch 598 tickers -> gate + top-10 -> _snapshot_log.md -> SSH push). External critique (Gemini) triaged into the Tier 3 plan; owner decisions recorded; plan LOCKED.

## Completed (Tier 1 + 2)
- ATR stop/target system: RETIRED (-78.9%, refuted) — issue #1
- Momentum champion: PROMOTED (+1.24%/rt, 6/10 yrs, survived fresh-data control)
- Intraday execution: FAILED (2 rules harvested)
- Position sizing: CLOSED (equal-weight top-10 locked)
- Deeper-dip mean reversion: FAILED walk-forward (OOS EV +0.53% < 0.6 bar, 3/5 yrs)
- Automation: launchd job proven, SSH-auth hardened, walk-forward date flags added to backtest scripts

## In progress / next (Tier 3 — issue #3, docs/TIER-3-TEST-PLAN.md)
1. **NEXT BUILD:** Test 1.1 spread-audit script (Corwin-Schultz on champion-held names + live quotes) — decides if the edge survives real friction; 1.2 re-runs champion at revised costs
2. **Owner action pending:** liquidate E5H/KJ5/A31 on Longbridge, report fills
3. Parallel: PEAD earnings-dataset collection (approved)
4. Then Phase 2 variants (2.1 skip-window -> 2.2 vol-adj 30d+60d -> 2.3 breadth gate -> 2.4 trailing exit -> 2.6 combined) and Phase 3 (3.1 volume breakout, 3.2 support bounce, 3.4 PEAD)
5. Phase 4 ops: structured verdict fields, log integrity check, monthly arkenstone rollup

## Key risks / open questions
- Champion's cost assumption (0.7% rt) unverified — Test 1.1 is the gate for everything
- If 1.2 fails: champion downgrades to provisional; priority shifts to survivable variants
- PEAD data availability for 10y SGX history unproven

## Reproducibility
- Data: data_v3_clean (393 tickers x 10y); data_live (rolling 400d, daily)
- Bars: Stage 1 EV > +0.6% & >=6/10 yrs; Stage 2 OOS EV >= +0.6% & >=4/5 yrs (see manual section 9)
