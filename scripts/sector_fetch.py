#!/usr/bin/env python3
"""
3.6 Phase A — fetch sector classification for the universe -> data_v3_clean/_sectors.csv.
Cached/resumable: re-running only fetches tickers not yet mapped. Coverage is printed;
if coverage < 80% of the universe, Test 3.6 is VOID pending better mapping (pre-registered).
"""
import glob, os, time
import pandas as pd
import yfinance as yf

DATA = 'data_v3_clean'
out = os.path.join(DATA, '_sectors.csv')
have = {}
if os.path.exists(out):
    try:
        have = {str(k): str(v) for k, v in pd.read_csv(out).values}
    except Exception:
        have = {}

files = sorted(glob.glob(os.path.join(DATA, '*.csv')))
tickers = [os.path.basename(f)[:-4] for f in files]
tickers = [t for t in tickers if not t.upper().startswith(('ES3', '^STI', '_'))]
print(f"universe tickers: {len(tickers)}")

rows = []
miss = 0
for i, t in enumerate(tickers):
    cached = have.get(t, '')
    if cached and cached not in ('', 'nan'):
        rows.append((t, cached))
        continue
    sym = t.replace('_SI', '.SI')
    sec = ''
    for attempt in (1, 2):
        try:
            info = yf.Ticker(sym).info
            sec = info.get('sector', '') or ''
            if sec:
                break
        except Exception as e:
            if attempt == 2:
                print(f"[{i+1}/{len(tickers)}] {t}: ERROR {str(e)[:50]}")
            time.sleep(1.0)
        time.sleep(0.4)
    if not sec:
        miss += 1
    rows.append((t, sec))
    if (i + 1) % 25 == 0 or not sec:
        print(f"[{i+1}/{len(tickers)}] {t}: {sec or 'MISSING'}")
    pd.DataFrame(rows, columns=['ticker', 'sector']).to_csv(out, index=False)

n_ok = sum(1 for _, s in rows if s)
print(f"\nCOVERAGE: {n_ok}/{len(rows)} ({100*n_ok/len(rows):.0f}%) -> {out}")
print("VOID if coverage < 80% (pre-registered Test 3.6 condition)")
