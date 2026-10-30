"""HOW LONG THE EX-FENCE LATCH HOLDS UNDER THE BANKED RELEASE AND UNDER HIS ALL-INCLUSIVE ONE.

WHY IT EXISTS. Joe 1030: *"why wouldn't we make the ex-fence latch all inclusive? ie line value
crosses past 75/25 (or 80/20) and is latched until a lif-off fires, instead of the latch releasing
on the cross to oob (current behaviour)"*.

THE BANKED RELEASE IS NOT A CROSS TO oob. v4_l2_proxy._latch releases on two things and neither is
an oob crossing:
    1  a barrage on that side          - self._releases(side), whole tape
    2  an OPPOSITE-SIDE ex-fence cross - confirmed over the same LIN2_EXFNC_LATCH_WOB 4 bars
So his proposal replaces those two with one release: the line's own lift-off.

THE THREE READS, per line and per side, at both fences:
    value       bars the line value is simply beyond the fence. No latch.
    banked      v4_l2_proxy's own latch, called directly - not restated here.
    all-inc     ON at the same confirmed ex-fence cross; OFF at that line's own lift-off on the
                SAME side, stamped at lift + LIFT_WOB - 1 because the Jig returns the lift-off bar
                and his standing rule is that the consumer adds the wob.

TWO THINGS IN `all-inc` ARE MINE AND ARE FLAGGED IN THE OUTPUT:
    - the lift-off is read on the SAME side as the latch, so a HIGH latch releases when the line
      leaves its HIGH extreme. He said "a lift-off" without naming the side or the line.
    - the wob is LIFT_WOB 8. LIN2_REV_WOB 12 is the other candidate and lineage2 already uses it
      for reversals at v4_lineage2.py:291.

NO MECH IS EDITED. The forward event loop below mirrors v4_l2_proxy._latch's, ties and all, so the
only difference measured is the release set.
"""
import io
import os
import sys
import time

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import v4_knobs as K
import v4_rcfg_sweep as RS
import v4_live_lines as LL
import v4_l2_proxy as PX
import ln
from optimus9.analysis.jig import lift_off
sys.stderr = _e

T0 = time.time()
HI = 20
K.LIN2_PSEUDO_MIN_TF = 99          # the state read is the live line, not the pseudo-closed one
K.LIN2_LATCH_EXFNC_ON = 1

E = RS.load((RS.K0, RS.R0, RS.S0))
MG = LL.mage(HI)
BD = PX.Board(E, E, MG=MG, MGE=MG, PS=None)
N = len(np.asarray(E[1], float))
W = max(1, int(K.LIN2_EXFNC_LATCH_WOB))


def forward(on, off, n):
    """v4_l2_proxy._latch's own loop: ties favour the latch, ON wins at a shared bar."""
    st = np.zeros(n, bool)
    cur, prev = False, 0
    for bb, kind in sorted([(int(x), 0) for x in off] + [(int(x), 1) for x in on]):
        if bb >= n:
            break
        st[prev:bb] = cur
        cur = bool(kind)
        prev = int(bb)
    st[prev:] = cur
    return st


def runs(st):
    """How many times the state turns on, and the mean bars it holds. -> (events, mean bars)."""
    s = np.asarray(st, bool)
    if not s.any():
        return 0, 0.0
    e = np.flatnonzero(np.diff(np.concatenate(([False], s, [False])).astype(np.int8)) == 1)
    f = np.flatnonzero(np.diff(np.concatenate(([False], s, [False])).astype(np.int8)) == -1)
    return len(e), float(np.mean(f - e))


print('# THE EX-FENCE LATCH: THE BANKED RELEASE AGAINST HIS ALL-INCLUSIVE ONE')
print('# TAPE %d bars | %s .. %s | RULED_OK %s' % (N, ln.U(0), ln.U(N - 1), K.RULED_OK))
print('# the latch hold is LIN2_EXFNC_LATCH_WOB %d bars = %d s, both rules.' % (W, W * 5))
print('# the banked release: a barrage on that side, OR an opposite-side ex-fence cross. NOT oob.')
print('# the all-inclusive release: that line\'s own lift-off on the same side, stamped at'
      ' lift + LIFT_WOB - 1 = lift + %d bars.' % (K.LIFT_WOB - 1))
print('# LIFT_PTS %d samples, LIFT_TOL %.1f r-points, LIFT_WOB %d bars - all at the bank.'
      % (K.LIFT_PTS, K.LIFT_TOL, K.LIFT_WOB))

for fnc in (80.0, 75.0):
    K.RMOM_FNC = fnc
    BD._lat = {}; BD._rel = {}          # the caches are keyed per (tf, side); the fence moved
    lo, hi = 100.0 - fnc, fnc
    print('')
    print('## RMOM_FNC %.1f -> (%.1f, %.1f)' % (fnc, lo, hi))
    print('')
    print('| the line | side | bars beyond by VALUE | bars latched, BANKED | bars latched,'
          ' ALL-INCLUSIVE | banked as %% of tape | all-inc as %% of tape | banked latch events |'
          ' banked mean bars on | all-inc latch events | all-inc mean bars on |')
    print('|---|---|---|---|---|---|---|---|---|---|---|')
    agg = {}
    for t in range(1, HI + 1):
        v = np.asarray(E[t], float)
        for side, nm in ((-1, 'LOW'), (+1, 'HIGH')):
            val = np.asarray(K.ex_fence_mask(v, side), bool) & np.isfinite(v)
            bank = np.asarray(BD._latch(t, side), bool)
            on = [int(x) for x in PX.Board._confirm(K.ex_fence_mask(v, side), W)]
            raw = lift_off(v, int(side), K.LIFT_PTS, K.gap_for(int(t)), K.LIFT_TOL, K.LIFT_WOB)
            off = [int(b) + int(K.LIFT_WOB) - 1 for b in raw]
            assert all(o >= 0 for o in off), 'a lift-off stamp is before the tape'
            allin = forward(on, off, N)
            eb, mb = runs(bank)
            ea, ma = runs(allin)
            agg[(t, side)] = (int(val.sum()), int(bank.sum()), int(allin.sum()), eb, ea)
            print('| ws%dr | %s | %d | %d | %d | %.2f%% | %.2f%% | %d | %.1f | %d | %.1f |'
                  % (t, nm, int(val.sum()), int(bank.sum()), int(allin.sum()),
                     100.0 * bank.sum() / N, 100.0 * allin.sum() / N, eb, mb, ea, ma))
    print('')
    print('| the read at RMOM_FNC %.1f | ws1..ws12 | ws1..ws20 |' % fnc)
    print('|---|---|---|')
    for lab, idx in (('summed bars beyond by VALUE', 0), ('summed bars latched, BANKED', 1),
                     ('summed bars latched, ALL-INCLUSIVE', 2),
                     ('latch events, BANKED', 3), ('latch events, ALL-INCLUSIVE', 4)):
        a = sum(agg[(t, s)][idx] for t in range(1, 13) for s in (-1, +1))
        b = sum(agg[(t, s)][idx] for t in range(1, HI + 1) for s in (-1, +1))
        print('| %s | %d | %d |' % (lab, a, b))
    for lab, idx in (('BANKED as %% of all line-side bars', 1),
                     ('ALL-INCLUSIVE as %% of all line-side bars', 2)):
        a = sum(agg[(t, s)][idx] for t in range(1, 13) for s in (-1, +1))
        b = sum(agg[(t, s)][idx] for t in range(1, HI + 1) for s in (-1, +1))
        print('| %s | %.2f%% | %.2f%% |' % (lab, 100.0 * a / (24 * N), 100.0 * b / (2 * HI * N)))

print('')
print('| the read | value |')
print('|---|---|')
print('| seconds to compute | %.1f |' % (time.time() - T0))
