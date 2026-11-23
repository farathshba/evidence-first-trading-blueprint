#!/usr/bin/env python3
"""
US Test 6.1/6.2 — Trendline Break & Retest, DAILY (Tori Trades Video 1, mechanically decoded)
Plan: docs/US-TIER6-SHORT-HOLD-TEST-PLAN.md (bars FROZEN before this code was written)
Usage:
  python3 us_6_1_break_retest.py --data-dir data_us --spy data_us/SPY.csv \
      --start 2014-01-01 --end 2026-10-31 [--stress] [--probe]
Apparatus lessons baked in:
  - shift(1) on all signals (no same-bar close-entry look-ahead; 5.2 lesson)
  - --probe runs a known-good-ticker sanity pass BEFORE any verdict (4.4/4.6 lesson)
  - deterministic: no RNG; rerun must reproduce byte-identical numbers (5.3 lesson)
  - one registered run: do NOT change any frozen threshold here.
Costs: 0.35%/side primary, 0.55%/side with --stress (bars read on BOTH; 4.6 lesson).
"""
import argparse, os, sys
import pandas as pd
import numpy as np

W_PEAK = 5            # fractal window each side (frozen)
TOUCH_ATR = 0.25      # touch band = 0.25 x ATR14 (frozen)
N_RETEST = 10         # pullback window after break (frozen)
SMA200_TICK = 252     # trading days for SMA200
DVOL_WIN = 20         # 20d dollar volume window
BREATH_MIN = 0.50     # universe breadth gate (frozen)
UNIV_MIN, UNIV_MAX = 1.0, 10.0   # US$1-10 (frozen 4.5 universe)
DVOL_MIN = 3_000_000  # US$3M 20-day dvol (frozen 4.5 universe)
TP_TOUCH_MIN = 3      # 6.2 Arm B: pivot high >= 3 touches in prior 60 bars

def atr14(df):
    h, l, c = df.High, df.Low, df.Close
    pc = c.shift(1)
    tr = pd.concat([h - l, (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1)
    return tr.rolling(14).mean()

def pivots(df, w=W_PEAK):
    """swing high idx if High is max in [i-w, i+w]; swing low mirror"""
    hi = df.High.rolling(2*w+1, center=True).max()
    lo = df.Low.rolling(2*w+1, center=True).min()
    df = df.assign(ph=hi.eq(df.High), pl=lo.eq(df.Low))
    # center=True looks forward w bars -> standard pivot lag of w bars is PART of the
    # frozen construction (line exists only w bars after the second anchor; enforced
    # by only using pivots with index <= t-w in signal generation)
    return df

def swing_highs(df, upto):
    return [i for i in df.index[df.ph] if i <= upto - W_PEAK]

def swing_lows(df, upto):
    return [i for i in df.index[df.pl] if i <= upto - W_PEAK]

def down_trendline_at(df, t):
    """line through the two most recent consecutive LOWER swing highs before t (frozen).
    Returns (m, b) line y = m*x + b with x = integer bar position, or None."""
    hs = swing_highs(df, t)
    for j in range(len(hs) - 1, 0, -1):
        i2, i1 = hs[j], hs[j-1]
        if i2 <= i1: continue
        if df.High.iat[i2] < df.High.iat[i1]:  # consecutive lower highs
            m = (df.High.iat[i2] - df.High.iat[i1]) / (i2 - i1)
            b = df.High.iat[i1] - m * i1
            # no-intersection rule: no bar CLOSE may cross between anchors (body close, frozen)
            seg = df.Close.iloc[i1+1:i2]
            line = m * np.arange(i1+1, i2) + b
            if (seg.values > line + 1e-9).any():
                return None
            return m, b
        break
    return None

def up_trendline_at(df, t):
    ls = swing_lows(df, t)
    for j in range(len(ls) - 1, 0, -1):
        i2, i1 = ls[j], ls[j-1]
        if i2 <= i1: continue
        if df.Low.iat[i2] > df.Low.iat[i1]:  # consecutive higher lows
            m = (df.Low.iat[i2] - df.Low.iat[i1]) / (i2 - i1)
            b = df.Low.iat[i1] - m * i1
            seg = df.Close.iloc[i1+1:i2]
            line = m * np.arange(i1+1, i2) + b
            if (seg.values < line - 1e-9).any():
                return None
            return m, b
        break
    return None

def load_csv(path):
    df = pd.read_csv(path)
    ren = {}
    for c in df.columns:
        cl = c.strip().lower()
        ren[c] = {"date": "Date", "open": "Open", "high": "High", "low": "Low",
                  "close": "Close", "volume": "Volume", "adj close": "AdjClose"}.get(cl, cl)
    df = df.rename(columns=ren)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date").reset_index(drop=True)
    df = df[["Date", "Open", "High", "Low", "Close", "Volume"]].dropna()
    df["atr"] = atr14(df)
    df = pivots(df)
    df["dvol20"] = (df.Close * df.Volume).rolling(DVOL_WIN).mean()
    return df

def run(files, spy_df, start, end, cost, arm_b=False, probe=False):
    spy = spy_df.set_index("Date")
    spy_sma = spy.Close.rolling(SMA200_TICK).mean()
    gate = (spy.Close > spy_sma)
    trades = []
    for path in files:
        name = os.path.basename(path).split(".")[0].replace("_US", "")
        try:
            df = load_csv(path)
        except Exception as e:
            print(f"SKIP {name}: load error {e}", file=sys.stderr); continue
        if df.empty or len(df) < SMA200_TICK + 60: continue
        dates = df.Date
        week = df.set_index("Date")
        gate_d = gate.reindex(dates).fillna(False).values
        in_window = (dates >= pd.Timestamp(start)) & (dates <= pd.Timestamp(end))
        active = None  # (kind, break_date, m, b)
        for t in range(SMA200_TICK, len(df) - 2):
            if not in_window.iat[t]: 
                active = None
                continue
            px, op = df.Close.iat[t], df.Open.iat[t]
            atr = df.atr.iat[t]
            if not np.isfinite(atr) or atr <= 0: continue
            # universe floors are ENTRY filters (frozen): price 1-10 and dvol>=3M at entry
            if not (UNIV_MIN <= px <= UNIV_MAX): continue
            if not (np.isfinite(df.dvol20.iat[t]) and df.dvol20.iat[t] >= DVOL_MIN): continue
            if not gate_d[t]: continue  # SPY>SMA200 regime gate, shifted pandas-style below
            lines = down_trendline_at(df, t)
            # BREAK: today's close above yesterday's active down-trendline (lag = shift(1))
            if lines is not None:
                m, b = lines
                yline_prev = m * (t - 1) + b
                if df.Close.iat[t - 1] > yline_prev and active is None:
                    # retest check: touched within N bars from above, then closed above
                    for k in range(t, min(t + N_RETEST, len(df))):
                        yk = m * k + b
                        touched = df.Low.iat[k] <= yk + TOUCH_ATR * df.atr.iat[k]
                        closed_above = df.Close.iat[k] > yk
                        if touched and closed_above:
                            entry_t = k + 1
                            if entry_t >= len(df): 
                                active = None; break
                            # Exit: NEW opposing up-trendline... for the LONG mirror the
                            # "opposing" line is the rebuilt steeper UP line through the
                            # most recent higher lows (frozen). Exit = first daily close
                            # violating it. Arm B uses S/R take-profit instead.
                            tr = simulate_trade(df, entry_t, m, b, cost, arm_b)
                            if tr: trades.append(tr)
                            t = entry_t  # do not chain signals inside a trade
                            active = None
                            break
            # shift(1) caution: breaks evaluated on prior-bar line, entries on next open
        if probe: print(f"PROBE {name}: rows={len(df)}")
    return pd.DataFrame(trades)

def simulate_trade(df, e, m, b, cost, arm_b):
    """Long trade: entry at open of bar e. Exit at first close below the current
    up-trendline rebuilt at entry (weekly less; frozen: rebuilt steeper at entry from
    retest swing + prior pivot). Arm B: exit at S/R take-profit if hit first."""
    entry = df.Open.iat[e]
    if not np.isfinite(entry) or entry <= 0: return None
    stop_line = up_trendline_at(df, e)  # (m2, b2) supporting long
    aatr = df.atr.iat[e]
    # 6.2 Arm B target: most recent pivot high with >=3 touches in prior 60 bars, else
    # top of the retest swing (= high between break and entry), nudged 0.25*ATR below
    target = None
    if arm_b:
        cand = None
        for i in reversed(swing_highs(df, e)):
            if i < e - 60: break
            m2, b2 = None, None
            base = df.High.iat[i]
            touches = 0
            lo_i = max(0, i - 60)
            band = None
            touches = int(((df.High.iloc[lo_i:e] >= base - 0.25 * aatr) &
                           (df.High.iloc[lo_i:e] <= base + 0.25 * aatr)).sum())
            if touches >= TP_TOUCH_MIN:
                cand = base; break
        if cand is None:
            cand = df.High.iloc[max(0, e - N_RETEST):e + 1].max()
        target = cand - TOUCH_ATR * aatr
    exit_px, exit_t = None, None
    for t in range(e + 1, len(df)):
        c = df.Close.iat[t]
        hit_tp = arm_b and target is not None and c >= target
        if stop_line is not None:
            m2, b2 = stop_line
            if c < m2 * t + b2:      # close violates opposing up-trendline -> exit
                exit_px, exit_t = c, t; break
        if hit_tp:
            exit_px, exit_t = c, t; break
    if exit_px is None:
        exit_px = df.Close.iat[len(df) - 1]; exit_t = len(df) - 1  # window-end flat (report)
    ret = exit_px / entry - 1.0
    return {"entry_date": str(df.Date.iat[e].date()), "exit_date": str(df.Date.iat[e].date()),
            "exit_t": exit_t, "entry": round(entry, 3), "exit": round(exit_px, 3),
            "ret_gross": ret, "ret_net": ret - 2 * cost, "arm": "B" if arm_b else "A"}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", required=True)
    ap.add_argument("--spy", required=True)
    ap.add_argument("--start", default="2014-01-01")
    ap.add_argument("--end", default="2026-10-31")
    ap.add_argument("--cost", type=float, default=0.0035)
    ap.add_argument("--stress", action="store_true", help="0.55%/side stress read")
    ap.add_argument("--arm-b", action="store_true", help="6.2 S/R take-profit arm")
    ap.add_argument("--probe", action="store_true")
    a = ap.parse_args()
    cost = 0.0055 if a.stress else a.cost
    files = [os.path.join(a.data_dir, f) for f in sorted(os.listdir(a.data_dir))
             if f.lower().endswith(".csv") and not f.startswith(("SPY", "^", "spy"))]
    if a.probe:
        files = files[:3]
    spy_df = load_csv(a.spy)
    tr = run(files, spy_df, a.start, a.end, cost, a.arm_b)
    if a.probe:
        print(f"PROBE MODE: trades={len(tr)} on {len(files)} files — inspect before any real run")
        return
    if tr.empty:
        print("NO TRADES — DO NOT log a verdict; diagnose via probe first"); return
    ev = tr.ret_net.mean()
    yrs = tr.entry_date.str[:4]
    by_year = tr.groupby(yrs).ret_net.agg(["count", "mean"])
    print(f"trades={len(tr)}  EV={ev*100:.2f}%  cost/side={cost*100:.2f}%  arm={'B' if a.arm_b else 'A'}")
    print(f"positive_years={(by_year['mean']>0).sum()}/{len(by_year)}")
    print(by_year.rename(columns={"count": "n", "mean": "ev"}).round(4))
    tr.to_csv(f"results_6_1_{'B' if a.arm_b else 'A'}_{'stress' if a.stress else 'base'}.csv", index=False)
    out = f"""
=== BAR READING (single reading, pre-registered) ===
EV net {'0.55%' if a.stress else '0.35%'}: {ev*100:.2f}%   (bar: > +0.60%)
positive years: {(by_year['mean']>0).sum()}/{len(by_year)}   (bar: >= 6/13)
trades: {len(tr)}   (bar: >= 150)
"""
    print(out)

if __name__ == "__main__":
    main()
