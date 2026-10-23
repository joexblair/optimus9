"""Score the deferred backstop signals with swing_detect, no exit mech. Joe 1022: *"instead of
generating an exit, use swing_detect(2%) to report maemfe"*.

TWO-STAGE, AND THE STAGES DO NOT TOUCH. The signals are generated causally by the backstop and
lineage; the scoring runs afterwards on `optimus9.compute.swing_detect.find_pivots` at 2%. Nothing
from the scoring feeds back into generation.

NO EXIT IS INVENTED. Each trade is measured from its open to the NEXT FAVOURABLE 2% pivot - a High
for a LONG, a Low for a SHORT - which is linelab.mae's own convention. A trade with no forward
pivot is measured to the end of the tape and flagged.

THE ENTRY IS TWO TIMESTAMPS. Joe 1022: *"the entry column needs to be split - the backstop's signal
timestamp, and the lineage walked open signal"*. The backstop's signal is the fire bar; the open is
the bar AFTER lineage prints EXHAUST.

PRICES. `__close__` from the tape, the RAW unsmoothed source. swing_detect is close-based by its own
docstring. MAE and MFE are taken on the same series as the pivots, so the pivot and the extreme it
bounds cannot disagree.

usage: v4_swing_score.py '2026-08-30 00:00:00' '2026-09-06 23:59:55' window 2.0
"""
import sys
import io

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
import ln
import v4_knobs as K
import v4_backstop as BS
import v4_deferred_trades as DT
from v4_backstop_trades import prices
_e = sys.stderr; sys.stderr = io.StringIO()
from optimus9.compute.swing_detect import find_pivots
sys.stderr = _e


def score(acc, close, pct):
    """Each open -> the next favourable `pct`% pivot, and the MAE/MFE to it."""
    piv = find_pivots(close, pct)
    out = []
    for r in acc:
        en = r['exh'] + 1
        d = 1 if r['dir'] == 'LONG' else -1
        fav = 'H' if d > 0 else 'L'
        nxt = next((pi for pi, pk in piv if pi > en and pk == fav), None)
        hit = nxt is not None
        seg = close[en:(nxt + 1)] if hit else close[en:]
        p0 = float(close[en])
        if len(seg) < 1 or p0 <= 0:
            continue
        dd = (np.asarray(seg, float) - p0) / p0 * 100.0 * d
        out.append({'fire': r['fire'], 'rev': r['rev'], 'en': en, 'dir': r['dir'], 'p0': p0,
                    'piv': nxt, 'hit': hit, 'bars': (nxt - en + 1) if hit else (len(close) - en),
                    'mae': float(dd.min()), 'mfe': float(dd.max())})
    return out, len(piv)


if __name__ == '__main__':
    A, B = ln.K(sys.argv[1]), ln.K(sys.argv[2])
    ow, pct = sys.argv[3], float(sys.argv[4])
    R = {t: ln.line('ws%dr' % t) for t in range(1, K.TF_CEILING + 3)}
    MG = {t: ln.line('ws%dMage' % t) for t in range(1, 13)}
    close, hi, lo = prices()
    f = BS.scan(A, B, R, MG, ln.U, 'lift', ow)
    rows = DT.defer(f, R, B)
    acc = DT.accept(rows)
    sc, npiv = score(acc, close, pct)
    print('# control ws5r 2026-09-03 00:35:00 = %.2f (DB-ruled known-good 12.48; the BANKED k6 rsi8 stc6 line reads 6.77 there)'
          % R[5][ln.K('2026-09-03 00:35:00')])
    print('# RULED_OK %s. oob_when %r. swing_detect pct %.1f%%, %d pivots on the full tape.'
          % (K.RULED_OK, ow, pct, npiv))
    print('# NO EXIT MECH. each trade is measured to its next favourable %.1f%% pivot.' % pct)
    print()
    print('| the backstop signal | the lineage open | dir | open px | the %.1f%% pivot | bars | MAE %% | MFE %% | MFE over MAE |'
          % pct)
    print('|---|---|---|---|---|---|---|---|---|')
    for t in sc:
        r = (t['mfe'] / abs(t['mae'])) if t['mae'] < 0 else float('inf')
        print('| %s | %s | %s | %.5f | %s | %d | %+.3f | %+.3f | %s |'
              % (ln.U(t['fire']), ln.U(t['en']), t['dir'], t['p0'],
                 ln.U(t['piv']) if t['hit'] else 'none - the tape ends', t['bars'],
                 t['mae'], t['mfe'], ('%.2f' % r) if np.isfinite(r) else 'no MAE'))
    if not sc:
        sys.exit(0)
    mf = np.array([t['mfe'] for t in sc]); ma = np.array([t['mae'] for t in sc])
    bb = np.array([t['bars'] for t in sc])
    print()
    print('| the summary | value |')
    print('|---|---|')
    print('| trades | %d |' % len(sc))
    print('| no forward pivot | %d |' % sum(1 for t in sc if not t['hit']))
    print('| MFE, mean | %+.3f%% |' % mf.mean())
    print('| MFE, median | %+.3f%% |' % float(np.median(mf)))
    print('| MAE, mean | %+.3f%% |' % ma.mean())
    print('| MAE, median | %+.3f%% |' % float(np.median(ma)))
    print('| MFE over MAE, on the means | %.2f |' % (mf.mean() / abs(ma.mean())))
    print('| MFE over MAE, median of the per-trade ratios | %.2f |'
          % float(np.median([t['mfe'] / abs(t['mae']) for t in sc if t['mae'] < 0])))
    print('| trades whose MFE beats their MAE | %d of %d |'
          % (int(sum(1 for t in sc if t['mfe'] > abs(t['mae']))), len(sc)))
    print('| MFE >= %.1f%%, the pivot threshold | %d |' % (pct, int((mf >= pct).sum())))
    print('| the span to the pivot, median | %d bars = %d s |'
          % (int(np.median(bb)), int(np.median(bb)) * 5))
    for dd in ('LONG', 'SHORT'):
        s2 = [t for t in sc if t['dir'] == dd]
        if not s2: continue
        print('| %s | %d trades, MFE mean %+.3f%%, MAE mean %+.3f%% |'
              % (dd, len(s2), float(np.mean([t['mfe'] for t in s2])),
                 float(np.mean([t['mae'] for t in s2]))))
