"""One arm: the banked chain's 94-day net under the current env knobs. Prints ONE row.

Joe 1023: *"create the 94 day net summaries for all 3 options vs banked, then sweep the knobs and
recreate the same summaries"*. This is the per-arm worker; the sweep is a shell loop over env.

ONLY OPTION 1 IS HERE. The pass rule is fully specified in his 1022 verbatim, so LIN_PASS 'ib'
(banked) against 'reversal' (his spec) is measurable. Options 2 and 3 - ws5r's own ib walk and the
lin-hop EXHAUST - have unresolved blanks and are NOT built; they are listed in v4_lineage.md.

usage: v4_pass_ab.py            (env sets the knobs; W_V4_EXPERIMENT=1 for an off-ruled arm)
"""
import sys
import io
import os

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
import ln
import v4_knobs as K
import v4_fast as F
import v4_deferred_trades as DT
import v4_rcfg_sweep as RS
from v4_equity import ledger, cap_pyramid, PCT, COINS, START, DRAG_22K
from v4_confluence import metrics
from v4_backstop_trades import prices
_e = sys.stderr; sys.stderr = io.StringIO()
from optimus9.compute.swing_detect import find_pivots
sys.stderr = _e

SPLIT = '2026-09-01 00:00:00'

if __name__ == '__main__':
    R = RS.load((RS.K0, RS.R0, RS.S0))
    MG = {t: ln.line('ws%dMage' % t) for t in range(1, 13)}
    close, hi, lo = prices()
    piv = find_pivots(close, PCT)
    A, B = 0, ln.N - 1
    sp = ln.K(SPLIT)
    F.reset()
    fires = F.scan(A, B, R, MG)
    RL = {t: R[t] for t in range(1, K.TF_CEILING + 3)}
    rows, verd = [], {}
    for d in fires:
        r = K.walkable_run(R, d['fire'], d['side'])
        stf = r[0] if r else None
        if stf is None:
            verd['NO WALKABLE RUN'] = verd.get('NO WALKABLE RUN', 0) + 1
            continue
        v, exh = F.walk(RL, stf, d['side'], d['rev'], B)
        verd[v] = verd.get(v, 0) + 1
        un = (v == 'EXHAUST' and exh is not None and exh >= B - 1)
        rows.append({'fire': d['fire'], 'rev': d['rev'], 'stamp': d['stamp'],
                     'side': d['side'], 'dir': d['dir'],
                     'verdict': 'UNRESOLVED' if un else v, 'exh': None if un else exh})
    L = cap_pyramid(ledger(DT.accept(rows), close, piv), K.MAX_PYRAMID)
    sw = [r for r in L if r['en'] < sp]
    ho = [r for r in L if r['en'] >= sp]
    def cell(rs):
        m = metrics(rs, COINS, DRAG_22K)
        if m is None:
            return '0 | - | - | - | - | - | -'
        nd = '%.2f' % m['ndd'] if np.isfinite(m['ndd']) else 'inf'
        pf = '%.2f' % m['pf'] if np.isfinite(m['pf']) else 'inf'
        return ('%d | %.1f | %+.2f | %+.2f | %.2f | %s | %s'
                % (m['n'], m['win_rate'], m['net_usd'], m['net_pct'], m['dd'], nd, pf))
    print('ARM|%s|%.1f|%.1f|%.1f|%d|%s|%d|%d|%s|%s|%s'
          % (K.LIN_PASS, K.LIN_IB_DWELL, K.RMOM_FNC, K.LIFT_WOB, K.TF_CEILING,
             K.RULED_OK, len(fires), verd.get('EXHAUST', 0),
             cell(L), cell(sw), cell(ho)))
