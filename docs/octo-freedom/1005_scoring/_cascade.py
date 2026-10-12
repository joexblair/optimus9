"""THE MAGE CASCADE, DIRECTION ONLY, THROUGH EVERY ws12r oob RUN. 1009.

Joe's mech, his §3 verbatim 0918: *"the first thing I look at is the lowest TF's value, and the
highest TF's value ... I can draw a mental downward line between those 2 numbers"*.

Joe 1009 settled the frame:
  the span       *"include g30: gcws30 to ws12"* - so gcws30Mage at the low end, ws12Mage at the high
  direction only *"direction only: yes"* - the UNPARKED half of #22. No bump count, no tolerance.
  clusters       *"run it with cluster testing disabled. we'll find an example as we walk each
                 ws12r oob"*. Every line's value is printed so a cluster is visible by eye.

AND HIS BLOCKER, 0918: *"this work is not calculated on dr - dr is only compared AFTER the
calculation has produced a decision based on the ladder's direction"*. So the cascade direction is
computed with no reference to the leg, and only then set beside dr.
"""
import os, sys, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
from optimus9.analysis.jig import Jig
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP

SC, box, U, PX = C.SC, C.box, C.SC.U, C.PX
N = len(SC.ts); TF = C.TRIG_TF
ts = np.asarray(SC.ts[:N], np.int64)
R12 = np.asarray(C.R[TF], float)[:N]
MG = {t: np.asarray(SC.LD(t * 60, 'Mage'), float)[:N] for t in range(1, TF + 1)}
with Jig(END_MS, hours=HOURS, warmup=WARMUP) as J:
    JT = np.asarray(J.ts, dtype=np.int64)
    G30 = np.asarray(J.causal.line('gcws30Mage'), float)
G = G30[np.clip(np.searchsorted(JT, ts), 0, len(JT) - 1)]
print('# gcws30Mage aligned to the tape: %d bars, %d finite' % (N, int(np.isfinite(G).sum())),
      flush=True)
LAD = ['g30'] + ['ws%d' % t for t in range(1, TF + 1)]
def rung(j):
    return [float(G[j])] + [float(MG[t][j]) for t in range(1, TF + 1)]
def casc(j):
    """the cascade DIRECTION, endpoints only, no dr. -> (+1 up, -1 down, 0 flat, lo, hi)"""
    v = rung(j)
    lo, hi = v[0], v[-1]
    if not (np.isfinite(lo) and np.isfinite(hi)): return 0, lo, hi
    return (1 if hi > lo else (-1 if hi < lo else 0)), lo, hi
DAY = lambda k: datetime.datetime.fromtimestamp(int(ts[k]) / 1000,
                                                datetime.timezone.utc).strftime('%Y-%m-%d')
NM = {1: 'UP', -1: 'DOWN', 0: 'flat'}
DAYS = set(os.environ.get('X_DAYS', '2026-07-15').split(','))
rows = []
for d, side in ((+1, 'HIGH'), (-1, 'LOW')):
    ob = ((R12 >= C.G_HI) if d > 0 else (R12 <= C.G_LO)) & np.isfinite(R12)
    st = np.flatnonzero(ob & ~np.r_[False, ob[:-1]]); en = np.flatnonzero(ob & ~np.r_[ob[1:], False])
    for a, b in zip(st, en):
        if DAY(int(a)) not in DAYS: continue
        dw = int(a) + C.GATE_BARS + 1
        reach = b >= dw
        c0, lo0, hi0 = casc(int(a))
        cd, lod, hid = casc(min(dw, N - 1)) if reach else (0, float('nan'), float('nan'))
        cE, loE, hiE = casc(int(b))
        rows.append((DAY(int(a)), U(int(a)), side, '%.1f' % ((b - a + 1) * 5 / 60.0),
                     'YES' if reach else 'no',
                     '%.2f' % lo0, '%.2f' % hi0, NM[c0],
                     ('%.2f' % lod) if reach else '—', ('%.2f' % hid) if reach else '—',
                     NM[cd] if reach else '—',
                     '%.2f' % loE, '%.2f' % hiE, NM[cE]))
rows.sort(key=lambda z: z[1])
print('\n# EVERY ws%dr oob RUN ON %s — the cascade at the run\'s open, at its dwell-ending, and at '
      'its end' % (TF, ', '.join(sorted(DAYS))))
box(('day', 'the run opens', 'oob side', 'run min', 'reached the dwell?',
     'g30Mage at open', 'ws12Mage at open', 'cascade at open',
     'g30Mage at dwell', 'ws12Mage at dwell', 'cascade at dwell',
     'g30Mage at end', 'ws12Mage at end', 'cascade at end'), rows)
print('\n- the cascade is gcws30Mage against ws12Mage, endpoints only. UP means ws12Mage is the')
print('  higher of the two. dr is NOT in this calculation, per Joe 0918.')
