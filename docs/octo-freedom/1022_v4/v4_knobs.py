"""octo-v4's knobs, BANKED. Joe 1022: *"find and bank all knobs.  your choice on the labels"*.

BANKED MEANS THE DEFAULT MOVES AND AN OFF-RULED RUN REFUSES. Joe's standing rule. Every value below
is the one he set; importing this module with any of them overridden raises unless the run declares
itself an experiment with W_V4_EXPERIMENT=1, and an experiment run prints every delta before it
proceeds. A spec doc is not in-use; this file is.

THE LABELS ARE MINE, the values are his. Module constants are UPPER_CASE, env overrides are
W_V4_<NAME>, matching the W_ convention the octo2 modules already use. Where Joe wrote a name
himself it is kept verbatim as the env name: W_V4_SAV_WS2_OOB_TEST is his `V4_SAV_WS2_OOB_TEST`.

THE CASCADE'S KNOBS ARE NOT RE-DECLARED HERE. MC_GAP, MC_ZOOM, MC_MIN, MC_TF_LO and MC_TF_HI are
Joe's 1017 rulings and live in the Jig, which is their one home. This module ASSERTS them instead,
so a change there refuses a v4 run rather than silently moving v4's verdict.

PROVISIONAL is marked per knob. Two are: TF_CEILING, where Joe said *"18, unsure.  use 10"*, and
GAP_PER_TF, where he said *"we can't validate this yet, let's choose 2.8 until we get to the
sweep"*. They are banked as defaults like the rest - provisional means he expects to move them,
not that they are unset.
"""
import os
import sys

EXPERIMENT = os.environ.get('W_V4_EXPERIMENT', '0') == '1'


def _knob(name, default, cast=float):
    return cast(os.environ.get('W_V4_' + name, str(default)))


# ── the board. Standing rulings, and now BANKED like everything else ─────────────────────────
#   Joe 1022: *"ensure all potential knobs are captured, including any that I haven't called out"*.
#   These are standing rulings he has never varied, but they move every verdict in v4, so they sit
#   in the bank with the rest and an off-ruled run refuses.
#   ONE KNOB PER FENCE, NOT TWO. Joe 1022: *"oob_hi and oob_lo are expressed as one knob, to avoid
#   imbalnace.  the formula is (100 -{knob:15}) - you'll see this in the codebase"*, and *"change
#   `mid` to a fence, same logic as above. 100-{knob:50}"*. The knob is the LOW end and the high end
#   is 100 - knob, which is jig.wsf_facing_dr's own form (*"the fence, 80 / 20 at knob 20"*) and
#   test_points' (*"momo_fence_r 17 -> (17.0, 83.0)"*). Two separate knobs could drift apart; one
#   cannot.
OOB_FNC = _knob('OOB_FNC', 15.0)    # oob is ALWAYS 15/85 -> the pair is (15.0, 85.0)
MID_FNC = _knob('MID_FNC', 50.0)    # the middle fence. At 50 the pair is (50.0, 50.0) - no band.
#   Joe 1022: *"low side = <50.  high side = >50"*. Moving it to 45 opens a 45-55 band, and what a
#   value INSIDE that band counts as is NOT RULED - it cannot arise at 50, so nothing decides it.
OOB_LO, OOB_HI = OOB_FNC, 100.0 - OOB_FNC
MID_LO, MID_HI = MID_FNC, 100.0 - MID_FNC
MID = MID_FNC                       # kept so a reader of the old name lands on the low end

# ── v4-lineage ────────────────────────────────────────────────────────────────────────────────
RMOM_FNC = _knob('RMOM_FNC', 80.0)        # the r fence, mirrored. 80 -> (20, 80)
LIN_HOP = _knob('LIN_HOP', 2, int)        # TFs the lin-hop VIEW reads ahead; the baton moves one
# REV_WOB DELETED, Joe 1023: *"delete REV_WOB"*. It was banked as "bars a v4-lineage reversal must
#   hold" and read by no code - the lineage reversal hold is LIFT_WOB, inside lift_off. The 1023
#   audit found it dead; keeping a ruled knob that nothing applies is worse than not having it.
IB_WOB = _knob('IB_WOB', 3, int)          # bars the ws5r ib cross must hold. SUPERSEDED for the
#   lineage ib cross by LIN_IB_DWELL below, and kept because it is his #10 ruling and the record of
#   what the static form was.
LIN_IB_DWELL = _knob('LIN_IB_DWELL', 2.5)  # bars per TF the lineage ib cross must hold, DYNAMIC.
#   Joe 1022: *"ok, we need a wob for lineage.  it needs to be dynamic: let's start with
#   int(TF * {knob:2.5, 'V4_LIN_IB_DWELL`})"*. WHY IT MOVED: on 2026-08-31 19:30:40 ws5r crossed to
#   ib at 16.25, reached 16.36 - 1.36 points past the fence - held THREE bars and fell straight back
#   to low oob and on down to 11.32. At the static IB_WOB 3 that flicker passed the hold on its last
#   bar and counted as ws5r walking to ib. int(5 * 2.5) = 12 bars rejects it.
LIN_PASS = os.environ.get('W_V4_LIN_PASS', 'ib')   # 'ib' | 'reversal'
#   HOW THE BATON PASSES. 'ib' is what the code has always done - walk the rider to ib, then pass.
#   'reversal' is what Joe's 1022 verbatim actually says, and he caught it on 1023: *"I thought
#   v4lineage uses reverse to pass the baton. the only exception belongs to ws5 and ws6, under
#   specific conditions"*.
#   HIS 1022 WORDS, three times over: *"baton-pass on riderTF reversing while riderTF+1 is oob"* /
#   *"baton-passing on riderTF reversal"* / *"for riderTF+1 to accept a baton-pass, riderTF+1 must
#   be exfence at the time of riderTF reversing"*.
#   THE IB WALK IS THE EXCEPTION, and it belongs to two places only: ws5r's own step (*"walk ws5r
#   to ib and test if ws{TF+lin-hop}r's are oob"*) and the hatch (*"walk current-rider until cross
#   to ib <- this applies only to a current rider that carried a reversal in lookback"*, which he
#   noted was *"current code, triggered by ws6r"*).
#   'ib' IS RULED BY MEASUREMENT, 1023, and that makes the code DELIBERATELY DIFFER FROM HIS
#   WRITTEN HANDOVER. Do not "fix" it back. Joe 1023, shown the 94-day A/B: *"let's align the
#   machine with ib"*. The two arms, everything else at the bank:
#       ib        565 trades, 66.9% win, +19,115.41 USDT, DD 344.61, net/DD 55.47, PF 3.61
#       reversal  594 trades, 66.2% win, +18,886.96 USDT, DD 426.85, net/DD 44.25, PF 3.39
#   So 'reversal' adds 29 trades and 82.24 USDT of drawdown, loses 20.2% of net-per-drawdown, and
#   ties on net. 'ib' wins every risk column. The knob stays so the spec reading is re-testable.
LIN_LOOKBACK_FLOORED = _knob('LIN_LOOKBACK_FLOORED', 1, int)   # 1 yes, 0 no
LIN_LOOKBACK_FLOOR_TF = _knob('LIN_LOOKBACK_FLOOR_TF', 6, int)  # the lowest rung that looks back
#   DOES THE LOOKBACK HAVE A TF FLOOR. Joe 1023, asked whether "starts at ws6r" means rungs below
#   ws6 never look back: *"yes. this needs to be a yes/no knob, and ws6 needs to be the
#   complimentary knob"*.
#   SO A RECEIVER BELOW THE FLOOR NEVER TESTS ITS LOOKBACK - it always takes the normal path, and
#   the baton-pass hatch cannot fire there.
#   WHERE IT CAME FROM. His hatch spec annotates the trigger *"<- current code, triggered by
#   ws6r"*, and the leg is 2026-08-31 19:45:40: ws5 hands to ws6, and ws6's reversal is already
#   105 s behind the baton at 19:43:55. I banked that annotation as "ws6r is the example" and
#   generalised the test to every rung - v4_lineage.md:213, *"it recurses without a special
#   case"*, which is my sentence, not his. He reads the annotation as the FLOOR.
#   THE CONDITIONS ARE STILL MISSING. He said the floor applies *"under specific conditions"* and
#   could not recall them; nothing in the repo records them. The floor is unconditional here.
#   THE NAMES ARE MINE. Joe has named neither knob.
#   THE DEFAULT IS ON because he ruled "yes". Every banked lineage number predates it, so the A/B
#   is reported beside it rather than the default being moved quietly.
TF_CEILING = _knob('TF_CEILING', 10, int)  # riderTF max. PROVISIONAL - his word is "unsure"

# ── v4saviour ─────────────────────────────────────────────────────────────────────────────────
SAV_WS2_OOB_TEST = _knob('SAV_WS2_OOB_TEST', 16.0)   # minutes. HIS NAME, his value
#   RAISED 10 -> 16 and ITS SCOPE WIDENED, Joe 1022: *"the ws2r oob CAP needs to also cover the
#   cases where ws1r does not reach oob.  increase CAP to {knob:16} minutes, and start the timer
#   when the trade opens"*. It is now ONE timer from the trade open covering the whole mech - the
#   ws1r oob run, its ib cross, the ws2r oob run and its ib cross - and no longer starts at the
#   ws1r ib cross. That supersedes his #27. The NAME is his and is kept, though it now bounds more
#   than the ws2r test.
SAV_IB_XWOB = _knob('SAV_IB_XWOB', 2, int)           # bars the ws1r oob->ib cross must hold
SAV_CASCADE_GAP = _knob('SAV_CASCADE_GAP', 12, int)      # bars between the coarse look-back samples
#   in mage_cascade_bar, for v4saviour's routed read ONLY. 12 bars = 1 min. Joe 1022: *"create a
#   v4-saviour specific knob that looks back in 1 minute jumps"*. The Jig's own MC_GAP stays at his
#   1017 value of 48 bars = 4 min and is still asserted; this is passed per call, so no other
#   consumer of the producer moves.
SAV_MAGE_GATE_WOB = _knob('SAV_MAGE_GATE_WOB', 8, int)   # bars ws1Mage must stay OUTSIDE the
#   past-50 gate before the branch-B walk routes back to the ws1r cascade test. Joe 1022: *"IF any
#   ws1Mage bar lands outside of the past-50-gate (wob 8), route to the ws1r mage-cascade test"*.
#   SAME VALUE as LIFT_WOB, DIFFERENT MECH - kept separate so moving one never moves the other.

#   THE CASCADE'S READ, for v4saviour's routed test ONLY. Joe 1022 asked for the look-back gap as a
#   v4saviour knob; ZOOM and MIN are the same shape and change the same verdict, so they are
#   captured here too and passed per call. MY STRUCTURAL CHOICE, stated: the Jig keeps his 1017
#   values as its own defaults and is still asserted, so no other consumer moves.
SAV_CASCADE_ZOOM = _knob('SAV_CASCADE_ZOOM', 2, int)     # rungs each cluster step compares across
SAV_CASCADE_MIN = _knob('SAV_CASCADE_MIN', 4, int)       # lines a cluster must cover
SAV_CASCADE_MODE = os.environ.get('W_V4_SAV_CASCADE_MODE', 'extrema')   # the bar picker's mode

# ── the trajectory read, for the dtf confluence ───────────────────────────────────────────────
TRAJ_WIDTH = _knob('TRAJ_WIDTH', 21.0)       # bars per TF-minute for rule2_trajectory's block.
#   Joe 1022: *"you'll see the peaks and troughs, and from there you can decide a dynamic
#   (width * TF) sampling width that will give you the best chance of ~accurately deciding
#   trajectory"* / *"lock it in"*. block = int(TRAJ_WIDTH * TF) = 1.75 of the line's OWN bar.
#   MEASURED over 4 days, 2026-08-31 to 09-04, against pivot-defined legs at 20 r-points. The
#   calibration target is lookahead; `trajectory` itself reads only backwards.
#       ws21r  85% accuracy, 71% coverage, skill 0.603 - its best of 13 widths
#       ws13r  86% accuracy, 74% coverage, skill 0.639 - its best of 13 widths
#   Both lines peak at the SAME width without being tuned separately, which is the compromise he
#   asked for. Joe 0924's fixed block 60 bars is width 2.5 here: 74% / 75% accuracy, skill 0.451 -
#   below the worst end of the useful range, because 60 bars is 0.21 of a ws21 bar.
#   Past 3 TF bars it collapses: width 60 reads 60% accuracy, barely a coin toss.
TRAJ_MIN_FRAC = _knob('TRAJ_MIN_FRAC', 0.5)  # min_bars as a fraction of the block. HELD at 0.5
#   through the width sweep and NOT swept itself - it has its own optimum and nobody has looked.
TRAJ_MIN_TRAVEL = _knob('TRAJ_MIN_TRAVEL', 0.0)  # the smallest |travel| that counts, r-points.
#   Joe 0924 left it unset: *"I would say the true threshold is in the OOS data"*. At 0.0 it passes
#   dust: 51 of 468 readings in the 1022 confluence test had a travel of EXACTLY zero and counted
#   as trajectory. The width does not fix that.

# ── v4-ws5rbackstop ───────────────────────────────────────────────────────────────────────────
BSTOP_SYNC_MIN = _knob('BSTOP_SYNC_MIN', 8.8)        # minutes either side of the ws5r reversal that
#   the ws1r / ws2r / ws3r same-side oob may land in. Joe 1022: *"the ws1r,ws2r,ws3r oob condition
#   has a +/-8.8 minute window to sync with ws5r reversing.  this needs to be causal"*.
BSTOP_POOL_HI = _knob('BSTOP_POOL_HI', 3, int)       # the oob pool is ws1r..ws{BSTOP_POOL_HI}r
BSTOP_OOB_WHEN = os.environ.get('W_V4_BSTOP_OOB_WHEN', 'window')     # DEFAULTED 1023
BSTOP_CASCADE_AT = os.environ.get('W_V4_BSTOP_CASCADE_AT', 'lift')   # DEFAULTED 1023
#   THE TWO BACKSTOP FORKS, now defaults. Joe 1023: *"I think all of our v4 mechs are groomed and
#   behaving well, so make them all default on their current configs"*. They were REQUIRED
#   parameters with no default, because he had not ruled them - `scan` refused to guess. Every run
#   since 1022 has passed 'window' and 'lift', and those are the values every number reported on
#   1022 and 1023 was measured under, so the default is the measured config and nothing else.
#     oob_when    'window' lets the ws1r/ws2r/ws3r oob land anywhere in the +/-BSTOP_SYNC_MIN;
#                 'at_fire' would also require a pool line to still be oob on the fire bar.
#                 Joe 1022 leaned 'window': *"I think the answer is 'just recent'"*.
#     cascade_at  'lift' reads the mage cascade at the ws5r reversal STAMP, which is his #25
#                 r-driven read; 'fire' would read it at the fire bar.
#   The assert in `scan` stays: an unknown value still refuses rather than falling back.

# ── lift-off ──────────────────────────────────────────────────────────────────────────────────
LIFT_PTS = _knob('LIFT_PTS', 6, int)        # samples in the window
LIFT_TOL = _knob('LIFT_TOL', 2.0)           # r-points off the window extreme
LIFT_WOB = _knob('LIFT_WOB', 8, int)        # bars the state must stay failed
GAP_PER_TF = _knob('GAP_PER_TF', 2.8)       # bars per TF-minute. PROVISIONAL until the sweep

# ── the r line config, and the account, BANKED 1023 ──────────────────────────────────────────
#   Joe 1023: *"bank k6 rsi8 stc6, make the current config (including 2 max_pyramid) the default
#   mech"*. It was chosen as centroid 2 on the SWEEP half alone and then came first on the
#   hold-out half (+211.71% against the previous bank's +86.49%), on full-tape net USDT
#   (+21,331.23 against +10,261.38) and on how much of its sweep rate survived the split
#   (0.92 against 0.69). The ordering was committed to before the hold-out was read.
# THE NAMES ARE WHAT THE SLOTS ACTUALLY HOLD, renamed 1023. Joe: *"I don't recollect on the
#   transposed knobs, I'll defer to you for the labelling"*. They were R_K / R_RSI / R_STC, which
#   read as k | rsi | stc - and the legacy tuple is ('k', rsi, stc, k_len, src), so the three
#   values were really rsi, stc and k_len. line_config.py's own opening paragraph names this bug:
#   *"Joe writes a k-line as k_len | rsi_len | stc_len | src. The legacy tuple was ('k', rsi_len,
#   stc_len, k_len, src) - Joe's FIRST number is the tuple's LAST."* It crept back because
#   v4_rcfg_sweep hand-wrote the positional tuple instead of using the named KLine.
#   THE ARRAYS DO NOT MOVE. KLine(k_len=6, rsi=6, stc=8).as_tuple() is ('k', 6, 8, 6, 'close'),
#   byte-identical to what was built, so every cached array stays addressed.
#
#   DEBANKED TO THE DB ROW, Joe 1024: *"the first thing we need to do is debank the r configs, so
#   that I can trust the charts that I built the spec on"*, then *"confirmed"* on R_KLEN 6 -> 7 and
#   R_RSI 6 -> 5.
#
#   WHY, and it is the root of a day of bad readings. There were TWO different configs in play:
#       the DB row       k_len 7, rsi 5, stc 8. mech_line_config mlc_pk 1, role 'r', mech 'wsf',
#                        live since 2026-01-01. THIS IS WHAT HIS CHARTS DRAW, and therefore what
#                        every spec he has written was read off.
#       the 1023 bank    k_len 6, rsi 6, stc 8. His own instruction - *"bank k6 rsi8 stc6, make the
#                        current config (including 2 max_pyramid) the default mech"* - chosen as
#                        centroid 2 of the 27-config sweep on the SWEEP half, then confirmed on the
#                        hold-out (+211.71% against +86.49%).
#   The sweep picked the best NET. The spec describes the CHARTS. For 1023 and most of 1024 the
#   code measured a config he has never looked at, and the mech readings were checked against it.
#   The sweep result is not discarded - it becomes a question for after the mechs match the spec:
#   does the net advantage survive once the build is faithful?
#
#   IN JOE'S NOTATION THE BANK IS NOW 7|5|8 - the DB row. 6|6|8 was the 1023 sweep centroid.
R_RSI = _knob('R_RSI', 5, int)              # the RSI length. DB mlc_rsi_len
R_STC = _knob('R_STC', 8, int)              # the STC length. DB mlc_stc_len - the DB and the 1023
#   sweep centroid agree on this one, so it is the only one that did not move.
R_KLEN = _knob('R_KLEN', 7, int)            # the StochRSI k length. DB mlc_k_len. The only one of
#   the three that moves the trade count much: k_len 6 carries roughly 2.4x the trades of k_len 7.
#   The finding was reported on 1023 as "stc is the only parameter that matters"; that was the
#   transposed reading.
MAX_PYRAMID = _knob('MAX_PYRAMID', 1, int)  # concurrent open positions the account will carry.
#   JOE'S WORD AND JOE'S NUMBER. 1024: *"set pyramid to 1"*. It is the LEVERAGE knob: N positions
#   open together means N stops can fire together, so the account-wipe leverage is
#   100 / (N x 1.100). At 1 that is 90.9x.
#   THE BOUNDARY IS `count < cap`, Joe 1024: *"count < cap is right"*. So 1 means at most one
#   position open in a direction, and a second signal on that side is DROPPED, not queued.
#   On 2026-09-01 the day is 19 trades at 1 against 27 at 2.

V4CORE_MAGE_FNC = _knob('V4CORE_MAGE_FNC', 5.0)   # the fence v4core's Mage test uses, mirrored.
#   Joe 1023 spec: *"(ws1Mage or ws2Mage are same-side past 5/95)"* / *"same-side past 5/95 means
#   <5 if target-side is low, >95 if target-side high"*, then *"fence knob: yes"*.
#   ONE KNOB, 100 - knob, the same form as OOB_FNC 15 and MID_FNC 50 - two separate knobs could
#   drift apart and one cannot. 5 -> (5.0, 95.0).
#   THE NAME IS MINE AND IT IS DELIBERATELY NOT "oob". oob is ALWAYS 15/85; this is a tighter
#   fence on the Mage lines for one mech, so it is named for the mech and the line it gates rather
#   than for a region. Joe has not named it.
#   HELD AT 5 UNTIL THE FULL WALK. Joe 1023: *"5/95 was my eyeballing. I wouldn't change it before
#   walking the full 6 day window, but it's an option"*. So it is a sweep candidate, not a ruling
#   he has defended - and the 10:26 arm he flagged reads ws1Mage 92.21 closed, which FAILS >95.
V4CORE_MAGE_LO, V4CORE_MAGE_HI = V4CORE_MAGE_FNC, 100.0 - V4CORE_MAGE_FNC

V4CORE_STEP0_JOIN = os.environ.get('W_V4_V4CORE_STEP0_JOIN', 'and')   # 'and' | 'or'
#   HOW STEP0 JOINS ws2r AND ws3r. Joe 1023: *"AND vs OR for step 0 needs to be a knob"*.
#   THE DEFAULT IS HIS AND HE GAVE THE MECHANISM, not a preference: *"STEP0 is specifically `AND`
#   to avoid re-entering mid cycle and creating a second stop"* / *"ws3r and ws2r represent the
#   humans' momentum cycles - when they are oob, a cycle is cycling. if one of these moments
#   creates a stop, I suspect an unstable market. waiting for (ws2r AND ws3r) feels like the safest
#   option we have for a profitable reentry."*
#   STEP0 ONLY. STEP2's join is `or` in his spec and is NOT knobbed - he asked for step 0.
#   THE NAME IS MINE, shaped like BSTOP_OOB_WHEN: a mode string with an assert rather than a
#   boolean, so a sweep row reads 'and' / 'or' instead of 1 / 0. Joe has not named it.

# THE CONTROL ROW'S TWO KNOWN-GOOD VALUES. 2026-09-03 00:35:00 on ws5r.
#   The control used to print ONE number against "ruled 12.48", which is the DB's
#   mech_lines('wsf') spec (k 5, rsi 8, stc 7). The moment the bank moved to k6 rsi8 stc6 that
#   label went stale: the banked line reads 6.77 at that bar, and the run printed "6.77 (ruled
#   12.48)" as though the cache had drifted. Both numbers are now named, and a run prints the one
#   that belongs to the line it is reading.
CONTROL_TS = '2026-09-03 00:35:00'
CONTROL_DB = 12.48                          # ws5r at 2026-09-03 00:35:00 on the DB row, which is
#   the BANK as of 1024. Every run's control row must read this.
CONTROL_BANK = 6.77                         # ws5r at the same bar on the 1023 sweep centroid
#   k_len 6 / rsi 6 / stc 8. Kept as the drift check against the config that was banked 1023-1024.

BARS_PER_MIN = 12                           # the 5 s grid

# ── v4core's SECOND ARM, Joe 1024. His words: *"add a second v4core arm: if ws1r is oob on target
#    side, min dwell 18 bars, and ws1Mage is same-side oob, and any TWO of ws4-8r are same-side
#    oob, arm."* STEP2's sibling - *"is it STEP2's sibling - yes"* - so either may fire.
ARM2 = _knob('ARM2', 1, int)                # 1 = the second arm is live
ARM2_DWELL = _knob('ARM2_DWELL', 18, int)   # bars the ws1r oob run must REACH. His number
ARM2_POOL_MIN = _knob('ARM2_POOL_MIN', 2, int)   # *"any TWO of ws4-8r"* - his number
CORE_LIN_ENTRY_TF = _knob('CORE_LIN_ENTRY_TF', 4, int)   # the rung v4core's SECOND ARM hands
#   lineage. HIS KNOB AND HIS NAME, 1024: *"maybe setting the entry TF to
#   {knob:4,'V4_CORE_LIN_ENTRY_TF'} will settle it"*. Read as W_V4_CORE_LIN_ENTRY_TF.
#   IT REPLACED ws1, which he first ruled - *"start from ws1. most of them are on the pivot, so
#   near-instant exhaust is typical behaviour"* - and then caught: *"there's a miswiring somewhere.
#   the A trade mech picked 0116 as the arm and walked it to 0137. this B trade has exhausted
#   immediate"*. Starting at ws1 makes the baton climb through ws2, and on the 2026-09-01 01:14:25
#   arm the emerging ws2r is 21.11 against the 20 fence, so the walk died at its first hand-off
#   with EXHAUST at 01:16:20. The oob at that bar sits at ws1r 10.14, then a HOLE at ws2r 21.11 and
#   ws3r 15.74, then ws4r 7.94 and ws5r 9.02 - so ws4 is where the walkable oob actually is, and it
#   is what the A-path backstop used to reach 01:37:10.

SAV_ARM_WALKBACK = _knob('SAV_ARM_WALKBACK', 30, int)   # minutes v4saviour's arm looks BACK from
#   the trade open for a counter-target-side ws5r extremum. Joe 1024: *"at trade open, walkback in
#   5 minute jumps (cap: 30 minutes) to find the ws5r extrema. if the extrema is oob, the gate is
#   closed and saviour may not fire"*, then *"full range"* on whether it samples the jumps or reads
#   every bar - so the extremum is over the WHOLE span, not 7 sampled points.
#   WHY HE ADDED IT, his own diagnosis: *"the LONG trades opening time was delayed by ~ws9
#   extending the open bar to a point where ws5r had already left oob"*. On the 2026-09-01 18:55:15
#   LONG the at-the-open arm read ws5r 47.99 and armed; the walkback finds 0.98 at 18:35:15, deep
#   LOW oob, so the gate closes and the 18:55 LONG runs on to the backstop's 19:43:15 SHORT.

# ── the ws4r handover inside the lineage walk. Joe 1024, NOT YET NAMED by him - he calls it
#    *"w4r to ws1Mage ib"*, so the prefix is descriptive of the lines and not a coined shorthand.
#    His 1024 framing: *"use the existing lineage code UNTIL ws4r is seen to be oob. when ws4r is
#    oob, the new mech finsihes the lineage flow"*, and *"if ws3r is able to pass the baton to
#    ws4r, then 'w4r to ws1Mage ib' takes over the walk and continues to exhaust"*.
LIN_W4 = _knob('LIN_W4', 0, int)            # 0 = arm A, the banked walk. 1 = arm B, the handover
LIN_W4_GRACE_S = _knob('LIN_W4_GRACE_S', 180, int)   # *"I propose we give 3 minutes grace"* - 1024
LIN_W4_G1_XWOB = _knob('LIN_W4_G1_XWOB', 4, int)     # bars IB must hold for the ws1Mage cross.
#                                             Joe 0911: *"reversal:2, boundary:4. both are knobs"*

# ── `sweep-pivots`, BANKED 1024. Joe named it; *"let's make it a machine and lock down the spec.
#    if there's knobs, make sure they're visible"*. The knobs live HERE, in the one home that
#    refuses an off-ruled run, and v4_sweep_pivots reads them from here.
SP_PICK = _knob('SP_PICK', 'lowest_pct', str)   # how a pivot is chosen from the index
SP_BAND = _knob('SP_BAND', 0.0)             # the near-same band, in pct POINTS
SP_CONTAIN = _knob('SP_CONTAIN', 0, int)    # 1 = the event must fall inside the TF's leg
SP_XWOB = _knob('SP_XWOB', 18, int)         # bars IB must hold for a Mage oob->ib cross
SP_ALIGN_S = _knob('SP_ALIGN_S', 300, int)  # the alignment window, seconds. READ ONLY by the
#                                             'window' PICK arm; 'lowest_pct' never reads it
SP_TFS = _knob('SP_TFS', 'wide', str)       # 'his' = his six, 'wide' = plus ws1Mage and ws2Mage
#   ALL SIX GO THROUGH _knob, so all six read the ONE prefix W_V4_SP_* and all six are covered by
#   check(). SP_PICK and SP_TFS were written reading W_SP_* directly, which put them outside the
#   refusal: an off-ruled SP_PICK ran as the machine and reported RULED_OK True.

# -- lineage2, the 1025 FORK ------------------------------------------------------------------
#   A FORK, not an arm of v4lineage. Joe 1025: *"I need a lineage2 fork of lineage - we're going to
#   play with a new idea"*. Nothing in the machine calls it; the knobs live here because v4_knobs is
#   the one knob home and a knob outside it cannot be checked.
L2_MOM_MAXTF = _knob('L2_MOM_MAXTF', 12, int)   # *"v4mom_maxTF = 12"*. The ladder's top rung.
L2_LIN_HOP = _knob('L2_LIN_HOP', 2, int)        # *"lin_hop = 2"*. Max hops rider -> candidate, and
#   it applies ONLY between cadence events. Joe 1025: *"when baton is being passed between cadence
#   markers, linhop applies. at a cadence event, linhop doesn't apply"*.
L2_T1_GRACE_S = _knob('L2_T1_GRACE_S', 120, int)  # *"the 2 minutes (CAUSALLY) following"*, and he
#   confirmed it is a knob. Seconds, forward of the cws1b oob->ib cross.
L2_GATE_MODE = _knob('L2_GATE_MODE', 'emerging', str)   # which ladder t3cadence's GATES read.
#   Joe 1026: *"build a proxy that sends the emerging values to the gate decision"*. The two gates
#   are t3's *"have been oob already in this trade"* population and its *"no higher TFs exfence"*
#   test; every other fence read stays CLOSED on his *"more accurate fence/exfence baton
#   decisions"*. 'closed' is the other arm of the A/B and `v4_l2_proxy.Board` is the one place the
#   routing lives.
#   WHAT IT MOVES, on his 2026-08-30 18:37 LOW walk: ws7r reaches LOW oob at 19:57:00 closed and
#   19:50:00 emerging, so t3 moves 7 minutes earlier. It does NOT reach the 19:20 he eyeballed -
#   ws7r's reversal stamp is 19:20:10 on both ladders, 30 minutes BEFORE either oob.
L2_CWS1R_WOB = _knob('L2_CWS1R_WOB', 1, int)    # lineage2 ONLY: the lift-off wob on cws1r, for
#   t1cadence's reversal. Joe 1026: *"a lineage2-only wob 1 for cws1r"*, after the measurement he
#   asked for. LIFT_WOB 8 does 69.4% of its filtering on the EMERGING ws1r and 3.0% on the closed
#   cws1r, and on 99.2% of cws1r lift-offs the VALUE does not move across the whole 8-bar hold -
#   the wob is shorter than one cws1r bar, so it holds a state the line cannot change. His words:
#   *"cws1 is closed bar, so the wob is built-in"*.
#   IT IS SEPARATE FROM LIFT_WOB ON PURPOSE. LIFT_WOB 8 is read by v4lineage, v4core, the backstop
#   and v4saviour; moving it would add 55,533 LOW lift-offs on the emerging ws1r alone.
L2_RE_IB_MIN = _knob('L2_RE_IB_MIN', 2, int)    # v4_reentry: how many Mage rungs above ws5 must
#   stay IB for the WHOLE ws5Mage oob run. Joe 1026 corrected his own wording: *"my 'any TF >5'
#   meant 'if any of the TFs higher than TF5' - I was looking for just one TF above 5 to be ib
#   while ws5Mage was oob"*, then *"on hindsight, it should be 2 or more TFs that were ib while
#   ws5Mage was oob"*. It is a COUNT of rungs that stayed in, not an all-of test - the first build
#   read his words as "no rung reached oob" and blocked 3 of his 4 examples.
L2_T3_FRAC = _knob('L2_T3_FRAC', 0.75)          # *"int(round(75%))"* of the HTF lines that HAVE
#   BEEN oob since the arm bar - his population, confirmed 1025, not all of ws7..ws12.
#   v4mom_fnc IS RMOM_FNC. Joe 1025, asked whether they are the same knob: *"yes"*. So there is no
#   L2 fence knob - moving RMOM_FNC moves lineage2 too, on purpose.
#   v4cadence_fnc is DROPPED. Joe 1025 asked *"#JOE, is this needed?"* and then: *"drop"*.
#   NO ib-CROSS DWELL KNOB EXISTS HERE. Joe 1025: *"no dwell. the way I see it: because we're on
#   closed bars, we have an automatic wob. it also means I have TV values that are precisely
#   aligned with what the code sees"*.

#   name                value              Joe's words, 1022 unless dated
RULED = {
    'RMOM_FNC':         (80.0,  '"v4_rmom_fnc, default 80 - fence used when testing if a r is close'
                                ' enough to oob to be predicted"'),
    'LIN_HOP':          (2,     '"1, 2"'),
    'IB_WOB':           (3,     '"10, 3"' + ' - SUPERSEDED by LIN_IB_DWELL'),
    'LIN_IB_DWELL':     (2.5,   '"it needs to be dynamic: let\'s start with'
                                ' int(TF * {knob:2.5, `V4_LIN_IB_DWELL`})"'),
    'TF_CEILING':       (10,    '"18, unsure.  use 10" - PROVISIONAL'),
    'LIN_PASS':         ('ib',  'the code\'s original. His 1022 spec says "reversal" - 1023'),
    'LIN_LOOKBACK_FLOORED': (1, '"yes" to rungs below ws6 never looking back - 1023'),
    'LIN_LOOKBACK_FLOOR_TF': (6, '"ws6 needs to be the complimentary knob" - 1023'),
    'R_RSI':            (5,     'DEBANKED to the DB row 1024 - see the R_* block above'),
    'R_STC':            (8,     'DEBANKED to the DB row 1024 - unchanged, the DB and the sweep'
                                ' centroid agree on stc'),
    'R_KLEN':           (7,     'DEBANKED to the DB row 1024 - see the R_* block above'),
    'MAX_PYRAMID':      (1,     '"set pyramid to 1" - 1024'),
    'BSTOP_OOB_WHEN':   ('window', '"I think the answer is \'just recent\'" - 1022,'
                                   ' defaulted 1023'),
    'BSTOP_CASCADE_AT': ('lift', '"not extrema - measure where the r reversals print" - #25,'
                                 ' defaulted 1023'),
    'V4CORE_MAGE_FNC':  (5.0,   '"same-side past 5/95" - 1023, his eyeballing, held'),
    'V4CORE_STEP0_JOIN': ('and', '"STEP0 is specifically AND to avoid re-entering mid cycle and'
                                 ' creating a second stop" - 1023'),
    'SAV_WS2_OOB_TEST': (16.0,  '"increase CAP to {knob:16} minutes, and start the timer'
                                ' when the trade opens"'),
    'SAV_IB_XWOB':      (2,     '"23, 2"'),
    'SAV_MAGE_GATE_WOB': (8,    '"IF any ws1Mage bar lands outside of the past-50-gate (wob 8),'
                                ' route to the ws1r mage-cascade test"'),
    'SAV_CASCADE_GAP':  (12,    '"create a v4-saviour specific knob that looks back in 1 minute'
                                ' jumps"'),
    'SAV_CASCADE_ZOOM': (2,     '"26, 2 knob" - the Jig\'s MC_ZOOM, captured at v4 level'),
    'SAV_CASCADE_MIN':  (4,     'his 1017 "4 or more consecutive TFs" - the Jig\'s MC_MIN,'
                                ' captured at v4 level'),
    'SAV_CASCADE_MODE': ('extrema', '"25, not extrema - measure where the r reversals print" for the'
                                ' r-driven reads; the ROUTED read is anchored on the ws1Mage'
                                ' extrema, so this mode is \'extrema\''),
    'TRAJ_WIDTH':       (21.0,  '"lock it in" - 1.75 of the line\'s own bar, the measured peak'
                                ' on BOTH ws21r and ws13r'),
    'TRAJ_MIN_FRAC':    (0.5,   'HELD at 0.5 through the width sweep, NOT swept itself'),
    'TRAJ_MIN_TRAVEL':  (0.0,   'Joe 0924: *"I would say the true threshold is in the OOS data"*'
                                ' - UNSET, and it passes dust'),
    'BSTOP_SYNC_MIN':   (8.8,   '"the ws1r,ws2r,ws3r oob condition has a +/-8.8 minute window to'
                                ' sync with ws5r reversing.  this needs to be causal"'),
    'BSTOP_POOL_HI':    (3,     '"(ws1r or ws2r or ws3r are same side oob)"'),
    'OOB_FNC':          (15.0,  'standing - oob is ALWAYS 15/85. ONE knob: *"oob_hi and oob_lo are'
                                ' expressed as one knob, to avoid imbalnace.  the formula is'
                                ' (100 -{knob:15})"*'),
    'MID_FNC':          (50.0,  '"change `mid` to a fence, same logic as above.'
                                ' 100-{knob:50}"'),
    'LIFT_PTS':         (6,     '"34, 6 knob"'),
    'LIFT_TOL':         (2.0,   '"35, 2.0 knob"'),
    'LIFT_WOB':         (8,     '"37, 8 knob" and "add a wob 8 to reduce the early reversals"'),
    'GAP_PER_TF':       (2.8,   '"let\'s choose 2.8 until we get to the sweep" - PROVISIONAL'),
    # ── sweep-pivots, 1024 ──────────────────────────────────────────────────────────────────────
    'SP_PICK':      ('lowest_pct', '"start at the lowest TF and scan upwards ... the TF swing/pivot'
                                   ' to pick should be the highest TF printing the lowest pct'
                                   ' (between pivot and event)" - 1024'),
    'SP_BAND':      (0.0,   'his near-same band. MEASURED: 53.6% of the 37,178 consecutive-pct'
                            ' gaps are EXACTLY 0 - TFs sharing a leg extremum - and p10 to p50 are'
                            ' all 0.0000 while p75 is 0.3705. So 0.0 already captures the'
                            ' clustering; widening to 0.5 cost 43.6% -> 28.8% within 0.25% of the'
                            ' pivot and bought only +1.397% -> +1.802% of leg. No knee - 1024'),
    'SP_CONTAIN':   (0,     'OFF. Right on the 3 events it was proposed against, wrong on 5,323:'
                            ' 2,198 events lose EVERY candidate, the median candidate count falls'
                            ' 8.0 -> 1.0, and the median distance off the pivot goes 0.327% ->'
                            ' 1.157% with the worst 8.953% -> 26.146% - 1024'),
    'SP_XWOB':      (18,    '"introduce a wob 18 and retest" - 1024. The only wob he named for'
                            ' this mech. It lifted the MFE-side rate on every TF'),
    'SP_ALIGN_S':   (300,   '"agreed on 300s" - 1024. UNREAD by the banked SP_PICK; it gates only'
                            ' the \'window\' arm, kept as the comparison'),
    'ARM2':         (1,     'v4core\'s second arm, live. "add a second v4core arm" - 1024'),
    'ARM2_DWELL':   (18,    '"min dwell 18 bars" - 1024. The ws1r oob run\'s own length, so the'
                            ' earliest arm is bar 18 of the run'),
    'ARM2_POOL_MIN': (2,    '"any TWO of ws4-8r are same-side oob" - 1024'),
    'CORE_LIN_ENTRY_TF': (4, '"maybe setting the entry TF to {knob:4,\'V4_CORE_LIN_ENTRY_TF\'}'
                             ' will settle it" - 1024, replacing his earlier "start from ws1"'),
    'SAV_ARM_WALKBACK': (30, '"at trade open, walkback in 5 minute jumps (cap: 30 minutes) to find'
                             ' the ws5r extrema. if the extrema is oob, the gate is closed and'
                             ' saviour may not fire" - 1024, with "full range" on the sampling'),
    'LIN_W4':       (0,     'arm A is the bank. The handover is arm B of the 1024 A/B and is NOT'
                            ' the machine until he rules it'),
    'LIN_W4_GRACE_S': (180, '"I propose we give 3 minutes grace to overcome the scenario" - 1024.'
                            ' UNANCHORED: the jump-back distribution has no knee, p75 is 0.3705'),
    'LIN_W4_G1_XWOB': (4,   'Joe 0911 "reversal:2, boundary:4. both are knobs" - the boundary one'),
    'SP_TFS':       ('wide', 'THE ONE ITEM AWAITING HIS WORD. His 1024 list was SIX - ws3Mage,'
                             ' ws5Mage, ws10Mage, ws15Mage, ws20Mage, ws30Mage. ws1Mage and'
                             ' ws2Mage are MINE, and every measurement that justified banking used'
                             ' all eight, so the banked value is the one that was RUN. On his six'
                             ' alone the 18-row check scores 8 of 18 against 17 of 18. At'
                             ' ALIGN_S 300 ws1Mage and ws2Mage are the scale TF on 41.0% of events'),
    'L2_MOM_MAXTF': (12,    '"v4mom_maxTF = 12" - 1025, the lineage2 fork'),
    'L2_LIN_HOP':   (2,     '"lin_hop = 2" - 1025. Applies BETWEEN cadences only, his ruling'),
    'L2_T1_GRACE_S': (120,  '"the 2 minutes (CAUSALLY) following" - 1025, confirmed a knob'),
    'L2_T3_FRAC':   (0.75,  '"int(round(75%))" - 1025, of the HTF lines that have been oob since'
                            ' the arm bar'),
    'L2_GATE_MODE': ('emerging', '"build a proxy that sends the emerging values to the gate'
                                 ' decision" - 1026. t3cadence\'s two gates only'),
    'L2_CWS1R_WOB': (1,     '"a lineage2-only wob 1 for cws1r" - 1026. On the closed line the wob'
                            ' suppresses 3.0% against the emerging line\'s 69.4%, and the value is'
                            ' unchanged across the whole hold on 99.2% of lift-offs'),
    'L2_RE_IB_MIN': (2,     '"it should be 2 or more TFs that were ib while ws5Mage was oob" -'
                            ' 1026. He asks whether 2 is too loose; the sweep-pivot scoring of the'
                            ' signals it produces is the measurement he called for'),
}

#   the Jig's own, Joe 1017. Asserted, never re-declared.
CASCADE_RULED = {'MC_GAP': 48, 'MC_ZOOM': 2, 'MC_MIN': 4, 'MC_TF_LO': 1, 'MC_TF_HI': 12}


def fence():
    """RMOM_FNC mirrored. 80 -> (20.0, 80.0). The trade side picks the end."""
    return (100.0 - RMOM_FNC, RMOM_FNC)


def oob(v, side):
    """Is v out of bounds on `side`. oob is 15/85, always."""
    return (float(v) >= OOB_HI) if side > 0 else (float(v) <= OOB_LO)


def ib(v):
    """Is v in bounds."""
    return OOB_LO < float(v) < OOB_HI


def ex_fence(v, side):
    """Is v past the r fence on `side`."""
    lo, hi = fence()
    return (float(v) >= hi) if side > 0 else (float(v) <= lo)


def mid_fence():
    """MID_FNC as (lo, hi). 50 -> (50.0, 50.0); 45 would be (45.0, 55.0)."""
    return (MID_LO, MID_HI)


def side_of(v):
    """+1 high side, -1 low side. Joe 1022: low side is < 50, high side > 50. 50 itself is LOW,
    because his rule is "< 50" and "> 50" and one of them must own the boundary - STRUCTURAL,
    and stated rather than decided quietly. At MID_FNC below 50 a value inside the band reads LOW
    for the same reason, and that case is UNRULED - see the MID_FNC comment."""
    return 1 if float(v) > MID_HI else -1


def looks_back(tf):
    """May this rung test its lookback. -> bool

    Joe 1023: *"yes"* to rungs below ws6 never looking back, *"this needs to be a yes/no knob, and
    ws6 needs to be the complimentary knob"*. With the floor OFF every rung looks back, which is
    what the code did from 1022 until now.
    """
    if not LIN_LOOKBACK_FLOORED:
        return True
    return int(tf) >= LIN_LOOKBACK_FLOOR_TF


def walkable_run(R, k, side, hold_tf=5, max_tf=None):
    """The CONTIGUOUS same-side oob run holding `hold_tf` at bar k. -> (lo, hi) or None.

    Joe 1023: *"at v4-ws5rbackstop's signal, find the highest same-side oob ws{1-maxTF}r and pass
    it to lineage"*, then, shown a set of ws4, ws5, ws7: *"why is ws7 there? the v4lineage spec
    only allows jumps of +1"*. So the set must be CONSECUTIVE - an oob rung lineage cannot reach
    by +1 steps is a separate island and is not part of the run. At that fire the walkable run is
    ws4-ws5 and ws7 is excluded.

    THEN: *"swap `highest` with `lowest`"*. The caller takes `lo`.

    `hold_tf` is ws5 because the backstop is a ws5r mech - the run must contain the line the fire
    came from. 134 of 602 fires have no such run, because ws5r had already left oob by the time the
    oob partner set the fire bar. Those return None and are the caller's to rule.
    THE COUNT MOVED WITH THE DEBANK. 175 of 1086 was measured on the 1023 centroid config
    (k_len 6, rsi 6, stc 8); on the DB row the r config is R_RSI 5 / R_STC 8 / R_KLEN 7 and the
    tape carries 602 fires. Re-measured 1024.

    CAUSAL: every line is read at bar k, which is the fire bar.
    """
    mx = TF_CEILING if max_tf is None else int(max_tf)
    if not oob(R[hold_tf][k], side):
        return None
    lo = hi = int(hold_tf)
    while lo - 1 >= 1 and oob(R[lo - 1][k], side):
        lo -= 1
    while hi + 1 <= mx and oob(R[hi + 1][k], side):
        hi += 1
    return lo, hi


def step0_r_ok(r2, r3, side):
    """STEP0's ws2r/ws3r test on `side`, joined by V4CORE_STEP0_JOIN. -> bool

    Joe 1023 ruled the default 'and' WITH its reason: the two lines are the momentum cycles, and
    waiting for both out of bounds avoids re-entering mid cycle and taking a second stop. STEP2's
    join stays `or` and is not this knob's business.
    """
    assert V4CORE_STEP0_JOIN in ('and', 'or'), \
        'V4CORE_STEP0_JOIN %r is not a mode' % (V4CORE_STEP0_JOIN,)
    a, b = oob(r2, side), oob(r3, side)
    return (a and b) if V4CORE_STEP0_JOIN == 'and' else (a or b)


def step2_r_ok(r2, r3, side):
    """STEP2's ws2r/ws3r test on `side`. Joe's spec says `or` and it is not knobbed."""
    return oob(r2, side) or oob(r3, side)


def past_v4core_mage(v, side):
    """Is v past v4core's Mage fence on `side`. high: v > 95. low: v < 5.

    Joe 1023: *"same-side past 5/95 means <5 if target-side is low, >95 if target-side high"*.
    STRICTLY past, which is his wording, so exactly 5.0 or 95.0 does not pass.
    """
    return (float(v) > V4CORE_MAGE_HI) if int(side) > 0 else (float(v) < V4CORE_MAGE_LO)


def past_mid(v, side):
    """Is v past the middle fence on `side`. high: v > MID_HI. low: v < MID_LO."""
    return (float(v) > MID_HI) if int(side) > 0 else (float(v) < MID_LO)


def gap_for(tf):
    """The lift-off sample gap for a timeframe, in bars. TF x GAP_PER_TF, rounded.

    Joe 1022 ruled the rounding: *"38, yes"* to round(). ws3 8.4 -> 8, ws7 19.6 -> 20.
    """
    return max(1, int(round(int(tf) * GAP_PER_TF)))


def lift_stamp(b):
    """The bar a lift-off at `b` becomes KNOWABLE. b + LIFT_WOB - 1, the last bar of the hold.

    jig.lift_off's own contract, 1022: *"A wob of n means the event is not KNOWABLE until
    bar + n - 1 ... This returns the lift-off bar ... the consumer adds the wob"*. Every consumer
    adds it HERE, so there is one copy of the arithmetic. At LIFT_WOB 8 the stamp is b + 7 bars
    = 35 s after the line left its extreme.
    """
    return int(b) + max(1, int(LIFT_WOB)) - 1


def lin_ib_dwell(tf):
    """The lineage ib dwell for a timeframe, in bars. int(TF * LIN_IB_DWELL), Joe's own formula."""
    return max(1, int(int(tf) * LIN_IB_DWELL))


def traj_block(tf):
    """rule2_trajectory's block for a timeframe, in bars. int(TRAJ_WIDTH x TF), Joe's own form."""
    return max(2, int(round(int(tf) * TRAJ_WIDTH)))


def traj_min_bars(tf):
    """its min_bars: TRAJ_MIN_FRAC of the block. HELD, not swept."""
    return max(1, int(traj_block(tf) * TRAJ_MIN_FRAC))


def bstop_sync_bars():
    """BSTOP_SYNC_MIN in bars. 8.8 min = 106 bars at the 5 s grid."""
    return int(round(BSTOP_SYNC_MIN * BARS_PER_MIN))


def sav_cap_bars():
    """V4_SAV_WS2_OOB_TEST in bars. 16 min = 192 bars at the 5 s grid. ONE timer from the open."""
    return int(round(SAV_WS2_OOB_TEST * BARS_PER_MIN))


def check(out=None):
    """THE RULED CHECK. Refuses an off-ruled run unless W_V4_EXPERIMENT=1. Called at import."""
    out = out or sys.stderr
    here = globals()
    off = [(k, here[k], v, why) for k, (v, why) in RULED.items() if here[k] != v]
    try:
        from optimus9.analysis import jig as _j
        cas = [(k, getattr(_j, k), v) for k, v in CASCADE_RULED.items() if getattr(_j, k) != v]
    except Exception as e:                       # the Jig must be importable for a v4 run
        raise RuntimeError('v4 cannot read the cascade rulings from the Jig: %s' % e)
    if cas:
        raise RuntimeError('the Jig\'s cascade knobs have moved off Joe 1017\'s rulings: '
                           + '; '.join('%s is %r, ruled %r' % c for c in cas))
    if not off:
        return True
    msg = '; '.join('%s is %r, ruled %r (%s)' % (k, got, want, why) for k, got, want, why in off)
    if not EXPERIMENT:
        raise RuntimeError('OFF-RULED v4 run refused. ' + msg
                           + '. Set W_V4_EXPERIMENT=1 to run it as an experiment.')
    out.write('# W_V4_EXPERIMENT=1 - THIS IS NOT THE MACHINE. %d knob(s) off the bank: %s\n'
              % (len(off), msg))
    return False


RULED_OK = check()


def table():
    """Every banked knob, one row each, for a report."""
    here = globals()
    rows = [('| the knob | value | units | ruled | Joe\'s words |'), ('|---|---|---|---|---|')]
    units = {'RMOM_FNC': 'r-points', 'LIN_HOP': 'TFs', 'IB_WOB': 'bars',
             'R_RSI': 'bars', 'R_STC': 'bars', 'R_KLEN': 'bars', 'MAX_PYRAMID': 'positions',
             'BSTOP_OOB_WHEN': 'mode', 'BSTOP_CASCADE_AT': 'mode', 'LIN_PASS': 'mode',
             'LIN_LOOKBACK_FLOORED': 'yes/no', 'LIN_LOOKBACK_FLOOR_TF': 'TF',
             'V4CORE_MAGE_FNC': 'r-points', 'V4CORE_STEP0_JOIN': 'mode',
             'TF_CEILING': 'TF', 'LIN_IB_DWELL': 'bars per TF', 'TRAJ_WIDTH': 'bars per TF-minute',
             'L2_MOM_MAXTF': 'timeframe', 'L2_LIN_HOP': 'timeframe hops',
             'L2_T1_GRACE_S': 'seconds', 'L2_T3_FRAC': 'fraction of the oob HTF lines',
             'L2_RE_IB_MIN': 'Mage rungs that stayed IB', 'L2_CWS1R_WOB': 'bars',
             'TRAJ_MIN_FRAC': 'fraction of the block', 'TRAJ_MIN_TRAVEL': 'r-points', 'SAV_WS2_OOB_TEST': 'minutes', 'SAV_IB_XWOB': 'bars',
             'SAV_MAGE_GATE_WOB': 'bars', 'SAV_CASCADE_GAP': 'bars',
             'LIFT_PTS': 'samples', 'LIFT_TOL': 'r-points', 'LIFT_WOB': 'bars',
             'OOB_HI': 'r-points',
             'GAP_PER_TF': 'bars per TF-minute', 'SAV_CASCADE_ZOOM': 'rungs',
             'SAV_CASCADE_MIN': 'lines', 'SAV_CASCADE_MODE': 'mode', 'OOB_HI': 'r-points',
             'OOB_FNC': 'r-points', 'MID_FNC': 'r-points',
             'BSTOP_SYNC_MIN': 'minutes', 'BSTOP_POOL_HI': 'TF'}
    for k, (v, why) in RULED.items():
        rows.append('| `%s` | %s | %s | %s | %s |'
                    % (k, here[k], units[k], 'YES' if here[k] == v else 'NO - off the bank', why))
    return '\n'.join(rows)
