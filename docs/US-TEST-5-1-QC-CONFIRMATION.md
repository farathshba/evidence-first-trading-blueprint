# Test 5.1 — QC Survivorship-Free Confirmation (frozen bars, 17 Oct 2026)

Purpose: decide whether the Mac/Yahoo Stage 1 PASS (EV +2.60%) survives survivorship-free data.
Baseline reference: PR #28 (4.5 on QC/AlgoSeek: EV +4.27%, 214 trades, 7/13 years, 2016-2026).

## Procedure (registered — no reruns, no parameter changes)
1. Open QuantConnect, create C# algorithm, paste scripts/us/qc_us_5_1_adr_conditioned.cs.
2. Run A (baseline): set ADR_MIN = 0.0. Record EV/trade, trades, positive years, maxDD.
3. Run B (conditioned): set ADR_MIN = 0.04 (file default). Record same metrics.
4. Read bars below. One reading, whatever it says.

## Frozen bars (from docs/US-TIER5-TEST-PLAN.md, Test 5.1)
- EV/trade net (0.35%/side) > +0.60%  — Run B
- Positive years >= 6/13 — Run B
- Trades >= 150 (else VOID) — Run B
- KEY BAR: Run B EV >= Run A EV + 0.30pp — else no adoption
- Cross-check sanity: Run A should approximately reproduce PR #28 (+4.27%). Large divergence
  (>1pp) = implementation mismatch — document before reading verdicts.

## Metrics extraction (QC web IDE)
- EV/trade: Trades tab -> mean per-trade return %. (QC reports wins/losses; compute mean of
  per-trade net returns; approximate via Total profit / trades / avg position notional if needed.)
- Positive years: monthly equity from Chart ("Strategy Equity"), count years with positive return.
- MaxDD: Drawdown chart value.
- Attach both result JSON/screenshots to the verdict PR.

## Known approximations (documented, pre-registered)
- Breadth computed over the 500-name coarse-capped candidate set (not full exchange) — same
  approximation class as PR #28; noted, not tuned.
- Coarse pre-filter uses single-day dollar volume; fine stage applies the true 20d mean.
- Survivorship caveat that killed the Yahoo runs does NOT apply here — AlgoSeek data is
  delisting-aware (the whole point of this gate).

## Verdict options
- PASS -> 5.1 becomes the confirmed US variant; Stage 2 walk-forward + paper OOS next,
  paper track may switch from 4.5 to 5.1 only via a new registered decision (2 Nov unchanged).
- FAIL/VOID -> tombstone or park logged; 4.5 remains the sole US paper candidate.
