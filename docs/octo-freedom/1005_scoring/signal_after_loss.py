"""After collective momentum is lost, Joe 1006: *"a signal is placed on the next g5Mage and g15Mage
same-side oob reversing"*. Find that bar after a given loss time, and show what REV is reading."""
import os, sys, io, contextlib
os.environ.setdefault('LG_DAY', '2026-09-25')
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC
import numpy as np
import inspect
from optimus9.analysis.jig import _mage_rev

DAY = '2026-09-25'
LOSS = os.environ.get('W_LOSS', '11:48:00')
k0 = SC.K('%s %s' % (DAY, LOSS))
print('# _mage_rev source, so the "reversing" test is on the record')
print('```'); print(inspect.getsource(_mage_rev)); print('```')
print('# REV_WOB = %d bars = %d s at the 5 s grid' % (SC.REV_WOB, SC.REV_WOB * 5))
print('\n# THE NEXT g5Mage + g15Mage SAME-SIDE oob WITH g5 REVERSING, after %s' % LOSS)
print('| ts | dr | g5Mage | g15Mage | g5 oob | g15 oob | g5 reversing | all three |')
print('|---|---|---|---|---|---|---|---|')
hit = None
for k in range(k0, len(SC.ts)):
    d = int(SC.DRv[k])
    if d == 0: continue
    g5, g15 = float(SC.MTD['g5'][k]), float(SC.MTD['g15'][k])
    if not (np.isfinite(g5) and np.isfinite(g15)): continue
    oob = (lambda v: v >= SC.HI) if d > 0 else (lambda v: v <= SC.LO)
    a, b, c = oob(g5), oob(g15), bool(SC.REV[k])
    if a and b and c:
        print('| %s | %+d | %.2f | %.2f | Y | Y | Y | **FIRES** |' % (SC.U(k), d, g5, g15))
        hit = k
        break
if hit is None:
    print('| — | | | | | | | no bar satisfies all three to the end of the tape |')
else:
    print('\n- %.1f min after the loss at %s' % ((int(SC.ts[hit]) - int(SC.ts[k0])) / 60000.0, LOSS))
    print('\n## THE FIVE BARS EITHER SIDE OF THE SIGNAL')
    print('| ts | dr | g5Mage | g15Mage | g5 oob | g15 oob | g5 reversing |')
    print('|---|---|---|---|---|---|---|')
    for k in range(hit - 5, hit + 6):
        d = int(SC.DRv[k]); g5, g15 = float(SC.MTD['g5'][k]), float(SC.MTD['g15'][k])
        oob = (lambda v: v >= SC.HI) if d > 0 else (lambda v: v <= SC.LO)
        print('| %s%s | %+d | %.2f | %.2f | %s | %s | %s |'
              % (SC.U(k), ' <-' if k == hit else '', d, g5, g15,
                 'Y' if oob(g5) else '-', 'Y' if oob(g15) else '-', 'Y' if bool(SC.REV[k]) else '-'))
