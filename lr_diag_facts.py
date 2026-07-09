"""lr_diag_facts.py — (1) current s2r gate lookback; (2) the 03:16:30 long's path: when the 5s SL fired vs
when the mfe peaked vs s7r near 04:47 (Joe: s7r=87 → should have curled out there)."""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import numpy as np
import datetime as dtm
from datetime import timezone
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config


def ms(s): return int(dtm.datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp() * 1000)
def dts(t): return dtm.datetime.utcfromtimestamp(int(t) / 1000).strftime('%H:%M:%S')


db = DatabaseManager(**get_db_config()); db.connect()
print('s2r gate lookback:', db.execute('''SELECT l.lrgl_lookback FROM lr_gate g JOIN lr_gate_line l ON l.lrgl_lrg_pk=g.lrg_pk
    WHERE g.lrg_name='s2r' ''', fetch=True))

cfg = bm.BiasConfig(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m', xm45=False,
                    mae=0.4, target=0.9, floater_anchor='last', verdict='pk', trigger_src='hlc3')
W = bm.BiasWindow(db, ms('2026-06-22 00:00'), cfg=cfg); lrcfg = lr_config(db)
ts, px = W.ts, W.px
s7r = W.line('s7r')
tj = int(np.searchsorted(ts, ms('2026-06-17 03:16:30')))
epx = px[tj]
ret = (px - epx) / epx * 100.0                              # long: favourable = +
sl_k = next((k for k in range(tj + 1, len(ts)) if ret[k] <= -lrcfg.sl), None)
end = min(len(ts), tj + lrcfg.horizon)
peak_k = tj + 1 + int(np.argmax(ret[tj + 1:end]))
print(f"03:16:30 long  entry@{epx:.4f}  horizon→{dts(ts[end-1])}")
print(f"  first 5s SL (ret≤-{lrcfg.sl}%): {dts(ts[sl_k]) if sl_k else 'never'}  ret={ret[sl_k]:.2f}%" if sl_k else "  no SL")
print(f"  mfe peak: {dts(ts[peak_k])}  ret=+{ret[peak_k]:.2f}%")
print(f"  s7r at 04:47: {s7r[int(np.searchsorted(ts, ms('2026-06-17 04:47:00')))]:.1f}  (Joe TV=87)")
# 30s vs 5s adverse around the SL
print("  5s ret around the SL bar:", [f"{dts(ts[k])}={ret[k]:+.2f}" for k in range(max(tj, (sl_k or tj) - 3), (sl_k or tj) + 2)] if sl_k else "")
db.disconnect()
