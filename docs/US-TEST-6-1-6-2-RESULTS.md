# Test 6.1 / 6.2 — Registered Run Results (Day 1, 23 Nov 2026)

Execution venue note: run by Vibe agent in remote sandbox (Python/pandas, data-analysis bundle), same repo code and same repo data as the owner's Mac would use. Determinism check rerun is byte-identical.

## Apparatus (pre-run, before the registered run)
- Repo pulled at main (squash merges #56–#62 included).
- **Loader patch (pre-run, mechanics untouched):** `load_csv()` expected capitalized headers (`Date`, `Open`, ...); `data_us/*.csv` use lowercase (`date`, `adj close`, ...). Patched to rename columns case-insensitively; no strategy logic touched. This is the committed version of `scripts/us/us_6_1_break_retest.py`.
- Probe (2014-01-01 → 2019-12-31, 3 files, `--probe`): `PROBE MODE: trades=51 on 3 files — inspect before any real run`. No exceptions, dates sane, trades nonzero. No bar reading off the probe.

## Registered run — Test 6.1 Arm A (retest entry, opposing-trendline exit)
Command: `python3 scripts/us/us_6_1_break_retest.py --data-dir data_us --spy data_us/SPY.csv --start 2014-01-01 --end 2026-10-31` — ONE registered run.

- trades = **15,578**, EV net 0.35%/side = **+2.86%**, positive years **10/12** (2014 had zero trades: universe files start 2014/2015+)
- Year-by-year (n, EV gross-of-nothing, net per trade):

| year | n | ev |
|---|---|---|
| 2015 | 360 | +0.1694 |
| 2016 | 373 | -0.0305 |
| 2017 | 617 | +0.1183 |
| 2018 | 498 | +0.1121 |
| 2019 | 503 | +0.0205 |
| 2020 | 677 | +0.1420 |
| 2021 | 1186 | +0.0487 |
| 2022 | 433 | +0.0252 |
| 2023 | 1843 | +0.0793 |
| 2024 | 2655 | +0.0199 |
| 2025 | 2880 | +0.0200 |
| 2026 | 3553 | -0.0465 |

Stress (0.55%/side): EV **+2.46%**, 10/12 years, 15,578 trades.

## Registered run — Test 6.2 Arm B (paired, fixed 1:2 target exit)
Same command with `--arm-b`, same market data (N identical = 15,578).

- EV net 0.35% = **+4.25%**, positive years **12/12**
- Stress (0.55%/side): EV **+3.85%**, 11/12 years
- Paired key bar: **B − A = 4.25 − 2.86 = +1.39pp ≥ +0.30pp** → Arm B beats Arm A on the registered head-to-head key bar.
- Arm B year-by-year ev: 2015 0.0464, 2016 0.0445, 2017 0.0663, 2018 0.0607, 2019 0.0352, 2020 0.0638, 2021 0.0549, 2022 0.0021, 2023 0.0561, 2024 0.0268, 2025 0.0530, 2026 0.0291.

## Determinism check
Rerun of 6.1 Arm A (full period) is **byte-identical** to the registered run (SKIP lines from `_manifest.csv` excluded, `_manifest` is not price data). Then STOP — one registered run per test respected.

## Bar reading (single reading, pre-registered bars)

| Bar (registered) | 6.1 Arm A | 6.2 Arm B |
|---|---|---|
| EV net 0.35% > +0.60% | +2.86% PASS | +4.25% PASS |
| ≥ 6/13 positive years | 10/12 (no 2014 trades) PASS | 12/12 PASS |
| ≥ 150 trades | 15,578 PASS | 15,578 PASS |
| Stress 0.55% still PASS | +2.46% PASS | +3.85% PASS |
| B − A ≥ +0.30pp | — | +1.39pp PASS |

## Verdict (Stage 1)
**6.1 Stage-1 PASS on Yahoo-snapshot apparatus; 6.2 paired-exit PASS with Arm B superior.** No verdict language beyond bar reading; no gate widening; numbers not revisited.

**Hard cautions before anyone believes this PASS:**
1. **Yahoo-snapshot inversion precedent (Tests 5.1, 5.3):** any Stage-1 pass at 0.35% MUST be re-confirmed survivorship-free on QC/AlgoSeek (or equivalent point-in-time, delusion-inclusive data) BEFORE it is believed. The 666-file `data_us/` universe is a present-day ticker snapshot; delisted tickers are absent, which historically inflated short-hold pass rates.
2. Same-day −42% tail trades on sub-US$4 names appear in the trade CSV (A-base rows 1–2, exit 1.97 across different entries on consecutive days) — data-quality audit of those tickers is part of the QC confirmation pass, not a bar-bending reason.
3. Friction reality check: 0.35%/side does not include slippage on US$1–10 microcaps; the 0.55% stress pass is necessary but not sufficient. Plus500 (CFD spread venue) friction audit requirement stands for any venue switch; registered US paper venue remains Longbridge.

## Provenance
- Code: `scripts/us/us_6_1_break_retest.py` (post-loader-patch, frozen mechanics: W=5 pivots, double-anchor trendlines, ±0.25×ATR touch, body-close no-intersection, N=10 retest, next-open entry, SPY>SMA200(1) gate, universes US$1–10 & dvol≥US$3M entry filters).
- Data: repo `data_us/` (666 CSVs, Yahoo daily, snapshot 2026-10-27 vintage), `data_us/SPY.csv` gate series. Unadjusted OHLC used per loader contract; `adj close` column present but unused.
- Runs: probe + one registered 6.1 + one registered 6.2 (+stress) + one determinism rerun. Raw stdout committed as `results/us_6_1_armA.txt`, `results/us_6_2_armB.txt`, `results/us_6_1_armA_stress.txt`, `results/us_6_2_armB_stress.txt`. Trade-level CSVs (`results_6_1_{A,B}_{base,stress}.csv`, ~15.6k rows each) are byte-reproducible from the committed code + data (determinism verified) and are staged for upload via the results folder.
- Date of run: 23 Nov 2026 (Asia/Singapore), remote sandbox, single operator session.
- Push history: PR #63 accidentally committed garbled payloads (agent-side encoding error, mechanics and results unaffected on disk); overwritten byte-exact by the immediately following correction PR, verified by round-trip diff of remote files against local run outputs.

## Next steps (pending owner go)
- QC/AlgoSeek survivorship-free re-confirmation of 6.1/6.2 BEFORE any adoption talk (mandatory by precedent).
- 6.3 (intraday trendline) is now UNBLOCKED in principle by the 6.1 Stage-1 pass, but remains gated on the data pipe (LEAN CLI / IBKR 1-min) AND on the QC confirmation above given caution #1.
- 5.4 (ORB, both pre-registered arms) → 6.4 → 6.5 per runbook order once intraday data is validated.
4. **Repo visibility note (flagged Day-1):** the lab repo is currently PUBLIC on GitHub (confirmed via unauthenticated API/codeload download), not private as assumed. Owner to decide whether to flip it private; until then treat all registered plans/results as world-readable.
- No changes to the 2 Nov live SGX champion or the US 4.5 Longbridge paper OOS.
