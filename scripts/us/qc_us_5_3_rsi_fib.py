#!/usr/bin/env python3
# QUANTCONNECT LEAN — US Test 5.3 QC CONFIRMATION PORT v3 (RSI div + Fib golden pocket)
#
# v3 (20 Oct): REMOVE self.history() ENTIRELY. v2 stalled twice at the SAME 15% mark
# (~2h+ total) -> deterministic wall, not throttling variance. Remaining suspect: the
# per-symbol seeding history requests (one per new universe member, hundreds total)
# wedging the cloud run at the same date. v3 uses ZERO history API calls: windows are
# built purely from daily slice bars, appended one per day, INCLUDING during warm-up
# (warm-up feed fills the 291-bar caches; trading still disabled until warm-up ends).
# Signal math (_signal/_ema/_rsi_series) byte-identical to v1/v2. Universe cap 200
# (restored; [:100] variant never got a clean comparison, and 100 is kept as fallback).
# Apparatus log: v1 stalled (per-day history x200, zero progress); v2 stalled at 15% x2
# (seeding history pulls suspected); v3 = no history calls at all. No v1/v2/v3 run
# consumed bars (all stalled pre-trade; zero trades).
#
# FROZEN RULE (identical): US$1-10, dvol>=US$3M; EMA50>EMA200; swing leg = prior 90d
# max-high day j, leg_low = min close of 90d ending at j; close in golden pocket
# 38.2-61.8%; RSI(14) Wilder div proxy (new 5d low, RSI > 10d min); entry at close,
# hold 21 trading days, non-overlapping; costs in ledger (-2x0.35%).
#
# FROZEN BARS (read once): EV > +0.60% net; >= 6/13 positive years; >= 150 trades else
# VOID; REPORT MAX_CONC (informational). CONFIRMED / INVERTED / VOID.
# Segments: A 2014-01-01..2020-06-30, B 2020-07-01..2026-07-15 (boundary uncounted).

from AlgorithmImports import *
from collections import deque
import numpy as np


class UsTest53RsiFibV3(QCAlgorithm):

    def initialize(self):
        self.set_start_date(2014, 1, 1)   # SEGMENT A; B: 2020-07-01..2026-07-15
        self.set_end_date(2020, 6, 30)
        self.set_cash(100000)
        self.set_benchmark("SPY")

        self.hold_days = 21
        self.cost_side = 0.0035
        self.rsi_period = 14
        self.min_price, self.max_price, self.min_dvol = 1.0, 10.0, 3e6
        self.win_len = 291

        self.add_universe(self._coarse, self._fine)
        # 300 warm-up days: fills the 291-bar windows BEFORE trading starts.
        self.set_warm_up(300, Resolution.Daily)

        self.exit_at = {}
        self.entry_px = {}
        self.trades = []
        self.in_flight = 0
        self.max_conc_seen = 0
        self.closes = {}   # symbol -> deque (oldest..latest)
        self.highs = {}

    # ---------- universe ----------
    def _coarse(self, coarse):
        if self.is_warming_up:
            return Universe.UNCHANGED
        return [c.symbol for c in coarse
                if c.has_fundamental_data
                and self.min_price <= c.adjusted_price <= self.max_price
                and c.dollar_volume >= self.min_dvol]

    def _fine(self, fine):
        # NOTE: fine is not order-guaranteed; cap kept for free-tier headroom.
        return [f.symbol for f in fine][:200]

    # ---------- helpers (identical math to v1/v2) ----------
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
        if self._ema(closes[-200:], 50) <= self._ema(closes[-200:], 200):
            return False
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
        if c_today >= closes[-6:-1].min():
            return False
        rs = self._rsi_series(closes[-30:])
        if len(rs) < 11:
            return False
        if rs[-1] <= min(rs[-11:-1]):
            return False
        return True

    # ---------- main loop ----------
    def on_data(self, slice):
        # v3: collect bars ALWAYS (incl. warm-up) — no history API anywhere.
        for s in self.active_securities.keys():
            bar = slice.get(s)
            if bar is None:
                continue
            if s in self.closes:
                self.closes[s].append(float(bar.close))
                self.highs[s].append(float(bar.high))
            else:
                self.closes[s] = deque([float(bar.close)], maxlen=self.win_len)
                self.highs[s] = deque([float(bar.high)], maxlen=self.win_len)

        if self.is_warming_up:
            return  # windows filling; no trading during warm-up

        # --- exits first (21-day hold) ---
        for s in list(self.exit_at.keys()):
            self.exit_at[s] -= 1
            if self.exit_at[s] <= 0:
                px = self.securities[s].close
                if px:
                    net = px / self.entry_px[s] - 1.0 - 2 * self.cost_side
                    self.trades.append((self.time.date(), str(s), net * 100))
                del self.exit_at[s]
                del self.entry_px[s]
                self.in_flight -= 1

        # --- entries: signal on cached windows ---
        for s in list(self.closes.keys()):
            if s in self.exit_at:
                continue
            if s not in self.active_securities.keys():
                continue
            cl = self.closes[s]
            if len(cl) < self.win_len:
                continue  # symbol newer than 291 days in cache
            c_arr = np.fromiter(cl, dtype=float)
            h_arr = np.fromiter(self.highs[s], dtype=float)
            if np.isnan(c_arr).any():
                continue
            if self._signal(c_arr, h_arr):
                px = self.securities[s].close
                if not px:
                    continue
                self.set_holdings(s, 0.02)
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
