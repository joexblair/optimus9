"""lr_diag_slspike.py — show the raw 5s data around 0617 03:44:40 where the SL fired on the 03:16:30 long.
W.px is what the SL reads; the kline OHLC shows whether the dip is a wick or a real close move."""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import numpy as np
import datetime as dtm
from datetime import timezone
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm


def ms(s): return int(dtm.datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp() * 1000)
def dts(t): return dtm.datetime.utcfromtimestamp(int(t) / 1000).strftime('%H:%M:%S')


db = DatabaseManager(**get_db_config()); db.connect()
cfg = bm.BiasConfig(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m', xm45=False,
                    mae=0.4, target=0.9, floater_anchor='last', verdict='pk', trigger_src='hlc3')
W = bm.BiasWindow(db, ms('2026-06-22 00:00'), cfg=cfg)
ts, px = W.ts, W.px
tj = int(np.searchsorted(ts, ms('2026-06-17 03:16:30')))
epx = px[tj]
sl_px = epx * (1 - 0.005)
# raw klines for the same window
kl = {r['kc_timestamp']: r for r in db.execute(
    "SELECT kc_timestamp, kc_open, kc_high, kc_low, kc_close, kc_volume FROM kline_collection "
    "WHERE kc_timestamp BETWEEN %s AND %s ORDER BY kc_timestamp", (ms('2026-06-17 03:44:00'), ms('2026-06-17 03:45:05')), fetch=True)}
print(f"entry 03:16:30 @ {epx:.5f}   SL trips at px ≤ {sl_px:.5f} (-0.5%)")
print(f"  {'time':8}  {'W.px':>8} {'ret%':>6} | {'open':>8} {'high':>8} {'low':>8} {'close':>8} {'vol':>6}")
i0 = int(np.searchsorted(ts, ms('2026-06-17 03:44:00')))
for i in range(i0, i0 + 13):
    t = int(ts[i]); ret = (px[i] - epx) / epx * 100
    k = kl.get(t)
    trip = '  <-- SL' if px[i] <= sl_px else ''
    ko = f"{k['kc_open']:>8.5f} {k['kc_high']:>8.5f} {k['kc_low']:>8.5f} {k['kc_close']:>8.5f} {k['kc_volume']:>6.0f}" if k else " (no kline row)"
    print(f"  {dts(t):8}  {px[i]:8.5f} {ret:+6.2f} | {ko}{trip}")
db.disconnect()
