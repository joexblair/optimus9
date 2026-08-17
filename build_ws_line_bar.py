"""build_ws_line_bar — every finisher line at every 5-second bar of 08-04, and every crossing.

Joe 0816: "prepare a 08-04 24 hour dataset that allows for quick response to these kind of
questions" — the first cross after a time among a set of lines, and the values of two lines for
some number of bars before they crossed.

TWO TABLES.

  ws_line_bar    one row per 5-second bar. One column per line. 17,281 rows.
                 Also a per-group flag marking the bars that START a new bar of that group's own
                 timeframe, so "the last 12 bars of ws4" has a definite meaning.

  ws_line_cross  one row per crossing. Every pair among x, m, Mage, b, r inside a group, plus
                 every line against the two boundaries 85 and 15. Both directions.

WHAT IS IN THEM. Groups ws1 to ws6 (1 to 6 minute), gcws15 (15 s) and gcws30 (30 s).
Kinds x, m, Mage, b, r. A kind is skipped where the line store has no config for it.

Nothing here is a mechanic. It is the raw lines and the raw crossings, so a question can be
answered with one query instead of a rerun.
"""
import sys
import datetime as dt
from datetime import timezone

import numpy as np

from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.compute.line_config import LineStore
from optimus9.orchestration.rpl_cache import cache_jig_perline
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP

START = dt.datetime(2026, 8, 4, 0, 0, tzinfo=timezone.utc)
END   = dt.datetime(2026, 8, 5, 0, 0, tzinfo=timezone.utc)

GROUPS = [('ws1', 60), ('ws2', 120), ('ws3', 180), ('ws4', 240), ('ws5', 300), ('ws6', 360),
          ('ws7', 420), ('ws8', 480), ('ws9', 540), ('ws10', 600),
          ('gcws15', 15), ('gcws30', 30)]
# ws7, ws9 and ws10 added to the line store on Joe 0816, "update the linestore accordingly", so
# every timeframe in jig.MOMO_CHECK_TFS (2 to 10) has all five lines.
KINDS = ['x', 'm', 'Mage', 'b', 'r']
COL = {'ws1': 'ws1', 'ws2': 'ws2', 'ws3': 'ws3', 'ws4': 'ws4', 'ws5': 'ws5', 'ws6': 'ws6',
       'ws7': 'ws7', 'ws8': 'ws8', 'ws9': 'ws9', 'ws10': 'ws10',
       'gcws15': 'g15', 'gcws30': 'g30'}


def u(ms):
    return dt.datetime.fromtimestamp(int(ms) / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    sysr = db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l, hi_boundary h, '
                      'lo_boundary lo FROM optimus9_system WHERE sys_pk=1', fetch=True)[0]
    HI, LO = float(sysr['h']), float(sysr['lo'])
    ls = LineStore(db)
    names, ovr = [], {}
    for g, _ in GROUPS:
        for k in KINDS:
            n = f'{g}{k}'
            try:
                ovr[n] = (*ls.resolve(n), ls.value_mode(n)); names.append(n)
            except Exception:
                print(f'  no config for {n}, skipped', flush=True)
    J = cache_jig_perline(END_MS, HOURS, WARMUP, ovr,
                          pxs_cfg={'src': sysr['s'], 'len': sysr['l']}, rebuild=False)
    ts = np.asarray(J.ts); W = J.W
    i0 = int(np.searchsorted(ts, int(START.timestamp() * 1000)))
    i1 = int(np.searchsorted(ts, int(END.timestamp() * 1000)))
    V = {n: np.asarray(W.line(n), float) for n in names}
    print(f'  {len(names)} lines, bars {i0} to {i1} = {i1 - i0 + 1:,}', flush=True)

    cols = [f'wlb_{COL[g]}{k}' for g, _ in GROUPS for k in KINDS if f'{g}{k}' in V]
    flags = [f'wlb_{COL[g]}_newbar' for g, _ in GROUPS]
    db.execute('CREATE TABLE IF NOT EXISTS ws_line_bar (\n'
               '  wlb_pk BIGINT AUTO_INCREMENT PRIMARY KEY,\n'
               '  wlb_ms BIGINT NOT NULL, wlb_utc DATETIME NOT NULL,\n'
               + ''.join(f'  {c} DOUBLE,\n' for c in cols)
               + ''.join(f'  {c} TINYINT NOT NULL DEFAULT 0,\n' for c in flags)
               + '  UNIQUE KEY uq_wlb (wlb_ms), KEY (wlb_utc))')
    have = {r['Field'] for r in db.execute('SHOW COLUMNS FROM ws_line_bar', fetch=True)}
    for c in cols:
        if c not in have:
            db.execute(f'ALTER TABLE ws_line_bar ADD COLUMN {c} DOUBLE')
    for c in flags:
        if c not in have:
            db.execute(f'ALTER TABLE ws_line_bar ADD COLUMN {c} TINYINT NOT NULL DEFAULT 0')

    rows = []
    for i in range(i0, i1 + 1):
        sec = int(ts[i]) // 1000
        r = [int(ts[i]), u(ts[i])]
        for g, _ in GROUPS:
            for k in KINDS:
                if f'{g}{k}' in V:
                    v = float(V[f'{g}{k}'][i])
                    r.append(None if not np.isfinite(v) else v)
        for g, tf in GROUPS:
            r.append(1 if sec % tf == 0 else 0)
        rows.append(tuple(r))
    allc = ['wlb_ms', 'wlb_utc'] + cols + flags
    db.execute('DELETE FROM ws_line_bar WHERE wlb_utc >= %s AND wlb_utc <= %s',
               (u(ts[i0]), u(ts[i1])))
    for s in range(0, len(rows), 2000):
        db.executemany(f'INSERT INTO ws_line_bar ({",".join(allc)}) VALUES '
                       f'({",".join(["%s"] * len(allc))})', rows[s:s + 2000])
    print(f'  ws_line_bar : {len(rows):,} rows, {len(allc)} columns', flush=True)

    db.execute('''CREATE TABLE IF NOT EXISTS ws_line_cross (
        wlc_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
        wlc_ms BIGINT NOT NULL, wlc_utc DATETIME NOT NULL,
        wlc_group   VARCHAR(8) NOT NULL,    -- ws1..ws6, gcws15, gcws30
        wlc_line    VARCHAR(6) NOT NULL,    -- the line that moved: x, m, Mage, b, r
        wlc_against VARCHAR(6) NOT NULL,    -- what it crossed: another kind, or 85, or 15
        wlc_dir     VARCHAR(4) NOT NULL,    -- up | down
        wlc_val     DOUBLE NOT NULL,        -- the moving line at the crossing bar
        wlc_level   DOUBLE NOT NULL,        -- what it crossed, at the crossing bar
        wlc_val_prev DOUBLE, wlc_level_prev DOUBLE,   -- both, one bar earlier
        UNIQUE KEY uq_wlc (wlc_group, wlc_line, wlc_against, wlc_dir, wlc_ms),
        KEY (wlc_utc), KEY (wlc_group, wlc_line), KEY (wlc_against))''')
    cr = []
    for g, _ in GROUPS:
        ks = [k for k in KINDS if f'{g}{k}' in V]
        pairs = [(a, b) for ai, a in enumerate(ks) for b in ks[ai + 1:]]
        pairs += [(k, str(int(HI))) for k in ks] + [(k, str(int(LO))) for k in ks]
        for a, b in pairs:
            A = V[f'{g}{a}']
            B = (np.full(len(A), float(b)) if b.isdigit() else V[f'{g}{b}'])
            for i in range(i0, i1 + 1):
                if A[i - 1] <= B[i - 1] and A[i] > B[i]:
                    cr.append((int(ts[i]), u(ts[i]), g, a, b, 'up',
                               float(A[i]), float(B[i]), float(A[i - 1]), float(B[i - 1])))
                elif A[i - 1] >= B[i - 1] and A[i] < B[i]:
                    cr.append((int(ts[i]), u(ts[i]), g, a, b, 'down',
                               float(A[i]), float(B[i]), float(A[i - 1]), float(B[i - 1])))
    db.execute('DELETE FROM ws_line_cross WHERE wlc_utc >= %s AND wlc_utc <= %s',
               (u(ts[i0]), u(ts[i1])))
    C = ['wlc_ms', 'wlc_utc', 'wlc_group', 'wlc_line', 'wlc_against', 'wlc_dir',
         'wlc_val', 'wlc_level', 'wlc_val_prev', 'wlc_level_prev']
    for s in range(0, len(cr), 2000):
        db.executemany(f'INSERT INTO ws_line_cross ({",".join(C)}) VALUES '
                       f'({",".join(["%s"] * len(C))})', cr[s:s + 2000])
    print(f'  ws_line_cross : {len(cr):,} rows', flush=True)
    db.disconnect()
    return 0


if __name__ == '__main__':
    sys.exit(main())
