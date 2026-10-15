"""THE CHAIN RECREATED: the existing lineage walk + the new >ws12 oob mech. 09-25. 1007.

Joe 1007: *"'recreate the chain' means using the exisitng lineage walk + the new ws12 oob mech"* /
*"let's see where the next MAE 1.1 stop"*.

ONE LEG, with both mechs composed:

  OPEN          the previous leg's exit, or the seed bar.
  MAE STOP      at the first bar the adverse excursion from this leg's open exceeds mae_stop_pct
                1.10, the leg closes AT that bar and THE CHAIN STOPS. Outranks everything.
  THE CEILING   ws12r crossing into oob extends the baton's ceiling to ws23, per leg.
  THE WALK      until the handover: exit-armed on ws2Mage, one-time KICKSTART, baton on an oob
                crossing within lin_hop, exit on x-cross or final stalled.
  THE HANDOVER  the first bar where a CONSECUTIVE ws12r oob run on the leg's dr side exceeds
                oob_gate_bars 72. From that bar the >ws12 mech owns the exit and the walk's
                x-cross and stall are SUPPRESSED.

                THIS IS MY COMPOSITION DECISION, stated so it can be flipped. Joe's spec says
                "apply this logic after ws12r is oob for >6 minutes", which reads as a handover,
                and the mech exists because the walk's ws23 x-cross fired 56.6 min after the pivot
                on leg 8. The alternative - both live, first to fire wins - is one line away.
  AFTER IT      the ws1Mage 50 dip with a dwell > dip_dwell_bars 12, confirmed at dip + 11, then
                the first ws1r or ws2r reversal carrying a divergence with x under r (dr +1).

  BRANCH 1      a counter-dr ws12x cross of ws12r inside the first 6 min of an oob run is RECORDED
                and NOT ACTED ON. It is a trade SIGNAL, and acting on it would change the leg set,
                which Joe has not asked for.

                CORRECTED 1009. This block used to say the signal was blocked on "spec open
                question #4 - what closes a branch-1 trade in an always-in-market chain". THOSE
                WERE MY WORDS, NOT JOE'S, and the question was never real: the chain is CONTINUOUS,
                so a signal bar is the current leg's EXIT and the next leg's OPEN on the flipped
                side, exactly like `final stalled`, `x-cross` and the >ws12 divergence. None of
                those has a close rule either. Joe 1009: *"the query on a close rule is confusing -
                our chain is continuous"*.

Knobs from ws12_baton_config v1 and lazy_g_config v1.
"""
import os, io, contextlib, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.compute import momo_core as MC
from optimus9.compute.momo_config import momo_bank, momo_config
from optimus9.compute.momo_gated import momo_window
from optimus9.analysis.lr_v2 import _mage_rev
from optimus9.analysis.jig import stall_mask, anchor_floater
from optimus9.compute.spec_config import spec_config
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
import time as _t; _T0 = _t.time()
_P = lambda m: print('# [%6.1fs] %s' % (_t.time() - _T0, m), flush=True)
_P('importing score39 ...')
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC
_P('ready')

D = os.environ.get('W_DAY', '2026-09-25')
START = os.environ.get('W_START', '08:10:00')
FIRST = int(os.environ.get('W_SIDE', '1'))
LEG0 = int(os.environ.get('W_LEG0', '7'))
db = DatabaseManager(**get_db_config()); db.connect()
W = spec_config(db, 'ws12_baton_config')
LIN_HOP = int(SC.LG['lin_hop']); BASE_HI = SC.TF[-1]
TRIG_TF, CEIL_HI = int(W['ceil_trig_tf']), int(W['ceil_hi'])
# W_CEIL - the FLAT active ceiling. Joe 1009: *"if we set _CEIL 30 so that ws12r is allowed to pass
# the baton up per lineages mechs"*. It overrides BOTH base_hi and ceil_hi, so the ceiling does NOT
# start at ws12 and rise on the ws12r oob crossing - it is the given number from the leg's open.
# That is how `_linonly.py` ran the two walks Joe has been reading, so this keeps them comparable.
# STATED because the banked build's ceiling is a two-step base_hi -> ceil_hi.
_CEIL = os.environ.get('W_CEIL', '30')
if _CEIL:
    BASE_HI = CEIL_HI = int(_CEIL)
# W_NO_GT12=1 turns the whole >ws12r oob mech OFF. Joe 1009: *">ws12r oob off"*. No oob run is
# tracked, so there is no HANDOVER, no dwell, no exhaustion window, no ws12x reversal and no
# dip + divergence exit. The lineage walk owns every exit. The MAE stop is untouched.
NO12 = os.environ.get('W_NO_GT12', '0') == '1'
# THE LINES STOP AT ws30 IN THE CACHE. `xcond` needs the rider's h+1 and h+2 target lines, so a
# rider at ws29 or ws30 has no target and CANNOT take the x-cross exit - it can only exit on
# `final stalled`. Stated, not worked around.
MAXTF = int(os.environ.get('W_MAXTF', 30))
# W_STALL_UP=1 - the rider ADVANCES one TF on its own stalled event instead of exiting the leg.
# Joe 1009: *"drop x-cross, advance rider tf on stalled event"*.
#
#   WHICH TF: rider + 1, one rung. The advance carries NO qualifying test. An oob test would make
#     it identical to the oob baton already above it, so the mech would not exist. `lin_hop` 2 is
#     the oob baton's reach for SKIPPING a dead rung, and an unconditional step has nothing to
#     skip. MY READING, stated.
#   ONE PER BAR: the new rider is NOT re-tested for its own stall on the same bar - the same shape
#     as the oob baton's pass, which also ends the bar. Without it a run of stalls walks the rider
#     from ws3 to the ceiling inside one bar.
#   THE EXIT: at the ceiling there is nowhere to advance, so the stall THERE exits as
#     `final stalled`. With `W_NOX=1` dropping the x-cross, that and the MAE stop are the only
#     exits the lineage walk has left.
#   THE OOB BATON STAYS. Joe said advance ON A STALL, which adds a path; it does not replace the
#     oob pass, so a higher oob rung within lin_hop still takes the baton first.
STALL_UP = os.environ.get('W_STALL_UP', '0') == '1'
# W_KICK - what the walk's FIRST rider is. Joe 1009: *"disable kickstart. let lineage advance
# naturally"*.
#   'high'  the banked KICKSTART: the HIGHEST oob TF at or under the ceiling. A one-time jump.
#   'low'   the LOWEST oob TF at or under the ceiling - the jump removed, the oob test kept.
#   'off'   the lowest loaded TF, ws1, with NO oob test. Lineage climbs from the bottom.
# RULED BY JOE 1010: *"W_KICK off"*. 'off' is the default from here. 'high' is the banked
# KICKSTART, kept only so the old build is still reachable by one env var.
KICK = os.environ.get('W_KICK', 'off')
# ---- THE LOOPED WALK, Joe 1010. *"looping the lineage walk when it reaches ws10 or ws15, instead
# of climbing all the way up the tfs. ie when the walk crosses into ws10 or ws15 OOB (all sweep
# able), loop back to ws1 and continue lineage walking until exhaustion (ie the 2 tfs above are in
# fence)"*.
#
# W_LOOP_TF  '' = off. A comma list of loop TFs, e.g. '10' or '15' or '10,15'. Sweepable, as asked.
#
#   THE TRIGGER is ws{loop TF}r's OWN oob state, and NOTHING ELSE. Joe 1013, after finding the
#     loop had fired 0 times in 42 walks: *"we take the first signal - I haven't specified any
#     delays on ws{loop-tf}r crossing to oob"*, and on the state: *"I think this is ok. the event
#     becomes the state until a counter-event removes the state"*.
#     So the loop fires on the FIRST bar of an oob state and re-arms when ws{loop TF}r leaves oob.
#     WHAT WAS REMOVED, 1013: a `rider >= t` clause - the walk's current line had to be ws10 or
#     higher. It was MY READING of his 1010 sentence and it appears in none of his four
#     descriptions of this mech. It is why the loop never fired: on 2026-07-19 the 11:56:05 walk
#     was following ws7 for the whole 12:00:00-12:16:25 stretch of ws10r oob.
#   THE RESET puts the rider back on ws1, the lowest loaded TF, and the walk carries on under the
#     same baton and stall rules.
#   IT LOOPS AGAIN if the walk climbs back to a loop TF that is still oob. No cap - Joe set none.
#   THE LOOP IS CHECKED BEFORE EXHAUSTION on the same bar, because his sentence makes exhaustion
#     the thing that ends the POST-loop walk.
# RULED 10 BY JOE 1013: *"ws10 is the loop tf"*, and after the 8-to-14 sweep *"we'll keep loop-tf
# at 10"*. 12 was tried and read +10.9666% against 10's +12.2632%; the curve breaks between ws10
# and ws11 by 1.3816% in one step - ws8/9/10 all above +12, ws11 to ws14 all below +11.6.
LOOP_TFS = sorted(int(z) for z in os.environ.get('W_LOOP_TF', '10').replace(' ', '').split(',') if z)
# ---- THE SIX SWITCHES FOR THIS LAP'S LOOP BEHAVIOURS. Joe 1013: *"each of those changes are a
# knob - please bank them in spec. we'll sweep everything when we reach the first END in 07-20"*.
# Every default is what he ruled; the names are mine.
#
#   W_LOOP_RIDER_GATE  1 restores the pre-1013 gate - the loop only fires when the walk's current
#     line is at or above the loop TF. Joe 1013: *"delete this. ws{loop-tf}r oob is the only
#     qualification needed to send the walk to ws1"*. 0 is his.
#   W_LOOP_ONCE        the reset to ws1 fires once per LEG. Joe 1013: *"the 'rider reset to ws1' is
#     a one-time event"*.
#   W_LOOP_JUMP_OFF    the jumpstart is disabled for the rest of the walk after that reset. Joe
#     1013: *"if the loop cycles from loop-tf to ws1, the jumpstart is disabled for the remainder
#     of the walk"*.
#   W_LOOP_CLEAR_OOB   the per-line "has been out and back" memory is cleared at every reset to
#     ws1. Joe 1013: *"repair as needed"*.
#   W_LOOP_CLOSE       the trade closes when the walk lands on a weak ws1 with no baton available.
#     Joe 1013: *"the baton pass is load-bearing - it must move up through the TFs ONLY IF IT CAN.
#     if it cannot ... then EXHAUSTION is printed immediately and the walk ends"*.
LOOP_RIDER_GATE = os.environ.get('W_LOOP_RIDER_GATE', '0') == '1'
LOOP_ONCE = os.environ.get('W_LOOP_ONCE', '1') == '1'
LOOP_JUMP_OFF = os.environ.get('W_LOOP_JUMP_OFF', '1') == '1'
LOOP_CLEAR_OOB = os.environ.get('W_LOOP_CLEAR_OOB', '1') == '1'
LOOP_CLOSE = os.environ.get('W_LOOP_CLOSE', '1') == '1'
# ---- TWO CEILINGS, SPLIT 1012. SRP.
#
# Joe 1012: *"yes they need to be split. CEIL might need 10 +2 - the +2 allows for correct
# exhaustion calcs"*, after finding that pinning lineage's ceiling to the loop TF had bounded
# lineage out of existence: the rider reached the loop TF, its reach became EMPTY, and exhaustion
# was structurally impossible for 40 minutes while ws8 sat stalled with its own reach in fence.
#
#   LOOP_TF    the loop's trigger line. W_LOOP's business, and the jumpstart's start bound (Joe
#              1011: *"the max jumpstart reach must be <= loopTF"*). It does NOT bound the walk.
#   LIN_CEIL   LINEAGE's ceiling: the top of the band the rider may climb and the top its reach may
#              read. LOOP_TF + LIN_HOP, so a rider sitting ON the loop TF still has a full
#              rider+1..rider+LIN_HOP reach and exhaustion can be computed there. That is Joe's
#              "+2" - written as LIN_HOP, not a literal 2, so it tracks the knob.
#
# WHO MAY READ WHICH: lineage reads LIN_CEIL only. W_LOOP reads LOOP_TF only. The >ws12 mech keeps
# its own per-leg `ceil` (BASE_HI -> CEIL_HI on a ws12r oob crossing) and neither of the others
# touches it. The invariant is an assert, not a comment.
LOOP_TF = min(LOOP_TFS) if LOOP_TFS else None
if LOOP_TFS:
    LIN_CEIL = min(MAXTF, LOOP_TF + LIN_HOP)
    assert LIN_CEIL >= LOOP_TF + LIN_HOP, (
        'LIN_CEIL %d leaves a rider on the loop TF ws%d without a full %d-rung reach, so '
        'exhaustion cannot be computed there. Raise W_MAXTF or lower W_LOOP_TF.'
        % (LIN_CEIL, LOOP_TF, LIN_HOP))
else:
    LIN_CEIL = CEIL_HI
# ============================================================================================
# THE MACHINE, 1013. Joe: *"make it the machine"* / *"I need full state in the live machine without
# needing multiple versions of the same arg"* / *"the history is in the past for us now. the machine
# we're building now is the only one - if we choose to bring a historical machine into our working
# machine, then we can modify it to work with the live machine"*.
#
# FOUR DEFAULTS MOVED TO THEIR RULED VALUES. Before this, every ruling of his lived as a knob while
# the default kept the superseded value, so an unset run was the OLD mech. His words, and what the
# default was:
#     W_ARM       mage -> cp    Joe 1011: "replace the current ws2Mage lineage walk qualifier
#                               with ws1-cp"
#     W_ARM_TF    2    -> 1     Joe 1009: "let's swap ws2Mage with ws1Mage"
#     W_LOOP_TF   off  -> 10    Joe 1013: "ws10 is the loop tf"
#     W_CEIL      unset-> 30    Joe 1013: "ws30 is the ceiling"
# THE HISTORY MOVES WITH THEM, on his ruling: every lineage-walk figure banked before 1013 was
# produced on the ws2Mage arm with no loop TF and no flat ceiling. Those numbers are the past.
# NOT AFFECTED: the +8.0377% chain. `_ibmech` and `_extmom` contain no arm reference, and in
# last-mile mode `armed` is True at the first bar so neither arming block runs. Proven by reading
# every MARM / ARM == read in this file.
# ============================================================================================
# `ws1-cp` — JOE'S NAME, 1011. The ws1 CHECKPOINT. It has two jobs.
#
#   W_ARM 'cp'     the ws1-cp REPLACES the ws2Mage arm as the walk's qualifier. Joe 1011:
#                  *"replace the current ws2Mage lineage walk qualifier with ws1-cp"*. The walk
#                  arms at the cp and the rider starts on ws1 on that same bar.
#   W_ARM 'mage'   the banked arm: `W_ARM_TF`Mage crossing into oob. Kept so the old build runs.
#   W_CP=1         the cp also RESETS the rider to ws1 whenever it fires mid-walk.
#
#   AT THE CP THE RIDER IS ws1, so its reach is rider+1 .. rider+LIN_HOP like any other rider -
#   nothing about the cp names particular lines. Joe 1011: *"ws2 and ws3 are only an example for
#   this 05:43 walk"*.
#
#   MODE 1, the only one built: ws1Mage AND ws1r both oob on the LEG's side. Same-side is Joe's
#     1010 ruling. MODE 2 (ws1Mage oob + an r divergence, bullish at dr -1 / bearish at dr +1) is
#     NOT built - `jig.divergence` is the mech and its docstring requires the RAW close, which the
#     tape cache does not hold. Raised with Joe, not worked around.
#   THE EDGE: the cp fires ONCE per run of the condition, so a cp that stays true for many bars
#     arms or resets once, not every bar.
#   W_CP_DWELL — THE DWELL. Joe 1012: *"add a 4 bar dwell to ws1cp"*. The condition must hold
#     `W_CP_DWELL` CONSECUTIVE bars for the cp to count. Default 4 bars = 20 s at the 5 s grid.
#     W_CP_DWELL=1 reproduces the pre-dwell build exactly.
#     WHY IT WAS ASKED FOR: the 02:33 07-18 SHORT's first low ws1-cp, 02:43:25, held ONE bar - both
#     lines were only just under the 15 line (ws1r 12.82, ws1Mage 14.28) and were back over on the
#     next bar. Joe: *"the 02:43 might be troublesome, its firing on a low-dwell ws1-cp"*.
#     THE STAMP IS THE LAST BAR OF THE HOLD, not the first. Stamping the first bar would act on a
#     bar whose 4-bar hold is not knowable for another 3 bars, which is lookahead. Same stamp rule
#     as `_linonly.py` on the x-cross hold, `ws_strat.candidates` (conf = cross + xwob - 1) and
#     `build_s46_event.sx_series`. So a cp whose condition first goes true at T is stamped
#     T + W_CP_DWELL - 1.
#     CONSECUTIVE, not cumulative - one false bar restarts the count at zero.
#     STILL OPEN, NOT DECIDED HERE: what a leg does when the condition is ALREADY standing at the
#     trade's open. The dwell counter starts at zero on the open bar, so a standing condition is
#     counted from the open and stamps a cp W_CP_DWELL bars in, even though nothing crossed. Raised
#     with Joe on the 07-18 03:41 legs; his ruling is outstanding.
# W_GC=1 — THE gc DEFERRAL OF EXHAUSTION. Joe 1011, spec in docs/octo-freedom/1011_gc_defer.md.
# At an exhaustion verdict, if BOTH gc gates pass the verdict is DEFERRED, not cancelled. The gates
# themselves live in `_gcgate.py` (SRP); this file owns the leg decision.
#
# THE HOLD'S END, Joe 1012, two separate rulings:
#   *"both g15r and g15Mage are needed to complete the walk"* - the pair arriving on the TARGET
#     BOARD ends the hold and the walk carries on. This is kept.
#   *"the only banked back stop is dr-flip ... remove g15 as an exit option"* - the 1011 branch
#     where the pair arriving AGAINST the board closed the leg is DELETED, with its opposing-g15
#     exit stamp. Nothing in the g15 pair can close a leg now.
# The dr-flip backstop is not wired yet; the one unspecified point is at the hold in run_leg.
#
# W_GC_HOLD — the one fork I could not resolve from Joe's words, so BOTH are built:
#   'wait'  during the hold ONLY the backstop is read. Joe's sequencing: *"there is momentum to
#           unwind BEFORE making the final baton-pass test"*. A baton candidate appearing mid-hold
#           is IGNORED under this arm, which is a consequence he should see.
#   'walk'  the walk carries on normally and the exhaustion exit is merely suppressed, so the baton
#           can still pass mid-hold. Joe's word *"keep walking"* points here.
# BAKED IN 1011. Joe: *"if the test retains 04:50 then bake the new mech in"*. After the
# re-exhaust guard both hold modes land on 04:50:35 / +0.9083, so the fork no longer bites on this
# leg and 'wait' is the default. W_GC=0 still reaches the pre-gc build.
# THE TRADE'S SIDE SETS THE TARGET BOARD. Joe 1012, ruling both halves after the 07-18 02:33
# trade armed four legs on the wrong board:
#   *"the trade's direction/'side' is what sets the target: SHORT trades use a low board target,
#   LONG trades use a high board target"*
#   *"always the end the trade is heading to"*
#   *"it can only be set once at the open of the trade"*
#
#   trade_side +1  = a SHORT (the banked `dr +1 = SHORT`), so the TARGET BOARD is LOW.
#   trade_side -1  = a LONG, so the TARGET BOARD is HIGH.
#   board = -trade_side, resolved ONCE at the trade's open bar.
#
# `d` INSIDE run_leg IS THE TARGET BOARD, NOT THE TRADE'S SIDE. Every test in the walk already
# takes `d` as "which end of the board am I working on" - the ws1-cp, the jumpstart, the baton, the
# stall, exhaustion, the loop end and the gc gates. Setting `d` to the board at the open is
# therefore the whole fix; none of those seven tests needed its own change. Joe 1012 on why that
# matters: *"this notion is more powerful than it might seem on the surface"*.
#
# WHAT THIS REPLACES. W_DR=global read `SC.DRv` on EVERY bar and reassigned `d` when it moved.
# `SC.DRv` moved 3 times inside the 02:33 trade (02:41:45, 03:11:35, 04:08:45), so the board moved
# with it and the walk hunted HIGH ws1-cps at 03:41. The knob is gone - Joe: the side *"can only be
# set once at the open of the trade"*.
#
# THE LEG'S pct SIGN READS THE TRADE'S SIDE, not the board, and 1012 corrected its direction - see
# the sgn block in run_leg. Adverse is the move AGAINST the trade.
GC = os.environ.get('W_GC', '1') == '1'
GC_HOLD = os.environ.get('W_GC_HOLD', 'wait')
assert GC_HOLD in ('wait', 'walk'), 'W_GC_HOLD must be wait or walk'
# W_LOOP_END — where the loop event ENDS. Joe 1011: *"the next mech extends the loop event: at
# ws{w loop tf}r oob - lookback 4 minutes for a same-side ws1-cp -- if found, stop (stub it for
# now) - walk forward to ws1-cp - this is the new `end of w_loop`"*, and on the target:
# *"and its target is 05:42:00, and beyond if lineage decrees"* - so the cp COMPLETES the loop and
# lineage carries on from ws1; it is not where the leg ends.
#
#   'cp'   (default) the ws{loopTF}r oob OPENS the loop and the rider is NOT reset there. The walk
#          carries on and the loop ENDS at the next ws1-cp, where the cp does the reset it already
#          does. Joe: *"at 05:42, the w_loop is complete and we start the lineage again from ws1"*.
#          ATTRIBUTION CORRECTED 1013, Joe: *"this was an observation, not a mech"*. That quote is
#          him reading one bar, not ruling where the loop ends. THE 'cp' DEFAULT IS MINE. His 1013
#          description of the mech is 'oob' below: *"the mech fires on ws{loop-tf}r crossing to oob
#          ... ws{loop-tf}r recyling the loop (to ws1) on its oob event"*.
#   'oob'  the pre-1011 behaviour: the rider resets to ws1 on the oob bar itself.
#
#   THE 4-MINUTE LOOKBACK IS A STUB, Joe's word. A same-side ws1-cp inside W_LOOP_LB bars before
#   the oob bar is DETECTED and TRACED, and nothing else happens - the forward walk proceeds as if
#   it were absent. Joe said *"if found, stop"*, and "stop" has more than one reading (stop the
#   loop, or stop the leg), so no behaviour is attached to it.
#
#   EXITS ARE UNTOUCHED during the forward walk. Joe 1011 parked exit entirely, so suppressing one
#   here would be me altering a mech he has not ruled on. The consequence on the 07-18 03:41 leg is
#   stated in my reply: the gc backstop still closes it before the forward cp arrives.
# RULED 'oob' BY JOE 1013: *"our machine updates for this lap: ... lineage last-mile loops to ws1
# on ws{loop-tf}r oob"*. The 'cp' default was MINE and it is gone - his 1013 description of the mech
# was 'oob' all along: *"the mech fires on ws{loop-tf}r crossing to oob ... ws{loop-tf}r recyling the
# loop (to ws1) on its oob event"*.
LOOP_END = os.environ.get('W_LOOP_END', 'oob')
assert LOOP_END in ('cp', 'oob'), 'W_LOOP_END must be cp or oob'
LOOP_LB = int(os.environ.get('W_LOOP_LB', 48))      # 4 min at the 5 s grid
# W_CP — WHAT A ws1-cp DOES TO THE RIDER.
#   '0'    nothing. The cp only ARMS (under W_ARM=cp) and ENDS a W_LOOP.
#   '1'    only a COMPLETING cp resets the rider to ws1. Joe 1012: *"drop the reset at every
#          ws1-cp"*, against his banked *"at 05:42, the w_loop is complete and we start the lineage
#          again from ws1"* - the completion, not every checkpoint.
#   'all'  EVERY cp resets the rider to ws1. Joe 1012 reopened this: *"I must have agreed to the
#          wrong thing - I'm expecting rider to be reset (ie back to ws1)"*. Built so the impact on
#          the banked trades can be measured before he commits to it. NOT the default.
CP_RIDER = os.environ.get('W_CP', '0')
assert CP_RIDER in ('0', '1', 'all'), 'W_CP must be 0, 1 or all'
CP = CP_RIDER in ('1', 'all')
CP_ALL = CP_RIDER == 'all'
CP_DWELL = int(os.environ.get('W_CP_DWELL', 4))
# ws1-cp MODE 2 — THE DIVERGENCE MODE. BAKED 1012, Joe: *"we need mode 2 baked in so that jumpstart
# can fire on the 14:33 ws1-cp"*. Default 'both': either mode arms, which is what he meant by
# *"your ws1cp mech has both modes baked"*.
#   '1'     mode 1 only - ws1r AND ws1Mage both oob on the target board. The pre-1012 build.
#   '2'     mode 2 only.
#   'both'  either one. THE DEFAULT.
# RE-ENABLED 1012, Joe: *"re-enable mode 2"*. He disabled it one turn earlier to see what it was
# holding up; disabling it cost the 14:46:20 and 18:56:10 finishers on the 07-17 14:10 SHORT, which
# never arms on mode 1 in time.
CP_MODE = os.environ.get('W_CP_MODE', 'both')
assert CP_MODE in ('1', '2', 'both'), "W_CP_MODE must be 1, 2 or both"
# THE MODE-2 TRIGGER, Joe 1012 verbatim: *"to set the anchor and initiate the divergence test, use
# ws1x crossing ws1Mage while ws1Mage is oob (crossing under for a LONG trade/high oob, crossing
# over for a SHORT trade/low oob)"*, and his 1012 sidenote: *"every ws1Mage oob + ws1x-cross-Mage,
# wob 2"*.
#   THE BOARD ANCHORS THE CROSS DIRECTION, not the trade label. Joe pairs them himself - "LONG
#   trade/high oob" and "SHORT trade/low oob" - so the rule reads off the board:
#     board HIGH -> ws1x crosses UNDER ws1Mage
#     board LOW  -> ws1x crosses OVER  ws1Mage
#   which is the banked x-cross direction rule with the board as its subject.
#   THE STAMP IS THE LAST BAR OF THE wob HOLD, cross + W_CP_XWOB - 1, the first bar the hold is
#   knowable. Same rule as W_CP_DWELL and every other hold in this build.
#   THE ANCHOR IS THAT STAMP BAR. `anchor_floater` step 1 takes it, step 2 finds the pivot, step 3
#   walks back for the floater, step 4 compares. The cp needs the comparison to FIRE on the board's
#   own sign - Joe's mode-2 wording was *"bullish at dr -1 / bearish at dr +1"*, and the board is
#   that sign. An anchor that does not fire is not a cp.
#   STEP 2 IS ON THE 50 RULE, AGREED BY JOE 1012 — and he corrected how it should be described:
#   *"the 50 rule (what I ran, the producer's default)" -agreed. honestly: its not a default, it's
#   lore"*. So it is not a fallback that happens when no `xn` is passed; it is the rule, carried
#   forward because it has always been there. `anchor_floater`'s own docstring still calls it
#   "MINE, and unruled" because Joe named a timestamp (~17:32:30) rather than a rule in 0912 - that
#   line is now out of date and his 1012 "agreed" settles it.
#   THE 0921 DWELL RULE IS IGNORED FOR THIS CALLER. Joe 1012: *"the dwell rule, your 0921 spec
#   -ignore"*. Not a knob here, not an open point.
CP_XWOB = int(os.environ.get('W_CP_XWOB', 2))
# W_EXIT_FIN — THE LEG EXITS ON THE g15r LINEAGE FINISHER. Joe 1012: *"walk a LONG trade that opens
# at 07-17 08:49:45 and exits on the finisher's g15 signal"*. 1 closes the leg at the first finisher
# the walk reaches; 0 is the banked behaviour, where the finisher ends the gc hold and the walk
# carries on. DEFAULT 0 - a new exit must not move the walks already banked, so it is passed per run
# until Joe says otherwise.
EXIT_FIN = os.environ.get('W_EXIT_FIN', '0') == '1'
# W_HTF_MOM — THE HTF MOMENTUM HOLD. Joe 1012, his words for the test: *"the leg does not close
# while N consecutive lines above the rider are mom-true toward the board"* / *"I agree"*, and on
# the sweep that set N: *"the gap of 1 feels more like a coin-toss than science - let's see how it
# looks across the other exits"* / *"that's good news"*.
#
# AT A LEG CLOSE: the longest run of CONSECUTIVE mom-true lines strictly ABOVE the rider, from
# rider+1 to W_HTF_MOM_TOP. If that run is >= W_HTF_MOM_N the leg does NOT close.
#
# N = 9 IS THE ONLY INTEGER THAT FITS, measured over 29 candidate bars in 10 legs on 2 days:
#   the highest run Joe wants to exit on   8   07-18 06:59:40
#   the lowest run Joe wants blocked      10   07-18 04:17:45, and 07-18 17:28:00 also sits at 10
#   bars at 9                              0   of 29
# 4 bars at 10 or above, 25 at 8 or below, nothing between. The boundary rests on two bars and the
# gap is one integer wide; widening from 19 to 29 bars did not fill it. Stated because it is thin.
#
# DEFAULT OFF, Joe 1012: *"put it in a knob, default off"*.
#
# IT DOES NOT TOUCH THE MAE STOP. The stop is a risk limit, not the walk deciding it has run out of
# momentum, and Joe's sentence is about the walk. Stated as a choice, not ruled.
#
# IT OWNS ITS OWN BAND (SRP). The run was measured over ws4..ws30, but ALL_TF stops at the ceiling -
# ws23 in the banked config, ws12 for lineage. Truncating at ws23 would change the numbers: the
# 06:59:40 run is ws23-ws30, which reads as 1 instead of 8. So the test loads its own mom-true masks
# up to W_HTF_MOM_TOP and does not borrow lineage's band. That build is minutes long, so it only
# happens when the knob is on.
# W_STALL_N — THE STALL SAMPLE COUNT. Joe 1012: *"`stalled` could be firing sooner than we need -
# 3 was an arbitrary number of samples to prove stalled, but it was never swept"*. The spec table's
# value is 6, not 3, and it is the DEFAULT here so an unset run is unchanged.
# THE RULE: a line is stalled when its last fresh extreme is W_STALL_N or more lattice samples back.
# The lattice is each TF's OWN momo bank - MOMO_SAMPLES points, MOMO_STEP_BARS apart - so the same
# count is a different wall-clock span on every line.
STALL_N = int(os.environ.get('W_STALL_N', SC.LG['stall_n']))
assert STALL_N >= 1, 'W_STALL_N is a sample count and must be at least 1'
HTF_MOM = os.environ.get('W_HTF_MOM', '0') == '1'
HTF_MOM_N = int(os.environ.get('W_HTF_MOM_N', 9))
HTF_MOM_TOP = int(os.environ.get('W_HTF_MOM_TOP', 30))
assert HTF_MOM_N >= 1, 'W_HTF_MOM_N is a count of lines and must be at least 1'
# THE MICROLOOP IS DELETED. Joe named it *"double dipping"* and dropped it 1012: *"ok, drop the
# 'double dipping' idea. I'm too attached to 06:59"*. It restarted the lineage walk at a g15r
# lineage finisher - rider to ws1, holder list cleared - and it cost the 06:59:40 finisher on the
# 07-18 02:33 SHORT by changing the path before the 05:48:05 defer could happen. There is no
# W_MICRO knob and no stub. Nothing here to re-enable.
#
# WHAT SURVIVED IT, because neither belongs to it: the baton-holder list is now walk state rather
# than being built only under W_TRACE_HOLD, and the >ws12 mech's x-side boolean is renamed `x_side`
# so it no longer collides with that list. Both were latent defects the microloop work exposed.
assert CP_XWOB >= 1, 'W_CP_XWOB is the ws1x cross hold in bars and must be at least 1'
assert CP_DWELL >= 1, 'W_CP_DWELL is the ws1-cp hold in bars and must be at least 1, got %d' % CP_DWELL
# W_ARM 'lastmile' - THE LAST-MILE MODE, 1013. Joe: *"create a last-mile mode that doesn't rely on
# ws1cp and fires kickstart at the last-mile handoff"*, after *"when the extension fires, walk the
# last mile using lineage"*.
#   THE WALK IS ARMED AT ITS FIRST BAR. There is no arming event to wait for, because the trade is
#   already open - the extension handed the walk a live leg. Measured on the 07-18 17:39:10 handoff:
#   the banked ws2Mage arm does not fire until 2026-07-18 18:25:10, 46.0 min later, which is already
#   past the ~18:09 ending Joe named. No kickstart setting reaches it, because arming gates the walk.
#   NO ws1-cp IS READ on this path: the cp arms only under W_ARM='cp', and with W_LOOP_TF off there
#   is no loop for a cp to end. Joe: *"doesn't rely on ws1cp"*.
#   THE KICKSTART FIRES AT THE HANDOFF. `W_KICK` defaults to 'high' in this mode - the banked
#   KICKSTART, the highest oob TF at or under the bound, taken as a one-time jump on the first bar.
#   Joe's 1010 ruling *"W_KICK off"* governs the ARMED walk, which climbs from ws1 after its own
#   arming event; it is not a ruling about a walk handed a live leg mid-move. W_KICK still overrides.
#   THE >ws12 MECH IS OFF in this mode. Joe: *"walk the last mile using lineage"* - the >ws12 mech
#   is not lineage, and when it fires it takes ownership of the exit ('the >ws12 mech owns the
#   exit'), which would end the last mile on a non-lineage branch. On this handoff ws12r is already
#   oob, so the handover fires 6.1 min in at ~17:45:20 and the lineage walk never climbs at all.
#   W_NO_GT12 still overrides. MY READING OF "using lineage", STATED.
ARM = os.environ.get('W_ARM', 'cp')
assert ARM in ('mage', 'cp', 'lastmile'), 'W_ARM must be mage, cp or lastmile'
LASTMILE = ARM == 'lastmile'
# JOE'S KNOB, HIS NAME, 1013: *"I think for last-mile work, the kickstart TF should be limited to
# {knob:5, 'LIN_LASTMILE_KCKSTRT_TFCAP'}"*. It caps the KICKSTART's reach in last-mile mode only -
# the baton is NOT capped by it, exactly as the loopTF bound works for the armed walk.
# WHY IT WAS NEEDED: uncapped, the kickstart at the 2026-07-18 17:39:15 handoff takes the highest
# oob line at or under the lineage ceiling ws30, which is ws12 (r 90.72). ws7 sits below that and
# can never become the rider, so the ~18:09 ending on ws7 was unreachable. Under the cap the
# highest oob line at or under ws5 is ws1 (r 95.74).
# FIXED AT 7, Joe 1013: *"let's fix the cap at 7"*, after the sweep. WAS 5.
# MEASURED over seven trades, this knob alone: ws5 +11.2050%, ws6 +11.1355%, ws7 +11.1335%. Raising
# it COSTS 0.0715% - only two trades move and both get worse, because W_KICK is 'high' so the
# kickstart always takes the highest oob line available and the walk then starts further up the
# ladder and exhausts on a shallower reach:
#     07-18 02:31 SHORT   ws5 ends 11:13:35 +4.8337%  ->  ws7 ends 11:15:30 +4.7703%
#     07-18 08:46 LONG    ws5 ends 10:07:10 +0.4014%  ->  ws7 ends 10:20:05 +0.3934%
# The 07-19 01:24 SHORT, which prompted the sweep, does not move at all: ws6-ws9 carried momentum at
# its handoff but only ws7 was oob, and at dwell 4 its handoff bar is 07:12:15, a different ladder.
# HIS CALL, TAKEN WITH THE COST STATED.
LASTMILE_KICK_TFCAP = int(os.environ.get('LIN_LASTMILE_KCKSTRT_TFCAP', 7))
# JOE'S KNOB, HIS NAME AND HIS SPELLING, 1013: *"we bank the {knob:12,'LINFIN_WALK_DELAy'}-bar
# gate"*. THE BLAST-RADIUS GATE ON THE JUMPSTART. Joe: *"it shouldn't have fired, for blast-radius
# reasons: at 18:44:15 ws1 and ws2 are tagged ib, and ws4 is oob and heading away from target-dr /
# blast-radius says that the TFs above ws1,2,4 will follow the lower lines / this means the
# jumpstart should not fire - the blast-radius + ws1-cp crossing to ib tells the mech that there is
# no momentum left"*.
#
# IT IS A DELAY, NOT A PEEK. His own word. The verdict needs the 12 bars to form, so the walk is
# HELD for them and the verdict lands at handoff + 12. Deciding at the handoff bar on bars that come
# after it would be lookahead - information later than the acting bar.
#
# A LINE VOTES `AWAY` at a bar when it is oob on the target end AND further from that end than it
# was at the handoff. The gate fires when AWAY_MIN or more lines have voted at least once across
# the walk. Lines are the TFs under the loop TF, matching the `left-target-dr` tag rule.
#
# WHY `AWAY` ALONE, MEASURED over the five handoffs - the full vote count is useless, the biggest
# winner carries the most votes:
#     handoff            the last mile did   votes/108   LEFT   AWAY   lines voting AWAY
#     07-18 18:12 SHORT  -0.1849%                   29     12     17   3 of 9
#     07-17 21:58 LONG   +0.0304%                   28     27      1   1 of 9
#     07-18 08:46 LONG   +0.0084%                   38     37      1   1 of 9
#     07-18 16:07 LONG   +0.9238%                   97     96      1   1 of 9
#     07-18 02:31 SHORT  -0.0277%                   67     67      0   0 of 9
# `LEFT` - been oob, now in-fence - is the WINNER's signature: 96 of 16:07's 97 votes. It is not a
# stand-down signal. `AWAY` separates 3 lines from 1, cleanly.
# JOE'S ws2r CALL WAS RIGHT: at the handoff bar ws2r 10.61 is oob and moving toward the target, a
# blip; walked 12 bars it votes AWAY on 7 of them.
#
# AWAY_MIN 2 IS MINE, AND ANCHORED, NOT PREFERRED: every one of the three winners sits at exactly 1
# line and the loser at 3, so 2 is the only value between them. Its name is mine too.
# IT CATCHES 1 OF THE 2 LOSERS. 07-18 02:31 lost 0.0277% with 0 AWAY votes and nothing in this
# measurement explains it. Stated.
# THE MAX JUMPSTART GAP, 1013. Joe: *"I saw that too, and it doesn't align with the spirit of the
# mech. find the max gap we've seen so far, and create an approatiate (maybe max-seen-gap*1.2) knob
# for it. apply the max-gap knob to the mech"* / *"set it to 24"*.
# THE KNOB'S NAME IS MINE; the value 24 is his.
# MEASURED, and the sample has NO VARIANCE: 6 of the 7 last-mile handoffs placed a rider on the very
# NEXT bar - 01:15:20, 11:11:15, 10:07:10, 17:39:10, 18:44:15 and 20:04:00 all gap 1 bar. The only
# outlier is the ws30-ride handoff at 2026-07-18 21:24:05, where the jumpstart sat 506 bars = 42.2
# min before ws3 went oob. So max-seen x 1.2 rounds back to 1 bar, which would mean the jumpstart
# fires on the next bar or never; Joe set 24 instead. Stated because the formula was his first idea
# and the data could not support it.
# WHEN THE GAP EXPIRES the walk ends at the expiry bar and the held close fires there - causal, that
# is the bar on which "no rider appeared" becomes known.
LASTMILE_MAX_GAP = int(os.environ.get('LIN_LASTMILE_MAX_GAP', 24))
LINFIN_WALK = int(os.environ.get('LINFIN_WALK_DELAy', 12))
LINFIN_AWAY_MIN = int(os.environ.get('LINFIN_WALK_AWAY_MIN', 2))
if LASTMILE:
    # BOTH DEFAULTS FLIP HERE, AND BOTH STAY OVERRIDABLE - an explicitly set env var always wins,
    # so every number below can be re-measured against the other setting. KICK and NO12 are read
    # near the top of this file, before ARM exists, which is why the flip lives here.
    if 'W_KICK' not in os.environ:
        KICK = 'high'
    if 'W_NO_GT12' not in os.environ:
        NO12 = True
# W_LOOP_EXH  when the exhaustion exit is live.
#
#   RULED BY JOE 1010, correcting my 'after_loop': *"this is only true if the lineage walks to the
#   loop-tf. if the lineage sees exhaustion before it reaches loop-tf (ie the swing is small so
#   doesn't attract a loop-tf OOB event), then act on the smaller exhaustion tf per our usual
#   process"*. So exhaustion is LIVE FROM THE ARM, loop or no loop, and a small swing exhausts on a
#   low TF and reverses there.
#
#   'on_stall'    (default) the exhaustion test runs on the bar the RIDER STALLS. *"per our usual
#                 process"* - a stall is what the walk already acts on, and the oob baton is tested
#                 before it, so reaching this point already means the baton had nothing to take.
#   'always'      the test runs on EVERY bar, stall or not. The other reading of the same ruling.
#   'after_loop'  DEAD, kept only to reproduce the first 1010 run. Joe ruled it out.
#   'off'         no exhaustion exit; the loop still runs and the old exits own the leg.
EXH_LOOP = os.environ.get('W_LOOP_EXH', 'on_stall')
assert EXH_LOOP in ('on_stall', 'always', 'after_loop', 'off'), \
    'W_LOOP_EXH must be on_stall, always, after_loop or off'
# "IN FENCE" IS THE BAKED EX-FENCE, NOT A KNOB. Joe 1010, when I offered it as a choice: *"this
# should already be the mech's baked code"*. So the test is the '.' tag from `bnd` - inside
# momo_fence_r 17/83 - and the weaker "just not oob" reading is gone. The two were measured before
# the ruling and gave BYTE-IDENTICAL legs on the 03:13:15 chain, so nothing moved with it.
assert KICK in ('high', 'low', 'off'), 'W_KICK must be high, low or off'
GATE_BARS, SIG_WIN = int(W['oob_gate_bars']), int(W['sig_window_bars'])
DIP_MID, DIP_DWELL = float(W['dip_mid']), int(W['dip_dwell_bars'])
# THE >ws12 MECH'S OWN oob FENCE, 1008. Joe: *"we should have a knob for >12 oob"*.
#
# The 72-bar gate, the branch-1 window and the ceiling trigger were all reading the GLOBAL oob
# 15/85 out of lazy_g - the same shape as reent_xwob borrowing the divergence mech's x_rev_xwob.
# `goob` is the >ws12 mech's test and nothing else uses it; the KICKSTART and the baton stay on
# `oobf` and the global fence.
#
# oob_gate_fence 15.0 reproduces today's behaviour exactly, so the knob changes nothing until it is
# swept. Symmetric: lo = the knob, hi = 100 - the knob.
G_LO = float(W['oob_gate_fence']); G_HI = 100.0 - G_LO
#   `goob` itself is defined beside `oobf`, once R exists.
DIP_FENCE = float(W['dip_fence'])            # Joe 1008: the dip is a BAND, not a level
DIP_HI, DIP_LO = DIP_FENCE, 100.0 - DIP_FENCE   # 53.0 and 47.0
RREV = int(W['rrev_wob'])
# THE MAE STOP. Joe 1013: *"the ensuing LONG trade stops at 1.1 (we don't need 2.5 MAE now - that
# was for a different era with different mechs)"*. The DB's `ws12_baton_config.mae_stop_pct` still
# holds 2.5 and is NOT touched - this overrides it in the machine. The knob name is mine.
MAE_STOP = float(os.environ.get('W_MAE_STOP', 1.1))
# ---- THE BATON'S CANDIDATE TEST, 1009. Joe's 1006 spec row for `lin_hop` reads *"jump no more
# than 2 higher TFs to find the next TF WITH MOMENTUM"*. The hop limit was built; the momentum
# clause never was - `oobf` stands in its place, and nothing in the file flagged the substitution.
# Measured 1009 on the banked build: the baton dies on ws1 34.0% of stalls and on ws1-ws4 76.7%,
# and at 326 of 326 stalls a higher line was trending with the leg while 0 were oob.
#
# W_BATON picks what a line must show to take the baton. Joe 1009: *"if a lin_hop line has
# momentum, lineage needs to make that line the rider"*, and *"r-pred and lineage need to be AB'd"*.
#
#   'oob'       r is out of bounds at this bar. AS BUILT, THE DEFAULT.
#   'momentum'  the line is mom-true - momo OR curl, Joe's 1009 definition, side-aware via momo_g's
#               own gate 1. His 1006 clause, finally built.
#   'rpred'     the line is PREDICTED to breach - Joe's 0730 mech, `predict_breach`: r in-bounds,
#               the anchor max(m, Mage) out of bounds, and the anchor's distance past the boundary
#               greater than r's distance short of it. Joe 1009: *"climbing r lines is a very old
#               mech that I've iterated and evolved over time"*.
#   'either'    momentum OR rpred. Joe 1009 agreed to this fourth arm.
#
# `stalled` stays reachable through W_PASS for the 1007 variant.
BATON = os.environ.get('W_BATON', 'oob')
assert BATON in ('oob', 'momentum', 'rpred', 'either'), \
    'W_BATON must be oob, momentum, rpred or either'
# W_PASS 'crossing_to_ib' - JOE'S THIRD BATON MODE, 1013, HIS NAME: *"this scenario invites a new
# mech to sit along side the 'oob' and 'stalled' modes / the new mode is 'crossing to ib'. instead
# of baton passing on oob or stalled, lineage-last-mile will baton pass on rider-tf returning to
# ib"*.
#   THE TRIGGER IS ON THE RIDER, NOT ON THE CANDIDATES. 'oob' and 'stalled' both ask a question of
#   the lines ABOVE the rider; this mode asks one of the rider itself, so it is handled at the
#   baton site rather than inside `baton_ok`.
#   THE RIDER MUST HAVE BEEN OOB FIRST. Joe's own example pins this: *"in this ~17:39 example, this
#   new mode would walk ws2r to a baton-pass at ~18:07"*. ws2r is 73.41 and already IN-FENCE when
#   it takes the baton at the 17:39 handoff; it climbs to 91.42 oob by 18:05:00 and is back to
#   77.14 in-fence by 18:08:00. Only "went oob, then returned" lands on ~18:07. A bare "is IB now"
#   test would pass the baton on the bar it received it.
#   THE RECEIVER IS THE NEXT TF UP, consecutively - his example walks ws1 -> ws2, and the rider
#   does not pick the highest of a reach the way 'oob' mode does.
#   NO DWELL AND NO WOB ON THE CROSS. He has not specified one, so the pass is the bar the rider
#   crosses back inside the fence.
#   THE SIDE-AWARE TEST IS THE WALK'S OWN `oobf`, so "ib" means inside the fence at the end of the
#   board the walk is working - for a HIGH board, r back under 85.
PASS = os.environ.get('W_PASS', 'oob')  # 'oob' (as built, Joe's tag ruling), 'stalled'
#                                        or 'crossing_to_ib' (Joe 1013).
assert PASS in ('oob', 'stalled', 'crossing_to_ib'), \
    'W_PASS must be oob, stalied or crossing_to_ib'.replace('stalied', 'stalled')
# THE EXHAUSTION EXIT IS SUPPRESSED IN THIS MODE, AND THIS IS THE ONE PIECE JOE DID NOT STATE.
# It is forced by his example. Exhaustion fires when the rider stalls and the 2 lines above it are
# inside the ex-fence 17/83 - which is EXACTLY the scenario he opened the mode with: *"Both lower
# kickstarts die on the next bar - ws2 73.41 and ws3 59.44 are already in-fence at the handoff /
# -this scenario invites a new mech to sit along side the 'oob' and 'stalled' modes"*. Measured: at
# the 17:39:10 handoff with the cap on, the kickstart takes ws1 at 17:39:15 and exhaustion ends the
# walk at 17:39:20, 5 s later, before any baton can pass. His ws2 pass at ~18:07 is unreachable
# with it live. So in this mode an in-fence line above the rider is not a dead end - it is the next
# rider, which is the whole point of the mode.
# WHAT ENDS THE WALK IS THEN THE WALK'S OTHER EXISTING EXITS - the ceiling, `final stalled`, the
# MAE stop, the >ws12 branch when it is on. NO END CONDITION OF HIS OWN HAS BEEN RULED FOR THIS
# MODE. Flagged, not invented.
XIB = PASS == 'crossing_to_ib'
#                                        THE BATON'S PASS TEST. Joe 1007: *"keeping the
#                                        x-cross and swapping oob with stalled"*.
# W_TRACE_NOX=1 records the x-cross exits that W_NOX=1 SUPPRESSES, and names them at the bar the
# ws12r oob run ends. Joe 1009: *"squashed was my shorthand - I was refering to the x-cross that we
# disabled 2 or 3 turns back"*. REPORTING ONLY - no branch reads it. Off by default because it
# restores the per-bar `xcond` call that W_NOX=1 saves.
TRACE_NOX = os.environ.get('W_TRACE_NOX', '0') == '1'
TRACE_LIN = os.environ.get('W_TRACE_LIN', '0') == '1'
# W_TRACE_HOLD=1 — REPORTING ONLY. Joe 1012: *"for each baton holder, add the stalled events"*.
# Every line that has HELD the baton on this leg keeps being watched after the baton leaves it, and
# its stall RISING EDGES are reported for the rest of the leg. His 1012 finding was ws8 stalling at
# 14:30:30 with its own reach in fence while the rider was ws10 - an exhaustion-shaped event the
# mech never looks at, because exhaustion is only ever tested on the CURRENT rider.
# The row carries the line's own r, its fence tag, its reach, and whether it is the rider, so the
# stall can be read against his definition: exhaustion is ws{tf} stalled, oob by design.
# EDGE-TRIGGERED per line. No branch reads it.
TRACE_HOLD = os.environ.get('W_TRACE_HOLD', '0') == '1'
# W_EXH_WHO — WHICH lines the exhaustion test is applied to.
#
# Joe 1012, closing the RCA: *"through the troubleshooting process you've been able to see why the
# current rider isn't the correct choice - sometimes lines printing momentum true don't make it to
# oob. remove the restriction"*. On the 07-17 leg ws6 stalled oob at 14:05:00 with ws7 73.25 and
# ws8 79.81 both in fence - exhaustion by the definition - and the mech never looked, because the
# rider was ws12.
#
#   'holders'  (default) every line that has HELD the baton on this leg is tested, the rider
#              included. A line stops being tested only when the leg ends.
#   'rider'    the pre-1012 behaviour, kept so the old runs reproduce.
#
# ORDER, MY CHOICE, STATED: the scan runs AFTER the rider's baton test, so a rider that can still
# hop advances instead of the leg exhausting. The alternative - scanning BEFORE the baton - would
# let a holder's exhaustion close a leg while lineage is actively climbing. Joe has not ruled it.
#
# WHEN SEVERAL HOLDERS EXHAUST ON ONE BAR every one is reported and the verdict is taken once. The
# verdict is "lineage is exhausted"; which line raised it is reporting, not a branch.
EXH_WHO = os.environ.get('W_EXH_WHO', 'holders')
assert EXH_WHO in ('holders', 'rider'), 'W_EXH_WHO must be holders or rider'
# W_SQX=1 TURNS JOE'S 1009 RULE ON. *"if oob ended before dwell completed, and a x-cross was
# squashed during the oob, then a B-trade is created and the A-trade is closed"*, and on the exit
# bar: *"re the causal oversight - we use the run ends timestamp to keep us live-ready"* - so A
# closes on the bar ws12r RETURNS IN-BOUNDS, the first bar where "the run ended short of the dwell"
# is knowable. Not the cross bar, which would need 3 bars of lookahead.
#
# ANY squashed cross inside the run counts - edge or already standing. RULED by Joe 1009 once the
# edge option was put to him with its count: *"I don't know how to handle x-cross correctly yet -
# the data will make it obvious in time so more hits are better than less"*. So the wide reading
# stands: 23 A-trades on the 94-day tape, against 10 for an EDGE-only test.
SQX = os.environ.get('W_SQX', '0') == '1'
# X-CROSS IS NOT AN EXIT. DELETED BY JOE 1011: *"'x-cross on ws1 · EXIT'. not good. drop this bias
# and delete 'x-cross as an exit' in the spec and related durable docs that are hindering you"*.
# The default is now OFF. The branch is left reachable by W_NOX=0 ONLY so pre-1011 runs can be
# reproduced; it is not part of the mech and must not be presented as one.
NOX = os.environ.get('W_NOX', '1') == '1'   # 1 disables the lineage walk's x-cross exit, leaving
#                                        `final stalled` as its only exit. Joe 1007 asked what
#                                        the swap left behind; this is the switch that shows it.
# ---- JOE'S DELEGATION GATE, 1008. ENV-SWITCHED AND OFF BY DEFAULT, so nothing is banked.
#
# Joe 1008: *"presently, whenever ws12r crosses to oob we automatically delegate to the >12 oob
# mech. sometimes, the delegation is a bad move ... to gate the delegation, we can look at ws60r's
# trajectory (per the traj spec). if ws60r's trajectory matches the oob side that ws12r is crossed
# into ... then we open the delegation gate"*.
#
assert not (SQX and not NOX), 'W_SQX=1 needs W_NOX=1 - with the x-cross live there is nothing ' \
                              'squashed for the rule to read'

# W_DGATE   'off'    as built - the handover fires on the oob run alone. THE DEFAULT.
#           'once'   tested ONCE, at the handover bar. If ws60r's trajectory is against the oob
#                    side there, this oob RUN never delegates - the lineage walk keeps the exit.
#
# 'retest' IS GONE, 1009. It was tested every bar while the oob run lasted and measured ZERO
# refusals at every width and both ceilings, so it was never a gate - it only delayed.
#
# THE DIRECTION SOURCE WAS REPLACED, 1009. It used to be `step_dir` - the sign of (ws60r now vs
# ws60r before its last step change) - a definition I wrote in 1007 for ws1r and then reused here
# "per the traj spec". JOE'S ESTABLISHED MECH IS `optimus9/compute/rule2_trajectory.py`, Joe 0924,
# task #22's first mechanism, and ITS OWN DOCSTRING diagnoses the bug: *"WHY THE BAR-TO-BAR READING
# WAS WRONG ... an unbroken-climb test returns 0 bars on every line"*. Measured on ws60r at
# 2026-08-22 13:33:50: step_dir's reference bar was 13:33:45, FIVE SECONDS back, on a line that had
# climbed +13.94 since 11:03. Every ws60r number taken before 1009 used step_dir and is void.
#
# `_trajmech.traj` is the ruled replacement - block samples, the run of same-signed sample diffs,
# the run's far end truncating the tail, a one-sample-at-a-time deferral through a flat tail, and
# `dir 0` on a wholly flat lookback. Its knobs, all Joe's unless marked:
#   W_TRAJ_BLOCK  60 bars = 5 min   Joe 1009 *"I think 5 minutes stays"*
#   W_TRAJ_TAIL   2 samples = 10 min   TRAJ_TAIL_TF_SAMP. Swept 1/2/3/6/12; all within 2.2 pts
#   W_TRAJ_LOOK   24 samples = 120 min  TRAJ_MULTI_TF_SAMP 2 x the 60 min TF-width
#   W_TRAJ_KIND   'close'   MINE - what one sample IS. Beats 'extreme' +22.4 vs +17.8
# TRAJ_MIN_TAIL_LIFE IS NOT HERE: Joe 1009 *"drop the tail-life deferral and keep #7 for dir 0
# only"*, after it overrode a correct call on 08-22's only paying reversal.
#
# ON `dir 0` the 4 mage/r rules decide, Joe 1008's #7: TRUE - pxs reverses - iff
# sign(ws60Mage - ws60r) == -(the oob side). It fired 1 time in 764 dwell-endings, and its own
# premise measured as a coin flip (sign(Mage-r) predicts ws60r's next move 49.7-53.6%), so it is
# recorded as Joe's rule with that caveat attached and nothing more.
#
# WHAT A CLOSED GATE DOES is unspecified, and there is only one other mech in the leg: the
# lineage walk keeps the exit (`final stalled` or the x-cross). Stated because it is a choice.
#
# THE TRAJECTORY IS READ AT THE BAR THE HANDOVER WOULD FIRE ON, never later. Reading it after that
# bar would be information past the decision.
#
# THE BAR IS THE LEG'S OWN. `oob_a` is set inside `run_leg` and resets at the leg's open, so a leg
# that opens mid-oob-run gets its own 6-minute clock. Measured on 08-22 leg 853: the global oob run
# starts 01:24:00 and my offline scripts put the dwell-ending at 01:30:05, but the leg opens
# 01:37:25 and THE CHAIN'S HANDOVER IS 01:43:35 - 13.5 min apart. The gate here has always read the
# leg's bar; it is the offline event lists that were wrong, including the one behind the +22.4.
#
# THE SIDE: inside run_leg the ws12r oob test is `goob(TRIG_TF, j, d)` on the LEG's own direction,
# so the oob side IS `d`. _delegate.py measured dr to add nothing
# - the oob side alone separated 71.3% / 37.5% against the three-way's 71.0% / 39.3%.
DGATE = os.environ.get('W_DGATE', 'off')
assert DGATE in ('off', 'once', 'traj', 'vote'), 'W_DGATE must be off, once, traj or vote'
# ---- W_DGATE='vote', Joe 1009. THE THREE-STEP DIRECTION, every step his.
# 1  THE 40-MINUTE VOTE on ws60r. *"let's replace diff weight with a simple how many UPS vs how
#    many DOWNS are in the tail"* / *"I meant the last 40 minutes"*. 40.0 min / the 5.0-min block =
#    8 diffs, counted not weighted. It replaces `travel` as the primary.
# 2  C3 BREAKS A TIE. *"maybe C3 is all we need - 1 miss out of 8 isn't trivial"* / *"we landed here
#    because of a tie in our test walk. let's apply C3"*. C3 is the traj majority across ws5-ws11,
#    which scored 7 of 8 on the 8 measured ties against Joe's own chart read - against 5 of 8 for
#    the 36-sample diff, 5 of 8 for the Mage count and 5 of 8 for the always-UP constant.
#    NOTE: on a tied bar the direction no longer comes from ws60r at all; it comes from ws5-ws11.
# 3  IF C3 ALSO TIES -> `travel`. NOT RULED BY JOE. C3 reads 7 lines so it can only tie on a flat
#    (3D 3U 1F); it did not tie once in the 56 readings measured across the 8 ties. Falling back to
#    `travel` is the minimum-change option and keeps a verdict always available. STATED, not chosen
#    by him.
#
# WHAT IS NOT CARRIED OVER: the 36-sample earliest-to-latest diff was built as a tie-breaker and
# C3 replaces it in that job, so it is not read here. `W_TRAJ_LOOK` 36 still bounds how far the
# flat-span deferral inside `travel` can reach, which is its only remaining effect.
VOTE_MIN = float(os.environ.get('W_VOTE_MIN', 40))
C3_LO = int(os.environ.get('W_C3_LO', 5))
C3_HI = int(os.environ.get('W_C3_HI', 11))
# W_VOTE_TIE picks what breaks a 4-4 vote: 'c3' is Joe's ruling, 'travel' is the ISOLATION ARM -
# the same 40-min vote with the old reading as the tie-break, so the vote's effect and C3's effect
# can be read apart instead of being one number.
VOTE_TIE = os.environ.get('W_VOTE_TIE', 'c3')
assert VOTE_TIE in ('c3', 'travel'), 'W_VOTE_TIE must be c3 or travel'
# W_TRACE_DGATE=1 adds ws60r's OWN reading to the trace at every bar the gate is or would be
# consulted. Joe 1009: *"there's also no events recorded from ws60r - they need to be visible to
# understnad its return"*. REPORTING ONLY - the extra rows carry no branch, so a run with the flag
# on and a run with it off take the same exits. It is off by default because it costs a `traj` call
# per oob-run OPENING (~5,700 over the 95-day tape) that the mech itself does not need.
TRACE_DG = os.environ.get('W_TRACE_DGATE', '0') == '1'
# ---- THE FULL SPEC, W_DGATE='traj', Joe 1009. OFF BY DEFAULT.
#
# 1  ws12r crosses to oob on the LEG's side. A-trade is already open. The dwell clock starts at
#    `oob_a` and RESETS whenever ws12r returns in-bounds.
# 2  an x-cross INSIDE the exhaustion window -> EXHAUSTION. Joe 1009: *"EXHAUSTION is the same as
#    weakness, and weakness signals a reveral. so if we get an x-cross inside ws12r's dwell, it
#    overrides ws60r (because ws60r is in a future that won't come) and creates a B-trade after
#    closing A-trade"*. ws60r is NOT consulted on this path.
# 3  the window completes with no x-cross -> ws12r is ESTABLISHED -> ws60r is consulted at the
#    dwell-ending (`oob_gate_bars`):
#      3a traj MATCHES the oob side  -> A stays open, the >ws12 mech owns the exit
#      3b traj AGAINST the oob side  -> wait for ws12r's own stall or x-cross AFTER the dwell, then
#                                       close A there. Joe 1009: *"we test ws60r at the end of the
#                                       dwell, and act on the stall/x-cross"*
# 4  the oob run ends before the dwell-ending -> no decision; the lineage walk keeps the exit.
#
# A's CLOSE IS B's OPEN. The chain alternates on every exit (`k = xk; d = -d` in the driver), so
# returning at the B bar closes A and opens B on the opposite side with no new driver code. Joe
# 1009: *"the traj decision allows for only one trade to exist"*.
#
# THE EXHAUSTION RULE IS JOE'S 0728/0729 MECH, `build_exhaust.py`: *"if x crosses r in the first 1/4
# seam"*. r oob and HOLDING past the 1/4 seam is ESTABLISHED -> continuation; x crossing back inside
# it means r never established -> exhaustion. 1/4 seam = TF minutes / 4 = TF x 3 bars.
#   W_EXH_FRAC  0.25   the window as a fraction of the trigger TF. Joe 1009: *"needs a metric-based
#                      sweep, but I don't hink it will be far from 0.25"*. SWEEPABLE, not settled.
#   XWOB_WS12X  4      bars the crossed side must HOLD before the cross is acted on. Joe 1009:
#                      *"let's pick a number between raw and safe - wob {knob:4, `XWOB_WS12X`}"*,
#                      between the raw cross bar and `build_exhaust.py`'s wob_n-1 = 8 bars.
#                      Joe 0729 in that file: *"Line values must be read at the RAW bar; a live
#                      system can only act at the CONFIRMED bar"*.
# THE CROSS IS THE STANDARD dr-BASED ONE, Joe 1009 *"yes - the standard dr based cross"*: on a leg
# with d > 0 the cross is ws12x going UNDER ws12r, on d < 0 it is ws12x going OVER. Identical to
# branch 1's condition at :300 and to the x-cross direction ruling of 0818.
# W_EXH_WIN picks what window the ws12x cross must land inside. Joe 1009 REVISED this: *"apply the
# 6 minute dwell gate to ws12r oob / if ws12x crosses ws12r during the dwell period, reverse the
# trade"*. So the window is the FULL DWELL, not the 1/4 seam it was built with.
#   'seam'   the 1/4 seam, TRIG_TF x W_EXH_FRAC = 3.0 min. As first built, Joe 0728/0729.
#   'dwell'  the whole oob_gate_bars dwell, 6.1 min. Joe 1009's revision. THE DEFAULT NOW.
EXH_WIN = os.environ.get('W_EXH_WIN', 'dwell')
assert EXH_WIN in ('seam', 'dwell'), 'W_EXH_WIN must be seam or dwell'
EXH_FRAC = float(os.environ.get('W_EXH_FRAC', 0.25))
# Joe 1009 raised the hold from 4 to 6: *"let's use 6 - it's safer"*. His 1009 words for the 4
# were *"let's pick a number between raw and safe"*; 6 is the safer end of that same choice. The 6
# he half-remembered was reent_xwob's 1007 ruling on one leg, which the 1008 sweep moved to 18 -
# a different knob, recorded so the two do not get conflated again.
XW12 = int(os.environ.get('XWOB_WS12X', 6))
TRAJ_BLOCK = int(os.environ.get('W_TRAJ_BLOCK', 60))
TRAJ_TAIL = int(os.environ.get('W_TRAJ_TAIL', 2))
TRAJ_LOOK = int(os.environ.get('W_TRAJ_LOOK', 24))
TRAJ_KIND = os.environ.get('W_TRAJ_KIND', 'close')
assert TRAJ_KIND in ('close', 'extreme'), 'W_TRAJ_KIND must be close or extreme'
EXH_BARS = (GATE_BARS + 1 if EXH_WIN == 'dwell'
            else int(round(TRIG_TF * EXH_FRAC * 60.0 / 5.0)))
_P('the exhaustion window is %r = %d bars = %.1f min; the ws%dx hold is %d bars = %.0f s'
   % (EXH_WIN, EXH_BARS, EXH_BARS * 5 / 60.0, TRIG_TF, XW12, XW12 * 5.0))
DIV_TFS = [int(s.strip().replace('ws', '').replace('r', '')) for s in W['div_lines'].split(',')]
EXF_HI = 100.0 - float(SC.LG['momo_fence_r']); EXF_LO = float(SC.LG['momo_fence_r'])
N = len(SC.ts)
# the loaded band must reach LIN_CEIL, which sits ABOVE the loop TF by LIN_HOP.
ALL_TF = list(range(SC.TF[0], max(CEIL_HI, LIN_CEIL) + 1))
RL = {t: SC.LD(t * 60, 'r')
      for t in range(SC.TF[0], min(max(CEIL_HI, LIN_CEIL) + 3, MAXTF + 1))}
R = {t: RL[t][:N] for t in RL}
X = {t: SC.LD(t * 60, 'x')[:N] for t in ALL_TF}
M2 = SC.Mg[2][:N]; G1 = SC.MTD['ws1'][:N]; PX = SC.PX[:N]
MG1 = SC.Mg[1][:N]        # ws1Mage, for the W_CP checkpoint. Same array as G1; named for the mech.
# RAW CLOSE for ws1-cp mode 2. `jig.divergence`'s docstring requires it - docs/o9-live/
# divergence_research.md:201, "DEMA-smoothing the price slope DESTROYS it ... The raw price slope is
# correct." It reached the tape cache on 1011 as `__close__`.
CLOSE_RAW = None if SC.CLOSE is None else np.asarray(SC.CLOSE, float)[:N]
assert CP_MODE == '1' or CLOSE_RAW is not None, (
    'ws1-cp mode 2 needs the RAW close and `__close__` is not on this tape. Rebuild the tape cache '
    'or set W_CP_MODE=1.')
if GC:
    import _gcgate
    GCG = _gcgate.GC(SC.LD(15, 'r'), SC.LD(30, 'r'), SC.LD(15, 'Mage'), SC.HI, SC.LO, N)
    _P('gc gate ready — gcws15r / gcws30r / gcws15Mage, step %d bars, span %d bars, gap %d bars, '
       'flip hold %d bars, hold mode %r'
       % (_gcgate.STEP, _gcgate.SPAN, _gcgate.GAP, _gcgate.FLIP_HOLD, GC_HOLD))
# THE ARMING LINE IS A KNOB, 1009. Joe: *"exit-armed needs ws2Mage crossing into oob ... this is a
# constant thorn in our side. let's swap ws2Mage with ws1Mage"*. The walk cannot exit before it
# arms, and 206 of 1,593 legs never armed at all - they summed -417.09, with 162 of them exiting on
# `mae breach`. W_ARM_TF 2 is the banked line; 1 is Joe's swap.
ARM_TF = int(os.environ.get('W_ARM_TF', 1))
MARM = SC.Mg[ARM_TF][:N] if ARM_TF in SC.Mg else np.asarray(SC.LD(ARM_TF * 60, 'Mage'), float)[:N]
_P('the arming line is ws%dMage (ruled ws1Mage, Joe 1009)' % ARM_TF)
# THE RULED CHECK, 1013. Joe: *"does this mean that when I say 'bank', you're not fixing the config
# as 'confirmed and in-use'?"* - it did not, and this is the guard. It only PRINTS: no default moves
# here, so no banked number shifts. An off-ruled run now says so before it reports a figure.
import _ruled
_EXP = os.environ.get('W_EXPERIMENT', '0') == '1'
for _rl in _ruled.line({'W_ARM': ARM, 'W_ARM_TF': ARM_TF,
                        'W_CEIL': _CEIL,
                        'W_LOOP_TF': LOOP_TF if LOOP_TF is not None else 'off',
                        'W_KICK': KICK, 'W_NO_GT12': '1' if NO12 else '0', 'W_PASS': PASS,
                        'W_CP_DWELL': CP_DWELL, 'W_CP_MODE': CP_MODE, 'W_STALL_N': STALL_N,
                        'W_LOOP_EXH': EXH_LOOP,
                        'W_IB_DWELL': os.environ.get('W_IB_DWELL', '2'),
                        'LIN_LASTMILE_KCKSTRT_TFCAP': LASTMILE_KICK_TFCAP},
                       lastmile=LASTMILE):
    _P(_rl)
# THE GATE, 1013. A printed warning only works if someone reads it, and the run that went wrong was
# one I did not read. An off-ruled run now REFUSES unless W_EXPERIMENT=1 says the deviation is
# deliberate - and that flag is itself printed, so a deliberate run says so in its own output.
_OFF = _ruled.check({'W_ARM': ARM, 'W_ARM_TF': ARM_TF,
                     'W_CEIL': _CEIL,
                     'W_LOOP_TF': LOOP_TF if LOOP_TF is not None else 'off',
                     'W_KICK': KICK, 'W_NO_GT12': '1' if NO12 else '0', 'W_PASS': PASS,
                     'W_CP_DWELL': CP_DWELL, 'W_CP_MODE': CP_MODE, 'W_STALL_N': STALL_N,
                     'W_LOOP_EXH': EXH_LOOP,
                     'W_IB_DWELL': os.environ.get('W_IB_DWELL', '2'),
                     'LIN_LASTMILE_KCKSTRT_TFCAP': LASTMILE_KICK_TFCAP},
                    lastmile=LASTMILE)
if _OFF and not _EXP:
    raise SystemExit(
        'REFUSED: %d knob(s) are off-ruled and W_EXPERIMENT is not set.\n%s\n'
        'Set W_EXPERIMENT=1 to run a deliberate deviation.'
        % (len(_OFF), '\n'.join('  %s running %s, ruled %s (%s)' % (k, a, v, w)
                                 for k, a, v, w, _q in _OFF)))
if _EXP:
    _P('W_EXPERIMENT=1 — this run is a DELIBERATE deviation from the ruled set')
BANK = {t: momo_bank(db, t) for t in ALL_TF}; db.disconnect()
ST = {}
STALL_RAW = {}        # the ungated stall mask per (tf, side). REPORTING ONLY, no branch reads it.
for t in ALL_TF:
    with momo_config(BANK[t]):
        with momo_window(int(BANK[t]['k_window']) * t):
            s_, n_ = int(MC.MOMO_STEP_BARS), int(MC.MOMO_SAMPLES)
    for dd in (-1, +1):
        _raw = stall_mask(RL[t], dd, STALL_N, s_, n_)
        # STALL IS EX-FENCE, SAME SIDE. Joe 1012: *"stall should be ex-fence (same-side)"*, after
        # confirming `jig.stall_mask` has NO fence condition at all - it only asks whether the line
        # made a new extreme in the last stall_n samples, so a line at 45.42 reads as stalled.
        #
        # GATED HERE, NOT IN THE PRODUCER. `jig.stall_mask` is shared with s46, ws5-fifo and the
        # other mechs; adding a fence inside it would change all of them at once. This build owns
        # its own gate and the producer stays untouched. STATED.
        _v = np.asarray(RL[t], float)[:N]
        _ok = (_v >= EXF_HI) if dd > 0 else (_v <= EXF_LO)
        ST[(t, dd)] = _raw[:N] & _ok
        STALL_RAW[(t, dd)] = _raw[:N]      # the ungated mask, for reporting only
REV = {t: _mage_rev(R[t], RREV) for t in DIV_TFS}
_P('stall_n ' + str(STALL_N) + '; stall gated to the same-side ex-fence %.0f/%.0f; %d of %d ws2 LONG stall bars survive the gate'
   % (EXF_LO, EXF_HI, int(ST[(2, +1)].sum()), int(STALL_RAW[(2, +1)].sum())))
_P('producers ready; LINEAGE ceiling ws%d (loopTF ws%s + lin_hop %d), >ws12 ceiling ws%d->ws%d, '
   'band ws%d-ws%d, gate %d bars at oob %.0f/%.0f, dip %.0f-%.0f dwell %d, stop %.2f'
   % (LIN_CEIL, LOOP_TF if LOOP_TF is not None else 'off', LIN_HOP, BASE_HI, CEIL_HI,
      ALL_TF[0], ALL_TF[-1], GATE_BARS, G_LO, G_HI, DIP_LO, DIP_HI, DIP_DWELL, MAE_STOP))

# ws60r AND ws60Mage, loaded only when the gate is on. `traj` is called per handover bar, not
# precomputed: the block walk reads at most TRAJ_LOOK x TRAJ_BLOCK bars and there are ~130
# handovers in a 95-day run, so the cost is nothing and nothing is cached that could drift.
if DGATE != 'off':
    from _trajmech import traj as _traj, sample_series as _samp
    R60 = np.asarray(SC.LD(60 * 60, 'r'), float)[:N]
    M60 = np.asarray(SC.LD(60 * 60, 'Mage'), float)[:N]
    _P('ws60r + ws60Mage loaded; gate %s, traj block %d tail %d look %d kind %s'
       % (DGATE, TRAJ_BLOCK, TRAJ_TAIL, TRAJ_LOOK, TRAJ_KIND))
else:
    _traj = _samp = R60 = M60 = None
VOTE_ND = int(round(VOTE_MIN / (TRAJ_BLOCK * 5 / 60.0)))
_sgn = lambda z: 0 if z == 0 else (1 if z > 0 else -1)

def vote40(j, d):
    """Joe's 40-minute UP/DOWN COUNT on ws60r. -> (dir, ups, downs, flats). Counted, not weighted."""
    sm = _samp(R60, j, TRAJ_BLOCK, TRAJ_LOOK, TRAJ_KIND, d)
    if len(sm) < VOTE_ND + 1:
        return 0, 0, 0, 0
    u = dn = fl = 0
    for i in range(VOTE_ND):
        z = _sgn(float(R60[sm[i][0]]) - float(R60[sm[i + 1][0]]))
        u += z > 0; dn += z < 0; fl += z == 0
    return _sgn(u - dn), u, dn, fl

def c3dir(j, d):
    """C3 - the traj majority across ws{C3_LO}r..ws{C3_HI}r. -> (dir, downs, ups, flats)."""
    u = dn = fl = 0
    for t in range(C3_LO, C3_HI + 1):
        if t not in R: continue
        r = _traj(np.asarray(R[t], float), j, TRAJ_BLOCK, TRAJ_TAIL, TRAJ_LOOK, TRAJ_KIND, d)
        u += r['dir'] > 0; dn += r['dir'] < 0; fl += r['dir'] == 0
    return _sgn(u - dn), dn, u, fl

def dgate_dir(j, d):
    """The delegation direction at bar j for a leg on side d. -> (dir, source, travel)

    dir is ws60r's trajectory per `_trajmech.traj`. On `dir 0` - a wholly flat lookback - Joe
    1008's 4 mage/r rules supply it from sign(ws60Mage - ws60r), which is the direction his rule
    implies: the Mage pulls r towards itself.
    """
    if DGATE == 'vote':
        v, u, dn, fl = vote40(j, d)
        if v != 0:
            return v, ('the %.0f-min vote, %d UP vs %d DOWN' % (VOTE_MIN, u, dn)), float(u - dn), \
                   _dgdet(j, d)
        c, cd, cu, cf = (0, 0, 0, 0) if VOTE_TIE == 'travel' else c3dir(j, d)
        if c != 0:
            return c, ('C3 broke the %d-%d tie — ws%d-ws%d traj %dD %dU %dF'
                       % (u, dn, C3_LO, C3_HI, cd, cu, cf)), float(cu - cd), _dgdet(j, d)
        r = _traj(R60, j, TRAJ_BLOCK, TRAJ_TAIL, TRAJ_LOOK, TRAJ_KIND, d)
        return r['dir'], (('the vote tied %d-%d — travel decides (W_VOTE_TIE=travel)' % (u, dn))
                          if VOTE_TIE == 'travel' else
                          ('the vote AND C3 both tied (%d-%d, %dD %dU %dF) — travel decides'
                           % (u, dn, cd, cu, cf))), r['travel'], _dgdet(j, d, r)
    r = _traj(R60, j, TRAJ_BLOCK, TRAJ_TAIL, TRAJ_LOOK, TRAJ_KIND, d)
    if r['dir'] != 0:
        return r['dir'], 'traj', r['travel'], _dgdet(j, d, r)
    g = float(M60[j]) - float(R60[j])
    if g == 0:
        return 0, 'flat and Mage == r', 0.0, _dgdet(j, d, r)
    return (1 if g > 0 else -1), 'the 4 mage/r rules', g, _dgdet(j, d, r)

DG_READ = {}      # (bar, side) -> ws60r's reading as ONE SHORT CELL, for the report's own
                  # column. Written only by `_dgdet`, read only by a report. Nothing branches on
                  # it, and it is keyed by side because the traj is read on the leg's dr.

def _dgdet(j, d, r=None):
    """EVERY NUMBER WS60r RETURNED AT BAR j, as one trace string. Joe 1009.

    Nothing branches on this. It exists so a walk shows what ws60r SAID, not only what the gate
    did with it - in particular the three readings that are invisible otherwise: the reading at
    the oob-run opening, the reading at a run that ends before the dwell completes, and the tail
    the traj actually used.
    """
    if r is None:
        r = _traj(R60, j, TRAJ_BLOCK, TRAJ_TAIL, TRAJ_LOOK, TRAJ_KIND, d)
    f = lambda v: ('%+.4f' % v) if np.isfinite(v) else 'n/a'
    rb = r['reversal_bar']
    DG_READ[(j, d)] = '%.2f %s %s' % (float(R60[j]),
                                      {1: 'UP +1', -1: 'DOWN -1', 0: 'FLAT 0'}[int(r['dir'])],
                                      f(float(r['travel'])))
    return ('ws60r %.2f, ws60Mage %.2f, Mage-r %+.2f | traj dir %s, travel %s over its tail of %d '
            'samples = %.1f min (run %d same-signed, %d deferred, the dr-opposed extremum at %s)'
            % (float(R60[j]), float(M60[j]), float(M60[j]) - float(R60[j]),
               {1: 'UP +1', -1: 'DOWN -1', 0: 'FLAT 0'}[int(r['dir'])], f(float(r['travel'])),
               int(r['tail_used']), r['tail_used'] * TRAJ_BLOCK * 5 / 60.0, int(r['run']),
               int(r['deferred']), SC.U(rb) if rb is not None else 'none'))

# ---- THE TWO NEW BATON PREDICATES. Built only when asked for, so the default run is untouched.
MOMT = {}
MOMD = {}
RPRED = {}
# THE dws TIMEFRAMES, read off the registered config, not written here. Joe ruled the timeframe
# 1013: *"timeframe 8 ,10,15"* - each dws line is measured on the timeframe it is BUILT on, not on
# the doubled one its r-config stands in for. So dws8r takes BANK[8] and the momo window
# k_window x 8 = 48 min, exactly as ws8r does.
DWS_TF = {_n: int(_v[0]) // 60 for _n, _v in SC.DWS_SPEC.items()}
# LAST-MILE NEEDS MOMT WHATEVER W_BATON SAYS. Joe 1013's `towards dr` is *"has momentum"* AND not
# tagged, and "has momentum" is the mom-true mask. Without this the mode would silently read an
# empty MOMT and call every line not-towards-dr, which exhausts the walk on its first bar.
if BATON in ('momentum', 'either') or LASTMILE:
    from _momtrue import momtrue_mask
    from optimus9.orchestration.build_ws_lines import HOURS, WARMUP
    for _bt in ALL_TF:          # NOT `_t` - that is the module's `time` handle, used by _P
        MOMT[_bt] = momtrue_mask(RL[_bt], _bt, BANK[_bt], SC.EM, HOURS, WARMUP, 'gated', N,
                                 log=lambda z: None)
    _P('mom-true masks ready for ws%d-ws%d' % (ALL_TF[0], ALL_TF[-1]))
    # KEYED BY NAME, never by timeframe. MOMT is keyed by the timeframe int and dws8r sits on tf 8,
    # so a shared dict would have dws8r overwrite ws8. `line_id` puts the name in the mask cache
    # key too, for the same reason.
    for _dn, _dtf in sorted(DWS_TF.items(), key=lambda kv: kv[1]):
        MOMD[_dn] = momtrue_mask(SC.LDN(_dn), _dtf, BANK[_dtf], SC.EM, HOURS, WARMUP, 'gated', N,
                                 log=lambda z: None, line_id=_dn)
    if MOMD:
        _P('mom-true masks ready for ' + ', '.join('%s on tf %d (window %d min)'
           % (_dn, _dtf, int(BANK[_dtf]['k_window']) * _dtf)
           for _dn, _dtf in sorted(DWS_TF.items(), key=lambda kv: kv[1])))
if BATON in ('rpred', 'either'):
    from optimus9.compute.breaching_line import predict_breach as _pb
    from optimus9.constants import FENCE_HI as _FH, FENCE_LO as _FL
    for _bt in ALL_TF:          # NOT `_t` - see above
        RPRED[_bt] = _pb(np.asarray(RL[_bt], float)[:N],
                         np.asarray(SC.LD(_bt * 60, 'm'), float)[:N],
                         np.asarray(SC.LD(_bt * 60, 'Mage'), float)[:N],
                         SC.HI, SC.LO, _FH, _FL)
    _P('r-pred ready for ws%d-ws%d, fence %.0f/%.0f' % (ALL_TF[0], ALL_TF[-1], _FH, _FL))

def baton_ok(t, j, d):
    """May line `t` take the baton at bar `j` on side `d`? ONE place, so an arm is one knob."""
    if BATON == 'oob':
        return ST[(t, d)][j] if PASS == 'stalled' else oobf(t, j, d)
    if BATON == 'momentum':
        return bool(MOMT[t][d][j])
    if BATON == 'rpred':
        return int(RPRED[t][j]) == (1 if d > 0 else -1)
    return bool(MOMT[t][d][j]) or int(RPRED[t][j]) == (1 if d > 0 else -1)

HTF_M = {}
if HTF_MOM:
    from _momtrue import momtrue_mask as _mtm
    from optimus9.orchestration.build_ws_lines import HOURS as _H, WARMUP as _WU
    _db2 = DatabaseManager(**get_db_config()); _db2.connect()
    for _ht in range(2, HTF_MOM_TOP + 1):
        try:
            _hr = np.asarray(SC.LD(_ht * 60, 'r'), float)[:N]
            HTF_M[_ht] = _mtm(_hr, _ht, momo_bank(_db2, _ht), SC.EM, _H, _WU, 'gated', N,
                              log=lambda z: None)
        except Exception as _e:
            _P('W_HTF_MOM: ws%d has no mom-true mask (%s)' % (_ht, str(_e)[:50]))
    _db2.disconnect()
    _P('W_HTF_MOM ready — ws%d-ws%d, N %d consecutive lines above the rider'
       % (min(HTF_M), max(HTF_M), HTF_MOM_N))

def htf_hold(rider, j, d):
    """Does the HTF momentum hold stop the leg closing at bar `j`? -> a trace string, or None.

    The longest run of CONSECUTIVE mom-true lines strictly above `rider`, up to HTF_MOM_TOP. A run
    of HTF_MOM_N or more holds the leg open. CAUSAL: every mask read is at bar `j`.
    """
    if not HTF_MOM or rider is None:
        return None
    best = 0; cur = 0; b0 = b1 = None; s0 = None
    for t in range(rider + 1, HTF_MOM_TOP + 1):
        if t not in HTF_M:
            cur = 0; continue
        if bool(HTF_M[t][d][j]):
            if cur == 0: s0 = t
            cur += 1
            if cur > best: best, b0, b1 = cur, s0, t
        else:
            cur = 0
    if best < HTF_MOM_N:
        return None
    return ('HTF MOMENTUM HOLD — ws%d-ws%d, %d consecutive lines above the rider ws%d are mom-true '
            'toward the %s board (N %d). the leg does NOT close here.'
            % (b0, b1, best, rider, 'HIGH' if d > 0 else 'LOW', HTF_MOM_N))

def cp2(j, d):
    """ws1-cp MODE 2 at bar `j`: the ws1x/ws1Mage cross, its wob hold, and the divergence.

    -> the `anchor_floater` dict when bar `j` is a confirmed mode-2 cp, else None.

    CAUSAL BY CONSTRUCTION: the cross sits at `j - CP_XWOB + 1`, the hold runs forward to `j`, and
    `anchor_floater` reads nothing past `j`. The assert below is the invariant, not a comment -
    stamping the cross bar itself would act on a hold that is not knowable for CP_XWOB-1 more bars.
    """
    c = j - CP_XWOB + 1
    if c < 1:
        return None
    assert c <= j, 'the mode-2 cross bar is ahead of its own stamp bar'
    # ws1Mage oob on the TARGET BOARD at the cross
    if not ((float(MG1[c]) >= SC.HI) if d > 0 else (float(MG1[c]) <= SC.LO)):
        return None
    x, m = X[1], MG1
    if d > 0:        # HIGH board: ws1x crosses UNDER ws1Mage
        if not (float(x[c]) < float(m[c]) and float(x[c - 1]) >= float(m[c - 1])):
            return None
        if not all(float(x[c + q]) < float(m[c + q]) for q in range(CP_XWOB)):
            return None
    else:            # LOW board: ws1x crosses OVER ws1Mage
        if not (float(x[c]) > float(m[c]) and float(x[c - 1]) <= float(m[c - 1])):
            return None
        if not all(float(x[c + q]) > float(m[c + q]) for q in range(CP_XWOB)):
            return None
    res = anchor_floater(R[1], CLOSE_RAW, d, j)
    if res is None or int(res['fired']) != d:
        return None
    return res

def bnd(t, k, d):
    v = float(R[t][k])
    if d > 0: return 'O' if v >= SC.HI else ('x' if v >= EXF_HI else '.')
    return 'O' if v <= SC.LO else ('x' if v <= EXF_LO else '.')
oobf = lambda t, k, d: (float(R[t][k]) >= SC.HI) if d > 0 else (float(R[t][k]) <= SC.LO)
# the >ws12 mech's own oob test, on the oob_gate_fence read above. Nothing else
# uses it: the KICKSTART and the baton stay on `oobf` and the global 15/85.
goob = lambda t, k, d: (float(R[t][k]) >= G_HI) if d > 0 else (float(R[t][k]) <= G_LO)
# THE LINEAGE WALK'S x-CROSS TARGET, NOW KNOB-DRIVEN. 1008. Joe: *"go for B"*.
#
# WAS, and it is still what x_tgt_role r + x_tgt_tfs both + x_tgt_fence 1 reproduces:
#     the rider's x against the r of h+1 AND h+2, with BOTH targets in-fence.
# NOW, #61 arm B:
#     the rider's x against the `b` line of h+1 ONLY, with no in-fence test on it.
#
# THE THREE KNOBS, and what each value means:
#   x_tgt_role   'b'     the LINE the x must cross. The five wsf roles are the same oscillator at
#                        five speeds - r is k 5/8/7, x is bb 5/0.35, m is bb 6/0.4, Mage is
#                        bb 38/0.93, and b is bb 49/0.95, the SLOWEST of them.
#   x_tgt_tfs    'next'  which TFs above the rider carry the target. 'both' = h+1 and h+2,
#                        'next' = h+1 only, 'self' = h itself.
#   x_tgt_fence  0       1 = the target must also be in-fence (neither oob nor past the ex-fence),
#                        which is what `bnd(t, k, d) == '.'` tested. 0 = no such test.
#
# THE IN-FENCE TEST IS READ ON THE TARGET LINE, not on r, so that it keeps testing the same lines
# it crosses when the role moves. Stated because #61 does not say.
XT_ROLE, XT_TFS = str(W['x_tgt_role']), str(W['x_tgt_tfs'])
XT_FENCE = int(W['x_tgt_fence'])
XT_OFF = {'both': (1, 2), 'next': (1,), 'self': (0,)}[XT_TFS]
TGT = R if XT_ROLE == 'r' else {t: SC.LD(t * 60, XT_ROLE)[:N] for t in RL}
def xcond(h, k, d):
    tt = [h + o for o in XT_OFF]
    if any(t not in TGT for t in tt): return False
    xv = float(X[h][k])
    if not all((xv < float(TGT[t][k])) if d > 0 else (xv > float(TGT[t][k])) for t in tt):
        return False
    if not XT_FENCE: return True
    return all(((float(TGT[t][k]) < EXF_HI) if d > 0 else (float(TGT[t][k]) > EXF_LO))
               for t in tt)
_lp = lambda n: ' (after %d loop%s)' % (n, '' if n == 1 else 's') if n else ' (no loop yet)'


def gc_defer(j, d, hist):
    """Do both gc gates pass at bar `j` for a leg on side `d`? -> a trace string, or None.

    Gate 1 position: gcws15r AND gcws30r both on the wrong side of 50 for the leg.
    Gate 2 trajectory: the QUALIFIED sign of the g15r anchor-to-now diff equals the leg side.
    """
    if not GCG.pos(j, d):
        return None
    sg = GCG.qualified_sign(j, d, hist)
    if sg != d:
        return None
    a = GCG.anchor(j, d)
    if a is None:
        return None
    ab, vb, diff, gaps = a
    # the position gate reads gcws30r ONLY (Joe 1012). gcws15r is printed for context because it
    # is the TRAJECTORY line, and it may sit anywhere in fence - the old string claimed both were
    # on the wrong side of 50, which was wrong the moment the gate stopped testing g15r.
    return ('gcws30r %.2f is %s 50 (position gate, g30r only); g15r %s from its %s extrema %.2f at '
            '%s (validated %s, %d gap%s walked), diff %+.2f; g15r is %.2f now'
            % (float(GCG.r30[j]), 'under' if d > 0 else 'over',
               'falling' if d < 0 else 'rising', 'high' if d < 0 else 'low',
               float(GCG.r15[ab]), SC.U(ab), SC.U(vb), gaps, '' if gaps == 1 else 's', diff,
               float(GCG.r15[j])))


def exhausted(rider, j, d, lin_ceil):
    """Is the walk exhausted at bar `j`? -> a trace string, or None.

    Joe 1010: *"the 2 tfs above are in fence"*. The reach is the baton's own, rider+1 ..
    rider+LIN_HOP, bounded by LINEAGE's ceiling - never by the loop TF. IN FENCE is the baked
    ex-fence 17/83 - the '.' tag -
    ruled by Joe 1010: *"this should already be the mech's baked code"*.
    """
    up = [t for t in range(rider + 1, min(rider + LIN_HOP, lin_ceil) + 1) if t in R]
    if not up:
        return None
    if not all(bnd(t, j, d) == '.' for t in up):
        return None
    word = 'all inside the ex-fence %.0f/%.0f' % (EXF_LO, EXF_HI)
    return 'the %d above are %s (%s)' \
        % (len(up), word, ', '.join('ws%d %.2f %s' % (t, float(R[t][j]), bnd(t, j, d))
                                    for t in up))


def towards_dr(t, j, d, xtag):
    """JOE 1013, HIS TWO STATES: *"I'd calculate 'towards dr' based on states: has momentum / has
    not been tagged as 'crossed to ib'"*. Nothing about the line's position is read - a line can be
    in-fence and still be heading to the target end, which is what qualified ws7 on the 07-18 16:07
    walk at 18:05:35 when it sat at 79.93.
    """
    return bool(MOMT[t][d][j]) and t not in xtag


def blast_radius(k0, d):
    """JOE 1013'S BLAST-RADIUS GATE. -> (fires, verdict bar, a trace string).

    Walked from the handoff `k0` for LINFIN_WALK bars. A line votes AWAY at a bar when it is oob on
    the target end AND further from that end than it was at `k0`. The gate fires when
    LINFIN_AWAY_MIN or more lines have voted at least once.

    CAUSAL: the verdict bar is k0 + LINFIN_WALK, so every bar read is at or before the bar the
    verdict acts on. The walk is a DELAY, which is Joe's own word for it.
    """
    top = (LOOP_TF if LOOP_TF is not None else LIN_CEIL)
    end = min(k0 + LINFIN_WALK, N - 1)
    votes = {}
    for t in range(1, top):
        if t not in R:
            continue
        a = R[t]
        for k in range(k0, end):
            if oobf(t, k, d) and ((float(a[k]) < float(a[k0])) if d > 0
                                  else (float(a[k]) > float(a[k0]))):
                votes[t] = votes.get(t, 0) + 1
    assert end >= k0, 'the blast-radius walk ran backwards'
    fired = len(votes) >= LINFIN_AWAY_MIN
    txt = ('%d line(s) voted AWAY over the %d-bar walk, min %d (%s)'
           % (len(votes), LINFIN_WALK, LINFIN_AWAY_MIN,
              ', '.join('ws%d %d of %d' % (t, v, LINFIN_WALK) for t, v in sorted(votes.items()))
              or 'none'))
    return fired, end, txt


def exhausted_cycle(rider, j, d, xtag):
    """THE LAST MILE'S EXHAUSTION. -> a trace string, or None.

    JOE 1013: *"the end is the EXHAUSTION event. I'm sure that this is the existing mech"* - and it
    is. This is `exhausted()` with ONE substitution: its inner test changes from "all the reach is
    inside the ex-fence" to "none of the reach is towards-dr". The reach is unchanged, rider+1 ..
    rider+LIN_HOP, which is Joe's 1010 *"the 2 tfs above are in fence"*.

    WHY THE SUBSTITUTION. Measured on the 07-18 16:07 LONG's last mile, board HIGH:
        2026-07-18 17:39:20  rider ws1, reach ws2 73.41 and ws3 59.44, both inside the ex-fence, so
                             the EXISTING test fires 5 s after the kickstart and the walk is over.
                             Both are untagged and mom-true - they are climbing to oob, reaching
                             95.64 and 100.00 within 9 min - so the cycle test does NOT fire.
        2026-07-18 18:12:00  rider ws4, reach ws5 71.72 and ws6 84.38. ws6 is above the ex-fence 83
                             so the EXISTING test does NOT fire. Both are tagged `left-target-dr`,
                             so the cycle test DOES.
    One change, both bars corrected.

    THE STALL GATE IS DROPPED, Joe 1013 verbatim: the cycle test *"replaces the stall gate ONLY for
    the last mile mech"*. Measured: at 2026-07-18 18:12:00 the rider ws4 is NOT stalled, so the
    `on_stall` gate alone would block the end. The armed walk keeps its stall gate untouched.

    THE REACH IS CAPPED AT THE LOOP TF HERE, Joe 1013: *"no line in the rider's reach passes
    loop-tf"*, and his reason - *"ws{loop-tf}r recyling the loop (to ws1) on its oob event"* means
    the lines above it are never the walk's business. An empty reach at that cap IS exhaustion.
    """
    top = min(rider + LIN_HOP, LIN_CEIL)
    if LOOP_TF is not None:
        top = min(top, LOOP_TF)
    up = [t for t in range(rider + 1, top + 1) if t in R]
    if not up:
        return ('the reach is empty at the loop TF ws%s - nothing above ws%d is this walk\'s '
                'business' % (LOOP_TF, rider))
    live = [t for t in up if towards_dr(t, j, d, xtag)]
    if live:
        return None
    return 'none of the %d above is towards-dr (%s)' % (
        len(up), ', '.join('ws%d %.2f %s' % (
            t, float(R[t][j]),
            'tagged `left-target-dr` %s' % SC.U(xtag[t]) if t in xtag else 'no momentum')
            for t in up))


xund = lambda t, k, d: (float(X[t][k]) < float(R[t][k])) if d > 0 else (float(X[t][k]) > float(R[t][k]))
# THE DIP IS A BAND, 1008. Joe: *"we'll use a small 100-{knob:53} fence, ie 47 to 53"* /
# *"fence 53 + dwell 6"*.
#
# WAS: `indip = G1 < dip_mid 50` for a LONG leg, `> 50` for a SHORT. A single level, and the dwell
# counted bars on the far side of it. At 17:54 on 09-25 that rejected the dip SEVEN times - the
# longest sub-50 run is 4 bars against a dwell of 12.
#
# NOW: the dip region is the BAND dip_lo 47 to dip_hi 53, symmetric about dip_mid 50.
#
# THE ENTRY IS STILL dr-ALIGNED, which the band alone is not: a LONG leg must come DOWN into the
# band from above DIP_HI, and a SHORT leg must come UP into it from below DIP_LO. Without this the
# band test is direction-blind and `dr_aligned` 1 would be contradicted.
#
# ONE EDGE, STATED: a dip that goes DEEPER than DIP_LO leaves the band and breaks the dwell, so a
# deeper dip can disqualify. The alternative - a one-sided `G1 <= DIP_HI` for a LONG - has no such
# edge. Joe's words name the band, so the band is what is built.
inband = lambda k: DIP_LO <= float(G1[k]) <= DIP_HI
indip = lambda k, d: inband(k)
entered = lambda k, d: (inband(k) and not inband(k - 1)
                        and ((float(G1[k - 1]) > DIP_HI) if d > 0
                             else (float(G1[k - 1]) < DIP_LO)))
WANT = lambda d: (-1 if d > 0 else +1)
def box(hdr, rr):
    w = [max(len(hdr[i]), max((len(str(x[i])) for x in rr), default=0)) for i in range(len(hdr))]
    B = lambda s, m, e: s + m.join('─' * (x + 2) for x in w) + e
    print(B('┌', '┬', '┐'))
    print('│' + '│'.join(' ' + hdr[i].center(w[i]) + ' ' for i in range(len(hdr))) + '│')
    print(B('├', '┼', '┤'))
    for x in rr:
        print('│' + '│'.join(' ' + str(x[i]).ljust(w[i]) + ' ' for i in range(len(hdr))) + '│')
    print(B('└', '┴', '┘'))

def run_leg(k0, trade_side):
    """ONE LEG'S WALK, from the handoff bar to the bar the trade closes.

    -> (the bar it ends on, why, the MAE, the ceiling bar, the handoff, the trace rows).

    The exits, in the order the bar tests them: the MAE stop, the W_LOOP reset and its close, the
    baton pass, the cycle exhaustion, and the >ws12 mech's own path when it is on.

    THE PARAMETERS THAT WERE HERE AND ARE GONE, 1014: `jump_off`, `state`, `rider0`, `looped_once`
    and `loop_oob0` carried walk state across the pieces of the oob hack's keep-going layer. That
    layer was removed on Joe's ruling that *"the oob hack state changes do not have any bearing on
    an open trade"*, so nothing passed them and they were four arguments a reader had to disprove.
    `W_LOOP_STATE_CARRY` went with them - it guarded `loop_oob0` and so could not change anything.
    """
    # trade_side is the dr at the trade's open: +1 a SHORT, -1 a LONG. The board the walk works on
    # is the end the trade is HEADING TO, which is the opposite end. Resolved here, once.
    assert int(trade_side) in (-1, 1), (
        "run_leg needs the trade's side at its open, +1 (SHORT) or -1 (LONG), got %r. A side of 0 "
        "means global dr has not resolved yet and the target board cannot be set." % (trade_side,))
    d = -int(trade_side)
    _board0 = d            # the board is set once; this is what the per-bar invariant checks
    # THE ADVERSE DIRECTION IS AGAINST THE TRADE. Joe 1012: the MAE stop *"is incorrect, likely
    # to be a casualty of wrong side. I'm basing it your 2.5% being almost exactly the profit we've
    # claimed in this SHORT trade"*. He is right: on the 07-18 02:33 SHORT the stop fired at
    # 05:55:10 on a 2.5036% PRICE FALL, which is that short's profit, not its drawdown.
    #   trade_side +1 = a SHORT, so ADVERSE is price RISING  -> sgn -1
    #   trade_side -1 = a LONG,  so ADVERSE is price FALLING -> sgn +1
    # i.e. sgn = -trade_side, and `adv = -((px - p0) / p0 * 100 * sgn)` is then the move AGAINST
    # the trade. The same sgn gives the realised number its sign.
    sgn = -int(trade_side)
    assert sgn in (-1, 1)
    tr = []; p0 = float(PX[k0])
    # ARMED AT THE HANDOFF in last-mile mode. The trade is already open - the extension handed this
    # walk a live leg, so there is no arming event to wait for. Every other mode arms on its own
    # event and this stays False. Joe 1013: *"fires kickstart at the last-mile handoff"*.
    armed = LASTMILE
    # JOE 1013'S BLAST-RADIUS GATE, before the jumpstart can place a rider. The walk is HELD for
    # LINFIN_WALK bars; if the lines under the loop TF have left the target end, the jumpstart does
    # not fire and the held close goes at the verdict bar.
    if LASTMILE:
        _bf, _bv, _bt = blast_radius(k0, -int(trade_side))
        if _bf:
            return _bv, 'blast radius - the jumpstart did not fire', 0.0, None, None, [
                (k0, 'LAST MILE HELD — the blast-radius walk opens'),
                (_bv, 'BLAST RADIUS — %s. the jumpstart does not fire and the held close goes '
                      'here' % _bt)]
    rider = None; mae = 0.0
    jump_off = False       # set by the W_LOOP reset; the jumpstart may not arm after it
    looped_once = False    # the reset to ws1 is one-time per leg
    loop_oob = {}          # ws{loop TF}r's oob state at this bar
    loop_oob_prev = dict(loop_oob)     # so the edge is NOT re-detected at a piece boundary
    loop_close = False     # the loop reset ws1 in; test its weakness on the next bar
    rider_oob = False      # W_PASS 'crossing_to_ib': has THIS rider been oob since it took over
    xib_stall_said = False  # one trace row per rider when crossing_to_ib ignores a stall
    # JOE 1013'S `left-target-dr` TAG SET. *"it would be less cost to tag {TFs < loop-tp} lines with
    # 'left-target-dr' as they cross to ib, and then clear all tags when lineage finishes its walk.
    # your code, your call"*. A dict {tf: the bar it crossed}, LOCAL TO THE WALK, so it is cleared
    # when the walk returns - no reset code and no state that can leak into the next leg. One
    # comparison per TF per bar, and nothing is computed for TFs at or above the loop TF.
    xtag = {}
    if LASTMILE:
        tr.append((k0, 'LAST MILE — armed at the handoff, no ws1-cp and no %sMage arm; the '
                       'KICKSTART takes the next bar (W_KICK %r, >ws12 mech %s)'
                   % (ARM_TF, KICK, 'off' if NO12 else 'ON')))
    looped = 0             # W_LOOP_TF: how many times the rider has been reset to ws1
    exh_armed = False      # W_LOOP_EXH 'after_loop': the exhaustion exit goes live on the 1st loop
    hit_from = None        # the rider the loop fired from, for the trace line only
    lin_prev = None        # W_TRACE_LIN: the last (rider, baton available, stalled) reported
    held = []              # every line that has held the baton, in order. WALK STATE, not
#                            reporting: W_EXH_WHO='holders' scans it. It used to be filled only
#                            under `if TRACE_HOLD`, so the holder scan silently fell back to the
#                            rider alone whenever W_TRACE_HOLD was 0. Fixed 1012.
    held_st = {}           # each held line's stall state on the previous bar, for the trace rows
    loop_open = None       # the bar the current W_LOOP BEGAN on - its arming or completing ws1-cp
    loop_end_armed = False  # True once the walk has REACHED the loop TF. Only then does a ws1-cp
#                             END the W_LOOP, and only then are a stall and an exhaustion held.
    loop_stall_said = False  # the held-stall row is emitted once per open loop, not per stall bar
    gc_hold = None         # W_GC: the bar an exhaustion verdict was deferred on
    gc_said = False        # the no-backstop row is emitted once per hold, not per bar
    gc_hist = {}           # W_GC: bar -> the raw g15r trajectory sign, for the 12-bar blip rule
    cp_run = 0             # how many CONSECUTIVE bars the ws1-cp condition has held, for W_CP_DWELL
    cp_n = 0               # how many ws1-cp resets this leg has taken
    ceil = BASE_HI; ceil_bar = None
    oob_a = None; hand = None; dip = None; conf = None; ib_run = 0
    gate_shut = False      # latched when the gate refused THIS oob run
    exh_x = None           # W_DGATE 'traj': the bar an in-window x-cross fired, awaiting XW12
    b_armed = False        # path 3b: traj said reverse, waiting for ws12r's stall or x-cross
    b_x = None             # that post-dwell x-cross, awaiting XW12
    nox_x = None           # W_TRACE_NOX: the first SUPPRESSED walk x-cross inside this oob run
    nox_r = None           # the rider it fired on
    nox_e = None           # was that cross an EDGE on its rider, or already standing?
    for j in range(k0 + 1, N):
        # THE BOARD NEVER MOVES INSIDE A TRADE. Joe 1012: the side *"can only be set once at the
        # open of the trade"*. This is an assert and not a comment because the bug it replaces was
        # exactly a mid-walk reassignment of `d`, and it was invisible in the rows it produced.
        assert d == _board0, (
            'the target board moved mid-walk, %+d -> %+d. It is set once at the trade open and '
            'every test downstream reads it.' % (_board0, d))
        # JOE 1013'S `left-target-dr` TAG, MAINTAINED AT THE TOP OF THE BAR, BEFORE ANY `continue`.
        # IT HAS TO BE HERE. Placed lower down - after the baton block - it was skipped on every bar
        # that `continue`s, and a baton pass is one of those bars. Measured on the 07-18 16:07
        # LONG: ws6 crossed oob -> ib at 2026-07-18 18:12:00, the same bar the baton passed to ws5,
        # so the cross was missed and ws6 was not tagged until its NEXT cross at 18:13:15. Same
        # class of bug as the `held` holder list, fixed 1012 for the same reason.
        if LASTMILE:
            for _tt in range(1, LOOP_TF if LOOP_TF is not None else LIN_CEIL):
                if _tt in R and _tt not in xtag and oobf(_tt, j - 1, d) and not oobf(_tt, j, d):
                    xtag[_tt] = j
        # THE oob-STATE SNAPSHOT, TAKEN AT THE TOP OF THE BAR BEFORE ANY `continue`, for the same
        # reason the `left-target-dr` tag is maintained here: a bar that `continue`s must not skip
        # it, or the edge is missed. `loop_oob` for THIS bar is computed below, just before the
        # loop block; this carries the PREVIOUS bar's reading forward.
        loop_oob_prev = dict(loop_oob)
        px = float(PX[j])
        if np.isfinite(px) and px > 0:
            adv = -((px - p0) / p0 * 100.0 * sgn)
            if adv > mae: mae = adv
            if adv > MAE_STOP:
                tr.append((j, 'MAE BREACH %.4f%% over %.2f%% - chain stops for review'
                           % (adv, MAE_STOP)))
                return j, 'mae breach', mae, ceil_bar, hand, tr
        # the ws12r oob run on the leg's dr side, and the handover
        if (not NO12) and goob(TRIG_TF, j, d):
            if oob_a is None:
                oob_a = j
                # DEAD LOOP DELETED 1008. It read
                #     for q in range(j + 1, min(N, j + SIG_WIN) + 1):
                #         if not oobf(TRIG_TF, q, d): break
                # and assigned nothing, returned nothing and had no side effect - the branch-1
                # scan immediately below is the real one. Its only behaviour was a CRASH: the
                # bound is min(N, ...) + 1 where the real loop uses min(N - 1, ...) + 1, so q
                # reached N and indexed one past the end of a 1,632,960-bar line. It killed the
                # overnight sweep at the tape end on configs whose chain ran within SIG_WIN
                # (72 bars) of the last bar. Deleting it changes no result.
                u = lambda z: float(X[TRIG_TF][z]) < float(R[TRIG_TF][z])
                for q in range(j + 1, min(N - 1, j + SIG_WIN) + 1):
                    if not goob(TRIG_TF, q, d): break
                    c = (u(q) and not u(q - 1)) if d > 0 else ((not u(q)) and u(q - 1))
                    if c:
                        tr.append((q, 'branch 1 cross — RECORDED, not acted on (ws%dx %.2f vs r %.2f)'
                                   % (TRIG_TF, float(X[TRIG_TF][q]), float(R[TRIG_TF][q]))))
                        break
                if DGATE in ('traj', 'vote') and TRACE_DG:
                    tr.append((j, 'ws60r READ at the oob-run opening — NOT a consultation, the '
                                  'dwell has not run. %s' % _dgdet(j, d)))
            if DGATE in ('traj', 'vote') and hand is None:
                xu = lambda z: float(X[TRIG_TF][z]) < float(R[TRIG_TF][z])
                # RENAMED FROM `held`, 1012: it collided with the baton-holder
                # LIST of the same name and would have wiped it. Only
                # W_NO_GT12=0 reaches here, which is why it never bit.
                x_side = xu(j) if d > 0 else (not xu(j))
                xc = (xu(j) and not xu(j - 1)) if d > 0 else ((not xu(j)) and xu(j - 1))
                # ---- 2: the EXHAUSTION window
                if (j - oob_a) <= EXH_BARS:
                    if exh_x is None and xc:
                        exh_x = j
                        tr.append((j, 'ws%dx crossed ws%dr inside the %d-bar exhaustion window '
                                      '(%.1f min of %.1f) — awaiting %d bars of hold'
                                   % (TRIG_TF, TRIG_TF, EXH_BARS,
                                      (j - oob_a) * 5 / 60.0, EXH_BARS * 5 / 60.0, XW12)))
                    elif exh_x is not None and not x_side:
                        tr.append((j, 'the exhaustion cross did NOT hold %d bars — cancelled'
                                   % XW12)); exh_x = None
                if exh_x is not None and x_side and (j - exh_x + 1) >= XW12:
                    tr.append((j, 'EXHAUSTION CONFIRMED — ws%dr never established, ws60r is '
                                  'overridden%s'
                               % (TRIG_TF, (' | THE READING IT OVERRODE: %s' % _dgdet(j, d))
                                  if TRACE_DG else '')))
                    return j, 'ws%dr exhaustion' % TRIG_TF, mae, ceil_bar, hand, tr
                # ---- 3b: traj said reverse; act on ws12r's own stall or x-cross
                if b_armed:
                    if ST[(TRIG_TF, d)][j]:
                        tr.append((j, 'ws%dr STALLED after the dwell' % TRIG_TF))
                        return j, 'ws%dr reversal on stalled' % TRIG_TF, mae, ceil_bar, hand, tr
                    if b_x is None and xc:
                        b_x = j
                        tr.append((j, 'ws%dx crossed ws%dr after the dwell — awaiting %d bars '
                                      'of hold' % (TRIG_TF, TRIG_TF, XW12)))
                    elif b_x is not None and not x_side:
                        tr.append((j, 'the post-dwell cross did NOT hold %d bars — cancelled'
                                   % XW12)); b_x = None
                    if b_x is not None and x_side and (j - b_x + 1) >= XW12:
                        tr.append((j, 'ws%dx CROSS CONFIRMED after the dwell' % TRIG_TF))
                        return j, 'ws%dr reversal on x-cross' % TRIG_TF, mae, ceil_bar, hand, tr
            if hand is None and not gate_shut and not b_armed and (j - oob_a) > GATE_BARS:
                if DGATE == 'off':
                    tj, src, tv, det = 0, 'the gate is off', 0.0, ''
                else:
                    tj, src, tv, det = dgate_dir(j, d)
                    if TRACE_DG:
                        tr.append((j, 'ws60r CONSULTED at the dwell-ending — ws%dr oob %.1f min of '
                                      'the %.1f required. %s'
                                   % (TRIG_TF, (j - oob_a) * 5 / 60.0,
                                      (GATE_BARS + 1) * 5 / 60.0, det)))
                if DGATE == 'off' or tj == d:
                    hand = j
                    tr.append((j, 'HANDOVER — ws%dr oob %.1f min; the >ws12 mech owns the exit%s'
                               % (TRIG_TF, (int(SC.ts[j]) - int(SC.ts[oob_a])) / 60000.0,
                                  '' if DGATE == 'off'
                                  else ' (gate OPEN — ws60r traj %+d matches the oob side %+d,'
                                       ' travel %+.4f, from %s)' % (tj, d, tv, src))))
                elif DGATE in ('traj', 'vote'):
                    b_armed = True
                    tr.append((j, 'DELEGATION REFUSED at the dwell-ending — ws60r traj %+d against '
                                  'the oob side %+d (travel %+.4f, from %s). ARMED: B opens on '
                                  'ws%dr\'s next stall or x-cross inside this oob run'
                               % (tj, d, tv, src, TRIG_TF)))
                else:
                    gate_shut = True
                    tr.append((j, 'DELEGATION REFUSED — ws60r traj %+d against the oob side %+d '
                                  '(travel %+.4f, from %s); this oob run never delegates and the '
                                  'walk keeps the exit' % (tj, d, tv, src)))
        else:
            # the oob run broke, so every latch clears with it. Joe 1009: the dwell clock is
            # continuous - any bar where ws12r returns in-bounds resets it.
            if oob_a is not None and DGATE in ('traj', 'vote') and TRACE_DG and hand is None \
               and not b_armed and not gate_shut:
                tr.append((j, 'ws60r NEVER CONSULTED on this oob run — ws%dr returned in-bounds at '
                              '%.2f after %.1f min, and the dwell-ending needs %.1f. The run ended '
                              '%.1f min short, so there was no delegation decision to make. Its '
                              'reading HERE, had it been asked: %s'
                           % (TRIG_TF, float(R[TRIG_TF][j]), (j - oob_a) * 5 / 60.0,
                              (GATE_BARS + 1) * 5 / 60.0,
                              (oob_a + GATE_BARS + 1 - j) * 5 / 60.0, _dgdet(j, d))))
            if oob_a is not None and TRACE_NOX and NOX and j < oob_a + GATE_BARS + 1:
                tr.append((j, 'THE RUN ENDED SHORT OF THE DWELL and %s'
                           % (('a SQUASHED x-cross fired in it at %s on ws%d — Joe 1009\'s rule '
                               'would close A here and open B [the cross was %s]'
                               % (SC.U(nox_x), nox_r,
                                  'an EDGE on ws%d' % nox_r if nox_e
                                  else 'ALREADY STANDING when it entered the run'))
                              if nox_x is not None
                              else 'NO squashed x-cross fired in it — the rule does not fire')))
            if SQX and nox_x is not None and hand is None and j < oob_a + GATE_BARS + 1:
                tr.append((j, 'A CLOSES — ws%dr returned in-bounds at %.2f after %.1f min, short '
                              'of the %.1f-min dwell-ending, and a walk x-cross was squashed in '
                              'the run at %s on ws%d.'
                           % (TRIG_TF, float(R[TRIG_TF][j]), (j - oob_a) * 5 / 60.0,
                              (GATE_BARS + 1) * 5 / 60.0, SC.U(nox_x), nox_r)))
                return j, 'ws%dr run short on a squashed x-cross' % TRIG_TF, mae, ceil_bar, hand, tr
            oob_a = None; gate_shut = False; exh_x = None; b_armed = False; b_x = None
            nox_x = None; nox_r = None; nox_e = None
        # CEIL_HI > BASE_HI guards the ceil_hi 12 arm: with CEIL_HI == BASE_HI the assignment
        # leaves `ceil == BASE_HI` true, so this branch re-fired on EVERY later oob crossing and
        # appended a duplicate 'CEILING ws12 -> ws12' line. Behaviour was always identical.
        if CEIL_HI > BASE_HI and ceil == BASE_HI \
           and goob(TRIG_TF, j, d) and not goob(TRIG_TF, j - 1, d):
            ceil = CEIL_HI; ceil_bar = j
            tr.append((j, 'CEILING ws%d -> ws%d (ws%dr %.2f)'
                       % (BASE_HI, CEIL_HI, TRIG_TF, float(R[TRIG_TF][j]))))
        # ---- after the handover: the >ws12 mech owns the exit
        if hand is not None:
            if dip is None:
                if entered(j, d):
                    n = 0
                    while j + n <= N - 1 and indip(j + n, d):
                        n += 1
                    if n > DIP_DWELL:
                        dip, conf = j, j + DIP_DWELL - 1
                        tr.append((j, 'dip into %.0f-%.0f — ws1Mage %.2f, run %d bars (%.1f min),'
                                   ' confirms %s'
                                   % (DIP_LO, DIP_HI, float(G1[j]), n, n * 5 / 60.0,
                                      SC.U(conf))))
                continue
            if j <= conf:
                continue
            for t in DIV_TFS:
                if REV[t][j] != WANT(d) or not xund(t, j, d): continue
                af = anchor_floater(R[t], PX, d, j)
                if af is None or int(af['fired']) == 0: continue
                tr.append((j, 'ws%dr reversal + divergence, x under r (floater %s, d_osc %+.2f)'
                           % (t, SC.U(af['floater'][0]), af['d_osc'])))
                return j, '>ws12 divergence on ws%dr' % t, mae, ceil_bar, hand, tr
            continue
        # ---- before the handover: the lineage walk
        # NO `continue` ON THE ARMING BAR, EITHER ARM. The jumpstart block below gets the same
        # bar the arm fired on, so the two arms are timed identically and neither one advantages
        # the other by a bar. Joe 1011's decoupling is about OWNERSHIP, not about forcing a delay.
        if ARM == 'mage' and not armed:
            if (d > 0 and float(MARM[j]) >= SC.HI and float(MARM[j - 1]) < SC.HI) or \
               (d < 0 and float(MARM[j]) <= SC.LO and float(MARM[j - 1]) > SC.LO):
                armed = True
                tr.append((j, 'exit-armed — ws%dMage %s %.0f (%.2f)'
                           % (ARM_TF, 'over' if d > 0 else 'under', SC.HI if d > 0 else SC.LO,
                              float(MARM[j]))))
            else:
                continue
        if GC:
            gc_hist[j] = GCG.raw_sign(j, d)
            if gc_hold is not None:
                # THE g15r `LINEAGE FINISHER` - JOE'S NAME, 1012: *"at the g15r `lineage
                # finisher` timestamp"*. It COMPLETES THE WALK. IT DOES NOT CLOSE A LEG. Joe 1012
                # ruled both halves:
                #   *"both g15r and g15Mage are needed to complete the walk"*
                #   *"the only banked back stop is dr-flip. I asked you earlier to remove g15 as an
                #   exit option. now I need you to delete it from the spec completely"*
                # So the pair arriving on the TARGET BOARD ends the hold and the walk carries on -
                # that is the completion. The 1011 branch where the pair arriving AGAINST the board
                # closed the leg at the opposing g15 bar is DELETED: not knobbed off, deleted. The
                # only thing that closes a leg from a hold is the dr-flip backstop.
                _side = GCG.oob_side(j, d)
                if _side == d:
                    tr.append((j, 'g15r LINEAGE FINISHER — g15r %.2f and g15Mage %.2f both oob on '
                                  'the target board here; the hold opened at %s, %.1f min ago, and '
                                  'ENDS. the walk carries on'
                               % (float(GCG.r15[j]), float(GCG.m15[j]), SC.U(gc_hold),
                                  (int(SC.ts[j]) - int(SC.ts[gc_hold])) / 60000.0)))
                    if EXIT_FIN:
                        _hh = htf_hold(rider, j, d)
                        if _hh is not None:
                            tr.append((j, _hh))
                        else:
                            return j, 'g15r lineage finisher', mae, ceil_bar, hand, tr
                    gc_hold = None
                else:
                    if _side == -d and not gc_said:
                        gc_said = True
                        tr.append((j, 'g15 arrived AGAINST the target board — g15r %.2f and '
                                      'g15Mage %.2f both oob. this does NOT close the leg any '
                                      'more (Joe 1012); the hold from %s stays open. reported '
                                      'once per hold.'
                                   % (float(GCG.r15[j]), float(GCG.m15[j]), SC.U(gc_hold))))
                    if GC_HOLD == 'wait':
                        continue
        # MODE 1 — ws1r AND ws1Mage both oob on the target board, held W_CP_DWELL bars.
        cp_now = (oobf(1, j, d)
                  and ((float(MG1[j]) >= SC.HI) if d > 0 else (float(MG1[j]) <= SC.LO))
                  ) if CP_MODE in ('1', 'both') else False
        # THE DWELL IS CAUSAL BY CONSTRUCTION: the count only ever reads bars at or before j, and
        # the cp fires on the bar the hold COMPLETES. An assert, not a comment, because the whole
        # point of the stamp is that it cannot be the first bar of the hold.
        cp_run = (cp_run + 1) if cp_now else 0
        cp_1 = (cp_run == CP_DWELL)
        assert not cp_1 or cp_run == CP_DWELL, 'the ws1-cp fired off its own hold count'
        # MODE 2 — the ws1x/ws1Mage cross plus the divergence. Tested only when mode 1 has not
        # already fired on this bar, so one bar is one cp and the row names which mode made it.
        cp_2 = None if (cp_1 or CP_MODE == '1') else cp2(j, d)
        cp_edge = bool(cp_1) or cp_2 is not None
        cp_why = ('mode 1, ws1r %.2f and ws1Mage %.2f both oob on the target board, held %d bars '
                  'from %s' % (float(R[1][j]), float(MG1[j]), CP_DWELL, SC.U(j - CP_DWELL + 1))
                  ) if cp_1 else ''
        if cp_2 is not None:
            _a, _p, _f = cp_2['anchor'], cp_2['pivot'], cp_2['floater']
            cp_why = ('mode 2, ws1x crossed %s ws1Mage at %s with ws1Mage %.2f oob, held %d bars; '
                      'divergence FIRED %+d — anchor %s ws1r %.2f close %.6f, pivot %s ws1r %.2f, '
                      'floater %s ws1r %.2f close %.6f, d_osc %+.2f d_px %+.6f'
                      % ('UNDER' if d > 0 else 'OVER', SC.U(j - CP_XWOB + 1),
                         float(MG1[j - CP_XWOB + 1]), CP_XWOB, int(cp_2['fired']),
                         SC.U(int(_a[0])), _a[1], _a[2], SC.U(int(_p[0])), _p[1],
                         SC.U(int(_f[0])), _f[1], _f[2], cp_2['d_osc'], cp_2['d_px']))
        # DECOUPLED, Joe 1011: *"were they coupled? if so, that was incorrect. make sure that it
        # is now decoupled from ws1-cp"*. The cp ARMS and nothing else - it does NOT choose the
        # first rider. That is the jumpstart's job and it runs as its own step below, under W_KICK,
        # on whatever bar its own test passes. The first version of this arm assigned
        # `rider = ws1` here, which did the jumpstart's work inside the cp.
        if ARM == 'cp' and not armed:
            if not cp_edge:
                continue
            armed = True; cp_n += 1
            loop_open = j; loop_end_armed = False; loop_stall_said = False; looped += 1
            tr.append((j, 'ws1-cp %d ARMS THE WALK and BEGINS W_LOOP %d — %s. The rider is not '
                          'set here; the jumpstart owns that.' % (cp_n, looped, cp_why)))
        # the cp RESET is a different job from the cp ARM: it only applies once a rider exists.
        if CP and rider is not None and cp_edge:
            cp_n += 1
            # A CP COMPLETES THE W_LOOP ONLY ONCE THE END IS ARMED by the ws{loopTF}r oob. A cp
            # BEFORE that oob is inside the loop and only resets the rider. Joe 1011 banked both
            # boundaries: the arming cp BEGINS the loop, the cp after the oob ENDS it.
            # A COMPLETING CP ALSO BEGINS *A* W_LOOP - not "the next one". Joe 1011 corrected the
            # wording: *"if you bank 'begins the next', you're opening up ambiguity if the
            # trade/walk hasn't made it to ws{w_loop_tf}r oob"*. A W_LOOP that never reaches the
            # loop TF never gets an end condition, so there is no sequence to be next in.
            #
            # THE A/B TRADE FLIP IS DISABLED. Joe 1011: *"this is disabled now"*. The old exhaustion
            # text said "A closes here and B opens on the opposite side"; it is deleted from every
            # trace string. The replacement is lineage taking over after a completed W_LOOP.
            if loop_open is not None and loop_end_armed:
                # A COMPLETING CP DOES NOT RESTART THE LOOP. Joe 1012: *"drop the loop reset on
                # ws1cp. from now on, loop only restarts on ws{w_loop_tf}r oob"*, and on the
                # distinction: *"I said 'restarts' and you're saying 'begins'. they're different
                # events - ws1cp is still the first checkpoint of any trade walk"*. So the arming
                # cp BEGINS the walk's first W_LOOP, a cp ENDS one, and only the loop TF going oob
                # RESTARTS one.
                tr.append((j, 'W_LOOP %d COMPLETE at this ws1-cp — it began %s, %.1f min ago; '
                              'lineage starts again from ws%d. No W_LOOP is open now; the next one '
                              'restarts when ws%dr goes oob.'
                           % (looped, SC.U(loop_open),
                              (int(SC.ts[j]) - int(SC.ts[loop_open])) / 60000.0, ALL_TF[0],
                              LOOP_TF if LOOP_TF is not None else 0)))
                loop_open = None; loop_end_armed = False; loop_stall_said = False
                # THE RIDER RESETS ONLY ON A COMPLETING CP. Joe 1012: *"drop the reset at every
                # ws1-cp"*. His banked rule is *"at 05:42, the w_loop is complete and we start the
                # lineage again from ws1"* - that is the COMPLETION, not every checkpoint. The
                # unconditional reset was mine.
                # THE MODE GOES IN THE ROW. Without it the completion row does not say which
                # mode ended the loop, and the loop's end is the number Joe reads.
                tr.append((j, 'ws1-cp %d completes it (%s) — the rider resets to ws%d from ws%d'
                           % (cp_n, cp_why, ALL_TF[0], rider)))
                rider = ALL_TF[0]
                if LOOP_CLEAR_OOB:
                    rider_oob = False   # a new line owes its OWN trip out and back
                continue
            if CP_ALL:
                tr.append((j, 'ws1-cp %d — %s. No W_LOOP completes here, but W_CP=all so the '
                              'rider RESETS to ws%d from ws%d.'
                           % (cp_n, cp_why, ALL_TF[0], rider)))
                rider = ALL_TF[0]
                if LOOP_CLEAR_OOB:
                    rider_oob = False   # a new line owes its OWN trip out and back
                continue
            tr.append((j, 'ws1-cp %d — %s. No W_LOOP completes here, so the rider stays on '
                          'ws%d.' % (cp_n, cp_why, rider)))
            continue
        # THE LOOP TF GOING oob does one of two jobs: it ARMS the end of an open W_LOOP, or it
        # RESTARTS a W_LOOP when none is open. A restarted loop arms its end on the same bar,
        # because that bar IS the loop TF oob.
        # THE STATE IS EDGE-TRIGGERED, Joe 1013: the first bar of the oob state fires it, and it
        # re-arms only when ws{loop TF}r leaves oob. `loop_oob` carries the state per loop TF.
        for _lt in LOOP_TFS:
            if _lt in R:
                loop_oob[_lt] = bool(oobf(_lt, j, d))
        # NO RIDER QUALIFICATION. Joe 1013: *"ws{loop-tf}r oob is the only qualification needed to
        # send the walk to ws1"*, and *"delete this"* of the `rider >= t` row. So a walk that has
        # not armed yet is ARMED by the loop - the rider becomes ws1 on the oob bar.
        if (LOOP_TFS and not (looped_once and LOOP_ONCE)
                and (not LOOP_RIDER_GATE or rider is not None)
                and (loop_open is None or not loop_end_armed)):
            hit = [t for t in LOOP_TFS
                   if t in R and loop_oob.get(t) and not loop_oob_prev.get(t)
                   and (not LOOP_RIDER_GATE or (rider is not None and rider >= t))]
            if hit:
                lt = max(hit)
                hit_from = rider
                skipped = rider is not None and rider > lt
                exh_armed = True
                where = ('ws%d%s and ws%dr is %.2f oob'
                         % (lt,
                            (' (jumped past it, rider was ws%d)' % hit_from) if skipped
                            else (' (the walk had no rider yet)' if hit_from is None else ''),
                            lt, float(R[lt][j])))
                if LOOP_END == 'oob':
                    rider = ALL_TF[0]; loop_end_armed = False
                    if LOOP_CLEAR_OOB:
                        rider_oob = False   # a new line owes its OWN trip out and back
                    # JOE 1013: the ONLY place the jumpstart-disabled flag is enabled.
                    jump_off = LOOP_JUMP_OFF
                    # JOE 1013: *"the constant W_LOOP ws10r events are a result of me saying
                    # 'ws{loop-tf}r oob', without stating that the 'rider reset to ws1' is a
                    # one-time event"*. ONE reset per LEG, carried across the pieces.
                    looped_once = True
                    loop_close = LOOP_CLOSE
                    tr.append((j, 'W_LOOP %d — the walk reached %s; the rider resets to ws%d, the '
                                  'JUMPSTART IS DISABLED for the rest of the walk, and lineage '
                                  'carries on' % (looped, where, rider)))
                    continue
                # THE 4-MINUTE LOOKBACK, stubbed
                lb = None
                for i in range(max(1, j - LOOP_LB), j + 1):
                    now_ = (oobf(1, i, d) and ((float(MG1[i]) >= SC.HI) if d > 0
                                               else (float(MG1[i]) <= SC.LO)))
                    prv_ = (oobf(1, i - 1, d) and ((float(MG1[i - 1]) >= SC.HI) if d > 0
                                                   else (float(MG1[i - 1]) <= SC.LO)))
                    if now_ and not prv_:
                        lb = i
                _restart = loop_open is None
                if _restart:
                    loop_open = j; looped += 1
                loop_end_armed = True; loop_stall_said = False
                tr.append((j, 'W_LOOP %d %s — the walk reached %s. %s The rider is NOT '
                              'reset here; the next ws1-cp ends the loop.'
                           % (looped,
                              'RESTARTS HERE and its end is ARMED' if _restart else 'END ARMED',
                              where,
                              ('LOOKBACK HIT: a same-side ws1-cp at %s, inside the %d-bar window '
                               '— STUBBED, no action taken.' % (SC.U(lb), LOOP_LB)) if lb
                              else ('no same-side ws1-cp in the %d bars before it.' % LOOP_LB))))
        if (rider is not None and not XIB
                and (EXH_LOOP == 'always'
                     or (EXH_LOOP == 'after_loop' and exh_armed))):
            e = exhausted(rider, j, d, LIN_CEIL)
            if e is not None:
                # A HELD LEG CANNOT BE RE-EXHAUSTED. Joe 1011, on the W_GC_HOLD='walk' run that
                # deferred at 04:14:30 and then died at 04:15:05: that exit was my plumbing, not
                # his logic. While a deferral is open the ONLY thing that can close the leg is the
                # g15 backstop (or the MAE stop, which is above this and untouched).
                if GC and gc_hold is not None:
                    tr.append((j, 'exhaustion on ws%d SUPPRESSED — the %s deferral is still open, '
                                  'waiting on the g15 backstop' % (rider, SC.U(gc_hold))))
                    continue
                g = gc_defer(j, d, gc_hist) if GC else None
                if g is not None:
                    gc_hold = j
                    tr.append((j, 'EXHAUSTED on ws%d%s — %s | gc DEFERS IT: %s'
                               % (rider, _lp(looped), e, g)))
                    continue
                if loop_end_armed:
                    tr.append((j, 'lineage ruled ws%d EXHAUSTED; W_LOOP %d DEFERS acting on it — '
                                  'it has reached its loop TF and waits for the ws1-cp that ends '
                                  'it (began %s)' % (rider, looped, SC.U(loop_open))))
                    continue
                tr.append((j, 'EXHAUSTED on ws%d%s — %s' % (rider, _lp(looped), e)))
                _hh = htf_hold(rider, j, d)
                if _hh is not None:
                    tr.append((j, _hh)); continue
                return j, 'loop exhaustion', mae, ceil_bar, hand, tr
        if rider is None and LASTMILE and (j - k0) > LASTMILE_MAX_GAP:
            tr.append((j, 'MAX GAP — no line at or under ws%d went oob within %d bars (%.1f min) '
                          'of the handoff; the jumpstart never fired and the held close goes here'
                       % (LASTMILE_KICK_TFCAP, LASTMILE_MAX_GAP, LASTMILE_MAX_GAP * 5 / 60.0)))
            return j, 'max jumpstart gap', mae, ceil_bar, hand, tr
        if rider is None:
            if KICK == 'off':
                rider = ALL_TF[0]
                if LOOP_CLEAR_OOB:
                    rider_oob = False   # a new line owes its OWN trip out and back
                tr.append((j, 'WALK STARTS on ws%d — KICKSTART disabled, no oob test, lineage '
                              'climbs from the bottom (r %.2f %s, lineage ceiling ws%d)'
                           % (rider, float(R[rider][j]), bnd(rider, j, d), LIN_CEIL)))
                continue
            # THE JUMPSTART'S REACH IS BOUNDED BY THE LOOP TF. Joe 1011: *"the max jumpstart
            # reach must be <= loopTF ... it's the max lineage walk before we loop back to ws1"*.
            # Without this the jumpstart could land ABOVE the loop point and the loop could never
            # fire on that rider. The BATON is deliberately NOT bounded - it has to be able to
            # climb to the loop TF or the loop never triggers at all.
            # UNRULED: with W_LOOP_TF off there is no loop TF, so the bound falls back to the
            # ceiling. Joe has not said what he wants there.
            # THE JUMPSTART'S BOUND IS THE LOOP TF, not a ceiling. Joe 1011: *"the max jumpstart
            # reach must be <= loopTF"*. With no loop TF it falls back to lineage's own ceiling.
            # This is the ONE place W_LOOP constrains lineage, and it is a START condition, not a
            # reach - lineage's reach is LIN_CEIL throughout.
            if jump_off:
                # JOE 1013: a loop has already recycled this walk to ws1, so the jumpstart may not
                # arm it. The ws1-cp arm and W_KICK 'off' are untouched - he disabled the jumpstart
                # and nothing else.
                #   THIS BRANCH IS UNREACHABLE TODAY and is kept because the flag is his mech. It
                #   needs the walk to have NO line while the flag is set, and the only place the
                #   flag is set writes ws1 into the line on the same bar. Stated, not deleted - a
                #   silent unreachable branch is what the 1013 audit kept finding.
                continue
            jmax = LOOP_TF if LOOP_TF is not None else LIN_CEIL
            if LASTMILE:
                jmax = min(jmax, LASTMILE_KICK_TFCAP)   # Joe 1013's cap, last-mile mode only
            c = [t for t in ALL_TF if t <= jmax and oobf(t, j, d)]
            if c:
                rider = min(c) if KICK == 'low' else max(c)
                tr.append((j, 'JUMPSTART — rider ws%d (%s oob line at or under ws%d, r %.2f; '
                              'start bounded by loopTF ws%s; lineage ceiling ws%d)'
                           % (rider, 'LOWEST' if KICK == 'low' else 'highest', jmax,
                              float(R[rider][j]),
                              LOOP_TF if LOOP_TF is not None else 'off', LIN_CEIL)))
            continue
        # THE HOLDER LIST IS BUILT EVERY BAR, whatever W_TRACE_HOLD says - W_EXH_WHO='holders'
        # reads it. Only the ROWS below are reporting.
        if rider not in held:
            held.append(rider); held_st[rider] = bool(ST[(rider, d)][j])
        if TRACE_HOLD:
            for _h in held:
                _now = bool(ST[(_h, d)][j])
                if _now and not held_st.get(_h, False):
                    _rc = [t for t in range(_h + 1, min(_h + LIN_HOP, LIN_CEIL) + 1) if t in R]
                    tr.append((j, 'HOLDER STALL — ws%d (r %.2f %s) stalled. %s. its reach %s'
                               % (_h, float(R[_h][j]), bnd(_h, j, d),
                                  'IT IS THE RIDER' if _h == rider
                                  else 'the rider is ws%d, so lineage does NOT test this' % rider,
                                  ', '.join('ws%d %.2f %s' % (t, float(R[t][j]), bnd(t, j, d))
                                            for t in _rc) or 'none, at lineage\'s ceiling')))
                held_st[_h] = _now
        if PASS == 'crossing_to_ib':
            # JOE 1013'S MODE. The trigger is the RIDER returning inside the fence, so this does not
            # ask `baton_ok` of the lines above - it asks one question of the rider.
            #   `rider_oob` is per-rider state, reset on every pass. A rider that is already IB when
            #   it arrives therefore waits for its OWN oob excursion before it can hand over, which
            #   is what puts his ws2 pass at ~18:07 instead of on the bar ws2 received the baton.
            if oobf(rider, j, d):
                rider_oob = True
            # THE RECEIVER MUST ITSELF BE towards-dr, Joe 1013: *"#1 apply the towards-dr test"*,
            # after the measurement. Until this the baton went to rider+1 whatever its state, so a
            # line already tagged `left-target-dr` could take it: on the 07-18 16:07 LONG the baton
            # went to ws5 at 2026-07-18 18:12:00 and exhaustion then fired a bar later on ws5's own
            # reach, ending at 18:13:00 and +1.7511% instead of 18:12:00 and +1.7205%.
            # THE CAP IS THE LOOP TF, the same bound exhaustion's reach carries - a receiver above
            # it would be a line this walk has no business with (Joe 1013).
            _top = min(LIN_CEIL, LOOP_TF) if LOOP_TF is not None else LIN_CEIL
            _nxt = rider + 1
            cand = [_nxt] if (rider_oob and not oobf(rider, j, d)
                              and _nxt <= _top and _nxt in R
                              and towards_dr(_nxt, j, d, xtag)) else []
        else:
            cand = [t for t in range(rider + 1, min(rider + LIN_HOP, LIN_CEIL) + 1)
                    if baton_ok(t, j, d)]
        # W_TRACE_LIN — REPORTING ONLY, no branch reads it. Joe 1011, on the silence after a w_loop
        # recycled the rider to ws1: *"there's no events, no line data, and no reasons stating why
        # the lineage stopped at ws1"*. A resting walk emits nothing, so this says what lineage
        # asked and what the answer was. EDGE-TRIGGERED on (rider, baton available, rider stalled),
        # so a long rest is one row, not one row per bar.
        if TRACE_LIN:
            _st = bool(ST[(rider, d)][j])
            _key = (rider, bool(cand), _st)
            if _key != lin_prev:
                _reach = [t for t in range(rider + 1, min(rider + LIN_HOP, LIN_CEIL) + 1)
                          if t in R]
                tr.append((j, 'lineage on ws%d — %s. reach %s. ws%d %s'
                           % (rider,
                              ('baton available: ws%s' % ', ws'.join(str(t) for t in cand))
                              if cand else 'NO baton available',
                              ', '.join('ws%d %.2f %s' % (t, float(R[t][j]), bnd(t, j, d))
                                        for t in _reach) or 'none, at the ceiling',
                              rider, 'STALLED' if _st else 'not stalled')))
                lin_prev = _key
        # JOE 1013'S IMMEDIATE CLOSE AFTER THE LOOP. His words: *"the bigger (and most important)
        # problem is that ws1 is printing weakness (ie is not low oob or is not printing momentum)
        # at the first W_LOOP (12:00), but the code doesn't react. the code's reaction at 12:00,
        # when it sees ws1 printing weak, and with no baton-pass opportunity, should be an immediate
        # close of the trade"*.
        #   WEAK  = ws1 is NOT oob on the target end, OR ws1 is NOT mom-true. Either one.
        #   NO BATON OPPORTUNITY = `cand` is empty, computed by the real baton block above, not
        #     duplicated here.
        # THE BAR: the loop resets ws1 in and `continue`s, so the first bar on which the new rider's
        # baton opportunity is KNOWABLE is the next one. On the 2026-07-19 09:54:25 SHORT that is
        # 12:00:05, 5 s after the loop at 12:00:00. Reading it on the loop bar itself would be a
        # verdict on a `cand` that has not been computed. STATED.
        if loop_close:
            loop_close = False
            _w_oob = oobf(ALL_TF[0], j, d)
            _w_mom = bool(MOMT[ALL_TF[0]][d][j]) if ALL_TF[0] in MOMT else False
            if not cand and (not _w_oob or not _w_mom):
                tr.append((j, 'LOOP CLOSE — the loop recycled the walk to ws%d and it is weak here '
                              '(r %.2f %s, %s) with no baton available. the trade closes.'
                           % (ALL_TF[0], float(R[ALL_TF[0]][j]),
                              'oob' if _w_oob else 'NOT oob',
                              'mom-true' if _w_mom else 'NO momentum')))
                return j, 'loop close - ws%d weak, no baton' % ALL_TF[0], mae, ceil_bar, hand, tr
            tr.append((j, 'LOOP CLOSE not taken — ws%d r %.2f %s, %s, baton %s'
                       % (ALL_TF[0], float(R[ALL_TF[0]][j]),
                          'oob' if _w_oob else 'NOT oob',
                          'mom-true' if _w_mom else 'NO momentum',
                          'available: ws%s' % ', ws'.join(str(t) for t in cand) if cand
                          else 'not available')))
        if cand:
            _was = rider
            rider = max(cand)
            rider_oob = False      # per-rider, so the new rider owes its own oob excursion
            xib_stall_said = False
            tr.append((j, 'baton -> ws%d %s (r %.2f%s)'
                       % (rider, BATON if BATON != 'oob' else PASS,
                          float(R[rider][j]),
                          ', ws%d crossed back inside the fence at %.2f' % (_was, float(R[_was][j]))
                          if PASS == 'crossing_to_ib' else ''))); continue
        # ---- JOE 1013'S CYCLE EXHAUSTION, LAST-MILE ONLY. The tag itself is maintained at the TOP
        # of this loop, not here - see the note there.
        if LASTMILE:
            _xe = exhausted_cycle(rider, j, d, xtag)
            if _xe is not None:
                tr.append((j, 'EXHAUSTED on ws%d%s — %s' % (rider, _lp(looped), _xe)))
                return j, 'exhaustion', mae, ceil_bar, hand, tr
        # THE EXHAUSTION SCAN, over every baton HOLDER. See W_EXH_WHO.
        if EXH_LOOP == 'on_stall' and EXH_WHO == 'holders' and not XIB:
            _who = held if held else [rider]
            _ex = [(t, exhausted(t, j, d, LIN_CEIL)) for t in _who if ST[(t, d)][j]]
            _ex = [(t, e) for t, e in _ex if e is not None]
            if _ex:
                for _t, _e in _ex:
                    tr.append((j, 'EXHAUSTED on ws%d%s%s — %s'
                               % (_t, '' if _t == rider else ' (a holder, not the rider ws%d)' % rider,
                                  _lp(looped), _e)))
                if GC and gc_hold is not None:
                    tr.append((j, 'the %s deferral is still open, waiting on the g15 backstop — '
                                  'this verdict is SUPPRESSED' % SC.U(gc_hold)))
                else:
                    g = gc_defer(j, d, gc_hist) if GC else None
                    if g is not None:
                        gc_hold = j
                        tr.append((j, 'gc DEFERS IT: %s' % g))
                    elif loop_end_armed:
                        tr.append((j, 'W_LOOP %d DEFERS acting on it — it has reached its loop TF '
                                      'and waits for the ws1-cp that ends it (began %s)'
                                   % (looped, SC.U(loop_open))))
                    else:
                        _hh = htf_hold(rider, j, d)
                        if _hh is not None:
                            tr.append((j, _hh))
                        else:
                            return j, 'loop exhaustion', mae, ceil_bar, hand, tr
                continue
        if ST[(rider, d)][j]:
            if EXH_LOOP == 'on_stall' and EXH_WHO == 'rider' and not XIB:
                e = exhausted(rider, j, d, LIN_CEIL)
                if e is not None:
                    # A HELD LEG CANNOT BE RE-EXHAUSTED - see the note at the other site.
                    if GC and gc_hold is not None:
                        tr.append((j, 'exhaustion on ws%d at its own stall SUPPRESSED — the %s '
                                      'deferral is still open, waiting on the g15 backstop'
                                   % (rider, SC.U(gc_hold))))
                        continue
                    g = gc_defer(j, d, gc_hist) if GC else None
                    if g is not None:
                        gc_hold = j
                        tr.append((j, 'EXHAUSTED on ws%d at its own stall%s — %s | gc DEFERS IT: %s'
                                   % (rider, _lp(looped), e, g)))
                        continue
                    if loop_end_armed:
                        tr.append((j, 'lineage ruled ws%d EXHAUSTED at its own stall; W_LOOP %d '
                                      'DEFERS acting on it — it has reached its loop TF and waits '
                                      'for the ws1-cp that ends it (began %s)'
                                   % (rider, looped, SC.U(loop_open))))
                        continue
                    tr.append((j, 'EXHAUSTED on ws%d at its own stall%s — %s'
                               % (rider, _lp(looped), e)))
                    _hh = htf_hold(rider, j, d)
                    if _hh is not None:
                        tr.append((j, _hh)); continue
                    return j, 'loop exhaustion', mae, ceil_bar, hand, tr
            if STALL_UP and rider < LIN_CEIL:
                rider += 1
                tr.append((j, 'stalled -> rider advances to ws%d (r %.2f %s)'
                           % (rider, float(R[rider][j]), bnd(rider, j, d))))
                continue
            # AN OPEN w_loop IS NOT CLOSED BY `final stalled`. Joe 1011: *"you've dropped the
            # ws1-cp event that follows ws{loop_tf}r oob"* - with the ceiling at the loop TF the
            # parked rider has an empty reach, so `final stalled` was ending the leg before the
            # forward ws1-cp could end the loop.
            # ATTRIBUTION CORRECTED 1013. This used to read "His spec puts the loop's end AT the
            # cp, so the walk waits for it". Joe 1013: *"this was an observation, not a mech"*. He
            # described what he saw at one bar; MAKING THE WALK WAIT FOR THE cp IS MINE. It is
            # reachable as W_LOOP_END='oob' if the recycle should fire on the oob bar instead.
            if loop_end_armed:
                if not loop_stall_said:          # ONE row per open loop, not one per stall bar
                    loop_stall_said = True
                    tr.append((j, 'lineage ruled ws%d STALLED; W_LOOP %d DEFERS acting on it — it '
                                  'has reached its loop TF (began %s) and waits for the ws1-cp '
                                  'that ends it. Reported once per loop, not per bar.'
                               % (rider, looped, SC.U(loop_open))))
                continue
            # `final stalled` IS ALSO SUPPRESSED IN crossing_to_ib MODE, for the same reason the
            # exhaustion exit is - both are STALL-BASED ENDS, and in this mode a stalled rider is
            # not an end, it is a rider that still owes its oob -> IB cross. Measured: with
            # exhaustion suppressed and this one live, the 17:39:10 handoff still ended at 17:39:20
            # on `final stalled on ws1 (r 88.98 O)`, 5 s in, so Joe's ws2 pass at ~18:07 stayed
            # unreachable. These are the ONLY two exits this mode suppresses; the ceiling, the MAE
            # stop, the x-cross and the >ws12 branch are untouched.
            if not XIB:
                tr.append((j, 'final stalled on ws%d (r %.2f %s)%s'
                           % (rider, float(R[rider][j]), bnd(rider, j, d),
                              " - AT LINEAGE'S CEILING ws%d" % LIN_CEIL if STALL_UP else '')))
                return j, 'final stalled', mae, ceil_bar, hand, tr
            if not xib_stall_said:
                xib_stall_said = True
                tr.append((j, 'lineage ruled ws%d STALLED; crossing_to_ib IGNORES it — the baton '
                              'moves on the rider\'s oob -> IB cross, not on its stall. Reported '
                              'once per rider.' % rider))
        if (not NOX) and xcond(rider, j, d):
            tr.append((j, 'x-cross on ws%d' % rider))
            return j, 'x-cross', mae, ceil_bar, hand, tr
        if NOX and (TRACE_NOX or SQX) and xcond(rider, j, d):
            # the bar the W_NOX=0 build would have EXITED on. Everything after the FIRST one is a
            # path that build never had, so only the first per oob run is named at the run's end.
            first = nox_x is None
            # EDGE vs LEVEL: `xcond` is a level test - ws{rider}x BELOW its target - so it stays
            # true for long stretches. An EDGE is its first true bar after a false one on the same
            # rider. The W_NOX=0 build exits on the first true bar it meets, which need not be an
            # edge: the baton can hand to a rider whose x is ALREADY across.
            edge = not xcond(rider, j - 1, d)
            if first and oob_a is not None:
                nox_x, nox_r, nox_e = j, rider, edge
            if not TRACE_NOX:
                continue
            tr.append((j, 'x-cross SQUASHED on ws%d — W_NOX=1, so the walk did NOT exit here '
                          '(ws%dx %.2f vs its target; %s)'
                       % (rider, rider, float(X[rider][j]),
                          ('inside the ws%dr oob run that opened %s'
                           % (TRIG_TF, SC.U(oob_a))) if oob_a is not None
                          else 'ws%dr is NOT oob on this bar' % TRIG_TF)))
    return None, 'tape end', mae, ceil_bar, hand, tr

def main():
    k0 = SC.K('%s %s' % (D, START))
    print('\n# THE CHAIN RECREATED FROM %s %s, side %s — lineage walk + the >ws12 oob mech'
          % (D, START, 'LONG' if FIRST > 0 else 'SHORT'))
    k, d, legs, n = k0, FIRST, [], LEG0
    while True:
        xk, why, mae, cb, hand, tr = run_leg(k, d)
        if xk is None:
            print('\n- leg %d found no exit before the tape end. the chain ends.' % (n + 1)); break
        n += 1
        p0 = float(PX[k]); sgn = -int(d)   # d is main()'s TRADE side; adverse is against it
        real = (float(PX[xk]) - p0) / p0 * 100.0 * sgn
        legs.append(dict(leg=n, side='LONG' if d > 0 else 'SHORT', open=k, exit=xk, real=real,
                         mae=mae, why=why, hand=hand))
        pct = lambda j: '%+.4f' % ((float(PX[j]) - p0) / p0 * 100.0 * sgn)
        mn = lambda j: '%+.1f' % ((int(SC.ts[j]) - int(SC.ts[k])) / 60000.0)
        print('\n## LEG %d — %s   open %s   pxs %.6f' % (n, legs[-1]['side'], SC.U(k), p0))
        box(('ts', '+min', 'event', 'pxs', 'pct'),
            [(SC.U(k), '+0.0', 'OPEN %s' % legs[-1]['side'], '%.6f' % p0, '+0.0000')]
            + [(SC.U(j), mn(j), lbl, '%.6f' % float(PX[j]), pct(j)) for j, lbl in tr]
            + [(SC.U(xk), mn(xk), 'EXIT — %s' % why, '%.6f' % float(PX[xk]), pct(xk))])
        if why == 'mae breach':
            print('\n- MAE breach at %s. THE CHAIN IS STOPPED FOR REVIEW.' % SC.U(xk)); break
        k = xk; d = -d

    def mm(s_, e_, dd):
        """MAE / MFE over the leg's own holding window, in the direction dr makes favourable."""
        seg = PX[s_:e_ + 1]
        seg = seg[np.isfinite(seg) & (seg > 0)]
        if seg.size == 0: return 0.0, 0.0
        p_ = float(PX[s_])
        f = float(seg.max()) if dd > 0 else float(seg.min())
        g = float(seg.min()) if dd > 0 else float(seg.max())
        return (max(0.0, -((g - p_) / p_ * 100.0 * dd)), (f - p_) / p_ * 100.0 * dd)

    # JOE'S SCORING RULE, 1007: *"if mae1.1 was hit, then MFE is zero and MAE is 1.1"*. A stopped leg
    # scores the KNOB value, not the measured overshoot - 1.1000, not 1.1504.
    print('\n# EVERY LEG AND THE RUNNING MAE / MFE')
    rows = []; rA = 0.0; rF = 0.0; rR = 0.0
    for L in legs:
        dd = 1 if L['side'] == 'LONG' else -1
        if L['why'] == 'mae breach':
            a_, f_ = MAE_STOP, 0.0
        else:
            a_, f_ = mm(L['open'], L['exit'], dd)
        rA += a_; rF += f_; rR += L['real']
        rows.append((str(L['leg']), L['side'], SC.U(L['open']), SC.U(L['exit']),
                     '%.1f' % ((int(SC.ts[L['exit']]) - int(SC.ts[L['open']])) / 60000.0),
                     L['why'], '%.4f' % a_, '%.4f' % f_,
                     ('%.2f' % (f_ / a_)) if a_ > 0 else 'inf',
                     '%+.4f' % L['real'], '%.4f' % rA, '%.4f' % rF, '%+.4f' % rR))
    box(('leg', 'side', 'open', 'exit', 'hold min', 'why', 'leg MAE', 'leg MFE', 'MFE/MAE',
         'realised', 'running MAE', 'running MFE', 'running realised'), rows)
    print('- a leg that hit the stop scores MFE 0.0000 and MAE %.4f, the knob value - Joe 1007.'
          % MAE_STOP)
    print('- running MFE/MAE over the chain: %.2f' % (rF / rA) if rA > 0 else '- running MAE is 0')

    print('\n# THE CHAIN FROM %s' % START)
    box(('leg', 'side', 'open', 'exit', 'hold min', 'handover', 'leg MAE', 'realised', 'why'),
        [(str(L['leg']), L['side'], SC.U(L['open']), SC.U(L['exit']),
          '%.1f' % ((int(SC.ts[L['exit']]) - int(SC.ts[L['open']])) / 60000.0),
          SC.U(L['hand']) if L['hand'] else '—',
          '%.4f' % L['mae'], '%+.4f' % L['real'], L['why']) for L in legs]
        + [('legs %d-%d' % (legs[0]['leg'], legs[-1]['leg']), '', SC.U(legs[0]['open']),
            SC.U(legs[-1]['exit']),
            '%.1f' % sum((int(SC.ts[L['exit']]) - int(SC.ts[L['open']])) / 60000.0 for L in legs),
            '%d of %d' % (sum(1 for L in legs if L['hand']), len(legs)),
            '%.4f' % max(L['mae'] for L in legs), '%+.4f' % sum(L['real'] for L in legs), '')])
    print('\n- %d legs, %d positive, %d handed over to the >ws12 mech'
          % (len(legs), sum(1 for L in legs if L['real'] > 0), sum(1 for L in legs if L['hand'])))


if __name__ == '__main__':
    main()
