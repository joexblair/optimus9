"""THE PSEUDO-CLOSED LINE, validated against the product's own closed read. Joe 1027.

TEST 1 - IS IT THE SAME LINE? On the bars where the midnight grid actually closes, a pseudo-closed
read is phased exactly like the grid, so it must EQUAL the product's closed value there. That is
the test that says this is the same indicator and not a new one.

TEST 2 - WHAT HE ACTUALLY NEEDS, his words: *"we only need the line to reach ex-fence. the next
move we need is an ex-fence reversal, which our proven lift-off mech seems to handle well"*. So the
reads that matter are the EX-FENCE STATE and the reversals taken while ex-fence, not raw reversal
counts.

TEST 3 - the bar warmup, doubled, to show the value is justified.
"""
import os, sys, io
import numpy as np
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1027_pseudo_closed')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln, v4_knobs as K, v4_rcfg_sweep as RS, v4_fast as F, v4_closed_prev as CP
import pseudo_closed as PC
from v4_backstop_trades import prices
sys.stderr = _e

A, B = ln.K('2026-08-30 00:00:00'), ln.K('2026-09-06 23:59:55')
close, _h, _l = prices()
E = RS.load((RS.K0, RS.R0, RS.S0))
TS = np.asarray(ln.ts, np.int64)
IDX = np.arange(A, B + 1)
TFS = [13, 14, 15, 16]

print('# THE PSEUDO-CLOSED LINE vs THE PRODUCT\'S CLOSED READ, %s .. %s' % (ln.U(A), ln.U(B)))
print('# pseudo-closed: ws{T}r computed on the bar sequence ENDING AT t - t, t-T, t-2T, ...')
print('#   so the value at t is the closed value of a ws{T} grid phased to close at t.')
print('# the chain is the product\'s own: SMA(Stoch(RSI(close,%d),%d),%d), BARS %d of history.'
      % (PC.RSI_N, PC.STC_N, PC.K_N, PC.BARS))
print('# RULED_OK %s' % K.RULED_OK)
print('')
print('## TEST 1 - on the bars where the midnight grid closes, it must EQUAL the closed read')
print('')
print('| the line | grid-close bars in range | max abs diff | median abs diff | bars over 0.01 |')
print('|---|---|---|---|---|')
PS = {}
for t in TFS:
    PS[t] = PC.series(close, t, IDX)
    tf_ms = t * 60 * 1000
    day = (TS[IDX] // 86_400_000) * 86_400_000
    #   a grid bucket CLOSES at the bar whose next bar opens a new bucket
    bo = day + ((TS[IDX] - day) // tf_ms) * tf_ms
    is_close = np.r_[bo[1:] != bo[:-1], False]
    em = np.asarray(E[t], float)
    cl = CP.series(em, t * 60)[IDX]
    #   the product's closed read at the bar AFTER a bucket closes is that bucket's value
    j = np.flatnonzero(is_close)
    d = np.abs(PS[t][j] - cl[j + 1]) if len(j) else np.array([])
    fin = np.isfinite(d)
    print('| ws%dr | %d | %s | %s | %s |'
          % (t, int(fin.sum()),
             '%.6f' % np.nanmax(d[fin]) if fin.any() else '-',
             '%.6f' % np.nanmedian(d[fin]) if fin.any() else '-',
             '%d' % int((d[fin] > 0.01).sum()) if fin.any() else '-'))

print('')
print('## TEST 2 - the EX-FENCE state, which is what he said the mech needs')
print('')
print('| the line | side | bars ex-fence CLOSED | bars ex-fence PSEUDO | bars ex-fence EMERGING |'
      ' pseudo agrees with closed | emerging agrees with closed |')
print('|---|---|---|---|---|---|---|')
for t in TFS:
    em = np.asarray(E[t], float)[IDX]
    cl = CP.series(np.asarray(E[t], float), t * 60)[IDX]
    ps = PS[t]
    for sd in (-1, +1):
        fc = np.array([bool(K.ex_fence(v, sd)) for v in cl])
        fp = np.array([bool(K.ex_fence(v, sd)) for v in ps])
        fe = np.array([bool(K.ex_fence(v, sd)) for v in em])
        n = len(IDX)
        print('| ws%dr | %s | %d | %d | %d | %.1f%% | %.1f%% |'
              % (t, 'LOW' if sd < 0 else 'HIGH', fc.sum(), fp.sum(), fe.sum(),
                 100.0 * (fp == fc).mean(), 100.0 * (fe == fc).mean()))

print('')
print('## TEST 3 - the bar warmup doubled, %d -> %d' % (PC.BARS, PC.BARS * 2))
print('')
print('| the line | max abs change | share of bars that move |')
print('|---|---|---|')
for t in TFS:
    mx, fr = PC.converged(close, t, IDX)
    print('| ws%dr | %.2e | %.4f%% |' % (t, mx, fr * 100.0))
