"""s5Mage_rev_emit.py (Joe 0705) — paint the ENGINE's s5Mage arm events as WHITE bgcolor on a 5s chart.

Calls the engine's `s5Mage_arm(W, cfg)` directly (arm_mode/arm_wob from lp_config) → the Pine marks EXACTLY
what v2_arm/v2_walk_ad/o9-live arm on, so Pine ⇄ engine can't diverge. Ships 5s-aligned timestamps, matched
by bar-containment (no line recompute in Pine). Load on a 5s FARTCOIN chart.

  python3 s5Mage_rev_emit.py
"""
import sys, time
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from sweep_eval import BASE_BIAS
from optimus9.analysis.lr import lr_config
from optimus9.analysis.lr_v2 import s5Mage_arm

dev = DatabaseManager(**get_db_config()); dev.connect()
cfg = lr_config(dev)
W = bm.BiasWindow(dev, int(time.time() * 1000), lookback=336, warmup=48,
                  cfg=bm.BiasConfig(**BASE_BIAS), lean=True)   # s5M from the DB (canonical)
ts = W.ts
vol = W.base['volume'].to_numpy(dtype=float)
n = len(ts)
evts = []
shifted = 0
for i, es, bd in s5Mage_arm(W, cfg):
    k = i
    while k < n and vol[k] == 0:            # arm on a NO-TRADE filler bar → walk to the next real (V>0) bar
        k += 1                              # so TV (which omits fillers) has a bar to paint. Display-only.
    if k < n:
        evts.append(int(ts[k]))
        if k != i:
            shifted += 1
dev.disconnect()

days = (int(ts[-1]) - int(ts[0])) / 86400000.0
print('s5Mage_arm (arm_wob=%s): %d arms over %.1fd = %.1f/day  (%d shifted off a filler bar to the next real bar)'
      % (cfg.arm_wob, len(evts), days, len(evts) / days, shifted))

arr = 'array.from(' + ', '.join(map(str, evts)) + ')'
body = '''//@version=5
indicator("s5Mage arm (first-OOB-reversal, wob%d) — white", overlay = true)
t_arr = %s
dur = timeframe.in_seconds() * 1000
hit = false
for i = 0 to array.size(t_arr) - 1
    tt = array.get(t_arr, i)
    if tt >= time and tt < time + dur
        hit := true
        break
bgcolor(hit ? color.new(color.white, 0) : na)
''' % (cfg.arm_wob, arr)
path = '/home/joe/thecodes/s5Mage_arm.pine'
open(path, 'w').write(body)
print('-> ' + path)
