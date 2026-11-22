# Test 5.4 Run Amendment — Pre-Registered Paired Arms (Owner Decision, 22 Nov 2026)

**Scope:** Amends the frozen registration of **Test 5.4 (15m Opening Range Breakout, gap-up only, same-day exit)** in docs/US-TESTS-5-4-5-6-INTRADAY-REGISTRATION.md BEFORE its first run, per owner decision 22 Nov 2026 (prompted by Tier 6 source triage, Video 3). All other frozen 5.4 mechanics — universe, window, costs, bars (EV > +0.60%, ≥6/10 yrs, ≥500 trades, 0.55% stress mandatory), gap-up-only filter, ≤2% width filter, same-day exit — are UNCHANGED.

**Discipline preserved:** one registered run, executed once, with the arms computed from that same run's fills. No gate-widening, no re-runs. These arms are pre-registered here and frozen BEFORE any 5.4 code executes.

**Arm 1 — Retest entry (vs registered confirmed-close entry):**
- Registered arm: entry on the 5-minute candle CLOSE beyond the 15-minute opening range.
- Arm 1: after the confirmed close beyond the range, enter on the pullback that touches the broken 15-minute range level (touch = within 0.25 × ATR(14, 5m)) within N=6 bars; confirmation candle closes beyond the range on the far side; entry next bar open. If no pullback occurs within N bars, the trade is skipped in Arm 1 (this skip-rate must be reported).
- **Key bar: Arm 1 EV − Registered-arm EV ≥ +0.30pp** for retest entry to be considered an improvement. Prior: 4.7b found breakout-entry strictly worse than nearness on the daily 52w scan — direction is that retest ≥ breakout, so a fail here quietly closes the breakout-vs-retest question on intraday too. Hard stop and all other mechanics identical.

**Arm 2 — Fixed 1:2 take-profit (vs registered day-end exit):**
- Registered arm: exit at day-end logic.
- Arm 2: target at 2× entry-to-stop distance, in the signal direction; stop unchanged; whichever of target / stop / day-end hits first closes the trade. Both arms reported from the same run.
- **Key bar: Arm 2 EV − Registered-arm EV ≥ +0.30pp** for the fixed-1:2 exit to be considered an improvement.

**Adoption logic unchanged:** even if an arm beats its key bar, 5.4's own Stage-1 bars must ALSO pass for anything to be adopted; nothing here touches the live 4.5 champion or the 2 Nov deployments.

**Notes:**
- Registered prediction (system-wide, standing): the whole 5.4 class FAILs — arms are expected to measure FAIL, tombstone-completion.
- Untestable Video 3 elements (wick/pressure reads, mental stops, discretionary targets) remain excluded and do NOT enter either arm.
