"""st5_gate_land.py (Joe 0706) — st5Mage @10min as the arm line, through the arm<->s3s4 integration.

Sets itf 27 -> 600s (st5 @10min), runs the STAY-OOB arm on st5M, then feeds the setups through:
  current gate_open  (either-r-breached rtr, slope-flip s2Mage)
  JOE tightened      (both s3r AND s4r breach+reverse wob-8, + s2Mage reverse; no-predict -> arm standalone)
Reports the 07-05 14:45 leg (arm / gate-open times) + aggregate. Gate lines (s3/s4/s2) unchanged; only the
arm line is st5Mage@10min. Diagnostic.
"""
import sys, time, calendar
sys.path.insert(0, '/home/joe/thecodes')
import numpy as np
from collections import Counter
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from sweep_eval import BASE_BIAS
from optimus9.analysis.lr_v2 import gate_open, gate_signals

dev = DatabaseManager(**get_db_config()); dev.connect()
cfg = lr_config(dev); HI, LO = cfg.hi, cfg.lo; WOB = cfg.arm_wob
dev.execute('UPDATE indicator_timeframes SET itf_seconds=600 WHERE itf_pk=27')          # st5 @10min
W = bm.BiasWindow(dev, int(time.time() * 1000), lookback=336, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS), lean=True)
ts = np.array(W.ts)
st = np.asarray(W.line('st5M'), float)
s3r = np.asarray(W.line('s3r'), float); s4r = np.asarray(W.line('s4r'), float)
sig = gate_signals(W, cfg)
dev.disconnect()
def dt(m): return time.strftime('%m-%d %H:%M:%S', time.gmtime(int(m) / 1000))
def ms(s): return calendar.timegm(time.strptime(s, '%Y-%m-%d %H:%M:%S')) * 1000
HOR = 2160; R_WOB = 8


def st5_setups():
    out = []; state = 0; br = 0; cnt = 0
    for k in range(1, len(st)):
        if state == 0:
            if st[k] >= HI and st[k - 1] < HI: br = 1; state = 1; cnt = 0
            elif st[k] <= LO and st[k - 1] > LO: br = -1; state = 1; cnt = 0
        elif state == 1:
            if (st[k] < HI) if br == 1 else (st[k] > LO): state = 0; cnt = 0
            else:
                ok = (st[k] >= st[k - 1]) if br == 1 else (st[k] <= st[k - 1]); cnt = cnt + 1 if ok else 0
                if cnt >= WOB: state = 2; cnt = 0
        elif state == 2:
            ok = (st[k] <= st[k - 1]) if br == 1 else (st[k] >= st[k - 1]); cnt = cnt + 1 if ok else 0
            if cnt >= WOB:
                i, es, bd = k, br, -br; cap = min(i + HOR, len(st))
                for j in range(i + 1, cap):
                    if (st[j] <= LO) if es == 1 else (st[j] >= HI): cap = j; break
                out.append((i, es, bd, cap, 'st5')); state = 0; cnt = 0
    return out


def gate_open_joe(setups):
    out = []
    for (i, es, bd, cap, src) in setups:
        pred = (sig['pred3'][i] == es and sig['s3m_oob'][i]) or (sig['pred4'][i] == es and sig['s4m_oob'][i])
        if not pred:
            out.append((i, es, bd, i, 'arm')); continue
        br3 = br4 = rv3 = rv4 = False; c3 = c4 = 0; opened = None
        for k in range(i + 1, cap):
            if (st[k] < HI) if es == 1 else (st[k] > LO):
                break                                                            # st5Mage IB -> abandon
            if not br3 and ((s3r[k] >= HI) if es == 1 else (s3r[k] <= LO)): br3 = True; c3 = 0
            if not br4 and ((s4r[k] >= HI) if es == 1 else (s4r[k] <= LO)): br4 = True; c4 = 0
            if br3 and not rv3:
                ok = (s3r[k] <= s3r[k - 1]) if es == 1 else (s3r[k] >= s3r[k - 1]); c3 = c3 + 1 if ok else 0
                if c3 >= R_WOB: rv3 = True
            if br4 and not rv4:
                ok = (s4r[k] <= s4r[k - 1]) if es == 1 else (s4r[k] >= s4r[k - 1]); c4 = c4 + 1 if ok else 0
                if c4 >= R_WOB: rv4 = True
            if rv3 and rv4 and sig['rev2M'][k] == bd:
                opened = (k, 'c2'); break
        if opened: out.append((i, es, bd, opened[0], opened[1]))
    return out


setups = st5_setups()
cur = {x[0]: x for x in gate_open(W, cfg, setups)}
joe = {x[0]: x for x in gate_open_joe(setups)}
print('st5Mage@10min arm  ·  setups=%d' % len(setups))
print('CURRENT gate:  opens=%d  %s' % (len(cur), dict(Counter(v[4] for v in cur.values()))))
print('JOE tightened: opens=%d  %s' % (len(joe), dict(Counter(v[4] for v in joe.values()))))
a, b = ms('2026-07-05 14:40:00'), ms('2026-07-05 15:25:00')
print('\n14:45 leg (target real turn 15:05-15:07):')
for (i, es, bd, cap, src) in setups:
    if a <= ts[i] <= b:
        c = cur.get(i); j = joe.get(i)
        cs = '%s r=%s' % (dt(ts[c[3]]), c[4]) if c else 'no-open'
        js = '%s r=%s' % (dt(ts[j[3]]), j[4]) if j else 'ABANDON/expire'
        print('  arm %s es=%+d  |  current: %s  |  JOE: %s' % (dt(ts[i]), es, cs, js))
