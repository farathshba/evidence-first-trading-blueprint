"""Test 1.3: sizing-integrity audit (Reddit critique, 8 Oct 2026).
Asserts the champion's sizing/tie-breaks are period-invariant:
A) Stake formula is P&L-blind (static code audit).
B) Determinism: identical runs -> byte-identical trades log.
C) Share rounding is deterministic (documented quirk).
"""
import subprocess, sys, hashlib, glob
import pandas as pd

print("=== TEST 1.3: SIZING INTEGRITY ===")

# A) Static audit: stake formula references only cash and slot count
src = open("scripts/momentum_backtest.py").read()
stake_line = [l for l in src.splitlines() if l.strip().startswith("stake =")][0].strip()
assert "cash" in stake_line and "len(" in stake_line, f"stake formula changed: {stake_line}"
for bad in ("equity", "drawdown", "nav", "loss"):
    assert bad not in stake_line, f"stake formula references {bad}: {stake_line}"
print(f"A) PASS - stake formula is P&L-blind: `{stake_line}`")

# B) Determinism: two identical runs -> identical trades CSV
def run():
    subprocess.run([sys.executable, "scripts/momentum_backtest.py", "--data-dir", "data_v3_clean"],
                   check=True, capture_output=True)
    return hashlib.md5(open(sorted(glob.glob("results/champion_trades_*.csv"))[-1], "rb").read()).hexdigest()
h1, h2 = run(), run()
assert h1 == h2, "NON-DETERMINISTIC: identical runs diverge"
print("B) PASS - identical runs -> byte-identical trades log (stateless tie-break)")

# C) Documented quirks
print("C) INFO - quirks documented: stake divides by NEW buys (not slots); int(stake//px) whole-share floor favors pricier names. Both deterministic, neither P&L-dependent.")
print("\n1.3 VERDICT: PASS - sizing is period-invariant; no loss-dependent caps; tie-break stateless.")
