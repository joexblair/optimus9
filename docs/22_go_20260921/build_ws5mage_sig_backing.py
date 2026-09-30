"""build_ws5mage_sig_backing - which banked signals sit on a ws5Mage oob run.

Joe 0930: *"I want to validate how often ws5mage crosses to oob, and how long it dwells vs the
0.3991 signals. ie, which signals are backed by ws5Mage oob"* / *"report for 09-01 to 09-03"* /
*"I need this as a table - drop them into the db please"* / *"make it one table. the signal N of 68
can be represented in one column as a timestamp"*.

ONE ROW PER BANKED SIGNAL. `wsb_sig_utc` is the row's identity - there is no N-of-68 column.

THE SIGNAL SET is the chain that produced +0.3911 per trade, rebuilt from sweep_v3_signal.Rig at
END_MS 2026-09-08 - NOT from wsf_leash, whose 121 rows sit 15 s earlier because the sig_conf
re-bank Joe ruled on 0929 is still un-applied.

BOTH FENCES ARE STORED. oob 15/85 is Joe's standing meaning of oob; Mage 25/75 is what the 3-signal
knob sweep selected. The fence is an OPEN question - 3 signals pointed at 25/75, 5 at 15/85 - so
neither is assumed and both get their own columns.

MINE, STATED
  1 a run is attributed to the dr at its FIRST bar, and a dr flip mid-run SPLITS it into two runs.
    The alternative lets a run span a flip, which makes "oob on the dr side" ambiguous.
  2 the run columns are the run CONTAINING the sig bar. When the sig bar is not oob they are NULL -
    the nearest neighbouring run is not recorded.
  3 the table name and column names are mine. Joe named the mechanic parts: ws5Mage, oob, dwell,
    signal, backed.

NOTHING IS DROPPED. New table, new name.

    python3 docs/22_go_20260921/build_ws5mage_sig_backing.py
    python3 docs/22_go_20260921/build_ws5mage_sig_backing.py --drop   # drops only THIS table
"""
import sys, datetime as dt, logging
sys.path.insert(0, '/home/joe/thecodes')
import numpy as np
import optimus9.orchestration.build_ws_lines as BWL
MS = lambda y, m, d, h=0: int(dt.datetime(y, m, d, h, tzinfo=dt.timezone.utc).timestamp() * 1000)
END = MS(2026, 9, 8)
BWL.END_MS = END; BWL.TAPE_END = dt.datetime.fromtimestamp(END / 1000, dt.timezone.utc)
logging.disable(logging.CRITICAL)
import sweep_v3_signal as S
from optimus9.compute.coil_moment import moments as coil_moments, release
from optimus9.compute import coil_exit
from optimus9.analysis.jig import ws1mage_rev
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

TABLE = 'ws5mage_sig_backing'
D0, D1 = MS(2026, 9, 1), MS(2026, 9, 4)          # Joe: 09-01 to 09-03 inclusive
F15, F25 = (15.0, 85.0), (25.0, 75.0)

DDL = '''CREATE TABLE IF NOT EXISTS %s (
    wsb_pk              BIGINT AUTO_INCREMENT PRIMARY KEY,
    wsb_knobs           VARCHAR(120) NOT NULL,
    wsb_sig_utc         DATETIME(3)  NOT NULL,
    wsb_sig_ms          BIGINT       NOT NULL,
    wsb_dr              TINYINT      NOT NULL,
    wsb_via             VARCHAR(16)  NOT NULL,
    wsb_ws5mage         DECIMAL(10,4) NULL,
    wsb_oob_1585        TINYINT      NOT NULL,
    wsb_run1585_start   DATETIME(3)  NULL,
    wsb_run1585_end     DATETIME(3)  NULL,
    wsb_run1585_bars    INT          NULL,
    wsb_run1585_secs    INT          NULL,
    wsb_bars_before1585 INT          NULL,
    wsb_bars_after1585  INT          NULL,
    wsb_oob_2575        TINYINT      NOT NULL,
    wsb_run2575_start   DATETIME(3)  NULL,
    wsb_run2575_end     DATETIME(3)  NULL,
    wsb_run2575_bars    INT          NULL,
    wsb_run2575_secs    INT          NULL,
    wsb_bars_before2575 INT          NULL,
    wsb_bars_after2575  INT          NULL,
    UNIQUE KEY uq_wsb (wsb_knobs, wsb_sig_ms),
    KEY k_sig (wsb_sig_ms))''' % TABLE

db = DatabaseManager(**get_db_config()); db.connect()
if '--drop' in sys.argv:
    db.execute('DROP TABLE IF EXISTS %s' % TABLE); print('B|dropped %s' % TABLE)
db.execute(DDL)

rig = S.Rig((MS(2026, 6, 10), MS(2026, 9, 8))); cfg = dict(S.BASE); ts = rig.ts
tsa = np.asarray(ts, np.int64)
U = lambda k: dt.datetime.fromtimestamp(int(ts[k]) / 1000, dt.timezone.utc)
k0 = int(np.searchsorted(tsa, D0)); k1 = int(np.searchsorted(tsa, D1))
Mg = np.asarray(rig.lines['ws5']['Mage'], float)
KNOBS = ('end%s_span%s..%s_latch_ws1Mage.ws%sm_magefence%g.%g'
         % (dt.datetime.fromtimestamp(END / 1000, dt.timezone.utc).strftime('%Y%m%d'),
            dt.datetime.fromtimestamp(D0 / 1000, dt.timezone.utc).strftime('%Y%m%d'),
            dt.datetime.fromtimestamp(D1 / 1000, dt.timezone.utc).strftime('%Y%m%d'),
            rig.Ct['latch_tf'], float(rig.Ct['mage_fence_lo']), float(rig.Ct['mage_fence_hi'])))

# ---- the banked signal set, same chain as +0.3911 ----
tfs = [t for t in rig.tfs if cfg['tf_lo'] <= t <= cfg['tf_hi']]
fin = 0
for tf in tfs:
    for r_ in ('m', 'Mage', 'r'):
        fin = max(fin, int(np.argmax(np.isfinite(np.asarray(rig.lines['ws%d' % tf][r_], float)))))
A = max(rig.A, fin); B = rig.B
segs = []; s = A
for k in range(A + 1, B + 1):
    if rig.DR[k] != rig.DR[k - 1]: segs.append((s, k - 1, int(rig.DR[s]))); s = k
segs.append((s, B, int(rig.DR[s])))
FL, FH = cfg['fence_lo'], cfg['fence_hi']; rows = []
for tf in tfs:
    sw = rig.sideways(tf, cfg); r_ = rig.R[tf]
    q = sw & np.isfinite(r_) & ((r_ < FL) | (r_ > FH))
    for (a_, b_, d) in segs:
        if not d: continue
        seg = q[a_:b_ + 1]
        if seg.any(): rows.append((a_ + int(np.argmax(seg)), tf, d))
rows.sort(key=lambda x: (x[0], x[1]))
SUP = np.zeros(rig.n, np.int16); SUPM = np.zeros(rig.n, np.int16)
for tf in tfs:
    SUP += (rig.D[tf] > 0).astype(np.int16); SUPM += (rig.D[tf] < 0).astype(np.int16)
ann = [dict(i=i, dr=d, ok=bool((SUP[i] if d > 0 else SUPM[i]) >= cfg['support_min']))
       for (i, tf, d) in rows]
look = cfg['lookback_s'] // 5
LEGS = ws1mage_rev(rig.lines['ws1']['Mage'],
                   rig.lines[rig.C['sig_line'].replace('Mage', '')]['Mage'], rig.hi, rig.lo,
                   dwell=cfg['dwell'], rev_wob=cfg['rev_wob'], hold=cfg['boundary_xwob'])
lag = 180 // 5; sigs = {}
for m in coil_moments(ann):
    d = m['dr']; cc = (lambda i, _d=d: float(rig.CC[i] * _d))
    p, conf = release(cc, m['i0'], m['i1'], lag, last_bar=rig.n - 1)
    ex = coil_exit.resolve(m, p, conf, LEGS[d], lag, look, bool(cfg['gap_fill']))
    if ex['rev'] is None: continue
    sg = int(ex['rev'])
    if A <= sg <= B: sigs.setdefault(sg, (d, ex['via']))
win = sorted(k for k in sigs if k0 <= k < k1)
print('B|%s|knobs %s' % (TABLE, KNOBS))
print('B|banked sig bars in %s -> %s: %d'
      % (U(k0).strftime('%Y-%m-%d'), U(k1 - 1).strftime('%Y-%m-%d'), len(win)))


def run_at(k, d, fen):
    """the oob run CONTAINING bar k on the dr side, or None. Splits at a dr flip."""
    lo_, hi_ = fen
    o = lambda i: ((Mg[i] >= hi_) if int(rig.DR[i]) > 0 else (Mg[i] <= lo_))
    if not o(k): return None
    a_ = k
    while a_ > k0 and o(a_ - 1) and int(rig.DR[a_ - 1]) == d: a_ -= 1
    b_ = k
    while b_ < k1 - 1 and o(b_ + 1) and int(rig.DR[b_ + 1]) == d: b_ += 1
    return a_, b_


pay = []
for k in win:
    d, via = sigs[k]
    r15 = run_at(k, d, F15); r25 = run_at(k, d, F25)
    rec = [KNOBS, U(k), int(ts[k]), d, via, float(Mg[k]) if np.isfinite(Mg[k]) else None]
    for r in (r15, r25):
        if r is None:
            rec += [0, None, None, None, None, None, None]
        else:
            a_, b_ = r
            rec += [1, U(a_), U(b_), b_ - a_ + 1, (b_ - a_ + 1) * 5, k - a_, b_ - k]
    pay.append(tuple(rec))
COLS = ['wsb_knobs', 'wsb_sig_utc', 'wsb_sig_ms', 'wsb_dr', 'wsb_via', 'wsb_ws5mage',
        'wsb_oob_1585', 'wsb_run1585_start', 'wsb_run1585_end', 'wsb_run1585_bars',
        'wsb_run1585_secs', 'wsb_bars_before1585', 'wsb_bars_after1585',
        'wsb_oob_2575', 'wsb_run2575_start', 'wsb_run2575_end', 'wsb_run2575_bars',
        'wsb_run2575_secs', 'wsb_bars_before2575', 'wsb_bars_after2575']
have = db.execute('SELECT COUNT(*) c FROM %s WHERE wsb_knobs=%%s' % TABLE, (KNOBS,),
                  fetch=True)[0]['c']
if have:
    print('B|%d rows already banked at these knobs - nothing written' % have)
else:
    db.executemany('INSERT INTO %s (%s) VALUES (%s)'
                   % (TABLE, ','.join(COLS), ','.join(['%s'] * len(COLS))), pay)
    print('B|banked %d rows|oob 15/85 %d|oob 25/75 %d'
          % (len(pay), sum(1 for r in pay if r[6] == 1), sum(1 for r in pay if r[13] == 1)))
db.disconnect()
