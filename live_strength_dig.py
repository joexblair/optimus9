"""live_strength_dig.py (Joe 0706) — does LINE STRENGTH (Kaufman efficiency of the leg INTO es) predict trade SIZE?

Joe's 'line strength' = few spikes on a BB/oscillator line's journey from -es to es ⇒ momentum ⇒ big move.
That's the Kaufman Efficiency Ratio (KER = |net| / Σ|Δ|) of the arming leg. For each of the 24 live trades:
find the leg into es (last -es extreme → entry), compute KER + spike-count for several lines, correlate with
the trade's MFE (its realized size). If high-KER ⇒ high-MFE, line strength = the small/large classifier.
Causal. es = -bd (bd +1 long / -1 short).
"""
import sys, time
sys.path.insert(0, '/home/joe/thecodes')
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from sweep_eval import BASE_BIAS

dev = DatabaseManager(**get_db_config()); dev.connect()
tr = dev.execute("SELECT led_id, side, entry_px, opened_ms FROM o9_live.o9_ledger WHERE status='closed' ORDER BY opened_ms", fetch=True)
W = bm.BiasWindow(dev, int(time.time() * 1000), lookback=336, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS), lean=True)
ts = np.array(W.ts); px = np.asarray(W.px, float)
LINES = ['s5m', 's5M', 's3M', 's7M', 's3m', 's4m']
V = {L: np.asarray(W.line(L), float) for L in LINES}
dev.disconnect()
HI, LO = 85.0, 15.0; CAP = 288                                            # journey lookback cap = 24min

def ker_spikes(arr):
    d = np.diff(arr); d = d[~np.isnan(d)]
    if len(d) < 2: return 0.0, 0
    ker = abs(np.nansum(d)) / (np.nansum(np.abs(d)) + 1e-9)
    sg = np.sign(d); sg = sg[sg != 0]
    spikes = int(np.sum(sg[1:] != sg[:-1])) if len(sg) > 1 else 0
    return ker, spikes

rows = []
for r in tr:
    bd = 1 if r['side'] == 'Buy' else -1; es = -bd; e = float(r['entry_px'])
    k = int(np.argmin(np.abs(ts - int(r['opened_ms']))))
    mfe = float(np.nanmax(bd * (px[k:k + 2160] - e) / e * 100.0))          # trade size proxy
    feat = {}
    for L in LINES:
        v = V[L]
        # journey start = last bar in [k-CAP,k] where L was at the -es extreme (opposite side)
        seg = v[max(0, k - CAP):k + 1]
        opp = (seg <= LO) if es == 1 else (seg >= HI)                      # -es side
        starts = np.where(opp)[0]
        s = starts[-1] if len(starts) else 0
        ker, sp = ker_spikes(seg[s:])
        feat[L] = (ker, sp)
    rows.append((r['led_id'], mfe, feat))

mfes = np.array([x[1] for x in rows])
med = np.median(mfes)
print('24 trades — line STRENGTH (KER) of the leg into es, vs trade MFE (median MFE=%.2f%%)\n' % med)
print('%-6s %8s %8s   %10s %10s' % ('line', 'corr(KER', 'corr(spk', 'bigMFE KER', 'smlMFE KER'))
print('%-6s %8s %8s   %10s %10s' % ('', ',MFE)', ',MFE)', '(top half)', '(bot half)'))
for L in LINES:
    ker = np.array([x[2][L][0] for x in rows]); sp = np.array([x[2][L][1] for x in rows])
    ck = np.corrcoef(ker, mfes)[0, 1]; cs = np.corrcoef(sp, mfes)[0, 1]
    big = ker[mfes >= med].mean(); sml = ker[mfes < med].mean()
    flag = '  <<<' if abs(ck) >= 0.35 else ''
    print('%-6s %+8.2f %+8.2f   %10.2f %10.2f%s' % (L, ck, cs, big, sml, flag))
print('\n(+corr(KER,MFE) ⇒ cleaner leg → bigger trade = your hypothesis; -corr(spk,MFE) same thing)')
