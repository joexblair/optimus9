"""THE 5 TIES C3 MADE WORSE, AS TIMESTAMP WALKS. 1009.

Joe 1009: *"I need the timestamps, from trade open to A/B-trade routing to exit"*.

Both arms are identical up to the routing bar - the tie-break is the only thing that differs and it
is only read at the dwell-ending - so each tie prints ONE walk: the shared prefix, the routing row,
then the two branches underneath it. The prefix identity is ASSERTED, not assumed.
"""
import os, sys, importlib, textwrap
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1005_scoring')
TIES = [('2026-07-07 01:34:00', +1), ('2026-07-14 01:38:15', +1), ('2026-08-01 21:59:00', -1),
        ('2026-09-05 09:05:35', -1), ('2026-09-08 00:39:00', +1)]
BFLIPSUF = ('exhaustion', 'reversal on stalled', 'reversal on x-cross', 'squashed x-cross')
EW = 46
W = [8, 7, EW, 8, 9, 9, 9, 9]
def wrapbox(hdr, rows):
    line = lambda l, m, r: l + m.join('-' * (x + 2) for x in W) + r
    put = lambda cs: '| ' + ' | '.join(str(c).ljust(x) for c, x in zip(cs, W)) + ' |'
    print(line('+', '+', '+')); print(put([h.center(x) for h, x in zip(hdr, W)]))
    print(line('+', '+', '+'))
    for r in rows:
        if r is None: print(line('+', '+', '+')); continue
        parts = textwrap.wrap(str(r[2]), EW) or ['']
        for i, p in enumerate(parts):
            print(put([(r[c] if i == 0 else '') if c != 2 else p for c in range(len(W))]))
    print(line('+', '+', '+'))

def load(tie):
    os.environ['W_DGATE'] = 'vote'; os.environ['W_VOTE_TIE'] = tie
    os.environ.pop('W_TRACE_DGATE', None); os.environ.pop('W_TRACE_NOX', None)
    for m in ('_chain10', '_trajmech', '_chain_2day'):
        sys.modules.pop(m, None)
    return importlib.import_module('_chain10')

def walk(C, k, d):
    xk, why, mae, cb, hand, tr = C.run_leg(k, d)
    out = dict(k=k, d=d, xk=xk, why=why, tr=list(tr), b=None)
    if xk is not None and any(why.endswith(z) for z in BFLIPSUF):
        bb = C.run_leg(xk, -d)
        if bb[0] is not None: out['b'] = bb
    return out

def mkrows(C, w, routing_bar):
    """-> (prefix rows up to and including routing_bar, branch rows after it)"""
    SC, PX, U = C.SC, C.PX, C.SC.U
    k, d, xk = w['k'], w['d'], w['xk']
    p0 = float(PX[k]); s = 1 if d > 0 else -1
    seg = np.asarray(PX[k:xk + 1], float); ok = np.isfinite(seg) & (seg > 0)
    rel = np.where(ok, (seg - p0) / p0 * 100.0 * s, np.nan)
    lo = np.minimum.accumulate(np.where(np.isnan(rel), np.inf, rel))
    hi = np.maximum.accumulate(np.where(np.isnan(rel), -np.inf, rel))
    iw, ib = int(np.nanargmin(rel)), int(np.nanargmax(rel))
    pa = lambda j: '%+.4f' % ((float(PX[j]) - p0) / p0 * 100.0 * s)
    mn = lambda j: '%+.1f' % ((int(SC.ts[j]) - int(SC.ts[k])) / 60000.0)
    am = lambda j: '%.4f' % max(0.0, -float(lo[j - k])); af = lambda j: '%.4f' % max(0.0, float(hi[j - k]))
    ev = [(j, t) for j, t in w['tr']] + [(k + iw, "A's MAE bar, %.4f" % -float(rel[iw])),
                                         (k + ib, "A's MFE bar, %.4f" % float(rel[ib]))]
    R = [(U(k), '+0.0', 'A OPENS %s' % ('LONG' if d > 0 else 'SHORT'), '%.6f' % p0, '+0.0000',
          '', '0.0000', '0.0000')]
    for j, t in sorted(ev):
        R.append((U(j), mn(j), t, '%.6f' % float(PX[j]), pa(j), '', am(j), af(j)))
    R.append((U(xk), mn(xk), 'A CLOSES on %s — realised %s' % (w['why'], pa(xk)),
              '%.6f' % float(PX[xk]), pa(xk), '', am(xk), af(xk)))
    if w['b'] is not None:
        bxk, bwhy = w['b'][0], w['b'][1]
        q0 = float(PX[xk]); bs = -s
        bseg = np.asarray(PX[xk:bxk + 1], float); bok = np.isfinite(bseg) & (bseg > 0)
        brel = np.where(bok, (bseg - q0) / q0 * 100.0 * bs, np.nan)
        blo = np.minimum.accumulate(np.where(np.isnan(brel), np.inf, brel))
        bhi = np.maximum.accumulate(np.where(np.isnan(brel), -np.inf, brel))
        pb = lambda j: '%+.4f' % ((float(PX[j]) - q0) / q0 * 100.0 * bs)
        bm = lambda j: '%.4f' % max(0.0, -float(blo[j - xk])); bf = lambda j: '%.4f' % max(0.0, float(bhi[j - xk]))
        R.append((U(xk), mn(xk), 'B OPENS %s at A\'s close bar' % ('LONG' if bs > 0 else 'SHORT'),
                  '%.6f' % q0, '', '+0.0000', '0.0000', '0.0000'))
        for j, t in sorted(w['b'][5]):
            if j <= xk or j > bxk: continue
            R.append((U(j), mn(j), 'B: %s' % t, '%.6f' % float(PX[j]), '', pb(j), bm(j), bf(j)))
        R.append((U(bxk), mn(bxk), 'B CLOSES on %s — realised %s' % (bwhy, pb(bxk)),
                  '%.6f' % float(PX[bxk]), '', pb(bxk), bm(bxk), bf(bxk)))
    pre = [r for r in R if r[0] <= C.SC.U(routing_bar)]
    post = [r for r in R if r[0] > C.SC.U(routing_bar)]
    return pre, post, R

CT = load('c3'); SCc, Uc = CT.SC, CT.SC.U
ROUT = {}
for ts, d in TIES:
    k = SCc.K(ts); w = walk(CT, k, d)
    rb = None
    for j, t in w['tr']:
        if t.startswith('HANDOVER') or t.startswith('DELEGATION REFUSED'): rb = j
    ROUT[(ts, d)] = (rb, w)
WC = {kk: v[1] for kk, v in ROUT.items()}
CV = load('travel')
WT = {}
for ts, d in TIES:
    WT[(ts, d)] = walk(CV, CV.SC.K(ts), d)

for n, (ts, d) in enumerate(TIES, 1):
    rb, wc = ROUT[(ts, d)]
    wt = WT[(ts, d)]
    _, _, allc = mkrows(CT, wc, rb)
    _, _, allt = mkrows(CV, wt, rb)
    # THE FIRST ROW THAT DIFFERS, not the routing bar. The assert that used to sit here fired on
    # 07-07 01:34:00: a leg can hold MORE THAN ONE gate decision, so the arms can already have
    # split at an earlier tie in the same leg. Found, not assumed.
    sp = 0
    while sp < min(len(allc), len(allt)) and allc[sp][:3] == allt[sp][:3]:
        sp += 1
    prec = allc[:sp]; postc = allc[sp:]; postt = allt[sp:]
    ndec = sum(1 for j, t in wc['tr']
               if t.startswith('HANDOVER') or t.startswith('DELEGATION REFUSED'))
    print('\n\n########## TIE %d — A opens %s %s   |   the last routing bar is %s   |   %d gate '
          'decision(s) in this leg   |   the arms split at row %d'
          % (n, ts, 'LONG' if d > 0 else 'SHORT', Uc(rb), ndec, sp + 1))
    rows = prec + [None] \
        + [('', '', '>>> BRANCH A: tie-break TRAVEL', '', '', '', '', '')] + postt + [None] \
        + [('', '', '>>> BRANCH B: tie-break C3', '', '', '', '', '')] + postc
    wrapbox(('ts', '+min', 'event', 'pxs', 'pct A', 'pct B', 'MAE sf', 'MFE sf'), rows)
