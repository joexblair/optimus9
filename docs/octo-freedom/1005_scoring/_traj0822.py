"""traj ON ws12r's DELEGATION — 2026-08-22 ONLY, one row per event. 1009.

Joe 1009: *"are we good to test with ws12r oob in small batches?"* / *"just 08-22 for now"*.

WHAT IS WIRED: at every ws12r oob dwell-ending on 08-22, `traj` reads ws60r and the #7 polarity
turns it into the return Joe specified:
    FALSE  traj MATCHES the oob side -> no reversal -> delegate to `>ws12r oob`
    TRUE   traj OPPOSES the oob side -> pxs reverses -> ws12r prints a trade signal on its
           stalled or x-cross event
    dir 0  the wholly-flat fallback, ws60Mage vs ws60r

WHAT THIS RUN DOES NOT DO. It reports the signal bar and does not run the chain, so nothing is
scored. `W_DGATE` stays off and the knobs are untouched.

CORRECTED 1009: this docstring used to claim a TRUE trade was blocked on a missing close rule.
MY WORDS, and wrong - Joe 1009: *"the query on a close rule is confusing - our chain is
continuous"*. A signal bar is the current leg's exit and the next leg's open, like every other
exit in the chain.

ws12r's OWN stalled and x-cross events are located for the signal bar, per Joe's *"ws12r will print
a trade signal on it's stalled or x-cross event"*:
    stalled   `jig.stall_mask` on ws12r at the leg's oob side, the same masks run_leg uses
    x-cross   ws12x crossing ws12r counter to the oob side - the branch-1 condition

KNOBS: block 60 bars = 5 min (Joe), TRAJ_TAIL_TF_SAMP 2 samples = 10 min (the sweep's best and
within 0.1 pts of every other value), TRAJ_MULTI_TF_SAMP 2 -> 24 samples, sample kind `close`.
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
GATE, BLOCK, TAIL, LOOK_N = C.GATE_BARS, 60, 2, 24
TF = C.TRIG_TF
DAY = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                               datetime.timezone.utc).strftime('%Y-%m-%d')
print('# 2026-08-22 only. ws%dr trigger, oob %.0f/%.0f, oob_gate_bars %d = %.1f min'
      % (TF, LO, HI, GATE, GATE * 5 / 60.0))
print('# traj: block %d bars = %.0f min, tail %d samples = %.0f min, lookback %d samples = %.0f min,'
      ' sample kind close'
      % (BLOCK, BLOCK * 5 / 60.0, TAIL, TAIL * BLOCK * 5 / 60.0, LOOK_N,
         LOOK_N * BLOCK * 5 / 60.0), flush=True)

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
print('# %d ws12r oob crossings on 08-22; %d reach the dwell-ending' % (len(EV), len(reach)),
      flush=True)

u = lambda z: float(X12[z]) < float(R12[z])
def first_signal(b, side, end):
    """ws12r's own stalled or x-cross event at or after bar b, inside the oob run."""
    for q in range(b, min(end, N - 1) + 1):
        if bool(ST[(TF, side)][q]): return q, 'ws%dr stalled' % TF
        if q >= 1 and (((u(q) and not u(q - 1)) if side > 0 else ((not u(q)) and u(q - 1)))):
            return q, 'ws%dx crossed ws%dr' % (TF, TF)
    return None, 'neither inside the oob run'

rows = []
for kx, side, run, end in reach:
    b = kx + GATE + 1
    if b >= N: continue
    r = traj(R60, b, BLOCK, TAIL, LOOK_N, 'close', side)
    d = r['dir']
    if d == 0:
        g = float(M60[b]) - float(R60[b])
        ret = (1 if g > 0 else -1) == -side
        src = '#7 fallback, Mage %s r' % ('>' if g > 0 else '<')
    else:
        ret = (d == -side)
        src = 'traj'
    sb, sw = first_signal(b, side, end) if ret else (None, '—')
    rows.append((U(kx), 'high oob' if side > 0 else 'low oob', '%.2f' % float(R12[kx]),
                 '%.1f' % (run * 5 / 60.0), U(b), '%.4f' % float(R60[b]),
                 ('UP' if d > 0 else ('DOWN' if d < 0 else 'flat — #7')),
                 '%+.4f' % r['travel'] if np.isfinite(r['travel']) else '—',
                 str(r['tail_used']), '%.0f' % (r['tail_used'] * BLOCK * 5 / 60.0),
                 U(r['reversal_bar']) if r['reversal_bar'] else '—', str(r['deferred']),
                 src,
                 '**TRUE — ws12r prints a trade signal**' if ret else 'FALSE — delegate',
                 U(sb) if sb else '—', sw,
                 ('SHORT' if side > 0 else 'LONG') if ret else '—',
                 '%.6f' % float(PXa[b])))
print('\n# EVERY ws12r oob DWELL-ENDING ON 08-22 — one row per event, in time order')
box(('the ws12r oob crossing', 'which side', 'ws12r there', 'oob run min', 'the dwell-ending',
     'ws60r there', 'traj dir', 'traj travel', 'tail used, samples', 'tail min',
     'the reversal it truncated to', 'deferrals', 'the direction came from', 'THE RETURN',
     'the signal bar', 'the signal event', 'the signal side', 'pxs at the dwell-ending'), rows)

nt = sum(1 for r in rows if r[13].startswith('**TRUE'))
print('\n# THE DAY IN ONE BLOCK')
box(('the measure', 'value'),
    [('ws12r oob crossings', str(len(EV))),
     ('reaching the 6-min dwell-ending', str(len(reach))),
     ('TRUE — ws12r prints a trade signal', '**%d**' % nt),
     ('FALSE — delegate to >ws12r oob', str(len(rows) - nt)),
     ('of the TRUE rows, a signal bar was found', str(sum(1 for r in rows
                                                          if r[13].startswith('**TRUE')
                                                          and r[14] != '—'))),
     ('direction from traj', str(sum(1 for r in rows if r[12] == 'traj'))),
     ('direction from the #7 fallback', str(sum(1 for r in rows if r[12] != 'traj')))])
print('\n- a TRUE row\'s trade is NOT scored. Its close rule does not exist - spec open #4, the same')
print('  question branch 1 has been parked on. The signal bar is reported so it can be charted.')
print('- "the reversal it truncated to" is the sample where the run broke. "tail min" is what the')
print('  tail actually spanned after that truncation and any deferral.')
