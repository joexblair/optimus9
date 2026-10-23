"""EMERGING against CLOSED on the banked mechs. The A/B that decides which the machine runs.

Joe 1023: *"my view of this depends on the data: if a blanket shift to closed bars improves the
existing banked mechs, then we use closed bars. if a blanket shift makes it worse, when we create
5 new lines (cws1-3r and cws1-2Mage) as closed and assign them to v4core"*.

WHAT IS HELD IDENTICAL. Every knob, the banked r trip, max_pyramid 2, the exit, the drag, the
hold-out split. The ONLY thing that moves is the value_mode of the line arrays the mech reads.
Both legs run the same code paths - v4_fast.scan, v4_fast.walk, DT.accept, ledger, cap_pyramid -
so a difference is the lines and nothing else.

THE A/B IS TWO-STAGE, as always: the causal timestamps are banked first by the walk, then scored
by the pivots. Scoring never feeds back into generation.

THE REASON THE CACHE KEY FIX MATTERS HERE. v4_fast caches reversals and oob runs by the line's own
digest as of 1023, so handing it a closed array cannot serve the emerging array's reversals. Under
the old key - (tf, side, knobs) - this file would have silently compared emerging against emerging.

usage: v4_mode_ab.py <out.md>
"""
import sys
import io
import os
import time

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
import ln
import v4_knobs as K
import v4_fast as F
import v4_deferred_trades as DT
import v4_rcfg_sweep as RS
from v4_equity import ledger, cap_pyramid, concurrency, peak_notional, PCT, CAP, COINS, START, DRAG_22K
from v4_confluence import metrics, HEAD, RULE, row
from v4_backstop_trades import prices
_e = sys.stderr; sys.stderr = io.StringIO()
from optimus9.compute.line_config import override
from optimus9.orchestration.build_ws_lines import HOURS, WARMUP
from optimus9.orchestration.rpl_cache import LINE_DIR, _line_key
from optimus9.compute.swing_detect import find_pivots
sys.stderr = _e

SPLIT_TS = '2026-09-01 00:00:00'
TFS = list(range(1, 13))


def arr(spec_tuple, tf, mode):
    p = os.path.join(LINE_DIR,
                     _line_key(ln.EM, HOURS, WARMUP, override(tf * 60, spec_tuple, mode)) + '.npy')
    if not os.path.exists(p):
        raise SystemExit('MISSING ARRAY, build it first: tf%d %s %s' % (tf, spec_tuple, mode))
    return np.asarray(np.load(p, mmap_mode='r'), float)[:ln.N]


def lines(trip, mode):
    """-> (R, MG) at one trip and one value_mode. The Mage spec is fixed; only r varies."""
    r_spec = ('k',) + tuple(trip) + ('close',)
    R = {tf: arr(r_spec, tf, mode) for tf in TFS}
    MG = {tf: arr(ln.SPEC['Mage'][0], tf, mode) for tf in TFS}
    return R, MG


def run(R, MG, close, piv, A, B):
    """the banked chain end to end. -> the ledger after max_pyramid."""
    F.reset()
    rows = []
    for d in F.scan(A, B, R, MG):
        v, bar = F.walk(R, 5, d['side'], d['rev'], B)
        un = (v == 'EXHAUST' and bar is not None and bar >= B - 1)
        rows.append({'fire': d['fire'], 'rev': d['rev'], 'stamp': d['stamp'],
                     'side': d['side'], 'dir': d['dir'],
                     'verdict': 'UNRESOLVED' if un else v, 'exh': None if un else bar})
    allrows = ledger(DT.accept(rows), close, piv)
    return allrows, cap_pyramid(allrows, K.MAX_PYRAMID), len(rows)


if __name__ == '__main__':
    out = open(sys.argv[1], 'w', buffering=1)

    def log(s):
        out.write(s + '\n'); print(s, flush=True)

    t0 = time.time()
    close, hi, lo = prices()
    piv = find_pivots(close, PCT)
    A, B = 0, ln.N - 1
    SPLIT = ln.K(SPLIT_TS)
    bank = (RS.K0, RS.R0, RS.S0)
    prev = (5, 8, 7)                     # the previous bank, which is also the DB wsf r row

    log('# EMERGING against CLOSED on the banked mechs. the full tape, %d bars = %.0f days.'
        % (ln.N, ln.N * 5 / 86400.0))
    log('# RULED_OK %s. max_pyramid %d. drag %.4f%%. %d coins. start USDT %.2f.'
        % (K.RULED_OK, K.MAX_PYRAMID, DRAG_22K, COINS, START))
    log('# THE EXIT: a stopped trade at -%.3f%%, a positive at %.0f%% of its MFE, bar-ordered,'
        % (CAP, 90))
    log('#   on CLOSE prices either way - the value_mode is the LINES, not the price series.')
    log('# THE SPLIT: sweep %s .. %s, hold-out %s .. %s.'
        % (ln.U(0), ln.U(SPLIT - 1), ln.U(SPLIT), ln.U(B)))
    log('# the r trips are the legacy tuple slots (rsi, stc, k_len) - NOT (k, rsi, stc).')
    log('')

    res = {}
    for name, trip in (('the bank', bank), ('the previous bank', prev)):
        for mode in ('emerging', 'closed'):
            R, MG = lines(trip, mode)
            allr, L, nfire = run(R, MG, close, piv, A, B)
            res[(name, mode)] = (allr, L, nfire, R)
            print('# %s %s: %d fires, %d trades, %d after max_pyramid, %.0f s'
                  % (name, mode, nfire, len(allr), len(L), time.time() - t0), flush=True)

    log('# THE CONTROL ROW, both modes, both trips. ws5r at %s.' % K.CONTROL_TS)
    log('')
    log('| the trip | emerging ws5r | closed ws5r | known-good |')
    log('|---|---|---|---|')
    kb = ln.K(K.CONTROL_TS)
    log('| the bank %r | %.2f | %.2f | emerging %.2f |'
        % (bank, res[('the bank', 'emerging')][3][5][kb],
           res[('the bank', 'closed')][3][5][kb], K.CONTROL_BANK))
    log('| the previous bank %r | %.2f | %.2f | emerging %.2f |'
        % (prev, res[('the previous bank', 'emerging')][3][5][kb],
           res[('the previous bank', 'closed')][3][5][kb], K.CONTROL_DB))
    log('')

    log('# THE SIGNAL COUNTS. the trade list the lines produce, before any scoring.')
    log('')
    log('| the leg | backstop fires | accepted trades | after max_pyramid %d |' % K.MAX_PYRAMID)
    log('|---|---|---|---|')
    for name, trip in (('the bank', bank), ('the previous bank', prev)):
        for mode in ('emerging', 'closed'):
            allr, L, nf, _ = res[(name, mode)]
            log('| %s, %s | %d | %d | %d |' % (name, mode, nf, len(allr), len(L)))
    log('')

    for half, pick in (('THE FULL TAPE', lambda r: True),
                       ('THE SWEEP HALF', lambda r: r['en'] < SPLIT),
                       ('THE HOLD-OUT HALF', lambda r: r['en'] >= SPLIT)):
        log('# %s' % half)
        log('')
        log(HEAD); log(RULE)
        for name, trip in (('the bank', bank), ('the previous bank', prev)):
            for mode in ('emerging', 'closed'):
                L = [r for r in res[(name, mode)][1] if pick(r)]
                log(row('%s, %s' % (name, mode), metrics(L, COINS, DRAG_22K)))
        log('')

    log('# THE EXPOSURE, full tape, after max_pyramid %d.' % K.MAX_PYRAMID)
    log('')
    log('| the leg | max concurrent | peak open notional USDT | the bar it peaks on |')
    log('|---|---|---|---|')
    for name, trip in (('the bank', bank), ('the previous bank', prev)):
        for mode in ('emerging', 'closed'):
            L = res[(name, mode)][1]
            mc, _ = concurrency(L)
            pk, pb = peak_notional(L, COINS)
            log('| %s, %s | %d | %.2f | %s |'
                % (name, mode, mc, pk, ln.U(min(pb, ln.N - 1))))
    log('# took %.0f s' % (time.time() - t0))
    out.close()
