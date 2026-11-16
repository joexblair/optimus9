"""HIS 1116: what max TF should M-no-rev report on? A PROBE, nothing banked.

HIS WORDS: *"the next job is to find the max TF that m-no-rev should report on. this could be a slow
process - I'll need buttons on oracle to show me the different max-m-no-rev-TF outputs. you can
help. 1) between 09-22 and 09-27, find every m-no-rev row that is printing at oracle's pivot roe (or
the row just before the pivot row) 2) for each, reduce the maxTF until you find a TF that does not
run past the pivot. there's probably a need for some kind of dwell on the retested reversals.
consider that while you're investigating"*.

WHAT A PIVOT ROW IS HERE: a row whose target-side byte differs from the row before it. That byte is
the pseudo trade's target side, so it changes exactly where one trade closes and the next opens - at
a ws2Mage sweep pivot. THE SIDE IS READ, NEVER DERIVED: it comes straight off the oracle's own last
byte, so this probe cannot disagree with the page about where a pivot is.

THE M-NO-REV MECH IT READS is the one his 1116 reset built: a lift-off reversal stores the EMERGING
Mage at its pivot bar and stops the print; the first later bar strictly further from 50 on the
target-side resumes it; a fresh cross into oob clears everything. It is reproduced here rather than
read off the page because the page prints only the HIGHEST qualifying TF, and this question needs
every TF.

usage: mnr_maxtf.py '<from>' '<to>'
"""
import io
import os
import sys
import urllib.request
import json

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fdm3_knobs as FK

V4 = '/home/joe/thecodes/docs/octo-freedom/1022_v4'
sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, V4)
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
os.chdir(V4)
_err = sys.stderr
sys.stderr = io.StringIO()
try:
    import ln
    import v4_closed_prev as CP
    import v4_knobs as K
    from optimus9.analysis import jig as JIG
finally:
    sys.stderr = _err

MNR_TOP = 30                    # the ceiling the page runs at today, HIS 1111 answer
BASE = 'http://127.0.0.1:%d' % int(FK.ORACLE_PORT)
META = json.load(urllib.request.urlopen(BASE + '/meta'))
STRIDE, NROWS = int(META['stride']), int(META['rows'])
T0, STEP = int(META['t0']), int(META['step'])

TS = np.asarray(ln.ts, np.int64)
FIRST = np.flatnonzero((TS % 60000) == 0)
FIRST = FIRST[FIRST + 12 < ln.N]
PRT = FIRST + 12
assert len(PRT) == NROWS, (len(PRT), NROWS)


def U(k):
    import datetime as dt
    return dt.datetime.fromtimestamp((T0 + int(k) * STEP) / 1000,
                                     dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


def K_OF(s):
    import datetime as dt
    return (int(dt.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
                .replace(tzinfo=dt.timezone.utc).timestamp() * 1000) - T0) // STEP


def side_bytes():
    """The row's pseudo-trade target side, off the oracle's own last byte."""
    sd = np.zeros(NROWS, np.int8)
    for a in range(0, NROWS, 20000):
        n = min(20000, NROWS - a)
        #   the A state is the banked one; 8789 locks it and refuses anything else
        u = ('%s/rows?start=%d&count=%d&flip=0&alo=%d&ahi=%d'
             % (BASE, a, n, int(FK.A_WS1_WS6), int(FK.A_WS7_WS15)))
        b = np.frombuffer(urllib.request.urlopen(u).read(), np.int8).reshape(-1, STRIDE)
        sd[a:a + n] = b[:, STRIDE - 1]
    return sd


def per_tf(sd_rows):
    """-> (qual [rows, 31] bool, dwell [(tf, stamp bar, resume bar)]).

    `qual[i, t]` is True where ws{t}Mage qualifies for M-no-rev on row i at that row's target side -
    the same test the column makes, with his 1116 reset. `dwell` records every reset: the reversal's
    knowable stamp and the bar the print resumed on, so the gap between them can be read.
    """
    idx = np.arange(ln.N)
    qual = np.zeros((NROWS, MNR_TOP + 1), bool)
    dwell = []
    for t in range(1, MNR_TOP + 1):
        em = np.asarray(ln.line('ws%dMage' % t), float)
        cp = np.asarray(CP.series(em, t * 60), float)
        raw = np.asarray(JIG.lift_off(em, +1, K.LIFT_PTS, K.gap_for(t), K.LIFT_TOL, K.LIFT_WOB), int)
        for sd in (+1, -1):
            with np.errstate(invalid='ignore'):
                oob = cp >= K.OOB_HI if sd > 0 else cp <= K.OOB_LO
            start = oob & ~np.concatenate([[False], oob[:-1]])
            cross = np.where(oob, np.maximum.accumulate(np.where(start, idx, -1)), -1)
            rw = np.asarray(JIG.lift_off(em, sd, K.LIFT_PTS, K.gap_for(t), K.LIFT_TOL, K.LIFT_WOB), int)
            st = np.asarray([K.lift_stamp(int(b)) for b in rw], int)
            o = np.argsort(st, kind='stable')
            st_s, raw_s = st[o], rw[o]
            with np.errstate(invalid='ignore'):
                stored_at = em[np.clip(raw_s, 0, ln.N - 1)]
            u = np.zeros(ln.N, bool)
            n, i = len(st_s), 0
            while i < ln.N:
                if not oob[i]:
                    i += 1
                    continue
                c = int(cross[i])
                armed, stored, kill = True, np.nan, -1
                p = int(np.searchsorted(st_s, c, side='left'))
                while i < ln.N and oob[i]:
                    while p < n and st_s[p] <= i:
                        if st_s[p] >= c:
                            armed, stored, kill = False, stored_at[p], int(st_s[p])
                        p += 1
                    if not armed and np.isfinite(stored):
                        v = em[i]
                        if np.isfinite(v) and ((v > stored) if sd > 0 else (v < stored)):
                            armed = True
                            dwell.append((t, kill, i))
                    u[i] = armed
                    i += 1
                i += 1 if i < ln.N and not oob[i] else 0
            qual[:, t] |= u[PRT] & (sd_rows == sd)
    return qual, dwell


def main():
    a, z = K_OF(sys.argv[1]), K_OF(sys.argv[2])
    sd = side_bytes()
    print('tape bars %d. read off port %d, %d rows.' % (ln.N, int(FK.ORACLE_PORT), NROWS))
    qual, dwell = per_tf(sd)
    top = np.where(qual.any(1), qual.shape[1] - 1 - np.argmax(qual[:, ::-1], 1), 0)
    #   a pivot row: its target side differs from the row before. HIS *"oracle's pivot roe"*
    piv = np.zeros(NROWS, bool)
    piv[1:] = sd[1:] != sd[:-1]
    pv = [int(i) for i in np.flatnonzero(piv) if a <= i <= z]
    print('pivot rows between %s and %s: %d' % (sys.argv[1], sys.argv[2], len(pv)))
    print()
    print('| the pivot row | the side it opens | the row | its M-no-rev TF at the ws30 ceiling '
          '| rows that TF runs past the pivot | the ceiling that stops it at the pivot '
          '| what that ceiling prints |')
    print('|' + '---|' * 7)
    for P in pv:
        for R in (P - 1, P):
            if R < 0 or not qual[R].any():
                continue
            t0 = int(top[R])
            #   how far past the pivot ws{t0} keeps qualifying, unbroken from R
            run = 0
            j = P + 1
            while j < NROWS and qual[j, t0]:
                run += 1
                j += 1
            #   the highest ceiling whose top TF stops at or before the pivot
            best, bt = None, 0
            for c in range(t0, 0, -1):
                tt = [t for t in range(1, c + 1) if qual[R, t]]
                if not tt:
                    continue
                h = max(tt)
                if not (P + 1 < NROWS and qual[P + 1, h]):
                    best, bt = c, h
                    break
            print('| %s | %s | %s | ws%d | %d | %s | %s |'
                  % (U(P), 'SHORT' if sd[P] < 0 else 'LONG' if sd[P] > 0 else 'none',
                     'the pivot row' if R == P else 'the row before',
                     t0, run, 'ws%d' % best if best else 'none at any ceiling',
                     'ws%d' % bt if best else '-'))
    #   HIS *"there's probably a need for some kind of dwell on the retested reversals"*
    g = np.asarray([r - k for _t, k, r in dwell if k >= 0], int)
    print()
    print('| the reset gap - bars from a reversal becoming knowable to the print resuming | value |')
    print('|---|---|')
    print('| resets in all, ws1..ws%d, whole tape | %d |' % (MNR_TOP, len(g)))
    if len(g):
        print('| the median gap | %d bars, %.1f min |' % (int(np.median(g)), np.median(g) * 5 / 60.0))
        print('| the mean gap | %.0f bars, %.1f min |' % (g.mean(), g.mean() * 5 / 60.0))
        for q in (10, 25, 50, 75, 90):
            print('| the %dth percentile | %d bars, %.1f min |'
                  % (q, int(np.percentile(g, q)), np.percentile(g, q) * 5 / 60.0))
        print('| resets that resumed on the very next bar | %d |' % int((g <= 1).sum()))


if __name__ == '__main__':
    main()
