"""s5Mage_oob_sweep.py (Joe 0706) — A/B the breach-confirm STAY-OOB guard.

Two variants of the two-wob latch, identical except state-1 (breach-confirm):
  OOB-GATED  (new, lr_v2.s5Mage_arm) — if the value falls IB before the count completes, ABANDON (hunt ended).
             ⇒ the reversal only ever fires off a SUSTAINED extreme.
  boundary-agnostic (first cut)     — breach-confirm reset-and-resumes on IB bars too (could confirm on chop).

Part 1: validate the fix kills the flagged 07-05 boundary-chop arms.
Part 2: sweep arm_wob, score each arm's MAE/MFE (bd-signed) to the next >=0.9% swing pivot, both variants.
Last 14d, EMERGING/causal.
"""
import sys, time, bisect, calendar
sys.path.insert(0, '/home/joe/thecodes')
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from sweep_eval import BASE_BIAS
from optimus9.compute.swing_detect import find_pivots

dev = DatabaseManager(**get_db_config()); dev.connect()
cfg = lr_config(dev); HI, LO = cfg.hi, cfg.lo
W = bm.BiasWindow(dev, int(time.time() * 1000), lookback=336, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS), lean=True)
ts = np.array(W.ts); s5 = np.asarray(W.line('s5M'), float); px = np.asarray(W.px, float)
dev.disconnect()
days = (int(ts[-1]) - int(ts[0])) / 86400000.0
v0 = int(np.argmax(~np.isnan(px)))
piv = [p[0] + v0 for p in find_pivots(px[v0:], 0.9)]


def arms(wob, gated):
    """Two-wob latch. gated=True ⇒ breach-confirm abandons the moment the value falls IB (STAY-OOB)."""
    out = []; state = 0; br = 0; cnt = 0
    for k in range(1, len(s5)):
        if state == 0:
            if s5[k] >= HI and s5[k - 1] < HI: br = 1; state = 1; cnt = 0
            elif s5[k] <= LO and s5[k - 1] > LO: br = -1; state = 1; cnt = 0
        elif state == 1:
            if gated and ((s5[k] < HI) if br == 1 else (s5[k] > LO)):
                state = 0; cnt = 0                                  # fell IB before confirming → hunt ended
            else:
                ok = (s5[k] >= s5[k - 1]) if br == 1 else (s5[k] <= s5[k - 1])
                cnt = cnt + 1 if ok else 0
                if cnt >= wob: state = 2; cnt = 0
        elif state == 2:
            ok = (s5[k] <= s5[k - 1]) if br == 1 else (s5[k] >= s5[k - 1])
            cnt = cnt + 1 if ok else 0
            if cnt >= wob: out.append((k, br, -br)); state = 0; cnt = 0
    return out


def dt(m): return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(m) / 1000))
def ms(s): return calendar.timegm(time.strptime(s, '%Y-%m-%d %H:%M:%S')) * 1000


# ---- Part 1: validation at the live wob ----
wob0 = cfg.arm_wob
ag = {int(ts[i]) for i, e, b in arms(wob0, gated=False)}
ga = {int(ts[i]) for i, e, b in arms(wob0, gated=True)}
flagged = ['2026-07-05 14:38:55', '2026-07-05 14:45:55', '2026-07-05 16:24:45']
print('VALIDATION @ wob=%d — flagged arms should be in AGNOSTIC and GONE in OOB-GATED:' % wob0)
for f in flagged:
    t = ms(f); near = lambda S: any(abs(x - t) <= 30000 for x in S)
    print('  %s   agnostic=%-5s  gated=%-5s  %s' % (
        f, 'ARM' if near(ag) else '-', 'ARM' if near(ga) else '-',
        'KILLED ✓' if near(ag) and not near(ga) else ('(no agnostic arm here)' if not near(ag) else 'STILL FIRES ✗')))
removed = len(ag) - len(ga)
print('  agnostic arms=%d · gated arms=%d · removed by STAY-OOB=%d (%.0f%%)\n' % (
    len(ag), len(ga), removed, 100 * removed / max(len(ag), 1)))


# ---- Part 2: sweep ----
def score(evs):
    maes, mfes = [], []
    for i, e, bd in evs:
        j = bisect.bisect_right(piv, int(i))
        if j >= len(piv): continue
        fav = bd * (px[i:piv[j] + 1] - px[i]) / px[i] * 100.0
        mfes.append(float(np.nanmax(fav))); maes.append(float(np.nanmin(fav)))
    if not maes: return None
    maes, mfes = np.array(maes), np.array(mfes)
    return len(maes), np.median(maes), np.median(mfes), np.median(mfes / np.maximum(np.abs(maes), 1e-9))


print('s5Mage arm — breach-confirm STAY-OOB A/B · %dd · %d real 0.9%% swings\n' % (round(days), len(piv)))
print('OOB-GATED (rev only off an extreme)          vs   boundary-agnostic (first cut)')
print('%-4s %7s %7s %7s %10s      %6s %10s' % ('wob', 'n', 'MAE', 'MFE', 'MFE/|MAE|', 'n', 'MFE/|MAE|'))
for wob in range(0, 13):
    g = score(arms(wob, gated=True)); a = score(arms(wob, gated=False))
    if not g or not a:
        print('%-4d  (no arms)' % wob); continue
    print('%-4d %7d %+7.3f %+7.3f %10.2f      %6d %10.2f' % (
        wob, g[0], g[1], g[2], g[3], a[0], a[3]))
