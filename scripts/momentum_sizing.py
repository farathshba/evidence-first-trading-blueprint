#!/usr/bin/env python3
"""Tier 2 item 1: Sizing study wrapping the ORIGINAL momentum engine verbatim.
Engine (from momentum_backtest.py, the version that PASSED): 126d lookback, top-10,
month-END rebalance, ES3 regime gate, price >= 1.0, dvol >= 1M, 0.35%/side.
Levers on top: --vol-target (scale new-position budget by realized vol), --dd-throttle
(halve budget when NAV drawdown <= -10% from peak, until recovered to -5%)."""
import argparse, glob, math, os
import pandas as pd

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument("--data-dir", default="data_v2_clean")
ap.add_argument("--lookback", type=int, default=126)
ap.add_argument("--top-n", type=int, default=10)
ap.add_argument("--min-price", type=float, default=1.0)
ap.add_argument("--min-dollar-vol", type=float, default=1_000_000)
ap.add_argument("--capital", type=float, default=100_000)
ap.add_argument("--cost-pct", type=float, default=0.35)
ap.add_argument("--regime-gate", type=int, default=1)
ap.add_argument("--vol-target", type=float, default=0.0, help="annualized pct vol target; 0=off")
ap.add_argument("--dd-throttle", action="store_true")
a = ap.parse_args()
cost = a.cost_pct / 100.0

def load(fp):
    df = pd.read_csv(fp)
    cols = {c.lower().replace(" ", ""): c for c in df.columns}
    ren = {cols[s]: s for s in ["date","open","high","low","close","adjclose","volume"] if s in cols}
    df = df.rename(columns=ren)
    if "adjclose" in df.columns: df["close"] = df["adjclose"]
    df = df[["date","close","volume"]].dropna()
    df["d"] = df["date"].astype(str).str[:10]
    return df.set_index("d")

books = {}
for fp in sorted(glob.glob(os.path.join(a.data_dir, "*.csv"))):
    t = os.path.basename(fp).replace(".csv", "")
    if t.startswith("_"): continue
    try: books[t] = load(fp)
    except Exception: pass

regime = None
if a.regime_gate:
    for cand in ("ES3_SI", "ES3", "^STI"):
        if cand in books:
            regime = books[cand]["close"].rolling(200).mean()
            break
    if regime is None:
        print("NOTE: ES3/^STI not in data; regime gate uses universe median instead")
        med = pd.concat([b["close"] for b in books.values()], axis=1).median(axis=1)
        regime = med.rolling(200).mean()

all_dates = sorted(set().union(*[set(b.index) for b in books.values()]))
month_ends = [d for prev, d in zip(all_dates, all_dates[1:]) if prev[:7] != d[:7]]

cash, holdings, trades, equity = a.capital, {}, [], []
nav_hist = []          # daily NAV series for vol targeting / throttle

for d in all_dates:
    # ---- daily mark-to-market (verbatim from original) ----
    nav = cash
    for t in holdings: nav += holdings[t]["shares"] * (books[t].loc[d, "close"] if d in books[t].index else holdings[t]["last"])
    for t in list(holdings): holdings[t]["last"] = books[t].loc[d, "close"] if d in books[t].index else holdings[t]["last"]
    equity.append((d, nav))
    nav_hist.append(nav)

    if d not in month_ends: continue
    # ---- regime gate (verbatim) ----
    if a.regime_gate and regime is not None and d in regime.index and pd.notna(regime.loc[d]) and books.get("ES3_SI", books.get("ES3")) is not None:
        px_series = books.get("ES3_SI", books.get("ES3"))["close"]
        if d in px_series.index and px_series.loc[d] < regime.loc[d]:
            for t in list(holdings):
                px = holdings[t]["last"]; proc = px * holdings[t]["shares"] * (1 - cost)
                trades.append(dict(ticker=t, exit_date=d, pnl=proc - holdings[t]["basis"], ret_pct=100*(proc-holdings[t]["basis"])/holdings[t]["basis"]))
                cash += proc; del holdings[t]
            continue
    # ---- rank (verbatim) ----
    scores = []
    for t, b in books.items():
        if d not in b.index: continue
        i = b.index.get_loc(d)
        if i < a.lookback + 21: continue
        px = b["close"].iloc[i]; past = b["close"].iloc[i - a.lookback]
        dvol = (b["close"] * b["volume"]).iloc[i-20:i].mean()
        if px >= a.min_price and dvol >= a.min_dollar_vol and past > 0:
            scores.append((t, px / past - 1))
    scores.sort(key=lambda x: -x[1])
    target = set(t for t, _ in scores[:a.top_n])
    # ---- sell non-targets (verbatim) ----
    for t in list(holdings):
        if t not in target:
            px = holdings[t]["last"]; proc = px * holdings[t]["shares"] * (1 - cost)
            trades.append(dict(ticker=t, exit_date=d, pnl=proc - holdings[t]["basis"], ret_pct=100*(proc-holdings[t]["basis"])/holdings[t]["basis"]))
            cash += proc; del holdings[t]
    # ---- sizing levers (NEW: scale the stake only; selection identical) ----
    gross = 1.0
    if a.vol_target > 0 and len(nav_hist) > 21:
        s = pd.Series(nav_hist[-21:]); r = s.pct_change().dropna()
        realized = r.std() * math.sqrt(252) * 100 if len(r) >= 10 and r.std() > 0 else 0.0
        if realized > 0: gross = min(1.0, a.vol_target / realized)
    if a.dd_throttle and nav_hist:
        peak = max(nav_hist); dd_now = nav / peak - 1 if peak > 0 else 0.0
        if dd_now <= -0.10: gross *= 0.5
    # ---- buy (verbatim except stake scaled by gross) ----
    stake = cash * gross / max(len(target - set(holdings)), 1)
    for t in sorted(target - set(holdings)):
        px = books[t].loc[d, "close"]
        sh = int(stake // px)
        if sh <= 0: continue
        out = sh * px
        if out > cash: continue
        cash -= out
        holdings[t] = dict(shares=sh, entry=px, edate=d, last=px, basis=out * (1 + cost))

nav = cash + sum(h["last"] * h["shares"] for h in holdings.values())
eq = pd.DataFrame(equity, columns=["date", "nav"])
rets = eq["nav"].pct_change().dropna()
sharpe = rets.mean()/rets.std()*math.sqrt(252) if rets.std() > 0 else float("nan")
dd = (eq["nav"]/eq["nav"].cummax() - 1).min() * 100
td = pd.DataFrame(trades)
mode = f"vol{a.vol_target if a.vol_target>0 else 'OFF'}_" + ("dd" if a.dd_throttle else "nodd")
print(f"\n=== SIZING STUDY [{mode}] ===")
print(f"Capital {a.capital:,.0f} -> {nav:,.0f}  total: {100*(nav/a.capital-1):+.1f}%  Sharpe: {sharpe:.2f}  maxDD: {dd:.1f}%")
if not td.empty:
    yr = td.copy(); yr["year"] = yr.exit_date.astype(str).str[:4]
    pos_years = (yr.groupby("year")["pnl"].sum() > 0).sum()
    print(f"Round-trips: {len(td)}  win rate: {100*(td.pnl>0).mean():.1f}%  EV/trip: {td.ret_pct.mean():+.2f}%  pos years: {pos_years}")
    verdict = (dd > -20) and (td.ret_pct.mean() >= 0.6) and (pos_years >= 6)
    print(f"PASS BAR: maxDD > -20% AND EV >= +0.6% AND pos years >= 6  ->  {'PASS' if verdict else 'FAIL'}")
    print("\nBy exit year:")
    print(yr.groupby("year").agg(trades=("pnl","size"), net_pnl=("pnl","sum")).round(0).to_string())
