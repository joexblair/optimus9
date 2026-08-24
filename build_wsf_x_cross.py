"""build_wsf_x_cross — every ws{tf}x crossing, per bar, per direction. Joe 0821.

Joe 0820: "do whatever you need to do. 'x X [Mage, b, boundary]' (race condition) is integral to the
spec. x X r should be caclulated also". Joe 0821: "yes, you need those x-crosses - build".

This is register task #61, open since 0818, and it is what blocks the walk forward from a declared
wsf-exhaust: Joe's rule is "if ws{weak-mage}x-cross has printed, then create a trade signal", and
nothing on this path has ever computed a crossing.

THE DIRECTION, Joe 0818: the fast partner turns BACK against the bias.
    read UPWARD   -> ws{tf}x crosses DOWN under its target
    read DOWNWARD -> ws{tf}x crosses UP over its target
Joe confirmed this reading: "x-cross direction: you've nailed it".

THE RACE. Joe 0818: "use ' x X [MAge,b,boundary]' for now" and "any one - race condition". So the
three are watched together and the FIRST to cross wins. `x X r` is stored beside them because Joe
0820 asked for it, and it is one of the three targets task #61 exists to sweep.

THE BOUNDARY is the one on the side being read - 85 upward, 15 downward, from optimus9_system.

A CROSSING NEEDS A SIDE CHANGE. x must be on one side of the target at the previous bar and the
other side at this bar. A line already through does not re-cross.

CAUSAL. Every read is this bar and the one before it.
"""
import sys
import datetime as dt
from datetime import timezone

import numpy as np

from optimus9.config import get_db_config
from optimus9 import DatabaseManager

WIN_FROM = '2026-08-04 00:00:00'
WIN_TO   = '2026-08-05 00:00:00'
TFS      = list(range(1, 9))
DRS      = (+1, -1)
TARGETS  = ('Mage', 'b', 'boundary', 'r')      # the race is the first three; r is stored beside them
XCROSS_XWOB = 5
# 5 s bars x must HOLD on the far side before a crossing counts. Same shape as the fence exit's
# xwob, its own knob and its own value.
#
# WHY 5. A run of N bars spans (N-1) x 5 seconds, so 5 bars is the first value that reaches 20 s;
# 4 stops at 15. Measured on 08-04 across 4,426 runs of x on the far side of its Mage, both
# directions, all eight timeframes:
#     1 bar    697 runs  15.7%        5 bars   184 runs   4.2%
#     2 bars   484 runs  10.9%        6 bars   188 runs   4.2%
#     3 bars   326 runs   7.4%        7 bars   148 runs   3.3%
#     4 bars   263 runs   5.9%      longer   1,672 runs  37.8%
# xwob 5 discards 1,770 runs (40.0%) and keeps 2,656. The extra bar over 4 costs 263 runs, 5.9%.
# THERE IS NO KNEE - the curve falls smoothly from 15.7% to 1.8%. 20 seconds is the target that
# picks it, and the knob is in the unique key so another value lands alongside.

DDL = '''CREATE TABLE IF NOT EXISTS wsf_x_cross (
    wxc_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    wxc_win_from DATETIME NOT NULL,
    wxc_xwob     SMALLINT NOT NULL DEFAULT 0,  -- KNOB. 5 s bars x must hold on the far side
    --   before a crossing counts. In the unique key.
    wxc_hi       DOUBLE   NOT NULL,   -- upper boundary, 85
    wxc_lo       DOUBLE   NOT NULL,   -- lower boundary, 15
    wxc_utc      DATETIME NOT NULL,   -- the bar the crossing completes
    wxc_tf       SMALLINT NOT NULL,   -- timeframe 1 to 8. The line is ws{tf}x
    wxc_dr       TINYINT  NOT NULL,   -- direction read. +1 upward, -1 downward
    wxc_x        DOUBLE,              -- ws{tf}x at this bar
    wxc_mage     DOUBLE,              -- ws{tf}Mage at this bar
    wxc_b        DOUBLE,              -- ws{tf}b at this bar
    wxc_r        DOUBLE,              -- ws{tf}r at this bar
    wxc_bound    DOUBLE,              -- the boundary on the side being read
    wxc_x_mage   TINYINT NOT NULL,    -- 1 = x crossed its Mage on this bar, against the bias
    wxc_x_b      TINYINT NOT NULL,    -- 1 = x crossed its b
    wxc_x_bound  TINYINT NOT NULL,    -- 1 = x crossed the boundary
    wxc_x_r      TINYINT NOT NULL,    -- 1 = x crossed its r
    wxc_race     TINYINT NOT NULL,    -- 1 = ANY of Mage, b or boundary crossed. THE RACE
    wxc_race_won VARCHAR(8),          -- which of the three it was. NULL when the race did not fire
    UNIQUE KEY uq_wxc (wxc_win_from, wxc_hi, wxc_lo, wxc_xwob, wxc_utc, wxc_tf, wxc_dr),
    KEY k_bar (wxc_utc), KEY k_race (wxc_race), KEY k_line (wxc_tf, wxc_dr))'''

COLS = ['wxc_win_from', 'wxc_xwob', 'wxc_hi', 'wxc_lo', 'wxc_utc', 'wxc_tf', 'wxc_dr',
        'wxc_x', 'wxc_mage', 'wxc_b', 'wxc_r', 'wxc_bound',
        'wxc_x_mage', 'wxc_x_b', 'wxc_x_bound', 'wxc_x_r', 'wxc_race', 'wxc_race_won']


def far_side(x, t, dr):
    """Is x on the far side of its target for this read? Upward -> below it. Downward -> above."""
    if not (np.isfinite(x) and np.isfinite(t)):
        return None
    return (x < t) if dr > 0 else (x > t)


def held(runs, key, x, t, dr):
    """Advance the hold counter for one (line, target, direction) and say whether it CONFIRMS here.

    Same semantics as the fence exit's xwob and as jig.momo_landed: the run counts CONSECUTIVE bars
    on the far side, and it only counts if x was on the NEAR side before it crossed. A crossing
    confirms on the bar the run reaches XCROSS_XWOB - not on the bar it started."""
    st = runs.setdefault(key, {'run': 0, 'was_near': False, 'fired': False})
    f = far_side(x, t, dr)
    if f is None:
        st['run'] = 0
        return False
    if not f:
        st.update(run=0, was_near=True, fired=False)
        return False
    if not st['was_near']:
        return False                      # standing on the far side since the start - no crossing
    st['run'] += 1
    if st['run'] >= XCROSS_XWOB and not st['fired']:
        st['fired'] = True
        return True
    return False


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    sysr = db.execute('SELECT hi_boundary hi, lo_boundary lo FROM optimus9_system WHERE sys_pk=1',
                      fetch=True)[0]
    HI, LO = float(sysr['hi']), float(sysr['lo'])

    cols = ', '.join(f'wlb_ws{tf}{k} `ws{tf}{k}`' for tf in TFS for k in ('x', 'Mage', 'b', 'r'))
    rows = db.execute(f'SELECT wlb_utc utc, {cols} FROM ws_line_bar '
                      f'WHERE wlb_utc >= %s AND wlb_utc <= %s ORDER BY wlb_utc',
                      (WIN_FROM, WIN_TO), fetch=True)
    print(f'  {len(rows):,} bars from ws_line_bar   boundaries {HI:.0f} / {LO:.0f}', flush=True)

    db.execute(DDL)
    have = {c['Field'] for c in db.execute('SHOW COLUMNS FROM wsf_x_cross', fetch=True)}
    if 'wxc_xwob' not in have:
        db.execute('ALTER TABLE wsf_x_cross ADD COLUMN wxc_xwob SMALLINT NOT NULL DEFAULT 0 '
                   'AFTER wxc_win_from')
        db.execute('ALTER TABLE wsf_x_cross DROP INDEX uq_wxc, ADD UNIQUE KEY uq_wxc '
                   '(wxc_win_from, wxc_hi, wxc_lo, wxc_xwob, wxc_utc, wxc_tf, wxc_dr)')
        print('  added wxc_xwob and rebuilt the unique key', flush=True)
    where = 'wxc_win_from=%s AND wxc_hi=%s AND wxc_lo=%s AND wxc_xwob=%s'
    kv = (WIN_FROM, HI, LO, XCROSS_XWOB)
    n = db.execute('SELECT COUNT(*) c FROM wsf_x_cross WHERE ' + where, kv, fetch=True)[0]['c']
    if n:
        print(f'  deleting {n:,} rows already stored at these boundaries', flush=True)
        db.execute('DELETE FROM wsf_x_cross WHERE ' + where, kv)

    out = []
    runs = {}
    for i in range(len(rows)):
        c = rows[i]
        utc = c['utc'].strftime('%Y-%m-%d %H:%M:%S')
        for tf in TFS:
            xn = float(c[f'ws{tf}x']); mn = float(c[f'ws{tf}Mage'])
            bn = float(c[f'ws{tf}b']); rn = float(c[f'ws{tf}r'])
            for dr in DRS:
                bound = HI if dr > 0 else LO
                xm = held(runs, (tf, dr, 'Mage'), xn, mn, dr)
                xb = held(runs, (tf, dr, 'b'), xn, bn, dr)
                xo = held(runs, (tf, dr, 'bound'), xn, bound, dr)
                xr = held(runs, (tf, dr, 'r'), xn, rn, dr)
                won = 'Mage' if xm else ('b' if xb else ('boundary' if xo else None))
                out.append((WIN_FROM, XCROSS_XWOB, HI, LO, utc, tf, dr,
                            xn, mn, bn, rn, bound,
                            int(xm), int(xb), int(xo), int(xr),
                            int(xm or xb or xo), won))
        if len(out) >= 40000:
            db.executemany(f'INSERT INTO wsf_x_cross ({",".join(COLS)}) VALUES '
                           f'({",".join(["%s"] * len(COLS))})', out)
            out = []
    if out:
        db.executemany(f'INSERT INTO wsf_x_cross ({",".join(COLS)}) VALUES '
                       f'({",".join(["%s"] * len(COLS))})', out)

    t = db.execute('SELECT COUNT(*) c, SUM(wxc_race) r, SUM(wxc_x_mage) m, SUM(wxc_x_b) b, '
                   'SUM(wxc_x_bound) o, SUM(wxc_x_r) xr FROM wsf_x_cross WHERE ' + where,
                   kv, fetch=True)[0]
    print(f'\n  wsf_x_cross : {int(t["c"]):,} rows', flush=True)
    print(f'    x crossed its Mage     : {int(t["m"]):,}', flush=True)
    print(f'    x crossed its b        : {int(t["b"]):,}', flush=True)
    print(f'    x crossed the boundary : {int(t["o"]):,}', flush=True)
    print(f'    THE RACE fired         : {int(t["r"]):,}', flush=True)
    print(f'    x crossed its r        : {int(t["xr"]):,}   (stored beside, not in the race)',
          flush=True)
    db.disconnect()
    return 0


if __name__ == '__main__':
    sys.exit(main())
