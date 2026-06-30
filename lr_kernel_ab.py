"""
lr_kernel_ab.py (Joe 0630) — AB combo sweep over the kernel-walk levers, all jumbled:
  arm line (s6m/s5m) × trigger (s3r-only/s4r-only/OR) × s2M-entry debounce (1/2/3 consecutive bd
  closed-bar steps) × arm wobslay-n. Metric = entry quality {n, medMAE, %MAE<0.5, %MFE>=0.7} — NO
  SL'd PnL. Ranked vs the baseline (s6m·OR·deb1·cfg-wob). floor held at cfg (follow-up sweep).
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import numpy as np, datetime as dtm, copy
from datetime import timezone
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_walk, lr_config, lr_setups
from optimus9.compute.breaching_line import predict_breach
from optimus9.constants import FENCE_HI, FENCE_LO


def ms(s): return int(dtm.datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp() * 1000)


db = DatabaseManager(**get_db_config()); db.connect()
cfg = bm.BiasConfig(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m', xm45=False,
                    mae=0.4, target=0.9, floater_anchor='last', verdict='pk', trigger_src='hlc3')
R1 = ms('2026-06-22 00:00'); START = ms('2026-06-17 00:00')
W = bm.BiasWindow(db, R1, cfg=cfg); lrcfg = lr_config(db)
ts, hi, lo, n = np.array(W.ts), lrcfg.hi, lrcfg.lo, len(W.ts)

# kernel lines — lever-independent, computed ONCE
s3r, s3m, s3M = W._line('s3r'), W._line('s3m'), W._line('s3M')
s4r, s4m, s4M = W._line('s4r'), W._line('s4m'), W._line('s4M')
pred3 = predict_breach(s3r, s3m, s3M, hi, lo, FENCE_HI, FENCE_LO)
pred4 = predict_breach(s4r, s4m, s4M, hi, lo, FENCE_HI, FENCE_LO)
# s2M closed slope: conf = signed run-length of consecutive same-direction steps; rev2 = the flip bar
_s2M = W._line('s2M'); conf = np.zeros(n, np.int32); rev2 = np.zeros(n, np.int8); cur = 0
for k in range(1, n):
    step = _s2M[k] - _s2M[k - 1]
    if step > 0:
        rev2[k] = 1 if cur < 0 else 0; cur = cur + 1 if cur > 0 else 1
    elif step < 0:
        rev2[k] = -1 if cur > 0 else 0; cur = cur - 1 if cur < 0 else -1
    conf[k] = cur


def new_entry(rj, es, cap, trig, deb):
    """arm: s3r/s4r predict-then-breach (trig selects which) → then the s2M reversal held `deb` bd-steps."""
    bd = -es; p3 = p4 = armed = pending = False
    for k in range(rj + 1, cap):
        if pred3[k] == es:
            p3 = True
        if pred4[k] == es:
            p4 = True
        s3b = (s3r[k] >= hi) if es == 1 else (s3r[k] <= lo)
        s4b = (s4r[k] >= hi) if es == 1 else (s4r[k] <= lo)
        c3 = p3 and s3b; c4 = p4 and s4b
        armd = c3 if trig == 's3' else c4 if trig == 's4' else (c3 or c4)
        if armd:
            armed = True
        if armed:
            if rev2[k] == bd:
                pending = True                       # fresh s2M flip toward the trade side
            if pending:
                if conf[k] * bd >= deb:
                    return k                          # held `deb` consecutive bd closed-bar steps
                if conf[k] * bd < 0:
                    pending = False                   # counter-flip — cancel, wait for the next flip
    return None


def run(arm, trig, deb, wob_n):
    c = copy.deepcopy(lrcfg); c.arms[0].lines[0].name = arm; c.wob_n = wob_n
    ent = []
    for _i, rj, es, bd, cap in lr_setups(W, c):
        k = new_entry(rj, es, cap, trig, deb)
        if k is not None and ts[k] >= START:
            ent.append((int(ts[k]), es, -es, k))
    walk = lr_walk(W, ent, lrcfg)
    if not walk:
        return (0, 9.99, 0, 0)
    mae = np.array([r[4] for r in walk]); mfe = np.array([r[5] for r in walk])
    return (len(walk), float(np.median(mae)), float(np.mean(mae < 0.5) * 100), float(np.mean(mfe >= 0.7) * 100))


W0 = lrcfg.wob_n
rows = [(arm, trig, deb, wn) + run(arm, trig, deb, wn)
        for arm in ('s6m', 's5m') for trig in ('s3', 's4', 'or') for deb in (1, 2, 3) for wn in (W0, W0 + 3)]
base = [r for r in rows if r[:4] == ('s6m', 'or', 1, W0)][0]
print(f'baseline s6m·OR·deb1·wob{W0}:  n={base[4]}  medMAE={base[5]:.2f}  %<0.5={base[6]:.0f}  %MFE>=.7={base[7]:.0f}')
print(f'grid: {len(rows)} combos — TOP 12 by medMAE (n>=30):')
for r in sorted([r for r in rows if r[4] >= 30], key=lambda r: r[5])[:12]:
    print(f'  {r[0]} {r[1]:<3} deb{r[2]} wob{r[3]:<2} | n={r[4]:3}  medMAE={r[5]:.2f}  %<0.5={r[6]:3.0f}  %MFE>=.7={r[7]:3.0f}')
db.disconnect()
