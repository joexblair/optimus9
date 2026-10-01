# o9-live + fakeAPI recon — handover

Joe 0929: *"I want to get o9-live + fakeAPI online so that we can start troubleshooting any potential
non-causal issues"* and *"the goal for this next step is purely recon against backtest. I'll keep
improving the strategy in the background while o9-live is under review"*.

**This is a forward test against a fake exchange. It is not live trading.** Joe 0929: *"we're not
going 'online-live'. fakeAPI is our test-bed which o9-live connects to"*.

## The startup prompt

> Read `README.md`, `SPEC.md`, `CODE_MAP.md`, `CAUSALITY.md`, `RECON.md` and `OPEN.md` in
> `docs/o9-live-recon/` — **not `MVP2.md`, it is out of scope and its closing section is stale** —
> then `.claude/joes-convo-style.md` and `docs/staying_light.md`.
>
> Before running anything: set `build_ws_lines.TAPE_END` back to **2026-09-08** per the precondition
> row below, then run the two commands under "Reproduce it before you trust it" and tell me whether
> they match the stated numbers.
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

**`MVP2.md` IS NOT PART OF THIS HANDOVER — DO NOT READ IT.** Joe 1001: *"keep MVP2 out of the
handover - it's for our future dev, not for o9-live (yet)"*. It is still on disk, and its closing
section describes the **pre-0929** scoring-cap mech and says MVP1 is blocked on a question
`OPEN.md`'s Ruled table has since closed. Reading it will mislead you.

## The one-line state

### 1001 — THE MACHINE IS `octo-freedom`. READ THIS BEFORE ANYTHING ELSE IN THIS PACKAGE

**THE MACHINE HAS A NAME AND IT IS JOE'S.** 1001: *"octo-freedom / it's now, it's the goal, and it's
got a little bit of chinese numerology sneaked in the back pocket"*. Use it. The module names
(`leash_walk`, `arm_state`) and the config key (`wtc_v4_v7_...`) predate the name and still carry
the old wording — the key is not renamed because changing it moves what every banked row is written
under, which is Joe's call, not a tidy-up.

**`octo-freedom` EMITS `WALK FIRES FROM`, FROM `optimus9/compute/leash_walk.py`. IT IS NOT THE v7
`wsl_sig_utc` CHAIN ANY MORE.** Joe 1001: *"there is no surviving mech that relies on `brk`, because
our verified strategy uses `WALK FIRES FROM` as our one and only signal"* and *"the Joe has validated
every row in this report, and has derived profit only from the `WALK FIRES FROM` timestamps,
therefore it is the only outcome that is stamped as ready for live trading"*.

| the machine | where |
|---|---|
| the arm, as carried state | `optimus9/compute/arm_state.py` |
| the walk that emits the signal | `optimus9/compute/leash_walk.py` |
| the knobs | `wsf_trade_config` **v4**, key `wtc_v4_v7_rule1_gateopen_mae0.70` |
| the acceptance test and the recon's reference | `report_leash_walk.py` |
| the exits and the stop | `optimus9/compute/trade_walk.py`, `mae_cap` 0.70 — unchanged |
| the gate | `rule1_gate.gate` at `walk_rule1_back_min` **5.0 min = 60 bars** — NOT the 7.0 in v3 |

    python3 report_leash_walk.py        # rebuilds Joe's 9 validated 09-01 bars and ASSERTS them

**WHAT IS OUT OF THE MECH, BY JOE'S 1001 RULING:** `coil_moment.release`, `coil_moment.moments`,
`coil_exit.resolve`, `i1`, `brk`, all four `actionable_*` fields, all four `via` branches. The walk
references none of them. The entry-bar lookahead this package used to carry was entirely in the GAP
and LOOKBACK branches, which no longer exist — **the signal bar is now decided at its own bar.**

**THE EVIDENCE IS ONE DAY.** 9 signal bars, 16 armed episodes, 09-01. Joe 1001, agreed explicitly:
*"we are well aware that this is not a proven strategy"*. MVP1 matches signals, not edge.

**EVERYTHING BELOW ABOUT THE v7 CHAIN IS THE HISTORICAL RECORD, NOT THE MACHINE.** Its numbers —
1,863 / 1,045 / 894 / +0.3911 — were measured and they stand as measured. They are not what o9-live
runs.

### 1001 — three further things that changed after this package was written on 0929

| | |
|---|---|
| **o9-live RUNS ON LIVE TAPE. NO CACHES** | Joe 1001: *"I'm expecting o9-live + fakeAPI to run on live tape - no caches"*. Already true, and verified: **0** references to `rpl_cache` or `.npz` anywhere in `optimus9/live/*.py` or `ops/run_o9live.py`. The line cache is a BACKTEST device only. Everything in the next row is therefore about reproducing the BACKTEST, which is the thing MVP1 matches the live signal against |
| **THE TAPE IS A PRECONDITION OF BOTH REPRODUCE COMMANDS, AND THE REPO NO LONGER DEFAULTS TO IT** | **The tape is a FIXED 94.5-day width anchored on its END** — `HOURS` 40 + 2×`WARMUP` 1114 = 2,268 h — so moving `TAPE_END` forward moves the START forward too. Not a no-op, and the right edge is not the problem: |

| `TAPE_END` | the tape it loads |
|---|---|
| **2026-09-08** — what every number here was measured on | 2026-06-05 12:00 → 2026-09-08 00:00 |
| **2026-09-30** — what the repo holds now, commit `b6ce18c` | **2026-06-27 12:00** → 2026-09-30 00:00 |

The backtest window is `measure_live_stop.py:29`, `FROM_MS, TO_MS = 2026-06-10 .. 2026-09-08`. On the
09-30 tape **06-10 is 17.5 days before the tape's first bar**, so `np.searchsorted` clamps `A` to 0
and the walk silently starts at 06-27 12:00 — **72.5 days, not 90**. `sweep_live_stop.py:75` prints
its day count from the `FROM_MS`/`TO_MS` constants rather than from the tape, so it still says "90".
**Set `TAPE_END` back to 2026-09-08 before running either command.** The 09-08 cache is still on disk.
| **a defect in the OOS path was found and fixed on 0930** | `Rig` loads two tapes and discards one's timestamps, and `build_wsf_trades` binds `END_MS` **by value** at import — so a process that walked more than one window read rule#1's `r` lines off the wrong tape. `oos_confirm_lag.py` and `score_5day_windows.py` both did it. Fixed, guarded with a hard `RuntimeError` on a tape mismatch, committed. IS rule#1 open is **unchanged**; both OOS windows' rule#1 open roughly **doubled**; IS reproduces **+0.3911 exactly**. See `CAUSALITY.md`. |
| **`confirm_lag_s` 165 is REJECTED; 180 stands** | 165 loses both OOS windows, **−0.0058** and **−0.0239** per trade. The 180 s throughout this package is the right number. |
| ~~the recon fires the BANKED v7 CHAIN~~ **SUPERSEDED 1001 — SEE THE MACHINE SECTION AT THE TOP** | Joe ruled this EARLIER on 1001, on the premise *"it has to be the banked v7 chain - the new mech's bars can't be reproduced"*. **The port falsified that premise**: the walk is `optimus9/compute/leash_walk.py` and `report_leash_walk.py` reproduces its bars from repo code. He then ruled the walk IS the machine. His *"the offline o9-live can fire on non-armed signals"* had the v7 chain as its subject and has no referent in the walk, which requires an arm by construction. **CLOSED 1001 — Joe: *"I'm dropping my request for extra non-armed signals"*. The walk emits only on an armed, dr-matched bar.** |

**THE OOS PERCENTAGES ARE NOT PUBLISHED WITH THEIR COUNTS, SO THEY ARE NOT QUOTED HERE.**
`oos_confirm_lag.py:126-146` prints `sig bars` and `rule#1 open` as integers and never a
percentage. Re-deriving them needs `TAPE_END` back at 2026-09-08 — see the row above. Until that run
is done, the direction is the finding and the rates are not.

**CORRECTED 1001 — the paragraph below was written BEFORE the port and every claim in it is now
false. The walk IS in the repo, its numbers ARE checkable, and its rule#1 lookback IS in the config
(`wsf_trade_config` v4, `walk_rule1_back_min` 5.0). Kept only so a reader who saw the old text knows
it moved. THE MACHINE SECTION AT THE TOP OF THIS FILE IS AUTHORITATIVE.**

~~A NEWER SIGNAL MECH IS IN DEVELOPMENT. IT IS NOT PART OF THIS HANDOVER AND IT IS NOT A RECON
GATE.~~ It is an arm / flat-run-race / `ws1mage-rev` chain, walked over **09-01 only**. Its DB
builders ARE committed — `docs/22_go_20260921/build_ws5mage_sig_backing.py`,
`update_ws5mage_sig_backing_latch.py`, `build_all_wsf_flatrun_grid.py` — but the **walk** scripts
that produced its reported numbers live in a job-scoped scratch directory that will be deleted, so
those numbers are a written record, not a checkable result. The record is
`docs/22_go_20260921/NOTES_momtf_mechdev.md`.

**rule#1's lookback for the recon is `rule1_back_min` 7.0, read from `wsf_trade_config` v3.** A
5-minute override was used in mech-dev only. It is not in the config, not in `trade_config.key()`,
and has **never been OOS'd**. The recon reads the config.

### 0929-late

**THE STRATEGY CHANGED SUBSTANTIALLY ON 0929-late. Everything below supersedes the older numbers
still present in this package.** Three rulings from Joe and one defect he caught:

| | |
|---|---|
| a sig_utc closes ONLY on an opposing dr | a same-dr sig_utc is INERT |
| the dr-flip backstop CLOSES but never OPENS | the book goes flat instead |
| MAE is capped at **0.70%** and the cap is a STOP | `MFE-MAE` prints `-0.70` when hit |

**ANYTHING MEASURED WITHOUT THE CAP IS A DIFFERENT MECH** and is not in this package. Joe 0929-late:
*"you should be handing over only the mech that the MAE cap was applied to"*.

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
    walk        trade_walk.walk - THREE live exits racing each other, first to fire wins:
                an opposing-dr sig_utc, the dr-flip backstop, and the stop. The flip never opens
    entry       the sig bar - the bar the signal NAMES
    stop        MAE cap 0.70% of entry, IN THE WALK. Joe specified 0.9 on 0929, ruled 0.70 on the
                first ladder, then re-ruled it on the re-walked ladder: "retain 0.7% as the stop"
    key         wtc_v3_v7_rule1_gateopen_mae0.70 - the cap is IN the key, Joe 0929-late
    score       MAE/MFE percentages of entry. NO P&L - Joe 0917

**THE NUMBERS, 90 days of line cache, 2026-06-10 .. 2026-09-08:**

| | |
|---|---|
| sig bars | 1,863 |
| pass rule#1 | 1,045 |
| **trades** | **894** |
| net > 0 | 479 (53.6%) |
| stopped at the cap | 381 (42.6%) |
| MAE sum | 403.022 |
| net sum | +349.638 |
| **net per trade** | **+0.3911** |

| closed by | n | of 894 |
|---|---|---|
| stop | 381 | 42.6% |
| dr-flip | 362 | 40.5% |
| sig_utc | 151 | 16.9% |

**Entry is the sig bar — the bar the signal NAMES.** That is the spec and it is what these numbers
measure.

**The stop RACES the other two exits; it does not replace them.** No trade re-scores because of it -
a stopped trade is -0.70 either way. What moves is its CLOSE BAR, and therefore when the book frees
up. The book used to be held a median 98 minutes past the stop bar, with 216 ungated sig_utc bars
sitting inside those windows, INERT because a position was open. Freeing them is worth 753 -> 894
trades and +0.3776 -> +0.3911 per trade.

**The cap was re-ruled against a re-walked ladder.** The first ladder scored one fixed trade set of
753 at every rung; with the stop live every rung has its own trade population, so all 80 rungs were
re-walked from the tape. Joe: *"retain 0.7% as the stop"*. `SPEC.md` carries all 81 rungs.

- net per trade peaks at cap 1.25, +0.3928 on 843 trades. **0.70 sits 0.4% below it.**
- net sum peaks at cap **0.70**, +349.638. It is the best rung on that measure.
- the band 0.70 to 1.30 spreads only 0.012 per trade. There is no knee in it.
- `net > 0 %` is **NOT monotonic** — 13 decreasing steps of 78, and its maximum is **62.5%** at caps
  2.60, 3.40 and 3.45, not 62.2% at no-stop. Ranking on win% picks cap 2.60 at **+0.2941** per
  trade, which costs **0.097** against the 0.70 rung. Corrected 1001; see `SPEC.md`.

Causality is unchanged and still holds: every module from `build_wsf_dtf_v3` down has been walked,
and the sig_utc chain was replayed in realtime on 0929 - 121 of 121 moments, zero revisions, median
165 s emission latency that is in the mech.

o9-live and fakeAPI **exist and run**, but on a different strategy. The bridge is the work.

**`docs/sweeps/` measures a mech without the MAE cap. It is not this mech. Do not use it.** Joe
0929-late: *"ok, the sweep is definitely poisoned. let's go back to baseline"* and *"you should be
handing over only the mech that the MAE cap was applied to"*.

## Reproduce it before you trust it

```
python3 sweep_live_stop.py        # the cap ladder, 81 rungs. The 0.70 rung is 894 / +0.3911
python3 report_realtime_replay.py # the causality proof: 121 of 121, zero revisions
```

**`build_wsf_trades.py` is NOT in that list.** It reads its signal bars from `wsf_leash`, and those
121 rows still hold the pre-`sig_conf` cross bars - 15 s early - and cover 09-01..09-06 only. Joe
ruled the fix: re-bank in place. Until then the banker is on stale bars and the sweep is not.
See `SPEC.md`, *Banking it*.

Both must come out of the tape and the DB alone. A mismatch is a finding, not a nuisance — see
`RECON.md`.
