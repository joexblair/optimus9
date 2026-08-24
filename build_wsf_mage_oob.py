"""build_wsf_mage_oob - the forward wait for the three Mage lines to go out of bounds together.

JOE 0824, verbatim, and this is the whole mechanic:

    "we could consume the raw 85 signals. for each signal without lookback validation, we hold and
     walk until (xwob:4) gcws30Mge + ws1Mage + ws2Mage are oob. we set dr at that moment, then run
     the wsf model"

HOMED IN WSF. Joe 0824: "I'm assuming that the lookback validation is homed in wsf, not dtf". It
was not - the 3-minute backward lookback lives in build_dtf_delegation.py. This forward wait is a
wsf builder from the start, and it reads the delegation moments from dtf rather than recomputing
them.

THE PRODUCERS ARE IMPORTED, NOT COPIED. jig.wsf_facing_dr is Joe's 80/20 three-Mage test and
jig.wsf_facing_dr_held puts his xwob 4 on it. Nothing about the direction rule is restated here.

THE MOMENT IS THE CONFIRMED BAR - the bar where the hold completes, four bars after the condition
first reads true. That follows the precedent already in wsf: wflb_mfr_xwob marks the CONFIRMED
fence exit, not the first bar past the fence.

NO CAP ON THE WAIT. The search runs to the end of the cached tape. Joe named no horizon.

    python3 build_wsf_mage_oob.py
"""
import sys
import datetime as dt
from datetime import timezone

import numpy as np

from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.compute.line_config import LineStore, override, mech_lines
from optimus9.orchestration.rpl_cache import cache_jig_perline
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP
from optimus9.analysis import ws_strat as WS
from optimus9.analysis.jig import wsf_facing_dr, wsf_facing_dr_held
import build_dtf_delegation as D

MAGE_XWOB = 4            # KNOB, Joe 0824: "(xwob:4)". 4 bars = 20 s at the 5 s grid
FACE = D.FACE            # ['gcws30Mage', 'ws1Mage', 'ws2Mage'], Joe 0823
MAGE_KNOB = D.MAGE_KNOB  # 20 -> the fence is 80 / 20

DDL = '''CREATE TABLE IF NOT EXISTS wsf_mage_oob (
    wmo_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    wmo_knobs VARCHAR(48) NOT NULL,     -- EVERY knob that changes a row, so a sweep lands alongside
    wmo_seq SMALLINT NOT NULL,          -- the delegation number, 1 to 85
    wmo_utc DATETIME NOT NULL,          -- the dtf-free delegation moment
    -- the three Mage lines AT the delegation moment
    wmo_g30Mage_at DOUBLE, wmo_ws1Mage_at DOUBLE, wmo_ws2Mage_at DOUBLE,
    wmo_dr_at TINYINT,                  -- wsf_facing_dr at that bar: 0 on every stub
    wmo_had_lookback TINYINT,           -- did the 3-minute BACKWARD lookback already answer it
    -- the forward wait: the CONFIRMED bar where all three have been out of bounds for MAGE_XWOB
    wmo_oob_utc DATETIME, wmo_oob_dr TINYINT, wmo_wait_s INT,
    wmo_g30Mage_oob DOUBLE, wmo_ws1Mage_oob DOUBLE, wmo_ws2Mage_oob DOUBLE,
    UNIQUE KEY uq_wmo (wmo_knobs, wmo_utc))'''

COLS = ['wmo_knobs', 'wmo_seq', 'wmo_utc', 'wmo_g30Mage_at', 'wmo_ws1Mage_at', 'wmo_ws2Mage_at',
        'wmo_dr_at', 'wmo_had_lookback', 'wmo_oob_utc', 'wmo_oob_dr', 'wmo_wait_s',
        'wmo_g30Mage_oob', 'wmo_ws1Mage_oob', 'wmo_ws2Mage_oob']


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    sy = db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l FROM optimus9_system '
                    'WHERE sys_pk=1', fetch=True)[0]
    MHI, MLO = 100.0 - MAGE_KNOB, float(MAGE_KNOB)

    ls = LineStore(db)
    ovr = {n: (*ls.resolve(n), ls.value_mode(n)) for n in set(list(WS.LINES) + FACE)}
    for g in mech_lines(db, 'wsf'):
        tf = g['tf_seconds'] // 60
        if f'ws{tf}{g["role"]}' in FACE:
            ovr[f'ws{tf}{g["role"]}'] = g['override']
    J = cache_jig_perline(END_MS, HOURS, WARMUP, ovr,
                          pxs_cfg={'src': sy['s'], 'len': sy['l']}, rebuild=False)
    ts = np.asarray(J.ts)
    MG = [np.asarray(J.W.line(n), float) for n in FACE]
    DRr = wsf_facing_dr(MG, MHI, MLO)            # Joe's 80/20 test, no hold
    DRh = wsf_facing_dr_held(DRr, MAGE_XWOB)     # the same, held MAGE_XWOB bars

    dele = db.execute('SELECT dds_seq q, dds_utc t, dds_g30Mage a, dds_ws1Mage b, dds_ws2Mage c, '
                      'dds_last_out_utc lo FROM dtf_delegation ORDER BY dds_utc', fetch=True)
    if not dele:
        print('  dtf_delegation is empty. Run build_dtf_delegation.py first.', flush=True)
        db.disconnect(); return 1

    knobs = f'mk{MAGE_KNOB}_mx{MAGE_XWOB}'
    db.execute(DDL)
    had = db.execute('SELECT COUNT(*) c FROM wsf_mage_oob WHERE wmo_knobs=%s',
                     (knobs,), fetch=True)[0]['c']
    if had:
        print(f'  replacing {had} rows at these knobs', flush=True)
        db.execute('DELETE FROM wsf_mage_oob WHERE wmo_knobs=%s', (knobs,))

    rows = []
    for x in dele:
        ms = int(dt.datetime.strptime(str(x['t']), '%Y-%m-%d %H:%M:%S')
                 .replace(tzinfo=timezone.utc).timestamp() * 1000)
        k = int(np.searchsorted(ts, ms))
        # the first CONFIRMED bar at or after the delegation. No cap - Joe named no horizon.
        j = next((z for z in range(k, len(DRh)) if DRh[z] != 0), None)
        if j is None:
            rows.append((knobs, x['q'], str(x['t']), x['a'], x['b'], x['c'],
                         int(DRr[k]), int(x['lo'] is not None), None, None, None,
                         None, None, None))
            continue
        u = dt.datetime.fromtimestamp(int(ts[j]) / 1000, timezone.utc)
        rows.append((knobs, x['q'], str(x['t']), x['a'], x['b'], x['c'],
                     int(DRr[k]), int(x['lo'] is not None),
                     u.strftime('%Y-%m-%d %H:%M:%S'), int(DRh[j]),
                     (int(ts[j]) - int(ts[k])) // 1000,
                     float(MG[0][j]), float(MG[1][j]), float(MG[2][j])))
    db.executemany(f'INSERT INTO wsf_mage_oob ({",".join(COLS)}) VALUES '
                   f'({",".join(["%s"] * len(COLS))})', rows)

    found = sum(1 for r in rows if r[8] is not None)
    print(f'\n  wsf_mage_oob : {len(rows)} delegation moments   knobs {knobs}\n'
          f'    a confirmed all-3-out bar at or after the delegation : {found}'
          f'   none to the end of the tape : {len(rows) - found}\n', flush=True)
    print(f"  {'dtf-free':<11}{'ws1Mage':>10}{'ws2Mage':>10}{'3 Mages oob':>14}"
          f"{'ws1Mage':>10}{'ws2Mage':>10}", flush=True)
    for r in rows:
        print(f"  {r[2][11:]:<11}{r[4]:>10.2f}{r[5]:>10.2f}"
              f"{(r[8][11:] if r[8] else 'none'):>14}"
              f"{(f'{r[12]:.2f}' if r[12] is not None else ''):>10}"
              f"{(f'{r[13]:.2f}' if r[13] is not None else ''):>10}", flush=True)
    db.disconnect()
    return 0


if __name__ == '__main__':
    sys.exit(main())
