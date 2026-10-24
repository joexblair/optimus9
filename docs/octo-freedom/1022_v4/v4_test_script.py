"""THE STANDALONE TEST-SCRIPT, Joe 1023. A faster EXHAUST than the lineage walk produces.

IT HAS NO NAME YET. Joe called it *"standalone test-script"*; naming a mech is his, so the file is
named after what it is and not after what it does.

WHY IT EXISTS. Joe 1023, on the 2026-09-01 01:16 leg: *"both EXHAUST times are ~0.8% past the low
pivot at 0130. this is our old nemesis: the slower the r, the more loss of profit."* And: *"I know
that ws4r reversal is accurate (enough) to a point where I'm not concerned about the small losses
between pxs pivot and ws4r reversing. what we need is a better method to create EXHAUST if ws4r has
a baton-pass candidate (ie ws5r)"*.

HIS SPEC, verbatim, indentation as he wrote it:

    after the ws4r reversal at 0116
    -after the next same-side of 50 ws1r reversal
    --at the next ws2Mage same-side oob
    ---print exhaust at the ws2MAge reversing, xwob 4

Read with his indentation rule - a deeper level nests INSIDE the one above - the four lines are a
sequence, each at or after the one before.

THE TWO FORKS HE RULED, 1023, and they are the defaults here:

    fork 1   *"_mage_rev(line, wob), via J.reversal"* for the ws2Mage reversing. NOT lift_off.
    fork 2   *"the same-side of 50: the ws1r value below 50. this aligns with the (invisible)
             SHORT's target-side"* - so the test is the VALUE against 50, via K.side_of.
    fork 2b  *"use the same reversal mech that lineage uses to detect reversals"* - so the ws1r
             reversal and the ws4r reversal are lift_off, through v4_fast.revs, exactly as lineage
             detects one. ONLY the ws2Mage step uses _mage_rev.
    the sign *"confirmed"* on *"the line turning back toward the middle - a LOW-side walk reverses
             up"*. `_mage_rev` gives +1 up-turn / -1 down-turn, so the sign is -side: a LOW-side
             walk takes +1, a HIGH-side walk -1.

ONE THING I CHOSE, STRUCTURAL, STATED RATHER THAN DEFAULTED QUIETLY:

    the start bar      his *"the ws4r reversal at 0116"* is the RAW bar 01:16:20. Every v4 caller
                       that ACTS on a reversal passes it through K.lift_stamp first, so the mech
                       starts at 01:16:55. The raw bar stays the instance's identity.

CAUSAL. Every bar the mech acts on is a stamp or an impulse bar computed from bars at or before it.
`lift_off` stamps are K.lift_stamp(raw); `_mage_rev` fires on the bar its run reaches wob. The
PIVOT is not an input - it is the scoring reference and it is found with lookahead, which is why it
is never read by any step.

usage: v4_test_script.py '2026-09-01 01:16:20' '2026-09-01 04:30:00'
"""
import sys
import io
import os
import json
import inspect

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
import ln
import v4_knobs as K
import v4_fast as F
import v4_rcfg_sweep as RS
from v4_backstop_trades import prices
_e = sys.stderr; sys.stderr = io.StringIO()
from optimus9.analysis.jig import px_smooth, lift_off, oob_ib_cross
from optimus9.analysis.lr_v2 import _mage_rev
from optimus9.compute.swing_detect import find_pivots
sys.stderr = _e

# ── the one knob his spec names, and it is his number ──────────────────────────────────────────
PIVOT_PCT = float(os.environ.get('W_TS_PIVOT_PCT', 0.50))   # UNRULED, and it is a SCORING knob -
#   no step reads it. ANCHORED TO A MEASUREMENT: Joe named *"the low pivot at 0130"*, and the first
#   LOW pivot at or after the 01:16:55 reversal stamp lands there only on px_smooth at 0.40% and
#   above - 01:31:15, 3 bars off his read - and it is the SAME bar at 0.40, 0.50, 0.75 and 1.00, a
#   plateau. On raw close every pct from 0.20 up answers 01:26:35, the raw-close low, which is not
#   his read; px_smooth at 0.15 and 0.20 answers 01:17:05, a 45 s wiggle. 0.50 is the middle of the
#   plateau, not a preference. Joe's to set.
EXH_STEP = os.environ.get('W_TS_EXH', 'ws2mage_rev')  # WHICH LINE AND EVENT PRINTS EXHAUST.
#   'ws2mage_rev' is his original 4th line, *"print exhaust at the ws2MAge reversing, xwob 4"*, and
#   stays the default. 'ws1mage_ib' is his 1023 test: *"ws4r rev -> ws1r rev -> ws2Mage oob ->
#   ws1Mage cross to ib"* - a DIFFERENT LINE on the last step, so a different producer, not a
#   different flavour of the same one. ws2Mage keeps step 3; ws1Mage only prints the exhaust.
G1_XWOB = int(os.environ.get('W_TS_G1_XWOB', 4))      # bars IB must hold for the ws1Mage cross.
#   Joe 0911, on ws1mage-rev: *"use these values, reversal:2, boundary:4. both are knobs"* - so 4
#   is his banked boundary hold, and it is kept as its OWN knob rather than borrowing M2_XWOB,
#   which is the ws2Mage reversal's hold and happens to share the value.
M2_DET = os.environ.get('W_TS_M2_DET', 'mage_rev')   # which producer detects the ws2Mage reversal.
#   'mage_rev' is Joe's fork-1 ruling and stays the default; 'lift_off' is his 1023 *"let's see the
#   chain on lift_off"*, run without moving the bank. The two read the same event through different
#   windows and their SIDE ARGUMENTS ARE NOT THE SAME SIGN:
#       lift_off   `side` says WHICH EXTREME to read. A HIGH-side walk reads the window HIGH, so
#                  side = +side, the walk's own side.
#       _mage_rev  the return sign says WHICH WAY the line turned. A HIGH-side walk turns DOWN, so
#                  sign = -side. Reading the high extreme and turning down are the same event.
M2_XWOB = int(os.environ.get('W_TS_M2_XWOB', 4))     # *"print exhaust at the ws2MAge reversing,
#   xwob 4"*. Bars of same-direction run _mage_rev needs before it confirms the turn. 4 = 20 s on
#   the 5 s grid. It is NOT K.LIFT_WOB 8 and it is NOT K.SAV_IB_XWOB 2 - a third wob, his number,
#   kept separate so moving one never moves another.


def instances(R, side, A, B):
    """THE RACE. Joe 1023: *"replace 'ws4r oob' with 'ws4r oob or ws5r oob, as a race'"*.

    -> a list of dicts, one per ws4r reversal whose oob support comes from EITHER line.

    WHY HE CHANGED IT, in his own numbers. On 2026-09-01 the ws5r HIGH oob run 03:11:00..03:17:25
    holds 78 bars; ws4r peaks at 83.10 inside it and never reaches the 85 fence, so 0 of 78 bars
    are ws4r oob while 78 of 78 are ws5r oob. Three ws4r reversals in that run - 03:13:00, 03:14:15
    and 03:17:15 - were thrown away by the ws4r-only test. Joe: *"the near ws4r miss at 0315 is
    supported by ws5 oob"*.

    THE REVERSAL IS STILL ws4r's. The race is between ws4r and ws5r for which one SUPPLIES the oob,
    and `won_by` records it, because which line carried the instance is data he will want.

    The detector is lineage's own - v4_fast.revs, which is lift_off with K.LIFT_PTS 6 samples,
    K.gap_for(4) bars between them, K.LIFT_TOL 2.0 r-points and K.LIFT_WOB 8 bars of hold. The oob
    test is on the SIGNAL, never on the detector: Joe 1023 *"the oob filter can't be applied to a
    reversal test"*.
    """
    out = []
    for b in F.revs(R[4], 4, side):
        b = int(b)
        if b < A or b > B:
            continue
        o4, o5 = K.oob(R[4][b], side), K.oob(R[5][b], side)
        if not (o4 or o5):
            continue
        out.append({'side': side, 'ws4r_raw': b, 'ws4r_stamp': K.lift_stamp(b),
                    'ws4r': float(R[4][b]), 'ws5r': float(R[5][b]),
                    'ws4r_oob': o4, 'ws5r_oob': o5,
                    'won_by': 'both' if (o4 and o5) else ('ws4r' if o4 else 'ws5r')})
    return out


def step_ws1r(R, side, frm, B):
    """*"after the next same-side of 50 ws1r reversal"*. -> (raw, stamp, value) or None.

    Lineage's detector (fork 2b), plus his fork-2 test: the ws1r VALUE on the same side of 50 as
    the walk, read through K.side_of, whose boundary ruling is its own (50 itself reads LOW).
    """
    for b in F.revs(R[1], 1, side):
        b = int(b)
        if b < frm or b > B:
            continue
        if K.side_of(R[1][b]) != side:
            continue
        return b, K.lift_stamp(b), float(R[1][b])
    return None


def step_ws2mage_oob(m2, side, frm, B):
    """*"at the next ws2Mage same-side oob"*. -> bar or None. oob is 15/85, always."""
    for b in range(int(frm), int(B) + 1):
        if K.oob(m2[b], side):
            return b
    return None


def step_ws2mage_rev(m2, mrev, side, frm, B):
    """*"print exhaust at the ws2MAge reversing, xwob 4"*. -> (bar, raw) or (None, None).

    `_mage_rev` is an IMPULSE, not a latch: it is non-zero only on the bar its signed run-length
    reaches wob, so the bar it fires on IS the event bar and the raw bar is that same bar.

    `lift_off` returns the RAW bar its at_extreme state first fails, and the state must then STAY
    failed for `wob` bars - so the bar the mech may act on is raw + wob - 1. That arithmetic uses
    M2_XWOB, NOT K.lift_stamp, because K.lift_stamp hardcodes K.LIFT_WOB 8 and this step's hold is
    Joe's xwob. Stamping with the wrong wob would claim a bar before the hold was proven.
    """
    if M2_DET == 'mage_rev':
        w = np.flatnonzero(mrev[int(frm):int(B) + 1] == -side)
        b = int(frm) + int(w[0]) if len(w) else None
        return b, b
    for raw in lift_off(m2, side, K.LIFT_PTS, K.gap_for(2), K.LIFT_TOL, M2_XWOB):
        raw = int(raw)
        if raw < int(frm):
            continue
        b = raw + M2_XWOB - 1
        return (b, raw) if b <= int(B) else (None, None)
    return None, None


def step_ws1mage_ib(g1x, side, frm, B):
    """*"ws1Mage cross to ib"*. -> (confirm bar, cross bar) or (None, None).

    `oob_ib_cross` is Joe's 0806 producer: it returns one tuple per oob -> ib crossing as
    (cross, confirm, side) where `cross` is the first IB bar, `confirm` = cross + xwob - 1 is the
    first bar the cross is KNOWABLE, and `side` is +1 if the run it LEFT was the high one. Only
    crosses leaving the walk's own side count, so a LOW-side walk wants side -1.

    The mech acts on `confirm`, never on `cross` - the IB hold is a knowledge delay, not lookahead.
    """
    for c, cf, sd in g1x:
        if c < int(frm) or sd != side:
            continue
        return (cf, c) if cf <= int(B) else (None, None)
    return None, None


def walk(R, m2, mrev, g1x, d, B):
    """One instance, his four steps in order. -> the instance dict, filled.

    NO PRICE ARGUMENT, ON PURPOSE - see the STAGE ONE / STAGE TWO guard in __main__.
    """
    side, stamp = d['side'], d['ws4r_stamp']
    s1 = step_ws1r(R, side, stamp, B)
    if s1 is None:
        d['stopped'] = 'no same-side-of-50 ws1r reversal'
        return d
    d['ws1r_raw'], d['ws1r_stamp'], d['ws1r'] = s1
    assert d['ws1r_stamp'] >= stamp, 'the ws1r step resolved before the ws4r reversal was knowable'
    ob = step_ws2mage_oob(m2, side, d['ws1r_stamp'], B)
    if ob is None:
        d['stopped'] = 'no same-side ws2Mage oob'
        return d
    d['m2_oob'], d['m2_oob_v'] = ob, float(m2[ob])
    assert ob >= d['ws1r_stamp'], 'the ws2Mage oob resolved before the ws1r reversal was knowable'
    if EXH_STEP == 'ws2mage_rev':
        d['exh'], d['exh_raw'] = step_ws2mage_rev(m2, mrev, side, ob, B)
    else:
        d['exh'], d['exh_raw'] = step_ws1mage_ib(g1x, side, ob, B)
    if d['exh'] is not None:
        assert d['exh'] >= ob, 'the ws2Mage reversal resolved before its own oob bar'
    d['stopped'] = None if d['exh'] is not None else (
        'no ws2Mage reversal towards the middle' if EXH_STEP == 'ws2mage_rev'
        else 'no ws1Mage oob -> ib cross on this side')
    return d


def lineage_exhaust(R, side, stamp, B):
    """The banked lineage walk from the SAME anchor and the same rung. -> (verdict, bar).

    This is the thing his spec is meant to beat, so it is run on the same anchor rather than
    quoted from another run.
    """
    return F.walk({t: R[t] for t in range(4, K.TF_CEILING + 3)}, 4, side, stamp, B)


def pivots(ps, pct):
    """Every px_smooth pivot, as (bar, kind). -> list. Cached by the caller."""
    return [(int(i), k) for i, k in find_pivots(np.asarray(ps, float), pct)]


def pivot(pv, side, frm):
    """The FIRST same-side px_smooth pivot at or after `frm`. -> bar or None.

    THE SCORING REFERENCE, NOT AN INPUT, and found with lookahead - which is why no step reads it.

    Joe 1023: *"the pivot we're targetting is 0130"*. px_smooth is what lows there, at 01:31:15;
    raw close lows five minutes earlier at 01:26:35, which is the series I had wrongly anchored to.
    A LOW-side walk takes the next 'L', a HIGH-side walk the next 'H'.

    THE FIRST VERSION OF THIS FUNCTION WAS WRONG AND THE WAY IT WAS WRONG MATTERS. It took the
    px_smooth extremum over the span from this instance's ws4r reversal to the NEXT instance's, and
    on the 01:16 leg that span reaches 02:23 and contains a LOWER low at 02:14:10. So it scored the
    mech against a pivot two moves later than the one Joe named, and reported +0.415% where his
    pivot gives +0.159%. A span I chose stood in for the pivot he named.
    """
    for b, k in pv:
        if b >= frm and k == ('L' if side < 0 else 'H'):
            return b
    return None


# ── THE STAGE GUARD. Joe 1023: *"confirm that the pivot is used only to validate the code? you're
#   riding the knife-edge if you already know the pivots - it can lead to seemingly helpful
#   additions to the mech that I don't know about"*.
#
#   An assert, not a promise. Every mech function is checked to take NO price-derived argument, so
#   a pivot cannot reach generation even by accident. The banked rule this enforces: bank the
#   causal timestamps first, score second, never feed scoring back into generation.
assert M2_DET in ('mage_rev', 'lift_off'), 'M2_DET %r is not a producer' % (M2_DET,)
assert EXH_STEP in ('ws2mage_rev', 'ws1mage_ib'), 'EXH_STEP %r is not a step' % (EXH_STEP,)
_PRICE_WORDS = ('close', 'px', 'ps', 'pv', 'piv', 'price', 'hi', 'lo', 'mae', 'mfe')
for _f in (instances, step_ws1r, step_ws2mage_oob, step_ws2mage_rev, walk, lineage_exhaust):
    for _a in inspect.signature(_f).parameters:
        assert not any(w in _a.lower() for w in _PRICE_WORDS), \
            '%s takes %r, which looks price-derived - STAGE ONE must not see price' % (_f.__name__, _a)


def stage_one(A, B):
    """Every instance and every EXHAUST bar, with NO price series in the process. -> rows.

    Nothing here can read a pivot: `prices`, `px_smooth` and `find_pivots` are not called, and the
    stage guard above asserts no mech function even has a parameter for one.
    """
    R = RS.load((RS.K0, RS.R0, RS.S0))
    m2 = ln.line('ws2Mage')
    mrev = np.asarray(_mage_rev(np.asarray(m2, float), M2_XWOB))
    g1x = oob_ib_cross(np.asarray(ln.line('ws1Mage'), float), K.OOB_HI, K.OOB_LO, G1_XWOB)
    F.reset()
    inst = sorted(instances(R, -1, A, B) + instances(R, +1, A, B), key=lambda d: d['ws4r_stamp'])
    for d in inst:
        walk(R, m2, mrev, g1x, d, B)
        d['lin_v'], d['lin_b'] = lineage_exhaust(R, d['side'], d['ws4r_stamp'], B)
    return R, inst


def stage_two(rows, A, B):
    """The scoring, on the bars STAGE ONE already banked. -> rows, each with its pivot."""
    close, _, _ = prices()
    PV = pivots(px_smooth(ln.ts, close), PIVOT_PCT)
    for d in rows:
        d['pv'] = pivot(PV, d['side'], d['ws4r_stamp'])
    return close


if __name__ == '__main__':
    A, B = ln.K(sys.argv[1]), ln.K(sys.argv[2])

    R, rows = stage_one(A, B)                       # no price loaded yet, by construction
    bank = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out', 'test_script_bank.json')
    os.makedirs(os.path.dirname(bank), exist_ok=True)
    with open(bank, 'w') as fh:                     # the timestamps are BANKED before scoring
        json.dump([{k: v for k, v in d.items() if k != 'pv'} for d in rows], fh, indent=1)
    close = stage_two(rows, A, B)                   # scoring reads the banked rows only

    print('# THE STANDALONE TEST-SCRIPT, Joe 1023. %s .. %s (his cap)' % (ln.U(A), ln.U(B)))
    print('# THE RACE: an instance is a ws4r reversal with *"ws4r oob or ws5r oob, as a race"*.')
    print('# the EXHAUST step is %r. fork 2 the ws1r VALUE vs 50, K.side_of.' % EXH_STEP)
    if EXH_STEP == 'ws1mage_ib':
        print('# step 4 is ws1Mage oob -> ib via oob_ib_cross, xwob %d. ws2Mage still owns step 3.'
              % G1_XWOB)
    else:
        print('# the ws2Mage reversal detector is %r, xwob %d.' % (M2_DET, M2_XWOB))
    if M2_DET != 'mage_rev':
        print('# NOT fork 1. Joe ruled _mage_rev; this run is his *"let\'s see the chain on')
        print('#   lift_off"*. The bank has NOT moved.')
    print('# fork 2b ws4r and ws1r reversals are lineage\'s own detector, v4_fast.revs = lift_off.')
    print('# the control: ws5r 2026-09-03 00:35:00 = %.2f (the BANKED k6 rsi8 stc6 line; the'
          % R[5][ln.K('2026-09-03 00:35:00')])
    print('#   DB-ruled line reads 12.48 there - the pair is the drift check, not a mismatch).')
    print('# RULED_OK %s. STAGE ONE banked %d instances to out/test_script_bank.json with no price'
          % (K.RULED_OK, len(rows)))
    print('#   series loaded; the PIVOT is find_pivots on px_smooth at %.2f%%, UNRULED, and it is'
          % PIVOT_PCT)
    print('#   read only in STAGE TWO. The stage guard asserts no mech function can take it.')
    print()

    print('| the read | value |')
    print('|---|---|')
    print('| instances - ws4r reversals winning the race | %d |' % len(rows))
    print('| of those, LOW side | %d |' % sum(1 for d in rows if d['side'] < 0))
    print('| of those, HIGH side | %d |' % sum(1 for d in rows if d['side'] > 0))
    for w in ('ws4r', 'ws5r', 'both'):
        print('| the race won by %s alone | %d |' % (w, sum(1 for d in rows if d['won_by'] == w)))
    print('| instances that printed EXHAUST | %d |' % sum(1 for d in rows if d.get('exh')))
    print()

    for d in rows:
        side = d['side']
        print('## the ws4r reversal %s, %s side, race won by %s'
              % (ln.U(d['ws4r_raw']), 'LOW' if side < 0 else 'HIGH', d['won_by']))
        print()
        print('| the step | the bar | the reading |')
        print('|---|---|---|')
        print('| ws4r reverses | %s | ws4r %.2f oob %s, ws5r %.2f oob %s, knowable %s |'
              % (ln.U(d['ws4r_raw']), d['ws4r'], d['ws4r_oob'], d['ws5r'], d['ws5r_oob'],
                 ln.U(d['ws4r_stamp'])))
        if 'ws1r_raw' in d:
            print('| the next ws1r reversal, same side of 50 | %s | ws1r %.2f, side %+d, knowable %s |'
                  % (ln.U(d['ws1r_raw']), d['ws1r'], K.side_of(d['ws1r']), ln.U(d['ws1r_stamp'])))
        if 'm2_oob' in d:
            print('| the next ws2Mage same-side oob | %s | ws2Mage %.2f |'
                  % (ln.U(d['m2_oob']), d['m2_oob_v']))
        if d.get('exh') is not None and EXH_STEP == 'ws1mage_ib':
            print('| **EXHAUST, ws1Mage crosses to ib** | **%s** | left the %s oob side, cross %s,'
                  ' ib held %d bars |'
                  % (ln.U(d['exh']), 'HIGH' if side > 0 else 'LOW', ln.U(d['exh_raw']), G1_XWOB))
        elif d.get('exh') is not None:
            if M2_DET == 'mage_rev':
                print('| **EXHAUST, ws2Mage reversing xwob %d** | **%s** | _mage_rev sign %+d,'
                      ' towards the middle |' % (M2_XWOB, ln.U(d['exh']), -side))
            else:
                print('| **EXHAUST, ws2Mage reversing xwob %d** | **%s** | lift_off side %+d, raw'
                      ' %s, hold %d bars proven |'
                      % (M2_XWOB, ln.U(d['exh']), side, ln.U(d['exh_raw']), M2_XWOB))
        print('| the banked lineage walk from the same anchor | %s | %s from ws4 |'
              % (ln.U(d['lin_b']) if d['lin_b'] is not None else '-', d['lin_v']))
        if d['stopped']:
            print('| the chain stopped | - | %s |' % d['stopped'])
        print()

    def pc(b, pv):
        if b is None or pv is None:
            return None
        p0 = float(close[pv])
        return (float(close[b]) - p0) / p0 * 100.0

    print('## the scoring - STAGE TWO, on the banked bars')
    print()
    print('| the ws4r reversal | side | won by | the pivot | EXHAUST, this mech | %% off the pivot |'
          ' lineage EXHAUST | %% off the pivot | earlier by |')
    print('|---|---|---|---|---|---|---|---|---|')
    gap = []
    for d in rows:
        pv, e, lb = d['pv'], d.get('exh'), d['lin_b']
        pe, pl = pc(e, pv), pc(lb, pv)
        if e is not None and lb is not None:
            gap.append((lb - e) * 5)
        print('| %s | %s | %s | %s | %s | %s | %s | %s | %s |'
              % (ln.U(d['ws4r_raw']), 'LOW' if d['side'] < 0 else 'HIGH', d['won_by'],
                 ln.U(pv) if pv is not None else '-',
                 ln.U(e) if e is not None else d['stopped'],
                 ('%+.3f%%' % pe) if pe is not None else '-',
                 ln.U(lb) if lb is not None else d['lin_v'],
                 ('%+.3f%%' % pl) if pl is not None else '-',
                 ('%+d s' % ((lb - e) * 5)) if (e is not None and lb is not None) else '-'))
    print()

    both = [d for d in rows if d.get('exh') is not None and d['lin_b'] is not None and d['pv']]
    print('| the summary | value |')
    print('|---|---|')
    print('| instances | %d |' % len(rows))
    print('| instances where both this mech and lineage printed EXHAUST | %d |' % len(both))
    if both:
        me = np.array([abs(pc(d['exh'], d['pv'])) for d in both])
        li = np.array([abs(pc(d['lin_b'], d['pv'])) for d in both])
        print('| this mech, distance off the pivot, mean of %d | %.3f%% |' % (len(both), me.mean()))
        print('| lineage, distance off the pivot, mean of %d | %.3f%% |' % (len(both), li.mean()))
        print('| this mech closer on | %d of %d |' % (int((me < li).sum()), len(both)))
        g = np.array(gap)
        print('| the mech is earlier by, median | %+d s |' % int(np.median(g)))
        print('| the mech is earlier by, min | %+d s |' % int(g.min()))
        print('| the mech is earlier by, max | %+d s |' % int(g.max()))
    for why in sorted({d['stopped'] for d in rows if d['stopped']}):
        print('| instances that stopped: %s | %d |' % (why, sum(1 for d in rows if d['stopped'] == why)))
