"""report_rule1_gate — rule#1 plus the scenario, at every wsf_leash signal. Joe 0923/0924.

Joe 0924: "bake it into rule#1 and recreate the gate data".

The decision lives in ONE producer and this file only loads lines, runs the divergence and prints.

    optimus9/compute/rule1_gate.py   the gate: rule#1 leg OR scenario leg
    optimus9/analysis/jig.py         anchor_floater - the divergence front end, NOT re-implemented

WHAT IS NOT IN THE DB, AND WHY IT IS NOT
  `rule1_tol` 7 min, the 27/73 fence and the ws2r/ws3r/gcws30r line set are Joe's values, said in
  chat and never banked. They are module constants below.

  Banking them needs a new wsf_dtf_v3_config version, and `leash_bank.knob_string` puts the config
  version INSIDE `wsl_knobs` — the v7/v8 in the 121-row bank Joe is working on IS the config
  version. A v11 would make the next leash bank write `v11_...` and split it off from the rows
  this report reads. That consequence is Joe's to sanction, so nothing was written.

  The two divergence knobs ARE banked and are read from the config: anchor_floater.block (v9) and
  anchor_floater.dwell_min_per_tf (v10).

NOT CAUSAL AT THE SIGNAL BAR. Joe 0924 ruled the window is "within (either side)" of sig_utc, so
the gate reads TOL_BARS after the signal and is knowable 210 s late. His rule, stated plainly.

    python3 report_rule1_gate.py
    python3 report_rule1_gate.py --instance v8 --md
"""
import argparse
import os
import sys

import numpy as np

from optimus9 import DatabaseManager
from optimus9.analysis.jig import Jig, anchor_floater
from optimus9.compute.line_config import mech_lines, override
from optimus9.compute.rule1_gate import gate
from optimus9.compute.v3_config import v3_config
from optimus9.config import get_db_config
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP
from optimus9.orchestration.rpl_cache import LINE_DIR, TAPE_DIR, _line_key, _tape_key

# Joe's values, said in chat, NOT in wsf_dtf_v3_config - see the module docstring for why.
RULE1_TOL_MIN = 7.0                 # KNOB, Joe 0924: "change it to 7 minutes". TOTAL, both sides
RULE1_FENCE = (27.0, 73.0)          # KNOB, Joe 0923: "the fence is 27:73"
GRID_S = 5                          # the tape's bar width in seconds
DIV_TF = 1                          # the line the divergence is run on: ws1r
SCENARIO_LINES = ('ws2r', 'ws3r', 'gcws30r')    # Joe 0924, his own list

INSTANCE = {
    'v7': 'v7_coil_lines[gcws30,ws1]_confirm_lag_s180_exit_anchornamed_bar_gap_fill1'
          '_lookback_s240_support_min23',
    'v8': 'v8_coil_lines[ws2,ws3]_confirm_lag_s180_exit_anchornamed_bar_gap_fill1'
          '_lookback_s240_support_min23',
}


def _specs(db):
    """role -> (src, mode), as build_wsf_dtf_v3 reads them."""
    spec = {}
    for g in mech_lines(db, 'wsf'):
        if g['role'] not in spec:
            _t, s_, m_ = g['override']
            spec[g['role']] = (s_, m_)
    return spec


def load(db, C):
    """Every line the gate needs, all on the 5 s tape grid. -> (ts, r1, r2, r3, g30r, x_next, px).

    ws1..ws3 come from the per-line cache build_wsf_dtf_v3 reads. gcws30r and the price come off
    the Jig and are mapped onto the same grid. `x_next` is ws{DIV_TF+1}x, which anchor_floater's
    step 2 dwell rule reads.
    """
    sy = db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l FROM optimus9_system '
                    'WHERE sys_pk=1', fetch=True)[0]
    spec = _specs(db)
    ts = np.load(os.path.join(TAPE_DIR, _tape_key(END_MS, HOURS, WARMUP,
                                                  {'src': sy['s'], 'len': sy['l']}) + '.npz'))['__ts__']
    cached = lambda tf, role: np.load(os.path.join(
        LINE_DIR, _line_key(END_MS, HOURS, WARMUP, override(tf * 60, *spec[role])) + '.npy'))
    with Jig(END_MS, hours=HOURS, warmup=WARMUP) as J:
        jt = np.asarray(J.ts, dtype=np.int64)
        g30r = np.asarray(J.causal.line('gcws30r'), float)
        px = np.asarray(J.px, float)
    idx = np.clip(np.searchsorted(jt, ts), 0, len(jt) - 1)
    px = np.asarray([v for v in px], float)
    good = np.isfinite(px)
    if not good.all():                      # the Jig's own gaps, carried forward then back
        px = np.interp(np.arange(len(px)), np.flatnonzero(good), px[good])
    return (ts, cached(1, 'r'), cached(2, 'r'), cached(3, 'r'), g30r[idx],
            cached(DIV_TF + 1, 'x'), px[idx])


def main(argv=None):
    a = argparse.ArgumentParser()
    a.add_argument('--instance', default='v7', choices=sorted(INSTANCE))
    a.add_argument('--md', action='store_true', help='pipe-delimited, for pasting into a report')
    o = a.parse_args(argv)

    db = DatabaseManager(**get_db_config()); db.connect()
    C = v3_config(db)
    rows = db.execute('SELECT wsl_dr, wsl_source, wsl_sig_utc, wsl_sig_ms FROM wsf_leash '
                      'WHERE wsl_knobs=%s AND wsl_sig_ms IS NOT NULL ORDER BY wsl_sig_ms',
                      (INSTANCE[o.instance],), fetch=True)
    ts, r1, r2, r3, g30r, x2, px = load(db, C)
    db.disconnect()

    oob = (float(C['oob_lo']), float(C['oob_hi']))
    tol = int(RULE1_TOL_MIN * 60 / GRID_S / 2)
    dwell_bars = DIV_TF * int(C['dwell_min_per_tf']) * (60 // GRID_S)
    blk = int(C['block'])

    p = (lambda *c: print('|'.join(str(v) for v in c))) if o.md else \
        (lambda *c: print((('  %-4s %-19s %-3s %-8s' + '%-6s' * 4 + '%-5s' + '%-7s' * 3 +
                            '%-8s %-5s %-7s %s') % c).rstrip()))
    print('rule#1 + the scenario   %s   %d rows' % (INSTANCE[o.instance], len(rows)))
    print('  gate       open = rule#1 leg OR scenario leg   (the OR is MINE, Joe said "bake it in")')
    print('  rule#1     ws1r AND (ws2r OR ws3r) strictly outside %g/%g on the dr side, any bar in '
          'the window' % RULE1_FENCE)
    print('  scenario   ws%dr divergence fires AND %s each have a bar strictly oob %g/%g on the '
          'dr side' % (DIV_TF, ', '.join(SCENARIO_LINES), oob[0], oob[1]))
    print('  window     rule1_tol %g min TOTAL = +/- %d bars = +/- %d s. Joe: "within (either '
          'side)", so the gate lands %d s AFTER the signal' % (RULE1_TOL_MIN, tol, tol * GRID_S,
                                                               tol * GRID_S))
    print('  divergence anchor_floater, block %d bars = %d s (v9), step 2 dwell = ws%dx for %d '
          'bars = %d min (v10)' % (blk, blk * GRID_S, DIV_TF + 1, dwell_bars,
                                   dwell_bars * GRID_S // 60))
    print('  not banked rule1_tol and the %g/%g fence are Joe\'s values held as module constants'
          % RULE1_FENCE)
    print('  dwell bars the rule#1 leg only. A row opened by the scenario alone reads 0')
    print('')
    p('#', 'wsl_sig_utc', 'dr', 'src', 'ws1r', 'ws2r', 'ws3r', 'dwell', 'div',
      'ws2oob', 'ws3oob', 'g30oob', 'rule#1', 'scen', 'GATE', 'change')

    n1 = ns = ng = 0
    added = []
    for n, x in enumerate(rows, 1):
        k = int(np.searchsorted(ts, int(x['wsl_sig_ms'])))
        dr = int(x['wsl_dr'])
        res = anchor_floater(r1, px, dr, k, block=blk, mid=50.0,
                             xn=x2, dwell_bars=dwell_bars, oob=oob)
        fired = 0 if res is None else int(res['fired'])
        g = gate(r1, r2, r3, g30r, dr, k, tol, RULE1_FENCE, oob, fired)
        n1 += g['rule1']; ns += g['scenario']; ng += g['open']
        change = 'NEW OPEN' if (g['open'] and not g['rule1']) else ''
        if change:
            added.append((n, x['wsl_sig_utc'], dr))
        p(n, x['wsl_sig_utc'].strftime('%m-%d %H:%M:%S'), '%+d' % dr, x['wsl_source'],
          g['ws1_bars'], g['ws2_bars'], g['ws3_bars'], g['dwell_bars'],
          'Y' if fired else '.', g['ws2_oob'], g['ws3_oob'], g['g30_oob'],
          'open' if g['rule1'] else 'closed', 'HIT' if g['scenario'] else '.',
          'OPEN' if g['open'] else 'closed', change)

    print('')
    print('  rows %d   rule#1 open %d   scenario hits %d   GATE open %d   closed %d'
          % (len(rows), n1, ns, ng, len(rows) - ng))
    print('  the scenario adds %d rows, %d distinct timestamps'
          % (len(added), len({u for _n, u, _d in added})))
    for n, u, dr in added:
        print('    #%-4d %s  dr %+d' % (n, u.strftime('%m-%d %H:%M:%S'), dr))
    return 0


if __name__ == '__main__':
    sys.exit(main())
