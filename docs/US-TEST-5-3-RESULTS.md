# US Test 5.3 — Results (18 Oct 2026)

## Run (first legitimate execution — v1 was VOID-by-apparatus: same-window rolling leg_low made the pocket unreachable, 0 trades; fixed per registration PR #43, verified on synthetic perfect setups pre-push)

- Apparatus: Mac lab, Yahoo daily snapshot (SURVIVORSHIP CAVEAT APPLIES), data_us 664 tickers,
  2014-01-02..2026-10-09, costs 0.35%/side, hold 21d non-overlapping, no regime gates
  (audits the setup itself).
- Rule: 50EMA>200SMA; swing leg = 90d min close PRIOR TO 90d max high, zone from swing high;
  close in 38.2-61.8% golden pocket; mechanical RSI divergence (new 5d low while RSI(14) above
  its 10d min); entry at signal close.
- Output (script commit e0edf3a):
  EV/trade +0.90% net | trades 1,630 | positive years 10/13

Year-by-year (mean net %): 2014 -3.48, 2015 -1.99, 2016 +1.57, 2017 +1.93, 2018 +0.07,
2019 +2.02, 2020 +4.84, 2021 +1.91, 2022 +1.81, 2023 -3.21, 2024 +0.43, 2025 +2.44, 2026 +0.02.

## Bars (frozen in Tier 5 plan, read once)

1. EV > +0.60% net: **PASS** (+0.90%)
2. >= 6/13 positive years: **PASS** (10/13)
3. >= 150 trades: **PASS** (1,630)

## Verdict: STAGE 1 PASS — AGAINST PREDICTION (expected FAIL)

The folklore survived its mechanical translation. Prediction record: wrong — and by the
standing evidence rule that UPGRADES suspicion rather than the result:

**QC/AlgoSeek survivorship-free confirmation REQUIRED before any adoption.** Rationale
(5.1 precedent, 17 Oct): Yahoo today-snapshot data inverted a +1.20pp Stage 1 edge into
-1.32pp on survivorship-free data. Same apparatus, same universe class (US$1-10
microcaps), same failure mode candidates: (a) delisted names that later died are simply
absent from this snapshot; (b) 2020's +4.84% year may carry crash-rebound names that no
longer exist; (c) 1,630 trades at +0.90% is a thin edge near the friction wall.

Additional flag (registration-miss pattern, cf. 5.1 maxDD): the run does not compute
portfolio-level maxDD or overlap exposure — 21d holds with 1,630 trades means heavy
concurrent positions; concentration/drawdown risk UNMEASURED. QC port must report it.

## Next gate

Port to QC LEAN (same frozen rule, same bars, AlgoSeek 2014-2026), single run, same
one-reading discipline. NO adoption, NO paper registration, NO rule changes before the
QC verdict. If QC inverts (as 5.1 did): tombstone with survivorship-artifact provenance.
