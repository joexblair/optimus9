"""WIRING ONLY. Joe 1024: *"be sure to heavily SRP your work"*.

This file owns no mech and no rule. It loads the lines, calls the three signal producers, hands
their signals to the router, and prints. Every decision lives in the module that owns it:

    what a signal IS            v4_signal
    v4core's signals            v4_sig_core
    the backstop's signals      v4_sig_bstop
    v4saviour's signal          v4_sig_saviour
    the fire, the direction,    v4_router
    the pyramid test, the hold

usage: v4_route_run.py <out|-> <start> <end> [max_pyramid]
"""
import io
import os
import sys

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
import ln
import v4_knobs as K
import v4_fast as F
import v4_rcfg_sweep as RS
import v4_core_arm as CA
import v4_signal as SG
import v4_sig_core as SC
import v4_sig_bstop as SB
import v4_sig_saviour as SS
import v4_router as RT
from v4_backstop_trades import prices


def main(dest, A, B, mx):
    out = sys.stdout if dest == '-' else open(dest, 'w', buffering=1)

    def log(s):
        out.write(s + '\n')
        if dest != '-':
            print(s, flush=True)

    R = RS.load((RS.K0, RS.R0, RS.S0))
    MG = {t: ln.line('ws%dMage' % t) for t in range(1, 13)}
    CL = CA.lines()
    close, hi, lo = prices()
    F.reset()

    sigs = SC.produce(CL, R, A, B) + SB.produce(R, MG, A, B)
    trades, held = RT.route(sigs, A, B,
                            saviour=lambda b, d: SS.produce(b, d, R, MG),
                            max_pyramid=mx)
    trades.sort(key=lambda t: (t['open'], t['dir']))

    log('# THE ROUTER. Joe 1024. %s .. %s. max_pyramid %d.' % (ln.U(A), ln.U(B), mx))
    log('# the mechs produce SIGNALS; the router owns the fire, the direction, the pyramid test')
    log('#   and the close-all rule. RULED_OK %s.' % K.RULED_OK)
    log('# the control: ws5r %s = %.2f, expected %.2f'
        % (K.CONTROL_TS, R[5][ln.K(K.CONTROL_TS)], K.CONTROL_DB))
    log('')
    log('| the read | value |')
    log('|---|---|')
    for m in SG.MECHS:
        log('| signals from %s | %d |' % (m, sum(1 for s in sigs if s['mech'] == m)))
    log('| signals routed | %d |' % len(sigs))
    log('| trades opened | %d |' % len(trades))
    log('| signals still HELD at the window end | %d |' % len(held))
    log('')
    log('| # | the signal | the open | wait | dir | by | the close | MAE % | MFE % | detail |')
    log('|---|---|---|---|---|---|---|---|---|---|')
    #   THE SIGNAL BAR AND THE WAIT ARE COLUMNS, not prose. A signal fires at the bar its hold
    #   clears, so a trade can open long after the bar its mech resolved on, and without these two
    #   columns the row reads as though the mech fired at the open.
    for n, t in enumerate(trades, 1):
        en = int(t['open'])
        ex = int(t.get('close', B))
        d = 1 if t['dir'] == 'LONG' else -1
        p0 = float(close[en])
        h = float(np.nanmax(hi[en:ex + 1])); l = float(np.nanmin(lo[en:ex + 1]))
        mfe = ((h - p0) if d > 0 else (p0 - l)) / p0 * 100.0
        mae = ((l - p0) if d > 0 else (p0 - h)) / p0 * 100.0
        sb = int(t['sig']['bar'])
        wait = (en - sb) * 5
        log('| %d | %s | %s | %s | %s | %s | %s | %+.3f | %+.3f | %s |'
            % (n, ln.U(sb), ln.U(en),
               '-' if wait <= 5 else '%dm%02ds' % divmod(wait, 60),
               t['dir'], t['sig']['mech'],
               ln.U(ex) if 'close' in t else 'still open',
               mae, mfe, t['sig']['why']))
    wait = [t for t in trades if int(t['open']) - int(t['sig']['bar']) > 1]
    if wait:
        log('')
        log('# WHY EACH HELD SIGNAL WAITED. One row per refusal, recorded by the router at the bar')
        log('#   it refused. `blocked by` is the OPEN BAR of each trade that filled max_pyramid.')
        log('')
        log('| # | the signal | refused at | wanted | blocked by | blocker | opened |')
        log('|---|---|---|---|---|---|---|')
        #   `blocker` = SIBLING when every blocking trade opened AT OR AFTER this signal's own bar,
        #   so the slot was taken by a signal that arrived at the same moment; EARLIER LEG when a
        #   blocking trade was already open before this signal landed. The two are different
        #   problems: a sibling block is a convergence of signals, an earlier-leg block is the
        #   pyramid cap doing what it is for.
        #   NOT an exact bar match: a blocking trade opens at ITS signal bar + 1, so a sibling's
        #   open is one bar AFTER the bar this signal shares with it.
        for t in trades:
            if int(t['open']) - int(t['sig']['bar']) <= 1:
                continue
            n = trades.index(t) + 1
            rf = t['sig'].get('refused', [])
            if not rf:
                log('| %d | %s | (none recorded) | | | | %s |'
                    % (n, ln.U(int(t['sig']['bar'])), ln.U(int(t['open']))))
            for i, (bar, dirn, blk) in enumerate(rf):
                sb = int(t['sig']['bar'])
                own = 'SIBLING' if blk and all(b >= sb for b in blk) else 'EARLIER LEG'
                log('| %s | %s | %s | %s | %s | %s | %s |'
                    % (n if i == 0 else '', ln.U(int(t['sig']['bar'])) if i == 0 else '',
                       ln.U(bar), dirn, ', '.join(ln.U(b) for b in blk), own,
                       ln.U(int(t['open'])) if i == len(rf) - 1 else ''))
    if held:
        log('')
        log('| the held signal | side | by | the bar it was refused | detail |')
        log('|---|---|---|---|---|')
        for s in sorted(held, key=lambda z: z['bar']):
            log('| %s | %s | %s | %s | %s |'
                % (ln.U(s['bar']), 'HIGH' if s['side'] > 0 else 'LOW', s['mech'],
                   ln.U(s['held_at']) if 'held_at' in s else 'past the window', s['why']))
    if dest != '-':
        out.close()


if __name__ == '__main__':
    main(sys.argv[1], ln.K(sys.argv[2]), ln.K(sys.argv[3]),
         int(sys.argv[4]) if len(sys.argv) > 4 else K.MAX_PYRAMID)
