"""WIRING ONLY. Joe 1024: *"be sure to heavily SRP your work"*.

This file owns no mech and no rule. It loads the lines, calls the three signal producers, hands
their signals to the router, and prints. Every decision lives in the module that owns it:

    what a mech hands the walk  v4_walk_req
    v4core's two arms           v4_sig_core
    the backstop's fire         v4_sig_bstop
    the walk and who owns it    v4_walk_hold
    what a signal IS            v4_signal
    v4saviour's signal          v4_sig_saviour
    the fire, the direction,    v4_router
    the pyramid test, the drop

usage: v4_route_run.py <out|-> <start> <end> <walk scope: global|side> [max_pyramid]

THE WALK SCOPE IS REQUIRED. Joe 1024 ruled the walk exclusive - *"no other mech can meddle with
the walk once walk has started working with a mech"* - and whether that is one walk globally or one
per side is his, unsettled. There is no default, so nothing runs on a reading I picked.

max_pyramid MAY NOT SILENTLY DIFFER FROM THE BANK. K.MAX_PYRAMID is 2 and it is RULED, but this
file took the cap as a plain argument, so every run at 1 printed `RULED_OK True` beside a machine
that was not the bank. An off-ruled cap now refuses unless W_V4_EXPERIMENT=1, which is the same
rule v4_knobs applies to every other knob.
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
import v4_walk_hold as WH
import v4_router as RT
from v4_backstop_trades import prices


def main(dest, A, B, scope, mx):
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

    #   LAYER ONE: each mech hands the walk a request, born of its own qualifiers. LAYER TWO: the
    #   walk lets ONE claim it and emits the router signal. Joe 1024.
    reqs = SC.requests(CL, R, A, B) + SB.requests(R, MG, A, B)
    wj = []
    base = WH.run(reqs, R, A, B, scope, journal=wj)
    #   THE SAVIOUR ARMS ON THE WALK'S OUTPUT, one hunt per signal, and its own output joins it.
    #   Joe 1024: *"router doesn't feedback"* - the router is handed one flat list, never a mech.
    gens = []
    sigs = base + SS.produce(base, R, MG, gens=gens)
    jn = []
    trades, dropped = RT.route(sigs, A, B, max_pyramid=mx, journal=jn)
    trades.sort(key=lambda t: (t['open'], t['dir']))

    log('# THE ROUTER. Joe 1024. %s .. %s. max_pyramid %d, walk scope %s.'
        % (ln.U(A), ln.U(B), mx, scope))
    log('# the mechs produce SIGNALS; the router owns the fire, the direction, the pyramid test')
    log('#   and the close-all rule. RULED_OK %s.' % K.RULED_OK)
    log('# the control: ws5r %s = %.2f, expected %.2f'
        % (K.CONTROL_TS, R[5][ln.K(K.CONTROL_TS)], K.CONTROL_DB))
    log('')
    log('| the read | value |')
    log('|---|---|')
    log('| walk requests from core arm1 | %d |' % sum(1 for q in reqs if q['mech'] == 'core arm1'))
    log('| walk requests from core arm2 | %d |' % sum(1 for q in reqs if q['mech'] == 'core arm2'))
    log('| walk requests from ws5rbackstop | %d |'
        % sum(1 for q in reqs if q['mech'] == 'ws5rbackstop'))
    for v in ('CLAIMED', 'DISCARDED', 'NO CLAIM'):
        log('|   the walk %s | %d |' % (v, sum(1 for r in wj if r['verdict'] == v)))
    for m in SG.MECHS:
        log('| signals from %s | %d |' % (m, sum(1 for s in sigs if s['mech'] == m)))
    for i, g in enumerate(gens, 1):
        log('|   of those, saviour generation %d | %d |' % (i, len(g)))
    log('| signals routed | %d |' % len(sigs))
    log('| trades opened | %d |' % len(trades))
    log('| signals DROPPED by the pyramid test | %d |' % len(dropped))
    log('')
    log('| # | the signal | the open | dir | by | the close | MAE % | MFE % | detail |')
    log('|---|---|---|---|---|---|---|---|---|')
    #   THE SIGNAL BAR IS A COLUMN so the row carries the bar its mech resolved on, not only the
    #   bar the trade opened. Under Joe's 1024 drop ruling the open is always the signal bar + 1.
    for n, t in enumerate(trades, 1):
        en = int(t['open'])
        ex = int(t.get('close', B))
        d = 1 if t['dir'] == 'LONG' else -1
        p0 = float(close[en])
        h = float(np.nanmax(hi[en:ex + 1])); l = float(np.nanmin(lo[en:ex + 1]))
        mfe = ((h - p0) if d > 0 else (p0 - l)) / p0 * 100.0
        mae = ((l - p0) if d > 0 else (p0 - h)) / p0 * 100.0
        sb = int(t['sig']['bar'])
        assert en == sb + 1, 'a trade opened on a bar that is not its signal bar + 1'
        log('| %d | %s | %s | %s | %s | %s | %+.3f | %+.3f | %s |'
            % (n, ln.U(sb), ln.U(en),
               t['dir'], t['sig']['mech'],
               ln.U(ex) if 'close' in t else 'still open',
               mae, mfe, t['sig']['why']))
    log('')
    log('# THE ROUTER\'S OWN DECISIONS. Joe 1024 set the columns: the timestamp, the data passed')
    log('#   in, what the router did with it, and why it did that.')
    log('#   PASSED IN is the signal as the mech handed it over - its bar, its side, its mech.')
    log('#   WHY is the same-direction count AFTER the close against max_pyramid. That one')
    log('#   comparison is the only thing that decides OPEN or DROP; nothing else refuses.')
    log('')
    log('| the bar | passed in | what the router did | why |')
    log('|---|---|---|---|')
    for r in jn:
        act = []
        if r['closed']:
            act.append('closed the %s opened %s'
                       % (r['shuts'], ', '.join(ln.U(b) for b in r['closed'])))
        act.append('opened a %s' % r['wants'] if r['verdict'] == 'OPENED'
                   else 'DROPPED the %s' % r['wants'])
        why = '%d %s open of max %d' % (r['count'], r['wants'], r['cap'])
        if r['blocked_by']:
            why += ' - the %s opened %s fills it' % (r['wants'],
                                                     ', '.join(ln.U(b) for b in r['blocked_by']))
        log('| %s | %s %s %s | %s | %s |'
            % (ln.U(r['bar']), ln.U(r['sig']), 'HIGH' if r['side'] > 0 else 'LOW', r['mech'],
               ', then '.join(act), why))

    log('')
    log('# THE WALK\'S OWN DECISIONS. One row per request, in the order the walk served them.')
    log('#   CLAIMED = this mech owns the walk to its exhaust bar inclusive.')
    log('#   DISCARDED = another mech held the walk; `held to` is that walk\'s exhaust bar.')
    log('#   NO CLAIM = the walk ran and did not exhaust, so nothing is held.')
    log('')
    log('| the request | side | the mech | start TF | the walk | verdict | held to | the signal |')
    log('|---|---|---|---|---|---|---|---|')
    for r in wj:
        log('| %s | %s | %s | ws%d | %s | %s | %s | %s |'
            % (ln.U(r['bar']), 'HIGH' if r['side'] > 0 else 'LOW', r['mech'], r['start_tf'],
               r.get('walk', '-'), r['verdict'],
               ln.U(r['held_by']) if 'held_by' in r else '-',
               ln.U(r['signal']) if 'signal' in r else '-'))

    if dropped:
        log('')
        log('# THE SIGNALS THE PYRAMID TEST DROPPED. Each was acted on once, at its own bar + 1,')
        log('#   and refused. There is no queue, so none of these is retried.')
        log('')
        log('| the signal | side | by | the bar it was refused | detail |')
        log('|---|---|---|---|---|')
        for z in sorted(dropped, key=lambda y: y['bar']):
            log('| %s | %s | %s | %s | %s |'
                % (ln.U(z['bar']), 'HIGH' if z['side'] > 0 else 'LOW', z['mech'],
                   ln.U(z['dropped_at']) if z['dropped_at'] is not None else 'past the window',
                   z['why']))
    if dest != '-':
        out.close()


if __name__ == '__main__':
    _scope = sys.argv[4]
    _mx = int(sys.argv[5]) if len(sys.argv) > 5 else K.MAX_PYRAMID
    if _mx != K.MAX_PYRAMID and not os.environ.get('W_V4_EXPERIMENT'):
        raise SystemExit('REFUSED: max_pyramid %d is not the bank (%d). Set W_V4_EXPERIMENT=1 for '
                         'an off-ruled run.' % (_mx, K.MAX_PYRAMID))
    main(sys.argv[1], ln.K(sys.argv[2]), ln.K(sys.argv[3]), _scope, _mx)
