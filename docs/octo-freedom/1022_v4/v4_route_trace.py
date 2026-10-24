"""THE WALK BETWEEN TWO REV-TRADES. Joe 1024: *"let's see the walk FROM 00:33 to the next
rev-trade"*.

NO MECH HERE. It runs the same pipeline `v4_route_run` runs - the two request producers, the walk
holder, the saviour, the router - and then prints what the WALK did inside one rev-trade interval.
The baton steps come from `v4_fast.walk`'s own `events` hook, which exists so a caller can ask what
the walk did without re-implementing it.

THE INTERVAL IS NOT CHOSEN HERE. `frm` names a bar; the first rev-trade at or after it opens the
interval and the NEXT rev-trade closes it. A rev-trade is a trade OPEN in the router's output -
Joe's *"CLOSE the trade, then OPEN a NEW trade in the opposite direction"*.

usage: v4_route_trace.py <out|-> <start> <end> <walk scope: global|side> <from>
"""
import io
import os
import sys

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
import ln
import v4_knobs as K
import v4_fast as F
import v4_rcfg_sweep as RS
import v4_core_arm as CA
import v4_sig_core as SC
import v4_sig_bstop as SB
import v4_sig_saviour as SS
import v4_walk_hold as WH
import v4_router as RT


def _tag(v, side):
    """How a bar's r value reads against the fences it is tested at. -> a short string."""
    if K.oob(v, side):
        return 'oob'
    return 'ex-fence' if K.ex_fence(v, side) else 'in-fence'


def main(dest, A, B, scope, frm):
    out = sys.stdout if dest == '-' else open(dest, 'w', buffering=1)

    def log(s):
        out.write(s + '\n')

    R = RS.load((RS.K0, RS.R0, RS.S0))
    MG = {t: ln.line('ws%dMage' % t) for t in range(1, 13)}
    CL = CA.lines()
    F.reset()

    reqs = SC.requests(CL, R, A, B) + SB.requests(R, MG, A, B)
    wj = []
    base = WH.run(reqs, R, A, B, scope, journal=wj)
    sigs = base + SS.produce(base, R, MG)
    trades, _ = RT.route(sigs, A, B)

    rev = sorted(int(t['open']) for t in trades)
    at = [r for r in rev if r >= int(frm)]
    if not at:
        log('# no rev-trade at or after %s' % ln.U(frm))
        return
    R0 = at[0]
    nxt = [r for r in rev if r > R0]
    R1 = nxt[0] if nxt else int(B)

    log('# THE WALK BETWEEN TWO REV-TRADES. Joe 1024. walk scope %s, max_pyramid %d.'
        % (scope, K.MAX_PYRAMID))
    log('# RULED_OK %s. the control: ws5r %s = %.2f, expected %.2f'
        % (K.RULED_OK, K.CONTROL_TS, R[5][ln.K(K.CONTROL_TS)], K.CONTROL_DB))
    log('')
    log('| the interval | bar |')
    log('|---|---|')
    log('| it opens on the rev-trade at | %s |' % ln.U(R0))
    log('| it closes on the next rev-trade at | %s |' % (ln.U(R1) if nxt else 'the window end'))
    log('| bars | %d = %d s |' % (R1 - R0, (R1 - R0) * 5))

    inside = [r for r in wj if R0 <= r['bar'] <= R1]
    log('')
    log('# EVERY WALK REQUEST INSIDE THE INTERVAL, in the order the walk served them.')
    log('')
    log('| the request | side | the mech | start TF | the walk | verdict | held to | the signal |')
    log('|---|---|---|---|---|---|---|---|')
    for r in inside:
        log('| %s | %s | %s | ws%d | %s | %s | %s | %s |'
            % (ln.U(r['bar']), 'HIGH' if r['side'] > 0 else 'LOW', r['mech'], r['start_tf'],
               r.get('walk', '-'), r['verdict'],
               ln.U(r['held_by']) if 'held_by' in r else '-',
               ln.U(r['signal']) if 'signal' in r else '-'))

    for r in inside:
        if r['verdict'] != 'CLAIMED':
            continue
        ev = []
        v, exh = F.walk(R, r['start_tf'], r['side'], r['anchor'], B, events=ev)
        log('')
        log('## the CLAIMED walk: %s %s from ws%d, anchor %s -> %s %s'
            % (r['mech'], 'HIGH' if r['side'] > 0 else 'LOW', r['start_tf'], ln.U(r['anchor']),
               v, ln.U(exh) if exh is not None else '-'))
        log('')
        if not ev:
            log('no baton hand-off: the walk resolved on its start rung.')
            continue
        log('| the baton bar | from | to | the receiver r | its reversal stamp | second walk |')
        log('|---|---|---|---|---|---|')
        for e in ev:
            log('| %s | ws%d | ws%d | %.2f %s | %s | %s |'
                % (ln.U(e['pas']), e['frm'], e['to'], e['r_to'], _tag(e['r_to'], r['side']),
                   ln.U(e['rev_to']) if e['rev_to'] is not None else 'none',
                   ln.U(e['p2']) if e['p2'] is not None else '-'))

    tfs = [t for t in (1, 2, 3, 4, 5, 6) if t in R]
    sd = inside[0]['side'] if inside else -1
    log('')
    log('# THE 5-SECOND ROWS, %s .. %s. r values on the DB-row config (rsi %d, stc %d, k_len %d),'
        % (ln.U(R0), ln.U(R1), RS.K0, RS.R0, RS.S0))
    log('#   tagged against the %s side, which the claimed walk carries.'
        % ('HIGH' if sd > 0 else 'LOW'))
    log('')
    log('| the bar | ' + ' | '.join('ws%dr' % t for t in tfs) + ' |')
    log('|---|' + '---|' * len(tfs))
    for k in range(R0, R1 + 1):
        log('| %s | ' % ln.U(k)
            + ' | '.join('%.2f %s' % (R[t][k], _tag(R[t][k], sd)) for t in tfs) + ' |')
    if dest != '-':
        out.close()


if __name__ == '__main__':
    main(sys.argv[1], ln.K(sys.argv[2]), ln.K(sys.argv[3]), sys.argv[4], ln.K(sys.argv[5]))
