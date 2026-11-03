"""THE fdm RE-ENTRY. Joe 1102: *"bank this and make it the reentry machine"*.

HIS SPEC AS IT NOW STANDS, after two 1103 rulings replaced gcws30b with ws1b:

    -IF there is no trade open (because of a STOP, or because the machine is starting)
    --IF ws1b crosses to oob                     <- the window OPENS here
    ---the window CLOSES when ws1b crosses back to ib
    ---the gate is ws1r AND (ws2r or ws3r), each SEEN ex-v4mom-fence anywhere inside the window
    ---tested at the window's close. If the test is true, open a trade

WHAT REPLACED WHAT, and both are his.

  1103, the close    *"make the window open on gcws30b ex-5/95, and close the window on ws1b to
                     ib"*. Before this, gcws30b's own ib cross closed it
  1103, the open     *"this table tells me that gcws30b is dangerous / replace gcws30b crossing to
                     ex-5/95 with ws1b crossing to oob"*. gcws30b is out of this mech entirely

WHAT THE TABLE SAID. Over the whole tape, 9538 gcws30b ex-5/95 opens on both sides, 2926 of them
with no ws1b oob inside 2 minutes - 30.7%. Of those 2926, 2142 were followed by a ws1r/ws2r/ws3r
oob on the event's own side at a MEDIAN LAG OF 0 s, so the r was already oob when gcws30b opened.
The 2026-09-15 14:00:00 HIGH open is the case he read it from: ws1r already 98.85 HIGH oob, and
ws1b stayed ib for 33 minutes before going oob at 14:33:00 - on the LOW side, the opposite way.

WHAT EACH PIECE IS, and every one of them is his:

  the window         ws1b's oob excursion on one side: the bar it crosses to oob, through to the
                     confirm bar of its oob->ib cross at FDM_RE_IB_XWOB
  the gate           SEEN, not dwelling: *"the lines need to be seen in the window, but do not
                     need to dwell for the window's full range"*. Membership is recorded as the
                     walk passes each bar and never expires inside the window
  the fire bar       the window's close. *"tested at gcws30b window's close.  if the test is true,
                     open a trade"* - the sentence survives its subject's replacement
  the side           the oob side the lines were found on, his 1102 answer, which is now ws1b's own
                     oob side. `v4_signal.direction` maps it and that mapping is banked: a HIGH oob
                     side opens a SHORT
  the long window    his 1103: *"a long running ws1b excursion is a sign of a trending leg that
                     hasn't stopped yet"*. NOTHING BOUNDS IT - the gate's membership span is the
                     whole excursion, however long

THE WINDOW IS NOW THE SAME SPAN AS THE CADENCE WINDOW, and that is worth stating plainly: both are
ws1b's oob excursion ending at its ib cross. The two mechs read DIFFERENT TESTS over it - the
cadence event needs the nestle and ws3Mage ex-25/75, the re-entry needs ws1r AND (ws2r or ws3r)
past the v4mom fence - and they fire for different reasons, one to decide an open trade and one to
open a trade from flat.

THE LINEAGE WALK IS GONE FROM THIS MECH. His 1101 draft had *"the highest TF is tagged as the
rider / follow the lineage walk (baton pass on rider to ib) / IF lineage prints exhaustion"*. On
1102 he dropped all three: *"drop the lineage walk. make the gate ws1r AND (ws2r or ws3r), tested
at gcws30b window's close"*. There is no rider here and no baton.

CAUSAL, AND THE ASSERTS CARRY IT. Membership is read at or before the bar it is recorded on. The
close is `oob_ib_cross`'s own confirm bar, which that producer documents as the first bar the cross
is KNOWABLE. The gate is evaluated at the close using only bars from the open to the close.
"""
import io
import sys

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
_e = sys.stderr; sys.stderr = io.StringIO()
try:
    import v4_knobs as K
    import v4_signal as SG
    import ln
    from optimus9.analysis.jig import oob_ib_cross
finally:
    sys.stderr = _e

MECH = 'fdm-reentry'


def windows(B1, side):
    """ws1b's oob excursions on `side`. -> [(the open bar, the close bar)].

    The open is the first bar ws1b is oob after a bar it was not. The close is the CONFIRM bar of
    that excursion's oob->ib cross at FDM_RE_IB_XWOB - the banked mech, not a value test.

    An excursion with no ib cross after it is NOT returned: it has not closed, so it cannot fire.
    His 1103 says that case is impossible, so it is the unreachable path rather than a branch.
    """
    b = np.asarray(B1, float)
    oob = (b >= K.OOB_HI) if int(side) > 0 else (b <= K.OOB_LO)
    w = max(1, int(K.FDM_RE_IB_XWOB))
    out = []
    for c, cf, s1 in oob_ib_cross(b, K.OOB_HI, K.OOB_LO, w):
        if int(s1) != int(side):
            continue
        j = int(c) - 1
        if j < 0 or not oob[j]:
            continue
        while j > 0 and oob[j - 1]:
            j -= 1
        assert j < int(c), 'a window closes at or before it opens'
        assert cf >= c, 'an ib cross confirm bar precedes its own cross bar'
        out.append((j, int(cf)))
    return out


def signals(B1, R, side=None):
    """Every fdm re-entry signal on the tape, bar-ordered. -> list of signals.

    `B1` is ws1b - the line whose oob excursion IS the window - and `R` the r ladder keyed by
    timeframe, both handed in by the caller so this file holds no opinion about which read they
    came from. `side` runs both when None.
    """
    sides = (-1, +1) if side is None else (int(side),)
    fnc = float(K.FDM_RE_GATE_FNC)
    out = []
    for sd in sides:
        edge = fnc if sd > 0 else (100.0 - fnc)
        for o, c in windows(B1, sd):
            seen = {}
            for tf in (1, 2, 3):
                a = np.asarray(R[tf], float)
                #   SEEN, not dwelling - his 1102 ruling. The slice ends at the close bar, so
                #   nothing after the bar the gate is evaluated on is read.
                hit = np.flatnonzero((a[o:c + 1] >= edge) if sd > 0 else (a[o:c + 1] <= edge))
                seen[tf] = (o + int(hit[0])) if len(hit) else None
                assert seen[tf] is None or seen[tf] <= c, 'a membership bar is after the close'
            if seen[1] is None or (seen[2] is None and seen[3] is None):
                continue
            got = [t for t in (1, 2, 3) if seen[t] is not None]
            out.append(SG.signal(c, sd, MECH, o,
                                 'ws1b %s oob window %s..%s, %.1f min, ws1r AND (ws2r or ws3r)'
                                 ' seen past the %.1f fence - %s - gate TRUE at the ws1b ib cross'
                                 % ('HIGH' if sd > 0 else 'LOW', SG.why_time(o), SG.why_time(c),
                                    (c - o) * 5 / 60.0, edge,
                                    ', '.join('ws%d %s' % (t, SG.why_time(seen[t])) for t in got))))
    return sorted(out, key=lambda x: x['bar'])
