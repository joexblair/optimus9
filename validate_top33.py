"""One-off: validate the grind's top-33 combos over a vol-masked 33-day window.
  1) extend the vol-mask rebuild to 33 days (official 1m → realistic 5s)
  2) re-score the top 33 over the 33-day window
  3) persist to bl_grind_validate so we can compare 90h stop vs 33d stop (robust vs overfit).
Not a grind — a fixed set of 33 combos over a longer span."""
import sys, time; sys.path.insert(0, '/home/joe/thecodes')
import numpy as np
from collections import defaultdict
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.data.bybit_kline_client import BybitKlineClient
from optimus9.data.synthetic_bar_builder import SyntheticBarBuilder as SBB
from optimus9.orchestration import bl_grind_sweep as S
from logger import get_logger
import logging; logging.getLogger('BybitKlineClient').setLevel('ERROR')
log = get_logger('Validate33')

DAYS, CLEAN_H, WARMUP_H = 33, 12, 12
now = int(time.time() * 1000)
db = DatabaseManager(**get_db_config()); db.connect()

# 1) profile intra-minute wiggle from the clean last 12h
rows = db.execute('SELECT kc_timestamp t,kc_open o,kc_high h,kc_low l,kc_close c FROM kline_collection '
                  'WHERE kc_tp_pk=1 AND kc_timestamp>=%s ORDER BY kc_timestamp', (now - CLEAN_H*3600000,), fetch=True)
mins = defaultdict(list)
for r in rows: mins[(r['t'] // 60000) * 60000].append(r)
ratios = []
for _, bs in mins.items():
    if len(bs) < 6: continue
    cl = np.array([float(b['c']) for b in bs]); O = float(bs[0]['o']); C = cl[-1]
    H = max(float(b['h']) for b in bs); L = min(float(b['l']) for b in bs); n = len(cl)
    if H > L: ratios.append(np.abs(cl - (O + np.arange(1, n + 1) * (C - O) / n)).max() / (H - L))
W = float(np.median(ratios)); log.info(f'wiggle={W:.3f} ({len(ratios)} clean mins)')

# 2) rebuild [window+warmup .. clean boundary] vol-masked, from official 1m
rs = now - (DAYS * 24 + WARMUP_H) * 3600000
re = now - CLEAN_H * 3600000
o1m = BybitKlineClient().fetch_klines('FARTCOINUSDT', '1', rs, re)
b5 = [b for b in SBB.split_batch(o1m, wiggle=W) if rs <= b['timestamp'] < re]
step = 6 * 3600000                                            # chunked delete (avoid 1206 lock-table)
t = rs
while t < re:
    db.execute('DELETE FROM kline_collection WHERE kc_tp_pk=1 AND kc_timestamp>=%s AND kc_timestamp<%s', (t, min(t + step, re)))
    t += step
ins = [(1, b['timestamp'], b['open'], b['high'], b['low'], b['close'], b['volume']) for b in b5]
for i in range(0, len(ins), 5000):
    db.executemany('INSERT IGNORE INTO kline_collection (kc_tp_pk,kc_timestamp,kc_open,kc_high,kc_low,kc_close,kc_volume) '
                   'VALUES (%s,%s,%s,%s,%s,%s,%s)', ins[i:i + 5000])
log.info(f'rebuilt {len(ins)} vol-masked bars over {DAYS}d from {len(o1m)} official 1m')

# 3) the top-33 combos by 90h stop
top = db.execute('SELECT k_len,rsi_len,stc_len,mn_len,mn_mult,mn_src FROM bl_grind_results WHERE n>=20 '
                 'ORDER BY avg_stop LIMIT 33', fetch=True)
combos = [(r['k_len'], r['rsi_len'], r['stc_len'], r['mn_len'], float(r['mn_mult']), r['mn_src']) for r in top]
db.disconnect()
log.info(f'validating {len(combos)} combos over {DAYS}d ({DAYS*24}h window)')

# 4) re-score over the 33-day window → bl_grind_validate
S.prepare(DAYS * 24, warmup_hours=WARMUP_H)
res = S.run_sweep(combos, workers=12, checkpoint=0, progress=10)
S.persist(res, table='bl_grind_validate')
log.info('VALIDATE COMPLETE')
