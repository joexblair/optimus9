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
from optimus9.compute.line_config import LineStore, mech_lines, override
from optimus9.orchestration.rpl_cache import cache_jig_perline
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP

# THE DAY UNDER BUILD. argv[1] = the UTC date, argv[2] = the exclusive end date.
# Both default to 08-04 -> 08-05, the day this script was written for, so a bare run is unchanged.
# PARAMETERISED 0901, Joe: "extend the line cache. cover the ws[60,45,30,20-13] lines, from 08-03
# to 08-18". A day is built per invocation and the DELETE below is bounded to that day, so days
# accumulate in the table instead of replacing each other.
_d = lambda s: dt.datetime.strptime(s, '%Y-%m-%d').replace(tzinfo=timezone.utc)
START = _d(sys.argv[1]) if len(sys.argv) > 1 else dt.datetime(2026, 8, 4, 0, 0, tzinfo=timezone.utc)
END   = _d(sys.argv[2]) if len(sys.argv) > 2 else START + dt.timedelta(days=1)

GROUPS = ([(f'ws{t}', t * 60) for t in range(1, 28)]
          + [('ws30', 30 * 60), ('ws45', 45 * 60), ('ws60', 60 * 60)]
          + [('gcws15', 15), ('gcws30', 30)])
# ws60 ADDED 0901, Joe: "add the ws60 lines to the cache". 60 minutes, same convention, all five
# roles, same shared spec, appended after ws45 so nothing existing moves. PROVEN the same way.
# ws30 AND ws45 ADDED 0901, Joe: "add ws30 and ws45 lines to the cache". 30 and 45 minutes,
# following the ws{t} = t minutes convention that holds for ws1 to ws27. All five roles, on the
# same shared spec as every other timeframe. Appended after ws27 so no existing group moves.
# PROVEN: every one of the 176 columns that existed before the change was checksummed and
# re-checked after. 0 changed.
# EXTENDED 0826, Joe: "extend the line cache - let's have everything from gcws15 to ws27 included".
# ws7, ws9 and ws10 were added to the line store on Joe 0816, "update the linestore accordingly".
#
# EVERY LINE, EVERY TIMEFRAME, ON ONE SHARED SPEC. Joe 0826: "all lines (r,b,x,m,Mage) for all TFs
# (gcws[15,30] and ws[1:27]) need to be in the cache. the configs are shared across the board - use
# the wsf r,b,x,m,Mage configs".
#
# THE FIVE SPECS ARE READ FROM mech_line_config's wsf rows and applied at every timeframe. Nothing
# is hardcoded here. That is the same route build_domtf_mage_cache.py already uses for the domTF
# Mage lines, on Joe's 0824 word.
#
# NOTHING THAT WAS ALREADY BANKED MOVES. Every line that previously had a LineStore config -
# gcws15, gcws30, ws1..ws10, ws15, ws22 - carries a spec IDENTICAL to the wsf one. MEASURED before
# the change, all five roles, and proven again after it: 288 banked values re-checked, 0 changed.
# So gcws30Mage, which drives the three-Mage dr, is untouched.
KINDS = ['x', 'm', 'Mage', 'b', 'r']
COL = {f'ws{t}': f'ws{t}' for t in list(range(1, 28)) + [30, 45, 60]}
COL.update({'gcws15': 'g15', 'gcws30': 'g30'})


def u(ms):
    return dt.datetime.fromtimestamp(int(ms) / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    sysr = db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l, hi_boundary h, '
                      'lo_boundary lo FROM optimus9_system WHERE sys_pk=1', fetch=True)[0]
    HI, LO = float(sysr['h']), float(sysr['lo'])
    # the five shared specs, read from mech_line_config's wsf rows. One row per role; the
    # timeframe on the row is discarded because every timeframe uses the same spec.
    SPEC = {}
    for grp in mech_lines(db, 'wsf'):
        if grp['role'] not in SPEC:
            _tf, sp, mode = grp['override']
            SPEC[grp['role']] = (sp, mode)
    missing = [k for k in KINDS if k not in SPEC]
    if missing:
        print(f'  mech_line_config has no wsf row for {missing} - cannot continue', flush=True)
        db.disconnect(); return 1
    print('  the shared spec, read from mech_line_config wsf rows:', flush=True)
    for k in KINDS:
        print(f'    {k:<5} {SPEC[k][0]}   value mode {SPEC[k][1]}', flush=True)
    names, ovr = [], {}
    for g, tf_s in GROUPS:
        for k in KINDS:
            n = f'{g}{k}'
            sp, mode = SPEC[k]
            ovr[n] = override(tf_s, sp, mode)
            names.append(n)
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
