"""EVERY ws{3,4,5,6}x CROSS OF ITS OWN r ON THE 07-15 03:13:15 LEG, AND THE WOB EACH ONE WOULD CARRY.

Joe 1009: *"share 4 sets of times / 1) the four ws3x-crosses before 04:10 with wob 2 / 2,3,4) the
same crosses for ws4,5,6 before 04:30 / for each of the 12 crosses, show me the potential wob
value"*.

  THE TARGET IS THE LINE'S OWN r. ws3x vs ws3r. Joe 0918: *"we're only crossing r"*. Stated.

  THE DIRECTION IS BOTH. Joe said "crosses", not counter-dr crosses, so every sign change is
  listed and the `dir` column says which way. The leg is on the LOW oob side, so `OVER` is the
  counter-side cross (x turning back up) and `UNDER` runs with the side.

  WOB 2 MARKS THE CROSS. A cross is listed when the new side holds 2 bars = 10 s. A 1-bar flicker
  does not qualify; the count of those is printed under each table, not dropped silently.

  POTENTIAL WOB = the FULL run of bars the new side held, from the cross bar until it flips back.
  That is the largest wob that cross would satisfy. No cap, no window - a run that is still open at
  the window end is marked `open`.

  THE WINDOW STARTS AT THE LEG OPEN 03:13:15. Joe gave only the end times. Stated.
"""
import os, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import score39 as SC

N = len(SC.ts)
U, PX = SC.U, np.asarray(SC.PX, float)[:N]
print('# TAPE %d bars, end %s' % (N, os.environ.get('LG_TAPE_END', '2026-10-04 (DEFAULT)')))
OPEN = os.environ.get('X_OPEN', '2026-07-15 03:13:15')
WOB = int(os.environ.get('X_WOB', 2))
SETS = [(3, '04:10:00'), (4, '04:30:00'), (5, '04:30:00'), (6, '04:30:00')]
k0 = SC.K(OPEN)
day = OPEN.split()[0]
mn = lambda j: '%+.1f' % ((int(SC.ts[j]) - int(SC.ts[k0])) / 60000.0)


def box(h, rows):
    w = [max(len(h[i]), max([len(r[i]) for r in rows] or [0])) for i in range(len(h))]
    ln = lambda l, m, r: l + m.join('─' * (x + 2) for x in w) + r
    f = lambda r: '│ ' + ' │ '.join(r[i].ljust(w[i]) for i in range(len(h))) + ' │'
    print(ln('┌', '┬', '┐')); print(f(h))
    print(ln('├', '┼', '┤'))
    for r in rows: print(f(r))
    print(ln('└', '┴', '┘'))


for tf, endt in SETS:
    x = np.asarray(SC.LD(tf * 60, 'x'), float)[:N]
    r = np.asarray(SC.LD(tf * 60, 'r'), float)[:N]
    k1 = SC.K('%s %s' % (day, endt))
    over = x > r                                   # True = x is ABOVE its own r
    rows = []; flick = 0; n = 0
    for j in range(k0 + 1, k1 + 1):
        if over[j] == over[j - 1]:
            continue
        side = bool(over[j])
        k = j
        while k < N and bool(over[k]) == side:
            k += 1
        run = k - j                                # the FULL hold, no cap
        if run < WOB:
            flick += 1
            continue
        n += 1
        rows.append((str(n), U(j), mn(j), 'OVER' if side else 'UNDER',
                     '%.2f' % float(x[j]), '%.2f' % float(r[j]),
                     U(j + WOB - 1), '%.6f' % float(PX[j]),
                     ('%d open' % run) if k >= N else str(run), '%.1f' % (run * 5 / 60.0)))
    print('\n# ws%dx crosses ws%dr   %s -> %s   wob %d bars = %.0f s'
          % (tf, tf, U(k0), U(k1), WOB, WOB * 5.0))
    box(('#', 'cross ts', '+min', 'dir', 'ws%dx' % tf, 'ws%dr' % tf,
         'wob %d met at' % WOB, 'pxs', 'potential wob (bars)', '= min'), rows)
    print('- %d crosses held %d+ bars. %d flickers held under %d bars and did not qualify.'
          % (n, WOB, flick, WOB))
    print('- two rows in a row with the same `dir` means the cross between them was a flicker '
          'that wob %d rejected.' % WOB)
    for dd in ('OVER', 'UNDER'):
        sub = [r for r in rows if r[3] == dd]
        print('- %s: %d crosses. the 4 longest holds: %s'
              % (dd, len(sub),
                 ', '.join('%s (%s bars)' % (r[1], r[8]) for r in
                           sorted(sub, key=lambda r: -int(r[8].split()[0]))[:4])))
    print('- dir OVER = ws%dx crossed UP over ws%dr. UNDER = crossed DOWN under it.' % (tf, tf))
    print('- potential wob = the full run of bars the new side held before flipping back, '
          'the largest wob this cross would satisfy.')
