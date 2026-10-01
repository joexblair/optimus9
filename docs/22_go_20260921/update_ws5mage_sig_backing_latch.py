"""update_ws5mage_sig_backing_latch - add the ARM LATCH columns to ws5mage_sig_backing.

Joe 0930: *"if this was a walk, 02:40 would have been in the `arm` state and could apply the mech"*
/ *"assuming that an arm cancels when ws5Mage crosses 50, how many of the 17 would be included by
this mech?"* / *"update the affected rows in the db table"*.

WHY THIS EXISTS. The build columns (`wsb_oob_1585`, `wsb_oob_2575`) are a SNAPSHOT - is ws5Mage oob
AT the sig bar. That is the wrong test for an arm that latches. These columns hold the LATCH:

    set      ws5Mage oob on the dr side for `DW` consecutive bars
    cancel   ws5Mage crosses 50 - the sign of (ws5Mage - 50) changes, either direction
    live     set, and not cancelled before the sig bar

IN-PLACE UPDATE. The unique key (wsb_knobs, wsb_sig_ms) does not change, so this follows Joe's 0920
ruling on the wsf_leash momTF columns: *"the key isn't changing, so break the no-update rule"*.
Idempotent - re-running recomputes and overwrites the same values.

MINE, STATED
  1 all 68 rows are written, not only the ones with a latch. 0 means "no live latch", never NULL,
    so the column has one meaning everywhere.
  2 the dr of the arm is NOT required to match the dr of the signal. Measured: it makes no
    difference - 49 and 56 either way - because every live latch already carries the signal's dr.
  3 the back-walk floor is 2026-08-31 00:00, one day before the span. A latch older than that is
    not found. No signal in the table has a latch within 2,440 s, so the floor never binds.

    python3 docs/22_go_20260921/update_ws5mage_sig_backing_latch.py
"""
import sys, os, datetime as dt, logging
sys.path.insert(0, os.environ['CLAUDE_JOB_DIR'] + '/tmp'); sys.path.insert(0, '/home/joe/thecodes')
logging.disable(logging.CRITICAL)
import numpy as np, mechdev_rig
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

TABLE = 'ws5mage_sig_backing'
DW = 9                                   # Joe 0930: 45 s at the 5 s grid
MID = 50.0                               # Joe 0930: "an arm cancels when ws5Mage crosses 50"
MS = lambda y, m, d, h=0: int(dt.datetime(y, m, d, h, tzinfo=dt.timezone.utc).timestamp() * 1000)
rig = mechdev_rig.load(expect_end_ms=MS(2026, 9, 8))
Mg = np.asarray(rig.lines['ws5']['Mage'], float)
tsa = np.asarray(rig.ts, np.int64)
FLOOR = rig.bar('2026-08-31 00:00:00')
U = lambda k: dt.datetime.fromtimestamp(int(rig.ts[k]) / 1000, dt.timezone.utc)

NEW = [('wsb_latch1585', 'TINYINT'), ('wsb_latch1585_arm', 'DATETIME(3)'),
       ('wsb_latch1585_secs', 'INT'),
       ('wsb_latch2575', 'TINYINT'), ('wsb_latch2575_arm', 'DATETIME(3)'),
       ('wsb_latch2575_secs', 'INT')]

db = DatabaseManager(**get_db_config()); db.connect()
added = 0
for col, typ in NEW:
    try:
        db.execute('ALTER TABLE %s ADD COLUMN %s %s NULL' % (TABLE, col, typ)); added += 1
    except Exception as e:
        if 'Duplicate' not in str(e): raise
print('U|%s|columns added %d of %d (the rest already present)' % (TABLE, added, len(NEW)))


def latch(k, fen):
    """-> (arm_bar, secs_live) for the live latch at bar k, or None."""
    lo_, hi_ = fen
    j = k
    while j > FLOOR:
        if (Mg[j] - MID) * (Mg[j - 1] - MID) < 0: break      # a 50-cross cancels everything before
        j -= 1
    arm = None; run = 0
    for i in range(j, k + 1):
        d = int(rig.DR[i])
        o = (Mg[i] >= hi_) if d > 0 else (Mg[i] <= lo_)
        if o and (run == 0 or int(rig.DR[i - 1]) == d): run += 1
        else: run = 0
        if run >= DW:
            arm = i; break         # the FIRST bar the dwell completes - Joe 0930 caught the last-bar bug
    if arm is None: return None
    return arm, int((int(rig.ts[k]) - int(rig.ts[arm])) / 1000)


# SCOPED TO THE UN-WOBBED ROWS. Joe 0930 caught this running unscoped and overwriting the
# wob build's fence-specific latch (2 and 6 bars) with this script's shared DW=9.
NOWOB = "wsb_knobs NOT LIKE '%%wob%%' AND wsb_kind='signal'"
rows = db.execute('SELECT wsb_pk, wsb_sig_ms FROM %s WHERE %s ORDER BY wsb_sig_ms'
                  % (TABLE, NOWOB), fetch=True)
pay = []; n15 = n25 = 0
for r in rows:
    k = int(np.searchsorted(tsa, int(r['wsb_sig_ms'])))
    rec = []
    for fen in ((15.0, 85.0), (25.0, 75.0)):
        L = latch(k, fen)
        if L is None: rec += [0, None, None]
        else:
            a, s = L; rec += [1, U(a), s]
    n15 += rec[0]; n25 += rec[3]
    pay.append(tuple(rec + [r['wsb_pk']]))
db.executemany('UPDATE %s SET %s WHERE wsb_pk=%%s'
               % (TABLE, ', '.join('%s=%%s' % c for c, _ in NEW)), pay)
print('U|updated %d rows|live latch 15/85 %d|live latch 25/75 %d' % (len(pay), n15, n25))
q = ('SELECT SUM(wsb_oob_2575=0 AND wsb_latch2575=1) recovered, '
     'SUM(wsb_oob_1585=0 AND wsb_oob_2575=0 AND wsb_latch2575=1) of17_25, '
     'SUM(wsb_oob_1585=0 AND wsb_oob_2575=0 AND wsb_latch1585=1) of17_15, '
     'SUM(wsb_oob_1585=0 AND wsb_oob_2575=0 AND wsb_latch2575=0 AND wsb_latch1585=0) still_out '
     'FROM %s WHERE %s' % (TABLE, NOWOB))
x = db.execute(q, fetch=True)[0]
print('U|snapshot-miss but latch-live at 25/75: %s' % x['recovered'])
print('U|of the 17 unbacked: latch covers %s at 25/75, %s at 15/85, still uncovered %s'
      % (x['of17_25'], x['of17_15'], x['still_out']))
db.disconnect()
