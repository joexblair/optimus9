"""
wob_sweep_armdelay.py (Joe 0704) — sweep the arm-delay wobslay: s5m wob (base arm = s5m reversal) x
s5Mage wob (big-leg delay = s5Mage reversal), each {2,3,4}. Metric = MAE (median/mean) + n, 4 windows.
No stop yet (that's the next step). finisher_v2(gcs5M), DB working configs (emerging).
"""
import sys, itertools; sys.path.insert(0, '/home/joe/thecodes')
import numpy as np, datetime as dtm; from datetime import timezone
import bias_machine as bm
from optimus9.analysis.lr import lr_config, lr_walk
from optimus9.analysis import lr_v2 as L
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from sweep_eval import BASE_BIAS

def ms(s): return int(dtm.datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp() * 1000)
db = DatabaseManager(**get_db_config()); db.connect(); cfg = bm.BiasConfig(**BASE_BIAS); lr = lr_config(db)
HI, LO = lr.hi, lr.lo
WINS = [ms('2026-06-16 13:00'), ms('2026-06-18 00:00'), ms('2026-06-21 00:00'), ms('2026-06-22 00:00')]
WOBS = (2, 3, 4)

def travelled_direct(line):
    n = len(line); dh = dl = False; last = 0; DH = np.zeros(n, bool); DL = np.zeros(n, bool)
    for k in range(n):
        if line[k] >= HI:
            if last == -1: dh = True
            last = 1; dl = False
        elif line[k] <= LO:
            if last == 1: dl = True
            last = -1; dh = False
        DH[k] = dh; DL[k] = dl
    return DH, DL

def dedup(ent):
    seen, out = set(), []
    for e in ent:
        if e[3] not in seen: seen.add(e[3]); out.append(e)
    return out

# precompute per window
PW = []
for end in WINS:
    W = bm.BiasWindow(db, end, lookback=72, warmup=80, cfg=cfg, lean=True); W._line = W._line_emerging
    setups = L.v2_arm(W, lr); sig = L.gate_signals(W, lr)
    s5m, s5M, s7M, s7mL, s7r = (W._line_emerging(n) for n in ('s5m', 's5M', 's7M', 's7m', 's7r'))
    d5h, d5l = travelled_direct(s5M); d7h, d7l = travelled_direct(s7M)
    pred7 = L.predict_breach(s7r, s7mL, s7M, HI, LO, L.FENCE_HI, L.FENCE_LO)
    kc = {}
    for (i, es, bd, cap, src) in setups:
        dir5 = d5l if es == -1 else d5h; dir7 = d7l if es == -1 else d7h
        s7r_es = (s7r <= LO) if es == -1 else (s7r >= HI)
        cond = dir5 & dir7 & (s7r_es | (pred7 == es))
        kc[(i, cap)] = next((k for k in range(i + 1, cap) if cond[k]), None)
    rev5m = {w: L._mage_rev(s5m, w) for w in WOBS}; rev5M = {w: L._mage_rev(s5M, w) for w in WOBS}
    PW.append((W, setups, sig, kc, rev5m, rev5M))

print('arm-delay wob sweep — MAE by (s5m_wob base, s5Mage_wob big-leg):')
print(' s5m s5M | window medMAE(n) ...            | pooled medMAE meanMAE n')
for wm, wM in itertools.product(WOBS, WOBS):
    maes, ns, per = [], 0, []
    for (W, setups, sig, kc, rev5m, rev5M) in PW:
        retimed = []
        for (i, es, bd, cap, src) in setups:
            k0 = kc[(i, cap)]
            if k0 is not None:                                            # big-leg → s5Mage reversal
                arm = next((k for k in range(k0, cap) if rev5M[wM][k] == bd), None)
            else:                                                         # base → s5m reversal
                arm = next((k for k in range(i + 1, cap) if rev5m[wm][k] == bd), None)
            if arm is not None: retimed.append((arm, es, bd, cap, src))
        ent = dedup(L.finisher_v2(W, lr, L.gate_open(W, lr, retimed, sig), 'gcs5M'))
        w = lr_walk(W, ent, lr); m = [x[4] for x in w]
        maes += m; ns += len(ent); per.append((float(np.median(m)) if m else 0, len(ent)))
    print(' %d   %d   | %s | %.2f  %.2f  %d' % (wm, wM,
          ' '.join('%.2f(%d)' % (p[0], p[1]) for p in per), float(np.median(maes)), float(np.mean(maes)), ns))
