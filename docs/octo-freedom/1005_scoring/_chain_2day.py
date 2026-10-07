"""THE CHAIN CONTINUED TO THE END OF 09-26, BOTH RE-ENTRY OPTIONS. 1007.

Joe 1007: *"I say we continue the chain to the end of 09-26 and review"* / *"is 1.1 too large? only
more numbers will confirm"*.

Same build as _reentry_ab.py, extended across both days. The tape is CONTIGUOUS at 5 s, so nothing
bounds a leg at midnight - a leg opened on 09-25 may exit on 09-26.

  OPTION A   ws1r <= momo_fence_r 17 at the RETURN bar, AND ws12Mage > ws1Mage at conf.
  OPTION B   every Mage ws1..ws12 > 50 at conf. No ws1r fence.

NO NEW LEG OPENS after 09-26 23:59:55; a leg already running exits naturally and its exit bar is
printed even if it falls past that. Stated because it is the only horizon in the run.

THE STOP OVERSHOOT is reported per stop, because Joe asked whether 1.1 is too large and the stop
bounds the TRIGGER, not the FILL: the exit is the first bar past 1.1, at whatever that bar's price
is.

Legs are attributed to the day of their OPEN bar - Joe's "day is the block unit".
"""
import os, sys, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C

SC, PX, box, MAE_STOP = C.SC, C.PX, C.box, C.MAE_STOP
R1, X1 = C.R[1], C.X[1]
N = len(SC.ts)
MG = {t: SC.Mg[t][:N] for t in SC.TF}
EXF_LO = float(SC.LG['momo_fence_r'])
XWOB = int(C.W['x_rev_xwob'])
K = lambda d, t: SC.K('%s %s' % (d, t))
START_D, END_D = '2026-09-25', '2026-09-26'
LAST_OPEN = K(END_D, '23:59:55')
DAYOF = lambda k: datetime.datetime.utcfromtimestamp(int(SC.ts[k]) / 1000).strftime('%Y-%m-%d')

below = (X1 < R1) & np.isfinite(X1) & np.isfinite(R1)
idx = np.arange(N)
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
        if cf > LAST_OPEN: return None, None
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

def run_chain(gate):
    rows = []; n = 0
    k, d, seg_n = K(START_D, '02:48:50'), +1, 0
    while True:
        xk, why, mae, cb, hand, tr = C.run_leg(k, d)
        if xk is None: break
        n += 1; seg_n += 1
        p0 = float(PX[k]); sgn = 1 if d > 0 else -1
        rows.append(dict(brk=False, leg=n, side='LONG' if d > 0 else 'SHORT', open=k, exit=xk,
                         real=(float(PX[xk]) - p0) / p0 * 100.0 * sgn, why=why, hand=hand, d=d,
                         mae_meas=mae, tr=(tr if why == 'mae breach' else None)))
        if why == 'mae breach' or (seg_n == 7 and n == 7):
            rb, cf = find_reentry(xk, gate)
            if cf is None:
                rows.append(dict(brk=True, a=xk, b=None)); break
            rows.append(dict(brk=True, a=xk, b=cf, rb=rb))
            k, d, seg_n = cf, +1, 0
            continue
        if xk >= LAST_OPEN: break
        k = xk; d = -d
    return rows

def tally(rows):
    rA = rF = rR = rC = 0.0
    for r in rows:
        if r['brk']: continue
        a_, f_ = (MAE_STOP, 0.0) if r['why'] == 'mae breach' else mm(r['open'], r['exit'], r['d'])
        rA += a_; rF += f_; rR += r['real']
        rC += (-MAE_STOP) if r['why'] == 'mae breach' else r['real']
    L = [r for r in rows if not r['brk']]
    return dict(legs=len(L), pos=sum(1 for r in L if r['real'] > 0), mae=rA, mfe=rF,
                real=rR, conv=rC, stops=sum(1 for r in L if r['why'] == 'mae breach'),
                reent=sum(1 for r in rows if r['brk'] and r.get('b')),
                last=L[-1]['exit'] if L else None,
                noreent=sum(1 for r in rows if r['brk'] and r.get('b') is None))

RES = {}
for lbl, g in (('OPTION A', gate_A), ('OPTION B', gate_B)):
    RES[lbl] = run_chain(g)

print('\n# BOTH OPTIONS, 09-25 02:48:50 TO THE END OF 09-26')
box(('option', 'legs', 'positive', 'stops', 're-entries', 'no re-entry', 'last exit',
     'running MAE', 'running MFE', 'MFE/MAE', 'realised as scored', 'realised at -1.10'),
    [(lbl, str(t['legs']), str(t['pos']), str(t['stops']), str(t['reent']), str(t['noreent']),
      '%s %s' % (DAYOF(t['last'])[5:], SC.U(t['last'])) if t['last'] else '—',
      '%.4f' % t['mae'], '%.4f' % t['mfe'],
      '%.2f' % (t['mfe'] / t['mae']) if t['mae'] else 'inf',
      '%+.4f' % t['real'], '%+.4f' % t['conv'])
     for lbl, rows in RES.items() for t in [tally(rows)]])

print('\n# PER DAY, BY THE LEG\'S OPEN BAR')
rows = []
for lbl, rr in RES.items():
    pd = collections.OrderedDict()
    for r in rr:
        if r['brk']: continue
        e = pd.setdefault(DAYOF(r['open']), dict(n=0, pos=0, st=0, mae=0.0, mfe=0.0, real=0.0))
        a_, f_ = (MAE_STOP, 0.0) if r['why'] == 'mae breach' else mm(r['open'], r['exit'], r['d'])
        e['n'] += 1; e['pos'] += 1 if r['real'] > 0 else 0
        e['st'] += 1 if r['why'] == 'mae breach' else 0
        e['mae'] += a_; e['mfe'] += f_; e['real'] += r['real']
    for dd, e in pd.items():
        rows.append((lbl, dd, str(e['n']), str(e['pos']), str(e['st']), '%.4f' % e['mae'],
                     '%.4f' % e['mfe'], '%.2f' % (e['mfe'] / e['mae']) if e['mae'] else 'inf',
                     '%+.4f' % e['real']))
box(('option', 'day', 'legs', 'positive', 'stops', 'MAE', 'MFE', 'MFE/MAE', 'realised'), rows)

print('\n# EVERY STOP AND ITS OVERSHOOT PAST %.2f' % MAE_STOP)
rows = []
for lbl, rr in RES.items():
    for r in rr:
        if r['brk'] or r['why'] != 'mae breach': continue
        rows.append((lbl, DAYOF(r['open'])[5:], r['side'], SC.U(r['open']), SC.U(r['exit']),
                     '%.1f' % ((int(SC.ts[r['exit']]) - int(SC.ts[r['open']])) / 60000.0),
                     '%+.4f' % r['real'], '%.4f' % (abs(r['real']) - MAE_STOP)))
box(('option', 'day', 'side', 'open', 'exit', 'hold min', 'realised', 'overshoot'), rows)
ov = [abs(r['real']) - MAE_STOP for lbl, rr in RES.items() for r in rr
      if not r['brk'] and r['why'] == 'mae breach']
print('- %d stops across both options; overshoot min %.4f, median %.4f, max %.4f'
      % (len(ov), min(ov), sorted(ov)[len(ov) // 2], max(ov)))
print('- the stop bounds the TRIGGER, not the FILL: the exit is the first bar past %.2f at that'
      % MAE_STOP)
print('  bar\'s price, so the overshoot is one bar of movement and is not bounded by the knob.')

print('\n# THE RE-ENTRIES')
rows = []
for lbl, rr in RES.items():
    for r in rr:
        if not r['brk']: continue
        rows.append((lbl, DAYOF(r['a'])[5:], SC.U(r['a']),
                     ('%s %s' % (DAYOF(r['b'])[5:], SC.U(r['b']))) if r.get('b') else 'NONE',
                     ('%.1f' % ((int(SC.ts[r['b']]) - int(SC.ts[r['a']])) / 60000.0))
                     if r.get('b') else '—',
                     SC.U(r['rb']) if r.get('b') else '—'))
box(('option', 'day of stop', 'stop bar', 're-entry conf', 'gap min', 'return bar'), rows)


# ---- the stopped trades, as timestamp-per-row event tables. Joe 1007: *"print all of the stopped
# trades. use the established timestamp-per-row event tables, print them sequentially"*.
for lbl, rr in RES.items():
    st = [r for r in rr if not r['brk'] and r['why'] == 'mae breach']
    print('\n\n' + '=' * 78)
    print('# %s — ALL %d STOPPED TRADES' % (lbl, len(st)))
    print('=' * 78)
    for r in st:
        k, xk, d = r['open'], r['exit'], r['d']
        p0 = float(PX[k]); sgn = 1 if d > 0 else -1
        pct = lambda j: '%+.4f' % ((float(PX[j]) - p0) / p0 * 100.0 * sgn)
        mn = lambda j: '%+.1f' % ((int(SC.ts[j]) - int(SC.ts[k])) / 60000.0)
        print('\n## %s %s   %s   open %s   pxs %.6f'
              % (DAYOF(k)[5:], SC.U(k), r['side'], SC.U(k), p0))
        box(('ts', '+min', 'event', 'pxs', 'pct'),
            [(SC.U(k), '+0.0', 'OPEN %s' % r['side'], '%.6f' % p0, '+0.0000')]
            + [(SC.U(j), mn(j), lab, '%.6f' % float(PX[j]), pct(j)) for j, lab in (r['tr'] or [])]
            + [(SC.U(xk), mn(xk), 'EXIT — mae breach', '%.6f' % float(PX[xk]), pct(xk))])
