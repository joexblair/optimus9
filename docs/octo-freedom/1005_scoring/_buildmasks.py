"""BUILD THE MOMENTUM MASK FOR EVERY LINE ws1-ws23. 1009.

Joe 1009: *"before a line stalls, momentum is true regardless of where it is on the board. if a
lin_hop line has momentum, lineage needs to make that line the rider"*, and his 1006 spec row
*"jump no more than 2 higher TFs to find the next TF with momentum"* - the clause the baton's
candidate test never implemented.

The baton needs to ask "does this line have momentum at this bar" once per candidate per bar, so
the answer has to be precomputed. One line is ~255 s, so all 23 is ~1 h 40 m, once, then cached.

A CONTROL IS PRINTED PER LINE: the share of bars that are mom-true. ws2 measured 26.82% / 26.96%
on 1009 before this run. If a later run of the same TF prints a different share, the cache or the
bank moved and the number must not be trusted.
"""
import os, sys, time
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
from _momtrue import momtrue_mask
from optimus9.orchestration.build_ws_lines import HOURS, WARMUP

N = len(C.SC.ts)
TFS = [t for t in C.ALL_TF]
print('# building momentum masks for %d lines: %s' % (len(TFS), ', '.join('ws%d' % t for t in TFS)),
      flush=True)
print('# tape %d bars, mom-true is momo OR curl, curl gates ON, strip-at-fence OFF\n' % N,
      flush=True)
t00 = time.time()
rows = []
for i, t in enumerate(TFS, 1):
    t0 = time.time()
    m = momtrue_mask(C.RL[t], t, C.BANK[t], C.SC.EM, HOURS, WARMUP, 'gated', N,
                     log=lambda s: None)
    rows.append((t, 100.0 * m[+1].sum() / N, 100.0 * m[-1].sum() / N, time.time() - t0))
    print('# %2d of %d  ws%-3d  mom-true  LONG %5.2f%%  SHORT %5.2f%%  (%4.0f s, %5.1f min total)'
          % (i, len(TFS), t, rows[-1][1], rows[-1][2], rows[-1][3], (time.time() - t00) / 60.0),
          flush=True)
print('\n# ALL %d DONE in %.1f min' % (len(TFS), (time.time() - t00) / 60.0))
C.box(('the line', 'mom-true LONG', 'mom-true SHORT', 'build seconds'),
      [('ws%d' % t, '%.2f%%' % a, '%.2f%%' % b, '%.0f' % c) for t, a, b, c in rows])
print('- CONTROL: ws2 measured 26.82%% LONG / 26.96%% SHORT on 1009. A different number here means')
print('  the cache or the bank moved.')
