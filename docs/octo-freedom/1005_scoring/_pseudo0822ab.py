"""EVERY 08-22 PSEUDO TRADE — A AND B, one row each. 1009.

Joe 1009: *"btw I want A and B trades included for 08-22"*.

One row per DISTINCT pseudo trade whose ws12r oob event falls on 08-22 - distinct meaning a unique
(open bar, side) pair, since consecutive events often resolve to the same open. A's row carries its
own MAE / MFE / realised; B's row sits directly under it when A exited on an exhaustion or a ws12r
reversal.

NOT ADDITIVE. These trades overlap - one A can still be open when a later ws12r event creates
another pseudo trade. The realised column is per trade, never a running total.
"""
import os, sys, datetime
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C

assert C.DGATE == 'traj', 'run with W_DGATE=traj'
SC, box, U = C.SC, C.box, C.SC.U
PXa = C.PX
N = len(SC.ts); TF = C.TRIG_TF
R12, M2 = C.R[TF], C.M2
HI, LO = SC.HI, SC.LO
DAY = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                               datetime.timezone.utc).strftime('%Y-%m-%d')
mn = lambda a, b: (int(SC.ts[b]) - int(SC.ts[a])) / 60000.0
D0, D1 = SC.K('2026-08-22 00:00:00'), SC.K('2026-08-22 23:59:55')
print('# 08-22 pseudo trades. exhaustion %d bars = %.1f min, XWOB_WS12X %d, oob_gate_bars %d, '
      'stop %.2f' % (C.EXH_BARS, C.EXH_BARS * 5 / 60.0, C.XW12, C.GATE_BARS, C.MAE_STOP), flush=True)

m = np.asarray(M2[:N], float); fin = np.isfinite(m)
up = np.zeros(N, bool); dn = np.zeros(N, bool)
up[1:] = fin[1:] & fin[:-1] & (m[:-1] <= LO) & (m[1:] > LO)
dn[1:] = fin[1:] & fin[:-1] & (m[:-1] >= HI) & (m[1:] < HI)
lu = ld = -1; LU = np.full(N, -1, np.int64); LD = np.full(N, -1, np.int64)
for k in range(N):
    if up[k]: lu = k
    if dn[k]: ld = k
    LU[k] = lu; LD[k] = ld
r = np.asarray(R12[:N], float)
EV = []
for k in range(max(1, D0), D1 + 1):
    for side in (+1, -1):
        now = (r[k] >= HI) if side > 0 else (r[k] <= LO)
        was = (r[k - 1] >= HI) if side > 0 else (r[k - 1] <= LO)
        if now and not was:
            EV.append((k, side, int(LU[k]) if side > 0 else int(LD[k]))); break

def score(k, d, xk, why):
    p0 = float(PXa[k]); sgn = 1 if d > 0 else -1
    seg = PXa[k:xk + 1]; ok = np.isfinite(seg) & (seg > 0)
    rel = np.where(ok, (seg - p0) / p0 * 100.0 * sgn, 0.0)
    return dict(real=(float(PXa[xk]) - p0) / p0 * 100.0 * sgn,
                mae=(C.MAE_STOP if why == 'mae breach' else -float(rel.min())),
                mfe=(0.0 if why == 'mae breach' else float(rel.max())),
                rawmfe=float(rel.max()))
BFLIP = ('ws%dr exhaustion' % TF, 'ws%dr reversal on stalled' % TF,
         'ws%dr reversal on x-cross' % TF)

rows = []; seen = set(); n = 0; tot = [0.0, 0.0]
for ev, side, o in EV:
    if o < 0 or (o, side) in seen: continue
    seen.add((o, side)); n += 1
    a = C.run_leg(o, side)
    if a[0] is None: continue
    sa = score(o, side, a[0], a[1])
    tot[0] += sa['real']
    rows.append((str(n), 'A', 'LONG' if side > 0 else 'SHORT', U(o), DAY(o), U(ev),
                 '%.2f' % float(r[ev]), 'HIGH oob' if side > 0 else 'LOW oob',
                 '%.1f' % mn(o, ev), U(a[0]), a[1], '%.1f' % mn(o, a[0]),
                 '%.4f' % sa['mae'], '%.4f' % sa['mfe'], '%.4f' % sa['rawmfe'],
                 '%+.4f' % sa['real'],
                 '%.4f' % (sa['mfe'] / sa['mae']) if sa['mae'] else '—',
                 'YES' if a[4] is not None else 'no'))
    if a[1] in BFLIP:
        b = C.run_leg(a[0], -side)
        if b[0] is not None:
            sb = score(a[0], -side, b[0], b[1])
            tot[1] += sb['real']
            rows.append((str(n), '**B**', 'LONG' if -side > 0 else 'SHORT', U(a[0]), DAY(a[0]),
                         '— A\'s close', '—', '—', '—', U(b[0]), b[1], '%.1f' % mn(a[0], b[0]),
                         '%.4f' % sb['mae'], '%.4f' % sb['mfe'], '%.4f' % sb['rawmfe'],
                         '%+.4f' % sb['real'],
                         '%.4f' % (sb['mfe'] / sb['mae']) if sb['mae'] else '—', '—'))
print('\n# EVERY 08-22 PSEUDO TRADE — A, and B directly under it where one opened')
box(('#', 'A / B', 'side', 'opens', 'the open\'s day', 'the ws12r oob event', 'ws12r there',
     'which side', 'lead min', 'closes', 'why', 'hold min', 'MAE', 'MFE as scored', 'MFE raw',
     'realised', 'MFE/MAE', 'delegated'), rows)
na = sum(1 for x in rows if x[1] == 'A'); nb = sum(1 for x in rows if x[1] == '**B**')
print('\n# 08-22')
box(('the measure', 'value'),
    [('ws12r oob events on 08-22', str(len(EV))),
     ('DISTINCT pseudo trades — A-trades', str(na)),
     ('of them, A exited on an exhaustion or reversal — a B opened', str(nb)),
     ('summed A realised — NOT a P&L, the trades overlap', '%+.4f' % tot[0]),
     ('summed B realised — same caveat', '%+.4f' % tot[1]),
     ('A-trades that delegated to >ws12r oob',
      str(sum(1 for x in rows if x[1] == 'A' and x[17] == 'YES')))])
