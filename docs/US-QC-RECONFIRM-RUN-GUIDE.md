# US Test 6.1/6.2 QuantConnect Re-Confirmation Run Guide

Dead-simple instructions. You do not need to code anything. You copy, paste, click, and paste results back into the chat.

## Why we are doing this (30 seconds)

Our first backtest (23 Nov) used free Yahoo data. Yahoo data can be wrong (it was wrong before in Tests 5.1 and 5.3). Our rules say: a win on Yahoo data does NOT count until the same test also wins on better data. QuantConnect (QC) has better data. It includes dead companies, so winners are not inflated by companies that simply survived. If the test passes on QC too, the strategy gets much more believable. If it fails on QC, the Day-1 PASS is cancelled, permanently. This exact rule was frozen and registered here: `docs/US-QC-RECONFIRM-6-1-6-2-SPEC.md`.

## What was already checked before you touch anything

The QC version (`scripts/qc/Main.py`) is not a fresh guess. It is a line-by-line port of our frozen script, and it was tested against the frozen script on real ticker data (ABAT, ABEO, ABEV plus SPY). Result: the two engines produced the same trades, every single one, on both test arms (154 trades out of 154, arm A and arm B, exact match on entry date, entry price, exit price, and return). Two port bugs were found and fixed during this check (a queue that never emptied, and a retest window one bar too long). That is why this check matters.

## Step 1: Make a free QC account (5 min)

1. Go to `quantconnect.com` and sign up. The free plan is enough.
2. In the Cloud tab, click **Create new project**.
3. Name it `us-6-1-reconfirm`. Choose **Python** as the language. Click Create.

## Step 2: Put the code in (3 min)

1. In your new project, click the file called `Main.py` in the left panel. The editor opens with some sample code in it.
2. Select ALL of that sample code and delete it.
3. Open the `Main.py` file from this repo (also attached in chat as a downloadable file). Select ALL of it, copy, and paste it into the QC editor.
4. Click **Build** (top right). It should say the build succeeded. If it shows a red error, do not fix anything yourself, just paste the error into the chat.

You only paste the code once. For all runs you only change 3 numbers at the top of the file.

## Step 3: Run the 6 registered runs

You change ONLY the SETTINGS block at the very top of the code (the lines between the `====` marks). After each edit: save, then click **Backtest**. Wait for it to finish. Then change the settings again for the next run.

| Run | What it is | PROBE | RUN_ARM | COST_PER_SIDE |
|---|---|---|---|---|
| R0 | Sanity probe (tiny, fast, one ticker) | `True` | `"A"` | `0.0035` |
| R1 | The real Test 6.1 (arm A) | `False` | `"A"` | `0.0035` |
| R2 | The real Test 6.2 (arm B) | `False` | `"B"` | `0.0035` |
| R3 | Stress-cost version of R1 | `False` | `"A"` | `0.0055` |
| R4 | Stress-cost version of R2 | `False` | `"B"` | `0.0055` |
| R5 | Exact rerun of R1 (must match R1 perfectly) | `False` | `"A"` | `0.0035` |

Important rules, frozen:

- ONE run per row. If a run crashes, paste the error in the chat. Do not rerun the same row over and over until numbers look nice. That is the one-run rule and it is what keeps us honest.
- Never change anything below the SETTINGS block.
- R0 should finish in a minute or two and produce few or no trades. It is a health check, not a verdict. Do not judge anything by R0.
- R1 to R5 scan every US stock, so each can take from ten minutes to over an hour on the free plan. That is normal. Let it run.

## Step 4: Copy the results back (2 min per run)

After each run finishes:

1. Click the run's **Logs** tab (bottom panel, next to Results).
2. Find the lines that start with:
   - `RUN CONFIG:`
   - `=== QC RE-CONFIRMATION SUMMARY`
   - every `trades=`, `positive_years=`, `CAUTION` line, and the year lines under them.
3. Copy those lines and paste them into the chat, one message per run, labelled `R0`, `R1`, ... `R5`. You do not need the giant chart-report graph, only the log lines.

If the log instead says `NO TRADES`, or the run errors out, paste that too. Do not diagnose alone, and do not rerun.

## What happens after you paste

The assistant reads each run against the frozen bars exactly once: EV net above +0.60%, at least 6 positive years out of up to 13, at least 150 trades, stress-cost run must still pass, and arm B must beat arm A by at least +0.30 percentage points. Two caution numbers (EV without the top 1% winners, and how much of the profit comes from the best 100 trades) are reported but do not pass or fail the test; they feed the fragility chat afterwards.

- If QC passes: the strategy earns the right to the next conversation (paper venue, spread auditing).
- If QC fails: the Day-1 PASS is void forever, the class is tombstoned, and we move on. No third data source unless the owner says so.

That is the whole job. Six runs, six log pastes, done.
