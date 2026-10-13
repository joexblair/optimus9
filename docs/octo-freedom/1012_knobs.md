# 1012 — EVERY KNOB IN THE CHAIN

Generated against `_chain10.py` and `_gcgate.py` on 1012. The DEFAULT column is what the code does
with no env var set. Where a knob belongs to a mech, the doc that specs it is named.

## THE WALK — arming, the rider, the baton

| knob | default | what it is | spec |
|---|---|---|---|
| `W_ARM` | mage | `cp` makes the ws1-cp the walk's qualifier instead of ws{`W_ARM_TF`}Mage | 1011 |
| `W_ARM_TF` | 2 | which Mage line the `mage` arm reads | 1009 |
| `W_CP` | 0 | 1 lets a COMPLETING ws1-cp reset the rider to ws1 mid-walk | 1011 |
| `W_CP_DWELL` | 4 | the ws1-cp hold in bars, 20 s. Consecutive; the cp is stamped at the LAST bar of the hold. 1 reproduces the pre-dwell build | 1011 |
| `W_CP_MODE` | both | which ws1-cp modes arm. `1` = mode 1 only (ws1r AND ws1Mage both oob), `2` = mode 2 only (the divergence), `both` = either | 1012 |
| `W_CP_XWOB` | 2 | mode 2's ws1x/ws1Mage cross hold in bars, 10 s. Stamped at the last bar of the hold | 1012 |
| `W_KICK` | off | the walk's FIRST rider. `high` = highest oob line at or under the loop TF, `low` = lowest, `off` = start on ws1 with no oob test | 1009 |
| `W_BATON` | oob | what a line must show to take the baton. `oob` = r out of bounds. `momentum` = mom-true, momo OR curl. `rpred` = `predict_breach`. `either` = momentum OR rpred | 1009 |
| `W_PASS` | oob | the 1007 variant's own pass test. `oob` or `stalled` | 1007 |
| `W_STALL_UP` | 0 | 1 advances the rider +1 TF on its own stall, no qualifying test | 1009 |
| `W_MAXTF` | 30 | the highest cached TF | — |

## LINEAGE'S CEILING AND EXHAUSTION

| knob | default | what it is | spec |
|---|---|---|---|
| `W_EXH_WHO` | holders | `holders` tests exhaustion on EVERY line that has held the baton, not just the current rider. Scanned AFTER the baton, so a hop advances instead of the leg exhausting | 1012 |
| `W_LOOP_EXH` | on_stall | when the loop's exhaustion exit goes live | 1011 |
| `W_EXH_WIN` | dwell | the window the ws12x cross must land inside. `dwell` = the whole oob gate dwell, 6.1 min (Joe 1009's revision). `seam` = the 1/4 seam, 3.0 min | 1009 |
| `W_EXH_FRAC` | 0.25 | the seam fraction, only read when `W_EXH_WIN=seam` | 1009 |

## W_LOOP

| knob | default | what it is | spec |
|---|---|---|---|
| `W_LOOP_TF` | '' | the loop TF, comma list. Also sets lineage's ceiling to loopTF + lin_hop | 1011 |
| `W_LOOP_END` | cp | `cp` = the loop ends at the next ws1-cp. `oob` = the pre-1011 reset on the oob bar | 1011 |
| `W_LOOP_LB` | 48 | the lookback window in bars, 4 min. STUBBED — detected and traced only | 1011 |

## THE gc DEFERRAL

| knob | default | what it is | spec |
|---|---|---|---|
| `W_GC` | 1 | the gc deferral of exhaustion. Baked 1011 | 1011 |
| `W_GC_HOLD` | wait | `wait` reads only the hold's end during a hold. `walk` lets the walk carry on with the exit merely suppressed | 1011 |
| `W_GC_STEP` | 2 | the trajectory sampling step in bars, 10 s (`_gcgate.py`) | 1011 |
| `W_GC_SPAN` | 72 | the trajectory span in bars, 6 min (`_gcgate.py`) | 1011 |
| `W_GC_GAP` | 24 | the gap walk in bars, 2 min (`_gcgate.py`) | 1011 |
| `W_GC_FLIP` | 12 | the blip rule — a trajectory sign flip must survive 12 bars, 1 min (`_gcgate.py`) | 1011 |

## THE >ws12 oob MECH

| knob | default | what it is | spec |
|---|---|---|---|
| `W_NO_GT12` | 0 | 1 turns the whole >ws12r oob mech OFF. `W_DGATE=off` does NOT — it makes the handover always fire | 1009 |
| `W_DGATE` | off | the direction gate on the >ws12 handover | 1009 |
| `W_VOTE_MIN` | 40 | the vote-40 threshold | 1009 |
| `W_VOTE_TIE` | c3 | what breaks a vote tie. `c3` or `travel` | 1009 |
| `W_C3_LO` | 5 | the c3 low bound | 1009 |
| `W_C3_HI` | 11 | the c3 high bound | 1009 |
| `W_TRAJ_BLOCK` | 60 | the trajectory sampler's block, bars. Inert while `W_DGATE=off` | 1009 |
| `W_TRAJ_TAIL` | 2 | the sampler's tail, bars. Inert while `W_DGATE=off` | 1009 |
| `W_TRAJ_LOOK` | 24 | the sampler's lookback, bars. Inert while `W_DGATE=off` | 1009 |
| `W_TRAJ_KIND` | close | what the sampler reads. `close` or `extreme`. Inert while `W_DGATE=off` | 1009 |
| `W_NOX` | 1 | x-cross as an exit is DELETED. Joe 1011 dropped it | 1011 |
| `W_SQX` | 0 | the squashed-cross variant | 1008 |

## REPORTING ONLY — no branch reads these

| knob | default | what it is |
|---|---|---|
| `W_TRACE_LIN` | 0 | what lineage asked on each bar and the answer |
| `W_TRACE_HOLD` | 0 | every baton holder's stall rising edges, with its own r, fence tag, reach, and whether it is the rider |
| `W_TRACE_DGATE` | 0 | the direction gate's reading |
| `W_TRACE_NOX` | 0 | the walk x-crosses that `W_NOX` suppressed |

## THE RUN WINDOW — `main()` only, not `run_leg`

| knob | default | what it is |
|---|---|---|
| `W_DAY` | 2026-09-25 | the day `main()` starts on |
| `W_START` | 08:10:00 | the bar `main()` starts on |
| `W_SIDE` | 1 | the first trade's side for `main()`. +1 a SHORT, -1 a LONG |
| `W_LEG0` | 7 | the leg counter's start, for labelling only |

`_1011v2.py` takes `V_DAY`, `V_OPEN`, `V_END` and `V_W` instead, and reads the trade's side from
global dr at the open bar. `V_SIDE` forces that side when global dr reads the other way; the side is
still set once, at the open.

## THE MOMENTUM EXTENSION, `_extmom.py`, 1013

| knob | default | what it does |
|---|---|---|
| `W_EXT_N` | 4 | the n-of-7 threshold. Joe: *"if n >=4 then ride"* |
| `W_EXT_TF` | 10 | `mom_cont_tf`, in minutes |
| `W_EXT_LINE` | dws | the ride line's family. `dws` -> dws10r, `ws` -> ws10r |
| `W_EXT_EXIT` | stall | `stall` the ride ends at the first ride-line stall · `n` it ends when n falls under `W_EXT_N` · `first` whichever comes first |
| `W_EXT_FENCE` | 0 | the stall's ex-fence gate. OFF per Joe: *"the ws{mom-cont-tf}r stall can fire infence"*. 1 only to re-measure the difference |

`W_EXT_EXIT`'s three values are three different numbers on the two qualifying closes of 07-17/07-18
— `stall` +7.1028%, `n` +7.1898%, `first` +7.0684%, against the standing +6.4370%. The default is
the proposal Joe banked. He has not ruled between them. See `1013_mom_extend.md`.

## NOT A KNOB

The target board. Joe 1012: *"it can only be set once at the open of the trade"*. There is no env
var and no fork — `W_DR` was deleted. See `1012_target_board.md`.
