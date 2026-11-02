"""THE fdm RE-ENTRY. Joe 1102: *"bank this and make it the reentry machine"*.

HIS SPEC, in the order he built it over 1101 and 1102:

    -IF there is no trade open (because of a STOP, or because of the machine starting)
    --IF gcws30b is ex-95/5-fnc                  <- the window OPENS here
    ---the window CLOSES when gcws30b returns to ib
    ---the gate is ws1r AND (ws2r or ws3r), each SEEN ex-v4mom-fence anywhere inside the window
    ---tested at the window's close. If the test is true, open a trade

WHAT EACH PIECE IS, and every one of them is his:

  the window's open   gcws30b at or beyond (100 - FDM_RE_B_FNC, FDM_RE_B_FNC) on the target side.
                      *"the reentry walk started at 0036 when gcws30b is high ex 5/95"*
  the window's close  `jig.oob_ib_cross` at the oob pair - THE BANKED MECH, not a value test. He
                      caught the difference: *"what mech are you using to detect this window's
                      close?  I see gcws30b "returning to ib" (the mech) at 0041"*. A bare
                      "under 95" test cut the 2026-08-03 stretch into four windows; the ib cross
                      gives ONE, closing 00:41:30, which he confirmed as his own read
  the gate            SEEN, not dwelling: *"the lines need to be seen in the window, but do not
                      need to dwell for the window's full range"*. Membership is recorded as the
                      walk passes each bar and never expires inside the window
  the fire bar        the close bar. *"tested at gcws30b window's close.  if the test is true,
                      open a trade"*
  the side            the oob side the lines were found on, his 1102 answer. `v4_signal.direction`
                      maps it to a trade and that mapping is banked: a HIGH oob side opens a SHORT

THE LINEAGE WALK IS GONE FROM THIS MECH. His 1101 draft had *"the highest TF is tagged as the
rider / follow the lineage walk (baton pass on rider to ib) / IF lineage prints exhaustion"*. On
1102 he dropped all three: *"drop the lineage walk. make the gate ws1r AND (ws2r or ws3r), tested
at gcws30b window's close"*. There is no rider here and no baton.

CAUSAL, AND THE ASSERTS CARRY IT. The open is a cross at its own bar. Membership is read at or
before the bar it is recorded on. The close is `oob_ib_cross`'s own confirm bar, which that
producer documents as the first bar the cross is KNOWABLE. The gate is evaluated at the close using
only bars from the open to the close.
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


def windows(G, side):
    """gcws30b's ex-fence windows on `side`. -> [(the open bar, the close bar)].

    The open is the first bar at or beyond the (lo, hi) pair after a bar that was not. The close is
    the CONFIRM bar of the next `oob_ib_cross` at the oob pair whose own cross bar is after that
    open - the banked mech, so the landing bar must be ib on BOTH sides strictly.

    A window with no ib cross after it is NOT returned: it has not closed, so it cannot fire.
    """
    g = np.asarray(G, float)
    hi = float(K.FDM_RE_B_FNC)
    lo = 100.0 - hi
    w = max(1, int(K.FDM_RE_IB_XWOB))
    beyond = (g >= hi) if int(side) > 0 else (g <= lo)
    crosses = [(int(c), int(cf)) for c, cf, s in oob_ib_cross(g, K.OOB_HI, K.OOB_LO, w)
               if int(s) == int(side)]
    out = []
    n = len(g)
    i = 1
    while i < n:
        if beyond[i] and not beyond[i - 1]:
            nxt = next(((c, cf) for c, cf in crosses if c > i), None)
            if nxt is None:
                break
            c, cf = nxt
            assert cf >= c, 'an ib cross confirm bar precedes its own cross bar'
            assert c > i, 'a window closes at or before it opens'
            out.append((i, cf))
            i = cf + 1
            continue
        i += 1
    return out


def signals(G, R, side=None):
    """Every fdm re-entry signal on the tape, bar-ordered. -> list of signals.

    `G` is gcws30b and `R` the r ladder keyed by timeframe, both handed in by the caller so this
    file holds no opinion about which read they came from. `side` runs both when None.
    """
    sides = (-1, +1) if side is None else (int(side),)
    fnc = float(K.FDM_RE_GATE_FNC)
    out = []
    for sd in sides:
        edge = fnc if sd > 0 else (100.0 - fnc)
        for o, c in windows(G, sd):
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
                                 'gcws30b %s window %s..%s, ws1r AND (ws2r or ws3r) seen past the'
                                 ' %.1f fence - %s - gate TRUE at the ib cross'
                                 % ('HIGH' if sd > 0 else 'LOW', SG.why_time(o), SG.why_time(c),
                                    edge,
                                    ', '.join('ws%d %s' % (t, SG.why_time(seen[t])) for t in got))))
    return sorted(out, key=lambda x: x['bar'])
