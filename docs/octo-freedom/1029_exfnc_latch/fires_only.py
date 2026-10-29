"""JUST THE FIRINGS - no pseudo lines, no chain walk. The cheap half of causal_open.py.

Joe's firing mech reads only ws1b and the ws1..ws12 Mage lines, all on the live read, so finding
every firing on the whole tape needs none of the heavy work. This prints them.

It does NOT answer which trade is live at 2026-08-30 00:00:00 - that needs the walk forward, which
is the slow run still going.
"""
import os, sys, io, time
import numpy as np
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln, v4_knobs as K
from optimus9.analysis.jig import oob_ib_cross
sys.stderr = _e
T0 = time.time()

WA = ln.K('2026-08-30 00:00:00')
B1 = np.asarray(ln.line('ws1b'), float)
MG = {t: np.asarray(ln.line('ws%dMage' % t), float) for t in range(1, 13)}
tf, need, hi = int(K.LIN2_CHAIN_OPEN_TF), int(K.LIN2_CHAIN_OPEN_LINES), int(K.L2_MOM_MAXTF)
lb = int(K.LIN2_CHAIN_OPEN_LOOKBACK_S) // 5
w = max(1, int(K.LIN2_CHAIN_OPEN_XWOB))
band = list(range(tf + 1, hi + 1))
m5 = MG[tf]
masks = {+1: K.oob_mask(m5, +1), -1: K.oob_mask(m5, -1)}

fires, crosses = [], 0
for c, cf, sd in oob_ib_cross(B1, K.OOB_HI, K.OOB_LO, w):
    crosses += 1
    f = int(cf) if w > 1 else int(c)
    g = masks[int(sd)]
    if not (bool(g[f]) or bool(g[max(0, f - lb):f + 1].any())):
        continue
    j = f if g[f] else None
    if j is None:
        for i in range(f, max(0, f - lb) - 1, -1):
            if g[i]:
                j = i
                break
    if j is None:
        continue
    i = j
    while i > 0 and g[i - 1]:
        i -= 1
    seg = m5[i:j + 1]
    if not np.isfinite(seg).any():
        continue
    k = i + (int(np.nanargmax(seg)) if sd > 0 else int(np.nanargmin(seg)))
    assert k <= f, 'the anchor is later than the firing bar - that read is not causal'
    v0 = float(m5[k])
    got = [t for t in band
           if np.isfinite(MG[t][k])
           and ((float(MG[t][k]) < v0) if sd > 0 else (float(MG[t][k]) > v0))]
    if len(got) >= need:
        fires.append((f, int(sd), k, v0, tuple(got)))
fires.sort()

print('# EVERY FIRING OF HIS MECH ON THE WHOLE TAPE - the cheap half')
print('# TAPE %d bars, %s .. %s | RULED_OK %s'
      % (len(B1), ln.U(0), ln.U(len(B1) - 1), K.RULED_OK))
print('# the trigger line is ws%dMage. lines required %d, from ws%d to ws%d.'
      % (tf, need, tf + 1, hi))
print('# the look-back on the trigger is %d seconds. the hold on the ws1b cross is %d bar(s).'
      % (K.LIN2_CHAIN_OPEN_LOOKBACK_S, w))
print('# the anchor is the furthest point reached between the run start and the firing bar.')
print('')
print('| the read | value |')
print('|---|---|')
print('| ws1b crosses in from out of bounds, whole tape | %d |' % crosses)
print('| of those, firings | %d |' % len(fires))
print('| the EARLIEST firing | %s |' % ln.U(fires[0][0]))
print('| its trade direction | %s |' % ('SHORT' if fires[0][1] > 0 else 'LONG'))
print('| firings at or before 2026-08-30 00:00:00 | %d |' % sum(1 for x in fires if x[0] <= WA))
print('| the bar I fitted to the time you quoted | 2026-08-29 23:53:50 |')
print('| the bar the backward search picked | 2026-08-29 23:56:00 |')
print('| seconds to compute | %.1f |' % (time.time() - T0))
print('')
print('## the first 10 firings on the tape')
print('')
print('| # | the firing bar | the side ws1b came in from | the trade direction |'
      ' the anchor bar | ws%dMage at the anchor | lines beyond it |' % tf)
print('|---|---|---|---|---|---|---|')
for n, (f, sd, k, v0, got) in enumerate(fires[:10], 1):
    print('| %d | %s | %s | %s | %s | %.2f | %d of %d |'
          % (n, ln.U(f), 'HIGH' if sd > 0 else 'LOW', 'SHORT' if sd > 0 else 'LONG',
             ln.U(k), v0, len(got), len(band)))
print('')
print('## the last 10 firings at or before 2026-08-30 00:00:00')
print('')
print('| the firing bar | the side ws1b came in from | the trade direction | the anchor bar |'
      ' ws%dMage at the anchor | lines beyond it |' % tf)
print('|---|---|---|---|---|---|')
for f, sd, k, v0, got in [x for x in fires if x[0] <= WA][-10:]:
    print('| %s | %s | %s | %s | %.2f | %d of %d |'
          % (ln.U(f), 'HIGH' if sd > 0 else 'LOW', 'SHORT' if sd > 0 else 'LONG',
             ln.U(k), v0, len(got), len(band)))
