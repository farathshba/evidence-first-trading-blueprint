# Evidence-First Trading Blueprint

A live-deployed SGX swing-trading system built on a single principle: **no
rule is adopted until it survives pre-registered backtests, and no rule is
retired without a written verdict.** This README is the summary of everything
tested and proven so far. The full trail is in docs/, scripts/, and issues.

## The live system (champion: "2.3 breadth-gate momentum")

- Universe: SGX, price >= S$1, 20-day dollar-volume >= S$1M
- Rank: 126-day return; hold top-10 equal weight; monthly rebalance
- Regime gate: ES3 (STI ETF) > SMA200, else stand aside
- Breadth gate: >= 50% of universe above SMA200, else go flat
- Documented performance (2016-2026, costs at 0.45%/side): EV +0.6%/trade at
  0.60%/side worst-case stress, 7/10 years positive, maxDD -31.1%
- Live spread audit (9 Oct 2026): 0.17% median half-spread on the live basket

## What was tested and proven

### Validated
| Finding | Evidence |
|---|---|
| 126d momentum, monthly hold, top-10 | Passed two-stage guardrail + worst-case-cost stress + live spread audit |
| Breadth gate (>=50% above SMA200) | Won the Phase 2 succession; adopted 9 Oct 2026 |
| Monthly-scale holding | The only tested structure that amortizes SGX friction |

### Tombstoned (failed with adequate sample — do not re-propose)
| Class | Verdict | Key evidence |
|---|---|---|
| ATR stop/target system | Retired | 10y: -78.9%, no edge |
| Short-hold volume breakout | Dead (class) | 102 trades, EV -0.83%, anti-correlated with champion |
| Mean reversion (dip-buy, support bounce) | Dead (2 tombstones) | Walk-forward fail; bounce EV -1.39%, 21% win rate |
| Intraday / overnight holds | Dead | Overnight edge inverted: -0.10%/night |

### Real but not tradable
| Effect | Evidence |
|---|---|
| Post-gap drift (PEAD testable core) | +0.23% EV — real but sub-friction; only pays post-2022 regime |

## The core finding: the friction wall

Every short-hold class tested — breakout, dip-buy, event-drift — is defeated
by the same ~0.9% round-trip cost wall. SGX small-cap moves at 1-20 day
horizons are too small to pay the friction. The champion's edge is not just
momentum: its monthly hold is the only tested structure that amortizes the
friction. This is why the system is what it is.

## Repo map

- `scripts/` — every backtest ever run (champion + all challengers)
- `docs/TIER-3-TEST-PLAN.md` — the complete decision log, verdict by verdict
- `docs/PHASE-4-RUNBOOK.md` — how the live system is executed
- `results/` — trades logs; `results_*.txt` — run outputs
- `data_v3_clean/` — daily price books
- Issue #3 — the Tier 3 board (all discussion and verdicts)

## Contributing

Read CONTRIBUTING.md. The short version: pre-register, walk-forward, model
costs, log honest verdicts, respect the tombstones.
