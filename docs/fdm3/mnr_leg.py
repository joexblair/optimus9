"""HIS 1116 single leg: ws5, ws10, ws12, ws15 Mage, M-no-rev starts and stops over one leg.

HIS WORDS: *"instead of a wholesale view of m-no-rev, let's start with a single leg. using only ws5,
ws10, ws12, and ws15 Mage / using a leg that opens low side 09-25 1540 to a highside 1830 end (those
times include a pre and post ~10minute buffer) / create a timestamped table that shows when each of
the 4 lines (in comlumns) start to print a m-no-rev and stop printing a m-no-rev value. the quiet
bars are muted in the table"*.

THE MECH IT READS is 8788's: his 1116 reprint-on-an-extremum. The page prints only the HIGHEST
qualifying TF, so a per-TF view has to be computed rather than read off the row bytes.

*"the quiet bars are muted"* taken as: ONE ROW PER CHANGE. A bar where nothing starts or stops does
not print.

HIS 1116 WOB AND CONSOLIDATION: *"add a 18bar wob to all, and consolidate them. 'consolidate them':
if another line (opens or is already opened) when another line is (closing or is in wob limbo),
m-no-rev would create a continuous print. add this consolidated output column next to 'its
target-side'"*.

  THE WOB, per line: when a line stops qualifying it does not close - it enters WOB LIMBO for WOB
  rows. If it qualifies again inside that window the print never broke; if the window runs out, the
  line closes at the bar the wob expires.

  THE CONSOLIDATED COLUMN: on at any row where ANY of the lines is printing or sitting in its wob
  limbo. One unbroken run of that is one consolidated print, which is what his *"continuous print"*
  asks for.

  WOB IS IN 5 s EMERGING BARS, his 1117 correction: *"the terms 'bars' has always meant the 5s
  emerging bars for us both"*. So it is applied on the 5 s grid, where the qualification itself is
  computed, and the result is sampled at each row's print bar - NOT counted in the table's
  one-minute rows, which is what I had wrong. Every run prints the wob in bars and in seconds so the
  unit cannot drift again.

  HIS END TIME IS NOT A CAP, his 1117 clarification: *"if you have an open m-no-rev at my end time,
  keep walking until it is closed"*. So the table covers his whole leg and then keeps going, past
  his end, until the consolidated print closes. It never shortens his leg.
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
WOB = 18                        # HIS 1116 *"a 18bar wob"* - 5 s emerging bars, his 1117 unit, so 90 s
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
#   HIS 1116: he names a leg's target himself - *"the 2020 to 2210 leg's target is lowside"*, then a
#   list of five legs with their sides. THE SIDE IS AN INPUT, so a given side is read across the
#   whole leg and the oracle's own row byte is not consulted for the qualification. Without one,
#   the row byte decides, as the page does.
#   THE SIDE IS REQUIRED. The wob runs on the 5 s grid and the oracle's side byte is only sampled at
#   each row's print bar, so there is no 5 s side array to fall back on - rather than half-build one,
#   this asks for the side he already states per leg.
if len(sys.argv) < 4:
    raise SystemExit('give the leg its target: high or low. ' + __doc__.splitlines()[-2])
LEG_SIDE = {'high': +1, 'low': -1}[sys.argv[3].lower()]
idx = np.arange(ln.N)
QUAL, QUAL5, VAL, WHY = {}, {}, {}, {}
for t in TFS:
    em = np.asarray(ln.line('ws%dMage' % t), float)
    cp = np.asarray(CP.series(em, t*60), float)
    q = np.zeros(NR, bool); q5 = np.zeros(ln.N, bool); why = {}
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
        if sd == LEG_SIDE:
            q |= u5[PRT]
            q5 |= u5
        for bar, txt in note.items():
            why[bar] = txt
    QUAL[t] = q
    QUAL5[t] = q5
    VAL[t] = cp
    WHY[t] = why

#   HIS 1116 WOB on the 5 s grid: a line that stops qualifying sits in limbo for WOB bars before it
#   closes. `state` is 2 while it prints, 1 while it is in limbo and 0 once it has closed, sampled at
#   each row's print bar.
STATE = {}
for t in TFS:
    q5 = QUAL5[t]
    st5 = np.zeros(ln.N, np.int8)
    left = 0
    for i in range(ln.N):
        if q5[i]:
            st5[i], left = 2, WOB
        elif left > 0:
            st5[i], left = 1, left - 1
    STATE[t] = st5[PRT]
#   HIS *"consolidate them"*: on wherever ANY line is printing or in its limbo
CONS = np.zeros(NR, bool)
for t in TFS:
    CONS |= STATE[t] > 0

#   HIS 1117: his end is not a cap. If the consolidated print is still on at his end, the table
#   keeps going until it closes.
ZW = Z
while ZW + 1 < NR and CONS[ZW]:
    ZW += 1
print('# the leg %s .. %s, target as he named it: %s'
      % (U(A), U(Z), 'HIGH' if LEG_SIDE > 0 else 'LOW'))
print('| the row | its target-side | the consolidated print | ws5Mage | ws10Mage | ws12Mage | ws15Mage |')
print('|---|---|---|---|---|---|---|')
shown = 0
for i in range(A, ZW + 1):
    cells, change = [], False
    for t in TFS:
        now, was = int(STATE[t][i]), int(STATE[t][i-1] if i else 0)
        if now == 2 and was != 2:
            cells.append('STARTS %.1f' % VAL[t][PRT[i]] if was == 0 else 'back %.1f' % VAL[t][PRT[i]])
            change = True
        elif now == 1 and was == 2:
            cells.append('in wob'); change = True
        elif now == 0 and was != 0:
            cells.append('stops'); change = True
        else:
            cells.append('')
    c, cw = bool(CONS[i]), bool(CONS[i-1] if i else False)
    cc = 'STARTS' if (c and not cw) else 'stops' if (cw and not c) else ('on' if c else '')
    if c != cw:
        change = True
    if change:
        print('| %s | %s | %s | %s |'
              % (U(i), 'LOW' if sd_rows[i] < 0 else 'HIGH' if sd_rows[i] > 0 else 'none', cc,
                 ' | '.join(cells)))
        shown += 1
print()
print('| the span | value |')
print('|---|---|')
for t in TFS:
    cp = VAL[t][PRT][A:Z + 1]
    with np.errstate(invalid='ignore'):
        nh, nl = int((cp >= K.OOB_HI).sum()), int((cp <= K.OOB_LO).sum())
    on = nh if (LEG_SIDE or 0) > 0 else nl if (LEG_SIDE or 0) < 0 else nh + nl
    print('| ws%dMage, its range and its oob bars on the leg target | %.1f .. %.1f, %d |'
          % (t, np.nanmin(cp), np.nanmax(cp), on))
print('| rows in his leg | %d |' % (Z - A + 1))
print('| rows walked, his leg plus the tail to close an open print | %d, to %s |'
      % (ZW - A + 1, U(ZW)))
print('| rows with a start or a stop | %d |' % shown)
print('| the wob | %d bars of 5 s, so %d s | ' % (WOB, WOB * 5))
runs = 0
for i in range(A, ZW + 1):
    if CONS[i] and not (CONS[i-1] if i > A else False):
        runs += 1
print('| consolidated prints in the span | %d |' % runs)
print('| rows the consolidated print covers | %d of %d walked |'
      % (int(CONS[A:ZW+1].sum()), ZW - A + 1))
print('| the target-side at %s | %s |' % (U(A), 'LOW' if sd_rows[A] < 0 else 'HIGH'))
print('| the target-side at %s | %s |' % (U(Z), 'LOW' if sd_rows[Z] < 0 else 'HIGH'))
ch = [i for i in range(A, Z+1) if sd_rows[i] != sd_rows[i-1]]
print('| pivot rows inside the span | %s |' % (', '.join(U(i)[11:16] for i in ch) or 'none'))
