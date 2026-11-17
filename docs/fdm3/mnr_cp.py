"""HIS 1117 M-no-rev: the banked print, resumed on a MORE EXTREME CLOSED-PREV bar. A probe.

HIS WORDS: *"this idea isn't working for m-no-rev. let's go back to the banked state (any Mage to
oob, m-no-rev prints. Mage reverses, m-no-rev stops printing) / instead of reacting to a more
extreme Mage value using emerging values, we'll use closed-prev. the mechanism is simple: first, the
existing 'any Mage to oob, m-no-rev prints. Mage reverses, m-no-rev stops printing' then, if the
following closed-prev bar is more extreme, m-no-rev starts printing again until it is terminated by
a fresh reversal. if the next closed-prev bar is less extreme, nothing happens"*.

SO, per line and per oob run:
  prints        from the cross into oob, as it always did
  stops         on a lift-off reversal whose knowable bar lands at or after that cross
  prints again  at the first of the line's OWN closed bars whose value is more extreme on the target
                side than the bar closed before it. A less extreme one does nothing and the next
                closed bar is tested the same way
  stops again   on the next reversal after that

  THE COMPARISON IS BETWEEN THE LINE'S OWN CLOSED BARS, not between 5 s bars: a closed-prev series
  is flat between its seams, so v4_closed_prev.seam_bars gives the only bars it steps on. For
  ws15Mage that is one comparison every 15 minutes.

  NO WOB. He described none for this mech, and the 18 bar wob belonged to the emerging version.

HIS END LOGIC, 1117: *"if you have an open m-no-rev at my end time, keep walking until it is
closed"* - the table covers his whole leg and then walks only as far as closing an open print.

usage: mnr_cp.py '<from>' '<to>' <high|low>
       mnr_cp.py legs                 # his six legs, start and end of every print
"""
import io
import os
import sys
import json
import datetime as dt
import urllib.request

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

#   HIS 1117: *"add all of these lines: ws5 to ws25"*, then *"if we drop the lowest from ws5 to
#   ws2"* - so the bottom of the range moves. MNR_TFS=lo:hi sets it for one run without an edit.
_R = os.environ.get('MNR_TFS', '5:25').split(':')
TFS = list(range(int(_R[0]), int(_R[1]) + 1))
PORT = 8788                     # the page carrying the M-no-rev work, his testing ground
META = json.load(urllib.request.urlopen('http://127.0.0.1:%d/meta' % PORT))
STRIDE, NROWS = int(META['stride']), int(META['rows'])
T0, STEP = int(META['t0']), int(META['step'])
TS = np.asarray(ln.ts, np.int64)
FIRST = np.flatnonzero((TS % 60000) == 0)
FIRST = FIRST[FIRST + 12 < ln.N]
PRT = FIRST + 12
assert len(PRT) == NROWS, (len(PRT), NROWS)
LEGS = [('2026-09-25 15:40:00', '2026-09-25 20:42:00', +1),
        ('2026-09-26 13:22:00', '2026-09-26 15:33:00', +1),
        ('2026-09-26 15:17:00', '2026-09-26 21:00:00', -1),
        ('2026-09-26 20:45:00', '2026-09-27 02:30:00', +1),
        ('2026-09-27 02:15:00', '2026-09-27 05:15:00', -1),
        ('2026-09-27 05:00:00', '2026-09-27 08:30:00', +1)]


def U(k):
    return dt.datetime.fromtimestamp((T0 + int(k) * STEP) / 1000,
                                     dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


def K_OF(s):
    return (int(dt.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
                .replace(tzinfo=dt.timezone.utc).timestamp() * 1000) - T0) // STEP


_CACHE = {}


def qualifies(t, sd):
    """-> (at each 5 s bar, at each oracle row, the closed-prev value, the resume bars).

    One walk per oob run. `armed` opens True at the cross, a reversal stamp turns it off, and one of
    the line's own closed bars more extreme than the bar before it turns it back on.

    CACHED per line and side: a line's walk does not read the leg, so six legs share one walk.
    """
    if (t, sd) in _CACHE:
        return _CACHE[(t, sd)]
    em = np.asarray(ln.line('ws%dMage' % t), float)
    cp = np.asarray(CP.series(em, t * 60), float)
    idx = np.arange(ln.N)
    with np.errstate(invalid='ignore'):
        oob = cp >= K.OOB_HI if sd > 0 else cp <= K.OOB_LO
    start = oob & ~np.concatenate([[False], oob[:-1]])
    cross = np.where(oob, np.maximum.accumulate(np.where(start, idx, -1)), -1)
    rw = np.asarray(JIG.lift_off(em, sd, K.LIFT_PTS, K.gap_for(t), K.LIFT_TOL, K.LIFT_WOB), int)
    st = np.sort(np.asarray([K.lift_stamp(int(b)) for b in rw], int))
    #   the only bars the closed-prev series steps on, and whether that step is more extreme
    #   A CLOSED-PREV SERIES STEPS ONE BAR AFTER ITS SEAM - seam_bars names the last 5 s bar of a
    #   completed bucket and the new value lands on the bar after it. Reading the step ON the seam
    #   compares a value with itself and the resume never fires, which is what it did until 1117.
    step = np.zeros(ln.N, bool)
    with np.errstate(invalid='ignore'):
        changed = cp[1:] != cp[:-1]
        more = (cp[1:] > cp[:-1]) if sd > 0 else (cp[1:] < cp[:-1])
    step[1:] = changed & more
    u = np.zeros(ln.N, bool)
    res = []
    n, i = len(st), 0
    while i < ln.N:
        if not oob[i]:
            i += 1
            continue
        c = int(cross[i])
        armed = True
        p = int(np.searchsorted(st, c, side='left'))
        while i < ln.N and oob[i]:
            while p < n and st[p] <= i:
                if st[p] >= c:
                    armed = False
                p += 1
            if not armed and step[i]:
                armed = True
                res.append(i)
            u[i] = armed
            i += 1
    _CACHE[(t, sd)] = (u, u[PRT], cp, res)
    return _CACHE[(t, sd)]


def leg(a_s, z_s, sd, table=True):
    A, Z = K_OF(a_s), K_OF(z_s)
    Q, CPV = {}, {}
    for t in TFS:
        _u5, q, cp, _r = qualifies(t, sd)
        Q[t], CPV[t] = q, cp
    on = np.zeros(NROWS, bool)
    for t in TFS:
        on |= Q[t]
    ZW = Z                       # HIS 1117: walk past his end only to close an open print
    while ZW + 1 < NROWS and on[ZW]:
        ZW += 1
    if not table:
        out, i, n = [], A, 0
        while i <= Z:
            if not on[i] or (i > A and on[i - 1]):
                i += 1
                continue
            j = i
            while j < NROWS and on[j]:
                j += 1
            last = {}
            for t in TFS:
                pr = np.flatnonzero(Q[t][i:j])
                if len(pr):
                    last[t] = i + int(pr[-1])
            lt = max(last, key=lambda x: last[x]) if last else 0
            n += 1
            out.append((n, i, j - 1, lt, last.get(lt, j - 1), Z))
            i = j
        return out
    print('# the leg %s .. %s, target as he named it: %s. Walked to %s to close the open print.'
          % (U(A), U(Z), 'HIGH' if sd > 0 else 'LOW', U(ZW)))
    #   ONE COLUMN, TOP TO BOTTOM: 21 line columns would be the open book he banned, so each row
    #   NAMES the lines that started and the lines that stopped on it.
    print('| the row | its target-side | the consolidated print | the lines that START, with their '
          'closed-prev value | the lines that STOP | lines printing after this row |')
    print('|' + '---|' * 6)
    for i in range(A, ZW + 1):
        up, dn = [], []
        for t in TFS:
            now, was = bool(Q[t][i]), bool(Q[t][i - 1] if i else False)
            if now and not was:
                up.append('ws%d %.1f' % (t, CPV[t][PRT[i]]))
            elif was and not now:
                dn.append('ws%d' % t)
        c, cw = bool(on[i]), bool(on[i - 1] if i else False)
        cc = 'STARTS' if (c and not cw) else 'stops' if (cw and not c) else ('on' if c else '')
        if up or dn or c != cw:
            live = [t for t in TFS if Q[t][i]]
            print('| %s | %s | %s | %s | %s | %s |'
                  % (U(i), 'HIGH' if sd > 0 else 'LOW', cc, ', '.join(up) or '-',
                     ', '.join(dn) or '-',
                     ', '.join('ws%d' % t for t in live) or 'none'))
    print()
    print('| the span | value |')
    print('|---|---|')
    print('| rows in his leg | %d |' % (Z - A + 1))
    print('| rows walked | %d, to %s |' % (ZW - A + 1, U(ZW)))
    print('| rows the consolidated print covers | %d of %d |' % (int(on[A:ZW + 1].sum()), ZW - A + 1))


#   MNR_BANDS=lo-hi,lo-hi,... sets the groups the bands mode measures; the default is his three.
BANDS = [(('ws%s..ws%s' % tuple(b.split('-'))),
          range(int(b.split('-')[0]), int(b.split('-')[1]) + 1))
         for b in os.environ.get('MNR_BANDS', '1-4,5-25,26-30').split(',')]


def bands():
    """HIS 1117 HYPOTHESIS: he cut ws1..ws4 and ws26..ws30 out of the column on an eyeballed read -
    *"I think that they will overrun"*. This measures each band's own prints against each leg end.
    """
    print('| his leg | its end | its target | the band | prints beginning in the leg '
          '| its LAST print starts | it ends | the line holding it | its end against his end |')
    print('|' + '---|' * 9)
    for a_s, z_s, sd in LEGS:
        A, Z = K_OF(a_s), K_OF(z_s)
        for lab, rng in BANDS:
            Q = {}
            for t in rng:
                _u5, q, _cp, _r = qualifies(t, sd)
                Q[t] = q
            on = np.zeros(NROWS, bool)
            for t in rng:
                on |= Q[t]
            runs, i = [], A
            while i <= Z:
                if not on[i] or (i > A and on[i - 1]):
                    i += 1
                    continue
                j = i
                while j < NROWS and on[j]:
                    j += 1
                last = {}
                for t in rng:
                    pr = np.flatnonzero(Q[t][i:j])
                    if len(pr):
                        last[t] = i + int(pr[-1])
                lt = max(last, key=lambda x: last[x]) if last else 0
                runs.append((i, j - 1, lt))
                i = j
            if not runs:
                print('| %s | %s | %s | %s | 0 | never | - | - | - |'
                      % (a_s[5:16], z_s[11:16], 'HIGH' if sd > 0 else 'LOW', lab))
                continue
            s0, end, lt = runs[-1]
            print('| %s | %s | %s | %s | %d | %s | %s | ws%d | %+d rows |'
                  % (a_s[5:16], z_s[11:16], 'HIGH' if sd > 0 else 'LOW', lab, len(runs),
                     U(s0)[11:16], U(end)[11:16], lt, end - Z))


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'bands':
        bands()
        return
    if len(sys.argv) > 1 and sys.argv[1] == 'legs':
        print('# the lines: ws%d to ws%d' % (TFS[0], TFS[-1]))
        print('| his leg start | his leg end | its target | the print | it starts | where it ends '
              '| the line holding it last | that line\'s last printing row | its end against his end |')
        print('|' + '---|' * 9)
        for a_s, z_s, sd in LEGS:
            rows = leg(a_s, z_s, sd, table=False)
            if not rows:
                print('| %s | %s | %s | - | never | - | - | - | - |'
                      % (a_s[5:16], z_s[11:16], 'HIGH' if sd > 0 else 'LOW'))
            for n, s0, end, lt, lr, Z in rows:
                print('| %s | %s | %s | %d | %s | %s | ws%d | %s | %+d rows |'
                      % (a_s[5:16], z_s[11:16], 'HIGH' if sd > 0 else 'LOW', n,
                         U(s0)[11:16], U(end)[11:16], lt, U(lr)[11:16], end - Z))
        return
    leg(sys.argv[1], sys.argv[2], {'high': +1, 'low': -1}[sys.argv[3].lower()])


if __name__ == '__main__':
    main()
