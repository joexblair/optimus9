"""THE MACHINE — the live chain, one entry point. 1013.

Joe 1013: *"make it the machine"* / *"I need full state in the live machine without needing multiple
versions of the same arg"* / *"the history is in the past for us now. the machine we're building now
is the only one"* / *"that live machine is what we will be continue our work on"*.

    python3 machine.py

NO ARGUMENTS, NO ENV VARS. The machine's config is declared below, in code. Every value that used to
be typed on a command line now lives here or in a moved default, because a run that forgot one
silently used a superseded mech - that is exactly what happened to the 2026-07-18 18:12:00 walk,
which armed on ws2Mage after Joe replaced it on 1011.

THE CHAIN, four links:

    1  the trade opens                      Joe's open mech, NOT SHARED YET
    2  the close event fires                `_ibmech`, the ws1Mage IB-cross mech
    3  the close is HELD and extended       `_extmom`, the momentum extension
    4  the last mile walks                  `_chain10` under W_ARM=lastmile

LINK 2 IS STILL DECLARED INPUT, NOT COMPUTED HERE. The four close bars below were produced by the
IB-cross walk banked in 2fa091e / ba38629, and wiring that walk into this entry point is the one
hand-stitch left. STATED so it is not mistaken for an end-to-end run.

LINK 3 IS COMPUTED. `_extmom.exit_bar` is called here, so the extension bar is no longer a literal.

THE FROZEN REFERENCE is asserted at the end. A regression fails this script rather than waiting to
be spotted in a table.
"""
import os
import sys

# THE MACHINE'S CONFIG, DECLARED. `setdefault` so a deliberate experiment can still override from
# the environment - and `_chain10`'s ruled gate will then refuse unless W_EXPERIMENT=1 as well.
os.environ.setdefault('W_ARM', 'lastmile')          # the walk is handed a live leg at the handoff
os.environ.setdefault('W_PASS', 'crossing_to_ib')   # the baton moves on the rider's oob -> ib cross
# W_CEIL 30, W_LOOP_TF 10, W_ARM_TF 1, LG_TAPE_END 2026-10-05 are now the moved DEFAULTS. They are
# not set here, on purpose: if a default drifts again the ruled gate catches it.

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import _chain10 as C
import _extmom as X

SC = C.SC
U = SC.U
N = C.N
PX = np.asarray(SC.PX, float)[:N]

# THE FOUR TRADES. (label, entry, the IB-cross close bar, dr)   dr +1 = SHORT, dr -1 = LONG.
TRADES = [
    ('07-17 21:58 LONG', '2026-07-17 21:58:00', '2026-07-18 01:15:20', -1),
    ('07-18 02:31 SHORT', '2026-07-18 02:31:00', '2026-07-18 10:40:40', +1),
    ('07-18 08:46 LONG', '2026-07-18 08:46:55', '2026-07-18 10:07:10', -1),
    ('07-18 16:07 LONG', '2026-07-18 16:11:10', '2026-07-18 16:38:15', -1),
]

# THE FROZEN REFERENCE, measured 1013 with every default in place and nothing passed.
FROZEN = {
    '07-17 21:58 LONG': (1.0517, 1.0821),
    '07-18 02:31 SHORT': (4.8615, 4.8337),
    '07-18 08:46 LONG': (0.3929, 0.4014),
    '07-18 16:07 LONG': (0.7967, 1.7205),
}
FROZEN_TOTAL = (7.1028, 8.0377)
TOL = 0.0002          # the 4-decimal printing precision, not a tolerance on the mech


def gross(e, x, dr):
    return (PX[e] - PX[x]) / PX[e] * 100.0 if dr > 0 else (PX[x] - PX[e]) / PX[e] * 100.0


def main():
    ws = (12, 15, 20, 30)
    dn = [k for k, _ in sorted(C.DWS_TF.items(), key=lambda kv: kv[1])]
    rows = [('ws%d' % t, C.MOMT[t]) for t in ws] + [(k, C.MOMD[k]) for k in dn]
    rn = X.ride_name()
    ride = SC.LDN(rn) if rn.startswith('dws') else SC.LD(X.TF * 60, 'r')
    em = X.ExtMom(rows, ride, C.BANK[X.TF], X.TF, C.EXF_HI, C.EXF_LO, N, C.STALL_N)
    C._P('the machine: extension on %s, n >= %d of %d, exit %r | last mile: kick cap ws%d, '
         'loopTF ws%s, lineage ceiling ws%d'
         % (rn, X.N_MIN, len(rows), X.EXIT, C.LASTMILE_KICK_TFCAP, C.LOOP_TF, C.LIN_CEIL))

    print()
    print('| trade | close event | n of %d | held? | extension fires | last mile ends | why | '
          'gross at the close | gross at the end | moved |' % len(rows))
    print('|---|---|---|---|---|---|---|---|---|---|')
    t0 = t1 = 0.0
    bad = []
    for lbl, ets, cts, dr in TRADES:
        e, c = SC.K(ets), SC.K(cts)
        board = dr                      # the close column's board is the FLIPPED dr
        n = em.n_at(c, board)
        xb, why_x = em.exit_bar(c, board)
        xb = c if xb is None else xb
        k, why, mae, cb, hand, tr = C.run_leg(xb, dr)
        kk = xb if k is None else k
        g0, g1 = gross(e, xb, dr), gross(e, kk, dr)
        t0 += g0
        t1 += g1
        print('| %s | %s | %d | %s | %s | %s | %s | %+.4f%% | %+.4f%% | %+.4f%% |'
              % (lbl, U(c), n, 'YES' if em.holds(c, board) else 'no', U(xb), U(kk),
                 str(why).replace('|', '·'), g0, g1, g1 - g0))
        f = FROZEN.get(lbl)
        if f is not None:
            if abs(g0 - f[0]) > TOL:
                bad.append('%s close gross %+.4f%%, frozen %+.4f%%' % (lbl, g0, f[0]))
            if abs(g1 - f[1]) > TOL:
                bad.append('%s end gross %+.4f%%, frozen %+.4f%%' % (lbl, g1, f[1]))
    print('| **TOTAL** | — | — | — | — | — | — | **%+.4f%%** | **%+.4f%%** | **%+.4f%%** |'
          % (t0, t1, t1 - t0))

    if abs(t0 - FROZEN_TOTAL[0]) > TOL:
        bad.append('TOTAL close gross %+.4f%%, frozen %+.4f%%' % (t0, FROZEN_TOTAL[0]))
    if abs(t1 - FROZEN_TOTAL[1]) > TOL:
        bad.append('TOTAL end gross %+.4f%%, frozen %+.4f%%' % (t1, FROZEN_TOTAL[1]))

    print()
    if bad:
        print('# FROZEN REFERENCE — %d MISMATCH(ES)' % len(bad))
        for b in bad:
            print('#   %s' % b)
        raise SystemExit('the machine moved against its frozen reference')
    print('# FROZEN REFERENCE — all %d figures match' % (len(FROZEN) * 2 + 2))


if __name__ == '__main__':
    main()
