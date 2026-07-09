"""lr_diag_1226.py — trace the LO-side (long) cascade around 0617 12:26 to see what blocks the expected long.
A long = s6m breaches LO (arm) → wobslay reverses UP → s30a finisher LO AND s2r gate LO clears → entry."""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import numpy as np
import datetime as dtm
from datetime import timezone
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config, _finisher_active, _gate_ok
from optimus9.compute.indicator_computer import IndicatorComputer as IC


def ms(s): return int(dtm.datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp() * 1000)
def dts(t): return dtm.datetime.utcfromtimestamp(int(t) / 1000).strftime('%H:%M:%S')


db = DatabaseManager(**get_db_config()); db.connect()
cfg = bm.BiasConfig(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m', xm45=False,
                    mae=0.4, target=0.9, floater_anchor='last', verdict='pk', trigger_src='hlc3')
W = bm.BiasWindow(db, ms('2026-06-22 00:00'), cfg=cfg); lrcfg = lr_config(db)
ts, hi, lo = W.ts, lrcfg.hi, lrcfg.lo
al = lrcfg.arms[0].lines[0].name
s6c = W._line(al); s6 = W._line_emerging(al)
sign = np.where(s6c >= hi, 1, np.where(s6c <= lo, -1, 0))
wob = IC.wobble_slayer(s6, lrcfg.wob_n, hi, lo, anchored=True, strict=True)
fin_hi, fin_lo = _finisher_active(W, lrcfg)
gate_hi, gate_lo = _gate_ok(W, lrcfg)
s2r = W.line('s2r')
t0, t1 = ms('2026-06-17 12:18:00'), ms('2026-06-17 12:34:00')
print('  time      s6m  sgn wob | finLO gateLO  s2r    <- LO side (long setup)')
for i in range(len(ts)):
    if not (t0 <= ts[i] < t1):
        continue
    if sign[i] != 0 or wob[i] != 0 or fin_lo[i] or (gate_lo[i] != gate_lo[i - 1]):
        flag = ''
        if sign[i] == -1 and sign[i - 1] != -1: flag += ' ARM-lo'
        if wob[i] == 1: flag += ' WOB-up'
        if fin_lo[i] and not fin_lo[i - 1]: flag += ' FIN-lo'
        print(f"  {dts(ts[i])} {s6c[i]:5.1f}  {sign[i]:+d}  {wob[i]:+d} |  {int(fin_lo[i])}     {int(gate_lo[i])}    {s2r[i]:5.1f}{flag}")
db.disconnect()
