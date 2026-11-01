"""Which lines print a LOW-side reversal between two bars. The producer is v4_fast.revs - the same
call v4_l2_proxy.rev_stamps makes - and the stamp is K.lift_stamp, so the bar reported here is the
bar the chain may act on. No oob filter on the detector (Joe 1023); the oob read is a COLUMN."""
import os, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
import ln
import v4_knobs as K
import v4_fast as F

A, B = ln.K(sys.argv[1]), ln.K(sys.argv[2])
print('tape bars %d | span bars %d | A %s | B %s' % (ln.N, B - A + 1, ln.U(A), ln.U(B)))
print('| knob | value |'); print('|---|---|')
for n in ('OOB_FNC', 'OOB_HI', 'OOB_LO', 'RMOM_FNC', 'LIFT_PTS', 'LIFT_TOL', 'LIFT_WOB',
          'GAP_PER_TF', 'L2_MOM_MAXTF'):
    print('| %s | %s |' % (n, getattr(K, n, 'NOT DECLARED')))
print()
TFS = []
for tf in range(1, 31):
    try:
        ln.line('ws%dr' % tf); TFS.append(tf)
    except Exception:
        pass
print('r lines on disk: ' + ' '.join('ws%dr' % t for t in TFS))
print()
print('| the raw lift-off bar | the line | its value there | the stamp | in-span by raw | in-span by stamp | oob-low at the raw bar? | the oob-low run holding it |')
print('|---|---|---|---|---|---|---|---|')
rows = []
for tf in TFS:
    a = ln.line('ws%dr' % tf)
    for b in F.revs(a, tf, -1):
        b = int(b); st = int(K.lift_stamp(b))
        if not (A <= b <= B or A <= st <= B):
            continue
        rh = F.run_holding(a, tf, -1, b)
        rows.append((b, tf, a[b], st,
                     'YES' if A <= b <= B else 'no',
                     'YES' if A <= st <= B else 'no',
                     'YES' if rh else 'no',
                     '%s to %s' % (ln.U(rh[0]), ln.U(rh[1])) if rh else '-'))
for b, tf, v, st, ir, isx, o, rr in sorted(rows):
    print('| %s | ws%dr | %.2f | %s | %s | %s | %s | %s |'
          % (ln.U(b), tf, v, ln.U(st), ir, isx, o, rr))
print()
print('| the read | value |'); print('|---|---|')
print('| r lines carrying a low-side reversal in the span | %d |' % len({r[1] for r in rows}))
print('| low-side reversals in the span | %d |' % len(rows))
