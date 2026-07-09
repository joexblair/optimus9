"""ker_adaptive_sl.py (Joe 0706) — KER-adaptive stop-loss vs flat SL, on the s5m-arm backtest.

o9-live's hard SL pre-empts strand_rescue. Model it as: apply a hard SL over the tape; if it fires before the
strand/curl natural exit → realize −SL, else the natural r. Sweep SL policy:
  flat {0.7 (current), 0.9, 1.1} · KER-adaptive (high-KER weak → tight; low-KER strong → wide).
KER = s5m 144-bar at entry (validated: low=strong reversal). Metric: net/win/dynamic-5x compound.
"""
import sys, datetime as dtm
from datetime import timezone
sys.path.insert(0, '/home/joe/thecodes')
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from optimus9.analysis.lr_v2 import v2_walk_ad, lr_exit_v2, strand_rescue

START, LEV, MAX_LOT, RT = 500.0, 5.0, 66000, 0.20
db = DatabaseManager(**get_db_config()); db.connect()
BCFG = bm.BiasConfig(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m', xm45=False,
                     mae=0.4, target=0.9, floater_anchor='last', verdict='pk', trigger_src='hlc3')
W = bm.BiasWindow(db, int(dtm.datetime.now(timezone.utc).timestamp() * 1000), cfg=BCFG)
cfg = lr_config(db); cfg.arm_mode = 's5m'
ts = np.array(W.ts); px = np.asarray(W.px, float); s5m = np.asarray(W.line('s5m'), float)
ent = v2_walk_ad(W, cfg)
resc = sorted(strand_rescue(W, cfg, ent, lr_exit_v2(W, cfg, ent, predict=False)), key=lambda x: x[0])
db.disconnect()

def ker(a):
    d = np.diff(a); d = d[~np.isnan(d)]
    return abs(d.sum()) / (np.abs(d).sum() + 1e-9) if len(d) > 1 else 1.0

TR = []                                                    # (k0, k1, bd, epx, r_natural, KER)
for (tms, exms, bd, epx, xpx, r, reason) in resc:
    k0 = int(np.argmin(np.abs(ts - int(tms)))); k1 = int(np.argmin(np.abs(ts - int(exms))))
    TR.append((k0, max(k1, k0 + 1), bd, float(epx), float(r), ker(s5m[max(0, k0 - 144):k0 + 1])))
kv = np.array([t[5] for t in TR]); KMED = np.median(kv)

def realize(k0, k1, bd, epx, rnat, sl):
    for b in range(k0 + 1, k1 + 1):                        # SL fires before the natural strand exit?
        if bd * (px[b] - epx) / epx * 100.0 <= -sl:
            return -sl
    return rnat

def compound(items):
    acct = START; wins = 0
    for r, epx in items:
        acct += min(MAX_LOT, acct * LEV / epx) * epx * (r - RT) / 100.0; wins += (r - RT) > 0
    return acct / START, 100 * wins / max(len(items), 1)

def policy(fn):
    items = [(realize(k0, k1, bd, epx, rnat, fn(kr)), epx) for k0, k1, bd, epx, rnat, kr in TR]
    return compound(items)

print('s5m-arm backtest n=%d · KER median %.2f · SL-policy sweep (SL pre-empts strand_rescue)\n' % (len(TR), KMED))
print('%-30s %8s %6s' % ('policy', 'compound', 'win%'))
for sl in (0.7, 0.9, 1.1, 1.3):
    x, w = policy(lambda kr, s=sl: s); print('%-30s %7.1fx %5.0f%%' % ('flat SL %.1f%%' % sl, x, w))
print()
for tight, wide in [(0.7, 1.1), (0.5, 1.1), (0.5, 1.3), (0.7, 1.3)]:
    x, w = policy(lambda kr, t=tight, wd=wide: t if kr > KMED else wd)
    print('%-30s %7.1fx %5.0f%%' % ('KER-adaptive %.1f(weak)/%.1f(strong)' % (tight, wide), x, w))
