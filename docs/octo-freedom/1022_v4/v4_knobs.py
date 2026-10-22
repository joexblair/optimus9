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
REV_WOB = _knob('REV_WOB', 3, int)        # bars a v4-lineage reversal must hold
IB_WOB = _knob('IB_WOB', 3, int)          # bars the ws5r ib cross must hold. SUPERSEDED for the
#   lineage ib cross by LIN_IB_DWELL below, and kept because it is his #10 ruling and the record of
#   what the static form was.
LIN_IB_DWELL = _knob('LIN_IB_DWELL', 2.5)  # bars per TF the lineage ib cross must hold, DYNAMIC.
#   Joe 1022: *"ok, we need a wob for lineage.  it needs to be dynamic: let's start with
#   int(TF * {knob:2.5, 'V4_LIN_IB_DWELL`})"*. WHY IT MOVED: on 2026-08-31 19:30:40 ws5r crossed to
#   ib at 16.25, reached 16.36 - 1.36 points past the fence - held THREE bars and fell straight back
#   to low oob and on down to 11.32. At the static IB_WOB 3 that flicker passed the hold on its last
#   bar and counted as ws5r walking to ib. int(5 * 2.5) = 12 bars rejects it.
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

# ── v4-ws5rbackstop ───────────────────────────────────────────────────────────────────────────
BSTOP_SYNC_MIN = _knob('BSTOP_SYNC_MIN', 8.8)        # minutes either side of the ws5r reversal that
#   the ws1r / ws2r / ws3r same-side oob may land in. Joe 1022: *"the ws1r,ws2r,ws3r oob condition
#   has a +/-8.8 minute window to sync with ws5r reversing.  this needs to be causal"*.
BSTOP_POOL_HI = _knob('BSTOP_POOL_HI', 3, int)       # the oob pool is ws1r..ws{BSTOP_POOL_HI}r

# ── lift-off ──────────────────────────────────────────────────────────────────────────────────
LIFT_PTS = _knob('LIFT_PTS', 6, int)        # samples in the window
LIFT_TOL = _knob('LIFT_TOL', 2.0)           # r-points off the window extreme
LIFT_WOB = _knob('LIFT_WOB', 8, int)        # bars the state must stay failed
GAP_PER_TF = _knob('GAP_PER_TF', 2.8)       # bars per TF-minute. PROVISIONAL until the sweep

BARS_PER_MIN = 12                           # the 5 s grid

#   name                value              Joe's words, 1022 unless dated
RULED = {
    'RMOM_FNC':         (80.0,  '"v4_rmom_fnc, default 80 - fence used when testing if a r is close'
                                ' enough to oob to be predicted"'),
    'LIN_HOP':          (2,     '"1, 2"'),
    'REV_WOB':          (3,     '"2, 3"'),
    'IB_WOB':           (3,     '"10, 3"' + ' - SUPERSEDED by LIN_IB_DWELL'),
    'LIN_IB_DWELL':     (2.5,   '"it needs to be dynamic: let\'s start with'
                                ' int(TF * {knob:2.5, `V4_LIN_IB_DWELL`})"'),
    'TF_CEILING':       (10,    '"18, unsure.  use 10" - PROVISIONAL'),
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


def past_mid(v, side):
    """Is v past the middle fence on `side`. high: v > MID_HI. low: v < MID_LO."""
    return (float(v) > MID_HI) if int(side) > 0 else (float(v) < MID_LO)


def gap_for(tf):
    """The lift-off sample gap for a timeframe, in bars. TF x GAP_PER_TF, rounded.

    Joe 1022 ruled the rounding: *"38, yes"* to round(). ws3 8.4 -> 8, ws7 19.6 -> 20.
    """
    return max(1, int(round(int(tf) * GAP_PER_TF)))


def lin_ib_dwell(tf):
    """The lineage ib dwell for a timeframe, in bars. int(TF * LIN_IB_DWELL), Joe's own formula."""
    return max(1, int(int(tf) * LIN_IB_DWELL))


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
    units = {'RMOM_FNC': 'r-points', 'LIN_HOP': 'TFs', 'REV_WOB': 'bars', 'IB_WOB': 'bars',
             'TF_CEILING': 'TF', 'LIN_IB_DWELL': 'bars per TF', 'SAV_WS2_OOB_TEST': 'minutes', 'SAV_IB_XWOB': 'bars',
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
