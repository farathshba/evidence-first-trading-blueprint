#!/usr/bin/env python3
"""TEST 3.2 — Regime-conditioned support bounce (3-10d). Pre-registered 9 Oct 2026.
Gate: ES3 close > ES3 SMA50.
Setup: px >= S$1, dvol >= S$1M; close within 2% of lower Bollinger band (20d, 2sd)
       OR within 2% of SMA20; RSI(14) < 35.
Entry: setup day closes bullish (close > open).
Exit: close < entry-day low (stop) OR 10-day time stop.
Costs 0.45%/side. Bars: Stage 1 EV > +0.6% AND >= 6/10 positive years; OOS EV > +0.6%.
Prior: LOW — cousin of failed deeper-dip; failure = second SGX mean-reversion tombstone.
"""
import argparse, glob, os, sys
import pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument("--data-dir", default="data_v3_clean")
ap.add_argument("--cost-pct", type=float, default=0.45)
ap.add_argument("--rsi-max", type=float, default=35.0)
ap.add_argument("--near-pct", type=float, default=2.0)   # proximity to support
ap.add_argument("--hold-days", type=int, default=10)
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

# regime gate: ES3 > SMA50
es3 = books.get("ES3_SI")
if es3 is None:
    print("ES3_SI missing — regime gate unavailable"); sys.exit(1)
es3_ok = set(d for d in es3.index if es3["close"].loc[d] > es3["close"].rolling(50).mean().loc[d])

def rsi(s, n=14):
    d = s.diff()
    up = d.clip(lower=0).ewm(alpha=1/n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1/n, adjust=False).mean()
    return 100 - 100/(1 + up/dn)

trades = []
for t, b in books.items():
    if t == "ES3_SI" or len(b) < 60: continue
    c, o, l, v = b["close"], b["open"], b["low"], b["volume"]
    sma20 = c.rolling(20).mean()
    sd20 = c.rolling(20).std()
    lb = sma20 - 2*sd20
    r = rsi(c)
    dvol = (c*v).rolling(20).mean()
    near = ((c - lb).abs() <= a.near_pct/100.0 * c) | ((c - sma20).abs() <= a.near_pct/100.0 * c)
    entry = (c >= 1.0) & (dvol >= 1_000_000) & near & (r < a.rsi_max) & (c > o)
    idx = b.index
    for i in range(59, len(idx)):
        d = idx[i]
        if not bool(entry.iloc[i]): continue
        if d not in es3_ok: continue
        if a.entry_start and d < a.entry_start: continue
        if a.entry_end and d > a.entry_end: continue
        epx, elow = float(c.iloc[i]), float(l.iloc[i])
        basis = epx * (1 + cost)
        exit_px, exit_d = None, None
        for j in range(i+1, min(i+1+a.hold_days, len(idx))):
            if float(c.iloc[j]) < elow:
                exit_px, exit_d = float(c.iloc[j]) * (1-cost), idx[j]
                break
        if exit_px is None:
            j2 = min(i+a.hold_days, len(idx)-1)
            exit_px, exit_d = float(c.iloc[j2]) * (1-cost), idx[j2]
        trades.append(dict(ticker=t, entry_date=d, exit_date=exit_d,
                           pnl_pct=100*(exit_px-basis)/basis))

td = pd.DataFrame(trades)
if td.empty:
    print("NO TRADES — strategy never triggered under pre-registered filters."); sys.exit(0)
td["year"] = td["exit_date"].str[:4]
ev = td["pnl_pct"].mean()
by_year = td.groupby("year")["pnl_pct"].agg(["count","sum"]).rename(columns={"count":"trades","sum":"sum_pct"})
pos_years = (by_year["sum_pct"] > 0).sum()
wr = 100 * (td["pnl_pct"] > 0).mean()

print("=== TEST 3.2: REGIME-CONDITIONED SUPPORT BOUNCE (3-10d) ===")
print(f"Round-trips: {len(td)}  win rate: {wr:.1f}%  EV: {ev:+.2f}%/trade")
print("\nBy exit year:"); print(by_year.round(2))
print(f"\nBAR: EV > +0.6%/trade after costs AND net positive in >= 6 of 10 years.")
print(f"Positive years: {pos_years}/{len(by_year)}")
verdict = "PASS" if ev > 0.6 and pos_years >= 6 and len(by_year) >= 8 else "FAIL"
print(f"STAGE 1 VERDICT: {verdict}")
td.to_csv("results/strategy_3_2_trades_raw.csv", index=False)
print("Trades log -> results/strategy_3_2_trades_raw.csv")
