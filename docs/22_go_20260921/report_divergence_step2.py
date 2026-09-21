"""report_divergence_step2 - spec_label 22_go_20260921, spec 12.1.

`anchor_floater` at every wsl_sig_utc, under Joe's 0921 step 2.

STEP 2, Joe 0921: "instead of relying on r passing 50 (paraphrasing), use ws{tf+1}x dwelling in
dr-opposing oob, for tf*{knob:1}".  A ws3r test reads ws4x for 3 minutes, a ws4r test reads ws5x
for 4 minutes.  The pivot is that run's x EXTREME - Joe chose the extreme over the run's first or
last bar.

STEP 1 unchanged.  STEP 3 keeps its 50 filter, which is Joe's own verbatim - "find the r extrema
that is on the same side as step 1's dr" - and drops the empty-block STOP: a block with no dr-side
bar is skipped and the walk continues.  The walk now ends only at a non-improving block or the
tape start, so a floater may sit on the previous day.

KNOBS, both banked: anchor_floater.block 60 bars = 300 s (v9), anchor_floater.dwell_min_per_tf 1
minute per timeframe (v10).

    python3 report_divergence_step2.py
    python3 report_divergence_step2.py --tfs 3,4 --from '2026-09-01' --to '2026-09-02' --knobs v7
"""
import argparse
import io
import os
import sys

import numpy as np

sys.stdout, _real = io.StringIO(), sys.stdout
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '_prelude.py')).read()
     .split("k=int(np.searchsorted")[0])
sys.stdout = _real

from optimus9.analysis.jig import anchor_floater
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

KNOBSETS = {
    'v7': 'v7_coil_lines[gcws30,ws1]_confirm_lag_s180_exit_anchornamed_bar_gap_fill1'
          '_lookback_s240_support_min23',
    'v8': 'v8_coil_lines[ws2,ws3]_confirm_lag_s180_exit_anchornamed_bar_gap_fill1'
          '_lookback_s240_support_min23',
}
VERDICT = {1: 'bearish +1', -1: 'bullish -1', 0: 'none 0'}


def main(tfs, t_from, t_to, knobs):
    oob = (W.OOB_LO, W.OOB_HI)
    blk = int(_C['block'])
    dpt = int(_C['dwell_min_per_tf'])
    a = int(np.searchsorted(ts, ms(t_from + ' 00:00:00')))
    b = int(np.searchsorted(ts, ms(t_to + ' 00:00:00')))
    x = {t + 1: Ln(t + 1, 'x') for t in tfs}

    db = DatabaseManager(**get_db_config()); db.connect()
    rows = db.execute('SELECT wsl_dr,wsl_source,wsl_sig_utc,wsl_sig_ms FROM wsf_leash '
                      'WHERE wsl_knobs=%s AND wsl_sig_ms IS NOT NULL ORDER BY wsl_sig_ms',
                      (KNOBSETS[knobs],), fetch=True)
    db.disconnect()

    print('divergence step 2   spec_label 22_go_20260921, spec 12.1')
    print('  instance   %s' % KNOBSETS[knobs])
    print('  window     %s -> %s' % (t_from, t_to))
    print('  step 2     ws{tf+1}x contiguous in the dr-opposing oob %g/%g for tf x %d min, '
          'pivot = that run\'s x extreme' % (oob[0], oob[1], dpt))
    print('  step 3     block %d bars = %d s, 50 filter kept, empty blocks SKIPPED' % (blk, blk * 5))
    print('  verdict    +1 bearish / -1 bullish / 0 none / no result = no anchor, pivot or floater')
    print('')
    head = '  wsl_sig_utc          dr  src     '
    for t in tfs:
        head += (' %-13s  %-16s  %-7s ' % ('ws%dr verdict' % t, 'ws%dr floater' % t, 'd_osc'))
    print(head)
    print('  ' + '-' * (len(head) - 2))
    tally = {t: {} for t in tfs}
    for r in rows:
        k = int(np.searchsorted(ts, int(r['wsl_sig_ms'])))
        if not (a <= k < b):
            continue
        d = int(r['wsl_dr'])
        line = '  %s  %+d  %-7s ' % (U(k), d, r['wsl_source'])
        for t in tfs:
            res = anchor_floater(RA[t], PXT, d, k, block=blk, mid=50.0,
                                 xn=x[t + 1], dwell_bars=t * dpt * 12, oob=oob)
            key = 'no result' if res is None else VERDICT[res['fired']]
            tally[t][key] = tally[t].get(key, 0) + 1
            line += (' %-13s  %-16s  %-7s ' %
                     (key, '' if res is None else U(res['floater'][0])[5:],
                      '' if res is None else '%+.2f' % res['d_osc']))
        print(line)
    print('  ' + '-' * (len(head) - 2))
    for t in tfs:
        print('  ws%dr  %s' % (t, '   '.join('%s %d' % (k, v) for k, v in sorted(tally[t].items()))))
    return 0


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--tfs', default='3,4')
    p.add_argument('--from', dest='t_from', default='2026-09-01')
    p.add_argument('--to', dest='t_to', default='2026-09-02')
    p.add_argument('--knobs', default='v7', choices=sorted(KNOBSETS))
    o = p.parse_args()
    sys.exit(main([int(v) for v in o.tfs.split(',')], o.t_from, o.t_to, o.knobs))
