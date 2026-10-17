# Test 5.1 QC CONFIRMATION — ADR-conditioned champion (survivorship-free)
# Spec: docs/US-TIER5-TEST-PLAN.md, Test 5.1. Baseline: PR #28 (4.5, EV +4.27%, 214 trades).
# RUN TWICE on QuantConnect (LEAN), identical settings except ADR_MIN:
#   Run A (baseline):    ADR_MIN = 0.0
#   Run B (conditioned): ADR_MIN = 0.04
# Frozen bars (registered 16 Oct, read AFTER both runs, no reruns):
#   EV/trade > +0.60% @ 0.35%/side AND >= 6/13 positive years AND >= 150 trades
#   AND conditioned EV >= baseline EV + 0.30pp — else no adoption.
# v3 17 Oct: fixed History-window bug (253 requested vs 260 required -> 0 trades).
# v4 17 Oct: guard OHLCV columns (KeyError on volume for some symbols) — skips logged.
# v5 17 Oct: (1) position sizing 0.95/TOP_N to stop 'Insufficient buying power' order
# rejections (execution plumbing; per-trade % EV and the 0.35% fee are size-independent;
# identical in both runs so the A-vs-B key bar remains valid). (2) Replaced the scheduled
# midnight rebalance flag (race with universe selection caused month-long no-trade gaps)
# with deterministic month-rollover detection inside FineSelection.

from AlgorithmImports import *

# ==== REGISTERED PARAMETERS (frozen — do not tune) ====
ADR_MIN = 0.04        # 0.0 for baseline run A
TOP_N = 10
MIN_PRICE = 1.0
MAX_PRICE = 10.0
MIN_DVOL = 3_000_000
COST_PER_SIDE = 0.0035
COARSE_CAP = 500     # cost control for fine stage (pre-registered tradeoff)
SIZE_FACTOR = 0.95   # buying-power buffer (execution plumbing, v5)
NEED_COLS = {"open", "high", "low", "close", "volume"}


class PercentFeeModel(FeeModel):
    "0.35%/side percentage fee (registered cost assumption)"
    def __init__(self, rate):
        self.rate = rate

    def GetOrderFee(self, parameters):
        quantity = abs(parameters.Order.Quantity)
        price = parameters.Security.Price
        fee = quantity * float(price) * self.rate
        return OrderFee(CashAmount(fee, "USD"))


class Us51AdrConditionedChampion(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2016, 1, 4)   # AlgoSeek survivorship-free window (PR #28)
        self.SetEndDate(2026, 10, 9)
        self.SetCash(100000)
        self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage)

        self.spy = self.AddEquity("SPY", Resolution.Daily).Symbol
        self.Securities[self.spy].SetFeeModel(PercentFeeModel(COST_PER_SIDE))

        self.active = set()
        self.last_sel_month = None   # v5: deterministic month-rollover detection

        self.AddUniverse(self.CoarseSelection, self.FineSelection)

    def OnSecuritiesChanged(self, changes):
        # apply the registered percent fee model to every equity the universe adds
        for a in changes.AddedSecurities:
            if a.Symbol != self.spy:
                self.Securities[a.Symbol].SetFeeModel(PercentFeeModel(COST_PER_SIDE))

    def CoarseSelection(self, coarse):
        # price band + single-day dvol pre-filter (fine stage applies true 20d mean)
        selected = [c for c in coarse
                    if MIN_PRICE <= c.Price <= MAX_PRICE
                    and c.DollarVolume >= MIN_DVOL
                    and c.Symbol.SecurityType == SecurityType.Equity]
        selected.sort(key=lambda c: c.DollarVolume, reverse=True)
        return [c.Symbol for c in selected[:COARSE_CAP]]

    def FineSelection(self, fine):
        # v5: rebalance on the first selection of each new month (deterministic)
        cur_month = (self.Time.year, self.Time.month)
        if cur_month == self.last_sel_month:
            return list(self.active)            # keep holdings between rebalances
        self.last_sel_month = cur_month

        candidates = []   # (symbol, nearness)
        for f in fine:
            s = f.Symbol
            bars = self.History(s, 400, Resolution.Daily)
            if bars.empty or len(bars) < 260:
                continue
            # v4: skip symbols whose history frame lacks full OHLCV columns
            if not NEED_COLS.issubset(bars.columns):
                self.Debug(f"skip {s.Value}: incomplete history frame: {list(bars.columns)}")
                continue
            closes = bars["close"].values
            highs = bars["high"].values
            lows = bars["low"].values
            volumes = bars["volume"].values

            # 20d dollar-volume mean
            dvol20 = float((closes[-20:] * volumes[-20:]).mean())
            if dvol20 < MIN_DVOL:
                continue

            # 20d mean ADR = (high-low)/close  [Test 5.1 filter]
            adr20 = float(((highs[-20:] - lows[-20:]) / closes[-20:]).mean())
            if ADR_MIN > 0 and adr20 < ADR_MIN:
                continue

            # nearness to 52w high (rank signal, matches Mac-lab near52w)
            hi52 = float(highs[-252:].max())
            nearness = float(closes[-1]) / hi52
            candidates.append((s, nearness))

        if not candidates:
            self.active.clear()
            return []

        # breadth gate: >=50% of candidates above their SMA200
        above = 0
        counted = 0
        for s, _ in candidates:
            h = self.History(s, 220, Resolution.Daily)
            if h.empty or len(h) < 200 or "close" not in h.columns:
                continue
            sma200 = float(h["close"].values.mean())
            counted += 1
            if float(h["close"].values[-1]) > sma200:
                above += 1
        breadth_ok = counted > 0 and (above / counted) >= 0.50

        # SPY regime gate
        sh = self.History(self.spy, 220, Resolution.Daily)
        spy_ok = (not sh.empty) and len(sh) >= 200 and "close" in sh.columns and \
                 float(sh["close"].values[-1]) > float(sh["close"].values.mean())

        if not spy_ok or not breadth_ok:
            self.active.clear()
            return []

        selected = [s for s, _ in sorted(candidates, key=lambda x: x[1], reverse=True)[:TOP_N]]
        self.active = set(selected)
        return selected

    def OnData(self, data):
        # entries: equal-weight anything newly in self.active and not yet held
        for s in self.active:
            if s == self.spy:
                continue
            if s in self.Portfolio and self.Portfolio[s].Invested:
                continue
            self.SetHoldings(s, SIZE_FACTOR / TOP_N)
        # exits: liquidate held names that fell out of the selection
        for s in list(self.Portfolio.Keys):
            if s == self.spy:
                continue
            if self.Portfolio[s].Invested and s not in self.active:
                self.Liquidate(s)
