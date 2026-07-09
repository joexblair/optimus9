"""waypoint_exit_pnl.py (Joe 0706) — PnL of the dud-cut rule: exit if NO r-confluence by T-min.

Overlays a causal early-exit on the s5m-arm's real trades (lr_exit_v2): if a trade is still open at T-min AND
zero of s1r..s4r have reached favorable-OOB, cut it at the T-min price (else keep the real exit). Compares net/
win/dynamic-5x compound vs baseline. Sweeps cut-time. Tests: does cutting the no-confluence duds early help?
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
RLINES = ['s1r', 's2r', 's3r', 's4r']; HI, LO = 85.0, 15.0
db = DatabaseManager(**get_db_config()); db.connect()
BCFG = bm.BiasConfig(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m', xm45=False,
                     mae=0.4, target=0.9, floater_anchor='last', verdict='pk', trigger_src='hlc3')
W = bm.BiasWindow(db, int(dtm.datetime.now(timezone.utc).timestamp() * 1000), cfg=BCFG)
cfg = lr_config(db); cfg.arm_mode = 's5m'
ts = np.array(W.ts); px = np.asarray(W.px, float)
V = {r: np.asarray(W.line(r), float) for r in RLINES}
ent = v2_walk(W, cfg)
resc = sorted(strand_rescue(W, cfg, ent, lr_exit_v2(W, cfg, ent, predict=False)), key=lambda x: x[0])
db.disconnect()

TR = []                                                          # (k0, bd, epx, actual_r, hold_ms)
for (tms, exms, bd, epx, xpx, r, reason) in resc:
    k0 = int(np.argmin(np.abs(ts - int(tms))))
    TR.append((k0, bd, float(epx), float(r), int(exms) - int(tms)))


def compound(items):
    acct = START; wins = 0
    for r, epx in items:
        acct += min(MAX_LOT, acct * LEV / epx) * epx * (r - RT) / 100.0; wins += (r - RT) > 0
    return acct / START, 100 * wins / max(len(items), 1)


def conf_by(k0, bd, B):
    c = 0
    for rl in RLINES:
        seg = V[rl][k0:k0 + B + 1]
        if np.nansum((seg >= HI) if bd == 1 else (seg <= LO)) > 0: c += 1
    return c


base = compound([(r, epx) for k0, bd, epx, r, hm in TR])
print('s5m-arm trades=%d\n' % len(TR))
print('%-24s %8s %6s %6s' % ('rule', 'compound', 'win%', 'cut#'))
print('%-24s %7.1fx %5.0f%%' % ('baseline (lr_exit_v2)', base[0], base[1]))
for Tmin in (10, 15, 20):
    B = Tmin * 12; items = []; cut = 0
    for k0, bd, epx, r, hm in TR:
        if hm > Tmin * 60000 and conf_by(k0, bd, B) == 0:
            nr = bd * (px[k0 + B] - epx) / epx * 100.0 if not np.isnan(px[k0 + B]) else r
            items.append((nr, epx)); cut += 1
        else:
            items.append((r, epx))
    c = compound(items)
    print('%-24s %7.1fx %5.0f%% %6d' % ('cut if conf==0 by %dm' % Tmin, c[0], c[1], cut))
