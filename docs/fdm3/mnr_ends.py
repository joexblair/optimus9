"""HIS 1116: *"the goal of our work is to improve the end time"*. His legs, and for each one every
consolidated M-no-rev print that begins inside it, followed to where it GENUINELY ends.

HIS CORRECTION, and the rule this file exists to honour: *"don't treat my end time as a cap. keep
going until the lines have reached an end (ie the wob expires)"*. So a print's START is bounded by
his leg and its END never is - the wobbed state runs over the whole tape and the walk follows each
print until every line has closed with no reprint. His leg end is printed as a marker to measure
against, nothing more.

The four lines, the 18 row wob and the consolidation are his 1116 spec; the mech underneath is his
1116 reprint-on-an-extremum, which lives on 8788.

usage: mnr_ends.py          # his legs as listed in LEGS
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
TFS, WOB = [5, 10, 12, 15], 18
M = json.load(urllib.request.urlopen('http://127.0.0.1:8788/meta'))
STR, NR, T0, STEP = int(M['stride']), int(M['rows']), int(M['t0']), int(M['step'])
ts = np.asarray(ln.ts, np.int64)
first = np.flatnonzero((ts % 60000) == 0); first = first[first+12 < ln.N]; PRT = first + 12
def U(k): return dt.datetime.fromtimestamp((T0+int(k)*STEP)/1000, dt.timezone.utc).strftime('%Y-%m-%d %H:%M')
def Kof(s): return (int(dt.datetime.strptime(s,'%Y-%m-%d %H:%M:%S').replace(tzinfo=dt.timezone.utc).timestamp()*1000)-T0)//STEP
idx = np.arange(ln.N)
Q = {}                                   # (tf, side) -> qualifies at each oracle row
for t in TFS:
    em = np.asarray(ln.line('ws%dMage' % t), float)
    cp = np.asarray(CP.series(em, t*60), float)
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
        u = np.zeros(ln.N, bool); n, i = len(st_s), 0
        while i < ln.N:
            if not oob[i]:
                i += 1; continue
            c = int(cross[i]); armed, stored = True, np.nan
            p = int(np.searchsorted(st_s, c, side='left'))
            while i < ln.N and oob[i]:
                while p < n and st_s[p] <= i:
                    if st_s[p] >= c:
                        armed, stored = False, stored_at[p]
                    p += 1
                if not armed and np.isfinite(stored):
                    v = em[i]
                    if np.isfinite(v) and ((v > stored) if sd > 0 else (v < stored)):
                        armed = True
                u[i] = armed; i += 1
        Q[(t, sd)] = u[PRT]
LEGS = [('2026-09-25 15:40:00', '2026-09-25 20:42:00', +1),
        ('2026-09-26 13:22:00', '2026-09-26 15:33:00', +1),
        ('2026-09-26 15:17:00', '2026-09-26 21:00:00', -1),
        ('2026-09-26 20:45:00', '2026-09-27 02:30:00', +1),
        ('2026-09-27 02:15:00', '2026-09-27 05:15:00', -1),
        ('2026-09-27 05:00:00', '2026-09-27 08:30:00', +1)]
print('| his leg start | his leg end | its target | the print | it starts '
      '| where it genuinely ENDS | the line holding it last | that line\'s last printing row '
      '| its end against his end |')
print('|' + '---|' * 9)
#   HIS 1116: *"don't treat my end time as a cap. keep going until the lines have reached an end (ie
#   the wob expires)"*. So the wobbed state runs over the WHOLE tape and each leg's print is followed
#   from its start to wherever it genuinely ends - his stated end is a marker, not a bound.
STATE = {}
for t in TFS:
    for sd in (+1, -1):
        q = Q[(t, sd)]
        st = np.zeros(NR, np.int8); left = 0
        for i in range(NR):
            if q[i]:
                st[i], left = 2, WOB
            elif left > 0:
                st[i], left = 1, left - 1
        STATE[(t, sd)] = st
for a_s, z_s, sd in LEGS:
    A, Z = Kof(a_s), Kof(z_s)
    on = np.zeros(NR, bool)
    for t in TFS:
        on |= STATE[(t, sd)] > 0
    #   every consolidated print that BEGINS inside his leg, each followed to its genuine end. The
    #   start is bounded by his leg, the end never is.
    i, n = A, 0
    while i <= Z:
        if not on[i] or (i > A and on[i-1]):
            i += 1
            continue
        s0 = i
        j = s0
        while j < NR and on[j]:
            j += 1
        end = j - 1
        last = {}
        for t in TFS:
            pr = np.flatnonzero(Q[(t, sd)][s0:end + 1])
            if len(pr):
                last[t] = s0 + int(pr[-1])
        lt = max(last, key=lambda t: last[t]) if last else 0
        lr = last.get(lt, end)
        n += 1
        print('| %s | %s | %s | %d | %s | %s | ws%d | %s | %+d rows |'
              % (a_s[5:16], z_s[11:16], 'HIGH' if sd > 0 else 'LOW', n, U(s0)[11:16],
                 U(end)[11:16], lt, U(lr)[11:16], end - Z))
        i = j
    if not n:
        print('| %s | %s | %s | - | never | - | - | - | - |'
              % (a_s[5:16], z_s[11:16], 'HIGH' if sd > 0 else 'LOW'))
