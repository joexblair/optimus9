"""build_tape_crossw — within-set line crosses per tape bar, detector parameterised by wob. Joe 0803 01:30.

    Joe: "I'd be interested in the same dataset built with wob_cross 8"

ONE TABLE, ONE CONCERN, MANY DETECTORS. rpl_tape_crossw is keyed (tw_ms, tw_wob) so every wobble setting
lives side by side and is directly comparable. --wob 0 is the RAW SIGN CHANGE variant (Joe 0803 00:05);
--wob 8 is _Causal.cross_wob at n=8; the jig's own anchor/confirm run at R.WOBN = 9.

WHAT cross_wob DOES (optimus9/analysis/jig.py:253-264). A cross is CONFIRMED once the line has held the
crossed side for n consecutive 5 s bars; a single bar back across RESETS the run. It demands a clean
cross, it is not bump tolerance. The function returns confirmed-in-effect per bar; the cross moment is
the RISING EDGE of that.

THE LAG IS REAL AND IS NOT A CAP. At wob 8 the confirmation lands 8 bars = 40 s AFTER the sign flip, so a
48-bar = 4 min lookback over confirmations reaches sign flips up to 4 min 40 s old. --wob 0 has no lag.
Both are banked so the lag is measurable rather than assumed.

THE 36 PAIRS — build_scn.CROSS order, 6 within-set pairs across 6 rsd sets:
    gcs5 5 s | gcs15 15 s | s30 30 s | s1 1 min | s2 2 min | s4 4 min
    r|m  r|x  r|M  m|x  m|M  x|M
pair k is CROSS[k-1]; its column is SUBSTRING(tw_dir, k, 1).

    tw_dir  '+' the most recent confirmed cross was A crossing ABOVE B | '-' below | '0' none in the lookback
    tw_age  '0' none | '1' <= 12 bars (60 s) | '2' <= 24 (120 s) | '3' <= 48 (240 s)

    python3 build_tape_crossw.py --wob 8
    python3 build_tape_crossw.py --wob 0        # raw sign change, for comparison
"""
import os, sys, time, datetime as dt
os.environ.setdefault('RPL_TF_CEILING', '4')
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_rpl_jig as J
import optimus9.orchestration.rpl_walk as R
from optimus9.analysis.jig import Jig, bbline, _Causal
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
from build_scn import SETS, KINDS, NAMES, PAIRS, CROSS, TAPE0

u = lambda m: dt.datetime.fromtimestamp(int(m) / 1000, dt.timezone.utc).strftime('%m-%d %H:%M:%S')
NB = 48                                   # 48 bars = 240 s = 4 min lookback. Joe 0803.

DDL = '''CREATE TABLE IF NOT EXISTS rpl_tape_crossw (
    tw_ms BIGINT, tw_wob TINYINT, tw_utc VARCHAR(20),
    tw_dir VARCHAR(36), tw_age VARCHAR(36), tw_n_cross TINYINT,
    PRIMARY KEY (tw_ms, tw_wob),
    KEY (tw_wob), KEY (tw_wob, tw_n_cross)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4'''


def features(V, wob, nb):
    """(DIRS, SINCE) per bar per pair. wob 0 = raw sign change of (A-B). wob n = rising edge of
    _Causal.cross_wob at n, which confirms after n consecutive bars on the crossed side."""
    n = V.shape[0]
    cau = _Causal(None)
    DIRS = np.zeros((n, len(CROSS)), np.int8)
    SINCE = np.full((n, len(CROSS)), nb + 1, np.int32)
    idx = np.arange(n)
    ci = 0
    for si, (s, _) in enumerate(SETS):
        base = si * 4
        for a, b in PAIRS:
            ia, ib = base + KINDS.index(a), base + KINDS.index(b)
            dd = V[:, ia] - V[:, ib]
            if wob <= 0:
                sg = np.sign(np.nan_to_num(dd, nan=0.0)).astype(np.int8)
                ev = np.r_[False, (sg[1:] != sg[:-1]) & (sg[1:] != 0) & (sg[:-1] != 0)]
                evd = np.where(ev, sg, 0).astype(np.int8)
            else:
                up = cau.cross_wob(dd, 0.0, 1, wob)
                dn = cau.cross_wob(dd, 0.0, -1, wob)
                eu = up & ~np.r_[False, up[:-1]]
                ed = dn & ~np.r_[False, dn[:-1]]
                ev = eu | ed
                evd = np.where(eu, 1, np.where(ed, -1, 0)).astype(np.int8)
            last = np.maximum.accumulate(np.where(ev, idx, -1))
            has = last >= 0
            SINCE[has, ci] = (idx - last)[has]
            DIRS[has, ci] = evd[last[has]]
            ci += 1
    SINCE[SINCE > nb] = nb + 1
    return DIRS, SINCE


def main(argv):
    wob = int(argv[argv.index('--wob') + 1]) if '--wob' in argv else 8
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
    print('jig build %.1f s   bars %d   pairs %d   WOB %d (%s)'
          % (time.time() - t0, n, len(CROSS), wob,
             'raw sign change, no lag' if wob <= 0 else 'confirms %d bars = %d s after the flip'
             % (wob, wob * 5)), flush=True)

    DIRS, SINCE = features(V, wob, NB)
    inw = SINCE <= NB
    print('crosses %.1f s   mean pairs crossed in the 4 min lookback %.2f'
          % (time.time() - t0, float(inw.sum(axis=1).mean())), flush=True)

    ch = np.where(~inw, ord('0'), np.where(DIRS > 0, ord('+'), np.where(DIRS < 0, ord('-'), ord('0'))))
    age = np.where(~inw, ord('0'),
                   np.where(SINCE <= 12, ord('1'), np.where(SINCE <= 24, ord('2'), ord('3'))))
    DS = ch.astype(np.uint8).view('S1').reshape(n, len(CROSS))
    AS_ = age.astype(np.uint8).view('S1').reshape(n, len(CROSS))
    dirs = [b''.join(DS[i]).decode() for i in range(n)]
    ages = [b''.join(AS_[i]).decode() for i in range(n)]
    ncr = inw.sum(axis=1).astype(np.int16)

    d.execute(DDL)
    d.execute('DELETE FROM rpl_tape_crossw WHERE tw_wob=%s', (wob,))
    sql = 'INSERT INTO rpl_tape_crossw (tw_ms,tw_wob,tw_utc,tw_dir,tw_age,tw_n_cross) VALUES (%s,%s,%s,%s,%s,%s)'
    t1 = time.time(); CH = 20000
    for a in range(0, n, CH):
        b = min(a + CH, n)
        rows = [(int(ts[i]), wob, u(ts[i]), dirs[i], ages[i], int(ncr[i])) for i in range(a, b)]
        d.executemany(sql, rows, chunk=5000)
        if (b // CH) % 15 == 0:
            print('  banked %d / %d   %.0f s' % (b, n, time.time() - t1), flush=True)
    got = d.execute('SELECT COUNT(*) n FROM rpl_tape_crossw WHERE tw_wob=%s', (wob,), fetch=True)[0]['n']
    print('rpl_tape_crossw wob=%d rows %d   total %.0f s' % (wob, got, time.time() - t0), flush=True)
    d.disconnect()


if __name__ == '__main__':
    main(sys.argv[1:])
