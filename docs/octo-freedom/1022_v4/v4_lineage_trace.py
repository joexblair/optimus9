"""Trace v4-lineage's baton chain on one leg, to the depth the mech is confirmed to.

WHAT THIS IS AND IS NOT. It is NOT the v4-lineage walker - no walker exists, because #17 (the open
mech) is held back by Joe on purpose. It is the reproducible proof of the one piece he confirmed on
1022: the SECOND WALK TO IB that settles a baton-pass whose new rider has already reversed.

Run it and it reproduces the 2026-08-31 trace in v4_lineage.md SS5 line for line.

usage: v4_lineage_trace.py '2026-08-31 19:00:00' '2026-08-31 21:30:00' 5 low
"""
import sys
import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
import ln
import v4_knobs as K
from optimus9.analysis.jig import lift_off


def oob_run_rev(R, t, side, A, B):
    """the line's longest same-side oob run in [A, B] and its oob-anchored reversal.

    THE REVERSAL IS OOB-ANCHORED: a lift_off bar where the line IS oob, the same test the backstop
    applies. A lift-off outside the run is a different move and is not this run's reversal.
    """
    a = R[t]
    m = (a >= K.OOB_HI) if side > 0 else (a <= K.OOB_LO)
    d = np.diff(np.r_[False, m[A:B + 1], False].astype(np.int8))
    runs = [(int(s) + A, int(e) + A)
            for s, e in zip(np.flatnonzero(d == 1), np.flatnonzero(d == -1) - 1)]
    if not runs:
        return None, None
    s, e = max(runs, key=lambda q: q[1] - q[0])
    L = [int(b) for b in lift_off(a, side, K.LIFT_PTS, K.gap_for(t), K.LIFT_TOL, K.LIFT_WOB)
         if s <= b <= e and K.oob(a[b], side)]
    return (s, e), (L[0] if L else None)


def ib_cross(R, t, frm, B):
    """the first ib cross at or after `frm` holding int(TF x LIN_IB_DWELL) bars. -> (bar, held)"""
    a, need = R[t], K.lin_ib_dwell(t)
    k = int(frm)
    while k < B:
        if K.ib(a[k]):
            j = k
            while j + 1 < B and K.ib(a[j + 1]):
                j += 1
            if (j - k + 1) >= need:
                return k, j - k + 1
            k = j + 1
        else:
            k += 1
    return None, 0


def walk(R, start_tf, side, A, B, log=print):
    """The baton chain from `start_tf`. -> (the verdict, the bar, the rows).

    JOE'S 1022 RULE, verbatim in v4_lineage.md SS5. A rider that arrives with a reversal ALREADY in
    its lookback does not pass on that stale reversal: it walks to ib a SECOND time, and if the
    receiver of THAT pass is also already reversed, EXHAUST. His logic: *"the 2nd "walk to ib" gives
    enough time for a reversal to print without contention"*.

    CAUSAL: every reversal and every ib cross is read at or before the bar it is acted on.
    """
    REV, RUN = {}, {}
    for t in range(start_tf, K.TF_CEILING + 3):
        RUN[t], REV[t] = oob_run_rev(R, t, side, A, B)
    rows = []

    def say(step, bar, read):
        rows.append((step, bar, read))
        log('| %s | %s | %s |' % (step, bar, read))

    rid = start_tf
    if REV.get(rid) is None:
        say('ws%d has no oob-anchored reversal' % rid, '-', '-')
        return 'NO REVERSAL', None, rows
    say('ws%d is the rider and reverses' % rid, ln.U(REV[rid]),
        'ws%dr %.2f' % (rid, float(R[rid][REV[rid]])))
    pas, held = ib_cross(R, rid, REV[rid], B)
    if pas is None:
        say('ws%d never crosses to ib' % rid, '-', 'the chain cannot advance')
        return 'NO IB CROSS', None, rows
    say('ws%d walks to ib, dwell %d bars' % (rid, K.lin_ib_dwell(rid)), ln.U(pas),
        'held %d bars = %d s' % (held, held * 5))

    while True:
        nxt = rid + 1
        if nxt > K.TF_CEILING:
            say('ws%d is the TF_CEILING' % rid, ln.U(pas), 'EXHAUST')
            return 'EXHAUST', pas, rows
        if REV.get(nxt) is None:
            say('ws%d has no oob-anchored reversal' % nxt, ln.U(pas), 'EXHAUST')
            return 'EXHAUST', pas, rows
        if not K.ex_fence(R[nxt][pas], side):
            say('ws%d -> ws%d, the receiver gate' % (rid, nxt), ln.U(pas),
                'ws%dr %.2f, not ex-fence - EXHAUST' % (nxt, float(R[nxt][pas])))
            return 'EXHAUST', pas, rows
        say('ws%d -> ws%d, the receiver gate' % (rid, nxt), ln.U(pas),
            'ws%dr %.2f, ex-fence YES' % (nxt, float(R[nxt][pas])))
        stale = REV[nxt] <= pas
        say('ws%d takes the baton' % nxt, ln.U(pas),
            'its reversal %s, %s in its lookback'
            % (ln.U(REV[nxt]), 'FOUND' if stale else 'not yet'))
        if not stale:
            rid = nxt
            say('the normal path', ln.U(pas), 'ws%d waits for its own reversal' % rid)
            say('ws%d reverses' % rid, ln.U(REV[rid]), 'ws%dr %.2f' % (rid, float(R[rid][REV[rid]])))
            pas, held = ib_cross(R, rid, REV[rid], B)
            if pas is None:
                say('ws%d never crosses to ib' % rid, '-', 'the chain cannot advance')
                return 'NO IB CROSS', None, rows
            say('ws%d walks to ib, dwell %d bars' % (rid, K.lin_ib_dwell(rid)), ln.U(pas),
                'held %d bars = %d s' % (held, held * 5))
            continue
        # HIS RULE: the second walk to ib
        p2, h2 = ib_cross(R, nxt, pas, B)
        if p2 is None:
            say('the SECOND walk to ib on ws%d' % nxt, '-', 'it never crosses - the chain cannot advance')
            return 'NO IB CROSS', None, rows
        assert p2 >= pas, 'the second walk resolved before the baton-pass bar'
        say('the SECOND walk to ib on ws%d' % nxt, ln.U(p2),
            'dwell %d bars, held %d bars = %d s' % (K.lin_ib_dwell(nxt), h2, h2 * 5))
        n2 = nxt + 1
        if n2 > K.TF_CEILING or REV.get(n2) is None:
            say('ws%d has no successor' % nxt, ln.U(p2), 'EXHAUST')
            return 'EXHAUST', p2, rows
        if not K.ex_fence(R[n2][p2], side):
            say('ws%d -> ws%d, the receiver gate' % (nxt, n2), ln.U(p2),
                'ws%dr %.2f, not ex-fence - EXHAUST' % (n2, float(R[n2][p2])))
            return 'EXHAUST', p2, rows
        say('ws%d -> ws%d, the receiver gate' % (nxt, n2), ln.U(p2),
            'ws%dr %.2f, ex-fence YES' % (n2, float(R[n2][p2])))
        if REV[n2] <= p2:
            say('ws%d is the second-new-rider' % n2, ln.U(p2),
                'its reversal %s, FOUND in its lookback' % ln.U(REV[n2]))
            say('EXHAUST', ln.U(p2), 'the second-new-rider carried a reversal too')
            return 'EXHAUST', p2, rows
        say('ws%d is the second-new-rider' % n2, ln.U(p2),
            'its reversal %s, not yet in its lookback' % ln.U(REV[n2]))
        rid = n2
        pas, held = ib_cross(R, rid, REV[rid], B)
        if pas is None:
            say('ws%d never crosses to ib' % rid, '-', 'the chain cannot advance')
            return 'NO IB CROSS', None, rows
        say('ws%d walks to ib, dwell %d bars' % (rid, K.lin_ib_dwell(rid)), ln.U(pas),
            'held %d bars = %d s' % (held, held * 5))


if __name__ == '__main__':
    A, B = ln.K(sys.argv[1]), ln.K(sys.argv[2])
    tf, side = int(sys.argv[3]), (1 if sys.argv[4] == 'high' else -1)
    R = {t: ln.line('ws%dr' % t) for t in range(tf, K.TF_CEILING + 3)}
    print('# control ws5r 2026-09-03 00:35:00 = %.2f (ruled 12.48)'
          % ln.line('ws5r')[ln.K('2026-09-03 00:35:00')])
    print('# RULED_OK %s. ib dwell int(TF x %.1f), oob %.1f/%.1f, ex-fence %s, ceiling ws%d'
          % (K.RULED_OK, K.LIN_IB_DWELL, K.OOB_LO, K.OOB_HI, K.fence(), K.TF_CEILING))
    print()
    print('| the step | the bar | the reading |')
    print('|---|---|---|')
    v, b, _ = walk(R, tf, side, A, B)
    print()
    print('| the verdict | the bar |')
    print('|---|---|')
    print('| **%s** | %s |' % (v, ln.U(b) if b else '-'))
