#!/usr/bin/env python3
# QUANTCONNECT LEAN — US Test 5.3 QC CONFIRMATION PORT v2 (RSI div + Fib golden pocket)
#
# v2 (19 Oct): PERFORMANCE REFACTOR — same frozen rule and bars as v1, logic UNTOUCHED.
# v1 pulled self.history([s], 291) for every symbol every day (~200 reqs/day -> the
# free-tier run stalled with no date progress). v2 maintains a ROLLING WINDOW cache:
# one history pull per symbol on first sight, then one bar appended per day via the
# daily slice. Same 291-bar signal input, same _signal() math, byte-for-byte rules.
# Apparatus note logged: this is an efficiency fix to an apparatus bug (stall), not a
# rule change — v1 run consumed no bars (stalled in warm-up, zero trades).
#
# FROZEN RULE (identical to Mac v2 / v1): US$1-10, dvol>=US$3M; EMA50>EMA200; swing leg
# = prior 90d max-high day j, leg_low = min close of 90d ending at j; close in golden
# pocket 38.2-61.8%; RSI(14) Wilder div proxy (new 5d low, RSI > 10d min); entry at
# close, hold 21 trading days, non-overlapping; costs applied in ledger (-2x0.35%).
#
# FROZEN BARS (read once): EV > +0.60% net; >= 6/13 positive years; >= 150 trades else
# VOID; REPORT maxDD + MAX_CONC (informational). CONFIRMED / INVERTED / VOID.
#
# Segments: A 2014-01-01..2020-06-30, B 2020-07-01..2026-07-15 (boundary uncounted).
# QC lessons baked in: no self.<name> shadowing QCAlgorithm members; combined
# coarse+fine selectors get Fundamental objects (has_fundamental_data); Securities
# close with None guard; SetWarmUp(300, Daily); compact logging (10KB cap).

from AlgorithmImports import *
from collections import deque
import numpy as np


class UsTest53RsiFibV2(QCAlgorithm):

    def initialize(self):
        self.set_start_date(2014, 1, 1)   # SEGMENT A; B: 2020-07-01..2026-07-15
        self.set_end_date(2020, 6, 30)
        self.set_cash(100000)
        self.set_benchmark("SPY")

        self.hold_days = 21
        self.cost_side = 0.0035
        self.rsi_period = 14
        self.min_price, self.max_price, self.min_dvol = 1.0, 10.0, 3e6
        self.win_len = 291   # rolling window per symbol (90 leg + 200 EMA + 1 today)

        self.add_universe(self._coarse, self._fine)
        self.set_warm_up(300, Resolution.Daily)

        self.exit_at = {}
        self.entry_px = {}
        self.trades = []
        self.in_flight = 0
        self.max_conc_seen = 0
        # v2 rolling caches
        self.closes = {}   # symbol -> deque of closes (oldest..latest, incl. today)
        self.highs = {}    # symbol -> deque of highs
        self.seeded = set()

    # ---------- universe ----------
    def _coarse(self, coarse):
        if self.is_warming_up:
            return Universe.UNCHANGED
        return [c.symbol for c in coarse
                if c.has_fundamental_data
                and self.min_price <= c.adjusted_price <= self.max_price
                and c.dollar_volume >= self.min_dvol]

    def _fine(self, fine):
        return [f.symbol for f in fine][:200]

    # ---------- helpers (identical math to v1) ----------
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
        if self.is_warming_up:
            return

        # --- v2: update rolling caches from the daily slice (one bar per symbol) ---
        for s in self.active_securities.keys():
            if s not in self.seeded:
                hist = self.history([s], self.win_len, Resolution.Daily)
                if hist is None or hist.empty:
                    continue
                try:
                    if isinstance(hist.index, MultiIndex):
                        c = hist.loc[str(s)]["close"].values
                        h = hist.loc[str(s)]["high"].values
                    else:
                        c = hist["close"].values
                        h = hist["high"].values
                except Exception:
                    continue
                if len(c) == 0:
                    continue
                self.closes[s] = deque(c.tolist(), maxlen=self.win_len)
                self.highs[s] = deque(h.tolist(), maxlen=self.win_len)
                self.seeded.add(s)
                continue  # history() excludes today's bar; today appended below
            bar = slice.get(s)
            if bar is not None:
                self.closes[s].append(float(bar.close))
                self.highs[s].append(float(bar.high))

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
                continue
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
