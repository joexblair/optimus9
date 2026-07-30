"""rc_split_probe — dissect the cyc1-r3 RC OOS·10d(-0.341) vs OOS·32(+0.193) split (Joe 0724). SAVED.

Loads the snapshotted RC cyc1-r3 elite (rc_cyc1r3_split_config.json) and scores it PER WINDOW across:
  - OOS_BLOCK (10 clean disjoint windows, all recent/July tape)
  - PANEL     (32 tape-spanning windows, mostly IS-era / May-June)
so the recent-regime windows that drag RC negative are visible against the older windows where it holds.
Reproduces the aggregate OOS·10d / OOS·32 nets ( _net = med(RC_MFE) - med(RC_MAE) ) to confirm the -0.341 / +0.193.
Writes table rc_split_probe (per-window). Run BETWEEN sweep rounds (one L0 build; watch RAM).
"""
import json, time
import numpy as np
import optimus9.orchestration.rpl_evo_sweep as e
import optimus9.orchestration.rpl_walk as R
from optimus9.orchestration.rpl_evo_sweep import _enter, _leg_net, OOS_BLOCK, PANEL
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

CFG = json.load(open('/home/joe/thecodes/rc_cyc1r3_split_config.json'))['config']
D = lambda s: time.strftime('%m-%d', time.gmtime(s / 1000))


def per_window(windows, ets, epx):
    """-> list of (date, ts, n_rc_legs, med_mfe, med_mae, net) + the aggregate net over ALL legs (the _net basis)."""
    out = []; all_mfe = []; all_mae = []
    for s, en in windows:
        legs = _leg_net(R.run_chain('bear', s, persist=False, end=en), ets, epx)
        rc = [(m, a) for m, a, isrc in legs if isrc]
        mfe = [m for m, a in rc]; mae = [a for m, a in rc]
        all_mfe += mfe; all_mae += mae
        net = (float(np.median(mfe)) - float(np.median(mae))) if rc else None
        out.append((D(s), s, len(rc), (float(np.median(mfe)) if rc else None),
                    (float(np.median(mae)) if rc else None), net))
    agg = (float(np.median(all_mfe)) - float(np.median(all_mae))) if all_mfe else None
    return out, agg


def main():
    restore, ets, epx = _enter(CFG)
    try:
        oos, oos_agg = per_window(OOS_BLOCK, ets, epx)
        pan, pan_agg = per_window(PANEL, ets, epx)
    finally:
        restore()
    print('AGG OOS10d net = %+.3f (expect ~-0.341) | OOS32 net = %+.3f (expect ~+0.193)' % (oos_agg, pan_agg))
    d = DatabaseManager(**get_db_config()); d.connect()
    d.execute("""CREATE TABLE IF NOT EXISTS rc_split_probe (
        rsp_id INT AUTO_INCREMENT PRIMARY KEY, rsp_set VARCHAR(8), rsp_date VARCHAR(8), rsp_ts BIGINT,
        rsp_n_rc INT, rsp_mfe DOUBLE, rsp_mae DOUBLE, rsp_net DOUBLE)""")
    d.execute('DELETE FROM rc_split_probe')
    for tag, rows in (('oos10', oos), ('panel32', pan)):
        for dt, ts, n, mfe, mae, net in rows:
            d.execute('INSERT INTO rc_split_probe (rsp_set,rsp_date,rsp_ts,rsp_n_rc,rsp_mfe,rsp_mae,rsp_net) VALUES (%s,%s,%s,%s,%s,%s,%s)',
                      (tag, dt, ts, n, mfe, mae, net))
    d.disconnect()
    # console: the recent-regime drag, ranked
    print('\nOOS10d (recent/July) per-window RC net, worst first:')
    for dt, ts, n, mfe, mae, net in sorted([r for r in oos if r[5] is not None], key=lambda r: r[5]):
        print('  %s  net %+.3f  (mfe %+.3f mae %+.3f, %d rc legs)' % (dt, net, mfe, mae, n))
    print('wrote rc_split_probe (%d oos10 + %d panel32 rows)' % (len(oos), len(pan)))


if __name__ == '__main__':
    main()
