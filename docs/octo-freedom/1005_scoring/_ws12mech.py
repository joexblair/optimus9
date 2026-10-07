"""JOE'S >ws12 BATON MECH, tested on a leg, with the dwell near-misses. 09-25. 1007.

JOE'S SPEC, verbatim:
  over ws12 baton mech dev
  -apply this logic after ws12r is oob for >6 minutes
  --if ws12x-crosses ws12r inside the first 6 minutes, the cross is the trade signal
  --wait for ws1Mage to "dip" over/under 50.  if +dr, then Mage will cross under 50, inverted for -dr
  ---#this is the signal that pressure is weakening
  ---start divergence testing for ws1r and ws2r, test at each ws1mage-rev
  ---if divergence is found, create an exit

JOE'S RULINGS, 1007:
  1  *"counter-dr. eg if +dr, x crosses under"*
  2  *"OR"*  -> divergence on ws1r OR ws2r
  3  *"all mage-rev tests are dr aligned: +dr requires a hi oob Mage"* -> a test bar must be in
     `rev` AND in `dwell_ok`. `ws1mage_rev`'s `rev` is direction-unfiltered by design; ruling 3
     rules it, and dwell_ok is the producer's own dr-side oob run (`g1 >= hi` at dr +1).
  4  *"mage dwell might break the >ws12 mech. report on the near misses when we don't get an exit
     near pivot"* -> STEP 5 prints EVERY `rev` bar after the dip whether or not dwell_ok passed,
     with the oob run length that dwell_ok measured, so the filter's cost is visible.

DECIDED ON PRECEDENT, overturnable: the dr is the LEG's own `d`, not the tape's per-bar dr; the
">6 minutes" is a CONSECUTIVE run of more than 72 bars at the 5 s grid; no wob on the 50 dip.

PRODUCERS: jig.anchor_floater, jig.ws1mage_rev, swing_detect.find_pivots at the banked swing.
"""
import os, io, contextlib, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.analysis.jig import anchor_floater, ws1mage_rev, WS1MR_DWELL, WS1MR_REV_WOB
from optimus9.compute.swing_detect import find_pivots
import time as _t; _T0 = _t.time()
_P = lambda m: print('# [%6.1fs] %s' % (_t.time() - _T0, m), flush=True)
_P('importing score39 ...')
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC
_P('ready')

D = os.environ.get('W_DAY', '2026-09-25')
OPEN_TS = os.environ.get('W_OPEN', '08:10:00')
DD = int(os.environ.get('W_DR', '1'))
GATE_MIN = 6.0
GATE_BARS = int(GATE_MIN * 60 / 5)
N = len(SC.ts)
K = lambda t: SC.K('%s %s' % (D, t))
R12 = SC.LD(12 * 60, 'r')[:N]; X12 = SC.LD(12 * 60, 'x')[:N]
R1 = SC.LD(60, 'r')[:N]; R2 = SC.LD(2 * 60, 'r')[:N]
G1 = SC.MTD['ws1'][:N]; PX = SC.PX[:N]
SWING = float(SC.LG['swing'])
PIV = {p: kk for p, kk in find_pivots(PX, SWING)}
_P('calling ws1mage_rev over %d bars ...' % N)
LEGS = ws1mage_rev(SC.MTD['ws1'], SC.MTD['g30'], SC.HI, SC.LO)
_P('ws1mage_rev done')
L = LEGS[DD]
REVS = set(int(x) for x in L['rev']); DWELL = set(int(x) for x in L['dwell_ok'])
oob12 = lambda k: (float(R12[k]) >= SC.HI) if DD > 0 else (float(R12[k]) <= SC.LO)
g1oob = lambda k: (float(G1[k]) >= SC.HI) if DD > 0 else (float(G1[k]) <= SC.LO)

def g1run(k):
    """ws1Mage's CONSECUTIVE dr-side oob run length in bars ending at k. What dwell_ok measures."""
    n = 0
    while k - n >= 0 and g1oob(k - n):
        n += 1
    return n

def box(hdr, rr):
    w = [max(len(hdr[i]), max((len(str(x[i])) for x in rr), default=0)) for i in range(len(hdr))]
    B = lambda s, m, e: s + m.join('─' * (x + 2) for x in w) + e
    print(B('┌', '┬', '┐'))
    print('│' + '│'.join(' ' + hdr[i].center(w[i]) + ' ' for i in range(len(hdr))) + '│')
    print(B('├', '┼', '┤'))
    for x in rr:
        print('│' + '│'.join(' ' + str(x[i]).ljust(w[i]) + ' ' for i in range(len(hdr))) + '│')
    print(B('└', '┴', '┘'))

k0 = K(OPEN_TS); p0 = float(PX[k0])
pct = lambda k: (float(PX[k]) - p0) / p0 * 100.0 * (1 if DD > 0 else -1)
mn = lambda k: (int(SC.ts[k]) - int(SC.ts[k0])) / 60000.0
print('\n# LEG OPEN %s %s, leg d %+d (%s), pxs %.6f'
      % (D, OPEN_TS, DD, 'LONG' if DD > 0 else 'SHORT', p0))

# ---- the leg's own target pivot, for "near pivot"
tgt = [p for p in sorted(PIV) if p > k0 and PIV[p] == ('H' if DD > 0 else 'L')]
pivot = tgt[0] if tgt else None
if pivot is not None:
    print('- target pivot (swing %.2f): %s, pct %+.4f, +%.1f min from the open'
          % (SWING, SC.U(pivot), pct(pivot), mn(pivot)))

# ---- STEP 1: the ws12r oob run and the >6 minute gate
runs = []; s_ = None; gate = None
for k in range(k0, N):
    if oob12(k):
        if s_ is None: s_ = k
        if gate is None and (k - s_) > GATE_BARS: gate = k
    elif s_ is not None:
        runs.append((s_, k - 1)); s_ = None
        if gate is not None: break
    if gate is not None and (k - gate) > GATE_BARS * 4: break
if s_ is not None: runs.append((s_, min(k, N - 1)))
print('\n# STEP 1 — ws12r oob runs from the open; the gate needs a run of MORE than %d bars (%.0f min)'
      % (GATE_BARS, GATE_MIN))
box(('oob from', 'to', 'run min', 'ws12r at start', 'ws12r at end', 'gate met?'),
    [(SC.U(a), SC.U(b), '%.1f' % ((int(SC.ts[b]) - int(SC.ts[a])) / 60000.0),
      '%.2f' % float(R12[a]), '%.2f' % float(R12[b]),
      'YES' if (b - a) > GATE_BARS else 'no') for a, b in runs]
    or [('—', '—', '—', '—', '—', '—')])
if gate is None:
    print('\n- ws12r never held oob past %.0f min after the open. the mech does not apply.' % GATE_MIN)
    sys.exit(0)
k_oob = next(a for a, b in runs if (b - a) > GATE_BARS)
print('- ws12r oob from %s; the gate is met at %s (+%.1f min from the open)'
      % (SC.U(k_oob), SC.U(gate), mn(gate)))

# ---- STEP 2 (branch 1): ws12x crossing ws12r counter-dr inside the first 6 minutes
print('\n# STEP 2 (branch 1) — ws12x crossing ws12r COUNTER-dr inside the first %.0f min of oob'
      % GATE_MIN)
w_end = min(N - 1, k_oob + GATE_BARS)
under = lambda k: float(X12[k]) < float(R12[k])
hit = []
for k in range(k_oob + 1, w_end + 1):
    c = (under(k) and not under(k - 1)) if DD > 0 else ((not under(k)) and under(k - 1))
    if c: hit.append(k)
box(('ts', '+min from open', 'ws12x', 'ws12r', 'direction', 'pxs', 'pct'),
    [(SC.U(k), '%+.1f' % mn(k), '%.2f' % float(X12[k]), '%.2f' % float(R12[k]),
      'x under r' if DD > 0 else 'x over r', '%.6f' % float(PX[k]), '%+.4f' % pct(k))
     for k in hit] or [('—', '—', '—', '—', 'no counter-dr cross in the window', '—', '—')])

# ---- STEP 3 (branch 2): the 50 dip
print('\n# STEP 3 (branch 2) — ws1Mage dips %s 50 after the gate' % ('under' if DD > 0 else 'over'))
dip = None
for k in range(gate, N):
    a, b = float(G1[k - 1]), float(G1[k])
    if (b < 50.0 <= a) if DD > 0 else (b > 50.0 >= a):
        dip = k; break
if dip is None:
    print('- ws1Mage never dipped across 50 after the gate. no exit from branch 2.')
    sys.exit(0)
print('- ws1Mage dip at %s (+%.1f min from the open): %.2f -> %.2f, pxs %.6f, pct %+.4f'
      % (SC.U(dip), mn(dip), float(G1[dip - 1]), float(G1[dip]), float(PX[dip]), pct(dip)))

# ---- STEP 4 + 5: every rev bar after the dip, dwell-qualified or not
SCAN = min(N - 1, dip + int(8 * 3600 / 5))      # 8 h of bars; stated, not a mech cap
rows = []; exit_k = None; exit_why = None; first_pass = None
for k in range(dip, SCAN + 1):
    if k not in REVS: continue
    ok = k in DWELL
    a1 = anchor_floater(R1, PX, DD, k)
    a2 = anchor_floater(R2, PX, DD, k)
    f1 = int(a1['fired']) if a1 else None
    f2 = int(a2['fired']) if a2 else None
    fired = (f1 not in (None, 0)) or (f2 not in (None, 0))
    rows.append(dict(k=k, ok=ok, run=g1run(k), g1=float(G1[k]), f1=f1, f2=f2, fired=fired,
                     a1=a1, a2=a2))
    if ok and fired and exit_k is None:
        exit_k, exit_why = k, ('ws1r' if f1 not in (None, 0) else 'ws2r')
    if first_pass is None and fired:
        first_pass = k
    if exit_k is not None and k > exit_k:
        break

print('\n# STEP 4 — THE dr-ALIGNED TESTS (rev AND dwell_ok), WHICH IS THE MECH AS RULED')
q = [r for r in rows if r['ok']]
box(('ts', '+min', 'min from pivot', 'ws1Mage', 'oob run bars', 'ws1r', 'ws1r fired',
     'ws2r', 'ws2r fired', 'verdict', 'pct'),
    [(SC.U(r['k']), '%+.1f' % mn(r['k']),
      ('%+.1f' % ((int(SC.ts[r['k']]) - int(SC.ts[pivot])) / 60000.0)) if pivot else '—',
      '%.2f' % r['g1'], str(r['run']), '%.2f' % float(R1[r['k']]),
      ('refused' if r['a1'] is None else '%+d' % r['f1']), '%.2f' % float(R2[r['k']]),
      ('refused' if r['a2'] is None else '%+d' % r['f2']),
      'EXIT' if r['fired'] else '-', '%+.4f' % pct(r['k'])) for r in q]
    or [('—',) * 11])

print('\n# STEP 5 — THE NEAR MISSES: every `rev` bar the dwell filter REJECTED')
nm = [r for r in rows if not r['ok']]
box(('ts', '+min', 'min from pivot', 'ws1Mage', 'dr-side oob?', 'oob run bars',
     'dwell needs', 'ws1r fired', 'ws2r fired', 'would have EXITED', 'pct'),
    [(SC.U(r['k']), '%+.1f' % mn(r['k']),
      ('%+.1f' % ((int(SC.ts[r['k']]) - int(SC.ts[pivot])) / 60000.0)) if pivot else '—',
      '%.2f' % r['g1'], 'Y' if g1oob(r['k']) else 'no', str(r['run']), str(WS1MR_DWELL),
      ('refused' if r['a1'] is None else '%+d' % r['f1']),
      ('refused' if r['a2'] is None else '%+d' % r['f2']),
      'YES' if r['fired'] else '-', '%+.4f' % pct(r['k'])) for r in nm]
    or [('—',) * 11])

print('\n# THE VERDICT ON THIS LEG')
rr = [('target pivot', SC.U(pivot) if pivot else '—',
       '%+.4f' % pct(pivot) if pivot else '—', '—')]
if exit_k is not None:
    rr.append(('mech exit (dr-aligned)', SC.U(exit_k), '%+.4f' % pct(exit_k),
               ('%+.1f min from pivot' % ((int(SC.ts[exit_k]) - int(SC.ts[pivot])) / 60000.0))
               if pivot else '—'))
else:
    rr.append(('mech exit (dr-aligned)', 'NONE', '—', '—'))
if first_pass is not None:
    rr.append(('earliest divergence of ANY rev bar', SC.U(first_pass), '%+.4f' % pct(first_pass),
               ('%+.1f min from pivot' % ((int(SC.ts[first_pass]) - int(SC.ts[pivot])) / 60000.0))
               if pivot else '—'))
box(('what', 'ts', 'pct', 'distance'), rr)
print('\n- rev bars scanned after the dip: %d; dwell-qualified %d; rejected by dwell %d'
      % (len(rows), len(q), len(nm)))
print('- ws1mage_rev knobs: dwell %d bars (%d s), rev_wob %d steps, sig line gcws30Mage'
      % (WS1MR_DWELL, WS1MR_DWELL * 5, WS1MR_REV_WOB))
print('- scan horizon after the dip: %d bars = %.1f h. STATED, not a mech rule.'
      % (SCAN - dip, (SCAN - dip) * 5 / 3600.0))
