"""ARE THE STOPS RE-ENTRY OPENS? chain 0, the full 95-day window. 1008.

Joe 1008: *"defintely separate them"* / *"I suspect a lot of the stops in the full window are
re-entry - check it out pls"*.

THE KNOBS ARE NOW SEPARATE: `reent_xwob` 6 is the re-entry router's own hold, Joe's SS12 ruling.
`x_rev_xwob` 8 stays with the >ws12 divergence mech it was measured for.

EVERY LEG IS TAGGED BY HOW ITS OPEN BAR WAS CHOSEN:
  re-entry open   the leg opened on a re-entry conf bar, i.e. the first leg after a 1.10 stop.
                  Always LONG, because the router forces +1.
  alternation     the leg opened on the previous leg's EXIT bar, with the side flipped.
  seed            the one leg that opened on the tape's first bar.

Then the stop rate is reported per tag. Nothing is scored as a verdict.
"""
import os, sys, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
import _chain_2day as T

SC, PX, box = C.SC, C.PX, C.box
N = len(SC.ts); U = SC.U
MAE_STOP = C.MAE_STOP
DAYOF = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                  datetime.timezone.utc).strftime('%Y-%m-%d')
print('# reent_xwob = %d bars (%.0f s), x_rev_xwob = %d bars — separated'
      % (T.XWOB, T.XWOB * 5, int(C.W['x_rev_xwob'])), flush=True)
print('# %d ws1x returns on the whole tape at hold %d' % (len(T.RETURNS), T.XWOB), flush=True)

def chain0(gate, seed, last):
    rows = []; n = 0
    k, d, tag = seed, +1, 'seed'
    while True:
        xk, why, mae, cb, hand, tr = C.run_leg(k, d)
        if xk is None: break
        n += 1
        p0 = float(PX[k]); sgn = 1 if d > 0 else -1
        rows.append(dict(leg=n, side='LONG' if d > 0 else 'SHORT', open=k, exit=xk, tag=tag,
                         real=(float(PX[xk]) - p0) / p0 * 100.0 * sgn, why=why, d=d, hand=hand))
        if why == 'mae breach':
            rb, cf = T.find_reentry(xk, gate, last)
            if cf is None: break
            k, d, tag = cf, +1, 're-entry open'
            continue
        if xk >= last: break
        k = xk; d = -d; tag = 'alternation'
    return rows

print('# chain 0 over the whole tape ...', flush=True)
L = chain0(T.gate_A, 1, N - 1)

def mm(s_, e_, dd):
    seg = PX[s_:e_ + 1]; seg = seg[np.isfinite(seg) & (seg > 0)]
    if seg.size == 0: return 0.0, 0.0
    p_ = float(PX[s_])
    f = float(seg.max()) if dd > 0 else float(seg.min())
    g = float(seg.min()) if dd > 0 else float(seg.max())
    return (max(0.0, -((g - p_) / p_ * 100.0 * dd)), (f - p_) / p_ * 100.0 * dd)

print('\n# CHAIN 0 AT reent_xwob %d — %s TO %s' % (T.XWOB, DAYOF(L[0]['open']), DAYOF(L[-1]['exit'])))
rows = []
for tag in ('re-entry open', 'alternation', 'seed'):
    G = [r for r in L if r['tag'] == tag]
    if not G: continue
    st = [r for r in G if r['why'] == 'mae breach']
    mae = mfe = real = 0.0
    for r in G:
        a_, f_ = (MAE_STOP, 0.0) if r['why'] == 'mae breach' else mm(r['open'], r['exit'], r['d'])
        mae += a_; mfe += f_; real += r['real']
    rows.append((tag, str(len(G)), str(sum(1 for r in G if r['real'] > 0)), str(len(st)),
                 '%.1f%%' % (100.0 * len(st) / len(G)),
                 '%.4f' % mae, '%.4f' % mfe, '%.2f' % (mfe / mae) if mae else 'inf',
                 '%+.4f' % real, '%+.6f' % (real / len(G))))
G = L
st = [r for r in G if r['why'] == 'mae breach']
mae = mfe = real = 0.0
for r in G:
    a_, f_ = (MAE_STOP, 0.0) if r['why'] == 'mae breach' else mm(r['open'], r['exit'], r['d'])
    mae += a_; mfe += f_; real += r['real']
rows.append(('ALL LEGS', str(len(G)), str(sum(1 for r in G if r['real'] > 0)), str(len(st)),
             '%.1f%%' % (100.0 * len(st) / len(G)), '%.4f' % mae, '%.4f' % mfe,
             '%.2f' % (mfe / mae), '%+.4f' % real, '%+.6f' % (real / len(G))))
box(('how the open bar was chosen', 'legs', 'positive', 'stops', 'stop rate', 'MAE', 'MFE',
     'MFE/MAE', 'realised', 'realised per leg'), rows)

print('\n# OF THE %d STOPS, HOW THEY WERE OPENED' % len(st))
c = collections.Counter(r['tag'] for r in st)
box(('how the stopped leg was opened', 'stops', 'share of all stops'),
    [(t, str(c[t]), '%.1f%%' % (100.0 * c[t] / len(st))) for t in
     sorted(c, key=lambda x: -c[x])])

print('\n# THE RE-ENTRY OPENS THAT STOPPED, BY HOW FAST THEY STOPPED')
rr = sorted([r for r in st if r['tag'] == 're-entry open'],
            key=lambda r: int(SC.ts[r['exit']]) - int(SC.ts[r['open']]))
hold = [(int(SC.ts[r['exit']]) - int(SC.ts[r['open']])) / 60000.0 for r in rr]
box(('the measure', 'value'),
    [('re-entry opens that stopped', str(len(rr))),
     ('fastest stop', '%.1f min, %s %s' % (hold[0], DAYOF(rr[0]['open']), U(rr[0]['open']))),
     ('median hold to the stop', '%.1f min' % sorted(hold)[len(hold) // 2]),
     ('slowest stop', '%.1f min, %s %s' % (hold[-1], DAYOF(rr[-1]['open']), U(rr[-1]['open']))),
     ('stopped within 10 min', '%d of %d (%.1f%%)'
      % (sum(1 for h in hold if h <= 10), len(hold), 100.0 * sum(1 for h in hold if h <= 10) / len(hold)))])

print('\n# SIDE SPLIT — the router forces LONG on every re-entry open')
rows = []
for tag in ('re-entry open', 'alternation'):
    G = [r for r in L if r['tag'] == tag]
    for sd in ('LONG', 'SHORT'):
        H = [r for r in G if r['side'] == sd]
        if not H: continue
        s_ = [r for r in H if r['why'] == 'mae breach']
        rows.append((tag, sd, str(len(H)), str(len(s_)), '%.1f%%' % (100.0 * len(s_) / len(H)),
                     '%+.4f' % sum(r['real'] for r in H)))
box(('how the open bar was chosen', 'side', 'legs', 'stops', 'stop rate', 'realised'), rows)
