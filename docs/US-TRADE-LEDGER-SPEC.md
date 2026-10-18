# US Paper-Track Trade Ledger — Specification v1.0 (18 Oct 2026)

Purpose: register the ledger BEFORE the 2 Nov 2026 Longbridge paper deployment, so the
post-quarter P&L audit (adopted 16 Oct from the Humbled Trader pattern) is scored against
a frozen schema, not improvised after seeing results. One schema, frozen now; changes only
via new version bump with reason logged.

Provenance note: schema adapted from OpenTerminalUI JournalEntry (MIT) per the 18 Oct
engine audit (arkenstone PR #3); evidence-first fields are ours. It is a LOGGING spec,
not an evaluation engine — no verdicts are ever read from this ledger.

## 1. Record schema (one row per executed trade, paper or live)

| Field | Type | Notes |
|---|---|---|
| trade_id | str | broker order id or synthetic id |
| symbol | str | |
| direction | enum | LONG only (system is long-only) |
| entry_ts / entry_price / qty | | fills as recorded by Longbridge |
| exit_ts / exit_price | nullable | open positions audited separately |
| fees_broker | float | actual |
| slippage_bps | float | (fill vs decision-price) in bps — see §3 |
| rule_version | str | which registered rule fired (e.g. "us45-v1") |
| bar_evidence | str nullable | registered test + bars backing the rule |
| rebalance_id | str | groups entries from same monthly rebalance |
| regime_snapshot | json | SPY>SMA200 bool, breadth, at decision time |
| data_provenance | 5-key | see §2 |
| execution_grade | enum A/B/C | A: rule followed + clean fill; B: rule followed, sloppy fill (slippage > 2× expected); C: rule broken (a rule-broken WIN is still C) |
| notes | text | free-form, never used for scoring |

Dropped from OpenTerminalUI schema (deliberate): emotion, rating — replaced by
execution_grade; feelings do not enter the audit.

## 2. Provenance contract (adopted verbatim from OpenTerminalUI Contract-1)

Every number written to the ledger or any report carries 5 keys:
source | quality (live/delayed/cached/synthetic/unavailable) | as_of | latency_ms | note

Source-to-quality map for us: longbridge=live, yahoo=snapshot(delayed),
qc-algoseek=export(cached). No number without provenance. Applies to: daily reports,
ledger writes, QC pipeline outputs.

## 3. Expected-vs-realized slippage validation (pattern from OpenTerminalUI execution_sim)

For every fill, record at decision time:
- decision_price (close/level the rule evaluated)
- expected_cost_bps = registered model: 0.35%/side baseline, decomposed as
  spread_bps + market_impact_bps + slippage_bps (per-fill decomposition adopted from
  OpenTerminalUI execution_sim/simulator.py; ATR-proportional term optional for SGX,
  not used US)
- realized_slippage_bps = fill vs decision_price

Monthly audit output: median + p90 realized vs expected. If median realized > 2×
expected for a full month, that is a REGISTERED finding — cost model re-registration
required before any further paper promotion (this is the 4.5 cost-caveat pattern:
measure the friction wall live, never assume it).

## 4. Audit bars (registered now, read after ~1 quarter of fills)

1. Median realized slippage <= 2× expected (35bps/side) — else cost re-registration
2. Ledger completeness: 100% of broker fills reconciled (target: zero unrecorded fills;
   discrepancy > 2% of fills = process incident, logged)
3. Execution grades: C-grade rate <= 5% — higher means the rulebook is being
   discretionary-traded, not system-traded
4. Paper EV/trade (net of broker fees) reported vs registered baseline EV — for
   drift observation ONLY, not a pass/fail (paper OOS authority gate is separately
   registered)

## 5. Storage & flow

- CSV/JSON per month in lab repo results/paper_ledger/ (committed weekly via PR)
- Longbridge statement export reconciled monthly against ledger rows
- Ledger is append-only; corrections are new rows with correction_of=trade_id
