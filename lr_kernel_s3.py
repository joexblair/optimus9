"""
lr_kernel_s3.py (Joe 0630) — KERNEL test: does "s3r predicted-then-breached near entry" separate low-MAE
entries from high-MAE ones, on the existing 145? s3 read CLOSED-bar. Plus the 0617 12:27-vs-12:20 check.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import numpy as np
import datetime as dtm
from datetime import timezone
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_detect, lr_walk, lr_config
from optimus9.compute.breaching_line import predict_breach
from optimus9.constants import FENCE_HI, FENCE_LO


def ms(s): return int(dtm.datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp() * 1000)


db = DatabaseManager(**get_db_config()); db.connect()
for nm in ('s3r', 's3m', 's3M', 's4r', 's4m', 's4M'):           # ensure s3/s4 are closed-bar
    r = db.execute("SELECT ic_pk FROM pk_optimizer.vw_indicator_configs_live WHERE ind_name=%s", (nm,), fetch=True)
    if r:
        db.execute("UPDATE indicator_configs SET ic_ivm_pk=1 WHERE ic_pk=%s", (r[0]['ic_pk'],))
cfg = bm.BiasConfig(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m', xm45=False,
                    mae=0.4, target=0.9, floater_anchor='last', verdict='pk', trigger_src='hlc3')
R1 = ms('2026-06-22 00:00'); START = ms('2026-06-17 00:00')
W = bm.BiasWindow(db, R1, cfg=cfg); lrcfg = lr_config(db)
ts, px, hi, lo = W.ts, W.px, lrcfg.hi, lrcfg.lo
entries = lr_detect(W, lrcfg, start_ms=START)
walk = lr_walk(W, entries, lrcfg)
mae = np.array([r[4] for r in walk])
s3r = W._line('s3r'); s3m = W._line('s3m'); s3M = W._line('s3M')      # closed
s4r = W._line('s4r'); s4m = W._line('s4m'); s4M = W._line('s4M')
pred3 = predict_breach(s3r, s3m, s3M, hi, lo, FENCE_HI, FENCE_LO)
pred4 = predict_breach(s4r, s4m, s4M, hi, lo, FENCE_HI, FENCE_LO)


def confirmed(tj, es, win, pred, sr):                            # predicted on setup side → then r breaches OOB same side
    a = max(0, tj - win)
    pk = np.where(pred[a:tj + 1] == es)[0]
    if len(pk) == 0:
        return False
    after = sr[a + pk[0]:tj + 1]
    return bool((after >= hi).any()) if es == 1 else bool((after <= lo).any())


def stats(m):
    return f"medMAE={np.median(m):.2f}%  meanMAE={np.mean(m):.2f}%  %MAE<0.5={np.mean(m < 0.5) * 100:.0f}%" if len(m) else "—"


print(f"baseline (all 145): {stats(mae)}\n15-min window:")
WIN = 180
c3 = np.array([confirmed(e[3], e[1], WIN, pred3, s3r) for e in entries])
c4 = np.array([confirmed(e[3], e[1], WIN, pred4, s4r) for e in entries])
for name, m in [('s3r only', c3), ('s4r only', c4), ('s3r OR s4r', c3 | c4), ('s3r AND s4r', c3 & c4), ('neither', ~(c3 | c4))]:
    print(f"  {name:12} n={int(m.sum()):3}  {stats(mae[m])}")

# 0617 12:27 (s3 lo-breach) vs 12:20 — forward max-drawdown (long), 90-min look-forward
print("\n12:27 vs 12:20 (0617, long):")
for label in ('12:20:00', '12:27:00'):
    j = int(np.searchsorted(ts, ms(f'2026-06-17 {label}')))
    fwd = px[j:j + 1080]
    dd = float((-(fwd - px[j]) / px[j] * 100).max())            # max adverse (down) for a long
    mfe = float(((fwd - px[j]) / px[j] * 100).max())
    print(f"  {label}  s3r={s3r[j]:.1f} (lo-breach={s3r[j] <= lo})  fwd MAE={dd:.2f}%  MFE=+{mfe:.2f}%")
db.disconnect()
