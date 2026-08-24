"""build_wsf_marker_snapshot — the Mage and r lines behind every one of Joe's 121 tagged markers.

Joe 0820: "create snapshots at each of the csv d and f markers, and compare the d snapshots against
the f snapshots to find the differences. when you boil that data down to a model, we can then look
at how to integrate the other mechanics".

THE STANCE. Nothing here reads domTF, wsf-exhaust, an x-cross, or a trade signal. Joe 0820: "I can
only be accurate about the data in the csv file. anything beyond that (domTF, wsf-exhausted, x-cross
trade signals) are outside of my view." The only ground truth is the 121 markers and their f or d
tag; everything on a row is measured at or before that marker's bar.

WHAT IS ON EVERY ROW. One row per (marker, offset, timeframe).
  the Mage value and the r value at that bar
  whether Mage is out of bounds ON THE MARKER'S OWN SIDE   - Joe's mage-weakness scan reads from this
  whether r is in bounds                                   - Joe 0820: "r-weakness is per-tf. if a
                                                             TF's r line is IB, then tag that TF as weak"
  the momentum verdict on the r line, read in the marker's own side - Joe 0820: "do I read momentum
                                                             in the marker's own side" / "yes", and
                                                             "r is the only line that uses momentum"

WHY THE LINE CACHE AND NOT ws_line_bar. ws_line_bar starts at 08-04 00:00:00, which puts a floor
1,600 s short of the deepest rung for the first two markers. The cached line arrays run from
2026-05-07 00:00:00 - 89.0 days before the window - so every marker carries a full ladder and no
cell is ever empty. Joe 0820 caught the difference between row coverage and warmup.

THE LADDER is Joe's call delegated to me, 0820: "your model, your call ... if you want to add more
sampling, then you should add more sampling. do a thorough job". The dense end is his own side-idea
grid (120 / 240 / 360 s). The deep end is 2,100 s = 35 minutes = his measured ws1 r cycle:
"a ws1 r cycle lasts ~35 minutes, so there's considerable data to be captured". It is in the unique
key, so a second ladder lands alongside instead of on top.

NOTHING IS DROPPED. No marker, no rung, no timeframe. 121 x 15 x 8 = 14,520 rows.
"""
import sys
import csv
import os
import datetime as dt
from datetime import timezone

import numpy as np

from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.compute.line_config import mech_lines
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP
from optimus9.orchestration.rpl_cache import LINE_DIR, TAPE_DIR, _line_key, _tape_key
from optimus9.compute import momo_gated as MG
from optimus9.compute.momo_gated import momo_g_why, momo_window
from optimus9.compute import momo_core as MC
import build_momo_landed as B

WIN_FROM = '2026-08-04 00:00:00'
TAGS_CSV = '/home/joe/thecodes/transfer/260819_wsf_model_training_timestamps.csv'
TFS      = list(range(1, 9))      # ws1 to ws8. Both Mage and r at each
GRID_S   = 5                      # the bar grid, seconds
FIXED    = 21
# MOMO_FIXED_SAMPLES. Joe 0820: "set it to 21 (both in your caller, and the code's default)".
# 21 is the shape Joe settled 0814 - docs/domTF-finisher_spec.md M10, "should it be 21 samples per
# line?" / "bank the spec and code". Every line's straight-line fit uses 21 points across its own
# window, so the gap scales with the timeframe: 10 s at ws1, 96 s at ws8.
# It is ASSIGNED below and never left to the module default. The first run of this script stored 21
# in the column while running at the then-default of 0, and that divergence was the defect.

# seconds before the marker. 0 is the marker bar itself - Joe 0820: "absolutely - I can't see how
# the model would be complete without it".
LADDER = [0, 30, 60, 120, 180, 240, 300, 360, 480, 600, 900, 1200, 1500, 1800, 2100]

DDL = '''CREATE TABLE IF NOT EXISTS wsf_marker_snapshot (
    wms_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    -- THE KNOBS. All in the unique key: change one and every row changes.
    wms_win_from      DATETIME     NOT NULL,  -- scope. 08-04, the CSV's own range
    wms_hi            DOUBLE       NOT NULL,  -- upper fence, 85, from mech_line_config
    wms_lo            DOUBLE       NOT NULL,  -- lower fence, 15, from mech_line_config
    wms_k_window      SMALLINT     NOT NULL,  -- K_WINDOW 4. momentum window = K_WINDOW x tf, minutes
    wms_fixed_samples SMALLINT     NOT NULL,  -- MOMO_FIXED_SAMPLES. 0 = sample count comes from
    --   the window; a positive value fixes the count and scales the gap instead
    wms_ladder        VARCHAR(128) NOT NULL,  -- the offset set, comma separated seconds
    -- THE MARKER. One of Joe's 121 hand-tagged rows.
    wms_marker        DATETIME     NOT NULL,  -- the g30_marker from the CSV
    wms_tag           CHAR(1)      NOT NULL,  -- 'f' fire or 'd' delay, Joe's tag
    wms_side          TINYINT      NOT NULL,  -- the marker's own side, from ws_fin_9of12
    -- THE RUNG.
    wms_offset_s      INT          NOT NULL,  -- seconds before the marker. 0 = the marker bar
    wms_bar_utc       DATETIME     NOT NULL,  -- the bar this row measures
    wms_tf            SMALLINT     NOT NULL,  -- timeframe 1 to 8
    -- WHAT IS MEASURED AT THAT BAR.
    wms_mage          DOUBLE,                 -- ws{tf}Mage value, 0 to 100
    wms_mage_oob      TINYINT,                -- 1 = Mage out of bounds ON THE MARKER'S SIDE
    wms_r             DOUBLE,                 -- ws{tf}r value, 0 to 100
    wms_r_ib          TINYINT,                -- 1 = r inside both fences. Joe's r-weakness tag
    wms_r_dist        DOUBLE,                 -- points this r line still has to travel to reach its
    --   fence, on the MARKER'S OWN SIDE (85 when the marker reads up, 15 when it reads down).
    --   Negative means the line is already past its fence. Joe 0820: "add it into the fold".
    wms_momo          VARCHAR(8),             -- momentum verdict on ws{tf}r, read in the marker's side
    UNIQUE KEY uq_wms (wms_win_from, wms_hi, wms_lo, wms_k_window, wms_fixed_samples,
                       wms_ladder, wms_marker, wms_offset_s, wms_tf),
    KEY k_tag (wms_tag), KEY k_rung (wms_offset_s, wms_tf), KEY k_momo (wms_momo))'''

COLS = ['wms_win_from', 'wms_hi', 'wms_lo', 'wms_k_window', 'wms_fixed_samples', 'wms_ladder',
        'wms_marker', 'wms_tag', 'wms_side', 'wms_offset_s', 'wms_bar_utc', 'wms_tf',
        'wms_mage', 'wms_mage_oob', 'wms_r', 'wms_r_ib', 'wms_r_dist', 'wms_momo']


def _f(x):
    """None for a value MySQL cannot store as a DOUBLE."""
    if x is None:
        return None
    x = float(x)
    return x if np.isfinite(x) else None


def read_tags():
    """Joe's CSV -> [(marker datetime, 'f' or 'd')]. The only ground truth on this path."""
    out = []
    with open(TAGS_CSV, encoding='utf-8-sig') as f:
        for row in csv.reader(f):
            if not row or row[0].startswith('g30'):
                continue
            d, t = row[0].split()
            out.append((dt.datetime(2026, int(d[:2]), int(d[2:]), *map(int, t.split(':')),
                                    tzinfo=timezone.utc), row[1].strip()))
    return sorted(out)


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    sysr = db.execute('SELECT pxsmooth_dema_src src, pxsmooth_dema_len len '
                      'FROM optimus9_system WHERE sys_pk=1', fetch=True)[0]
    PXS = {'src': sysr['src'], 'len': sysr['len']}

    MG.MOMO_FIXED_SAMPLES = FIXED     # ASSIGNED, not inherited. Joe 0820
    tags = read_tags()
    nf = sum(1 for _, t in tags if t == 'f')
    print(f'  {len(tags)} markers from the CSV: {nf} tagged f, {len(tags) - nf} tagged d', flush=True)

    # the marker's own side, from ws_fin_9of12. Joe 0820: read momentum in the marker's own side.
    side = {str(r['u']): int(r['s']) for r in db.execute(
        "SELECT wsf_utc u, wsf_side s FROM ws_fin_9of12 WHERE wsf_win_from=%s "
        "AND wsf_ho_rule='median' AND wsf_line_hcap='ws1b:1'", (WIN_FROM,), fetch=True)}
    missing = [m for m, _ in tags if m.strftime('%Y-%m-%d %H:%M:%S') not in side]
    if missing:
        print(f'  STOPPING: {len(missing)} markers have no side in ws_fin_9of12, first '
              f'{missing[0]}', flush=True)
        return 1

    # the line arrays. mech_line_config is the config source - one row per role, spread over the band.
    lines = {}
    for g in mech_lines(db, 'wsf'):
        tf = g['tf_seconds'] // 60
        if g['role'] in ('Mage', 'r') and tf in TFS:
            lines[(g['role'], tf)] = np.load(
                os.path.join(LINE_DIR, _line_key(END_MS, HOURS, WARMUP, g['override']) + '.npy'))
            HI, LO = g['hi'], g['lo']
    print(f'  {len(lines)} line arrays loaded, {len(next(iter(lines.values()))):,} bars each   '
          f'fences {HI:.0f} / {LO:.0f}', flush=True)

    ts = np.load(os.path.join(TAPE_DIR, _tape_key(END_MS, HOURS, WARMUP, PXS) + '.npz'))['__ts__']
    idx = {}
    for m, _ in tags:
        idx[m] = int(np.searchsorted(ts, int(m.timestamp() * 1000)))
    deepest = min(idx.values()) - LADDER[-1] // GRID_S
    print(f'  tape {len(ts):,} bars.  deepest bar any rung reaches: index {deepest:,}  '
          f'({"inside the tape" if deepest >= 0 else "OFF THE FRONT - STOPPING"})', flush=True)
    if deepest < 0:
        return 1

    lad = ','.join(str(x) for x in LADDER)
    db.execute(DDL)
    have = {c['Field'] for c in db.execute('SHOW COLUMNS FROM wsf_marker_snapshot', fetch=True)}
    if 'wms_r_dist' not in have:      # the table predates the column. Joe 0820
        db.execute('ALTER TABLE wsf_marker_snapshot ADD COLUMN wms_r_dist DOUBLE AFTER wms_r_ib')
        print('  added column wms_r_dist to the existing table', flush=True)
    where = ('wms_win_from=%s AND wms_hi=%s AND wms_lo=%s AND wms_k_window=%s '
             'AND wms_fixed_samples=%s AND wms_ladder=%s')
    kv = (WIN_FROM, HI, LO, B.K_WINDOW, FIXED, lad)
    n = db.execute('SELECT COUNT(*) c FROM wsf_marker_snapshot WHERE ' + where,
                   kv, fetch=True)[0]['c']
    if n:
        print(f'  deleting {n:,} rows already stored at these knobs', flush=True)
        db.execute('DELETE FROM wsf_marker_snapshot WHERE ' + where, kv)

    def u(ms):
        return dt.datetime.fromtimestamp(int(ms) / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    total = 0
    for tf in TFS:
        mage, r = lines[('Mage', tf)], lines[('r', tf)]
        rows = []
        with momo_window(B.K_WINDOW * tf):
            for m, tag in tags:
                dr = side[m.strftime('%Y-%m-%d %H:%M:%S')]
                i_m = idx[m]
                for off in LADDER:
                    i = i_m - off // GRID_S
                    mv, rv = float(mage[i]), float(r[i])
                    _, _, f = momo_g_why(r, dr, i, quad=True)
                    rows.append((
                        WIN_FROM, HI, LO, B.K_WINDOW, FIXED, lad,
                        m.strftime('%Y-%m-%d %H:%M:%S'), tag, dr, off, u(ts[i]), tf,
                        _f(mv),
                        None if not np.isfinite(mv) else int(mv >= HI if dr > 0 else mv <= LO),
                        _f(rv),
                        None if not np.isfinite(rv) else int(LO < rv < HI),
                        _f((HI - rv) if dr > 0 else (rv - LO)),
                        MC.verdict(f)[0]))
        db.executemany(f'INSERT INTO wsf_marker_snapshot ({",".join(COLS)}) VALUES '
                       f'({",".join(["%s"] * len(COLS))})', rows)
        total += len(rows)
        print(f'  ws{tf}Mage and ws{tf}r : {len(rows):,} rows  '
              f'({len(tags)} markers x {len(LADDER)} rungs)', flush=True)

    print(f'\n  wsf_marker_snapshot : {total:,} rows written', flush=True)
    db.disconnect()
    return 0


if __name__ == '__main__':
    sys.exit(main())
