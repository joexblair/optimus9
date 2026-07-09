"""divergence_v2.py (Joe 0706) — divergence exit, r-lines vs m-lines, A/B'd against the curl (lr_exit_v2).

Divergence per line (episode-based, causal confirm at episode end). Favorable-side (sign==bd) = exhaustion → exit.
Line families: r-lines (k-type) vs m-lines (BB oscillators, smoother). Modes per confluence K:
  curl-only (baseline) · curl+div (div overrides only if earlier) · div-only (div OR 0.7 SL, curl ignored — the pure A/B).
Metric = dynamic-5x compound + win%.
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

START, LEV, MAX_LOT, RT, SL, WIN = 500.0, 5.0, 66000, 0.20, 0.7, 60
HI, LO = 85.0, 15.0
FAMILIES = {'r-lines': ['s1r', 's2r', 's3r', 's4r'], 'm-lines': ['s1m', 's2m', 's3m', 's4m', 's5m']}
db = DatabaseManager(**get_db_config()); db.connect()
BCFG = bm.BiasConfig(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m', xm45=False,
                     mae=0.4, target=0.9, floater_anchor='last', verdict='pk', trigger_src='hlc3')
W = bm.BiasWindow(db, int(dtm.datetime.now(timezone.utc).timestamp() * 1000), cfg=BCFG)
cfg = lr_config(db); cfg.arm_mode = 's5m'
ts = np.array(W.ts); px = np.asarray(W.px, float)
allL = sorted(set(sum(FAMILIES.values(), [])))
V = {l: np.asarray(W.line(l), float) for l in allL}
ent = v2_walk(W, cfg)
resc = sorted(strand_rescue(W, cfg, ent, lr_exit_v2(W, cfg, ent, predict=False)), key=lambda x: x[0])
db.disconnect()


def div_sig(r):
    n = len(r); sig = np.zeros(n)
    for thr, cp, co, val in [(HI, np.greater, np.less, 1), (LO, np.less, np.greater, -1)]:
        eps = []; i = 0; oob = (r >= thr) if val == 1 else (r <= thr)
        while i < n:
            if oob[i]:
                j = i
                while j < n and oob[j]: j += 1
                rr = r[i:j]; m = int(np.nanargmax(rr) if val == 1 else np.nanargmin(rr))
                eps.append((j - 1, px[i + m], rr[m])); i = j
            else: i += 1
        for k in range(1, len(eps)):
            eb, pc, rc = eps[k]; _, pp, rp = eps[k - 1]
            if cp(pc, pp) and co(rc, rp): sig[eb] = val
    return sig


DIV = {l: div_sig(V[l]) for l in allL}
TR = []
for (tms, exms, bd, epx, xpx, r, reason) in resc:
    k0 = int(np.argmin(np.abs(ts - int(tms)))); k1 = int(np.argmin(np.abs(ts - int(exms))))
    TR.append((k0, max(k1, k0 + 1), bd, float(epx), float(r)))


def compound(items):
    acct = START; wins = 0
    for r, epx in items:
        acct += min(MAX_LOT, acct * LEV / epx) * epx * (r - RT) / 100.0; wins += (r - RT) > 0
    return acct / START, 100 * wins / max(len(items), 1)


def div_bar(k0, k1, bd, lines, K):
    for b in range(k0 + 1, k1 + 1):
        if sum(1 for l in lines if np.any(DIV[l][max(k0, b - WIN):b + 1] == bd)) >= K:
            return b
    return None


base = compound([(ar, epx) for k0, k1, bd, epx, ar in TR])
print('s5m-arm trades=%d · baseline curl (lr_exit_v2): %.1fx / %.0f%% win\n' % (len(TR), base[0], base[1]))
print('%-9s %-4s %-14s %-14s %-14s' % ('family', 'K', 'curl+div', 'div-only+SL', ''))
for fam, lines in FAMILIES.items():
    for K in (1, 2):
        cd, do = [], []
        for k0, k1, bd, epx, ar in TR:
            b = div_bar(k0, k1, bd, lines, K)
            # curl+div: div overrides only if earlier than the natural exit
            if b is not None and b < k1 and not np.isnan(px[b]):
                cd.append((bd * (px[b] - epx) / epx * 100.0, epx))
            else:
                cd.append((ar, epx))
            # div-only: exit at div bar OR the 0.7 SL bar (curl ignored)
            slbar = None
            for j in range(k0 + 1, k1 + 1):
                if bd * (px[j] - epx) / epx * 100.0 <= -SL: slbar = j; break
            cand = [x for x in (b, slbar) if x is not None]
            xb = min(cand) if cand else k1
            do.append((bd * (px[xb] - epx) / epx * 100.0 if not np.isnan(px[xb]) else ar, epx))
        cx, cw = compound(cd); dx, dw = compound(do)
        print('%-9s K=%-2d curl+div %5.1fx/%2.0f%%   div-only %5.1fx/%2.0f%%' % (fam, K, cx, cw, dx, dw))
