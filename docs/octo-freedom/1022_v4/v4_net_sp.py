"""The ws5rbackstop net, re-scored with `sweep-pivots` beside the banked 2% pivot. Joe 1024.

Joe 1024, his option 3: *"recreate the ws5rbackstop sweep that we banked yesterday. that gives us
a level of comfort or discomfort, without interfering in our in-progress v4core to 'ws4r to ws1Mage
ib' design flow"*. The backstop is BANKED, so its trades owe nothing to the mech under design -
which is the circularity he caught in the 5,323-event population.

WHAT CHANGES, AND IT IS ONE LINE. `v4_equity.ledger` measures the MFE from the entry to *"the next
favourable 2% pivot"*. That fixed pct is what `sweep-pivots` exists to replace. Same trades, same
entries, same exit rule, scored twice:

    banked         the window ends at the next favourable 2% pivot after the entry
    sweep-pivots   the window ends at the end of the sweep-pivots leg for that entry

THE SIDE MAPPING INVERTS, stated because it is easy to get backwards. A LONG wants price UP, so its
leg is one opened by a LOW cross: `side = -1`. `swing(bar, side)` has favourable = -side, so
`side = -d`.

sweep-pivots AS LOCKED, Joe 1024 option A: PICK 'lowest_pct', BAND 0.0, CONTAIN off, XWOB 18, and
the TF set is his six plus ws1Mage and ws2Mage. The measurement behind locking it: the event lands
a QUARTER into its leg whatever the leg's size - share 0.176 to 0.295 across legs from 0.5% to 4%+
- and 97.3% of 5,323 events fire BEFORE their pivot with 83.5% already favourable of it.

ONLY 12 OF THE 27 CONFIGS RUN. 15 line caches are gone from .rpl_cache/lines - every config with
k_len 5 or rsi 7 - and `RS.load` is read-only. The bank (6,8,6) and the DB row (5,8,7) are both
present. The missing ones are named in the output, never silently skipped.

THE OOB FILTER IS OFF, which is Joe's 1023 ruling: *"the oob filter can't be applied to a reversal
test"*. The 1024 net comparison found the bank and the DB row DISAGREE on whether it helps, so
nothing was changed.

usage: v4_net_sp.py <out.md>
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
import v4_rcfg_sweep as RS
import v4_deferred_trades as DT
import v4_sweep_pivots as SP
from v4_equity import ledger, CAPTURE, CAP
from v4_backstop_trades import prices
_e = sys.stderr; sys.stderr = io.StringIO()
from optimus9.compute.swing_detect import find_pivots
sys.stderr = _e

PCT = 2.0
DRAGS = (('0.1100', 0.1100), ('0.1770', 0.1770), ('0.1975', 0.1975))


def sp_bound(close):
    """-> a `bound` callable for v4_equity.ledger, backed by sweep-pivots."""
    def f(en, d):
        s = SP.scale(en, -d, wide=True)
        return None if (s is None or s.get('close') is None) else s['close']
    return f


if __name__ == '__main__':
    out = open(sys.argv[1], 'w', buffering=1)

    def log(s):
        out.write(s + '\n'); print(s, flush=True)

    MG = {t: ln.line('ws%dMage' % t) for t in range(1, 13)}
    close, hi, lo = prices()
    piv = find_pivots(close, PCT)
    A, B = 0, ln.N - 1
    BND = sp_bound(close)
    BANK = (RS.K0, RS.R0, RS.S0)

    log('# THE ws5rbackstop NET, RE-SCORED. Joe 1024, his option 3.')
    log('# the trades, the entries and the exit rule are IDENTICAL. Only the MFE window differs.')
    log('#   banked        -> the next favourable %.1f%% pivot after the entry (%d pivots)'
        % (PCT, len(piv)))
    log('#   sweep-pivots  -> the end of the sweep-pivots leg. PICK %r, BAND %.3f, CONTAIN %s,'
        % (SP.PICK, SP.BAND, 'on' if SP.CONTAIN else 'off'))
    log('#                    XWOB %d, TFs = his six plus ws1Mage and ws2Mage' % SP.XWOB)
    log('# THE EXIT IS JOE 1022: a stopped trade at -%.3f%%, a positive at %.0f%% of its MFE, read'
        % (CAP, CAPTURE * 100))
    log('#   in BAR ORDER. The 90%% leg is NOT causal - a SCORED net, not a tradeable one.')
    log('# the oob filter is OFF - Joe 1023, *"the oob filter can\'t be applied to a reversal test"*.')
    log('# the triple is (rsi, stc, k_len). RULED_OK %s. DRAG IS ITS OWN COLUMN.' % K.RULED_OK)
    log('')

    runnable, missing = [], []
    for trip in RS.cfgs():
        try:
            RS.load(trip); runnable.append(trip)
        except Exception:
            missing.append(trip)
    log('| the read | value |')
    log('|---|---|')
    log('| configs in the sweep | %d |' % (len(runnable) + len(missing)))
    log('| run here | %d |' % len(runnable))
    log('| SKIPPED, the line cache is gone from .rpl_cache/lines | %d |' % len(missing))
    for t in missing:
        log('| skipped | %r |' % (t,))
    log('')
    log('| rsi | stc | k_len | the MFE window | trades | stopped | stop rate | gross %% |'
        ' gross per trade %% | median MFE %% | drag at 0.1975 %% | NET at 0.1975 %% |')
    log('|---|---|---|---|---|---|---|---|---|---|---|---|')
    t0 = time.time()
    for i, trip in enumerate(runnable, 1):
        R = RS.load(trip)
        ctl = R[5][ln.K('2026-09-03 00:35:00')]
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
        mark = ' <- BANK' if trip == BANK else (' <- DB row' if trip == (5, 8, 7) else '')
        for lab, bnd in (('banked 2% pivot', None), ('sweep-pivots', BND)):
            L = ledger(acc, close, piv, bnd)
            n = len(L)
            if n == 0:
                log('| %d | %d | %d%s | %s | 0 | 0 | - | - | - | - | - | - |'
                    % (trip + (mark, lab)))
                continue
            g = np.array([r['od_g'] for r in L])
            stp = sum(1 for r in L if r['why'] == 'STOP')
            gross = float(g.sum()); dr = 0.1975
            log('| %d | %d | %d%s | %s | %d | %d | %.1f%% | %+.2f | %+.4f | %+.3f | %.2f | %+.2f |'
                % (trip[0], trip[1], trip[2], mark, lab, n, stp, stp / n * 100.0,
                   gross, gross / n, float(np.median([r['mfe'] for r in L])),
                   n * dr, gross - n * dr))
        print('# config %d of %d, ws5r control %.2f, %.0f s'
              % (i, len(runnable), ctl, time.time() - t0), flush=True)
    log('# took %.0f s' % (time.time() - t0))
    out.close()
