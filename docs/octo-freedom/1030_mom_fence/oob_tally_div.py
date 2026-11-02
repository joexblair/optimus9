"""THE oob r LINES AND THEIR TRAJECTORY AT THE THREE DIVERGENCE BARS.

His 1101 question: *"is the difference between the 09-03 divergences and the 08-14 0713 the amount
of oob r lines?"* and *"add away/toward tagging as well"*.

All three bars are LOW target side - the 09-03 leg 2 is a SHORT, his 2324 example reads bullish on
the low side, and the 08-14 walk is a SHORT.

TOWARD/AWAY IS THE BANKED TRAJECTORY READ, v4_lineage2.towards - the same one the baton candidate
test uses, perspective = the target side. AWAY is simply not toward; the producer has one answer.
"""
import io
import os
import sys

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
#   THE SWALLOW COVERS THE NOISY IMPORTS ONLY, and `finally` restores stderr whatever happens.
_e = sys.stderr; sys.stderr = io.StringIO()
try:
    import v4_knobs as K
    import v4_rcfg_sweep as RS
    import v4_live_lines as LL
    import v4_l2_proxy as PX
    import v4_lineage2 as L2
    import ln
finally:
    sys.stderr = _e

E = RS.load((RS.K0, RS.R0, RS.S0))
MG = LL.mage()
BD = PX.Board(E, E, MG=MG, MGE=MG, PS=None)
SIDE = -1
lo, hi = K.fence()
BARS = [('his bullish 2324', '2026-09-03 23:24:00'),
        ('the 0437 cadence', '2026-09-03 04:37:55'),
        ('the 08-14 0713 cadence', '2026-08-14 07:13:05')]
print('# THE oob r LINES AND THEIR TRAJECTORY | low target side | oob %.1f/%.1f | fence (%.1f, %.1f)'
      % (K.OOB_LO, K.OOB_HI, lo, hi))
print('# toward/away is v4_lineage2.towards, the banked trajectory read the baton test uses')
print()
TALLY = {}
for lbl, t in BARS:
    k = ln.K(t)
    rows = []
    for tf in range(1, int(K.L2_MOM_MAXTF) + 1):
        if tf not in BD.tfs:
            continue
        v = float(BD.value(tf, k))
        rows.append((tf, v,
                     bool(BD.oob(tf, k, SIDE)),
                     bool(K.ex_fence(v, SIDE)),
                     bool(BD.baton_ex_fence(tf, k, SIDE, at_cadence=True)),
                     bool(L2.towards(BD, tf, k, SIDE))))
    TALLY[lbl] = rows
    print('## %s - %s' % (lbl, t))
    print()
    print('| rung | r value | oob at or below %.1f? | past the %.1f fence? | LATCHED? |'
          ' toward or away? |' % (K.OOB_LO, lo))
    print('|---|---|---|---|---|---|')
    for tf, v, ob, ex, lt, tw in rows:
        print('| ws%d | %.2f | %s | %s | %s | %s |'
              % (tf, v, 'YES' if ob else 'no', 'YES' if ex else 'no',
                 'YES' if lt else 'no', 'toward' if tw else 'away'))
    print()
print('## the three bars side by side')
print()
print('| the read | %s |' % ' | '.join(l for l, _t in BARS))
print('|---|%s' % ('---|' * len(BARS)))
def cnt(rows, f):
    return sum(1 for r in rows if f(r))
METRICS = [('r lines oob at or below %.1f' % K.OOB_LO, lambda r: r[2]),
           ('r lines past the %.1f fence' % lo, lambda r: r[3]),
           ('r lines LATCHED', lambda r: r[4]),
           ('r lines tagged toward', lambda r: r[5]),
           ('r lines tagged away', lambda r: not r[5]),
           ('oob AND toward', lambda r: r[2] and r[5]),
           ('oob AND away', lambda r: r[2] and not r[5]),
           ('latched AND toward', lambda r: r[4] and r[5]),
           ('latched AND away', lambda r: r[4] and not r[5])]
for nm, f in METRICS:
    print('| %s | %s |' % (nm, ' | '.join(str(cnt(TALLY[l], f)) for l, _t in BARS)))
print('| rungs on the ladder | %s |' % ' | '.join(str(len(TALLY[l])) for l, _t in BARS))
