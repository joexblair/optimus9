"""Run the lineage walk on every 09-25 octo-sig. Reproduce 11:28:15 -> 11:48:00, then the other 38."""
import os, sys, io, contextlib
os.environ.setdefault('LG_DAY', '2026-09-25')
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC, baton as BT
import numpy as np
import lineage_walk as LW

DAY = '2026-09-25'
C = BT.compute(DAY + ' 00:00:00', DAY + ' 23:59:55', 'octosig/%s.out' % DAY, warn=False)
LAST = len(SC.ts) - 1
LIN_TF, LIN_HOP = SC.TF, int(SC.LG['lin_hop'])
rows = []
for k, sig, _l, _b2, _w, arm in sorted(C.OS):
    j = k - C.A
    d = int(C.D[j])                                  # the ON-BOOK octo-sig's dr, never re-read
    # THE WALK STARTS AT THE g5extrema, Joe 1006: *"09:28:05 is the g5extrema, literally the best
    # place to test because it shows how the market is behaving from a momentum perspective"*.
    # Same bar the routing reads - score39's `ex`, banked as os_g5ex_ts, knob lazy_g.walk_start.
    r = SC.classify(k, sig)
    anc = int(r['m']['ex']) if r['m'].get('ex') is not None else k
    w = LW.walk(SC.Rl, SC.DRv, C.ST12, C.A, C.N, anc, d, SC.HI, SC.LO, LAST, LIN_TF, LIN_HOP,
                'SHORT' if d > 0 else 'LONG')
    rows.append((sig, k, d, w, anc))

print('# THE LINEAGE WALK ON ALL %d 09-25 OCTO-SIGS   knob key %s' % (len(rows), SC.LG_KEY))
print('# walk starts at the g5extrema | side from the octo-sig, never re-read | upward only, hop <= %d' % LIN_HOP)
print('| octo-sig | g5extrema | anchor lag | dr | side | rider at anchor | baton chain | why it ended | walked ts | lag from octo-sig | holder oob |')
print('|---|---|---|---|---|---|---|---|---|')
for sig, k, d, w, anc in rows:
    ch = ' > '.join('ws%d@%s' % (t, SC.U(kk)) for kk, t in w['chain']) if w['chain'] else '—'
    wt = SC.U(w['walked_k']) if w['walked_k'] is not None else '—'
    lag = ('%.1f' % ((int(SC.ts[w['walked_k']]) - int(SC.ts[k])) / 60000.0)) if w['walked_k'] is not None else '—'
    ro = {True: 'Y', False: '-', None: '—'}[w['holder_oob_at_loss']]
    print('| %s | %s | %+.1f | %+d | %s | %s | %s | %s | %s | %s | %s |'
          % (sig, SC.U(anc), (int(SC.ts[anc]) - int(SC.ts[k])) / 60000.0, d,
             'SHORT' if d > 0 else 'LONG',
             ('ws%d' % w['rider0']) if w['rider0'] else 'NONE', ch, w['why'], wt, lag, ro))

print('\n# THE COLLAPSE - how many octo-sigs land on each walked bar')
agg = {}
for sig, k, d, w, anc in rows:
    if w['walked_k'] is None: continue
    key = (SC.U(w['walked_k']), 'SHORT' if d > 0 else 'LONG')
    agg.setdefault(key, []).append(sig)
print('| walked ts | side | octo-sigs | which |'); print('|---|---|---|---|')
for (wt, sd) in sorted(agg):
    v = agg[(wt, sd)]
    print('| %s | %s | %d | %s |' % (wt, sd, len(v), ', '.join(v)))
print('\n- %d walked rows land on %d distinct bars' % (sum(len(v) for v in agg.values()), len(agg)))

print('\n# THE COLLAPSE - how many octo-sigs land on each walked bar')
agg = {}
for sig, k, d, w, anc in rows:
    if w['walked_k'] is None: continue
    agg.setdefault((SC.U(w['walked_k']), 'SHORT' if d > 0 else 'LONG'), []).append(sig)
print('| walked ts | side | octo-sigs | which |'); print('|---|---|---|---|')
for key in sorted(agg):
    v = agg[key]
    print('| %s | %s | %d | %s |' % (key[0], key[1], len(v), ', '.join(v)))
print('\n- %d walked rows land on %d distinct bars' % (sum(len(v) for v in agg.values()), len(agg)))

print('\n# THE NO-RIDER ROWS - the full ladder at the g5extrema')
for sig, k, d, w, anc in rows:
    if w['rider0'] is not None: continue
    print('\n## octo-sig %s, g5extrema %s, dr %+d' % (sig, SC.U(anc), d))
    print('| TF | r | band | mom-true | stalled |'); print('|---|---|---|---|---|')
    ja = anc - C.A
    for t in LIN_TF:
        v = float(SC.Rl[t][anc])
        b = ('O' if v >= SC.HI else ('x' if v >= 100.0 - float(SC.LG['momo_fence_r']) else '.')) if d > 0 \
            else ('O' if v <= SC.LO else ('x' if v <= float(SC.LG['momo_fence_r']) else '.'))
        print('| ws%d | %.2f | %s | %s | %s |' % (t, v, b, 'Y' if C.MT12[t][ja] else '-',
                                                  'Y' if C.ST12[t][ja] else '-'))

print('\n# THE CONCRETIONS, COUNTED')
n = len(rows)
why = {}
for _s, _k, _d, w, _a in rows: why[w['why']] = why.get(w['why'], 0) + 1
print('| case | rows of %d |' % n); print('|---|---|')
for kk in sorted(why): print('| ended: %s | %d |' % (kk, why[kk]))
print('| no rider at the g5extrema | %d |' % sum(1 for r in rows if r[3]['rider0'] is None))
print('| g5extrema BEFORE the octo-sig (lookback) | %d |' % sum(1 for r in rows if r[4] < r[1]))
print('| g5extrema AFTER the octo-sig (fwd) | %d |' % sum(1 for r in rows if r[4] > r[1]))
print('| rider was ws1 or ws2 (needs ST12) | %d |' % sum(1 for r in rows if r[3]['rider0'] in (1, 2)))
print('| same-bar tie between rider+1 and rider+2 | %d |' % sum(r[3]['ties'] for r in rows))
print('| tag holder STILL oob when it printed stalled (fires anyway, Joe 1006) | %d |' % sum(1 for r in rows if r[3]['holder_oob_at_loss'] is True))
print('| tag holder back in-fence when it printed stalled | %d |' % sum(1 for r in rows if r[3]['holder_oob_at_loss'] is False))
w2 = [r for r in rows if r[3]['walked_k'] is not None]
print('| a walked timestamp was produced | %d |' % len(w2))
if w2:
    lags = sorted((int(SC.ts[r[3]['walked_k']]) - int(SC.ts[r[1]])) / 60000.0 for r in w2)
    print('\n| walk lag, minutes | value |'); print('|---|---|')
    print('| min | %.1f |' % lags[0]); print('| median | %.1f |' % lags[len(lags) // 2])
    print('| max | %.1f |' % lags[-1])
