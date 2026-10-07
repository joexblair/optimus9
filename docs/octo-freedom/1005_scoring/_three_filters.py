"""JOE'S THREE PROPOSED FILTERS, measured against the 25 qualifying ws2r bars. Leg 8, 09-25. 1007.

JOE 1007, potential improvements:
  1)  *"we require a floor for the divergence"*            -> a floor on |d_osc|. Value unnamed.
  1a) *"we require the floater to be oob"*                 -> at dr +1 the floater is a HIGH
      (step 3 takes the max on the dr side of 50), so oob = floater r >= 85.
  2)  *"we use a dwell > 12 bars"*                         -> on the ws1Mage 50 dip. 12 bars = 60 s.

THE BASELINE SET: every ws2r reversal in the leg that carries an anchor_floater divergence AND has
ws2x under ws2r. 25 of them. Joe's target is 09:32:15.

d_osc = anchor r - floater r. At dr +1 the anchor is a high and bearish means r makes a LOWER high,
so a real divergence has d_osc < 0 and the FLOOR is on its magnitude.

THE DIP CONFIRM BAR follows oob_ib_cross's own convention: a dip that must hold `dwell` bars is
knowable at dip + dwell - 1, not at the dip bar. Stated, because it moves the gate by 55 s.
"""
import os, io, contextlib, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.analysis.lr_v2 import _mage_rev
from optimus9.analysis.jig import anchor_floater
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC

D = '2026-09-25'; OPEN_TS = '08:10:00'; END_TS = '10:25:00'; DD = 1
PIVOT_TS = '09:28:25'; TARGET_TS = '09:32:15'
REV_WOB = 2
DIP_DWELL = 12                     # Joe's "> 12 bars"; the test below is RUN > 12, strictly
N = len(SC.ts)
K = lambda t: SC.K('%s %s' % (D, t))
R2 = SC.LD(2 * 60, 'r')[:N]; X2 = SC.LD(2 * 60, 'x')[:N]
G1 = SC.MTD['ws1'][:N]; PX = SC.PX[:N]
k0, k1, kp = K(OPEN_TS), K(END_TS), K(PIVOT_TS)
p0 = float(PX[k0])
pct = lambda k: (float(PX[k]) - p0) / p0 * 100.0 * (1 if DD > 0 else -1)
fp = lambda k: (int(SC.ts[k]) - int(SC.ts[kp])) / 60000.0
WANT = -1 if DD > 0 else +1

def box(hdr, rr):
    w = [max(len(hdr[i]), max((len(str(x[i])) for x in rr), default=0)) for i in range(len(hdr))]
    B = lambda s, m, e: s + m.join('─' * (x + 2) for x in w) + e
    print(B('┌', '┬', '┐'))
    print('│' + '│'.join(' ' + hdr[i].center(w[i]) + ' ' for i in range(len(hdr))) + '│')
    print(B('├', '┼', '┤'))
    for x in rr:
        print('│' + '│'.join(' ' + str(x[i]).ljust(w[i]) + ' ' for i in range(len(hdr))) + '│')
    print(B('└', '┴', '┘'))

REV = _mage_rev(R2, REV_WOB)
xund = lambda k: (float(X2[k]) < float(R2[k])) if DD > 0 else (float(X2[k]) > float(R2[k]))
Q = []
for k in range(k0, k1 + 1):
    if REV[k] != WANT or not xund(k): continue
    af = anchor_floater(R2, PX, DD, k)
    if af is None or int(af['fired']) == 0: continue
    fb, fr, fpx = af['floater']
    Q.append(dict(k=k, af=af, fb=int(fb), fr=float(fr), dosc=float(af['d_osc']),
                  dpx=float(af['d_px'])))

print('# THE BASELINE SET — ws2r reversal + divergence + ws2x under ws2r, %d bars' % len(Q))
box(('ts', 'min from pivot', 'ws2r anchor', 'ws2x', 'floater bar', 'floater r', 'floater oob',
     'd_osc', 'abs d_osc', 'd_px', 'pct'),
    [(SC.U(q['k']), '%+.1f' % fp(q['k']), '%.2f' % float(R2[q['k']]), '%.2f' % float(X2[q['k']]),
      SC.U(q['fb']), '%.2f' % q['fr'],
      'Y' if ((q['fr'] >= SC.HI) if DD > 0 else (q['fr'] <= SC.LO)) else '-',
      '%+.2f' % q['dosc'], '%.2f' % abs(q['dosc']), '%+.6f' % q['dpx'], '%+.4f' % pct(q['k']))
     for q in Q])

kt = K(TARGET_TS)
tq = next((q for q in Q if q['k'] == kt), None)
print('\n- the pivot is %s at %+.4f. Joe\'s target %s is %sin the set.'
      % (PIVOT_TS, pct(kp), TARGET_TS, '' if tq else 'NOT '))
if tq:
    print('- at the target: abs d_osc %.2f, floater %s r %.2f (%s), pct %+.4f'
          % (abs(tq['dosc']), SC.U(tq['fb']), tq['fr'],
             'oob' if tq['fr'] >= SC.HI else 'IN-FENCE', pct(tq['k'])))

# ---- 1a: the floater oob filter
oobf = lambda fr: (fr >= SC.HI) if DD > 0 else (fr <= SC.LO)
print('\n# FILTER 1a — THE FLOATER MUST BE OOB')
A = [q for q in Q if oobf(q['fr'])]
box(('bars in', 'bars out', 'first survivor', 'min from pivot', 'pct at it'),
    [[str(len(A)), str(len(Q) - len(A)),
      SC.U(A[0]['k']) if A else '—', '%+.1f' % fp(A[0]['k']) if A else '—',
      '%+.4f' % pct(A[0]['k']) if A else '—']])

# ---- 1: the divergence floor
print('\n# FILTER 1 — A FLOOR ON abs(d_osc).  Does any floor leave the target first?')
rows = []
for fl in (0, 5, 10, 15, 20, 21, 25, 30, 35, 40):
    S = [q for q in Q if abs(q['dosc']) >= fl]
    rows.append((str(fl), str(len(S)), SC.U(S[0]['k']) if S else '—',
                 '%+.1f' % fp(S[0]['k']) if S else '—',
                 '%+.4f' % pct(S[0]['k']) if S else '—',
                 'YES' if (S and S[0]['k'] == kt) else '-'))
box(('abs d_osc floor', 'bars in', 'first survivor', 'min from pivot', 'pct at it',
     'is the target first?'), rows)

# ---- 2: the dip dwell > 12 bars
print('\n# FILTER 2 — THE ws1Mage 50 DIP WITH A DWELL > %d BARS (%d s)'
      % (DIP_DWELL, DIP_DWELL * 5))
indip = (lambda k: float(G1[k]) < 50.0) if DD > 0 else (lambda k: float(G1[k]) > 50.0)
dips = []
for k in range(k0 + 1, k1 + 1):
    if indip(k) and not indip(k - 1):
        n = 0
        while k + n <= N - 1 and indip(k + n):
            n += 1
        dips.append((k, n))
box(('dip bar', 'min from pivot', 'ws1Mage', 'run bars', 'run min', 'dwell > %d?' % DIP_DWELL,
     'confirm bar (dip + dwell - 1)'),
    [(SC.U(k), '%+.1f' % fp(k), '%.2f' % float(G1[k]), str(n), '%.1f' % (n * 5 / 60.0),
      'YES' if n > DIP_DWELL else 'no',
      SC.U(k + DIP_DWELL - 1) if n > DIP_DWELL else '—') for k, n in dips]
    or [('—',) * 7])
ok = [(k, n) for k, n in dips if n > DIP_DWELL]
if ok:
    gate = ok[0][0] + DIP_DWELL - 1
    S = [q for q in Q if q['k'] > gate]
    print('- gate opens at %s (dip %s confirmed after %d bars)'
          % (SC.U(gate), SC.U(ok[0][0]), DIP_DWELL))
    box(('bars after the gate', 'first survivor', 'min from pivot', 'pct at it',
         'is the target first?'),
        [[str(len(S)), SC.U(S[0]['k']) if S else '—', '%+.1f' % fp(S[0]['k']) if S else '—',
          '%+.4f' % pct(S[0]['k']) if S else '—',
          'YES' if (S and S[0]['k'] == kt) else '-']])
else:
    print('- no dip in the leg holds more than %d bars.' % DIP_DWELL)

# ---- the three together
print('\n# ALL THREE TOGETHER')
rows = []
for lbl, S in (('baseline', Q),
               ('1a floater oob', [q for q in Q if oobf(q['fr'])]),
               ('2 dip dwell > 12', [q for q in Q if ok and q['k'] > ok[0][0] + DIP_DWELL - 1]),
               ('1a + 2', [q for q in Q if oobf(q['fr']) and ok
                           and q['k'] > ok[0][0] + DIP_DWELL - 1])):
    rows.append((lbl, str(len(S)), SC.U(S[0]['k']) if S else '—',
                 '%+.1f' % fp(S[0]['k']) if S else '—',
                 '%+.4f' % pct(S[0]['k']) if S else '—',
                 'YES' if (S and S[0]['k'] == kt) else '-'))
box(('filters', 'bars in', 'first survivor', 'min from pivot', 'pct at it',
     'is the target first?'), rows)
print('\n- oob fence %.0f/%.0f; REV_WOB %d steps (carried over, r has no ruled value)'
      % (SC.HI, SC.LO, REV_WOB))
print('- the x-cross exit this leg took: 10:25:00 at %+.4f; the pivot %s at %+.4f'
      % (pct(K('10:25:00')), PIVOT_TS, pct(kp)))
