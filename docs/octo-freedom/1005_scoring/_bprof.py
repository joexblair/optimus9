"""THE B-TRADE MAE/MFE PROFILE, AND JOE'S >80% REVERSAL PREMISE. 1009.

Joe 1009: *"the current code let's an incoming trade continue on its path, but when I look at ws12r
oob events against pxs, >80% of them reverse pxs - the very opposite of the current code"* / *"how
do we know that this isn't just an exit issue? we can find out: let's see the MAE MFE profile per
row, for individual B trades that fired on the worse 5 day span"* / *"MAE MFE profile: how high
does MFE climb before it is stopped by MAE"*.

PART 1  the premise, measured: at every ws12r oob crossing, which way does pxs go.
PART 2  the worst contiguous 5-DAY span by net, found not chosen.
PART 3  every B trade inside it, with MFE-BEFORE-MAE - the best the trade reached BEFORE its
        adverse extreme - beside the MAE that ended it.
"""
import os, sys, importlib, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1005_scoring')
os.environ['W_DGATE'] = 'vote'; os.environ['W_VOTE_TIE'] = 'c3'
for m in ('_chain10', '_trajmech', '_chain_2day'):
    sys.modules.pop(m, None)
import _chain10 as C, _chain_2day as T
SC, box, U, PX = C.SC, C.box, C.SC.U, C.PX
N = len(SC.ts); TF = C.TRIG_TF
R12 = np.asarray(C.R[TF], float)[:N]
DAY = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                datetime.timezone.utc).strftime('%Y-%m-%d')
px = np.asarray(PX[:N], float)

print('# PART 1 — THE PREMISE. at every ws%dr oob crossing, which way does pxs go' % TF, flush=True)
rows = []
for d, nm in ((+1, 'HIGH oob'), (-1, 'LOW oob')):
    ob = ((R12 >= C.G_HI) if d > 0 else (R12 <= C.G_LO)) & np.isfinite(R12)
    cr = np.flatnonzero(ob & ~np.r_[False, ob[:-1]])
    en = np.flatnonzero(ob & ~np.r_[ob[1:], False])
    endof = {}
    for a, b in zip(np.flatnonzero(ob & ~np.r_[False, ob[:-1]]), en): endof[int(a)] = int(b)
    for w in (5, 10, 20, 40, 60):
        nb = int(round(w * 60 / 5.0)); rev = con = fl = 0
        for a in cr:
            j = min(N - 1, int(a) + nb)
            p0, p1 = float(px[a]), float(px[j])
            if not (np.isfinite(p0) and np.isfinite(p1) and p0 > 0): continue
            ch = (p1 - p0) / p0 * 100.0
            # the oob side points one way; a REVERSAL is pxs moving AGAINST it
            s = 1 if d > 0 else -1
            if ch * s > 0: con += 1
            elif ch * s < 0: rev += 1
            else: fl += 1
        tt = rev + con + fl
        rows.append((nm, '%d min' % w, str(tt), str(rev), '%.1f%%' % (100.0 * rev / tt),
                     str(con), '%.1f%%' % (100.0 * con / tt), str(fl)))
    # and to the END of the oob run
    rev = con = fl = 0
    for a in cr:
        b = endof.get(int(a))
        if b is None: continue
        p0, p1 = float(px[a]), float(px[b])
        if not (np.isfinite(p0) and np.isfinite(p1) and p0 > 0): continue
        ch = (p1 - p0) / p0 * 100.0; s = 1 if d > 0 else -1
        if ch * s > 0: con += 1
        elif ch * s < 0: rev += 1
        else: fl += 1
    tt = rev + con + fl
    rows.append((nm, 'to the oob run end', str(tt), str(rev), '%.1f%%' % (100.0 * rev / tt),
                 str(con), '%.1f%%' % (100.0 * con / tt), str(fl)))
box(('the oob side', 'measured over', 'events', 'pxs REVERSED (against the oob side)', '% reversed',
     'pxs CONTINUED', '% continued', 'flat'), rows)
print('- a REVERSAL is pxs moving AGAINST the oob side: HIGH oob and pxs falls, or LOW oob and pxs')
print('  rises. Measured from the crossing bar, no trade involved.', flush=True)

# ---- the chain
_i = np.arange(N); fin = np.isfinite(T.X1) & np.isfinite(T.R1)
def holds(m, w):
    run = (_i + 1) - np.maximum.accumulate(np.where(m, 0, _i + 1))
    h = run >= w; cf = h & ~np.r_[False, h[:-1]]
    return [(int(c) - (w - 1), int(c)) for c in np.flatnonzero(cf) if int(c) - (w - 1) >= 1]
T.XWOB = 18
T.RETURNS = sorted([(a, b, +1) for a, b in holds((T.X1 >= T.R1) & fin, 18)]
                   + [(a, b, -1) for a, b in holds((T.X1 <= T.R1) & fin, 18)], key=lambda z: z[1])
BFLIPSUF = ('exhaustion', 'reversal on stalled', 'reversal on x-cross', 'squashed x-cross')
legs = []
k, d, g = 1, +1, 0
while True:
    g += 1
    if g > 20000: break
    xk, why, mae, cb, hand, tr = C.run_leg(k, d)
    if xk is None: break
    p0 = float(px[k]); s = 1 if d > 0 else -1
    legs.append(dict(k=k, xk=xk, d=d, why=why, real=(float(px[xk]) - p0) / p0 * 100.0 * s,
                     isB=False))
    if any(why.endswith(z) for z in BFLIPSUF):
        legs[-1]['opensB'] = True
    if why == 'mae breach':
        rb, cf, sd = T.find_reentry(xk, T.gate_A, N - 1)
        if cf is None: break
        k, d = cf, sd; continue
    if xk >= N - 1: break
    k = xk; d = -d
for i, L in enumerate(legs):
    if i and legs[i - 1].get('opensB') and L['k'] == legs[i - 1]['xk']:
        L['isB'] = True
print('\n# the chain: %d legs, %d of them are B-trades (opened at a flip exit)'
      % (len(legs), sum(1 for L in legs if L['isB'])), flush=True)

print('\n# PART 2 — THE WORST CONTIGUOUS 5-DAY SPAN BY NET, found not chosen')
days = sorted(set(DAY(L['k']) for L in legs))
best = None
for i in range(len(days) - 4):
    win = set(days[i:i + 5])
    sel = [L for L in legs if DAY(L['k']) in win]
    net = sum(L['real'] for L in sel) - len(sel) * 0.11
    if best is None or net < best[0]: best = (net, days[i:i + 5], sel)
net, win, sel = best
box(('the worst 5-day span', 'value'),
    [('the days', ' '.join(win)), ('legs in it', str(len(sel))),
     ('gross', '%+.4f' % sum(L['real'] for L in sel)),
     ('drag', '%.4f' % (len(sel) * 0.11)), ('NET AFTER DRAG', '%+.4f' % net),
     ('B-trades in it', str(sum(1 for L in sel if L['isB'])))])

def prof(L):
    k, xk, d = L['k'], L['xk'], L['d']
    p0 = float(px[k]); s = 1 if d > 0 else -1
    seg = px[k:xk + 1]; ok = np.isfinite(seg) & (seg > 0)
    rel = np.where(ok, (seg - p0) / p0 * 100.0 * s, np.nan)
    iw, ib = int(np.nanargmin(rel)), int(np.nanargmax(rel))
    mfe_before_mae = float(np.nanmax(rel[:iw + 1])) if iw >= 0 else 0.0
    return dict(mae=-float(rel[iw]), mfe=float(rel[ib]), maebar=k + iw, mfebar=k + ib,
                mfe_before=max(0.0, mfe_before_mae), first='MAE' if iw < ib else 'MFE')

print('\n# PART 3 — EVERY B TRADE IN THAT SPAN. "how high did MFE climb before MAE stopped it"')
rows = []
for L in sel:
    if not L['isB']: continue
    p = prof(L)
    rows.append((DAY(L['k']), U(L['k']), 'LONG' if L['d'] > 0 else 'SHORT', U(L['xk']),
                 '%.1f' % ((int(SC.ts[L['xk']]) - int(SC.ts[L['k']])) / 60000.0), L['why'],
                 '%+.4f' % L['real'], '%.4f' % p['mae'], '%.4f' % p['mfe'],
                 '%.4f' % p['mfe_before'], U(p['mfebar']), U(p['maebar']), p['first'],
                 '%.2f' % (p['mfe'] / p['mae']) if p['mae'] > 0 else 'inf'))
box(('day', 'B opens', 'side', 'B closes', 'held min', 'on what', 'realised', 'MAE', 'MFE',
     'MFE BEFORE the MAE bar', 'the MFE bar', 'the MAE bar', 'which came first', 'MFE/MAE'), rows)
if rows:
    bs = [L for L in sel if L['isB']]
    ps = [prof(L) for L in bs]
    box(('across the %d B trades in the span' % len(bs), 'value'),
        [('summed realised', '%+.4f' % sum(L['real'] for L in bs)),
         ('MAE first — the open is early', str(sum(1 for p in ps if p['first'] == 'MAE'))),
         ('MFE first — it gave back', str(sum(1 for p in ps if p['first'] == 'MFE'))),
         ('median MFE BEFORE the MAE bar', '%.4f' % float(np.median([p['mfe_before'] for p in ps]))),
         ('median MAE', '%.4f' % float(np.median([p['mae'] for p in ps]))),
         ('median MFE', '%.4f' % float(np.median([p['mfe'] for p in ps]))),
         ('B trades whose MFE-before-MAE never cleared 0.11 — one fee',
          str(sum(1 for p in ps if p['mfe_before'] < 0.11))),
         ('B trades stopped on mae breach', str(sum(1 for L in bs if L['why'] == 'mae breach')))])
