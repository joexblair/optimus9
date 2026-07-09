"""ker_gate_validate.py (Joe 0706) — does the KER entry-gate hold at a FIXED (causal) threshold, multi-window?

The confluence win used quartiles (data-relative, non-causal). A realtime gate needs a fixed cutoff. Test:
keep entry iff s5m-KER < THR AND s3m-KER < THR (both fast oscillators = choppy/exhausted = strong reversal).
Sweep THR over 4 windows; report kept%, win%, avgNet vs ALL. If the lift holds at a fixed THR → wire-able.
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

RT = 0.20
def ms(s): return int(dtm.datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp() * 1000)
ENDS = ['2026-06-24 00:00', '2026-06-28 00:00', '2026-07-02 00:00', '2026-07-06 12:00']
BCFG = bm.BiasConfig(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m', xm45=False,
                     mae=0.4, target=0.9, floater_anchor='last', verdict='pk', trigger_src='hlc3')
db = DatabaseManager(**get_db_config()); db.connect()
def ker(a):
    d = np.diff(a); d = d[~np.isnan(d)]
    return abs(d.sum()) / (np.abs(d).sum() + 1e-9) if len(d) > 1 else 1.0

THRS = [0.10, 0.12, 0.15, 0.18]
agg = {t: [] for t in THRS}; base = []
for end in ENDS:
    W = bm.BiasWindow(db, ms(end), cfg=BCFG); cfg = lr_config(db); cfg.arm_mode = 's5m'
    ts = np.array(W.ts); s5m = np.asarray(W.line('s5m'), float); s3m = np.asarray(W.line('s3m'), float)
    ent = v2_walk_ad(W, cfg)
    resc = strand_rescue(W, cfg, ent, lr_exit_v2(W, cfg, ent, predict=False))
    T = []
    for (tms, exms, bd, epx, xpx, r, reason) in resc:
        k = int(np.argmin(np.abs(ts - int(tms))))
        T.append((float(r) - RT, ker(s5m[max(0, k - 144):k + 1]), ker(s3m[max(0, k - 144):k + 1])))
    rr = np.array([t[0] for t in T]); base.append((len(T), 100 * np.mean(rr > 0), rr.mean()))
    for thr in THRS:
        sub = [t[0] for t in T if t[1] < thr and t[2] < thr]
        if sub:
            s = np.array(sub); agg[thr].append((len(sub), len(T), 100 * np.mean(s > 0), s.mean()))
        else:
            agg[thr].append((0, len(T), 0, 0))
db.disconnect()

b = np.array(base)
print('KER entry-gate (s5m-KER<THR AND s3m-KER<THR) — 4 windows · s5m arm\n')
print('BASELINE (all): mean n=%.0f  win %.0f%%  avgNet %+.3f\n' % (b[:, 0].mean(), b[:, 1].mean(), b[:, 2].mean()))
print('%-6s %8s %8s %9s' % ('THR', 'kept%', 'win%', 'avgNet'))
for thr in THRS:
    a = np.array(agg[thr]); kept = 100 * a[:, 0].sum() / a[:, 1].sum()
    print('%-6.2f %7.0f%% %7.0f%% %+9.3f   per-win: %s' % (
        thr, kept, a[:, 2].mean(), a[:, 3].mean(), ' '.join('%.0f' % w for w in a[:, 2])))
