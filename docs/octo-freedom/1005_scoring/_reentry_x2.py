"""THE RE-ENTRY CROSS: ex-r-momo-fence instead of oob, and read at COUNTER-dr. 09-25. 1007.

Joe 1007: *"we could make it ex-r-momo-fence instead of oob"* / *"at 11:12, the mage ladder isn't
present. come to think of it, 11:12 isn't a best-placed cross for +dr - the test should be at
counter-dr for maximised results"*.

  the fence     oob is oob_hi/oob_lo 85/15. The EX-FENCE is 100-momo_fence_r / momo_fence_r = 83/17.
                So the low gate moves from ws1r <= 15 to ws1r <= 17.
  counter-dr    Joe's ruling: dr +1 = towards dr = LONG. A LONG re-entry is COUNTER-dr when the
                bar's dr is -1. Both his bars are LONG reads, so counter-dr means dr -1 at the bar.
  xwob 6        measured better than 8 - the 11:19:05 cross holds 6 bars, not 8.

Joe's two hand-picked bars: 08:10:00 and 11:21:00.
"""
import sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
SC, PX, box = C.SC, C.PX, C.box
R1, X1 = C.R[1], C.X[1]
N = len(SC.ts)
DRv = (SC.DR if hasattr(SC, 'DR') else SC.DRv)[:N]
EXF_LO = float(SC.LG['momo_fence_r'])          # 17
K = lambda t: SC.K('2026-09-25 %s' % t)
d0, d1 = K('00:00:00'), K('23:59:55')
XWOB = 6

v = (X1 > R1) & np.isfinite(X1) & np.isfinite(R1)
idx = np.arange(N)
run = (idx + 1) - np.maximum.accumulate(np.where(v, 0, idx + 1))
held = run >= XWOB
confm = held & ~np.r_[False, held[:-1]]
CX = [(int(c) - (XWOB - 1), int(c)) for c in np.flatnonzero(confm)
      if int(c) - (XWOB - 1) >= 1 and d0 <= int(c) - (XWOB - 1) <= d1]

print('# THE GATE, FOUR WAYS — xwob %d, ws1x crossing over ws1r, on 09-25' % XWOB)
rows = []
for lbl, fn in (('no gate', lambda k: True),
                ('ws1r <= 15 (oob)', lambda k: float(R1[k]) <= SC.LO),
                ('ws1r <= 17 (ex-fence)', lambda k: float(R1[k]) <= EXF_LO),
                ('ws1r <= 17 AND dr -1 (counter-dr)',
                 lambda k: float(R1[k]) <= EXF_LO and int(DRv[k]) < 0),
                ('dr -1 only', lambda k: int(DRv[k]) < 0)):
    s = [z for z in CX if fn(z[0])]
    rows.append((lbl, str(len(s)), '%.1f' % (len(s) / 24.0)))
box(('gate at the cross bar', 'crosses on 09-25', 'per hour'), rows)

print('\n# JOE\'S TWO BARS — the lines and the dr at each')
box(('bar', 'ws1r', '<= 15?', '<= 17?', 'dr', 'counter-dr for a LONG?', 'pxs'),
    [(ts, '%.2f' % float(R1[K(ts)]),
      'Y' if float(R1[K(ts)]) <= SC.LO else '-',
      'Y' if float(R1[K(ts)]) <= EXF_LO else '-',
      '%+d' % int(DRv[K(ts)]),
      'YES' if int(DRv[K(ts)]) < 0 else 'no — it is towards dr',
      '%.6f' % float(PX[K(ts)])) for ts in ('08:10:00', '11:12:45', '11:19:30', '11:21:00',
                                            '11:22:30')])

print('\n# EVERY CROSS IN THE TWO RE-ENTRY WINDOWS, WITH THE GATES AND THE dr')
for a_, b_ in (('07:30:00', '08:30:00'), ('11:00:00', '11:40:00')):
    s = [z for z in CX if K(a_) <= z[1] <= K(b_)]
    print('\n## %s to %s' % (a_, b_))
    box(('cross bar', 'conf bar', 'ws1r at cross', '<= 15?', '<= 17?', 'dr at cross',
         'counter-dr?', 'pxs at conf'),
        [(SC.U(k), SC.U(c), '%.2f' % float(R1[k]),
          'Y' if float(R1[k]) <= SC.LO else '-',
          'Y' if float(R1[k]) <= EXF_LO else '-',
          '%+d' % int(DRv[k]), 'Y' if int(DRv[k]) < 0 else '-',
          '%.6f' % float(PX[c])) for k, c in s] or [('—',) * 8])

print('\n# UNDER ws1r <= 17 AND dr -1: THE FIRST CROSS AFTER EACH CHAIN STOP')
G = [z for z in CX if float(R1[z[0]]) <= EXF_LO and int(DRv[z[0]]) < 0]
rows = []
for lbl, stop, joe in (('leg 7 ended 07:51:05', '07:51:05', '08:10:00'),
                       ('leg 11 stopped 11:07:45', '11:07:45', '11:21:00')):
    ks, kj = K(stop), K(joe)
    nxt = [z for z in G if z[1] > ks]
    if not nxt:
        rows.append((lbl, stop, joe, '—', '—', '—', '—')); continue
    k, c = nxt[0]
    rows.append((lbl, stop, joe, SC.U(k), SC.U(c),
                 '%+.1f' % ((int(SC.ts[c]) - int(SC.ts[kj])) / 60000.0),
                 '%+.4f' % ((float(PX[c]) - float(PX[kj])) / float(PX[kj]) * 100.0)))
box(('chain event', 'stop/end bar', "Joe's bar", 'first gated cross', 'conf bar',
     'conf vs Joe min', 'LONG cost vs Joe'), rows)
print('\n- "LONG cost vs Joe" positive = the gated bar is a BETTER long entry than Joe\'s bar.')
print('- ex-fence %.0f from lazy_g_config momo_fence_r; oob %.0f/%.0f' % (EXF_LO, SC.HI, SC.LO))
