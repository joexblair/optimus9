"""ker_confluence.py (Joe 0706) — can a 2nd entry-time axis confluence with s5m-KER to beat the Q1-best (63%)?

s5m 144-bar KER at entry = validated router (lowest quartile = 63% win). Test whether adding a second line's
KER (both-low = double-confirmed choppy/exhausted leg) or a composite multi-line KER sharpens the separation.
Metric: win% + avg net expectancy of the confluence subset vs s5m-Q1 alone. Causal-at-entry.
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

RT = 0.20; LINES = ['s5m', 's3m', 's4m', 's2m', 's5r', 's3r', 's4r', 's5M', 's3M']
db = DatabaseManager(**get_db_config()); db.connect()
BCFG = bm.BiasConfig(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m', xm45=False,
                     mae=0.4, target=0.9, floater_anchor='last', verdict='pk', trigger_src='hlc3')
W = bm.BiasWindow(db, int(dtm.datetime.now(timezone.utc).timestamp() * 1000), cfg=BCFG)
cfg = lr_config(db); cfg.arm_mode = 's5m'
ts = np.array(W.ts)
V = {l: np.asarray(W.line(l), float) for l in LINES}
ent = v2_walk(W, cfg)
resc = sorted(strand_rescue(W, cfg, ent, lr_exit_v2(W, cfg, ent, predict=False)), key=lambda x: x[0])
db.disconnect()

def ker(a):
    d = np.diff(a); d = d[~np.isnan(d)]
    return abs(d.sum()) / (np.abs(d).sum() + 1e-9) if len(d) > 1 else 1.0

rows = []                                                    # {line: KER}, prof, net
for (tms, exms, bd, epx, xpx, r, reason) in resc:
    k = int(np.argmin(np.abs(ts - int(tms))))
    K = {l: ker(V[l][max(0, k - 144):k + 1]) for l in LINES}
    rows.append((K, (float(r) - RT) > 0, float(r) - RT))

def stat(sub):
    if not sub: return (0, 0, 0)
    return len(sub), 100 * np.mean([s[1] for s in sub]), np.mean([s[2] for s in sub])

base_win = 100 * np.mean([r[1] for r in rows])
print('s5m-arm trades=%d · base win %.0f%%\n' % (len(rows), base_win))
q = {l: np.quantile([r[0][l] for r in rows], 0.25) for l in LINES}
n, w, e = stat([r for r in rows if r[0]['s5m'] < q['s5m']])
print('s5m-KER Q1 (baseline router): n=%d win %.0f%% avgNet %+.3f\n' % (n, w, e))

print('CONFLUENCE — s5m-KER low AND 2nd-line-KER low (both bottom quartile):')
print('%-8s %6s %6s %8s' % ('2nd line', 'n', 'win%', 'avgNet'))
for l in LINES:
    if l == 's5m': continue
    sub = [r for r in rows if r[0]['s5m'] < q['s5m'] and r[0][l] < q[l]]
    n, w, e = stat(sub)
    flag = '  <<<' if w > 66 and n >= 40 else ''
    print('%-8s %6d %5.0f%% %+8.3f%s' % (l, n, w, e, flag))

print('\nCOMPOSITE multi-line KER (mean of a set), bottom quartile:')
for nm, ls in [('s5m+s3m+s4m', ['s5m', 's3m', 's4m']), ('s5m+s5r', ['s5m', 's5r']),
               ('all m-lines', ['s5m', 's3m', 's4m', 's2m'])]:
    comp = np.array([np.mean([r[0][x] for x in ls]) for r in rows])
    thr = np.quantile(comp, 0.25)
    sub = [r for i, r in enumerate(rows) if comp[i] < thr]
    n, w, e = stat(sub)
    print('  %-14s n=%d win %.0f%% avgNet %+.3f' % (nm, n, w, e))
