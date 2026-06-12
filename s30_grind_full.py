"""
s30_grind_full — single-entity joint grid around the 3 robust placement centers, over 11
windows (every 3d). Joe's spec: k(±1,3) · rsi(±2,5) · stc(±2,5) · K-src(all 5) · bb_len
{6,7,8,9,10} · bb-src(all 5) · bb_mult(60: 0.15→9.0 step 0.15). Entry = bias-gated s30r OOB
onset; exit = first favourable-side bar where the BB machine state ∈ {1,2,3} (mask=any) via
run_bb; 0.33 stop, 45-min cap.

FAST-PATH (exact, validated in pilot): f_bb rescales to 30/70 so %B = 50 + 20·z/mult →
%B(mult) = 50 + (%B(mult=1) − 50)/mult. Compute each BB line ONCE at mult=1 via the proven
_line (exact resample/map), derive all 60 mults by a scalar, only rerun the state machine.

Metric per joint combo over 11 windows: net/win per window (edge) + the K-config's median
stop-to-swing (placement). Persist all_pos (net+ in every window). PILOT=1 shrinks + validates.
"""
import os, sys, time
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import logging
for n in ('BybitKlineClient', 'BLDetect', 'KlineLoader', 'DatabaseManager'):
    logging.getLogger(n).setLevel('ERROR')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.bl_detect import BLDetect, FENCE_HI, FENCE_LO
from optimus9.compute.breaching_line import BreachingLine
from optimus9.compute.indicator_computer import IndicatorComputer as IC
from optimus9.orchestration.gate_signal_sweep import bny30_oob_side

PILOT = os.environ.get('PILOT') == '1'
STOP, TAKE, CAP, OOBH, OOBL = 0.33, 0.9, 540, 85.0, 15.0
NWIN, STEP_D, DAY_MS = 11, 3, 86400000
SRCS = ['close', 'hl2', 'hlc3', 'ohlc4', 'hlcc4']
CENTERS = [(4, 16, 8), (7, 14, 8), (3, 12, 10)]
BBLEN = [6, 7, 8, 9, 10]
MULTS = [round(0.15 * i, 2) for i in range(1, 61)]      # 0.15 → 9.0
if PILOT:
    CENTERS = [(4, 16, 8)]; SRCS = ['close', 'ohlc4']; BBLEN = [7, 8]; MULTS = [0.75, 1.5, 3.0]; NWIN = 3


def latched_bias(oob):
    bias = np.zeros(len(oob), np.int8); cur = 0
    for i in range(len(oob)):
        if oob[i] != 0 and (i == 0 or oob[i - 1] == 0):
            cur = -int(oob[i])
        bias[i] = cur
    return bias


def build_sparse(a):
    n = len(a); K = max(1, int(np.log2(n)) + 1)
    mn = np.empty((K, n), a.dtype); mx = np.empty((K, n), a.dtype); mn[0] = a; mx[0] = a
    for k in range(1, K):
        s = 1 << (k - 1)
        mn[k, :n - (1 << k) + 1] = np.minimum(mn[k - 1, :n - (1 << k) + 1], mn[k - 1, s:n - (1 << k) + 1 + s])
        mx[k, :n - (1 << k) + 1] = np.maximum(mx[k - 1, :n - (1 << k) + 1], mx[k - 1, s:n - (1 << k) + 1 + s])
    return mn, mx


def rq(tbl, lg, l, r, is_min):
    k = lg[r - l]; s = (1 << k); A = tbl[k, l]; B = tbl[k, r - s + 1]
    return np.minimum(A, B) if is_min else np.maximum(A, B)


def krange(c, d):
    return [max(2, c + i) for i in range(-d, d + 1)]


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    dmax = int(db.execute('SELECT MAX(kc_timestamp) m FROM kline_collection WHERE kc_tp_pk=1', fetch=True)[0]['m'])
    det = BLDetect(db, lookback_hours=24, warmup_hours=12)
    c = det._cfg; fp = float(c['blc_fence_pad'])
    bl = BreachingLine(mult=30 // 5, curl_floor=float(c['blc_curl_floor']), curl_lookback=int(c['blc_curl_lookback']),
                       pseudo_cross=float(c['blc_pseudo_cross']), grace=int(c['blc_grace']),
                       exit2_ref=str(c['blc_exit2_ref']), exit_mask=7, bb_pad=float(c['blc_bb_pad']),
                       fence_hi=FENCE_HI + fp, fence_lo=FENCE_LO - fp)

    def kline(base, Mk, k, r, s, src):
        return det._line(base, {'kind': 'k', 'tf_seconds': 30, 'k_len': k, 'rsi_len': r, 'stc_len': s, 'src': src})[Mk]

    def bb1(base, blen, src):                         # %B at mult=1 (full base, for derivation)
        return det._line(base, {'kind': 'bb', 'tf_seconds': 30, 'bb_len': blen, 'bb_mult': 1.0, 'src': src})

    db.execute('DROP TABLE IF EXISTS s30_full_results')
    db.execute('''CREATE TABLE s30_full_results (sfr_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
        ck INT,cr INT,cs INT, k_len INT,rsi INT,stc INT,k_src VARCHAR(6),
        bb_len INT,bb_src VARCHAR(6),bb_mult FLOAT,
        tot_n INT, mean_pnl FLOAT, min_net FLOAT, min_win FLOAT, med_stop FLOAT, won_pct FLOAT,
        all_pos TINYINT, KEY(all_pos), KEY(min_net), KEY(mean_pnl))''')

    # ── windows ──
    W = []; t0 = time.time()
    for i in range(NWIN):
        base, ts, win_start, _, _ = det._setup(dmax - i * STEP_D * DAY_MS)
        Mk = ts >= win_start
        if Mk.sum() < 1000:
            continue
        rc = base['close'].to_numpy(float)[Mk]; n = len(rc)
        lg = np.floor(np.log2(np.maximum(np.arange(n + 1), 1))).astype(np.int64)
        mn, mx = build_sparse(rc)
        cyc = ts // (30 * 1000); seam = np.empty(len(ts), bool); seam[0] = True; seam[1:] = cyc[1:] != cyc[:-1]
        bias = latched_bias(bny30_oob_side(base))[Mk]
        W.append(dict(base=base, ts=ts, Mk=Mk, rc=rc, n=n, lg=lg, mn=mn, mx=mx, seam=seam, bias=bias))
    print(f'{len(W)} windows ready ({time.time()-t0:.0f}s)')

    def entries_place(w, k, r, s, src):
        line = kline(w['base'], w['Mk'], k, r, s, src)
        lo = line < OOBL; hi = line > OOBH
        lo_on = np.flatnonzero(lo & ~np.concatenate([[False], lo[:-1]]))
        hi_on = np.flatnonzero(hi & ~np.concatenate([[False], hi[:-1]]))
        bars = np.concatenate([lo_on, hi_on]).astype(np.int64)
        dirs = np.concatenate([np.ones(len(lo_on), np.int8), -np.ones(len(hi_on), np.int8)])
        keep = dirs == w['bias'][bars]; bars, dirs = bars[keep], dirs[keep]
        rc = w['rc']; won = 0; stops = []                      # placement: stop-to-swing
        for e, d in zip(bars, dirs):
            seg = rc[e + 1:e + 1 + CAP]
            if len(seg) == 0:
                continue
            rel = (seg - rc[e]) / rc[e] * 100 * d
            ht = np.where(rel >= TAKE)[0]
            if len(ht):
                won += 1; cc = int(ht[0])
                stops.append(float(np.maximum(0.0, -rel[:cc + 1]).max()) if cc > 0 else 0.0)
        return bars, dirs, won, stops

    def bb_exits(w, blen, src, mult, b1cache):
        key = (blen, src)
        if key not in b1cache:
            b1cache[key] = det._line(w['base'], {'kind': 'bb', 'tf_seconds': 30, 'bb_len': blen, 'bb_mult': 1.0, 'src': src})
        pctb = 50.0 + (b1cache[key] - 50.0) / mult
        st = bl.run_bb(pctb, seam=w['seam'])['state'][w['Mk']]
        pm = pctb[w['Mk']]
        active = (st == 1) | (st == 2) | (st == 3)
        return (np.flatnonzero(active & (pm > OOBH)).astype(np.int64),
                np.flatnonzero(active & (pm < OOBL)).astype(np.int64))

    def sim(w, bars, dirs, exhi, exlo):
        if len(bars) == 0:
            return 0, 0.0, 0.0
        rc, n, lg, mn, mx = w['rc'], w['n'], w['lg'], w['mn'], w['mx']
        pnl = np.empty(len(bars))
        for grp, exarr in ((1, exhi), (-1, exlo)):
            gm = dirs == grp
            if not gm.any():
                continue
            e = bars[gm]
            if len(exarr) == 0:
                ex = e + CAP
            else:
                pos = np.searchsorted(exarr, e, side='right'); has = pos < len(exarr)
                ex = np.where(has, exarr[np.clip(pos, 0, len(exarr) - 1)], e + CAP)
            ex = np.minimum(np.minimum(ex, n - 1), e + CAP)
            adv = (rc[e] - rq(mn, lg, e, ex, True)) / rc[e] * 100 if grp == 1 else (rq(mx, lg, e, ex, False) - rc[e]) / rc[e] * 100
            ret = (rc[ex] - rc[e]) / rc[e] * 100 * grp
            pnl[gm] = np.where(adv >= STOP, -STOP, ret)
        return len(pnl), float((pnl > 0).mean() * 100), float(pnl.sum())

    total_pos = 0; t1 = time.time()
    for (ck, cr, cs) in CENTERS:
        Ks = [(k, r, s, src) for k in krange(ck, 1) for r in krange(cr, 2) for s in krange(cs, 2) for src in SRCS]
        # precompute per window: K entries+placement, BB-mult exit structs
        Kent = [[] for _ in W]; BBex = [[] for _ in W]; b1c = [dict() for _ in W]
        for wi, w in enumerate(W):
            for (k, r, s, src) in Ks:
                Kent[wi].append(entries_place(w, k, r, s, src))
            for blen in BBLEN:
                for src in SRCS:
                    for mult in MULTS:
                        BBex[wi].append(bb_exits(w, blen, src, mult, b1c[wi]))
        BBcfg = [(blen, src, mult) for blen in BBLEN for src in SRCS for mult in MULTS]
        # placement per K-config across windows
        Kplace = []
        for ki in range(len(Ks)):
            stops = [x for wi in range(len(W)) for x in Kent[wi][ki][3]]
            won = sum(Kent[wi][ki][2] for wi in range(len(W)))
            ent = sum(len(Kent[wi][ki][0]) for wi in range(len(W)))
            Kplace.append((float(np.median(stops)) if stops else None, won / ent * 100 if ent else 0))
        rows = []
        for ki, (k, r, s, ksrc) in enumerate(Ks):
            medstop, wonpct = Kplace[ki]
            for bi, (blen, bsrc, mult) in enumerate(BBcfg):
                ws = [sim(w, *Kent[wi][ki][:2], *BBex[wi][bi]) for wi, w in enumerate(W)]
                nets = [x[2] for x in ws]; wins = [x[1] for x in ws]; ns = [x[0] for x in ws]
                allpos = int(all(x > 0 for x in nets) and all(x >= (3 if PILOT else 5) for x in ns))
                if not allpos:
                    continue
                total_pos += 1
                rows.append((ck, cr, cs, k, r, s, ksrc, blen, bsrc, mult, sum(ns),
                             sum(nets) / sum(ns) if sum(ns) else 0, min(nets), min(wins),
                             medstop, wonpct, allpos))
            if len(rows) >= 10000:
                db.executemany('''INSERT INTO s30_full_results (ck,cr,cs,k_len,rsi,stc,k_src,bb_len,bb_src,bb_mult,
                    tot_n,mean_pnl,min_net,min_win,med_stop,won_pct,all_pos) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', rows); rows = []
        if rows:
            db.executemany('''INSERT INTO s30_full_results (ck,cr,cs,k_len,rsi,stc,k_src,bb_len,bb_src,bb_mult,
                tot_n,mean_pnl,min_net,min_win,med_stop,won_pct,all_pos) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', rows)
        print(f'  center {ck}/{cr}/{cs}: {total_pos:,} all_pos so far ({time.time()-t1:.0f}s)')
    print(f'done: {total_pos:,} all_pos combos in {time.time()-t1:.0f}s')

    print('\\n=== TOP 12 by per-trade edge (all_pos all windows, min_win≥33) ===')
    for t in db.execute('''SELECT * FROM s30_full_results WHERE min_win>=33 ORDER BY mean_pnl DESC LIMIT 12''', fetch=True):
        print(f'  k{t["k_len"]} r{t["rsi"]} s{t["stc"]}/{t["k_src"]:>5} bb{t["bb_len"]}/{t["bb_mult"]:.2f}/{t["bb_src"]:>5} '
              f'n={t["tot_n"]:>5} mean={t["mean_pnl"]:.3f} minNet={t["min_net"]:>5.1f} minWin={t["min_win"]:.0f} medStop={t["med_stop"] or 0:.3f}')
    db.disconnect()


if __name__ == '__main__':
    main()
