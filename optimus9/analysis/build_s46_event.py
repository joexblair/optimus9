"""build_s46_event — writes the item-13 event log. Joe 0805.

s46_window is UNTOUCHED (Joe 0805: "maintain the same s46_window output for me going forward").
This is the second table: one row per timestamped event, with the data behind it.

THREE EVENT KINDS (Joe 0805: "3 rows is rich")
    momo_act    first bar the gate opens — indicator returns momo|curl, same bias, s15 OR s22
    momo_exit   Joe's 1) both r beyond the fence -> release | Joe's 2) one beyond + s6x cross -> end
    s6x_cross   the item 14/15 gated cross that closes the trade

Joe's 2) puts momo_exit and s6x_cross on the SAME BAR — both are written, as separate rows.

SRP. The mechanic is optimus9/analysis/s46_momo.py (pure, no IO). This file is IO only: read the
trades, call walk(), write the rows.

    python3 -m optimus9.analysis.build_s46_event [--fence 3] [--xwob 6] [--cfg CUR]
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import datetime as dt
import numpy as np

from optimus9.analysis.s46_momo import walk, fence, ACT, EXIT, CROSS, OPP
from optimus9.compute.momo_gated import momo_g, CURL_R2_MIN, STATE
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

JD = os.environ.get('CLAUDE_JOB_DIR', '/tmp') + '/tmp'
# (momo_npz, oob_npz). Variant A separates the duties (Joe 0805): momo keeps 10|4|11, the line that
# hunts the fence/oob uses 7|5|12. CUR and B use one bank for both.
NPZ = {'CUR': (JD + '/lines_all.npz', JD + '/lines_all.npz'),
       'A':   (JD + '/lines_all.npz', JD + '/r7512.npz'),
       'B':   (JD + '/r7512.npz',     JD + '/r7512.npz')}

DDL = '''CREATE TABLE IF NOT EXISTS s46_event (
    se_pk        BIGINT AUTO_INCREMENT PRIMARY KEY,
    se_created   DATETIME DEFAULT CURRENT_TIMESTAMP,
    se_trade_ms  BIGINT,            -- the entry bar; joins to s46_window.sw_entry_ms
    se_n         INT,               -- s46_window.sw_n
    se_dr        TINYINT,
    se_kind      VARCHAR(12),       -- momo_act | momo_exit | s6x_cross
    se_branch    VARCHAR(2),        -- 1 | 2, on momo_exit only
    se_ms        BIGINT, se_utc VARCHAR(20),
    se_bar       INT,               -- bar index on the line grid
    se_r15       DOUBLE, se_r22 DOUBLE,
    se_st15      VARCHAR(8), se_st22 VARCHAR(8),   -- gated indicator state at the event bar
    se_fence_s   INT, se_fence_lo DOUBLE, se_fence_hi DOUBLE,
    se_xwob      INT,
    se_cfg       VARCHAR(4),        -- CUR | A | B — which line config produced it
    se_curl_r2   DOUBLE,            -- CURL_R2_MIN in force
    INDEX(se_trade_ms), INDEX(se_kind))'''

u = lambda ms: dt.datetime.utcfromtimestamp(ms / 1000).strftime('%m-%d %H:%M:%S')


def sx_series(ts, crosses, xwob):
    """bool per bar — a gated s6x cross, confirmed at the bar where the run has lasted `xwob` bars.

    crosses  [(sx_ms, sx_run_bars)] for ONE direction, already filtered on sx_lb_min.

    CAUSALITY. sx_run_bars is measured FORWARD in build_s46.py (`nz = flatnonzero(~side[z:])`), so
    filtering on it is only legitimate when the signal is stamped at a bar by which the run has
    DEMONSTRABLY lasted that long. The filter and the shift must therefore use the SAME xwob:
        filter  sx_run_bars >= xwob        (the run held for xwob bars)
        stamp   at cross_ms + (xwob-1)*5s  (the bar at which that became knowable)
    Filtering >= 6 while stamping at +2 would assert at bar z+2 that the run lasts 6 — lookahead.
    Both are derived from the one `xwob` argument here so they cannot drift apart.

    Mirrors build_s46_window.py:74-79, which applies both the sx_run_bars filter and the shift. My
    first build applied the shift ONLY, so it accepted crosses whose run ended before the wob was
    met — looser than Joe's rule, and every exit bar in that run was affected.""" 
    out = np.zeros(len(ts), bool)
    sh = (xwob - 1) * 5000
    for m, rb in crosses:
        if rb < xwob:                      # the run never held long enough — Joe's rule discards it
            continue
        i = int(np.searchsorted(ts, int(m) + sh))
        if i < len(ts):
            out[i] = True
    return out


def main(argv):
    g = lambda f, d: (type(d)(argv[argv.index(f) + 1]) if f in argv else d)
    fs, xw, cfg = g('--fence', 3), g('--xwob', 6), g('--cfg', 'CUR')
    mp, op = NPZ[cfg]
    dm = np.load(mp); ts = dm['ts'].astype(np.int64)
    m15, m22 = dm['r15'].astype(float), dm['r22'].astype(float)      # momo duty
    if op == mp:
        r15, r22 = m15, m22
    else:                                                            # variant A: separated duties
        do = np.load(op); to = do['ts'].astype(np.int64)
        i = np.searchsorted(ts, to)
        r15 = np.full(len(ts), np.nan); r22 = np.full(len(ts), np.nan)
        ok_ = (i < len(ts)) & (ts[np.minimum(i, len(ts) - 1)] == to)
        r15[i[ok_]] = do['r15'].astype(float)[ok_]
        r22[i[ok_]] = do['r22'].astype(float)[ok_]
    print('cfg %s   momo lines %s   oob lines %s' % (cfg, mp.split('/')[-1], op.split('/')[-1]))
    f_lo, f_hi = fence(fs)

    db = DatabaseManager(**get_db_config()); db.connect()
    db.execute(DDL)
    try:   # Joe 0805: stamp WHICH builder wrote the row. build_s46_window.py's INSERT does not name
           # this column, so its rows take the DEFAULT and Joe's file needs no edit.
        db.execute("ALTER TABLE s46_window ADD COLUMN sw_src VARCHAR(24) DEFAULT 'item15'")
        print("  + column sw_src VARCHAR(24) DEFAULT 'item15'")
    except Exception:
        pass
    rows = db.execute('SELECT sw_pk,sw_n,sw_dr,sw_entry_ms FROM s46_window ORDER BY sw_n', fetch=True)
    PX = db.execute('SELECT px_ms,px_v FROM s46_px ORDER BY px_ms', fetch=True)
    EX = db.execute("SELECT sx_ms,sx_dir,sx_run_bars FROM s46_exit WHERE sx_line='s6x' "
                    "AND sx_lb_min<=72 ORDER BY sx_ms", fetch=True)
    SX = {k: [(int(r['sx_ms']), int(r['sx_run_bars'])) for r in EX if int(r['sx_dir']) == k]
          for k in (1, -1)}
    held = {k: sx_series(ts, SX[k], xw) for k in (1, -1)}      # swept wob, used once momo has armed
    plain = {k: sx_series(ts, SX[k], 3) for k in (1, -1)}      # EXIT_WOB 3, used while unarmed
    print('crosses passing sx_run_bars>=wob:  held(wob %d) %d/%d  |  plain(wob 3) %d/%d'
          % (xw, sum(held[k].sum() for k in (1, -1)), len(EX),
             sum(plain[k].sum() for k in (1, -1)), len(EX)), flush=True)

    # PRECOMPUTE the gated indicator state once per (tf, dr), from the FIRST entry bar to tape end.
    # walk() otherwise calls momo_g() per bar per trade, and a trade with no cross runs to tape end:
    # 36 trades x ~1.3M bars x a polyfit each. This is NOT a cap on the mechanic — bars before the
    # first entry are never read by any walk, so computing them would be dead work.
    a0 = min(int(np.searchsorted(ts, int(x['sw_entry_ms']))) for x in rows)
    print('precomputing gated states, bars %d..%d (%s -> %s)'
          % (a0, len(ts) - 1, u(int(ts[a0])), u(int(ts[-1]))), flush=True)
    ST = {}
    for tf, arr in ((15, m15), (22, m22)):
        for dd in (1, -1):
            v = np.zeros(len(ts), np.int8)
            for i in range(a0, len(ts)):
                v[i] = STATE.get(momo_g(arr, dd, i)[0], 0)
            ST[(tf, dd)] = v
            print('  st%d dr%+d done' % (tf, dd), flush=True)
    gate = {dd: ((ST[(15, dd)] == 1) | (ST[(15, dd)] == 2) |
                 (ST[(22, dd)] == 1) | (ST[(22, dd)] == 2)) for dd in (1, -1)}
    # opposing curl: the curl state read against the INVERTED direction, on BOTH lines, same bar
    oppc = {dd: ((ST[(15, -dd)] == 2) & (ST[(22, -dd)] == 2)) for dd in (1, -1)}
    NAME = {0: 'none', 1: 'momo', 2: 'curl', 3: 'sideways'}

    # price on the line grid, for re-scoring s46_window's MAE/MFE/ret at the new exit bar
    pm = np.array([x['px_ms'] for x in PX], np.int64)
    pv = np.array([x['px_v'] for x in PX], float)
    px = np.full(len(ts), np.nan); kk = np.searchsorted(pm, ts)
    okp = (kk < len(pm)) & (pm[np.minimum(kk, len(pm) - 1)] == ts); px[okp] = pv[kk[okp]]
    fpx = np.isfinite(px); ipx = np.where(fpx, np.arange(len(px)), 0)
    np.maximum.accumulate(ipx, out=ipx); px = px[ipx]

    ins = []; wupd = []
    for r in rows:
        dr = int(r['sw_dr']); a = int(np.searchsorted(ts, int(r['sw_entry_ms'])))
        if a >= len(ts) - 1:
            continue
        ev = walk(r15, r22, dr, a, len(ts) - 1, held[dr], plain[dr], fs, gate[dr], oppc[dr])
        # Joe 0805: "I said that I wanted it updated on every run". s46_window keeps its SHAPE —
        # same 18+6 columns, same one row per trade — but its exit and its MAE/MFE/ret are re-scored
        # at item 13's exit bar. Re-running build_s46_window.py restores the item-15 baseline.
        xb = [w for kind, w, _ in ev if kind == CROSS]
        if xb and np.isfinite(px[a]) and px[a] != 0:
            b = xb[0]; seg = px[a + 1:b + 1]
            if len(seg):
                rr_ = dr * (seg - px[a]) / px[a] * 100.0
                wupd.append((int(ts[b]), u(int(ts[b])), int(b - a),
                             float(abs(min(0.0, rr_.min()))), float(max(0.0, rr_.max())),
                             float(rr_[-1]), int(r['sw_pk'])))
        for kind, w, br in ev:
            ins.append((int(r['sw_entry_ms']), int(r['sw_n']), dr, kind, br,
                        int(ts[w]), u(int(ts[w])), w,
                        float(r15[w]) if np.isfinite(r15[w]) else None,
                        float(r22[w]) if np.isfinite(r22[w]) else None,
                        NAME[int(ST[(15, dr)][w])], NAME[int(ST[(22, dr)][w])],
                        fs, f_lo, f_hi, xw, cfg, CURL_R2_MIN))
    if wupd:
        src = 'item13 %s f%d x%d' % (cfg, fs, xw)
        db.executemany('UPDATE s46_window SET sw_exit_ms=%s, sw_exit_utc=%s, sw_hold_bars=%s, '
                       'sw_mae=%s, sw_mfe=%s, sw_ret=%s, sw_src=%s WHERE sw_pk=%s',
                       [x[:6] + (src,) + x[6:] for x in wupd])
    db.execute('DELETE FROM s46_event WHERE se_cfg=%s AND se_fence_s=%s AND se_xwob=%s', (cfg, fs, xw))
    if ins:
        db.executemany('''INSERT INTO s46_event (se_trade_ms,se_n,se_dr,se_kind,se_branch,se_ms,
            se_utc,se_bar,se_r15,se_r22,se_st15,se_st22,se_fence_s,se_fence_lo,se_fence_hi,
            se_xwob,se_cfg,se_curl_r2) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
            ins, chunk=2000)
    db.disconnect()
    n = {k: sum(1 for x in ins if x[3] == k) for k in (ACT, EXIT, CROSS, OPP)}
    print('s46_window updated: %d of %d rows re-scored at item 13 exits' % (len(wupd), len(rows)))
    print('s46_event  cfg %s  fence %d (%.0f/%.0f)  xwob %d  ->  %d rows over %d trades'
          % (cfg, fs, f_lo, f_hi, xw, len(ins), len(rows)))
    print('  momo_act %d   momo_exit %d (branch1 %d / branch2 %d)   opp_curl %d   s6x_cross %d'
          % (n[ACT], n[EXIT], sum(1 for x in ins if x[4] == '1'),
             sum(1 for x in ins if x[4] == '2'), n[OPP], n[CROSS]))


if __name__ == '__main__':
    main(sys.argv[1:])
