#!/usr/bin/env python3
"""Daily unattended job: refresh the full-universe rolling store and write the
day's system snapshot (ES3 gate + top-10 momentum rank) to the append-only log.
Design: one rolling store (data_live/), overwritten daily — no folder sprawl.
The log (data_live/_snapshot_log.md) is the durable audit trail; copy it to
arkenstone monthly."""
import glob, os, sys, datetime
import pandas as pd
import yfinance as yf

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TICKERS = os.path.join(BASE, "tickers_yahoo.txt")
STORE = os.path.join(BASE, "data_live")
LOG = os.path.join(BASE, "_snapshot_log.md")
os.makedirs(STORE, exist_ok=True)

tickers = [t.strip() for t in open(TICKERS) if t.strip() and not t.startswith("#")]
today = datetime.date.today().isoformat()
print(f"[{today}] fetching {len(tickers)} tickers (400d rolling)...", flush=True)

ok, fail = 0, 0
for i, t in enumerate(tickers):
    try:
        df = yf.download(t, period="400d", interval="1d", auto_adjust=False,
                         progress=False, threads=False)
        if df is None or len(df) < 220:
            fail += 1; continue
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.rename(columns=str.lower)[["open","high","low","close","volume"]].dropna()
        df.to_csv(os.path.join(STORE, f"{t.replace('.','_')}.csv"), index_label="date")
        ok += 1
    except Exception:
        fail += 1
    if (i+1) % 100 == 0:
        print(f"  ... {i+1}/{len(tickers)}", flush=True)
print(f"fetch done: {ok} ok, {fail} failed", flush=True)

# ---- dedicated ES3 fetch (gate index; never part of the ranked universe) ----
for t in ("ES3.SI",):
    try:
        df = yf.download(t, period="400d", interval="1d", auto_adjust=False,
                         progress=False, threads=False)
        if df is not None and len(df):
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            df.rename(columns=str.lower)[["open","high","low","close","volume"]].dropna() \
                .to_csv(os.path.join(STORE, "ES3_SI.csv"), index_label="date")
            print("ES3 fetched ok", flush=True)
    except Exception as e:
        print(f"WARN: ES3 fetch failed: {e}", flush=True)

# ---- snapshot: ES3 gate + top-10 momentum rank ----
def load(name):
    fp = os.path.join(STORE, name)
    if not os.path.exists(fp): return None
    df = pd.read_csv(fp)
    df.columns = [c.lower().strip() for c in df.columns]
    return df.dropna(subset=["close"]).set_index("date")

es3 = load("ES3_SI.csv")
gate_state = "UNKNOWN"
if es3 is not None and len(es3) >= 200:
    sma = es3["close"].rolling(200).mean().iloc[-1]
    px = es3["close"].iloc[-1]
    gate_state = "OPEN" if px > sma else "CLOSED"

scores = []
for fp in glob.glob(os.path.join(STORE, "*.csv")):
    t = os.path.basename(fp).replace(".csv", "")
    if t.startswith("_") or t in ("ES3_SI",): continue
    df = pd.read_csv(fp)
    df.columns = [c.lower().strip() for c in df.columns]
    if "close" not in df.columns or len(df) < 147: continue
    px = df["close"].iloc[-1]
    past = df["close"].iloc[-127]
    dvol = (df["close"] * df["volume"]).iloc[-20:].mean() if "volume" in df.columns else 0
    if past > 0 and px >= 1.0 and dvol >= 1_000_000:
        scores.append((t, px / past - 1, dvol))
scores.sort(key=lambda x: -x[1])
top10 = [f"{t} ({r:+.1%})" for t, r, _ in scores[:10]]

entry = (f"\n## {today}\n"
         f"- ES3 gate: **{gate_state}**\n"
         f"- Top-10 momentum (126d, price>=1, dvol>=1M): {', '.join(top10) if top10 else 'none'}\n"
         f"- Data: {ok} ok / {fail} failed\n")
with open(LOG, "a") as f:
    f.write(entry)
print(f"snapshot logged -> {LOG}", flush=True)
# ---- auto-commit the audit log ----
import subprocess
try:
    subprocess.run(["git", "add", LOG], cwd=BASE, check=True)
    subprocess.run(["git", "commit", "-m", f"daily snapshot {today}"], cwd=BASE, check=True)
    subprocess.run(["git", "push"], cwd=BASE, check=True)
    print("audit log committed + pushed", flush=True)
except subprocess.CalledProcessError as e:
    print(f"WARN: git push failed: {e}", flush=True)  # log entry still saved locally

print(entry)
