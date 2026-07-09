"""ker_multiwin.py (Joe 0706) — multi-window validation of the s5m-KER size-router.

Per window (s5m arm, lr_exit_v2 real exit): split trades by s5m 144-bar KER at entry. Report ALL vs the
lowest-KER quartile (Q1) expectancy/win, and the KER<0.50 filter's compound lift. Robust if Q1 beats ALL and
KER<0.50 lifts in EVERY window. 4 windows across the clean tape (~10d lookback each). Causal.
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
def ms(s): return int(dtm.datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp() * 1000)
ENDS = ['2026-06-24 00:00', '2026-06-28 00:00', '2026-07-02 00:00', '2026-07-06 12:00']
BCFG = bm.BiasConfig(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m', xm45=False,
                     mae=0.4, target=0.9, floater_anchor='last', verdict='pk', trigger_src='hlc3')
db = DatabaseManager(**get_db_config()); db.connect()

def ker(a):
    d = np.diff(a); d = d[~np.isnan(d)]
    return abs(d.sum()) / (np.abs(d).sum() + 1e-9) if len(d) > 1 else 1.0
def compound(sub):
    acct = START
    for k, r, epx, kv in sorted(sub, key=lambda x: x[0]):
        acct += min(MAX_LOT, acct * LEV / epx) * epx * (r - RT) / 100.0
    return acct / START
def expect(sub):
    rr = np.array([x[1] - RT for x in sub]); return rr.mean(), 100 * np.mean(rr > 0)

print('%-9s %6s | %-22s | %-22s | %s' % ('win-end', 'n', 'ALL', 'Q1 lowest-KER', 'KER<0.50'))
print('%-9s %6s | %8s %6s %5s | %8s %6s | %6s' % ('', '', 'avgNet', 'win', 'x', 'avgNet', 'win', 'x'))
agg = []
for end in ENDS:
    W = bm.BiasWindow(db, ms(end), cfg=BCFG); cfg = lr_config(db); cfg.arm_mode = 's5m'
    ts = np.array(W.ts); s5m = np.asarray(W.line('s5m'), float)
    ent = v2_walk(W, cfg)
    resc = sorted(strand_rescue(W, cfg, ent, lr_exit_v2(W, cfg, ent, predict=False)), key=lambda x: x[0])
    T = []
    for (tms, exms, bd, epx, xpx, r, reason) in resc:
        k = int(np.argmin(np.abs(ts - int(tms)))); T.append((k, float(r), float(epx), ker(s5m[max(0, k - 144):k + 1])))
    kv = np.array([x[3] for x in T]); q1 = np.quantile(kv, 0.25)
    am, aw = expect(T); ax = compound(T)
    q1sub = [t for t in T if t[3] < q1]; qm, qw = expect(q1sub)
    fx = compound([t for t in T if t[3] < 0.50])
    print('%-9s %6d | %+8.3f %5.0f%% %4.1fx | %+8.3f %5.0f%% | %5.1fx' % (
        end[5:10], len(T), am, aw, ax, qm, qw, fx))
    agg.append((am, aw, ax, qm, qw, fx))
db.disconnect()
a = np.array(agg)
print('%-9s %6s | %+8.3f %5.0f%% %4.1fx | %+8.3f %5.0f%% | %5.1fx' % (
    'MEAN', 0, a[:, 0].mean(), a[:, 1].mean(), a[:, 2].mean(), a[:, 3].mean(), a[:, 4].mean(), a[:, 5].mean()))
