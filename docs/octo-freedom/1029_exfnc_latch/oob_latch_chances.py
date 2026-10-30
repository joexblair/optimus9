"""EVERY BAR WHERE THE oob LATCH COULD HAVE DECIDED ANYTHING. Joe 1029 chose arm C.

The rider's hold-against-exhaust test at a cadence is:

    oob true                                    -> HOLD
    oob false, latched ex-fence, not reversed   -> HOLD
    oob false, latched ex-fence, REVERSED       -> fall through to the exhaust

So the oob read can only change an outcome at a cadence bar where the rider HAS reversed. Anywhere
else the ex-fence latch has already taken the hold, whatever oob says.

THIS WALKS EVERY LEG and lists, per cadence bar the walk evaluated, the rider, whether it had
reversed, what the two oob reads said, and whether the two disagree. A row where the rider reversed
AND the reads disagree is a chance the mech had. Any other row is not.

It prints the whole 2026-08-30 chain and then the same count over 2026-08-30..09-06, so the
decision to run the wider A/B rests on a number.
"""
import os, sys, io, time
import numpy as np
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln, v4_knobs as K, v4_rcfg_sweep as RS
import v4_live_lines as LL, v4_l2_proxy as PX, v4_chain as CH
import v4_signal as SG, v4_sig_lin2_reentry as L2R
from v4_backstop_trades import prices
sys.stderr = _e
T0 = time.time()

close, phi, plo = prices()
E = RS.load((RS.K0, RS.R0, RS.S0))
CL = LL.arm_lines(E)
MG = LL.mage(12)
B1 = np.asarray(CL['b'], float)
SIG = [g for g in L2R.signals(B1, MG) if g['bar'] == ln.K('2026-08-29 23:53:50')]
assert len(SIG) == 1
OPEN_DIR = SG.direction(int(SIG[0]['side']))
OPEN = (SG.fire_bar(SIG[0]), SG.target_side(OPEN_DIR))
ALLSIG = L2R.signals(B1, MG)
CADENCE_TYPES = ('t1', 't2', 'barrage', 'cws1b counter-oob', 'retest')

print('# EVERY CHANCE THE oob LATCH HAD TO DECIDE ANYTHING')
print('# the rider oob read can only change an outcome at a cadence where the rider HAS reversed.')
print('# everywhere else the ex-fence latch has already taken the hold, whatever oob says.')
print('# a CHANCE is a cadence bar where the rider reversed AND the two oob reads disagree.')
print('')


def scan(A, B, label, per_row):
    K.LIN2_LATCH_OOB_ON = 0
    bd = PX.Board(E, E, MG=MG, MGE=MG, PS=None)
    lg, zero, op = CH.legs(CL, bd, close, phi, plo, A, B, MG=MG, B1=B1, open_at=OPEN,
                           resig=ALLSIG)
    rows, n_cad, n_rev, n_dis, n_chance = [], 0, 0, 0, 0
    for i, x in enumerate(lg, 1):
        side = x['side']
        for r in x['rows']:
            b, rd = r.get('bar'), r.get('rider')
            if b is None or rd is None:
                continue
            if str(r.get('ctype') or '') not in CADENCE_TYPES:
                continue
            n_cad += 1
            revd = bool(bd.reversed_in(rd, side, int(x['opn']), int(b)))
            K.LIN2_LATCH_OOB_ON = 0
            ov = bool(bd.baton_oob(rd, b, side))
            K.LIN2_LATCH_OOB_ON = 1
            od = bool(bd.baton_oob(rd, b, side))
            K.LIN2_LATCH_OOB_ON = 0
            if revd:
                n_rev += 1
            if ov != od:
                n_dis += 1
            ch = revd and ov != od
            if ch:
                n_chance += 1
            rows.append((i, b, rd, side, revd, ov, od, ch, r['stage']))
    print('## %s' % label)
    print('')
    if per_row:
        print('| leg | the cadence bar | the rider | its value | had it reversed? |'
              ' oob by value | oob at depth | the reads disagree? | A CHANCE? | the stage |')
        print('|---|---|---|---|---|---|---|---|---|---|')
        for i, b, rd, side, revd, ov, od, ch, st in rows:
            print('| %d | %s | ws%d | %.2f | %s | %s | %s | %s | %s | %s |'
                  % (i, ln.U(b), rd, bd.value(rd, b), 'YES' if revd else 'no',
                     'yes' if ov else 'no', 'yes' if od else 'no',
                     'YES' if ov != od else 'no', 'YES' if ch else 'no', st))
        print('')
    print('| the read | value |')
    print('|---|---|')
    print('| legs walked | %d |' % len(lg))
    print('| cadence bars with a rider | %d |' % n_cad)
    print('| of those, the rider had reversed | %d |' % n_rev)
    print('| of those, the two oob reads disagree | %d |' % n_dis)
    print('| CHANCES - reversed AND the reads disagree | **%d** |' % n_chance)
    print('')
    return n_chance


c1 = scan(ln.K('2026-08-30 00:00:00'), ln.K('2026-08-30 23:59:55'), '2026-08-30, every row', True)
c2 = scan(ln.K('2026-08-30 00:00:00'), ln.K('2026-09-06 23:59:55'),
          '2026-08-30 to 09-06, the counts only', False)
print('| the read | value |')
print('|---|---|')
print('| chances on 2026-08-30 | %d |' % c1)
print('| chances over 2026-08-30 to 09-06 | %d |' % c2)
print('| so the wider A/B | %s |'
      % ('is worth running - the mech has chances to act'
         if c2 > 0 else 'CANNOT test the mech - it has no chance to act in that window either'))
print('| seconds to compute | %.1f |' % (time.time() - T0))
