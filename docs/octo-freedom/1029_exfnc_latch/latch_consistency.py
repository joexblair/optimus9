"""TWO READS THE LATCH ARM EXPOSED, measured rather than asserted.

    1  oob-LATCHED WHILE NOT EX-FENCE-LATCHED. By VALUE oob (15/85) is a subset of ex-fence
       (20/80), so "oob and not ex-fence" is impossible on a line's value. Two INDEPENDENT latches
       - my decision 1 - can produce it, because each is cleared only by its OWN fence's
       opposite-side cross. This counts the bars where it happens.
    2  THE RIDER THE LATCH PICKS. `rider_at` takes the HIGHEST latched line, so if ws12 is latched
       most of the day it is the rider most of the day and the baton never passes. This counts, at
       every bar of 2026-08-30, which TF the rider scan would return on each read.
"""
import os, sys, io
import numpy as np
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1027_pseudo_closed')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln, v4_knobs as K, v4_rcfg_sweep as RS, v4_closed_prev as CP
import v4_l2_proxy as PX, pseudo_closed as PC
from v4_backstop_trades import prices
sys.stderr = _e

DAY = '2026-08-30'
A, B = ln.K('%s 00:00:00' % DAY), ln.K('%s 23:59:55' % DAY)
MINTF = int(K.LIN2_PSEUDO_MIN_TF)
TOP = max(int(K.L2_MOM_MAXTF), int(K.LIN2_BARRAGE_MAX_TF))
NB = B - A + 1

close, _h, _l = prices()
E = RS.load((RS.K0, RS.R0, RS.S0))
C = CP.ladder(E)
MGL = {t: CP.line('ws%dMage' % t, t * 60) for t in range(1, 13)}
MGE = {t: ln.line('ws%dMage' % t) for t in range(1, 13)}
IDX = np.arange(A, B + 1)
PS = {}
for t in range(MINTF, TOP + 1):
    PS[t] = np.full(len(close), np.nan)
    PS[t][IDX] = PC.series(close, t, IDX)
BD = PX.Board(C, E, MG=MGL, MGE=MGE, PS=PS)
MX = int(K.L2_MOM_MAXTF)

print('# THE LATCH ARM: THE oob/EX-FENCE CONSISTENCY AND THE RIDER IT PICKS')
print('# %s, %d bars. LIN2_LATCH_EXFNC_ON %d | LIN2_EXFNC_LATCH_WOB %d bars | RULED_OK %s'
      % (DAY, NB, K.LIN2_LATCH_EXFNC_ON, K.LIN2_EXFNC_LATCH_WOB, K.RULED_OK))
print('')

print('## 1 - REMOVED. There is no oob latch - his 1029 correction. Every oob\n      read in the walk is the line value.')
print('')
print('## 2 - the rider the scan returns at every bar, by read')
print('')
for src, lab in (('value', 'LIN2_LATCH_EXFNC_ON 0 - the banked read'),
                 ('latch', 'LIN2_LATCH_EXFNC_ON 1 - the latch read')):
    M = np.zeros((MX + 1, NB), bool)
    for t in range(1, MX + 1):
        if src == 'value':
            M[t] = K.ex_fence_mask(BD.line(t), -1)[A:B + 1]
        else:
            M[t] = BD._latch(t, -1)[A:B + 1]
    rid = np.zeros(NB, int)
    for t in range(1, MX + 1):
        rid[M[t]] = t
    print('### %s, LOW side' % lab)
    print('')
    print('| the rider the scan returns | bars | %% of the %d bars |' % NB)
    print('|---|---|---|')
    for t in range(0, MX + 1):
        n = int(np.count_nonzero(rid == t))
        if n:
            print('| %s | %d | %.1f%% |' % ('none - no ex-fence line' if t == 0 else 'ws%d' % t,
                                            n, n / NB * 100.0))
    print('')
