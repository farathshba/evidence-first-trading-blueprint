#!/usr/bin/env python3
"""
US-1 Phase 0a — build the US sub-US$10 universe -> data_us/ (one CSV per ticker) + data_us/_manifest.csv.
Universe per docs/PHASE-US-1-RUNBOOK.md: US common stocks, price US$1-10, 20-day dollar-volume >= US$3M;
exclude OTC/pink, ADRs, SPACs pre-deal, leveraged ETFs. SURVIVORSHIP CAVEAT: this snapshot is TODAY's
universe; Stage 1 results carry the pre-registered caveat unless a delisting-aware list is sourced.
Diagnostics at every stage (lesson from SGX: silent failures must announce themselves).
"""
import argparse, json, os, time, urllib.request
import pandas as pd
import yfinance as yf

def http_get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='data_us')
    ap.add_argument('--min-price', type=float, default=1.0)
    ap.add_argument('--max-price', type=float, default=10.0)
    ap.add_argument('--min-dvol', type=float, default=3e6)
    ap.add_argument('--start', default='2016-01-01')
    ap.add_argument('--limit', type=int, default=0, help='cap number of tickers (0 = no cap), for smoke runs')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    # Stage 1: candidate list from the public Nasdaq screener (no key).
    print('[stage 1] fetching Nasdaq screener list ...')
    url = ('https://api.nasdaq.com/api/screener/stocks?tableonly=true&limit=25&offset=0'
           '&download=true')
    js = json.loads(http_get(url).decode('utf-8'))
    rows = js.get('data', {}).get('rows', []) or js.get('data', {}).get('table', {}).get('rows', [])
    print(f'[diag] screener returned {len(rows)} raw rows')
    if not rows:
        raise SystemExit('NO SCREENER ROWS — endpoint may have changed; paste me the JSON head')

    df = pd.DataFrame(rows)
    cols = {c.lower().strip(): c for c in df.columns}
    def col(*names):
        for n in names:
            if n in cols: return cols[n]
        return None
    print(f"[diag] screener columns: {list(df.columns)}")
    cs, cp, cv = col('symbol'), col('lastsale', 'lastprice', 'last sale', 'price'), col('volume')
    if not all([cs, cp, cv]):
        raise SystemExit(f"MISSING COLUMN - symbol={cs} price={cp} volume={cv}; paste me the [diag] screener columns line above")
    df = df.rename(columns={cs: 'symbol', cp: 'price', cv: 'volume'})
    for c in ('symbol', 'price', 'volume'):
        df[c] = df[c].astype(str).str.replace(r'[$,%]', '', regex=True)
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df = df[df['symbol'].str.match(r'^[A-Z]{1,5}$', na=False)]
    df = df[(df['price'] >= a.min_price) & (df['price'] <= a.max_price)]
    # Nasdaq screener covers Nasdaq/NYSE/NYSE American listed = exchange-listed only (no OTC/pink).
    print(f'[diag] price band US${a.min_price}-{a.max_price}: {len(df)} candidates')

    # Stage 2: history + liquidity filter via yfinance, cached/resumable.
    have = {f[:-4] for f in os.listdir(a.out) if f.endswith('.csv')}
    tickers = [t for t in df['symbol'] if t not in have]
    if a.limit: tickers = tickers[:a.limit]
    print(f'[stage 2] fetching history for {len(tickers)} new tickers (cached: {len(have)})')

    keep, drops = [], {'short_hist': 0, 'no_data': 0, 'low_dvol': 0}
    for i, t in enumerate(tickers):
        try:
            raw = yf.download(t + '.US' if False else t, start=a.start, auto_adjust=False,
                              progress=False, threads=False)
        except Exception:
            raw = pd.DataFrame()
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = [c[0] if isinstance(c, tuple) else str(c) for c in raw.columns]
        raw = raw.reset_index()
        raw.columns = [str(c).strip().lower() for c in raw.columns]
        dcol = next((c for c in raw.columns if 'date' in c or c == 'price'), None)
        if raw.empty or dcol is None or 'close' not in raw.columns:
            drops['no_data'] += 1
            continue
        raw[dcol] = pd.to_datetime(raw[dcol]).dt.normalize()
        raw = raw.sort_values(dcol)
        if len(raw) < 260:
            drops['short_hist'] += 1
            continue
        dv = raw.set_index(dcol)
        dvol20 = (dv['close'] * dv['volume']).rolling(20).mean().iloc[-1]
        if not (dvol20 >= a.min_dvol):
            drops['low_dvol'] += 1
            continue
        raw.to_csv(os.path.join(a.out, f'{t}.csv'), index=False)
        keep.append({'ticker': t, 'price_now': float(dv['close'].iloc[-1]),
                     'dvol20': float(dvol20), 'rows': len(raw)})
        if (i + 1) % 50 == 0:
            print(f'[diag] {i+1}/{len(tickers)} processed; kept {len(keep)}')
        time.sleep(0.25)

    for f in os.listdir(a.out):
        if f.endswith('.csv') and f != '_manifest.csv':
            t = f[:-4]
            if t not in [k['ticker'] for k in keep]:
                try:
                    d = pd.read_csv(os.path.join(a.out, f))
                    dv = d.set_index(d.columns[0])
                    keep.append({'ticker': t, 'price_now': float(dv['close'].iloc[-1]),
                                 'dvol20': float((dv['close']*dv['volume']).rolling(20).mean().iloc[-1]),
                                 'rows': len(d)})
                except Exception:
                    pass
    pd.DataFrame(keep).to_csv(os.path.join(a.out, '_manifest.csv'), index=False)

    print(f'\n[RESULT] universe: {len(keep)} tickers in {a.out}/')
    print(f'[diag] drops: {drops}')
    print('[diag] SURVIVORSHIP CAVEAT APPLIES: today-only universe snapshot (runbook section 2)')

if __name__ == '__main__':
    main()
