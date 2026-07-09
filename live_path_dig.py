"""live_path_dig.py (Joe 0706) — entry problem or exit problem? Price path of the 24 live trades.

For each trade over [opened_ms, closed_ms]: MFE%/MAE% (bd-signed) on the tape vs the realized exit. If losers
reached decent MFE before stopping → the entries are fine, the EXIT/stop is the lever. If losers go straight
against → entry filtering. bd=+1 Buy / -1 Sell. Causal tape (W.px).
"""
import sys, time
sys.path.insert(0, '/home/joe/thecodes')
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from sweep_eval import BASE_BIAS

dev = DatabaseManager(**get_db_config()); dev.connect()
tr = dev.execute("SELECT led_id, side, entry_px, exit_px, net, opened_ms, closed_ms FROM o9_live.o9_ledger WHERE status='closed' ORDER BY opened_ms", fetch=True)
W = bm.BiasWindow(dev, int(time.time() * 1000), lookback=336, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS), lean=True)
ts = np.array(W.ts); px = np.asarray(W.px, float)
dev.disconnect()

rows = []
for r in tr:
    bd = 1 if r['side'] == 'Buy' else -1; e = float(r['entry_px'])
    k0 = int(np.argmin(np.abs(ts - int(r['opened_ms'])))); k1 = int(np.argmin(np.abs(ts - int(r['closed_ms']))))
    path = px[k0:k1 + 1]; fav = bd * (path - e) / e * 100.0
    mfe = float(np.nanmax(fav)); mae = float(np.nanmin(fav))
    ret = bd * (float(r['exit_px']) - e) / e * 100.0
    rows.append((r['led_id'], bd, float(r['net']) > 0, mfe, mae, ret, (k1 - k0) * 5 / 60))

W_ = [x for x in rows if x[2]]; L_ = [x for x in rows if not x[2]]
print('24 live trades — price path (MFE/MAE %% bd-signed over the hold)\n')
print('%-8s %6s %6s %6s %5s' % ('group', 'MFE', 'MAE', 'exit', 'holdm'))
for nm, g in (('WINNERS', W_), ('LOSERS', L_)):
    print('%-8s %+6.2f %+6.2f %+6.2f %5.0f  (n=%d)' % (
        nm, np.mean([x[3] for x in g]), np.mean([x[4] for x in g]), np.mean([x[5] for x in g]),
        np.mean([x[6] for x in g]), len(g)))

print('\nLOSERS — did they go favorable before stopping?')
for tp in (0.3, 0.5, 0.7, 0.9):
    n = sum(1 for x in L_ if x[3] >= tp)
    print('  reached MFE >= %.1f%%: %2d / %d losers' % (tp, n, len(L_)))
print('\nper-loser (MFE reached, then stopped at MAE):')
for x in sorted(L_, key=lambda z: -z[3]):
    print('  #%2d %-4s MFE %+.2f  MAE %+.2f  exit %+.2f' % (x[0], 'long' if x[1] == 1 else 'short', x[3], x[4], x[5]))

# what would a fixed take-profit have done? (exit at first TP touch, else the real exit)
print('\ncounterfactual: fixed take-profit (else real exit), fee ~0.035%%/side:')
for tp in (0.4, 0.5, 0.6, 0.7):
    tot = 0.0; wins = 0
    for x in rows:
        r = tp if x[3] >= tp else x[5]                    # TP touched → +tp, else realized exit ret
        r -= 0.07                                          # ~round-trip fee %
        tot += r; wins += r > 0
    print('  TP=%.1f%%: net sum %+.2f%% over 24, win %.0f%%' % (tp, tot, 100 * wins / len(rows)))
