#!/usr/bin/env python3
"""Honest portfolio backtest: fixed-fraction sizing, capped positions, pct costs,
exits at 2xATR stop / 4xATR target (stop checked before target: conservative)."""
import argparse, glob, math, os
import pandas as pd

def load(fp):
    df = pd.read_csv(fp)
    cols = {c.lower().replace(" ", ""): c for c in df.columns}
    ren = {cols[s]: s for s in ["date","open","high","low","close","adjclose","volume"] if s in cols}
    df = df.rename(columns=ren)
    if "adjclose" in df.columns: df["close"] = df["adjclose"]
    return df[["date","close","high","low","volume"]].dropna().reset_index(drop=True)

def prepare(df, vol_spike, atr_max_pct, min_avg_vol):
    c, h, l, v = df["close"], df["high"], df["low"], df["volume"]
    df["sma_f"] = c.rolling(20).mean()
    df["sma_s"] = c.rolling(200).mean()
    df["avgvol"] = v.rolling(20).mean()
    pc = c.shift(1)
    tr = pd.concat([h-l, (h-pc).abs(), (l-pc).abs()], axis=1).max(axis=1)
    df["atr"] = tr.rolling(14).mean()
    df["signal"] = ((c > df["sma_s"]) & (c > df["sma_f"]) &
                    (v >= vol_spike * df["avgvol"]) &
                    (df["atr"] <= atr_max_pct * c) &
                    (df["avgvol"] > min_avg_vol))
    return df.dropna(subset=["sma_s", "atr", "avgvol"])

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument("--data-dir", default="data")
ap.add_argument("--capital", type=float, default=100_000)
ap.add_argument("--risk-pct", type=float, default=2.0)
ap.add_argument("--max-positions", type=int, default=60)
ap.add_argument("--cost-pct", type=float, default=0.15, help="cost per side, % of notional")
ap.add_argument("--vol-spike", type=float, default=1.5)
ap.add_argument("--stop-atr", type=float, default=2.0)
ap.add_argument("--tp-atr", type=float, default=4.0)
ap.add_argument("--min-avg-vol", type=float, default=500_000)
ap.add_argument("--atr-max-pct", type=float, default=0.15)
a = ap.parse_args()
cost = a.cost_pct / 100.0

books, by_date, all_dates = {}, {}, set()
for fp in sorted(glob.glob(os.path.join(a.data_dir, "*.csv"))):
    t = os.path.basename(fp).replace(".csv", "")
    if t.startswith("_"): continue
    try:
        df = prepare(load(fp), a.vol_spike, a.atr_max_pct, a.min_avg_vol)
    except Exception as e:
        print(f"skip {t}: {e}"); continue
    df["d"] = df["date"].astype(str).str[:10]
    books[t] = df.set_index("d")
    for _, row in df.iterrows():
        all_dates.add(row["d"])
        if row["signal"]:
            by_date.setdefault(row["d"], []).append(t)

cash, positions, trades, equity = a.capital, {}, [], []
for d in sorted(all_dates):
    for t in list(positions):
        p = positions[t]
        row = books[t].loc[d] if d in books[t].index else None
        if row is None: continue
        px, reason = None, None
        if row["low"] <= p["stop"]:   px, reason = p["stop"], "stop"
        elif row["high"] >= p["target"]: px, reason = p["target"], "target"
        if px is not None:
            proceeds = px * p["shares"] * (1 - cost)
            cash += proceeds
            pnl = proceeds - p["cost_basis"]
            trades.append(dict(ticker=t, entry_date=p["edate"], exit_date=d,
                                entry=p["entry"], exit=px, reason=reason,
                                pnl=pnl, ret_pct=100*pnl/p["cost_basis"]))
            del positions[t]
    nav = cash
    for t, p in positions.items():
        row = books[t].loc[d] if d in books[t].index else None
        if row is not None: p["last"] = row["close"]
        nav += p["last"] * p["shares"]
    equity.append((d, nav))
    for t in by_date.get(d, []):
        if t in positions or len(positions) >= a.max_positions: continue
        row = books[t].loc[d]
        stake = nav * a.risk_pct / 100.0
        shares = int(stake // row["close"])
        if shares <= 0 or shares * row["close"] > cash: continue
        outlay = shares * row["close"]
        cash -= outlay
        positions[t] = dict(shares=shares, entry=row["close"], edate=d, last=row["close"],
                            stop=row["close"] - a.stop_atr * row["atr"],
                            target=row["close"] + a.tp_atr * row["atr"],
                            cost_basis=outlay * (1 + cost))

nav = cash
for t, p in positions.items():
    proceeds = p["last"] * p["shares"] * (1 - cost)
    pnl = proceeds - p["cost_basis"]
    trades.append(dict(ticker=t, entry_date=p["edate"], exit_date="open", entry=p["entry"],
                       exit=p["last"], reason="end_of_test", pnl=pnl,
                       ret_pct=100*pnl/p["cost_basis"]))
    nav += proceeds
final_nav = nav

eq = pd.DataFrame(equity, columns=["date", "nav"])
rets = eq["nav"].pct_change().dropna()
total_ret = 100 * (final_nav / a.capital - 1)
sharpe = (rets.mean() / rets.std() * math.sqrt(252)) if len(rets) > 2 and rets.std() > 0 else float("nan")
dd = (eq["nav"] / eq["nav"].cummax() - 1).min() * 100
td = pd.DataFrame(trades)
if td.empty:
    print("No trades generated. Check tickers/data and rules."); raise SystemExit
wins, losses = td[td.pnl > 0], td[td.pnl <= 0]
ev = td.ret_pct.mean()
yr = td.copy(); yr["year"] = yr.exit_date.astype(str).str[:4]
bands = td.copy()
bands["band"] = pd.cut(bands.entry, [0, 0.20, 1.0, 10.0, 1e9],
                       labels=["<0.20", "0.20-1.00", "1.00-10.00", ">10"])

print("\n=== BACKTEST VERDICT ===")
print(f"Capital {a.capital:,.0f} -> {final_nav:,.0f}   total return: {total_ret:+.1f}%   Sharpe: {sharpe:.2f}   max drawdown: {dd:.1f}%")
print(f"Trades: {len(td)}   win rate: {100*len(wins)/max(len(td),1):.1f}%   avg win: {wins.ret_pct.mean() if len(wins) else 0:+.1f}%   avg loss: {losses.ret_pct.mean() if len(losses) else 0:+.1f}%")
print(f"Per-trade EV after costs: {ev:+.2f}%")
print(f"Stops:targets = {len(td[td.reason=='stop'])}:{len(td[td.reason=='target'])}   (2xATR/4xATR geometry predicts 2:1 for a random walk)")
print("\nBy entry price band:")
print(bands.groupby("band", observed=True).agg(trades=("pnl","size"), win_rate=("pnl", lambda s: f"{100*(s>0).mean():.0f}%"), net_pnl=("pnl","sum")).to_string())
print("\nBy exit year:")
print(yr.groupby("year").agg(trades=("pnl","size"), net_pnl=("pnl","sum")).round(0).to_string())
print("\nDECISION RULE: a variant passes only if EV > +0.6% after costs AND net P&L positive in >= 6 of 10 years.")
print("Costs: set --cost-pct to your broker's real fee before trusting absolute numbers.")
