"""arm_delay_walk.py — manual-walk export of the causal arm-delay events (Joe 0707).

Two configs — BEST (arm s10/len9, predict s10r, wob7) and SWEET (arm s7/len11, predict s10r, wob6). Emits every
DELAYED-arm event (predicted -> arm delayed to where s10r reverses, _mage_rev at that wob) over the last 2 days to
`arm_delay_walk` (utc_dt = the delayed-arm bar). Joe walks these against the s3s4 mechanic. NO pnl. Lines via
line_overrides (no seeds). Run:  python3 arm_delay_walk.py
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
WALK_DAYS = 2
# label: (arm prefix, arm itf, m_len, m_mult, M_mult, r prefix, r itf, wob)
CONFIGS = {
    "best":  ("s10", 600, 9, 0.5, 0.70, "s10", 600, 7),
    "sweet": ("s7", 420, 11, 0.5, 0.74, "s10", 600, 6),
}


def _lo(cfgs):
    o = {}
    for _, (ap, atf, L, mmult, Mmult, rp, rtf, w) in cfgs.items():
        o["%sm%d" % (ap, L)] = (atf, ("bb", L, mmult, "ohlc4"), "emerging")
        o["%sM" % ap] = (atf, ("bb", 37, Mmult, "ohlc4"), "emerging")
        o["%sr" % rp] = (rtf, ("k", 6, 6, 5, "close"), "emerging")
    return o


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    cfg = lr_config(dev); HI, LO = cfg.hi, cfg.lo
    now = int(time.time() * 1000)
    W = bm.BiasWindow(dev, now, lookback=96, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS), line_overrides=_lo(CONFIGS))
    ts = np.asarray(W.ts); px = np.asarray(W.px, float); n = len(ts)
    v0 = int(np.argmax(~np.isnan(px)))
    piv = [pp[0] + v0 for pp in find_pivots(px[v0:], SWING_PCT)]
    cutoff = now - WALK_DAYS * 86400000

    rows = []
    for label, (ap, atf, L, mmult, Mmult, rp, rtf, w) in CONFIGS.items():
        m = np.asarray(W.line("%sm%d" % (ap, L)), float)
        M = np.asarray(W.line("%sM" % ap), float)
        r = np.asarray(W.line("%sr" % rp), float)
        pred = predict_breach(r, m, M, HI, LO, FENCE_HI, FENCE_LO)
        rrev = np.asarray(_mage_rev(r, w))
        msign = np.where(m >= HI, 1, np.where(m <= LO, -1, 0))
        arms = [(i, int(msign[i])) for i in range(1, n) if msign[i] != 0 and msign[i] != msign[i - 1]]
        for b, es in arms:
            e = next((k for k in range(b + 1, n) if msign[k] != es), n)
            pf = next((k for k in range(b, e) if pred[k] == es), None)
            if pf is None:
                continue                                             # not predicted -> not a delayed arm
            rk = next((k for k in range(pf, e) if rrev[k] == -es), None)
            if rk is None or int(ts[rk]) < cutoff:
                continue
            j = bisect.bisect_right(piv, rk)
            if j >= len(piv):
                continue
            fav = -es * (px[rk:piv[j] + 1] - px[rk]) / px[rk] * 100.0
            if not fav.size:
                continue
            dt = dtm.datetime.fromtimestamp(int(ts[rk]) / 1000, timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            rows.append((dt, label, round(float(np.nanmin(fav)), 4), round(float(np.nanmax(fav)), 4)))

    rows.sort(key=lambda x: (x[0], x[1]))
    dev.execute("DROP TABLE IF EXISTS arm_delay_walk")
    dev.execute("""CREATE TABLE arm_delay_walk (
        id INT AUTO_INCREMENT PRIMARY KEY, utc_dt DATETIME, best_or_sweet VARCHAR(5), mae FLOAT, mfe FLOAT)""")
    dev.executemany("INSERT INTO arm_delay_walk (utc_dt,best_or_sweet,mae,mfe) VALUES (%s,%s,%s,%s)", rows)
    byc = {}
    for _, lab, _, _ in rows:
        byc[lab] = byc.get(lab, 0) + 1
    print("wrote %d delayed-arm events -> arm_delay_walk (last %dd): %s" % (len(rows), WALK_DAYS, byc))
    dev.disconnect()


if __name__ == "__main__":
    main()
