#!/usr/bin/env python3
"""Cross-sectional momentum on SGX: rank by 6-month return, hold top N, rebalance monthly.
Universe: liquid names only (price >= MIN_PRICE, avg dollar volume >= MIN_DOLLAR_VOL).
Only enters when the market regime filter passes (ES3 proxy above its 200-day SMA) if REGIME_GATE=1."""
import argparse, glob, math, os
import pandas as pd

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument("--data-dir", default="data")
ap.add_argument("--lookback", type=int, default=126, help="ranking window in trading days (~6 months)")
ap.add_argument("--top-n", type=int, default=10)
ap.add_argument("--min-price", type=float, default=1.0)
ap.add_argument("--min-dollar-vol", type=float, default=1_000_000, help="avg daily $ traded")
ap.add_argument("--capital", type=float, default=100_000)
ap.add_argument("--cost-pct", type=float, default=0.35, help="cost per side, %% of notional")
ap.add_argument("--regime-gate", type=int, default=1, help="1 = only hold when ES3 above SMA200")
ap.add_argument("--skip", type=int, default=0, help="skip-window: exclude the most recent N days from the ranking return (2.1)")
ap.add_argument("--vol-adj", type=int, default=0, help="vol-adjust: ranking window for realized sigma; score = ret/sigma (2.2; 0=off)")
ap.add_argument("--breadth", type=int, default=0, help="breadth gate: min %% of universe above own SMA200 required for entries (2.3; 0=off)")
ap.add_argument("--trail", type=float, default=0.0, help="trailing exit: exit when close < peak close since entry * (1 - trail) (2.4; 0=off)")
ap.add_argument("--entry-start", default=None, help="YYYY-MM-DD: earliest entry date (walk-forward)")
ap.add_argument("--entry-end", default=None, help="YYYY-MM-DD: latest entry date (walk-forward)")
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

# market regime proxy: ES3 (STI ETF); fall back to universe median if absent
regime = None
if a.regime_gate:
    for cand in ("ES3_SI", "ES3", "^STI"):
        if cand in books:
            regime = books[cand]["close"].rolling(200).mean()
            break
    if regime is None:
        print("NOTE: ES3/^STI not in data; regime gate uses universe median instead")
        print("WARNING: gate check requires ES3 present; with only the median proxy the gate is INACTIVE. Failing closed.")
        med = pd.concat([b["close"] for b in books.values()], axis=1).median(axis=1)
        regime = med.rolling(200).mean()

all_dates = sorted(set().union(*[set(b.index) for b in books.values()]))
month_ends = [d for prev, d in zip(all_dates, all_dates[1:]) if prev[:7] != d[:7]]

cash, holdings, trades, equity = a.capital, {}, [], []
for d in all_dates:
    # value portfolio
    nav = cash
    for t in holdings: nav += holdings[t]["shares"] * (books[t].loc[d, "close"] if d in books[t].index else holdings[t]["last"])
    for t in list(holdings): holdings[t]["last"] = books[t].loc[d, "close"] if d in books[t].index else holdings[t]["last"]
    equity.append((d, nav))
    if a.trail:
        for t in list(holdings):
            h = holdings[t]
            if d in books[t].index:
                _c = books[t].loc[d, "close"]
                h["peak"] = max(h.get("peak", h["entry"]), _c)
                if _c < h["peak"] * (1 - a.trail):
                    proc = _c * h["shares"] * (1 - cost)
                    trades.append(dict(ticker=t, entry_date=h["edate"], exit_date=d, entry=h["entry"], exit=_c, pnl=proc - h["basis"], ret_pct=100*(proc - h["basis"])/h["basis"]))
                    cash += proc; del holdings[t]
    if d not in month_ends: continue
    # regime gate
    if a.regime_gate and regime is not None and d in regime.index and pd.notna(regime.loc[d]) and books.get("ES3_SI", books.get("ES3")) is not None:
        px_series = books.get("ES3_SI", books.get("ES3"))["close"]
        if d in px_series.index and px_series.loc[d] < regime.loc[d]:
            # risk-off: liquidate
            for t in list(holdings):
                px = holdings[t]["last"]; proc = px * holdings[t]["shares"] * (1 - cost)
                trades.append(dict(ticker=t, entry_date=holdings[t]["edate"], exit_date=d, entry=holdings[t]["entry"], exit=px, pnl=proc - holdings[t]["basis"], ret_pct=100*(proc-holdings[t]["basis"])/holdings[t]["basis"]))
                cash += proc; del holdings[t]
            continue
    # rank by lookback return among liquid names
    scores = []
    for t, b in books.items():
        if d not in b.index: continue
        i = b.index.get_loc(d)
        if i < a.lookback + a.skip + 21: continue
        px = b["close"].iloc[i]; past = b["close"].iloc[i - a.lookback - a.skip]
        dvol = (b["close"] * b["volume"]).iloc[i-20:i].mean()
        if px >= a.min_price and dvol >= a.min_dollar_vol and past > 0:
            ret = px / past - 1
            if a.vol_adj:
                sig = b["close"].iloc[i - a.vol_adj:i].pct_change().std()
                scores.append((t, ret / sig if sig and sig > 0 else -9e9))
            else:
                scores.append((t, ret))
    scores.sort(key=lambda x: -x[1])
    target = set(t for t, _ in scores[:a.top_n])
    # sell non-targets, then buy targets with equal weight
    for t in list(holdings):
        if t not in target:
            px = holdings[t]["last"]; proc = px * holdings[t]["shares"] * (1 - cost)
            trades.append(dict(ticker=t, entry_date=holdings[t]["edate"], exit_date=d, entry=holdings[t]["entry"], exit=px, pnl=proc - holdings[t]["basis"], ret_pct=100*(proc-holdings[t]["basis"])/holdings[t]["basis"]))
            cash += proc; del holdings[t]
    _d_ok = True
    if a.entry_start and d < a.entry_start: _d_ok = False
    if a.entry_end and d > a.entry_end: _d_ok = False
    if a.breadth:
        _above = 0; _n = 0
        for t2, b2 in books.items():
            if d in b2.index:
                i2 = b2.index.get_loc(d)
                if i2 >= 200:
                    _n += 1
                    if b2["close"].iloc[i2] >= b2["close"].iloc[i2-199:i2+1].mean():
                        _above += 1
        if _n > 0 and (100 * _above / _n) < a.breadth:
            _d_ok = False
    stake = cash / max(len(target - set(holdings)), 1) if _d_ok else 0
    for t in sorted(target - set(holdings)):
        px = books[t].loc[d, "close"]
        sh = int(stake // px)
        if sh <= 0: continue
        out = sh * px
        if out > cash: continue
        cash -= out
        holdings[t] = dict(shares=sh, entry=px, edate=d, last=px, peak=px, basis=out * (1 + cost))

nav = cash + sum(h["last"] * h["shares"] for h in holdings.values())
eq = pd.DataFrame(equity, columns=["date", "nav"])
dr = eq["nav"].pct_change()
w = eq.assign(drop=dr).nsmallest(5, "drop")[["date", "nav", "drop"]]
print("WORST 5 NAV DAYS:")
print(w.to_string(index=False))
rets = eq["nav"].pct_change().dropna()
sharpe = rets.mean()/rets.std()*math.sqrt(252) if rets.std() > 0 else float("nan")
dd = (eq["nav"]/eq["nav"].cummax() - 1).min() * 100
td = pd.DataFrame(trades)
print("\n=== SGX MOMENTUM VERDICT ===")
print(f"Capital {a.capital:,.0f} -> {nav:,.0f}  total: {100*(nav/a.capital-1):+.1f}%  Sharpe: {sharpe:.2f}  maxDD: {dd:.1f}%")
if not td.empty:
    wins = td[td.pnl > 0]
    yr = td.copy(); yr["year"] = yr.exit_date.str[:4]
    print(f"Round-trips: {len(td)}  win rate: {100*len(wins)/len(td):.1f}%  avg: {td.ret_pct.mean():+.2f}%")
    print("\nBy exit year:")
    print(yr.groupby("year").agg(trades=("pnl","size"), net_pnl=("pnl","sum")).round(0).to_string())
print("\nBAR: EV > +0.6%/trade after costs AND net positive in >= 6 of 10 years.")
import os
os.makedirs("results", exist_ok=True)
_tag = (f"skip{a.skip}" if a.skip else "") + (f"_voladj{a.vol_adj}" if a.vol_adj else "") + (f"_br{a.breadth}" if a.breadth else "") or "raw"
_win = ""
if a.entry_start or a.entry_end:
    _win = f"_{a.entry_start or 'start'}_{a.entry_end or 'end'}"
out_csv = f"results/champion_trades_{a.lookback}d_top{a.top_n}_cost{a.cost_pct}_{_tag}{_win}.csv"
td.to_csv(out_csv, index=False)
print(f"Trades log -> {out_csv}")
