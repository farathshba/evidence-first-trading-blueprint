#!/usr/bin/env python3
"""screen_universe.py — generic rule-based screener over a folder of per-ticker OHLCV CSVs.

Expects one CSV per ticker with columns: Date, Open, High, Low, Close, (Adj Close), Volume.
Edit the constants to match YOUR rules. No network needed — screens local files only.

Usage:
    DATA_DIR=~/data python3 screen_universe.py
"""
import os, glob
import pandas as pd

DATA_DIR     = os.environ.get("DATA_DIR", "./data")
VOL_SPIKE    = 1.5      # today's volume >= this x the prior 20-day average
MIN_AVG_VOL  = 500_000  # average shares/day (judge in dollars for cheap stocks!)
ATR_MAX_PCT  = 0.15     # ATR(14) < this fraction of price
SMA_FAST, SMA_SLOW = 20, 200

def load(fp):
    df = pd.read_csv(fp)
    cols = {c.lower().replace(" ", ""): c for c in df.columns}
    ren = {cols[s]: s for s in ["date","open","high","low","close","adjclose","volume"] if s in cols}
    df = df.rename(columns=ren)
    if "adjclose" in df.columns: df["close"] = df["adjclose"]
    keep = [c for c in ["date","close","high","low","volume"] if c in df.columns]
    df = df[keep].dropna(subset=["close","high","low","volume"])
    return df[df["volume"] > 0].reset_index(drop=True)

def check(df):
    if len(df) < SMA_SLOW + 1: return None
    c, h, l, v = df["close"], df["high"], df["low"], df["volume"]
    price = c.iloc[-1]
    sma_f = c.iloc[-SMA_FAST:].mean()
    sma_s = c.iloc[-SMA_SLOW:].mean()
    avg_vol = v.iloc[-21:-1].mean()
    pc = c.shift(1)
    tr = pd.concat([h-l, (h-pc).abs(), (l-pc).abs()], axis=1).max(axis=1)
    atr = tr.iloc[-14:].mean()
    spike = v.iloc[-1] / avg_vol if avg_vol > 0 else 0
    conds = {
        "trend": bool(price > sma_s),
        "momentum": bool(price > sma_f),
        "spike": bool(spike >= VOL_SPIKE),
        "atr": bool(atr < ATR_MAX_PCT * price),
        "liquidity": bool(avg_vol > MIN_AVG_VOL),
    }
    n = int(sum(conds.values()))
    return dict(price=round(float(price), 4), n=n,
                spike=round(float(spike), 2),
                atr_pct=round(100 * float(atr) / float(price), 1),
                avg_vol=int(avg_vol), dollar_vol=int(avg_vol * price),
                verdict="ENTER" if all(conds.values()) else "WAIT")

rows, latest = [], ""
for fp in sorted(glob.glob(os.path.join(DATA_DIR, "*.csv"))):
    name = os.path.basename(fp).replace(".csv", "")
    if name.startswith("_"): continue
    try:
        df = load(fp)
        if "date" in df.columns and len(df):
            latest = max(latest, str(df["date"].iloc[-1])[:10])
        r = check(df)
        if r: rows.append((name, r))
    except Exception as e:
        print(f"skip {name}: {e}")

passes = sorted([x for x in rows if x[1]["verdict"] == "ENTER"], key=lambda x: -x[1]["spike"])
near   = sorted([x for x in rows if x[1]["verdict"] != "ENTER" and x[1]["n"] >= 4], key=lambda x: -x[1]["spike"])

print(f"\nUniverse screened: {len(rows)} | data through {latest or '?'}")
print(f"ENTER ({len(passes)}):")
for t, r in passes:
    print(f"  {t:10} price={r['price']:<9} spike={r['spike']}x  atr={r['atr_pct']}%  vol={r['avg_vol']:,}  dollar_vol={r['dollar_vol']:,}/day")
print(f"\nNEAR-MISSES, 4/5 conditions ({len(near)}):")
for t, r in near[:30]:
    print(f"  {t:10} price={r['price']:<9} spike={r['spike']}x  atr={r['atr_pct']}%")
if not passes:
    print("\n(no ENTER signals — no new entries today)")
print("\nReminder: stale ENTERs are leads, not signals. Live-verify before acting.")
