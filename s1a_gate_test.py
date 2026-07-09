"""s1a_gate_test.py (Joe 0706) — TEST: s1a gates the s5Mage wob_breach.

s1a (same-side, hi shown), all measured EMERGING/causal:
  - s1Mage OOB AND reversing = MAGE_WOB consecutive 5s bars not-higher (hi) while OOB.  [wob ALWAYS in 5s bars]
  - s1m OOB (concurrent).
  - s1r was OOB somewhere in the trailing RLB_BARS x s1_TF window (r-lookback is TF-bar based → 57min @180s).
When s1a fires → wob_breach=true for the s5Mage arm → the existing reversal wob (arm_wob) fires + tears down.

s5Mage arm rewire (state-1 only): cross OOB → await s1a (abandon if s5M falls IB) → s1a → wob_breach → reversal.
Diagnostic only (no engine change). s1 lines are 180s now (itf_pk=4 edited).
"""
import sys, time, calendar
sys.path.insert(0, '/home/joe/thecodes')
import numpy as np, pandas as pd
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from sweep_eval import BASE_BIAS

dev = DatabaseManager(**get_db_config()); dev.connect()
cfg = lr_config(dev); HI, LO = cfg.hi, cfg.lo; ARM_WOB = cfg.arm_wob
W = bm.BiasWindow(dev, int(time.time() * 1000), lookback=336, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS), lean=True)
ts = np.array(W.ts)
s5 = np.asarray(W.line('s5M'), float); s1M = np.asarray(W.line('s1M'), float)
s1m = np.asarray(W.line('s1m'), float); s1r = np.asarray(W.line('s1r'), float)
S1_TF = int(dev.execute("SELECT itf_seconds FROM vw_indicator_configs_live WHERE ind_name='s1M'", fetch=True)[0]['itf_seconds'])
dev.disconnect()
def dt(m): return time.strftime('%H:%M:%S', time.gmtime(int(m) / 1000))
def ms(s): return calendar.timegm(time.strptime(s, '%Y-%m-%d %H:%M:%S')) * 1000
days = (int(ts[-1]) - int(ts[0])) / 86400000.0
RLB_BARS = 19
r_win = int(RLB_BARS * S1_TF / 5)                                          # 19 x s1_TF, in 5s bars


def reversing(side, mw):
    """s1Mage OOB & a MAGE_WOB non-increasing(hi)/non-decreasing(lo) run — wob in 5s bars. Bool on 5s grid."""
    oob = (s1M >= HI) if side == 1 else (s1M <= LO)
    run = np.zeros(len(s1M), dtype=int)
    for i in range(1, len(s1M)):
        ok = (s1M[i] <= s1M[i - 1]) if side == 1 else (s1M[i] >= s1M[i - 1])
        run[i] = run[i - 1] + 1 if ok else 0
    return oob & (run >= mw)


def s1a(side, mw):
    oob_m = (s1m >= HI) if side == 1 else (s1m <= LO)
    r_oob = (s1r >= HI) if side == 1 else (s1r <= LO)
    r_look = pd.Series(r_oob.astype(float)).rolling(r_win, min_periods=1).max().to_numpy() > 0   # TF-bar r-lookback
    return reversing(side, mw) & oob_m & r_look


def arms(mw):
    hi = s1a(1, mw); lo = s1a(-1, mw)
    out = []; state = 0; br = 0; cnt = 0; ck = 0
    for k in range(1, len(s5)):
        if state == 0:
            if s5[k] >= HI and s5[k - 1] < HI: br = 1; state = 1; ck = k
            elif s5[k] <= LO and s5[k - 1] > LO: br = -1; state = 1; ck = k
        elif state == 1:                                                  # await s1a; abandon if s5M falls IB
            if (s5[k] < HI) if br == 1 else (s5[k] > LO):
                state = 0
            elif (hi[k] if br == 1 else lo[k]):
                state = 2; cnt = 0                                        # s1a fired → wob_breach
        elif state == 2:
            ok = (s5[k] <= s5[k - 1]) if br == 1 else (s5[k] >= s5[k - 1])
            cnt = cnt + 1 if ok else 0
            if cnt >= ARM_WOB: out.append((ck, k, br)); state = 0
    return out


a, b = ms('2026-07-05 14:40:00'), ms('2026-07-05 15:10:00')
print('s1a-gated s5Mage arm  ·  s1_TF=%ds  ·  arm_wob=%d  ·  r-lookback=%dx%ds=%dmin  ·  wob in 5s bars'
      % (S1_TF, ARM_WOB, RLB_BARS, S1_TF, RLB_BARS * S1_TF // 60))
print('leg 14:45 target reversal 15:05-15:07  ·  ungated STAY-OOB arm = 14:45:55, 215/14d\n')
print('%-14s %-14s %s' % ('s1Mage 5s-wob', 'leg arm', '14d (per day)'))
for mw in [4, 6, 8, 10, 12, 16, 20, 24, 30, 40]:
    ar = arms(mw); leg = [dt(ts[k]) for c, k, br in ar if a <= ts[k] <= b]
    print('%-14d %-14s %d (%.1f/day)' % (mw, (leg[0] if leg else '(none)'), len(ar), len(ar) / days))
