"""test_arm_gate_v2.py (Joe 0706) — TEST the arm<->s3s4 integration (tightened gate).

Diverge at the s5Mage first-wob (setup bar i): predict s3/s4.
  no predict            → ARM fires standalone at i.
  s3r OR s4r predicted  → wait: BOTH s3r AND s4r must BREACH then REVERSE (wob=R_WOB), AND s2Mage reverse → OPEN.
                          abandon if s5Mage falls IB during the wait.
Compares to the CURRENT gate_open (either-r-breached rtr, slope-flip). Diagnostic only — mirrors the real
gate_signals (pred3/pred4/rev2M) so it's faithful; production = tighten gate_open's rtr, not a new machine.
"""
import sys, time, calendar
sys.path.insert(0, '/home/joe/thecodes')
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from sweep_eval import BASE_BIAS
from optimus9.analysis.lr_v2 import v2_arm, gate_open, gate_signals

dev = DatabaseManager(**get_db_config()); dev.connect()
cfg = lr_config(dev); HI, LO = cfg.hi, cfg.lo
W = bm.BiasWindow(dev, int(time.time() * 1000), lookback=336, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS), lean=True)
ts = np.array(W.ts)
s3r = np.asarray(W.line('s3r'), float); s4r = np.asarray(W.line('s4r'), float); s5M = np.asarray(W.line('s5M'), float)
sig = gate_signals(W, cfg)
dev.disconnect()
def dt(m): return time.strftime('%m-%d %H:%M:%S', time.gmtime(int(m) / 1000))
def ms(s): return calendar.timegm(time.strptime(s, '%Y-%m-%d %H:%M:%S')) * 1000
days = (int(ts[-1]) - int(ts[0])) / 86400000.0
R_WOB = 8


def gate_open_joe(setups, r_wob=R_WOB):
    out = []
    for (i, es, bd, cap, src) in setups:
        pred = (sig['pred3'][i] == es and sig['s3m_oob'][i]) or (sig['pred4'][i] == es and sig['s4m_oob'][i])
        if not pred:
            out.append((i, es, bd, i, 'arm')); continue                          # no-predict → arm standalone
        br3 = br4 = rv3 = rv4 = False; c3 = c4 = 0; opened = None
        for k in range(i + 1, cap):
            if (s5M[k] < HI) if es == 1 else (s5M[k] > LO):
                break                                                            # s5Mage IB → abandon
            if not br3 and ((s3r[k] >= HI) if es == 1 else (s3r[k] <= LO)): br3 = True; c3 = 0
            if not br4 and ((s4r[k] >= HI) if es == 1 else (s4r[k] <= LO)): br4 = True; c4 = 0
            if br3 and not rv3:
                ok = (s3r[k] <= s3r[k - 1]) if es == 1 else (s3r[k] >= s3r[k - 1]); c3 = c3 + 1 if ok else 0
                if c3 >= r_wob: rv3 = True
            if br4 and not rv4:
                ok = (s4r[k] <= s4r[k - 1]) if es == 1 else (s4r[k] >= s4r[k - 1]); c4 = c4 + 1 if ok else 0
                if c4 >= r_wob: rv4 = True
            if rv3 and rv4 and sig['rev2M'][k] == bd:
                opened = (k, 'c2'); break
        if opened: out.append((i, es, bd, opened[0], opened[1]))
    return out


setups = v2_arm(W, cfg)
cur = {x[0]: x for x in gate_open(W, cfg, setups)}
joe = {x[0]: x for x in gate_open_joe(setups)}
from collections import Counter
print('setups=%d' % len(setups))
print('CURRENT gate: opens=%d  reasons=%s' % (len(cur), dict(Counter(v[4] for v in cur.values()))))
print('JOE tightened: opens=%d  reasons=%s' % (len(joe), dict(Counter(v[4] for v in joe.values()))))
print('   (reason arm=no-predict standalone · c2=both-r-breach-reverse + s2Mage · none=abandoned/expired)\n')

a, b = ms('2026-07-05 14:40:00'), ms('2026-07-05 15:20:00')
print('14:45 leg (target real turn 15:05-15:07):')
for (i, es, bd, cap, src) in setups:
    if a <= ts[i] <= b:
        c = cur.get(i); j = joe.get(i)
        cs = '%s r=%s' % (dt(ts[c[3]]), c[4]) if c else 'no-open'
        js = '%s r=%s' % (dt(ts[j[3]]), j[4]) if j else 'ABANDON/expire'
        print('  arm %s es=%+d  |  current-gate: %s  |  JOE: %s' % (dt(ts[i]), es, cs, js))
