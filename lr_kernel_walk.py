"""
lr_kernel_walk.py (Joe 0630) — the kernel WALK. Reuse lr_detect's arm (s6m) + reversal unchanged; replace the
finisher with: entry = first of (s3r OR s4r predict-then-breach, setup side) OR (s2M reversal toward the trade
side, boundary-agnostic wobslay). MAE/MFE off lr_walk (swing_detect). Compare to the current 145.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import numpy as np
import datetime as dtm
from datetime import timezone
from collections import Counter
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_detect, lr_walk, lr_config
from optimus9.compute.indicator_computer import IndicatorComputer as IC
from optimus9.compute.breaching_line import predict_breach
from optimus9.constants import FENCE_HI, FENCE_LO


def ms(s): return int(dtm.datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp() * 1000)


db = DatabaseManager(**get_db_config()); db.connect()
cfg = bm.BiasConfig(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m', xm45=False,
                    mae=0.4, target=0.9, floater_anchor='last', verdict='pk', trigger_src='hlc3')
R1 = ms('2026-06-22 00:00'); START = ms('2026-06-17 00:00')
W = bm.BiasWindow(db, R1, cfg=cfg); lrcfg = lr_config(db)
ts, px, hi, lo, n = W.ts, W.px, lrcfg.hi, lrcfg.lo, len(W.ts)

base_mae = np.array([r[4] for r in lr_walk(W, lr_detect(W, lrcfg, start_ms=START), lrcfg)])

al = lrcfg.arms[0].lines[0].name                                  # s6m
s6c = W._line(al); s6 = W._line_emerging(al)
sign = np.where(s6c >= hi, 1, np.where(s6c <= lo, -1, 0))
wob6 = IC.wobble_slayer(s6, lrcfg.wob_n, hi, lo, anchored=True, strict=True)
s3r, s3m, s3M = W._line('s3r'), W._line('s3m'), W._line('s3M')
s4r, s4m, s4M = W._line('s4r'), W._line('s4m'), W._line('s4M')
pred3 = predict_breach(s3r, s3m, s3M, hi, lo, FENCE_HI, FENCE_LO)
pred4 = predict_breach(s4r, s4m, s4M, hi, lo, FENCE_HI, FENCE_LO)
# s2M reversal = the CLOSED s2M's slope flipping (down→up = +1, up→down = -1); boundary-agnostic, no wobslay
_s2M = W._line('s2M'); _d = np.diff(_s2M); rev2 = np.zeros(n, np.int8); _last = 0
for _k in range(1, n):
    _step = _d[_k - 1]
    if _step > 0:
        if _last < 0:
            rev2[_k] = 1
        _last = 1
    elif _step < 0:
        if _last > 0:
            rev2[_k] = -1
        _last = -1


def new_entry(rj, es):
    """s3r OR s4r predict-then-breach (arms) → THEN the first s2M reversal toward the trade side IS the entry."""
    bd = -es
    p3 = p4 = armed = False
    for k in range(rj + 1, min(n, rj + lrcfg.horizon)):
        if pred3[k] == es:
            p3 = True
        if pred4[k] == es:
            p4 = True
        s3b = (s3r[k] >= hi) if es == 1 else (s3r[k] <= lo)
        s4b = (s4r[k] >= hi) if es == 1 else (s4r[k] <= lo)
        if (p3 and s3b) or (p4 and s4b):
            armed = True                                  # the s3r/s4r confirmation
        if armed and rev2[k] == bd:                       # THEN s2M slope-flip = the entry
            return k
    return None


entries, trigs = [], []
i = 1
while i < n:
    if sign[i] != 0 and sign[i] != sign[i - 1]:
        es = int(sign[i]); rj = None
        for j in range(i, min(n, i + lrcfg.horizon)):
            if sign[j] == -es:
                break
            if wob6[j] == -es and j - lrcfg.wob_n >= 0 and abs(s6[j] - s6[j - lrcfg.wob_n]) >= lrcfg.floor:
                rj = j; break
        if rj is not None:
            k = new_entry(rj, es)
            if k is not None and ts[k] >= START:
                entries.append((int(ts[k]), es, -es, k))
        i = next((kk for kk in range(i + 1, n) if sign[kk] != es), n)
        continue
    i += 1

new_mae = np.array([r[4] for r in lr_walk(W, entries, lrcfg)])


def stats(m):
    return f"n={len(m):3}  medMAE={np.median(m):.2f}%  meanMAE={np.mean(m):.2f}%  %MAE<0.5={np.mean(m < 0.5) * 100:.0f}%" if len(m) else "n=0"


print(f"baseline (current finisher):       {stats(base_mae)}")
print(f"s3r/s4r-armed → s2M-reversal walk: {stats(new_mae)}")
db.disconnect()
