"""Every bar of ws1b from 2026-08-29 23:50:00 to 23:57:00, so the two crossings are on the page.

Joe 1029: *"why 2356? does it fit inside the mech? I see ws1b crossing before 2356, and ws1b
crossing to ib is the fire bar"*.

ws1b is read live. "beyond 85" is the high out-of-bounds test. A crossing in is the first bar that
is no longer beyond it after a run that was.
"""
import os, sys, io
import numpy as np
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln, v4_knobs as K
sys.stderr = _e

A, B = ln.K('2026-08-29 23:50:00'), ln.K('2026-08-29 23:57:00')
V = np.asarray(ln.line('ws1b'), float)
M5 = np.asarray(ln.line('ws5Mage'), float)
HI = K.OOB_HI
beyond = K.oob_mask(V, +1)
g5 = K.oob_mask(M5, +1)

print('# ws1b EVERY BAR, 2026-08-29 23:50:00 .. 23:57:00')
print('# ws1b is the live read. "beyond %.0f" is the high out-of-bounds test.' % HI)
print('# a crossing IN is the first bar no longer beyond it, after a run that was.')
print('')
print('| the bar | ws1b | beyond %.0f? | what happens here | ws5Mage | ws5Mage beyond %.0f? |'
      % (HI, HI))
print('|---|---|---|---|---|---|')
for i in range(A, B + 1):
    ev = ''
    if beyond[i - 1] and not beyond[i]:
        ev = 'CROSSES IN - a firing bar'
    elif not beyond[i - 1] and beyond[i]:
        ev = 'goes back out'
    print('| %s | %.2f | %s | %s | %.2f | %s |'
          % (ln.U(i), float(V[i]), 'yes' if beyond[i] else 'no', ev or '-',
             float(M5[i]), 'yes' if g5[i] else 'no'))
print('')
print('| the read | value |')
print('|---|---|')
ins = [i for i in range(A, B + 1) if beyond[i - 1] and not beyond[i]]
outs = [i for i in range(A, B + 1) if not beyond[i - 1] and beyond[i]]
print('| crossings IN inside this span | %d - %s |'
      % (len(ins), ', '.join(ln.U(i) for i in ins) if ins else 'none'))
print('| times it went back out | %d - %s |'
      % (len(outs), ', '.join(ln.U(i) for i in outs) if outs else 'none'))
print('| the highest ws5Mage between the first crossing in and the last | %.2f |'
      % (float(np.nanmax(M5[ins[0]:ins[-1] + 1])) if len(ins) > 1 else float('nan')))
