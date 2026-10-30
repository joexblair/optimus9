"""THE MOM FENCE'S POPULATION, at 20/80 and at 25/75, over ws1..ws20.

WHY IT EXISTS. Joe 1030: *"the next thing I need is an understanding of the 20/80 mom fence. make
the fence 75/25, and increase the TF from 12 to 20"*. Before either knob moves, this is what the
fence IS: how many bars each r line sits beyond it, how many crossings INTO it, and how many lines
sit beyond it at once - the population the baton candidate test consumes.

THE TWO KNOBS HIS WORDS NAME, read from v4_knobs.py:
    RMOM_FNC      80.0 -> the pair (20.0, 80.0). His 1025 *"yes"* - v4mom_fnc IS RMOM_FNC.
                  His 1030 value is 75.0 -> (25.0, 75.0).
    L2_MOM_MAXTF  12   -> *"v4mom_maxTF = 12"*, the ladder's top rung. His 1030 value is 20.

NOTHING IS MOVED HERE. Both knobs stay at the bank for this run and the second fence is applied
alongside, so the two populations are measured on one pass of the same lines.

THE LINES ARE THE CONFIGURED r SET, v4_rcfg_sweep.load at (K0, R0, S0) - the same arrays the board
reads, which already covers ws1r..ws30r on disk. oob 15/85 is printed beside each row because oob
sits INSIDE the fence (his 1029 ruling), so the three populations nest.
"""
import io
import sys
import time

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
import v4_knobs as K
import v4_rcfg_sweep as RS
_e = sys.stderr; sys.stderr = io.StringIO()
import ln
sys.stderr = _e

T0 = time.time()
HI = 20                                  # his 1030 ladder top. ws1..ws20
BANK_TOP = int(K.L2_MOM_MAXTF)           # 12 - the bank, printed for the comparison
FENCES = ((80.0, 'the bank 20/80'), (75.0, 'his 1030 25/75'))


def beyond(v, side, fnc):
    """Past the fence `fnc` mirrored, on `side`. The same form as v4_knobs.ex_fence_mask."""
    lo, hi = 100.0 - float(fnc), float(fnc)
    return (v >= hi) if int(side) > 0 else (v <= lo)


def crossings(m, fin):
    """Bars where `m` turns on, counted only where both bars are finite. -> int."""
    ok = fin[1:] & fin[:-1]
    return int(np.count_nonzero(m[1:] & ~m[:-1] & ok))


E = RS.load((RS.K0, RS.R0, RS.S0))
R = {t: np.asarray(E[t], float) for t in range(1, HI + 1)}
N = len(R[1])
print('# bars on the tape: %d  |  %s .. %s' % (N, ln.U(0), ln.U(N - 1)))
print('# RMOM_FNC at the bank %.1f -> (%.1f, %.1f)  |  L2_MOM_MAXTF at the bank %d'
      % (K.RMOM_FNC, 100.0 - K.RMOM_FNC, K.RMOM_FNC, BANK_TOP))
print('# this run moves NEITHER knob. RULED_OK %s' % K.RULED_OK)

print('')
print('## every line, every side - the three nested populations')
print('')
print('| the line | side | finite bars | bars beyond 20/80 | % of finite | crossings into 20/80'
      ' | bars beyond 25/75 | % of finite | crossings into 25/75 | bars oob 15/85 | crossings into'
      ' 15/85 |')
print('|---|---|---|---|---|---|---|---|---|---|---|')
tot = {}
for t in range(1, HI + 1):
    v = R[t]
    fin = np.isfinite(v)
    nf = int(fin.sum())
    for side, nm in ((-1, 'LOW'), (+1, 'HIGH')):
        m80 = beyond(v, side, 80.0) & fin
        m75 = beyond(v, side, 75.0) & fin
        mob = np.asarray(K.oob_mask(v, side), bool) & fin
        tot[(t, side)] = dict(n80=int(m80.sum()), n75=int(m75.sum()), nob=int(mob.sum()),
                              c80=crossings(m80, fin), c75=crossings(m75, fin),
                              cob=crossings(mob, fin), nf=nf)
        d = tot[(t, side)]
        print('| ws%dr | %s | %d | %d | %.2f%% | %d | %d | %.2f%% | %d | %d | %d |'
              % (t, nm, nf, d['n80'], 100.0 * d['n80'] / nf, d['c80'],
                 d['n75'], 100.0 * d['n75'] / nf, d['c75'], d['nob'], d['cob']))

print('')
print('## what each change adds, one row per change')
print('')
print('| the change | bars beyond the fence | crossings into the fence |')
print('|---|---|---|')


def grp(top, fnc):
    key = 'n80' if fnc == 80.0 else 'n75'
    ck = 'c80' if fnc == 80.0 else 'c75'
    b = sum(tot[(t, s)][key] for t in range(1, top + 1) for s in (-1, +1))
    c = sum(tot[(t, s)][ck] for t in range(1, top + 1) for s in (-1, +1))
    return b, c


b1, c1 = grp(BANK_TOP, 80.0)
b2, c2 = grp(BANK_TOP, 75.0)
b3, c3 = grp(HI, 80.0)
b4, c4 = grp(HI, 75.0)
print('| the bank - ws1..ws%d at 20/80 | %d | %d |' % (BANK_TOP, b1, c1))
print('| the fence alone - ws1..ws%d at 25/75 | %d | %d |' % (BANK_TOP, b2, c2))
print('| the ladder alone - ws1..ws%d at 20/80 | %d | %d |' % (HI, b3, c3))
print('| both - ws1..ws%d at 25/75 | %d | %d |' % (HI, b4, c4))
print('| the fence alone, as a change | %+d | %+d |' % (b2 - b1, c2 - c1))
print('| the ladder alone, as a change | %+d | %+d |' % (b3 - b1, c3 - c1))
print('| both, as a change | %+d | %+d |' % (b4 - b1, c4 - c1))

print('')
print('## how many lines sit beyond the fence AT ONCE - one row per arm per count')
print('# the baton candidate test consumes this count, so this is the population it sees.')
print('# "bars with at least k" is cumulative; k runs to the arm\'s own ladder top.')
print('')
print('| the arm | side | at least k lines beyond | bars | % of the tape |')
print('|---|---|---|---|---|')
ARMS = ((BANK_TOP, 80.0, 'ws1..ws%d at 20/80 - the bank' % BANK_TOP),
        (BANK_TOP, 75.0, 'ws1..ws%d at 25/75' % BANK_TOP),
        (HI, 80.0, 'ws1..ws%d at 20/80' % HI),
        (HI, 75.0, 'ws1..ws%d at 25/75 - his 1030' % HI))
for top, fnc, lab in ARMS:
    for side, nm in ((-1, 'LOW'), (+1, 'HIGH')):
        cnt = np.zeros(N, int)
        for t in range(1, top + 1):
            v = R[t]
            cnt += (beyond(v, side, fnc) & np.isfinite(v)).astype(int)
        for k in range(1, top + 1):
            b = int(np.count_nonzero(cnt >= k))
            if b == 0:
                break
            print('| %s | %s | %d | %d | %.2f%% | ' % (lab, nm, k, b, 100.0 * b / N))

print('')
print('| the read | value |')
print('|---|---|')
print('| seconds to compute | %.1f |' % (time.time() - T0))
