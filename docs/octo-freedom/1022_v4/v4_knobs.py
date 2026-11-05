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
RMOM_FNC = _knob('RMOM_FNC', 75.0)        # the r fence, mirrored. 80 -> (20, 80)
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
LIN_PASS = os.environ.get('W_V4_LIN_PASS', 'ib')   # 'ib' | 'reversal' | 'reversal+quarter'
LIN_PASS_QUARTER = _knob('LIN_PASS_QUARTER', 0.25)   # the fraction of the TF width the third mode
#   waits after a reversal. THE 0.25 IS HIS, from his worked example; the knob NAME and the mode
#   string 'reversal+quarter' are MINE and he has not named either.
#   HIS WORDS, 1031: *"swaps "ib" with "reverasal + 1/4 width of the TF" -eg a ws22 rider has
#   reversed ex fence at 0756, the baton pass happens at (0756 + (0.25 * 22 minutes)"*.
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
SAV_CASCADE_TF_HI = _knob('SAV_CASCADE_TF_HI', 12, int)  # the cascade ladder's top rung.
#   12 IS THE BANKED VALUE and it is what v4_machine.py gets. HIS 1103 ASK for fdm2's own use of
#   v4saviour is 6 - *"reduce the mage cascade to ws1-ws6"* - and fdm2's driver passes that
#   explicitly rather than moving this default, because moving it changes the live machine.
#   AT 6 THE LADDER IS 6 LINES, so SAV_CASCADE_MIN 4 is still reachable: a cluster can cover 4, 5
#   or 6 of them. At 3 it could not, and the verdict would be 'neither' on every bar.
SAV_CASCADE_ANCHOR = os.environ.get('W_V4_SAV_CASCADE_ANCHOR', 'liftoff')   # 'liftoff'|'ws1mage'
#   WHICH BAR THE CASCADE IS READ AT.
#     'liftoff'   the r line's most recent lift-off STAMP at or before the ib cross. His #25,
#                 *"not extrema - measure where the r reversals print"*, and the banked value
#     'ws1mage'   ws1Mage's most recent target-side extremum, via mage_cascade_bar - the same
#                 anchor his ws1Mage route already uses. HIS 1103 *"test at the ws1Mage extremum"*
#   AT 'ws1mage' THE r LINE IS NOT READ FOR THE ANCHOR AT ALL, so the lift-off's emerging read
#   drops out and every cascade input is the chart-matched one.

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
L2_MOM_MAXTF = _knob('L2_MOM_MAXTF', 30, int)   # *"v4mom_maxTF = 12"*. The ladder's top rung.
L2_LIN_HOP = _knob('L2_LIN_HOP', 2, int)        # *"lin_hop = 2"*. Max hops rider -> candidate, and
#   it applies ONLY between cadence events. Joe 1025: *"when baton is being passed between cadence
#   markers, linhop applies. at a cadence event, linhop doesn't apply"*.
L2_T1_GRACE_S = _knob('L2_T1_GRACE_S', 120, int)  # *"the 2 minutes (CAUSALLY) following"*, and he
#   confirmed it is a knob. Seconds, forward of the cws1b oob->ib cross.
# -- the t3 REPLACEMENT, Joe 1026. A 2-STAGED LATCH ------------------------------------------
#   HIS SPEC, verbatim: *"I see a potential replacement for t3, and it's 2-staged latch / 1st latch,
#   the bearish divergence that fires on the 2151 t1 cadence / 2nd latch, ws7r reversing (with
#   wob12) and no baton candidate options PLUS the supporting ws4,5,6r matryoshka reversals"*.
#   Then *"the old t3 is defunct"*, so L2_T3_ON's default moves to 0 below.
LIN2_CAD_LATCH_ON = _knob('LIN2_CAD_LATCH_ON', 1, int)      # the latch on/off. BANKED ON - it is his mech.
LIN2_T3_MIN_TF = _knob('LIN2_T3_MIN_TF', 5, int)    # HIS NAME AND HIS VALUE, 1026:
#   *"the rider between ws{knob:5,'lin2_t3_min_tf'} and ws12"*. The rider range latch 2 accepts.
LIN2_CAD_LATCH_LIFE_S = _knob('LIN2_CAD_LATCH_LIFE_S', 600, int)   # *"3, 10 minutes (knob)"* - how long
#   latch 1 stays latched. Seconds. HE SET THE VALUE; the knob's NAME is mine, not his.
LIN2_SUPPORT_LINES = _knob('LIN2_SUPPORT_LINES', 3, int)   # *"7, 3 lines below the rider"*. ALL of
#   them must have reversed - his original reading named ws4, ws5 and ws6 under a ws7 rider.
LIN2_RELATCH_ON = _knob('LIN2_RELATCH_ON', 1, int)   # THE EX-FENCE LATCH RE-LATCH, on/off.
#   HIS MECH, 1031, verbatim: *"if lift off prints a reversal for a line, and that line's value
#   falls back to the value printed at lift-off, re-enable the latch"*, with his candidate rule:
#   *"if ws12 is printing 31, then it's infence and it must return to ex-fence if it wants to be
#   latched. it shouldn't be included in the "bump that pushes a line towards infence, only to fail
#   reaching infence" candidates"*.
#   WHY IT EXISTS. Under LIN2_EXFNC_LATCH_REL 'lift' a lift-off can fire while the line is STILL
#   ex-fence, which ends the episode; the on-edge is a CROSS from in-fence to ex-fence, so a line
#   that has not reached in-fence has no edge available and stays unlatched. His read: *"the
#   reversal "bumped" the line closer to in-fence, but infence was never reached"*. Measured on
#   2026-08-14 07:02:10 at fence (25.0, 75.0): ws5 19.09, ws7 22.93 and ws8 4.46 were all past the
#   low fence with no latch, ws8 for 11.3 min.
#   THE THREE TESTS, all his:
#     1  the lift-off that released the latch fired while the line was STILL ex-fence - read at the
#        RAW lift-off bar, his ruling *"understood and agreed"*: the raw bar is where the event
#        happened, the stamp is 7 bars = 35 s later and the line has moved further by then.
#     2  and the line has not reached in-fence between that lift-off and the bar being tested.
#     3  and the line's value has come back to the value it printed at that lift-off.
#   AT CADENCES ONLY, his ruling and his reason: *"cadence only.  the point of cadences: at ws1r
#   reversing, that is the moment when matryoshka is leading the higher lines direction"*.
#   WHAT RELEASES A RE-LATCHED LINE: the next lift-off on that line, his *"yes"*. The code takes
#   the LAST release at or before the bar, so a new lift-off becomes the release in force and is
#   reviewed afresh at the following cadence. No extra state.
#   NO EXTRA HOLD ON THE RE-LATCH. LIN2_EXFNC_LATCH_WOB 4 debounces a CROSS; a re-latch is not a
#   cross, and the cadence bar IS the decision bar. STRUCTURAL, stated, not his.
#   "AT OR BEYOND" ON TEST 3: on a low side the value must be at or BELOW the lift-off value, on a
#   high side at or above. The inclusive form is MINE - he wrote "falls back to the value".
#   DEFAULT OFF so the arm is measured before it is banked.
#  -- HIS 1101 DIVERGENCE-AT-A-CADENCE UPDATE -----------------------------------------------------
#   His words: *"divergence update: -divergence currently fires at the arm / -floater_anchor/
#   divergence and PM (price matching) also needs to be tested at a cadence even. ordered before
#   lineage (ie lineage tests after devergence tests) / -examples on 09-03 / --bullish 2324, floater
#   2312 / --bullish 0437, floater 0418"*.
#   WHY IT WAS BUILT: no ex-fence latch wob can exhaust the 2026-09-03 04:37:55 cadence. Measured
#   across 17 values from 1 to 480 bars - at 120 bars = 600 s the candidate set empties and the bar
#   lands on HOLD, never on EXHAUST, because HOLD fires on `baton_oob(rider)` and ws12r reads 13.56
#   against the 15.0 oob fence. His condition: *"I want a ex-fence wob that creates an exhaust ar
#   0437.  if that can't be done, then we have to apply this new update now"*.
#   *** HIS 1101 RULING: DIVERGENCE IS COMPLETELY DISABLED, AND ws1r IS THE WRONG LINE FOR IT. ***
#   Verbatim: *"divergence can be completely disabled.  in the notes, make it clear that ws1r is not
#   the best divergence test: ws1 works in small cycles that are not profitable.  ws3r seems to have
#   more divergence potential (eyeballed)"*.
#   HIS EYEBALL READ IS A RESULT, not an absence of one: ws3r has the divergence potential, ws1r's
#   cycles are too small to be worth trading. No ws3r divergence has been measured here - the line
#   the producer reads is ws1r (CL['r'][1]) at every call site - so ws3r is a BUILD he has not asked
#   for yet, and this note is the record of why it would be the one to build.
LIN2_DIV_ON = _knob('LIN2_DIV_ON', 0, int)   # HIS KNOB NAME. The divergence test AT EVERY CADENCE,
#   on/off. At 0 the divergence runs only at the arm, which is the pre-1101 behaviour.
#   THE ORDER IS HIS, confirmed 1101: it runs BEFORE the lineage tests - before the rider pickup,
#   before the candidate scan and before HOLD. That ordering is the whole mech: at 04:37:55 HOLD
#   takes the bar today, so a test placed after it could never fire.
#   HIS TRUTH TABLE, 1101 verbatim: *"if divergence's verdict is bullish and the target-side is low,
#   router receives a rev-trade signal.  if divergence is bearish and target-side is high, router
#   receives a rev-trade signal. if neither match, the outcome is none"*.
#   THAT IS `verdict == target side`. anchor_floater's state is +1 for a divergence supporting a
#   SHORT - bearish - and -1 for one supporting a LONG - bullish; the target side is +1 high and -1
#   low. bullish + low is -1 == -1; bearish + high is +1 == +1. It is the SAME condition the arm
#   has always used, so no sign is re-derived and no second truth table exists.
#   *** THE ARM'S OWN COMMENT CONTRADICTS ITS OWN CODE. *** It reads "A SHORT is side +1 here",
#   which is wrong - a SHORT's target side is the LOW one, -1. The CONDITION beside it is right and
#   matches his 1101 table. The comment is corrected, the condition is untouched.
#   DEFAULT OFF so the arm is measured before it is banked.
LIN2_DIV_AT = os.environ.get('W_V4_LIN2_DIV_AT', 'cadence')   # WHICH BAR the divergence is
#   anchored on at a cadence: 'cadence' = the cadence bar itself, 'extremum' = the target-side
#   ws1Mage extremum at or before it.
#   HIS 1101 PROPOSAL, verbatim: *"2324 is when the cadence fires.  maybe divergence will work
#   better if it's anchored on the ws1Mage extremum - walk back to look forward and find the
#   target-side ws1Mage extremum, anchor on it and test for divergence"*.
#   IT IS THE SAME PICKER THE MAGE CASCADE USES - jig.mage_cascade_bar in 'extrema' mode, his 1029
#   ruling *"were the mage cascades anchored on a ws1Mage's extremum? if not, they should be"*. So
#   no new producer: the walk back is unbounded, the gap is MC_GAP 48 bars = 4 min - his own 1017
#   number - and the returned bar may never exceed the cadence bar, which that producer asserts.
#   WHY HE PROPOSED IT. At the 2026-09-03 23:24:00 cadence, anchored on the cadence bar, pxs rises
#   +0.000100 from the floater while ws1r rises +38.02, so both signs are positive and the read is
#   price-matched - refused. He does not read 2324 as price-matched. A +0.000100 move is 0.060% of
#   price, and the anchor is the lever he reached for rather than the PM floor.
#   NEITHER ARM IS RULED. 'cadence' is the default and the pre-1101 behaviour; the two are reported
#   side by side against his own examples, not chosen.
#   THE KNOB NAME AND BOTH ARM NAMES ARE MINE.
LIN2_DIV_PM_FLOOR = _knob('LIN2_DIV_PM_FLOOR', 0.0)   # HIS KNOB NAME. The floor PM - price
#   matching - needs before it may act. 0.0 = PM DISABLED, his 1101: *"PM matching.  it needs a
#   floor that I don't have yet - disable PM matching for lineage2"*.
#   PM IS ALREADY REFUSED by `div_verdict`, which returns None for abs(state) == 2 alongside state
#   0. So at 0.0 nothing changes and this knob is the declared home for the floor when he sets it.
#   NOTHING READS IT YET. It is declared, ruled at 0.0, and wired to no test - stated, so a later
#   reader does not assume a mech behind it.

#  -- HIS 1031 t1 CADENCE UPDATE -----------------------------------------------------------------
#   His words: *"t1 cadence update: -ws1b is replaced by gcws30b, wob 6 / -the "r reversing
#   target-side past 50" gate is replaced with "r reversing on target-side ex-{100-{knob:56}
#   fence}" / --example 09-03 1152 does not qualify because r is 50.3. 1233 does qualify because r
#   is 59"*.
#   *** HIS 1101 SPEC REVISION: t1's b LINE MUST BE EX-5/95, NOT oob 15/85. *** His words:
#   *"I can't see the gcws30b ex 5/95"* / *"I might have overlooked 5/95 fence for gcws30b in the
#   spec"* / *"I've just found it - I omitted the 5/95 requirement for gcws30b"*.
#   BEFORE THIS the t1 b read was oob 15/85 on whatever line LIN2_T1_B_LINE named - K.OOB_HI/LO
#   both in the beyond-state and in the oob->ib cross. The 5/95 pair replaces that pair for the
#   line t1 reads; on the high side beyond 95 already implies beyond 85, so this is a narrowing,
#   and the CROSS back to in-bounds is now a cross back inside 95.
#   THE KNOB IS ONE HOME FOR THE FENCE and it applies to whichever line t1 reads - a structural
#   call of MINE, stated: a fence keyed to a line name would need a second copy of the mapping the
#   b-line knob already owns. AT THE ws1b ARM of LIN2_T1_B_LINE this wants 85.0, not 95.0.
#   HIS 1101 ADDITION: a 1 MINUTE MINIMUM DWELL ON gcws30b's IB STATE. His words: *"add a 1 minute
#   minimum dwell on gcws30b ib"*. The cadence may not fire until the b line's in-bounds state has
#   held this many bars, counting the cross bar itself. It is ADDITIVE to LIN2_T1_B_WOB 6 - he said
#   "add" - so the fire bar is max(the cross's confirm bar, the cross + dwell - 1, the reversal
#   stamp), and at 12 the dwell is what binds.
#   *** THE SIDE OF THE FENCE IS HIS WORD "ib" READ LITERALLY, AND THERE IS A SECOND READING. ***
#   The 05:19:25 cadence he questioned fired off a BEYOND-the-fence run of exactly 6 bars = 30 s
#   (gcws30b at 2.66, 05:18:30..05:18:55). A 1-minute minimum on the BEYOND side would delete that
#   cadence; this ib dwell only moves it 30 s later, to 05:19:55. Both are measured for him rather
#   than chosen here - LIN2_B1_OOB_DWELL is where the beyond-side version would go.
LIN2_T1_B_IB_DWELL = _knob('LIN2_T1_B_IB_DWELL', 12, int)   # bars = 60 s at 12.
LIN2_T1_B_FNC = _knob('LIN2_T1_B_FNC', 95.0)   # the t1 b line's fence, 95 -> (5.0, 95.0).
LIN2_T1_B_LINE = os.environ.get('W_V4_LIN2_T1_B_LINE', 'gcws30b')   # the b line t1 reads. 'ws1b'
#   is the pre-1031 arm. THE KNOB NAME IS MINE; the line is his. Both are kept so one run can hold
#   t1 on the new line and the arm on the old.
LIN2_T1_B_WOB = _knob('LIN2_T1_B_WOB', 6, int)   # HIS VALUE. The oob->ib cross hold for t1's b
#   line, in bars at the 5 s grid, so 6 = 30 s. It REPLACES LIN2_CROSS_WOB 12 for this cross and
#   this cross only; every other cross to ib in the tree keeps 12. The t1 fire bar is c + wob - 1,
#   his 1031 ruling that the wob has earnt its place.
LIN2_T1_R_FNC = _knob('LIN2_T1_R_FNC', 56.0)   # HIS VALUE and his own {knob:56} notation. The r
#   reversal gate's fence, mirrored: (100 - 56, 56) = (44.0, 56.0). A LOW target needs the r value
#   at or below 44.0, a HIGH target at or above 56.0.
#   IT REPLACES the "same side of 50" test, which was `K.side_of`. His worked examples, 2026-09-03:
#   r 50.3 at 11:52 sits between the pair and does NOT qualify; r 59 at 12:33 clears 56.0 on the
#   high side and DOES.
#   THE r LINE IS UNCHANGED - ws1r, his 1031 ruling.
#   THE VALUE IS READ AT THE REVERSAL'S STAMP, which is what the pre-1031 gate did. MINE, by
#   precedent, not his.
LIN2_T1_GRACE_AT = os.environ.get('W_V4_LIN2_T1_GRACE_AT', 'cross')   # WHERE t1's 120 s grace
#   window starts: 'cross' = the b line's ib cross bar c, 'confirm' = its hold bar c + wob - 1.
#   HIS 1031 ANSWER when asked: *"I'm not sure about this.  my spec build notes didn't allow for
#   it.  give it an on off knob and show the diff"*. 'cross' is the pre-1031 behaviour and the
#   default; the diff between the two arms is reported, not chosen.
#   THE KNOB NAME AND BOTH ARM NAMES ARE MINE.

#  -- HIS 1031 ARM UPDATE, arm_race condition 2 ---------------------------------------------------
#   His words: *"arm update: -replace ws1b, with gcws30b oob / --gcws30b must be outside of a 95/5
#   fence / --add ws2r oob ??and ws3r oob, to the existing ws1r oob?? / -gcws30b uses a wob 6 for
#   both to-oob and to-ib crosses, and for the dwell in ex-95/5-fence"*, corrected by him on 1031:
#   *"gcws30b ex=5/95-fence replaces ws1b oob"*.
#   WHICH MECH: arm_race condition 2, the only one of the three that reads ws1b. Settled by his own
#   *"I'm sure we need ws2r oob in the race conditon"* and by *"the timestamps are arm timestamps
#   and this is why your opens don't match"*. It does not touch the open or chain_open.
LIN2_ARM_B_LINE = os.environ.get('W_V4_LIN2_ARM_B_LINE', 'gcws30b')   # the b line race condition 2
#   reads. 'ws1b' is the pre-1031 arm. THE KNOB NAME IS MINE.
LIN2_ARM_B_FNC = _knob('LIN2_ARM_B_FNC', 95.0)   # HIS VALUE. The arm b line's own fence, mirrored
#   to (5.0, 95.0). "AT OR BEYOND" is his 1031 word: at or above 95.0, or at or below 5.0.
#   IT IS A THIRD FENCE PAIR, not oob 15/85 and not the r fence - his 1031 *"yes, different
#   fences"*.
LIN2_ARM_B_WOB = _knob('LIN2_ARM_B_WOB', 6, int)   # HIS VALUE, bars at the 5 s grid = 30 s. Three
#   uses, all his: the to-oob cross, the to-ib cross, and the dwell beyond the 5/95 fence.
LIN2_ARM_WS3R_ON = _knob('LIN2_ARM_WS3R_ON', 0, int)   # whether ws3r oob joins the arm's r
#   group. OFF, because he bracketed it in question marks and then said *"I'm sure we need ws2r oob
#   in the race conditon, I'm not convinced we need ws3r"*. THE KNOB NAME IS MINE.
#   THE r GROUP IS AN OR, his 1031 revision: *"(ws1r or ws2r) + gcws30b"*. His first wording -
#   "add ws2r oob to the existing ws1r oob" - read as a conjunction and was built that way; it
#   fired on 40 bars of 2026-09-03 on the low side and 49 on the high side. The OR replaces it,
#   and ws3r joins the same group rather than being a fourth conjunct.

#   *** HIS 1101 BLANKET RULE: NO EXHAUST WHILE ANY RUNG ON THE BOARD IS oob. *** His words:
#   *"0554 can't exhaust - ws3r is oob so it must walk to the next cadence"*, then, asked whether
#   it was the rider or the band: *"the oob rule doesn't apply to a rider - it's a blanket rule
#   across the board"*.
#   THE BOARD IS THE FULL RANGE, ws1..L2_MOM_MAXTF, his standing meaning of the word - not the
#   candidate band and not the rungs above the rider. ws3 at the 2026-09-03 05:54:25 exhaust sits
#   BELOW the rider ws5 and could never be a candidate, and his rule still covers it.
#   THE READ IS `Board.oob`, routed by LIN2_CP_OOB, so it is the same oob the rest of the walk uses.
#   THE KNOB NAME IS MINE; the rule and its scope are his.
#   *** HIS 1101 THIRD ARM: THE LIN-HOP REACH TEST. *** *"let's try this: if a line that is inside
#   of lin-hop's reach is ex-fence, then walk to the next cadence"*. The reach is the rider's own
#   hop band, rider + 1 .. rider + L2_LIN_HOP, which is 2 - so two rungs above the rider.
#
#   ALL FOUR ARMS LIVE IN ONE KNOB so they can be A/B'd without stacking:
#     'off'                 no board test - the pre-1101 walk
#     'board_oob'           any ws1..L2_MOM_MAXTF oob blocks. His first wording
#     'board_oob_rev'       oob AND not reversed since the previous cadence. His correction
#     'linhop_exfnc'        any rung in rider + 1 .. rider + L2_LIN_HOP ex-fence blocks. This one
#   THE ARM NAMES ARE MINE. The four rules are his, each in his own words above.
LIN2_BOARD_HOLD = os.environ.get('W_V4_LIN2_BOARD_HOLD', 'linhop_exfnc')
#   BANKED at his new arm on *"let's try this"*. The other three are one env var away.
LIN2_BOARD_OOB_HOLD = _knob('LIN2_BOARD_OOB_HOLD', 1, int)   # SUPERSEDED by LIN2_BOARD_HOLD above.
#   Kept at 1 so an old caller reading it is unchanged; the walk reads LIN2_BOARD_HOLD now.
LIN2_TOP_RESET_ON = _knob('LIN2_TOP_RESET_ON', 1, int)   # THE LADDER-TOP RIDER RESET, on/off.
#   HIS MECH, 1031, verbatim: *"I have an new trick that I haven't shared yet: when ws30 exhausts,
#   set the rider to zero and test for baton pass candidates (same logic, max jump = 8 TFs)"*.
#   WHERE IT SITS: in front of the t4/exhaust row, which is the branch a cadence reaches when the
#   rider is not oob, is no-longer-ex-fence or has reversed, and the candidate scan came back
#   empty. On the 2026-08-14 0659 walk that is the row at 2026-08-14 10:41:20, rider ws30 26.81.
#   THE TRIGGER IS THE LADDER TOP, rider >= L2_MOM_MAXTF. His "ws30" IS the ceiling on that walk
#   and there is nowhere above it for a baton to go. STRUCTURAL and mine - he named a rung, not a
#   condition, and at a different ceiling his rung would be a different number.
#   THE RESET SCAN is `candidates` from rider 0 with the cap at 0 + LIN2_RIDER_JUMP, which is his
#   "same logic, max jump = 8 TFs". It reads at_cadence, so his 1031 re-latch speaks here too.
#   NO LIMIT ON REPEATS, HIS RULING. Asked on 1031 whether a rider that climbs back to the top and
#   exhausts again may reset again, his answer was *"yes"*. So the absence of a limit is his, not a
#   default of mine: a leg may reset without end.
#   THE KNOB NAME IS MINE and the mech is unnamed - he called it "a new trick".
#   DEFAULT OFF so the arm is measured before it is banked.
LIN2_RIDER_JUMP = _knob('LIN2_RIDER_JUMP', 8, int)   # BARS NO - TIMEFRAMES. The most the rider may
#   advance at one cadence marker. 0 = no bound, which is what the code did before 1031.
#   HIS MECH AND HIS VALUE, 1031: *"let's add a rule to lineage: at a cadence marker, the rider TF
#   can only jump by {knob:8} TFs"* / *"arm starts with rider=0. at the 0701 t1, the rider is ws8"*
#   / *"ws8.  it's a knob, so either way we can tune if needed"*.
#   THE ARM ASSIGNS NO RIDER under this rule - his *"arm starts with rider=0"* - so the first
#   cadence scans with the bound 0 + LIN2_RIDER_JUMP.
#   IT READS THE LATCH, NOT THE VALUE. With LIN2_RELATCH_ON 1 the re-latch puts ws5, ws7 and ws8
#   back in the latched set at 2026-08-14 07:02:10, so the highest LATCHED rung at or below ws8 is
#   ws8 - his own answer - and the scan keeps querying the latch as his 1029 spec requires. Without
#   the re-latch no rung at or below ws8 was latched there and the bound returned nothing.
#   THE KNOB NAME IS MINE. He has not named it.
LIN2_CAD_TYPES = os.environ.get('W_V4_LIN2_CAD_TYPES', 't1')   # WHICH CADENCE TYPES THE WALK
#   MAY DECIDE AT. 'all' applies no filter and is the bank. Otherwise a comma list of type names:
#   't1', 't2', 'ws1b counter-oob', 'barrage', 'retest', 't3', 'latch'.
#   HIS 1031 ASK: *"test only at the t1 cadences"* -> 't1'.
#   IT FILTERS THE REVIEW LIST, IT DOES NOT TURN A MECH OFF. Each cadence mech keeps its own ON
#   knob - LIN2_BARRAGE_ON, LIN2_COUNTER_OOB_ON, L2_T3_ON, LIN2_CAD_LATCH_ON, L2_ARM_RETEST - and
#   that knob still owns whether the mech RUNS. This one owns which of the cadences it produced
#   the walk reviews. Two homes for one fact would drift; t2 has no ON knob at all, which is why
#   a per-mech switch could not serve this ask.
#   THE RETEST GATE IS NOT FILTERED AWAY BY THIS. It still holds the walk's start and re-scans the
#   rider; only its own cadence bar stops being a decision bar. A gate is not a test.
#   THE KNOB NAME AND THE TYPE STRINGS ARE MINE. The type strings are the ones the walk already
#   emits in its `ctype` column, so a report and this filter cannot disagree.
LIN2_PASS = os.environ.get('W_V4_LIN2_PASS', 'ib')   # HOW LINEAGE2'S BATON LEAVES THE RIDER:
#   'ib' | 'reversal' | 'reversal+quarter'. THE KNOB NAME AND THE MODE STRINGS ARE MINE; the three
#   mechs are his, 1031: *"using the current "pass on ib" ... make a second table that swaps "ib"
#   with "reversal" / make a third table that swaps "ib" with "reverasal + 1/4 width of the TF"
#   --eg a ws22 rider has reversed ex fence at 0756, the baton pass happens at (0756 + (0.25 * 22
#   minutes)"*.
#   'ib' IS THE BANK and is _pass_bars' two rules unchanged: the oob -> ib cross, and the ex-fence
#   -> in-fence edge which under the latch IS the latch's release.
#   'reversal' AND 'reversal+quarter' REPLACE BOTH RULES, not just the first. "swaps ib with
#   reversal" is read literally: the pass bar becomes the rider's own reversal. THE LATCH IS STILL
#   LIVE under them - it gates every candidate through `baton_ex_fence` - it just no longer
#   produces a pass bar of its own. If he meant rule 2 kept, that is a fourth mode.
#   THE WOB IS LIN2_REV_WOB 12, not LIFT_WOB 8: every other reversal read in v4_lineage2.py uses
#   LIN2_REV_WOB, and a second wob in the same file would be two answers to one question.
LIN2_PASS_QUARTER = _knob('LIN2_PASS_QUARTER', 0.25)   # the fraction of the rider's own TF width
#   the third mode waits after its reversal. THE 0.25 IS HIS, from the worked example above; the
#   knob name is mine. int(0.25 x TF x 12) bars: ws22 -> 66 bars = 330 s, which takes 07:56:00 to
#   08:01:30 exactly as he wrote it.
LIN2_REV_WOB = _knob('LIN2_REV_WOB', 12, int)       # *"1 static wob12. noted, we'll keep the
#   static"*. Bars the lift-off state must hold, for THIS mech only - LIFT_WOB 8 is untouched and
#   every other mech keeps it. Measured 1026: at 12 the ws7r 2026-10-26 22:00:15 reversal drops and
#   21:53:20 and 22:03:05 survive; across ws5/7/9/12r over 08-30..09-03 a seam-aligned dynamic wob
#   kept ~25% fewer reversals and was slower on every one, median 75-80 s against the static 55 s.

# -- the BARRAGE mech, Joe 1027. BANKED, and wiring it into the chain is the open task ------------
#   HIS QUESTION, then his agreement:
#     *"if there was a tolerance that allowed for low-side ws1r reversing to pseudo fit 'inside the
#      ws1Mage oob to ib' at 02:29, would it have detected a barrage of low-side reversals and
#      declared exhaust?"*
#     *"so the tolerance alone will not select 02:29. It needs a second condition - the barrage
#      itself is the obvious candidate"* / *"agreed"* / *"bank the barrage results"*
#   THE THREE CONDITIONS: ws1Mage crosses oob -> ib on a side; ws1r reverses on the SAME side
#   within LIN2_BARRAGE_TOL_S of that cross; at least LIN2_BARRAGE_LINES r lines reverse on that
#   side between the cross and the ws1r reversal.
LIN2_BARRAGE_TOL_S = _knob('LIN2_BARRAGE_TOL_S', 70, int)   # MEASURED off his 02:29 instance - the
#   gap from the 2026-08-30 02:27:50 ws1Mage cross to the 02:29:00 ws1r reversal. Not a chosen value
#   and not swept. Of 204 LOW-side ws1Mage ib-crosses on 08-30, 94 have a ws1r reversal inside 120 s
#   and the median gap is 140 s, so the tolerance ALONE selects nothing - that is why the barrage
#   condition exists.
LIN2_BARRAGE_LINES = _knob('LIN2_BARRAGE_LINES', 6, int)    # MEASURED off the same instance - the
#   6 lines reversing LOW inside those 70 s were ws3, ws4, ws8, ws6, ws7, ws1. Also not swept.
#   WITH BOTH: 204 LOW-side crosses on 08-30 reduce to 8 instances, in 3 clusters.
LIN2_BARRAGE_MIN_TF = _knob('LIN2_BARRAGE_MIN_TF', 9, int)  # 0 = OFF. THE MINIMUM TF ALLOWED TO
#   CONTRIBUTE to the barrage count - a floor applied BEFORE LIN2_BARRAGE_LINES is tested.
#   HIS DEFINITION, 1027, correcting mine: *"my minTF isn't your minTF (my error). I meant 'the
#   minimum TF allowed to contribute'. example: 'ws1,ws2,ws3,ws4,ws5,ws7,ws9,ws12' would be
#   restricted to 'ws5,ws7,ws9,ws12' if minTF =5"*.
#   WHAT I BUILT FIRST was a MEMBERSHIP test - at least one line at or above min_tf, with the count
#   still taken over every TF. He spotted it himself: *"wouldn't minTF 12 break the minimum
#   required lines? at minTF 12, there is only one line"*. Under his definition it would, and that
#   is the point of the floor.
#   *** THE VALUE 9 IS NOW UNRULED, AND AT 9 THIS MECH FIRES NOTHING. *** His 9 was ruled against
#   the membership reading - a different mechanic - so it is not his ruling on this one. Under the
#   floor reading the contributing pool at 9 is ws9..ws12, four lines, and LIN2_BARRAGE_LINES 6
#   cannot be met by four lines: the barrage produces ZERO cadences. The pair (min_tf, lines) has
#   to be ruled together and neither half is mine. out/l2_barrage_sweep.md is the grid he rules on.
LIN2_BARRAGE_MAX_TF = _knob('LIN2_BARRAGE_MAX_TF', 15, int)  # THE BARRAGE'S OWN CEILING, in TF.
#   HIS VALUE AND HIS MECH, 1029: *"barrage maxTF needs to increase, knob:15. with this in place,
#   the sweep of barrage's minTF (and maxTF, range:[12-22]) will be able to test (compared against
#   the last sweep)"*.
#   IT IS BARRAGE-ONLY, AND THAT IS MY CALL, stated: his words were "barrage maxTF", and
#   L2_MOM_MAXTF 12 is a ceiling in six other places (the rider scan, the baton candidates, the
#   latch range, t3's HTF set, v4_reentry) plus a FLOOR in test#1/test#2. Moving the shared one
#   would move all of them, so the barrage gets its own and L2_MOM_MAXTF stays 12.
#   LINES ws1..ws30 ARE ON DISK for both the emerging and the closed read, so his [12-22] range is
#   buildable. SIX OF THE ELEVEN VALUES have a short final midnight bucket and so their
#   pseudo-closed read is NOT bit-exact to the product's closed read at a grid close: ws13 (1440/13
#   = 110.77), ws14 (102.86), ws17 (84.71), ws19 (75.79), ws21 (68.57), ws22 (65.45). Exact:
#   ws12, ws15, ws16, ws18, ws20. ws15 and ws16 were measured at max diff 0.000000.
#   IT INTERACTS WITH LIN2_BARRAGE_FIT 'cap', which raises the ceiling dynamically. This knob is
#   the BASE ceiling and 'cap' may still raise it; with FIT 'off', banked, nothing raises it.
LIN2_BARRAGE_MIN_TF_MODE = os.environ.get('W_V4_LIN2_BARRAGE_MIN_TF_MODE', 'membership')
#   HOW LIN2_BARRAGE_MIN_TF IS APPLIED. Joe 1028 chose this arm - *"B"* - to run the legs on *"the
#   settings that built the pine-emit"*.
#     'membership'  at least ONE contributing line is at or above MIN_TF, and the COUNT is taken
#                   over ws1..L2_MOM_MAXTF. This is what out/l2_barrage.pine and the banked
#                   out/l2_barrage_0830_0906.md were built on: 24 cadences over 08-30..09-06.
#     'floor'       only lines at or above MIN_TF may contribute at all - HIS OWN definition,
#                   1028: *"I meant 'the minimum TF allowed to contribute'"*.
#   *** THE FLOOR ARM IS EMPTY AT THE CURRENT PAIR. *** MIN_TF 9 leaves ws9..ws12, four lines, and
#   LIN2_BARRAGE_LINES 6 cannot be met by four, so the mech fires NOTHING. The (MIN_TF, LINES) pair
#   has to be ruled together for that arm; until then 'membership' is the default so the mech does
#   not ship empty. THE ARM NAMES ARE MINE; the two readings are both his.
LIN2_B1_HOLD = _knob('LIN2_B1_HOLD', 0, int)   # bars ws1b's crossing back inside must hold
#   before the two cadences count it as inside. 0 = the instantaneous read, which is what they do
#   today.
#   HIS MECH, 1029: *"could the ws1b test incorporate the wob 12? ie if ws1b to ib has not
#   qualified its wob 12, then its value is not passed in"*, and the reason: *"what I'm trying to
#   capture is the ws1b low oob excursion that runs from 0100 to 0121"*.
#   MEASURED on 2026-08-30, the live read: ws1b's low-side excursion runs 00:59:25 to 01:20:45 and
#   contains FOUR crossings back inside, of 9, 4, 2 and 9 bars. The instantaneous read breaks the
#   excursion at the first of them. At 12 bars none of the four qualifies and the real exit at
#   01:20:50 holds 550 bars, so the excursion reads as one event confirmed 01:21:45 - his 0121.
#   THE KNOB NAME IS MINE. The value 12 is his, and it is the same count as the crossing hold the
#   two cadences already apply to ws1r.
#   DEFAULT 0 so the arm is measured before it is banked.
#   *** BANKED OFF 1101. *** His words: *"disable the latch.  I introduced it get around
#   emerging"*. The chart-matched ex-fence read above is what it was standing in for, so the
#   latch comes out rather than running beside it. 1 is the pre-1101 arm.
LIN2_LATCH_EXFNC_ON = _knob('LIN2_LATCH_EXFNC_ON', 0, int)   # the PER-LINE EX-FENCE LATCH, on/off.
#   HIS MECH AND HIS KNOB NAME, 1029, verbatim:
#       I have a third option to add to pseudo-close and 180 wob: use a per-line latch
#       -the mech would latch on when the r line crosses into exfence, with a small
#        {knob:4,'LIN2_EXFNC_LATCH_WOB'} WOB
#       -the latch releases on lift-off's signal
#       -the baton-passing consumers will no longer test a line's value to decide ex-fence (and
#        oob). they will query the latch state
#       -any non-baton-passing mechs can still use line values for decisions
#   and 1029: *"ADD LIN2_LATCH_EXFNC_ON / no need for a latch life on this new mech / the mech I
#   propose is purely for baton-passing"*.
#   *** THE RELEASE LINE WAS REVISED BY HIM ON 1031. *** It read *"-the latch releases on
#   barrage's signal"* from 1029 until then, and his words replacing it: *"I see what you're
#   saying.  I was premature to use barrage - it wasn't fully tested and clearly isn't helping us
#   on our 08-14 0659 walk / replace "-the latch releases on barrage's signal" with "-the latch
#   releases on lift-off's signal""*.
#   WHAT IT MOVED: LIN2_EXFNC_LATCH_REL's default and its ruling, 'bank' -> 'lift', and the arm
#   formerly called 'bank' is renamed 'barrage' because it is no longer the bank. EVERY LATCH
#   FIGURE MEASURED BEFORE 1031 WAS TAKEN ON THE BARRAGE ARM and is off-spec from here.
#   WHAT IT DID NOT MOVE: the opposite-side ex-fence clear. It was never in his spec and no
#   verbatim note of his exists for it anywhere in the tree - it is MINE and unruled. It lives in
#   the 'barrage' arm only, so the spec'd arm does not read it.
#   BANKED ON, 1029: *"bank this as the machine"*, after the three reads were measured on
#   2026-08-30 with one open at 23:53:55 SHORT. It was proposed as a third option against
#   pseudo-closed and the live read, and it is the one he banked.
#   NO LIFE KNOB, on his instruction. The only release is the barrage's signal, so a line that
#   latches and never meets a barrage stays latched to the window's end. No cap is applied.
LIN2_LATCH_OOB_ON = _knob('LIN2_LATCH_OOB_ON', 0, int)   # whether the baton path's oob reads go
#   through the latch as well as its ex-fence reads. 0 = the line value, which is banked.
#   Joe 1029: *"earlier in the transcript, you had a specific oob latch that produced higher net on
#   that day. I dropped it, but now feels like a good time to check it - so that we're sure about
#   the mech and the code, do a 08-30 chain AB test to validate or drop the oob latch"*.
#   IT IS ONE LATCH READ AT DEPTH, not a second latch. My first build was two independent latches,
#   one on the RMOM_FNC pair and one on 15/85, each cleared only by its own fence's opposite-side
#   crossing - and they drifted into "oob but not ex-fence" for 27,460 bars on 2026-08-30 across
#   all 24 line-sides. His reading rules that state out: *"I see ex-fence as a literal term:
#   'external of the fence', ie oob is definitely ex-fence"*, and the code agrees - 0 values across
#   0.00 to 100.00 are oob without also being ex-fence. So the depth read is a FILTER on the one
#   latch: latched, AND 15/85 confirmed at or after that latch's own on-bar. It cannot drift.
LIN2_EXFNC_LATCH_WOB = _knob('LIN2_EXFNC_LATCH_WOB', 4, int)   # HIS NAME AND HIS VALUE - *"a small
#   {knob:4,'LIN2_EXFNC_LATCH_WOB'} WOB"*. BARS, at the 5 s grid, so 4 = 20 s. Bars is MY reading
#   and it follows every other wob in the tree: LIFT_WOB 8, LIN2_REV_WOB 12, LIN2_CROSS_WOB 12.
#   The latch turns on at the CONFIRM bar, cross + wob - 1, and only if the line held beyond the
#   fence for every bar of that window - the same shape _pass_bars uses for its off-edge.
LIN2_EXFNC_LATCH_REL = os.environ.get('W_V4_LIN2_EXFNC_LATCH_REL', 'lift')   # WHAT RELEASES
#   THE PER-LINE EX-FENCE LATCH. THE KNOB'S NAME IS MINE; the mech in the 'lift' arm is his, 1030:
#   *"why wouldn't we make the ex-fence latch all inclusive? ie line value crosses past 75/25 (or
#   80/20) and is latched until a lif-off fires, instead of the latch releasing on the cross to
#   oob (current behaviour)"*.
#     'lift'  the latched line's own lift-off, and NOTHING else. THE SPEC'D ARM AND THE DEFAULT
#             since his 1031 revision of the release line.
#     'barrage'  a barrage on that side, OR an opposite-side ex-fence cross confirmed over
#             LIN2_EXFNC_LATCH_WOB. His 1029 release before he revised it, plus the opposite-side
#             clear that is mine and unruled. RENAMED FROM 'bank' on 1031: it is not the bank any
#             more, and a value that says it is would be wrong in every report header.
#             Every latch figure measured before 1031 was taken on this arm.
#   HIS PREMISE WAS CORRECTED BEFORE THIS WAS BUILT: the banked arm does not release on a cross to
#   oob. oob is read THROUGH the latch by the baton path; it never releases it.
#   THREE THINGS INSIDE 'lift' ARE MINE AND UNRULED - he said "a lift-off" and named no more:
#     1  it is the LATCHED LINE's own lift-off, not ws1r's
#     2  it is read on the SAME side as the latch, so a HIGH latch clears when the line leaves its
#        HIGH extreme
#     3  the stamp is lift + LIFT_WOB - 1 = lift + 7 bars = 35 s, his standing rule that the
#        producer returns the raw bar and the consumer adds the wob. LIN2_REV_WOB 12 is the other
#        candidate and lineage2 already uses it for reversals at v4_lineage2.py:291.
#   MEASURED BEFORE IT WAS WIRED, in 1030_mom_fence/latch_release_ab.md: over ws1..ws20 at 75/25
#   'bank' holds 46.55% of all line-side bars and 'lift' holds 13.89%, which is within reach of
#   the 16.5% the plain line value reads. 'lift' is the RESTRICTIVE arm, not the inclusive one.
#   THE SAMPLING RESTARTS AT THE LATCH, his 1030 ruling after he was shown lift-off's lattice:
#   *"lift-off per-line sampling is set to zero (samples collected) when the ex-fence latch is
#   latched"*. A lift-off only releases an episode once all LIFT_PTS 6 samples sit at or after
#   that episode's latch-on bar - 5 x gap_for(tf) bars, which is 15 bars = 75 s on ws1r and 280
#   bars = 1400 s on ws20r. It is built in the 'lift' branch of v4_l2_proxy._latch.
#   *** THE SCOPE IS UNRULED. *** He said it of the latch's own release. Lift-off is also the
#   barrage's reversal detector through v4_fast.revs, and v4core, the backstop and v4saviour all
#   read it. Whether their sampling restarts at the latch too is HIS, and nothing outside the
#   latch is touched.
LIN2_B1_OOB_DWELL = _knob('LIN2_B1_OOB_DWELL', 0, int)   # BARS cws1b must hold past the oob
#   fence before its oob state counts. Joe 1030, after being shown that cws1b entered the LOW oob
#   four separate times in 85 s on 2026-08-30 22:22 and the counter-oob cadence fired on each:
#   *"add a minimum oob dwell of 12 bars for cws1b"*. "dwell" is HIS word - LIN_IB_DWELL already
#   carries it. HIS VALUE IS 12 = 60 s at the 5 s grid.
#     0 or 1  the plain per-bar read. THE BANK, so nothing measured so far moves.
#     D       the state turns on at the entry bar + D - 1, and only if cws1b held past the fence
#             on every bar of that window. A run shorter than D never counts as oob at all.
#   IT IS THE MIRROR OF LIN2_B1_HOLD, not a replacement: the hold is on the crossing back INSIDE,
#   this is on the entry. Both live in v4_l2_cadence.b1_beyond, which is cws1b's one oob state.
#   WHO READS IT, all four through b1_beyond: the t1 cadence, the t2 cadence, the arm's
#   cws1b+cws1r test, and the cws1b counter-target-side oob cadence.
#   *** TWO CONSEQUENCES, STATED NOT HIDDEN. ***
#     1  t2's test is cws1b NOT oob. A dwell makes fewer bars count as oob, so t2 fires MORE often,
#        not less. That direction is the opposite of the other three and it is HIS to accept.
#     2  the chain open reads ws1b through jig.oob_ib_cross with its own LIN2_CHAIN_OPEN_XWOB 1,
#        a Jig producer with its own contract. It is NOT routed through this dwell. HIS to rule.
# ── THE CASCADE'S REVERSAL GATE - HIS MECH, 1030. HE HAS NOT NAMED IT ───────────────────────
#   His words: *"of the 57, how many reversal decisions would be gated if there wasn't an immediate
#   exhaust at the cadence event? ie, if ws1-4r show no baton candidates at the cadence event
#   (exhaust) then the cascade's (up/down) reversal signal is honored"*, and on the reading back:
#   *"agreed - that's my design"* and *"go for it"*.
#
#   WHAT IT DOES. At a cadence where the mage cascade's verdict OPPOSES the open trade, the walk
#   currently exhausts and rev-trades at once. With this ON it first scans ws1r..ws4r for a
#   baton-pass candidate. A candidate there means a fast line is still past the fence AND still
#   travelling toward the target side, so the trade still has a lead running and the cascade's
#   reversal is NOT honoured. With no candidate, the reversal stands.
#
#   IT IS NOT THE BATON. `candidates` normally scans UPWARD from the rider's rung, so with a rider
#   at ws17 the rungs ws1..ws4 are ones the baton would never look at. This reuses the candidate
#   test's two conditions - past the fence, and `towards` - on a range the baton has no claim on.
#   HIS WORD on that reading: *"agreed - that's my design"*.
#
#   WHY IT MATTERS THIS MUCH. Measured over 2026-08-30..09-06 with the stop OFF: the cascade owns
#   123 of 143 leg exits - 86.0% - and it is the only owner with a negative total, -17.8102. Of
#   the 122 reversals with a next leg to judge, 57 opened a leg that ended negative - 46.7%.
#
#   IT GATES THE REVERSAL ONLY, not the cascade's other branch. A verdict that MATCHES the trade
#   takes no action and keeps walking; that is not a reversal signal and is untouched.
LIN2_CASC_REV_GATE_ON = _knob('LIN2_CASC_REV_GATE_ON', 0, int)   # on/off. THE KNOB NAME IS MINE -
#   he has not named this mech. 0 is the bank, so nothing measured before it moves.
LIN2_CASC_REV_GATE_HI = _knob('LIN2_CASC_REV_GATE_HI', 4, int)   # the scan's top rung. HIS VALUE,
#   from *"ws1-4r"*; the knob name is mine. The floor is ws1.
#   *** WHAT A GATED CADENCE DOES NEXT IS MINE AND UNRULED. *** It falls through to the board
#   review, so the baton, the HOLD branch and the t4/exhaust test all still get their turn at that
#   bar. The alternative - take no action and keep walking, as the cascade's MATCHES branch does -
#   is the other reading of his words and is NOT what is built.

# ── LIN2_MATRY_WSF_TAKEOVER - HIS MECH AND HIS NAME, 1030 ────────────────────────────────────
#   His spec verbatim, and the context he gave with it: *"smaller/faster lines form the lead for
#   higher/slower lines (matryoshka)"*, after *"do you remember the days when we looped on ws10, so
#   that we didn't get caught in higher TF (like ws17r) that takes to long to produce an actioable
#   signal? we're seeing the same thing now, but now we have the benefit of using cadences"*.
#
#       --if a rider is >=ws{knob:7, 'LIN2_MATRY_WSF_TAKEOVER_TF'}
#       ---if a t1 or t2 cadence fires
#       ----if a scan from ws1 to ws4 finds two consecutive TFs printing infence, or between
#            exfence and oob
#       -----print exhaustion and sent rev-trade to the router
#
#   WHAT HE SETTLED WHEN I PUT THE GAPS TO HIM, 1030, one line each:
#     the two states      read on the TARGET side only, so together they are every value UNDER
#                         the target oob fence - 85.0 at OOB_FNC 15. His correction: *"your logic
#                         is mixing high side and low side ... your numbers for this are 75 and 85
#                         (high-side/LONG)"*. There is no unnamed value between them.
#     "two consecutive"   adjacent TF numbers - *"2 - yes"*
#     the lines           LIVE, never closed - *"CLOSED LINES ARE NOT WELCOME IN OUR STRATEGY"*
#     value or latch      the VALUE. A latch is one yes/no and cannot separate "between exfence
#                         and oob" from "oob". He accepted that read: *"understood"*
#     the baton           it fires even when baton-pass candidates exist - *"because matryoshka is
#                         leading"*
#     the cadences        t1, t2, and the retest gate's own cadence - *"7 - noted"* to adding it
LIN2_MATRY_WSF_TAKEOVER_ON = _knob('LIN2_MATRY_WSF_TAKEOVER_ON', 0, int)   # on/off. THE NAME'S
#   _ON SUFFIX IS MINE; he named the mech. 0 is the bank so nothing measured so far moves.
LIN2_MATRY_WSF_TAKEOVER_TF = _knob('LIN2_MATRY_WSF_TAKEOVER_TF', 7, int)   # HIS KNOB NAME AND HIS
#   VALUE, written into his spec line as {knob:7}. The rider's TF must be AT OR OVER this for the
#   mech to look at all.
LIN2_MATRY_WSF_TAKEOVER_AT = os.environ.get('W_V4_LIN2_MATRY_WSF_TAKEOVER_AT', 'event')  # WHICH
#   BAR THE ws1..ws4 SCAN READS. THE KNOB NAME IS MINE; the two arms are his, 1030: *"I'm not sure
#   if this is event anchored or ws1mage extremum anchored. test both"*.
#     'event'     the cadence bar itself
#     'extremum'  the ws1Mage extremum at or before the cadence bar, picked by
#                 jig.mage_cascade_bar(mode='extrema', gap=MC_GAP 48) - the same picker the mage
#                 cascade uses since his 1029 *"were the mage cascades anchored on a ws1Mage's
#                 extremum? if not, they should be"*. Not a second copy of that logic.
#   NEITHER IS RULED. Both are measured and the numbers go to him.
LIN2_MATRY_WSF_SCAN_HI = _knob('LIN2_MATRY_WSF_SCAN_HI', 4, int)   # the scan's top rung. HIS
#   VALUE, from *"a scan from ws1 to ws4"*; the knob NAME is mine. The floor is ws1, also his.
#   *** THE ORDER IS MINE AND UNRULED. *** The mech sits AFTER the mage-cascade no-action test, so
#   a cadence whose cascade verdict matches the trade direction keeps walking and never reaches it.
#   He ruled the mech against the BATON, not against the cascade.
LIN2_CHAIN_OPEN_ON = _knob('LIN2_CHAIN_OPEN_ON', 1, int)   # the chain's FIRST open, on/off.
#   HIS MECH AND HIS RULING, 1029: *"the chain open should be on the ws5Mage oob with at least one
#   higher TF Mage printing closer to 50. that moment is 08-29 ~2345, and it's a SHORT"*, then the
#   logic corrected by him in the same breath: *"'closer to 50' was poor logic - help me simplify
#   the logic: if ws5Mage is high oob, then at least 2 higher TFs must be printing LOWER values. if
#   ws5MAge is low oob, then the higher TFs must be printing higher"*.
#   IT REPLACES A HANDED-IN FIRST SIDE. Before this the chain opened at the window's first bar on a
#   side passed in as +1 - not a mech, just a boundary and a choice. Now the open is produced.
#   DEFAULT ON, and that is MY call: *"should be"* is a ruling, so the default moves. The OFF arm
#   keeps the old handed-in open so the two are comparable in one table.
#   THE SCAN RUNS BACKWARD from the window's first bar, with NO limit: Joe 1029 *"we're always
#   going to have an incoming trade to start a window... option B is the answer"*. It is causal -
#   it finds a PAST event, and the trigger at bar k reads only bar k.
LIN2_CHAIN_OPEN_TF = _knob('LIN2_CHAIN_OPEN_TF', 5, int)   # the trigger line: ws{TF}Mage. HIS LINE.
LIN2_CHAIN_OPEN_LOOKBACK_S = _knob('LIN2_CHAIN_OPEN_LOOKBACK_S', 300, int)   # HIS VALUE - the
#   ws{TF}Mage oob gate passes if it is oob AT the firing bar or was oob inside this trailing span.
#   *"if ws5Mage is oob or has been oob in the last 5 minutes on the candidate-side"*. Seconds.
LIN2_CHAIN_OPEN_XWOB = _knob('LIN2_CHAIN_OPEN_XWOB', 1, int)   # bars the ws1b ib state must hold
#   for the cross to fire. 1 = the RAW cross bar.
#   MY CALL, AND IT IS CONTESTED BY HIS OWN EARLIER RULING. His 1027 *"add the wob12 to all
#   crosses"* points at 12; LIN2_CROSS_WOB 12 is that knob. MEASURED on his instance, all four arms
#   give the SAME anchor, the same 7-of-7 count and the same SHORT - only the open bar moves:
#     emerging raw      2026-08-29 23:53:50   +0.8 min from his "2353"
#     emerging wob 12   2026-08-29 23:54:45   +1.8 min
#     closed_prev raw   2026-08-29 23:54:00   +1.0 min
#     closed_prev w12   2026-08-29 23:54:55   +1.9 min
#   1 is banked because it is nearest his call and the ws{TF}Mage gate plus the anchor test already
#   stand in for a hold. Set W_V4_LIN2_CHAIN_OPEN_XWOB=12 to take the other arm.
LIN2_CHAIN_OPEN_LINES = _knob('LIN2_CHAIN_OPEN_LINES', 2, int)  # HIS VALUE - *"at least 2 higher
#   TFs"*. How many of ws{TF+1}..ws{L2_MOM_MAXTF} Mage must print on the far side of the trigger's
#   own value: LOWER when the trigger is HIGH oob, HIGHER when it is LOW oob.
#   THE BAND IS ws{TF+1}..ws{L2_MOM_MAXTF}, MY call: L2_MOM_MAXTF 12 is the ladder's top rung
#   everywhere else and the Mage ladder is built ws1..ws12 in every driver. His instance does not
#   discriminate - at 2026-08-29 23:50:00 closed, all 7 of ws6..ws12 qualify.
#   THE SIDE IS THE COUNTER SIDE of the trigger's oob: HIGH oob -> SHORT. His instance is a HIGH
#   oob at 87.75 which he called a SHORT. NO WOB - he named none.
LIN2_PSEUDO_MIN_TF = _knob('LIN2_PSEUDO_MIN_TF', 99, int)
#   99 = OFF, BANKED 1029: *"bank this as the machine"* names the arm with the ex-fence latch ON
#   and the pseudo-closed line OUT. 4 was his 1028 value for the arm where pseudo answers ws4 and
#   up; it is kept here as that arm's number, not as the machine's.
#   THE ORIGINAL 1028 NOTE FOLLOWS, unchanged:   # the LOWEST TF whose EX-FENCE read
#   comes from the pseudo-closed line. Joe 1028: *"we can't confine it to above ws12. we've already
#   had cases yesterday when a line that I thought should be ex-fence and the walk saw the emerging
#   spikes which early-exhausted the walk. let's confine pseudo-closed to >3"*, and on the band
#   *"I see ws1-3 as fast lines"*. So ws1..ws3 keep their current reads and ws4 upward go pseudo.
#     HIS VALUE. The knob's name is mine.
#   WHY THE EX-FENCE READ AND NOT THE REVERSALS: *"1, pseudo for exfence. the candidates for a
#   reversal mech are lift-off and pseudo - we need to see both reversal times in different columns
#   when the walk's leg report is printed"*. So the reversal mech is UNDECIDED and the walk keeps
#   lift-off; both times are reported side by side.
#   AN EX-FENCE READ NEEDS ONE SAMPLE, so it carries no cadence dependency. The 3-cadence hole in
#   the cadence-sampled turn rule does not touch it - his own point: *"most of the walk is
#   invisible until a cadence event"*.
#   THE VALUE PRINTED BESIDE A PSEUDO EX-FENCE DECISION IS THE PSEUDO VALUE. That is MY call: a row
#   reading "cws5 r 80.58, the highest ex-fence" with a closed number against a pseudo decision
#   would misreport which board the walk used.
#   IT IS NOT CACHEABLE TAPE-WIDE. pseudo-closed holds 121 TF-bar samples per 5 s bar, so a full
#   1.63M-bar tape is ~1.5 GB per line. It is computed for a run's own window plus 120 x T bars of
#   history - ~17 MB per line for a one-day chain run.
LIN2_REV_FENCE = _knob('LIN2_REV_FENCE', 40, int)   # THE REVERSAL FENCE. Joe 1028, his own words
#   and his own value: *"we require our reversals for a SHORT, (low-side target) to reverse below
#   40. for a LONG, high-side target, the reverse must be above 60 (100 - {knob:40}) fence"*, then
#   *"this feels like the right direction. lock it in"*.
#     a LOW-side reversal counts only if the line is BELOW this
#     a HIGH-side reversal counts only if the line is ABOVE 100 - this
#   IT IS A THIRD FENCE AND IT HAS NO NAME BUT ITS VALUE. oob is 15/85 (his standing rule) and
#   ex-fence is RMOM_FNC 80 mirrored to 20/80. 40/60 is neither, so nothing here calls it anything
#   but the fence at LIN2_REV_FENCE.
LIN2_REV_FENCE_AT = os.environ.get('W_V4_LIN2_REV_FENCE_AT', 'confirm')   # WHICH value clears the
#   fence. He did not specify, both were measured, and he ruled: *"at the CONFIRM ... this feels
#   like the right direction. lock it in"*.
#     'confirm'  the value at the bar the turn becomes KNOWABLE on. THE BANKED READING, and the
#                causal one - it tests the bar a decision is actually made at.
#     'turn'     the value at the sampled extreme itself, which is only known in hindsight.
#   MEASURED 08-30..09-06 on ws13r, cadence-sampled turns: at 'turn' 78 LOW / 66 HIGH clear the
#   fence of 133 / 135; at 'confirm' 56 / 57. On his six 2026-08-31 pivot legs the early-reversal
#   count goes 8 -> 5 at 'turn' and 8 -> 4 at 'confirm', and clean legs 1 of 6 -> 3 of 6.
#   *** THE SCOPE IS UNRULED. *** He said lock the fence in, not where it applies. It could gate
#   (a) only test#1's dtf reversal read, (b) every reversal lineage2 consumes - the latch, the
#   rider's own turn, the barrage count - or (c) only the cadence-sampled view it was measured on.
#   (b) would move the latch, the barrage and every rider decision, so nothing is wired until he
#   says which. The knob exists; no consumer reads it yet.
LIN2_BARRAGE_WIN_S = _knob('LIN2_BARRAGE_WIN_S', 0, int)   # THE COUNTING WINDOW, measured from
#   the ws1Mage cross bar, in seconds. Joe 1027, option A, after he asked what the tolerance was
#   actually for: *"so the tolerance is the maximum possible counting window. that's not how I
#   understood it. I thought tolerance allows for ws1mage and ws1r to sync"* / *"A. let the data
#   supply the best value for it"*.
#   WHY IT EXISTS: his own spec line put the count *"between the cross and the ws1r reversal"*, so
#   LIN2_BARRAGE_TOL_S was capping the counting window as a SIDE EFFECT of gating the ws1r sync.
#   One knob was doing two jobs and he only ever intended the first.
#     0   the window IS the ws1r reversal bar - the as-built behaviour, so nothing measured so far
#         moves. THE DEFAULT, because the value is his and the data has not supplied it yet.
#     >0  the window is cross + this, independent of when ws1r reverses
#   THE KNOB'S NAME IS MINE. THE VALUE IS UNRULED - it comes off the sweep he asked for.
LIN2_BARRAGE_FIT = os.environ.get('W_V4_LIN2_BARRAGE_FIT', 'off')   # what happens when the
#   min_tf floor leaves fewer lines than LIN2_BARRAGE_LINES requires. Joe 1027, who named both
#   mechanics and asked for both to be tested: *"there's 2 ways to handle this, and both need to be
#   tested / 1) dynamiclaly reduce the minimum required lines to fit them all inside the ws12cap /
#   2) dynamically increase the ws12 cap to include the minimum required lines"*.
#     'off'    neither. The pool stays ws{min_tf}..ws{L2_MOM_MAXTF} and a short pool fires nothing.
#              THE BANKED ARM, so no measurement taken so far moves.
#     'lines'  HIS 1 - the required count drops to the pool's size. At min_tf 9 the pool is
#              ws9..ws12 and LINES 6 becomes 4.
#     'cap'    HIS 2 - the ceiling rises to ws{min_tf + LINES - 1}. At min_tf 9 with LINES 6 the
#              ceiling becomes ws14, so dtf lines (>ws12, his 1017 band name) contribute. That is
#              the same bound I removed as a DEFECT when it happened by accident; here it is his
#              mechanic, asked for by name.
#   THE ARM NAMES ARE MINE. 'off' is the default so the bank does not move on a sweep.
LIN2_BARRAGE_FENCE = os.environ.get('W_V4_LIN2_BARRAGE_FENCE', 'any')   # which reversals may
#   contribute, by the line's FENCE STATE at its own reversal bar. Joe 1027: *"sweep reversing
#   infence vs reversing exfence"*.
#     'any'  no fence test - the banked behaviour, and what every measurement so far used
#     'in'   only a line that is INSIDE the r fence on the target side at its reversal bar
#     'ex'   only a line that is EX-FENCE on the target side at its reversal bar
#   The fence read is CLOSED, at the RAW reversal bar, per his 1026 *"move everything except
#   reversal detection to closed bars"*. It stays causal because the barrage acts at the reversal's
#   STAMP, which is later than the bar the fence is read at.
#   THE KNOB'S NAME AND ITS THREE ARM NAMES ARE MINE. 'any' is the default so the bank does not
#   move on a sweep.
LIN2_BARRAGE_ON = _knob('LIN2_BARRAGE_ON', 1, int)   # the barrage in the chain, on/off. BANKED ON,
#   Joe 1027: *"bank the barrage results and wire the mech into the chain"*. The knob's NAME is
#   mine; 0 is the A/B arm.

LIN2_MISMATCH_ACTION = os.environ.get('W_V4_LIN2_MISMATCH_ACTION', 'rev-trade')   # what a
#   mage-cascade MISMATCH does. Joe 1027: *"make this a knob: rev-trade, or, close only (so that
#   reentry creates the next open)"*.
#     'rev-trade'   the walk ends and the opposite side opens at the exhaust bar + 1. THE BANK.
#     'close-only'  the walk ends and NO opposite side opens - reentry is left to open the next one
#   IT GOVERNS THE cws1b COUNTER-OOB CADENCE ONLY, Joe 1027: *"narrow it - applies only to cws1b
#   counter oob"*. Every other cadence type always rev-trades on a mismatch.
#   'close-only' CURRENTLY LEAVES A GAP: v4_reentry is not wired into the chain (task 31), so
#   nothing opens the next trade and the chain stops at that exhaust.
LIN2_MAE_CAP = _knob('LIN2_MAE_CAP', 1.1)       # Joe 1027: *"if MAE > 1.1, cap mae at 1.1 and print
#   0 in mfe"*. A STOP-LOSS MODEL in the REPORT only - it changes no decision in the walk. A trade
#   whose adverse excursion passes the cap is reported at the cap with MFE 0, because it would have
#   been closed before it reached its favourable excursion. HIS CAP, HIS VALUE - the standing rule
#   is that no cap exists unless he sets one.

LIN2_CAND_NOT_REVERSED = _knob('LIN2_CAND_NOT_REVERSED', 0, int)   # a THIRD term on the baton
#   candidate test, Joe 1027: *"that's a good idea. can we test it on the day?"*. The banked rule is
#   ex-fence AND `towards` and NOTHING ELSE, so a line that has already reversed can still receive
#   the baton - measured on 2026-08-30 11:33:00, where ws12r took it at 82.87 carrying a reversal
#   stamped 11:23:40, 9 m 20 s earlier.
#     0  OFF - the banked rule, unchanged
#     1  a candidate must have NO reversal stamped since the rider took the baton
#     2  a candidate must have NO reversal stamped since the walk armed
#   DEFAULT 0 so the bank does not move on a test. THE REVERSAL WOB USED IS LIN2_REV_WOB 12, which
#   is MY choice - he named no wob for this term and LIFT_WOB 8 is the other candidate.
#   A THIRD READING IS NOT BUILT: replacing `towards` with the banked away/toward tag, which he
#   settled on 1027 as reading from the target side. That is a different mech, not a term.
LIN2_CASCADE_NO_ACTION = _knob('LIN2_CASCADE_NO_ACTION', 0, int)   # Joe 1027: *"get a mage-verdict,
#   and if its verdict matches the trade direction then take no action (ie keep walking)"*, and on
#   the mapping *"1, confirmed"*: `up` matches a LONG (target side HIGH), `down` matches a SHORT
#   (target side LOW). `neither` -> *"2, let the cadence decide"*, so it is NOT suppressed.
#   HIS FULL TRUTH TABLE, 1027, after the first build only had the no-action half:
#       LONG  + up    -> no action        LONG  + down  -> REV-TRADE
#       SHORT + down  -> no action        SHORT + up    -> REV-TRADE
#       neither       -> the cadence decides
#   A MISMATCH IS AN EXIT, not a fall-through to the board review.
#   THE cws1b COUNTER-OOB CADENCE IS EXEMPT FROM THE NO-ACTION HALF ONLY.
#   THE MECHANIC HAS NO NAME BUT HIS. I called it "suppression" in a report on 1027; that was
#   my coinage and it is gone. The cadence TAKES NO ACTION and the walk KEEPS WALKING - his
#   words. The row stage is 'NO ACTION'.
#   BANKED ON BY HIM, 1027: *"1, bank it, and make the current machine default"*. 0 is the A/B arm.

LIN2_CROSS_WOB = _knob('LIN2_CROSS_WOB', 12, int)   # Joe 1027: *"add the wob12 to all crosses to
#   ib and crosses to in-mom-fnc"*. Bars the NEW state must hold; the actionable bar is the LAST
#   bar of the hold, never the cross bar. It governs FIVE sites, every one of them a cross INTO the
#   gentler state - t1's cws1b oob->ib, t2's cws1r oob->ib, v4-arm-lineage-retest's cws1r oob->ib,
#   and both of the walk's pass-bar rules.
#   IT DOES NOT GOVERN CROSSES THE OTHER WAY. He named crosses to ib and to in-mom-fnc only, so
#   entering oob or entering ex-fence still carries no dwell - a single bar past the fence still
#   makes a line ex-fence and a rider candidate.
#   IT SUPERSEDES TWO EARLIER RULINGS OF HIS, both recorded here rather than quietly dropped:
#     1026, the retest's gap 5 - *"5, your read"* accepting L2_CWS1R_WOB 1 for ITS oob->ib cross
#     1026, in v4_l2_cadence's own header - *"every `oob_ib_cross` call takes xwob 1 and the cross
#       bar IS the actionable bar"*
#   The knob's NAME is mine, not his.
LIN2_COUNTER_OOB_ON = _knob('LIN2_COUNTER_OOB_ON', 0, int)   # the cws1b counter-target-side
#   oob cadence, Joe 1026: *"create a cadence when cws1b crosses to counter target-side oob (eg
#   08-30 1921)"*, marked IMPORTANT and *"go"* on 1027. BANKED ON. No wob - he named no dwell.
#   He has not NUMBERED this cadence, so its rows carry the description 'cws1b counter-oob'.

#  ── THE CHART-MATCHED READ: his 1101 reversal of the 1029 "drop prev-close" ──────────────────
#
#   HIS 1101 WORDS, verbatim: *"I didn't realise the closed_prev was exactly the same as "seam -5,
#   carried forward" - I was wrong to disable that"* / *"it makes sense to me that we will use
#   closed_prev only for exiting fences.  keeping the lift-off on emerging allows us to capture
#   those much needed 0445 reversal timestamps"* / *"I'm not sure about closed_prev for ib.  my gut
#   says emerging: create a knob that tests both options"* / *"1) build for both options, then we
#   can test both with ease a reduced downtime"*.
#
#   WHAT THE READ IS. `v4_closed_prev.series` - the line's EMERGING value at the last 5 s bar of
#   the most recently COMPLETED coarse bar, carried forward. That is the value TradingView shows as
#   that bar's close (docs/emerging_bar_open.md line 93), read causally. NaN until the first coarse
#   bar has completed, and a NaN fails every fence test, which is the quiet direction.
#
#   WHY IT MATTERS, measured on 2026-09-03 03:59:55..04:47:55, ws4r: 23 of 578 5 s bars are past
#   the 25.0 fence and NONE of the 13 chart points is. His words: *"if I take seam, then 0436
#   prints an ex-fence latch value that I can't see on the charts"*.
#
#   THE THREE KNOB NAMES ARE MINE. He named the reads - "exiting fences", "ib" - not the labels.
LIN2_CP_EXFNC = os.environ.get('W_V4_LIN2_CP_EXFNC', 'closed_prev')   # the ex-fence read's source.
#   BANKED 'closed_prev' on his 1101 ruling *"closed_prev only for exiting fences"*. 'emerging' is
#   the other arm and is the pre-1101 behaviour.
LIN2_CP_OOB = os.environ.get('W_V4_LIN2_CP_OOB', 'emerging')          # the oob 15/85 read's source.
#   BANKED 'emerging'. He did not put oob in either of his two categories; asked which, he said
#   *"build for both options, then we can test both with ease a reduced downtime"*. The bank is
#   therefore today's read and 'closed_prev' is the arm, so banking it moves no verdict by itself.
LIN2_CP_IB = os.environ.get('W_V4_LIN2_CP_IB', 'emerging')            # the oob->ib cross's source.
#   BANKED 'emerging' - *"my gut says emerging: create a knob that tests both options"*. His gut IS
#   the bank until the arms are measured.
#   *** 1101, LATER: HE MOVED ws1r ONTO THE CHART-MATCHED READ. *** *"change ws1r to closed-p"*.
#   That reverses the ws1 half of his earlier rule *"ws1{any} and gcws1{any} stay on emerging"*,
#   whose reason was the 09-03 0326 arm - so the arm race's own ws1r oob read moves with it and
#   the arm list is re-measured beside his five validated timestamps, not assumed.
#   REVERSAL DETECTION IS STILL EMERGING and that is unchanged: `ws1r_revs` feeds on the emerging
#   array, his *"keeping the lift-off on emerging"*. Only ws1r's VALUE reads move.
LIN2_CP_MIN_TF = _knob('LIN2_CP_MIN_TF', 1, int)   # the TF floor for the chart-matched read.
#   HIS 1101 RULE: *"ws1{any} and gcws1{any} stay on emerging (otherwise we lose the 09-03 0326
#   arm). all else is closed-prev"*. At 2 every ws1 line is exempt.
#   *** MY gcws READING WAS WRONG AND HIS LITERAL WORDS WERE RIGHT. *** I read "gcws1{any}" as
#   "every line at or below ws1's 60 s", which exempted gcws30b at 30 s. Asked directly whether
#   "make this the machine" routes gcws30b, he said *"yes"*. So the exemption is gcws1-anything,
#   which is a line that does not exist, and gcws30b routes like everything else. This floor
#   governs the r ladder only; gcws30b has its own knob below because it is not in that ladder.
#   *** HIS 1101 REVISION: THE LIFT-OFF DETECTOR NEEDS A CHART-MATCHED MODE. *** *"lift-off needs
#   a close-p mode - it only reacts to full 1 minute bars"*.
#   WHY HE ASKED. On 2026-09-03 the t1 r gate took a reversal at 06:24:35 where ws1r on the
#   every-bar read fell 69.18 -> 62.38, a turn AWAY from the high target side, because `lift_off`
#   fired on an intra-bar move. On the chart-matched series the line steps once per 60 s bar, so a
#   lift-off can only land on a bar close.
#   THIS REVISES HIS EARLIER RULING, and that is on the record: *"keeping the lift-off on emerging
#   allows us to capture those much needed 0445 reversal timestamps"*. Those 0445 reversals were
#   his reason for the every-bar read, and this arm gives them up. 'emerging' is the other arm.
#   SCOPE: the t1 r gate's ws1r reversal BARS only. `_rev_pairs`, which finds each RUNG's reversal
#   for the baton, is a different consumer and is NOT routed by this - he named lift-off in the
#   context of the t1 marker and the rungs are not measured here.
#  ── THE fdm RE-ENTRY: his 1102 mech, banked on his *"bank this and make it the reentry machine"* ─
#
#   HIS SPEC, built in this order:
#     the window OPENS   gcws30b at or beyond the (5.0, 95.0) pair on the target side
#     the window CLOSES  gcws30b's oob->ib cross at the 15/85 pair - `jig.oob_ib_cross`, the banked
#                        mech. His words: *"I see gcws30b "returning to ib" (the mech) at 0041"*,
#                        and the cross bar on 2026-08-03 is 00:41:30, which he confirmed:
#                        *"00:41:30 is my view also"*
#     the GATE           ws1r AND (ws2r or ws3r), each SEEN past the r fence anywhere inside the
#                        window. His *"the lines need to be seen in the window, but do not need to
#                        dwell for the window's full range"*
#     the FIRE           at the close bar. His *"tested at gcws30b window's close.  if the test is
#                        true, open a trade"*
#   THE SIDE IS THE OOB SIDE THE LINES WERE FOUND ON, his 1102 answer. `v4_signal.direction` then
#   maps it: a HIGH oob side opens a SHORT. That mapping is banked and not mine.
FDM_RE_IB_XWOB = _knob('FDM_RE_IB_XWOB', 1, int)  # the window's ib cross hold, in bars.
#   1 MEANS THE CROSS BAR ITSELF, the same hold the cadence event uses on ws1b.
FDM_RE_B_FNC = _knob('FDM_RE_B_FNC', 5.0)       # gcws30b's own fence, 5 -> (5.0, 95.0).
#   READ ONLY BY THE ARMS THAT NAME gcws30b. The banked window is ws1b at both ends.
FDM_RE_WIN_OPEN = os.environ.get('W_V4_FDM_RE_WIN_OPEN', 'ws1b')
FDM_RE_WIN_CLOSE = os.environ.get('W_V4_FDM_RE_WIN_CLOSE', 'ws1b')
#   WHAT OPENS AND WHAT CLOSES THE RE-ENTRY WINDOW. His 1103: *"other than this binary option, do
#   you see any other permuatations of ws1b and gcws30b?  if so, test the net outputs"* / *"run EFG
#   as well"*.
#     open 'ws1b'      ws1b crosses to oob on the side. THE BANK, his *"replace gcws30b crossing
#                      to ex-5/95 with ws1b crossing to oob"*
#     open 'gcws30b'   gcws30b crosses beyond FDM_RE_B_FNC on the side
#     open 'both'      ws1b oob on the side AND gcws30b beyond its fence on EITHER side
#     open 'first'     whichever of those two conditions holds first
#     open 'sameside'  both on the SAME side
#     close 'ws1b'     ws1b's oob->ib cross on the side. THE BANK
#     close 'gcws30b'  gcws30b's oob->ib cross on the side, read at the oob pair
#   'both', 'first' and 'sameside' ARE MINE - he asked whether other permutations exist and told me
#   to run them. They are not permutations of the two slots; they are new opening tests.
#   HIS 1105 PURGE: *"purge '--gcws30b is past the 5/95 fence, on either side' from the reentry
#   spec"*. The gcws30b clause is OUT of the opening test, so the open is 'ws1b' alone - ws1b oob
#   on the side and nothing else. gcws30b is still read by the cadence-event mech and by the
#   window's own close arm; this purge is the OPENING test only.
#   ── THE RE-ENTRY'S OWN WALK, BANKED 1104 ──────────────────────────────────────────────────────
#   HIS 1104 SPEC, which REPLACED the ws1r AND (ws2r or ws3r) gate outright - his *"that looks like
#   our reentry mech ... bake this into the machine, and make this the machine"*, and his *"replace
#   it"* when asked whether the old gate survived:
#
#     -if a cadence window opens
#     --walk until ws5 reverses
#     ---if ws5r reverses while ex-20/80-fence
#     ----if ws6r is oob
#     -----walk forward until ws6r reverses
#     ----else if ws6r is not oob
#     -----scan the wsf TFs above ws6 for a wsf ws{higher TF}r that is infence
#     -----if a higher wsf TF r is infence
#     ------open a trade on the last to fire, out of ws5r reversing or ws6r reversal or ws1b
#           crossing to ib
#     #all signals are sameside of the cadence
#
#   FDM_RE_GATE_FNC IS GONE with the gate it served. Nothing reads it.
FDM_RE_REV_READ = os.environ.get('W_V4_FDM_RE_REV_READ', 'closed_prev')
#   WHICH READ THE ws5 AND ws6 REVERSALS COME OFF. His 1104 *"-use closed-prev"*, which OVERRIDES
#   the standing fdm rule that lift-off is the one emerging read. 'emerging' is the arm it replaced.
#   MEASURED on 2026-09-15 and 2026-09-16, per distinct trade: closed-prev cut the trade count from
#   23 to 13 and moved every reversal onto the line's own 5 or 6 minute grid, and it is what let the
#   ws6r gate below catch the 18:17 window. The two are banked together because he ruled them in
#   sequence against the same window.
FDM_RE_WS5_FNC = _knob('FDM_RE_WS5_FNC', 20.0)   # ws5r's fence AT its reversal, 20 -> (20, 80).
#   HIS 1104 *"if ws5r reverses while ex-20/80-fence"*. The smaller end, his convention. It is a
#   SEPARATE knob from FDM_FNC_2080 so sweeping it cannot move step 1's fence or the population's.
FDM_RE_WS6_GATE = os.environ.get('W_V4_FDM_RE_WS6_GATE', 'ex2080')
#   WHAT MAKES THE WALK WAIT FOR ws6 TO REVERSE. His 1104 *"the ws6r gate might need to move from
#   oob to ex-20/80-fence"*, then banked with *"that looks like our reentry mech"*.
#     'ex2080'  ws6r at or past the FDM_FNC_2080 pair on the side. THE BANK
#     'oob'     ws6r oob on the side. The arm it replaced, his first spec
#   ex-20/80 is a SUPERSET of oob, so the bank can only send MORE windows down the wait branch.
#   MEASURED on the two days: 11 of 12 trades are identical between the arms. The whole difference
#   is the 2026-09-15 18:17 / 18:37:30 cluster, where oob opened two trades at -5.470% and -0.133%
#   and ex-20/80 opens one at -0.824% with +1.428% favourable.
FDM_RE_REV_TF = _knob('FDM_RE_REV_TF', 5, int)    # the line whose reversal starts the walk.
FDM_RE_GATE_TF = _knob('FDM_RE_GATE_TF', 6, int)  # the line that gates the wait, read at that bar.
#   HIS 1104: *"replace ws5 and ws6 with higher TFs, and scan higher than ws12"*. ws5 and ws6 are
#   the spec he wrote the mech on and they stay the DEFAULT; the knobs exist so the pair can be
#   lifted without a second copy of the walk. The gate TF must sit above the reversal TF, and the
#   assert in v4_fdm_reentry.signals carries that.
FDM_RE_CLIMB = os.environ.get('W_V4_FDM_RE_CLIMB', 'off')
#   HIS 1104 PROBE: *"it might be a dynamic mech - ride upwards through the TFs until you reach a
#   tf showing the in fence r line, then open the trade"*.
#     'off'       the banked ws5/ws6 mech - one gate line, then the fixed scan band. THE BANK
#     'value'     climb from the reversal line + 1, stepping up while each r is ex-fence, and open
#                 at the first in-fence r. One bar, one read per rung
#     'reversal'  the same climb, but each ex-fence rung must print its OWN reversal before the
#                 climb steps up. His ws6 branch, generalised to every rung
#   WHAT COUNTS AS EX-FENCE ON A RUNG is FDM_RE_WS6_GATE, the same knob the single gate used.
FDM_RE_CLIMB_HI = _knob('FDM_RE_CLIMB_HI', 12, int)
#   THE CLIMB'S CEILING. 12 is wsf's own top, his 1017 band names. A climb that reaches the ceiling
#   without an in-fence rung produces NO trade, which is the same shape as the band finding nothing.
FDM_RE_SCAN_FLOOR = os.environ.get('W_V4_FDM_RE_SCAN_FLOOR', 'gate')
#   WHERE THE SCAN BAND STARTS. His *"scan higher than ws12"* reads two ways and BOTH are arms:
#     'gate'  the TF above the gate line, which is the mech's own shape - ws7 when the gate is ws6
#     'ws13'  strictly above ws12, his sentence read literally, whatever the pair is
#   The band's ceiling is FDM_RE_SCAN_HI. 'gate' with the banked pair reproduces FDM_RE_SCAN_LO 7.
FDM_RE_SCAN_LO = _knob('FDM_RE_SCAN_LO', 7, int)   # the scan's first TF. ws6 + 1.
FDM_RE_SCAN_HI = _knob('FDM_RE_SCAN_HI', 12, int)  # the scan's last TF. wsf's own ceiling.
#   HIS 1104 *"scan the wsf TFs above ws6"*. wsf is ws1-ws12, his 1017 band names, so the band is
#   ws7..ws12. A line passes when it is STRICTLY inside the FDM_FNC_2080 pair - "ex" includes oob,
#   his rule, so a line past either end is not in-fence.
FDM_RE_FIRE_IB = _knob('FDM_RE_FIRE_IB', 1, int)
#   IS ws1b's ib CLOSE IN THE LAST-TO-FIRE SET. His 1104 *"open a trade on the last to fire, out of
#   ws5r reversing or ws6r reversal or ws1b crossing to ib"*, so 1 is his spec. 0 drops the ib close
#   and leaves the two reversals, which is the arm his update replaced.
#   ON THE TWO DAYS the ib close was last on 1 of 19 trade rows under the banked gate.

#   ── fdm2, HIS 1103 MACHINE ────────────────────────────────────────────────────────────────────
#   The bimodal walk-or-rev-trade decision REPLACED the old fdm-cadence body: *"yes, but don't
#   delete the fdm work.  let's call this sandbox `fdm2`"*. The old body is untouched in
#   1103_fdm/; nothing of it is read by these knobs, and his offline spec notes are out of the
#   sandbox entirely - his *"theses fdm_spec notes have no place"*.
FDM_FNC_2080 = _knob('FDM_FNC_2080', 20.0)      # HIS NAME 'fdm-20-80-fnc'. 20 -> (20.0, 80.0).
#   "ex" INCLUDES oob, his standing rule, so the test is r <= 20 low / r >= 80 high.
FDM_M3_FNC = _knob('FDM_M3_FNC', 25.0)          # ws3Mage's own fence in the preamble, 25 -> 25/75.
FDM_M3_RESCUE_ON = _knob('FDM_M3_RESCUE_ON', 1, int)   # 1 runs his 1103 ws3Mage gate update.
FDM_M3_RESCUE_FNC = _knob('FDM_M3_RESCUE_FNC', 40.0)   # the rescue's ws3Mage fence, 40 -> 40/60.
#   HIS 1103 MECH UPDATE, verbatim:
#     -IF a cadence is gated at the windows close (ws1b to ib) because ws3Mage stayed infence
#     --IF ws3r was oob during the window (from gcws30b ex-5/95, to ws1b crossing to ib)
#     ---IF ws3Mage was ex-40/60-fence during the window
#     ----print a cadence event
#   THE RESCUE'S WINDOW IS HIS, AND IT IS NOT THE CADENCE EXCURSION. He names it: from gcws30b's
#   cross beyond FDM_RE_B_FNC to the ws1b ib cross. gcws30b's ex-fence bar can sit well before
#   ws1b goes oob - 2026-09-15 14:00:00 against 14:33:00 - so this span usually CONTAINS the
#   cadence excursion rather than matching it.
#   40/60 IS WIDER THAN THE 25/75 IT RESCUES, so ws3Mage has less distance to cover; the price is
#   the new ws3r oob requirement, which 25/75 never asked for.
FDM_POP_LO = _knob('FDM_POP_LO', 3, int)        # the reversal population's floor TF. ws3..ws30.
#   HIS 1103: *"ws3 to ws30 for both the cadence and the ws10x-cadence"*. The top is L2_MOM_MAXTF
#   30, so the population is 28 lines before the ex-fence filter.
FDM_STEP1_ABOVE_TF = _knob('FDM_STEP1_ABOVE_TF', 3, int)   # step 1 scans STRICTLY above this TF.
#   HIS 1103 *"above in timeframe"* on *"lines printing above ws3r"*, so the scan is ws4..ws30 -
#   27 lines. DIFFERENT RANGE FROM THE POPULATION, which starts at ws3. Both are his words.
FDM_X10_WOB = _knob('FDM_X10_WOB', 24, int)     # the ws10x race's hold, 24 bars = 120 s.
#   HIS 1103 RULING: *"now that we have the grade period, we can leverage a smaller wob: use 24"*.
#   He had written "wob 24 or 36" and used 36 in his own 1841 example; 36 is the other arm.
FDM_X10_FRM = os.environ.get('W_V4_FDM_X10_FRM', 'cross')   # 'cross' | 'confirm'.
#   WHICH BAR OF THE ws10x RACE MUST FOLLOW THE CADENCE EVENT. RULED 'cross' at 1103 - he read the
#   as-built spec with this marked #MINE and said *"your #MINE lines are all good"*. 'confirm' lets
#   a race that began before the cadence event count; it is the arm, not the bank.
FDM_REV_FROM = os.environ.get('W_V4_FDM_REV_FROM', 'event')   # 'event' | 'window'.
#   WHERE THE REVERSAL COUNT STARTS. HIS 1103 ASK, two poles: *"add a 2-pole knob: 'from the
#   cadence event bar' and 'from the cadence event bar's window open'"*.
#     'event'    the cadence event bar - ws1b's oob->ib cross
#     'window'   the FIRST bar of that cadence event's ws1b oob excursion
#   'window' always starts earlier, so it can only count the same reversals or more.
#   'event' IS THE DEFAULT because it is the behaviour every number so far was measured on; he
#   gave the two poles and did not rule between them, so 'window' is unmeasured.
FDM_X10_GRACE_PCT = _knob('FDM_X10_GRACE_PCT', 40.0)   # HIS NAME 'fdm-ws10x-cad-grace'. Percent.
FDM_X10_TRADE_PCT = _knob('FDM_X10_TRADE_PCT', 50.0)   # the grace walk's rev-trade threshold.
#   HIS VALUE, his *">=50%"*. THE KNOB IS MINE - he named only the 40 as a knob, and a stated
#   threshold with no knob cannot be moved without an edit.
FDM_X10_GRACE_MIN = _knob('FDM_X10_GRACE_MIN', 5.0)    # the grace walk's length, minutes.
#   HIS VALUE, his *"we add a 5 minute walk"*. 5.0 min = 60 bars at the 5 s grid. THE KNOB IS MINE.
#   ── fdm2's OWN v4saviour SETTINGS, banked 1103 ────────────────────────────────────────────────
#   HIS 1103: *"bank the config that produced branch B at 1404 and wire it into the sandbox"*.
#   THEY ARE fdm2's OWN KNOBS, NOT THE SAV_* ONES. v4_machine.py and v4_sig_saviour.py read
#   SAV_CASCADE_MIN 4 and SAV_CASCADE_ZOOM 2, so moving those defaults would move the live
#   octo-v4 machine. Same reason FDM_RE_WS5_FNC is separate from FDM_FNC_2080.
FDM_SAV_ON = _knob('FDM_SAV_ON', 0, int)        # 1 wires v4saviour into fdm2's leg walk.
#   OFF, HIS 1103: *"we're dropping saviour for now - I still think it has a place, but only if I
#   can find the confluence it needs to be stable"*. The settings below keep their measured values
#   so the config is not lost. What it cost at FDM_SAV_ON 1, each day against its own off arm:
#   2026-08-03 -1.051% -> -3.103% net on 5 firings, and 2026-09-15 +7.316% -> -15.040% on 9.
FDM_SAV_READ = os.environ.get('W_V4_FDM_SAV_READ', 'emerging')   # 'emerging' | 'chart'
#   HIS *"use emerging values, at the emerging ws1Mage extermum"*. At 'emerging' the r fences, the
#   lift-off and the Mage ladder all read the emerging set and the extremum sampler takes no seam
#   lattice, because an emerging line steps on every 5 s bar.
FDM_SAV_TF_HI = _knob('FDM_SAV_TF_HI', 3, int)  # the cascade ladder's top rung. His *"ws1-3"*.
FDM_SAV_MIN = _knob('FDM_SAV_MIN', 3, int)      # lines a cluster must cover. 3 of the 3-line ladder.
FDM_SAV_ZOOM = _knob('FDM_SAV_ZOOM', 2, int)    # rungs each cluster step compares across.
#   MIN 3 WITH ZOOM 2 IS THE PAIR THAT FIRED. Measured on the 2026-09-15 13:56:10 LONG: min 3
#   zoom 2 reverses at 14:04:05 off branch B; min 4 zoom 2, min 4 zoom 1 and min 3 zoom 1 all
#   stay open. At zoom 1 the ws2->ws3 step is +1.6574 and breaks the low cluster; zoom 2 compares
#   ws1 against ws3 directly at -17.4088.
FDM_SAV_ARM = _knob('FDM_SAV_ARM', 0, int)      # 0 drops the ws5r walkback arm. His *"remove the
#   armed gate"*. At 0 ws5r is not read at all.
FDM_MAE_CAP = _knob('FDM_MAE_CAP', 1.1)         # the stop, percent adverse from the open.
#   HIS 1103 *"add the typical mae1.1 stop"* AND *"yes, move it to default"*. ON, always applied -
#   unlike LIN2_MAE_CAP 1.1, which stayed behind W_MAE_CAP=on in lineage2's sealed driver.

#   ── the fdm2-conf machine, BANKED 1104 ─────────────────────────────────────────────────────────
#   HIS 1104: *"make this the fdm2-conf machine"*. The table's row is a DATA BAR - a bar where the
#   mech collects the board and decides `walk` or `rev-trade` - and the decision is made on the
#   INCOMING trade AND ITS SIDE, his words.
#   ── his 1104 re-entry mod: the x-cross of a waiting line's own r ──────────────────────────────
#   HIS SPEC, verbatim:
#       -IF a ws{a TF}r line is ex-20/80-fence and waiting to reverse before handing over to the
#        next highest TF (example ws5r lowside, 08-07 0650 to 0705)
#       --IF a ws{a TF}x crosses the ws{a TF}r line using emerging values and wob 12 (crosses over
#         for lowside, crosses UNDER for highside) (example ws5x crossing over ws5r at 0702)
#       ---IF ws{a TF +1}r is infence (example at 0702, ws6r is 43)
#       ----rev-trade
#   HIS 1104 CORRECTION on the direction: *"1, under for highside"*, which restores the banked
#   x-cross rule - under for a high side, over for a low one.
FDM_RE_XCROSS_ON = _knob('FDM_RE_XCROSS_ON', 1, int)   # 1 wires his mod into the re-entry walk.
FDM_RE_XWOB = _knob('FDM_RE_XWOB', 12, int)      # his hold, bars. 12 bars = 60 s.
#   HIS VALUE, *"wob 12"*. Same number as LIN2_CROSS_WOB 12, which lives in lineage2 and is a
#   different mechanic, so the two are held apart.
FDM_RE_XCROSS_TFS = os.environ.get('W_V4_FDM_RE_XCROSS_TFS', 'band')  # 'band'|'both'|'rev'|'gate'.
FDM_RE_XCROSS_LO = _knob('FDM_RE_XCROSS_LO', 4, int)   # the LOWEST line the mod watches.
#   HIS 1105: *"make ws4 the lowest TF"*. 4, not the trigger line - the floor being the trigger
#   line was my own choice and it hid the one cross that passes at 2026-08-07 05:44:20, ws4x with
#   ws4r having reached 12.1980 past the 20 fence at 05:44:00 and ws5r 30.4863 in-fence. Every
#   line from ws5 up fails the fence in that stretch; ws5r's deepest is 20.8752, 0.88 short.
#   WHICH LINES THE MOD WATCHES. HIS 1105: *"in my spec, I intentionally referd to `a TF`, so
#   that you would see the dynamic nature of the mod"*, and his 1104 *"any lines that fdm2-reentry
#   needs"*.
#     'band'   EVERY line from FDM_RE_REV_TF 5 up to FDM_RE_SCAN_HI 12 - the lines the re-entry
#              reads. THE BANK, his dynamic reading. The earliest qualifying confirm across the
#              band fires
#     'both'   only the reversal line and the gate line, two fixed points. The arm it replaced
#     'rev'    the reversal line alone
#     'gate'   the gate line alone
#   THE BAND'S TOP IS FDM_RE_SCAN_HI, not a knob of its own: those are the lines the re-entry
#   already reads, and a line above them would need him to say so. THAT CHOICE IS MINE.
FDM_RE_XCROSS_FNC_AT = os.environ.get('W_V4_FDM_RE_XCROSS_FNC_AT', 'stretch')  # 'stretch'|'cross'
#   WHERE HIS EX-20/80 CONDITION IS READ. HIS 1105 CORRECTION: *"there was no such 'ws4r is not
#   past the 20 fence' gate on the ws{a TF}x cross"*. In his spec the fence sits on the OUTER
#   line - *"a ws{a TF}r line IS ex-20/80-fence and waiting to reverse"* - so it is the STATE the
#   line is in while waiting, not a test at the cross bar.
#     'stretch'  the line was past the fence at some bar from the window's open to the cross.
#                THE BANK, his reading
#     'cross'    the line is past the fence AT the cross bar. The arm I had built, which added a
#                gate he did not write
FDM_RE_XCROSS_UP_READ = os.environ.get('W_V4_FDM_RE_XCROSS_UP_READ', 'closed_prev')
#   THE ws{TF+1}r IN-FENCE READ. 'closed_prev' because his own example number, *"ws6r is 43"*, is
#   the closed-prev value at that bar - emerging reads 40.79 there. THE KNOB NAME IS MINE and the
#   read is my call, stated. 'emerging' is the other arm.

FDM_CONF_READ = os.environ.get('W_V4_FDM_CONF_READ', 'closed_prev')   # 'closed_prev' | 'emerging'.
#   THE VALUE SOURCE for the fdm2-conf table's toward/away. BANKED 'closed_prev' on his 1104
#   *"make sure that closed-prev is the standard for everything except lift-off"*, which is the
#   LATER of his two rulings here - the earlier was *"emerging must be the answer to the larger
#   question"* for this table, and 'emerging' keeps it as the arm. The lift-off inside
#   jig.fdm2_cad_mom_detector reads EMERGING at either setting; this knob never touches it.
FDM_CONF_BARS = os.environ.get('W_V4_FDM_CONF_BARS', 'event+x10')   # 'event' | 'event+x10'.

#   ── fdm2-wsxcad-director, HIS NAME 1104 ────────────────────────────────────────────────────────
#   HIS UPDATE 1: *"instead of using a static TF10 to create the ws10x-cadence, we will set the TF
#   dynamically based on the highest TF (`fdm-conf-xcross-candidate`) that is printing `away` while
#   the TF lines above `fdm-conf-xcross-candidate` are `towards` and ex-20/80-fence"*.
#   `fdm-conf-xcross-candidate` IS HIS KNOB NAME for the chosen line. The others here are mine.
FDM_XCAD_ON = _knob('FDM_XCAD_ON', 1, int)      # 1 routes the cadence through the director.
#   ON, HIS 1104 *"apply the update to the code so that ws10 does not interfere with the intention
#   of the spec"*. At 0 the race stays pinned to ws10 and every banked fdm2 number is reproduced.
FDM_XCAD_RULE = os.environ.get('W_V4_FDM_XCAD_RULE', 'B')   # 'B' | 'A'.
#   WHICH READING OF *"the TF lines above"*. HIS 1104 *"unsure.  use B for now, we can change it
#   to A if the data doesn't match my eye's verdict"*.
#     'B'  the next FDM_XCAD_ABOVE lines above the candidate, each towards AND ex-20/80
#     'A'  every ex-20/80 line above the candidate is towards, however many there are
#   Both pick ws8r at his own 2026-08-07 16:11:00 example; they part on other bars.
FDM_XCAD_ABOVE = _knob('FDM_XCAD_ABOVE', 2, int)    # lines above, rule 'B' only.
#   2 IS HIS OWN COUNT, from his confluence rule *"the 2 lines above the highest TF"*. At 3 his
#   16:11:00 example produces NO candidate, so 3 is ruled out by his example.
FDM_XCAD_EXF = _knob('FDM_XCAD_EXF', 0, int)    # 1 requires the candidate line to be ex-20/80.
#   0 IS HIS RULING, 1104: asked whether the candidate must be ex-20/80 he answered *"no"*.
FDM_XCAD_FRM = os.environ.get('W_V4_FDM_XCAD_FRM', 'confirm')   # 'confirm' | 'cross'.
#   WHICH BAR UPDATE 2 STARTS FROM. HIS 1104 *"the conf bar"*. At his example the confirm is
#   16:17:30 and the cross 16:15:35.
FDM_XCAD_C2_SCOPE = os.environ.get('W_V4_FDM_XCAD_C2_SCOPE', 'tagged')  # 'tagged' | 'board'.
#   HIS SECOND CLAUSE, *"AND there are no more ex-20/80-fence lines tagged as `towards`"*, has two
#   readings and his word "tagged" is what splits them:
#     'tagged'  the lines that were BOTH ex-20/80 AND towards at the cadence event. None of them
#               may still read towards at the test bar
#     'board'   any line that is ex-20/80 AND towards AT THE TEST BAR blocks it, tagged or not
#   'tagged' is the default because he wrote "tagged". THE REPORT PRINTS BOTH VERDICTS so the
#   reading can be settled on numbers. THE KNOB IS MINE.
FDM_XCAD_TAG_AT = os.environ.get('W_V4_FDM_XCAD_TAG_AT', 'event')   # 'event' | 'xbar'.
#   WHERE THE `towards` TAGS COME FROM. HIS 1104 *"tagged at the cadence event bar"*. At his
#   example that is 16 of 30 lines at 16:11:00 against 18 of 30 at 16:17:30.
FDM_XCAD_REV_FROM = os.environ.get('W_V4_FDM_XCAD_REV_FROM', 'window')   # 'window' | 'event'.
#   WHERE THE REVERSAL GATE'S SPAN STARTS for update 2's re-read. HIS 1104 *"the target-side
#   reversal must fire between the opening of the cadence window and the confirmed x-cross bar"*,
#   so 'window' is the bank. IT GATES ONLY THE REVERSAL - the extremum keeps the trade's own open
#   as its anchor, because he named the span for the reversal and nothing else. THAT READING IS MINE.
FDM_XCAD_REV_TO = os.environ.get('W_V4_FDM_XCAD_REV_TO', 'read')   # 'read' | 'confirm'.
#   WHERE THE REVERSAL GATE'S SPAN ENDS. HIS 1104 CORRECTION OF HIS OWN RULING: *"the window's end
#   can't be the confirmed x-cross - that would mean the grace period has zero value. update my
#   statement to suit"*. At 'read' the span ends at the bar being read, so a turn that lands
#   during the walk is counted the moment its stamp lands. At 'confirm' it ends at the confirmed
#   cross and the count is frozen for the whole walk, which is what he just struck out.
#   MEASURED on 2026-08-07 16:11:00: at 'confirm' ws11 and ws12 both counted 0 turns for all 10
#   minutes although ws11 turned at 16:17:45 and ws12 at 16:18:25.
FDM_XCAD_SEAM_S = _knob('FDM_XCAD_SEAM_S', 15.0)    # seconds past the ws1 seam, HIS value.
#   HIS 1104 *"walk to the next ws1 seam+15s"*. 15 s = 3 bars at the 5 s grid.
FDM_XCAD_WALK_MIN = _knob('FDM_XCAD_WALK_MIN', 10.0)    # the truncating walk, minutes. HIS value.
#   HIS 1104 *"walk forward 10 minutes, test for `away` at each emerging bar, truncate the walk if
#   the test passes"*. The SHAPE is the grace walk's, which he called "the established walk":
#   re-test every 5 s bar and break out on the first pass. 10.0 min = 120 bars.
FDM_XCAD_FALLBACK = os.environ.get('W_V4_FDM_XCAD_FALLBACK', 'exfnc')  # 'exfnc' | 'off'.
#   HIS 1105 ADDITION: *"IF the scan for TFs inside of {linhop} jumps shows no candidates, then
#   scan the entire range for ex-20/80-fence lines instead. if any are found, the cadence verdict
#   is 'keep on walking'"*.
#     'exfnc'  no candidate -> scan ws1..ws{HI} for ex-20/80 lines on the side. Any found and the
#              verdict is WALK. THE BANK
#     'off'    no candidate goes straight to FDM_XCAD_NONE, the arm this replaced
#   HIS *"{linhop} jumps"* NAMES THE EXISTING CANDIDATE TEST, which looks FDM_XCAD_ABOVE 2 lines
#   above each line - the same 2 as LIN_HOP. The two knobs are left separate because one belongs
#   to the director and the other to lineage; the VALUE is identical so nothing moves. SAY SO IF
#   THEY SHOULD BE ONE KNOB.
FDM_XCAD_NONE = os.environ.get('W_V4_FDM_XCAD_NONE', 'rev-trade')   # 'rev-trade' | 'no-action'.
#   WHAT NO CANDIDATE MEANS. HIS 1104 *"unless I'm wrong, no candidates = rev-trade.  validate
#   this in the existing code"* - validated: v4_fdm2.walk already returns a REV-TRADE row the
#   moment step 1's count is 0, so "no qualifying lines fires a rev-trade" is the code's own
#   precedent. Step 1's set is a different set from the director's, which is why this is a knob.
#   WHICH BARS THE TABLE COLLECTS THE BOARD ON. 'event+x10' is every cadence event plus that
#   event's own ws10x race confirm - the two bars the machine already owns. 'event' drops the race
#   confirm. THE KNOB NAME IS MINE. His 1104 ws8x experiment is NOT a value here: the race on a
#   line other than ws10 has no producer yet, and which line it would run on is unruled.

LIN2_CP_LIFT = os.environ.get('W_V4_LIN2_CP_LIFT', 'closed_prev')
LIN2_CP_WS1R = os.environ.get('W_V4_LIN2_CP_WS1R', 'closed_prev')   # ws1r's VALUE source in
#   the t1 r gate. BANKED 'closed_prev' on his 1101 *"change ws1r to closed-p"*. THE KNOB NAME IS
#   MINE. It routes the GATE's value read only - `ws1r_revs`, which finds the reversal bars, keeps
#   the emerging array because he ruled lift-off stays emerging. The two are different questions:
#   WHEN did ws1r reverse (emerging) and WHAT was its value at that stamp (this knob).
LIN2_CP_GCWS30B = os.environ.get('W_V4_LIN2_CP_GCWS30B', 'closed_prev')   # gcws30b's source.
#   BANKED 'closed_prev' on his 1101 *"yes"*. THE KNOB NAME IS MINE; the line and the ruling are
#   his. It routes gcws30b for EVERY consumer - the t1 cadence and the arm race both read
#   CL['g30b'] - because he routed the LINE, not one mech's view of it.
#   WHAT IT MOVES, measured before it was banked: the high-side t1 count over 2026-09-03
#   01:30..03:30 goes 3 -> 4, his 02:35 reversal appears as the 02:36:25 cadence, and the 02:15
#   cadence he could not see on his chart is gone on both sources once the 5/95 fence is in.
#   IT ALSO MOVES THE ARM, which is not measured yet: his validated arm list - 17:16, 22:01, 23:39,
#   00:07, 00:36 - was matched on the EMERGING gcws30b to within 1.4 min, and the arm race reads
#   this same array. 'emerging' is the other arm of the knob.

L2_ARM_RETEST = _knob('L2_ARM_RETEST', 1, int)  # v4-arm-lineage-retest on/off. BANKED ON - he
#   named it and ruled all nine of its gaps on 1026. 0 is the A/B arm.
L2_T3_ON = _knob('L2_T3_ON', 0, int)            # t3cadence on/off. BANKED **OFF** 1026 - Joe:
#   *"10, yes - the old t3 is defunct"*. The 2-staged latch above replaces it. 1 is the A/B arm,
#   kept so the superseded mech can still be measured against the latch.
#   Joe 1026, after the 24 t3 events scored: *"I see what you see - it doesn't hold up ... disable
#   t3 and walk forward from the arm"*. Off is an EXPERIMENT, so the run refuses without
#   W_V4_EXPERIMENT=1 and prints the delta. t1, t2 and t4 are untouched by it.
L2_GATE_MODE = _knob('L2_GATE_MODE', 'closed', str)   # which ladder t3cadence's oob population
#   gate reads. Joe 1026 FINAL: *"move everything except reversal detection to closed bars"*.
#   HE MOVED IT TWICE. First *"build a proxy that sends the emerging values to the gate decision"*,
#   which set it to 'emerging'; then, shown that t3's population was counting an EMERGING ws7r oob
#   that the closed cws7r never had, *"move everything except reversal detection to closed bars"*.
#   So the ONLY emerging read left in lineage2 is the reversal detection - his 1025 reason stands
#   for that one: *"I don't want slower TF's running on closed bars because it spoils the line
#   reversal times"*. 'emerging' is kept as the other arm of the A/B.
#   `v4_l2_proxy.Board` is the one place the routing lives.
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
L2_T3_MIN_MATRY = _knob('L2_T3_MIN_MATRY', 2, int)  # the fewest matryoshka lines that must have
#   REVERSED for t3 to fire. Joe 1026: *"use the >=2 applied to the lines that actually reversed"*.
#   t3's need is `max(this, round(L2_T3_FRAC x the ex-fence population))`.
#   IT WAS ON THE RANGE FIRST, from his *"when the rider has fewer than 2 lines in its matryoshka,
#   t3 simply never fires"*. That let t3 fire on a SINGLE reversal: at 2026-08-30 20:11:00 the
#   rider was ws9, its matryoshka {ws7, ws8} met the floor, only ws7 had reached ex-fence, and
#   round(0.75 x 1) = 1. One line satisfied a rule whose point is *"if >1 lines ... have
#   reversed"*. The range check survives as an early-out only.
#   The matryoshka of a rider at TF N is ws7..N-1 - *"ws7 is the floor for t3"*.
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
    'RMOM_FNC':         (75.0,  '"v4_rmom_fnc, default 80 - fence used when testing if a r is close'
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
    'SAV_CASCADE_TF_HI': (12, 'THE BANKED LADDER TOP, what v4_machine gets. HIS 1103 "reduce the mage cascade to ws1-ws6" is fdm2\'s own value, passed by its driver so the live machine is untouched'),
    'SAV_CASCADE_ANCHOR': ('liftoff', 'HIS #25 "not extrema - measure where the r reversals print" is the bank. "ws1mage" is his 1103 "test at the ws1Mage extremum", passed by fdm2\'s driver'),
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
    'L2_MOM_MAXTF': (30,    '"v4mom_maxTF = 12" - 1025, the lineage2 fork'),
    'L2_LIN_HOP':   (2,     '"lin_hop = 2" - 1025. Applies BETWEEN cadences only, his ruling'),
    'L2_T1_GRACE_S': (120,  '"the 2 minutes (CAUSALLY) following" - 1025, confirmed a knob'),
    'L2_T3_FRAC':   (0.75,  '"L2_T3_FRAC 0.75 survives" - 1026. Of the rider\'s matryoshka lines'
                            ' that reached EX-FENCE since the arm, not oob: "requiring lines to be'
                            ' oob excludes the lines that reached only ex-fence before reversing"'),
    'L2_T3_MIN_MATRY': (2,  '"use the >=2 applied to the lines that actually reversed" - 1026.'
                            ' t3 needs max(2, round(L2_T3_FRAC x the ex-fence population))'),
    'L2_ARM_RETEST': (1,    'BANKED ON. v4-arm-lineage-retest, Joe 1026: "let\'s add a'
                            ' `v4-arm-lineage-retest` mech that will fire at arm". His nine'
                            ' rulings are in v4_lineage2.md; 0 is the A/B arm'),
    'LIN2_BARRAGE_TOL_S': (70, 'MEASURED off his 2026-08-30 02:29 instance - the 02:27:50 cross'
                               ' to the 02:29:00 ws1r reversal. Not chosen, not swept'),
    'LIN2_BARRAGE_LINES': (6,  'MEASURED off the same instance - ws3,4,8,6,7,1 inside those 70 s.'
                               ' With the tolerance it cuts 204 LOW crosses to 8 instances'),
    'LIN2_BARRAGE_MIN_TF': (9, '*** UNRULED AND EMPTY AT 9. *** His 1027 definition is "the'
                               ' minimum TF allowed to contribute", a floor applied BEFORE the'
                               ' line count. At 9 the pool is ws9..ws12 (four lines) and'
                               ' LIN2_BARRAGE_LINES 6 cannot be met, so the mech fires NOTHING.'
                               ' His 9 was ruled against a membership reading - a different'
                               ' mechanic. (min_tf, lines) must be ruled together'),
    'LIN2_BARRAGE_MIN_TF_MODE': ('membership', 'the arm the pine emit and the banked 24-cadence'
                                               ' list were built on - one contributing line at or'
                                               ' above MIN_TF, count over ws1..12. HIS choice 1028'
                                               ' ("B"). The "floor" arm is HIS definition but is'
                                               ' EMPTY at MIN_TF 9 / LINES 6, so the pair must be'
                                               ' ruled before it can be the default'),
    'LIN2_PSEUDO_MIN_TF': (99, '99 = OFF. "bank this as the machine" - 1029 names the arm with'
                               ' the ex-fence latch ON and pseudo OUT. 4 is the other arm'),
    'LIN2_REV_FENCE': (40, 'HIS value and HIS words 1028: a LOW reversal counts only below 40, a'
                           ' HIGH only above 60. "lock it in". A THIRD fence - not oob (15/85) and'
                           ' not ex-fence (20/80). THE SCOPE IS UNRULED: no consumer reads it yet'),
    'LIN2_REV_FENCE_AT': ('confirm', 'the value at the bar the turn becomes KNOWABLE on - the'
                                     ' causal one. HIS ruling 1028 after both were measured.'
                                     ' "turn" is the hindsight reading'),
    'LIN2_BARRAGE_WIN_S': (0, 'the counting window is the ws1r reversal bar - the as-built'
                              ' behaviour, so nothing measured so far moves. His 1027 option A'
                              ' split it from the tolerance, which only ever meant to let ws1Mage'
                              ' and ws1r sync. THE VALUE IS UNRULED and comes off the sweep'),
    'LIN2_BARRAGE_FIT': ('off', 'neither of his two fits - a short pool fires nothing. THE BANKED'
                                ' ARM. lines = his "reduce the minimum required lines to fit them'
                                ' all inside the ws12cap"; cap = his "increase the ws12 cap to'
                                ' include the minimum required lines". The arm names are MINE'),
    'LIN2_BARRAGE_FENCE': ('any', 'no fence test on a contributing reversal - the banked behaviour'
                                  ' and what every measurement so far used. in/ex are the sweep'
                                  ' arms for his 1027 "sweep reversing infence vs reversing'
                                  ' exfence". The knob name and the arm names are MINE'),
    'LIN2_BARRAGE_ON': (1,  'BANKED ON, Joe 1027: "bank the barrage results and wire the mech into'
                            ' the chain". It fires as a CADENCE and that cadence EXHAUSTS - his'
                            ' "both - a cadence keeps the walk\'s transactions uniform, and'
                            ' exhaust will fire". 0 is the A/B arm'),
    'LIN2_MISMATCH_ACTION': ('rev-trade', '"make this a knob: rev-trade, or, close only (so that'
                                          ' reentry creates the next open)" - 1027, narrowed the'
                                          ' same day to the cws1b counter-oob cadence ONLY.'
                                          ' close-only stops the chain until v4_reentry is wired,'
                                          ' task 31'),
    'LIN2_MAE_CAP': (1.1,   '"if MAE > 1.1, cap mae at 1.1 and print 0 in mfe" - 1027. A'
                            ' stop-loss model in the REPORT only; it moves no decision'),
    'LIN2_CAND_NOT_REVERSED': (0, 'OFF is the bank. 1 = no reversal since the rider took the'
                                  ' baton, 2 = none since the arm. His 1027 "can we test it on the'
                                  ' day?" - the test arms, not a banked change. The wob is'
                                  ' LIN2_REV_WOB 12, which is MINE'),
    'LIN2_CASCADE_NO_ACTION': (0, 'BANKED OFF 1031 - "completely disable the mage cascade",'
                                 ' after it was shown owning 123 of 143 leg exits at -17.8102'
                                 ' summed and ending all 5 of the 0659 variants at their first'
                                 ' cadence. The verdict is still PRINTED as data. WAS (1, his'
                                 ' word 1027 - "bank it, and make the current'
                                 ' machine default". "if its verdict matches the trade direction then take'
                                 ' no action (ie keep walking)" - 1027. up = LONG, down = SHORT,'
                                 ' his "1, confirmed". neither is NOT suppressed - "let the cadence'
                                 ' decide"'),
    'LIN2_CROSS_WOB': (12,  '"add the wob12 to all crosses to ib and crosses to in-mom-fnc" -'
                            ' 1027. Five sites: t1, t2, the retest gate, and both pass-bar rules.'
                            ' Supersedes L2_CWS1R_WOB 1 on the retest cross and the "xwob 1" header'
                            ' ruling. Crosses INTO oob or ex-fence still carry no dwell'),
    'LIN2_COUNTER_OOB_ON': (0, 'BANKED OFF 1030 - "drop the opposing oob side forced exit".'
                               ' Its replacement is UNRULED, his own words. WAS (1, "create a'
                               ' cadence when cws1b crosses to counter'
                               ' target-side oob (eg 08-30 1921)" - 1026, "go" - 1027. Raw cross'
                               ' bar, no wob. 69 firings arm..exhaust over 08-30..09-03'),
    'LIN2_CAD_LATCH_ON': (1,    'BANKED ON. the 2-staged latch, Joe 1026: "I see a potential'
                            ' replacement for t3, and it\'s 2-staged latch"'),
    'LIN2_CHAIN_OPEN_ON': (1, 'HIS MECH - "the chain open should be on the ws5Mage oob" - 1029.'
                              ' ON: "should be" is a ruling. OFF keeps the handed-in first side'),
    'LIN2_CHAIN_OPEN_TF': (5, 'HIS LINE - ws5Mage - 1029'),
    'LIN2_CHAIN_OPEN_LOOKBACK_S': (300, 'HIS VALUE - "has been oob in the last 5 minutes" - 1029'),
    'LIN2_CHAIN_OPEN_XWOB': (1, 'MINE. The RAW ws1b cross. His "wob12 to all crosses" (1027)'
                                ' points at 12; raw is 0.8 min from his "2353" against 1.8'),
    'LIN2_CHAIN_OPEN_LINES': (2, 'HIS VALUE - "at least 2 higher TFs must be printing LOWER'
                                 ' values" - 1029. The band ws6..ws12 is mine'),
    'LIN2_BARRAGE_MAX_TF': (15, 'HIS VALUE - "barrage maxTF needs to increase, knob:15" - 1029.'
                                ' Barrage-only; L2_MOM_MAXTF stays 12. Sweep range [12-22] is his'),
    'LIN2_B1_HOLD': (0, 'HIS MECH - "if ws1b to ib has not qualified its wob 12, then its'
                        ' value is not passed in" - 1029. OFF until measured. At 12 it holds his'
                        ' 2026-08-30 00:59:25..01:20:45 low excursion together as one event'),
    'LIN2_LATCH_EXFNC_ON': (0, 'BANKED OFF 1101: "disable the latch.  I introduced it get'
                               ' around emerging". The chart-matched ex-fence read replaces it.'
                               ' WAS (1, HIS MECH, HIS KNOB NAME AND HIS BANK - "ADD'
                               ' LIN2_LATCH_EXFNC_ON" then "bank this as the machine", 1029)'),
    'LIN2_CP_EXFNC': ('closed_prev', 'BANKED 1101: "we will use closed_prev only for exiting'
                                     ' fences". "emerging" is the pre-1101 arm'),
    'LIN2_CP_OOB': ('emerging', 'BANKED at today\'s read 1101. He put oob in neither category and'
                                ' said "build for both options", so the bank moves no verdict and'
                                ' "closed_prev" is the arm'),
    'LIN2_CP_IB': ('emerging', 'BANKED 1101 on his gut - "my gut says emerging: create a knob that'
                               ' tests both options". "closed_prev" is the arm'),
    'FDM_RE_IB_XWOB': (1, 'the ib cross hold that closes the re-entry window. 1 is the cross bar itself, the same hold the cadence event uses on ws1b'),
    'FDM_RE_B_FNC': (5.0, 'gcws30b\'s own fence, 5 -> (5, 95), the smaller end per his 1103 convention. WAS 95.0'),
    'FDM_RE_WIN_OPEN': ('ws1b', 'HIS 1105 PURGE of the gcws30b clause: "purge \'--gcws30b is past the 5/95 fence, on either side\' from the reentry spec". WAS \'both\', banked 1103 on his "let\'s bank E, and make it the machine" - that arm opened where ws1b was oob AND gcws30b ex-5/95, and the 28-run sweep had it the only arm positive on 08-03 at +0.152% and tied best on 09-15 at +14.325%. The other settings are gcws30b, both, first and sameside'),
    'FDM_RE_WIN_CLOSE': ('ws1b', 'HIS 1103 "close the window on ws1b to ib". "gcws30b" is the arm it replaced'),
    'FDM_RE_REV_READ': ('closed_prev', 'BANKED 1104 - his "-use closed-prev" for the ws5 and ws6 reversals, overriding the standing rule that lift-off is the one emerging read. "emerging" is the arm it replaced'),
    'FDM_RE_WS5_FNC': (20.0, 'BANKED 1104 - his "if ws5r reverses while ex-20/80-fence". The smaller end of the pair, and its own knob so a sweep cannot move step 1\'s fence'),
    'FDM_RE_WS6_GATE': ('ex2080', 'BANKED 1104 - his "the ws6r gate might need to move from oob to ex-20/80-fence", then "that looks like our reentry mech". "oob" is the arm it replaced. The one cluster that moved: 2026-09-15 18:17, from -5.470% to -0.824%'),
    'FDM_RE_CLIMB': ('off', 'BANKED OFF - his 1104 probe "ride upwards through the TFs until you reach a tf showing the in fence r line". "value" reads each rung at one bar; "reversal" makes each ex-fence rung print its own reversal first'),
    'FDM_RE_CLIMB_HI': (12, 'the climb\'s ceiling, wsf\'s own top'),
    'FDM_RE_REV_TF': (5, 'the line whose reversal starts the walk. His spec is ws5; the knob exists for his 1104 "replace ws5 and ws6 with higher TFs"'),
    'FDM_RE_GATE_TF': (6, 'the line that gates the wait. His spec is ws6'),
    'FDM_RE_SCAN_FLOOR': ('gate', 'where the scan band starts: "gate" is the TF above the gate line, the mech\'s own shape; "ws13" is his "scan higher than ws12" read literally'),
    'FDM_RE_SCAN_LO': (7, 'the scan band\'s floor when FDM_RE_SCAN_FLOOR is a fixed TF rather than the gate + 1'),
    'FDM_RE_SCAN_HI': (12, 'the scan band\'s ceiling. wsf is ws1-ws12, his 1017 band names'),
    'FDM_RE_FIRE_IB': (1, 'BANKED 1104 - ws1b\'s ib close is in the last-to-fire set, his "out of ws5r reversing or ws6r reversal or ws1b crossing to ib". 0 drops it'),
    'FDM_FNC_2080': (20.0, 'HIS OWN KNOB NAME, "fdm-20-80-fnc", at his own value. Both the step-1 test and the reversal population read it; "ex" includes oob'),
    'FDM_M3_FNC': (25.0, 'HIS 1103 "ws3Mage is settled on 25/75". The knob name is mine; the value is his'),
    'FDM_M3_RESCUE_ON': (1, 'HIS 1103 MECH UPDATE - a cadence gated on ws3Mage staying infence is rescued when ws3r went oob and ws3Mage reached ex-40/60 in the gcws30b-to-ws1b window'),
    'FDM_M3_RESCUE_FNC': (40.0, 'HIS 1103 "IF ws3Mage was ex-40/60-fence during the window". Wider than the 25/75 it rescues'),
    'FDM_POP_LO': (3, 'HIS 1103 "ws3 to ws30 for both the cadence and the ws10x-cadence". The top comes from L2_MOM_MAXTF 30, not from a second knob'),
    'FDM_STEP1_ABOVE_TF': (3, 'HIS 1103 "above in timeframe" - step 1 scans ws4..ws30. STRICTLY above, so this knob is the excluded rung, not the floor'),
    'FDM_X10_WOB': (24, 'HIS 1103 RULING "now that we have the grade period, we can leverage a smaller wob: use 24". 36 is the other arm, from his own 1841 example'),
    'FDM_X10_FRM': ('cross', 'RULED 1103 - he read it marked #MINE in the as-built spec and said "your #MINE lines are all good". "confirm" is the arm'),
    'FDM_REV_FROM': ('event', 'HIS 1103 2-POLE ASK. "event" is the bank because every number so far was measured on it; "window" starts at the cadence event\'s ws1b excursion open and is unmeasured'),
    'FDM_X10_GRACE_PCT': (40.0, 'HIS OWN KNOB NAME, "fdm-ws10x-cad-grace", at his own value'),
    'FDM_X10_TRADE_PCT': (50.0, 'HIS VALUE ">=50%". The knob is mine - a stated threshold with no knob cannot be moved without an edit'),
    'FDM_X10_GRACE_MIN': (5.0, 'HIS VALUE "we add a 5 minute walk". The knob is mine. 5.0 min = 60 bars at the 5 s grid'),
    'FDM_MAE_CAP': (1.1, 'HIS 1103 "add the typical mae1.1 stop" + "yes, move it to default". ALWAYS ON, unlike LIN2_MAE_CAP which stayed behind W_MAE_CAP=on'),
    'FDM_RE_XCROSS_ON': (1, 'ON, his 1104 "let\'s make a small mod to the reentry". At 0 the re-entry walk is the 1104 banked one and every number before this mod is reproduced'),
    'FDM_RE_XWOB': (12, 'HIS VALUE "wob 12" = 60 s. Held apart from LIN2_CROSS_WOB 12, a different mechanic'),
    'FDM_RE_XCROSS_LO': (4, 'HIS 1105 "make ws4 the lowest TF". It is NOT tied to the trigger line - that floor was mine and it hid the ws4x cross at 2026-08-07 05:44:20 which is the only one in that stretch to pass all three of his gates'),
    'FDM_RE_XCROSS_TFS': ('band', 'HIS 1105 "I intentionally referd to `a TF`, so that you would see the dynamic nature of the mod" - every line from FDM_RE_REV_TF up to FDM_RE_SCAN_HI. WAS \'both\', two fixed waiting points. THE KNOB NAME AND THE BAND\'S TOP ARE MINE'),
    'FDM_RE_XCROSS_FNC_AT': ('stretch', 'HIS 1105 "there was no such ws4r is not past the 20 fence gate on the ws{a TF}x cross" - the fence is the state the line is in while waiting, read across the stretch from the window open to the cross. "cross" is the arm I had wrongly built'),
    'FDM_RE_XCROSS_UP_READ': ('closed_prev', 'his own example number "ws6r is 43" is the closed-prev value; emerging reads 40.79 there. THE READ IS MY CALL'),
    'FDM_CONF_READ': ('closed_prev', 'BANKED 1104 - his "make sure that closed-prev is the standard for everything except lift-off", the LATER of his two rulings for this table. "emerging" is the arm it replaced'),
    'FDM_CONF_BARS': ('event+x10', 'BANKED 1104 - the two data bars the machine owns, the cadence event and that event\'s ws10x race confirm. "event" is the narrower arm. THE KNOB NAME IS MINE'),
    'FDM_XCAD_ON': (1, 'ON, HIS 1104 "apply the update to the code so that ws10 does not interfere with the intention of the spec". At 0 the race pins ws10 and every banked fdm2 number is reproduced'),
    'FDM_XCAD_C2_SCOPE': ('tagged', 'HIS WORD "tagged" in the second clause. "board" tests every ex-20/80 line at the test bar instead. The report prints both verdicts; THE KNOB IS MINE'),
    'FDM_XCAD_RULE': ('B', 'HIS 1104 "unsure.  use B for now, we can change it to A if the data doesn\'t match my eye\'s verdict"'),
    'FDM_XCAD_ABOVE': (2, 'HIS OWN COUNT from the confluence rule, "the 2 lines above the highest TF". At 3 his 16:11:00 example produces no candidate'),
    'FDM_XCAD_EXF': (0, 'HIS 1104 "no" - the candidate line does not have to be ex-20/80 itself'),
    'FDM_XCAD_FRM': ('confirm', 'HIS 1104 "the conf bar". "cross" is the arm, 1 min 55 s earlier at his own example'),
    'FDM_XCAD_TAG_AT': ('event', 'HIS 1104 "tagged at the cadence event bar"'),
    'FDM_XCAD_REV_FROM': ('window', 'HIS 1104 "the target-side reversal must fire between the opening of the cadence window and the confirmed x-cross bar". It gates the reversal only; the extremum keeps the trade open as its anchor, and THAT reading is mine'),
    'FDM_XCAD_REV_TO': ('read', 'HIS 1104 CORRECTION "the window\'s end can\'t be the confirmed x-cross - that would mean the grace period has zero value". At "confirm" the turn count is frozen for the whole walk'),
    'FDM_XCAD_SEAM_S': (15.0, 'HIS VALUE "the next ws1 seam+15s". 15 s = 3 bars'),
    'FDM_XCAD_WALK_MIN': (10.0, 'HIS VALUE "walk forward 10 minutes". The shape is the grace walk he called "the established walk" - re-test every 5 s bar, break on the first pass'),
    'FDM_XCAD_FALLBACK': ('exfnc', 'HIS 1105 "scan the entire range for ex-20/80-fence lines instead. if any are found, the cadence verdict is keep on walking". "off" is the arm it replaced, where no candidate went straight to FDM_XCAD_NONE'),
    'FDM_XCAD_NONE': ('rev-trade', 'HIS 1104 "no candidates = rev-trade", validated against v4_fdm2.walk which already rev-trades when step 1 counts 0'),
    'FDM_SAV_ON': (0, 'OFF, HIS 1103 "we\'re dropping saviour for now". It was wired and measured: 2026-08-03 -1.051% -> -3.103% net, 2026-09-15 +7.316% -> -15.040%'),
    'FDM_SAV_READ': ('emerging', 'HIS 1103 "use emerging values, at the emerging ws1Mage extermum". "chart" is the other arm'),
    'FDM_SAV_TF_HI': (3, 'HIS 1103 "reduce the cascade to ws1-3". fdm2\'s own knob, not SAV_CASCADE_TF_HI, so the live machine keeps 12'),
    'FDM_SAV_MIN': (3, 'HIS 1103 "SAV_CASCADE_MIN 4 -> 3" - the arm that fired branch B at 2026-09-15 14:04:05. fdm2\'s own knob; SAV_CASCADE_MIN stays 4 for the live machine'),
    'FDM_SAV_ZOOM': (2, 'UNCHANGED FROM THE SHARED VALUE but held separately. Measured: at zoom 1 the 1356 LONG stays open at either min, because the ws2->ws3 step +1.6574 breaks the low cluster'),
    'FDM_SAV_ARM': (0, 'HIS 1103 "remove the armed gate". At 0 the ws5r walkback is skipped and ws5r is not read'),
    'LIN2_CP_LIFT': ('closed_prev', 'BANKED 1101 - "lift-off needs a close-p mode - it only reacts to full 1 minute bars". The t1 ws1r reversal BARS; it REVISES his earlier "keeping the lift-off on emerging" and gives up the 0445 reversals. _rev_pairs is not routed'),
    'LIN2_CP_WS1R': ('closed_prev', 'BANKED 1101 - "change ws1r to closed-p". The t1 r gate\'s VALUE read only; the reversal BARS stay emerging'),
    'LIN2_CP_GCWS30B': ('closed_prev', 'BANKED 1101 on his "yes" to routing gcws30b. It moves the t1 cadence AND the arm race - both read CL[\'g30b\']. "emerging" is the other arm'),
    'LIN2_CP_MIN_TF': (1, 'HIS RULE 1101, AS HE LEFT IT: "change ws1r to closed-p" moved the floor from 2 to 1, reversing the ws1 half of "ws1{any} and gcws1{any} stay on emerging". WAS (2, HIS RULE 1101: "ws1{any} and gcws1{any} stay on emerging (otherwise we'
                          ' lose the 09-03 0326 arm). all else is closed-prev". At 2 every ws1'
                          ' line is exempt. THE gcws HALF IS A READING OF MINE - no gcws1 line'
                          ' exists, so no sub-wsf line is routed at all'),
    'LIN2_LATCH_OOB_ON': (0, 'OFF, the banked arm. His 1029 ask to A/B it: "do a 08-30 chain AB'
                             ' test to validate or drop the oob latch". One latch read at depth,'
                             ' never a second latch'),
    'LIN2_CASC_REV_GATE_ON': (0, 'OFF is the bank - his 1030 mech, measured before it can'
                                ' be the default. The knob name is mine; he has not named'
                                ' the mech'),
    'LIN2_CASC_REV_GATE_HI': (4, 'his "ws1-4r". The knob name is mine, the floor is ws1'),
    'LIN2_MATRY_WSF_TAKEOVER_ON': (0, 'OFF is the bank - his 1030 mech, measured before'
                                      ' it can be the default. The _ON suffix is mine'),
    'LIN2_MATRY_WSF_TAKEOVER_TF': (7, 'HIS knob name and HIS value, written into his own'
                                      ' spec line as {knob:7}'),
    'LIN2_MATRY_WSF_TAKEOVER_AT': ('event', 'the cadence bar. "extremum" reads the'
                                            ' ws1Mage extremum instead - his "test both"'
                                            ' and NEITHER is ruled'),
    'LIN2_MATRY_WSF_SCAN_HI': (4, 'his "a scan from ws1 to ws4". The knob name is mine'),
    'LIN2_B1_OOB_DWELL': (0, 'the plain per-bar read - the bank, so nothing measured so'
                            ' far moves. His 1030 value is 12 bars = 60 s, after the'
                            ' 2026-08-30 22:22 trace showed cws1b entering the LOW oob'
                            ' four times in 85 s. Read by t1, t2, the arm and the'
                            ' counter-oob cadence, all through b1_beyond'),
    'LIN2_EXFNC_LATCH_REL': ('lift', 'the latched line\'s own lift-off and nothing else - his'
                             ' 1031 revision of the 1029 release line. WAS \'bank\' at the'
                             ' barrage plus the opposite-side clear, which is now the'
                             ' \'barrage\' arm and carries every pre-1031 latch figure.'
                             ' THE KNOB NAME IS MINE, the mech is his, and three choices'
                             ' inside the arm are mine and unruled - see the declaration'),
    'LIN2_EXFNC_LATCH_WOB': (4, 'HIS NAME AND HIS VALUE - "a small'
                                ' {knob:4,\'LIN2_EXFNC_LATCH_WOB\'} WOB" - 1029. Bars is mine'),
    'LIN2_T3_MIN_TF': (5,   'HIS NAME, HIS VALUE - "the rider between'
                            ' ws{knob:5,\'lin2_t3_min_tf\'} and ws12"'),
    'LIN2_CAD_LATCH_LIFE_S': (600, '"10 minutes (knob)" - 1026. How long latch 1 stays latched.'
                               ' Seconds. The value is his; the knob name is mine'),
    'LIN2_SUPPORT_LINES': (3, '"3 lines below the rider" - 1026. ALL of them must have reversed;'
                              ' his own reading named ws4, ws5, ws6 under a ws7 rider'),
    'LIN2_DIV_ON': (0, 'OFF, AND HIS 1101 WORD IS "divergence can be completely disabled". ws1r is the wrong line for the test - "ws1 works in small cycles that are not profitable" - and "ws3r seems to have more divergence potential (eyeballed)". ws3r is unbuilt. HIS knob'
                       ' name. At 0 the divergence runs only at the arm'),
    'LIN2_DIV_AT': ('cadence', 'the cadence bar itself, the pre-1101 behaviour. "extremum"'
                               ' anchors on the target-side ws1Mage extremum - his 1101'
                               ' proposal. NEITHER arm is ruled; the knob name is mine'),
    'LIN2_DIV_PM_FLOOR': (0.0, 'PM DISABLED - "it needs a floor that I don\'t have yet". HIS'
                               ' knob name. Declared and read by nothing, on purpose'),
    'LIN2_T1_B_IB_DWELL': (12, 'HIS 1101 ADDITION - "add a 1 minute minimum dwell on gcws30b ib" = 12 bars = 60 s. ADDITIVE to the wob 6. THE SIDE IS HIS WORD "ib" READ LITERALLY; a beyond-side minimum would be LIN2_B1_OOB_DWELL and would delete the 05:19:25 cadence rather than move it'),
    'LIN2_T1_B_FNC': (95.0, 'HIS 1101 SPEC REVISION - "I omitted the 5/95 requirement for gcws30b". t1\'s b read was oob 15/85 before this. At the ws1b arm it wants 85.0'),
    'LIN2_T1_B_LINE': ('gcws30b', 'HIS line, 1031 - ws1b is replaced by gcws30b. "ws1b" is the'
                                  ' pre-1031 arm. The knob name is mine'),
    'LIN2_T1_B_WOB': (6, 'HIS value - wob 6. Replaces LIN2_CROSS_WOB 12 for t1\'s b-line cross'
                         ' only; every other cross to ib keeps 12'),
    'LIN2_T1_R_FNC': (56.0, 'HIS value and his own {knob:56} notation - the r reversal gate\'s'
                            ' fence, mirrored to (44.0, 56.0), replacing the side-of-50 test'),
    'LIN2_T1_GRACE_AT': ('cross', 'the pre-1031 behaviour. He asked for an on/off knob and the'
                                  ' diff, so NEITHER arm is ruled'),
    'LIN2_ARM_B_LINE': ('gcws30b', 'HIS line, 1031 - gcws30b ex-5/95-fence replaces ws1b oob in'
                                   ' arm_race condition 2'),
    'LIN2_ARM_B_FNC': (95.0, 'HIS value - a 95/5 fence, mirrored to (5.0, 95.0), "at or beyond"'
                             ' his word'),
    'LIN2_ARM_B_WOB': (6, 'HIS value - the to-oob cross, the to-ib cross, and the dwell beyond'
                          ' the 5/95 fence'),
    'LIN2_ARM_WS3R_ON': (0, 'OFF - he bracketed ws3r in question marks, then said he is not'
                            ' convinced. ws2r is IN unconditionally'),
    'LIN2_BOARD_HOLD': ('linhop_exfnc', 'BANKED at his 1101 third arm - "if a line that is inside of lin-hop\'s reach is ex-fence, then walk to the next cadence". The arms are off, board_oob, board_oob_rev and linhop_exfnc; the names are mine, the four rules are his'),
    'LIN2_BOARD_OOB_HOLD': (1, 'HIS RULE 1101 - "the oob rule doesn\'t apply to a rider - it\'s a blanket rule across the board". No exhaust while any ws1..L2_MOM_MAXTF r is oob on the target side; the walk holds to the next cadence'),
    'LIN2_TOP_RESET_ON': (1, 'BANKED ON 1031 after the truncation test passed on the 08-14 0659'
                             ' walk. His "new trick"; the knob name is mine and the mech is'
                             ' unnamed. No limit on repeats, his own "yes"'),
    'LIN2_RELATCH_ON': (1, 'BANKED ON 1031 - his re-latch, with his candidate rule and his'
                           ' fall-back test both kept. The _ON suffix and the knob name are mine'),
    'LIN2_RIDER_JUMP': (8, 'HIS value and HIS mech, BANKED 1031 - "a riderTF can advance no more'
                           ' than 8 TFs" at a cadence marker, from a rider of 0 at the arm. It'
                           ' bounds the rider scan AND the cadence candidate scan. The name is'
                           ' mine'),
    'LIN2_CAD_TYPES': ('t1', 'no filter - every cadence the mechs produce is reviewed. His'
                              ' 1031 "test only at the t1 cadences" is a test arm, not a bank'
                              ' move. The knob name and the type strings are mine'),
    'LIN2_PASS':    ('ib',  'the bank - _pass_bars\' two rules. His 1031 asks for \'reversal\''
                            ' and \'reversal+quarter\' as tables, not as a bank move'),
    'LIN2_PASS_QUARTER': (0.25, 'HIS value, from his ws22 worked example. The knob name is mine.'
                                ' Only read when LIN2_PASS is \'reversal+quarter\''),
    'LIN2_REV_WOB': (12,    '"static wob12. noted, we\'ll keep the static" - 1026. THIS MECH ONLY;'
                            ' LIFT_WOB 8 is untouched. A seam-aligned dynamic wob kept ~25% fewer'
                            ' reversals and was slower on every one, measured 08-30..09-03'),
    'L2_T3_ON':     (0,     'BANKED OFF 1026 - "the old t3 is defunct". 1 is the A/B arm; 0 is the experiment arm he asked'
                            ' for on 1026 after its 24 events scored - 11 of the 24 fired with the'
                            ' rider already at cws12, where no pass is possible'),
    'L2_GATE_MODE': ('closed', '"move everything except reversal detection to closed bars" -'
                               ' 1026 FINAL. t3cadence\'s oob population gate'),
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


def oob_mask(a, side):
    """`oob` asked at EVERY bar of an array, in one pass. -> bool array.

    THE SAME RULE AS `oob`, ONE HOME. Joe 1026: *"whichever mech is deciding `oob` needs to receive
    the emerging values"* - which is a question about who hands it the number, and it exposed four
    places that had restated the comparison inline to vectorise it. A restated rule drifts the
    moment OOB_FNC or the boundary changes, so the vector form lives here beside the scalar one and
    the two cannot disagree.
    """
    import numpy as _np
    v = _np.asarray(a, float)
    return (v >= OOB_HI) if int(side) > 0 else (v <= OOB_LO)


def ib(v):
    """Is v in bounds."""
    return OOB_LO < float(v) < OOB_HI


def ex_fence(v, side):
    """Is v past the r fence on `side`."""
    lo, hi = fence()
    return (float(v) >= hi) if side > 0 else (float(v) <= lo)


def beyond_mask(a, side, lo, hi):
    """Is each bar of `a` at or beyond the (lo, hi) pair on `side`. -> bool array.

    THE GENERIC ONE. `oob_mask` is this at (OOB_LO, OOB_HI) and `ex_fence_mask` is this at
    `fence()`; both keep their own names because a caller naming the fence it means is the point.
    This exists for a third pair - his 1031 arm fence (5.0, 95.0), which is neither of those - and
    "AT OR BEYOND" is his own word for the comparison.
    """
    import numpy as _np
    v = _np.asarray(a, float)
    return (v >= float(hi)) if int(side) > 0 else (v <= float(lo))


def ex_fence_mask(a, side):
    """`ex_fence` asked at EVERY bar of an array, in one pass. -> bool array.

    THE SAME RULE AS `ex_fence`, ONE HOME - the sibling of `oob_mask` and for the same reason. The
    per-line ex-fence latch needs the fence state over a whole series to find its cross-in edges,
    and _pass_bars already had `np.array([K.ex_fence(x, side) for x in v], bool)` inline. A
    restated comparison drifts the moment RMOM_FNC moves, so the vector form lives here.
    """
    import numpy as _np
    lo, hi = fence()
    v = _np.asarray(a, float)
    return (v >= hi) if int(side) > 0 else (v <= lo)


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


def fnc_pair(fnc):
    """A fence knob's mirrored pair. -> (lo, hi). ONE HOME FOR HIS CONVENTION.

    HIS 1103 RULING: *"the way that I should be supplying a knob is (100 - {knob:15}), ie I use
    the smallest number to describe the fence's max"*. So a fence knob ALWAYS holds the SMALLER
    end, and hi is derived.

    WHAT IT PREVENTS. Before this, fence knobs stored opposite ends of the same kind of thing -
    FDM_FNC_2080 20.0 held the lower, FDM_RE_GATE_FNC 85.0 and RMOM_FNC 75.0 held the upper - and
    the mirror expression at each read site had to match its own knob. Writing a lower-end value
    into an upper-end site inverts the test and nothing errors: that voided the ws10x gate's first
    run, where RMOM_FNC 75.0 went into a lower-end formula and produced a fence near 50.

    THE ASSERT IS THE GATE, not the comment. A value above 50 is an upper-end number in a
    lower-end slot, which is the exact mistake this exists to catch.
    """
    f = float(fnc)
    assert 0.0 <= f <= 50.0, \
        ('a fence knob must hold the SMALLER end of its pair, his "(100 - {knob:15})" - got %r,'
         ' which is an upper-end value in a lower-end slot' % f)
    return f, 100.0 - f


def side_edge(fnc, side):
    """The edge a line must reach on `side` for a fence knob. -> float.

    `side` +1 high / -1 low. A HIGH side reads the pair's hi, a LOW side its lo.
    """
    lo, hi = fnc_pair(fnc)
    assert int(side) in (+1, -1), 'side is +1 high / -1 low'
    return hi if int(side) > 0 else lo


def lift_stamp(b):
    """The bar a lift-off at `b` becomes KNOWABLE. b + LIFT_WOB - 1, the last bar of the hold.

    jig.lift_off's own contract, 1022: *"A wob of n means the event is not KNOWABLE until
    bar + n - 1 ... This returns the lift-off bar ... the consumer adds the wob"*. Every consumer
    adds it HERE, so there is one copy of the arithmetic. At LIFT_WOB 8 the stamp is b + 7 bars
    = 35 s after the line left its extreme.
    """
    return int(b) + max(1, int(LIFT_WOB)) - 1


def cad_allowed(ty):
    """May the walk decide at a cadence of type `ty`. -> bool.

    ONE HOME for LIN2_CAD_TYPES. 'all' is the bank and passes everything.
    """
    want = str(LIN2_CAD_TYPES).strip()
    if want == 'all':
        return True
    return str(ty) in [x.strip() for x in want.split(',') if x.strip()]


def lin2_quarter_tf(tf):
    """Bars in LIN2_PASS_QUARTER of a timeframe's width, for lineage2's third pass mode. -> int.

    The sibling of `lin_quarter_tf`, kept separate because it reads lineage2's own knob. ws22 at
    0.25 is 66 bars = 330 s, which takes 07:56:00 to 08:01:30 - his worked example.
    """
    return max(1, int(LIN2_PASS_QUARTER * int(tf) * 12))


def lin_quarter_tf(tf):
    """Bars in LIN_PASS_QUARTER of a timeframe's width. -> int.

    int(0.25 x TF minutes) at the 5 s grid is 3 x TF bars. His ws22 example is 66 bars = 5.5 min,
    which takes 07:56:00 to 08:01:30. ONE HOME for the arithmetic, so the mode and any report of it
    cannot disagree.
    """
    return max(1, int(LIN_PASS_QUARTER * int(tf) * 12))


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
             'L2_T3_MIN_MATRY': 'matryoshka lines that reversed',
             'TRAJ_MIN_FRAC': 'fraction of the block', 'TRAJ_MIN_TRAVEL': 'r-points', 'SAV_WS2_OOB_TEST': 'minutes', 'SAV_IB_XWOB': 'bars',
             'SAV_MAGE_GATE_WOB': 'bars', 'SAV_CASCADE_GAP': 'bars',
             'LIN2_B1_HOLD': 'bars',
             'LIN2_LATCH_OOB_ON': 'on/off',
             'LIN2_CHAIN_OPEN_ON': 'on/off', 'LIN2_CHAIN_OPEN_TF': 'TF',
             'LIN2_CHAIN_OPEN_LOOKBACK_S': 'seconds',
             'LIN2_CHAIN_OPEN_XWOB': 'bars',
             'LIN2_CHAIN_OPEN_LINES': 'lines',
             'LIN2_BARRAGE_MAX_TF': 'TF', 'LIN2_EXFNC_LATCH_WOB': 'bars',
             'LIN2_LATCH_EXFNC_ON': 'on/off',
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
