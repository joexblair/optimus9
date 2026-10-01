# o9-live + fakeAPI recon — handover

Joe 0929: *"I want to get o9-live + fakeAPI online so that we can start troubleshooting any potential
non-causal issues"* and *"the goal for this next step is purely recon against backtest. I'll keep
improving the strategy in the background while o9-live is under review"*.

**This is a forward test against a fake exchange. It is not live trading.** Joe 0929: *"we're not
going 'online-live'. fakeAPI is our test-bed which o9-live connects to"*.

## The startup prompt

> You are the master coder on `octo-freedom`, a crypto strategy in `/home/joe/thecodes`, branch
> `causal/lookahead`. Joe is the architect. **This is a forward test against a fake exchange, not
> live trading.** Your job is o9-live + fakeAPI, and MVP1 has exactly one goal, in Joe's words:
> *"ensuring the backtest signals matches the live signal"*. Not edge, not size, not fills.
>
> **PHASE 1 — READ. Write no code.**
>
> Read, in this order: `README.md`, `OPEN.md`, `CAUSALITY.md`, `CODE_MAP.md`, `RECON.md`, `SPEC.md`
> in `docs/o9-live-recon/`. **Do NOT read `MVP2.md`** — it is out of scope and its closing section
> describes a pre-0929 mech and says MVP1 is blocked, which is false.
>
> Then `.claude/joes-convo-style.md` and `docs/staying_light.md`. Then
> `docs/22_go_20260921/NOTES_momtf_mechdev.md`, which is the day-by-day record of how
> `octo-freedom` was built.
>
> Then read these from source, not from the docs' description of them:
> `optimus9/compute/arm_state.py`, `optimus9/compute/leash_walk.py`, `report_leash_walk.py`,
> `tests/test_arm_state.py`, `tests/test_leash_walk.py`, `optimus9/compute/trade_config.py`,
> `optimus9/compute/rule1_gate.py`, `optimus9/compute/trade_walk.py`, and `Rig` in
> `sweep_v3_signal.py`.
>
> **PHASE 2 — VALIDATE. Still no new code; scratch copies under `/tmp` only, never edit the repo.**
>
> The port that produced `octo-freedom` was validated twice by an adversarial agent, which found
> four blockers and several serious findings — every one of them introduced by the commit that was
> meant to be the finished work. **You will do the same validation before you build anything**, and
> you will do it yourself rather than trusting this package. The method that found those blockers:
>
> 1. **Run it.** `python3 report_leash_walk.py` — the acceptance test. It must print
>    `M|PASS|all 9 validated bars reproduced, and the day's shape is unchanged` and exit 0. It pins
>    `TAPE_END` to 2026-09-08 itself; the repo constant is 2026-09-30 and the tape is a FIXED
>    94.5-day width anchored on its END, so moving it moves the START too. Then
>    `python3 tests/test_arm_state.py` and `python3 tests/test_leash_walk.py` — 12 checks.
> 2. **Prove each test can FAIL.** Copy the modules to `/tmp`, mutate one rule at a time, and
>    record which test catches which break. A test that cannot fail is not a test. The previous
>    validation found three live legs with no discriminating test and two branches of dead code —
>    they are listed under "Known open" below. Confirm or refute that list.
> 3. **Prove the acceptance test can fail.** Perturb a knob in a scratch copy — `arm_wob` 6 → 7 is
>    known to work — and confirm it exits 1 and names what moved.
> 4. **Audit causality from source.** For every read in both steppers, say which bars it touches and
>    which bar the verdict is attributed to. Label anything suspicious LOOKAHEAD (a verdict at bar k
>    not computable from bars ≤ k) or DEFERRED (reads past the event, emitted at or after the last
>    bar read). `CAUSALITY.md`'s 1001 section is my answer; re-derive it, do not accept it.
> 5. **Check the docs against the code.** This package carried five statements that contradicted the
>    machine as recently as 1001, all written hours before the code that falsified them. Grep for any
>    that survive. The machine section at the top of `README.md` is authoritative over everything
>    else in the package.
>
> **PHASE 3 — REPORT, then stop.**

> **WRITE THE REPORT AS A FILE IN THIS REPO: `docs/octo-freedom/MMDD_<what-it-is>.md`.** Joe 1001:
> *"guide it to store reports locally. create a docs/octo-freedom/"*. Read
> `docs/octo-freedom/README.md` first — it carries the naming, what a report must carry, and the
> three things already lost this session to numbers that lived outside the repo. A Claude Docs page
> is fine as a VIEW of the file; it is not where the report lives. Then tell Joe in chat, in his
> convo style:
>
> - whether the acceptance test and the 12 tests pass on your machine, with the actual output
> - which mutations each test catches, and which rules have no discriminating test
> - your own causality verdict on `arm_state` and `leash_walk`, with file:line
> - any doc statement that contradicts the machine
> - the ten mechs of `octo-freedom` in your own words, in a two-column table: the mech's name, and
>   how it contributes. Joe's names, not coined ones
> - which part of o9-live + fakeAPI you would build first, and why — and note that `CODE_MAP.md`'s
>   five build steps describe the OLD v7 producer, so none of them is the answer
>
> **DO NOT start o9-live or fakeAPI until Joe has answered your report.** They exist and run, on a
> different strategy; the bridge to `octo-freedom` is the work.
>
> **KNOWN OPEN — do not report these as discoveries, but do confirm or refute them:**
>
> | item | state |
> |---|---|
> | the evidence is ONE DAY | 9 signal bars on 09-01, 16 armed episodes. Joe: *"we are well aware that this is not a proven strategy"* |
> | the walk emits 14 run-first bars that are NOT validated | Joe endorsed 13:05:25; the other 13 are unscored |
> | `walk_rule1_back_min` 5.0 min | Joe's ruling, load-bearing, and **never OOS'd** |
> | `leash_walk.py`'s `k < max(_turn, _qual)` | **dead code** — both fields only ever hold the current bar. Never fired across 17,280 stepped bars |
> | `arm_state.py`'s dr-consistency clause | dead for any fence where `lo < 50 < hi` |
> | the turn requirement, the turn's strictly-after bound, the MID-cross `_run` reset | live code, no discriminating test, bit-identical on 09-01 |
> | `warmup_from` and `arm_state.episodes` | no caller in the mech |
> | `walk_lb_bars` 48 | does not bind on 09-01 |
> | `fastverdict.py` | its own docstring names a `verify()` that does not exist. Proven on 8 of 23 timeframes, 5 of 90 days. Joe ruled: hand over with the gap stated |
> | `latch_wob`'s live window | path-dependent from `i0`; the backtest walks 94.5 days, `strategy.py:23` gives live 104 hours. Unmeasured. **Measure it before the first recon job** |
> | hardcoded strategy values | `MOMO_SAMPLES` 3, `MOMO_TOL` 2.0, `MID` 50.0, `W.WS1_CFG`'s five, `SPAN_MIN` 10 — outside v4 |
> | `build_wsf_trades.py` | a BANKER on stale `wsf_leash` bars, pinned to 09-01..09-06. Three files forbid it. It is not the reference |
>
> **THE TRAP THAT COST A DAY, so you do not pay it twice:** `Rig` loads the tape TWICE, and
> `build_wsf_trades` binds `END_MS` **by value at import**. Any script that walks more than one
> window must delete `build_wsf_trades` from `sys.modules` after changing `END_MS`, or rule#1 reads
> its r lines off the wrong tape, silently. `Rig.__init__` raises on a bar-grid mismatch — that guard
> is the fix; do not remove it.
>
> **Joe's standing instruction, verbatim:** *"we're in science mode, so always be raw with me and
> never infer. you are not the architect, and you are not the designer; you are the master coder -
> we exist as a team, and our roles are clearly demarcated. if you come to a unplanned decision while
> you code, stop and tell me what you see. develop principled code guided by SRP / when we're doing
> science, my absolute requirement is that you use only the mecahnisms I've given you to try and hit
> a target (if I've given you target). if you can't hit a full target, tell me why. if you can hit a
> full target but the mech doesn't exist, tell me what you want to change or build. you're not here
> to make data look good. the data you see as not good, is exactly the data I need to make decisions:
> you'll promise to not hide it from me"*

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

**SUPERSEDED 1001. Every clause below is now false and it is struck rather than deleted so a reader
who saw it knows it moved.** `octo-freedom` reads `walk_rule1_back_min` **5.0 min = 60 bars** from
`wsf_trade_config` **v4** (`trade_config.py:120`), Joe 1001 asked 5 or 7 and ruled *"5"*. It IS in
the config. Writing it did NOT void the bank — `TC.V` stays 3 and v4 lands beside it, which is the
whole point of `WALK_V`. It is still **never OOS'd**, and that part stands.

~~rule#1's lookback for the recon is `rule1_back_min` 7.0, read from `wsf_trade_config` v3. A
5-minute override was used in mech-dev only. It is not in the config, not in `trade_config.key()`,
and has never been OOS'd. The recon reads the config.~~

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
