"""TRAJ_MIN_TAIL_LIFE — 08-22, both answers side by side. 1009.

Joe 1009: *"if the tail's life is < ({knob:0.5,'TRAJ_MIN_TAIL_LIFE'} * TF), defer to the 4 mage/r
rules"*.

THE TAIL'S LIFE, my reading, stated: the span the tail ACTUALLY covers after the reversal
truncation and any deferral - `tail_used` samples x `block` bars. Not the tail knob's request.

ws60r: TRAJ_MIN_TAIL_LIFE 0.5 x 60 min = 30 min = 6 samples at block 60.

THE RULE SITS IN THE CALLER, not in `_trajmech`, because the 4 mage/r rules read a SECOND line and
the mech owns one. `_trajmech` already returns `tail_used`, so nothing in it changes.

PRINTED: traj's answer, the tail's life, whether the rule defers, #7's answer, and the FINAL return
- so the rule's effect on every row is visible rather than asserted.
"""
import os, sys, datetime
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from _trajmech import traj
import _chain10 as C

SC, box, U = C.SC, C.box, C.SC.U
PXa = C.PX
N = len(SC.ts)
R60 = np.asarray(SC.LD(60 * 60, 'r'), float)[:N]
M60 = np.asarray(SC.LD(60 * 60, 'Mage'), float)[:N]
R12, X12, ST = C.R[C.TRIG_TF], C.X[C.TRIG_TF], C.ST
HI, LO = SC.HI, SC.LO
GATE, BLOCK, TAIL, LOOK_N, TF = C.GATE_BARS, 60, 2, 24, C.TRIG_TF
TFW = 60                                  # ws60r's TF-width, minutes
MIN_LIFE = 0.5                            # TRAJ_MIN_TAIL_LIFE
MIN_LIFE_MIN = MIN_LIFE * TFW
print('# 2026-08-22. TRAJ_MIN_TAIL_LIFE %.1f x %d min = %.0f min = %.0f samples at block %d'
      % (MIN_LIFE, TFW, MIN_LIFE_MIN, MIN_LIFE_MIN * 60 / (BLOCK * 5), BLOCK), flush=True)

k0, k1 = SC.K('2026-08-22 00:00:00'), SC.K('2026-08-22 23:59:55')
EV = []
k = max(1, k0)
while k <= k1:
    for side in (+1, -1):
        now = (float(R12[k]) >= HI) if side > 0 else (float(R12[k]) <= LO)
        was = (float(R12[k - 1]) >= HI) if side > 0 else (float(R12[k - 1]) <= LO)
        if now and not was:
            j = k
            while j < N and (((float(R12[j]) >= HI) if side > 0 else (float(R12[j]) <= LO))): j += 1
            EV.append((k, side, j - k, j)); break
    k += 1
reach = [e for e in EV if e[2] > GATE + 1]

u = lambda z: float(X12[z]) < float(R12[z])
def first_signal(b, side, end):
    for q in range(b, min(end, N - 1) + 1):
        if bool(ST[(TF, side)][q]): return q, 'ws%dr stalled' % TF
        if q >= 1 and (((u(q) and not u(q - 1)) if side > 0 else ((not u(q)) and u(q - 1)))):
            return q, 'ws%dx crossed ws%dr' % (TF, TF)
    return None, 'neither inside the oob run'

EYE = {'01:30:05': 'FALSE', '07:42:05': 'TRUE', '13:39:55': 'TRUE',
       '15:32:20': 'FALSE', '19:06:05': 'FALSE'}
#      Joe 1009: "13:33 should be up. the rest are correct" - 13:33 is low oob, so UP OPPOSES the
#      oob side, which is a TRUE. The other four keep the answers he confirmed.

rows = []
for kx, side, run, end in reach:
    b = kx + GATE + 1
    if b >= N: continue
    r = traj(R60, b, BLOCK, TAIL, LOOK_N, 'close', side)
    life = r['tail_used'] * BLOCK * 5 / 60.0
    tdir = r['dir']
    tret = (tdir == -side) if tdir else None
    g = float(M60[b]) - float(R60[b])
    m7 = ((1 if g > 0 else -1) == -side) if g != 0 else None
    defer = (tdir == 0) or (life < MIN_LIFE_MIN)
    final = m7 if defer else tret
    want = EYE.get(U(b))
    got = 'TRUE' if final else 'FALSE'
    rows.append((U(kx), 'high oob' if side > 0 else 'low oob', U(b),
                 ('UP' if tdir > 0 else ('DOWN' if tdir < 0 else 'flat')),
                 '%.0f' % life, 'YES — under %.0f min' % MIN_LIFE_MIN if defer else 'no',
                 '%.4f' % float(M60[b]), '%.4f' % float(R60[b]), '%+.4f' % g,
                 'HIGHER' if g > 0 else 'LOWER',
                 ('TRUE' if m7 else 'FALSE') if m7 is not None else '—',
                 ('TRUE' if tret else 'FALSE') if tret is not None else '—',
                 '**%s**' % got, want or '—',
                 'MATCH' if want == got else ('**MISS**' if want else '—')))
print('\n# 08-22, EVERY DWELL-ENDING — traj, the tail-life rule, #7, and the final return')
box(('the ws12r oob crossing', 'which side', 'the dwell-ending', 'traj dir', "tail's life, min",
     'does the rule DEFER', 'ws60Mage', 'ws60r', 'Mage - r', 'Mage is', '#7 says',
     'traj says', 'THE FINAL RETURN', "Joe's eye", 'verdict'), rows)

print('\n# THE SIGNALS THE FINAL RETURN PRINTS')
srows = []
for kx, side, run, end in reach:
    b = kx + GATE + 1
    if b >= N: continue
    r = traj(R60, b, BLOCK, TAIL, LOOK_N, 'close', side)
    life = r['tail_used'] * BLOCK * 5 / 60.0
    g = float(M60[b]) - float(R60[b])
    m7 = (1 if g > 0 else -1) == -side
    final = m7 if (r['dir'] == 0 or life < MIN_LIFE_MIN) else (r['dir'] == -side)
    if not final: continue
    sb, sw = first_signal(b, side, end)
    srows.append((U(kx), 'high oob' if side > 0 else 'low oob', U(b),
                  U(sb) if sb else '—', sw,
                  '%.1f' % ((int(SC.ts[sb]) - int(SC.ts[b])) / 60000.0) if sb else '—',
                  'SHORT' if side > 0 else 'LONG',
                  '%.6f' % float(PXa[b]), '%.6f' % float(PXa[sb]) if sb else '—'))
box(('the ws12r oob crossing', 'which side', 'the dwell-ending', 'the signal bar',
     'the signal event', 'min after the dwell-ending', 'the signal side',
     'pxs at the dwell-ending', 'pxs at the signal'), srows or [('—',) * 9])
n = len(rows)
print('\n# THE DAY')
box(('the measure', 'value'),
    [('dwell-endings', str(n)),
     ('the tail-life rule DEFERRED to the 4 mage/r rules', '**%d**'
      % sum(1 for r in rows if r[5].startswith('YES'))),
     ('traj kept', str(sum(1 for r in rows if not r[5].startswith('YES')))),
     ('final return TRUE — ws12r prints a trade signal',
      str(sum(1 for r in rows if r[12] == '**TRUE**'))),
     ('final return FALSE — delegate', str(sum(1 for r in rows if r[12] == '**FALSE**'))),
     ('rows matching Joe\'s eye', '**%d of %d**'
      % (sum(1 for r in rows if r[14] == 'MATCH'), sum(1 for r in rows if r[13] != '—')))])
