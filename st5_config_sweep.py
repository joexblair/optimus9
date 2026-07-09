"""st5_config_sweep.py (Joe 0706) — sweep st5Mage@10min line config (len/mult/src), arm MAE/MFE to next swing.

Edits the st5M DB row (ic_bb_len/ic_bb_mult/ic_src) one dimension at a time (others at baseline 37/0.83/ohlc4),
rebuilds W, runs the arm on st5M both ways (OOB-GATED STAY-OOB vs boundary-agnostic). 14d, arm_wob from lp.
Restores st5M to baseline at the end. itf 27 held at 600s (10min).
"""
import sys, time, bisect
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
ST5M = dev.execute("SELECT ic.ic_pk FROM indicator_configs ic JOIN vw_indicator_configs_live v ON v.ic_pk=ic.ic_pk "
                   "WHERE v.ind_name='st5M'", fetch=True)[0]['ic_pk']
dev.execute('UPDATE indicator_timeframes SET itf_seconds=600 WHERE itf_pk=27')       # st5 @10min
END = int(time.time() * 1000)                                                        # FIXED window end (else the tape drifts per rebuild → stale pivots)
BASE = dict(ln=37, mu=0.83, src='ohlc4')
piv = None; days = None


def arms(s, gated):
    out = []; st = 0; br = 0; cnt = 0
    for k in range(1, len(s)):
        if st == 0:
            if s[k] >= HI and s[k - 1] < HI: br = 1; st = 1; cnt = 0
            elif s[k] <= LO and s[k - 1] > LO: br = -1; st = 1; cnt = 0
        elif st == 1:
            if gated and ((s[k] < HI) if br == 1 else (s[k] > LO)):
                st = 0; cnt = 0
            else:
                ok = (s[k] >= s[k - 1]) if br == 1 else (s[k] <= s[k - 1]); cnt = cnt + 1 if ok else 0
                if cnt >= WOB: st = 2; cnt = 0
        elif st == 2:
            ok = (s[k] <= s[k - 1]) if br == 1 else (s[k] >= s[k - 1]); cnt = cnt + 1 if ok else 0
            if cnt >= WOB: out.append((k, br, -br)); st = 0; cnt = 0
    return out


def evalcfg(ln, mu, src):
    global piv, days
    dev.execute("UPDATE indicator_configs SET ic_bb_len=%s, ic_bb_mult=%s, ic_src=%s WHERE ic_pk=%s",
                (ln, mu, src, ST5M))
    W = bm.BiasWindow(dev, END, lookback=336, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS), lean=True)
    ts = W.ts; s = np.asarray(W.line('st5M'), float); px = np.asarray(W.px, float)
    if piv is None:
        days = (int(ts[-1]) - int(ts[0])) / 86400000.0
        v0 = int(np.argmax(~np.isnan(px))); piv = [p[0] + v0 for p in find_pivots(px[v0:], 0.9)]
    r = {}
    for gated in (True, False):
        maes, mfes = [], []
        for i, es, bd in arms(s, gated):
            j = bisect.bisect_right(piv, int(i))
            if j >= len(piv): continue
            fav = bd * (px[i:piv[j] + 1] - px[i]) / px[i] * 100.0
            mfes.append(float(np.nanmax(fav))); maes.append(float(np.nanmin(fav)))
        mae, mfe = np.array(maes), np.array(mfes)
        r[gated] = (len(mae), np.median(mae), np.median(mfe), np.median(mfe / np.maximum(np.abs(mae), 1e-9)))
    return r


def table(title, vals, mk):
    print('\n%s  (14d, arm_wob=%d, st5@10min)' % (title, WOB))
    print('   OOB-GATED (STAY-OOB)               vs  boundary-agnostic')
    print('%-8s %5s %8s %8s %10s      %10s' % ('val', 'n', 'MAE', 'MFE', 'MFE/|MAE|', 'MFE/|MAE|'))
    for v in vals:
        ln, mu, src = mk(v); r = evalcfg(ln, mu, src); g = r[True]; a = r[False]
        print('%-8s %5d %+8.3f %+8.3f %10.2f      %10.2f' % (str(v), g[0], g[1], g[2], g[3], a[3]))


table('st5M bb_len', [36, 37, 38, 39], lambda v: (v, BASE['mu'], BASE['src']))
table('st5M bb_mult', [0.73, 0.78, 0.83, 0.88], lambda v: (BASE['ln'], v, BASE['src']))
table('st5M src', ['close', 'ohlc4', 'hlc3', 'hlcc4', 'hl2'], lambda v: (BASE['ln'], BASE['mu'], v))

dev.execute("UPDATE indicator_configs SET ic_bb_len=%s, ic_bb_mult=%s, ic_src=%s WHERE ic_pk=%s",
            (BASE['ln'], BASE['mu'], BASE['src'], ST5M))                              # restore baseline
print('\n(st5M restored to %d|%.2f|%s)' % (BASE['ln'], BASE['mu'], BASE['src']))
dev.disconnect()
