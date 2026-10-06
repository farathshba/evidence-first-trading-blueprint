#!/usr/bin/env python3
"""Clean raw (unadjusted) price data: drop glitch rows, EXCLUDE tickers whose
price series contains consolidation/split artifacts (daily move beyond +/-60%).
Writes cleaned CSVs to --out, prints what was excluded and why."""
import argparse, glob, os
import pandas as pd

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument("--in-dir", default="~/Projects/quantjourney/data")
ap.add_argument("--out", default="data_clean")
ap.add_argument("--min-price", type=float, default=0.05)
ap.add_argument("--max-move", type=float, default=0.60, help="abs daily move fraction that flags artifact")
a = ap.parse_args()
IN = os.path.expanduser(a.in_dir)
os.makedirs(a.out, exist_ok=True)

kept, dropped, flagged = 0, [], {}
for fp in sorted(glob.glob(os.path.join(IN, "*.csv"))):
    t = os.path.basename(fp).replace(".csv", "")
    try:
        df = pd.read_csv(fp)
        df.columns = [c.lower().strip() for c in df.columns]
        if "close" not in df.columns: continue
        df = df.dropna(subset=["close"])
        df = df[df["close"] >= a.min_price]          # glitch rows
        if len(df) < 260: continue                    # too short to trade anyway
        ret = df["close"].pct_change().abs()
        bad = ret > a.max_move
        if bad.any():
            flagged[t] = int(bad.sum())
            continue                                  # exclude whole ticker: unadjusted, unsafe
        df.to_csv(os.path.join(a.out, t + ".csv"), index=False)
        kept += 1
    except Exception as e:
        dropped.append(f"{t}: {e}")

print(f"Kept {kept} clean tickers -> {a.out}/")
print(f"EXCLUDED {len(flagged)} tickers with split/consolidation artifacts (unadjustable without Adj Close):")
for t, n in sorted(flagged.items(), key=lambda x: -x[1])[:15]:
    print(f"  {t}: {n} artifact days")
print(f"Skipped/unreadable: {len(dropped)}")
