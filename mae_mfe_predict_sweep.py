"""mae_mfe_predict_sweep.py — multi-dim arm A/B for the spec redesign (Joe 0707). NO pnl, NO arm-delay.

Sweep: TF in {s5,s7,s10} x m-line bb_len in {5..11}. Per arm (m-line OOB breach) apply the PREDICTION logic, pick an
anchor, score MAE/MFE (bd=-es signed) to the next >=0.9% swing. Dumps EVERY arm to o9's analysis DB table
`mae_mfe_sweep` (raw, per-event — not GrindStore, which is KPI-first). Also prints the median table. All lines via
line_overrides (no seeds); s10 borrows s7 shapes (m 0.5/ohlc4, M 37|0.70/ohlc4, r k6|6|5|close) at itf 600s.

INTERPRETATION (Joe: correct any before trusting it) — anchor per m-line OOB breach ("the arm"):
  * episode      = from the m-breach until m leaves that OOB side.
  * r PREDICTED  = predict_breach(r,m,M)==es at any bar DURING the m-OOB episode ("predict while m OOB").
  * PREDICTED    -> anchor = first bar in the episode where r is OOB (same side) AND r slope-flips toward IB
                   ("r reverses OOB"); if r never reverses -> anchor_type='no_reversal' (no MAE/MFE).
  * NOT predicted-> anchor = the m-breach bar (current arm logic).
Run:  python3 mae_mfe_predict_sweep.py
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

SWING_PCT = 0.9
LENS = range(5, 12)
TFS = [("s5", 300, 0.4, 0.83), ("s7", 420, 0.5, 0.74), ("s10", 600, 0.5, 0.70)]   # (prefix, itf, m_mult, M_mult)


def overrides():
    o = {}
    for p, tf, mmult, Mmult in TFS:
        o["%sM" % p] = (tf, ("bb", 37, Mmult, "ohlc4"), "emerging")
        o["%sr" % p] = (tf, ("k", 6, 6, 5, "close"), "emerging")
        for L in LENS:
            o["%sm%d" % (p, L)] = (tf, ("bb", L, mmult, "ohlc4"), "emerging")
    return o


def _dt(ms):
    return dtm.datetime.fromtimestamp(int(ms) / 1000, timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    cfg = lr_config(dev); HI, LO = cfg.hi, cfg.lo
    W = bm.BiasWindow(dev, int(time.time() * 1000), lookback=336, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS),
                      line_overrides=overrides())
    ts = np.asarray(W.ts); px = np.asarray(W.px, float); n = len(ts)
    days = (int(ts[-1]) - int(ts[0])) / 86400000.0
    v0 = int(np.argmax(~np.isnan(px)))
    piv = [pp[0] + v0 for pp in find_pivots(px[v0:], SWING_PCT)]

    rows = []                                                        # per-arm raw
    console = []                                                     # (tf,len,path,n,MAE,MFE,ratio)
    for p, tf, mmult, Mmult in TFS:
        M = np.asarray(W.line("%sM" % p), float); r = np.asarray(W.line("%sr" % p), float)
        for L in LENS:
            m = np.asarray(W.line("%sm%d" % (p, L)), float)
            pred = predict_breach(r, m, M, HI, LO, FENCE_HI, FENCE_LO)
            msign = np.where(m >= HI, 1, np.where(m <= LO, -1, 0))
            arms = [(i, int(msign[i])) for i in range(1, n) if msign[i] != 0 and msign[i] != msign[i - 1]]
            agg = {"predicted": [], "not-predicted": []}
            for b, es in arms:
                e = next((k for k in range(b + 1, n) if msign[k] != es), n)
                predicted = bool(np.any(pred[b:e] == es))
                if predicted:
                    rev = next((k for k in range(b, e) if (r[k] >= HI if es == 1 else r[k] <= LO)
                                and (r[k] < r[k - 1] if es == 1 else r[k] > r[k - 1])), None)
                    anchor, atype = (rev, "r_reversal") if rev is not None else (None, "no_reversal")
                else:
                    anchor, atype = b, "m_breach"
                mae = mfe = swing_ms = None
                if anchor is not None:
                    j = bisect.bisect_right(piv, int(anchor))
                    if j < len(piv):
                        fav = -es * (px[anchor:piv[j] + 1] - px[anchor]) / px[anchor] * 100.0
                        if fav.size:
                            mae, mfe, swing_ms = float(np.nanmin(fav)), float(np.nanmax(fav)), int(ts[piv[j]])
                    if mae is not None:
                        agg["predicted" if predicted else "not-predicted"].append((mae, mfe))
                rows.append((p, L, int(ts[b]), _dt(ts[b]), es, int(predicted), atype,
                             int(ts[anchor]) if anchor is not None else None,
                             mae, mfe, swing_ms))
            for key in ("predicted", "not-predicted"):
                v = agg[key]
                if v:
                    mae = np.array([x[0] for x in v]); mfe = np.array([x[1] for x in v])
                    console.append((p, L, key, len(v), np.median(mae), np.median(mfe),
                                    np.median(mfe / np.maximum(np.abs(mae), 1e-9))))

    # --- write raw to DB ---
    dev.execute("DROP TABLE IF EXISTS mae_mfe_sweep")
    dev.execute("""CREATE TABLE mae_mfe_sweep (
        id BIGINT AUTO_INCREMENT PRIMARY KEY, tf VARCHAR(4), m_len TINYINT, arm_ms BIGINT, arm_dt DATETIME,
        es TINYINT, predicted TINYINT, anchor_type VARCHAR(12), anchor_ms BIGINT NULL, mae FLOAT NULL, mfe FLOAT NULL,
        swing_ms BIGINT NULL, KEY k_tf_len (tf, m_len), KEY k_pred (predicted), KEY k_atype (anchor_type))""")
    dev.executemany("INSERT INTO mae_mfe_sweep (tf,m_len,arm_ms,arm_dt,es,predicted,anchor_type,anchor_ms,mae,mfe,"
                    "swing_ms) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", rows)
    print("wrote %d arm rows -> mae_mfe_sweep  (%dd, %d swings)\n" % (len(rows), round(days), len(piv)))
    print("%-4s %4s %-14s %6s %8s %8s %9s" % ("TF", "len", "path", "n", "MAE", "MFE", "MFE/|MAE|"))
    for p, L, key, nn, mae, mfe, ratio in console:
        print("%-4s %4d %-14s %6d %+8.3f %+8.3f %9.2f" % (p, L, key, nn, mae, mfe, ratio))
    dev.disconnect()


if __name__ == "__main__":
    main()
