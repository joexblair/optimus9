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

LINK 2 IS COMPUTED, 1013. Joe: *"close link 2"*. `_ibmech.IBMech.walk(open_bar, dr)` returns the
close bar, so it is no longer a literal. The four bars banked in 2fa091e / ba38629 are kept below as
the EXPECTED values and asserted - if the mech and the banked walk ever disagree, this says so
rather than quietly taking the mech's answer.

LINK 3 IS COMPUTED. `_extmom.exit_bar` is called here, so the extension bar is no longer a literal.

LINK 1 IS THE ONLY DECLARED INPUT LEFT: the trade's open bar and side. Joe has not shared the open
mech.

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
import _htfgate as HG
import _restart as RS
import _ibmech as IB

SC = C.SC
U = SC.U
N = C.N
PX = np.asarray(SC.PX, float)[:N]

# THE FOUR TRADES. (label, entry, the EXPECTED close bar, dr)   dr +1 = SHORT, dr -1 = LONG.
# The close bar is COMPUTED by _ibmech.walk; the value here is the banked one it is checked against.
TRADES = [
    ('07-17 21:58 LONG', '2026-07-17 21:58:00', '2026-07-18 01:15:20', -1),
    ('07-18 02:31 SHORT', '2026-07-18 02:31:00', '2026-07-18 06:34:30', +1),
    ('07-18 08:46 LONG', '2026-07-18 08:46:55', '2026-07-18 10:07:10', -1),
    ('07-18 16:07 LONG', '2026-07-18 16:11:10', '2026-07-18 16:38:00', -1),
    # ADDED 1013, Joe: *"re-freeze the reference and add both trades, for 10.2784%"*. These two are
    # the 07-18 chain's own links - each opens on the bar the one before it ended, so the chain from
    # 16:11:10 is now asserted end to end: 16:07 ends 18:12:00, 18:12 opens there and ends 18:45:15,
    # 18:45 opens there.
    ('07-18 18:12 SHORT', '2026-07-18 18:12:00', '2026-07-18 18:44:35', +1),
    ('07-18 18:45 LONG', '2026-07-18 18:45:15', '2026-07-18 20:05:40', -1),
]

# THE FROZEN REFERENCE, RE-FROZEN 1013. Joe: *"re-freeze the reference and add both trades, for
# 10.2784%"*.
# WHAT MOVED AND WHY. The ws30 mode fires on TWO trades, not the one I estimated: 07-17 21:58 LONG
# as well as 07-18 18:45 LONG. ws30 was mom-true toward 21:58's own board at its 01:15:20 close, so
# that trade now holds to 03:41:10 and ends at +1.3666% against the +1.0821% of the previous freeze.
# The gate caught it and refused to run rather than let the number drift - that is the whole point
# of it, and the re-freeze is Joe's call, taken here.
#     07-17 21:58 LONG   end  1.0821 -> 1.3666   the ws30 mode
#     the other three    end  unchanged
#     two trades ADDED   the 07-18 chain's own links
# RE-FROZEN AGAIN 1013 for W_IB_DWELL 2, Joe: *"bank, commit and push, make this machine live"*.
# Four of the six close events move with the dwell - 02:31 10:40:40 -> 06:34:30, 16:07 16:38:15 ->
# 16:38:00, 18:12 18:44:15 -> 18:44:35, 18:45 20:04:00 -> 20:05:40 - so TRADES' expected bars moved
# with them. Five of the six end figures move; only 18:45 is unchanged.
# RE-FROZEN 1013 FOR THIS LAP'S LOOP WORK, Joe: *"bank, commit and push. update docs. make this
# machine live"*. Two of the six moved and both gained, because the loop now fires on the loop
# line's own out-of-bounds state and the trade closes when the baton cannot move:
#     07-18 08:46 LONG   end  0.3934 -> 0.4014   the walk ends 10:20:05 -> 10:07:20
#     07-18 16:07 LONG   end  1.7205 -> 1.9325   the walk ends 18:12:00 -> 18:10:05
# The 16:07 move also breaks the 18:12 join he built on 1013 - leg 5 still opens 18:12:00, which is
# now 1.9 min after leg 4 ends. FLAGGED, his to rule.
FROZEN = {
    '07-17 21:58 LONG': (1.1199, 1.3945),
    '07-18 02:31 SHORT': (5.2666, 4.9508),
    '07-18 08:46 LONG': (0.3929, 0.4014),
    '07-18 16:07 LONG': (0.7967, 1.9325),
    '07-18 18:12 SHORT': (0.4362, 0.4083),
    '07-18 18:45 LONG': (1.4948, 1.5793),
}
FROZEN_TOTAL = (9.5071, 10.6667)
# RE-FROZEN AGAIN 1013 for the kickstart cap at ws7, Joe: *"let's fix the cap at 7"*. Two trades
# moved and both got worse - 02:31 +4.8337 -> +4.7703 and 08:46 +0.4014 -> +0.3934 - so the total
# fell +10.2783 -> +10.2069. HIS CALL, taken with the cost on the table; the gate caught all three
# mismatches before the re-freeze, as it is meant to.
TOL = 0.0002          # the 4-decimal printing precision, not a tolerance on the mech


def gross(e, x, dr):
    return (PX[e] - PX[x]) / PX[e] * 100.0 if dr > 0 else (PX[x] - PX[e]) / PX[e] * 100.0




def build():
    """The machine's live links, built once. -> (ib, em, rows, gate, restart)

    THE GATE IS BUILT HERE, 1013. It was ruled on 1013 and lived only in throwaway drivers until
    Joe asked *"does that mean we've baked and banked a mech that hasn't been applied globally?"*.
    It is built and returned so no caller has to make its own; it is NOT yet applied to the
    declared opens - that blocks the 07-18 08:46 LONG and rewrites the frozen reference, which is
    Joe's call.
    """
    ws = (12, 15, 20, 30)
    dn = [k for k, _ in sorted(C.DWS_TF.items(), key=lambda kv: kv[1])]
    rows = [('ws%d' % t, C.MOMT[t]) for t in ws] + [(k, C.MOMD[k]) for k in dn]
    rn = X.ride_name()
    ride = SC.LDN(rn) if rn.startswith('dws') else SC.LD(X.TF * 60, 'r')
    em = X.ExtMom(rows, ride, C.BANK[X.TF], X.TF, C.EXF_HI, C.EXF_LO, N, C.STALL_N)
    ib = IB.IBMech(SC)
    gate = HG.HTFGate(SC)
    # JOE 1013'S CHAIN RESTART. Built here so no caller makes its own.
    restart = RS.Restart(C.R, C.MOMT, C.MG1, C.oobf, C.LOOP_TF, SC.HI, SC.LO, N)
    C._P('link 2 live: IB-cross ceiling ws%d, cp dwell %d bars, IB wob %d bars, grace %d bars, '
         'g30 delegation %s at %d bars'
         % (IB.CEIL, IB.DWELL, IB.WOB, IB.REVWALK, 'ON' if IB.G30 else 'off', IB.G30BARS))
    C._P('the machine: extension on %s, n >= %d of %d, exit %r | last mile: kick cap ws%d, '
         'loopTF ws%s, lineage ceiling ws%d'
         % (rn, X.N_MIN, len(rows), X.EXIT, C.LASTMILE_KICK_TFCAP, C.LOOP_TF, C.LIN_CEIL))
    C._P('the HTF gate: lines ws%s, x/r pair ws%d, release %d bars then ws%dr IB, re-enable %d bars'
         % (', ws'.join(str(t) for t in HG.TFS), gate.x_tf, gate.wob, HG.IB_TF, gate.ren_wob))
    C._P('the chain restart: armed on ws%sr crossing INTO oob, ws1Mage in-fence > %d bars, '
         'ws%s away from the oob side'
         % (C.LOOP_TF, RS.MAGE_DWELL, ', ws'.join(str(t) for t in RS.AWAY_TFS)))
    return ib, em, rows, gate, restart


def chain(e, dr, ib, em, rows, gate=None):
    """THE WHOLE CHAIN FOR ONE OPEN. -> dict, or None at link 2.

        e    the open bar.   dr  +1 a SHORT, -1 a LONG.

    Link 2 the close event, link 3 the hold and extension, link 4 the last mile. Every bar is
    computed; the only input is the open. ONE function, so no caller can stitch a different mech
    into the middle of it - that substitution is what produced the wrong 18:12:00 answer on 1013.
    """
    board = dr                      # the close column's board is the FLIPPED dr
    own = -dr                       # the end the TRADE is heading to
    c, why_c, ib_rows = ib.walk(e, dr)
    if c is None:
        return {'open': e, 'dr': dr, 'close': None, 'why_close': why_c, 'ib_rows': ib_rows}
    n = em.n_at(c, board)
    held = em.holds(c, board)
    # JOE 1013'S ws30 MODE, link 3. When ws30 is mom-true toward the TRADE'S OWN board at the close
    # event, ws30 becomes the hold-and-ride line for THIS trade and the close fires at the first
    # target-side ws1cp-ib after ws30r goes oob - not at the dws10r stall. Joe: *"let ws30 fire the
    # hold and ride it"* / *"I think the `ws30 -> oob -> ws1cp-ib` flow is the best option for a
    # surgical way to use a line as wide as ws30"*.
    # The large-leg tests are NOT in this path - see 1013_large_leg_findings.md.
    ws30 = X.WS30 and em.ws30_aligned(c, own)
    ws30_bars = None
    if ws30:
        w = em.ws30_oob(c, own, C.R[30], SC.HI, SC.LO)
        cp2 = dec2 = None
        if w is not None:
            cp2, dec2, _v2 = ib.next_cp_ib(w, own)
        if dec2 is not None:
            xb, why_x = dec2, 'ws30 mode: ws30r oob %s, then the ws1cp-ib' % U(w)
            ws30_bars = (w, cp2, dec2)
        else:
            ws30 = False
    if not ws30:
        xb, why_x = em.exit_bar(c, board)
        xb = c if xb is None else xb
    _st = {}
    k, why, mae, cb, hand, tr = C.run_leg(xb, dr, state=_st)
    kk = xb if k is None else k
    # THE WALK'S EVENTS, for reporting only. No branch reads it.
    tr_all = [(b, str(t)) for b, t in tr]
    # THE oob HACK'S KEEP-GOING LAYER IS GONE. Joe 1013: *"the oob hack state changes do not have
    # any bearing on an open trade"* and, on the 2026-07-19 09:54:25 SHORT, *"11:04 closes the leg"*
    # with *"we must always honor the first event - if we don't honor the first, then we are not
    # causal"*. The layer existed only to override the first exhaustion; it overrode it 82 times on
    # that leg and carried it 55 minutes past its own close. Removed, not switched off.
    return {'open': e, 'dr': dr, 'close': c, 'why_close': why_c, 'ib_rows': ib_rows,
            'n': n, 'held': held, 'ext': xb, 'why_ext': why_x,
            'ws30': ws30, 'ws30_bars': ws30_bars, 'tr_all': tr_all,
            'end': kk, 'why_end': why, 'mae': mae, 'tr': tr,
            'gross_close': gross(e, c, dr), 'gross_ext': gross(e, xb, dr),
            'gross_end': gross(e, kk, dr)}


def main():
    ib, em, rows, gate, restart = build()

    print()
    print('| trade | close event | n of %d | held? | extension fires | last mile ends | why | '
          'gross at the close | gross at the end | moved |' % len(rows))
    print('|---|---|---|---|---|---|---|---|---|---|')
    t0 = t1 = 0.0
    bad = []
    for lbl, ets, cts, dr in TRADES:
        e = SC.K(ets)
        r = chain(e, dr, ib, em, rows)
        if r['close'] is None:
            bad.append('%s link 2 found no close event: %s' % (lbl, r['why_close']))
            continue
        if r['close'] != SC.K(cts):
            bad.append('%s computed close %s, banked %s' % (lbl, U(r['close']), U(SC.K(cts))))
        g0, g1 = r['gross_ext'], r['gross_end']
        t0 += g0
        t1 += g1
        print('| %s | %s | %d | %s | %s | %s | %s | %+.4f%% | %+.4f%% | %+.4f%% |'
              % (lbl, U(r['close']), r['n'], 'YES' if r['held'] else 'no', U(r['ext']),
                 U(r['end']), str(r['why_end']).replace('|', '·'), g0, g1, g1 - g0))
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
