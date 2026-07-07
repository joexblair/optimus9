"""mae_mfe_multiwin.py — multi-window repeatability of the causal-arm-delay quality sweep (Joe 0707).

Runs the PREDICTED-path (delayed arm) MFE/|MAE| sweep (arm_TF x m_len x r_TF x wob) over 7-day windows tiling the
SANITISED tape (05-18 -> now; warmup kept inside the span). A combo that stays top across windows = the live config.
Writes per (combo,window) to `mae_mfe_multiwin` + per-combo consistency to `mae_mfe_multiwin_summary`
(median/worst-window ratio + #windows in the per-window top-decile). NO pnl. Run:  python3 mae_mfe_multiwin.py
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
from optimus9.analysis.lr_v2 import _mage_rev

SWING_PCT = 0.9
LENS = range(5, 12)
WOBS = [4, 5, 6, 7, 8]
TFS = [("s5", 300, 0.4, 0.83), ("s7", 420, 0.5, 0.74), ("s10", 600, 0.5, 0.70)]
RTFS = ["s5", "s7", "s10"]
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
    e = SANITISE + dtm.timedelta(days=WARMUP_D + LOOK_D)
    out = []
    while e <= now:
        out.append(e)
        e += dtm.timedelta(days=LOOK_D)
    if not out or (now - out[-1]).days >= 3:
        out.append(now)
    return out


def combos_for_window(dev, end_ms, bcfg, lr, HI, LO):
    W = bm.BiasWindow(dev, end_ms, lookback=LOOK_D * 24, warmup=WARMUP_D * 24, cfg=bcfg, line_overrides=overrides())
    ts = np.asarray(W.ts); px = np.asarray(W.px, float); n = len(ts)
    v0 = int(np.argmax(~np.isnan(px)))
    piv = [pp[0] + v0 for pp in find_pivots(px[v0:], SWING_PCT)]
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
                    rv = rrev[(j, w)]; vals = []
                    for b, es in arms:
                        if pf[b] is None:
                            continue
                        rk = next((k for k in range(pf[b], eps[b]) if rv[k] == -es), None)
                        if rk is None:
                            continue
                        jj = bisect.bisect_right(piv, rk)
                        if jj >= len(piv):
                            continue
                        fav = -es * (px[rk:piv[jj] + 1] - px[rk]) / px[rk] * 100.0
                        if fav.size:
                            vals.append((float(np.nanmin(fav)), float(np.nanmax(fav))))
                    if vals:
                        mae = np.array([x[0] for x in vals]); mfe = np.array([x[1] for x in vals])
                        res[(p, L, j, w)] = (len(vals), float(np.median(mae)), float(np.median(mfe)),
                                             float(np.median(mfe / np.maximum(np.abs(mae), 1e-9))))
    return res


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    cfg = lr_config(dev); HI, LO = cfg.hi, cfg.lo
    bcfg = bm.BiasConfig(**BASE_BIAS)
    ends = window_ends()
    dev.execute("DROP TABLE IF EXISTS mae_mfe_multiwin")
    dev.execute("""CREATE TABLE mae_mfe_multiwin (id INT AUTO_INCREMENT PRIMARY KEY, arm_tf VARCHAR(4), m_len TINYINT,
        r_tf VARCHAR(4), wob TINYINT, win_end DATETIME, n INT, mae FLOAT, mfe FLOAT, ratio FLOAT)""")
    per = {}                                                          # combo -> [ratio per window]
    for wi, end in enumerate(ends):
        res = combos_for_window(dev, int(end.timestamp() * 1000), bcfg, lr_config(dev), HI, LO)
        ratios = sorted(v[3] for v in res.values())
        top_dec = ratios[int(0.9 * len(ratios))] if ratios else 0
        rows = []
        for (p, L, j, w), (nn, mae, mfe, ratio) in res.items():
            rows.append((p, L, j, w, end.strftime("%Y-%m-%d"), nn, round(mae, 4), round(mfe, 4), round(ratio, 4)))
            per.setdefault((p, L, j, w), []).append((ratio, ratio >= top_dec))
        dev.executemany("INSERT INTO mae_mfe_multiwin (arm_tf,m_len,r_tf,wob,win_end,n,mae,mfe,ratio) "
                        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)", rows)
        print("window %d/%d ending %s: %d combos, top-decile ratio>=%.2f" % (
            wi + 1, len(ends), end.strftime("%Y-%m-%d"), len(res), top_dec), flush=True)

    summ = []
    nwin = len(ends)
    for (p, L, j, w), lst in per.items():
        rs = [x[0] for x in lst]; ntop = sum(1 for x in lst if x[1])
        summ.append((p, L, j, w, len(lst), round(float(np.median(rs)), 4), round(float(np.min(rs)), 4), ntop))
    dev.execute("DROP TABLE IF EXISTS mae_mfe_multiwin_summary")
    dev.execute("""CREATE TABLE mae_mfe_multiwin_summary (id INT AUTO_INCREMENT PRIMARY KEY, arm_tf VARCHAR(4),
        m_len TINYINT, r_tf VARCHAR(4), wob TINYINT, n_win INT, median_ratio FLOAT, worst_ratio FLOAT, n_top_decile INT,
        KEY k_med (median_ratio))""")
    dev.executemany("INSERT INTO mae_mfe_multiwin_summary (arm_tf,m_len,r_tf,wob,n_win,median_ratio,worst_ratio,"
                    "n_top_decile) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", summ)
    print("\n%d windows -> mae_mfe_multiwin + _summary\nTOP-20 by median ratio (need n_win=%d for full coverage):"
          % (nwin, nwin))
    print("%-4s %4s %-4s %4s %5s %8s %8s %6s" % ("aTF", "len", "rTF", "wob", "nwin", "medRatio", "worst", "nTopD"))
    for p, L, j, w, nw, med, worst, ntop in sorted(summ, key=lambda s: -s[5])[:20]:
        print("%-4s %4d %-4s %4d %5d %8.2f %8.2f %6d" % (p, L, j, w, nw, med, worst, ntop))
    dev.disconnect()


if __name__ == "__main__":
    main()
