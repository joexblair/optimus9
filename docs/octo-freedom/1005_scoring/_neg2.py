"""THE FIRST 2 ARM-8 LEGS WITH A NEGATIVE ENTRY. 1008.

Joe 1008: *"show me the first 2 arm 8 negative on net"*.

NEGATIVE ON NET = the turn walk landed the entry on the WRONG side of the open pxs, so `entry
better by %` is negative. By Joe's test that is the walk facing the wrong direction. The legs are
taken in CHAIN ORDER and the first 2 are printed, picked from the run and not transcribed.

Arm 8 is the TURN walk at `ent_rev_wob` 4 on frame `dr`: no ws2Mage arm, no baton, no oob
requirement - the walk watches ws1r and lands on its first turn against the walk's travel.

PER LEG, TWO BLOCKS, BOTH ONE RECORD PER ROW:
  1  ws1r bar by bar from the open to the landing, with the turn flag and the entry it gives
  2  the leg's own timestamped decisions, from WALK STARTS to EXIT
"""
import os, sys, datetime
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
import _chain_2day as T
import _nakedchain as NK

SC, PX, box = C.SC, C.PX, C.box
R = C.R
N = len(SC.ts); U = SC.U
HI, LO = SC.HI, SC.LO
EXF_LO = float(SC.LG['momo_fence_r']); EXF_HI = 100.0 - EXF_LO
R1 = R[1]
REV1 = NK.REV1T
WOB = NK.TURN_WOB
DAYOF = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                  datetime.timezone.utc).strftime('%Y-%m-%d')

def fen(v, d):
    if d > 0: return 'hi oob' if v >= HI else ('hi ex-f' if v >= EXF_HI else 'in-fence')
    return 'lo oob' if v <= LO else ('lo ex-f' if v <= EXF_LO else 'in-fence')

rows_ = NK.run_chain_naked(T.gate_A, 'end', 'turn_dr')
legs = [r for r in rows_ if not r['brk']]
neg = [r for r in legs if r['imp'] < 0]
print('# arm 8, ent_rev_wob %d, frame dr — %d legs, %d with a NEGATIVE entry'
      % (WOB, len(legs), len(neg)))
box(('leg', 'side', 'the walk starts', 'frame', 'entry bar', 'naked min', 'entry better by %',
     'exit', 'why'),
    [(str(r['leg']), r['side'], '%s %s' % (DAYOF(r['walkfrom'])[5:], U(r['walkfrom'])),
      '%+d' % r['frame'], U(r['land']), '%.1f' % r['naked'], '%+.4f' % r['imp'],
      U(r['exit']), r['why']) for r in neg])

for r in neg[:2]:
    k, lb, xk, d, fr = r['walkfrom'], r['land'], r['exit'], r['d'], r['frame']
    P0 = float(PX[k]); pe = float(PX[lb]); sgn = r['d']
    want = NK.WANT_TURN(fr)
    mn = lambda j: '%+.1f' % ((int(SC.ts[j]) - int(SC.ts[k])) / 60000.0)
    ent = lambda j: (P0 - float(PX[j])) / P0 * 100.0 * sgn
    ps = lambda j: '%+.4f' % ((float(PX[j]) - P0) / P0 * 100.0 * sgn)
    pz = lambda j: '%+.4f' % ((float(PX[j]) - pe) / pe * 100.0 * sgn)

    print('\n\n' + '=' * 78)
    print('## LEG %d — %s   the walk starts %s %s   pxs %.6f   frame dr %+d   turn wanted %s'
          % (r['leg'], r['side'], DAYOF(k)[5:], U(k), P0, fr, 'UP' if want > 0 else 'DOWN'))
    print('=' * 78)

    print('\n# ws1r BAR BY BAR, THE OPEN TO THE LANDING')
    tbl = []; prev = None
    for j in range(k, lb + 1):
        v = float(R1[j])
        tbl.append((U(j), mn(j), '%.2f' % v,
                    '—' if prev is None else '%+.2f' % (v - prev),
                    fen(v, fr),
                    ('TURN %s' % ('UP' if int(REV1[j]) > 0 else 'DOWN')) if int(REV1[j]) else '',
                    '%.6f' % float(PX[j]), '%+.4f' % ent(j)))
        prev = v
    box(('ts', '+min', 'ws1r', 'ws1r step', 'ws1r on frame %+d' % fr, 'reversal',
         'pxs', '%s entry better by %%' % r['side']), tbl)
    bidx = int(np.argmin([float(PX[j]) for j in range(k, lb + 1)])) if sgn > 0 \
        else int(np.argmax([float(PX[j]) for j in range(k, lb + 1)]))
    bb = k + bidx
    box(('the question', 'the answer'),
        [('the best %s pxs in the span' % r['side'],
          '%.6f at %s, entry %+.4f' % (float(PX[bb]), U(bb), ent(bb))),
         ('the landing pxs', '%.6f at %s, entry %+.4f' % (pe, U(lb), ent(lb))),
         ('the open bar already the best?', 'YES' if bb == k else 'no — the best is %s' % U(bb)),
         ('ws1r at the open', '%.2f, %s on frame %+d' % (float(R1[k]), fen(float(R1[k]), fr), fr)),
         ('ws1r at the landing turn',
          '%.2f, %s on frame %+d' % (float(R1[lb]), fen(float(R1[lb]), fr), fr)),
         ('did ws1r reach the frame\'s oob fence before turning?',
          'YES' if any(C.oobf(1, j, fr) for j in range(k, lb + 1)) else
          'NO — weak, and weak lets pxs climb')])

    print('\n# THE LEG\'S TIMESTAMPED DECISIONS')
    _, why, mae, cb, hand, tr2 = C.run_leg(lb, d)
    tbl = [(U(k), '+0.0', 'WALK STARTS — naked, nothing open', '%.6f' % P0, '+0.0000', '—')]
    tbl += [(U(lb), mn(lb), 'LANDING — %s' % r['lw'], '%.6f' % pe, ps(lb), '—')]
    tbl += [(U(lb), mn(lb), 'ENTER %s' % r['side'], '%.6f' % pe, ps(lb), '+0.0000')]
    tbl += [(U(j), mn(j), lab, '%.6f' % float(PX[j]), ps(j), pz(j)) for j, lab in tr2]
    tbl += [(U(xk), mn(xk), 'EXIT — %s' % why, '%.6f' % float(PX[xk]), ps(xk), pz(xk))]
    box(('ts', '+min', 'event', 'pxs', 'pct from the walk start', 'pct from entry'), tbl)
    print('- pct from the walk start is NOT P&L above the ENTER row - nothing is open while the')
    print('  walk walks. The leg realised %+.4f from its entry.' % r['real'])
