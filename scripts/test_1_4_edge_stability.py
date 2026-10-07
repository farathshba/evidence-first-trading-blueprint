"""Test 1.4: edge-stability decomposition (Reddit critique, 8 Oct 2026).
Is the champion's edge distributed or concentrated?"""
import glob
import pandas as pd

td = pd.read_csv(sorted(glob.glob("results/champion_trades_*.csv"))[-1])
td["year"] = td.exit_date.str[:4]
td["half"] = td.exit_date.str[:4] + td.exit_date.str[5:7].apply(lambda m: "-H1" if int(m) <= 6 else "-H2")

print("=== TEST 1.4: EDGE-STABILITY DECOMPOSITION ===")
print(f"\nTotal round-trips: {len(td)}  net P&L: {td.pnl.sum():,.0f}  win rate: {100*(td.pnl>0).mean():.1f}%  avg EV: {td.ret_pct.mean():+.2f}%")

print("\n--- By year (win rate & EV stability) ---")
g = td.groupby("year").agg(trades=("pnl","size"), win_rate=("pnl", lambda x: round(100*(x>0).mean(),1)),
                           ev_pct=("ret_pct","mean"), net_pnl=("pnl","sum")).round(2)
print(g.to_string())

print("\n--- By half ---")
h = td.groupby("half").agg(trades=("pnl","size"), ev_pct=("ret_pct","mean"), net_pnl=("pnl","sum")).round(2)
print(h.to_string())

print("\n--- Profit concentration (the fragility question) ---")
for n in (1, 5, 10, 20):
    share = td.nlargest(n, "pnl").pnl.sum() / td.pnl.sum() * 100
    print(f"Top {n:>2} trades carry {share:6.1f}% of total net profit")
neg = td[td.pnl < 0]
print(f"Winners: {(td.pnl>0).sum()} ({td[td.pnl>0].pnl.sum():,.0f})  Losers: {len(neg)} ({neg.pnl.sum():,.0f})")

print("\nInterpretation:")
print("- Top-5 > 60% of profit => lottery-ticket edge: fragile; discount variant EV gains")
print("- Win rate steady across years + profit distributed => durable thin edge")
