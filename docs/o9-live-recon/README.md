# o9-live + fakeAPI recon — handover

Joe 0929: *"I want to get o9-live + fakeAPI online so that we can start troubleshooting any potential
non-causal issues"* and *"the goal for this next step is purely recon against backtest. I'll keep
improving the strategy in the background while o9-live is under review"*.

**This is a forward test against a fake exchange. It is not live trading.** Joe 0929: *"we're not
going 'online-live'. fakeAPI is our test-bed which o9-live connects to"*.

## The startup prompt

> Read every file in `docs/o9-live-recon/`, then `.claude/joes-convo-style.md` and
> `docs/staying_light.md`. Run the two commands under "Reproduce it before you trust it" in
> `README.md` and tell me whether they match the stated numbers.
>
> Then, in your own words: read back the trade rules from `OPEN.md`'s **Ruled** table — that table,
> not `SPEC.md`'s narrative, is what the code does — state the difference
> between a forward read and a deferred decision as `CAUSALITY.md` draws it, and tell me which of
> the five build steps in `CODE_MAP.md` you would do first and why.
>
> Do not write code until I answer.

## The files

| | |
|---|---|
| `SPEC.md` | the strategy, the knobs, and what a recon has to prove |
| `CODE_MAP.md` | what already exists, what is new, and the five things that are NOT built |
| `CAUSALITY.md` | the full audit, module by module, and the one trap that is still live |
| `RECON.md` | the recon procedure, the wake mechanism, and the 24-hour re-validation |
| `OPEN.md` | what Joe has ruled, what he has not, and the traps |
| `MVP2.md` | what MVP1 deliberately leaves out, and why. **Not MVP1 work** |

## The one-line state

**THE STRATEGY CHANGED SUBSTANTIALLY ON 0929-late. Everything below supersedes the older numbers
still present in this package.** Three rulings from Joe and one defect he caught:

| | |
|---|---|
| a sig_utc closes ONLY on an opposing dr | a same-dr sig_utc is INERT |
| the dr-flip backstop CLOSES but never OPENS | the book goes flat instead |
| MAE is capped at **0.70%** and the cap is a STOP | `MFE-MAE` prints `-0.70` when hit |

Three more rulings landed 0929-late, after the above:

| | |
|---|---|
| same-bar, stop vs opposing sig_utc | **the STOP wins** — Joe: *"use stop"* |
| order type | **market**, both legs. Limit placement is MVP2 |
| the stop is client-side for MVP1 | a LARGER exchange-resident backstop is MVP2 |

**THE MACHINE, as handed over:**

    signal      wsf_leash v7 `wsl_sig_utc`, from the banked wsf_dtf_v3 knobs
                span 10, slope 0.40, fence 25/75, samples 21, tf 1..23, support_min 23
    gate        rule1_gate config v2 - backward-only [k-84 bars, k], run clamped at the edge
    walk        trade_walk.walk - opposing-dr close, dr-flip closes only. BOTH rulings are in
                the code as of 0929-late; the banked wsf_trades rows are NOT - see OPEN.md item 8
    stop        MAE cap 0.70%, at the first bar the adverse excursion reaches it. Joe specified
                0.9 on 0929, saw the 0.05 sweep, and ruled 0.70. IT IS APPLIED IN SCORING ONLY -
                sweep_mae_cap.py, not trade_walk.walk - because "does a stop free the book" is
                unruled. See OPEN.md item 10
    score       MAE/MFE percentages of entry. NO P&L - Joe 0917

**THE NUMBERS, 90 days of line cache, 2026-06-10 .. 2026-09-08:**

| | |
|---|---|
| sig bars | 1,863 |
| pass rule#1 | 1,045 |
| **trades** | **753** |
| net > 0 | 409 (54.3%) |
| stopped at the cap | 311 (41.3%) |
| MAE sum | 334.677 |
| net sum | +284.313 |
| **net per trade** | **+0.3776** |

**ENTRY IS THE sig BAR, which is the CEILING and not achievable.** `sweep_mae_cap.py` enters on the
bar the signal NAMES; o9-live cannot know that bar for a median 165 s. The emit-bar variant is a
separate axis and Joe has not ruled which one the strategy is — see `OPEN.md` item 11. Every number
in this table is the ceiling.

The cap is worth **+0.1464 -> +0.3776 per trade** against no cap - the largest single effect found
on 0929. It is the PEAK of a 0.05-step sweep from 0.05 to 4.00, and 0.55 to 0.95 is a plateau where
every value is within 0.04 per trade of the peak, so the choice is not knife-edge. Every cap tested
from 0.15 up beats no cap.

| cap % | trades | net > 0 | stopped | net per trade |
|---|---|---|---|---|
| 0.40 | 753 | 321 (42.6%) | 425 (56.4%) | +0.3037 |
| 0.60 | 753 | 382 (50.7%) | 350 (46.5%) | +0.3553 |
| **0.70** | **753** | **409 (54.3%)** | **311 (41.3%)** | **+0.3776** |
| 0.80 | 753 | 418 (55.5%) | 291 (38.6%) | +0.3689 |
| 0.90 | 753 | 426 (56.6%) | 266 (35.3%) | +0.3585 |
| 1.10 | 753 | 445 (59.1%) | 219 (29.1%) | +0.3655 |
| 2.20 | 753 | 464 (61.6%) | 102 (13.5%) | +0.2794 |
| no cap | 753 | 468 (62.2%) | 0 | +0.1464 |

`net > 0 %` and `net per trade` disagree across the whole ladder - the win count climbs
monotonically to 62.2% at no cap while the per-trade peaks at 0.70. A tighter cap turns would-be
winners into -cap losses but kills the big losers faster. **Rank on net per trade; Joe ruled 0.70
on that basis.**

Causality is unchanged and still holds: every module from `build_wsf_dtf_v3` down has been walked,
and the sig_utc chain was replayed in realtime on 0929 - 121 of 121 moments, zero revisions, median
165 s emission latency that is in the mech.

o9-live and fakeAPI **exist and run**, but on a different strategy. The bridge is the work.

**THE 0929 KNOB SWEEP IS VOID AND ITS NUMBERS ARE NOT IN THIS PACKAGE.** ~240 configs were swept
before the dr-flip-never-opens ruling, so the swept trade population was dominated by dr-flip OPENS
and a knob "gain" was the flip share moving, not the signal. Joe 0929-late: *"ok, the sweep is
definitely poisoned. let's go back to baseline"*.

**Do not act on `docs/sweeps/`, and do not quote it.** Not its knob values, not its rankings, not
its per-config counts. It is kept as the record of a wrong turn. The baseline this package hands
over is the banked configuration, not anything that sweep produced.

## Reproduce it before you trust it

```
python3 sweep_mae_cap.py          # 753 trades over 90 days, peak cap 0.70 at +0.3776/trade
python3 report_realtime_replay.py # the causality proof: 121 of 121, zero revisions

# build_wsf_trades.py no longer reproduces its own banked rows - trade_walk.walk carries both
# 0929-late rulings and the bank does not. See OPEN.md item 8 before running it.
```

Both must come out of the tape and the DB alone. A mismatch is a finding, not a nuisance — see
`RECON.md`.
