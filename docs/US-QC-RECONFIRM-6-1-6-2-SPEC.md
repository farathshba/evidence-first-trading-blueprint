# QC / Survivorship-Free Re-Confirmation Spec for Tests 6.1 / 6.2 (registered 23 Nov 2026)

Purpose: re-verify the Stage-1 PASS of 6.1 / 6.2 (docs/US-TESTT-6-1-6-2-RESULTS.md) on
point-in-time, delusion-inclusive (delisted tickers present) daily data BEFORE the PASS
may be believed or discussed for adoption. Mandated by the Yahoo-snapshot inversion
precedent (Tests 5.1, 5.3).

## Data (the whole point of this run)
- QuantConnect cloud daily-resolution US equity data (includes delisted tickers,
  point-in-time universe via CoarseUniverseSelection), or equivalent point-in-time
  source (AlgoSeek). Fallback: another point-in-time provider only with owner go.
- Universe each day: US$1 <= close <= US$10, 20-day mean dollar volume >= US$3M
  computed from that day backward, with that day's real constituents (incl. those
  later delisted). Gate: SPY close > SPY SMA200, one-day lag, identical to the
  registered spec.

## Strategy mechanics (FROZEN: byte-identical to scripts/us/us_6_1_break_retest.py)
- W=5 fractal pivots (center, lag inherent), double-anchor down-trendlines through
  consecutive lower swing highs with body-close no-intersection between anchors.
- Break: prior-bar close above line; retest within N=10 bars (low <= line +
  0.25*ATR14, close above line); entry next open.
- Exit Arm A: first close below the opposing up-trendline (rebuilt at entry).
- Exit Arm B: S/R take-profit (recent pivot high >=3 touches in prior 60 bars,
  else retest-swing high, minus 0.25*ATR), else Arm A exit. Paired B vs A.
- Costs: 0.35%/side primary, 0.55%/side stress read. Period 2014-01-01..2026-10-31.

## Bars (identical to registration; NO widening, NO re-tuning)
- EV net 0.35% > +0.60%; >= 6/13 positive years; >= 150 trades; stress pass;
  B - A >= +0.30pp.
- PASS on QC => the Day-1 PASS is confirmed. FAIL on QC => the Yahoo PASS is void
  and the strategy class stays dead. No third attempt on this class without owner go.

## Pre-registered CAUTION metrics (reported, NOT pass/fail; do not gate on them)
- EV excluding the top 1% of winners (Day-1 value: +0.31%, below the bar; fragility
  known and carried forward, not hidden).
- Share of total net PnL from top 1% / top 100 trades; same-day-turn tail counts;
  split-event audit (Day-1 sweep: 4 split-signature days across 666 files:
  VISN x2, CMCT, CLRO).
- Data-quality notes registered: Yahoo loader used RAW close (adj close present but
  unused); trades CSV writer bug: exit_date column recorded the entry date
  (registered results unaffected: metrics use returns only). Both fixed for the QC run.

## One-run discipline
- Probe on QC with a single known ticker first (apparatus sanity), then ONE
  registered full run per arm/cost, then singles bar reading. Determinism: rerun
  once, byte-identical summary. No parameter may be touched between QC runs.
- Execution venue for this test: QC cloud backtest daily resolution (free tier
  suffices) OR local LEAN CLI with same data. Verdict doc: docs/US-TEST-6-1-6-2-QC-RESULTS.md.
