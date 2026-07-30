"""build_cadence_markers — the s8 cadence markers table (Joe 0724). SAVED (survives compaction).

Cadence = xm_cross(base='s8', wob=6): s8x×s8m with the trade cross's refining stack MINUS the align gate —
  wob=6 debounce → side-specific sustained-OOB dwell (min_dwell=180s) → opposite-side guard.  NO align[s8m,hs30m].
Each marker also records what it samples for the weakness read: s8x/s8m at the mark, and hs60x/hs60m + |x-50|/|m-50|/gap.
Window = the trade-report slice (06-25 12:00 .. 06-27 00:00) so the markers line up with trade_report_hs60.tr_lastcad.
"""
import sys, time
import numpy as np
from datetime import datetime, timezone
import linelab as LL
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

WRITE = '--write' in sys.argv
S = int(datetime(2026, 6, 25, 12, 0, tzinfo=timezone.utc).timestamp() * 1000)
E = int(datetime(2026, 6, 27,  0, 0, tzinfo=timezone.utc).timestamp() * 1000)
FMT = lambda ms: time.strftime('%m-%d %H:%M:%S', time.gmtime(ms / 1000))

DDL = """CREATE TABLE IF NOT EXISTS cadence_markers (
  cm_id INT AUTO_INCREMENT PRIMARY KEY,
  cm_ts BIGINT, cm_time VARCHAR(20), cm_dir VARCHAR(6),
  cm_s8x DOUBLE, cm_s8m DOUBLE,
  cm_hs60x DOUBLE, cm_hs60m DOUBLE, cm_dx DOUBLE, cm_dm DOUBLE, cm_gap DOUBLE
)"""


def build():
    cache, ets, epx, names = LL.warm()
    ts = cache.ts
    cad = LL.xm_cross(cache, 's8', wob=6, lookback_tf=3, min_dwell_s=180, align_line=None, start=S, end=E)
    s8x, s8m = LL.line(cache, 's8x'), LL.line(cache, 's8m')
    hx, hm = LL.line(cache, 'hs60x'), LL.line(cache, 'hs60m')
    rows = []
    for tms, bd in cad:
        ci = int(np.searchsorted(ts, tms))
        x, m = float(hx[ci]), float(hm[ci]); dx, dm = abs(x - 50), abs(m - 50)
        rows.append(dict(cm_ts=tms, cm_time=FMT(tms), cm_dir=('long' if bd == 1 else 'short'),
                         cm_s8x=round(float(s8x[ci]), 2), cm_s8m=round(float(s8m[ci]), 2),
                         cm_hs60x=round(x, 2), cm_hs60m=round(m, 2),
                         cm_dx=round(dx, 2), cm_dm=round(dm, 2), cm_gap=round(dx - dm, 2)))
    return rows


def write_db(rows):
    d = DatabaseManager(**get_db_config()); d.connect()
    d.execute(DDL)
    d.execute('DELETE FROM cadence_markers')
    cols = ['cm_ts', 'cm_time', 'cm_dir', 'cm_s8x', 'cm_s8m', 'cm_hs60x', 'cm_hs60m', 'cm_dx', 'cm_dm', 'cm_gap']
    ph = ','.join(['%s'] * len(cols))
    for r in rows:
        d.execute('INSERT INTO cadence_markers (%s) VALUES (%s)' % (','.join(cols), ph), tuple(r[c] for c in cols))
    d.disconnect()
    nl = sum(1 for r in rows if r['cm_dir'] == 'long')
    print('WROTE %d cadence markers (long %d / short %d) -> cadence_markers' % (len(rows), nl, len(rows) - nl))


if __name__ == '__main__':
    rows = build()
    print('=== s8 cadence markers over %s .. %s: %d ===' % (FMT(S), FMT(E), len(rows)))
    if WRITE:
        write_db(rows)
