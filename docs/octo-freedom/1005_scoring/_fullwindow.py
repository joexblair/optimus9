"""THE FULL WINDOW — the turn walk against the baseline across the whole tape. 1008.

Joe 1008: *"we could confluence that further by looking at ws1r's trajectory + infence. in this case
it's upward so the walk is immediately a no-op"* / *"what happened to the 15:41 signal? it was on my
stopped list and the reason I bought up the idea of walking signals for optimisation"* / *"honestly,
I'm not sure if this is a valualble mech. after 15:41 is confirmed, let's test across the full
window"*.

15:41 IS CONFIRMED: arm 8 leg 17 walks 15:41:00 -> 15:46:25, entry +0.6912, exits 16:33:10 on
`final stalled` at +1.9043, against the baseline's -1.2981 mae breach at 15:50:40. A +3.2024 swing.

THE WINDOW. "the full window" is taken as THE WHOLE CONTIGUOUS TAPE - 2026-07-02 12:00:00 to
2026-10-04 23:59:55, 1,632,960 bars at 5 s. MY READING, stated so it can be corrected: the chain
needs no octo-sig to open, it seeds once and alternates, so nothing restricts it to the 12 days that
carry sanctioned rows. The seed is the tape's first bar, side +1, matching the 2-day runs' FIRST.

FOUR ARMS, all on gate A's re-entry router:
  arm 0   the baseline. No walk.
  arm 8   the TURN walk, ent_rev_wob 4, frame dr. The best 2-day walk arm.
  arm 9   arm 8 PLUS Joe's no-op confluence.
  arm 10  the TURN walk on frame = inverse of the side, plus the confluence.

PER DAY IS THE UNIT. Joe: *"2 days is not a sample"*. Every day the chain touches is reported, and
no aggregate is presented as a verdict.
"""
import os, sys, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
import _chain_2day as T
import _nakedchain as NK

SC, PX, box = C.SC, C.PX, C.box
N = len(SC.ts); U = SC.U
MAE_STOP = C.MAE_STOP
DAYOF = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                  datetime.timezone.utc).strftime('%Y-%m-%d')
SEED = 1
LAST = N - 1
print('# tape %d bars, %s %s -> %s %s'
      % (N, DAYOF(0), U(0), DAYOF(N - 1), U(N - 1)), flush=True)

def base_chain(gate, seed, last):
    """arm 0 over an arbitrary window - T.run_chain is pinned to the 2-day one."""
    rows = []; n = 0
    k, d, seg_n = seed, +1, 0
    while True:
        xk, why, mae, cb, hand, tr = C.run_leg(k, d)
        if xk is None: break
        n += 1; seg_n += 1
        p0 = float(PX[k]); sgn = 1 if d > 0 else -1
        rows.append(dict(brk=False, leg=n, side='LONG' if d > 0 else 'SHORT', open=k, exit=xk,
                         real=(float(PX[xk]) - p0) / p0 * 100.0 * sgn, why=why, hand=hand, d=d,
                         naked=0.0, imp=0.0, walkfrom=k, land=k, frame=d, lw='no walk'))
        if why == 'mae breach':
            rb, cf = T.find_reentry(xk, gate, last)
            if cf is None:
                rows.append(dict(brk=True, a=xk, b=None)); break
            rows.append(dict(brk=True, a=xk, b=cf, rb=rb))
            k, d, seg_n = cf, +1, 0
            continue
        if xk >= last: break
        k = xk; d = -d
    return rows

print('# arm 0  — baseline, full window ...', flush=True)
A0 = base_chain(T.gate_A, SEED, LAST)
print('# arm 8  — TURN walk wob %d, frame dr ...' % NK.TURN_WOB, flush=True)
A8 = NK.run_chain_naked(T.gate_A, 'end', 'turn_dr', SEED, LAST, False)
print('# arm 9  — TURN walk wob %d, frame dr + the no-op confluence ...' % NK.TURN_WOB, flush=True)
A9 = NK.run_chain_naked(T.gate_A, 'end', 'turn_dr', SEED, LAST, True)
print('# arm 10 — TURN walk wob %d, frame = inverse of the side + the confluence ...'
      % NK.TURN_WOB, flush=True)
A10 = NK.run_chain_naked(T.gate_A, 'end', 'turn_inv', SEED, LAST, True)
ARMS = [('arm 0 — baseline, no walk', A0),
        ('arm 8 — TURN walk, frame dr', A8),
        ('arm 9 — TURN walk, frame dr + no-op confluence', A9),
        ('arm 10 — TURN walk, frame = inverse of the side + confluence', A10)]

def mm(s_, e_, dd):
    seg = PX[s_:e_ + 1]; seg = seg[np.isfinite(seg) & (seg > 0)]
    if seg.size == 0: return 0.0, 0.0
    p_ = float(PX[s_])
    f = float(seg.max()) if dd > 0 else float(seg.min())
    g = float(seg.min()) if dd > 0 else float(seg.max())
    return (max(0.0, -((g - p_) / p_ * 100.0 * dd)), (f - p_) / p_ * 100.0 * dd)

print('\n# THE FULL WINDOW, %s TO %s' % (DAYOF(SEED), DAYOF(LAST)))
rows = []
for lbl, rr in ARMS:
    L = [r for r in rr if not r['brk']]
    mae = mfe = real = 0.0
    for r in L:
        a_, f_ = (MAE_STOP, 0.0) if r['why'] == 'mae breach' else mm(r['open'], r['exit'], r['d'])
        mae += a_; mfe += f_; real += r['real']
    nk = sum(r.get('naked', 0.0) for r in L)
    im = sum(r.get('imp', 0.0) for r in L)
    noop = sum(1 for r in L if r.get('naked', 0.0) == 0.0)
    rows.append((lbl, str(len(L)), str(sum(1 for r in L if r['real'] > 0)),
                 str(sum(1 for r in L if r['why'] == 'mae breach')),
                 str(sum(1 for r in rr if r['brk'] and r.get('b'))),
                 '%.4f' % mae, '%.4f' % mfe, '%.2f' % (mfe / mae) if mae else 'inf',
                 '%+.4f' % real, '%.1f' % nk, '%+.4f' % im, str(noop)))
box(('arm', 'legs', 'positive', 'stops', 're-entries', 'running MAE', 'running MFE', 'MFE/MAE',
     'realised as scored', 'minutes naked', 'entry improvement', 'legs not moved'), rows)
print('- a stopped leg scores MAE %.4f and MFE 0.0000, Joe 1007.' % MAE_STOP)
print('- "legs not moved" counts legs whose entry bar IS their walk-start bar.')

print('\n# PER DAY — every day the chain touches')
days = sorted({DAYOF(r['open']) for lbl, rr in ARMS for r in rr if not r['brk']})
rows = []
for dd in days:
    for lbl, rr in ARMS:
        L = [r for r in rr if not r['brk'] and DAYOF(r['open']) == dd]
        if not L: continue
        mae = mfe = real = 0.0
        for r in L:
            a_, f_ = (MAE_STOP, 0.0) if r['why'] == 'mae breach' \
                else mm(r['open'], r['exit'], r['d'])
            mae += a_; mfe += f_; real += r['real']
        rows.append((dd, lbl.split('—')[0].strip(), str(len(L)),
                     str(sum(1 for r in L if r['real'] > 0)),
                     str(sum(1 for r in L if r['why'] == 'mae breach')),
                     '%.4f' % mae, '%.4f' % mfe, '%.2f' % (mfe / mae) if mae else 'inf',
                     '%+.4f' % real, '%.1f' % sum(r.get('naked', 0.0) for r in L)))
box(('day', 'arm', 'legs', 'positive', 'stops', 'MAE', 'MFE', 'MFE/MAE', 'realised',
     'minutes naked'), rows)

print('\n# THE WALK ARMS AGAINST THE BASELINE, DAY BY DAY')
b = {}
for r in A0:
    if r['brk']: continue
    b.setdefault(DAYOF(r['open']), 0.0)
    b[DAYOF(r['open'])] += r['real']
rows = []
for lbl, rr in ARMS[1:]:
    w = {}
    for r in rr:
        if r['brk']: continue
        w.setdefault(DAYOF(r['open']), 0.0)
        w[DAYOF(r['open'])] += r['real']
    win = sum(1 for dd in w if dd in b and w[dd] > b[dd])
    los = sum(1 for dd in w if dd in b and w[dd] < b[dd])
    rows.append((lbl.split('—')[0].strip(), str(len(w)), str(win), str(los),
                 '%+.4f' % (sum(w.values()) - sum(b.get(dd, 0.0) for dd in w))))
box(('arm', 'days', 'days it BEAT the baseline', 'days it LOST', 'realised vs the baseline'), rows)
