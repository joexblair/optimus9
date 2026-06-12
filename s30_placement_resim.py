"""
s30 placement re-sim — the REPORTING layer (Joe: use the earlier-defined columns).

The 950k grind is the cheap SELECTOR. Here we pull a broad candidate set (net-reliable
∪ placement-reliable ∪ best-edge), re-run each instrumented against real 0.9 swings, and
rank by CLEAN PLACEMENT (near_zero%) not raw net — the actual objective (s30r owning the
swing it sees, landing past the adverse turn).

Per trade, the earlier columns: trade_ts (s30r OOB entry) · exit_ts (s30M favourable mask
exit) · closest_swing_ts / adverse_swing_ts (find_pivots 0.9) · won (reached +0.9% before
stop) · secs_to_won · max_stop_needed (heat) · near_zero (≤0.10). Plus exit_pnl (banked at
the s30M exit, 0.33 stop). Per-combo placement aggregates across 4×24h windows → ranked.
Per-trade rows persisted for the TOP combos (pine recon).
"""
import sys, time
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import logging
for n in ('BybitKlineClient', 'BLDetect', 'KlineLoader', 'DatabaseManager'):
    logging.getLogger(n).setLevel('ERROR')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.bl_detect import BLDetect
from optimus9.compute.swing_detect import find_pivots

STOP, TAKE, CAP = 0.33, 0.9, 540
HI, LO = 85.0, 15.0
OFFSETS = [0, 5, 10, 15]; DAY_MS = 86400000
MASKS = {'any': {1, 2, 3}, 'done': {3}}
NEAR_ZERO = 0.10
TOP_PERSIST = 10                                # per-trade rows persisted for the best N combos


def oob_onsets(line):
    lo = line < LO; hi = line > HI
    lo_on = np.flatnonzero(lo & ~np.concatenate([[False], lo[:-1]]))
    hi_on = np.flatnonzero(hi & ~np.concatenate([[False], hi[:-1]]))
    bars = np.concatenate([lo_on, hi_on])
    dirs = np.concatenate([np.ones(len(lo_on), np.int8), -np.ones(len(hi_on), np.int8)])
    o = np.argsort(bars); return bars[o].astype(np.int64), dirs[o]


def nearest_ts(piv_bars, tsm, e):
    if len(piv_bars) == 0:
        return None
    k = int(np.searchsorted(piv_bars, e))
    c = min([x for x in (k - 1, k) if 0 <= x < len(piv_bars)], key=lambda x: abs(piv_bars[x] - e))
    return int(tsm[piv_bars[c]])


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    dmax = int(db.execute('SELECT MAX(kc_timestamp) m FROM kline_collection WHERE kc_tp_pk=1', fetch=True)[0]['m'])

    # broad candidate union
    cand = {}
    for order in ('min_net DESC', 'min_win DESC', 'mean_pnl DESC'):
        for r in db.execute(f'''SELECT r_klen,r_rsi,r_stc,m_bblen,m_bbmult,mask FROM s30_grind_results
                                WHERE all_pos=1 ORDER BY {order} LIMIT 200''', fetch=True):
            cand[(r['r_klen'], r['r_rsi'], r['r_stc'], r['m_bblen'], r['m_bbmult'], r['mask'])] = 1
    cand = list(cand)
    print(f'{len(cand)} candidates (net ∪ placement ∪ edge)')

    db.execute('DROP TABLE IF EXISTS s30_placement')
    db.execute('''CREATE TABLE s30_placement (
        spl_pk BIGINT AUTO_INCREMENT PRIMARY KEY, r_klen INT,r_rsi INT,r_stc INT,
        m_bblen INT,m_bbmult FLOAT,mask VARCHAR(6), tot_n INT, won_pct FLOAT, nearzero_pct FLOAT,
        win_pct FLOAT, net FLOAT, med_s2w FLOAT, med_mstop FLOAT,
        min_nearzero FLOAT, min_won FLOAT, min_net FLOAT)''')
    db.execute('''DROP TABLE IF EXISTS s30_recon_trades''')
    db.execute('''CREATE TABLE s30_recon_trades (
        srt_pk BIGINT AUTO_INCREMENT PRIMARY KEY, combo VARCHAR(48), window_off INT,
        trade_ts BIGINT, exit_ts BIGINT, dir TINYINT, closest_swing_ts BIGINT, adverse_swing_ts BIGINT,
        won TINYINT, secs_to_won INT, max_stop_needed FLOAT, near_zero TINYINT, exit_pnl FLOAT)''')

    det = BLDetect(db, lookback_hours=24, warmup_hours=12)
    s30M_cfg = det._cfg_dict(18)
    fam_m = {'name': 's30M', 'tf_seconds': s30M_cfg['tf_seconds'], 'line_type': 'bb', 'k': s30M_cfg,
             'predictor_min': None, 'predictor_maj': None, 'exit_support': None,
             'exit3_support': None, 'exit_mask': 7, 'pk_ic_pk': None}
    s30r_fam = [f for f in det._families if f['name'] == 's30r'][0]

    # ── per-window: precompute tape + pivots; cache line computes by param-key ──
    W = []; t0 = time.time()
    for off in OFFSETS:
        base, ts, win_start, _, _ = det._setup(dmax - off * DAY_MS)
        Mk = ts >= win_start
        rc = base['close'].to_numpy(float)[Mk]; tsm = ts[Mk].astype('int64')
        piv = find_pivots(rc, 0.9)
        pv_all = np.array(sorted(p[0] for p in piv))
        pv_lo = np.array(sorted(p[0] for p in piv if p[1] == 'L'))
        pv_hi = np.array(sorted(p[0] for p in piv if p[1] == 'H'))
        W.append(dict(base=base, ts=ts, Mk=Mk, rc=rc, tsm=tsm, n=len(rc),
                      pv_all=pv_all, pv_lo=pv_lo, pv_hi=pv_hi, r_cache={}, m_cache={}))
    print(f'window tapes + pivots ready ({time.time()-t0:.0f}s)')

    def s30r_entries(w, k, r, s):
        key = (k, r, s)
        if key not in w['r_cache']:
            line = det._line(w['base'], {**s30r_fam['k'], 'k_len': k, 'rsi_len': r, 'stc_len': s})[w['Mk']]
            w['r_cache'][key] = oob_onsets(line)
        return w['r_cache'][key]

    def s30M_exits(w, bl, bm, mask):
        key = (bl, bm)
        if key not in w['m_cache']:
            st = det._run_family({**fam_m, 'k': {**s30M_cfg, 'bb_len': bl, 'bb_mult': bm}}, w['base'], w['ts'])[3]['state'][w['Mk']]
            lm = det._line(w['base'], {**s30M_cfg, 'bb_len': bl, 'bb_mult': bm})[w['Mk']]
            w['m_cache'][key] = (st, lm > HI, lm < LO)
        st, hiS, loS = w['m_cache'][key]
        inm = np.isin(st, list(MASKS[mask]))
        return np.flatnonzero(inm & hiS).astype(np.int64), np.flatnonzero(inm & loS).astype(np.int64)

    def trades(w, ent, exhi, exlo):
        bars, dirs = ent; out = []
        rc, n, tsm = w['rc'], w['n'], w['tsm']
        for e, d in zip(bars, dirs):
            exarr = exhi if d == 1 else exlo
            p = np.searchsorted(exarr, e, side='right')
            ex = int(exarr[p]) if p < len(exarr) else e + CAP
            ex = min(ex, n - 1, e + CAP)
            seg = rc[e:ex + 1]
            rel = (seg - rc[e]) / rc[e] * 100 * d
            hit = np.where(rel >= TAKE)[0]
            won = len(hit) > 0
            cut = int(hit[0]) if won else len(rel) - 1
            mstop = float(np.maximum(0.0, -rel[:cut + 1]).max()) if cut >= 0 else 0.0
            adv_exit = float(np.maximum(0.0, -rel).max())
            exit_pnl = -STOP if adv_exit >= STOP else float(rel[-1])
            out.append((int(tsm[e]), int(tsm[ex]), int(d),
                        nearest_ts(w['pv_all'], tsm, e),
                        nearest_ts(w['pv_lo'] if d == 1 else w['pv_hi'], tsm, e),
                        int(won), (int(hit[0]) + 1) * 5 if won else None,
                        round(mstop, 3), int(mstop <= NEAR_ZERO), round(exit_pnl, 4)))
        return out

    rows_p = []; t1 = time.time()
    for ci, (k, r, s, bl, bm, mask) in enumerate(cand):
        per_win = []; combo = f'{k},{r},{s},{bl},{bm},{mask}'
        for w in W:
            ent = s30r_entries(w, k, r, s); hi, lo = s30M_exits(w, bl, bm, mask)
            per_win.append(trades(w, ent, hi, lo))
        flat = [(combo, OFFSETS[wi], *t) for wi, ws in enumerate(per_win) for t in ws]
        # per-window aggregates
        won_w, nz_w, net_w, n_w = [], [], [], []
        for ws in per_win:
            if not ws:
                won_w.append(0); nz_w.append(0); net_w.append(0); n_w.append(0); continue
            won_w.append(np.mean([t[5] for t in ws]) * 100)
            nz_w.append(np.mean([t[8] for t in ws]) * 100)
            net_w.append(sum(t[9] for t in ws))
            n_w.append(len(ws))
        tot_n = sum(n_w)
        allt = [t for ws in per_win for t in ws]
        s2w = [t[6] for t in allt if t[6] is not None]
        rows_p.append((k, r, s, bl, bm, mask, tot_n,
                       float(np.mean([t[5] for t in allt]) * 100) if allt else 0,
                       float(np.mean([t[8] for t in allt]) * 100) if allt else 0,
                       float(np.mean([t[9] > 0 for t in allt]) * 100) if allt else 0,
                       float(sum(t[9] for t in allt)),
                       float(np.median(s2w)) if s2w else None,
                       float(np.median([t[7] for t in allt])) if allt else None,
                       float(min(nz_w)), float(min(won_w)), float(min(net_w))))
        if ci < TOP_PERSIST or True:            # stash all trades; we filter persist after ranking
            db.executemany('''INSERT INTO s30_recon_trades
                (combo,window_off,trade_ts,exit_ts,dir,closest_swing_ts,adverse_swing_ts,won,secs_to_won,max_stop_needed,near_zero,exit_pnl)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', flat)
    db.executemany('''INSERT INTO s30_placement
        (r_klen,r_rsi,r_stc,m_bblen,m_bbmult,mask,tot_n,won_pct,nearzero_pct,win_pct,net,med_s2w,med_mstop,min_nearzero,min_won,min_net)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''', rows_p)
    print(f're-sim done: {len(cand)} combos in {time.time()-t1:.0f}s')

    print('\\n=== TOP 15 by CLEAN PLACEMENT (worst-window near_zero%, gated net+ all windows) ===')
    top = db.execute('''SELECT * FROM s30_placement WHERE min_net>0
        ORDER BY min_nearzero DESC LIMIT 15''', fetch=True)
    print(f'{"klen":>4}{"rsi":>4}{"stc":>4}{"bblen":>6}{"mult":>6}{"mask":>5} {"n":>5} '
          f'{"won%":>6}{"nz%":>6}{"win%":>6}{"net":>8}{"s2w":>6}{"mstop":>7}{"minNZ":>6}{"minWon":>7}')
    for t in top:
        print(f'{t["r_klen"]:>4}{t["r_rsi"]:>4}{t["r_stc"]:>4}{t["m_bblen"]:>6}{t["m_bbmult"]:>6.2f}'
              f'{t["mask"]:>5} {t["tot_n"]:>5} {t["won_pct"]:>6.1f}{t["nearzero_pct"]:>6.1f}'
              f'{t["win_pct"]:>6.1f}{t["net"]:>8.1f}{(t["med_s2w"] or 0):>6.0f}{(t["med_mstop"] or 0):>7.3f}'
              f'{t["min_nearzero"]:>6.1f}{t["min_won"]:>7.1f}')
    db.disconnect()


if __name__ == '__main__':
    main()
