"""The NET of the deferred backstop trades, after Bybit fees and slippage, over the 27 r-configs.

Joe 1022: *"re stc and all of its new friends: what's the overall net (bybit fees and slippage)"*.

THE EXIT IS JOE'S, 1022: *"exit:  90% of MFE"*, read in BAR ORDER against the stop by
v4_equity.ledger - this file owns no copy of the rule.
    a stopped trade   exits at the pseudo stop, -1.100%. That is a real, causal exit rule.
    a positive trade  exits at 0.90 x its MFE, the MFE measured to the next favourable 2% pivot.
THE MFE IS KNOWN ONLY AFTERWARDS, so the 90% leg is NOT CAUSAL and this is a SCORED net, not a
tradeable one. It answers "if we captured 90% of the move, what is left after costs" and nothing
more. No exit mech exists for the backstop - #17 is held back.

THE COSTS ARE THE BANKED ONES, from _fill.py's decomposition of docs/arm_delay_book.md:
    0.1100%  Joe 1007: *"0.11 is bybit's fees"* - the figure _sweep2 and _lineworker carry
    0.1770%  taker/taker round trip: 0.110 fee + 0.067 slippage
    0.1975%  the banked conservative: (5.50 fee + 4.375 slip) x 2 legs, 22,000 coins
All three are reported. DRAG IS ITS OWN COLUMN, never folded into the net.

usage: v4_net.py <out.md>
"""
import sys
import io
import os
import datetime as dt
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
from v4_equity import ledger, CAPTURE  # ONE copy of Joe's exit rule, and it lives there
from v4_backstop_trades import prices
_e = sys.stderr; sys.stderr = io.StringIO()
from optimus9.compute.swing_detect import find_pivots
sys.stderr = _e

PCT, CAP = 2.0, 1.1
DRAGS = (('0.1100', 0.1100), ('0.1770', 0.1770), ('0.1975', 0.1975))


def net_of(acc, close, piv):
    """-> the per-trade gross returns, and how many were stopped.

    THE TWO EXITS ARE READ IN BAR ORDER, by v4_equity.ledger. The earlier version here booked a
    stop whenever the segment minimum reached -CAP whatever the order, which charged the stop to
    trades whose 90%-of-MFE exit had already fired.
    """
    L = ledger(acc, close, piv)
    return (np.array([r['od_g'] for r in L]),
            sum(1 for r in L if r['why'] == 'STOP'))


if __name__ == '__main__':
    out = open(sys.argv[1], 'w', buffering=1)

    def log(s):
        out.write(s + '\n'); print(s, flush=True)

    MG = {t: ln.line('ws%dMage' % t) for t in range(1, 13)}
    close, hi, lo = prices()
    piv = find_pivots(close, PCT)
    A, B = 0, ln.N - 1
    log('# the NET over the 27 r-configs. the full tape, %d bars = %.0f days.'
        % (ln.N, ln.N * 5 / 86400.0))
    log('# THE EXIT, Joe 1022: a stopped trade at -%.3f%%, a positive at %.0f%% of its MFE.'
        % (CAP, CAPTURE * 100))
    log('#   the MFE is known only AFTERWARDS - a SCORED net, not a tradeable one.')
    log('# %d pivots at %.1f%%. DRAG IS ITS OWN COLUMN.' % (len(piv), PCT))
    log('')
    log('| k | rsi | stc | trades | stopped | gross % | gross per trade % | '
        'drag at 0.1100 % | drag at 0.1770 % | drag at 0.1975 % | '
        'NET at 0.1100 % | NET at 0.1770 % | NET at 0.1975 % |')
    log('|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    t0 = time.time()
    for i, trip in enumerate(RS.cfgs(), 1):
        R = RS.load(trip)
        F.reset()
        f = F.scan(A, B, R, MG, 'window')
        rows = []
        for d in f:
            v, bar = F.walk(R, 5, d['side'], d['rev'], B)
            un = (v == 'EXHAUST' and bar is not None and bar >= B - 1)
            rows.append({'fire': d['fire'], 'rev': d['rev'], 'stamp': d['stamp'],
                         'side': d['side'], 'dir': d['dir'],
                         'verdict': 'UNRESOLVED' if un else v, 'exh': None if un else bar})
        acc = DT.accept(rows)
        g, stp = net_of(acc, close, piv)
        n = len(g)
        mark = ' <- BANKED' if trip == (RS.K0, RS.R0, RS.S0) else ''
        if n == 0:
            log('| %d | %d | %d%s | 0 | 0 | - | - | - | - | - | - | - | - |' % (trip + (mark,)))
            continue
        gross = float(g.sum())
        cells = [n * dr for _, dr in DRAGS] + [gross - n * dr for _, dr in DRAGS]
        log('| %d | %d | %d%s | %d | %d | %+.2f | %+.4f | %.2f | %.2f | %.2f | '
            '%+.2f | %+.2f | %+.2f |'
            % ((trip[0], trip[1], trip[2], mark, n, stp, gross, gross / n) + tuple(cells)))
        print('# arm %d of 27, %.0f s' % (i, time.time() - t0), flush=True)
    log('# took %.0f s' % (time.time() - t0))
    out.close()
