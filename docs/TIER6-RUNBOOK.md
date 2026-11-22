# Tier 6 — Day-1 Execution Runbook (23 Nov 2026)

Owner go received 22 Nov: "test all of these strategies tomorrow onwards" — US small caps, short-hold track. This runbook sequences the FIRST legal run of each registered test. One-run discipline: probes first, then one registered run, then bar reading.

## Day 1 (Mon 23 Nov) — the free stuff
1. `pull` the lab repo (Tier 6 scripts are on main).
2. Smoke pass: `python3 scripts/us/us_6_1_break_retest.py --data-dir data_us --spy data_us/SPY.csv --start 2014-01-01 --end 2019-12-31 --probe` — probe on 3 files: nonzero trades, no exceptions, sane dates. (Do NOT read bars off the probe.)
3. Registered run 6.1 Arm A: full `--start 2014-01-01 --end 2026-10-31`. ONE run. Save stdout + CSV into results/.
4. 6.2 Arm B: same run with `--arm-b` (paired: consumes the same market data; key bar B−A ≥ +0.30pp).
5. Stress pass at 0.55%/side for whichever arm(s) are being read (`--stress`) — mandatory stress read per 4.6 lesson.
6. Determinism check: rerun 6.1 Arm A once; numbers must be byte-identical (5.3 lesson). Then STOP — one registered run only.
7. Log verdict doc `docs/US-TEST-6-1-6-2-RESULTS.md` + PR (template: trades, EV, years, bars table, probe outputs, provenance 5-key: yahoo=delayed-snapshot etc.).

## Day 1 blockers check — LEAN CLI (unlocks 5.4/6.3/6.4/6.5)
- owner: `pip install lean`, `lean login`, single AAPL 1-min download per docs/RUNBOOK-5-4-5-6-LEAN-CLI.md
- if download fails → IBKR 1-min bulk route (pre-registered fallback)
- once plumbing validated: 5.4 (+ both pre-registered arms per docs/US-TEST-5-4-RUN-AMENDMENT.md) → 6.4 → 6.5 in that order

## Test 6.3 gate
- runs ONLY if 6.1 clears Stage 1 bars (EV > +0.60%, ≥6/13 yrs, ≥150 trades). If 6.1 fails: 6.3 is VOID-by-precedent; do not build intraday trendline code.

## Reminders (standing)
- Year-by-year table and bar table go in the verdict; no verdict language before ALL bars are read once.
- Probe before ANY verdict; diagnose apparatus, never bend bars.
- Any Stage-1 PASS at 0.35% must be re-confirmed survivorship-free (QC/AlgoSeek) BEFORE it is believed — Yahoo-snapshot inversion precedent (5.1, 5.3).
- All results and verdicts go to the lab repo via PR; GitHub App can push directly now.
- 2 Nov live/paper deployments are untouched by Tier 6 until every bar reads.
