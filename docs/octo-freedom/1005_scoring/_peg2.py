"""PEGGING, RECODED on Joe's anchor. 1007.

My first coding found the previous dr-ex-fence BAR and failed his self-check (returned ws1, he says
ws3). ws1Mage chatters across 83, so two "visits" were 10 s apart and the test was vacuous.

JOE'S SENTENCE ANCHORS IT: *"ws3MAge did not cross into low ex-fence when ws2Mage and ws1Mage both
crossed into low ex-fence at ~10:06"*. That shared crossing IS the anchor.

  anchor      ws1Mage's most recent COUNTER-dr ex-fence bar at or before the open
  pegged(t)   ws{t}Mage has NO counter-dr ex-fence bar in [anchor, open]
  the answer  the LOWEST pegged TF

Knob-free, and consistent with the matryoshka order - the lowest TF leads, so ws1 is the anchor.
"""
import sys, datetime
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
SC, box = C.SC, C.box
N = len(SC.ts)
DRv = (SC.DR if hasattr(SC, 'DR') else SC.DRv)[:N]
MM = {t: SC.LD(t * 60, 'Mage')[:N] for t in range(1, 31)}
EXF_LO = float(SC.LG['momo_fence_r']); EXF_HI = 100.0 - EXF_LO
K = lambda s: SC.K(s)

def peg(k):
    dr = int(DRv[k])
    ctf = (lambda v: v <= EXF_LO) if dr > 0 else (lambda v: v >= EXF_HI)
    anc = None
    for j in range(k, max(0, k - 34560) - 1, -1):
        v = float(MM[1][j])
        if np.isfinite(v) and ctf(v): anc = j; break
    if anc is None: return dr, None, None, []
    det = []
    for t in range(1, 31):
        hits = [j for j in range(anc, k + 1) if np.isfinite(MM[t][j]) and ctf(float(MM[t][j]))]
        det.append((t, len(hits), SC.U(hits[0]) if hits else '—',
                    'crossed' if hits else 'PEGGED'))
    pg = [t for t, n_, f, s in det if s == 'PEGGED']
    return dr, anc, (pg[0] if pg else None), det

k56 = K('2026-09-25 10:56:40')
dr, anc, pg, det = peg(k56)
print('# THE 10:56:40 SELF-CHECK, RECODED')
print('- dr %+d, so the counter-dr ex-fence is %s'
      % (dr, 'LOW <= %.0f' % EXF_LO if dr > 0 else 'HIGH >= %.0f' % EXF_HI))
print('- anchor = ws1Mage\'s most recent counter-dr ex-fence bar: %s' % (SC.U(anc) if anc else '—'))
print('- my recoding returns: %s   (Joe says ws3)' % ('ws%d' % pg if pg else 'none'))
box(('TF', 'counter-ex-fence bars in [anchor, open]', 'first one', 'verdict'),
    [('ws%d' % t, str(n_), f, s) for t, n_, f, s in det[:8]])

print('\n# ws1Mage, ws2Mage, ws3Mage PER MINUTE, 10:00 TO 10:57 — the raw paths')
a, b = K('2026-09-25 10:00:00'), K('2026-09-25 10:57:00')
box(('ts', 'ws1Mage', '<= 17?', 'ws2Mage', '<= 17?', 'ws3Mage', '<= 17?'),
    [(SC.U(j), '%.2f' % float(MM[1][j]), 'Y' if float(MM[1][j]) <= EXF_LO else '-',
      '%.2f' % float(MM[2][j]), 'Y' if float(MM[2][j]) <= EXF_LO else '-',
      '%.2f' % float(MM[3][j]), 'Y' if float(MM[3][j]) <= EXF_LO else '-')
     for j in range(a, b + 1, 12)])
print('\n- ws1Mage min over 10:00..10:57: %.2f at %s'
      % (float(np.nanmin(MM[1][a:b+1])), SC.U(a + int(np.nanargmin(MM[1][a:b+1])))))
print('- ws2Mage min: %.2f at %s'
      % (float(np.nanmin(MM[2][a:b+1])), SC.U(a + int(np.nanargmin(MM[2][a:b+1])))))
print('- ws3Mage min: %.2f at %s'
      % (float(np.nanmin(MM[3][a:b+1])), SC.U(a + int(np.nanargmin(MM[3][a:b+1])))))
