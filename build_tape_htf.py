"""build_tape_htf — bank the HTF Mages per tape bar. Joe 0803 02:40.

    Joe 0802, his last tip in the handover: "if your predictions don't pan out, start by looking at the
    HTFs (>22) - you might find something bigger cutting an opposing path"

THE GAP THIS CLOSES. Every dimension measured tonight lives at s4 or below — band position, momo state,
line crosses, arm side. Nothing above s22 has been in any table, so the one thing Joe's note points at
when predictions fail has never been tested.

THE LINES — build_rpl_jig.HTF_MAGE, bb 37 | 0.7 | close at TF 30 / 45 / 60 / 90 min. Same Mage spec as
every other Mage in the stack. NOT TF120: bb length 37 at a 2 h bar needs 74 h and the rolling window is
72 h, so it would bank NaN dressed as data (build_rpl_jig.py:105-107).

WHAT IS BANKED, per bar
    th_h30 .. th_h90   raw values, so any banding threshold can be applied later as a query
    th_band            4 chars, one per HTF, the same 5-band encoding used everywhere else:
                       0 lo-oob <=15 | 1 (15,30] | 2 (30,60] | 3 (60,85) | 4 hi-oob >=85
    th_stack           'A' strictly ascending h30<h45<h60<h90 | 'D' strictly descending | 'M' mixed
                       — whether the HTF ladder is ordered, which is what "something bigger cutting an
                       opposing path" would look like as a state
    th_oob_n           how many of the 4 are OOB (band 0 or 4)
    th_slope           sign of h30 minus its value 60 bars = 5 min earlier: '+' rising, '-' falling, '0' flat
                       (the fastest HTF is the one that moves inside a trade's lifetime)

    python3 build_tape_htf.py
"""
import os, sys, time, datetime as dt
os.environ.setdefault('RPL_TF_CEILING', '4')
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_rpl_jig as J
import optimus9.orchestration.rpl_walk as R
from optimus9.analysis.jig import Jig, bbline
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
from build_scn import TAPE0

u = lambda m: dt.datetime.fromtimestamp(int(m) / 1000, dt.timezone.utc).strftime('%m-%d %H:%M:%S')
HTF = [('jH30', 30.0), ('jH45', 45.0), ('jH60', 60.0), ('jH90', 90.0)]
SLOPE_BARS = 60                                   # 60 bars = 5 min at the 5 s grid
LOMID, HIMID = 30.0, 60.0

DDL = '''CREATE TABLE IF NOT EXISTS rpl_tape_htf (
    th_ms BIGINT PRIMARY KEY, th_utc VARCHAR(20),
    th_h30 DOUBLE, th_h45 DOUBLE, th_h60 DOUBLE, th_h90 DOUBLE,
    th_band VARCHAR(4), th_stack VARCHAR(1), th_oob_n TINYINT, th_slope VARCHAR(1),
    KEY (th_band), KEY (th_stack), KEY (th_oob_n), KEY (th_slope)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4'''


def main(argv):
    HI, LO = R.HI, R.LO
    ovr = {}
    for nm, tf in HTF:
        ovr.update(bbline(nm, tf, length=37, mult=0.7, src='close'))

    d = DatabaseManager(**get_db_config()); d.connect()
    end_ms = int(d.execute('SELECT MAX(kc_timestamp) m FROM kline_collection', fetch=True)[0]['m'])
    hours = int((end_ms - TAPE0) / 3600000) + 1
    t0 = time.time()
    with Jig(end_ms, hours=hours, warmup=J.WIN_WARMUP, overrides=ovr) as j:
        ts = np.asarray(j.ts, np.int64)
        V = np.vstack([np.asarray(j.W.line(nm), float) for nm, _ in HTF]).T      # (n,4)
    n = len(ts)
    print('jig build %.1f s   bars %d   HTF lines %d' % (time.time() - t0, n, len(HTF)), flush=True)

    B = np.full(V.shape, -1, np.int8)
    f = np.isfinite(V)
    B[f & (V <= LO)] = 0
    B[f & (V > LO) & (V <= LOMID)] = 1
    B[f & (V > LOMID) & (V <= HIMID)] = 2
    B[f & (V > HIMID) & (V < HI)] = 3
    B[f & (V >= HI)] = 4
    band = np.array([''.join(str(x) if x >= 0 else '-' for x in r) for r in B])
    asc = (V[:, 0] < V[:, 1]) & (V[:, 1] < V[:, 2]) & (V[:, 2] < V[:, 3])
    des = (V[:, 0] > V[:, 1]) & (V[:, 1] > V[:, 2]) & (V[:, 2] > V[:, 3])
    stack = np.where(asc, 'A', np.where(des, 'D', 'M'))
    oobn = ((B == 0) | (B == 4)).sum(axis=1).astype(np.int8)
    h30 = V[:, 0]
    prev = np.r_[np.full(SLOPE_BARS, np.nan), h30[:-SLOPE_BARS]]
    dsl = h30 - prev
    slope = np.where(~np.isfinite(dsl), '0', np.where(dsl > 0.5, '+', np.where(dsl < -0.5, '-', '0')))
    print('stack A %d  D %d  M %d   |  oob_n mean %.2f   |  slope + %d  - %d  0 %d'
          % (int(asc.sum()), int(des.sum()), int((~asc & ~des).sum()), float(oobn.mean()),
             int((slope == '+').sum()), int((slope == '-').sum()), int((slope == '0').sum())), flush=True)

    d.execute(DDL)
    d.execute('DELETE FROM rpl_tape_htf')
    sql = ('INSERT INTO rpl_tape_htf (th_ms,th_utc,th_h30,th_h45,th_h60,th_h90,th_band,th_stack,'
           'th_oob_n,th_slope) VALUES (' + ','.join(['%s'] * 10) + ')')
    nz = lambda v: (None if not np.isfinite(v) else float(v))
    t1 = time.time(); CH = 20000
    for a in range(0, n, CH):
        b = min(a + CH, n)
        rows = [(int(ts[i]), u(ts[i]), nz(V[i, 0]), nz(V[i, 1]), nz(V[i, 2]), nz(V[i, 3]),
                 band[i], str(stack[i]), int(oobn[i]), str(slope[i])) for i in range(a, b)]
        d.executemany(sql, rows, chunk=5000)
        if (b // CH) % 15 == 0:
            print('  banked %d / %d   %.0f s' % (b, n, time.time() - t1), flush=True)
    got = d.execute('SELECT COUNT(*) n FROM rpl_tape_htf', fetch=True)[0]['n']
    print('rpl_tape_htf rows %d   total %.0f s' % (got, time.time() - t0), flush=True)
    d.disconnect()


if __name__ == '__main__':
    main(sys.argv[1:])
