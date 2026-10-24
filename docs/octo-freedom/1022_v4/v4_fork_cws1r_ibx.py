"""A FORK, NOT LINEAGE. Joe 1024: *"we'll need a fork of lineage to play with - the idea I have is
different than anything we've built so far, so I don't want to make adjustents in lineage"*.

NOT YET NAMED by him, so this file is named for the lines it reads - the cws1r oob x ib cross - and
not for a coined mechanic. It imports nothing from `v4_fast` and changes nothing there.

HIS TARGET. Joe 1024: *"we're going to improve the 0137 timestamp. my target is the low side ws1r
reversal at 0129"*. On 2026-09-01 lineage's exhaust is 01:37:10; his target is 01:29.

HIS TEST, verbatim. Its opening clause was withdrawn by him on 1024 - *"it's best to delete that
statement so that it doesn't cause confusion"* - and is gone from this file rather than carried with
an annotation, which is what he asked for. The side rule below replaces it.

    from 08-31 2135, walk to the first cws1r oob x ib.
    -at that bar:  capture a cws1 anchored mage-cascade verdict
    -keep walking and testing mage cascade per bar
    -record when the verdict flips to flat, and when it flips to {opposite of the first anchor's
     verdict}

THE SIDE IS DERIVED, NOT ASSUMED. Joe 1024, after the 23:18 run picked a cross 78 minutes out:

    I assumed you would have a way to detect the timestamps side - that's on me. the way to find
    the source side is to lookback (from the timestamp) for the last ws1Mage oob - that will settle
    the confusion

So the SOURCE side is the side of the most recent ws1Mage oob at or before the start bar, and the
cws1r cross hunted is the one leaving the OPPOSITE side's oob run. He settled that by pointing at
the cross he expected: from 2026-08-31 23:18 the lookback finds a LOW ws1Mage oob at 23:15:55, and
the 23:31:00 cross he named left a HIGH oob run. It also agrees with the banked frame - a low-oob
source unwinds upward, and the high oob is what that move hunts.

THIS IS THE ONLY SIDE RULE IN THIS FORK. There is no second one to reconcile it against.

The lookback is UNBOUNDED, back to the tape start if it must. On his five starts it never needed
more than 2m05s, and three of the five timestamps are themselves a ws1Mage oob bar.

EMERGING OR CLOSED MAKES NO DIFFERENCE ON HIS FIVE. He wrote ws1Mage, so the lookback reads the
emerging line; the closed cws1Mage gives the same side on all five, with the oob bar differing by
25 s on one of them.

THREE READINGS ARE MINE AND STATED, none of them a number I invented:

    THE CROSS DWELL IS `SAV_IB_XWOB` 2 bars, and it is not a borrowed guess: that knob's own
    comment is *"bars the ws1r oob->ib cross must hold"*. Same line, same cross type, Joe's number.
    The bar acted on is the CONFIRM bar - `cross + xwob - 1` - which is `oob_ib_cross`'s contract.

    THE ANCHOR IS cws1Mage, re-derived AT EVERY BAR through `jig.mage_cascade_bar` in its
    'extrema' mode. That is what *"a cws1 anchored mage-cascade verdict"* names, and Joe 1017 set
    the producer: *"in our current state, the most recent mage extrema is captured from ws1Mage"*.
    Re-deriving per bar is what makes *"testing mage cascade per bar"* mean anything - the anchor
    moves when a new same-side extreme lands.

    THE LADDER IS THE EMERGING ws1Mage..ws12Mage SET, which is what every existing cascade consumer
    reads. Only the ANCHOR line is closed, because he wrote cws1. If he wants a closed ladder the
    lines are built and it is one argument.

NO END BAR IS CHOSEN HERE. The per-bar test runs to the window end and reports 'no flip' when it
never happens. A horizon would be a cap he has not specified.

CAUSAL ON THE CROSS, LOOKAHEAD ON THE WALK. The confirm bar is knowable at itself; the per-bar
cascade reads each bar at that bar. `mage_cascade_bar` asserts its own bar never exceeds the event.

usage: v4_fork_cws1r_ibx.py <out|-> <end> <'YYYY-MM-DD HH:MM:SS'> [more starts ...]
"""
import io
import os
import sys

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
import ln
import v4_knobs as K
import v4_core_arm as CA
import v4_signal as SG
_e = sys.stderr; sys.stderr = io.StringIO()
from optimus9.analysis.jig import mage_cascade, mage_cascade_bar, oob_ib_cross
sys.stderr = _e

OPP = {'up': 'down', 'down': 'up'}
FLAT = 'neither'


def source_side(line, bar):
    """The side of the most recent oob at or before `bar`. -> (the bar, the side) or (None, None).

    Joe 1024: *"the way to find the source side is to lookback (from the timestamp) for the last
    ws1Mage oob"*. oob is 15/85, always. No cap on the walk back - his standing rule.
    """
    v = np.asarray(line, float)
    for j in range(int(bar), -1, -1):
        if v[j] >= K.OOB_HI:
            return j, +1
        if v[j] <= K.OOB_LO:
            return j, -1
    return None, None


def _cascade_at(CM1, MG, bar, side):
    """The cws1Mage-anchored cascade at `bar`. -> (the anchor bar, the verdict) or (None, None)."""
    got = mage_cascade_bar(CM1, int(bar), int(side), mode='extrema')
    if got is None:
        return None, None
    ab = int(got[0])
    assert ab <= int(bar), 'the cascade anchor is past the bar it is read on'
    c = mage_cascade(MG, ab, zoom=K.SAV_CASCADE_ZOOM, min_lines=K.SAV_CASCADE_MIN)
    return ab, (None if c is None else c['verdict'])


def one(CL, EM1, MG, frm, B, log):
    """One of his start points. -> the row dict. The side is derived, never passed in."""
    r1 = np.asarray(CL['r'][1], float)
    CM1 = np.asarray(CL['M'][1], float)
    row = {'frm': int(frm)}
    sb, src = source_side(EM1, frm)
    if src is None:
        row['stage'] = 'no ws1Mage oob at or before the start'
        return row
    side = -int(src)                                   # the cross leaves the OPPOSITE oob run
    row.update({'src_bar': sb, 'src': src, 'side': side})
    xc = [(c, cf) for c, cf, s in oob_ib_cross(r1, K.OOB_HI, K.OOB_LO, K.SAV_IB_XWOB)
          if s == int(side) and cf >= int(frm)]
    if not xc:
        row['stage'] = 'no cws1r oob x ib cross on that side in the window'
        return row
    cross, conf = xc[0]
    row.update({'cross': int(cross), 'conf': int(conf)})
    ab, v0 = _cascade_at(CM1, MG, conf, side)   # the cascade anchor's side is the CROSS's
    row.update({'anchor0': ab, 'v0': v0})
    if v0 is None:
        row['stage'] = 'no cascade verdict at the confirm bar'
        return row

    flat = opp = None
    want = OPP.get(v0)
    trail = []
    for k in range(int(conf), int(B) + 1):
        a, v = _cascade_at(CM1, MG, k, side)
        if v is None:
            continue
        if not trail or trail[-1][2] != v:
            trail.append((k, a, v))                    # a VERDICT change. The anchor moving on its
            #   own is not a flip - he asked to record when the VERDICT flips, and the anchor steps
            #   almost every bar, which buried the three changes under hundreds of rows.
        if flat is None and v == FLAT:
            flat = k
        if want and opp is None and v == want:
            opp = k
        if flat is not None and (want is None or opp is not None):
            break
    row.update({'flat': flat, 'opp': opp, 'want': want, 'trail': trail})
    row['stage'] = 'measured'
    return row


def main(dest, B, starts):
    out = sys.stdout if dest == '-' else open(dest, 'w', buffering=1)

    def log(s):
        out.write(s + '\n')

    CL = CA.lines()
    MG = {t: ln.line('ws%dMage' % t) for t in range(1, 13)}
    EM1 = np.asarray(ln.line('ws1Mage'), float)

    log('# A FORK OF LINEAGE - cws1r oob x ib, then the cws1Mage-anchored cascade per bar.')
    log('# Joe 1024. the SIDE IS DERIVED: the last ws1Mage oob at or before the start gives the')
    log('#   SOURCE side, and the cws1r cross hunted leaves the OPPOSITE side\'s oob run.')
    log('# the cross dwell is SAV_IB_XWOB %d bars = %d s, acted on at the CONFIRM bar.'
        % (K.SAV_IB_XWOB, K.SAV_IB_XWOB * 5))
    log('# the cascade: zoom %d rungs, min_lines %d, ladder ws1Mage..ws12Mage EMERGING,'
        % (K.SAV_CASCADE_ZOOM, K.SAV_CASCADE_MIN))
    log('#   anchor cws1Mage CLOSED via mage_cascade_bar mode extrema. window ends %s.' % ln.U(B))
    log('# RULED_OK %s.' % K.RULED_OK)
    log('')
    rows = [one(CL, EM1, MG, ln.K(s), B, log) for s in starts]

    log('| the start | the last ws1Mage oob | source side | the cross side | the cws1r cross | '
        'its confirm | the anchor | the first verdict | flips to flat | flips to %s | the stage |'
        % '/'.join(sorted(OPP)))
    log('|---|---|---|---|---|---|---|---|---|---|---|')
    for r in rows:
        log('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |'
            % (ln.U(r['frm']),
               ln.U(r['src_bar']) if r.get('src_bar') is not None else '-',
               ('HIGH' if r['src'] > 0 else 'LOW') if r.get('src') else '-',
               ('HIGH' if r['side'] > 0 else 'LOW') if r.get('side') else '-',
               ln.U(r['cross']) if 'cross' in r else '-',
               ln.U(r['conf']) if 'conf' in r else '-',
               ln.U(r['anchor0']) if r.get('anchor0') is not None else '-',
               r.get('v0') or '-',
               ln.U(r['flat']) if r.get('flat') is not None else 'no flip',
               ('%s %s' % (r.get('want') or '-',
                           ln.U(r['opp']) if r.get('opp') is not None else 'no flip')),
               r['stage']))

    for r in rows:
        if r['stage'] != 'measured':
            continue
        log('')
        log('## %s - every verdict change from the confirm bar' % ln.U(r['frm']))
        log('')
        log('| the bar | the anchor | the verdict | s from the confirm |')
        log('|---|---|---|---|')
        for k, a, v in r['trail']:
            log('| %s | %s | %s | %+d |'
                % (ln.U(k), ln.U(a), v, (k - r['conf']) * 5))
    if dest != '-':
        out.close()


if __name__ == '__main__':
    main(sys.argv[1], ln.K(sys.argv[2]), sys.argv[3:])
