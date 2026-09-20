"""report_x_reversal_mage - spec_label 22_go_20260921.

Every ws{tf}x reversal that fires while ws{tf}Mage is SAME-SIDE oob.

JOE'S WORDS, 0920:
    "print all of the ws12x reversals wob6 that fire when ws12Mage is same side oob, for 09-01
     and 09-02"
    then "show the same report based on ws8x and ws8Mage"

SAME SIDE is read as: a -1 down-turn needs ws{tf}Mage >= 85, a +1 up-turn needs ws{tf}Mage <= 15.
oob is 15/85 - Joe 0913, "oob is alwasy 15/85" - NOT the 25/75 Mage fence and NOT the 17/83
r-momo-fence.

THE REVERSAL is the banked producer, jig._Causal.reversal -> lr_v2._mage_rev.  It is boundary
agnostic and confirms after `wob` consecutive same-direction steps; it does NOT require the line
to keep going that way afterwards.  At 09-01 11:50:05 ws12x posts a down-turn at 98.73 and then
climbs to 115.29 before falling through 85.

THE STRETCH COLUMN groups the reversals by the ws{tf}Mage oob excursion they fired inside, because
Joe asked for a wob "that would make that specific reversal the first one to fire".  That wob is
NOT computed here: raising the wob moves a confirmation LATER, it does not filter one in place, so
"the first one" needs a ruling before it can be measured.  Open item, 0920.

    python3 report_x_reversal_mage.py 12
    python3 report_x_reversal_mage.py 8 --wob 6 --from '2026-09-01 00:00:00' --to '2026-09-03 00:00:00'
"""
import argparse
import io
import os
import sys

import numpy as np

sys.stdout, _real = io.StringIO(), sys.stdout
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '_prelude.py')).read()
     .split("k=int(np.searchsorted")[0])
sys.stdout = _real

from optimus9.analysis.jig import _Causal


def oob_side(v, hi, lo):
    """+1 hi oob, -1 lo oob, 0 inside. oob is 15/85."""
    return 1 if v >= hi else (-1 if v <= lo else 0)


def qualifying(x, mage, wob, i0, i1, hi, lo):
    """-> [(bar, turn, side)] for every reversal firing while the Mage is SAME-SIDE oob.

    same side: turn -1 with the Mage hi oob, turn +1 with the Mage lo oob.
    """
    rev = _Causal(None).reversal(x, wob)
    out = []
    for j in range(int(i0), int(i1)):
        if rev[j] == 0:
            continue
        s = oob_side(float(mage[j]), hi, lo)
        if s == 0:
            continue
        if (rev[j] < 0 and s > 0) or (rev[j] > 0 and s < 0):
            out.append((j, int(rev[j]), s))
    return out


def stretch_starts(mage, i0, i1, hi, lo):
    """-> {bar: (side, start_bar)} for every bar the Mage is oob, keyed by its excursion."""
    out, cur = {}, None
    for j in range(int(i0), int(i1)):
        s = oob_side(float(mage[j]), hi, lo)
        if s == 0:
            cur = None
            continue
        if cur is None or cur[0] != s:
            cur = (s, j)
        out[j] = cur
    return out


def main(tf, wob, t_from, t_to):
    x, mage = Ln(tf, 'x'), Ln(tf, 'Mage')
    hi, lo = W.OOB_HI, W.OOB_LO
    i0 = int(np.searchsorted(ts, ms(t_from)))
    i1 = int(np.searchsorted(ts, ms(t_to)))
    q = qualifying(x, mage, wob, i0, i1, hi, lo)
    st = stretch_starts(mage, i0, i1, hi, lo)
    grp = {}
    for j, _t, _s in q:
        grp.setdefault(st[j], []).append(j)

    print('x-reversal with Mage   spec_label 22_go_20260921')
    print('  line             ws%dx, with ws%dMage' % (tf, tf))
    print('  reversal         jig._Causal.reversal, wob %d bars = %d s' % (wob, wob * 5))
    print('  oob              %g/%g' % (lo, hi))
    print('  same side        a -1 down-turn with the Mage >= %g, a +1 up-turn with it <= %g'
          % (hi, lo))
    print('  window           %s -> %s' % (t_from, t_to))
    print('  qualifying       %d reversals in %d Mage oob stretches' % (len(q), len(grp)))
    print('')
    print('  bar                  ws%-2dx    ws%-2dMage  turn   oob stretch start   n in stretch'
          % (tf, tf))
    print('  ' + '-' * 78)
    for j, t, _s in q:
        print('  %s  %8.2f  %9.2f  %-5s  %-18s  %d'
              % (U(j), float(x[j]), float(mage[j]), 'down' if t < 0 else 'up',
                 U(st[j][1])[5:], len(grp[st[j]])))
    return 0


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('tf', type=int)
    p.add_argument('--wob', type=int, default=6)
    p.add_argument('--from', dest='t_from', default='2026-09-01 00:00:00')
    p.add_argument('--to', dest='t_to', default='2026-09-03 00:00:00')
    a = p.parse_args()
    sys.exit(main(a.tf, a.wob, a.t_from, a.t_to))
