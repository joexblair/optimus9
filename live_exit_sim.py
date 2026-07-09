"""live_exit_sim.py (Joe 0706) — simulate exit rules on the 24 live trades' REAL forward price paths.

For each trade, walk the tape forward from entry (up to HORIZON) applying each exit rule; realized ret = fav at
exit. Compares: actual · SL-only · fixed TP+SL · trailing(activate then give-back)+SL. Net %/win over 24, ~0.07%
RT fee. Tests whether banking favorable excursion (esp. a trail that keeps the +1.8% runners) flips o9-live.
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
HORIZON = 2160; FEE = 0.07; SL = 0.7

paths = []
for r in tr:
    bd = 1 if r['side'] == 'Buy' else -1; e = float(r['entry_px'])
    k0 = int(np.argmin(np.abs(ts - int(r['opened_ms']))))
    fav = bd * (px[k0:k0 + HORIZON] - e) / e * 100.0
    fav = fav[~np.isnan(fav)]
    actual = bd * (float(r['exit_px']) - e) / e * 100.0
    paths.append((r['led_id'], fav, actual))


def sim(rule):
    rets = []
    for lid, fav, actual in paths:
        rets.append(rule(fav, actual) - FEE)
    rets = np.array(rets)
    win = np.array([lid for lid, f, a in paths])  # unused
    return rets.sum(), 100 * np.mean(rets > 0), rets[rets > 0].mean() if (rets > 0).any() else 0, rets[rets <= 0].mean() if (rets <= 0).any() else 0


def r_actual(fav, actual): return actual


def r_sl_tp(tp):
    def f(fav, actual):
        for x in fav:
            if x <= -SL: return -SL
            if x >= tp: return tp
        return fav[-1]
    return f


def r_trail(act, trail):
    def f(fav, actual):
        peak = -1e9; armed = False
        for x in fav:
            if x <= -SL and not armed: return -SL
            peak = max(peak, x)
            if peak >= act: armed = True
            if armed and x <= peak - trail: return x
        return fav[-1]
    return f


print('exit-rule sim on 24 live real paths (SL=%.1f%%, fee %.2f%% RT)\n' % (SL, FEE))
print('%-26s %8s %6s %7s %7s' % ('rule', 'net%', 'win%', 'avgW', 'avgL'))
variants = [('actual (baseline)', r_actual),
            ('SL only (hold+0.7 stop)', r_sl_tp(999)),
            ('TP 0.4 + SL', r_sl_tp(0.4)), ('TP 0.5 + SL', r_sl_tp(0.5)), ('TP 0.6 + SL', r_sl_tp(0.6)),
            ('trail act0.3 give0.2', r_trail(0.3, 0.2)), ('trail act0.3 give0.3', r_trail(0.3, 0.3)),
            ('trail act0.4 give0.2', r_trail(0.4, 0.2)), ('trail act0.5 give0.3', r_trail(0.5, 0.3))]
for name, rule in variants:
    net, win, aw, al = sim(rule)
    print('%-26s %+8.2f %5.0f%% %+7.2f %+7.2f' % (name, net, win, aw, al))
