"""live_vs_backtest_events.py (Joe 0706) — do o9-live ARM + s3s4-GATE events fire in sync with the backtest?

Finishers (s15a/s30a) already qualified in-sync (Joe). So compare the upstream: o9_state_log 'arm' + 's3s4_gate'
events vs the backtest v2_arm + gate_open over the SAME live window. Match by time (±tol); report counts,
matched, and offsets. Divergence here = the realtime-fidelity gap that drops 67%→33%.
"""
import sys, time
sys.path.insert(0, '/home/joe/thecodes')
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from optimus9.analysis.lr_v2 import v2_arm, gate_open

db = DatabaseManager(**get_db_config()); db.connect()
def dt(m): return time.strftime('%m-%d %H:%M:%S', time.gmtime(int(m) / 1000))
# live events (use kline_ms = the bar the event belongs to)
larm = sorted(int(x['kline_ms']) for x in db.execute("SELECT kline_ms FROM o9_live.o9_state_log WHERE state='arm'", fetch=True))
lgate = sorted(int(x['kline_ms']) for x in db.execute("SELECT kline_ms FROM o9_live.o9_state_log WHERE state='s3s4_gate'", fetch=True))
lo, hi = min(larm + lgate), max(larm + lgate)
print('live window %s -> %s · arms=%d · gates=%d' % (dt(lo), dt(hi), len(larm), len(lgate)))

BCFG = bm.BiasConfig(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m', xm45=False,
                     mae=0.4, target=0.9, floater_anchor='last', verdict='pk', trigger_src='hlc3')
W = bm.BiasWindow(db, hi + 60000, lookback=72, warmup=48, cfg=BCFG)
cfg = lr_config(db); cfg.arm_mode = 's5m'
ts = np.array(W.ts)
setups = v2_arm(W, cfg)
barm = sorted(int(ts[i]) for (i, es, bd, cap, src) in setups if lo <= ts[i] <= hi)
bgate = sorted(int(ts[ok]) for (i, es, bd, ok, r, cap) in gate_open(W, cfg, setups) if lo <= ts[ok] <= hi)
db.disconnect()


def match(A, B, tol=60000):
    B = list(B); m = 0; offs = []
    for a in A:
        j = min(range(len(B)), key=lambda k: abs(B[k] - a)) if B else None
        if j is not None and abs(B[j] - a) <= tol:
            m += 1; offs.append(B[j] - a); B.pop(j)
    return m, offs


print('\nBACKTEST (same window, s5m arm): arms=%d · gates=%d' % (len(barm), len(bgate)))
for nm, L, B in [('ARM', larm, barm), ('GATE', lgate, bgate)]:
    m, offs = match(L, B)
    print('  %-5s live=%3d backtest=%3d  matched=%3d (±60s)  live-only=%3d  bt-only=%3d  med-offset=%+.0fs'
          % (nm, len(L), len(B), m, len(L) - m, len(B) - m, np.median(offs) / 1000 if offs else 0))
# show the first few live arms vs nearest backtest arm
print('\nfirst 8 live ARM events vs nearest backtest arm:')
for a in larm[:8]:
    near = min(barm, key=lambda b: abs(b - a)) if barm else 0
    print('  live %s   nearest-bt %s   (%+ds)' % (dt(a), dt(near), (near - a) // 1000))
