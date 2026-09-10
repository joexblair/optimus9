"""build_mage_boundary_signal — the Mage-crosses-boundary signal, banked. Joe 0910: "that's the
best outcome - bank it and add to the spec".

THE MECHANIC HAS NO NAME. Joe 0910: "this new mech doesn't have a specific job at present".
Every name in this file - the module, the table, the column prefix - is a PLACEHOLDER built from
Joe's own words. Rename on his word; do not coin one.

THE ROW. One row per (wsf_dtf_v3 row, mode). The wsf_dtf_v3 row is the HAND-OFF: its bar and its
dr. From that bar:

  1. walk forward, no cap, to the first bar ws1Mage's consecutive-oob run reaches DWELL bars.
     oob is the dr-side boundary - 85.0 at dr +1, 15.0 at dr -1.
  2. the SIGNAL is the first bar STRICTLY AFTER that where gcws{30|15}Mage crosses the same
     boundary in the dr direction. dr +1 the line crosses DOWN through 85.0, dr -1 it crosses UP
     through 15.0 - the settled x-cross direction rule, which is also the out-of-bounds ->
     in-bounds direction gcws30b uses in build_ws_fin and emit_ws_gated.
  3. no confirmation hold on that crossing. Joe was offered one 0910 and did not take it.

MODES. Joe 0910: "add a mode that uses gcws15 in place of gcws30, to make the signals more
surgical". `g30` uses gcws30Mage/x/m (30 s); `g15` uses gcws15Mage/x/m (15 s). ws1Mage and the
boundary are the same in both. The mode is in the knob string, so the two banks sit side by side.

NOT IN THIS MECHANIC, AND OPEN. Joe's first description of it had two more components:
  - ws1Mage reversing, _mage_rev(ws1Mage, 2) - 2 consecutive same-direction 5 s bars
  - a gcws15 x-cross-m inside a 15-second lookback of that reversal
Neither is in the construction Joe read and passed on 0910. They dropped out when the reporting
moved to listing crosses. They are NOT silently rejected - they are unresolved.

THE DWELL FLOOR IS MINE. Joe 0910: "ws1Mage needs to be oob for longer than the 03:29:20 dwell".
That dwell measured 2 bars = 10 s, so any run of 3 bars = 15 s or more satisfies him. 3 is the
SMALLEST satisfying value, picked by me. Any larger floor also satisfies his sentence and moves
the timestamps.

    python3 build_mage_boundary_signal.py            build and bank both modes
    python3 build_mage_boundary_signal.py --show     print what is banked
"""
import sys
import os
import time
import datetime as dt
from datetime import timezone

import numpy as np

from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP, line_names, overrides, PREFIXES
from optimus9.orchestration.rpl_cache import LINE_DIR, TAPE_DIR, _line_key, _tape_key

DWELL   = 3           # ws1Mage oob run, bars = 15 s. MINE - smallest run longer than 10 s
HOLD    = 0           # confirmation bars on the boundary crossing. Joe declined one 0910
MODES   = ['g30', 'g15']
LINEOF  = {'g30': 'gcws30', 'g15': 'gcws15'}
SRC_KNOBS = 'v3_sp10_sl0.4_f25.75_drws1Mage.ws13m_bv1'   # the wsf_dtf_v3 bank the hand-offs come from

DDL = '''CREATE TABLE IF NOT EXISTS mage_boundary_signal (
    mbs_pk        BIGINT AUTO_INCREMENT PRIMARY KEY,
    mbs_knobs     VARCHAR(160) NOT NULL,  -- every knob that moves a row. First part of the key
    mbs_mode      VARCHAR(8)   NOT NULL,  -- 'g30' = gcws30 lines, 'g15' = gcws15 lines
    mbs_handoff_utc DATETIME   NOT NULL,  -- the wsf_dtf_v3 row bar this walk starts from
    mbs_handoff_ms  BIGINT     NOT NULL,
    mbs_src_line  INT          NOT NULL,  -- wsf_dtf_v3.wdv_line, the timeframe in minutes
    mbs_dr        TINYINT      NOT NULL,  -- +1 or -1, from the source row
    mbs_dwell_utc DATETIME     NULL,      -- bar ws1Mage's oob run reaches DWELL. NULL = never
    mbs_dwell_min DOUBLE       NULL,      -- minutes from the hand-off bar
    mbs_sig_utc   DATETIME     NULL,      -- the boundary crossing. NULL = none to the cache end
    mbs_sig_min   DOUBLE       NULL,      -- minutes from the hand-off bar
    mbs_mage      DOUBLE       NULL,      -- gcws{30|15}Mage at the signal bar
    mbs_x         DOUBLE       NULL,      -- gcws{30|15}x   at the signal bar
    mbs_m         DOUBLE       NULL,      -- gcws{30|15}m   at the signal bar
    mbs_ws1mage   DOUBLE       NULL,      -- ws1Mage        at the signal bar
    mbs_n_cross   INT          NULL,      -- boundary crossings EITHER direction, hand-off to signal
    UNIQUE KEY u_row (mbs_knobs, mbs_handoff_utc, mbs_src_line),
    KEY k_ms (mbs_handoff_ms), KEY k_mode (mbs_mode, mbs_dr))'''

COLS = ['mbs_knobs', 'mbs_mode', 'mbs_handoff_utc', 'mbs_handoff_ms', 'mbs_src_line', 'mbs_dr',
        'mbs_dwell_utc', 'mbs_dwell_min', 'mbs_sig_utc', 'mbs_sig_min',
        'mbs_mage', 'mbs_x', 'mbs_m', 'mbs_ws1mage', 'mbs_n_cross']


def knobs(mode):
    return f'mb_{mode}_dw{DWELL}_hold{HOLD}_srcv3'


def runs_ge(mask, n):
    """Per bar: has `mask` been true for n consecutive bars ending here. Vectorised cross_wob run."""
    idx = np.arange(len(mask))
    reset = np.where(mask, 0, idx + 1)
    return (idx + 1) - np.maximum.accumulate(reset) >= n


def cross_idx(v, level, direction):
    """Bars where `v` crosses `level`. direction -1 = downward through it, +1 = upward."""
    d = v - level
    a, b = d[:-1], d[1:]
    ok = ~(np.isnan(a) | np.isnan(b))
    hit = ((a >= 0) & (b < 0)) if direction < 0 else ((a <= 0) & (b > 0))
    return np.flatnonzero(ok & hit) + 1


def main(show=False):
    t0 = time.time()
    db = DatabaseManager(**get_db_config()); db.connect()
    db.execute(DDL)
    if show:
        for r in db.execute('SELECT mbs_knobs k, COUNT(*) n, SUM(mbs_sig_utc IS NULL) miss, '
                            'MIN(mbs_handoff_utc) lo, MAX(mbs_handoff_utc) hi, AVG(mbs_sig_min) am '
                            'FROM mage_boundary_signal GROUP BY mbs_knobs ORDER BY k', fetch=True):
            print(f"  {r['k']:<28}{r['n']:>6} rows  {r['miss']} without a signal  "
                  f"{r['lo']} -> {r['hi']}  mean {float(r['am'] or 0):.2f} min", flush=True)
        db.disconnect(); return 0

    sy = db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l, hi_boundary hi, '
                    'lo_boundary lo FROM optimus9_system WHERE sys_pk=1', fetch=True)[0]
    HI, LO = float(sy['hi']), float(sy['lo'])
    OVR = overrides(db, line_names(db, PREFIXES))
    src = db.execute('SELECT wdv_utc, wdv_ms, wdv_line, wdv_dr FROM wsf_dtf_v3 WHERE wdv_knobs=%s '
                     'ORDER BY wdv_ms, wdv_line', (SRC_KNOBS,), fetch=True)

    ts = np.load(os.path.join(TAPE_DIR, _tape_key(END_MS, HOURS, WARMUP,
                 {'src': sy['s'], 'len': sy['l']}) + '.npz'))['__ts__']
    N = lambda n: np.load(os.path.join(LINE_DIR, _line_key(END_MS, HOURS, WARMUP, OVR[n]) + '.npy'))
    G1 = N('ws1Mage')
    u = lambda i: dt.datetime.fromtimestamp(int(ts[i]) / 1000, tz=timezone.utc)

    # ws1Mage oob dwell, per side. The run counts through bars before the hand-off - a line already
    # oob on arrival can satisfy the floor at the hand-off bar itself. THAT IS MINE.
    dwell_ok = {+1: np.flatnonzero(runs_ge(G1 >= HI, DWELL)),
                -1: np.flatnonzero(runs_ge(G1 <= LO, DWELL))}

    print(f'  source {SRC_KNOBS}: {len(src):,} hand-offs', flush=True)
    print(f'  ws1Mage oob dwell floor {DWELL} bars = {DWELL * 5} s   boundary {HI:g} / {LO:g}   '
          f'crossing hold {HOLD}', flush=True)

    for mode in MODES:
        g = LINEOF[mode]
        MA, XV, MV = N(f'{g}Mage'), N(f'{g}x'), N(f'{g}m')
        # the dr-direction crossing, and every crossing either way (for the n_cross count)
        sig_ix = {+1: cross_idx(MA, HI, -1), -1: cross_idx(MA, LO, +1)}
        any_ix = {+1: np.sort(np.concatenate([cross_idx(MA, HI, -1), cross_idx(MA, HI, +1)])),
                  -1: np.sort(np.concatenate([cross_idx(MA, LO, +1), cross_idx(MA, LO, -1)]))}
        K = knobs(mode)
        out = []
        for r in src:
            dr = int(r['wdv_dr'])
            if dr == 0:
                continue
            i0 = int(np.searchsorted(ts, int(r['wdv_ms'])))
            dw = dwell_ok[dr]
            p = int(np.searchsorted(dw, i0))
            ib = int(dw[p]) if p < len(dw) else None
            sg = None
            if ib is not None:
                s = sig_ix[dr]
                q = int(np.searchsorted(s, ib, side='right'))     # STRICTLY after the dwell bar
                sg = int(s[q]) if q < len(s) else None
            nc = None
            if sg is not None:
                a = any_ix[dr]
                nc = int(np.searchsorted(a, sg, side='right') - np.searchsorted(a, i0, side='right'))
            out.append((K, mode, r['wdv_utc'], int(r['wdv_ms']), int(r['wdv_line']), dr,
                        None if ib is None else u(ib).strftime('%Y-%m-%d %H:%M:%S'),
                        None if ib is None else round((int(ts[ib]) - int(r['wdv_ms'])) / 60000, 4),
                        None if sg is None else u(sg).strftime('%Y-%m-%d %H:%M:%S'),
                        None if sg is None else round((int(ts[sg]) - int(r['wdv_ms'])) / 60000, 4),
                        None if sg is None else round(float(MA[sg]), 2),
                        None if sg is None else round(float(XV[sg]), 2),
                        None if sg is None else round(float(MV[sg]), 2),
                        None if sg is None else round(float(G1[sg]), 2), nc))

        n = db.execute('SELECT COUNT(*) c FROM mage_boundary_signal WHERE mbs_knobs=%s',
                       (K,), fetch=True)[0]['c']
        if n:
            print(f'  {mode}: {n:,} rows already banked at {K} - nothing written', flush=True)
        else:
            db.executemany(f"INSERT INTO mage_boundary_signal ({','.join(COLS)}) "
                           f"VALUES ({','.join(['%s'] * len(COLS))})", out)
            print(f'  {mode}: banked {len(out):,} rows at {K}', flush=True)
    db.disconnect()
    print(f'  {time.time() - t0:.0f}s', flush=True)
    return 0


if __name__ == '__main__':
    sys.exit(main('--show' in sys.argv))
