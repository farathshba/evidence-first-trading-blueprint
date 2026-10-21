#!/usr/bin/env python3
"""
TEST 5.4 — Opening Range Breakout (15-min ORB). PRE-REGISTERED: arkenstone PR #9.
FROZEN RULE: universe = frozen 4.5 daily universe (US$1-10, 20d dvol>=US$3M);
OR = 09:30-09:45 ET range; entry: minute close strictly > OR high, gap-up only
(day open >= prior day close); exit: same-day 16:00 close; long-only; 0.35%/side.
FROZEN BARS: EV > +0.60% net; >= 6/10 positive years; >= 500 trades else VOID;
report max losing streak + per-year means. VERDICT: PASS / FAIL / VOID.
Prediction (registered): FAIL (friction wall).
ONE RUN. No gate-widening.
Data: data_us_minute/<TICKER>.csv (datetime,open,high,low,close,volume; US/Eastern)
      data_us/<TICKER>.csv daily (universe eligibility; same files as 5.2/4.5)
"""
import argparse, glob, os
import numpy as np
import pandas as pd

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--minute-dir', default='data_us_minute')
    ap.add_argument('--daily-dir', default='data_us')
    ap.add_argument('--cost', type=float, default=0.35)
    ap.add_argument('--start', default='2016-01-01')
    ap.add_argument('--end', default='2026-07-15')
    a = ap.parse_args()

    # ---- 1. daily universe eligibility (frozen 4.5 filters) ----
    elig_days = {}   # ticker -> set of eligible dates
    for f in sorted(glob.glob(os.path.join(a.daily_dir, '*.csv'))):
        t = os.path.basename(f)[:-4]
        if t.startswith('_') or t.upper() == 'SPY':
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
        dvol = (c * v).rolling(20).mean()
        e = (c >= 1.0) & (c <= 10.0) & (dvol >= 3e6)
        elig_days[t] = set(e.index[e.fillna(False)].strftime('%Y-%m-%d'))

    print(f"[diag] daily universe built: {len(elig_days)} tickers")
    print("[diag] SURVIVORSHIP CAVEAT: daily snapshot universe (Stage 1 apparatus).")

    t_lo, t_hi = pd.Timestamp(a.start), pd.Timestamp(a.end)
    trades = []
    files = sorted(glob.glob(os.path.join(a.minute_dir, '*.csv')))
    print(f"[diag] minute files: {len(files)}")
    for f in files:
        t = os.path.basename(f)[:-4]
        if t not in elig_days:
            continue
        ed = elig_days[t]
        try:
            df = pd.read_csv(f)
            df.columns = [str(c).strip().lower() for c in df.columns]
            if 'datetime' in df.columns:
                df.index = pd.to_datetime(df['datetime'])
            elif 'date' in df.columns and 'time' in df.columns:
                df.index = pd.to_datetime(df['date'] + ' ' + df['time'])
            else:
                dc = [c for c in df.columns if 'date' in c or 'time' in c]
                if not dc:
                    continue
                df.index = pd.to_datetime(df[dc[0]])
            df = df.sort_index()
        except Exception:
            continue
        if df.empty:
            continue
        df['dstr'] = df.index.strftime('%Y-%m-%d')
        df['mins'] = df.index.hour * 60 + df.index.minute
        for d, g in df.groupby('dstr'):
            if d not in ed:
                continue
            g = g[(g['mins'] >= 570) & (g['mins'] <= 960)]  # 09:30-16:00 ET
            if g.empty:
                continue
            prior_close = g['close'].astype(float).iloc[0]  # placeholder; fixed below
            # gap filter needs PRIOR DAY close: track via first-bar open vs prev day
            # (handled by keeping a per-ticker prev-day close)
            day_open = float(g['open'].iloc[0])
            or_w = g[g['mins'] < 585]   # 09:30-09:44:59 => first 15 minutes
            if or_w.empty:
                continue
            or_high = float(or_w['high'].max())
            after = g[g['mins'] >= 585]
            if after.empty:
                continue
            entry = None
            for ts, row in after.iterrows():
                if float(row['close']) > or_high:
                    entry = float(row['close'])
                    break
            if entry is None:
                continue
            exit_px = float(g['close'].iloc[-1])  # 16:00 close (last bar of day)
            net = (exit_px / entry - 1.0) * 100 - 2 * a.cost
            trades.append((pd.Timestamp(d), t, net, day_open))

    # NOTE: gap-up filter is applied post-hoc below using day_open vs prev close
    # available from the daily files (kept exact per registration).
    tdf = pd.DataFrame(trades, columns=['date', 'ticker', 'net', 'day_open'])
    # attach prior close from daily data for the gap filter
    pc = {}
    for t in tdf['ticker'].unique():
        fp = os.path.join(a.daily_dir, t + '.csv')
        try:
            d = pd.read_csv(fp)
            d.columns = [str(c).strip().lower() for c in d.columns]
            d['date'] = pd.to_datetime(d['date']).dt.normalize()
            pc[t] = d.set_index('date')['close'].astype(float)
        except Exception:
            pass
    keep = []
    for _, r in tdf.iterrows():
        s = pc.get(r['ticker'])
        if s is None:
            continue
        pos = s.index.searchsorted(r['date'])
        if pos == 0:
            continue
        prev_c = s.iloc[pos - 1]
        if r['day_open'] >= prev_c:   # gap-up only (frozen rule)
            keep.append(True)
        else:
            keep.append(False)
    tdf = tdf[np.array(keep)]

    tdf['year'] = tdf['date'].dt.year
    yr = tdf.groupby('year')['net'].agg(['mean', 'count'])
    ev = tdf['net'].mean() if len(tdf) else float('nan')
    # max losing streak
    streak = mx = 0
    for n in tdf.sort_values('date')['net']:
        streak = streak + 1 if n < 0 else 0
        mx = max(mx, streak)

    print(f"\n=== TEST 5.4: 15m ORB (gap-up only, same-day exit), costs {a.cost:.2f}%/side ===")
    print(f"EV/trade: {ev:+.2f}% | trades: {len(tdf)} | positive years: {(yr['mean']>0).sum()}/{len(yr)} | max losing streak: {mx}")
    print("\nYear-by-year:")
    for y, row in yr.iterrows():
        print(f"  {y}: mean {row['mean']:+6.2f}%  n={int(row['count'])}")

    if len(tdf) < 500:
        print(f"\nVOID: {len(tdf)} < 500 trades (pre-registered)")
        return
    b1 = ev > 0.60
    b2 = (yr['mean'] > 0).sum() >= 6
    print(f"\nBAR 1 (EV > +0.60%): {'PASS' if b1 else 'FAIL'} ({ev:+.2f}%)")
    print(f"BAR 2 (>= 6/10 positive years): {'PASS' if b2 else 'FAIL'} ({(yr['mean']>0).sum()}/{len(yr)})")

if __name__ == '__main__':
    main()
