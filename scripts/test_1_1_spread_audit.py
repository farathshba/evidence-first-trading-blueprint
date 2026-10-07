"""Test 1.1: Spread & friction audit (Tier 3, Gemini critique).
Corwin-Schultz (2012) high-low spread estimator on the champion's actually-held
names, from our own 10y daily candles. Output: revised cost per price band.

Corwin-Schultz: for consecutive 2-day windows,
  beta = (ln(H_t/T_t))^2 + (ln(H_{t+1}/L_{t+1}))^2          (2-day squared range)
  gamma = (ln(H_2/L_2))^2                                  (2-day high-low)
  alpha = (sqrt(2*beta) - sqrt(beta)) / (3 - 2*sqrt(2)) - sqrt(gamma/(3 - 2*sqrt(2)))
  spread_pct = 2*(exp(alpha) - 1) / (1 + exp(alpha))        (as fraction of price)
Daily spread = mean of 2-day estimates, negative values floored at 0.
"""
import glob, os
import numpy as np
import pandas as pd

print("=== TEST 1.1: SPREAD & FRICTION AUDIT ===")

# 1) The champion's actually-held names (entry prices from the trade log)
td = pd.read_csv(sorted(glob.glob("results/champion_trades_*.csv"))[-1])
held = td.groupby("ticker").agg(entries=("entry", "size"), avg_entry=("entry", "mean")).reset_index()
print(f"\nChampion held {len(held)} distinct names over the 10y period")

def corwin_schultz(df):
    h, l = df["high"].values, df["low"].values
    n = len(df); ests = []
    k = 3 - 2 * np.sqrt(2)
    for i in range(n - 1):
        h2 = max(h[i], h[i+1]); l2 = min(l[i], l[i+1])
        if l2 <= 0 or h[i] <= 0 or l[i] <= 0 or h[i+1] <= 0 or l[i+1] <= 0: continue
        beta = (np.log(h[i]/l[i]))**2 + (np.log(h[i+1]/l[i+1]))**2
        gamma = (np.log(h2/l2))**2
        alpha = (np.sqrt(2*beta) - np.sqrt(beta)) / k - np.sqrt(gamma/k)
        s = 2*(np.exp(alpha) - 1) / (1 + np.exp(alpha))
        ests.append(max(s, 0.0))
    return float(np.nanmean(ests)) if ests else np.nan

# 2) Estimate spread per held name (time-weighted: full history where it traded)
rows = []
for _, r in held.iterrows():
    fp = os.path.join("data_v3_clean", r.ticker + ".csv")
    if not os.path.exists(fp):
        rows.append(dict(ticker=r.ticker, avg_entry=r.avg_entry, entries=r.entries, cs_spread_pct=np.nan))
        continue
    df = pd.read_csv(fp)
    cols = {c.lower().replace(" ", ""): c for c in df.columns}
    df = df.rename(columns={cols[s]: s for s in ("high","low","close") if s in cols})
    sp = corwin_schultz(df)
    rows.append(dict(ticker=r.ticker, avg_entry=r.avg_entry, entries=r.entries, cs_spread_pct=sp*100))

sp = pd.DataFrame(rows).dropna(subset=["cs_spread_pct"]).sort_values("cs_spread_pct")
print("\n--- Corwin-Schultz effective spread (one-way, % of price) ---")
print(sp.to_string(index=False, float_format=lambda x: f"{x:,.2f}"))

# 3) Median spread by entry price band
bands = [(0, 2), (2, 5), (5, 100)]
print("\n--- Revised cost input by price band (median CS spread) ---")
revised = {}
for lo, hi in bands:
    sel = sp[(sp.avg_entry >= lo) & (sp.avg_entry < hi)]
    if len(sel):
        med = sel.cs_spread_pct.median()
        revised[f"{lo}-{hi}"] = med
        print(f"S${lo:>2}-S${hi:<3}: n={len(sel):>3}  median one-way spread: {med:5.2f}%")

# 4) The verdict table: modeled vs measured round-trip friction
print("\n--- Verdict input: round-trip friction (2x spread as proxy, commissions excluded) ---")
for b, med in revised.items():
    print(f"Band S${b}: CS round-trip ~{2*med:.2f}% vs modeled 0.70%  ->  {'HIGHER' if 2*med > 0.70 else 'ok'}")

# 5) EV impact pre-check: what spread drag does to +1.24% EV
full_med = sp.cs_spread_pct.median()
print(f"\nUniverse median one-way spread: {full_med:.2f}%  (round-trip {2*full_med:.2f}%)")
print(f"Champion EV +1.24% was net of 0.70% modeled round-trip.")
print(f"If real round-trip is {2*full_med:.2f}%, EV becomes ~{1.24 + 0.70 - 2*full_med:+.2f}%  (Test 1.2 runs this properly per-band)")
sp.to_csv("results/spread_audit_champion_names.csv", index=False)
print("\nSpread table -> results/spread_audit_champion_names.csv")
