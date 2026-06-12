"""
s30r × s30M swing grind (task: BL turn/exit line dial-in).

CANONICAL trade (pre/post collapsed — Joe 2026-06-12): s30r OOB onset = entry
(mean-revert: OOB-low→long, OOB-high→short) · hard 0.33% stop · exit = first bar
after entry where s30M is OOB on the FAVOURABLE side with state ∈ mask · else a
45-min mark-to-market. P&L = -0.33 if stopped, else exit return.

SCORING = reliability over PnL (a 30s line only needs to OWN THE SWING IT SEES — it
can't know what the HTF lines do above it). Rank favours combos net-positive in EVERY
window with steady placement win%, not a one-window spike. All per-window stats are
persisted so the rank formula stays re-derivable.

4 windows × 24h, ends 5 days apart. Computes are SHARED across the joint grid: each
s30r line and s30M machine computes once per window; the s30r×s30M×mask sims are free.
PILOT=1 env shrinks the grid for timing + diagnostics.
"""
import os, sys, time
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import logging
for n in ('BybitKlineClient', 'BLDetect', 'KlineLoader', 'DatabaseManager'):
    logging.getLogger(n).setLevel('ERROR')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.bl_detect import BLDetect

PILOT = os.environ.get('PILOT') == '1'
STOP, TAKE_CAP = 0.33, 540                      # 0.33% hard stop · 45-min mark-to-market (540×5s)
HI, LO = 85.0, 15.0                             # OOB boundaries (fixed; not swept)
OFFSETS = [0, 5, 10, 15]                        # window ends, days back
DAY_MS = 86400000
MASKS = {'any': {1, 2, 3}, 'done': {3}}        # exit on first favourable OOB · or wait for complete

if PILOT:
    R_KLEN, R_RSI, R_STC = [3, 4, 5], [10, 14], [12, 16]
    M_BBLEN, M_BBMULT = [24, 37, 50], [0.83, 1.24]
else:
    R_KLEN = list(range(2, 11))                                    # 9
    R_RSI  = list(range(6, 25, 2))                                 # 10
    R_STC  = list(range(6, 29, 2))                                 # 12   → 1080 s30r
    M_BBLEN = list(range(10, 87, 4))                               # 20
    M_BBMULT = [round(0.4 + 0.1 * i, 2) for i in range(22)]        # 0.4..2.5 → 22  → 440 s30M


def build_sparse(a):
    """Sparse tables for O(1) range min & max over a[l:r+1]."""
    n = len(a); K = max(1, int(np.log2(n)) + 1)
    mn = np.empty((K, n), a.dtype); mx = np.empty((K, n), a.dtype)
    mn[0] = a; mx[0] = a
    for k in range(1, K):
        s = 1 << (k - 1)
        mn[k, :n - (1 << k) + 1] = np.minimum(mn[k - 1, :n - (1 << k) + 1], mn[k - 1, s:n - (1 << k) + 1 + s])
        mx[k, :n - (1 << k) + 1] = np.maximum(mx[k - 1, :n - (1 << k) + 1], mx[k - 1, s:n - (1 << k) + 1 + s])
    return mn, mx


def rq(tbl, lg, l, r, is_min):
    """Vectorized range query over arrays l,r (inclusive)."""
    k = lg[r - l]; s = (1 << k)
    A = tbl[k, l]; B = tbl[k, r - s + 1]
    return np.minimum(A, B) if is_min else np.maximum(A, B)


def oob_onsets(line):
    """Entry bars + dirs: OOB-low onset → long(+1), OOB-high onset → short(-1)."""
    lowoob = line < LO; hioob = line > HI
    lo_on = np.flatnonzero(lowoob & ~np.concatenate([[False], lowoob[:-1]]))
    hi_on = np.flatnonzero(hioob & ~np.concatenate([[False], hioob[:-1]]))
    bars = np.concatenate([lo_on, hi_on])
    dirs = np.concatenate([np.ones(len(lo_on), np.int8), -np.ones(len(hi_on), np.int8)])
    o = np.argsort(bars)
    return bars[o].astype(np.int64), dirs[o]


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    dmax = int(db.execute('SELECT MAX(kc_timestamp) m FROM kline_collection WHERE kc_tp_pk=1', fetch=True)[0]['m'])
    db.execute('DROP TABLE IF EXISTS s30_grind_results')
    db.execute('''CREATE TABLE s30_grind_results (
        sgr_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
        r_klen INT, r_rsi INT, r_stc INT, m_bblen INT, m_bbmult FLOAT, mask VARCHAR(6),
        w0_n INT,w0_win FLOAT,w0_net FLOAT, w1_n INT,w1_win FLOAT,w1_net FLOAT,
        w2_n INT,w2_win FLOAT,w2_net FLOAT, w3_n INT,w3_win FLOAT,w3_net FLOAT,
        tot_n INT, tot_net FLOAT, mean_pnl FLOAT, min_net FLOAT, min_win FLOAT, all_pos TINYINT,
        KEY(all_pos), KEY(min_net))''')

    det = BLDetect(db, lookback_hours=24, warmup_hours=12)
    s30M_cfg = det._cfg_dict(18)
    fam_m = {'name': 's30M', 'tf_seconds': s30M_cfg['tf_seconds'], 'line_type': 'bb', 'k': s30M_cfg,
             'predictor_min': None, 'predictor_maj': None, 'exit_support': None,
             'exit3_support': None, 'exit_mask': 7, 'pk_ic_pk': None}
    s30r_fam = [f for f in det._families if f['name'] == 's30r'][0]

    r_combos = [(k, r, s) for k in R_KLEN for r in R_RSI for s in R_STC]
    m_combos = [(bl, bm) for bl in M_BBLEN for bm in M_BBMULT]
    print(f'grid: {len(r_combos)} s30r × {len(m_combos)} s30M × {len(MASKS)} masks '
          f'= {len(r_combos)*len(m_combos)*len(MASKS):,} joint  ·  4 windows  ·  PILOT={PILOT}')

    # ── precompute per window: s30r entries, s30M exit structures, sparse tables ──
    W = []
    t0 = time.time()
    for off in OFFSETS:
        base, ts, win_start, _, _ = det._setup(dmax - off * DAY_MS)
        Mk = ts >= win_start
        rc = base['close'].to_numpy(float)[Mk]; n = len(rc)
        lg = np.floor(np.log2(np.maximum(np.arange(n + 1), 1))).astype(np.int64)
        mn, mx = build_sparse(rc)
        ent = []
        for (k, r, s) in r_combos:
            line = det._line(base, {**s30r_fam['k'], 'k_len': k, 'rsi_len': r, 'stc_len': s})[Mk]
            ent.append(oob_onsets(line))
        mex = []                                  # per s30M: dict mask→(hi_bars, lo_bars)
        for (bl, bm) in m_combos:
            st = det._run_family({**fam_m, 'k': {**s30M_cfg, 'bb_len': bl, 'bb_mult': bm}}, base, ts)[3]['state'][Mk]
            lm = det._line(base, {**s30M_cfg, 'bb_len': bl, 'bb_mult': bm})[Mk]
            hi_side = lm > HI; lo_side = lm < LO
            d = {}
            for mn_, sset in MASKS.items():
                inmask = np.isin(st, list(sset))
                d[mn_] = (np.flatnonzero(inmask & hi_side).astype(np.int64),
                          np.flatnonzero(inmask & lo_side).astype(np.int64))
            mex.append(d)
        W.append(dict(rc=rc, n=n, lg=lg, mn=mn, mx=mx, ent=ent, mex=mex))
        print(f'  win off={off:>2}d  bars={n}  precompute done  ({time.time()-t0:.0f}s elapsed)')
    print(f'precompute total: {time.time()-t0:.0f}s')

    def sim(entries, exhi, exlo, w):
        """Vectorized P&L for one (s30r,s30M,mask) over one window. Returns (n, win%, net)."""
        bars, dirs = entries
        if len(bars) == 0:
            return 0, 0.0, 0.0
        rc, n, lg, mn, mx = w['rc'], w['n'], w['lg'], w['mn'], w['mx']
        pnl = np.empty(len(bars))
        for grp, exarr in ((1, exhi), (-1, exlo)):
            gm = dirs == grp
            if not gm.any():
                continue
            e = bars[gm]
            # exit = first favourable mask bar after entry; else 45-min mark-to-market
            if len(exarr) == 0:
                ex = e + TAKE_CAP
            else:
                pos = np.searchsorted(exarr, e, side='right')
                has = pos < len(exarr)
                ex = np.where(has, exarr[np.clip(pos, 0, len(exarr) - 1)], e + TAKE_CAP)
            ex = np.minimum(ex, n - 1)
            ex = np.minimum(ex, e + TAKE_CAP)
            # stop: adverse over [e,ex]
            if grp == 1:
                worst = rq(mn, lg, e, ex, True); adv = (rc[e] - worst) / rc[e] * 100
            else:
                worst = rq(mx, lg, e, ex, False); adv = (worst - rc[e]) / rc[e] * 100
            ret = (rc[ex] - rc[e]) / rc[e] * 100 * grp
            pnl[gm] = np.where(adv >= STOP, -STOP, ret)
        return len(pnl), float((pnl > 0).mean() * 100), float(pnl.sum())

    # ── sim loop ──
    print('sim...'); t1 = time.time(); rows = []; done = 0
    total = len(r_combos) * len(m_combos) * len(MASKS)
    for ri, (k, r, s) in enumerate(r_combos):
        for mi, (bl, bm) in enumerate(m_combos):
            for mask in MASKS:
                ws = []
                for w in W:
                    hi, lo = w['mex'][mi][mask]
                    ws.append(sim(w['ent'][ri], hi, lo, w))
                nets = [x[2] for x in ws]; wins = [x[1] for x in ws]; ns = [x[0] for x in ws]
                tot_n = sum(ns); tot_net = sum(nets)
                all_pos = int(all(x > 0 for x in nets) and all(x >= (3 if PILOT else 8) for x in ns))
                mean_pnl = tot_net / tot_n if tot_n else 0.0
                rows.append((k, r, s, bl, bm, mask, ns[0], wins[0], nets[0], ns[1], wins[1], nets[1],
                             ns[2], wins[2], nets[2], ns[3], wins[3], nets[3], tot_n, tot_net,
                             mean_pnl, min(nets), min(wins), all_pos))
                done += 1
        if len(rows) >= 20000:
            db.executemany('''INSERT INTO s30_grind_results
                (r_klen,r_rsi,r_stc,m_bblen,m_bbmult,mask,w0_n,w0_win,w0_net,w1_n,w1_win,w1_net,
                 w2_n,w2_win,w2_net,w3_n,w3_win,w3_net,tot_n,tot_net,mean_pnl,min_net,min_win,all_pos)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', rows)
            rows = []
            print(f'  {done:,}/{total:,}  ({time.time()-t1:.0f}s, {done/(time.time()-t1):.0f}/s)')
    if rows:
        db.executemany('''INSERT INTO s30_grind_results
            (r_klen,r_rsi,r_stc,m_bblen,m_bbmult,mask,w0_n,w0_win,w0_net,w1_n,w1_win,w1_net,
             w2_n,w2_win,w2_net,w3_n,w3_win,w3_net,tot_n,tot_net,mean_pnl,min_net,min_win,all_pos)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', rows)
    print(f'sim done: {total:,} combos in {time.time()-t1:.0f}s ({total/(time.time()-t1):.0f}/s)')

    # ── reliability ranking ──
    print('\\n=== TOP 15 by reliability (all 4 windows net+, ranked by worst-window net) ===')
    top = db.execute('''SELECT r_klen,r_rsi,r_stc,m_bblen,m_bbmult,mask,tot_n,tot_net,mean_pnl,min_net,min_win
        FROM s30_grind_results WHERE all_pos=1 ORDER BY min_net DESC LIMIT 15''', fetch=True)
    if not top:
        print('  (none net-positive in all 4 windows — loosening to tot_net)')
        top = db.execute('''SELECT r_klen,r_rsi,r_stc,m_bblen,m_bbmult,mask,tot_n,tot_net,mean_pnl,min_net,min_win
            FROM s30_grind_results ORDER BY tot_net DESC LIMIT 15''', fetch=True)
    print(f'{"klen":>4}{"rsi":>4}{"stc":>4} {"bblen":>5}{"mult":>6} {"mask":>5} {"tot_n":>6} '
          f'{"tot_net":>8} {"mean":>7} {"min_net":>8} {"min_win":>7}')
    for t in top:
        print(f'{t["r_klen"]:>4}{t["r_rsi"]:>4}{t["r_stc"]:>4} {t["m_bblen"]:>5}{t["m_bbmult"]:>6.2f} '
              f'{t["mask"]:>5} {t["tot_n"]:>6} {t["tot_net"]:>8.2f} {t["mean_pnl"]:>7.3f} '
              f'{t["min_net"]:>8.2f} {t["min_win"]:>7.1f}')
    npos = db.execute('SELECT COUNT(*) c FROM s30_grind_results WHERE all_pos=1', fetch=True)[0]['c']
    print(f'\\n{npos:,} combos net-positive across ALL 4 windows  → s30_grind_results')
    db.disconnect()


if __name__ == '__main__':
    main()
