"""08-22's CHAIN LEGS, THE DELEGATED WALKS, AND THE UPDATED DECISION TABLE. 1009.

Joe 1009: *"we don't need to use the close just yet - we need to see the individual 08-22 delegated
walks (chain legs), and the final MAE MFE of each leg, from the working table (below, needs an
update on 07:36) / the delegations are either a trade signal (loose use of "delegation"), or
`>ws12r oob`"*.

TWO PARTS.

  PART 1  the 5-row decision table, UPDATED for the 1009 ruling - TRAJ_MIN_TAIL_LIFE dropped, the
          4 mage/r rules for `dir 0` only. So `traj`'s answer stands on every row where it has a
          direction, which on 08-22 is all 5.

  PART 2  the chain's legs across 08-22, run from the tape seed so they are the real legs, with
          each leg's own MAE, MFE and realised, and the full walk of every leg that carries a
          ws12r oob dwell-ending.

THE CHAIN IS THE BANKED BUILD, UNTOUCHED: x-cross on ws{h+1}b no in-fence, mae_stop_pct 2.5,
reent_xwob 18, ceil_hi 23, oob_gate_bars 72, dip_dwell_bars 6, W_DGATE off. Nothing from `traj` is
wired in - the decision table says what it WOULD have returned, the legs say what the chain DID.

A LEG'S MAE/MFE is measured from its own open on its own side across its own span. A stopped leg
scores MAE = mae_stop_pct and MFE 0.0000, Joe 1007.
"""
import os, sys, datetime
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from _trajmech import traj
import _chain10 as C
import _chain_2day as T

SC, box, U = C.SC, C.box, C.SC.U
PXa = C.PX
N = len(SC.ts)
R60 = np.asarray(SC.LD(60 * 60, 'r'), float)[:N]
M60 = np.asarray(SC.LD(60 * 60, 'Mage'), float)[:N]
R12 = C.R[C.TRIG_TF]
HI, LO = SC.HI, SC.LO
GATE, BLOCK, TAIL, LOOK_N, TF = C.GATE_BARS, 60, 2, 24, C.TRIG_TF
DAY = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                               datetime.timezone.utc).strftime('%Y-%m-%d')
D0, D1 = SC.K('2026-08-22 00:00:00'), SC.K('2026-08-22 23:59:55')
print('# the banked build: x-cross ws{h+1}%s fence %d, stop %.2f, reent_xwob %d, ceil_hi %d,'
      ' oob_gate_bars %d, dip_dwell_bars %d, W_DGATE %s'
      % (C.XT_ROLE, C.XT_FENCE, C.MAE_STOP, T.XWOB, C.CEIL_HI, GATE, C.DIP_DWELL, C.DGATE),
      flush=True)
print('# traj: block %d = %.0f min, tail %d = %.0f min, lookback %d = %.0f min, kind close'
      % (BLOCK, BLOCK * 5 / 60.0, TAIL, TAIL * BLOCK * 5 / 60.0, LOOK_N,
         LOOK_N * BLOCK * 5 / 60.0), flush=True)

# ---- the ws12r oob crossings on 08-22 that reach a dwell-ending
EV = []
k = max(1, D0)
while k <= D1:
    for side in (+1, -1):
        now = (float(R12[k]) >= HI) if side > 0 else (float(R12[k]) <= LO)
        was = (float(R12[k - 1]) >= HI) if side > 0 else (float(R12[k - 1]) <= LO)
        if now and not was:
            j = k
            while j < N and (((float(R12[j]) >= HI) if side > 0 else (float(R12[j]) <= LO))): j += 1
            if j - k > GATE + 1: EV.append((k, side, j - k, j, k + GATE + 1))
            break
    k += 1

EYE = {'01:30:05': 'FALSE', '07:42:05': 'TRUE', '13:39:55': 'TRUE',
       '15:32:20': 'FALSE', '19:06:05': 'FALSE'}
print('\n# PART 1 — THE DECISION TABLE, UPDATED FOR THE 1009 RULING')
rows = []
DEC = {}
for kx, side, run, end, b in EV:
    r = traj(R60, b, BLOCK, TAIL, LOOK_N, 'close', side)
    g = float(M60[b]) - float(R60[b])
    if r['dir'] == 0:
        ret = (1 if g > 0 else -1) == -side
        src = 'the 4 mage/r rules — dir 0'
    else:
        ret = (r['dir'] == -side)
        src = 'traj'
    got = 'TRUE' if ret else 'FALSE'
    DEC[b] = (got, side, kx, end)
    want = EYE.get(U(b))
    rows.append((U(b), 'high oob' if side > 0 else 'low oob',
                 'UP' if r['dir'] > 0 else ('DOWN' if r['dir'] < 0 else 'flat'),
                 '%+.4f' % r['travel'] if np.isfinite(r['travel']) else '—',
                 '%.0f' % (r['tail_used'] * BLOCK * 5 / 60.0),
                 '%.4f' % float(M60[b]), '%.4f' % float(R60[b]), '%+.4f' % g,
                 src, '**%s**' % got, want or '—',
                 'MATCH' if want == got else ('**MISS**' if want else '—'),
                 'a TRADE SIGNAL' if ret else '>ws12r oob'))
box(('the dwell-ending', 'side', 'traj dir', 'traj travel', "tail's life, min", 'ws60Mage',
     'ws60r', 'Mage - r', 'the direction came from', 'THE RETURN', 'your eye', 'verdict',
     'the delegation goes to'), rows)

# ---- PART 2: the chain from the seed
print('\n# PART 2 — THE CHAIN. running from the tape seed so 08-22\'s legs are the real legs ...',
      flush=True)
legs = []; k, d, g = 1, +1, 0
run_real = 0.0
while True:
    g += 1
    if g > 20000: break
    xk, why, mae, cb, hand, tr = C.run_leg(k, d)
    if xk is None: break
    p0 = float(PXa[k]); sgn = 1 if d > 0 else -1
    seg = PXa[k:xk + 1]; ok = np.isfinite(seg) & (seg > 0)
    rel = np.where(ok, (seg - p0) / p0 * 100.0 * sgn, 0.0)
    real = (float(PXa[xk]) - p0) / p0 * 100.0 * sgn
    run_real += real
    legs.append(dict(n=len(legs) + 1, open=k, exit=xk, d=d, why=why, hand=hand, tr=tr,
                     mae=(C.MAE_STOP if why == 'mae breach' else -float(rel.min())),
                     mfe=(0.0 if why == 'mae breach' else float(rel.max())),
                     real=real, run=run_real))
    if k > D1: break
    if why == 'mae breach':
        rb, cf, sd = T.find_reentry(xk, T.gate_A, N - 1)
        if cf is None: break
        k, d = cf, sd; continue
    if xk >= N - 1: break
    k = xk; d = -d

day = [L for L in legs if not (L['exit'] < D0 or L['open'] > D1)]
mn = lambda a, b: (int(SC.ts[b]) - int(SC.ts[a])) / 60000.0
dwl = {}
for b, (got, side, kx, end) in DEC.items():
    for L in day:
        if L['open'] <= b <= L['exit']: dwl.setdefault(L['n'], []).append((b, got, kx))

print('\n# EVERY CHAIN LEG TOUCHING 2026-08-22')
box(('leg', 'side', 'open', 'exit', 'hold min', 'why', 'leg MAE', 'leg MFE', 'realised',
     'running realised', 'carries a ws12r oob dwell-ending', 'the dwell-ending', 'THE RETURN'),
    [(str(L['n']), 'LONG' if L['d'] > 0 else 'SHORT', U(L['open']), U(L['exit']),
      '%.1f' % mn(L['open'], L['exit']), L['why'], '%.4f' % L['mae'], '%.4f' % L['mfe'],
      '%+.4f' % L['real'], '%+.4f' % L['run'],
      'YES — delegated' if L['hand'] is not None else ('yes, not delegated'
                                                       if L['n'] in dwl else 'no'),
      ', '.join(U(b) for b, _, _ in dwl.get(L['n'], [])) or '—',
      ', '.join(gt for _, gt, _ in dwl.get(L['n'], [])) or '—') for L in day])

print('\n# THE WALK OF EVERY LEG CARRYING A ws12r oob DWELL-ENDING')
for L in day:
    if L['n'] not in dwl: continue
    p0 = float(PXa[L['open']]); sgn = 1 if L['d'] > 0 else -1
    pct = lambda j: '%+.4f' % ((float(PXa[j]) - p0) / p0 * 100.0 * sgn)
    rel = lambda j: '%+.1f' % mn(L['open'], j)
    print('\n## LEG %d — %s   open %s   exit %s on %s   MAE %.4f   MFE %.4f   realised %+.4f'
          % (L['n'], 'LONG' if L['d'] > 0 else 'SHORT', U(L['open']), U(L['exit']), L['why'],
             L['mae'], L['mfe'], L['real']))
    for b, got, kx in dwl[L['n']]:
        print('   the ws12r oob crossing %s, dwell-ending %s -> THE RETURN %s (%s)'
              % (U(kx), U(b), got, 'a TRADE SIGNAL' if got == 'TRUE' else '>ws12r oob'))
    box(('ts', '+min', 'event', 'pxs', 'pct for this leg'),
        [(U(L['open']), '+0.0', 'OPEN %s' % ('LONG' if L['d'] > 0 else 'SHORT'),
          '%.6f' % p0, '+0.0000')]
        + [(U(j), rel(j), lbl, '%.6f' % float(PXa[j]), pct(j)) for j, lbl in L['tr']]
        + [(U(L['exit']), rel(L['exit']), 'EXIT on %s' % L['why'],
            '%.6f' % float(PXa[L['exit']]), pct(L['exit']))])
print('\n# THE DAY')
box(('the measure', 'value'),
    [('legs touching 08-22', str(len(day))),
     ('of them, delegated to >ws12r oob', str(sum(1 for L in day if L['hand'] is not None))),
     ('ws12r oob dwell-endings on 08-22', str(len(EV))),
     ('the return would be a TRADE SIGNAL', str(sum(1 for v in DEC.values() if v[0] == 'TRUE'))),
     ('the return would stay >ws12r oob', str(sum(1 for v in DEC.values() if v[0] == 'FALSE'))),
     ('summed realised across the day\'s legs', '%+.4f' % sum(L['real'] for L in day)),
     ('summed leg MAE', '%.4f' % sum(L['mae'] for L in day)),
     ('summed leg MFE', '%.4f' % sum(L['mfe'] for L in day)),
     ('MFE/MAE across the day', '%.4f' % (sum(L['mfe'] for L in day)
                                          / sum(L['mae'] for L in day)
                                          if sum(L['mae'] for L in day) else 0))])
