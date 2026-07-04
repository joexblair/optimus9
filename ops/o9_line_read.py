"""o9_line_read.py — current LINE POSITIONING at the latest emerging bar → the raw material for an hourly
'what happens next' opinion. Prints each key line's value · OOB state · recent slope, the cascade phase +
arm side, the arm-delay big-leg state, and recent price action. Read this, then form a reasoned forward call.
"""
import sys, time
sys.path.insert(0, '/home/joe/thecodes')
import numpy as np
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from optimus9.analysis.lr_v2 import v2_arm, arm_delay, gate_open, v2_phase, oob_2_oob, bigleg_gate
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from sweep_eval import BASE_BIAS

db = DatabaseManager(**get_db_config()); db.connect(); cfg = bm.BiasConfig(**BASE_BIAS); lr = lr_config(db)
now = int(time.time() * 1000); end = (now // 5000) * 5000
W = bm.BiasWindow(db, end, lookback=8, warmup=6, cfg=cfg, lean=True); W._line = W._line_emerging
HI, LO = lr.hi, lr.lo
ts = W.ts


def rd(name):
    try:
        v = np.asarray(W.line(name), float)
    except Exception:
        return None
    val = v[-1]
    st = 'OOB-HI' if val >= HI else 'OOB-LO' if val <= LO else 'ob' if val >= 70 else 'os' if val <= 30 else 'mid'
    d = val - v[-7] if len(v) >= 7 else 0.0                 # ~30s slope
    sl = 'rising' if d > 0.4 else 'falling' if d < -0.4 else 'flat'
    return val, st, sl, d


print('=== o9 LINE READ @ %s ===' % time.strftime('%m-%d %H:%M:%S', time.gmtime(end / 1000)))
px = float(W.base['close'].to_numpy()[-1])
mv = (px / float(W.base['close'].to_numpy()[-13]) - 1) * 100 if len(W.base) >= 13 else 0
print('price %.5f  (%+.2f%% last 1min)' % (px, mv))
for grp, names in (('ARM', ['s5m', 's5r']), ('TIDE/big-leg', ['s5M', 's7M']),
                   ('GATE-predict', ['s3r', 's3m', 's4r', 's4m', 's2r']), ('GATE-rev', ['s1M']),
                   ('FINISHERS', ['s15r', 's30r', 's30M']), ('EXIT s7', ['s7r', 's7m', 's7M']),
                   ('FAST', ['gcs5', 'gcs5M'])):
    parts = []
    for nm in names:
        r = rd(nm)
        if r:
            parts.append('%s=%.1f[%s,%s]' % (nm, r[0], r[1], r[2]))
    print('  %-14s %s' % (grp, '  '.join(parts) if parts else '(none resolve)'))

# arm side + cascade phase
setups = v2_arm(W, lr)
if lr.arm_bigleg:
    setups = arm_delay(W, lr, setups)
T = len(ts) - 1
live = [s for s in setups if s[0] <= T < s[3]]
if live:
    i, es, bd, cap, src = max(live, key=lambda s: s[0])
    side = 'LONG' if bd == 1 else 'SHORT'
    opens = {s[0]: (s[3], s[4]) for s in gate_open(W, lr, setups)}
    gk = opens.get(i)
    print('  ARM live: %s via %s @%s | gate=%s' % (side, src, time.strftime('%H:%M:%S', time.gmtime(int(ts[i]) / 1000)),
          ('OPEN(%s)@%s' % (gk[1], time.strftime('%H:%M:%S', time.gmtime(int(ts[gk[0]]) / 1000))) if gk and gk[0] <= T else 'latched-waiting')))
else:
    print('  ARM live: none (flat/idle)')
ch, cl = bigleg_gate(W, lr)
print('  big-leg gate now: hi(long)=%s lo(short)=%s' % (bool(ch[T]), bool(cl[T])))
ph = v2_phase(W, lr, 0)
print('  cascade: %s [%s]' % (ph['label'], ph['tone']))
db.disconnect()
