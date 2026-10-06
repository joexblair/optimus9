"""Complete Joe's walk from 11:15 on 09-25: does ws9 stall before ws10/ws11 exit the fence?

THE LINEAGE WALKS UPWARD ONLY, NEVER BACKWARDS. Joe 1006: *"it's important that the lineage walks
TFs upward, never backwards"*. At 11:15 the rider is ws9 - the HIGHEST TF that has exited the fence.
ws7 and ws8 are oob too and are not looked at again. The candidate set is {ws10, ws11}, hop <= 2 TF
numbers from the rider. ws12 is +3 and is out of reach until ws10 or ws11 takes the baton.
"""
import os, sys, io, contextlib
os.environ.setdefault('LG_DAY', '2026-09-25')
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC, baton as BT
import numpy as np

import os as _o
DAY = '2026-09-25'
S = _o.environ.get('W_FROM', '11:15:00'); E = '23:59:55'
RIDER = int(_o.environ.get('W_RIDER', '9')); CAND = (RIDER + 1, RIDER + 2)
C = BT.compute(DAY + ' 00:00:00', DAY + ' 23:59:55', 'octosig/%s.out' % DAY, warn=False)
k0, k1 = SC.K('%s %s' % (DAY, S)), SC.K('%s %s' % (DAY, E))
TF = list(range(1, 13))

def band(t, k, d):
    v = float(SC.Rl[t][k])
    if not np.isfinite(v): return '?'
    if d > 0: return 'O' if v >= 85.0 else ('x' if v >= 83.0 else '.')
    return 'O' if v <= 15.0 else ('x' if v <= 17.0 else '.')

print('# THE WALK FROM %s, rider ws%d, candidates %s   (upward only)'
      % (S, RIDER, ','.join('ws%d' % t for t in CAND)))

# ---- the two clocks
print('\n## CLOCK 1 - ws%d STALL onsets after %s' % (RIDER, S))
print('| ts | dr | ws%d r | ws%d band |' % (RIDER, RIDER)); print('|---|---|---|---|')
stall_k = None
for k in range(k0, k1 + 1):
    j = k - C.A
    if C.ST[RIDER][j] and not C.ST[RIDER][j - 1]:
        d = int(C.D[j])
        print('| %s | %+d | %.2f | %s |' % (SC.U(k), d, float(SC.Rl[RIDER][k]), band(RIDER, k, d)))
        if stall_k is None: stall_k = k

print('\n## CLOCK 2 - ws10 / ws11 band crossings after %s' % S)
print('| ts | TF | from -> to | r | dr |'); print('|---|---|---|---|---|')
prev = {t: band(t, k0, int(C.D[k0 - C.A])) for t in CAND}
for k in range(k0 + 1, k1 + 1):
    j = k - C.A; d = int(C.D[j])
    for t in CAND:
        b = band(t, k, d)
        if b != prev[t]:
            print('| %s | ws%d | %s -> %s | %.2f | %+d |' % (SC.U(k), t, prev[t], b, float(SC.Rl[t][k]), d))
            prev[t] = b

print('\n## THE VERDICT BAR - ws%d first stall onset after %s' % (RIDER, S))
if stall_k is None:
    print('ws%d never stalls between %s and %s.' % (RIDER, S, E))
else:
    j = stall_k - C.A; d = int(C.D[j])
    print('ws%d stalls at **%s**, dr %+d, %.1f min after 11:15:00\n'
          % (RIDER, SC.U(stall_k), d, (int(SC.ts[stall_k]) - int(SC.ts[k0])) / 60000.0))
    print('| TF | r | band | mom-true | stalled | in the candidate set |')
    print('|---|---|---|---|---|---|')
    for t in TF:
        st = ('Y' if C.ST[t][j] else '-') if t in C.ST else 'n/a'
        tag = 'RIDER' if t == RIDER else ('candidate' if t in CAND else '-')
        print('| ws%d | %.2f | %s | %s | %s | %s |'
              % (t, float(SC.Rl[t][k]) if False else float(SC.Rl[t][stall_k]),
                 band(t, stall_k, d), 'Y' if C.MT12[t][j] else '-', st, tag))
    exited = [t for t in CAND if band(t, stall_k, d) == 'O']
    print('\n- candidates that had EXITED THE FENCE at the stall bar: **%s**'
          % (', '.join('ws%d' % t for t in exited) or 'NONE'))
    print('- collective momentum: **%s**' % ('held' if exited else 'LOST'))

print('\n## THE g5Mage / g15Mage SAME-SIDE oob STATE, from 11:15:00 to the end of the day')
print('# the fence is dr-sided: dr +1 reads >= %.0f, dr -1 reads <= %.0f' % (SC.HI, SC.LO))
print('| ts | dr | g5Mage | g15Mage | both oob same side | g5 rev flag |')
print('|---|---|---|---|---|---|')
prev_both = None
for k in range(k0, k1 + 1):
    j = k - C.A; d = int(C.D[j])
    g5, g15 = float(SC.MTD['g5'][k]), float(SC.MTD['g15'][k])
    oob = (lambda v: v >= SC.HI) if d > 0 else (lambda v: v <= SC.LO)
    both = bool(np.isfinite(g5) and np.isfinite(g15) and oob(g5) and oob(g15))
    if both != prev_both:
        print('| %s | %+d | %.2f | %.2f | %s | %s |'
              % (SC.U(k), d, g5, g15, 'YES' if both else 'no',
                 'Y' if bool(SC.REV[k]) else '-'))
        prev_both = both
