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


def _beyond(a, side, fnc):
    """Is `a` at or beyond the mirrored `fnc` pair on `side`. -> bool array."""
    x = np.asarray(a, float)
    hi = float(fnc)
    return (x >= hi) if int(side) > 0 else (x <= 100.0 - hi)


def _opens(B1, G, side):
    """The window's open bars on `side`, by FDM_RE_WIN_OPEN. -> int array.

    An open is the first bar the opening test holds after a bar it did not.

      'ws1b'      ws1b oob on `side`. THE BANK
      'gcws30b'   gcws30b beyond FDM_RE_B_FNC on `side`
      'both'      ws1b oob on `side` AND gcws30b beyond its fence on EITHER side
      'first'     whichever of those two holds
      'sameside'  both on `side`

    The last three are MINE - he asked whether other permutations exist and said to run them.
    """
    w1 = _beyond(B1, side, float(K.OOB_HI)) if int(side) > 0 else \
        (np.asarray(B1, float) <= float(K.OOB_LO))
    m = str(K.FDM_RE_WIN_OPEN)
    if m == 'ws1b':
        hold = w1
    else:
        assert G is not None, 'this window arm reads gcws30b and none was handed in'
        gs = _beyond(G, side, float(K.FDM_RE_B_FNC))
        ge = gs | _beyond(G, -int(side), float(K.FDM_RE_B_FNC))
        hold = {'gcws30b': gs, 'both': w1 & ge, 'first': w1 | ge,
                'sameside': w1 & gs}[m]
    return np.flatnonzero(hold[1:] & ~hold[:-1]) + 1


def windows(B1, side, G=None):
    """The re-entry windows on `side`. -> [(the open bar, the close bar)].

    The close is the CONFIRM bar of the closing line's oob->ib cross whose own cross bar is after
    the open - the banked mech, not a value test. FDM_RE_WIN_CLOSE picks the line, and gcws30b's
    cross is read at the oob pair, as it always was.

    A window with no closing cross after it is NOT returned: it has not closed, so it cannot fire.
    One window per close, so overlapping opens collapse onto the same close rather than firing
    twice - the walk resumes after each close.
    """
    w = max(1, int(K.FDM_RE_IB_XWOB))
    cl = str(K.FDM_RE_WIN_CLOSE)
    if cl == 'ws1b':
        L = np.asarray(B1, float)
    else:
        assert G is not None, 'this window arm closes on gcws30b and none was handed in'
        L = np.asarray(G, float)
    crosses = [(int(c), int(cf)) for c, cf, s1 in oob_ib_cross(L, K.OOB_HI, K.OOB_LO, w)
               if int(s1) == int(side)]
    out, used = [], -1
    for o in _opens(B1, G, side):
        if int(o) <= used:
            continue
        nxt = next(((c, cf) for c, cf in crosses if c > int(o)), None)
        if nxt is None:
            break
        c, cf = nxt
        assert cf >= c, 'an ib cross confirm bar precedes its own cross bar'
        assert c > int(o), 'a window closes at or before it opens'
        out.append((int(o), int(cf)))
        used = int(cf)
    return out


def signals(B1, R, side=None, G=None):
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
        for o, c in windows(B1, sd, G):
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
                                 '%s window %s..%s, %.1f min, opened on %s and closed on %s,'
                                 ' ws1r AND (ws2r or ws3r) seen past the %.1f fence - %s - gate'
                                 ' TRUE at the close'
                                 % ('HIGH' if sd > 0 else 'LOW', SG.why_time(o), SG.why_time(c),
                                    (c - o) * 5 / 60.0, K.FDM_RE_WIN_OPEN,
                                    K.FDM_RE_WIN_CLOSE, edge,
                                    ', '.join('ws%d %s' % (t, SG.why_time(seen[t])) for t in got))))
    return sorted(out, key=lambda x: x['bar'])
