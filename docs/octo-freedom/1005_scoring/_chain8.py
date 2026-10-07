"""THE CHAIN CONTINUED FROM JOE'S 08:10 OPEN. 09-25. 1007.

JOE: *"07:51 is stopped, so the chain is broken and needs a new open bar. I've chosen 08:10 as the
open bar to continue the chain on, because ws1r is low oob reversing and there is an upward Mage
cascade"*.

  OPEN         09-25 08:10:00, LONG - Joe's read is upward (ws1r low oob reversing, upward Mage
               cascade). The bar and the direction are his; nothing here re-derives them.
  THE MECH     exactly the one that produced legs 1-7: one-time KICKSTART picks the rider, the
               established lineage walk owns it after that (baton on an oob crossing within
               LIN_HOP), exit on x-cross or final stalled. THE STASH IS OFF - Joe put it in limbo.
  THE STOP     Joe 1007: *"stop the chain for review when you reach the next MAE >1.1"*. The leg
               closes AT the breach bar - the first bar on which the 1.1 is known - and the chain
               halts there for review. No day bound, no leg cap: the breach is the terminator.
"""
import os, io, contextlib, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.compute import momo_core as MC
from optimus9.compute.momo_config import momo_bank, momo_config
from optimus9.compute.momo_gated import momo_window, momo_g_why
from optimus9.analysis.jig import stall_mask
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
import time as _t; _T0 = _t.time()
_P = lambda m: print('# [%6.1fs] %s' % (_t.time() - _T0, m), flush=True)
_P('importing score39 ...')
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC
_P('ready')

D, START, FIRST = '2026-09-25', '08:10:00', +1          # Joe's open bar and his upward read
MAE_STOP = float(os.environ.get('MAE_STOP', '1.1'))     # Joe 1007, percent, per leg, from its open
LIN_TF, LIN_HOP = SC.TF, int(SC.LG['lin_hop'])
EXF_HI = 100.0 - float(SC.LG['momo_fence_r']); EXF_LO = float(SC.LG['momo_fence_r'])
N = len(SC.ts)
NEED = sorted(set(LIN_TF) | {LIN_TF[-1] + 1, LIN_TF[-2] + 2})
R = {t: SC.LD(t * 60, 'r')[:N] for t in NEED}
X = {t: SC.LD(t * 60, 'x')[:N] for t in LIN_TF}
M2 = SC.Mg[2][:N]; PX = SC.PX[:N]
DRv = SC.DR if hasattr(SC, 'DR') else SC.DRv
db = DatabaseManager(**get_db_config()); db.connect()
BANK = {t: momo_bank(db, t) for t in LIN_TF}; db.disconnect()
ST = {}
for t in LIN_TF:
    with momo_config(BANK[t]):
        with momo_window(int(BANK[t]['k_window']) * t):
            s_, n_ = int(MC.MOMO_STEP_BARS), int(MC.MOMO_SAMPLES)
    for dd in (-1, +1):
        ST[(t, dd)] = stall_mask(SC.Rl[t], dd, int(SC.LG['stall_n']), s_, n_)
_P('producers ready; tape %d bars to %s' % (N, SC.U(N - 1)))

def bnd(t, k, d):
    v = float(R[t][k])
    if d > 0: return 'O' if v >= SC.HI else ('x' if v >= EXF_HI else '.')
    return 'O' if v <= SC.LO else ('x' if v <= EXF_LO else '.')
oobf = lambda t, k, d: (float(R[t][k]) >= SC.HI) if d > 0 else (float(R[t][k]) <= SC.LO)
def xcond(h, k, d):
    t1, t2 = h + 1, h + 2
    if t1 not in R or t2 not in R: return False
    xv = float(X[h][k])
    c = (xv < float(R[t1][k]) and xv < float(R[t2][k])) if d > 0 else \
        (xv > float(R[t1][k]) and xv > float(R[t2][k]))
    return c and bnd(t1, k, d) == '.' and bnd(t2, k, d) == '.'
def box(hdr, rr):
    w = [max(len(hdr[i]), max((len(str(x[i])) for x in rr), default=0)) for i in range(len(hdr))]
    L = lambda a, m, b: a + m.join('─' * (x + 2) for x in w) + b
    print(L('┌', '┬', '┐'))
    print('│' + '│'.join(' ' + hdr[i].center(w[i]) + ' ' for i in range(len(hdr))) + '│')
    print(L('├', '┼', '┤'))
    for x in rr:
        print('│' + '│'.join(' ' + str(x[i]).ljust(w[i]) + ' ' for i in range(len(hdr))) + '│')
    print(L('└', '┴', '┘'))

k0 = SC.K('%s %s' % (D, START))
print('\n# THE STATE AT JOE\'S OPEN BAR %s' % START)
box(('TF', 'r', 'band (+dr)', 'Mage', 'x'),
    [('ws%d' % t, '%.2f' % float(R[t][k0]), bnd(t, k0, +1),
      ('%.2f' % float(SC.Mg[t][k0])) if t in SC.Mg else '—',
      ('%.2f' % float(X[t][k0])) if t in X else '—') for t in LIN_TF])
print('- dr at %s: %+d   pxs %.6f' % (START, int(DRv[k0]), float(PX[k0])))

def run_leg(k, d):
    tr = []; p0 = float(PX[k]); sgn = 1 if d > 0 else -1
    armed = False; rider = None; mae = 0.0
    for j in range(k + 1, N):
        px = float(PX[j])
        if np.isfinite(px) and px > 0:
            adv = -((px - p0) / p0 * 100.0 * sgn)
            if adv > mae: mae = adv
            if adv > MAE_STOP:
                tr.append((j, 'MAE BREACH %.4f%% over %.2f%% - chain stops for review'
                           % (adv, MAE_STOP)))
                return j, 'mae breach', mae, tr
        if not armed:
            if (d > 0 and float(M2[j]) >= SC.HI and float(M2[j - 1]) < SC.HI) or \
               (d < 0 and float(M2[j]) <= SC.LO and float(M2[j - 1]) > SC.LO):
                armed = True
                tr.append((j, 'exit-armed — ws2Mage %s %.0f (%.2f)'
                           % ('over' if d > 0 else 'under', SC.HI if d > 0 else SC.LO,
                              float(M2[j]))))
            else:
                continue
        if rider is None:
            c = [t for t in LIN_TF if oobf(t, j, d)]
            if c:
                rider = max(c)
                tr.append((j, 'KICKSTART — rider ws%d (r %.2f oob)' % (rider, float(R[rider][j]))))
            continue
        cand = [t for t in range(rider + 1, min(rider + LIN_HOP, LIN_TF[-1]) + 1)
                if oobf(t, j, d)]
        if cand:
            rider = max(cand)
            tr.append((j, 'baton -> ws%d oob (r %.2f)' % (rider, float(R[rider][j])))); continue
        if ST[(rider, d)][j]:
            tr.append((j, 'final stalled on ws%d (r %.2f %s)'
                       % (rider, float(R[rider][j]), bnd(rider, j, d))))
            return j, 'final stalled', mae, tr
        if xcond(rider, j, d):
            tr.append((j, 'x-cross on ws%d' % rider))
            return j, 'x-cross', mae, tr
    return None, 'tape end', mae, tr

k, d, legs, n = k0, FIRST, [], 7
while True:
    xk, why, mae, tr = run_leg(k, d)
    if xk is None:
        print('\n- leg %d found no exit before the tape end. the chain ends.' % (n + 1)); break
    n += 1
    p0 = float(PX[k]); sgn = 1 if d > 0 else -1
    real = (float(PX[xk]) - p0) / p0 * 100.0 * sgn
    legs.append(dict(leg=n, side='LONG' if d > 0 else 'SHORT', open=k, exit=xk, real=real,
                     mae=mae, why=why))
    if True:
        pct = lambda j: '%+.4f' % ((float(PX[j]) - p0) / p0 * 100.0 * sgn)
        mn = lambda j: '%+.1f' % ((int(SC.ts[j]) - int(SC.ts[k])) / 60000.0)
        print('\n## LEG %d — %s   open %s   pxs %.6f'
              % (n, legs[-1]['side'], SC.U(k), p0))
        box(('ts', '+min', 'event', 'pxs', 'pct'),
            [(SC.U(k), '+0.0', 'OPEN %s' % legs[-1]['side'], '%.6f' % p0, '+0.0000')]
            + [(SC.U(j), mn(j), lbl, '%.6f' % float(PX[j]), pct(j)) for j, lbl in tr]
            + [(SC.U(xk), mn(xk), 'EXIT — %s' % why, '%.6f' % float(PX[xk]), pct(xk))])
    if why == 'mae breach':
        print('\n- MAE breach at %s. THE CHAIN IS STOPPED FOR REVIEW.' % SC.U(xk)); break
    k = xk; d = -d

print('\n# THE CHAIN FROM %s' % START)
box(('leg', 'side', 'open', 'exit', 'hold min', 'leg MAE', 'realised', 'why'),
    [(str(L['leg']), L['side'], SC.U(L['open']), SC.U(L['exit']),
      '%.1f' % ((int(SC.ts[L['exit']]) - int(SC.ts[L['open']])) / 60000.0),
      '%.4f' % L['mae'], '%+.4f' % L['real'], L['why']) for L in legs]
    + [('legs %d-%d' % (legs[0]['leg'], legs[-1]['leg']), '', SC.U(legs[0]['open']),
        SC.U(legs[-1]['exit']),
        '%.1f' % sum((int(SC.ts[L['exit']]) - int(SC.ts[L['open']])) / 60000.0 for L in legs),
        '%.4f' % max(L['mae'] for L in legs), '%+.4f' % sum(L['real'] for L in legs), '')])
print('\n- %d legs, %d positive, worst leg MAE %.4f, legs breaching 1.1: %d'
      % (len(legs), sum(1 for L in legs if L['real'] > 0), max(L['mae'] for L in legs),
         sum(1 for L in legs if L['mae'] > 1.1)))
print('- legs 1-7 (02:48:50 -> 07:51:05) were +4.1310. legs %d-%d add %+.4f, running %+.4f'
      % (legs[0]['leg'], legs[-1]['leg'], sum(L['real'] for L in legs),
         4.1310 + sum(L['real'] for L in legs)))
