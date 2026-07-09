"""divergence_exit.py (Joe 0706) — confluenced r-divergence as a signal-based exit for the s5m-arm book.

Per r-line: detect OOB episodes; compare consecutive same-side episodes for divergence (bearish@OOB-hi: price
higher-high + osc lower-high; bullish@OOB-lo: price lower-low + osc higher-high). Confirmed causally at episode
END. For a trade, the FAVORABLE-side divergence (long→bearish, short→bullish; sign==bd) = the move exhausting →
EXIT to bank. Confluence = # of s1r..s4r firing it within a window. Compare net/win/compound vs lr_exit_v2.
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
RLINES = ['s1r', 's2r', 's3r', 's4r']; HI, LO = 85.0, 15.0; WIN = 60
db = DatabaseManager(**get_db_config()); db.connect()
BCFG = bm.BiasConfig(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m', xm45=False,
                     mae=0.4, target=0.9, floater_anchor='last', verdict='pk', trigger_src='hlc3')
W = bm.BiasWindow(db, int(dtm.datetime.now(timezone.utc).timestamp() * 1000), cfg=BCFG)
cfg = lr_config(db); cfg.arm_mode = 's5m'
ts = np.array(W.ts); px = np.asarray(W.px, float)
Vr = {r: np.asarray(W.line(r), float) for r in RLINES}
ent = v2_walk(W, cfg)
resc = sorted(strand_rescue(W, cfg, ent, lr_exit_v2(W, cfg, ent, predict=False)), key=lambda x: x[0])
db.disconnect()


def div_sig(r):
    """+1 bearish-div (OOB-hi exhaustion) / -1 bullish-div (OOB-lo), per bar at causal confirm (episode end)."""
    n = len(r); sig = np.zeros(n)
    for side, thr, cmp_price, cmp_osc, val in [(1, HI, np.greater, np.less, 1), (-1, LO, np.less, np.greater, -1)]:
        eps = []                                                   # (end, price_extreme, osc_extreme)
        i = 0
        oob = (r >= thr) if side == 1 else (r <= thr)
        while i < n:
            if oob[i]:
                j = i
                while j < n and oob[j]: j += 1
                rr = r[i:j]
                m = int(np.nanargmax(rr) if side == 1 else np.nanargmin(rr))
                eps.append((j - 1, px[i + m], rr[m]))
                i = j
            else:
                i += 1
        for k in range(1, len(eps)):
            eb, pc, rc = eps[k]; _, pp, rp = eps[k - 1]
            if cmp_price(pc, pp) and cmp_osc(rc, rp):
                sig[eb] = val
    return sig


DIV = {r: div_sig(Vr[r]) for r in RLINES}
TR = []                                                            # (k0, k1, bd, epx, actual_r)
for (tms, exms, bd, epx, xpx, r, reason) in resc:
    k0 = int(np.argmin(np.abs(ts - int(tms)))); k1 = int(np.argmin(np.abs(ts - int(exms))))
    TR.append((k0, max(k1, k0 + 1), bd, float(epx), float(r)))


def compound(items):
    acct = START; wins = 0
    for r, epx in items:
        acct += min(MAX_LOT, acct * LEV / epx) * epx * (r - RT) / 100.0; wins += (r - RT) > 0
    return acct / START, 100 * wins / max(len(items), 1)


def run(K):
    items = []; used = 0
    for k0, k1, bd, epx, ar in TR:
        exit_bar = None
        for b in range(k0 + 1, k1 + 1):                            # scan the trade's life
            c = sum(1 for r in RLINES if np.any(DIV[r][max(k0, b - WIN):b + 1] == bd))
            if c >= K:
                exit_bar = b; break
        if exit_bar is not None and exit_bar < k1 and not np.isnan(px[exit_bar]):
            nr = bd * (px[exit_bar] - epx) / epx * 100.0; items.append((nr, epx)); used += 1
        else:
            items.append((ar, epx))
    return compound(items) + (used,)


base = compound([(ar, epx) for k0, k1, bd, epx, ar in TR])
print('s5m-arm trades=%d · divergence-exit (favorable-side, confluence K, window %dm)\n' % (len(TR), WIN * 5 // 60))
print('%-28s %8s %6s %6s' % ('rule', 'compound', 'win%', 'div-exits'))
print('%-28s %7.1fx %5.0f%%' % ('baseline (lr_exit_v2)', base[0], base[1]))
for K in (1, 2, 3):
    x, w, u = run(K)
    print('%-28s %7.1fx %5.0f%% %6d' % ('exit on div confluence>=%d' % K, x, w, u))
