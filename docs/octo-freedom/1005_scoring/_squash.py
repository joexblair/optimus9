"""WHAT "A SQUASHED x-CROSS" COUNTS, ON EVERY ws12r oob RUN THAT ENDED BEFORE THE DWELL. 1009.

Joe 1009: *"if oob ended before dwell completed, and a x-cross was squashed during the oob, then a
B-trade is created and the A-trade is closed"*.

The rule's population is unambiguous: a ws12r oob run whose length never reaches the dwell-ending.
"SQUASHED" is not - the code already has three different things a cross can fail at, and each one
selects a different set of runs. This counts all three, on the whole tape, so the choice has a
number under it instead of a preference.

  A  CANCELLED BY THE HOLD    the cross fired inside the EXHAUSTION window, then ws12x crossed
                              back before XWOB_WS12X bars of hold - the explicit
                              "did NOT hold 4 bars - cancelled" row.
  B  CUT OFF BY THE RUN END   the cross fired, held every bar it had, and the OOB RUN ENDED before
                              the hold reached XWOB_WS12X. Nothing rejected it; it ran out of run.
  C  OUTSIDE THE WINDOW       the cross fired after the exhaustion window closed, so the
                              exhaustion rule never looked at it - trade 1's 00:15:20 cross, 20 s
                              late. Today it prints "branch 1 cross - RECORDED, not acted on".

Each run is classified by its FIRST cross only, and the three are mutually exclusive.
"""
import os, sys, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C

SC, box, U = C.SC, C.box, C.SC.U
N = len(SC.ts); TF = C.TRIG_TF
R12 = np.asarray(C.R[TF], float)[:N]; X12 = np.asarray(C.X[TF], float)[:N]
GB, EB, XW = C.GATE_BARS, C.EXH_BARS, C.XW12
DAY = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                datetime.timezone.utc).strftime('%Y-%m-%d')
print('# ws12r oob runs, both sides, %d bars = %d days' % (N, N * 5 // 86400))
print('# the fence is oob_gate_fence %.0f/%.0f; the dwell-ending needs %d bars = %.1f min;'
      % (C.G_LO, C.G_HI, GB + 1, (GB + 1) * 5 / 60.0))
print('# the exhaustion window is %d bars = %.1f min; the hold is XWOB_WS12X %d bars = %.0f s'
      % (EB, EB * 5 / 60.0, XW, XW * 5.0), flush=True)

rows = []; tot = collections.Counter(); per = collections.defaultdict(list)
for d, name in ((+1, 'HIGH oob (LONG legs)'), (-1, 'LOW oob (SHORT legs)')):
    ob = (R12 >= C.G_HI) if d > 0 else (R12 <= C.G_LO)
    ob &= np.isfinite(R12)
    st = np.flatnonzero(ob & ~np.r_[False, ob[:-1]])
    en = np.flatnonzero(ob & ~np.r_[ob[1:], False])
    xu = X12 < R12
    held = xu if d > 0 else ~xu
    xc = held & ~np.r_[False, held[:-1]]
    c = collections.Counter()
    for a, b in zip(st, en):
        c['runs'] += 1
        if b >= a + GB + 1:
            c['the dwell completed'] += 1; continue
        c['THE RUN ENDED BEFORE THE DWELL'] += 1
        cs = np.flatnonzero(xc[a + 1:b + 1])
        if not len(cs):
            c['  no x-cross in the run at all'] += 1; continue
        j = int(cs[0]) + a + 1
        inw = (j - a) <= EB
        # the consecutive bars the cross HELD, from j, bounded by the run's own last bar b
        seg = held[j:b + 1]
        hb = int(np.argmin(seg)) if not seg.all() else int(len(seg))
        if not inw:
            kind = 'C  the cross is OUTSIDE the exhaustion window'
        elif hb >= XW:
            kind = 'it CONFIRMED - the exhaustion already fires here'
        elif j + hb - 1 == b:
            # it held every bar it was given and the OOB RUN ran out first
            kind = 'B  CUT OFF BY THE RUN END'
        else:
            kind = 'A  CANCELLED BY THE HOLD'
        c['  ' + kind] += 1
        per[kind].append((DAY(j), name.split()[0], U(a), U(j), U(b),
                          '%.1f' % ((b - a + 1) * 5 / 60.0), '%.1f' % ((j - a) * 5 / 60.0),
                          '%.2f' % R12[j], '%.2f' % X12[j], str(min(hb, XW)),
                          '%.1f' % ((a + GB + 1 - b) * 5 / 60.0)))
    rows.append((name, c)); tot.update(c)

for name, c in rows:
    print('\n# %s' % name)
    box(('the outcome', 'runs'), [(k, str(v)) for k, v in sorted(c.items())])
print('\n# BOTH SIDES')
box(('the outcome', 'runs', 'of the runs that ended short'),
    [(k, str(v), '%.1f%%' % (100.0 * v / tot['THE RUN ENDED BEFORE THE DWELL'])
      if k.startswith('  ') else '') for k, v in sorted(tot.items())])
print('\n# WHAT EACH READING WOULD FIRE ON — the count that decides the knob')
box(('the reading of "squashed"', 'B-trades it creates', 'of all oob runs'),
    [(k, str(len(v)), '%.2f%%' % (100.0 * len(v) / tot['runs']))
     for k, v in sorted(per.items())]
    + [('A + B  (the cross failed its hold, either way)',
        str(len(per['A  CANCELLED BY THE HOLD']) + len(per['B  CUT OFF BY THE RUN END'])), ''),
       ('A + B + C  (any cross that produced no exit)',
        str(sum(len(v) for k, v in per.items() if not k.startswith('it CONFIRMED'))), '')])
for k in sorted(per):
    print('\n# %s — every one, %d rows' % (k, len(per[k])))
    box(('day', 'side', 'the oob run opens', 'the cross', 'the run ends', 'run min',
         'cross at +min', 'ws12r', 'ws12x', 'bars it held', 'min short of the dwell'), per[k])
