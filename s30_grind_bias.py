"""
s30 grind v2 — bny30 BIAS-gated entries + two support/exit lines (s30M Major vs s30m mini).

Fixes the v1 floor (ungated s30r OOB bled 62% stops): entry = s30r OOB onset kept ONLY when
its mean-revert dir matches the LATCHED bny30 bias (−oob at last IB→OOB breach, held through
IB). Two grinds run simultaneously — the favourable-side mask exit driven by s30M (src ohlc4)
vs s30m (src hlcc4), bb_len/bb_mult swept for each. Canonical trade otherwise: 0.33 stop,
45-min cap, P&L −0.33 if stopped else exit return. Reliability over PnL, 4×24h windows.
Results → s30_grind_results (now with a `support` column).
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
from optimus9.orchestration.gate_signal_sweep import bny30_oob_side

PILOT = os.environ.get('PILOT') == '1'
STOP, CAP, HI, LO = 0.33, 540, 85.0, 15.0
OFFSETS = [0, 5, 10, 15]; DAY_MS = 86400000
MASKS = {'any': {1, 2, 3}, 'done': {3}}
SUPPORTS = [('maj', 18), ('min', 34)]          # s30M Major (ohlc4) · s30m mini (hlcc4) — case-distinct labels
                                               #   (MySQL collation is case-insensitive: 'M'=='m' would merge)

if PILOT:
    R_KLEN, R_RSI, R_STC = [3, 4, 5], [10, 14], [12, 16]
    M_BBLEN, M_BBMULT = [24, 37, 50], [0.83, 1.24]
else:
    R_KLEN = list(range(2, 11))                                    # 9
    R_RSI  = list(range(6, 25, 2))                                 # 10
    R_STC  = list(range(6, 29, 2))                                 # 12  → 1080
    M_BBLEN = list(range(10, 87, 4))                               # 20
    M_BBMULT = [round(0.4 + 0.1 * i, 2) for i in range(22)]        # 0.4..2.5 → 22  → 440


def latched_bias(oob):
    bias = np.zeros(len(oob), np.int8); cur = 0
    for i in range(len(oob)):
        if oob[i] != 0 and (i == 0 or oob[i - 1] == 0):
            cur = -int(oob[i])                 # OOB-low → long(+1), OOB-high → short(-1)
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


def oob_onsets_biased(line, bias):
    lo = line < LO; hi = line > HI
    lo_on = np.flatnonzero(lo & ~np.concatenate([[False], lo[:-1]]))
    hi_on = np.flatnonzero(hi & ~np.concatenate([[False], hi[:-1]]))
    bars = np.concatenate([lo_on, hi_on])
    dirs = np.concatenate([np.ones(len(lo_on), np.int8), -np.ones(len(hi_on), np.int8)])
    keep = dirs == bias[bars]                  # bny30 bias gate: mean-revert dir must match latch
    bars, dirs = bars[keep], dirs[keep]
    o = np.argsort(bars); return bars[o].astype(np.int64), dirs[o]


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    dmax = int(db.execute('SELECT MAX(kc_timestamp) m FROM kline_collection WHERE kc_tp_pk=1', fetch=True)[0]['m'])
    db.execute('DROP TABLE IF EXISTS s30_grind_results')
    db.execute('''CREATE TABLE s30_grind_results (
        sgr_pk BIGINT AUTO_INCREMENT PRIMARY KEY, support VARCHAR(4),
        r_klen INT,r_rsi INT,r_stc INT,m_bblen INT,m_bbmult FLOAT,mask VARCHAR(6),
        w0_n INT,w0_win FLOAT,w0_net FLOAT, w1_n INT,w1_win FLOAT,w1_net FLOAT,
        w2_n INT,w2_win FLOAT,w2_net FLOAT, w3_n INT,w3_win FLOAT,w3_net FLOAT,
        tot_n INT,tot_net FLOAT,mean_pnl FLOAT,min_net FLOAT,min_win FLOAT,all_pos TINYINT,
        KEY(support),KEY(all_pos),KEY(min_net))''')

    det = BLDetect(db, lookback_hours=24, warmup_hours=12)
    sup_cfg = {tag: det._cfg_dict(icpk) for tag, icpk in SUPPORTS}
    fam_tpl = lambda cfg: {'name': 's30M', 'tf_seconds': cfg['tf_seconds'], 'line_type': 'bb', 'k': cfg,
                           'predictor_min': None, 'predictor_maj': None, 'exit_support': None,
                           'exit3_support': None, 'exit_mask': 7, 'pk_ic_pk': None}
    s30r_fam = [f for f in det._families if f['name'] == 's30r'][0]

    r_combos = [(k, r, s) for k in R_KLEN for r in R_RSI for s in R_STC]
    m_combos = [(bl, bm) for bl in M_BBLEN for bm in M_BBMULT]
    print(f'grid: {len(r_combos)} s30r × {len(m_combos)} s30M-bb × {len(SUPPORTS)} support × {len(MASKS)} mask '
          f'= {len(r_combos)*len(m_combos)*len(SUPPORTS)*len(MASKS):,} joint · 4 win · PILOT={PILOT}')

    W = []; t0 = time.time()
    for off in OFFSETS:
        base, ts, win_start, _, _ = det._setup(dmax - off * DAY_MS)
        Mk = ts >= win_start
        rc = base['close'].to_numpy(float)[Mk]; n = len(rc)
        bias = latched_bias(bny30_oob_side(base))[Mk]
        lg = np.floor(np.log2(np.maximum(np.arange(n + 1), 1))).astype(np.int64)
        mn, mx = build_sparse(rc)
        ent = [oob_onsets_biased(det._line(base, {**s30r_fam['k'], 'k_len': k, 'rsi_len': r, 'stc_len': s})[Mk], bias)
               for (k, r, s) in r_combos]
        mex = {}                               # support tag → list over m_combos of {mask:(hi,lo)}
        for tag, _ in SUPPORTS:
            cfg = sup_cfg[tag]; lst = []
            for (bl, bm) in m_combos:
                kc = {**cfg, 'bb_len': bl, 'bb_mult': bm}
                st = det._run_family({**fam_tpl(cfg), 'k': kc}, base, ts)[3]['state'][Mk]
                lm = det._line(base, kc)[Mk]; hiS = lm > HI; loS = lm < LO
                d = {mnm: (np.flatnonzero(np.isin(st, list(ss)) & hiS).astype(np.int64),
                           np.flatnonzero(np.isin(st, list(ss)) & loS).astype(np.int64)) for mnm, ss in MASKS.items()}
                lst.append(d)
            mex[tag] = lst
        W.append(dict(rc=rc, n=n, lg=lg, mn=mn, mx=mx, ent=ent, mex=mex,
                      nbias=int((bias != 0).sum()), nent=sum(len(e[0]) for e in ent)))
        print(f'  win off={off:>2}d  bars={n}  bias-bars={W[-1]["nbias"]}  precompute done ({time.time()-t0:.0f}s)')
    print(f'precompute total: {time.time()-t0:.0f}s')

    def sim(entries, exhi, exlo, w):
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
            if len(exarr) == 0:
                ex = e + CAP
            else:
                pos = np.searchsorted(exarr, e, side='right'); has = pos < len(exarr)
                ex = np.where(has, exarr[np.clip(pos, 0, len(exarr) - 1)], e + CAP)
            ex = np.minimum(np.minimum(ex, n - 1), e + CAP)
            if grp == 1:
                adv = (rc[e] - rq(mn, lg, e, ex, True)) / rc[e] * 100
            else:
                adv = (rq(mx, lg, e, ex, False) - rc[e]) / rc[e] * 100
            ret = (rc[ex] - rc[e]) / rc[e] * 100 * grp
            pnl[gm] = np.where(adv >= STOP, -STOP, ret)
        return len(pnl), float((pnl > 0).mean() * 100), float(pnl.sum())

    print('sim...'); t1 = time.time(); rows = []; done = 0
    total = len(r_combos) * len(m_combos) * len(SUPPORTS) * len(MASKS)
    for tag, _ in SUPPORTS:
        for ri, (k, r, s) in enumerate(r_combos):
            for mi, (bl, bm) in enumerate(m_combos):
                for mask in MASKS:
                    ws = [sim(w['ent'][ri], *w['mex'][tag][mi][mask], w) for w in W]
                    nets = [x[2] for x in ws]; wins = [x[1] for x in ws]; ns = [x[0] for x in ws]
                    all_pos = int(all(x > 0 for x in nets) and all(x >= (3 if PILOT else 8) for x in ns))
                    rows.append((tag, k, r, s, bl, bm, mask, ns[0], wins[0], nets[0], ns[1], wins[1], nets[1],
                                 ns[2], wins[2], nets[2], ns[3], wins[3], nets[3], sum(ns), sum(nets),
                                 sum(nets) / sum(ns) if sum(ns) else 0.0, min(nets), min(wins), all_pos))
                    done += 1
            if len(rows) >= 20000:
                db.executemany('''INSERT INTO s30_grind_results (support,r_klen,r_rsi,r_stc,m_bblen,m_bbmult,mask,
                    w0_n,w0_win,w0_net,w1_n,w1_win,w1_net,w2_n,w2_win,w2_net,w3_n,w3_win,w3_net,tot_n,tot_net,mean_pnl,min_net,min_win,all_pos)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', rows)
                rows = []; print(f'  {done:,}/{total:,} ({time.time()-t1:.0f}s)')
    if rows:
        db.executemany('''INSERT INTO s30_grind_results (support,r_klen,r_rsi,r_stc,m_bblen,m_bbmult,mask,
            w0_n,w0_win,w0_net,w1_n,w1_win,w1_net,w2_n,w2_win,w2_net,w3_n,w3_win,w3_net,tot_n,tot_net,mean_pnl,min_net,min_win,all_pos)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', rows)
    print(f'sim done: {total:,} in {time.time()-t1:.0f}s')

    for tag, _ in SUPPORTS:
        print(f'\\n=== TOP 8 support={tag} by worst-window net (net+ all windows) ===')
        top = db.execute(f'''SELECT * FROM s30_grind_results WHERE support='{tag}' AND all_pos=1
            ORDER BY min_net DESC LIMIT 8''', fetch=True)
        npos = db.execute(f"SELECT COUNT(*) c FROM s30_grind_results WHERE support='{tag}' AND all_pos=1", fetch=True)[0]['c']
        print(f'  {npos:,} net-positive all 4 windows')
        for t in top:
            print(f'  k{t["r_klen"]} r{t["r_rsi"]} s{t["r_stc"]} bb{t["m_bblen"]}/{t["m_bbmult"]:.2f} {t["mask"]:>4} '
                  f'n={t["tot_n"]:>5} net={t["tot_net"]:>7.1f} mean={t["mean_pnl"]:.3f} minNet={t["min_net"]:>6.2f} minWin={t["min_win"]:.0f}')
    db.disconnect()


if __name__ == '__main__':
    main()
