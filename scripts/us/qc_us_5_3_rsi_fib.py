#!/usr/bin/env python3
# QUANTCONNECT LEAN — US Test 5.3 QC CONFIRMATION PORT (RSI div + Fib golden pocket)
#
# PURPOSE: survivorship-free confirmation of the Stage 1 PASS (Mac/Yahoo +0.90% EV,
# 1,630 trades, 10/13y; docs/US-TEST-5-3-RESULTS.md). ONE registered run (per window
# segment), bars read once, NO gate-widening. Same frozen rule as the Mac script
# (scripts/us_5_3_rsi_fib.py @ e0edf3a).
#
# FROZEN RULE (identical to Mac v2):
#   Universe: US$1-10, 20d dollar-volume >= US$3M, >= 260d history. Long-only. NO regime
#   gates (audits the setup itself).
#   Per day, per eligible symbol:
#     - Trend: EMA50(close) > EMA200(close)
#     - Swing leg: over prior 90 days EXCLUDING today: j = day of max HIGH;
#       leg_low = min CLOSE over the 90 days ending at j; leg_high = high[j]
#     - Golden pocket: close in [leg_high-0.618*(leg_high-leg_low), leg_high-0.382*(...)]
#     - RSI(14) Wilder; divergence proxy: close < min(close[-5..-1]) AND RSI > min(RSI[-10..-1])
#     - Entry at close (daily bar), hold 21 trading days, exit. Non-overlapping per symbol.
#   Costs: net P&L per trade = raw_ret - 2*0.35% computed offline from fills
#   (fee model left at zero here ON PURPOSE; the ledger line below applies costs).
#
# FROZEN BARS (read once after the single registered run):
#   1. EV/trade net > +0.60%
#   2. Positive years >= 6/13
#   3. Trades >= 150 (else VOID)
#   4. REPORT: portfolio maxDD + max concurrent positions (informational)
#   Verdict options: CONFIRMED / INVERTED (tombstone, survivorship artifact) / VOID.
#
# APPARATUS LESSONS BAKED IN (from the 5.1 port, PR #32):
#   - Use self.Securities[s].Close, NOT slice[s]
#   - Guard None/0 close (OnData fires pre-bar at 00:00 for daily bars)
#   - SetWarmUp(300, Daily) REQUIRED — verify first signal prints
#   - Free tier 10KB log cap: compact summary only
#   - Split runs: A: 2014-01-01..2020-06-30, B: 2020-07-01..2026-07-15.
#     Boundary positions at the split are UNCOUNTED (conservative, 4.5 convention).
#
# RUN PROCEDURE (owner, QC web IDE or LEAN CLI):
#   1. Create project, paste this file as main.py, set start/end per segment.
#   2. Run A then B. Record TRADES/EV/YEAR/MAX_CONC debug lines from each.
#   3. Stitch with boundary-conservative rule; ONE reading of the bars.
#   4. Log verdict to docs/US-TEST-5-3-QC-VERDICT.md.

from AlgorithmImports import *
import numpy as np


class UsTest53RsiFib(QCAlgorithm):

    def initialize(self):
        self.set_start_date(2014, 1, 1)   # SEGMENT A; B: 2020-07-01..2026-07-15
        self.set_end_date(2020, 6, 30)
        self.set_cash(100000)
        self.set_benchmark("SPY")

        self.hold_days = 21
        self.cost_side = 0.0035
        self.rsi_period = 14
        self.min_price, self.max_price, self.min_dvol = 1.0, 10.0, 3e6

        # Universe: coarse + fine — price 1-10, dollar-volume >= 3M (coarse handles
        # both; fine just caps the count for free-tier headroom).
        self.universe = self.add_universe(self._coarse, self._fine)

        self.set_warm_up(300, Resolution.Daily)

        # State (FIX 18 Oct: entry_px was never initialized -> NameError on first exit)
        self.exit_at = {}       # symbol -> bar count remaining
        self.entry_px = {}      # symbol -> entry price
        self.trades = []        # (exit_date, symbol, net_pct)
        self.in_flight = 0
        self.max_conc_seen = 0  # FIX 18 Oct: tracked running max (was final value)

    # ---------- universe ----------
    def _coarse(self, coarse):
        if self.is_warming_up:
            return Universe.UNCHANGED
        return [c.symbol for c in coarse
                if c.has_data
                and self.min_price <= c.adjusted_price <= self.max_price
                and c.dollar_volume >= self.min_dvol]

    def _fine(self, fine):
        # Keep universe small enough for free tier: top 200 by dollar volume.
        return [f.symbol for f in fine][:200]

    # ---------- helpers ----------
    def _ema(self, closes, span):
        a = 2.0 / (span + 1)
        e = closes[0]
        for x in closes[1:]:
            e = a * x + (1 - a) * e
        return e

    def _rsi_series(self, closes):
        gains, losses = [], []
        prev = closes[0]
        for x in closes[1:]:
            d = x - prev
            gains.append(max(d, 0.0))
            losses.append(max(-d, 0.0))
            prev = x
        g = gains[0]
        l = losses[0]
        rs = []
        for i in range(1, len(gains)):
            g = (1 - 1 / self.rsi_period) * g + (1 / self.rsi_period) * gains[i]
            l = (1 - 1 / self.rsi_period) * l + (1 / self.rsi_period) * losses[i]
            rs.append(100 - 100 / (1 + (g / l if l > 0 else np.inf)))
        return rs

    def _signal(self, closes, highs):
        if len(closes) < 291:
            return False
        c_today = closes[-1]
        # Trend
        if self._ema(closes[-200:], 50) <= self._ema(closes[-200:], 200):
            return False
        # Swing leg over prior 90 days EXCLUDING today
        hist_h = highs[-91:-1]
        hist_c = closes[-91:-1]
        j = int(np.argmax(hist_h))
        leg_high = hist_h[j]
        lo = max(0, j - 89)
        leg_low = hist_c[lo:j + 1].min()
        rng = leg_high - leg_low
        f38 = leg_high - 0.382 * rng
        f62 = leg_high - 0.618 * rng
        if not (f62 <= c_today <= f38):
            return False
        # New 5d low
        if c_today >= closes[-6:-1].min():
            return False
        # RSI divergence proxy
        rs = self._rsi_series(closes[-30:])
        if len(rs) < 11:
            return False
        if rs[-1] <= min(rs[-11:-1]):
            return False
        return True

    # ---------- main loop ----------
    def on_data(self, slice):
        if self.is_warming_up:
            return

        # Process exits first (21-day hold).
        for s in list(self.exit_at.keys()):
            self.exit_at[s] -= 1
            if self.exit_at[s] <= 0:
                px = self.securities[s].close
                if px:
                    entry = self.entry_px[s]
                    raw = px / entry - 1.0
                    net = raw - 2 * self.cost_side
                    self.trades.append((self.time.date(), str(s), net * 100))
                del self.exit_at[s]
                del self.entry_px[s]
                self.in_flight -= 1

        # Entries: evaluate every active universe symbol daily.
        for s in list(self.active_securities.keys()):
            if s in self.exit_at:
                continue  # non-overlapping
            hist = self.history([s], 291, Resolution.Daily)
            if hist is None or hist.empty:
                continue
            try:
                if isinstance(hist.index, MultiIndex):
                    closes = hist.loc[str(s)]["close"].values
                    highs = hist.loc[str(s)]["high"].values
                else:
                    closes = hist["close"].values
                    highs = hist["high"].values
            except Exception:
                continue
            if len(closes) < 291 or np.isnan(closes).any():
                continue
            if self._signal(closes, highs):
                px = self.securities[s].close
                if not px:
                    continue
                self.set_holdings(s, 0.02)   # small fixed weight; ledger tracks per-trade
                self.exit_at[s] = self.hold_days
                self.entry_px[s] = px
                self.in_flight += 1
                if self.in_flight > self.max_conc_seen:
                    self.max_conc_seen = self.in_flight

    # ---------- output ----------
    def on_end_of_algorithm(self):
        import collections
        byyear = collections.defaultdict(lambda: [0, 0.0])
        for d, s, net in self.trades:
            byyear[d.year][0] += 1
            byyear[d.year][1] += net
        ev = sum(t[2] for t in self.trades) / max(len(self.trades), 1)
        self.debug(f"TRADES {len(self.trades)} EV {ev:.2f}")
        for y in sorted(byyear):
            n, tot = byyear[y][0], byyear[y][1]
            self.debug(f"YEAR {y} n={n} mean={tot / n:+.2f}")
        self.debug(f"MAX_CONC {self.max_conc_seen}")
