"""live_vs_backtest_trades.py (Joe 0706) — selection gap or execution gap? Match o9-live trades to backtest.

o9-live ran v2_walk_ad (s5m arm). Build the backtest v2_walk_ad trades over the same window, match to o9-live's
real trades by entry time (±tol) + side. For matched: compare realized ret% + entry px (execution/fill/timing).
Unmatched = selection divergence. This isolates the 67%(bt)→33%(live) cause.
"""
import sys, time
sys.path.insert(0, '/home/joe/thecodes')
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from optimus9.analysis.lr_v2 import v2_walk_ad, lr_exit_v2, strand_rescue

db = DatabaseManager(**get_db_config()); db.connect()
def dt(m): return time.strftime('%m-%d %H:%M', time.gmtime(int(m) / 1000))
lt = db.execute("SELECT side, entry_px, exit_px, net, opened_ms FROM o9_live.o9_ledger WHERE status='closed' ORDER BY opened_ms", fetch=True)
LIVE = []
for r in lt:
    bd = 1 if r['side'] == 'Buy' else -1; e = float(r['entry_px'])
    ret = bd * (float(r['exit_px']) - e) / e * 100.0
    LIVE.append((int(r['opened_ms']), bd, e, ret))
lo = min(x[0] for x in LIVE); hi = max(x[0] for x in LIVE)

BCFG = bm.BiasConfig(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m', xm45=False,
                     mae=0.4, target=0.9, floater_anchor='last', verdict='pk', trigger_src='hlc3')
W = bm.BiasWindow(db, hi + 3600000, lookback=72, warmup=48, cfg=BCFG)
cfg = lr_config(db); cfg.arm_mode = 's5m'
ts = np.array(W.ts); px = np.asarray(W.px, float)
ent = v2_walk_ad(W, cfg)
resc = strand_rescue(W, cfg, ent, lr_exit_v2(W, cfg, ent, predict=False))
BT = []
for (tms, exms, bd, epx, xpx, r, reason) in resc:
    if lo - 120000 <= tms <= hi + 120000: BT.append((int(tms), bd, float(epx), float(r)))
db.disconnect()
BT.sort()

# match LIVE ↔ BT by entry time (±90s) + side
btpool = list(BT); matched = []; live_only = []
for (lms, lbd, lpx, lret) in LIVE:
    cand = [(abs(b[0] - lms), i) for i, b in enumerate(btpool) if b[1] == lbd and abs(b[0] - lms) <= 90000]
    if cand:
        _, i = min(cand); b = btpool.pop(i); matched.append((lms, lbd, lpx, lret, b[2], b[3]))
    else:
        live_only.append((lms, lbd, lpx, lret))
bt_only = btpool

print('window %s → %s\nLIVE trades=%d · BT(v2_walk_ad) trades=%d\n' % (dt(lo), dt(hi), len(LIVE), len(BT)))
print('MATCHED=%d  live-only=%d  bt-only=%d' % (len(matched), len(live_only), len(bt_only)))
if matched:
    lr = np.array([m[3] for m in matched]); br = np.array([m[5] for m in matched])
    pxd = np.array([(m[2] - m[4]) / m[4] * 100 for m in matched])
    print('\n--- MATCHED trades: live vs backtest ---')
    print('  live  ret: avg %+.3f%%  win %.0f%%' % (lr.mean(), 100 * np.mean(lr > 0)))
    print('  bt    ret: avg %+.3f%%  win %.0f%%' % (br.mean(), 100 * np.mean(br > 0)))
    print('  entry-px diff (live-bt): avg %+.3f%%  |max| %.3f%%' % (pxd.mean(), np.max(np.abs(pxd))))
    print('  per-trade ret gap (live-bt): avg %+.3f%%' % (lr - br).mean())
    print('\n  sample matched (live_ret | bt_ret | entry-px-diff%):')
    for m in matched[:12]:
        print('   %s bd%+d  live %+.2f | bt %+.2f | pxΔ %+.3f%%' % (dt(m[0]), m[1], m[3], m[5], (m[2] - m[4]) / m[4] * 100))
if live_only:
    lr = np.array([m[3] for m in live_only])
    print('\n--- LIVE-ONLY (bt did NOT take): n=%d avg ret %+.3f%% win %.0f%% ---' % (len(live_only), lr.mean(), 100 * np.mean(lr > 0)))
