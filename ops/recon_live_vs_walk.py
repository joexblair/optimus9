"""recon_live_vs_walk.py [led_id]  — reconcile o9-live closed trade(s) against the backtest strategy walk.

The o9-live loop is stateless-by-design: window-ending-at-now == the backtest window ⇒ live == backtest
BY CONSTRUCTION. This verifies that invariant on a real closed trade — the guardrail against the look-ahead /
timing drift that sank o9-live before ([[project_v2_lookahead]]). Runs v2_walk_ad + strand_rescue over a
window covering the trade (same 8h/6h config the live loop uses, causal/emerging), then checks the live
trade matches a walk trade (entry bar within tol + same side). Reports SYNC / DESYNC + a diagnosis.

  python3 ops/recon_live_vs_walk.py            # reconcile the last 10 closed trades
  python3 ops/recon_live_vs_walk.py 42         # reconcile led_id 42
"""
import sys, time
sys.path.insert(0, '/home/joe/thecodes')
import datetime as dtm
from datetime import timezone
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from optimus9.analysis.lr_v2 import v2_walk_ad, lr_exit_v2, strand_rescue
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from sweep_eval import BASE_BIAS

TOL_MS = 15000          # entry-bar match tolerance (±3 bars) — absorbs the seam+grace decision offset
LB, WM = 8, 6           # match the live loop's window (run_o9live)


def dt(ms):
    return dtm.datetime.fromtimestamp(ms / 1000, timezone.utc).strftime('%m-%d %H:%M:%S')


def main():
    led = int(sys.argv[1]) if len(sys.argv) > 1 else None
    o9cfg = get_db_config(); o9cfg['database'] = 'o9_live'
    o9 = DatabaseManager(**o9cfg); o9.connect()
    q = ("SELECT led_id, side, qty, entry_px, exit_px, net, reason, opened_ms, closed_ms FROM o9_ledger "
         "WHERE status='closed'" + (" AND led_id=%s" % led if led else "") + " ORDER BY led_id DESC LIMIT 10")
    trades = o9.execute(q, fetch=True)
    o9.disconnect()
    if not trades:
        print('recon: no closed trades to reconcile'); return
    trades = list(reversed(trades))

    # backtest walk over a window covering the trades (dev/pk_optimizer tape), same config as the live loop
    dev = DatabaseManager(**get_db_config()); dev.connect(); cfg = bm.BiasConfig(**BASE_BIAS); lr = lr_config(dev)
    now = int(time.time() * 1000); end = (now // 5000) * 5000
    W = bm.BiasWindow(dev, end, lookback=LB, warmup=WM, cfg=cfg, lean=True); W._line = W._line_emerging
    ents = v2_walk_ad(W, lr)
    resc = strand_rescue(W, lr, ents, lr_exit_v2(W, lr, ents, predict=False))
    dev.disconnect()
    walk = {int(r[0]): (int(r[2]), int(r[1]), r[6]) for r in resc}     # entry_ms -> (bd, exit_ms, reason)
    wents = sorted(walk)
    w0 = int(W.ts[0])

    print('recon: %d live closed trade(s) vs walk (%d walk trades in window %s→%s)'
          % (len(trades), len(resc), dt(w0), dt(int(W.ts[-1]))))
    bad = 0
    for t in trades:
        sd = 1 if t['side'] == 'Buy' else -1
        om = int(t['opened_ms'])
        if om < w0:
            print('  led %-4s %s %s  entry %s  → OUT-OF-WINDOW (walk starts %s; widen window to check)'
                  % (t['led_id'], t['side'], round(float(t['entry_px']), 6), dt(om), dt(w0)))
            continue
        near = min(wents, key=lambda x: abs(x - om)) if wents else None
        d = (om - near) / 1000.0 if near is not None else None
        if near is not None and abs(om - near) <= TOL_MS and walk[near][0] == sd:
            print('  led %-4s %s  entry %s  → SYNC  (walk entry %s, Δ%+.1fs, walk-reason=%s live-reason=%s)'
                  % (t['led_id'], t['side'], dt(om), dt(near), d, walk[near][2], t['reason']))
        else:
            bad += 1
            if near is None:
                why = 'walk produced NO trades in window'
            elif abs(om - near) > TOL_MS:
                why = 'nearest walk entry %s is Δ%+.1fs away (>%.0fs tol) — no matching entry' % (dt(near), d, TOL_MS / 1000)
            else:
                why = 'nearest walk entry %s SAME bar but side=%+d ≠ live %+d — polarity/desync' % (dt(near), walk[near][0], sd)
            print('  led %-4s %s  entry %s  → ⚠ DESYNC  (%s)' % (t['led_id'], t['side'], dt(om), why))
    print('recon: %d/%d in sync%s' % (len(trades) - bad, len(trades), '' if not bad else '  ← INVESTIGATE'))


if __name__ == '__main__':
    main()
