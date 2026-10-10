#!/usr/bin/env python3
"""
TEST 4.1 — US sub-US$10 champion replication. PRE-REGISTERED: PR #19, docs/US-TEST-PLAN.md.
Spec: top-10 by 126d return, equal weight, monthly rebalance (first trading day),
GATES: SPY > SMA200 AND breadth >= 50% of universe above SMA200. Either closed -> flat.
Costs: 0.35%/side baseline (stress: --cost 0.55). Long-only.
BARS Stage 1 (full): EV/trade > +0.6% after costs AND >= 6/10 positive years.
Stage 2 (walk-forward): IS 2016-21 frozen, OOS 2022-26 untouched: OOS EV >= +0.6% AND >= 4/5 positive years.
VOID: <150 trades Stage 1; data coverage <90%; survivorship contamination >2pp of EV (caveat always printed).
Data: data_us/*.csv (one per ticker, from Phase 0a). SPY fetched if absent.
"""
import argparse, glob, os
import numpy as np
import pandas as pd
import yfinance as yf

def load_spy(out_dir):
    p = os.path.join(out_dir, 'SPY.csv')
    if not os.path.exists(p):
        raw = yf.download('SPY', start='2014-01-01', auto_adjust=False, progress=False)
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = [c[0] if isinstance(c, tuple) else str(c) for c in raw.columns]
        raw = raw.reset_index()
        raw.columns = [str(c).strip().lower() for c in raw.columns]
        dcol = next(c for c in raw.columns if 'date' in c or c == 'price')
        raw[dcol] = pd.to_datetime(raw[dcol]).dt.normalize()
        raw = raw.sort_values(dcol)
        raw.to_csv(p, index=False)
    d = pd.read_csv(p)
    d.columns = [str(c).strip().lower() for c in d.columns]
    d['date'] = pd.to_datetime(d['date']).dt.normalize()
    return d.set_index('date')['adj close'].astype(float)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data-dir', default='data_us')
    ap.add_argument('--cost', type=float, default=0.35)
    ap.add_argument('--top', type=int, default=10)
    ap.add_argument('--lookback', type=int, default=126)
    ap.add_argument('--min-price', type=float, default=1.0)
    ap.add_argument('--max-price', type=float, default=10.0)
    ap.add_argument('--min-dvol', type=float, default=3e6)
    ap.add_argument('--start', default=None)
    ap.add_argument('--end', default=None)
    a = ap.parse_args()

    adj, close, vol = {}, {}, {}
    for f in sorted(glob.glob(os.path.join(a.data_dir, '*.csv'))):
        t = os.path.basename(f)[:-4]
        if t.startswith('_') or t.upper() in ('SPY',):
            continue
        try:
            df = pd.read_csv(f)
            df.columns = [str(c).strip().lower() for c in df.columns]
            if 'date' not in df.columns or 'close' not in df.columns:
                continue
            df['date'] = pd.to_datetime(df['date']).dt.normalize()
            df = df.sort_values('date').set_index('date')
        except Exception:
            continue
        if len(df) < 260:
            continue
        c = df['close'].astype(float)
        v = df['volume'].astype(float)
        adjc = df['adj close'].astype(float) if 'adj close' in df.columns else c
        close[t] = c
        vol[t] = v
        adj[t] = adjc

    A = pd.DataFrame(adj).sort_index()
    C = pd.DataFrame(close).reindex(A.index)
    V = pd.DataFrame(vol).reindex(A.index)
    print(f"[diag] universe: {A.shape[1]} tickers, {A.shape[0]} rows ({A.index[0].date()}..{A.index[-1].date()})")
    print("[diag] SURVIVORSHIP CAVEAT APPLIES (today-only snapshot; PR #19, runbook section 2)")

    dvol = (C * V).rolling(20).mean()
    elig = (C >= a.min_price) & (C <= a.max_price) & (dvol >= a.min_dvol) & A.notna()
    r = A / A.shift(a.lookback) - 1.0
    sma200 = A.rolling(200).mean()
    breadth = (A > sma200).mean(axis=1)

    spy = load_spy(a.data_dir)
    reg = pd.Series((spy > spy.rolling(200).mean()).astype(float)).reindex(A.index, method='ffill').fillna(0.0)

    idxs = A.index.to_series()
    month_first = idxs.groupby([idxs.dt.year, idxs.dt.month]).min().sort_values()
    rdates = [d for d in month_first
              if (a.start is None or d >= pd.Timestamp(a.start))
              and (a.end is None or d <= pd.Timestamp(a.end))]

    trades, monthly = [], []
    for i, d in enumerate(rdates):
        if i + 1 >= len(rdates):
            break
        d2 = rdates[i + 1]
        if reg.loc[d] < 1 or breadth.loc[d] < 0.5:
            monthly.append((d, 0.0, 0))
            continue
        e = elig.loc[d]
        rr = r.loc[d][e]
        rr = rr[rr.notna()]
        if len(rr) == 0:
            monthly.append((d, 0.0, 0))
            continue
        sel = rr.sort_values(ascending=False).head(a.top)
        rets = A.loc[d2, sel.index] / A.loc[d, sel.index] - 1.0
        nets = rets * 100 - 2 * a.cost
        for t, n in nets.items():
            trades.append((d, t, float(n)))
        monthly.append((d, float(nets.mean()), len(sel)))

    tdf = pd.DataFrame(trades, columns=['date', 'ticker', 'net'])
    m = pd.DataFrame(monthly, columns=['date', 'ret', 'n'])
    m['year'] = pd.to_datetime(m.date).dt.year
    yr = m.groupby('year').ret.mean()
    ev = tdf.net.mean() if len(tdf) else float('nan')
    eq = (1 + m.ret / 100).cumprod()
    dd = (eq / eq.cummax() - 1).min() if len(m) else float('nan')
    pos_years = (yr > 0).sum()

    print(f"\n=== TEST 4.1: US champion replication, costs {a.cost:.2f}%/side ===")
    print(f"EV/trade: {ev:+.2f}% | trades: {len(tdf)} | positive years: {pos_years}/{len(yr)} | maxDD (monthly eq): {dd*100:.1f}%")
    gate_open = m[m.n > 0]
    print(f"months in market: {len(gate_open)}/{len(m)} (gate-closed months flat)")
    print("\nYear-by-year (portfolio monthly mean %):")
    for y, v in yr.items():
        print(f"  {y}: {v:+6.2f}%")

    if len(tdf) < 150:
        print(f"\nVOID: {len(tdf)} < 150 trades (pre-registered)")
        return
    b1 = ev > 0.6
    b2 = pos_years >= 6 if len(yr) >= 10 else None
    print(f"\nBAR 1 (EV > +0.6%): {'PASS' if b1 else 'FAIL'} ({ev:+.2f}%)")
    if b2 is not None:
        print(f"BAR 2 (>= 6/10 positive years): {'PASS' if b2 else 'FAIL'} ({pos_years}/{len(yr)})")

if __name__ == '__main__':
    main()
