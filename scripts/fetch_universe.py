#!/usr/bin/env python3
"""Download ~10 years of daily OHLCV for every ticker in tickers.txt into data/."""
import argparse, os, time
import pandas as pd
import yfinance as yf

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument("--tickers", default="tickers.txt")
ap.add_argument("--out", default="data")
ap.add_argument("--years", type=int, default=10)
ap.add_argument("--delay", type=float, default=0.8)
a = ap.parse_args()

if not os.path.exists(a.tickers):
    raise SystemExit(f"Tickers file '{a.tickers}' not found. Create it first.")
tickers = [l.strip() for l in open(a.tickers) if l.strip() and not l.strip().startswith("#")]
if not tickers:
    raise SystemExit("No tickers found in the file.")
os.makedirs(a.out, exist_ok=True)
start = (pd.Timestamp.today() - pd.DateOffset(years=a.years)).strftime("%Y-%m-%d")

manifest, ok, failed = [], 0, []
for i, t in enumerate(tickers, 1):
    try:
        df = yf.download(t, start=start, auto_adjust=False, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        if df is None or df.empty:
            raise RuntimeError("no data returned")
        df = df.reset_index()
        df = df[["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"]].dropna()
        if len(df) < 250:
            raise RuntimeError(f"only {len(df)} rows - too short")
        df.to_csv(os.path.join(a.out, t.replace(".", "_") + ".csv"), index=False)
        manifest.append(dict(ticker=t, rows=len(df),
                             first=str(df["Date"].iloc[0])[:10],
                             last=str(df["Date"].iloc[-1])[:10], status="ok"))
        ok += 1
    except Exception as e:
        failed.append(t)
        manifest.append(dict(ticker=t, rows=0, first="", last="", status=f"failed: {e}"))
    if i % 25 == 0:
        print(f"  ... {i}/{len(tickers)}")
    time.sleep(a.delay)

pd.DataFrame(manifest).to_csv(os.path.join(a.out, "_manifest.csv"), index=False)
print(f"Done: {ok} downloaded, {len(failed)} failed -> details in {a.out}/_manifest.csv")
if failed:
    print("Failed (first 20):", ", ".join(failed[:20]))
