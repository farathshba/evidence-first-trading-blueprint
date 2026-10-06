#!/usr/bin/env python3
"""Mean reversion on SGX: buy 3-day dips (cumulative -8% or more) on names above
SMA200, exit after --hold days or on close >= SMA20, whichever first. Long-only,
equal-weight slots, real costs. Trend filter is the whole thesis: no dip-buying downtrends."""
import argparse, glob, math, os
import pandas as pd

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument("--data-dir", default="data_v2_clean")
ap.add_argument("--dip", type=float, default=8.0, help="min 3-day %% drop to trigger")
ap.add_argument("--hold", type=int, default=5, help="max holding days")
ap.add_argument("--max-slots", type=int, default=5)
ap.add_argument("--min-price", type=float, default=0.20)
ap.add_argument("--min-dollar-vol", type=float, default=200_000)
ap.add_argument("--capital", type=float, default=100_000)
ap.add_argument("--cost-pct", type=float, default=0.35)
a = ap.parse_args()
cost = a.cost_pct / 100.0

books = {}
for fp in sorted(glob.glob(os.path.join(a.data_dir, "*.csv"))):
    t = os.path.basename(fp).replace(".csv", "")
    if t.startswith("_") or t == "ES3_SI": continue
    try:
        df = pd.read_csv(fp)
        df.columns = [c.lower().strip() for c in df.columns]
        if "close" not in df.columns or len(df) < 260: continue
        df = df.dropna(subset=["close"]).set_index("date")
        df["sma20"] = df["close"].rolling(20).mean()
        df["sma200"] = df["close"].rolling(200).mean()
        df["r3"] = df["close"].pct_change(3) * 100
        df["dvol"] = (df["close"] * df["volume"]).rolling(20).mean() if "volume" in df.columns else 1e9
        books[t] = df
    except Exception:
        pass

all_dates = sorted(set().union(*[set(b.index) for b in books.values()]))
cash, holdings, trades, equity = a.capital, {}, [], []

for d in all_dates:
    # exits first: time-based or recovery to sma20
    for t in list(holdings):
        h = holdings[t]; b = books[t]
        if d not in b.index:
            if h["days"] >= a.hold + 2:  # stale data, force-exit at last known
                px = h["last"]; proc = px * h["shares"] * (1 - cost)
                trades.append(dict(ticker=t, ret_pct=100*(proc - h["basis"])/h["basis"], pnl=proc - h["basis"], exit_date=h["lastd"]))
                cash += proc; del holdings[t]
            continue
        px = b.loc[d, "close"]; h["days"] += 1; h["last"] = px; h["lastd"] = d
        rec = px >= b.loc[d, "sma20"]
        if rec or h["days"] >= a.hold:
            proc = px * h["shares"] * (1 - cost)
            trades.append(dict(ticker=t, ret_pct=100*(proc - h["basis"])/h["basis"], pnl=proc - h["basis"], exit_date=d))
            cash += proc; del holdings[t]
    # entries: dip + above sma200 + liquid
    if len(holdings) < a.max_slots:
        cands = []
        for t, b in books.items():
            if t in holdings or d not in b.index: continue
            row = b.loc[d]
            if not (row["close"] > 0 and row["close"] > row["sma200"] and pd.notna(row["sma200"])): continue
            if row["r3"] <= -a.dip and row["close"] >= a.min_price and row["dvol"] >= a.min_dollar_vol:
                cands.append((t, row["r3"]))
        cands.sort(key=lambda x: x[1])  # deepest dip first
        stake = cash / (a.max_slots - len(holdings))
        for t, _ in cands:
            if len(holdings) >= a.max_slots or cash < stake: break
            px = books[t].loc[d, "close"]
            sh = int(stake * (1 - cost) // px)
            if sh <= 0: continue
            out = sh * px
            if out > cash: continue
            cash -= out
            holdings[t] = dict(shares=sh, basis=out, days=0, last=px, lastd=d)
    nav = cash + sum(h["last"] * h["shares"] for h in holdings.values())
    equity.append((d, nav))

for t, h in holdings.items():  # close out at end
    proc = h["last"] * h["shares"] * (1 - cost)
    trades.append(dict(ticker=t, ret_pct=100*(proc - h["basis"])/h["basis"], pnl=proc - h["basis"], exit_date=h["lastd"]))
    cash += proc
nav = cash
eq = pd.DataFrame(equity, columns=["date", "nav"])
rets = eq["nav"].pct_change().dropna()
sharpe = rets.mean()/rets.std()*math.sqrt(252) if rets.std() > 0 else float("nan")
dd = (eq["nav"]/eq["nav"].cummax() - 1).min() * 100
td = pd.DataFrame(trades)
print("\n=== SGX MEAN REVERSION VERDICT ===")
print(f"Capital {a.capital:,.0f} -> {nav:,.0f}  total: {100*(nav/a.capital-1):+.1f}%  Sharpe: {sharpe:.2f}  maxDD: {dd:.1f}%")
if not td.empty:
    wins = td[td.pnl > 0]
    yr = td.copy(); yr["year"] = yr.exit_date.str[:4]
    print(f"Round-trips: {len(td)}  win rate: {100*len(wins)/len(td):.1f}%  avg: {td.ret_pct.mean():+.2f}%")
    print("\nBy exit year:")
    print(yr.groupby("year").agg(trades=("pnl","size"), net_pnl=("pnl","sum")).round(0).to_string())
print("\nBAR: EV > +0.6%/trade after costs AND net positive in >= 6 of 10 years.")
