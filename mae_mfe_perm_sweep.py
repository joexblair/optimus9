"""mae_mfe_perm_sweep.py — causal-arm-delay permutation sweep for the spec redesign (Joe 0707). NO pnl.

GOAL: use r-PREDICTION+REVERSAL to DELAY the arm (the causal replacement for the look-ahead arm_delay). The arm line
(m + its Mage, same TF) can be predicted by an r from ANY of the 3 TF sets. Sweep the prediction permutations + wob +
m_len, score MAE/MFE (bd=-es signed) to the next >=0.9% swing.

Dimensions: arm_TF{s5,s7,s10} x m_len{5..11} x r_TF{s5,s7,s10} x wob{WOBS} .
Per arm (m_i OOB breach): PREDICTED = predict_breach(r_j,m_i,M_i)==es while m_i OOB -> delay anchor = first bar after
the predict where r_j reverses toward bd (_mage_rev(r_j,wob), boundary-agnostic). NOT predicted -> anchor = m-breach.

Writes per-combo medians to `mae_mfe_summary` (pk_optimizer). Prints top-20 predicted by MFE/|MAE|. Lines via
line_overrides (no seeds); s10 borrows s7 shapes at itf 600s.
Run:  python3 mae_mfe_perm_sweep.py
"""
import time, bisect
import numpy as np

import bias_machine as bm
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.lr import lr_config
from sweep_eval import BASE_BIAS
from optimus9.compute.swing_detect import find_pivots
from optimus9.compute.breaching_line import predict_breach, FENCE_HI, FENCE_LO
from optimus9.analysis.lr_v2 import _mage_rev

SWING_PCT = 0.9
LENS = range(5, 12)
WOBS = [4, 5, 6, 7, 8]
TFS = [("s5", 300, 0.4, 0.83), ("s7", 420, 0.5, 0.74), ("s10", 600, 0.5, 0.70)]   # (prefix, itf, m_mult, M_mult)
RTFS = ["s5", "s7", "s10"]


def overrides():
    o = {}
    for p, tf, mmult, Mmult in TFS:
        o["%sM" % p] = (tf, ("bb", 37, Mmult, "ohlc4"), "emerging")
        o["%sr" % p] = (tf, ("k", 6, 6, 5, "close"), "emerging")
        for L in LENS:
            o["%sm%d" % (p, L)] = (tf, ("bb", L, mmult, "ohlc4"), "emerging")
    return o


def score(anchor, es, px, piv):
    j = bisect.bisect_right(piv, int(anchor))
    if j >= len(piv):
        return None
    fav = -es * (px[anchor:piv[j] + 1] - px[anchor]) / px[anchor] * 100.0
    return (float(np.nanmin(fav)), float(np.nanmax(fav))) if fav.size else None


def med(vals):
    if not vals:
        return (0, None, None, None)
    mae = np.array([v[0] for v in vals]); mfe = np.array([v[1] for v in vals])
    return (len(vals), float(np.median(mae)), float(np.median(mfe)),
            float(np.median(mfe / np.maximum(np.abs(mae), 1e-9))))


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    cfg = lr_config(dev); HI, LO = cfg.hi, cfg.lo
    W = bm.BiasWindow(dev, int(time.time() * 1000), lookback=336, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS),
                      line_overrides=overrides())
    ts = np.asarray(W.ts); px = np.asarray(W.px, float); n = len(ts)
    days = (int(ts[-1]) - int(ts[0])) / 86400000.0
    v0 = int(np.argmax(~np.isnan(px)))
    piv = [pp[0] + v0 for pp in find_pivots(px[v0:], SWING_PCT)]

    rlines = {j: np.asarray(W.line("%sr" % j), float) for j in RTFS}
    rrev = {(j, w): np.asarray(_mage_rev(rlines[j], w)) for j in RTFS for w in WOBS}
    summ = []                                                         # (arm_tf,m_len,r_tf,wob,path,n,MAE,MFE,ratio)
    for p, tf, mmult, Mmult in TFS:
        M = np.asarray(W.line("%sM" % p), float)
        for L in LENS:
            m = np.asarray(W.line("%sm%d" % (p, L)), float)
            msign = np.where(m >= HI, 1, np.where(m <= LO, -1, 0))
            arms = [(i, int(msign[i])) for i in range(1, n) if msign[i] != 0 and msign[i] != msign[i - 1]]
            eps = {b: next((k for k in range(b + 1, n) if msign[k] != es), n) for b, es in arms}
            for j in RTFS:
                rj = rlines[j]; pred = predict_breach(rj, m, M, HI, LO, FENCE_HI, FENCE_LO)
                predk = {}                                           # arm -> (predicted, first_predict_bar)
                for b, es in arms:
                    e = eps[b]
                    pf = next((k for k in range(b, e) if pred[k] == es), None)
                    predk[b] = pf
                notp = [score(b, es, px, piv) for b, es in arms if predk[b] is None]
                notp = [x for x in notp if x]
                summ.append((p, L, j, 0, "not-predicted") + med(notp))
                for w in WOBS:
                    rv = rrev[(j, w)]; pv = []
                    for b, es in arms:
                        pf = predk[b]
                        if pf is None:
                            continue
                        rk = next((k for k in range(pf, eps[b]) if rv[k] == -es), None)
                        if rk is None:
                            continue
                        sc = score(rk, es, px, piv)
                        if sc:
                            pv.append(sc)
                    summ.append((p, L, j, w, "predicted") + med(pv))

    dev.execute("DROP TABLE IF EXISTS mae_mfe_summary")
    dev.execute("""CREATE TABLE mae_mfe_summary (
        id INT AUTO_INCREMENT PRIMARY KEY, arm_tf VARCHAR(4), m_len TINYINT, r_tf VARCHAR(4), wob TINYINT,
        path VARCHAR(14), n INT, mae FLOAT NULL, mfe FLOAT NULL, ratio FLOAT NULL,
        KEY k_path (path), KEY k_ratio (ratio))""")
    dev.executemany("INSERT INTO mae_mfe_summary (arm_tf,m_len,r_tf,wob,path,n,mae,mfe,ratio) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", summ)
    print("wrote %d combo rows -> mae_mfe_summary  (%dd, %d swings)\n" % (len(summ), round(days), len(piv)))
    top = sorted([s for s in summ if s[4] == "predicted" and s[5] >= 100 and s[8] is not None],
                 key=lambda s: -s[8])[:20]
    print("TOP-20 predicted by MFE/|MAE| (n>=100):")
    print("%-4s %4s %-4s %4s %6s %8s %8s %8s" % ("aTF", "len", "rTF", "wob", "n", "MAE", "MFE", "ratio"))
    for p, L, j, w, path, nn, mae, mfe, ratio in top:
        print("%-4s %4d %-4s %4d %6d %+8.3f %+8.3f %8.2f" % (p, L, j, w, nn, mae, mfe, ratio))
    dev.disconnect()


if __name__ == "__main__":
    main()
