"""live_feat_dig.py (Joe 0706) — what separated o9-live winners from losers? Feature scan on the 24 real trades.

For each trade, at arm time (opened_ms), compute per candidate line L: is L moving WITH the trade (bd) over
several horizons, and is L OOB. bd = +1 long (Buy) / -1 short (Sell). Split winners (net>0) vs losers, report
mean(bd·slopesign) per line×horizon — the cells where winners≫losers are the discriminators (a would-be filter).
Free-rein exploratory. Causal/emerging (W.line).
"""
import sys, time
sys.path.insert(0, '/home/joe/thecodes')
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from sweep_eval import BASE_BIAS

dev = DatabaseManager(**get_db_config()); dev.connect()
tr = dev.execute("SELECT led_id, side, entry_px, exit_px, net, opened_ms FROM o9_live.o9_ledger WHERE status='closed' ORDER BY opened_ms", fetch=True)
W = bm.BiasWindow(dev, int(time.time() * 1000), lookback=336, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS), lean=True)
ts = np.array(W.ts)
LINES = ['s3M', 's5M', 's7M', 's15M', 's30M', 's3m', 's4m', 's5m', 's3r', 's4r', 's5r']
V = {L: np.asarray(W.line(L), float) for L in LINES}
dev.disconnect()
HI, LO = 85.0, 15.0
HZ = [12, 36, 72]                                                     # 1min, 3min, 6min slope windows (5s bars)

trades = []
for r in tr:
    bd = 1 if r['side'] == 'Buy' else -1
    k = int(np.argmin(np.abs(ts - int(r['opened_ms']))))
    win = float(r['net']) > 0
    trades.append((r['led_id'], bd, k, win, float(r['net'])))
W_ = [t for t in trades if t[3]]; L_ = [t for t in trades if not t[3]]
print('trades=%d  winners=%d  losers=%d\n' % (len(trades), len(W_), len(L_)))


def slopesign(L, k, h):
    a, b = V[L][k], V[L][max(0, k - h)]
    if np.isnan(a) or np.isnan(b): return 0.0
    return np.sign(a - b)


print('mean(bd·slopesign)  — +1 = line moving WITH the trade at entry, -1 = against')
print('%-6s %18s %18s   %s' % ('line', 'WINNERS (n=%d)' % len(W_), 'LOSERS (n=%d)' % len(L_), 'gap (W-L) per hz'))
for L in LINES:
    wrow = [np.mean([t[1] * slopesign(L, t[2], h) for t in W_]) for h in HZ]
    lrow = [np.mean([t[1] * slopesign(L, t[2], h) for t in L_]) for h in HZ]
    gaps = [w - l for w, l in zip(wrow, lrow)]
    flag = '  <<<' if max(abs(g) for g in gaps) >= 0.5 else ''
    print('%-6s  %s   %s   %s%s' % (L,
          ' '.join('%+5.2f' % x for x in wrow), ' '.join('%+5.2f' % x for x in lrow),
          ' '.join('%+5.2f' % g for g in gaps), flag))

# composite alignment: # of Mage lines (s3M,s5M,s7M,s15M,s30M) moving with bd at 3min
MAGE = ['s3M', 's5M', 's7M', 's15M', 's30M']
def align(t): return sum(1 for L in MAGE if t[1] * slopesign(L, t[2], 36) > 0)
print('\nMage-alignment (# of %d Mage lines moving WITH the trade @3min):' % len(MAGE))
print('  winners: mean %.2f  ·  losers: mean %.2f' % (np.mean([align(t) for t in W_]), np.mean([align(t) for t in L_])))
for thr in (3, 4, 5):
    kept = [t for t in trades if align(t) >= thr]
    if kept:
        net = sum(t[4] for t in kept); wr = 100 * sum(t[3] for t in kept) / len(kept)
        print('  filter align>=%d : keeps %2d/24 trades, net %+.3f, win %.0f%%' % (thr, len(kept), net, wr))
