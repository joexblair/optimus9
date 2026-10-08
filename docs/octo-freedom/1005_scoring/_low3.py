"""ws1/ws2/ws3 AT 12:27 AGAINST 10:56 — the usable comparison. 1008.

Joe 1008: *"this is the difference between the higher TF lines I was bracketing at 12:27, vs the
lower TF ws3. if you review ws3/2/1 at 12:27 you'll see a usable comparison"*.

The SAME ws1-anchored test that returned his ws3 at 10:56, run at 12:27, on the low three.
Plus the higher-TF RESIDENCE at the dr-side fence, which is the other thing he called pegging.
"""
import sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
SC, box = C.SC, C.box
N = len(SC.ts)
DRv = (SC.DR if hasattr(SC, 'DR') else SC.DRv)[:N]
MM = {t: SC.LD(t * 60, 'Mage')[:N] for t in range(1, 31)}
RL = {t: SC.LD(t * 60, 'r')[:N] for t in range(1, 31)}
EXF_LO = float(SC.LG['momo_fence_r']); EXF_HI = 100.0 - EXF_LO
K = lambda s: SC.K(s)

def last_counter(t, k, dr):
    ctf = (lambda v: v <= EXF_LO) if dr > 0 else (lambda v: v >= EXF_HI)
    for j in range(k, max(0, k - 34560) - 1, -1):
        v = float(MM[t][j])
        if np.isfinite(v) and ctf(v): return j
    return None

def peg(k):
    dr = int(DRv[k])
    anc = last_counter(1, k, dr)
    if anc is None: return dr, None, None, []
    ctf = (lambda v: v <= EXF_LO) if dr > 0 else (lambda v: v >= EXF_HI)
    det = []
    for t in range(1, 31):
        hits = [j for j in range(anc, k + 1) if np.isfinite(MM[t][j]) and ctf(float(MM[t][j]))]
        det.append((t, len(hits), hits[0] if hits else None))
    pg = [t for t, n_, f in det if not n_]
    return dr, anc, (pg[0] if pg else None), det

print('# THE LOW THREE, BOTH LEGS — same ws1-anchored test')
rows = []
for ts in ('2026-09-25 10:56:40', '2026-09-25 12:27:05'):
    k = K(ts); dr, anc, pg, det = peg(k)
    cs = 'LOW <= %.0f' % EXF_LO if dr > 0 else 'HIGH >= %.0f' % EXF_HI
    for t in (1, 2, 3):
        n_, f = det[t - 1][1], det[t - 1][2]
        lc = last_counter(t, k, dr)
        rows.append((ts[11:], '%+d' % dr, cs, 'ws%d' % t,
                     '%.2f' % float(MM[t][k]), '%.2f' % float(RL[t][k]),
                     SC.U(lc) if lc else 'none in 48h',
                     ('%.1f' % ((int(SC.ts[k]) - int(SC.ts[lc])) / 60000.0)) if lc else '—',
                     str(n_), 'crossed' if n_ else 'PEGGED'))
box(('open', 'dr', 'counter side', 'TF', 'Mage', 'r', 'last counter-side visit',
     'min before the open', 'visits since the ws1 anchor', 'verdict'), rows)

for ts in ('2026-09-25 10:56:40', '2026-09-25 12:27:05'):
    k = K(ts); dr, anc, pg, det = peg(k)
    print('- %s: dr %+d, ws1 anchor %s, lowest pegged TF %s'
          % (ts[11:], dr, SC.U(anc) if anc else '—', 'ws%d' % pg if pg else 'NONE'))

print('\n# THE HIGHER TFs AT 12:27 — RESIDENCE at the dr-side fence, the other "pegging"')
k = K('2026-09-25 12:27:05'); dr = int(DRv[k])
drf = (lambda v: v >= EXF_HI) if dr > 0 else (lambda v: v <= EXF_LO)
opp = (lambda v: v <= EXF_LO) if dr > 0 else (lambda v: v >= EXF_HI)
rows = []
for t in range(10, 25):
    j = k; run = 0
    while j >= 0 and np.isfinite(MM[t][j]) and not opp(float(MM[t][j])):
        run += 1; j -= 1
    first = j + 1
    rows.append(('ws%d' % t, '%.2f' % float(MM[t][k]),
                 '%+.1f' % (float(MM[t][k]) - EXF_HI),
                 SC.U(first), '%.1f' % (run * 5 / 60.0),
                 'Y' if float(MM[t][k]) >= EXF_HI else '-'))
box(('TF', 'Mage at 12:27', 'distance to hi ex-fence', 'held above the LOW fence since',
     'residence min', 'at the hi ex-fence now'), rows)
print('- "residence" = the unbroken run, back from the open, with no visit to the LOW ex-fence.')
print('- at dr -1 the LOW fence is the dr side, so this run is time spent AWAY from it.')
