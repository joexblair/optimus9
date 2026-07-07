"""gate_target_sweep.py — Stage 3 of Joe's arm-to-gate challenge (0707). NO pnl.

Goal: find the arm config whose events land INSIDE the s3s4 process [proc_start, gate_open] or JUST BEFORE it
[proc_start-J, proc_start] for the GOOD gates (best MAE-to-swing). Metric = hit-rate = fraction of good gates that have
an arm event (same es) in [proc_start-J, gate_open]. Arm-event pool uses BOTH delayed (predicted -> r-reversal, wob)
and non-delayed (else -> m-breach). Sweep arm_TF x m_len x r_TF x wob. Same report structure as the perm sweep:
per-combo table `gate_target_summary` + console top-20 by hit-rate.

Definitions (Joe 0707, refinable): GOOD_MAE=-0.15 (top ~25%) · J=90s ('just before'). Gates + arms computed in ONE
window so times align. Run:  python3 gate_target_sweep.py
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
from optimus9.analysis.lr_v2 import _mage_rev, v2_arm, gate_open

SWING_PCT = 0.9
GOOD_MAE = -0.15                 # good gate = MAE-to-swing better than this (top ~25%)
J_MS = 90 * 1000                 # 'just before' window
LENS = range(5, 12)
WOBS = [4, 5, 6, 7, 8]
TFS = [("s5", 300, 0.4, 0.83), ("s7", 420, 0.5, 0.74), ("s10", 600, 0.5, 0.70)]
RTFS = ["s5", "s7", "s10"]


def overrides():
    o = {}
    for p, tf, mmult, Mmult in TFS:
        o["%sM" % p] = (tf, ("bb", 37, Mmult, "ohlc4"), "emerging")
        o["%sr" % p] = (tf, ("k", 6, 6, 5, "close"), "emerging")
        for L in LENS:
            o["%sm%d" % (p, L)] = (tf, ("bb", L, mmult, "ohlc4"), "emerging")
    return o


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    cfg = lr_config(dev); HI, LO = cfg.hi, cfg.lo
    W = bm.BiasWindow(dev, int(time.time() * 1000), lookback=336, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS),
                      line_overrides=overrides())
    ts = np.asarray(W.ts); px = np.asarray(W.px, float); n = len(ts)
    days = (int(ts[-1]) - int(ts[0])) / 86400000.0
    v0 = int(np.argmax(~np.isnan(px)))
    piv = [pp[0] + v0 for pp in find_pivots(px[v0:], SWING_PCT)]

    # --- good gates (MAE-to-swing better than GOOD_MAE): windows [proc_start-J, gate_open] per es ---
    good = {1: [], -1: []}                                            # es -> [(lo_ms, hi_ms)]
    for (i, es, bd, open_k, reason, cap) in gate_open(W, cfg, v2_arm(W, cfg)):
        j = bisect.bisect_right(piv, int(open_k))
        if j >= len(piv):
            continue
        fav = -es * (px[open_k:piv[j] + 1] - px[open_k]) / px[open_k] * 100.0
        if fav.size and float(np.nanmin(fav)) > GOOD_MAE:
            good[es].append((int(ts[i]) - J_MS, int(ts[open_k])))
    for es in good:
        good[es].sort()
    ngood = {es: len(good[es]) for es in good}

    def hit_rate(events):
        """fraction of good gates (per es) that contain >=1 arm event of that es in their [lo,hi] window."""
        ev = {1: sorted(t for t, e in events if e == 1), -1: sorted(t for t, e in events if e == -1)}
        hit = tot = 0
        for es in (1, -1):
            for lo, hi in good[es]:
                tot += 1
                k = bisect.bisect_left(ev[es], lo)
                if k < len(ev[es]) and ev[es][k] <= hi:
                    hit += 1
        return hit, tot

    rlines = {j: np.asarray(W.line("%sr" % j), float) for j in RTFS}
    rrev = {(j, w): np.asarray(_mage_rev(rlines[j], w)) for j in RTFS for w in WOBS}
    summ = []
    for p, tf, mmult, Mmult in TFS:
        M = np.asarray(W.line("%sM" % p), float)
        for L in LENS:
            m = np.asarray(W.line("%sm%d" % (p, L)), float)
            msign = np.where(m >= HI, 1, np.where(m <= LO, -1, 0))
            arms = [(i, int(msign[i])) for i in range(1, n) if msign[i] != 0 and msign[i] != msign[i - 1]]
            eps = {b: next((k for k in range(b + 1, n) if msign[k] != es), n) for b, es in arms}
            for j in RTFS:
                rj = rlines[j]; pred = predict_breach(rj, m, M, HI, LO, FENCE_HI, FENCE_LO)
                pf = {b: next((k for k in range(b, eps[b]) if pred[k] == es), None) for b, es in arms}
                for w in WOBS:
                    rv = rrev[(j, w)]; events = []
                    for b, es in arms:
                        anchor = b                                   # non-delayed default (m-breach)
                        if pf[b] is not None:
                            rk = next((k for k in range(pf[b], eps[b]) if rv[k] == -es), None)
                            if rk is not None:
                                anchor = rk                          # delayed (r-reversal)
                        events.append((int(ts[anchor]), es))
                    hit, tot = hit_rate(events)
                    summ.append((p, L, j, w, len(events), hit, tot, round(hit / tot, 4) if tot else 0.0))

    dev.execute("DROP TABLE IF EXISTS gate_target_summary")
    dev.execute("""CREATE TABLE gate_target_summary (
        id INT AUTO_INCREMENT PRIMARY KEY, arm_tf VARCHAR(4), m_len TINYINT, r_tf VARCHAR(4), wob TINYINT,
        n_arms INT, gates_hit INT, gates_total INT, hit_rate FLOAT, KEY k_hr (hit_rate))""")
    dev.executemany("INSERT INTO gate_target_summary (arm_tf,m_len,r_tf,wob,n_arms,gates_hit,gates_total,hit_rate) "
                    "VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", summ)
    print("wrote %d combos -> gate_target_summary  (%dd; good gates: es+1=%d es-1=%d, MAE>%.2f, J=%ds)\n"
          % (len(summ), round(days), ngood[1], ngood[-1], GOOD_MAE, J_MS // 1000))
    print("TOP-20 by hit-rate (arm events land in good-gate windows):")
    print("%-4s %4s %-4s %4s %7s %7s %7s %8s" % ("aTF", "len", "rTF", "wob", "n_arms", "hit", "total", "hit_rate"))
    for p, L, j, w, na, hit, tot, hr in sorted(summ, key=lambda s: -s[7])[:20]:
        print("%-4s %4d %-4s %4d %7d %7d %7d %8.3f" % (p, L, j, w, na, hit, tot, hr))
    dev.disconnect()


if __name__ == "__main__":
    main()
