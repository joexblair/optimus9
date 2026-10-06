"""WHY `neither` — the join table behind every OPEN · no rule row. Joe 1005: *"create a new table
that will join to the `neither`s, telling us the reason why r1 or r2 were not qualified"*.

THE TWO TESTS, read out of score39.mtd - this table reports nothing but their inputs:

  r1 QUALIFIES iff ALL FOUR of g5Mage, g15Mage, g30Mage, ws1Mage are finite AND oob ON THE dr SIDE
     (>= 85 at dr +1, <= 15 at dr -1). Each line is read at ITS OWN extremum inside its tolerance
     window around the mtd step-1 extrema bar: g5 0 bars, g15 3, g30 6, ws1 0 (score39.TOL).
       -> r1 failed because specific lines were NOT oob. One row per line says which, and by how far.

  r2 QUALIFIES iff NOT r1 AND the cascade faces dr:  net = ws1Mage - g15Mage, and
     towards = (net > 0) at dr +1, (net < 0) at dr -1.
       -> r2 failed because the net was AWAY. One signed number, repeated on each of the four rows.

  `neither` = NOT r1 AND NOT towards. Both reasons are therefore present on every row.

GRAIN: ONE ROW PER (signal x mtd line) - FOUR rows per `neither` signal. Joe's report rule, 0815:
*"ONE record per row ... never split a series into side-by-side column groups"*. g5/g15/g30/ws1 are
a series, so they go down the page, not across it. The signal-level r2 facts repeat on all four rows
so a single join answers both questions without a second table.

JOIN: (nw_knob_key, nw_day, nw_bar_ms) -> octosig_rulings (os_knob_key, os_day, os_bar_ms).

PRODUCERS: score39.mtd only. `vbar` was added to its return 1005 for the extremum-bar column; the
report's output was re-verified byte-identical after the change. Nothing is re-implemented here.
"""
import os as _os, sys, io, contextlib, datetime as dt
import numpy as np
_HERE = _os.path.dirname(_os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, '/home/joe/thecodes')
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    with contextlib.redirect_stderr(io.StringIO()):
        import score39 as SC
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

SRC = _os.environ.get('LG_SRC', 'octosig_rulings')
TABLE = _os.environ.get('LG_TABLE', 'octosig_neither_why')
Q = lambda s: s.replace('__TBL__', TABLE)
LINES = ('g5', 'g15', 'g30', 'ws1')
ts = np.asarray(SC.ts, np.int64)
U = lambda i: dt.datetime.fromtimestamp(int(ts[int(i)]) / 1000, dt.timezone.utc).strftime('%H:%M:%S')

db = DatabaseManager(**get_db_config()); db.connect()
db.execute(Q('''CREATE TABLE IF NOT EXISTS __TBL__ (
    nw_pk          BIGINT AUTO_INCREMENT PRIMARY KEY,
    nw_knob_key    VARCHAR(190) NOT NULL,      -- joins octosig_rulings.os_knob_key
    nw_day         DATE         NOT NULL,
    nw_ts          VARCHAR(8)   NOT NULL,
    nw_bar_ms      BIGINT       NOT NULL,      -- joins octosig_rulings.os_bar_ms
    nw_dr          TINYINT      NOT NULL,
    nw_line        VARCHAR(8)   NOT NULL,      -- g5 | g15 | g30 | ws1  (the mtd Mage line)
    nw_tol_bars    TINYINT      NOT NULL,      -- its tolerance window, score39.TOL: 0 / 3 / 6 / 0
    nw_value       DECIMAL(12,4) NULL,         -- the line at ITS extremum inside the window
    nw_extrema_ts  VARCHAR(8)   NOT NULL,      -- the bar that value came from
    nw_fence       DECIMAL(6,2) NOT NULL,      -- 85 at dr +1, 15 at dr -1
    nw_dist_fence  DECIMAL(12,4) NULL,         -- signed: + = oob by this much, - = SHORT by this much
    nw_is_oob      TINYINT      NOT NULL,      -- 1 = this line satisfied r1's test
    nw_blocks_r1   TINYINT      NOT NULL,      -- 1 = this line is a reason r1 failed
    nw_noob        TINYINT      NOT NULL,      -- how many of the 4 were oob (signal level)
    nw_miss        VARCHAR(32)  NOT NULL,      -- the lines that were not oob (signal level)
    nw_r1_reason   VARCHAR(96)  NOT NULL,      -- why r1 did not qualify
    nw_r2_net      DECIMAL(12,4) NULL,         -- ws1Mage - g15Mage at the extrema
    nw_r2_needed   VARCHAR(16)  NOT NULL,      -- 'net > 0' at dr +1, 'net < 0' at dr -1
    nw_r2_towards  TINYINT      NOT NULL,      -- 0 on every row here, by definition of `neither`
    nw_r2_reason   VARCHAR(96)  NOT NULL,      -- why r2 did not qualify
    nw_src         VARCHAR(10)  NOT NULL,      -- lookback | fwd - how step 1 found the extrema
    nw_extrema_bar VARCHAR(8)   NOT NULL,      -- the mtd step-1 extrema bar itself
    nw_lag_min     DECIMAL(10,2) NOT NULL,     -- extrema bar minus the signal bar, minutes
    UNIQUE KEY uq_nw (nw_knob_key, nw_day, nw_bar_ms, nw_line),
    INDEX (nw_day), INDEX (nw_line), INDEX (nw_is_oob))'''))

rows = db.execute("""SELECT os_knob_key k, os_day d, os_ts t, os_bar_ms ms, os_dr dr
    FROM %s WHERE os_route='neither' ORDER BY os_day, os_bar_ms""" % SRC, fetch=True)
print('# %s: %d `neither` signals -> %d rows at 4 lines each' % (SRC, len(rows), len(rows) * 4))

ins = []
for r in rows:
    k = int(np.searchsorted(ts, int(r['ms'])))
    m = SC.mtd(k)
    if m['route'] != 'neither':
        print('# MISMATCH %s %s: octosig_rulings says neither, mtd says %s' % (r['d'], r['t'], m['route']))
        continue
    d = int(m['d']); fence = SC.HI if d > 0 else SC.LO
    miss = ','.join(m['miss'])
    r1_reason = '%s not oob at %s %.0f (%d of 4 oob)' % (miss, 'hi' if d > 0 else 'lo', fence, m['noob'])
    need = 'net > 0' if d > 0 else 'net < 0'
    r2_reason = 'cascade net %+.2f is AWAY from dr, needed %s' % (m['net'], need)
    for n in LINES:
        v = m['v'][n]
        fin = bool(np.isfinite(v))
        oob = fin and ((v >= SC.HI) if d > 0 else (v <= SC.LO))
        dist = (float(v) - SC.HI) if (fin and d > 0) else ((SC.LO - float(v)) if fin else None)
        ins.append((r['k'], r['d'], r['t'], int(r['ms']), d, n, SC.TOL[n],
                    (round(float(v), 4) if fin else None), U(m['vbar'][n]), fence,
                    (round(dist, 4) if dist is not None else None),
                    1 if oob else 0, 0 if oob else 1, m['noob'], miss, r1_reason,
                    round(float(m['net']), 4), need, 1 if m['towards'] else 0, r2_reason,
                    m['src'], U(m['ex']), round(float(m['lag']), 2)))

COLS = ('nw_knob_key,nw_day,nw_ts,nw_bar_ms,nw_dr,nw_line,nw_tol_bars,nw_value,nw_extrema_ts,'
        'nw_fence,nw_dist_fence,nw_is_oob,nw_blocks_r1,nw_noob,nw_miss,nw_r1_reason,nw_r2_net,'
        'nw_r2_needed,nw_r2_towards,nw_r2_reason,nw_src,nw_extrema_bar,nw_lag_min')
NCOL = len(COLS.split(','))
assert not ins or len(ins[0]) == NCOL, 'tuple %d vs %d columns' % (len(ins[0]), NCOL)
db.execute(Q('DELETE FROM __TBL__ WHERE nw_knob_key=%s'), (rows[0]['k'],))
db.executemany(Q('INSERT INTO __TBL__ (%s) VALUES (%s)' % (COLS, ','.join(['%s'] * NCOL))), ins)
print('# INSERTED %d rows into %s' % (len(ins), TABLE))
db.disconnect()
