"""
bl_dialin_pxbasis — ablation: is px_smooth inflating the placement vs raw close?
The entries (bias-gated PK within ±lookback of c_bls:3) are basis-independent — only the
placement WALK differs. So we re-eval the grind's top combos on its OWN 9 windows and measure
each entry's smallest-adverse-to-swing on BOTH px_smooth and raw close, then compare.
Divergence ⇒ px_smooth is the artifact ("bringing us down"); agreement ⇒ basis is innocent.
"""
import sys, json
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import logging
for n in ('BybitKlineClient', 'BLDetect', 'KlineLoader', 'DatabaseManager'):
    logging.getLogger(n).setLevel('ERROR')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.bl_detect import BLDetect, GCA5M_RAW
from optimus9.orchestration.gate_signal_sweep import bny30_oob_side, pine_aligned_signals
from bl_dialin import latched_bias, BREACH, TAKE, CAP, STOPMAX, WIN_FILE

SUPPORT_IC = 34


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    det = BLDetect(db, lookback_hours=24, warmup_hours=12)
    s30r = [f for f in det._families if f['name'] == BREACH][0]
    sup0 = det._cfg_dict(SUPPORT_IC)
    others = [f for f in det._families if f['name'] != BREACH]
    ends = json.load(open(WIN_FILE))['ends']                       # the grind's own 9 windows
    top = db.execute('SELECT k_len,rsi,stc,k_src,bb_len,bb_mult,bb_src,exit_mask,lookback,med_stop '
                     'FROM bl_dialin_results WHERE all_win=1 ORDER BY med_stop ASC LIMIT 30', fetch=True)

    W = []
    for e in ends:
        base, ts, ws, _, px = det._setup(e)
        Mk = ts >= ws
        st = np.vstack([det._run_family(f, base, ts)[3]['state'] for f in others])
        fixed = np.where((st == 0).all(axis=0), 99, np.where(st == 0, 99, st).min(axis=0))
        bias = latched_bias(bny30_oob_side(base))
        ai, ad = pine_aligned_signals(base, det._db, GCA5M_RAW, gate=False)
        pk = np.zeros(len(ts), np.int8); pk[ai] = ad
        W.append(dict(base=base, ts=ts, Mk=Mk, fixed=fixed, bias=bias, pk=pk,
                      smooth=np.asarray(px, float), close=base['close'].to_numpy(float)))

    def walk(price, i, d):
        seg = price[i + 1:i + 1 + CAP]
        if len(seg) == 0:
            return None
        rel = (seg - price[i]) / price[i] * 100 * d; hit = np.where(rel >= TAKE)[0]
        if not len(hit):
            return None
        return float(np.maximum(0.0, -rel[:int(hit[0]) + 1]).max()) if hit[0] > 0 else 0.0

    print(f'px-basis ablation · {len(top)} top combos · {len(W)} grind windows · lookback per combo')
    print(f'{"combo":>34} {"n_sm":>5}{"medSmooth":>10}{"n_cl":>5}{"medClose":>10}{"Δmed":>8}')
    rows = []
    for t in top:
        k, r, s, ks, bl, bm, bs, mask, lb = (t['k_len'], t['rsi'], t['stc'], t['k_src'],
                                             t['bb_len'], t['bb_mult'], t['bb_src'], t['exit_mask'], t['lookback'])
        sm_all, cl_all = [], []
        for w in W:
            fam = {**s30r, 'k': {**s30r['k'], 'k_len': k, 'rsi_len': r, 'stc_len': s, 'src': ks},
                   'exit_support': {**sup0, 'bb_len': bl, 'bb_mult': bm, 'src': bs}, 'exit_mask': mask}
            srs = det._run_family(fam, w['base'], w['ts'])[3]['state']
            srnz = np.where(srs == 0, 99, srs)
            cb = np.minimum(w['fixed'], srnz); cb = np.where(cb == 99, 0, cb).astype(np.int8)[w['Mk']]
            pkm = w['pk'][w['Mk']]; bm_ = w['bias'][w['Mk']]; sm = w['smooth'][w['Mk']]; cl = w['close'][w['Mk']]
            g3 = np.flatnonzero((cb[1:] == 3) & (cb[:-1] != 3)) + 1
            for i in np.flatnonzero((pkm != 0) & (pkm == bm_)):
                if not len(g3) or np.min(np.abs(g3 - i)) > lb:
                    continue
                d = int(pkm[i])
                vs = walk(sm, i, d); vc = walk(cl, i, d)
                if vs is not None and vs <= STOPMAX:
                    sm_all.append(vs)
                if vc is not None and vc <= STOPMAX:
                    cl_all.append(vc)
        ms = float(np.median(sm_all)) if sm_all else float('nan')
        mc = float(np.median(cl_all)) if cl_all else float('nan')
        rows.append((ms, mc))
        print(f'  k{k} r{r} s{s}/{ks:>5} bb{bl}/{bm:.2f}/{bs:>5} m{mask} lb{lb:>2} '
              f'{len(sm_all):>5}{ms:>10.3f}{len(cl_all):>5}{mc:>10.3f}{mc-ms:>+8.3f}')
    sm = np.array([r[0] for r in rows]); cl = np.array([r[1] for r in rows])
    d = cl - sm; d = d[~np.isnan(d)]
    print(f'\\nverdict: median Δ(close−smooth) = {np.median(d):+.4f}  (mean {np.mean(d):+.4f}, max |Δ| {np.nanmax(np.abs(d)):.4f})')
    print('  ~0 ⇒ basis innocent (placement is real); large + ⇒ px_smooth was UNDER-counting adverse (inflating)')
    db.disconnect()


if __name__ == '__main__':
    main()
