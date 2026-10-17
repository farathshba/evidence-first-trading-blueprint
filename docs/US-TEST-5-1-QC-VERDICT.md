# US Test 5.1 — QC Confirmation Verdict (17 Oct 2026)

## Verdict: VOID-pending-debug (key bar fails decisively; ADR-conditioning NOT confirmed)

Run on QuantConnect v5 (commit 5b2e56f) with AlgoSeek survivorship-free
daily data, 2016-08-02 to 2026-07-18, 0.35%/side costs. One reading of the
frozen bars after both runs; no reruns; no parameter changes.

## Results

| Metric | Run A (ADR_MIN=0.0) | Run B (ADR_MIN=0.04) | Bar | Result |
|---|---|---|---|---|
| Trades | 276 | 197 | B >= 150 | PASS |
| EV/trade (net) | +1.55% | +0.23% | B > +0.60% | FAIL |
| Positive years | 5/9 | 4/6 | B >= 6/13 | FAIL |
| Key bar | — | +0.23% vs A+0.30pp | B >= A+0.30pp | FAIL (by 1.62pp) |

## Sanity check (Run A vs PR #28 calibration): FAIL

Run A should approximate PR #28 (+4.27% EV, ~214 trades). Observed
+1.55% / 276 trades — 2.72pp divergence, above the 1pp debug threshold.
Per the frozen procedure, this makes the official log VOID-pending-debug:
verdicts are not formally readable until the implementation mismatch is
explained/fixed.

## Why the VOID still kills the idea practically

The two runs share identical plumbing; the sanity-check failure is a
level calibration problem that cannot flip the SIGN of the A-B gap. The
key bar fails by 1.62pp in the wrong direction: the ADR>=4% condition
makes the strategy WORSE on survivorship-free data, versus the Stage 1
Mac/Yahoo result (B +2.60% vs A +1.40%). The Stage 1 edge is therefore
most plausibly a survivorship/data artifact. A faithful v6 port is
unlikely to close a 1.6pp inverted gap.

## Implementation defects to carry into any v6 attempt

1. **Split-adjusted universe drift**: QC prices are split-adjusted, so
   the US$1-10 filter selects on adjusted price (entries like AHT
   ~$5,499, CLEU ~$11,160) — a different universe than the nominal-price
   spec used on Mac/Yahoo.
2. **Persistent flat gaps**: multi-month no-trade stretches in bull
   regimes (2017H2, mid-2023–mid-2024) — suspected FineSelection
   month-rollover race still dropping rebalances.

## Consequences

- Test 5.1 (ADR-conditioned champion) does NOT replace unconditioned 4.5
  in the US paper track. Tombstone unless a v6 faithful port reverses the gap.
- Unconditioned 4.5 remains the registered paper variant; 2 Nov
  deployments are unaffected.
- Proceed to Tests 5.2 (breakout trigger) and 5.3 (RSI+Fib) on Mac, per plan.
