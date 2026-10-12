# 1011 — the gc deferral of exhaustion, the ws1-cp, the looped walk

## HOW TO READ THE NUMBERS IN THIS DOC

Joe 1011: *"fixed numbers (like 22) are dangerous in docs, unless they're clearly marked as
examples"*.

- A number written as `{knob}` is a KNOB and is the mech.
- Every timestamp and every line value in this doc comes from ONE leg - 2026-07-18 03:41:00 SHORT -
  and is an EXAMPLE of the mech firing, never a rule. 04:14:30, 04:50:00, 05:42:00, ws3, ws10,
  ws13, ws22, 88.14, -34.00 and the rest are all that leg's instance values.
- A line number written as ws{n} without a knob marker is whichever line the walk was on at that
  bar, not a line the mech names.

Joe 1011, in conversation, after the 07-18 03:41 SHORT leg exhausted on ws3 at 04:14:30 with
ws4 18.57 and ws5 43.12 both inside the ex-fence:

> the next mech is new, and it's designed for the near misses that break the lineage`s baton-pass
> at 04:14:30, gcws15r and gcws30r are both above 50, and g15r downward trajectory. we're in a
> SHORT position, so `over50` positioning and downward traj indicate there is momentum to unwind
> before making the final baton-pass test

## THE MATRYOSHKA READING, Joe's word

g15r LEADS, g30r LAGS. Joe 1011: *"g30r looks like it's trajectory is up, and this is where we
apply the matryoshkaic view. g15 is pulling g30 around"* and, after correcting himself,
*"and g15r is leading that fall"*.

So g30r still pointing UP while g15r points DOWN is NOT a contradiction - it is the lag. g30r's
higher position on the board is the distance it still has to give.

## THE MECH

The leg is SHORT in this example; every side test mirrors for a LONG.

The rider stalls and its reach (rider+1 .. rider+LIN_HOP) is in fence, so `exhausted()` would close
the leg. BEFORE that verdict is accepted:

1. POSITION GATE — gcws15r AND gcws30r both on the WRONG side of 50 for the leg side, read at the
   stall bar. BOTH lines. Joe 1011: *"read on both. g30r is overarching, so in the 04:14 example its
   higher positioning on the board says that it has potential to fall, and g15r is leading that
   fall"*.
2. TRAJECTORY GATE — g15r ONLY. Joe 1011: *"I think this is the right move, based on matyoshka"*.
   a. find the COUNTER-SIDE EXTREMA by walking BACKWARD in 2-minute gaps. Joe: *"using a mech that
      is similar to divergence machine's 'hunting for an exterma', walk backwards in 2 minute gaps
      to look forward for the counter-side extrema"*. The walk stops at the first gap that adds
      nothing better. His worked example: *"the g15 high extrema at ~04:12 would be found by a
      backward walk to 04:11:30, and validated at 04:09:30"*.
   b. THE VALIDATION BAR is the bar the proof completes - the gap that added nothing. Joe:
      *"sidenote, the 'validated at' is not in divergence machine"*. So this mech reports it and the
      divergence machine does not.
   c. that extrema is the ANCHOR. Sample from the anchor to now EVERY 10 SECONDS over a 6-MINUTE
      span and take the diff. Joe: *"sample every 10 seconds for 4 minutes"*, then raised to 6:
      *"my 4 minutes is likely too small. let's make it 6 minutes"*.
   d. for a SHORT the diff must be DOWNWARD.
   CAUSAL: both the extrema bar and the validation bar are BEHIND the stall bar. The walk is
   backward from now. Nothing is read forward.
3. BOTH GATES PASS -> the exhaustion exit is DEFERRED, not cancelled. Joe: *"yes"*. The rider stays
   put. Nothing takes the baton, because nothing is oob to take it.
4. THE HOLD'S END — SPLIT IN TWO BY JOE 1012. The 1011 step 4 did two jobs with one test; he ruled
   them separately and they do not both survive.

   a. THE g15r `LINEAGE FINISHER` - Joe's name, 1012. It COMPLETES THE WALK. KEPT. Joe 1012: *"both g15r and g15Mage are needed to complete the
      walk"*. The pair arriving oob on the TARGET BOARD ends the hold and the walk carries on,
      lineage tests the baton. His 1011 words for the same thing: *"if we receive a low oob
      qualifier in our 04:14:30 example then the walk is still facing downward"*.
   b. g15 AS AN EXIT. DELETED. Joe 1012: *"the only banked back stop is dr-flip. I asked you earlier
      to remove g15 as an exit option. now I need you to delete it from the spec completely"*. The
      1011 branch where the pair arrived AGAINST the board and closed the leg is gone, and so is its
      exit stamp on the opposing g15 bar. Not knobbed off - deleted. `oob_side` survives in
      `_gcgate.py` and its docstring bars this use.
      WHAT HAPPENS NOW when the pair arrives against the board: nothing. The hold stays open and the
      trace says so once per hold.

   THE dr-FLIP BACKSTOP IS PARKED, `POI` tagged. Joe 1012: *"dr-flip backstop: parking it for now
   <- `POI` tag please"*. Not built, not knobbed, not stubbed. The open point when it is picked up
   again: must the flip happen DURING the hold, or does a global dr already opposite the trade close
   the hold on its first bar? On the 07-18 02:33 SHORT global dr was already -1 from 04:08:45, so
   the 05:48:05 hold closes on its own bar under the second reading and runs on under the first.
   WHILE IT IS PARKED a hold ends only on the walk-completion test at 4a. If the g15 pair never
   arrives on the target board, the hold does not end.
5. BLIP RULE — a FLIP IN THE TRAJECTORY'S SIGN must survive 12 bars (1 minute) before it counts.
   Joe: *"that's what I mean"*. SHORT-CIRCUIT: *"if the 12 bars follow the line into oob then the
   qualification is automatically given and the lineage tests for baton-pass"*.

## POI — Joe's tag, 1011. Two open points he wants surfaced if a baton-pass goes missing.

| POI | what it is |
|---|---|
| the short-circuit's test is weaker than the completion's | the walk-completion test needs g15Mage AND g15r oob; the 12-bar short-circuit needs only g15r. STILL OPEN after the 1012 split - the completion test survived, so the asymmetry survived with it. Joe: *"not deliberate - your note is valid. tag this as for further investigation - if we miss a baton-pass that I think should work, this will be one of the pieces I'll be interested in"* |
| the dr-flip backstop | PARKED 1012, Joe's tag. The hold's only end is now the walk-completion test. Joe: *"dr-flip backstop: parking it for now"* |
| the 6-minute span vs a long half-cycle | the anchor must fall inside the span. Joe: *"I think the g15r cycles (oob to same oob) are typically 4-5 minutes per half cycle ... your logic stand though"* |

## MY READINGS, stated because Joe implied rather than ruled them

- THE SPAN IS 6 MINUTES AND THE ANCHOR MUST FALL INSIDE IT. An extrema older than 6 minutes means
  the trajectory gate cannot form. That case is the second POI.
- THE 2-MINUTE EXTREMA GAPS ARE UNCHANGED by the span moving 4 -> 6 minutes. They are a separate
  backward walk with their own stop rule.

## WHAT IT DOES TO THE WALK, and the scale of it

Exhaustion stops being a verdict and becomes a question. On the current build exhaustion ends 12 of
13 legs, so this touches the main path, not a corner. Put to Joe as a risk; he ruled:
*"it is - I see this as solving a lot of hidden issues. I'm not saying it will work gloabally
straight away, this is just the foundation we are building"*.

NOT BUILT. Waiting on Joe's word.

## PARKED 1011 — exit is off the table until lineage is baked

Joe 1011: *"take exit off the table for now. lineage isn't baked yet, and it needs to be before we
jump ahead"*.

Recorded so it is not lost, NOT built, NOT to be raised again until Joe reopens it:

- `POI` Joe 1011: *"at the moment, I'm seeing ws1-cp as a prerequirement for exit"*.
- Joe 1011: *"at 05:42, the w_loop is complete and we start the lineage again from ws1"*.
- The question I put to him and he parked rather than answered: whether the MAE stop also needs a
  ws1-cp, or is the one exit that can land on any bar.

## STILL OPEN AS A BUILD ITEM — the loop extension, Joe 1011, NOT STARTED

> the next mech extends the loop event
> at ws{w loop tf}r oob
> -lookback 4 minutes for a same-side ws1-cp
> --if found, stop  (stub it for now)
> -walk forward to ws1-cp
> -this is the new `end of w_loop`

EXAMPLE, this one leg: the 4-minute lookback finds nothing - its cps are 04:11:25 and 04:12:45,
both outside 4 min of the loopTF oob - so the forward walk is the live branch and its target is the
ws1-cp at 05:42:00. Joe 1011 on that target: *"and beyond if lineage decrees"* - the cp COMPLETES
the loop, it is not where the leg ends.

## DELETED 1011 — x-cross is NOT an exit

Joe 1011, on the 05:43:00 row of the loop-extension trace: *"'x-cross on ws1 - EXIT'. not good.
drop this bias and delete 'x-cross as an exit' in the spec and related durable docs that are
hindering you"*.

- `W_NOX` now defaults to 1, so the lineage walk's x-cross exit does not fire.
- the branch stays reachable by `W_NOX=0` for reproducing pre-1011 runs ONLY. It is not part of the
  mech and must not be described as one.
- every earlier figure in these docs that counts x-cross exits is a record of a superseded build.
  `1010_ws10_exit.md` had one and it is now labelled as such.
- the >ws12r mech's own ws12x-vs-ws12r reversal is a DIFFERENT mech and Joe dropped that separately
  on 1009 (*"drop the x-cross mech - I was wrong to bring that online now"*). Neither is an exit.

## ADDED 1011 — W_TRACE_LIN, reporting only

Joe 1011, on the silence after the w_loop recycled the rider to ws1: *"lineage walk restarted after
w_loop recycles: I don't think so - there's no events, no line data, and no reasons stating why the
lineage stopped at ws1"*.

A resting walk emits no trace rows, so the report showed nothing between the recycle and the exit.
`W_TRACE_LIN=1` emits a row whenever (rider, baton available, rider stalled) changes, carrying the
reach values and their fence tags. Edge-triggered, so a long rest is one row. No branch reads it.

## 1011 — THE CEILING MATCHES THE LOOP TF

Joe 1011: *"ws_ceil now needs to match w_loop_tf"*.

- with a loop TF set, `BASE_HI` and `CEIL_HI` both become it. The baton cannot climb past the loop
  TF either, and the jumpstart's separate bound collapses into the same number.
- `W_CEIL` is now only effective when NO loop TF is set. It is silently overridden otherwise, which
  is stated in the code beside the override.
- CONSEQUENCE, to be read off a trace rather than assumed: with the ceiling AT the loop TF and
  `W_LOOP_END=cp`, a rider sitting on the loop TF has an EMPTY reach, so neither the baton nor the
  exhaustion test can fire while the loop is open. The walk waits for the cp.

## THE KNOBS THIS MECH ADDED, all in `_chain10.py` unless noted

| knob | default | what it is |
|---|---|---|
| `W_ARM` | mage | `cp` makes the ws1-cp the walk's qualifier instead of ws{`W_ARM_TF`}Mage |
| `W_CP` | 0 | 1 lets the ws1-cp reset the rider mid-walk |
| `W_CP_DWELL` | 4 | the ws1-cp hold in bars, 20 s. Joe 1012: *"add a 4 bar dwell to ws1cp"*. Consecutive; the cp is stamped at the LAST bar of the hold. 1 reproduces the pre-dwell build |
| `W_LOOP_TF` | '' | the loop TF, comma list. Also sets the ceiling |
| `W_LOOP_END` | cp | `cp` = the loop ends at the next ws1-cp. `oob` = the pre-1011 reset on the oob bar |
| `W_LOOP_LB` | 48 | the lookback window in bars, 4 min. STUBBED - detected and traced only |
| `W_GC` | 1 | the gc deferral. Baked on 1011 |
| `W_GC_HOLD` | wait | `wait` / `walk`. Both land identically on the example leg |
| `W_GC_STEP` | 2 | the trajectory sampling step in bars, 10 s (`_gcgate.py`) |
| `W_GC_SPAN` | 72 | the trajectory span in bars, 6 min (`_gcgate.py`) |
| `W_GC_GAP` | 24 | the extrema-hunt gap in bars, 2 min (`_gcgate.py`) |
| `W_GC_FLIP` | 12 | the blip rule hold in bars, 1 min (`_gcgate.py`) |
| `W_NOX` | 1 | x-cross as an exit is DELETED. 0 reaches pre-1011 runs only |
| `W_TRACE_LIN` | 0 | reporting only: what lineage asked and what the answer was |

## DISABLED 1011 — the A / B trade flip

Joe 1011, on the exhaustion trace text *"A closes here and B opens on the opposite side"*: *"this is
disabled now, please make sure the spec doc has this clearly notated"*.

- EVERY trace string carrying that sentence has had it removed from `_chain10.py`.
- THE REPLACEMENT, Joe's words: *"the replacement to A and B trades is now 'lineage taking over
  after a completed w_loop'"*.
- so continuity no longer comes from closing one side and opening the other at a verdict. It comes
  from a completed W_LOOP handing back to lineage at the ws1-cp.
- any figure in these docs produced before this was disabled describes a build where the flip was
  live. The chain driver's own `d = -d` alternation is a SEPARATE thing and is untouched.

## BANKED 1011 — the W_LOOP's boundaries and its name

`W_LOOP` is Joe's name, 1011: *"what is the loops name? I'm ok with W_LOOP if that works for you"*.
I had no name for it.

| banked | Joe's words |
|---|---|
| a W_LOOP BEGINS at the ws1-cp that arms the walk | *"this is the confirmed beginning of the loop. bank it"* |
| a W_LOOP ENDS at the ws1-cp that follows the walk reaching ws{loop_tf}r oob | *"this is the confirmed end of the loop. bank it"* |
| a completing ws1-cp also BEGINS a W_LOOP | *"a completing cp also begins a W_LOOP"* - NOT "the next": *"if you bank 'begins the next', you're opening up ambiguity if the trade/walk hasn't made it to ws{w_loop_tf}r oob"* |
| lineage is tested on the bar after a W_LOOP completes | *"immediate testing for lineage is the confirmed behaviour after a LOOP completes. bank it"* |
| a NEW leg does NOT test lineage immediately - it must walk to a ws1-cp first | *"immedaite testing is NOT lineage's behaviour at the start of a new leg/walk - a new (reentry) leg must walk to ws1-cp before lineage is tested"* |

A W_LOOP that never reaches ws{loop_tf}r oob never gets an end condition. That is why the
completing cp begins *a* W_LOOP and not *the next* one - there is no sequence to be next in.

### WHEN A STALL CAN AND CANNOT END THE LEG

In plain terms, and Joe has not named this state so it carries no shorthand:

- from the ws1-cp that begins a W_LOOP until the walk REACHES ws{loop_tf}r oob: lineage behaves
  normally. A stall, and an exhaustion, can still end the leg.
- once the walk has REACHED ws{loop_tf}r oob: a stall and an exhaustion are HELD. The leg waits for
  the ws1-cp that ends the W_LOOP.
- it has to be the second half only. If the hold ran from the W_LOOP's beginning, nothing could ever
  end a leg by stalling - including the stall at 04:14:30 on the example leg, which is the one the
  gc deferral was built to rule on.

## SPEC NOTE 1012 — what triggers the lineage-divergence test. NOT BUILT.

Joe 1012, as a sidenote: *"the lineage-divergence test will take place on every ws1Mage oob +
ws1x-cross-Mage, wob 2. standard x-cross, cross over for low oob, cross under for hi oob"*.

- the TRIGGER is ws1Mage oob AND ws1x crossing ws1Mage, held `wob` 2 bars.
- the cross TARGET is ws1Mage, not ws1r. Earlier the ws1-cp mode 2 was described as
  *"ws1Mage oob + ws1r with divergence"*; this note names the x-cross of ws1Mage as what fires the
  test.
- the DIRECTION is the standard one and matches the banked x-cross rule: ws1x crosses OVER for a
  LOW oob board, UNDER for a HIGH oob board. That is the counter-side cross.
- wob 2 = 2 bars = 10 s at the 5 s grid.

RECORDED, NOT BUILT. The divergence machine itself is now unblocked - the raw close went into the
tape cache on 1011 - but Joe has not said to build it.
