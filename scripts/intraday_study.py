#!/usr/bin/env python3
"""Tier 2 item 2: WHERE does SGX intraday drift live?
Decomposition of open->close returns by condition: trend (SMA200), momentum rank
(126d return, top decile), gap direction. No costs in stage 1. Reports conditional
means so we can see if any pocket could clear the ~0.7% round-trip cost wall."""
import glob, os
import pandas as pd

DATA = "data_v2_clean"
rows = []
for fp in sorted(glob.glob(os.path.join(DATA, "*.csv"))):
    t = os.path.basename(fp).replace(".csv", "")
    if t.startswith("_") or t == "ES3_SI": continue
    try:
        df = pd.read_csv(fp)
        df.columns = [c.lower().replace(" ", "") for c in df.columns]
        if not {"open", "close"}.issubset(df.columns): continue
        df = df.dropna(subset=["open", "close"])
        df["intraday"] = df["close"] / df["open"] - 1
        df["gap"] = df["open"] / df["close"].shift(1) - 1
        df["sma200"] = df["close"].rolling(200).mean()
        df["mom126"] = df["close"].pct_change(126)
        df["dvol"] = (df["close"] * df["volume"]).rolling(20).mean() if "volume" in df.columns else 1e9
        df = df[(df["close"] >= 1.0) & (df["dvol"] >= 1_000_000)]  # tradable universe only
        rows.append(df[["intraday", "gap", "sma200", "mom126"]].dropna())
    except Exception:
        pass

df = pd.concat(rows)
df["uptrend"] = df["mom126"].notna() & (df["sma200"].notna())  # placeholder, replaced below
# proper flags
df["uptrend"] = df["sma200"] > 0  # sma200 exists implies we can compare below
print(f"Total obs: {len(df):,}")
print(f"\n== STAGE 1: RAW INTRADAY DECOMPOSITION (gross, no costs) ==")
print(f"All tradable obs:          mean {100*df.intraday.mean():+.4f}%   median {100*df.intraday.median():+.4f}%")

# momentum decile
df["mom_rank"] = df.groupby(df.index)["mom126"].rank(pct=True)
top = df[df.mom_rank >= 0.9]; rest = df[df.mom_rank < 0.9]
print(f"Top-decile momentum:       mean {100*top.intraday.mean():+.4f}%  (n={len(top):,})")
print(f"Rest:                      mean {100*rest.intraday.mean():+.4f}%  (n={len(rest):,})")

# gap condition
up = df[df.gap > 0]; dn = df[df.gap <= 0]
print(f"Gap-up opens:              mean {100*up.intraday.mean():+.4f}%  (n={len(up):,})")
print(f"Gap-down/flat opens:       mean {100*dn.intraday.mean():+.4f}%  (n={len(dn):,})")

# combined pocket: top-decile momentum + gap-up
pocket = df[(df.mom_rank >= 0.9) & (df.gap > 0)]
print(f"Pocket (top-mom + gap-up): mean {100*pocket.intraday.mean():+.4f}%  (n={len(pocket):,})")
pocket2 = df[(df.mom_rank >= 0.9) & (df.gap <= 0)]
print(f"Pocket (top-mom + no gap): mean {100*pocket2.intraday.mean():+.4f}%  (n={len(pocket2):,})")

print("\nSTAGE-1 GATE: any pocket >= +0.25% gross -> run costed sim; else FAIL and close item.")
