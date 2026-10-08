"""THE ws60r GATE, PAIRED PER LEG — no chain, no re-phasing. 1008.

Joe 1008: *"run that"*, on my proposal: score only the legs the gate touches, each run twice from
the SAME open bar, so the chain never continues and nothing downstream moves.

WHY. Every whole-chain number I gave for the gate is contaminated the same way Joe invalidated the
ceil_hi comparison: a refused delegation moves that leg's exit bar, the next leg opens AT that exit
bar, and every leg after it re-phases. 17 of 1623 legs were bar-identical across a ceil_hi change.
57 refusals move 1,600 legs' phases, so the 40-pair mean of -13.2173 is not evidence about the gate.

THE DESIGN
  the population   every leg in the UNGATED chain whose handover fired while ws60r's trajectory was
                   AGAINST the oob side. Those are exactly the delegations the gate would refuse.
  each one twice   run_leg(open, side) with the gate OFF, then with the gate ON. Same open bar,
                   same side, same lines. The only difference is the refusal.
  what is compared that leg's own realised, MAE, MFE, exit bar and exit reason.
  what is removed  the chain. Neither arm continues past the leg, so no open bar moves.

n IS THE REFUSAL COUNT, not the leg count. Reported, split fit / hold.

SECOND DELIVERABLE, Joe 1008: *"show me all of the ws12r oob timestamps between 08-22 and 08-27
where the ws60r trajectory was down if ws12r was low oob, or trajectory up if ws12r was high oob"*.
That is the gate-OPEN condition. The traj is printed at BOTH candidate bars - the oob crossing and
the dwell-ending - because which one the gate should read has never been ruled.
"""
import os, sys, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
import _chain_2day as T

assert C.DGATE != 'off', 'import with W_DGATE=once so TRAJ60 is built; the arms flip C.DGATE'
SC, PX, box, U = C.SC, C.PX, C.box, C.SC.U
N = len(SC.ts); FEE = 0.11
TRAJ, TF = C.TRAJ60, C.TRIG_TF
R12 = C.R[TF]; HI, LO = SC.HI, SC.LO
DAY = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                               datetime.timezone.utc).strftime('%Y-%m-%d')
_days = sorted({DAY(k) for k in range(0, N, 2000)})
BLK = {'fit': set(_days[:47]), 'hold': set(_days[47:])}
print('# tape %d bars; ws%dr trigger, oob %.0f/%.0f, stop %.2f' % (N, TF, LO, HI, C.MAE_STOP),
      flush=True)

def score(k, d, xk, why):
    p0 = float(PX[k]); sgn = 1 if d > 0 else -1
    seg = PX[k:xk + 1]; ok = np.isfinite(seg) & (seg > 0)
    rel = np.where(ok, (seg - p0) / p0 * 100.0 * sgn, 0.0)
    real = (float(PX[xk]) - p0) / p0 * 100.0 * sgn
    if why == 'mae breach': return real, C.MAE_STOP, 0.0
    return real, -float(rel.min()), float(rel.max())

def arm(ceil, gb, dd):
    C.CEIL_HI, C.GATE_BARS, C.DIP_DWELL = ceil, gb, dd
    C.DGATE = 'off'
    legs = []; k, d, g = 1, +1, 0
    while True:
        g += 1
        if g > 20000: break
        xk, why, mae, cb, hand, tr = C.run_leg(k, d)
        if xk is None: break
        legs.append((k, d, xk, why, hand))
        if why == 'mae breach':
            rb, cf, sd = T.find_reentry(xk, T.gate_A, N - 1)
            if cf is None: break
            k, d = cf, sd; continue
        if xk >= N - 1: break
        k = xk; d = -d
    # the delegations the gate would refuse
    cand = [(k, d, xk, why, hand) for k, d, xk, why, hand in legs
            if hand is not None and int(TRAJ[hand]) != (1 if d > 0 else -1)]
    rows = []
    for k, d, xk, why, hand in cand:
        C.DGATE = 'off'
        a = C.run_leg(k, d)
        C.DGATE = 'once'
        b = C.run_leg(k, d)
        C.DGATE = 'off'
        if a[0] is None or b[0] is None: continue
        ra, aa, fa = score(k, d, a[0], a[1])
        rb_, ab, fb = score(k, d, b[0], b[1])
        rows.append(dict(open=k, d=d, hand=hand, traj=int(TRAJ[hand]),
                         xa=a[0], wa=a[1], ra=ra, aa=aa, fa=fa,
                         xb=b[0], wb=b[1], rb=rb_, ab=ab, fb=fb))
    return legs, cand, rows

CFG = [(23, 72, 6, 'THE BANKED BUILD'),
       (12, 192, 18, 'THE ONE GATED ARM THAT BEAT BANKED ON BOTH HALVES')]
for ceil, gb, dd, lab in CFG:
    legs, cand, rows = arm(ceil, gb, dd)
    nh = sum(1 for z in legs if z[4] is not None)
    print('\n\n# %s — ceil_hi %d, oob_gate_bars %d, dip_dwell_bars %d' % (lab, ceil, gb, dd),
          flush=True)
    box(('the measure', 'value'),
        [('legs in the ungated chain', str(len(legs))),
         ('of them, delegated', str(nh)),
         ('delegations the gate would REFUSE', '**%d**' % len(cand)),
         ('as % of delegations', '%.1f%%' % (100.0 * len(cand) / nh) if nh else '—'),
         ('pairs scored', str(len(rows)))])
    if not rows: continue
    for blk in ('fit', 'hold', 'all'):
        rr = [r for r in rows if blk == 'all' or DAY(r['open']) in BLK[blk]]
        if not rr: continue
        dr = sum(r['rb'] - r['ra'] for r in rr)
        da = sum(r['ab'] - r['aa'] for r in rr)
        df = sum(r['fb'] - r['fa'] for r in rr)
        sa = sum(1 for r in rr if r['wa'] == 'mae breach')
        sb = sum(1 for r in rr if r['wb'] == 'mae breach')
        mma = sum(r['fa'] for r in rr) / sum(r['aa'] for r in rr) if sum(r['aa'] for r in rr) else 0
        mmb = sum(r['fb'] for r in rr) / sum(r['ab'] for r in rr) if sum(r['ab'] for r in rr) else 0
        box(('the %s block' % blk, 'delegation ALLOWED', 'delegation REFUSED', 'delta'),
            [('pairs', str(len(rr)), str(len(rr)), '—'),
             ('summed realised', '%+.4f' % sum(r['ra'] for r in rr),
              '%+.4f' % sum(r['rb'] for r in rr), '**%+.4f**' % dr),
             ('summed MAE', '%.4f' % sum(r['aa'] for r in rr),
              '%.4f' % sum(r['ab'] for r in rr), '%+.4f' % da),
             ('summed MFE', '%.4f' % sum(r['fa'] for r in rr),
              '%.4f' % sum(r['fb'] for r in rr), '%+.4f' % df),
             ('MFE/MAE', '%.4f' % mma, '%.4f' % mmb, '%+.4f' % (mmb - mma)),
             ('legs stopped', str(sa), str(sb), '%+d' % (sb - sa)),
             ('pairs the refusal IMPROVES', '—',
              str(sum(1 for r in rr if r['rb'] > r['ra'])),
              '%d of %d' % (sum(1 for r in rr if r['rb'] > r['ra']), len(rr)))])
    print('\n## EVERY PAIR, in time order')
    box(('day', 'open', 'side', 'the dwell-ending', 'ws60r traj there', 'ALLOWED exit',
         'ALLOWED why', 'ALLOWED realised', 'REFUSED exit', 'REFUSED why', 'REFUSED realised',
         'realised delta', 'MAE allowed', 'MAE refused'),
        [(DAY(r['open']), U(r['open']), 'LONG' if r['d'] > 0 else 'SHORT', U(r['hand']),
          '%+d' % r['traj'], U(r['xa']), r['wa'], '%+.4f' % r['ra'],
          U(r['xb']), r['wb'], '%+.4f' % r['rb'], '%+.4f' % (r['rb'] - r['ra']),
          '%.4f' % r['aa'], '%.4f' % r['ab']) for r in sorted(rows, key=lambda z: z['open'])])

# ---- Joe's timestamp list
C.CEIL_HI, C.GATE_BARS, C.DIP_DWELL = 23, 72, 6
lo = SC.K('2026-08-22 00:00:00'); hi = SC.K('2026-08-27 23:59:55')
print('\n\n# EVERY ws12r oob CROSSING, 2026-08-22 to 2026-08-27, WHERE THE GATE IS OPEN')
print('# gate open = ws60r traj DOWN with ws12r low oob, or traj UP with ws12r high oob')
rows = []
k = max(1, lo)
while k <= hi:
    for side in (+1, -1):
        now = (float(R12[k]) >= HI) if side > 0 else (float(R12[k]) <= LO)
        was = (float(R12[k - 1]) >= HI) if side > 0 else (float(R12[k - 1]) <= LO)
        if now and not was:
            j = k
            while j < N and (((float(R12[j]) >= HI) if side > 0 else (float(R12[j]) <= LO))): j += 1
            run = j - k
            de = k + C.GATE_BARS + 1 if run > C.GATE_BARS + 1 else None
            tx = int(TRAJ[k]); td = int(TRAJ[de]) if de and de < N else None
            if tx == side:
                rows.append((DAY(k), U(k), 'high oob' if side > 0 else 'low oob',
                             '%.2f' % float(R12[k]),
                             '%+d' % tx, 'UP' if tx > 0 else 'DOWN',
                             '%.1f' % (run * 5 / 60.0),
                             U(de) if de else 'run too short — no dwell-ending',
                             ('%+d' % td) if td is not None else '—',
                             ('gate OPEN' if td == side else 'gate CLOSED') if td is not None else '—',
                             '%.6f' % float(PX[k])))
            break
    k += 1
box(('day', 'ws12r oob crossing', 'which side', 'ws12r there', 'ws60r traj at the crossing',
     'direction', 'oob run min', 'the dwell-ending', 'ws60r traj at the dwell-ending',
     'the gate at the dwell-ending', 'pxs at the crossing'), rows)
print('\n- every row listed has the gate OPEN AT THE CROSSING, which is Joe\'s condition.')
print('- the last two columns re-read ws60r at the dwell-ending, where the delegation actually')
print('  fires. A row can be OPEN at the crossing and CLOSED 6 minutes later.')
