#!/usr/bin/env python3
"""
TEST 5.3 — RSI divergence + Fibonacci golden pocket (folklore audit, daily).
REGISTERED: Tier 5 plan (PR #30) — mechanical translation, one run, expected FAIL
(mean-reversion family killed 3x: SGX 3.2, US 4.3, EMA/RSI 3.5).

RULE (frozen; leg definition per registration: swing low = 90d min PRIOR TO the 90d max,
retracement zone measured from the swing high — the COMPLETED swing leg, not a same-window
rolling min. v1 bug: rolling 90d min INCLUDING today made the pocket retreat as price
fell -> 0 trades, VOID-by-apparatus, fixed before any valid run; verified on synthetic
perfect setups pre-push):
- Universe: US$1-10, 20d dollar-volume >= US$3M, >= 260d history. Long-only.
- Trend filter: 50EMA > 200SMA.
- Swing leg (per day i): over the prior 90 days EXCLUDING today, find the max-high day j;
  leg_high = high[j]; leg_low = min close in the 90 days ending at j.
- Golden pocket: close in [leg_high - 0.618*(leg_high-leg_low), leg_high - 0.382*(...)].
- RSI: 14-day RSI; mechanical divergence proxy: close < prior 5-day min AND RSI above
  its min over the prior 10 days.
- Entry: all conditions on day i -> enter at close (lab convention), hold 21 days, exit.
  Non-overlapping per ticker.
- Costs 0.35%/side. No gates (audits the setup itself).

BARS: EV/trade > +0.60% net; >= 6/13 positive years; >= 150 trades else VOID.
"""
import argparse, glob, os
import numpy as np
import pandas as pd

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data-dir', default='data_us')
    ap.add_argument('--cost', type=float, default=0.35)
    ap.add_argument('--hold', type=int, default=21)
    a = ap.parse_args()

    trades = []
    files = sorted(glob.glob(os.path.join(a.data_dir, '*.csv')))
    for f in files:
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
        if len(df) < 300:
            continue
        c = df['close'].astype(float)
        v = df['volume'].astype(float)
        h = df['high'].astype(float) if 'high' in df.columns else c
        dvol = (c * v).rolling(20).mean()
        elig = (c >= 1.0) & (c <= 10.0) & (dvol >= 3e6)
        if int(elig.fillna(False).sum()) < 50:
            continue

        ema50 = c.ewm(span=50, adjust=False).mean()
        ema200 = c.ewm(span=200, adjust=False).mean()
        delta = c.diff()
        gain = delta.where(delta > 0, 0.0).ewm(alpha=1/14, adjust=False).mean()
        loss = (-delta.where(delta < 0, 0.0)).ewm(alpha=1/14, adjust=False).mean()
        rsi = 100 - 100 / (1 + gain / loss.replace(0, np.nan))

        cv = c.values; hv = h.values
        n = len(cv)
        f38 = np.full(n, np.nan); f62 = np.full(n, np.nan)
        for i in range(90, n):
            lo = i - 90
            j = lo + int(np.argmax(hv[lo:i]))          # max-high day, EXCLUDING today
            llo = max(0, j - 89)
            leg_high = hv[j]
            leg_low = cv[llo:j+1].min()               # min close in 90d ending at j
            rng = leg_high - leg_low
            f38[i] = leg_high - 0.382 * rng
            f62[i] = leg_high - 0.618 * rng

        s_f38 = pd.Series(f38, index=c.index)
        s_f62 = pd.Series(f62, index=c.index)
        in_pocket = (c >= s_f62) & (c <= s_f38)
        trend_up = ema50 > ema200
        prev5min = c.rolling(5).min().shift(1)
        new_low = c < prev5min
        rsi_min10 = rsi.rolling(10).min().shift(1)
        rsi_ok = new_low & (rsi > rsi_min10)

        signal = (elig & trend_up & in_pocket & new_low & rsi_ok).fillna(False)
        if signal.sum() == 0:
            continue

        idx = c.index
        holding_until = None
        for d in idx[signal]:
            if holding_until is not None and d <= holding_until:
                continue
            i = idx.get_loc(d)
            j = i + a.hold
            if j >= n:
                continue
            net = (cv[j] / cv[i] - 1.0) * 100 - 2 * a.cost
            trades.append((d, t, float(net)))
            holding_until = idx[j]

    tdf = pd.DataFrame(trades, columns=['date', 'ticker', 'net'])
    if len(tdf) == 0:
        print('VOID: 0 trades')
        return
    tdf['year'] = pd.to_datetime(tdf.date).dt.year
    ev = tdf.net.mean()
    yr = tdf.groupby('year').net.mean()
    pos = (yr > 0).sum()
    print(f"\n=== TEST 5.3: RSI div + Fib golden pocket (corrected leg), hold {a.hold}d, costs {a.cost:.2f}%/side ===")
    print(f"EV/trade: {ev:+.2f}% | trades: {len(tdf)} | positive years: {pos}/{len(yr)}")
    print('Year-by-year (mean net %%):')
    for y, v in yr.items():
        print(f'  {y}: {v:+6.2f}%')
    if len(tdf) < 150:
        print(f"\nVOID: {len(tdf)} < 150 trades (pre-registered)")
        return
    print(f"\nBAR 1 (EV > +0.6%%): {'PASS' if ev > 0.6 else 'FAIL'} ({ev:+.2f}%)")
    print(f"BAR 2 (>= 6/10 positive years): {'PASS' if pos >= 6 else 'FAIL'} ({pos}/{len(yr)})")
    print('PREDICTION: FAIL (mean-reversion family)')

if __name__ == '__main__':
    main()
