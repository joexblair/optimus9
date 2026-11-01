"""v4_lineage_trace.walk from EVERY start rung, under each baton-pass mode. One driver.

WHY. Joe gave an armed event, not a rider timeframe. The start rung decides the whole walk: from
ws1 all three modes exhaust at the ws1 -> ws2 gate inside a minute. This runs the SAME walk()
function - not a second copy of it - across every rung so the anchor is his to pick.

K.LIN_PASS IS SET ON THE MODULE between runs. The walk reads it through K, so this is the same code
path the env var takes; nothing is re-implemented.

usage: baton_rungs.py '<A>' '<B>' <high|low>
"""
import io, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
import ln
import v4_knobs as K
import v4_lineage_trace as T

A, B = ln.K(sys.argv[1]), ln.K(sys.argv[2])
SIDE = 1 if sys.argv[3] == 'high' else -1
MODES = ('ib', 'reversal', 'reversal+quarter')
TOP = 30
R = {t: ln.line('ws%dr' % t) for t in range(1, TOP + 1)}
print('# A %s  B %s  side %s' % (ln.U(A), ln.U(B), sys.argv[3]))
print('# RULED_OK %s. ib dwell int(TF x %.1f), oob %.1f/%.1f, ex-fence %s, ceiling ws%d'
      % (K.RULED_OK, K.LIN_IB_DWELL, K.OOB_LO, K.OOB_HI, K.fence(), K.TF_CEILING))
print('# quarter width = %.2f x TF x 12 bars: ws22 -> %d bars = %d s'
      % (K.LIN_PASS_QUARTER, K.lin_quarter_tf(22), K.lin_quarter_tf(22) * 5))
print()
print('| the start rung | the mode | the verdict | the verdict bar | baton passes | the top rung reached | the first reversal bar |')
print('|---|---|---|---|---|---|---|')
for t0 in range(1, TOP + 1):
    for m in MODES:
        K.LIN_PASS = m
        buf = io.StringIO()
        v, b, rows = T.walk(R, t0, SIDE, A, B, log=lambda s: buf.write(s + '\n'))
        passes = sum(1 for r in rows if 'takes the baton' in r[0] or 'second-new-rider' in r[0])
        tops = [int(r[0].split('ws')[1].split()[0].rstrip(',').split('-')[0])
                for r in rows if 'ws' in r[0] and r[0].split('ws')[1][:1].isdigit()]
        fr = next((r[1] for r in rows if 'is the rider and reverses' in r[0]), '-')
        print('| ws%d | %s | %s | %s | %d | ws%d | %s |'
              % (t0, m, v, ln.U(b) if b else '-', passes, max(tops) if tops else t0, fr))
