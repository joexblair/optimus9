"""THE FIRST FOUR 08-22 ws12r SIGNALS, FULL MONTY. 1009.

Joe 1009: *"before we sweep: let's do a code-driven walk on the first four 08-22 sweep signals
(full-monty, starting from the incoming trade to the ws12r interchange, to the final MAEMFE result),
in an onscreen row-timestamped table"*.

A SIGNAL = a bar where ws12r crosses into oob ON THE LEG'S OWN SIDE, i.e. the bar where `oob_a` is
set in `run_leg`. That is the interchange: the dwell clock starts there and one of Joe's four paths
follows. The first four on 08-22, in time order.

PER SIGNAL, three blocks, all on one timeline:
  the INCOMING trade   the leg before A - its open, its walk, its exit. A's open IS that exit bar,
                       so relocating anything about A moves it.
  the A-trade          its open, its full walk, the ws12r interchange, its exit.
  the OUTCOME          A's MAE, MFE and realised; and B's if the decision opened one, since A's
                       exit bar IS B's open bar.

THE MECH IS W_DGATE='traj' - Joe's full 1009 spec: the exhaustion override inside the 1/4 seam,
ws60r at the dwell-ending, and B on ws12r's own stall or x-cross after it.
W_EXH_FRAC 0.25 -> EXH_BARS 36 = 3.0 min. XWOB_WS12X 4 bars = 20 s.
Run alongside W_DGATE='off' so every row can be read against today's behaviour.
"""
import os, sys, datetime
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
import _chain_2day as T

assert C.DGATE == 'traj', 'run with W_DGATE=traj'
SC, box, U = C.SC, C.box, C.SC.U
PXa = C.PX
N = len(SC.ts); TF = C.TRIG_TF
R12, X12 = C.R[TF], C.X[TF]
HI, LO = SC.HI, SC.LO
DAY = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                               datetime.timezone.utc).strftime('%Y-%m-%d')
D0, D1 = SC.K('2026-08-22 00:00:00'), SC.K('2026-08-22 23:59:55')
mn = lambda a, b: (int(SC.ts[b]) - int(SC.ts[a])) / 60000.0
print('# W_DGATE %s   exhaustion window %d bars = %.1f min (W_EXH_FRAC %.2f x ws%d)'
      % (C.DGATE, C.EXH_BARS, C.EXH_BARS * 5 / 60.0, C.EXH_FRAC, TF))
print('# XWOB_WS12X %d bars = %.0f s   oob_gate_bars %d = %.1f min   stop %.2f'
      % (C.XW12, C.XW12 * 5, C.GATE_BARS, C.GATE_BARS * 5 / 60.0, C.MAE_STOP), flush=True)

def chain():
    out = []; k, d, g = 1, +1, 0
    while True:
        g += 1
        if g > 20000: break
        xk, why, mae, cb, hand, tr = C.run_leg(k, d)
        if xk is None: break
        p0 = float(PXa[k]); sgn = 1 if d > 0 else -1
        seg = PXa[k:xk + 1]; ok = np.isfinite(seg) & (seg > 0)
        rel = np.where(ok, (seg - p0) / p0 * 100.0 * sgn, 0.0)
        out.append(dict(n=len(out) + 1, open=k, exit=xk, d=d, why=why, hand=hand, tr=tr,
                        mae=(C.MAE_STOP if why == 'mae breach' else -float(rel.min())),
                        mfe=(0.0 if why == 'mae breach' else float(rel.max())),
                        rawmfe=float(rel.max()),
                        real=(float(PXa[xk]) - p0) / p0 * 100.0 * sgn))
        if k > D1: break
        if why == 'mae breach':
            rb, cf, sd = T.find_reentry(xk, T.gate_A, N - 1)
            if cf is None: break
            k, d = cf, sd; continue
        if xk >= N - 1: break
        k = xk; d = -d
    return out

legs = chain()
print('# %d legs to the end of 08-22' % len(legs), flush=True)

# the interchanges: the bar oob_a is set, per leg, on the leg's own side
SIG = []
for L in legs:
    if L['exit'] < D0 or L['open'] > D1: continue
    oa = None
    for j in range(L['open'] + 1, L['exit'] + 1):
        on = (float(R12[j]) >= HI) if L['d'] > 0 else (float(R12[j]) <= LO)
        if on and oa is None:
            oa = j
            if D0 <= j <= D1: SIG.append((j, L))
        elif not on:
            oa = None
SIG = SIG[:4]
print('# %d interchanges on 08-22, showing the first %d\n' % (len(SIG), len(SIG)), flush=True)

xu = lambda z: float(X12[z]) < float(R12[z])
for n, (sig, L) in enumerate(SIG, 1):
    i = legs.index(L)
    prev = legs[i - 1] if i else None
    nxt = legs[i + 1] if i + 1 < len(legs) else None
    p0 = float(PXa[L['open']]); sgn = 1 if L['d'] > 0 else -1
    pct = lambda j: '%+.4f' % ((float(PXa[j]) - p0) / p0 * 100.0 * sgn)
    rel = lambda j: '%+.1f' % mn(L['open'], j)
    print('\n\n# SIGNAL %d of %d — ws%dr oob interchange at %s on %s, A-trade %s'
          % (n, len(SIG), TF, U(sig), DAY(sig), 'LONG' if L['d'] > 0 else 'SHORT'))
    rows = []
    if prev is not None:
        pp = float(PXa[prev['open']]); ps = 1 if prev['d'] > 0 else -1
        rows.append((U(prev['open']), rel(prev['open']),
                     'INCOMING TRADE OPENS %s' % ('LONG' if prev['d'] > 0 else 'SHORT'),
                     '%.6f' % pp, pct(prev['open'])))
        for j, lbl in prev['tr']:
            rows.append((U(j), rel(j), 'incoming: %s' % lbl, '%.6f' % float(PXa[j]), pct(j)))
        rows.append((U(prev['exit']), rel(prev['exit']),
                     'INCOMING TRADE CLOSES on %s, its realised %+.4f, MAE %.4f, MFE %.4f'
                     % (prev['why'], prev['real'], prev['mae'], prev['mfe']),
                     '%.6f' % float(PXa[prev['exit']]), pct(prev['exit'])))
    rows.append((U(L['open']), '+0.0', '>>> A-TRADE OPENS %s'
                 % ('LONG' if L['d'] > 0 else 'SHORT'), '%.6f' % p0, '+0.0000'))
    ev = list(L['tr'])
    ev.append((sig, '### ws%dr CROSSES INTO %s oob at %.2f — THE INTERCHANGE. the dwell clock '
                    'starts; exhaustion window to %s, dwell-ending at %s'
               % (TF, 'HIGH' if L['d'] > 0 else 'LOW', float(R12[sig]),
                  U(min(N - 1, sig + C.EXH_BARS)), U(min(N - 1, sig + C.GATE_BARS + 1)))))
    for j, lbl in sorted(ev, key=lambda z: z[0]):
        rows.append((U(j), rel(j), lbl, '%.6f' % float(PXa[j]), pct(j)))
    rows.append((U(L['exit']), rel(L['exit']),
                 '>>> A-TRADE CLOSES on %s' % L['why'], '%.6f' % float(PXa[L['exit']]),
                 pct(L['exit'])))
    if nxt is not None and nxt['open'] == L['exit']:
        np0 = float(PXa[nxt['open']])
        rows.append((U(nxt['open']), rel(nxt['open']),
                     '>>> B-TRADE OPENS %s at the same bar'
                     % ('LONG' if nxt['d'] > 0 else 'SHORT'), '%.6f' % np0, pct(nxt['open'])))
        for j, lbl in nxt['tr']:
            rows.append((U(j), rel(j), 'B: %s' % lbl, '%.6f' % float(PXa[j]), pct(j)))
        rows.append((U(nxt['exit']), rel(nxt['exit']),
                     '>>> B-TRADE CLOSES on %s, its realised %+.4f' % (nxt['why'], nxt['real']),
                     '%.6f' % float(PXa[nxt['exit']]), pct(nxt['exit'])))
    box(('ts', 'min from A\'s open', 'event', 'pxs', 'pct for the A-trade'), rows)
    out = [('A-trade', 'LONG' if L['d'] > 0 else 'SHORT', U(L['open']), U(L['exit']),
            '%.1f' % mn(L['open'], L['exit']), L['why'], '%.4f' % L['mae'], '%.4f' % L['mfe'],
            '%.4f' % L['rawmfe'], '%+.4f' % L['real'],
            '%.4f' % (L['mfe'] / L['mae']) if L['mae'] else '—')]
    if nxt is not None and nxt['open'] == L['exit']:
        out.append(('B-trade', 'LONG' if nxt['d'] > 0 else 'SHORT', U(nxt['open']), U(nxt['exit']),
                    '%.1f' % mn(nxt['open'], nxt['exit']), nxt['why'], '%.4f' % nxt['mae'],
                    '%.4f' % nxt['mfe'], '%.4f' % nxt['rawmfe'], '%+.4f' % nxt['real'],
                    '%.4f' % (nxt['mfe'] / nxt['mae']) if nxt['mae'] else '—'))
    print('\n### THE RESULT')
    box(('the trade', 'side', 'open', 'close', 'hold min', 'why', 'MAE', 'MFE as scored',
         'MFE raw', 'realised', 'MFE/MAE'), out)
    print('- "MFE as scored" is 0.0000 on a stopped leg, Joe 1007. "MFE raw" is the real excursion.')
