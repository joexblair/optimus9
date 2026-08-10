"""ws_cross_list — OOB->IB crossings of ws22b / ws22Mage / ws15b / ws15Mage on three emerging bar
grids. Joe 0806. Onscreen only; nothing is written.

    5s  pxs (frac 1/12) xwob 8 = 40 s hold
    10s pxs (frac 1/6)  xwob 4 = 40 s
    15s pxs (frac 1/4)  xwob 3 = 45 s

The lines stay on the 5 s grid. The GRID is coarsened: each coarse bar takes the line's value at its
LAST 5 s bar (emerging), and xwob is counted in COARSE bars. Producers: jig.px_smooth /
jig.coarsen / jig.oob_ib_cross.

    python3 ws_cross_list.py [--n 5] [--persist 12]

--persist FRAC writes that grid's crossings to ws_cross. Joe 0806 took the 5s/xwob-8 grid; the frac
and xwob are COLUMNS, so the 10s and 15s grids can be banked alongside without colliding.
"""
import sys, datetime as dt
from datetime import timezone
import numpy as np

from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.compute.line_config import LineStore
from optimus9.orchestration.rpl_cache import cache_jig_perline
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP
from optimus9.analysis.jig import px_smooth, coarsen, oob_ib_cross, FRAC_SECONDS

LINES = ['ws22b', 'ws22Mage', 'ws15b', 'ws15Mage']
DDL = '''CREATE TABLE IF NOT EXISTS ws_cross (
    wsc_pk        BIGINT AUTO_INCREMENT PRIMARY KEY,
    wsc_frac      SMALLINT NOT NULL,          -- emerging bar = 60/frac seconds (jig.BAR_FRACTIONS)
    wsc_bar_sec   SMALLINT NOT NULL,          -- ... that bar size, spelled out
    wsc_xwob      SMALLINT NOT NULL,          -- bars the line must hold between the levels to confirm
    wsc_line      VARCHAR(12) NOT NULL,
    wsc_tf_sec    SMALLINT NOT NULL,          -- the line's own timeframe
    wsc_bb_len    SMALLINT NOT NULL, wsc_bb_mult DECIMAL(8,4) NOT NULL,
    wsc_cross_ms  BIGINT NOT NULL, wsc_cross_utc VARCHAR(19),   -- first bar back between the levels
    wsc_conf_ms   BIGINT NOT NULL, wsc_conf_utc VARCHAR(19),    -- cross + (xwob-1): first knowable bar
    wsc_side      TINYINT NOT NULL,           -- +1 the run was above 85, -1 below 15
    wsc_val       DOUBLE,                     -- the line at the cross bar
    wsc_val_prev  DOUBLE,                     -- the line at the last bar beyond the level
    wsc_pxs       DOUBLE,                     -- smoothed price at the cross bar, on the same grid
    UNIQUE KEY uq_wsc (wsc_frac, wsc_xwob, wsc_line, wsc_cross_ms),
    KEY (wsc_cross_ms), KEY (wsc_line), KEY (wsc_side))'''
GRIDS = [(12, 8), (6, 4), (4, 3)]                 # (frac, xwob) -> 5s/8, 10s/4, 15s/3
START = dt.datetime(2026, 8, 4, 12, 0, tzinfo=timezone.utc)
u = lambda t: dt.datetime.fromtimestamp(int(t) / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


def main(n=5, persist=None):
    db = DatabaseManager(**get_db_config()); db.connect()
    row = db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l, hi_boundary h, lo_boundary lo '
                     'FROM optimus9_system WHERE sys_pk=1', fetch=True)[0]
    HI, LO, DLEN = float(row['h']), float(row['lo']), int(row['l'])
    ls = LineStore(db)
    ovr = {x: (*ls.resolve(x), ls.value_mode(x)) for x in LINES}
    J = cache_jig_perline(END_MS, HOURS, WARMUP, ovr, pxs_cfg={'src': row['s'], 'len': DLEN})
    ts = np.asarray(J.ts); V = {x: np.asarray(J.W.line(x), float) for x in LINES}
    evt = np.asarray(J.evt, bool)
    kr = db.execute('SELECT kc_timestamp t, kc_close c FROM kline_collection WHERE kc_tp_pk=1 '
                    'AND kc_timestamp BETWEEN %s AND %s', (int(ts[0]), int(ts[-1])), fetch=True)
    px = np.full(len(ts), np.nan)
    kt = np.array([r['t'] for r in kr], np.int64); kc = np.array([float(r['c']) for r in kr])
    o = np.argsort(kt); kt, kc = kt[o], kc[o]
    j = np.searchsorted(ts, kt); ok = (j < len(ts)) & (ts[np.clip(j, 0, len(ts) - 1)] == kt)
    px[j[ok]] = kc[ok]
    i0 = int(np.searchsorted(ts, int(START.timestamp() * 1000)))
    for x in LINES:
        print(f"  {x:<10} {ls.resolve(x)[1]}  @{ls.resolve(x)[0]}s")
    print(f'window {u(ts[i0])} -> {u(ts[-1])}   boundaries {HI}/{LO}   DEMA len {DLEN}\n')

    for frac, xwob in GRIDS:
        sec = FRAC_SECONDS[frac]
        pxs = px_smooth(ts, px, evt, length=DLEN, frac=frac)
        allx = []
        per = {}
        for x in LINES:
            cv, cidx = coarsen(V[x], ts, frac)
            cr = [(k, c, s) for (k, c, s) in oob_ib_cross(cv, HI, LO, xwob) if cidx[k] >= i0]
            per[x] = len(cr)
            for k, c, s in cr:
                allx.append((int(ts[cidx[k]]), x, s, int(ts[cidx[c]]), float(cv[k]),
                             float(cv[k - 1]), float(pxs[cidx[k]])))
        allx.sort()
        if persist == frac:
            db.execute(DDL)
            db.execute('DELETE FROM ws_cross WHERE wsc_frac=%s AND wsc_xwob=%s', (frac, xwob))
            rows = [(frac, sec, xwob, x, ls.resolve(x)[0], ls.resolve(x)[1][1], ls.resolve(x)[1][2],
                     t, u(t), ct, u(ct), sd, v, pv, p) for (t, x, sd, ct, v, pv, p) in allx]
            db.executemany('INSERT INTO ws_cross (wsc_frac,wsc_bar_sec,wsc_xwob,wsc_line,wsc_tf_sec,'
                           'wsc_bb_len,wsc_bb_mult,wsc_cross_ms,wsc_cross_utc,wsc_conf_ms,wsc_conf_utc,'
                           'wsc_side,wsc_val,wsc_val_prev,wsc_pxs) VALUES '
                           '(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', rows)
            got = db.execute('SELECT COUNT(*) n FROM ws_cross WHERE wsc_frac=%s AND wsc_xwob=%s',
                             (frac, xwob), fetch=True)[0]['n']
            print(f'>>> ws_cross: {len(rows)} rows offered, {got} in table at frac 1/{frac} '
                  f'({sec}s) xwob {xwob}')
        print(f'=== pxs {sec}s (frac 1/{frac})  xwob {xwob} = {xwob * sec}s hold   '
              f'{len(allx)} crossings   ' + '  '.join(f'{k}={v}' for k, v in per.items()))
        print(f"    {'#':>2} {'cross_utc':<20} {'line':<10} {'side':>4} {'conf_utc':<9} "
              f"{'val@cross':>10} {'val@prev':>9} {'pxs':>9}")
        for i, (t, x, s, ct, v, pv, p) in enumerate(allx[:n], 1):
            print(f"    {i:>2} {u(t):<20} {x:<10} {s:>+4} {u(ct)[11:]:<9} {v:>10.2f} {pv:>9.2f} {p:>9.5f}")
        print()
    db.disconnect()


if __name__ == '__main__':
    a = sys.argv
    main(n=int(a[a.index('--n') + 1]) if '--n' in a else 5,
         persist=int(a[a.index('--persist') + 1]) if '--persist' in a else None)
