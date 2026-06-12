"""
s30_exit_lever — is the EXIT the fee-lever, or is the entry's swing-follow rate the cap?

Champion entry (k5 r17 s9, src hlcc4, bny30-bias-gated) over 11 windows. Run it through
4 exits and compare net-of-fee edge: favourable-mask BB (bb9/1.20/hl2, the stage-1 winner),
fixed +0.7%/+0.5% take-profits, and hold-to-45min-cap — all with the 0.33% stop. If none
clears taker (~0.11%), the exit isn't the lever; the ~25% swing-follow rate is.
"""
import sys, time
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import logging
for n in ('BybitKlineClient', 'BLDetect', 'KlineLoader', 'DatabaseManager'):
    logging.getLogger(n).setLevel('ERROR')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.bl_detect import BLDetect, FENCE_HI, FENCE_LO
from optimus9.compute.breaching_line import BreachingLine
from optimus9.orchestration.gate_signal_sweep import bny30_oob_side

STOP, CAP, OOBH, OOBL = 0.33, 540, 85.0, 15.0
NWIN, STEP_D, DAY_MS = 11, 3, 86400000
TAKER, MAKER = 0.11, 0.04
KCFG = dict(k_len=5, rsi_len=17, stc_len=9, src='hlcc4')
BBCFG = dict(bb_len=9, bb_mult=1.20, src='hl2')


def latched_bias(oob):
    b = np.zeros(len(oob), np.int8); cur = 0
    for i in range(len(oob)):
        if oob[i] != 0 and (i == 0 or oob[i - 1] == 0):
            cur = -int(oob[i])
        b[i] = cur
    return b


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    dmax = int(db.execute('SELECT MAX(kc_timestamp) m FROM kline_collection WHERE kc_tp_pk=1', fetch=True)[0]['m'])
    det = BLDetect(db, lookback_hours=24, warmup_hours=12)
    c = det._cfg; fp = float(c['blc_fence_pad'])
    bl = BreachingLine(mult=6, curl_floor=float(c['blc_curl_floor']), curl_lookback=int(c['blc_curl_lookback']),
                       pseudo_cross=float(c['blc_pseudo_cross']), grace=int(c['blc_grace']),
                       exit2_ref=str(c['blc_exit2_ref']), exit_mask=7, bb_pad=float(c['blc_bb_pad']),
                       fence_hi=FENCE_HI + fp, fence_lo=FENCE_LO - fp)
    EXITS = ['favmask', 'tp0.7', 'tp0.5', 'cap']
    agg = {e: dict(n=0, wins=0, pnl=0.0, nets=[]) for e in EXITS}

    for i in range(NWIN):
        base, ts, ws, _, _ = det._setup(dmax - i * STEP_D * DAY_MS)
        Mk = ts >= ws
        if Mk.sum() < 1000:
            continue
        rc = base['close'].to_numpy(float)[Mk]; n = len(rc)
        bias = latched_bias(bny30_oob_side(base))[Mk]
        kline = det._line(base, {'kind': 'k', 'tf_seconds': 30, **KCFG})[Mk]
        lo = kline < OOBL; hi = kline > OOBH
        lo_on = np.flatnonzero(lo & ~np.concatenate([[False], lo[:-1]]))
        hi_on = np.flatnonzero(hi & ~np.concatenate([[False], hi[:-1]]))
        bars = np.concatenate([lo_on, hi_on]).astype(np.int64)
        dirs = np.concatenate([np.ones(len(lo_on), np.int8), -np.ones(len(hi_on), np.int8)])
        keep = dirs == bias[bars]; bars, dirs = bars[keep], dirs[keep]
        # favourable-mask exit structures
        cyc = ts // 30000; seam = np.empty(len(ts), bool); seam[0] = True; seam[1:] = cyc[1:] != cyc[:-1]
        pctb = det._line(base, {'kind': 'bb', 'tf_seconds': 30, **BBCFG})
        st = bl.run_bb(pctb, seam=seam)['state'][Mk]; pm = pctb[Mk]
        active = (st == 1) | (st == 2) | (st == 3)
        exhi = np.flatnonzero(active & (pm > OOBH)).astype(np.int64)
        exlo = np.flatnonzero(active & (pm < OOBL)).astype(np.int64)
        for e, d in zip(bars, dirs):
            seg = rc[e + 1:e + 1 + CAP]
            if len(seg) == 0:
                continue
            rel = (seg - rc[e]) / rc[e] * 100 * d
            stp = np.where(rel <= -STOP)[0]; stp = int(stp[0]) if len(stp) else 10 ** 9
            for ex in EXITS:
                if ex == 'favmask':
                    arr = exhi if d == 1 else exlo
                    p = np.searchsorted(arr, e, side='right'); xb = int(arr[p]) - e - 1 if p < len(arr) else len(rel) - 1
                    xb = min(xb, len(rel) - 1)
                    pnl = -STOP if (stp <= xb) else float(rel[xb])
                elif ex == 'cap':
                    pnl = -STOP if stp < len(rel) else float(rel[-1])
                else:
                    tp = float(ex[2:]); tphit = np.where(rel >= tp)[0]; tphit = int(tphit[0]) if len(tphit) else 10 ** 9
                    pnl = (-STOP if stp < tphit else tp) if min(stp, tphit) < 10 ** 9 else float(rel[-1])
                a = agg[ex]; a['n'] += 1; a['wins'] += (pnl > 0); a['pnl'] += pnl

    print(f'champion entry k{KCFG["k_len"]} r{KCFG["rsi_len"]} s{KCFG["stc_len"]}/{KCFG["src"]} · 11 windows')
    print(f'{"exit":>10}{"n":>7}{"win%":>7}{"gross":>8}{"net_taker":>10}{"net_maker":>10}')
    for ex in EXITS:
        a = agg[ex]; mean = a['pnl'] / a['n'] if a['n'] else 0
        print(f'{ex:>10}{a["n"]:>7}{a["wins"]/a["n"]*100:>7.1f}{mean:>8.3f}{mean-TAKER:>+10.3f}{mean-MAKER:>+10.3f}')
    db.disconnect()


if __name__ == '__main__':
    main()
