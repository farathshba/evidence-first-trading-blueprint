#!/usr/bin/env python3
"""
TEST 5.2 — breakout-trigger vs nearness-trigger. PRE-REGISTERED: PR #33,
docs/US-TEST-5-2-REGISTRATION.md.
Identical to the 4.5 champion (rank-mode near52w) EXCEPT: --breakout keeps only
candidates whose rebalance-day close is strictly ABOVE their 252-day high
(fresh breakout). Unfilled slots stay empty — NO substitutes.
BARS: EV/trade > +0.60% net @ 0.35%/side; >= 6/13 positive years; >= 150 trades
(else VOID); KEY: beat the 4.5 baseline EV (+1.40%) by >= +0.30pp on the same window.
One run. No gate-widening.
Data: data_us/*.csv (same as champion script). SPY fetched if absent.
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
    ap.add_argument('--breadth', type=float, default=0.5, help='breadth gate: fraction of universe above SMA200')
    ap.add_argument('--cost', type=float, default=0.35)
    ap.add_argument('--side', default='top', choices=['top','bottom'], help='rank side: top winners or bottom losers')
    ap.add_argument('--rank-mode', default='ret', choices=['ret','near52w'], help='ranking signal: lookback return or nearness to 52w high')
    ap.add_argument('--top', type=int, default=10)
    ap.add_argument('--lookback', type=int, default=126)
    ap.add_argument('--min-price', type=float, default=1.0)
    ap.add_argument('--max-price', type=float, default=10.0)
    ap.add_argument('--min-dvol', type=float, default=3e6)
    ap.add_argument('--min-adr', type=float, default=0.0, help='min 20d mean of (high-low)/close, e.g. 0.04 = 4%')
    ap.add_argument('--breakout', action='store_true', help='TEST 5.2: enter only if rebalance-day close is strictly above the 252d high')
    ap.add_argument('--start', default=None)
    ap.add_argument('--end', default=None)
    a = ap.parse_args()

    adj, close, vol, hi, lo = {}, {}, {}, {}, {}
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
        h = df['high'].astype(float) if 'high' in df.columns else c
        l = df['low'].astype(float) if 'low' in df.columns else c
        close[t] = c
        hi[t] = h
        lo[t] = l
        vol[t] = v
        adj[t] = adjc

    A = pd.DataFrame(adj).sort_index()
    C = pd.DataFrame(close).reindex(A.index)
    V = pd.DataFrame(vol).reindex(A.index)
    H = pd.DataFrame(hi).reindex(A.index)
    L = pd.DataFrame(lo).reindex(A.index)
    print(f"[diag] universe: {A.shape[1]} tickers, {A.shape[0]} rows ({A.index[0].date()}..{A.index[-1].date()})")
    print("[diag] SURVIVORSHIP CAVEAT APPLIES (today-only snapshot; PR #19, runbook section 2)")
    print(f"[diag] TEST 5.2 breakout-trigger: {a.breakout}")

    dvol = (C * V).rolling(20).mean()
    adr = ((H - L) / C).rolling(20).mean()
    elig = (C >= a.min_price) & (C <= a.max_price) & (dvol >= a.min_dvol) & A.notna() & (adr >= a.min_adr)
    r = (A / A.rolling(252).max()) if a.rank_mode == 'near52w' else (A / A.shift(a.lookback) - 1.0)
    sma200 = A.rolling(200).mean()
    above = (A > sma200)
    listed = sma200.notna()
    denom = listed.sum(axis=1).replace(0, np.nan)
    breadth = (above.where(listed).sum(axis=1) / denom).fillna(0.0)

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
        if reg.loc[d] < 1 or breadth.loc[d] < a.breadth:
            monthly.append((d, 0.0, 0))
            continue
        e = elig.loc[d]
        rr = r.loc[d][e]
        rr = rr[rr.notna()]
        if len(rr) == 0:
            monthly.append((d, 0.0, 0))
            continue
        sel = rr.sort_values(ascending=(a.side == 'bottom')).head(a.top)
        if a.breakout:
            # TEST 5.2 registered rule: enter only if rebalance-day close is strictly
            # above the 252-day high (both on the same nominal close series C).
            hh = C.rolling(252).max().loc[d]
            ok = C.loc[d, sel.index] > hh.loc[sel.index]
            sel = sel[ok.fillna(False)]  # unfilled slots stay empty — no substitutes
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

    print(f"\n=== TEST 5.2: breakout-trigger (close > 252d high), costs {a.cost:.2f}%/side ===")
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
    print(f"KEY BAR (beat 4.5 baseline +1.40% by >= +0.30pp): {'PASS' if ev >= 1.70 else 'FAIL'} ({ev:+.2f}% vs required +1.70%)")

if __name__ == '__main__':
    main()
