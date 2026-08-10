"""build_tape_cross — bank every within-set line cross per tape bar. Joe 0803 01:15.

    Joe: "of the 425,554 LONG bars and 443,191 SHORT bars, which line crosses filtered out MAE >= 0.65"

rpl_scn_cross holds crosses for 461 signals and 2,213 matches only — never for the tape, so the question
needed a rebuild. This banks it once, alongside rpl_tape_momo, keyed on the same tm_ms.

WHAT A CROSS IS HERE — Joe 0803 00:05: raw sign change of (A - B), immediate, no wobble tolerance.
LOOKBACK 48 bars = 4 min at the 5 s grid, Joe's ruling.

THE 36 PAIRS — the 6 within-set pairs across the 6 rsd sets, in build_scn.CROSS order:
    sets  gcs5 5 s | gcs15 15 s | s30 30 s | s1 1 min | s2 2 min | s4 4 min
    pairs r|m  r|x  r|M  m|x  m|M  x|M
so pair k is CROSS[k-1] and its column is SUBSTRING(tc_dir, k, 1).

TWO 36-CHAR COLUMNS, one char per pair, so any pair is a SUBSTRING and any subset is a LIKE:
    tc_dir  '+' A is now ABOVE B after the most recent cross | '-' below | '0' no cross inside the lookback
    tc_age  '0' none | '1' <= 12 bars (60 s) | '2' <= 24 bars (120 s) | '3' <= 48 bars (240 s)

Mage is bb 37 | 0.7 | close, the rsd mult; r/m/x are the generic R.LN specs at each TF — identical to
build_scn.py so the two tables describe the same lines.

    python3 build_tape_cross.py
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
from build_scn import SETS, KINDS, NAMES, PAIRS, CROSS, TAPE0, cross_features

u = lambda m: dt.datetime.fromtimestamp(int(m) / 1000, dt.timezone.utc).strftime('%m-%d %H:%M:%S')
NB = 48                                   # 48 bars = 240 s = 4 min. Joe 0803.

DDL = '''CREATE TABLE IF NOT EXISTS rpl_tape_cross (
    tc_ms BIGINT PRIMARY KEY, tc_utc VARCHAR(20),
    tc_dir VARCHAR(36), tc_age VARCHAR(36),
    tc_n_cross TINYINT,                       -- how many of the 36 pairs crossed inside the lookback
    KEY (tc_n_cross)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4'''


def main(argv):
    ovr = {}
    for s, tf in SETS:
        for k in KINDS:
            nm = '%s_%s' % (s, k)
            ovr.update(bbline(nm, tf, length=37, mult=0.7, src='close') if k == 'M'
                       else R._mk(nm, tf, R.LN[k]))

    d = DatabaseManager(**get_db_config()); d.connect()
    end_ms = int(d.execute('SELECT MAX(kc_timestamp) m FROM kline_collection', fetch=True)[0]['m'])
    hours = int((end_ms - TAPE0) / 3600000) + 1
    t0 = time.time()
    with Jig(end_ms, hours=hours, warmup=J.WIN_WARMUP, overrides=ovr) as j:
        ts = np.asarray(j.ts, np.int64)
        V = np.vstack([np.asarray(j.W.line(nm), float) for nm in NAMES]).T
    n = len(ts)
    print('jig build %.1f s   bars %d   pairs %d' % (time.time() - t0, n, len(CROSS)), flush=True)

    DIRS, SINCE = cross_features(V, NB)
    print('crosses %.1f s' % (time.time() - t0), flush=True)

    # encode
    inw = SINCE <= NB
    ch = np.where(~inw, ord('0'), np.where(DIRS > 0, ord('+'), np.where(DIRS < 0, ord('-'), ord('0'))))
    age = np.where(~inw, ord('0'),
                   np.where(SINCE <= 12, ord('1'), np.where(SINCE <= 24, ord('2'), ord('3'))))
    DS = ch.astype(np.uint8).view('S1').reshape(n, len(CROSS))
    AS_ = age.astype(np.uint8).view('S1').reshape(n, len(CROSS))
    dirs = [b''.join(DS[i]).decode() for i in range(n)]
    ages = [b''.join(AS_[i]).decode() for i in range(n)]
    ncr = inw.sum(axis=1).astype(np.int16)
    print('encoded %.1f s   mean crosses in lookback %.2f' % (time.time() - t0, float(ncr.mean())), flush=True)

    d.execute(DDL)
    d.execute('DELETE FROM rpl_tape_cross')
    sql = ('INSERT INTO rpl_tape_cross (tc_ms,tc_utc,tc_dir,tc_age,tc_n_cross) VALUES (%s,%s,%s,%s,%s)')
    t1 = time.time(); CH = 20000
    for a in range(0, n, CH):
        b = min(a + CH, n)
        rows = [(int(ts[i]), u(ts[i]), dirs[i], ages[i], int(ncr[i])) for i in range(a, b)]
        d.executemany(sql, rows, chunk=5000)
        if (b // CH) % 15 == 0:
            print('  banked %d / %d   %.0f s' % (b, n, time.time() - t1), flush=True)
    got = d.execute('SELECT COUNT(*) n FROM rpl_tape_cross', fetch=True)[0]['n']
    print('rpl_tape_cross rows %d   total %.0f s' % (got, time.time() - t0), flush=True)
    print('pair order:')
    for k, c in enumerate(CROSS, 1):
        print('  %2d  %s' % (k, c))
    d.disconnect()


if __name__ == '__main__':
    main(sys.argv[1:])
