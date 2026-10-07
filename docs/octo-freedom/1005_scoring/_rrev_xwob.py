"""ws1r / ws2r REVERSALS, THE DIVERGENCE AT EACH, AND THE xwob ON THE x-CROSS. Leg 8, 09-25. 1007.

JOE 1007:
  *"I'm targetting the ws2r divergence at ~09:32"*
  *"let's drop ws1mage-rev and replace it with ws1r-reversing for the ws1 divergence test, and
    ws2r-reversing for its divergence test"*
  *"what I see consitently is a ws{tf being tested}x crossing under (for +dr) its r at the time
    that r is reversing (which makes sense - BBs lead Ks)"*
  *"what xwob would we need to correclty pick the x-cross that pushes r into a reversal?"*

PRODUCERS, both existing:
  lr_v2._mage_rev(line, wob_n)   boundary-agnostic reversal. `s_qualify_parts` fixes the sign:
                                 a reversal AT THE HI SIDE is `== -1` (the line turned down), so a
                                 +dr r-reversal is -1. REV_WOB 2 steps is the banked value for the
                                 Mage reversal; r's own reversal wob is a SEPARATE knob Joe has not
                                 named, so 2 is carried over and said out loud.
  jig.anchor_floater             the divergence, 4 steps, the 50 filter baked in step 3.

THE x-CROSS WITH A wob, following oob_ib_cross's own convention: the cross bar is the FIRST bar of
a run where x < r (for +dr) that HOLDS xwob consecutive bars; `conf` = cross + xwob - 1 is the bar
it becomes knowable. Causal either way - the wob delays knowledge, it does not read forward.

THE PAIRING, cap-free: each reversal is paired with the LAST cross at or before it. A reversal with
no cross since the previous reversal is UNMATCHED. A cross with no reversal before the next cross is
SPURIOUS. No window, no horizon - the lag distribution is reported as it falls out.
"""
import os, io, contextlib, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.analysis.lr_v2 import _mage_rev
from optimus9.analysis.jig import anchor_floater
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC

D = os.environ.get('W_DAY', '2026-09-25')
OPEN_TS = os.environ.get('W_OPEN', '08:10:00')
END_TS = os.environ.get('W_END', '10:25:00')
DD = int(os.environ.get('W_DR', '1'))
REV_WOB = int(os.environ.get('REV_WOB', '2'))
XWOBS = [1, 2, 3, 4, 6, 8, 12, 18, 24]
TFS = [1, 2]
N = len(SC.ts)
K = lambda t: SC.K('%s %s' % (D, t))
R = {t: SC.LD(t * 60, 'r')[:N] for t in TFS}
X = {t: SC.LD(t * 60, 'x')[:N] for t in TFS}
PX = SC.PX[:N]
k0, k1 = K(OPEN_TS), K(END_TS)
p0 = float(PX[k0])
pct = lambda k: (float(PX[k]) - p0) / p0 * 100.0 * (1 if DD > 0 else -1)
mn = lambda k: (int(SC.ts[k]) - int(SC.ts[k0])) / 60000.0
WANT = -1 if DD > 0 else +1          # the dr-side reversal sign, per s_qualify_parts

def box(hdr, rr):
    w = [max(len(hdr[i]), max((len(str(x[i])) for x in rr), default=0)) for i in range(len(hdr))]
    B = lambda s, m, e: s + m.join('─' * (x + 2) for x in w) + e
    print(B('┌', '┬', '┐'))
    print('│' + '│'.join(' ' + hdr[i].center(w[i]) + ' ' for i in range(len(hdr))) + '│')
    print(B('├', '┼', '┤'))
    for x in rr:
        print('│' + '│'.join(' ' + str(x[i]).ljust(w[i]) + ' ' for i in range(len(hdr))) + '│')
    print(B('└', '┴', '┘'))
md = lambda v: (sorted(v)[len(v) // 2] if v else float('nan'))

REV = {t: _mage_rev(R[t], REV_WOB) for t in TFS}
revbars = {t: [k for k in range(k0, k1 + 1) if REV[t][k] == WANT] for t in TFS}

def crosses(t, xwob):
    """-> [(cross_bar, conf_bar)] where x < r (for +dr) holds xwob consecutive bars."""
    v = (X[t] < R[t]) if DD > 0 else (X[t] > R[t])
    v = v & np.isfinite(X[t]) & np.isfinite(R[t])
    idx = np.arange(N)
    run = (idx + 1) - np.maximum.accumulate(np.where(v, 0, idx + 1))
    held = run >= max(1, xwob)
    conf = held & ~np.r_[False, held[:-1]]
    out = []
    for c in np.flatnonzero(conf):
        k = c - (xwob - 1)
        if k >= 1 and k0 <= k <= k1:
            out.append((int(k), int(c)))
    return out

print('# LEG 8 — open %s, window to %s, leg d %+d, pxs %.6f' % (OPEN_TS, END_TS, DD, p0))
print('- r reversal: _mage_rev(r, %d) == %+d. The pivot sits at 09:28:25, pct %+.4f.'
      % (REV_WOB, WANT, pct(K('09:28:25'))))

for t in TFS:
    print('\n# ws%dr REVERSALS IN THE WINDOW, WITH THE DIVERGENCE AT EACH' % t)
    rows = []
    for k in revbars[t]:
        af = anchor_floater(R[t], PX, DD, k)
        rows.append((SC.U(k), '%+.1f' % mn(k),
                     '%+.1f' % ((int(SC.ts[k]) - int(SC.ts[K('09:28:25')])) / 60000.0),
                     '%.2f' % float(R[t][k]), '%.2f' % float(X[t][k]),
                     'Y' if float(X[t][k]) < float(R[t][k]) else '-',
                     ('refused' if af is None else '%+d' % int(af['fired'])),
                     ('—' if af is None else SC.U(af['floater'][0])),
                     ('—' if af is None else '%+.2f' % af['d_osc']),
                     'DIVERGENCE' if (af and int(af['fired']) != 0) else '-',
                     '%+.4f' % pct(k)))
    box(('ts', '+min from open', 'min from pivot', 'ws%dr' % t, 'ws%dx' % t, 'x under r',
         'fired', 'floater', 'd_osc', 'verdict', 'pct'), rows or [('—',) * 11])
    fired = [k for k in revbars[t] if (lambda a: a and int(a['fired']) != 0)(
        anchor_floater(R[t], PX, DD, k))]
    if fired:
        print('- first ws%dr reversal carrying a divergence: %s (%+.1f min from the pivot), '
              'pct %+.4f' % (t, SC.U(fired[0]),
                             (int(SC.ts[fired[0]]) - int(SC.ts[K('09:28:25')])) / 60000.0,
                             pct(fired[0])))
    else:
        print('- NO ws%dr reversal in the window carries a divergence.' % t)

for t in TFS:
    print('\n# ws%d — THE xwob SWEEP: does the x-cross pick the reversal?' % t)
    rv = revbars[t]
    rows = []
    for xw in XWOBS:
        cx = crosses(t, xw)
        cb = [c for c, _ in cx]
        lags = []; unmatched = 0; prev = k0 - 1
        for r_ in rv:
            cand = [c for c in cb if prev < c <= r_]
            if cand:
                lags.append((int(SC.ts[r_]) - int(SC.ts[cand[-1]])) / 60000.0)
            else:
                unmatched += 1
            prev = r_
        spur = 0
        for i, c in enumerate(cb):
            nxt = cb[i + 1] if i + 1 < len(cb) else k1 + 1
            if not any(c <= r_ < nxt for r_ in rv):
                spur += 1
        rows.append((str(xw), '%d' % (xw * 5), str(len(cb)), str(len(rv)),
                     '%.2f' % (len(cb) / len(rv)) if rv else '—',
                     str(len(rv) - unmatched), str(unmatched), str(spur),
                     '%+.2f' % md(lags) if lags else '—',
                     '%+.2f' % (sum(lags) / len(lags)) if lags else '—',
                     '%+.2f' % max(lags) if lags else '—'))
    box(('xwob bars', 'seconds', 'crosses', 'reversals', 'crosses per reversal', 'matched',
         'unmatched', 'spurious', 'lag med min', 'lag mean min', 'lag max min'), rows)

print('\n- REV_WOB %d steps is carried over from the Mage reversal knob. r has no ruled value.'
      % REV_WOB)
print('- window %s to %s = %d bars; ws1r reversals %d, ws2r reversals %d'
      % (OPEN_TS, END_TS, k1 - k0 + 1, len(revbars[1]), len(revbars[2])))
