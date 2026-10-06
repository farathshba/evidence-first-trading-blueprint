#!/usr/bin/env python3
"""Overnight edge on SGX: buy at today's close, sell at tomorrow's open.
Universe: liquid names (>= min dollar-vol). Variants: all names vs trend filter
(close > SMA200). Reports the strategy EV after costs AND the raw market-wide
overnight vs intraday decomposition so we can see WHERE any edge lives."""
import argparse, glob, math, os
import pandas as pd

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument("--data-dir", default="data_v2_clean")
ap.add_argument("--trend-filter", action="store_true", help="only trade names with close > SMA200")
ap.add_argument("--top-liquidity", type=int, default=50, help="trade only the N most-liquid names")
ap.add_argument("--min-price", type=float, default=0.20)
ap.add_argument("--cost-pct", type=float, default=0.35)
a = ap.parse_args()
cost = a.cost_pct / 100.0

books, overnights, intradays = {}, [], []
for fp in sorted(glob.glob(os.path.join(a.data_dir, "*.csv"))):
    t = os.path.basename(fp).replace(".csv", "")
    if t.startswith("_") or t == "ES3_SI": continue
    try:
        df = pd.read_csv(fp)
        df.columns = [c.lower().strip() for c in df.columns]
        if not {"open", "close"}.issubset(df.columns) or len(df) < 260: continue
        df = df.dropna(subset=["open", "close"])
        df["dvol"] = (df["close"] * df["volume"]).rolling(60).mean() if "volume" in df.columns else 1e9
        df["sma200"] = df["close"].rolling(200).mean()
        books[t] = df
        on = (df["open"].shift(-1) / df["close"] - 1)          # close -> next open
        intr = (df["close"] / df["open"] - 1)                   # open -> same close
        overnights.append(on.dropna()); intradays.append(intr.dropna())
    except Exception:
        pass

# market-wide decomposition (raw, no costs, all tickers)
all_on = pd.concat(overnights); all_in = pd.concat(intradays)
print(f"\n== RAW DECOMPOSITION ({len(overnights)} tickers, {len(all_on)} overnight obs) ==")
print(f"mean overnight: {100*all_on.mean():+.4f}%   mean intraday: {100*all_in.mean():+.4f}%")
print(f"median overnight: {100*all_on.median():+.4f}%   overnight > 0 share: {100*(all_on > 0).mean():.1f}%")

# portfolio sim: every day, hold the top-N most liquid eligible names close->open
dates = sorted(set().union(*[set(b.index) for b in books.values()]))
pnl_by_date, trades = [], 0
for d in dates:
    cands = []
    for t, b in books.items():
        if d not in b.index: continue
        i = b.index.get_loc(d)
        row = b.iloc[i]
        if i + 1 >= len(b): continue
        nxt = b.iloc[i + 1]
        if row["close"] < a.min_price or pd.isna(row["dvol"]): continue
        if a.trend_filter and (pd.isna(row["sma200"]) or row["close"] <= row["sma200"]): continue
        cands.append((t, row["dvol"], row["close"], nxt["open"]))
    cands.sort(key=lambda x: -x[1])
    sel = cands[: a.top_liquidity]
    day_pnl, day_trades = 0.0, 0
    for t, dv, c, o in sel:
        gross = (o / c - 1) - 2 * cost          # buy at close, sell at open, both legs costed
        day_pnl += gross; day_trades += 1
    if day_trades:
        pnl_by_date.append((d, day_pnl / day_trades, day_trades))
        trades += day_trades

df = pd.DataFrame(pnl_by_date, columns=["date", "ret", "n"])
ev = df["ret"].mean() * 100
sharpe = df["ret"].mean() / df["ret"].std() * math.sqrt(252) if df["ret"].std() > 0 else float("nan")
eq = (1 + df["ret"]).cumprod()
dd = (eq / eq.cummax() - 1).min() * 100
df["year"] = df["date"].astype(str).str[:4]
print(f"\n=== SGX OVERNIGHT EDGE VERDICT {'(trend-filtered) ' if a.trend_filter else ''}===")
print(f"top-{a.top_liquidity} liquidity | EV/round-trip after costs: {ev:+.3f}%  Sharpe: {sharpe:.2f}  cum: {100*(eq.iloc[-1]-1):+.1f}%  maxDD: {dd:.1f}%")
print(f"round-trips: {trades}")
print("\nBy year (avg net EV %/trade, net positive days share):")
g = df.groupby("year").agg(ev_pct=("ret", lambda x: 100*x.mean()), pos_share=("ret", lambda x: 100*(x>0).mean()), n=("ret","size"))
print(g.round(2).to_string())
print("\nBAR: EV > +0.6%/trade after costs AND net positive in >= 6 of 10 years.")
