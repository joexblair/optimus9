"""THE AGE OF THE LAST SAME-SIDE dtf REVERSAL AT EVERY BARRAGE FIRE. Joe 1027.

    "the data will need to set the lookback window"

HIS TWO SETTLED CONCRETIONS, applied here:
    ws13 is IN - *"ws13 in. my error, should have been >12"*, so the band is ws13..ws30
    the side  - *"dtf reversal side is the same side as the signal"*

NOTHING IS GATED. This reports the age, in minutes, of the most recent same-side reversal above
ws12 at each fire. A window value is whatever he reads off the distribution.

His examples quote ws13/14 by name, so that pair is reported separately from the whole band - if
his eyeball was the pair rather than the band, the two columns will disagree and that is the tell.
"""
import os, sys, io
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
EV = []
for sd in (-1, +1):
    for bar, _t, _w in CAD.barrage(BD, sd, A, B, tol_s=70, lines=6, min_tf=0, fence='any',
                                   fit='off', win_s=0, cand=CD[sd]):
        EV.append((int(bar), int(sd)))
EV.sort()

DTF = [t for t in sorted(BD.tfs) if t > 12]            # his "should have been >12"
revs = {sd: {t: sorted(int(b) for b in F.revs(BD.E[t], t, sd)) for t in DTF} for sd in (-1, +1)}


def last_age(bar, sd, tfs):
    """minutes since the most recent same-side reversal among `tfs`, and which line. -> (mins, tf)."""
    best = None
    for t in tfs:
        prior = [b for b in revs[sd][t] if b <= bar]
        if not prior:
            continue
        if best is None or prior[-1] > best[0]:
            best = (prior[-1], t)
    if best is None:
        return None, None
    return (bar - best[0]) * 5 / 60.0, best[1]


print('# THE LAST SAME-SIDE dtf REVERSAL AT EVERY BARRAGE FIRE, %s .. %s' % (ln.U(A), ln.U(B)))
print('# dtf = ws13..ws%d, his "should have been >12". the side is the SIGNAL side, his ruling.' % DTF[-1])
print('# reversals are EMERGING (reversal timing, his 1026 rule) at LIFT_WOB %d.' % K.LIFT_WOB)
print('# NOTHING IS GATED. the age is in MINUTES before the fire bar; no window is applied.')
print('')
print('| the barrage fire | side | last dtf reversal | age min | the line | last ws13/ws14 only |'
      ' age min | the line |')
print('|---|---|---|---|---|---|---|---|')
AG, AG14 = [], []
for bar, sd in EV:
    a_all, t_all = last_age(bar, sd, DTF)
    a_14, t_14 = last_age(bar, sd, [t for t in (13, 14) if t in revs[sd]])
    if a_all is not None:
        AG.append(a_all)
    if a_14 is not None:
        AG14.append(a_14)
    pa = (lambda a, t, bb: ('%s | %.1f | ws%d' % (ln.U(bb - int(a * 60 / 5)), a, t))
          if a is not None else 'none | - | -')
    print('| %s | %s | %s | %s |'
          % (ln.U(bar), 'HIGH' if sd > 0 else 'LOW', pa(a_all, t_all, bar), pa(a_14, t_14, bar)))

_med = lambda v: sorted(v)[len(v) // 2] if v else float('nan')
print('')
print('| the age read, minutes | whole dtf band | ws13/ws14 only |')
print('|---|---|---|')
print('| events | %d | %d |' % (len(AG), len(AG14)))
print('| median | %.1f | %.1f |' % (_med(AG), _med(AG14)))
print('| shortest | %.1f | %.1f |' % (min(AG), min(AG14)))
print('| longest | %.1f | %.1f |' % (max(AG), max(AG14)))
print('')
print('## how many of the %d fires test#1 BLOCKS at each window' % len(EV))
print('')
print('| the window | whole dtf band blocks | ws13/ws14 only blocks |')
print('|---|---|---|')
for w in (1, 2, 5, 7, 10, 15, 20, 30, 45, 60, 90, 120, 150, 180):
    print('| %d min | %d of %d | %d of %d |'
          % (w, sum(1 for a in AG if a <= w), len(EV),
             sum(1 for a in AG14 if a <= w), len(EV)))
print('')
print('## his three named examples')
print('')
print('| his words | the fire bar | side | last dtf age min | last ws13/14 age min |')
print('|---|---|---|---|---|')
for lbl, ts in (('09-03 0314 - 10 min acceptable', '2026-09-03 03:14:00'),
                ('09-03 0714 - 10 min suits', '2026-09-03 07:14:00'),
                ('09-03 0226 - last was ~150 min earlier', '2026-09-03 02:26:00')):
    k = ln.K(ts)
    bar, sd = min(EV, key=lambda z: abs(z[0] - k))
    a_all, t_all = last_age(bar, sd, DTF)
    a_14, t_14 = last_age(bar, sd, [t for t in (13, 14) if t in revs[sd]])
    print('| %s | %s | %s | %.1f on ws%d | %s |'
          % (lbl, ln.U(bar), 'HIGH' if sd > 0 else 'LOW', a_all, t_all,
             ('%.1f on ws%d' % (a_14, t_14)) if a_14 is not None else 'none'))
