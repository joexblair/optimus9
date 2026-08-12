#!/usr/bin/env python3
"""big bar detection — EXPERIMENTAL. Joe 0810.

Joe's spec, verbatim:
    - this highlights the need for a "big bar detection" mechanic (EXPERIMENTAL)
    -- the mechanic's purpose is to fire a signal immediately at the completion of a large price
       move. it has 2 conditions:
    --- 1) price moves more than 1% in the direction of our bias, inside of {knob:180} seconds,
           FOLLOWED BY ws1x crossing (under for bull bias/SHORT trade, or over for LONG) ws1b
    --- 2) a momentum tagged line is inside the fence, but close enough to the fence's edge so that
           a 1% price movement would spike the momentum line out of the fence
           {knob: fence edge minus 2 (eg 78/22) }
    run this across a small window, 08-04 12:00 to 22:00

The indentation is logical: 1) and 2) are siblings under "it has 2 conditions", so both must hold.

MY READINGS — not stated by Joe, flagged so they can be overruled:

  BIAS = the momentum tag's `dr`. Condition 2 is about "a momentum tagged line", and for a 1% move
  to spike that line OUT of the fence it has to run in the tag's own direction. So one `dr` serves
  both conditions. dr +1 = bull bias -> SHORT; dr -1 = bear bias -> LONG, per Joe's parenthesis.

  THE 1% IS EXTREMUM-TO-CURRENT inside the trailing 180 s. dr +1: (px - min(window)) / min.
  dr -1: (max(window) - px) / max. The window ENDS at the current bar, so it is causal, and it
  catches a move that completed in 40 s as well as one that took the full 180 s. Endpoint-to-
  endpoint would miss the fast ones.

  "FOLLOWED BY" = the ws1x/ws1b cross must land on a bar where condition 1 is STILL true. Joe gave
  no separate window for the gap, and inventing a second knob is worse than reusing the 180 s.

  ROW UNIT = one row per (cross bar x qualifying tagged line), same unit as momo_landed.

TAG STATE follows the walk's CURRENT clear rule. 0810 first run: tags cleared on every
momo_landed. 0810 second run: Joe replaced that with "highest TF momentum line curling against
bias" (clear_on='hi_tf_counter_curl'), so the clear bars are read from momo_landed_bar.mlb_cleared
and the membership is checked against the banked mlb_live_tfs. `dr` still comes from the most
recent marker that tagged each line.

    python3 build_big_bar_detection.py
"""
import sys, datetime as dt
from datetime import timezone

import numpy as np

from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.compute.line_config import LineStore, KLine, override
from optimus9.orchestration.rpl_cache import cache_jig_perline
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP
import build_momo_landed as B

CLEAR_ON = B.CLEAR_ON             # which momo_landed clear rule the tag state follows

MOVE_PCT = 1.0                    # KNOB: "price moves more than 1%"
MOVE_SEC = 180                    # KNOB {180}: the window the move must complete inside
EDGE_SLACK = 2                    # KNOB "fence edge minus 2 (eg 78/22)"
FENCE = B.FENCE                   # 20 -> fence [20, 80]
XLINE, BLINE = 'ws1x', 'ws1b'     # the cross pair
W_LO = dt.datetime(2026, 8, 4, 12, 0, tzinfo=timezone.utc)
W_HI = dt.datetime(2026, 8, 9, 12, 0, tzinfo=timezone.utc)   # full 120 h, Joe 0810

HI_EDGE, LO_EDGE = 100 - FENCE, FENCE                  # 80 / 20
HI_BAND, LO_BAND = HI_EDGE - EDGE_SLACK, LO_EDGE + EDGE_SLACK   # 78 / 22

DDL = '''CREATE TABLE IF NOT EXISTS big_bar_detection (
    bbd_pk       BIGINT AUTO_INCREMENT PRIMARY KEY,
    bbd_move_pct DOUBLE NOT NULL,        -- KNOB 1.0 %
    bbd_move_sec SMALLINT NOT NULL,      -- KNOB 180 s = 36 bars at the 5 s grid
    bbd_slack    SMALLINT NOT NULL,      -- KNOB 2 -> band [78,80) hi, (20,22] lo
    bbd_fence    SMALLINT NOT NULL,      -- 20 -> fence [20, 80]
    bbd_ms       BIGINT NOT NULL, bbd_utc VARCHAR(19),   -- the ws1x/ws1b cross bar. the signal
    bbd_tf       SMALLINT NOT NULL,      -- the tagged ws{TF}r that satisfied condition 2
    bbd_dr       TINYINT NOT NULL,       -- the tag's side. +1 bull bias, -1 bear bias
    bbd_trade    VARCHAR(5) NOT NULL,    -- SHORT for dr +1, LONG for dr -1. Joe's parenthesis
    bbd_marker_ms BIGINT, bbd_marker_utc VARCHAR(19),    -- the ws1 marker that created the tag
    bbd_move_ms  BIGINT, bbd_move_utc VARCHAR(19),       -- first bar condition 1 went true
    bbd_gap_sec  DOUBLE,                 -- move -> cross, seconds
    bbd_pct      DOUBLE,                 -- the realised move at the cross bar, %
    bbd_px_from  DOUBLE, bbd_px_at DOUBLE,
    bbd_r        DOUBLE,                 -- ws{TF}r at the cross bar
    bbd_ws1x     DOUBLE, bbd_ws1b DOUBLE,
    UNIQUE KEY uq_bbd (bbd_move_pct, bbd_move_sec, bbd_slack, bbd_ms, bbd_tf),
    KEY (bbd_ms), KEY (bbd_tf), KEY (bbd_dr))'''

COLS = ('bbd_move_pct,bbd_move_sec,bbd_slack,bbd_fence,bbd_ms,bbd_utc,bbd_tf,bbd_dr,bbd_trade,'
        'bbd_marker_ms,bbd_marker_utc,bbd_move_ms,bbd_move_utc,bbd_gap_sec,bbd_pct,'
        'bbd_px_from,bbd_px_at,bbd_r,bbd_ws1x,bbd_ws1b')


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    sysr = db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l FROM optimus9_system '
                      'WHERE sys_pk=1', fetch=True)[0]
    ls = LineStore(db)
    ovr = {n: (*ls.resolve(n), ls.value_mode(n)) for n in (XLINE, BLINE, 'ws1Mage')}
    for tf in B.TFS:
        ovr[f'r{tf}'] = override(tf * 60, KLine(**B.R_SPEC), 'emerging')
    print(f'loading {len(ovr)} lines ...', flush=True)
    J = cache_jig_perline(END_MS, HOURS, WARMUP, ovr,
                          pxs_cfg={'src': sysr['s'], 'len': sysr['l']}, rebuild=False)
    ts = np.asarray(J.ts)
    pxs = np.asarray(J.pxs, float)
    X = np.asarray(J.W.line(XLINE), float)
    Bl = np.asarray(J.W.line(BLINE), float)
    R = {tf: np.asarray(J.W.line(f'r{tf}'), float) for tf in B.TFS}
    u = B.u

    i0 = int(np.searchsorted(ts, int(W_LO.timestamp() * 1000)))
    i1 = int(np.searchsorted(ts, int(W_HI.timestamp() * 1000)))
    nb = MOVE_SEC // 5                                   # 36 bars
    print(f'window {u(ts[i0])} -> {u(ts[i1 - 1])}   {i1 - i0:,} bars   move {MOVE_PCT}% in '
          f'{MOVE_SEC}s ({nb} bars)   band [{HI_BAND},{HI_EDGE}) hi / ({LO_EDGE},{LO_BAND}] lo',
          flush=True)

    # --- tag state, exactly as momo_landed holds it: created at a marker, ALL cleared on a landing
    mk = db.execute("SELECT mlb_ms m, mlb_marker_side s, mlb_tag_tfs t FROM momo_landed_bar "
                    "WHERE mlb_marker=1 ORDER BY mlb_ms", fetch=True)
    MK = {int(x['m']): (int(x['s']),
                        {int(p.split(':')[0]) for p in x['t'].split(',')} if x['t'] else set())
          for x in mk}
    LD = {int(x['m']) for x in db.execute(
        'SELECT mlb_ms m FROM momo_landed_bar WHERE mlb_fence=%s AND mlb_xwob=%s AND mlb_kwindow=%s '
        'AND mlb_clear=%s AND mlb_cleared=1',
        (B.FENCE, B.XWOB, B.K_WINDOW, CLEAR_ON), fetch=True)}
    # cross-check the reconstruction against the banked per-bar live set
    BANK = {int(x['mlb_ms']): (x['mlb_live_tfs'] or '') for x in db.execute(
        'SELECT mlb_ms, mlb_live_tfs FROM momo_landed_bar WHERE mlb_fence=%s AND mlb_xwob=%s '
        'AND mlb_kwindow=%s AND mlb_clear=%s', (B.FENCE, B.XWOB, B.K_WINDOW, CLEAR_ON), fetch=True)}
    mismatch = 0

    live = {}                       # tf -> (dr, marker_ms)
    rows, per_bar = [], {}
    n_c1a = n_c1b = n_c1 = n_live = n_c2 = 0
    for i in range(i0, i1):
        t = int(ts[i])
        if t in MK:
            dr, tfs = MK[t]
            for tf in tfs:
                live[tf] = (dr, t)
        if t in BANK and ','.join(str(x) for x in sorted(live)) != BANK[t]:
            mismatch += 1
        # --- condition 1a: the 1% move, extremum-to-current inside the trailing 180 s
        w = pxs[max(0, i - nb + 1):i + 1]
        w = w[np.isfinite(w)]
        up = dn = 0.0
        if len(w) and np.isfinite(pxs[i]):
            lo, hi = w.min(), w.max()
            up = (pxs[i] - lo) / lo * 100.0 if lo > 0 else 0.0
            dn = (hi - pxs[i]) / hi * 100.0 if hi > 0 else 0.0
        # --- condition 1b: the ws1x / ws1b cross on THIS bar
        if i > 0 and np.isfinite(X[i]) and np.isfinite(Bl[i]) \
                and np.isfinite(X[i - 1]) and np.isfinite(Bl[i - 1]):
            x_under = X[i] < Bl[i] and X[i - 1] >= Bl[i - 1]     # bull bias -> SHORT
            x_over = X[i] > Bl[i] and X[i - 1] <= Bl[i - 1]      # bear bias -> LONG
        else:
            x_under = x_over = False

        if up > MOVE_PCT or dn > MOVE_PCT: n_c1a += 1
        if x_under or x_over: n_c1b += 1
        if (up > MOVE_PCT and x_under) or (dn > MOVE_PCT and x_over): n_c1 += 1
        if live: n_live += 1
        if any(np.isfinite(R[tf][i]) and ((d > 0 and HI_BAND <= R[tf][i] < HI_EDGE)
                                          or (d < 0 and LO_EDGE < R[tf][i] <= LO_BAND))
               for tf, (d, _m) in live.items()): n_c2 += 1
        for tf, (dr, mms) in sorted(live.items()):
            moved = up if dr > 0 else dn
            if moved <= MOVE_PCT:
                continue
            if not (x_under if dr > 0 else x_over):
                continue
            # --- condition 2: the tagged line is INSIDE the fence, within EDGE_SLACK of its edge
            v = R[tf][i]
            if not np.isfinite(v):
                continue
            if dr > 0 and not (HI_BAND <= v < HI_EDGE):
                continue
            if dr < 0 and not (LO_EDGE < v <= LO_BAND):
                continue
            # first bar in the trailing window where condition 1a was already true
            j = i
            while j - 1 >= max(i0, i - nb + 1):
                ww = pxs[max(0, j - 1 - nb + 1):j]
                ww = ww[np.isfinite(ww)]
                if not len(ww):
                    break
                m = ((pxs[j - 1] - ww.min()) / ww.min() if dr > 0
                     else (ww.max() - pxs[j - 1]) / ww.max()) * 100.0
                if m <= MOVE_PCT:
                    break
                j -= 1
            src = w.min() if dr > 0 else w.max()
            rows.append((MOVE_PCT, MOVE_SEC, EDGE_SLACK, FENCE, t, u(t), tf, dr,
                         'SHORT' if dr > 0 else 'LONG', mms, u(mms), int(ts[j]), u(ts[j]),
                         (t - int(ts[j])) / 1000.0, float(moved), float(src), float(pxs[i]),
                         float(v), float(X[i]), float(Bl[i])))
            per_bar.setdefault(t, []).append(tf)
        if t in LD:
            live.clear()

    db.execute(DDL)
    db.execute('DELETE FROM big_bar_detection WHERE bbd_move_pct=%s AND bbd_move_sec=%s '
               'AND bbd_slack=%s', (MOVE_PCT, MOVE_SEC, EDGE_SLACK))
    if rows:
        db.executemany(f'INSERT INTO big_bar_detection ({COLS}) VALUES '
                       f'({",".join(["%s"] * len(COLS.split(",")))})', rows)
    print(f'tag state: clear_on={CLEAR_ON}, {len(LD)} clear bars in the tape; '
          f'reconstruction mismatches vs mlb_live_tfs: {mismatch}', flush=True)
    nn = i1 - i0
    print(f'C1a 1% in {MOVE_SEC}s        {n_c1a:>7,} bars  {100*n_c1a/nn:5.2f}%')
    print(f'C1b ws1x x ws1b        {n_c1b:>7,} bars  {100*n_c1b/nn:5.2f}%')
    print(f'C1a AND C1b            {n_c1:>7,} bars  {100*n_c1/nn:5.2f}%')
    print(f'    any live tag       {n_live:>7,} bars  {100*n_live/nn:5.2f}%')
    print(f'C2  a live tag in band {n_c2:>7,} bars  {100*n_c2/nn:5.2f}%')
    print(f'big_bar_detection : {len(rows)} rows on {len(per_bar)} distinct signal bars', flush=True)
    for t in sorted(per_bar):
        print(f'   {u(t)}  ws{"r, ws".join(str(x) for x in sorted(per_bar[t]))}r')
    db.disconnect()


if __name__ == '__main__':
    sys.exit(main())
