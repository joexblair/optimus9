"""HIS 1116 single leg: ws5, ws10, ws12, ws15 Mage, M-no-rev starts and stops over one leg.

HIS WORDS: *"instead of a wholesale view of m-no-rev, let's start with a single leg. using only ws5,
ws10, ws12, and ws15 Mage / using a leg that opens low side 09-25 1540 to a highside 1830 end (those
times include a pre and post ~10minute buffer) / create a timestamped table that shows when each of
the 4 lines (in comlumns) start to print a m-no-rev and stop printing a m-no-rev value. the quiet
bars are muted in the table"*.

THE MECH IT READS is 8788's: his 1116 reprint-on-an-extremum. The page prints only the HIGHEST
qualifying TF, so a per-TF view has to be computed rather than read off the row bytes.

*"the quiet bars are muted"* taken as: ONE ROW PER CHANGE. A bar where none of the four lines starts
or stops does not print.
"""
import io, os, sys, json, datetime as dt, urllib.request
import numpy as np
sys.path.insert(0, '/home/joe/thecodes/docs/fdm3')
import fdm3_knobs as FK
V4 = '/home/joe/thecodes/docs/octo-freedom/1022_v4'
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, V4)
os.environ.setdefault('LG_TAPE_END', '2026-10-05'); os.chdir(V4)
_e = sys.stderr; sys.stderr = io.StringIO()
try:
    import ln, v4_closed_prev as CP, v4_knobs as K
    from optimus9.analysis import jig as JIG
finally:
    sys.stderr = _e

TFS = [5, 10, 12, 15]
PORT = 8788                     # the page carrying the reprint, his testing ground
M = json.load(urllib.request.urlopen('http://127.0.0.1:%d/meta' % PORT))
STR, NR, T0, STEP = int(M['stride']), int(M['rows']), int(M['t0']), int(M['step'])
ts = np.asarray(ln.ts, np.int64)
first = np.flatnonzero((ts % 60000) == 0); first = first[first + 12 < ln.N]
PRT = first + 12
assert len(PRT) == NR

def U(k):
    return dt.datetime.fromtimestamp((T0 + int(k)*STEP)/1000, dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
def Kof(s):
    return (int(dt.datetime.strptime(s, '%Y-%m-%d %H:%M:%S').replace(tzinfo=dt.timezone.utc).timestamp()*1000) - T0)//STEP

sd_rows = np.zeros(NR, np.int8)
for a in range(0, NR, 20000):
    n = min(20000, NR - a)
    u = 'http://127.0.0.1:%d/rows?start=%d&count=%d&flip=0&alo=%d&ahi=%d' % (PORT, a, n, int(FK.A_WS1_WS6), int(FK.A_WS7_WS15))
    b = np.frombuffer(urllib.request.urlopen(u).read(), np.int8).reshape(-1, STR)
    sd_rows[a:a+n] = b[:, STR-1]

#   HIS LEG, with his own ~10 minute buffer at each end. Passed in rather than hard-coded once he
#   names another one.
A = Kof(sys.argv[1] if len(sys.argv) > 2 else '2026-09-25 15:40:00')
Z = Kof(sys.argv[2] if len(sys.argv) > 2 else '2026-09-25 18:30:00')
idx = np.arange(ln.N)
QUAL, VAL, WHY = {}, {}, {}
for t in TFS:
    em = np.asarray(ln.line('ws%dMage' % t), float)
    cp = np.asarray(CP.series(em, t*60), float)
    q = np.zeros(NR, bool); why = {}
    for sd in (+1, -1):
        with np.errstate(invalid='ignore'):
            oob = cp >= K.OOB_HI if sd > 0 else cp <= K.OOB_LO
        start = oob & ~np.concatenate([[False], oob[:-1]])
        cross = np.where(oob, np.maximum.accumulate(np.where(start, idx, -1)), -1)
        rw = np.asarray(JIG.lift_off(em, sd, K.LIFT_PTS, K.gap_for(t), K.LIFT_TOL, K.LIFT_WOB), int)
        st = np.asarray([K.lift_stamp(int(b)) for b in rw], int)
        o = np.argsort(st, kind='stable'); st_s, raw_s = st[o], rw[o]
        with np.errstate(invalid='ignore'):
            stored_at = em[np.clip(raw_s, 0, ln.N-1)]
        u5 = np.zeros(ln.N, bool); note = {}
        n, i = len(st_s), 0
        while i < ln.N:
            if not oob[i]:
                i += 1; continue
            c = int(cross[i]); armed, stored = True, np.nan
            p = int(np.searchsorted(st_s, c, side='left'))
            while i < ln.N and oob[i]:
                while p < n and st_s[p] <= i:
                    if st_s[p] >= c:
                        if armed:
                            note[i] = 'a reversal, stored %.1f' % stored_at[p]
                        armed, stored = False, stored_at[p]
                    p += 1
                if not armed and np.isfinite(stored):
                    v = em[i]
                    if np.isfinite(v) and ((v > stored) if sd > 0 else (v < stored)):
                        armed = True
                        note[i] = 'past the stored %.1f' % stored
                u5[i] = armed
                i += 1
        q |= u5[PRT] & (sd_rows == sd)
        for bar, txt in note.items():
            why[bar] = txt
    QUAL[t] = q
    VAL[t] = cp
    WHY[t] = why

print('| the row | its target-side | ws5Mage | ws10Mage | ws12Mage | ws15Mage |')
print('|---|---|---|---|---|---|')
shown = 0
for i in range(A, Z + 1):
    cells, change = [], False
    for t in TFS:
        now, was = QUAL[t][i], (QUAL[t][i-1] if i else False)
        if now and not was:
            cells.append('STARTS %.1f' % VAL[t][PRT[i]]); change = True
        elif was and not now:
            cells.append('stops'); change = True
        else:
            cells.append('')
    if change:
        print('| %s | %s | %s |' % (U(i), 'LOW' if sd_rows[i] < 0 else 'HIGH' if sd_rows[i] > 0 else 'none',
                                    ' | '.join(cells)))
        shown += 1
print()
print('| the span | value |')
print('|---|---|')
for t in TFS:
    cp = VAL[t][PRT][A:Z + 1]
    with np.errstate(invalid='ignore'):
        nh, nl = int((cp >= K.OOB_HI).sum()), int((cp <= K.OOB_LO).sum())
    print('| ws%dMage, its value range and its oob bars | %.1f .. %.1f, %d high, %d low |'
          % (t, np.nanmin(cp), np.nanmax(cp), nh, nl))
print('| rows in it | %d |' % (Z - A + 1))
print('| rows with a start or a stop | %d |' % shown)
print('| the target-side at %s | %s |' % (U(A), 'LOW' if sd_rows[A] < 0 else 'HIGH'))
print('| the target-side at %s | %s |' % (U(Z), 'LOW' if sd_rows[Z] < 0 else 'HIGH'))
ch = [i for i in range(A, Z+1) if sd_rows[i] != sd_rows[i-1]]
print('| pivot rows inside the span | %s |' % (', '.join(U(i)[11:16] for i in ch) or 'none'))
