"""HOW OFTEN DOES B ACTUALLY OPEN — the ws12r stall / x-cross inside the oob run. 1009.

Joe 1009: *"we test ws60r at the end of the dwell, and act on the stall/x-cross"* / *"check the
count"*.

THE QUESTION: on a refusal, B opens at ws12r's own stall or x-cross INSIDE the oob run. If that
event is usually absent, B almost never opens and the whole mech is the refusal, not the signal.

RUN ON THE CHAIN ITSELF, so every bar is the one `run_leg` uses: the leg's own `oob_a`, the leg's
own side, the dwell-ending the chain computes. W_DGATE=once supplies the refusals.

  ws12r stalled   `ST[(12, d)]` - the same stall mask run_leg reads
  ws12x x-cross   ws12x crossing ws12r counter to the oob side, the branch-1 condition
  the window      the dwell-ending to the last bar of that oob run. Nothing beyond it.

THE A-CLOSE / B-OPEN BAR IS THE SIGNAL BAR. Reported per event, with the minutes from the
dwell-ending and the pxs at both bars so the entry difference is visible.
"""
import os, sys, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
import _chain_2day as T

assert C.DGATE == 'once', 'run with W_DGATE=once'
SC, box, U = C.SC, C.box, C.SC.U
PXa = C.PX
N = len(SC.ts); TF = C.TRIG_TF
R12, X12, ST = C.R[TF], C.X[TF], C.ST
HI, LO = SC.HI, SC.LO
DAY = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                               datetime.timezone.utc).strftime('%Y-%m-%d')
_days = sorted({DAY(k) for k in range(0, N, 2000)})
BLK = {'fit': set(_days[:47]), 'hold': set(_days[47:])}
print('# gate %s, oob_gate_bars %d, traj tail %d look %d block %d kind %s'
      % (C.DGATE, C.GATE_BARS, C.TRAJ_TAIL, C.TRAJ_LOOK, C.TRAJ_BLOCK, C.TRAJ_KIND), flush=True)

u = lambda z: float(X12[z]) < float(R12[z])
def oob_end(b, d):
    j = b
    while j < N and (((float(R12[j]) >= HI) if d > 0 else (float(R12[j]) <= LO))): j += 1
    return j - 1

def first_signal(b, d, end):
    for q in range(b, min(end, N - 1) + 1):
        st = bool(ST[(TF, d)][q])
        xc = q >= 1 and (((u(q) and not u(q - 1))) if d > 0 else ((not u(q)) and u(q - 1)))
        if st and xc: return q, 'both on the same bar'
        if st: return q, 'ws%dr stalled' % TF
        if xc: return q, 'ws%dx crossed ws%dr' % (TF, TF)
    return None, 'neither inside the oob run'

ref = []
k, d, g = 1, +1, 0
while True:
    g += 1
    if g > 20000: break
    xk, why, mae, cb, hand, tr = C.run_leg(k, d)
    if xk is None: break
    for j, lbl in tr:
        if lbl.startswith('DELEGATION REFUSED'):
            end = oob_end(j, d)
            sb, sw = first_signal(j, d, end)
            ref.append(dict(dwell=j, d=d, end=end, sb=sb, sw=sw, legopen=k, legexit=xk, why=why))
    if why == 'mae breach':
        rb, cf, sd = T.find_reentry(xk, T.gate_A, N - 1)
        if cf is None: break
        k, d = cf, sd; continue
    if xk >= N - 1: break
    k = xk; d = -d

mn = lambda a, b: (int(SC.ts[b]) - int(SC.ts[a])) / 60000.0
got = [r for r in ref if r['sb'] is not None]
print('\n# THE COUNT — every refusal across 95 days')
box(('the measure', 'all 95 days', 'fit', 'hold'),
    [('refusals', str(len(ref)),
      str(sum(1 for r in ref if DAY(r['dwell']) in BLK['fit'])),
      str(sum(1 for r in ref if DAY(r['dwell']) in BLK['hold']))),
     ('**B OPENS** — a stall or x-cross inside the oob run', '**%d**' % len(got),
      str(sum(1 for r in got if DAY(r['dwell']) in BLK['fit'])),
      str(sum(1 for r in got if DAY(r['dwell']) in BLK['hold']))),
     ('as %', '%.1f%%' % (100.0 * len(got) / len(ref)) if ref else '—',
      '%.1f%%' % (100.0 * sum(1 for r in got if DAY(r['dwell']) in BLK['fit'])
                  / max(1, sum(1 for r in ref if DAY(r['dwell']) in BLK['fit']))),
      '%.1f%%' % (100.0 * sum(1 for r in got if DAY(r['dwell']) in BLK['hold'])
                  / max(1, sum(1 for r in ref if DAY(r['dwell']) in BLK['hold'])))),
     ('**NO B** — the oob run ends first', '**%d**' % (len(ref) - len(got)),
      str(sum(1 for r in ref if r['sb'] is None and DAY(r['dwell']) in BLK['fit'])),
      str(sum(1 for r in ref if r['sb'] is None and DAY(r['dwell']) in BLK['hold'])))])

wc = collections.Counter(r['sw'] for r in ref)
box(('what fired', 'refusals', 'as %'),
    [(w, str(c), '%.1f%%' % (100.0 * c / len(ref))) for w, c in wc.most_common()])

if got:
    lag = sorted(mn(r['dwell'], r['sb']) for r in got)
    rl = sorted(mn(r['dwell'], r['end']) for r in ref)
    box(('the timing', 'min'),
        [('B opens this long after the dwell-ending — median', '%.1f' % lag[len(lag) // 2]),
         ('the same, 25th / 75th', '%.1f / %.1f' % (lag[len(lag) // 4], lag[3 * len(lag) // 4])),
         ('the same, min / max', '%.1f / %.1f' % (lag[0], lag[-1])),
         ('the oob run has this much left at the dwell-ending — median',
          '%.1f' % rl[len(rl) // 2]),
         ('the same, min / max', '%.1f / %.1f' % (rl[0], rl[-1]))])
    ent = [(float(PXa[r['sb']]) - float(PXa[r['dwell']])) / float(PXa[r['dwell']]) * 100.0 * (-r['d'])
           for r in got]
    box(('B\'s entry at the signal bar vs at the dwell-ending', 'value'),
        [('mean, + = a BETTER entry for B', '%+.4f%%' % (sum(ent) / len(ent))),
         ('median', '%+.4f%%' % sorted(ent)[len(ent) // 2]),
         ('better on', '%d of %d' % (sum(1 for e in ent if e > 0), len(ent))),
         ('worse on', '%d of %d' % (sum(1 for e in ent if e < 0), len(ent)))])

print('\n# EVERY REFUSAL, in time order')
box(('day', 'the dwell-ending', 'A was', 'the oob run ends', 'run left, min', 'B opens',
     'what fired', 'min after the dwell-ending', 'pxs at the dwell-ending', 'pxs at B\'s open',
     'B entry better by'),
    [(DAY(r['dwell']), U(r['dwell']), 'LONG' if r['d'] > 0 else 'SHORT', U(r['end']),
      '%.1f' % mn(r['dwell'], r['end']),
      U(r['sb']) if r['sb'] else '— no B', r['sw'],
      '%.1f' % mn(r['dwell'], r['sb']) if r['sb'] else '—',
      '%.6f' % float(PXa[r['dwell']]),
      '%.6f' % float(PXa[r['sb']]) if r['sb'] else '—',
      '%+.4f%%' % ((float(PXa[r['sb']]) - float(PXa[r['dwell']])) / float(PXa[r['dwell']])
                   * 100.0 * (-r['d'])) if r['sb'] else '—')
     for r in ref])
