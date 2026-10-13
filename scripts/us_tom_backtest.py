#!/usr/bin/env python3
"""Test 4.6: turn-of-month seasonality backtest (pre-registered bars)."""
import argparse, glob, os
import numpy as np
import pandas as pd

ap = argparse.ArgumentParser()
ap.add_argument('--data-dir', default='data_us')
ap.add_argument('--start', default=None)
ap.add_argument('--end', default=None)
ap.add_argument('--cost', type=float, default=0.35)  # % per side
ap.add_argument('--top', type=int, default=10)
ap.add_argument('--min-price', type=float, default=1.0)
ap.add_argument('--max-price', type=float, default=10.0)
ap.add_argument('--min-dvol', type=float, default=3e6)
a = ap.parse_args()

# ---- load universe (same conventions as us_champion_backtest) ----
frames = {}
for f in sorted(glob.glob(os.path.join(a.data_dir, '*.csv'))):
    t = os.path.basename(f)[:-4]
    df = pd.read_csv(f)
    cols = {c.lower(): c for c in df.columns}
    dcol = next((cols[k] for k in ['date','datetime','timestamp'] if k in cols), None)
    ccol = next((cols[k] for k in ['close','adj close','adj_close','c'] if k in cols), None)
    vcol = next((cols[k] for k in ['volume','v'] if k in cols), None)
    if dcol is None or ccol is None: continue
    s = pd.Series(df[ccol].values, index=pd.to_datetime(df[dcol].values)).astype(float)
    s = s[~s.index.duplicated()].sort_index()
    frames[t] = s
A = pd.DataFrame(frames).sort_index()
vframes = {}
for f in sorted(glob.glob(os.path.join(a.data_dir, '*.csv'))):
    t = os.path.basename(f)[:-4]
    df = pd.read_csv(f)
    dcol = next((c for c in ['date','datetime','timestamp'] if c in df.columns), None)
    vcol = next((c for c in ['volume','Volume','v'] if c in df.columns), None)
    if dcol is None or vcol is None: continue
    vs = pd.Series(pd.to_numeric(df[vcol], errors='coerce').values,
                   index=pd.to_datetime(df[dcol].values)).astype(float)
    vs = vs[~vs.index.duplicated()].sort_index()
    vframes[t] = vs
V = pd.DataFrame(vframes).sort_index().reindex(A.index)
print(f"[diag] volume matrix: {V.notna().sum().sum()} valid cells ({(V.notna().sum().sum()/(V.shape[0]*V.shape[1])):.0%} density)")
print(f"[diag] universe: {A.shape[1]} tickers, {len(A)} rows ({A.index.min().date()}..{A.index.max().date()})")
print("[diag] SURVIVORSHIP CAVEAT APPLIES (today-only snapshot; PR #19)")

C = A
dvol = (C * V).rolling(20).mean()
elig = (C >= a.min_price) & (C <= a.max_price) & (dvol >= a.min_dvol) & C.notna()

# ---- build turn-of-month windows: last 4 trading days + first 3 of next month ----
idx = pd.Series(A.index, index=A.index)
ym = A.index.to_period('M')
first_of_month = pd.Series(A.index, index=A.index).groupby(ym).min()   # first trading day each month
last_of_month = pd.Series(A.index, index=A.index).groupby(ym).max()    # last trading day each month
in_window = pd.Series(False, index=A.index)
for m in last_of_month.index:
    if m not in first_of_month.index: continue
    lm, fm = last_of_month[m], first_of_month[m]
    tail = A.index[(A.index <= lm)][-4:]                     # last 4 trading days of month m
    nxt = A.index[(A.index > fm)][:2]                       # 2 more days after the 1st (total 3 of next)
    head = [fm] + list(nxt)
    in_window.loc[list(tail) + head] = True
windates = A.index[in_window.values]

if a.start: windates = windates[windates >= pd.Timestamp(a.start)]
if a.end:   windates = windates[windates <= pd.Timestamp(a.end)]
print(f"[diag] TOM trading days in sample: {len(windates)}")

# ---- simulate: at each month-boundary window, pick top-10 liquidity names, hold the window ----
wins = []
periods = sorted(set(pd.PeriodIndex(windates, freq='M')))
for m in periods:
    wdates = [d for d in windates if d.to_period('M') in (m, m+1)]
    # window = tail of month m + head of month m+1; anchor selection at first tail day
    tail = [d for d in wdates if d.to_period('M') == m]
    head = [d for d in wdates if d.to_period('M') == m+1]
    if not tail or not head: continue
    d0 = tail[0]; d1 = head[-1]
    e = elig.loc[d0]
    if e.sum() < a.top: continue
    rank = dvol.loc[d0][e].sort_values(ascending=False).head(a.top)
    gross = (A.loc[d1, rank.index] / A.loc[d0, rank.index] - 1.0).mean()
    net = gross - 2*(a.cost/100.0)
    wins.append((d0, net, len(rank)))

w = pd.DataFrame(wins, columns=['date','ret','n'])
if len(w) == 0:
    print("VOID: no windows"); raise SystemExit
w['year'] = w.date.dt.year
yr = w.groupby('year').ret.mean()
nwin = len(w)
mean_net = w.ret.mean()
pos_years = int((yr > 0).sum()); tot_years = len(yr)
print(f"\n=== TEST 4.6: turn-of-month, costs {a.cost:.2f}%/side ===")
print(f"Mean window return (net): {mean_net*100:+.2f}% | windows: {nwin} | positive years: {pos_years}/{tot_years}")
print("\nYear-by-year (mean net window return %):")
for y, v in yr.items(): print(f"  {y}: {v*100:+.2f}%")
bar = 0.30/100.0
if nwin < (100 if not a.start else 40):
    print(f"\nVOID: {nwin} < {'100' if not a.start else '40'} windows (pre-registered)")
else:
    b1 = "PASS" if mean_net > bar else f"FAIL ({mean_net*100:+.2f}% <= +0.30%)"
    b2 = "PASS" if pos_years >= (6 if not a.start else 3) else f"FAIL ({pos_years}/{tot_years})"
    print(f"\nBAR 1 (mean window > +0.30% net): {b1}")
    print(f"BAR 2 (>= {6 if not a.start else 3}/{tot_years if not a.start else 5} positive years): {b2}")
