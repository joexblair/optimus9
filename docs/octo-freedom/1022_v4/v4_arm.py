"""ONE sweep arm: the deferred backstop trades over a span, at whatever the env knobs say.

Forked per arm by v4_mech_sweep.py so the bank's refusal is exercised for real - an off-bank arm
must carry W_V4_EXPERIMENT=1 or v4_knobs raises, which is the point of banking them.

prints one markdown row. usage: v4_arm.py <A> <B> <label>
"""
import sys
import io

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
import ln
import v4_knobs as K
import v4_fast as F
import v4_deferred_trades as DT
import v4_swing_score as SS
from v4_backstop_trades import prices

PCT, CAP = 2.0, 1.1                      # HELD - the scorer is not swept

A, B = ln.K(sys.argv[1]), ln.K(sys.argv[2])
LABEL = sys.argv[3]
R = {t: ln.line('ws%dr' % t) for t in range(1, K.TF_CEILING + 3)}
MG = {t: ln.line('ws%dMage' % t) for t in range(1, 13)}
close, hi, lo = prices()
F.reset()
f = F.scan(A, B, R, MG, 'window')
rows = []
for d in f:
    v, bar = F.walk(R, 5, d['side'], d['rev'], B)
    unres = (v == 'EXHAUST' and bar is not None and bar >= B - 1)
    rows.append({'fire': d['fire'], 'rev': d['rev'], 'side': d['side'], 'dir': d['dir'],
                 'verdict': 'UNRESOLVED' if unres else v, 'exh': None if unres else bar})
acc = DT.accept(rows)
sc, _ = SS.score(acc, close, PCT)
st = []
for t in sc:
    q = dict(t)
    q['stopped'] = t['mae'] <= -CAP
    if q['stopped']:
        q['mae'], q['mfe'] = -CAP, 0.0
    st.append(q)
if not st:
    print('| %s | %d | %d | 0 | 0 | - | - | - | - |'
          % (LABEL, len(f), sum(1 for r in rows if r['verdict'] == 'EXHAUST')))
    sys.exit(0)
mf = np.array([t['mfe'] for t in st]); ma = np.array([t['mae'] for t in st])
pos = [t for t in st if not t['stopped']]
print('| %s | %d | %d | %d | %d | %+.3f | %+.3f | %.3f | %+.3f |'
      % (LABEL, len(f), sum(1 for r in rows if r['verdict'] == 'EXHAUST'), len(st), len(pos),
         float(mf.mean()), float(ma.mean()),
         float(mf.mean() / abs(ma.mean())) if ma.mean() else 0.0,
         float(np.mean([t['mfe'] for t in pos])) if pos else 0.0))
