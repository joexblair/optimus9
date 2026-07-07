"""arm_gate_multiwin.py — combined QUALITY + s3s4-PROXIMITY multi-window sweep (Joe 0707). NO pnl.

For each combo (arm_TF x m_len x r_TF x wob) over 7-day windows tiling the SANITISED tape (05-18+), score BOTH:
  * quality  = median MFE/|MAE| of the delayed arm (predicted -> r-reversal, _mage_rev wob) to next >=0.9% swing.
  * proximity= hit-rate: fraction of GOOD s3s4 gates (MAE-to-swing>-0.15) with an arm event (delayed OR non-delayed,
               same es) in [proc_start-90s, gate_open]. Gate uses the standard dial-in (s2/s3/s4/s1M, s5m arm).
Goal: find the config robust on BOTH across windows (s10=quality, s5=proximity; s6 may bridge). TFs incl s6
(itf360, m .45/ohlc4, M 37|.70/ohlc4, r k6|6|5|close). Writes arm_gate_multiwin (combo x window) + _summary.
Run:  python3 arm_gate_multiwin.py
"""
import time, bisect, datetime as dtm
from datetime import timezone
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
GOOD_MAE = -0.15
J_MS = 90 * 1000
LENS = range(5, 12)
WOBS = [4, 5, 6, 7, 8]
TFS = [("s5", 300, 0.4, 0.83), ("s6", 360, 0.45, 0.70), ("s7", 420, 0.5, 0.74), ("s10", 600, 0.5, 0.70)]
RTFS = ["s5", "s6", "s7", "s10"]
SANITISE = dtm.datetime(2026, 5, 18, tzinfo=timezone.utc)
WARMUP_D, LOOK_D = 2, 7


def overrides():
    o = {}
    for p, tf, mmult, Mmult in TFS:
        o["%sM" % p] = (tf, ("bb", 37, Mmult, "ohlc4"), "emerging")
        o["%sr" % p] = (tf, ("k", 6, 6, 5, "close"), "emerging")
        for L in LENS:
            o["%sm%d" % (p, L)] = (tf, ("bb", L, mmult, "ohlc4"), "emerging")
    return o


def window_ends():
    now = dtm.datetime.now(timezone.utc)
    e = SANITISE + dtm.timedelta(days=WARMUP_D + LOOK_D); out = []
    while e <= now:
        out.append(e); e += dtm.timedelta(days=LOOK_D)
    if not out or (now - out[-1]).days >= 3:
        out.append(now)
    return out


def one_window(dev, end_ms, bcfg, lr, HI, LO):
    W = bm.BiasWindow(dev, end_ms, lookback=LOOK_D * 24, warmup=WARMUP_D * 24, cfg=bcfg, line_overrides=overrides())
    ts = np.asarray(W.ts); px = np.asarray(W.px, float); n = len(ts)
    v0 = int(np.argmax(~np.isnan(px)))
    piv = [pp[0] + v0 for pp in find_pivots(px[v0:], SWING_PCT)]

    good = {1: [], -1: []}
    for (i, es, bd, ok, reason, cap) in gate_open(W, lr, v2_arm(W, lr)):
        jj = bisect.bisect_right(piv, int(ok))
        if jj >= len(piv):
            continue
        fav = -es * (px[ok:piv[jj] + 1] - px[ok]) / px[ok] * 100.0
        if fav.size and float(np.nanmin(fav)) > GOOD_MAE:
            good[es].append((int(ts[i]) - J_MS, int(ts[ok])))
    for es in good:
        good[es].sort()

    def score_swing(anchor, es):
        jj = bisect.bisect_right(piv, int(anchor))
        if jj >= len(piv):
            return None
        fav = -es * (px[anchor:piv[jj] + 1] - px[anchor]) / px[anchor] * 100.0
        return (float(np.nanmin(fav)), float(np.nanmax(fav))) if fav.size else None

    def hit_rate(events):
        ev = {1: sorted(t for t, e in events if e == 1), -1: sorted(t for t, e in events if e == -1)}
        hit = tot = 0
        for es in (1, -1):
            for lo, hi in good[es]:
                tot += 1
                k = bisect.bisect_left(ev[es], lo)
                if k < len(ev[es]) and ev[es][k] <= hi:
                    hit += 1
        return hit / tot if tot else 0.0

    rlines = {j: np.asarray(W.line("%sr" % j), float) for j in RTFS}
    rrev = {(j, w): np.asarray(_mage_rev(rlines[j], w)) for j in RTFS for w in WOBS}
    res = {}
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
                    rv = rrev[(j, w)]; qvals = []; events = []
                    for b, es in arms:
                        anchor = b
                        if pf[b] is not None:
                            rk = next((k for k in range(pf[b], eps[b]) if rv[k] == -es), None)
                            if rk is not None:
                                anchor = rk
                                sc = score_swing(rk, es)
                                if sc:
                                    qvals.append(sc)
                        events.append((int(ts[anchor]), es))
                    ratio = 0.0
                    if qvals:
                        mae = np.array([x[0] for x in qvals]); mfe = np.array([x[1] for x in qvals])
                        ratio = float(np.median(mfe / np.maximum(np.abs(mae), 1e-9)))
                    res[(p, L, j, w)] = (round(ratio, 4), round(hit_rate(events), 4))
    return res


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    cfg = lr_config(dev); HI, LO = cfg.hi, cfg.lo
    bcfg = bm.BiasConfig(**BASE_BIAS)
    ends = window_ends()
    dev.execute("DROP TABLE IF EXISTS arm_gate_multiwin")
    dev.execute("""CREATE TABLE arm_gate_multiwin (id INT AUTO_INCREMENT PRIMARY KEY, arm_tf VARCHAR(4), m_len TINYINT,
        r_tf VARCHAR(4), wob TINYINT, win_end DATETIME, quality FLOAT, proximity FLOAT)""")
    per = {}
    for wi, end in enumerate(ends):
        res = one_window(dev, int(end.timestamp() * 1000), bcfg, lr_config(dev), HI, LO)
        rows = [(p, L, j, w, end.strftime("%Y-%m-%d"), q, hr) for (p, L, j, w), (q, hr) in res.items()]
        dev.executemany("INSERT INTO arm_gate_multiwin (arm_tf,m_len,r_tf,wob,win_end,quality,proximity) "
                        "VALUES (%s,%s,%s,%s,%s,%s,%s)", rows)
        for (p, L, j, w), (q, hr) in res.items():
            per.setdefault((p, L, j, w), []).append((q, hr))
        print("window %d/%d %s: %d combos" % (wi + 1, len(ends), end.strftime("%Y-%m-%d"), len(res)), flush=True)

    summ = []
    for (p, L, j, w), lst in per.items():
        q = [x[0] for x in lst]; h = [x[1] for x in lst]
        summ.append((p, L, j, w, len(lst), round(float(np.median(q)), 4), round(float(np.min(q)), 4),
                     round(float(np.median(h)), 4), round(float(np.min(h)), 4),
                     round(float(np.median(q)) * float(np.median(h)), 4)))
    dev.execute("DROP TABLE IF EXISTS arm_gate_multiwin_summary")
    dev.execute("""CREATE TABLE arm_gate_multiwin_summary (id INT AUTO_INCREMENT PRIMARY KEY, arm_tf VARCHAR(4),
        m_len TINYINT, r_tf VARCHAR(4), wob TINYINT, n_win INT, med_quality FLOAT, worst_quality FLOAT,
        med_prox FLOAT, worst_prox FLOAT, combined FLOAT, KEY k_comb (combined))""")
    dev.executemany("INSERT INTO arm_gate_multiwin_summary (arm_tf,m_len,r_tf,wob,n_win,med_quality,worst_quality,"
                    "med_prox,worst_prox,combined) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", summ)
    nwin = len(ends)
    print("\n%d windows -> arm_gate_multiwin + _summary\nTOP-20 by COMBINED (med_quality x med_prox), n_win=%d:" % (nwin, nwin))
    print("%-4s %4s %-4s %4s %8s %8s %8s %8s %9s" % ("aTF", "len", "rTF", "wob", "medQ", "worstQ", "medProx", "worstP", "combined"))
    for p, L, j, w, nw, mq, wq, mp, wp, comb in sorted([s for s in summ if s[4] == nwin], key=lambda s: -s[9])[:20]:
        print("%-4s %4d %-4s %4d %8.2f %8.2f %8.3f %8.3f %9.3f" % (p, L, j, w, mq, wq, mp, wp, comb))
    dev.disconnect()


if __name__ == "__main__":
    main()
