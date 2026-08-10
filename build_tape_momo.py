"""build_tape_momo — bank the momo state of every tape bar so subset cuts are QUERIES. Joe 0803 00:40.

    Joe: "for high level matching, we should only hunt for matching momo in s4, s15, s22. what does that
    give you? your data for this should already be in db tables, so that analysis is optimised"

IT WAS NOT IN A TABLE. rpl_scn_momo held momo state for 461+463 signals and 2,213 nearest-neighbour
matches — never for the 1,365,840 tape bars. So every new subset cut has been costing a 4-minute rebuild.
This banks the tape once; after it, any subset is a SUBSTRING comparison.

THE VECTOR ORDER IS THE POINT. MOMO_LINES puts the rule-3 trio FIRST:
    position 1 = s4r      2 = s15r     3 = s22r        <- exhv2's R_SPEC, the decision lines
    position 4 = gcs5_r   5 = gcs15_r  6 = s30_r  7 = s1_r  8 = s2_r  9 = s4_r   <- the rsd r set
so Joe's high-level cut is LEFT(tm_vec_up, 3), and the full 9-line cut is the whole column.

STATE ENCODING, one char per line: 0 none | 1 sideways | 2 curl | 3 momo. Both directions banked on the
same row because they are two readings of one bar, not two bars.

FORWARD OUTCOME, banked per direction, no horizon and no cap: bars to a 1.3% move, the MAE incurred
reaching it, and the clean flag (reached AND mae <= 0.65). A bar that never reaches its target has NULL
bars and NULL mae, recorded as never rather than truncated.

ARMED, so the pool is queryable: tm_armed = s1Mage or s2Mage is OOB at this bar; tm_arm_side carries
which boundary. Everything measured tonight showed the right comparison pool is armed bars, not all bars.

    python3 build_tape_momo.py
"""
import os, sys, time, datetime as dt
os.environ.setdefault('RPL_TF_CEILING', '4')
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_rpl_jig as J
import optimus9.orchestration.rpl_walk as R
from optimus9.analysis.jig import Jig
from optimus9.compute.indicator_computer import IndicatorComputer as IC
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
from vmomo import vmomo
from build_scn import SETS, MOMO_LINES, TAPE0, forward_leg

u = lambda m: dt.datetime.fromtimestamp(int(m) / 1000, dt.timezone.utc).strftime('%m-%d %H:%M:%S')
TARGET, MAEMAX = 1.3, 0.65

DDL = '''CREATE TABLE IF NOT EXISTS rpl_tape_momo (
    tm_ms BIGINT PRIMARY KEY, tm_utc VARCHAR(20), tm_px DOUBLE,
    tm_armed TINYINT, tm_arm_side VARCHAR(2),
    tm_vec_up VARCHAR(9), tm_vec_dn VARCHAR(9),
    tm_bars_up INT, tm_mae_up DOUBLE, tm_clean_up TINYINT,
    tm_bars_dn INT, tm_mae_dn DOUBLE, tm_clean_dn TINYINT,
    KEY (tm_armed), KEY (tm_vec_up), KEY (tm_vec_dn),
    KEY (tm_clean_up), KEY (tm_clean_dn)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4'''


def main(argv):
    HI, LO = R.HI, R.LO
    ovr = {}
    for s, tf in SETS:
        ovr.update(R._mk('%s_r' % s, tf, R.LN['r']))
    ovr.update(J.LINES)

    d = DatabaseManager(**get_db_config()); d.connect()
    end_ms = int(d.execute('SELECT MAX(kc_timestamp) m FROM kline_collection', fetch=True)[0]['m'])
    hours = int((end_ms - TAPE0) / 3600000) + 1
    t0 = time.time()
    with Jig(end_ms, hours=hours, warmup=J.WIN_WARMUP, overrides=ovr) as j:
        ts = np.asarray(j.ts, np.int64)
        base = j.W.base
        evt = base['volume'].to_numpy(dtype=float) > 0
        src = IC.build_source(base, R.PXS_CFG['src'])
        ei = np.flatnonzero(evt)
        px = np.full(len(src), np.nan); px[ei] = IC.dema(src[ei], int(R.PXS_CFG['len']))
        fin = np.isfinite(px)
        ix = np.where(fin, np.arange(len(px)), 0); np.maximum.accumulate(ix, out=ix)
        px = px[ix]; px[:int(np.argmax(fin))] = px[int(np.argmax(fin))]
        RLALL = {v: np.asarray(j.W.line(v), float) for _, v in MOMO_LINES}
        G1 = np.asarray(j.W.line('jMg1'), float); G2 = np.asarray(j.W.line('jMg2'), float)
    n = len(ts)
    print('jig build %.1f s   bars %d' % (time.time() - t0, n), flush=True)

    SV = {dr: np.vstack([vmomo(RLALL[s_], dr)[0] for _, s_ in MOMO_LINES]).T for dr in (1, -1)}
    HITL, MAEL = forward_leg(px, 1, TARGET)
    HITS, MAES = forward_leg(px, -1, TARGET)
    print('momo + forward legs  %.1f s' % (time.time() - t0), flush=True)

    o1 = (G1 >= HI) | (G1 <= LO)
    o2 = (G2 >= HI) | (G2 <= LO)
    armed = o1 | o2
    side = np.where(o1, np.where(G1 >= HI, 'hi', 'lo'),
                    np.where(o2, np.where(G2 >= HI, 'hi', 'lo'), ''))
    VU = np.array([''.join(map(str, r)) for r in SV[1]])
    VD = np.array([''.join(map(str, r)) for r in SV[-1]])
    cu = (HITL >= 0) & (MAEL <= MAEMAX)
    cd = (HITS >= 0) & (MAES <= MAEMAX)
    print('armed bars %d / %d   clean-up %d   clean-dn %d'
          % (int(armed.sum()), n, int(cu.sum()), int(cd.sum())), flush=True)

    d.execute(DDL)
    d.execute('DELETE FROM rpl_tape_momo')
    sql = ('INSERT INTO rpl_tape_momo (tm_ms,tm_utc,tm_px,tm_armed,tm_arm_side,tm_vec_up,tm_vec_dn,'
           'tm_bars_up,tm_mae_up,tm_clean_up,tm_bars_dn,tm_mae_dn,tm_clean_dn) VALUES ('
           + ','.join(['%s'] * 13) + ')')
    nz = lambda v: (None if not np.isfinite(v) else float(v))
    t1 = time.time(); CH = 20000
    for a in range(0, n, CH):
        b = min(a + CH, n)
        rows = [(int(ts[i]), u(ts[i]), nz(px[i]), int(armed[i]), (side[i] or None), VU[i], VD[i],
                 (int(HITL[i] - i) if HITL[i] >= 0 else None), nz(MAEL[i]), int(cu[i]),
                 (int(HITS[i] - i) if HITS[i] >= 0 else None), nz(MAES[i]), int(cd[i]))
                for i in range(a, b)]
        d.executemany(sql, rows, chunk=5000)
        if (b // CH) % 10 == 0:
            print('  banked %d / %d   %.0f s' % (b, n, time.time() - t1), flush=True)
    got = d.execute('SELECT COUNT(*) n FROM rpl_tape_momo', fetch=True)[0]['n']
    print('rpl_tape_momo rows %d   total %.0f s' % (got, time.time() - t0), flush=True)
    d.disconnect()


if __name__ == '__main__':
    main(sys.argv[1:])
