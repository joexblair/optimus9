"""st5_tf_sweep.py (Joe 0706) — sweep the st5 (s5 clone) TF and run the arm on st5Mage.

Edits the dedicated itf (pk 27, only st5* uses it) across 6..11min, rebuilds W, runs the STAY-OOB two-wob arm
(arm_wob from lp_config) on st5M. Reports per TF: arm count, MAE/MFE (bd-signed) to next 0.9% swing pivot,
and the 07-05 14:45 leg arm time (target real turn 15:05-15:07). Diagnostic; leaves itf 27 at the last value.
"""
import sys, time, bisect, calendar
sys.path.insert(0, '/home/joe/thecodes')
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from sweep_eval import BASE_BIAS
from optimus9.compute.swing_detect import find_pivots

dev = DatabaseManager(**get_db_config()); dev.connect()
cfg = lr_config(dev); HI, LO = cfg.hi, cfg.lo; WOB = cfg.arm_wob
ST_ITF = 27
def dt(m): return time.strftime('%H:%M:%S', time.gmtime(int(m) / 1000))
def ms(s): return calendar.timegm(time.strptime(s, '%Y-%m-%d %H:%M:%S')) * 1000


def arms(s):
    out = []; state = 0; br = 0; cnt = 0
    for k in range(1, len(s)):
        if state == 0:
            if s[k] >= HI and s[k - 1] < HI: br = 1; state = 1; cnt = 0
            elif s[k] <= LO and s[k - 1] > LO: br = -1; state = 1; cnt = 0
        elif state == 1:
            if (s[k] < HI) if br == 1 else (s[k] > LO): state = 0; cnt = 0
            else:
                ok = (s[k] >= s[k - 1]) if br == 1 else (s[k] <= s[k - 1]); cnt = cnt + 1 if ok else 0
                if cnt >= WOB: state = 2; cnt = 0
        elif state == 2:
            ok = (s[k] <= s[k - 1]) if br == 1 else (s[k] >= s[k - 1]); cnt = cnt + 1 if ok else 0
            if cnt >= WOB: out.append((k, br, -br)); state = 0; cnt = 0
    return out


piv = None; days = None; a = ms('2026-07-05 14:40:00'); b = ms('2026-07-05 15:15:00')
print('st5Mage arm (STAY-OOB, arm_wob=%d) — TF sweep · MAE/MFE to next 0.9%% swing · leg 14:45 target 15:05-15:07\n' % WOB)
print('%-6s %6s %7s %8s %8s %10s   %s' % ('TF', 'n', 'n/day', 'MAE', 'MFE', 'MFE/|MAE|', '14:45 leg arm'))
for tfm in (6, 7, 8, 9, 10, 11):
    dev.execute('UPDATE indicator_timeframes SET itf_seconds=%s WHERE itf_pk=%s', (tfm * 60, ST_ITF))
    W = bm.BiasWindow(dev, int(time.time() * 1000), lookback=336, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS), lean=True)
    ts = W.ts; st = np.asarray(W.line('st5M'), float); px = np.asarray(W.px, float)
    if piv is None:
        days = (int(ts[-1]) - int(ts[0])) / 86400000.0
        v0 = int(np.argmax(~np.isnan(px))); piv = [p[0] + v0 for p in find_pivots(px[v0:], 0.9)]
    ar = arms(st)
    maes, mfes = [], []
    for i, es, bd in ar:
        j = bisect.bisect_right(piv, int(i))
        if j >= len(piv): continue
        fav = bd * (px[i:piv[j] + 1] - px[i]) / px[i] * 100.0
        mfes.append(float(np.nanmax(fav))); maes.append(float(np.nanmin(fav)))
    leg = [dt(ts[i]) for i, es, bd in ar if a <= ts[i] <= b]
    mae, mfe = np.array(maes), np.array(mfes)
    print('%-6s %6d %7.1f %+8.3f %+8.3f %10.2f   %s' % (
        '%dmin' % tfm, len(ar), len(ar) / days, np.median(mae), np.median(mfe),
        np.median(mfe / np.maximum(np.abs(mae), 1e-9)), leg or '(none)'))
dev.disconnect()
