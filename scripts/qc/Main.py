# QUANTCONNECT CLOUD ALGORITHM - US Test 6.1/6.2 survivorship-free re-confirmation
# QC port of scripts/us/us_6_1_break_retest.py (frozen mechanics, one-run discipline).
# Upload as Main.py in a NEW QC Python project. Edit ONLY the SETTINGS block per run.
# Runs (per docs/US-QC-RECONFIRM-6-1-6-2-SPEC.md):
#   R0 probe  : PROBE=True,  RUN_ARM="A", COST_PER_SIDE=0.0035
#   R1 6.1 A  : PROBE=False, RUN_ARM="A", COST_PER_SIDE=0.0035
#   R2 6.2 B  : PROBE=False, RUN_ARM="B", COST_PER_SIDE=0.0035
#   R3 stress : PROBE=False, RUN_ARM="A", COST_PER_SIDE=0.0055
#   R4 stress : PROBE=False, RUN_ARM="B", COST_PER_SIDE=0.0055
#   R5 determinism rerun of R1 (numbers must match R1 exactly)

from AlgorithmImports import *

# ==== SETTINGS (edit these between runs; NEVER the frozen constants below) ====
RUN_ARM = "A"           # "A" = opposing-trendline exit | "B" = S/R take-profit exit
COST_PER_SIDE = 0.0035   # 0.0035 base cost | 0.0055 stress cost
PROBE = False            # True = single-ticker apparatus sanity run
PROBE_SYMBOL = "SENS"    # used only when PROBE = True
DUMP_TRADES = False      # True = log every trade row (produces a huge log)
# ============================================================================

W_PEAK = 5
TOUCH_ATR = 0.25
N_RETEST = 10
SMA200_TICK = 252
DVOL_WIN = 20
UNIV_MIN, UNIV_MAX = 1.0, 10.0
DVOL_MIN = 3000000.0
TP_TOUCH_MIN = 3
EPS = 1e-9


class UsSixOneReconfirm(QCAlgorithm):

    def initialize(self):
        self.set_start_date(2014, 1, 1)
        self.set_end_date(2026, 10, 31)
        self.set_cash(100000)
        self.universe_settings.resolution = Resolution.DAILY
        # CRITICAL DATA FIX (25 Nov): QC defaults to ADJUSTED (dividends+split
        # adjusted) prices. Day-1 used split-adjusted-only closes (Yahoo 'close'
        # column). Dividend-adjusted data erases ex-div gaps, so the Arm-A stop
        # line almost never triggers, trades hold for years, EV explodes (R1
        # showed +38.6%/trade). Use SPLIT_ADJUSTED to match the frozen methodology.
        self.universe_settings.data_normalization_mode = DataNormalizationMode.SPLIT_ADJUSTED
        self.spy_symbol = self.add_equity(
            "SPY", Resolution.DAILY,
            data_normalization_mode=DataNormalizationMode.SPLIT_ADJUSTED).symbol
        self.subscribed = set()
        self.spy_closes = []
        self.gate_by_date = {}
        self.state = {}
        self.trades = []
        if PROBE:
            self.add_equity(PROBE_SYMBOL, Resolution.DAILY,
                            data_normalization_mode=DataNormalizationMode.SPLIT_ADJUSTED)
        else:
            self.add_universe(self.coarse)
        self.log("RUN CONFIG: arm=%s cost/side=%.4f probe=%s" % (RUN_ARM, COST_PER_SIDE, PROBE))
        self.log("DATA NORM: split-adjusted (matches Day-1 close-column convention)")

    def coarse(self, coarse):
        # Point-in-time superset: subscribe permanently on first qualification.
        # Permanent subscription keeps each symbol's price history contiguous,
        # exactly like the per-file backtest. Delisted tickers keep their data.
        for f in coarse:
            p = f.price
            if 0.90 <= p <= 10.5 and f.symbol not in self.subscribed:
                self.subscribed.add(f.symbol)
        return list(self.subscribed)

    def on_data(self, slice):
        # QC cloud: slice.bars is a .NET DataDictionary exposing .Values (capital V).
        # Local harness uses a plain Python dict with .values(). Support both.
        _bars = slice.bars
        _vals = getattr(_bars, "Values", None)
        bars = list(_vals) if _vals is not None else list(_bars.values())
        if not bars:
            return
        for bar in bars:
            sym = bar.symbol
            if sym == self.spy_symbol or sym.value == "SPY":
                self._on_spy(bar)
            else:
                self._on_symbol_bar(sym, bar)

    def _on_spy(self, bar):
        d = bar.end_time.date()
        self.spy_closes.append(bar.close)
        n = len(self.spy_closes)
        if n < SMA200_TICK:
            self.gate_by_date[d] = False
        else:
            sma = sum(self.spy_closes[n - SMA200_TICK:]) / float(SMA200_TICK)
            self.gate_by_date[d] = self.spy_closes[-1] > sma

    def _new_state(self):
        return {"o": [], "h": [], "l": [], "c": [], "d": [], "prods": [], "tr": [],
                "swing_h": [], "swing_l": [], "wins": [], "eq": [], "pos": []}

    def _on_symbol_bar(self, sym, bar):
        st = self.state.setdefault(sym.value, self._new_state())
        st["sym"] = st.get("sym", sym.value)
        o, h, l, c, v = bar.open, bar.high, bar.low, bar.close, bar.close * bar.volume
        if not (o > 0 and h > 0 and l > 0 and c > 0):
            return
        st["o"].append(o); st["h"].append(h); st["l"].append(l); st["c"].append(c)
        st["d"].append(bar.end_time.date()); st["prods"].append(v)
        n = len(st["c"])
        if n == 1:
            st["tr"].append(h - l)
        else:
            pc = st["c"][n - 2]
            st["tr"].append(max(h - l, abs(h - pc), abs(l - pc)))
        # pivot confirmation: with bar n-1 in hand, pivot index n-6 is decidable
        j = n - 6
        if j >= W_PEAK:
            hh, ll = st["h"], st["l"]
            if hh[j] == max(hh[j - W_PEAK:j + W_PEAK + 1]):
                st["swing_h"].append(j)
            if ll[j] == min(ll[j - W_PEAK:j + W_PEAK + 1]):
                st["swing_l"].append(j)
        t = n - 1
        atr_t = self._atr(st, t)
        # 1) queued entries execute at this bar's open (entry = open of bar E)
        while st["eq"]:
            st["eq"].pop()
            self._register_position(st, t)
        # 2) exits for open virtual positions (checked from bar e+1 onward)
        for pos in list(st["pos"]):
            if t > pos["e"]:
                px = st["c"][t]
                m2, b2 = pos["stop"]
                exit_px = None
                if m2 is not None and px < m2 * t + b2:
                    exit_px = px
                elif RUN_ARM == "B" and pos["target"] is not None and px >= pos["target"]:
                    exit_px = px
                if exit_px is not None:
                    self._record_trade(st, pos, exit_px, t)
                    st["pos"].remove(pos)
        # 3) mature retest windows (each break-bar keeps its OWN window;
        #    faithful port: the original scans forward from EVERY break bar
        #    independently, so windows overlap and trades may overlap)
        if atr_t is not None:
            for w in list(st["wins"]):
                if t >= w["t0"] + N_RETEST:
                    st["wins"].remove(w)
                    continue
                m, b = w["m"], w["b"]
                yk = m * t + b
                if st["l"][t] <= yk + TOUCH_ATR * atr_t and st["c"][t] > yk:
                    st["wins"].remove(w)
                    st["eq"].append(True)
        # 4) new break detection at bar t (filters here; k = t checked now)
        if atr_t is None or atr_t <= 0:
            return
        if not PROBE:
            px = st["c"][t]
            if not (UNIV_MIN <= px <= UNIV_MAX):
                return
            if t < DVOL_WIN - 1:
                return
            dv = sum(st["prods"][t - DVOL_WIN + 1:t + 1]) / float(DVOL_WIN)
            if dv < DVOL_MIN:
                return
            if not self.gate_by_date.get(st["d"][t], False):
                return
        line = self._down_line(st, t)
        if line is None:
            return
        m, b = line
        if st["c"][t - 1] > m * (t - 1) + b:
            yk = m * t + b
            if st["l"][t] <= yk + TOUCH_ATR * atr_t and st["c"][t] > yk:
                st["eq"].append(True)      # retest satisfied on the break bar itself
            else:
                st["wins"].append({"m": m, "b": b, "t0": t})

    def _atr(self, st, i):
        if i < 13 or i >= len(st["tr"]):
            return None
        w = st["tr"][i - 13:i + 1]
        return sum(w) / 14.0

    def _down_line(self, st, t):
        # two most recent swing highs with index <= t - W_PEAK
        order = self._upto(st["swing_h"], t - W_PEAK)
        if order is None or len(order) < 2:
            return None
        for j in range(len(order) - 1, 0, -1):
            i2, i1 = order[j], order[j - 1]
            if i2 <= i1:
                continue
            if st["h"][i2] < st["h"][i1]:
                m = (st["h"][i2] - st["h"][i1]) / float(i2 - i1)
                b = st["h"][i1] - m * i1
                for idx in range(i1 + 1, i2):
                    if st["c"][idx] > m * idx + b + EPS:
                        return None
                return (m, b)
            break
        return None

    def _up_line(self, st, e):
        order = self._upto(st["swing_l"], e - W_PEAK)
        if order is None or len(order) < 2:
            return (None, None)
        for j in range(len(order) - 1, 0, -1):
            i2, i1 = order[j], order[j - 1]
            if i2 <= i1:
                continue
            if st["l"][i2] > st["l"][i1]:
                m = (st["l"][i2] - st["l"][i1]) / float(i2 - i1)
                b = st["l"][i1] - m * i1
                for idx in range(i1 + 1, i2):
                    if st["c"][idx] < m * idx + b - EPS:
                        return (None, None)
                return (m, b)
            break
        return (None, None)

    @staticmethod
    def _upto(arr, limit):
        # monotonic list; return tail with all elements <= limit
        lo, hi = 0, len(arr)
        while lo < hi:
            mid = (lo + hi) // 2
            if arr[mid] <= limit:
                lo = mid + 1
            else:
                hi = mid
        if lo == 0:
            return None
        return arr[max(0, lo - 64):lo]

    def _register_position(self, st, E):
        entry = st["o"][E]
        stop = self._up_line(st, E)
        aatr = self._atr(st, E)
        target = None
        if RUN_ARM == "B" and aatr is not None:
            cand = None
            order = self._upto(st["swing_h"], E - W_PEAK)
            if order:
                for j in range(len(order) - 1, -1, -1):
                    i = order[j]
                    if i < E - 60:
                        break
                    base = st["h"][i]
                    lo_i = max(0, i - 60)
                    cnt = 0
                    for idx in range(lo_i, E):
                        hh = st["h"][idx]
                        if base - TOUCH_ATR * aatr <= hh <= base + TOUCH_ATR * aatr:
                            cnt += 1
                    if cnt >= TP_TOUCH_MIN:
                        cand = base
                        break
            if cand is None:
                lo = max(0, E - N_RETEST)
                cand = max(st["h"][lo:E + 1])
            target = cand - TOUCH_ATR * aatr
        if entry > 0:
            st["pos"].append({"e": E, "entry": entry, "stop": stop,
                              "target": target, "atr_e": aatr})

    def _record_trade(self, st, pos, exit_px, t):
        ret_gross = exit_px / pos["entry"] - 1.0
        self.trades.append({
            "entry_date": st["d"][pos["e"]].isoformat(),
            "exit_date": st["d"][t].isoformat(),
            "entry": pos["entry"], "exit": exit_px,
            "ret_gross": ret_gross, "ret_net": ret_gross - 2.0 * COST_PER_SIDE,
            "sym": st["sym"], "arm": RUN_ARM})

    def on_end_of_algorithm(self):
        # window-end flat: close any open virtual position at its last close
        # (queued-but-never-filled entries are dropped, matching the original's
        # "entry_t >= len(df)" skip at end of data)
        for key, st in self.state.items():
            n = len(st["c"])
            for pos in list(st["pos"]):
                if n >= 1:
                    self._record_trade(st, pos, st["c"][n - 1], n - 1)
                st["pos"].remove(pos)
        tr = self.trades
        n = len(tr)
        if n == 0:
            self.log("NO TRADES - do NOT log a verdict; diagnose via probe first")
            return
        rets = [x["ret_net"] for x in tr]
        ev = sum(rets) / float(n)
        by_year = {}
        for x in tr:
            y = x["entry_date"][:4]
            cnt, s = by_year.get(y, (0, 0.0))
            by_year[y] = (cnt + 1, s + x["ret_net"])
        pos_years = sum(1 for y in by_year if by_year[y][1] / by_year[y][0] > 0)
        self.log("=== QC RE-CONFIRMATION SUMMARY (arm=%s) ===" % RUN_ARM)
        self.log("trades=%d  EV(net, cost %.2f%%/side) = %.4f%%" %
                 (n, COST_PER_SIDE * 100, ev * 100))
        self.log("positive_years=%d/%d  (bar: >= 6/13)" % (pos_years, len(by_year)))
        self.log("EV bar: > +0.60%% | trades bar: >= 150")
        for y in sorted(by_year):
            cnt, s = by_year[y]
            self.log("  %s  n=%d  ev=%.4f" % (y, cnt, s / cnt))
        # pre-registered caution metrics (reported, not pass/fail)
        desc = sorted(rets, reverse=True)
        k1 = max(1, int(0.01 * n))
        ev_ex_top1 = sum(desc[k1:]) / float(n - k1)
        tot = sum(rets)
        self.log("CAUTION (not pass/fail): EV excl. top-1%% winners = %.4f%%" % (ev_ex_top1 * 100))
        if tot > 0:
            self.log("CAUTION (not pass/fail): top-100 trades share of net PnL = %.1f%%" %
                     (sum(desc[:100]) / tot * 100))
        wins = sorted(tr, key=lambda x: -x["ret_net"])[:50]
        self.log("TOP-50 WINNERS AUDIT sym,entry_date,exit_date,entry,exit,ret_net")
        for x in wins:
            self.log("%s,%s,%s,%.2f,%.2f,%.2f%%" %
                     (x["sym"], x["entry_date"], x["exit_date"], x["entry"],
                      x["exit"], x["ret_net"] * 100))
        if DUMP_TRADES:
            self.log("entry_date,exit_date,entry,exit,ret_gross,ret_net,arm")
            for x in tr:
                self.log("%s,%s,%.5f,%.5f,%.6f,%.6f,%s" %
                         (x["entry_date"], x["exit_date"], x["entry"], x["exit"],
                          x["ret_gross"], x["ret_net"], x["arm"]))
