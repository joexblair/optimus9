"""Joe's proposed lineage start: walk from `no r block` to the next ws2Mage-rev, then start the walk.

JOE 1007: *"re the early fire - I've been toying with walking from `no r block` to the next
ws2mage-rev, then start the lineage walk"*.

MEASURED, NOT ADOPTED. This finds the ws2Mage reversals after the 09-25 19:49:55 `no r block` event
and shows what the lineage and the x-cross condition would do if the walk started there instead of
at ws1 momentum.

THE REVERSAL PRODUCER is jig._mage_rev, the same one score39 uses for g5Mage - `rev_wob` = 2 steps
from lazy_g_config (ws1mage_rev.rev_wob in wsf_dtf_v3_config). It returns a SIGNED flag: +1 = the
line turned UP, -1 = turned DOWN.

WHAT IS NOT SPECIFIED, and is therefore reported both ways rather than chosen:
  - WHICH DIRECTION counts at dr +1. A turn up (+1) or a turn down (-1).
  - whether a FENCE applies to ws2Mage before the reversal counts, as ws1mage-rev uses rev_hi/rev_lo.
"""
import io, contextlib, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.analysis.jig import _mage_rev
import time as _t; _T0 = _t.time()
_P = lambda m: print('# [%5.1fs] %s' % (_t.time() - _T0, m), flush=True)
_P('importing score39 ...')
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC
_P('ready')

D, DR = '2026-09-25', +1
SIG, EX = '19:49:55', '19:46:00'
EXF = 100.0 - float(SC.LG['momo_fence_r'])
M2 = SC.Mg[2]                                  # ws2Mage, already loaded by score39
REV = _mage_rev(M2, int(SC.LG['rev_wob']))
_P('ws2Mage reversals built, rev_wob %d' % int(SC.LG['rev_wob']))

a = SC.K('%s %s' % (D, EX)); b = SC.K('%s 21:10:00' % D)
print('\n# ws2Mage REVERSALS after the g5extrema %s   rev_wob %d steps'
      % (EX, int(SC.LG['rev_wob'])))
print('| ts | +min from %s | direction | ws2Mage | ws2r | band |' % SIG)
print('|---|---|---|---|---|---|')
k0 = SC.K('%s %s' % (D, SIG))
R2 = SC.Rl[2]
band = lambda v: 'O' if v >= SC.HI else ('x' if v >= EXF else '.')
first = {+1: None, -1: None}
for k in range(a, b + 1):
    r = int(REV[k])
    if r == 0: continue
    if first[r] is None and k >= k0: first[r] = k
    print('| %s | %+.1f | %s | %.2f | %.2f | %s |'
          % (SC.U(k), (int(SC.ts[k]) - int(SC.ts[k0])) / 60000.0,
             'UP +1' if r > 0 else 'DOWN -1', float(M2[k]), float(R2[k]), band(float(R2[k]))))

print('\n# IF THE LINEAGE STARTED AT THAT BAR — what holds the tag, and when')
print('| start rule | start bar | +min from the octo-sig | ws1 r there | ws1 band |')
print('|---|---|---|---|---|')
R1 = SC.Rl[1]
for lbl, d in (('next ws2Mage-rev UP', +1), ('next ws2Mage-rev DOWN', -1)):
    k = first[d]
    if k is None:
        print('| %s | — | — | | |' % lbl); continue
    print('| %s | %s | %+.1f | %.2f | %s |'
          % (lbl, SC.U(k), (int(SC.ts[k]) - int(SC.ts[k0])) / 60000.0,
             float(R1[k]), band(float(R1[k]))))

print('\n# THE BARS THAT MATTER ON THIS TRADE, for reference')
for lbl, ts in (('g5extrema', '19:46:00'), ('octo-sig / open', '19:49:55'),
                ('ws1 momentum (current start)', '19:48:00'),
                ('x-cross fires on ws1 (the early fire)', '19:49:00'),
                ('exit-armed', '19:54:00'), ('baton -> ws11 oob', '20:32:35'),
                ('price MFE', '20:34:30'), ('x-cross fires on ws11', '20:45:50'),
                ('stall exit', '20:57:40')):
    k = SC.K('%s %s' % (D, ts))
    print('| %s | %-38s | %+7.1f min | ws2Mage %8.2f | REV %+d |'
          % (ts, lbl, (int(SC.ts[k]) - int(SC.ts[k0])) / 60000.0, float(M2[k]), int(REV[k])))
