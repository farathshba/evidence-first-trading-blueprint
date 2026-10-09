#!/usr/bin/env python3
"""
3.6 Phase B — sector momentum overlay vs champion baseline. PRE-REGISTERED 10 Oct 2026.
Spec + bars: docs/TIER-3-TEST-PLAN.md (Test 3.6). Long-only, monthly rebalance,
identical engine for both arms — the ONLY difference is selection:
  OVERLAY : top-10 by 126d return restricted to the top-2 sectors by equal-weight
            sector 126d momentum (sectors need >=5 eligible members; shortfalls
            filled from the next-ranked sectors).
  BASELINE: top-10 by 126d return, no sector filter (champion selection).
Both arms use the champion 2.3 gates: ES3 > SMA200 AND breadth >= 50% above SMA200.
Costs: 0.45%/side per position-month round trip.
VOID condition: sector coverage < 80% of universe.
"""
import argparse, glob, os
import numpy as np
import pandas as pd

def load_es3(data_dir):
    p = os.path.join(data_dir, 'ES3.SI.csv')
    if os.path.exists(p):
        e = pd.read_csv(p, parse_dates=['Date']).sort_values('Date')
        s = e.set_index('Date')['Adj Close'].astype(float)
    else:
        import yfinance as yf
        raw = yf.download('ES3.SI', start='2014-01-01', auto_adjust=False, progress=False)
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = [c[0] if isinstance(c, tuple) else str(c) for c in raw.columns]
        raw = raw.reset_index()
        raw.columns = [str(c).strip().lower() for c in raw.columns]
        dcol = next(c for c in raw.columns if 'date' in c or c == 'price')
        raw[dcol] = pd.to_datetime(raw[dcol])
        s = raw.set_index(dcol)['adj close'].astype(float).sort_index()
    idx = pd.to_datetime(s.index)
    if getattr(idx, 'tz', None) is not None:
        idx = idx.tz_localize(None)
    s.index = idx.normalize()
    return s.astype(float)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data-dir', default='data_v3_clean')
    ap.add_argument('--sectors', default='data_v3_clean/_sectors.csv')
    ap.add_argument('--cost', type=float, default=0.45)
    ap.add_argument('--min-price', type=float, default=1.0)
    ap.add_argument('--min-dvol', type=float, default=1e6)
    ap.add_argument('--top-sectors', type=int, default=2)
    ap.add_argument('--top-stocks', type=int, default=10)
    ap.add_argument('--start', default=None)
    ap.add_argument('--end', default=None)
    a = ap.parse_args()

    adj, close, vol = {}, {}, {}
    for f in sorted(glob.glob(os.path.join(a.data_dir, '*.csv'))):
        t = os.path.basename(f)[:-4]
        if t.upper().startswith(('ES3', '^STI', '_')):
            continue
        try:
            df = pd.read_csv(f)
            df.columns = [str(c).strip().title() for c in df.columns]
            if 'Date' not in df.columns or 'Adj Close' not in df.columns:
                continue
            df['Date'] = pd.to_datetime(df['Date']).dt.normalize()
            df = df.sort_values('Date').set_index('Date')
        except Exception:
            continue
        if len(df) < 260:
            continue
        adj[t] = df['Adj Close'].astype(float)
        close[t] = df['Close'].astype(float)
        vol[t] = df['Volume'].astype(float)

    A = pd.DataFrame(adj).sort_index()
    C = pd.DataFrame(close).reindex(A.index)
    V = pd.DataFrame(vol).reindex(A.index)
    print(f"[diag] universe: {A.shape[1]} tickers, {A.shape[0]} rows ({A.index[0].date()}..{A.index[-1].date()})")

    dvol = (C * V).rolling(20).mean()
    elig = (C >= a.min_price) & (dvol >= a.min_dvol) & A.notna()
    r126 = A / A.shift(126) - 1.0
    sma200 = A.rolling(200).mean()
    breadth = (A > sma200).mean(axis=1)

    es3 = load_es3(a.data_dir)
    reg = pd.Series((es3 > es3.rolling(200).mean()).astype(float)).reindex(A.index, method='ffill').fillna(0.0)

    sec_map = {str(k): str(v) for k, v in pd.read_csv(a.sectors).values}
    covered = sum(1 for t in A.columns if sec_map.get(t, '') not in ('', 'nan'))
    cov_pct = 100 * covered / A.shape[1]
    print(f"[diag] sector coverage: {covered}/{A.shape[1]} ({cov_pct:.0f}%)")

    idxs = A.index.to_series()
    month_first = idxs.groupby([idxs.dt.year, idxs.dt.month]).min().sort_values()
    rdates = [d for d in month_first
              if (a.start is None or d >= pd.Timestamp(a.start))
              and (a.end is None or d <= pd.Timestamp(a.end))]

    def picks_at(d, sector_filter):
        if reg.loc[d] < 1 or breadth.loc[d] < 0.5:
            return []
        e = elig.loc[d]
        r = r126.loc[d][e]
        r = r[r.notna()]
        if len(r) == 0:
            return []
        if not sector_filter:
            return list(r.sort_values(ascending=False).head(a.top_stocks).index)
        rs = {t: sec_map[t] for t in r.index
              if sec_map.get(t, '') not in ('', 'nan')}
        if not rs:
            return []
        r = r.loc[list(rs.keys())]
        sec = pd.Series(rs)
        gm = r.groupby(sec).mean()
        counts = r.groupby(sec).size()
        gm = gm[counts >= 5].sort_values(ascending=False)
        if len(gm) == 0:
            return []
        top = set(gm.index[:a.top_sectors])
        in_top = [t for t in r.index if rs[t] in top]
        sel = r.loc[in_top].sort_values(ascending=False).head(a.top_stocks)
        if len(sel) < a.top_stocks:
            rest = r.drop(sel.index).sort_values(ascending=False).head(a.top_stocks - len(sel))
            sel = pd.concat([sel, rest])
        return list(sel.index)

    def run(sector_filter):
        trades, monthly = [], []
        for i, d in enumerate(rdates):
            if i + 1 >= len(rdates):
                break
            d2 = rdates[i + 1]
            sel = picks_at(d, sector_filter)
            if not sel:
                monthly.append((d, 0.0, 0))
                continue
            rets = A.loc[d2, sel] / A.loc[d, sel] - 1.0
            nets = rets * 100 - 2 * a.cost
            for t, n in nets.items():
                trades.append((d, t, float(n)))
            monthly.append((d, float(nets.mean()), len(sel)))
        m = pd.DataFrame(monthly, columns=['date', 'ret', 'n'])
        m['year'] = pd.to_datetime(m.date).dt.year
        tdf = pd.DataFrame(trades, columns=['date', 'ticker', 'net'])
        ev = tdf.net.mean() if len(tdf) else float('nan')
        yr = m.groupby('year').ret.mean()
        eq = (1 + m.ret / 100).cumprod()
        dd = (eq / eq.cummax() - 1).min() if len(m) else float('nan')
        return dict(ev=ev, pos=(yr > 0).sum(), years=len(yr), dd=dd, yr=yr, n=len(tdf), m=m)

    O = run(True)
    B = run(False)

    print("\n=== OVERLAY (sector momentum) ===")
    print(f"EV/trade: {O['ev']:+.2f}% | trades: {O['n']} | positive years: {O['pos']}/{O['years']} | maxDD (monthly): {O['dd']*100:.1f}%")
    print("=== BASELINE (champion selection) ===")
    print(f"EV/trade: {B['ev']:+.2f}% | trades: {B['n']} | positive years: {B['pos']}/{B['years']} | maxDD (monthly): {B['dd']*100:.1f}%")

    print("\nYear-by-year (overlay EV vs baseline EV, portfolio monthly mean %):")
    for y in sorted(set(O['yr'].index) | set(B['yr'].index)):
        o = O['yr'].get(y, float('nan'))
        b = B['yr'].get(y, float('nan'))
        print(f"  {y}: overlay {o:+6.2f}%  baseline {b:+6.2f}%  delta {o-b:+5.2f}pp")

    if cov_pct < 80:
        print(f"\nCOVERAGE {cov_pct:.0f}% < 80% — TEST 3.6 IS VOID (pre-registered condition)")
        return
    b1 = O['ev'] is not None and not np.isnan(O['ev']) and O['ev'] > 0.6
    b2 = O['pos'] >= 6
    b3 = O['ev'] >= B['ev']
    b4 = O['dd'] >= B['dd'] - 0.05
    print(f"\nBAR 1 (overlay EV > +0.6% after costs):        {'PASS' if b1 else 'FAIL'}  ({O['ev']:+.2f}%)")
    print(f"BAR 2 (>= 6/10 positive years):                {'PASS' if b2 else 'FAIL'}  ({O['pos']}/{O['years']})")
    print(f"BAR 3 (overlay EV >= baseline EV):             {'PASS' if b3 else 'FAIL'}  ({O['ev'] - B['ev']:+.2f}pp)")
    print(f"BAR 4 (maxDD not worse than baseline by >5pp):  {'PASS' if b4 else 'FAIL'}  ({O['dd']*100:.1f}% vs {B['dd']*100:.1f}%)")

if __name__ == '__main__':
    main()
