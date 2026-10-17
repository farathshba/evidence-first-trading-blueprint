/*
 * Test 5.1 QC CONFIRMATION — ADR-conditioned champion (survivorship-free)
 * Spec: docs/US-TIER5-TEST-PLAN.md, Test 5.1. Baseline: PR #28 (4.5, EV +4.27%, 214 trades).
 * RUN TWICE on QuantConnect (LEAN), identical settings except ADR_MIN:
 *   Run A (baseline):   ADR_MIN = 0.0m
 *   Run B (conditioned): ADR_MIN = 0.04m
 * Frozen bars (registered 16 Oct, read AFTER both runs, no reruns):
 *   EV/trade > +0.60% @ 0.35%/side AND >= 6/13 positive years AND >= 150 trades
 *   AND conditioned EV >= baseline EV + 0.30pp — else no adoption.
 * Universe: US$1-10, 20d dollar-volume >= $3M, common equities, >= 260 trading days history.
 * Gates: SPY>SMA200 AND breadth>=0.50. Long-only, top-10, monthly rebalance (first trading day).
 * Costs: 0.35%/side via custom percent fee model below.
 */
using System;
using System.Collections.Generic;
using System.Linq;
using QuantConnect;
using QuantConnect.Algorithm;
using QuantConnect.Data;
using QuantConnect.Data.Market;
using QuantConnect.Data.UniverseSelection;
using QuantConnect.Orders;
using QuantConnect.Orders.Fees;
using QuantConnect.Securities;

namespace QuantConnect.Algorithm.CSharp
{
    // 0.35%/side percentage fee model (registered cost assumption)
    public class PercentFeeModel : FeeModel
    {
        private readonly decimal _rate;
        public PercentFeeModel(decimal rate) { _rate = rate; }
        public override OrderFee GetOrderFee(OrderFeeParameters parameters)
        {
            var security = parameters.Security;
            var price = security.Price;
            return new OrderFee(new CashAmount(Math.Abs(parameters.Order.Quantity) * price * _rate, Currencies.USD));
        }
    }

    public class Us51AdrConditionedChampion : QCAlgorithm
    {
        // ==== REGISTERED PARAMETERS (frozen — do not tune) ====
        public const decimal ADR_MIN = 0.04m;    // 0.0m for baseline run A
        public const int    TOP_N = 10;
        public const decimal MIN_PRICE = 1.0m, MAX_PRICE = 10.0m;
        public const decimal MIN_DVOL = 3000000m;
        public const decimal COST_PER_SIDE = 0.0035m;

        private Symbol _spy;
        private bool _rebalanceDue;
        private readonly HashSet<Symbol> _active = new HashSet<Symbol>();

        public override void Initialize()
        {
            SetStartDate(2016, 1, 4);   // AlgoSeek survivorship-free full sample (PR #28 window)
            SetEndDate(2026, 10, 9);
            SetCash(100000);
            SetBrokerageModel(new QuantConnect.Brokerages.DefaultBrokerageModel());

            _spy = AddEquity("SPY", Resolution.Daily).Symbol;
            Securities[_spy].SetFeeModel(new PercentFeeModel(COST_PER_SIDE));

            AddUniverse(CoarseSelection, FineSelection);
            Schedule.On(DateRules.MonthStart(), TimeRules.Midnight, () => _rebalanceDue = true);
        }

        public override void OnSecuritiesChanged(SecurityChanges changes)
        {
            foreach (var a in changes.AddedSecurities)
                if (a.Symbol != _spy)
                    Securities[a.Symbol].SetFeeModel(new PercentFeeModel(COST_PER_SIDE));
        }

        public IEnumerable<Symbol> CoarseSelection(IEnumerable<CoarseFundamental> coarse)
        {
            return coarse
                .Where(c => c.Price >= MIN_PRICE && c.Price <= MAX_PRICE
                            && c.DollarVolume >= MIN_DVOL
                            && c.Symbol.SecurityType == SecurityType.Equity)
                .OrderByDescending(c => c.DollarVolume)
                .Take(500)                                     // cost control for fine stage
                .Select(c => c.Symbol);
        }

        public IEnumerable<Symbol> FineSelection(IEnumerable<FineFundamental> fine)
        {
            if (!_rebalanceDue) return _active;                 // only reselect on rebalance days
            _rebalanceDue = false;

            var candidates = new List<Tuple<Symbol, decimal>>();
            foreach (var f in fine)
            {
                var s = f.Symbol;
                var bars = History(s, 253, Resolution.Daily).ToList();
                if (bars.Count < 260) continue;

                int n20 = Math.Max(0, bars.Count - 20);
                decimal dvol20 = bars.Skip(n20).Sum(b => b.Close * b.Volume) / 20m;
                if (dvol20 < MIN_DVOL) continue;

                // 20d mean ADR = (high-low)/close  [Test 5.1 filter]
                decimal adr20 = bars.Skip(n20).Sum(b => (b.High - b.Low) / b.Close) / 20m;
                if (ADR_MIN > 0 && adr20 < ADR_MIN) continue;

                // nearness to 52w high (rank signal, matches Mac-lab near52w)
                var last252 = bars.Skip(Math.Max(0, bars.Count - 252));
                decimal hi52 = last252.Max(b => b.High);
                decimal nearness = bars.Last().Close / hi52;
                candidates.Add(Tuple.Create(s, nearness));
            }
            if (candidates.Count == 0) return Enumerable.Empty<Symbol>();

            // breadth gate: >=50% of candidates above their SMA200
            int above = 0, counted = 0;
            foreach (var c in candidates)
            {
                var h = History(c.Item1, 200, Resolution.Daily).ToList();
                if (h.Count < 200) continue;
                decimal sma200 = h.Average(b => b.Close);
                counted++;
                if (h.Last().Close > sma200) above++;
            }
            bool breadthOk = counted > 0 && (decimal)above / counted >= 0.50m;

            // SPY regime gate
            var spyHist = History(_spy, 200, Resolution.Daily).ToList();
            bool spyOk = spyHist.Count >= 200 && spyHist.Last().Close > spyHist.Average(b => b.Close);

            if (!spyOk || !breadthOk) { _active.Clear(); return Enumerable.Empty<Symbol>(); }

            var selected = candidates.OrderByDescending(c => c.Item2).Take(TOP_N).Select(c => c.Item1).ToList();
            _active.Clear();
            foreach (var s in selected) _active.Add(s);
            return selected;
        }

        public override void OnData(Slice data)
        {
            // entries: equal-weight anything newly in _active and not yet held
            foreach (var s in _active)
            {
                if (s == _spy) continue;
                if (!Portfolio.ContainsKey(s) || !Portfolio[s].Invested)
                    SetHoldings(s, 1.0m / TOP_N);
            }
            // exits: liquidate held names that fell out of the selection
            foreach (var kvp in Portfolio)
            {
                var s = kvp.Key;
                if (s == _spy) continue;
                if (kvp.Value.Invested && !_active.Contains(s))
                    Liquidate(s);
            }
        }
    }
}
