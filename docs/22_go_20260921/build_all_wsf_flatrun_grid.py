"""build_all_wsf_flatrun_grid - the `flatrun` row of all_wsf_flatruns, on an 8-MINUTE GRID.

Joe 0930: *"build a db table that shows the `flatrun` data (it's a row in all_wsf_flatruns) at 8
minute intervals, for 09-01"*, then *"use ws4r to ws23r"*.

WHAT IT IS. `all_wsf_flatruns` carries eight rows per wsl_sig_utc, one of which is `flatrun`. That
table is keyed on SIGNALS, so the flat-run reading only exists at the 121 signal bars. This table
takes the same reading and samples it on a regular 8-minute grid across 09-01 - 180 anchors,
00:00:00 through 23:52:00 - whether or not a signal happened there.

THE CELL IS THE BANKED ONE, UNCHANGED:

    j = first bar at or after (anchor - BACK) where flat_run_at(RA[t], j, dr, FENCE, SAMPLES, TOL)
        is not None,  rendered hh:mm

  BACK 96 bars = 8 min, FENCE = momo_fence_r 17/83, SAMPLES 3, TOL 2.0 - all read from the same
  places build_all_wsf_flatruns.py reads them, via the same _prelude. NULL means no flat run fired
  anywhere from the lookback start to the end of the tape.

  With 8-minute anchors and an 8-minute lookback the search windows TILE EXACTLY: anchor N starts
  looking at the bar anchor N-1 sits on.

THREE THINGS ARE MINE AND ARE STATED

1 NO INSTANCE COLUMN. The banked table carries v7 and v8 because the SIGNALS differ between them.
  `flat_run_at` reads only the r-line, the dr and the knobs - it never touches coil_lines - so on a
  fixed grid there is nothing for an instance to change. One row per (anchor, dr source).

2 THE dr IS CARRIED TWICE, NOT CHOSEN. The banked table uses `wsl_dr`, which does not exist at an
  anchor that is not a signal. Rather than pick a substitute, this writes TWO rows per anchor and
  says which in `afg_dr_src`:
      latch       dr_latch.latch at the anchor bar - no wob, what wsl_dr is derived from
      latch_wob   dr_latch.latch_wob at LATCH_W 8, what the trade walk reads live
  They differ on 7 of 242 rows in the banked leash set, so the choice is not free and it is Joe's.

3 THE WINDOW IS END_MS 2026-09-08 00:00 - the window all_wsf_flatruns was built on, so the two are
  comparable cell for cell. TAPE_END currently points at 2026-09-30; this sets END_MS back for its
  own run only and does not touch the constant.

NOTHING IS DROPPED. `all_wsf_flatruns` is untouched.

    python3 docs/22_go_20260921/build_all_wsf_flatrun_grid.py
    python3 docs/22_go_20260921/build_all_wsf_flatrun_grid.py --drop   # drops only the GRID table
"""
import sys, os, io, datetime as dt
from datetime import timezone

sys.path.insert(0, '/home/joe/thecodes')
import optimus9.orchestration.build_ws_lines as BWL
BWL.TAPE_END = dt.datetime(2026, 9, 8, 0, 0, tzinfo=timezone.utc)
BWL.END_MS = int(BWL.TAPE_END.timestamp() * 1000)

import numpy as np
_o = sys.stdout; sys.stdout = io.StringIO()
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '_prelude.py'))
     .read().split("k=int(np.searchsorted")[0])
sys.stdout = _o
from optimus9.compute.test_points import flat_run_at
from optimus9.compute.dr_latch import latch, latch_wob
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
from optimus9.compute import trade_config as TC

TABLE = 'all_wsf_flatrun_grid'
TFS = range(4, 24)                       # Joe 0930: "use ws4r to ws23r"
SAMPLES = 3; TOL = 2.0; BACK = 96        # 96 bars = 8 min, the banked lookback
STEP = 96                                # 96 bars = 8 min, Joe's interval
DAY = '2026-09-01'
KNOBS = 'fence%g.%g_samples%d_tol%g_back%d' % (FENCE[0], FENCE[1], SAMPLES, TOL, BACK)

DDL = '''CREATE TABLE IF NOT EXISTS %s (
    afg_pk       BIGINT AUTO_INCREMENT PRIMARY KEY,
    afg_knobs    VARCHAR(80) NOT NULL,
    afg_day      VARCHAR(10) NOT NULL,
    afg_dr_src   VARCHAR(10) NOT NULL,
    afg_n        SMALLINT    NOT NULL,
    afg_dr       TINYINT     NOT NULL,
    afg_at_utc   DATETIME(3) NOT NULL,
    afg_at_ms    BIGINT      NOT NULL,
    %s
    UNIQUE KEY uq_afg (afg_knobs, afg_day, afg_dr_src, afg_at_ms),
    KEY k_at (afg_at_ms, afg_dr_src))''' % (
    TABLE, '\n    '.join('afg_ws%d VARCHAR(32) NULL,' % t for t in TFS))
COLS = (['afg_knobs', 'afg_day', 'afg_dr_src', 'afg_n', 'afg_dr', 'afg_at_utc', 'afg_at_ms']
        + ['afg_ws%d' % t for t in TFS])

db = DatabaseManager(**get_db_config()); db.connect()
if '--drop' in sys.argv:
    db.execute('DROP TABLE IF EXISTS %s' % TABLE); print('B|dropped %s' % TABLE)
db.execute(DDL)
Ct = TC.load(db, TC.V)

tsa = np.asarray(ts, dtype=np.int64)
d0 = int(dt.datetime.strptime(DAY, '%Y-%m-%d').replace(tzinfo=timezone.utc).timestamp() * 1000)
d1 = d0 + 86400000
a0 = int(np.searchsorted(tsa, d0)); a1 = int(np.searchsorted(tsa, d1))
anchors = list(range(a0, a1, STEP))
G1 = np.asarray(MA[1], float)
M13 = np.asarray(Ln(int(Ct['latch_tf']), 'm'), float)
DR_L = latch(G1, M13, 0, len(tsa) - 1,
             hi=float(Ct['mage_fence_hi']), lo=float(Ct['mage_fence_lo']))
DR_W = latch_wob(G1, M13, 0, len(tsa) - 1, wob=int(Ct['latch_wob']),
                 hi=float(Ct['mage_fence_hi']), lo=float(Ct['mage_fence_lo']))
print('B|%s|knobs %s|day %s|tfs ws%d..ws%d|anchors %d at %d bars = %d min'
      % (TABLE, KNOBS, DAY, TFS[0], TFS[-1], len(anchors), STEP, STEP * 5 // 60))
print('B|window END_MS %s|tape %s -> %s|%d bars'
      % (BWL.TAPE_END.strftime('%Y-%m-%d %H:%M'), U(0), U(len(tsa) - 1), len(tsa)))

RR = {t: np.asarray(RA[t], float) for t in TFS}
hhmm = lambda j: U(j)[11:16]
pay = []; nul = 0; pre = 0; cells = 0
for src, DRA in (('latch', DR_L), ('latch_wob', DR_W)):
    for n_, k in enumerate(anchors, 1):
        d = int(DRA[k])
        if d == 0: d = 1                                  # the latch has not set yet; flat_run_at needs a side
        s0 = max(0, k - BACK)
        row = [KNOBS, DAY, src, n_, int(DRA[k]), U(k), int(tsa[k])]
        for t in TFS:
            j = next((q for q in range(s0, len(tsa))
                      if flat_run_at(RR[t], q, d, FENCE, SAMPLES, TOL) is not None), None)
            cells += 1
            if j is None:
                row.append(None); nul += 1
            else:
                row.append(hhmm(j))
                if j < k: pre += 1
        pay.append(tuple(row))
have = db.execute('SELECT COUNT(*) c FROM %s WHERE afg_knobs=%%s AND afg_day=%%s' % TABLE,
                  (KNOBS, DAY), fetch=True)[0]['c']
if have:
    print('B|%d rows already banked at this knobs/day - nothing written' % have)
else:
    db.executemany('INSERT INTO %s (%s) VALUES (%s)'
                   % (TABLE, ','.join(COLS), ','.join(['%s'] * len(COLS))), pay)
    print('B|banked %d rows|%d cells|NULL %d|cell EARLIER than its anchor %d'
          % (len(pay), cells, nul, pre))
db.disconnect()
