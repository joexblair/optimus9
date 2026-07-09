"""
leverage_sweep_armdelay.py (Joe 0704) — re-tune the dynamic-sizing leverage for the ARM-DELAY stack. Goal:
the fastest ramp to the 66k-COIN cap that NEVER liquidates (min-equity stays safely > 0). Trades are
leverage-invariant → compute the arm-delay book once (v2_walk_ad + exit, stop=lp_lr_sl), then sweep LEV.
06-12→06-22, $500 start, compounding. cost=0.20% EST. HOLD LIGHTLY (one window, un-OOS).
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import datetime as dtm; from datetime import timezone
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from optimus9.analysis.lr_v2 import v2_walk_ad, lr_exit_v2, strand_rescue
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from sweep_eval import BASE_BIAS

def ms(s): return int(dtm.datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp() * 1000)
START, MAXLOT, RT = 500.0, 66000, 0.20
db = DatabaseManager(**get_db_config()); db.connect(); cfg = bm.BiasConfig(**BASE_BIAS); lr = lr_config(db)
W = bm.BiasWindow(db, ms('2026-06-22 00:00'), lookback=240, warmup=80, cfg=cfg, lean=True); W._line = W._line_emerging
ents = sorted(v2_walk_ad(W, lr))
resc = sorted(strand_rescue(W, lr, ents, lr_exit_v2(W, lr, ents, predict=False)), key=lambda x: x[0])

def run(lev):
    acct = START; peak = START; maxdd = 0.0; mineq = START; cap_t = None
    for i, (tms, exms, bd, epx, xpx, r, reason) in enumerate(resc):
        lot = min(MAXLOT, acct * lev / float(epx))
        if lot >= MAXLOT and cap_t is None: cap_t = i
        acct += lot * float(epx) * (r - RT) / 100.0
        peak = max(peak, acct); maxdd = max(maxdd, (peak - acct) / peak); mineq = min(mineq, acct)
        if acct <= 0: return ('LIQUIDATED@%d' % i, acct, maxdd, mineq, cap_t)
    return (None, acct, maxdd, mineq, cap_t)

print('arm-delay leverage re-tune (stop=%.2f%%, %d trades, $500 → , 66k-COIN cap):' % (lr.sl, len(resc)))
print(' lev | final$    x    maxDD  min-eq  cap@trade(of %d)  status' % len(resc))
for lev in (3, 5, 8, 10, 12, 15, 20):
    liq, acct, maxdd, mineq, cap_t = run(lev)
    print('  %-3g | $%-8.0f %-5.1f %4.0f%%  $%-6.0f  %-6s           %s' % (
        lev, acct, acct / START, 100 * maxdd, mineq, str(cap_t), liq or 'ok'))
db.disconnect()
