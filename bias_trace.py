"""bias_trace.py — the cascade's per-30s condition trace, persisted. (Joe 0713)

Every rung's LINE VALUE and its TRUE/FALSE, one row per eval-grid sample, into `bias_trace` (`bt_`).
The picture (bias_emit.py) says WHERE it fired; this says WHY it did or didn't, and it's queryable —
no re-run to ask a new question of the same window.

Rungs (same producers as bias_emit — nothing re-implemented here):
  1  s20m OOB on es            (sampled at s20's 1/4-TF seam, held)
  2  s10r predicted on es      (sampled at s10's 1/4-TF seam, held)
  3  |s10m - s10r| now  <  |s10m - s10r| at the previous 1/4-TF seam
  4  s1m OOB on es  AND  s1m crosses s1r toward 50   (cross measured on the eval grid)

Also carries `bt_s10r_closed` — the closed-value line beside the emerging one, so the flat-r question
stays visible in the data instead of needing a special run.

  python3 bias_trace.py 2026-07-13_16:49 2026-07-13_17:15          (UTC, inclusive)
"""
import sys, datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.analysis.jig import Jig
from optimus9 import DatabaseManager
from optimus9.config import get_db_config
import bias_emit as BE

CFG_TAG = 'j0713'

DDL = """CREATE TABLE IF NOT EXISTS bias_trace(
  bt_pk INT AUTO_INCREMENT PRIMARY KEY, bt_cfg VARCHAR(24),
  bt_ts BIGINT, bt_dt DATETIME, bt_px DOUBLE,
  bt_s20m FLOAT, bt_c1_hi TINYINT, bt_c1_lo TINYINT,
  bt_s10r FLOAT, bt_s10r_closed FLOAT, bt_pred10 TINYINT, bt_c2_hi TINYINT, bt_c2_lo TINYINT,
  bt_s10m FLOAT, bt_gap FLOAT, bt_gap_pre FLOAT, bt_c3 TINYINT,
  bt_s1m FLOAT, bt_s1r FLOAT, bt_oob_hi TINYINT, bt_oob_lo TINYINT, bt_x30 TINYINT,
  bt_c4_hi TINYINT, bt_c4_lo TINYINT,
  bt_all VARCHAR(4),
  UNIQUE KEY u_row (bt_cfg, bt_ts), KEY k_dt (bt_dt))"""

COLS = ("bt_cfg,bt_ts,bt_dt,bt_px,bt_s20m,bt_c1_hi,bt_c1_lo,bt_s10r,bt_s10r_closed,bt_pred10,"
        "bt_c2_hi,bt_c2_lo,bt_s10m,bt_gap,bt_gap_pre,bt_c3,bt_s1m,bt_s1r,bt_oob_hi,bt_oob_lo,"
        "bt_x30,bt_c4_hi,bt_c4_lo,bt_all")

U = lambda s: dtm.datetime.strptime(s, '%Y-%m-%d_%H:%M').replace(tzinfo=timezone.utc)
t_beg, t_end = U(sys.argv[1]), U(sys.argv[2])
T0, T1 = int(t_beg.timestamp() * 1000), int(t_end.timestamp() * 1000)

with Jig(T1 + 3600_000, hours=6, warmup=90, overrides=BE.overrides([BE.TF_FAST, BE.TF_MID, BE.TF_COARSE])) as j:
    C, W = j.causal, j.W
    ts, px = np.asarray(j.ts, np.int64), np.asarray(j.px, float)
    sc = BE.TF_COARSE * 60 // BE.SEAM_DIV * 1000
    sm = BE.TF_MID * 60 // BE.SEAM_DIV * 1000

    s20m = C.line(f's{BE.TF_COARSE}m')
    s10m, s10r = C.line(f's{BE.TF_MID}m'), C.line(f's{BE.TF_MID}r')
    s10r_cls = np.asarray(W._line(f's{BE.TF_MID}r'), float)      # the closed line, beside the emerging one
    s1m, s1r = C.line(f's{BE.TF_FAST}m'), C.line(f's{BE.TF_FAST}r')

    sg20, sg1 = C.sign(f's{BE.TF_COARSE}m'), C.sign(f's{BE.TF_FAST}m')
    pred10 = C.predict_set(f's{BE.TF_MID}', tol=BE.PREDICT_TOL, maj='Mage')
    c1h, c1l = C.seam_hold(sg20 == 1, sc), C.seam_hold(sg20 == -1, sc)
    c2h, c2l = C.seam_hold(pred10 == 1, sm), C.seam_hold(pred10 == -1, sm)
    mp, rp = C.seam_prev(f's{BE.TF_MID}m', sm), C.seam_prev(f's{BE.TF_MID}r', sm)
    gap, gap_pre = np.abs(s10m - s10r), np.abs(mp - rp)
    c3 = gap < gap_pre
    x = C.cross(f's{BE.TF_FAST}m', f's{BE.TF_FAST}r', BE.EVAL_MS)

    ks = [k for k in range(len(ts)) if T0 <= ts[k] <= T1 and ts[k] % BE.EVAL_MS == 0]
    rows = []
    for k in ks:
        c4h = bool(sg1[k] == 1 and x[k] == -1)
        c4l = bool(sg1[k] == -1 and x[k] == 1)
        ah = bool(c1h[k] and c2h[k] and c3[k] and c4h)
        al = bool(c1l[k] and c2l[k] and c3[k] and c4l)
        f = lambda v: None if not np.isfinite(v) else round(float(v), 3)
        rows.append((CFG_TAG, int(ts[k]),
                     dtm.datetime.fromtimestamp(ts[k] / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M:%S'),
                     float(px[k]), f(s20m[k]), int(c1h[k]), int(c1l[k]),
                     f(s10r[k]), f(s10r_cls[k]), int(pred10[k]), int(c2h[k]), int(c2l[k]),
                     f(s10m[k]), f(gap[k]), f(gap_pre[k]), int(c3[k]),
                     f(s1m[k]), f(s1r[k]), int(sg1[k] == 1), int(sg1[k] == -1), int(x[k]),
                     int(c4h), int(c4l), 'HI' if ah else ('LO' if al else '')))

d = DatabaseManager(**get_db_config()); d.connect()
d.execute(DDL)
d.execute("DELETE FROM bias_trace WHERE bt_cfg=%s AND bt_ts BETWEEN %s AND %s", (CFG_TAG, T0, T1))
ph = ','.join(['%s'] * len(COLS.split(',')))
d.executemany(f"INSERT INTO bias_trace ({COLS}) VALUES ({ph})", rows)
n = d.execute("SELECT COUNT(*) c FROM bias_trace WHERE bt_cfg=%s", (CFG_TAG,), fetch=True)[0]['c']
d.disconnect()

print(f'bias_trace  cfg={CFG_TAG}   wrote {len(rows)} rows  ({sys.argv[1]} -> {sys.argv[2]}, '
      f'{BE.EVAL_MS//1000}s grid)   table now holds {n}')
print(f'  fires: HI {sum(1 for r in rows if r[-1]=="HI")}  ·  LO {sum(1 for r in rows if r[-1]=="LO")}')
print(f'  knobs: eval {BE.EVAL_MS//1000}s · seam TF/{BE.SEAM_DIV} · predict_tol {BE.PREDICT_TOL} · '
      f'r {BE.R_CFG} · m {BE.M_CFG} · Mage {BE.MAGE_CFG}')
