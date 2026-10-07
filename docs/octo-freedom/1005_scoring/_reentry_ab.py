"""THE RE-ENTRY A/B — the cascade mech against "all Mages above 50". 09-25. 1007.

Joe 1007: *"there is another perspective: what happens if I'm wrong about the mech and we only
require all Mages to be above 50? 08:11 still climbed - in fact there's 2% of gain between 08:11
and 08:46. the only way to find the answer is to walk forward after an mae1.1 and A/B the 2
options"*.

BOTH OPTIONS SHARE THE CROSS, which is Joe's: ws1x pierces below ws1r (no wob - a thin spike is
allowed) then returns above it and HOLDS `x_rev_xwob` bars. The decision is taken at `conf` =
return + xwob - 1, the first bar the return is knowable.

  OPTION A   the cascade mech.  ws1r <= momo_fence_r 17 at the RETURN bar, AND ws12Mage > ws1Mage
             at conf.
  OPTION B   Joe's alternative. ALL Mages ws1..ws12 > 50 at conf. No ws1r fence - he said "only
             require", so the fence comes off.

THREE CODINGS ARE MINE AND NOT RULED:
  1  A's cascade test is `ws12Mage > ws1Mage`, the simplest faithful reading of Joe's verbatim 0918
     process: *"the first thing I look at is the lowest TF's value, and the highest TF's value ...
     I can draw a mental downward line between those 2 numbers"*. It does NOT test the peak TF, the
     bump count or the r ladder. The 0918 bump gate reversed OOS and is not rebuilt.
  2  the ws1r fence is read at the RETURN bar and the Mage condition at CONF. Both are causal at
     conf; reading ws1r at conf would be a different number from the ones measured so far.
  3  LONG-only. Both of Joe's hand-picked bars are upward reads and the mirrored SHORT re-entry is
     spec open #3, unruled.

THE CHAIN: seeded 02:48:50, 7 legs (Joe called 07:51 "stopped"), then the re-entry mech owns every
reopen to the day end. No hand-fed bars.
"""
import os, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C

SC, PX, box, MAE_STOP = C.SC, C.PX, C.box, C.MAE_STOP
R1, X1 = C.R[1], C.X[1]
N = len(SC.ts)
MG = {t: SC.Mg[t][:N] for t in SC.TF}
EXF_LO = float(SC.LG['momo_fence_r'])
XWOB = int(C.W['x_rev_xwob'])
D = C.D
K = lambda t: SC.K('%s %s' % (D, t))
DAY_END = K('23:59:55')

below = (X1 < R1) & np.isfinite(X1) & np.isfinite(R1)
idx = np.arange(N)
run = (idx + 1) - np.maximum.accumulate(np.where(~below, 0, idx + 1))     # run of ABOVE-r bars
above_run = (idx + 1) - np.maximum.accumulate(np.where(below, 0, idx + 1))
held = above_run >= XWOB
CONF = held & ~np.r_[False, held[:-1]]
RETURNS = [(int(c) - (XWOB - 1), int(c)) for c in np.flatnonzero(CONF) if int(c) - (XWOB - 1) >= 1]

gate_A = lambda rb, cf: (float(R1[rb]) <= EXF_LO
                         and float(MG[SC.TF[-1]][cf]) > float(MG[1][cf]))
gate_B = lambda rb, cf: all(float(MG[t][cf]) > 50.0 for t in SC.TF)

def find_reentry(stop_bar, gate):
    for rb, cf in RETURNS:
        if cf <= stop_bar: continue
        if cf > DAY_END: return None, None
        if gate(rb, cf): return rb, cf
    return None, None

def mm(s_, e_, dd):
    seg = PX[s_:e_ + 1]
    seg = seg[np.isfinite(seg) & (seg > 0)]
    if seg.size == 0: return 0.0, 0.0
    p_ = float(PX[s_])
    f = float(seg.max()) if dd > 0 else float(seg.min())
    g = float(seg.min()) if dd > 0 else float(seg.max())
    return (max(0.0, -((g - p_) / p_ * 100.0 * dd)), (f - p_) / p_ * 100.0 * dd)

def run_chain(gate, label):
    rows = []; n = 0
    k, d, seg_n = K('02:48:50'), +1, 0
    while True:
        xk, why, mae, cb, hand, tr = C.run_leg(k, d)
        if xk is None or xk > DAY_END: break
        n += 1; seg_n += 1
        p0 = float(PX[k]); sgn = 1 if d > 0 else -1
        rows.append(dict(brk=False, leg=n, side='LONG' if d > 0 else 'SHORT', open=k, exit=xk,
                         real=(float(PX[xk]) - p0) / p0 * 100.0 * sgn, why=why, hand=hand, d=d))
        if why == 'mae breach' or (seg_n == 7 and n == 7):
            stop = xk
            rb, cf = find_reentry(stop, gate)
            if cf is None:
                rows.append(dict(brk=True, a=stop, b=None)); break
            rows.append(dict(brk=True, a=stop, b=cf, rb=rb))
            k, d, seg_n = cf, +1, 0
            continue
        k = xk; d = -d
    return rows

def report(label, rows):
    print('\n## %s' % label)
    out = []; rA = rF = rR = 0.0
    for r in rows:
        if r['brk']:
            if r['b'] is None:
                out.append(('—', 'NO RE-ENTRY', SC.U(r['a']), '—', '—',
                            'no qualifying return before the day end', '—', '—', '—',
                            '%.4f' % rA, '%.4f' % rF, '%+.4f' % rR))
                continue
            out.append(('—', 'RE-ENTRY', SC.U(r['a']), SC.U(r['b']),
                        '%.1f' % ((int(SC.ts[r['b']]) - int(SC.ts[r['a']])) / 60000.0),
                        'return %s, conf %s' % (SC.U(r['rb']), SC.U(r['b'])),
                        '—', '—', '—', '%.4f' % rA, '%.4f' % rF, '%+.4f' % rR))
            continue
        a_, f_ = (MAE_STOP, 0.0) if r['why'] == 'mae breach' else mm(r['open'], r['exit'], r['d'])
        rA += a_; rF += f_; rR += r['real']
        out.append((str(r['leg']), r['side'], SC.U(r['open']), SC.U(r['exit']),
                    '%.1f' % ((int(SC.ts[r['exit']]) - int(SC.ts[r['open']])) / 60000.0),
                    r['why'], '%.4f' % a_, '%.4f' % f_, '%+.4f' % r['real'],
                    '%.4f' % rA, '%.4f' % rF, '%+.4f' % rR))
    box(('leg', 'side', 'open', 'exit', 'hold min', 'why / detail', 'leg MAE', 'leg MFE',
         'realised', 'running MAE', 'running MFE', 'running realised'), out)
    L = [r for r in rows if not r['brk']]
    return dict(legs=len(L), pos=sum(1 for r in L if r['real'] > 0), mae=rA, mfe=rF, real=rR,
                stops=sum(1 for r in L if r['why'] == 'mae breach'),
                reent=sum(1 for r in rows if r['brk'] and r.get('b')),
                last=L[-1]['exit'] if L else None)

print('# qualifying returns on the day: %d at xwob %d' % (len(RETURNS), XWOB))
print('# option A gate: ws1r <= %.0f at the return AND ws12Mage > ws1Mage at conf' % EXF_LO)
print('# option B gate: every Mage ws1..ws%d > 50 at conf' % SC.TF[-1])
RES = {}
for lbl, g in (('OPTION A — cascade: ws1r <= 17 at the return + ws12Mage > ws1Mage',  gate_A),
               ('OPTION B — all Mages ws1..ws12 above 50', gate_B)):
    RES[lbl] = run_chain(g, lbl)
T = {lbl: report(lbl, rows) for lbl, rows in RES.items()}

print('\n# THE A/B')
box(('option', 'legs', 'positive', 'stops', 're-entries', 'last exit', 'running MAE',
     'running MFE', 'MFE/MAE', 'running realised'),
    [(lbl.split(' — ')[0], str(t['legs']), str(t['pos']), str(t['stops']), str(t['reent']),
      SC.U(t['last']) if t['last'] else '—', '%.4f' % t['mae'], '%.4f' % t['mfe'],
      '%.2f' % (t['mfe'] / t['mae']) if t['mae'] else 'inf', '%+.4f' % t['real'])
     for lbl, t in T.items()])

print('\n# WHAT EACH GATE SAYS AT THE BARS ALREADY ON THE TABLE')
box(('bar', 'ws1r at return', 'A: ws1r <= 17', 'A: ws12M > ws1M', 'A passes', 'Mages below 50',
     'B passes'),
    [(ts, '%.2f' % float(R1[K(ts)]),
      'Y' if float(R1[K(ts)]) <= EXF_LO else '-',
      'Y' if float(MG[SC.TF[-1]][K(ts)]) > float(MG[1][K(ts)]) else '-',
      'YES' if gate_A(K(ts), K(ts)) else 'no',
      ', '.join('ws%d' % t for t in SC.TF if float(MG[t][K(ts)]) <= 50.0) or 'none',
      'YES' if gate_B(K(ts), K(ts)) else 'no')
     for ts in ('08:08:05', '08:08:45', '08:11:25', '08:46:25', '08:51:00',
                '11:19:05', '11:22:05')])
