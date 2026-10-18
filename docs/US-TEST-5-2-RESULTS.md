# US Test 5.2 — Results (18 Oct 2026)

## Run (first legitimate execution — two prior attempts VOID-by-apparatus: empty script PR #37; off-by-one 252d-max-including-day-d bug PR #40, both fixed before any valid run)

- Apparatus: Mac lab, Yahoo daily snapshot (survivorship caveat applies), data_us 664 tickers,
  2014-01-02..2026-10-09, costs 0.35%/side, gates SPY>SMA200 + breadth>=0.50, top-10 near52w
  rank, monthly rebalance, entry only if rebalance-day close > prior-252d high (shift(1)), no substitutes.
- Output (script commit 2ea29c0):
  EV/trade +1.05% net | trades 167 | positive years 6/13 | maxDD (monthly eq) -38.4% | months in market 42/153

Year-by-year (portfolio monthly mean %): 2016 +0.14, 2017 -0.64, 2018 +1.45, 2019 flat(gate),
2020 +0.64, 2021 +0.71, 2022 flat(gate), 2023 -1.22, 2024 +0.08, 2025 +0.87, 2026 -0.19;
2014/2015 flat (warm-up/gate).

## Bars (frozen in docs/US-TEST-5-2-REGISTRATION.md, read once)

1. EV > +0.60% net: **PASS** (+1.05%)
2. >= 6/13 positive years: **PASS** (6/13)
3. >= 150 trades: **PASS** (167)
4. KEY BAR — beat unconditioned 4.5 baseline EV (+1.40%) by >= +0.30pp (i.e. >= +1.70%): **FAIL** (+1.05%)

## Verdict: FAIL — no adoption

Prediction confirmed: on the SAME 52w-high scan, the breakout entry trigger UNDERPERFORMS
the nearness entry (SGX 3.1b tombstone reconfirmed on US data). The breakout filter is also
far more restrictive (42/153 months in market vs 4.5's fuller exposure) and carries a worse
maxDD (-38.4% vs -23.8% Yahoo-basis). Restrictiveness without EV = complexity with no payoff.

Consequences (per registration):
- No QC follow-up (FAIL path: tombstone stands, zero additional compute).
- 4.5 nearness-trigger remains the US paper variant untouched; 2 Nov deployments unchanged.
- Breakout-vs-nearness question CLOSED on both markets. Class tombstone: breakout entries.
- Next: Test 5.3 (RSI+Fib folklore audit) on the Mac — expected FAIL.
