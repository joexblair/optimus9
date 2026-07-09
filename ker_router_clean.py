"""ker_router_clean.py (Joe 0706) — does s5m-KER split the s5m-arm's REAL trades by quality?

Uses the real exit (lr_exit_v2 + strand_rescue, the 10x baseline). For each resulting trade, compute s5m 144-bar
KER at entry. Split by KER (quartiles + thresholds); report per-subset avg net ret/trade (expectancy = the clean
quality metric, count-unbiased), win%, and dynamic-5x compound x (secondary). If LOW-KER ≫ HIGH-KER expectancy,
the size-router is real. Causal.
"""
import sys, datetime as dtm
from datetime import timezone
sys.path.insert(0, '/home/joe/thecodes')
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from optimus9.analysis.lr_v2 import v2_walk, lr_exit_v2, strand_rescue

START, LEV, MAX_LOT, RT = 500.0, 5.0, 66000, 0.20
db = DatabaseManager(**get_db_config()); db.connect()
BCFG = bm.BiasConfig(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m', xm45=False,
                     mae=0.4, target=0.9, floater_anchor='last', verdict='pk', trigger_src='hlc3')
W = bm.BiasWindow(db, int(dtm.datetime.now(timezone.utc).timestamp() * 1000), cfg=BCFG)
cfg = lr_config(db); cfg.arm_mode = 's5m'
ts = np.array(W.ts); s5m = np.asarray(W.line('s5m'), float)
ent = v2_walk(W, cfg)
resc = sorted(strand_rescue(W, cfg, ent, lr_exit_v2(W, cfg, ent, predict=False)), key=lambda x: x[0])
db.disconnect()

def ker(a):
    d = np.diff(a); d = d[~np.isnan(d)]
    return abs(d.sum()) / (np.abs(d).sum() + 1e-9) if len(d) > 1 else 1.0

T = []                                                        # (bar, ret, epx, ker)
for (tms, exms, bd, epx, xpx, r, reason) in resc:
    k = int(np.argmin(np.abs(ts - int(tms))))
    T.append((k, float(r), float(epx), ker(s5m[max(0, k - 144):k + 1])))

def compound(sub):
    acct = START
    for k, r, epx, kv in sorted(sub, key=lambda x: x[0]):
        acct += min(MAX_LOT, acct * LEV / epx) * epx * (r - RT) / 100.0
    return acct / START

def stats(sub):
    if not sub: return (0, 0, 0, 0)
    rr = np.array([x[1] - RT for x in sub])
    return len(sub), rr.mean(), 100 * np.mean(rr > 0), compound(sub)

kv = np.array([x[3] for x in T])
print('s5m-arm real trades (lr_exit_v2) = %d · KER median %.2f, mean %.2f\n' % (len(T), np.median(kv), kv.mean()))
n, m, w, x = stats(T)
print('ALL                 n=%4d  avgNet %+.3f%%  win %.0f%%  compound %.1fx\n' % (n, m, w, x))

print('by KER QUARTILE (low KER = choppy leg = your "large-trade" regime):')
qs = np.quantile(kv, [0.25, 0.5, 0.75])
bins = [('Q1 low  <%.2f' % qs[0], lambda v: v < qs[0]),
        ('Q2 %.2f-%.2f' % (qs[0], qs[1]), lambda v: qs[0] <= v < qs[1]),
        ('Q3 %.2f-%.2f' % (qs[1], qs[2]), lambda v: qs[1] <= v < qs[2]),
        ('Q4 high >%.2f' % qs[2], lambda v: v >= qs[2])]
for nm, f in bins:
    n, m, w, x = stats([t for t in T if f(t[3])])
    print('  %-16s n=%4d  avgNet %+.3f%%  win %.0f%%  compound %.1fx' % (nm, n, m, w, x))

print('\ncumulative LOW-KER filter (keep KER < thr):')
for thr in (0.30, 0.40, 0.50, 0.60):
    n, m, w, x = stats([t for t in T if t[3] < thr])
    print('  keep KER<%.2f : n=%4d  avgNet %+.3f%%  win %.0f%%  compound %.1fx' % (thr, n, m, w, x))
