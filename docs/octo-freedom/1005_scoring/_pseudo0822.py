"""08-22's PSEUDO TRADES — the count, and the first two in full. 1009.

Joe 1009: *"I can't work with summaries - I need the first two trades thanks / confirm there 234
trades on 08-22?"*.

234 IS NOT 08-22. It is one row of the 95-day B-trade exit mix: the B-trades whose exit was
`x-cross`, across the whole tape. This file prints 08-22's own count and its first two pseudo
trades, bar by bar.

THE RULE, unchanged from `_pseudo.py` and matching both of Joe's worked examples:
  the event  every ws12r crossing into oob, either side
  the side   the oob side. HIGH -> LONG, LOW -> SHORT
  the open   walking back, the newest ws2Mage crossing INTO in-bounds from the COUNTER-dr side
  forward    run_leg(open, side), then run_leg(A_exit, -side) when A exits on an exhaustion or a
             ws12r reversal
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
print('# W_DGATE %s  exhaustion %d bars = %.1f min  XWOB_WS12X %d  oob_gate_bars %d  stop %.2f'
      % (C.DGATE, C.EXH_BARS, C.EXH_BARS * 5 / 60.0, C.XW12, C.GATE_BARS, C.MAE_STOP), flush=True)

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

print('\n# 2026-08-22 — THE COUNT')
box(('the measure', 'value'),
    [('ws12r oob events on 08-22', str(len(EV))),
     ('of them HIGH oob — A opens LONG', str(sum(1 for _, s, _ in EV if s > 0))),
     ('of them LOW oob — A opens SHORT', str(sum(1 for _, s, _ in EV if s < 0))),
     ('DISTINCT pseudo trades — same open bar and side',
      str(len({(o, s) for _, s, o in EV if o >= 0}))),
     ('events whose open falls on an earlier day',
      str(sum(1 for _, _, o in EV if 0 <= o < D0)))])
print('\n# EVERY 08-22 EVENT AND ITS PSEUDO-OPEN, in time order')
box(('#', 'the ws12r oob event', 'ws12r there', 'which side', 'A opens', 'the day of that open',
     'ws2Mage at the open', 'lead min'),
    [(str(i + 1), U(k), '%.2f' % float(r[k]), 'HIGH oob' if s > 0 else 'LOW oob',
      U(o) if o >= 0 else '—', DAY(o) if o >= 0 else '—',
      '%.2f -> %.2f' % (float(m[o - 1]), float(m[o])) if o >= 1 else '—',
      '%.1f' % mn(o, k) if o >= 0 else '—') for i, (k, s, o) in enumerate(EV)])

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

seen = set(); shown = 0
for ev, side, o in EV:
    if o < 0 or (o, side) in seen: continue
    seen.add((o, side)); shown += 1
    if shown > 2: break
    a = C.run_leg(o, side)
    if a[0] is None: continue
    sa = score(o, side, a[0], a[1])
    p0 = float(PXa[o]); sgn = 1 if side > 0 else -1
    pct = lambda j: '%+.4f' % ((float(PXa[j]) - p0) / p0 * 100.0 * sgn)
    rel = lambda j: '%+.1f' % mn(o, j)
    print('\n\n# PSEUDO TRADE %d — the ws12r oob event at %s, A opens %s %s'
          % (shown, U(ev), U(o), 'LONG' if side > 0 else 'SHORT'))
    rows = [(U(o), '+0.0', '>>> A-TRADE OPENS %s — ws2Mage crossed into IB %.2f -> %.2f from the '
             'counter-dr %s side' % ('LONG' if side > 0 else 'SHORT', float(m[o - 1]), float(m[o]),
                                     'LO' if side > 0 else 'HI'), '%.6f' % p0, '+0.0000')]
    evs = list(a[5])
    evs.append((ev, '### ws%dr CROSSES INTO %s oob at %.2f — THE INTERCHANGE. exhaustion window to '
                    '%s, dwell-ending %s'
                % (TF, 'HIGH' if side > 0 else 'LOW', float(r[ev]),
                   U(min(N - 1, ev + C.EXH_BARS)), U(min(N - 1, ev + C.GATE_BARS + 1)))))
    for j, lbl in sorted(evs, key=lambda z: z[0]):
        rows.append((U(j), rel(j), lbl, '%.6f' % float(PXa[j]), pct(j)))
    rows.append((U(a[0]), rel(a[0]), '>>> A-TRADE CLOSES on %s' % a[1],
                 '%.6f' % float(PXa[a[0]]), pct(a[0])))
    out = [('A-trade', 'LONG' if side > 0 else 'SHORT', U(o), U(a[0]),
            '%.1f' % mn(o, a[0]), a[1], '%.4f' % sa['mae'], '%.4f' % sa['mfe'],
            '%.4f' % sa['rawmfe'], '%+.4f' % sa['real'],
            '%.4f' % (sa['mfe'] / sa['mae']) if sa['mae'] else '—')]
    if a[1] in BFLIP:
        b = C.run_leg(a[0], -side)
        if b[0] is not None:
            sb = score(a[0], -side, b[0], b[1])
            rows.append((U(a[0]), rel(a[0]), '>>> B-TRADE OPENS %s at the same bar'
                         % ('LONG' if -side > 0 else 'SHORT'), '%.6f' % float(PXa[a[0]]),
                         pct(a[0])))
            for j, lbl in b[5]:
                rows.append((U(j), rel(j), 'B: %s' % lbl, '%.6f' % float(PXa[j]), pct(j)))
            rows.append((U(b[0]), rel(b[0]), '>>> B-TRADE CLOSES on %s, its realised %+.4f'
                         % (b[1], sb['real']), '%.6f' % float(PXa[b[0]]), pct(b[0])))
            out.append(('B-trade', 'LONG' if -side > 0 else 'SHORT', U(a[0]), U(b[0]),
                        '%.1f' % mn(a[0], b[0]), b[1], '%.4f' % sb['mae'], '%.4f' % sb['mfe'],
                        '%.4f' % sb['rawmfe'], '%+.4f' % sb['real'],
                        '%.4f' % (sb['mfe'] / sb['mae']) if sb['mae'] else '—'))
    box(('ts', 'min from A\'s open', 'event', 'pxs', 'pct for the A-trade'), rows)
    print('\n### THE RESULT')
    box(('the trade', 'side', 'open', 'close', 'hold min', 'why', 'MAE', 'MFE as scored',
         'MFE raw', 'realised', 'MFE/MAE'), out)
