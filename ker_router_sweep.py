"""ker_router_sweep.py (Joe 0706) — s5m-KER size-router × exit-rule permutation sweep on the s5m-arm backtest.

Entries from v2_walk (s5m arm). Per entry: s5m 144-bar KER (line strength) + forward tape path. Sweep:
  EXIT  = lr_exit_v2 (current baseline) · SL-only 0.7 · TP0.5+SL · trail act0.3/give0.3 · trail act0.5/give0.3
  ROUTER= all · keep LOW-KER (<thr = large-trade regime) · keep HIGH-KER (>thr, control)
Metric = dynamic-5x compounding final$ (build_v2_walk convention), + n / win% / net%. Raw-tape exits are causal.
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
HOR, SL, KTHR = 2160, 0.7, 0.40
db = DatabaseManager(**get_db_config()); db.connect()
BCFG = bm.BiasConfig(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m', xm45=False,
                     mae=0.4, target=0.9, floater_anchor='last', verdict='pk', trigger_src='hlc3')
W = bm.BiasWindow(db, int(dtm.datetime.now(timezone.utc).timestamp() * 1000), cfg=BCFG)
cfg = lr_config(db); cfg.arm_mode = 's5m'
px = np.asarray(W.px, float); s5m = np.asarray(W.line('s5m'), float)
ent = v2_walk(W, cfg)
span = (int(W.ts[-1]) - int(W.ts[0])) / 86400000.0


def ker(a):
    d = np.diff(a); d = d[~np.isnan(d)]
    return abs(d.sum()) / (np.abs(d).sum() + 1e-9) if len(d) > 1 else 1.0


# per entry: (bar, bd, entry_px, KER, fav-path)
E = []
for (tms, es, bd, k) in ent:
    e = float(px[k])
    if np.isnan(e) or e <= 0: continue
    fav = bd * (px[k:k + HOR] - e) / e * 100.0
    E.append((k, bd, e, ker(s5m[max(0, k - 144):k + 1]), fav))
E.sort(key=lambda x: x[0])


def ex_sl(fav):
    for x in fav:
        if x <= -SL: return -SL
    return fav[np.isfinite(fav)][-1] if np.isfinite(fav).any() else 0.0
def ex_tp(tp):
    def f(fav):
        for x in fav:
            if not np.isnan(x):
                if x <= -SL: return -SL
                if x >= tp: return tp
        return fav[np.isfinite(fav)][-1] if np.isfinite(fav).any() else 0.0
    return f
def ex_trail(act, give):
    def f(fav):
        peak = -1e9
        for x in fav:
            if np.isnan(x): continue
            if x <= -SL and peak < act: return -SL
            peak = max(peak, x)
            if peak >= act and x <= peak - give: return x
        return fav[np.isfinite(fav)][-1] if np.isfinite(fav).any() else 0.0
    return f


def compound(items):                                       # items = [(ret, entry_px), ...] time-ordered
    acct = START; wins = 0
    for r, epx in items:
        lot = min(MAX_LOT, acct * LEV / epx)
        acct += lot * epx * (r - RT) / 100.0
        wins += (r - RT) > 0
    return acct, 100 * wins / max(len(items), 1)


EXITS = [('SL-only 0.7', ex_sl), ('TP0.5+SL', ex_tp(0.5)),
         ('trail .3/.3', ex_trail(0.3, 0.3)), ('trail .5/.3', ex_trail(0.5, 0.3))]
ROUTERS = [('all', lambda e: True), ('LOW-KER<%.2f' % KTHR, lambda e: e[3] < KTHR), ('HIGH-KER>%.2f' % KTHR, lambda e: e[3] >= KTHR)]

# baseline: current lr_exit_v2 + strand_rescue (whole arm)
resc = sorted(strand_rescue(W, cfg, ent, lr_exit_v2(W, cfg, ent, predict=False)), key=lambda x: x[0])
bacct = START; bw = 0
for (tms, exms, bd, epx, xpx, r, reason) in resc:
    lot = min(MAX_LOT, bacct * LEV / float(epx)); bacct += lot * float(epx) * (r - RT) / 100.0; bw += (r - RT) > 0
db.disconnect()

print('s5m-arm backtest — KER router × exit sweep · %.1fd · dynamic-5x · %.2f%% RT · %d entries\n' % (span, RT, len(E)))
print('BASELINE  lr_exit_v2 (current), all trades: $%.0f (%.1fx), win %.0f%%\n' % (bacct, bacct / START, 100 * bw / len(resc)))
print('%-14s %-14s %5s %9s %6s %7s' % ('exit', 'router', 'n', 'final$', 'x', 'win%'))
for enm, ef in EXITS:
    for rnm, rf in ROUTERS:
        kept = [e for e in E if rf(e)]
        items = [(ef(e[4]), e[2]) for e in kept]
        acct, win = compound(items)
        print('%-14s %-14s %5d %9.0f %5.1fx %5.0f%%' % (enm, rnm, len(kept), acct, acct / START, win))
