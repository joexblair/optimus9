# 1012 — THE TRADE'S SIDE SETS THE TARGET BOARD

Joe 1012, ruling three things in his own words:

> the trade's direction/"side" is what sets the target: SHORT trades use a low board target, LONG
> trades use a high board target

> always the end the trade is heading to

> it can only be set once at the open of the trade

> this notion is more powerful than it might seem on the surface

## THE RULE

| the trade | its side | the board it hunts |
|---|---|---|
| SHORT | `dr +1` (the banked `dr +1 = SHORT`) | LOW |
| LONG | `dr -1` | HIGH |

- the board is the end the trade is **heading to**, never the end it came from.
- it is resolved **once**, on the trade's open bar, and never read again.
- in code: `run_leg(k0, trade_side)` and `d = -trade_side` on entry. `d` inside the walk is the
  TARGET BOARD, not the trade's side.

## WHY IT IS ONE CHANGE AND NOT SEVEN

Every test in the walk already takes `d` as "which end of the board am I working on". Setting `d`
to the board at the open is the whole fix — none of these needed its own edit:

| the test | what it asks |
|---|---|
| ws1-cp | are ws1r and ws1Mage both oob on the board |
| the jumpstart | which lines are oob on the board right now |
| the baton | is the next line showing momentum toward the board |
| the stall | has this line stopped making new extremes on the board |
| exhaustion | are the lines above the rider all short of the board |
| the loop end | has the walk reached ws{`W_LOOP_TF`}r oob on the board |
| the gc gates | is g30r on the wrong side of 50, is g15r travelling toward the board |

## WHAT IT REPLACES

`W_DR=global` read `SC.DRv` on EVERY bar and reassigned `d` when it moved. It is DELETED — Joe:
the side *"can only be set once at the open of the trade"*.

`SC.DRv` moved 3 times inside the 07-18 02:33 trade:

| ts | SC.DRv from | to |
|---|---|---|
| 02:41:45 | +1 | -1 |
| 03:11:35 | -1 | +1 |
| 04:08:45 | +1 | -1 |

Each move swapped the board, so the walk hunted HIGH ws1-cps at 03:41 on a SHORT. Joe: *"it was
looking up when it should always have been looking down"*.

THE INVARIANT, not a docstring: `assert d == _board0` at the top of every bar of the walk. The bug
this replaces was a mid-walk reassignment of `d` and it was invisible in the rows it produced.

## WHAT MOVED, 07-18 02:33 SHORT, W_CP_DWELL 4

| what | before | after |
|---|---|---|
| legs opened 03:41:00-03:41:50 | 4, each dead in 15-20 s | 0 — they were high-board arms |
| the walk's first arm | 03:41:05 | 04:11:40 |
| unarmed from the open | — | 02:33:00 to 04:11:40, 98.7 min |
| W_LOOP 1 COMPLETE | 05:42:00 | 05:42:15 |
| leg 1 exit | MAE breach 05:54:30 | MAE breach 2.5036% at 05:55:10 |

The 05:42 landing Joe banked on 1011 HOLDS. The 15 s is the ws1-cp dwell stamp, not the board.

## STILL OPEN, NOT DECIDED

What a leg does when the ws1-cp condition is ALREADY standing on the board at the trade's open. The
dwell counter starts at zero on the open bar, so a condition true for minutes still stamps a cp
`W_CP_DWELL` bars in with nothing having crossed. Raised on the 07-18 03:41 legs; Joe's ruling is
outstanding. The two readings:

| reading | effect |
|---|---|
| no cp — wait for the condition to actually arrive on the board | a leg opening inside a standing condition never arms on it |
| a standing condition at the open counts | current behaviour, delayed by the dwell |

## THE ADVERSE SIGN, RULED 1012

Joe on the MAE stop: *"this mech is incorrect, likely to be a casuality of wrong side. I'm basing
it your 2.5% being almost exactly the profit we've claimed in this SHORT trade"*.

He is right. On the 07-18 02:33 SHORT the stop fired at 05:55:10 on a 2.5036% PRICE FALL, which is
that short's PROFIT, not its drawdown.

| the trade | adverse is | sgn |
|---|---|---|
| `trade_side +1` = SHORT | price RISING | -1 |
| `trade_side -1` = LONG | price FALLING | +1 |

So `sgn = -trade_side`, and `adv = -((px - p0) / p0 * 100 * sgn)` is the move AGAINST the trade.
The same sgn signs the realised number. The stop level itself, `mae_stop_pct` 2.50%, is unchanged -
Joe diagnosed the SIGN, not the level.

## THE g15r `LINEAGE FINISHER` COMPLETES THE WALK; IT IS NOT AN EXIT, 1012

Two rulings, one test. Joe:

> both g15r and g15Mage are needed to complete the walk

> the only banked back stop is dr-flip. I asked you earlier to remove g15 as an exit option. now I
> need you to delete it from the spec completely

| the g15 pair arrives | 1011 | now |
|---|---|---|
| oob on the TARGET BOARD | ends the hold, walk carries on | SAME - this is "completes the walk" |
| oob AGAINST the board | closed the leg at the opposing g15 bar | DELETED. Nothing happens; the hold stays open |

Nothing in the g15 pair can close a leg. The only banked backstop is dr-flip, which is not wired
yet - see `1011_gc_defer.md` step 4 for the one unspecified point.

I had deleted BOTH halves on the first pass, which took the walk-completion test with the exit.
Restored.

## THE BANKED WALK — 07-18 02:33 SHORT, Joe 1012: *"that walk is good - bank"*

RUN: `_1011v2.py`, `V_DAY=2026-07-18 V_OPEN=02:33:00 V_END=08:00:00`, tape 1,632,960 bars,
`LG_TAPE_END=2026-10-05`. 111 rows. Output `v2_0233_v3.out`.

KNOBS: `W_NO_GT12=1 W_STALL_UP=1 W_LOOP_EXH=on_stall W_CP=1 W_ARM=cp W_KICK=high W_LOOP_TF=10
W_LOOP_END=cp W_BATON=momentum W_CP_DWELL=4 W_TRACE_LIN=1 W_TRACE_HOLD=1`.

| ts | event |
|---|---|
| 02:33:00 | OPEN — dr +1, a SHORT, hunts the LOW board |
| 04:11:40 | ws1-cp 1 ARMS and BEGINS W_LOOP 1 — ws1r 11.59, ws1Mage 8.95, held 4 bars from 04:11:25 |
| 04:11:40 | JUMPSTART — rider ws3, r 11.46 |
| 04:14:30 | EXHAUSTED on ws3, a holder; the rider was ws5 — ws4 18.57, ws5 43.12 both in the ex-fence |
| 04:14:30 | gc DEFERS IT — g30r 76.76 over 50; g15r falling from 88.14, diff -34.00 |
| 04:17:45 | g15r LINEAGE FINISHER — g15r 9.58, g15Mage -21.60; the hold ran 3.2 min |
| 04:50:00 | W_LOOP 1 END ARMED — ws10r 10.10 oob |
| 05:00:00 | CEILING ws12 -> ws23, ws12r 8.49 |
| 05:34:35 | ws12 STALLED; W_LOOP 1 defers acting on it |
| 05:36:05 | EXHAUSTED on ws11, a holder; the rider was ws12 — ws12 19.65 in the ex-fence |
| 05:36:05 | gc DEFERS IT — g30r 50.22 over 50; g15r falling from 69.01, diff -24.07 |
| 05:38:30 | g15r LINEAGE FINISHER — g15r 14.44, g15Mage 0.19; the hold ran 2.4 min |
| 05:42:15 | W_LOOP 1 COMPLETE at this ws1-cp — began 04:11:40, 90.6 min |
| 05:42:15 | ws1-cp 2 completes it — the rider resets to ws1 from ws12 |
| 05:48:05 | EXHAUSTED on ws11, a holder; the rider was ws3 — ws12 20.50 in the ex-fence |
| 05:48:05 | gc DEFERS IT — g30r 81.97 over 50; g15r falling from 88.07, diff -41.90 |
| 06:18:10 | g15 arrived AGAINST the board — g15r 93.29, g15Mage 86.32. Does NOT close the leg; the hold stays open |
| 06:59:40 | g15r LINEAGE FINISHER — g15r 13.40, g15Mage -3.39; the hold ran 71.6 min |
| 08:00:00 | WINDOW ENDS — the leg is still open. Its exit is 09:09:00, loop exhaustion |

Joe called the 06:59 arrival before it was measured: *"a downward leg that starts at 05:48:05 and
ends at ~06:59 when g15Mage+r are TARGET-SIDE oob"*. It landed at 06:59:40.

WHAT THE 1012 FIXES MOVED, against the same window run before them:

| what | before | after |
|---|---|---|
| legs opened 03:41:00-03:41:50 | 4, each dead in 15-20 s | 0 - they were high-board arms |
| the walk's first arm | 03:41:05 | 04:11:40 |
| the 02:43:25 one-bar ws1-cp | armed a leg | dropped by the 4-bar dwell |
| W_LOOP 1 COMPLETE | 05:42:00 | 05:42:15 |
| the MAE stop | fired 05:55:10 on the SHORT's own profit | does not fire |
| the 05:48:05 hold | unresolved at the leg's death | ends 06:59:40 on the g15r lineage finisher |
| leg 1's exit | MAE breach 05:54:30 | 09:09:00, loop exhaustion |

## THE BANKED WALK IS NOT THE CODE'S DEFAULT — flagged, not changed

7 of the knobs above differ from the code's defaults, so the banked walk needs them set every run:

| knob | code default | the banked walk |
|---|---|---|
| `W_NO_GT12` | 0 | 1 |
| `W_STALL_UP` | 0 | 1 |
| `W_CP` | 0 | 1 |
| `W_ARM` | mage | cp |
| `W_KICK` | off | high |
| `W_LOOP_TF` | '' | 10 |
| `W_BATON` | oob | momentum |

`W_KICK` is the sharpest case: Joe ruled *"W_KICK off"* on 1010 and *"W_KICK ON: high"* on 1011, and
the default still carries the 1010 ruling. Baking these as defaults would silently change every
other script that imports `_chain10`, so it is Joe's call, not mine.

## ws1-cp MODE 2 — THE DIVERGENCE MODE. BAKED 1012

Joe: *"we need mode 2 baked in so that jumpstart can fire on the 14:33 ws1-cp"*.

THE TRIGGER, his words: *"to set the anchor and initiate the divergence test, use ws1x crossing
ws1Mage while ws1Mage is oob (crossing under for a LONG trade/high oob, crossing over for a SHORT
trade/low oob)"*, and his 1012 sidenote *"every ws1Mage oob + ws1x-cross-Mage, wob 2"*.

THE BOARD ANCHORS THE CROSS DIRECTION, not the trade label. He pairs them himself:

| board | ws1x crosses | ws1Mage must be |
|---|---|---|
| HIGH (a LONG) | UNDER ws1Mage | high oob |
| LOW (a SHORT) | OVER ws1Mage | low oob |

THE STAMP is cross + `W_CP_XWOB` - 1, the first bar the hold is knowable.
THE ANCHOR is that stamp bar. `jig.anchor_floater(ws1r, RAW close, board, k)` runs the four steps,
and the cp needs step 4 to FIRE on the board's own sign - his *"bullish at dr -1 / bearish at
dr +1"*. An anchor that does not fire is not a cp.

STEP 2 IS THE 50 RULE, agreed by Joe 1012, and he corrected how to describe it: *"the 50 rule (what
I ran, the producer's default)" -agreed. honestly: its not a default, it's lore"*. The 0921 dwell
rule is IGNORED for this caller - *"the dwell rule, your 0921 spec -ignore"*.

| knob | default | what it is |
|---|---|---|
| `W_CP_MODE` | both | `1` mode 1 only, `2` mode 2 only, `both` either arms |
| `W_CP_XWOB` | 2 | the ws1x/ws1Mage cross hold in bars, 10 s |

WHAT IT PROVED, 07-17 14:10:45 SHORT: the walk armed at **14:33:05** on mode 2, the jumpstart took
ws3 at r 2.14 on that same bar, and the next exhaustion was **14:38:30**. Mode 1 would not have
armed until 16:42:15 - 129.2 min later.

THE 14:33:05 CP, in full:

| part | value |
|---|---|
| ws1x crossed OVER ws1Mage at | 14:33:00 |
| ws1Mage at the cross | 8.00, low oob |
| anchor | 14:33:05, ws1r 32.87, close 0.133080 |
| pivot | 14:32:15, ws1r 50.77 |
| floater | 14:25:55, ws1r 5.62, close 0.133470 |
| d_osc | +27.25 |
| d_px | -0.000390 |
| fired | -1, the low board's sign |

WHAT IT MOVED on the banked 02:33 walk: the arm 04:11:40 -> 04:11:00 and W_LOOP 1's end
05:42:15 -> 05:12:05. The three gc deferrals, their three finishers and the leg's exit are all
unchanged. Joe 1012: *"the lineage finsihers are really all I'm interested in - how the walk gets
there is organic"*, so the loop's end moving is accepted.

The cp that took 05:42 off the loop's end was mode 2 at 05:12:05 with `d_osc` **+1.62** - the
weakest divergence in the window. There is no size requirement on the comparison. Recorded, not
acted on.

## "DOUBLE DIPPING" — BUILT AND DELETED, 1012

Joe asked *"what happens if we restart the lineage walk at the `lineage finsiher` g15r event? do we
get to walk more ground, find an exhaustion event ... and feed the walk back into the lineage
finisher for another microloop?"*, ruled *"rider to ws1, holder list clears. build it"*, saw the
result and dropped it: *"ok, drop the 'double dipping' idea. I'm too attached to 06:59"*.

WHAT IT MEASURED, before deletion:

| leg | finisher | rider was | holders cleared | the microloop's exhaustion | fed back? |
|---|---|---|---|---|---|
| 07-18 02:33 | 04:17:45 | ws5 | 3 | 05:36:05 on ws11 | YES - deferred, finisher 05:38:30, microloop 2 |
| 07-18 02:33 | 05:38:30 | ws3 | 10 | 06:16:00 on ws1 | no - no defer, leg closed |
| 07-17 13:25 | 14:10:45 | ws12 | 5 | 14:29:00 on ws7 | no |
| 07-17 14:10 | 14:46:20 | ws5 | 3 | 15:49:40 on ws1 | no |

Every microloop walked ws1 -> ws12 and found an exhaustion. It fed back once in three legs. The
cost: the 07-18 02:33 leg's exit moved 09:09:00 -> 06:16:00 and the **06:59:40 finisher stopped
existing**, because microloop 1 changed the path before the 05:48:05 defer could happen.

DELETED - no `W_MICRO`, no stub, nothing to re-enable. The deletion record lives in `_chain10.py`
next to `W_CP_XWOB`.

## TWO LATENT DEFECTS THE MICROLOOP WORK EXPOSED — KEPT

Joe 1012: *"the two kept things: noted"*.

| what | the defect | why it never bit |
|---|---|---|
| the baton-holder list is now walk state | it was built only inside `if TRACE_HOLD`, so `W_EXH_WHO='holders'` silently fell back to the rider alone whenever `W_TRACE_HOLD` was 0 | every run this session passed `W_TRACE_HOLD=1` |
| the >ws12 mech's x-side boolean renamed `x_side` | it was also called `held` and would have overwritten the holder list on any bar that branch ran | every run passed `W_NO_GT12=1`, which keeps that branch off |

Neither moves any of the three 1012 walks.

## V_SIDE, in `_1011v2.py`

Forces the trade's side when global dr at the open reads the other way. The side is still set ONCE,
at the open; this only changes where that one read comes from, and the header row says which.
