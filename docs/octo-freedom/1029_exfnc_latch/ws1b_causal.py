"""The two ws1b crossings, judged ONLY on bars at or before each one.

Joe 1029: *"most of your update relies on lookahead. be strictly causal and recreate your
response"*.

WHAT I GOT WRONG. I judged the 23:53:50 crossing by saying ws1b stayed under 85 through 23:55:40,
and I judged the 23:55:45 trip back out by saying it lasted exactly 3 bars. Both read bars after
the event. I also reported the highest ws5Mage between the two crossings, which cannot be known at
the first one.

WHAT IS KNOWABLE AT A CROSSING BAR, with a hold of H bars: the bar before was beyond the line, and
every bar from the crossing to crossing + H - 1 is not. Nothing after that. So this prints, per
crossing and per hold, only the bars inside that window.
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
HI = K.OOB_HI
beyond = K.oob_mask(V, +1)
XS = [i for i in range(A, B + 1) if beyond[i - 1] and not beyond[i]]

print('# THE ws1b CROSSINGS, JUDGED ONLY ON BARS AT OR BEFORE EACH ONE')
print('# ws1b is the live read. the line is %.0f.' % HI)
print('')
print('| the read | value |')
print('|---|---|')
print('| crossings in, 2026-08-29 23:50:00 to 23:57:00 | %d |' % len(XS))
for n, i in enumerate(XS, 1):
    print('| crossing %d | %s, ws1b %.2f, previous bar %.2f |'
          % (n, ln.U(i), float(V[i]), float(V[i - 1])))
print('')
print('## each crossing, per hold, using only the bars inside its own hold window')
print('')
print('| the crossing | the hold | the window it reads | every bar under %.0f? |'
      ' confirmed at | the values in the window |' % HI)
print('|---|---|---|---|---|---|')
for i in XS:
    for h in (1, 3, 12):
        hi_bar = i + h - 1
        win = V[i:hi_bar + 1]
        ok = bool((~beyond[i:hi_bar + 1]).all())
        print('| %s | %d bar%s = %d s | %s .. %s | %s | %s | %s |'
              % (ln.U(i), h, '' if h == 1 else 's', h * 5, ln.U(i), ln.U(hi_bar),
                 'yes' if ok else 'NO', ln.U(hi_bar) if ok else 'not confirmed',
                 ', '.join('%.2f' % x for x in win)))
print('')
print('| the read | value |')
print('|---|---|')
print('| what a 1-bar hold needs | the crossing bar itself |')
print('| what a 3-bar hold needs | the crossing bar and the 2 after it |')
print('| what a 12-bar hold needs | the crossing bar and the 11 after it |')
print('| what NONE of them needs | any bar beyond the hold window |')
