"""THE 60 LOOP ARMS OVER THE WHOLE TAPE, EVERY LEG BANKED PER DAY. 1010.

Joe 1010: *"did you sweep in steps of 1? that would be the next move before we hold out"* / *"hit
it"*.

  ONE CONTINUOUS CHAIN PER ARM, NOT ONE PER DAY. The chain is continuous by design - a leg's exit
  IS the next leg's open - so restarting it at every midnight would invent 94 artificial opens and
  94 arbitrary starting sides. Each leg is instead TAGGED with the UTC date it opened in, and any
  day split is then a reporting operation on the banked legs. It is also ~94x cheaper: 60 chains,
  not 5,640. STATED, because it is a change from the single-day sweep.

  NO SPLIT IS APPLIED. Joe has not named the in-sample / hold-out cut, so every leg of every arm is
  written to the TSV and the split stays his to make. Nothing here chooses a winner.

  THE START is the first bar where every line this build reads is finite - data-driven, not a cap.
  THE SIDE of the first leg is SHORT; over hundreds of legs the first side's effect is one leg.
  A STOPPED LEG CLOSES AND FLIPS, it does not halt the chain, same as the single-day sweep.
  DRAG IS ITS OWN COLUMN at 0.11% per leg boundary, never folded into gross.

  THE LIVE CONTROL is asserted, not assumed: the single-day arm `loop off / on_stall` from
  03:13:15 SHORT must reproduce 15 legs and gross +5.8153 inside THIS process before the tape run
  starts. A hash-keyed line cache that silently serves a different window fails this.
"""
import os, sys, time, datetime
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C

SC, box, U, PX = C.SC, C.box, C.SC.U, C.PX
N = len(SC.ts)
DRAG = float(os.environ.get('W_DRAG', 0.11))
OUT = os.environ.get('W_OUT', '/home/joe/.claude/jobs/6eb9931e/tmp/loop_holdout_legs.tsv')
DAYOF = lambda k: datetime.datetime.utcfromtimestamp(int(SC.ts[k]) / 1000).strftime('%Y-%m-%d')

# the first bar where every line is finite
need = [C.R[t] for t in C.ALL_TF] + [C.X[t] for t in C.ALL_TF] + [C.MARM, C.G1, PX]
K0 = max(int(np.argmax(np.isfinite(np.asarray(a, float)[:N]))) for a in need)
print('# TAPE %d bars, %s -> %s. first all-finite bar %d = %s'
      % (N, U(0), U(N - 1), K0, U(K0)), flush=True)
print('# ceiling %d, lin_hop %d, W_KICK %s, W_STALL_UP %s, W_NOX %s, W_NO_GT12 %s, stop %.2f, '
      'drag %.2f%%/boundary'
      % (C.CEIL_HI, C.LIN_HOP, C.KICK, C.STALL_UP, C.NOX, C.NO12, C.MAE_STOP, DRAG), flush=True)


def chain(k_start, d_start, k_end):
    """one continuous chain. -> list of leg dicts. A stop closes and flips."""
    k, d, out = k_start, d_start, []
    while k < k_end:
        xk, why, mae, cb, hand, tr = C.run_leg(k, d)
        if xk is None or xk > k_end:
            break
        p0 = float(PX[k]); sg = 1 if d > 0 else -1
        out.append(dict(day=DAYOF(k), open=k, exit=xk, d=d, why=why, mae=mae,
                        real=(float(PX[xk]) - p0) / p0 * 100.0 * sg,
                        loops=sum(1 for _, t in tr if t.startswith('LOOP ')),
                        hold=(int(SC.ts[xk]) - int(SC.ts[k])) / 60000.0))
        k = xk; d = -d
    return out


# ---- THE LIVE CONTROL, asserted
C.LOOP_TFS, C.EXH_LOOP = [], 'on_stall'
_c = chain(SC.K('2026-07-15 03:13:15'), -1, SC.K('2026-07-15 23:59:55'))
_g = sum(l['real'] for l in _c)
print('# CONTROL loop off / on_stall, 2026-07-15 03:13:15 SHORT: %d legs, gross %+.4f'
      % (len(_c), _g), flush=True)
assert len(_c) == 15 and abs(_g - 5.8153) < 5e-4, \
    'CONTROL DRIFTED: expected 15 legs / +5.8153, got %d / %+.4f' % (len(_c), _g)
print('# control matches the 1010 single-day sweep. proceeding.', flush=True)

ARMS = [('off', e) for e in ('on_stall', 'always')] + \
       [(str(t), e) for t in range(2, C.CEIL_HI + 1) for e in ('on_stall', 'always')]
fh = open(OUT, 'w')
fh.write('loop_tf\texhaustion\tday\topen\texit\tside\twhy\tloops\thold_min\tmae\trealised\n')
rows = []
t0 = time.time()
for i, (lt, e) in enumerate(ARMS):
    C.LOOP_TFS = [] if lt == 'off' else [int(lt)]
    C.EXH_LOOP = e
    legs = chain(K0, -1, N - 1)
    for l in legs:
        fh.write('%s\t%s\t%s\t%s\t%s\t%s\t%s\t%d\t%.1f\t%.4f\t%+.4f\n'
                 % (lt, e, l['day'], U(l['open']), U(l['exit']),
                    'LONG' if l['d'] > 0 else 'SHORT', l['why'], l['loops'], l['hold'],
                    l['mae'], l['real']))
    fh.flush()
    g = sum(l['real'] for l in legs); dr = len(legs) * DRAG
    days = sorted({l['day'] for l in legs})
    pos = sum(1 for l in legs if l['real'] > 0)
    rows.append((lt, e, str(len(legs)), str(len(days)), '%.1f' % float(np.median([l['hold'] for l in legs])),
                 '%+.4f' % g, '%.2f' % dr, '%+.4f' % (g - dr),
                 '%d' % sum(1 for l in legs if l['why'] == 'mae breach'),
                 '%d' % sum(l['loops'] for l in legs), '%.1f%%' % (100.0 * pos / len(legs))))
    print('# [%5.0fs] %2d/%d  loop %-3s %-8s  legs %4d over %d days  net %+9.4f'
          % (time.time() - t0, i + 1, len(ARMS), lt, e, len(legs), len(days), g - dr), flush=True)
fh.close()
box(('loop tf', 'exhaustion', 'legs', 'days', 'median hold min', 'gross', 'drag',
     'NET AFTER DRAG', 'stops', 'loops', 'positive legs'), rows)
print('- every leg of every arm is in %s, one row per leg, tagged with the day it OPENED in.' % OUT)
print('- no in-sample / hold-out split is applied. That cut is Joe\'s.')
print('- drag is %.2f%% x the leg count, its own column.' % DRAG)
