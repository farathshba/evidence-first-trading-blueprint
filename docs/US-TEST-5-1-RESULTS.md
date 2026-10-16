# Test 5.1 Results — ADR-Conditioned Champion (Stage 1, 16 Oct 2026)

Registered plan: docs/US-TIER5-TEST-PLAN.md. Apparatus: Mac lab, Yahoo daily snapshot
(survivorship caveat applies). Runs: results/us_5_1_baseline.txt and results/us_5_1_adr4.txt.

## Numbers (0.35%/side costs, 2014-2026, near52w top-10 monthly)

| Metric | Baseline (4.5) | ADR >= 4.0% |
|---|---|---|
| EV/trade net | +1.40% | +2.60% |
| Trades | 560 | 559 |
| Positive years | 7/13 | 7/13 |
| MaxDD (monthly eq) | -23.8% | **-49.8%** |

## Frozen bars read
- EV > +0.60%: PASS (+2.60%)
- Beat baseline by >= +0.30pp: PASS (+1.20pp)
- Trades >= 150: PASS (559)
- Years >= 6/13: PASS (7/13)

**VERDICT: Stage 1 PASS (screening-grade).**

## Honest flags (on record)
1. **MaxDD doubled to -49.8%** — was not a registered bar (registration miss, noted for
   future plans). Does not overturn the verdict, but deployment-relevant: if ever adopted,
   argues for smaller capital despite higher EV.
2. **Survivorship caveat applies** — today-only Yahoo snapshot. High-vol survivors carry
   flattering histories; the +2.60% may partly be snapshot bias. **QC/AlgoSeek survivorship-free
   confirmation REQUIRED before any adoption.** (Same path as 4.5 -> PR #28.)

## Status
- Next gate: QC survivorship-free confirmation of the ADR-conditioned variant.
- 2 Nov deployments unchanged: 4.5-US paper rebalance runs on the UNCONDITIONED registered
  variant; 5.1 does not touch live/paper plans until confirmed.
- Tests 5.2 (breakout trigger) and 5.3 (RSI+Fib) still queued, unchanged.
