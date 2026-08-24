"""build_wsf_bar_tf — the Mage side of every bar, plus how each r line last moved.

Joe 0820: "build a full dataset (for the per-marker report) for the whole day so that you can
quickly answer requests without recreating the data".

WHAT ALREADY EXISTED, and is NOT rebuilt here:
  wsf_line_bar   r value, momentum verdict, stall, seconds since the stall started, fit slope, fit
                 quality, out of bounds - for ws1r to ws8r, both directions, all 17,281 bars of
                 08-04, at MOMO_FIXED_SAMPLES 21. 276,496 rows.
  ws_line_bar    every line value including Mage, ws1 to ws10, all 17,281 bars.

WHAT WAS MISSING, and is what this builds:
  the Mage reading per bar, per timeframe, per direction, and the mage-weakness-tf that falls out
  of it - which was only ever banked at the 121 signal bars, in ws_fin_weak_mage.
  how each r line last moved - its previous distinct value and how long ago it changed. These lines
  only move when their own timeframe's bar forms, so a 5-second reading is flat most of the time
  and "which way is it going" cannot be read off two adjacent bars.

THE MAGE-WEAKNESS SCAN carries the spec's 120-second tolerance (WMT_LOOKBACK_S, ws-finisher_spec
KNOBS): a Mage that was out of bounds at any bar inside the last 120 seconds still counts as out.
Both forms are on the row - the tolerance version and the seconds-since-last-out that feeds it - so
the no-tolerance scan is a query, not a rebuild.

NOT IN HERE, because neither has a definition yet:
  "heading toward / heading away" - Joe 0820 called it a new request. The raw travel is banked so
  that whatever definition lands can be computed without rebuilding.
  the wsf momentum state - momoc, exhaust, momo-none. The three-state flow has five open questions.
"""
import sys
import os
import datetime as dt
from datetime import timezone

import numpy as np

from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.compute.line_config import mech_lines
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP
from optimus9.orchestration.rpl_cache import LINE_DIR, TAPE_DIR, _line_key, _tape_key

WIN_FROM = '2026-08-04 00:00:00'
WIN_TO   = '2026-08-05 00:00:00'
TFS      = list(range(1, 9))
DRS      = (+1, -1)
GRID_S   = 5
WMT_LOOKBACK_S = 120     # ws-finisher_spec KNOBS. Joe 0817: "add a lookback tolerance ... knob:120sec"
WMT_TF_LO = 2            # Joe 0821: "reduce the range for weak-mage-tf - it will now be applied to
#                          TF2 to TF8". Was TF1 to TF8. The scan starts here.

DDL = '''CREATE TABLE IF NOT EXISTS wsf_bar_tf (
    wbt_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    wbt_win_from   DATETIME NOT NULL,
    wbt_hi         DOUBLE   NOT NULL,   -- upper fence, 85
    wbt_lo         DOUBLE   NOT NULL,   -- lower fence, 15
    wbt_wmt_lookback_s SMALLINT NOT NULL, -- the Mage tolerance, 120 seconds
    wbt_wmt_tf_lo   SMALLINT NOT NULL DEFAULT 1,  -- KNOB. lowest timeframe the weak-mage scan
    --   starts at. Joe 0821 moved it from 1 to 2. In the unique key.
    wbt_utc        DATETIME NOT NULL,   -- the bar, 5-second grid
    wbt_tf         SMALLINT NOT NULL,   -- timeframe 1 to 8
    wbt_dr         TINYINT  NOT NULL,   -- direction read. +1 upward, -1 downward
    -- MAGE
    wbt_mage       DOUBLE,              -- ws{tf}Mage value, 0 to 100
    wbt_mage_oob   TINYINT,             -- 1 = out of bounds on THIS direction's side, at this bar
    wbt_mage_ago_s INT,                 -- seconds since this Mage was last out of bounds. NULL = never
    wbt_mage_oob_tol TINYINT,           -- 1 = out of bounds at this bar OR inside the 120 s tolerance
    wbt_weak_mage_tf SMALLINT,          -- the bar's mage-weakness-tf under the tolerance. NULL = all
    --   eight were out of bounds, which the spec records as a result, not a failure
    -- HOW THE r LINE LAST MOVED. Direction-independent - the value is the value.
    wbt_r          DOUBLE,              -- ws{tf}r value, 0 to 100
    wbt_r_prev     DOUBLE,              -- the previous DISTINCT value this line printed
    wbt_r_held_s   INT,                 -- seconds it has held the current value
    wbt_r_step     VARCHAR(7),          -- how it got here from the previous distinct value
    wbt_r_over50   TINYINT,             -- 1 = above 50. Joe 0820 read ws8r "not over 50" as not engaged
    UNIQUE KEY uq_wbt (wbt_win_from, wbt_hi, wbt_lo, wbt_wmt_lookback_s, wbt_wmt_tf_lo,
                       wbt_utc, wbt_tf, wbt_dr),
    KEY k_bar (wbt_utc), KEY k_line (wbt_tf, wbt_dr), KEY k_wmt (wbt_weak_mage_tf))'''

COLS = ['wbt_win_from', 'wbt_hi', 'wbt_lo', 'wbt_wmt_lookback_s', 'wbt_wmt_tf_lo',
        'wbt_utc', 'wbt_tf', 'wbt_dr',
        'wbt_mage', 'wbt_mage_oob', 'wbt_mage_ago_s', 'wbt_mage_oob_tol', 'wbt_weak_mage_tf',
        'wbt_r', 'wbt_r_prev', 'wbt_r_held_s', 'wbt_r_step', 'wbt_r_over50']


def _f(x):
    x = float(x)
    return x if np.isfinite(x) else None


def travel(a, i0, i1):
    """For every bar in [i0, i1]: the previous DISTINCT value, and how long the current one has held.

    These lines step only when their own timeframe's bar closes, so between steps the 5-second
    reading repeats. Two adjacent bars therefore say nothing about direction; the previous distinct
    value does."""
    n = len(a)
    changed = np.empty(n, bool)
    changed[0] = True
    changed[1:] = a[1:] != a[:-1]
    idx = np.arange(n)
    last = np.maximum.accumulate(np.where(changed, idx, -1))       # bar this value first printed
    prev_i = np.maximum(last - 1, 0)                                # the bar before that
    return a[prev_i][i0:i1 + 1], ((idx - last) * GRID_S)[i0:i1 + 1]


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    sysr = db.execute('SELECT pxsmooth_dema_src src, pxsmooth_dema_len len '
                      'FROM optimus9_system WHERE sys_pk=1', fetch=True)[0]
    PXS = {'src': sysr['src'], 'len': sysr['len']}

    lines = {}
    for g in mech_lines(db, 'wsf'):
        tf = g['tf_seconds'] // 60
        if g['role'] in ('Mage', 'r') and tf in TFS:
            lines[(g['role'], tf)] = np.load(
                os.path.join(LINE_DIR, _line_key(END_MS, HOURS, WARMUP, g['override']) + '.npy'))
            HI, LO = g['hi'], g['lo']

    ts = np.load(os.path.join(TAPE_DIR, _tape_key(END_MS, HOURS, WARMUP, PXS) + '.npz'))['__ts__']
    i0 = int(np.searchsorted(ts, int(dt.datetime.fromisoformat(WIN_FROM)
                                     .replace(tzinfo=timezone.utc).timestamp() * 1000)))
    i1 = int(np.searchsorted(ts, int(dt.datetime.fromisoformat(WIN_TO)
                                     .replace(tzinfo=timezone.utc).timestamp() * 1000)))
    nbar = i1 - i0 + 1
    utcs = [dt.datetime.fromtimestamp(int(x) / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            for x in ts[i0:i1 + 1]]
    print(f'  window {WIN_FROM} -> {WIN_TO}   {nbar:,} bars   fences {HI:.0f}/{LO:.0f}', flush=True)

    tol_bars = WMT_LOOKBACK_S // GRID_S      # 24 bars at the 5-second grid, the signal bar included

    db.execute(DDL)
    have = {c['Field'] for c in db.execute('SHOW COLUMNS FROM wsf_bar_tf', fetch=True)}
    if 'wbt_wmt_tf_lo' not in have:
        db.execute('ALTER TABLE wsf_bar_tf ADD COLUMN wbt_wmt_tf_lo SMALLINT NOT NULL DEFAULT 1 '
                   'AFTER wbt_wmt_lookback_s')
        db.execute('ALTER TABLE wsf_bar_tf DROP INDEX uq_wbt, ADD UNIQUE KEY uq_wbt '
                   '(wbt_win_from, wbt_hi, wbt_lo, wbt_wmt_lookback_s, wbt_wmt_tf_lo, '
                   'wbt_utc, wbt_tf, wbt_dr)')
        print('  added wbt_wmt_tf_lo and rebuilt the unique key', flush=True)
    where = ('wbt_win_from=%s AND wbt_hi=%s AND wbt_lo=%s AND wbt_wmt_lookback_s=%s '
             'AND wbt_wmt_tf_lo=%s')
    kv = (WIN_FROM, HI, LO, WMT_LOOKBACK_S, WMT_TF_LO)
    n = db.execute('SELECT COUNT(*) c FROM wsf_bar_tf WHERE ' + where, kv, fetch=True)[0]['c']
    if n:
        print(f'  deleting {n:,} rows already stored at these knobs', flush=True)
        db.execute('DELETE FROM wsf_bar_tf WHERE ' + where, kv)

    total = 0
    for dr in DRS:
        # per timeframe: is Mage out of bounds on THIS side, how long since it last was, and
        # whether the 120-second tolerance still counts it as out
        oob, ago, tol = {}, {}, {}
        for tf in TFS:
            m = lines[('Mage', tf)]
            o = (m >= HI) if dr > 0 else (m <= LO)
            idx = np.arange(len(m))
            lasto = np.maximum.accumulate(np.where(o, idx, -1))
            ago[tf] = np.where(lasto < 0, -1, (idx - lasto) * GRID_S)[i0:i1 + 1]
            oob[tf] = o[i0:i1 + 1]
            tol[tf] = (ago[tf] >= 0) & (ago[tf] <= WMT_LOOKBACK_S)
        # the scan: ws1 upward, the first Mage the tolerance does NOT count as out
        wmt = np.zeros(nbar, np.int16)
        for tf in [t for t in TFS if t >= WMT_TF_LO][::-1]:
            wmt = np.where(~tol[tf], tf, wmt)
        for tf in TFS:
            r = lines[('r', tf)]
            rprev, rheld = travel(r, i0, i1)
            rv = r[i0:i1 + 1]
            rows = []
            for k in range(nbar):
                a, b = float(rv[k]), float(rprev[k])
                rows.append((WIN_FROM, HI, LO, WMT_LOOKBACK_S, WMT_TF_LO, utcs[k], tf, dr,
                             _f(lines[('Mage', tf)][i0 + k]), int(oob[tf][k]),
                             None if ago[tf][k] < 0 else int(ago[tf][k]), int(tol[tf][k]),
                             int(wmt[k]) or None,
                             _f(a), _f(b), int(rheld[k]),
                             'rising' if a > b else 'falling' if a < b else 'flat',
                             int(a > 50)))
            db.executemany(f'INSERT INTO wsf_bar_tf ({",".join(COLS)}) VALUES '
                           f'({",".join(["%s"] * len(COLS))})', rows)
            total += len(rows)
        d = 'upward' if dr > 0 else 'downward'
        print(f'  read {d:<8}: {nbar * len(TFS):,} rows over 8 timeframes', flush=True)

    print(f'\n  wsf_bar_tf : {total:,} rows', flush=True)
    db.disconnect()
    return 0


if __name__ == '__main__':
    sys.exit(main())
