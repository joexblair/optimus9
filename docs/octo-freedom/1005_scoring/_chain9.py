"""THE CHAIN WITH JOE'S ws12r CEILING RULE. 09-25. 1007.

JOE: *"add this rule - if ws12r crosses into oob, then extend the max TF to ws23"* /
     *"this is a per leg mech"*.

  THE CEILING    starts at ws12 (`LIN_TF[-1]`) at every leg OPEN. On the first bar of the leg where
                 ws12r CROSSES into oob on the leg's own dr side (over 85 for a LONG leg, under 15
                 for a SHORT one) the ceiling latches to ws23 and HOLDS for the rest of that leg.
                 PER LEG: the next leg opens back at ws12. The crossing is checked on every bar
                 from the open, before the kickstart and the baton read it.
  WHAT IT BOUNDS the kickstart's scan AND the baton's candidate range. The baton still hops at most
                 LIN_HOP TF numbers and still never goes backwards.
  x-cross        unchanged - ws{rider}x against ws{rider+1}r and ws{rider+2}r, both in-fence. With
                 the ceiling at ws23 that reads ws24r and ws25r; both lines exist.
  THE STOP       Joe 1007: the leg closes AT the first bar where its adverse excursion from its own
                 open exceeds MAE_STOP, and the chain halts there for review.
  THE STASH      OFF. Joe put it in limbo.
"""
import os, io, contextlib, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.compute import momo_core as MC
from optimus9.compute.momo_config import momo_bank, momo_config
from optimus9.compute.momo_gated import momo_window
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

D = os.environ.get('W_DAY', '2026-09-25')
START = os.environ.get('W_START', '08:10:00')
FIRST = int(os.environ.get('W_SIDE', '1'))              # +1 = LONG
LEG0 = int(os.environ.get('W_LEG0', '7'))               # the leg number the chain resumes after
MAE_STOP = float(os.environ.get('MAE_STOP', '1.1'))     # percent, per leg, from its own open
CEIL_TRIG_TF = int(os.environ.get('CEIL_TRIG_TF', '12'))    # the line whose oob crossing extends
CEIL_HI = int(os.environ.get('CEIL_HI', '23'))              # the extended ceiling
LIN_HOP = int(SC.LG['lin_hop'])
BASE_HI = SC.TF[-1]                                     # ws12, the resting ceiling
EXF_HI = 100.0 - float(SC.LG['momo_fence_r']); EXF_LO = float(SC.LG['momo_fence_r'])
N = len(SC.ts)
ALL_TF = list(range(SC.TF[0], CEIL_HI + 1))             # ws1..ws23, every possible rider
RL = {t: SC.LD(t * 60, 'r') for t in range(SC.TF[0], CEIL_HI + 3)}      # unsliced, for stall_mask
R = {t: RL[t][:N] for t in RL}                                          # +2 TFs for the x-cross targets
X = {t: SC.LD(t * 60, 'x')[:N] for t in ALL_TF}
M2 = SC.Mg[2][:N]; PX = SC.PX[:N]
DRv = SC.DR if hasattr(SC, 'DR') else SC.DRv
db = DatabaseManager(**get_db_config()); db.connect()
BANK = {t: momo_bank(db, t) for t in ALL_TF}; db.disconnect()
ST = {}
for t in ALL_TF:
    with momo_config(BANK[t]):
        with momo_window(int(BANK[t]['k_window']) * t):
            s_, n_ = int(MC.MOMO_STEP_BARS), int(MC.MOMO_SAMPLES)
    for dd in (-1, +1):
        ST[(t, dd)] = stall_mask(RL[t], dd, int(SC.LG['stall_n']), s_, n_)
_P('producers ready; riders ws%d..ws%d, resting ceiling ws%d, extended ws%d, hop %d'
   % (ALL_TF[0], ALL_TF[-1], BASE_HI, CEIL_HI, LIN_HOP))

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

def run_leg(k, d):
    """-> (exit_k, why, mae, ceil_bar, trace). ceil_bar = the bar the ceiling latched, or None."""
    tr = []; p0 = float(PX[k]); sgn = 1 if d > 0 else -1
    armed = False; rider = None; mae = 0.0; ceil = BASE_HI; ceil_bar = None
    for j in range(k + 1, N):
        px = float(PX[j])
        if np.isfinite(px) and px > 0:
            adv = -((px - p0) / p0 * 100.0 * sgn)
            if adv > mae: mae = adv
            if adv > MAE_STOP:
                tr.append((j, 'MAE BREACH %.4f%% over %.2f%% - chain stops for review'
                           % (adv, MAE_STOP)))
                return j, 'mae breach', mae, ceil_bar, tr
        if ceil == BASE_HI and oobf(CEIL_TRIG_TF, j, d) and not oobf(CEIL_TRIG_TF, j - 1, d):
            ceil = CEIL_HI; ceil_bar = j
            tr.append((j, 'CEILING ws%d -> ws%d — ws%dr crossed into oob (r %.2f, was %.2f)'
                       % (BASE_HI, CEIL_HI, CEIL_TRIG_TF, float(R[CEIL_TRIG_TF][j]),
                          float(R[CEIL_TRIG_TF][j - 1]))))
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
            c = [t for t in ALL_TF if t <= ceil and oobf(t, j, d)]
            if c:
                rider = max(c)
                tr.append((j, 'KICKSTART — rider ws%d (r %.2f oob, ceiling ws%d)'
                           % (rider, float(R[rider][j]), ceil)))
            continue
        cand = [t for t in range(rider + 1, min(rider + LIN_HOP, ceil) + 1) if oobf(t, j, d)]
        if cand:
            rider = max(cand)
            tr.append((j, 'baton -> ws%d oob (r %.2f)' % (rider, float(R[rider][j])))); continue
        if ST[(rider, d)][j]:
            tr.append((j, 'final stalled on ws%d (r %.2f %s)'
                       % (rider, float(R[rider][j]), bnd(rider, j, d))))
            return j, 'final stalled', mae, ceil_bar, tr
        if xcond(rider, j, d):
            tr.append((j, 'x-cross on ws%d (vs ws%dr %.2f %s and ws%dr %.2f %s)'
                       % (rider, rider + 1, float(R[rider + 1][j]), bnd(rider + 1, j, d),
                          rider + 2, float(R[rider + 2][j]), bnd(rider + 2, j, d))))
            return j, 'x-cross', mae, ceil_bar, tr
    return None, 'tape end', mae, ceil_bar, tr

k0 = SC.K('%s %s' % (D, START))
print('\n# CHAIN FROM %s %s, side %s, ws%dr ceiling rule ON'
      % (D, START, 'LONG' if FIRST > 0 else 'SHORT', CEIL_TRIG_TF))
k, d, legs, n = k0, FIRST, [], LEG0
while True:
    xk, why, mae, cb, tr = run_leg(k, d)
    if xk is None:
        print('\n- leg %d found no exit before the tape end. the chain ends.' % (n + 1)); break
    n += 1
    p0 = float(PX[k]); sgn = 1 if d > 0 else -1
    real = (float(PX[xk]) - p0) / p0 * 100.0 * sgn
    legs.append(dict(leg=n, side='LONG' if d > 0 else 'SHORT', open=k, exit=xk, real=real,
                     mae=mae, why=why, ceil=cb))
    pct = lambda j: '%+.4f' % ((float(PX[j]) - p0) / p0 * 100.0 * sgn)
    mn = lambda j: '%+.1f' % ((int(SC.ts[j]) - int(SC.ts[k])) / 60000.0)
    print('\n## LEG %d — %s   open %s   pxs %.6f' % (n, legs[-1]['side'], SC.U(k), p0))
    box(('ts', '+min', 'event', 'pxs', 'pct'),
        [(SC.U(k), '+0.0', 'OPEN %s' % legs[-1]['side'], '%.6f' % p0, '+0.0000')]
        + [(SC.U(j), mn(j), lbl, '%.6f' % float(PX[j]), pct(j)) for j, lbl in tr]
        + [(SC.U(xk), mn(xk), 'EXIT — %s' % why, '%.6f' % float(PX[xk]), pct(xk))])
    if why == 'mae breach':
        print('\n- MAE breach at %s. THE CHAIN IS STOPPED FOR REVIEW.' % SC.U(xk)); break
    k = xk; d = -d

print('\n# THE CHAIN FROM %s' % START)
box(('leg', 'side', 'open', 'exit', 'hold min', 'ceiling latched', 'leg MAE', 'realised', 'why'),
    [(str(L['leg']), L['side'], SC.U(L['open']), SC.U(L['exit']),
      '%.1f' % ((int(SC.ts[L['exit']]) - int(SC.ts[L['open']])) / 60000.0),
      (SC.U(L['ceil']) if L['ceil'] is not None else '—'),
      '%.4f' % L['mae'], '%+.4f' % L['real'], L['why']) for L in legs]
    + [('legs %d-%d' % (legs[0]['leg'], legs[-1]['leg']), '', SC.U(legs[0]['open']),
        SC.U(legs[-1]['exit']),
        '%.1f' % sum((int(SC.ts[L['exit']]) - int(SC.ts[L['open']])) / 60000.0 for L in legs),
        '%d of %d' % (sum(1 for L in legs if L['ceil'] is not None), len(legs)),
        '%.4f' % max(L['mae'] for L in legs), '%+.4f' % sum(L['real'] for L in legs), '')])
print('\n- %d legs, %d positive, %d latched the ws%d ceiling, worst leg MAE %.4f'
      % (len(legs), sum(1 for L in legs if L['real'] > 0),
         sum(1 for L in legs if L['ceil'] is not None), CEIL_TRIG_TF,
         max(L['mae'] for L in legs)))
