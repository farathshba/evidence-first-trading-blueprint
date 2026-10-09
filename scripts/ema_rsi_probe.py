#!/usr/bin/env python3
"""
3.5 EMA 9/20 + RSI(14) daily probe — PRE-REGISTERED 9 Oct 2026, before any run.
Tests the ema-9-20-rsi-atr-trading skill at the closest testable granularity.
The skill's 15M/1H/4H versions are untestable with lab data (daily only) ->
not adoptable regardless; this probe tests the daily cousin.

SPEC (long only):
  Entry: EMA9 crosses above EMA20 (on Adj Close) AND RSI14 > 50 AND close > EMA9,
         on an eligible name (price >= S$1, 20d dollar-vol >= S$1M),
         regime open (ES3 > SMA200). Fill: next day's Open.
  Exit:  EMA9 crosses below EMA20 OR close < EMA20. Fill: next day's Open.
  ATR stops/targets EXCLUDED a priori (refuted component, retired Oct 2026).
  Costs: 0.45%/side (both sides applied to every trade).

PRE-REGISTERED BARS (same as every Tier 3 test):
  Stage 1: EV > +0.6%/trade after costs AND positive in >= 6/10 years
  Stage 2: OOS (2022-26) EV >= +0.6% AND positive in >= 4/5 years
"""
import argparse, glob, os
import numpy as np
import pandas as pd

def rsi_wilder(close, n=14):
    d = close.diff()
    up, dn = d.clip(lower=0.0), -d.clip(upper=0.0)
    ru = up.ewm(alpha=1/n, adjust=False).mean()
    rd = dn.ewm(alpha=1/n, adjust=False).mean()
    rs = ru / rd.replace(0, np.nan)
    return 100 - 100/(1+rs)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data-dir', default='data_v3_clean')
    ap.add_argument('--cost', type=float, default=0.45)
    ap.add_argument('--min-price', type=float, default=1.0)
    ap.add_argument('--min-dvol', type=float, default=1e6)
    ap.add_argument('--entry-start', default=None)
    ap.add_argument('--entry-end', default=None)
    a = ap.parse_args()

    # Regime: ES3 > SMA200 (file first, yfinance fallback)
    p = os.path.join(a.data_dir, 'ES3.SI.csv')
    if os.path.exists(p):
        e = pd.read_csv(p, parse_dates=['Date']).sort_values('Date')
    else:
        import yfinance as yf
        e = yf.download('ES3.SI', start='2014-01-01', auto_adjust=False).reset_index()
        e.columns = [str(c).title() for c in e.columns]
    es3 = e.set_index('Date')['Adj Close'].astype(float)
    reg_series = (es3 > es3.rolling(200).mean()).astype(float)

    trades = []
    files = sorted(glob.glob(os.path.join(a.data_dir, '*.csv')))
    for f in files:
        base = os.path.basename(f)[:-4]
        if base.upper().startswith(('ES3', '^STI')): continue
        try:
            df = pd.read_csv(f, parse_dates=['Date']).sort_values('Date').reset_index(drop=True)
        except Exception:
            continue
        if len(df) < 260: continue
        adj   = df['Adj Close'].astype(float)
        close = df['Close'].astype(float)
        open_ = df['Open'].astype(float)
        vol   = df['Volume'].astype(float)
        if adj.isna().all(): continue

        ema9, ema20 = adj.ewm(span=9, adjust=False).mean(), adj.ewm(span=20, adjust=False).mean()
        rsi = rsi_wilder(adj)
        dvol = (close * vol).rolling(20).mean()

        cross_up = (ema9 > ema20) & (ema9.shift(1) <= ema20.shift(1))
        cross_dn = (ema9 < ema20) & (ema9.shift(1) >= ema20.shift(1))
        entry_ok = cross_up & (rsi > 50) & (close > ema9) & (close >= a.min_price) & (dvol >= a.min_dvol)
        exit_sig = cross_dn | (close < ema20)
        if a.entry_start: entry_ok &= (df['Date'] >= pd.Timestamp(a.entry_start))
        if a.entry_end:   entry_ok &= (df['Date'] <= pd.Timestamp(a.entry_end))

        reg = reg_series.reindex(df['Date'], method='ffill').fillna(0.0).values
        eo, xs, n = entry_ok.values, exit_sig.values, len(df)
        i = 0
        while i < n - 1:
            if eo[i] and reg[i] == 1 and not np.isnan(open_.iloc[i+1]):
                ep = open_.iloc[i+1]; j = i + 1
                while j < n - 1 and not xs[j]: j += 1
                if j >= n - 1:
                    xp, xd = adj.iloc[n-1], df['Date'].iloc[n-1]; j = n - 1
                else:
                    xp, xd = open_.iloc[j+1], df['Date'].iloc[j+1]
                if ep and not np.isnan(xp) and xp > 0:
                    net = (xp/ep - 1) * 100 - 2*a.cost
                    trades.append((df['Date'].iloc[i], base, round(ep,3), round(xp,3), xd,
                                   round(net,3), (j+1)-(i+1)))
                i = j + 1
            else:
                i += 1

    t = pd.DataFrame(trades, columns=['sig_date','ticker','entry','exit','exit_date','ev_pct','hold_days'])
    if t.empty:
        print("NO TRADES"); return
    t['year'] = pd.to_datetime(t.sig_date).dt.year
    print(f"Trades: {len(t)} | EV/trade: {t.ev_pct.mean():+.2f}% | median: {t.ev_pct.median():+.2f}% | "
          f"win rate: {(t.ev_pct>0).mean()*100:.1f}% | avg hold: {t.hold_days.mean():.0f}d")
    print("\nYear-by-year:")
    yr = t.groupby('year').agg(n=('ev_pct','size'), ev=('ev_pct','mean'), win=('ev_pct', lambda s: (s>0).mean()*100))
    for y, r in yr.iterrows():
        print(f"  {y}: n={int(r.n):4d}  EV={r.ev:+.2f}%  win={r.win:.0f}%")
    pos_years = (yr.ev > 0).sum(); tot_years = len(yr)
    print(f"\nPositive years: {pos_years}/{tot_years}")
    print(f"BAR 1 (EV > +0.6% after costs):  {'PASS' if t.ev_pct.mean() > 0.6 else 'FAIL'}")
    print(f"BAR 2 (>= 6/10 positive years): {'PASS' if pos_years >= 6 else 'FAIL'}")
    t.to_csv('results/ema_rsi_probe_trades.csv', index=False)

if __name__ == '__main__':
    main()
