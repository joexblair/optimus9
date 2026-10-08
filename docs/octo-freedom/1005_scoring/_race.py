"""HOW THE DELEGATION FAILS TO BE CALLED — one leg, both ceilings, bar by bar. 1008.

Joe 1008: *"use simple terms to show me how the delegation failed to be called when ws12r went
oob"*.

THE SHORT VERSION. The delegation is not skipped and nothing refuses it. It is on a 6-minute clock
that starts when ws12r crosses into oob, and the lineage walk is running the whole time on the same
leg. Whichever fires first ends the matter:

  the walk exits first        the LEG CLOSES. There is no delegation, because there is no leg left.
  the 6 minutes elapse first  the handover fires and the walk is switched off for the rest of the leg.

So capping the ceiling at ws12 does not block the delegation. It makes the WALK FASTER: the baton
stops climbing at ws12 instead of carrying on to ws23, so ws12's own stall and x-cross are tested
from that bar on instead of ws13's, ws14's and so on. A faster walk wins the race more often.

PRINTED BELOW: the legs whose delegation flipped, each run twice - ceiling ws23 and ceiling ws12 -
with every walk event, the ws12r oob crossing, the bar the 6 minutes would expire, and the exit.
"""
import os, sys, datetime
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C

SC, PX, box, U = C.SC, C.PX, C.box, C.SC.U
N = len(SC.ts)
assert C.GATE_BARS == 72 and C.DGATE == 'off', 'the banked width, gate off'
DAYOF = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                  datetime.timezone.utc).strftime('%Y-%m-%d')
LEGS = [('2026-07-22 23:20:15', +1), ('2026-07-29 02:32:05', -1),
        ('2026-10-03 01:18:00', -1)]
print('# oob_gate_bars %d = %.1f min at the 5 s grid; ceil_trig_tf ws%d'
      % (C.GATE_BARS, C.GATE_BARS * 5 / 60.0, C.TRIG_TF), flush=True)

for ts, d in LEGS:
    k0 = SC.K(ts)
    print('\n\n## %s  %s   open pxs %.6f' % (ts, 'LONG' if d > 0 else 'SHORT', float(PX[k0])))
    for ceil in (23, 12):
        C.CEIL_HI = ceil
        xk, why, mae, cb, hand, tr = C.run_leg(k0, d)
        mn = lambda j: '%+.1f' % ((int(SC.ts[j]) - int(SC.ts[k0])) / 60000.0)
        p0 = float(PX[k0]); sgn = 1 if d > 0 else -1
        pct = lambda j: '%+.4f' % ((float(PX[j]) - p0) / p0 * 100.0 * sgn)
        rows = [(U(k0), '+0.0', 'OPEN %s' % ('LONG' if d > 0 else 'SHORT'), pct(k0))]
        for j, lbl in tr:
            rows.append((U(j), mn(j), lbl, pct(j)))
        if cb is not None:
            exp = cb + C.GATE_BARS + 1
            rows.append((U(exp) if exp < N else '—', mn(exp) if exp < N else '—',
                         'the 6 minutes from the ws%dr oob crossing expire HERE%s' % (C.TRIG_TF,
                          ' — the handover fired' if hand is not None
                          else ' — but the leg had already closed'),
                         pct(exp) if exp < N else '—'))
        rows.append((U(xk), mn(xk), 'EXIT on %s' % why, pct(xk)))
        rows.sort(key=lambda r: r[0] if r[0] != '—' else 'zz')
        print('\n### ceiling ws%d%s   ->   exits %s on %s, realised %s'
              % (ceil, '  (BANKED)' if ceil == 23 else '  (extension OFF)', U(xk), why, pct(xk)))
        box(('ts', '+min', 'what happened', 'pct for this leg'), rows)
        print('- delegation: %s' % ('CALLED at %s' % U(hand) if hand is not None
                                    else 'NEVER CALLED — the walk exited first'))
