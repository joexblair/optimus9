"""ws13r REVERSALS ACROSS HIS 08-31 PIVOT SEQUENCE, PER WOB OPTION. Joe 1027/1028:

    "on 08-31, travel between each of these pivots: 0055, 0256, 0744, 1023, 1119, 1353
     -if you see reversals at 0353, 0417, 1154, 1211, that's acceptable
     the conditions are the same: the first reversal after the pivot, and no early reversals
     between the pivots."

PER LEG (P_i -> P_i+1), PER OPTION, PER SIDE:
    EARLY        a reversal stamped strictly between the two pivots - a violation, unless it falls
                 within +/-5 min of one of his four acceptable times, which is then marked
    FIRST AFTER  the first reversal stamped at or after the closing pivot, and its gap

HIS FOUR ACCEPTABLE TIMES are 03:53, 04:17, 11:54, 12:11. The +/-5 min is HIS OWN standing note
that his times are estimates; it is not a tolerance invented for this run.

BOTH SIDES ARE REPORTED. He named the side only for the 1443 instance, and a pivot's side is his
chart read, not something to derive here.

1353 -> 1443 CLOSES THE SEQUENCE using the 1443 pivot from the earlier run, so the last leg is not
left open. That is stated, not assumed silently.
"""
import os, sys, io
import numpy as np
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln, v4_knobs as K, v4_rcfg_sweep as RS, v4_closed_prev as CP
from optimus9.analysis.jig import lift_off
sys.stderr = _e

DAY = '2026-08-31'
PIV = ['00:55', '02:56', '07:44', '10:23', '11:19', '13:53', '14:43']
OK_T = ['03:53', '04:17', '11:54', '12:11']
TOLB = 60                                           # +/-5 min in 5 s bars - his own estimate note
P = [ln.K('%s %s:00' % (DAY, s)) for s in PIV]
OKB = [ln.K('%s %s:00' % (DAY, s)) for s in OK_T]
em = np.asarray(RS.load((RS.K0, RS.R0, RS.S0))[13], float)
cl = CP.series(em, 13 * 60)
OPTS = [('wob 8 BANKED', em, 8), ('wob 20', em, 20), ('wob 32', em, 32),
        ('wob 39 = T/4', em, 39), ('closed wob 8', cl, 8)]
REV = {}
for nm, line, w in OPTS:
    for sd in (-1, +1):
        REV[(nm, sd)] = sorted(int(b) + w - 1 for b in
                               lift_off(line, sd, K.LIFT_PTS, K.gap_for(13), K.LIFT_TOL, int(w)))

print('# ws13r REVERSALS ACROSS HIS %s PIVOT SEQUENCE' % DAY)
print('# pivots: %s. his acceptable reversals: %s (+/-5 min, his own estimate note).'
      % (', '.join(PIV), ', '.join(OK_T)))
print('# a reversal is at its STAMP - raw + wob - 1, the bar it is actionable on.')
print('# 1353 -> 1443 closes the sequence with the 1443 pivot from the earlier run.')
print('# BOTH SIDES are reported: a pivot\'s side is his chart read. RULED_OK %s' % K.RULED_OK)
print('')
print('| the leg | side | the option | early reversals between the pivots | verdict |'
      ' first reversal after the closing pivot | its gap |')
print('|---|---|---|---|---|---|---|')
SUM = {}
for i in range(len(P) - 1):
    a, b = P[i], P[i + 1]
    leg = '%s -> %s' % (PIV[i], PIV[i + 1])
    for sd in (-1, +1):
        for nm, line, w in OPTS:
            r = REV[(nm, sd)]
            early = [x for x in r if a < x < b]
            exempt = [x for x in early if any(abs(x - o) <= TOLB for o in OKB)]
            bad = [x for x in early if x not in exempt]
            after = [x for x in r if x >= b]
            vd = ('clean' if not early else
                  ('acceptable' if not bad else 'TURNED BACK x%d' % len(bad)))
            k = (nm, sd)
            s = SUM.setdefault(k, [0, 0, 0, []])
            s[0] += 1
            if not bad:
                s[1] += 1
            s[2] += len(bad)
            gap = ('%+.1f min' % ((after[0] - b) * 5 / 60.0)) if after else '-'
            if after:
                s[3].append((after[0] - b) * 5 / 60.0)
            print('| %s | %s | %s | %s | %s | %s | %s |'
                  % (leg, 'LOW' if sd < 0 else 'HIGH', nm,
                     ', '.join(ln.U(x)[11:] for x in early) or 'none', vd,
                     ln.U(after[0]) if after else 'none to the data end', gap))

_med = lambda v: sorted(v)[len(v) // 2] if v else float('nan')
print('')
print('| side | the option | legs | legs with no turn-back | unwanted early reversals |'
      ' median gap after the pivot |')
print('|---|---|---|---|---|---|')
for sd in (-1, +1):
    for nm, _l, _w in OPTS:
        s = SUM[(nm, sd)]
        print('| %s | %s | %d | %d of %d | %d | %s |'
              % ('LOW' if sd < 0 else 'HIGH', nm, s[0], s[1], s[0], s[2],
                 '%+.1f min' % _med(s[3]) if s[3] else '-'))
