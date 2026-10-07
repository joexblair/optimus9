"""THE 21:48 RUN OPENED UP. 09-25, dr -1. Joe 1007: *"that makes the 21:48 to 23:22 the only real
concern"*.

THE QUESTION: the dip confirmed at 22:05:55 and the exit did not come until 23:22:45 - 76.8 min.
The exit needs THREE things at one bar: an r reversal on the dr side, a divergence, and x over r
(dr -1). This prints every reversal bar in the window with which of the three held, so the binding
one is visible rather than guessed.

Also prints the bar the `mae_stop_pct` 1.10 stop would have fired, since Joe's own stop is a banked
knob and this run breaches it.

dr -1, so the pre-existing trade is SHORT and DOWN is favourable - Joe's ruling, *"if dr is +1,
then towards dr is up, and the trade is LONG. inverse for -1dr"*.
"""
import os, io, contextlib, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.analysis.lr_v2 import _mage_rev
from optimus9.analysis.jig import anchor_floater
from optimus9.compute.spec_config import spec_config
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC

D, DD = '2026-09-25', -1
OOB_TS, GATE_TS, SIG_TS = '21:48:00', '21:54:05', '21:48:40'
DIP_TS, CONF_TS, EXIT_TS = '22:05:00', '22:05:55', '23:22:45'
db = DatabaseManager(**get_db_config()); db.connect()
W = spec_config(db, 'ws12_baton_config'); db.disconnect()
RREV = int(W['rrev_wob']); MAE_STOP = float(W['mae_stop_pct'])
DIV_TFS = [int(s.strip().replace('ws', '').replace('r', '')) for s in W['div_lines'].split(',')]
N = len(SC.ts)
K = lambda t: SC.K('%s %s' % (D, t))
R12 = SC.LD(12 * 60, 'r')[:N]
R = {t: SC.LD(t * 60, 'r')[:N] for t in DIV_TFS}
X = {t: SC.LD(t * 60, 'x')[:N] for t in DIV_TFS}
G1 = SC.MTD['ws1'][:N]; PX = SC.PX[:N]
REV = {t: _mage_rev(R[t], RREV) for t in DIV_TFS}
WANT = -1 if DD > 0 else +1
xok = lambda t, k: (float(X[t][k]) < float(R[t][k])) if DD > 0 else (float(X[t][k]) > float(R[t][k]))

kg = K(GATE_TS); p0 = float(PX[kg])
pct = lambda k: (float(PX[k]) - p0) / p0 * 100.0 * DD
mn = lambda k: (int(SC.ts[k]) - int(SC.ts[kg])) / 60000.0

def box(hdr, rr):
    w = [max(len(hdr[i]), max((len(str(x[i])) for x in rr), default=0)) for i in range(len(hdr))]
    B = lambda s, m, e: s + m.join('─' * (x + 2) for x in w) + e
    print(B('┌', '┬', '┐'))
    print('│' + '│'.join(' ' + hdr[i].center(w[i]) + ' ' for i in range(len(hdr))) + '│')
    print(B('├', '┼', '┤'))
    for x in rr:
        print('│' + '│'.join(' ' + str(x[i]).ljust(w[i]) + ' ' for i in range(len(hdr))) + '│')
    print(B('└', '┴', '┘'))

print('# THE 21:48 RUN — dr %+d, SHORT, measured from the gate bar %s at pxs %.6f'
      % (DD, GATE_TS, p0))
box(('walked event', 'ts', '+min', 'pct', 'ws12r', 'ws1Mage', 'ws1r', 'ws2r', 'pxs'),
    [(lbl, SC.U(K(t)), '%+.1f' % mn(K(t)), '%+.4f' % pct(K(t)), '%.2f' % float(R12[K(t)]),
      '%.2f' % float(G1[K(t)]), '%.2f' % float(R[1][K(t)]), '%.2f' % float(R[2][K(t)]),
      '%.6f' % float(PX[K(t)]))
     for lbl, t in (('ws12r oob from', OOB_TS), ('branch 1 cross', SIG_TS),
                    ('gate bar', GATE_TS), ('50 dip', DIP_TS), ('dip confirmed', CONF_TS),
                    ('EXIT on ws1r', EXIT_TS))])

ke, kc = K(EXIT_TS), K(CONF_TS)
seg = PX[kg:ke + 1]; idx = np.arange(kg, ke + 1)
ok = np.isfinite(seg) & (seg > 0); seg, idx = seg[ok], idx[ok]
f = int(seg.argmin()); g = int(seg.argmax())      # dr -1: favourable = DOWN
print('\n# THE PRICE PATH OVER THE HOLD')
box(('what', 'ts', '+min', 'pxs', 'pct'),
    [('gate', SC.U(kg), '+0.0', '%.6f' % p0, '+0.0000'),
     ('MFE', SC.U(int(idx[f])), '%+.1f' % mn(int(idx[f])), '%.6f' % float(seg[f]),
      '%+.4f' % pct(int(idx[f]))),
     ('MAE', SC.U(int(idx[g])), '%+.1f' % mn(int(idx[g])), '%.6f' % float(seg[g]),
      '%+.4f' % pct(int(idx[g]))),
     ('EXIT', SC.U(ke), '%+.1f' % mn(ke), '%.6f' % float(PX[ke]), '%+.4f' % pct(ke))])

stop_k = None
for k in range(kg + 1, ke + 1):
    if -pct(k) > MAE_STOP:
        stop_k = k; break
print('\n# WHERE THE %.2f STOP WOULD HAVE FIRED' % MAE_STOP)
box(('what', 'ts', '+min', 'pct', 'vs the actual exit'),
    [('stop bar', SC.U(stop_k) if stop_k else '—',
      '%+.1f' % mn(stop_k) if stop_k else '—',
      '%+.4f' % pct(stop_k) if stop_k else '—',
      ('%.1f min before the exit' % ((int(SC.ts[ke]) - int(SC.ts[stop_k])) / 60000.0))
      if stop_k else '—')])

print('\n# EVERY r REVERSAL FROM THE DIP CONFIRM TO THE EXIT — WHICH OF THE THREE HELD')
rows = []
for k in range(kc + 1, ke + 1):
    for t in DIV_TFS:
        if REV[t][k] != WANT: continue
        af = anchor_floater(R[t], PX, DD, k)
        fired = None if af is None else int(af['fired'])
        rows.append((SC.U(k), '%+.1f' % mn(k), 'ws%dr' % t, '%.2f' % float(R[t][k]),
                     '%.2f' % float(X[t][k]),
                     'Y', ('refused' if af is None else ('%+d' % fired)),
                     'Y' if xok(t, k) else 'no',
                     'EXIT' if (fired not in (None, 0) and xok(t, k)) else '-',
                     '%+.4f' % pct(k)))
box(('ts', '+min', 'line', 'r', 'x', 'reversal', 'divergence', 'x over r', 'verdict', 'pct'), rows)

blk = [r for r in rows if r[8] == '-']
print('\n- %d reversal bars in the window, %d blocked, %d fired' % (len(rows), len(blk),
                                                                    len(rows) - len(blk)))
nod = sum(1 for r in rows if r[6] in ('refused', '+0'))
nox = sum(1 for r in rows if r[7] == 'no')
print('- blocked by NO DIVERGENCE: %d; blocked by x NOT over r: %d (a bar can be both)'
      % (nod, nox))
best = min(rows, key=lambda r: float(r[9])) if rows else None
if best:
    print('- the best pct available at any reversal bar in the window: %s at %s'
          % (best[9], best[0]))
