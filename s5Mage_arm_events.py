"""s5Mage_arm_events.py (Joe 0706) — dump the s5Mage two-wob arm events to pk_optimizer.s5Mage_arm_events.

Per arm: the boundary CROSS, the WOB_BREACH confirm, and the ARM (wob_signal) — plus s5Mage + volume at
each. vol_at_arm=0 ⇒ the arm bar is a NO-TRADE filler bar (TV omits it → the pine can't paint it there).
Two-wob latch (arm_wob from lp_config). Last 14d, emerging/causal.
"""
import sys, time
sys.path.insert(0, '/home/joe/thecodes')
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from sweep_eval import BASE_BIAS
from optimus9.live.strategy import StrategyLoop


def dt(ms):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(ms) / 1000))


dev = DatabaseManager(**get_db_config()); dev.connect()
cfg = lr_config(dev); HI, LO = cfg.hi, cfg.lo; wob = cfg.arm_wob
strat = StrategyLoop(dev, bm.BiasConfig(**BASE_BIAS), cfg, 'FARTCOINUSDT', buffer_hours=336, warmup_hours=48)
W = strat.window(int(time.time() * 1000))
ts = np.array(W.ts); s5M = np.asarray(W.line('s5M'), float)
vol = W.base['volume'].to_numpy(dtype=float)

# two-wob state machine, recording cross / breach / arm per arm
rows = []; state = 0; br = 0; cnt = 0; cross_k = 0; breach_k = 0
for k in range(1, len(s5M)):
    if state == 0:
        if s5M[k] >= HI and s5M[k - 1] < HI: br = 1; state = 1; cnt = 0; cross_k = k
        elif s5M[k] <= LO and s5M[k - 1] > LO: br = -1; state = 1; cnt = 0; cross_k = k
    elif state == 1:                                          # must STAY OOB (Joe 0706) — matches lr_v2.s5Mage_arm
        if (s5M[k] < HI) if br == 1 else (s5M[k] > LO):
            state = 0; cnt = 0                                # fell back IB before confirming → hunt ended
        else:
            ok = (s5M[k] >= s5M[k - 1]) if br == 1 else (s5M[k] <= s5M[k - 1])
            cnt = cnt + 1 if ok else 0
            if cnt >= wob: state = 2; cnt = 0; breach_k = k
    elif state == 2:
        ok = (s5M[k] <= s5M[k - 1]) if br == 1 else (s5M[k] >= s5M[k - 1])
        cnt = cnt + 1 if ok else 0
        if cnt >= wob: rows.append((cross_k, breach_k, k, br)); state = 0; cnt = 0

dev.execute('DROP TABLE IF EXISTS s5Mage_arm_events')
dev.execute('''CREATE TABLE s5Mage_arm_events (
    id BIGINT AUTO_INCREMENT PRIMARY KEY, side VARCHAR(5),
    cross_dt DATETIME, wob_breach_dt DATETIME, arm_dt DATETIME,
    s5Mage_at_arm FLOAT, vol_at_arm FLOAT, vol_at_cross FLOAT, arm_bar_filler TINYINT)''')
ins = []
for ck, bk, ak, b in rows:
    ins.append(('SHORT' if b == 1 else 'LONG', dt(ts[ck]), dt(ts[bk]), dt(ts[ak]),
                round(float(s5M[ak]), 2), round(float(vol[ak]), 4), round(float(vol[ck]), 4),
                1 if vol[ak] == 0 else 0))
dev.executemany('INSERT INTO s5Mage_arm_events (side,cross_dt,wob_breach_dt,arm_dt,s5Mage_at_arm,'
                'vol_at_arm,vol_at_cross,arm_bar_filler) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)', ins)
print('wrote %d arm events -> pk_optimizer.s5Mage_arm_events' % len(rows))
nfill = sum(1 for r in ins if r[7] == 1)
print('arms on a NO-TRADE filler bar (vol_at_arm=0): %d / %d' % (nfill, len(rows)))

# 07-05 20:00..20:20 arms — the false 20:18 boundary-chop arm should now be GONE
print('\n07-05 arms in 20:00..20:20 (post STAY-OOB fix):')
found = [ak for ck, bk, ak, b in rows
         if time.strftime('%Y-%m-%d %H:%M', time.gmtime(int(ts[ak]) / 1000)).startswith('2026-07-05 20:1')]
for ak in found:
    print('  ARM %s  s5Mage=%.2f  vol=%.1f' % (dt(ts[ak]), s5M[ak], vol[ak]))
print('  (expect ONLY the 20:10 real arm; NO 20:18 — cross 20:15:05 dipped IB at 20:15:35 → hunt ended)')
dev.disconnect()
