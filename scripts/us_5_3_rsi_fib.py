#!/usr/bin/env python3
"""
TEST 5.3 — RSI divergence + Fibonacci golden pocket (folklore audit, daily).
REGISTERED: Tier 5 plan (PR #30) — mechanical translation, one run, expected FAIL
(mean-reversion family killed 3x: SGX 3.2, US 4.3, EMA/RSI 3.5).

RULE (frozen):
- Universe: US$1-10, 20d dollar-volume >= US$3M, >= 260d history. Long-only.
- Trend filter: 50EMA > 200SMA (SMA via EMA in pandas: ewm span).
- Pullback: daily close into 38.2-61.8% golden pocket of the last 90-day swing leg
  (swing low = 90d min prior to 90d max; retracement zone from swing high).
- RSI: 14-day RSI regular bullish divergence — price makes a lower low within the
  pullback (close < previous 5-day min) while RSI(14) is higher than its value at
  that previous low (mechanical proxy for divergence).
- Entry: all conditions true on the same day -> enter at next-day open proxy (close
  to close, consistent with lab convention), hold 21 days (monthly-equivalent),
  then exit. Non-overlapping: a ticker cannot re-enter while holding.
- Costs 0.35%/side. No gates (this tests the setup itself, not a portfolio).

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
        if (c < 1).any() is False:
            pass
        # eligibility series (universe filters)
        elig = (c >= 1.0) & (c <= 10.0) & (dvol >= 3e6)
        if elig.sum() < 50:
            continue

        # indicators
        ema50 = c.ewm(span=50, adjust=False).mean()
        ema200 = c.ewm(span=200, adjust=False).mean()
        delta = c.diff()
        gain = delta.where(delta > 0, 0.0).ewm(alpha=1/14, adjust=False).mean()
        loss = (-delta.where(delta < 0, 0.0)).ewm(alpha=1/14, adjust=False).mean()
        rsi = 100 - 100 / (1 + gain / loss.replace(0, np.nan))

        swing_high_90 = h.rolling(90).max()
        swing_low_win = c.rolling(90).min().shift(1)  # proxy low window
        # Fib golden pocket: for day i, leg high = 90d max; leg low = min of 90d
        # window ending 5 days before the high printed (approx). Mechanical proxy:
        # low = rolling 90d min over same window as high.
        leg_high = swing_high_90
        leg_low = c.rolling(90).min()
        fib38 = leg_high - 0.382 * (leg_high - leg_low)
        fib62 = leg_high - 0.618 * (leg_high - leg_low)

        prev5min = c.rolling(5).min().shift(1)
        in_pocket = (c >= fib38) & (c <= fib62)
        trend_up = ema50 > ema200
        new_low = c < prev5min
        # divergence proxy: price makes new 5d low but RSI is above its 10-day min
        # (i.e., RSI not making a corresponding low)
        rsi_min10 = rsi.rolling(10).min().shift(1)
        rsi_ok = new_low & (rsi > rsi_min10)

        signal = elig & trend_up & in_pocket & new_low & rsi_ok
        if signal.sum() == 0:
            continue

        # entries with hold, non-overlapping
        idx = c.index
        sig_dates = idx[signal.fillna(False)]
        holding_until = None
        for d in sig_dates:
            if holding_until is not None and d <= holding_until:
                continue
            i = idx.get_loc(d)
            j = i + a.hold
            if j >= len(idx):
                continue
            entry_px = c.iloc[i]
            exit_px = c.iloc[j]
            net = (exit_px / entry_px - 1.0) * 100 - 2 * a.cost
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
    print(f"\n=== TEST 5.3: RSI div + Fib golden pocket, hold {a.hold}d, costs {a.cost:.2f}%/side ===")
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
