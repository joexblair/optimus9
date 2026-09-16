#!/usr/bin/env python3
"""build_sneaky_trade_1 — bank every sneaky-trade-1 signal to the db. Joe 0916.

WHY A TABLE AND NOT A PICKLE
  o9-live's reconciliation compares two lists: what the mech said, and what actually filled. A
  pickle in a session scratchpad is not a list another session can read. Every row here carries a
  stable key (the test-point bar and the sourcing timeframe) so a fill can be matched to it.

EVERY ROW IS BANKED, INCLUDING THE ONES THE GATE DECLINES. `st1_taken` carries the verdict and
`st1_why` the reason. A reconciler needs to see a signal that should NOT have traded as much as
one that should — an extra fill is as much a break as a missing one.

THE PRODUCER IS optimus9/compute/sneaky_trade_1.py. This script only walks the tape and writes.
"""
import os, sys, time, numpy as np, pandas as pd, datetime as dt
from datetime import timezone
sys.path.insert(0, '/home/joe/thecodes')
import walk_mom_models as W
from optimus9.analysis.jig import Jig
from optimus9.compute.test_points import test_point, stretches
from optimus9.compute import sneaky_trade_1 as ST
from optimus9.compute.line_config import override, mech_lines
from optimus9.compute.momo_config import momo_bank
from optimus9.compute.momo_seam import seam_mask
from optimus9.compute.v3_config import v3_config
from optimus9.orchestration.rpl_cache import LINE_DIR, TAPE_DIR, _line_key, _tape_key
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

DDL = '''CREATE TABLE IF NOT EXISTS sneaky_trade_1 (
    st1_pk        BIGINT AUTO_INCREMENT PRIMARY KEY,
    st1_tp_bar    BIGINT NOT NULL,        -- the test-point bar index. half the key
    st1_src       TINYINT NOT NULL,       -- the sourcing timeframe. the other half
    st1_tp_utc    VARCHAR(19) NOT NULL,   -- the test-point, for a human and for a chart
    st1_dr        TINYINT NOT NULL,       -- the dr stretch. +1 -> LONG, -1 -> SHORT. Joe 0916
    st1_side      VARCHAR(5)  NOT NULL,   -- LONG | SHORT. Derived, stored so nobody re-derives it
    st1_hi        TINYINT NOT NULL,       -- the carrying timeframe
    st1_drop      DECIMAL(8,3),           -- the dr-signed Mage cascade drop at the test-point
    st1_wrong     TINYINT,                -- the cascade's crookedness, of 11 steps
    st1_fx_bar    BIGINT NOT NULL,        -- the carrying line's r-momo-fence exit
    st1_fx_utc    VARCHAR(19) NOT NULL,
    st1_open_bar  BIGINT NOT NULL,        -- the ws1x crossing. THE OPEN
    st1_open_utc  VARCHAR(19) NOT NULL,
    st1_open_px   DECIMAL(18,8) NOT NULL, -- pxs at the open bar
    st1_close_bar BIGINT NOT NULL,        -- the first gcws30mage-rev after the fence exit. THE CLOSE
    st1_close_utc VARCHAR(19) NOT NULL,
    st1_close_px  DECIMAL(18,8) NOT NULL,
    st1_mins      DECIMAL(10,2) NOT NULL, -- open to close
    st1_mae_pct   DECIMAL(8,4),           -- pxs at EVERY 5 s bar, in the dr direction
    st1_mfe_pct   DECIMAL(8,4),
    st1_move_pct  DECIMAL(8,4),           -- close to open, in the dr direction
    st1_taken     TINYINT NOT NULL,       -- the gate verdict
    st1_why       VARCHAR(32),            -- why it was declined
    st1_build     VARCHAR(19) NOT NULL,   -- when this row was written
    UNIQUE KEY uk_st1 (st1_tp_bar, st1_src)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4'''

TFS = [1, 2, 3, 4]
CFG = dict(momo_slope_min=0.05, momo_slack_ref=0.05, momo_r2_min=0.0, level_slack=40.0, momo_seam='skip_r2')
W0, W1 = '2026-06-10 00:00:00', '2026-09-05 00:00:00'
# THE GATE - Joe 0916, chosen on block 1 of three and held out on blocks 2 and 3
DROP_MIN, SRC_SET, HI_SET, NEED_CLIMB = 50.0, (1, 2), (4,), False

def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    db.execute(DDL)
    C = v3_config(db)
    sy = db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l FROM optimus9_system WHERE sys_pk=1', fetch=True)[0]
    spec = {}
    for g in mech_lines(db, 'wsf'):
        if g['role'] not in spec:
            _t, s_, m_ = g['override']; spec[g['role']] = (s_, m_)
    BK = {t: momo_bank(db, t, version=1) for t in range(1, 13)}
    MFR = float(C['momo_fence_r']); FENCE = (MFR, 100.0 - MFR)
    MAGE_FENCE = (W.MAGE_LO, W.MAGE_HI); LOOKBACK = int(C['tp_lookback_min']) * 12
    ts = np.load(os.path.join(TAPE_DIR, _tape_key(END_MS, HOURS, WARMUP, {'src': sy['s'], 'len': sy['l']}) + '.npz'))['__ts__']
    Ln = lambda tf, r_: np.load(os.path.join(LINE_DIR, _line_key(END_MS, HOURS, WARMUP, override(tf * 60, *spec[r_])) + '.npy'))
    R = {t: Ln(t, 'r') for t in range(1, 13)}
    M = {t: Ln(t, 'Mage') for t in range(1, 13)}
    X1 = Ln(1, 'x'); n = len(ts)
    ms = lambda s: int(dt.datetime.strptime(s, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc).timestamp() * 1000)
    us = lambda i: dt.datetime.fromtimestamp(int(ts[i]) / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    iw = int(np.searchsorted(ts, ms('2026-06-06 00:00:00')))
    DRs = W.dr_latch(M[1], Ln(13, 'm'), iw, n - 1)
    DRCH = np.flatnonzero(np.r_[False, (DRs[1:] != DRs[:-1]) & (DRs[1:] != 0)])
    SEAM = {t: seam_mask(ts, t) for t in range(1, 13)}
    with Jig(END_MS, hours=HOURS, warmup=WARMUP) as J:
        MR = J.causal.ws1mage_rev(sig_mage='gcws30Mage', g1='gcws30Mage')
        JT = np.asarray(J.ts, dtype=np.int64)
        PXS = pd.Series(np.asarray(J.px, float)).ffill().bfill().to_numpy()
    jrow = lambda b: int(np.searchsorted(JT, int(ts[b])))
    nflip = lambda k: (int(DRCH[np.searchsorted(DRCH, k, 'right')])
                       if np.searchsorted(DRCH, k, 'right') < len(DRCH) else n - 1)
    A0, A1 = int(np.searchsorted(ts, ms(W0))), int(np.searchsorted(ts, ms(W1)))
    STR = [s for s in stretches(DRs, iw, n) if s[1] > A0 and s[0] < A1]
    print('window %s -> %s   %d dr stretches' % (W0, W1, len(STR)), flush=True)
    rows = []; t0 = time.time(); stamp = dt.datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    for q, (F, Fp, dr) in enumerate(STR):
        pool = {}
        for t in TFS:
            rec = test_point(R[t], M[t], dr, F, Fp, FENCE, MAGE_FENCE, W.MAGE_DWELL, LOOKBACK)
            if rec is None: continue
            v = np.array([M[u][rec['bar']] for u in range(1, 13)], float)
            if not np.isfinite(v).all(): continue
            rec.update(tf=t, drop=float(dr * (v[0] - v[-1])),
                       wrong=int((dr * -np.diff(v) < 0).sum()), claims={})
            for up in range(t + 1, 5):
                ok, _ = W.momentum_true(R[up], BK[up], CFG, dr, rec['bar'], SEAM[up], up)
                rec['claims'][up] = int(ok)
            pool[t] = rec
        for t, rec in pool.items():
            if not (A0 <= rec['bar'] < A1): continue
            carry = [u for u, c in rec['claims'].items() if c]
            hi = max(carry) if carry else t
            mx = rec['bar'] if not carry else (pool[hi]['bar'] if hi in pool else None)
            if mx is None: continue
            sig = ST.signal(rec['bar'], dr, t, hi, mx, rec['drop'], X1, R[hi],
                            MR[dr]['sig_conf'], nflip(mx), FENCE, W.OOB_LO, W.OOB_HI,
                            DROP_MIN, SRC_SET, HI_SET, NEED_CLIMB)
            if sig is None: continue
            a, c = jrow(sig['ob']), jrow(sig['eb'])
            if c <= a: c = min(a + 1, len(PXS) - 1)
            P0, PX = float(PXS[a]), float(PXS[c])
            mv = (PXS[a:c + 1] - P0) / P0 * 100.0 * dr
            rows.append((sig['tp'], t, us(sig['tp']), dr, sig['side'], hi,
                         round(rec['drop'], 3), rec['wrong'],
                         sig['fx'], us(sig['fx']), sig['ob'], us(sig['ob']), round(P0, 8),
                         sig['eb'], us(sig['eb']), round(PX, 8),
                         round((ts[sig['eb']] - ts[sig['ob']]) / 6e4, 2),
                         round(float(-mv.min()), 4), round(float(mv.max()), 4), round(float(mv[-1]), 4),
                         1 if sig['taken'] else 0, sig['why'] or None, stamp))
        if q % 500 == 0: print('  %d/%d stretches  %d rows  %.0fs' % (q, len(STR), len(rows), time.time() - t0), flush=True)
    cols = ('st1_tp_bar,st1_src,st1_tp_utc,st1_dr,st1_side,st1_hi,st1_drop,st1_wrong,'
            'st1_fx_bar,st1_fx_utc,st1_open_bar,st1_open_utc,st1_open_px,'
            'st1_close_bar,st1_close_utc,st1_close_px,st1_mins,'
            'st1_mae_pct,st1_mfe_pct,st1_move_pct,st1_taken,st1_why,st1_build')
    ph = ','.join(['%s'] * 23)
    upd = ','.join('%s=VALUES(%s)' % (c, c) for c in cols.split(',') if c not in ('st1_tp_bar', 'st1_src'))
    db.executemany('INSERT INTO sneaky_trade_1 (%s) VALUES (%s) ON DUPLICATE KEY UPDATE %s' % (cols, ph, upd), rows)
    print('banked %d rows  (%d taken)  %.0fs' % (len(rows), sum(1 for r in rows if r[20] == 1), time.time() - t0), flush=True)
    db.disconnect()

if __name__ == '__main__':
    main()
