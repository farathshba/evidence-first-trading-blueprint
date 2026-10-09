#!/usr/bin/env python3
"""TEST 3.4-PROXY — Post-gap drift (PEAD testable core). Pre-registered 9 Oct 2026.
Trigger: overnight gap >= +3% (open vs prior close) on volume >= 3x 20d avg;
         px >= S$1, dvol >= S$1M.
Entry: t+1 at close if close > gap-day candle midpoint.
Exit: SMA10 < SMA20 (death cross) OR 20-day time stop.
Costs 0.45%/side. Bars: Stage 1 EV > +0.6% AND >= 6/10 positive years; OOS EV > +0.6%.
Prior: LOW. Label caveat: gaps include non-earnings announcements (SGX small caps often
have no analyst consensus); contamination works AGAINST finding drift.
"""
import argparse, glob, os, sys
import pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("--data-dir", default="data_v3_clean")
ap.add_argument("--cost-pct", type=float, default=0.45)
ap.add_argument("--gap-pct", type=float, default=3.0)
ap.add_argument("--vol-mult", type=float, default=3.0)
ap.add_argument("--hold-days", type=int, default=20)
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

trades = []
for t, b in books.items():
    if len(b) < 60 or t == "ES3_SI": continue
    c, o, h, l, v = b["close"], b["open"], b["high"], b["low"], b["volume"]
    gap = 100 * (o / c.shift(1) - 1)
    dvol = (c * v).rolling(20).mean()
    vavg = v.rolling(20).mean().shift(1)
    mid = (h + l) / 2
    trig = (gap >= a.gap_pct) & (v >= a.vol_mult * vavg) & (c >= 1.0) & (dvol >= 1_000_000)
    sma10, sma20 = c.rolling(10).mean(), c.rolling(20).mean()
    idx = b.index
    for i in range(21, len(idx) - 1):
        d0 = idx[i]
        if not bool(trig.iloc[i]): continue
        if a.entry_start and d0 < a.entry_start: continue
        if a.entry_end and d0 > a.entry_end: continue
        # entry next day if close > gap-day midpoint
        j = i + 1
        if float(c.iloc[j]) <= float(mid.iloc[i]): continue
        epx = float(c.iloc[j]); basis = epx * (1 + cost)
        exit_px, exit_d = None, None
        for k in range(j + 1, min(j + 1 + a.hold_days, len(idx))):
            if float(sma10.iloc[k]) < float(sma20.iloc[k]):
                exit_px, exit_d = float(c.iloc[k]) * (1 - cost), idx[k]; break
        if exit_px is None:
            k2 = min(j + a.hold_days, len(idx) - 1)
            exit_px, exit_d = float(c.iloc[k2]) * (1 - cost), idx[k2]
        trades.append(dict(ticker=t, gap_date=d0, entry_date=idx[j], exit_date=exit_d,
                           gap_pct=round(float(gap.iloc[i]), 2),
                           pnl_pct=100 * (exit_px - basis) / basis))

td = pd.DataFrame(trades)
if td.empty:
    print("NO TRADES — trigger never fired under pre-registered filters."); sys.exit(0)
td["year"] = td["exit_date"].str[:4]
ev = td["pnl_pct"].mean()
by_year = td.groupby("year")["pnl_pct"].agg(["count", "sum"]).rename(columns={"count": "trades", "sum": "sum_pct"})
pos_years = (by_year["sum_pct"] > 0).sum()
wr = 100 * (td["pnl_pct"] > 0).mean()

print("=== TEST 3.4-PROXY: POST-GAP DRIFT (5-20d) ===")
print(f"Round-trips: {len(td)}  win rate: {wr:.1f}%  EV: {ev:+.2f}%/trade")
print("\nBy exit year:"); print(by_year.round(2))
print(f"\nBAR: EV > +0.6%/trade after costs AND net positive in >= 6 of 10 years.")
print(f"Positive years: {pos_years}/{len(by_year)}")
verdict = "PASS" if ev > 0.6 and pos_years >= 6 and len(by_year) >= 8 else "FAIL"
print(f"STAGE 1 VERDICT: {verdict}")
td.to_csv("results/strategy_3_4_trades_raw.csv", index=False)
print("Trades log -> results/strategy_3_4_trades_raw.csv")
