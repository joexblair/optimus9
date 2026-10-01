"""build_ws5mage_backing_wob - ws5mage_sig_backing rebuilt with the fence-specific arm wob.

Joe 0930: *"apply the suggested wobs and rebuild the table"*, after the wob curve measured off the
un-wobbed rows:

    fence 15/85   wob 2 bars = 10 s   332 of 439 runs kept, 30 of 30 carriers, 36 of 36 signals
    fence 25/75   wob 6 bars = 30 s   242 of 518 runs kept, 35 of 35 carriers, 51 of 51 signals

Both are the LARGEST wob that costs no carrier. The ceiling is the shortest carrier run at each
fence - 2 bars at 09-02 15:15:05 for 15/85, 7 bars at 09-01 23:24:45 for 25/75.

THE WOBS ARE IN THE KNOBS STRING, so these rows land BESIDE the un-wobbed ones, not over them.
Nothing is dropped and the A/B stays queryable - `wsb_knobs LIKE '%wob%'` selects this build.

ONE SCRIPT, whole table. Supersedes the three-step build (build_ws5mage_sig_backing.py, then
update_..._latch.py, then add_..._unclaimed_excursions.py) which remain for the un-wobbed rows.

ROWS
  kind 'signal'     one per banked sig bar in the span. The signal set does NOT depend on the wob.
  kind 'excursion'  one per ws5Mage oob run that reaches the fence's wob and carries NO signal.
THE LATCH columns use the fence's own wob, not a shared 9 - the arm cannot be set by a run shorter
than the wob that defines an arm.

    python3 docs/22_go_20260921/build_ws5mage_backing_wob.py
"""
import sys, os, datetime as dt, logging
sys.path.insert(0, os.environ['CLAUDE_JOB_DIR'] + '/tmp'); sys.path.insert(0, '/home/joe/thecodes')
logging.disable(logging.CRITICAL)
import numpy as np, mechdev_rig
from optimus9.compute.coil_moment import moments as coil_moments, release
from optimus9.compute import coil_exit
from optimus9.analysis.jig import ws1mage_rev
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

TABLE = 'ws5mage_sig_backing'
MID = 50.0
WOB = {'15/85': 2, '25/75': 6}                        # Joe 0930, measured knee per fence
FEN = {'15/85': (15.0, 85.0), '25/75': (25.0, 75.0)}
MS = lambda y, m, d, h=0: int(dt.datetime(y, m, d, h, tzinfo=dt.timezone.utc).timestamp() * 1000)
END = MS(2026, 9, 8); D0, D1 = MS(2026, 9, 1), MS(2026, 9, 4)
rig = mechdev_rig.load(expect_end_ms=END)
Mg = np.asarray(rig.lines['ws5']['Mage'], float)
tsa = np.asarray(rig.ts, np.int64)
U = lambda k: dt.datetime.fromtimestamp(int(rig.ts[k]) / 1000, dt.timezone.utc)
k0 = int(np.searchsorted(tsa, D0)); k1 = int(np.searchsorted(tsa, D1))
FLOOR = rig.bar('2026-08-31 00:00:00')
KNOBS = ('end%s_span%s..%s_latch_ws1Mage.ws%sm_magefence%g.%g_wob1585.%d_wob2575.%d'
         % (dt.datetime.fromtimestamp(END / 1000, dt.timezone.utc).strftime('%Y%m%d'),
            dt.datetime.fromtimestamp(D0 / 1000, dt.timezone.utc).strftime('%Y%m%d'),
            dt.datetime.fromtimestamp(D1 / 1000, dt.timezone.utc).strftime('%Y%m%d'),
            rig.Ct['latch_tf'], float(rig.Ct['mage_fence_lo']), float(rig.Ct['mage_fence_hi']),
            WOB['15/85'], WOB['25/75']))
print('B|knobs %s' % KNOBS)
print('B|wobs|15/85 %d bars = %d s|25/75 %d bars = %d s'
      % (WOB['15/85'], WOB['15/85'] * 5, WOB['25/75'], WOB['25/75'] * 5))


def runs(fl):
    lo_, hi_ = FEN[fl]; out = []; st = None; sd = None
    for k in range(k0, k1):
        d = int(rig.DR[k])
        o = (Mg[k] >= hi_) if d > 0 else (Mg[k] <= lo_)
        if o and st is None: st, sd = k, d
        elif o and d != sd: out.append((st, k - 1, sd)); st, sd = k, d
        elif (not o) and st is not None: out.append((st, k - 1, sd)); st = None
    if st is not None: out.append((st, k1 - 1, sd))
    return out


def run_at(k, d, fl):
    lo_, hi_ = FEN[fl]
    o = lambda i: ((Mg[i] >= hi_) if int(rig.DR[i]) > 0 else (Mg[i] <= lo_))
    if not o(k): return None
    a = k
    while a > k0 and o(a - 1) and int(rig.DR[a - 1]) == d: a -= 1
    b = k
    while b < k1 - 1 and o(b + 1) and int(rig.DR[b + 1]) == d: b += 1
    return a, b


def latch(k, fl):
    """live latch at k using THIS fence's wob. set on wob, cancel on a 50-cross.

    THE ARM IS THE FIRST BAR THE DWELL COMPLETES after the last cancel - not the last bar that
    happens to sit past the wob. Joe 0930 caught the original: inside a long oob run EVERY bar from
    the wob onward satisfies `run >= wob`, so taking the last one put the arm on the row's own bar.
    Same class as the twowin.py defect - counting bars already past the wob instead of the bar that
    reaches it.
    """
    lo_, hi_ = FEN[fl]; w = WOB[fl]
    j = k
    while j > FLOOR:
        if (Mg[j] - MID) * (Mg[j - 1] - MID) < 0: break
        j -= 1
    arm = None; run = 0
    for i in range(j, k + 1):
        d = int(rig.DR[i])
        o = (Mg[i] >= hi_) if d > 0 else (Mg[i] <= lo_)
        if o and (run == 0 or int(rig.DR[i - 1]) == d): run += 1
        else: run = 0
        if run >= w:
            arm = i; break          # the FIRST bar the dwell completes, not the last bar past it
    return (arm, int((int(rig.ts[k]) - int(rig.ts[arm])) / 1000)) if arm is not None else None


# ---- the banked signal set, same chain as +0.3911 ----
import optimus9.orchestration.build_ws_lines as BWL
BWL.END_MS = END; BWL.TAPE_END = dt.datetime.fromtimestamp(END / 1000, dt.timezone.utc)
import sweep_v3_signal as S
full = S.Rig((MS(2026, 6, 10), END)); cfg = dict(S.BASE)
tfs = [t for t in full.tfs if cfg['tf_lo'] <= t <= cfg['tf_hi']]
fin = 0
for tf in tfs:
    for r_ in ('m', 'Mage', 'r'):
        fin = max(fin, int(np.argmax(np.isfinite(np.asarray(full.lines['ws%d' % tf][r_], float)))))
A = max(full.A, fin); B = full.B
segs = []; s = A
for k in range(A + 1, B + 1):
    if full.DR[k] != full.DR[k - 1]: segs.append((s, k - 1, int(full.DR[s]))); s = k
segs.append((s, B, int(full.DR[s])))
FL, FH = cfg['fence_lo'], cfg['fence_hi']; vr = []
for tf in tfs:
    sw = full.sideways(tf, cfg); r_ = full.R[tf]
    q = sw & np.isfinite(r_) & ((r_ < FL) | (r_ > FH))
    for (a_, b_, d) in segs:
        if not d: continue
        seg = q[a_:b_ + 1]
        if seg.any(): vr.append((a_ + int(np.argmax(seg)), tf, d))
vr.sort(key=lambda x: (x[0], x[1]))
SUP = np.zeros(full.n, np.int16); SUPM = np.zeros(full.n, np.int16)
for tf in tfs:
    SUP += (full.D[tf] > 0).astype(np.int16); SUPM += (full.D[tf] < 0).astype(np.int16)
ann = [dict(i=i, dr=d, ok=bool((SUP[i] if d > 0 else SUPM[i]) >= cfg['support_min']))
       for (i, tf, d) in vr]
LEGS = ws1mage_rev(full.lines['ws1']['Mage'],
                   full.lines[full.C['sig_line'].replace('Mage', '')]['Mage'], full.hi, full.lo,
                   dwell=cfg['dwell'], rev_wob=cfg['rev_wob'], hold=cfg['boundary_xwob'])
lag = 180 // 5; look = cfg['lookback_s'] // 5; sigs = {}
for m in coil_moments(ann):
    d = m['dr']; cc = (lambda i, _d=d: float(full.CC[i] * _d))
    p, conf = release(cc, m['i0'], m['i1'], lag, last_bar=full.n - 1)
    ex = coil_exit.resolve(m, p, conf, LEGS[d], lag, look, bool(cfg['gap_fill']))
    if ex['rev'] is None: continue
    sg = int(ex['rev'])
    if A <= sg <= B: sigs.setdefault(sg, (d, ex['via']))
win = sorted(k for k in sigs if k0 <= k < k1)
print('B|banked sig bars in the span: %d' % len(win))

COLS = ['wsb_knobs', 'wsb_kind', 'wsb_fence', 'wsb_sig_utc', 'wsb_sig_ms', 'wsb_dr', 'wsb_via',
        'wsb_ws5mage',
        'wsb_oob_1585', 'wsb_run1585_start', 'wsb_run1585_end', 'wsb_run1585_bars',
        'wsb_run1585_secs', 'wsb_bars_before1585', 'wsb_bars_after1585',
        'wsb_oob_2575', 'wsb_run2575_start', 'wsb_run2575_end', 'wsb_run2575_bars',
        'wsb_run2575_secs', 'wsb_bars_before2575', 'wsb_bars_after2575',
        'wsb_latch1585', 'wsb_latch1585_arm', 'wsb_latch1585_secs',
        'wsb_latch2575', 'wsb_latch2575_arm', 'wsb_latch2575_secs']


def fence_block(k, d):
    """the 12 run columns then the 6 latch columns, both fences, wob-aware."""
    out = []
    for fl in ('15/85', '25/75'):
        r = run_at(k, d, fl)
        if r is None or (r[1] - r[0] + 1) < WOB[fl]:
            out += [0, None, None, None, None, None, None]
        else:
            a, b = r
            out += [1, U(a), U(b), b - a + 1, (b - a + 1) * 5, k - a, b - k]
    for fl in ('15/85', '25/75'):
        L = latch(k, fl)
        out += [0, None, None] if L is None else [1, U(L[0]), L[1]]
    return out


pay = []; carr = {'15/85': set(), '25/75': set()}
for k in win:
    d, via = sigs[k]
    blk = fence_block(k, d)
    for fl, idx in (('15/85', 1), ('25/75', 8)):
        if blk[0 if fl == '15/85' else 7] == 1:
            carr[fl].add(int(blk[idx].timestamp() * 1000))
    pay.append(tuple([KNOBS, 'signal', None, U(k), int(rig.ts[k]), d, via,
                      float(Mg[k]) if np.isfinite(Mg[k]) else None] + blk))
stat = {}
for fl in ('15/85', '25/75'):
    allr = runs(fl); kept = [r for r in allr if (r[1] - r[0] + 1) >= WOB[fl]]
    unc = [r for r in kept if int(rig.ts[r[0]]) not in carr[fl]]
    stat[fl] = (len(allr), len(kept), len(carr[fl]), len(unc))
    for (a, b, d) in unc:
        pay.append(tuple([KNOBS, 'excursion', fl, U(a), int(rig.ts[a]), d, 'none',
                          float(Mg[a]) if np.isfinite(Mg[a]) else None] + fence_block(a, d)))
for fl in ('15/85', '25/75'):
    t, kp, c, u = stat[fl]
    print('B|fence %s|runs %d|reach wob %d|carriers %d|UNCLAIMED rows %d' % (fl, t, kp, c, u))
db = DatabaseManager(**get_db_config()); db.connect()
have = db.execute('SELECT COUNT(*) c FROM %s WHERE wsb_knobs=%%s' % TABLE, (KNOBS,),
                  fetch=True)[0]['c']
if have:
    print('B|%d rows already banked at these knobs - nothing written' % have)
else:
    db.executemany('INSERT INTO %s (%s) VALUES (%s)'
                   % (TABLE, ','.join(COLS), ','.join(['%s'] * len(COLS))), pay)
    print('B|inserted %d rows' % len(pay))
for r in db.execute("SELECT wsb_kind k, wsb_fence f, COUNT(*) n FROM %s WHERE wsb_knobs=%%s "
                    "GROUP BY 1,2 ORDER BY 1,2" % TABLE, (KNOBS,), fetch=True):
    print('B|this build|kind %-9s fence %-6s rows %s' % (r['k'], r['f'] or '-', r['n']))
print('B|--- both builds side by side ---')
for r in db.execute("SELECT wsb_knobs k, wsb_kind d, wsb_fence f, COUNT(*) n FROM %s "
                    "GROUP BY 1,2,3 ORDER BY 1,2,3" % TABLE, fetch=True):
    print('B|%s|%s|%s|%s' % ('wob' if 'wob' in r['k'] else 'no-wob', r['d'], r['f'] or '-', r['n']))
db.disconnect()
