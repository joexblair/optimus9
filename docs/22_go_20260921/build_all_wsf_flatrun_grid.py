"""build_all_wsf_flatrun_grid - the `flatrun` row of all_wsf_flatruns, on a 4-MINUTE GRID.

Joe 0930: *"build a db table that shows the `flatrun` data (it's a row in all_wsf_flatruns) at 8
minute intervals, for 09-01"*, then *"use ws4r to ws23r"*.

RE-GRIDDED TO 4 MINUTES, Joe 1001: *"overwrite (authorised) the current all_wsf_flatrun_grid table
with 4 minute spaced rows"*. `STEP` 96 -> 48 bars. **`BACK` STAYS AT 96 bars = 8 min** - asked
directly, with the tiling consequence in front of him, and he chose it over following the lookback
down to 4 min.

WHAT IT IS. `all_wsf_flatruns` carries eight rows per wsl_sig_utc, one of which is `flatrun`. That
table is keyed on SIGNALS, so the flat-run reading only exists at the 121 signal bars. This table
takes the same reading and samples it on a regular 4-minute grid across 09-01 - 360 anchors,
00:00:00 through 23:56:00 - whether or not a signal happened there.

THE CELL IS THE BANKED ONE, UNCHANGED:

    j = first bar at or after (anchor - BACK) where flat_run_at(RA[t], j, dr, FENCE, SAMPLES, TOL)
        is not None,  rendered hh:mm

  BACK 96 bars = 8 min, FENCE = momo_fence_r 17/83, SAMPLES 3, TOL 2.0 - all read from the same
  places build_all_wsf_flatruns.py reads them, via the same _prelude. NULL means no flat run fired
  anywhere from the lookback start to the end of the tape.

  THE WINDOWS NO LONGER TILE - THEY OVERLAP BY 4 MINUTES, AND THAT IS JOE'S CHOICE. At `STEP` 48
  and `BACK` 96 each anchor searches the 8 min behind it while anchors sit 4 min apart, so every
  bar is searched twice and ADJACENT ANCHORS OFTEN RETURN THE SAME FLAT-RUN BAR. He was offered the
  tiling alternative - `BACK` following to 48 - and chose this. The grid therefore samples more
  often WITHOUT searching anything new: 720 rows, fewer distinct cell values than rows.

  The 8-minute version tiled exactly: anchor N started looking at the bar anchor N-1 sat on. Its
  rows are gone, per his authorised overwrite, and its knobs string is NOT reusable - see 4 below.

THREE THINGS ARE MINE AND ARE STATED

1 NO INSTANCE COLUMN. The banked table carries v7 and v8 because the SIGNALS differ between them.
  `flat_run_at` reads only the r-line, the dr and the knobs - it never touches coil_lines - so on a
  fixed grid there is nothing for an instance to change. One row per (anchor, dr source).

5 `afg_ws{t}_bars` IS WRITTEN BY THIS SCRIPT NOW, AND IT WAS NOT. The 20 `_bars` columns existed in
  the table and held values, but NOTHING IN THE REPO POPULATED THEM - they were added and filled by
  an ad-hoc command in an earlier session and never banked as code. The 1001 re-grid's authorised
  overwrite deleted those rows and wrote 720 new ones with all 20 columns NULL, which is how the
  gap surfaced. They are computed here, in the same loop, from values this script already holds.

  WHY THE COLUMN EXISTS: `afg_ws{t}` is rendered `hh:mm` by `hhmm = lambda j: U(j)[11:16]`, which
  DROPS THE DATE. The search starts at `anchor - BACK` and runs to the END OF THE TAPE when no flat
  run fires inside the lookback, so a cell can sit days away from its anchor and still read as a
  plausible time. `afg_ws{t}_bars` is the SIGNED bar offset `j - k`: negative is before the anchor,
  positive after, and 2,803 of 14,400 cells on the 4-minute grid are negative. Without it the
  `hh:mm` is ambiguous.

4 `STEP` IS NOW IN THE KNOBS STRING, AND IT WAS NOT BEFORE. MINE. The old string
  `fence17.83_samples3_tol2_back96` carried the fence, samples, tol and lookback but NOT the
  interval - so an 8-minute grid and a 4-minute grid would have banked under the IDENTICAL key and
  been indistinguishable in the table. Joe's own rule: every knob that changes rows goes in the
  unique key. The string is now `..._back96_step48`, so the two grids could coexist; they do not,
  because he authorised the overwrite and `--overwrite` deleted the 8-minute rows.

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
def _arg(flag, default):
    """`--flag VALUE` from argv, else `default`. Added 1003 so the day and the tape are ARGUMENTS
    instead of constants - Joe asked for 10-02 and 10-03 rows, and editing two module constants per
    run is how a builder stops being reproducible."""
    return sys.argv[sys.argv.index(flag) + 1] if flag in sys.argv else default


# 1003: `--tape-end` defaults to the 09-08 window the banked 09-01 rows were built on, so a run with
# no flags behaves exactly as before. A later day needs a tape that COVERS it: the tape is a fixed
# span anchored on its END, so 10-03 data needs an end at or after 10-04.
BWL.TAPE_END = dt.datetime.strptime(_arg('--tape-end', '2026-09-08'), '%Y-%m-%d').replace(tzinfo=timezone.utc)
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
SAMPLES = 3; TOL = 2.0; BACK = 96        # 96 bars = 8 min, the banked lookback. Joe 1001 kept
#                                          it at 8 min when the grid went to 4 - the windows OVERLAP
STEP = 48                                # 48 bars = 4 min, Joe 1001: "4 minute spaced rows"
DAY = _arg('--day', '2026-09-01')     # 1003: an argument, not a constant
KNOBS = ('fence%g.%g_samples%d_tol%g_back%d_step%d'
         % (FENCE[0], FENCE[1], SAMPLES, TOL, BACK, STEP))

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
    TABLE, '\n    '.join('afg_ws%d VARCHAR(32) NULL,\n    afg_ws%d_bars INT NULL,' % (t, t)
                          for t in TFS))
COLS = (['afg_knobs', 'afg_day', 'afg_dr_src', 'afg_n', 'afg_dr', 'afg_at_utc', 'afg_at_ms']
        + [c for t in TFS for c in ('afg_ws%d' % t, 'afg_ws%d_bars' % t)])

db = DatabaseManager(**get_db_config()); db.connect()
if '--drop' in sys.argv:
    db.execute('DROP TABLE IF EXISTS %s' % TABLE); print('B|dropped %s' % TABLE)
db.execute(DDL)
if '--overwrite' in sys.argv:
    # DESTRUCTIVE, AND OFF BY DEFAULT. Joe 1001 authorised the overwrite for the 4-minute re-grid:
    # *"overwrite (authorised)"*. It is a FLAG and not the default because a committed builder that
    # silently wipes rows on every run is a different thing from one Joe pointed at a table once.
    # It deletes every row for this DAY regardless of knobs, which is what "overwrite the current
    # table" means - the 8-minute rows have to go, and they carry a different knobs string now.
    n = db.execute('SELECT COUNT(*) c FROM %s WHERE afg_day=%%s' % TABLE, (DAY,),
                   fetch=True)[0]['c']
    db.execute('DELETE FROM %s WHERE afg_day=%%s' % TABLE, (DAY,))
    print('B|--overwrite: deleted %d rows for day %s, ALL knobs strings' % (n, DAY))
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
print('B|lookback %d bars = %d min|windows %s by %d min'
      % (BACK, BACK * 5 // 60, 'TILE' if BACK == STEP else 'OVERLAP',
         abs(BACK - STEP) * 5 // 60))
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
                row.append(None); row.append(None); nul += 1
            else:
                row.append(hhmm(j))
                row.append(int(j - k))       # SIGNED bars from the anchor. See 5 below
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
    chk = db.execute('SELECT COUNT(*) n, COUNT(afg_ws4) v, COUNT(afg_ws4_bars) b FROM %s '
                     'WHERE afg_knobs=%%s AND afg_day=%%s' % TABLE, (KNOBS, DAY), fetch=True)[0]
    print('B|written-back check|rows %d|afg_ws4 non-null %d|afg_ws4_bars non-null %d|%s'
          % (chk['n'], chk['v'], chk['b'],
             'OK' if chk['v'] == chk['b'] == chk['n'] else 'MISMATCH - a column was not written'))
db.disconnect()
