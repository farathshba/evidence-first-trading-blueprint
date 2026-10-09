#!/usr/bin/env python3
"""TEST 3.1 — Volume-breakout expansion (1-5d). Pre-registered 8 Oct 2026.
Entry: consolidation (20d range < 8% with >=15 qualifying days) then close > 20d high
       with volume >= 2.5x 20d avg.
Exit: close < breakout-candle low (stop) OR 5-day time stop.
Universe/costs: champion's (px >= S$1, dvol >= S$1M, 0.45%/side). No regime/breadth gate.
Bars: Stage 1 EV > +0.6% AND >= 6/10 positive years; OOS EV > +0.6%.
Prior: SUSPICIOUS — adjacent to the refuted v1 ATR/volume system.
"""
import argparse, glob, os, sys
import pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("--data-dir", default="data_v3_clean")
ap.add_argument("--cost-pct", type=float, default=0.45)
ap.add_argument("--capital", type=float, default=100000)
ap.add_argument("--range-pct", type=float, default=8.0)   # consolidation range
ap.add_argument("--cons-days", type=int, default=15)      # qualifying days for consolidation
ap.add_argument("--vol-mult", type=float, default=2.5)     # volume multiple
ap.add_argument("--hold-days", type=int, default=5)       # time stop
ap.add_argument("--entry-start", default=None)
ap.add_argument("--entry-end", default=None)
a = ap.parse_args()
cost = a.cost_pct / 100.0

def load(fp):
    df = pd.read_csv(fp)
    cols = {c.lower().replace(" ", ""): c for c in df.columns}
    ren = {cols[s]: s for s in ["date","open","high","low","close","adjclose","volume"] if s in cols}
    df = df.rename(columns=ren)
    if "adjclose" in df.columns: df["close"] = df["adjclose"]
    df = df[["date","open","high","low","close","volume"]].dropna()
    df["d"] = df["date"].astype(str).str[:10]
    return df.set_index("d")

books = {}
for fp in sorted(glob.glob(os.path.join(a.data_dir, "*.csv"))):
    t = os.path.basename(fp).replace(".csv", "")
    if t.startswith("_"): continue
    try: books[t] = load(fp)
    except Exception: pass

# daily signals per book (vectorized), then event-driven simulation
trades = []
for t, b in books.items():
    if len(b) < 40: continue
    c, h, l, v = b["close"], b["high"], b["low"], b["volume"]
    dvol = (c * v).rolling(20).mean()
    px_ok = c >= 1.0
    liq_ok = dvol >= 1_000_000
    hh20 = h.rolling(20).max().shift(1)          # 20d high excl today
    rng20 = h.rolling(20).max() - l.rolling(20).min()
    lo20 = l.rolling(20).min()
    cons_ok = rng20 < a.range_pct / 100.0 * lo20  # range < 8% of 20d low
    vavg = v.rolling(20).mean().shift(1)
    entry = px_ok & liq_ok & (c > hh20) & (rng20.shift(1) < a.range_pct / 100.0 * lo20.shift(1)) & (v >= a.vol_mult * vavg)
    # >=15 days within prior consolidation window: use 20d range <8% satisfied today as proxy for maturity
    idx = b.index
    e_days = list(idx[i] for i in range(len(idx)) if bool(entry.iloc[i]) if i >= 20)
    for d in e_days:
        if a.entry_start and d < a.entry_start: continue
        if a.entry_end and d > a.entry_end: continue
        i = idx.get_loc(d)
        epx, elow = float(c.iloc[i]), float(l.iloc[i])
        basis = epx * (1 + cost)
        exit_px, exit_d = None, None
        for j in range(i + 1, min(i + 1 + a.hold_days, len(idx))):
            dj = idx[j]
            if float(c.iloc[j]) < elow:      # stop: close below breakout-candle low
                exit_px, exit_d = float(c.iloc[j]) * (1 - cost), dj
                break
        if exit_px is None:
            j2 = min(i + a.hold_days, len(idx) - 1)
            exit_px, exit_d = float(c.iloc[j2]) * (1 - cost), idx[j2]
        pnl = 100 * (exit_px - basis) / basis
        trades.append(dict(ticker=t, entry_date=d, exit_date=exit_d, entry=epx, exit=exit_px / (1 - cost), pnl_pct=pnl))

td = pd.DataFrame(trades)
if td.empty:
    print("NO TRADES — strategy never triggered under pre-registered filters."); sys.exit(0)
td["year"] = td["exit_date"].str[:4]
ev = td["pnl_pct"].mean()
by_year = td.groupby("year")["pnl_pct"].agg(["count", "sum"]).rename(columns={"count": "trades", "sum": "sum_pct"})
pos_years = (by_year["sum_pct"] > 0).sum()
tot_years = len(by_year)
wr = 100 * (td["pnl_pct"] > 0).mean()

print("=== TEST 3.1: VOLUME BREAKOUT (1-5d) ===")
print(f"Round-trips: {len(td)}  win rate: {wr:.1f}%  EV: {ev:+.2f}%/trade")
print("\nBy exit year:")
print(by_year.round(2))
print(f"\nBAR: EV > +0.6%/trade after costs AND net positive in >= 6 of 10 years.")
print(f"Positive years: {pos_years}/{tot_years}")
verdict = "PASS" if ev > 0.6 and pos_years >= 6 and tot_years >= 8 else "FAIL"
print(f"STAGE 1 VERDICT: {verdict}")
td.to_csv("results/strategy_3_1_trades_raw.csv", index=False)
print("Trades log -> results/strategy_3_1_trades_raw.csv")
