"""THE dtf STATE AT EVERY BARRAGE FIRE. Joe 1027's test#1 and test#2 inputs. Measures only."""
import os, sys, io
import numpy as np
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln, v4_knobs as K, v4_rcfg_sweep as RS, v4_fast as F
import v4_closed_prev as CP, v4_l2_proxy as PX, v4_l2_cadence as CAD
sys.stderr = _e

A, B = ln.K('2026-08-30 00:00:00'), ln.K('2026-09-06 23:59:55')
E = RS.load((RS.K0, RS.R0, RS.S0))
BD = PX.Board(CP.ladder(E), E, MGE={t: ln.line('ws%dMage' % t) for t in range(1, 13)})
CD = {sd: CAD.barrage_candidates(BD, sd) for sd in (-1, +1)}

#   the event set he is validating: the 28 at tol 70 / lines 6 / floor off / window as built.
#   the 24 he was shown are the subset carrying a ws9+ line - flagged per row.
EV = []
for sd in (-1, +1):
    for bar, _t, why in CAD.barrage(BD, sd, A, B, tol_s=70, lines=6, min_tf=0, fence='any',
                                    fit='off', win_s=0, cand=CD[sd]):
        top = int(why.split('top ws')[1].split(' -')[0])
        EV.append((int(bar), int(sd), top))
EV.sort()

DTF = [t for t in sorted(BD.tfs) if t >= 13]
WINS = (60, 300, 600, 1800, 3600)                  # candidate "recently" windows - NOT a ruling
revs = {sd: {t: sorted(int(b) for b in F.revs(BD.E[t], t, sd)) for t in DTF} for sd in (-1, +1)}

print('# THE dtf STATE AT EVERY BARRAGE FIRE, %s .. %s' % (ln.U(A), ln.U(B)))
print('# the event set is tol 70 / lines 6 / floor off / window as built = 28 events.')
print('# dtf = ws13..ws%d, his 1017 band name for >ws12. NOTHING IS GATED HERE - this measures.' % DTF[-1])
print('# reversals are EMERGING (reversal timing), fences are CLOSED (state) - his 1026 rule.')
print('# the "recently" windows are candidates for his knob, not a ruling: %s s'
      % ', '.join(str(w) for w in WINS))
print('')
print('| the fire bar | side | top wsf | in the 24 | dtf reversed SAME side within 60/300/600/1800/3600 s |'
      ' dtf ex-fence SAME side at fire | dtf ex-fence OPPOSITE side at fire |')
print('|---|---|---|---|---|---|---|')
for bar, sd, top in EV:
    same = []
    for w in WINS:
        lo = bar - w // 5
        same.append(','.join('ws%d' % t for t in DTF if any(lo <= b <= bar for b in revs[sd][t]))
                    or '-')
    exs = ','.join('ws%d' % t for t in DTF if BD.ex_fence(t, bar, sd)) or '-'
    exo = ','.join('ws%d' % t for t in DTF if BD.ex_fence(t, bar, -sd)) or '-'
    print('| %s | %s | ws%d | %s | %s | %s | %s |'
          % (ln.U(bar), 'HIGH' if sd > 0 else 'LOW', top, 'yes' if top >= 9 else 'no',
             ' // '.join(same), exs, exo))

print('')
print('## his four named examples, checked')
print('')
print('| his words | the nearest fire bar | side | what the data shows |')
print('|---|---|---|---|')
for lbl, ts in (('test#1 blocks 08-31 1432', '2026-08-31 14:32:00'),
                ('test#1 blocks 08-31 1832', '2026-08-31 18:32:00'),
                ('test#2 blocks 08-30 0234', '2026-08-30 02:34:00'),
                ('test#2 blocks 08-30 1906', '2026-08-30 19:06:00')):
    k = ln.K(ts)
    n = min(EV, key=lambda z: abs(z[0] - k))
    bar, sd, _tp = n
    r600 = ','.join('ws%d' % t for t in DTF
                    if any(bar - 120 <= b <= bar for b in revs[sd][t])) or 'none'
    exs = ','.join('ws%d' % t for t in DTF if BD.ex_fence(t, bar, sd)) or 'none'
    print('| %s | %s (%+d s) | %s | dtf reversed same side in 600 s: %s \\| dtf ex-fence same side: %s |'
          % (lbl, ln.U(bar), (bar - k) * 5, 'HIGH' if sd > 0 else 'LOW', r600, exs))
