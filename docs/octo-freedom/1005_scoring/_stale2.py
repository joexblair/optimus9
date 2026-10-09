"""THE EARLIEST-TO-LATEST DIFF AS A TIE-BREAKER, AND C2 RE-BANDED. 1009.

Joe 1009: *"increase the samples to 3 * TF. then we can look at the diff between the latest and the
earliest sample - they could be a tie breaker if there is a positive (UP) or negative (DOWN)
diff"*, and *"I see the lower wsf lines as ws1 to ws3/ws4. the smaller lines of the wsf group"*.

THE ARITHMETIC, from `_trajmech`'s own spec: `look_n` is the lookback IN SAMPLES and Joe 1008 set it
as *"({knob:2,'TRAJ_MULTI_TF_SAMP'} * TF-width)"* - 2 x the trigger TF 12 = the 24 in force. So
"3 * TF" raises that knob to 3: 3 x 12 = 36 samples, 180.0 min at the 5.0-min block.

The tie-breaker read is sample[0] - sample[look_n-1]: the WHOLE span, not the tail, and not
truncated by the reversal. Positive -> UP, negative -> DOWN.
"""
import os, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
from _trajmech import traj, sample_series

SC, box, U = C.SC, C.box, C.SC.U
N = len(SC.ts); HI, LO = SC.HI, SC.LO
R60 = np.asarray(SC.LD(60 * 60, 'r'), float)[:N]
M60 = np.asarray(SC.LD(60 * 60, 'Mage'), float)[:N]
BL = C.TRAJ_BLOCK * 5 / 60.0
MULT = int(os.environ.get('X_MULT', 3)); TFW = C.TRIG_TF
LOOK = MULT * TFW
sg = lambda z: 0 if z == 0 else (1 if z > 0 else -1)
NM = {0: 'TIED 0', 1: 'UP +1', -1: 'DOWN -1'}
TIES = [('2026-08-23 01:28:15', +1), ('2026-08-23 20:54:05', -1)]

print('# TRAJ_MULTI_TF_SAMP %d x TF-width %d = look_n %d samples = %.1f min at the %.1f-min block'
      % (MULT, TFW, LOOK, LOOK * BL, BL), flush=True)
print('# in force today: 2 x 12 = 24 samples = %.1f min\n' % (24 * BL), flush=True)

for ts, d in TIES:
    k = SC.K(ts)
    print('\n########## %s   leg dr %+d   THE VOTE TIES 4-4' % (ts, d))
    rows = []
    for ln in (24, LOOK):
        s = sample_series(R60, k, C.TRAJ_BLOCK, ln, C.TRAJ_KIND, d)
        if len(s) < 2: continue
        v = [x[1] for x in s]
        df = v[0] - v[-1]
        t = traj(R60, k, C.TRAJ_BLOCK, C.TRAJ_TAIL, ln, C.TRAJ_KIND, d)
        rows.append(('%d samples = %.1f min%s' % (ln, ln * BL, ' <- "3 * TF"' if ln == LOOK else
                                                  ' <- in force'),
                     str(len(s)), U(s[0][0]), '%.4f' % v[0], U(s[-1][0]), '%.4f' % v[-1],
                     '%+.4f' % df, NM[sg(df)],
                     'AGAINST dr' if sg(df) == -d else ('MATCHES dr' if sg(df) == d else 'tied'),
                     '%+.4f' % t['travel'] if np.isfinite(t['travel']) else 'n/a', NM[t['dir']]))
    box(('the lookback', 'samples taken', 'the LATEST bar', 'ws60r there', 'the EARLIEST bar',
         'ws60r there', 'latest - earliest', 'the tie-breaker says', 'vs the oob side',
         'travel over the tail', 'travel dir'), rows)
    # the Mage over the same span, as a beacon level - Joe: not its diffs
    s = sample_series(R60, k, C.TRAJ_BLOCK, LOOK, C.TRAJ_KIND, d)
    g = [float(M60[b]) - float(R60[b]) for b, _ in s]
    box(('the beacon over the %d-sample span' % LOOK, 'value'),
        [('Mage-r at the latest sample', '%+.4f' % g[0]),
         ('Mage-r at the earliest sample', '%+.4f' % g[-1]),
         ('how many of the %d samples have the Mage ABOVE r' % len(g),
          '%d = %.0f%%' % (sum(1 for z in g if z > 0), 100.0 * sum(1 for z in g if z > 0) / len(g))),
         ('median Mage-r', '%+.4f' % float(np.median(g))),
         ('min / max', '%+.4f / %+.4f' % (min(g), max(g)))])

print('\n\n########## C2 RE-BANDED — "the lower wsf lines as ws1 to ws3/ws4"')
k = SC.K(TIES[0][0])
for band in ((1, 3), (1, 4)):
    sel = list(range(band[0], band[1] + 1))
    rows = []
    for t in sel:
        r = np.asarray(C.R[t], float)[:N]
        was = np.flatnonzero(r[:k + 1] >= HI)
        rows.append(('ws%dr' % t, '%.2f' % float(r[k]),
                     '%.1f' % ((k - int(was[-1])) * 5 / 60.0) if len(was) else 'never',
                     U(int(was[-1])) if len(was) else '—',
                     'yes' if float(r[k]) >= HI or float(r[k]) <= LO else 'no'))
    mins = [(k - int(np.flatnonzero(np.asarray(C.R[t], float)[:k + 1] >= HI)[-1])) * 5 / 60.0
            for t in sel]
    vals = [float(C.R[t][k]) for t in sel]
    print('\n# ws%d-ws%d at %s' % (band[0], band[1], TIES[0][0]))
    box(('the line', 'r now', 'min since last HI oob (>=%.0f)' % HI, 'that bar', 'oob right now?'),
        rows)
    box(('the band ws%d-ws%d' % (band[0], band[1]), 'value'),
        [('min since HI oob — least', '%.1f min' % min(mins)),
         ('min since HI oob — median', '%.1f min' % float(np.median(mins))),
         ('min since HI oob — most', '%.1f min' % max(mins)),
         ('r now — min / median / max', '%.2f / %.2f / %.2f'
          % (min(vals), float(np.median(vals)), max(vals))),
         ('how many oob right now', '%d of %d' % (sum(1 for z in vals if z >= HI or z <= LO),
                                                  len(vals)))])
