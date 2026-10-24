"""WHY ONE BAR CARRIED SEVERAL SIGNALS. Joe 1024: *"pick the first 'blocked by sibling' and show me
the 5sec timestamped rows that produced the block"*.

NO MECH HERE. It calls the same producers the router is fed by and re-runs each signal's lineage
walk with `v4_fast.walk`'s own `events` hook, which exists so a caller can ask what the walk did
without re-implementing it. Every number printed comes from the module that owns it.

usage: v4_route_trace.py <out|-> <start> <end> <the signal bar>
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


def _tag(v, side):
    """How a bar's r value reads against the fences it is tested at. -> a short string."""
    t = []
    if K.oob(v, side):
        t.append('oob')
    elif K.ex_fence(v, side):
        t.append('ex-fence')
    else:
        t.append('in-fence')
    return ' '.join(t)


def main(dest, A, B, T):
    out = sys.stdout if dest == '-' else open(dest, 'w', buffering=1)

    def log(s):
        out.write(s + '\n')

    R = RS.load((RS.K0, RS.R0, RS.S0))
    MG = {t: ln.line('ws%dMage' % t) for t in range(1, 13)}
    CL = CA.lines()
    F.reset()

    sigs = [s for s in SC.produce(CL, R, A, B) + SB.produce(R, MG, A, B) if s['bar'] == T]
    sigs.sort(key=lambda s: (s['side'], s['src']))

    log('# THE SIGNALS THAT LANDED ON %s. Joe 1024.' % ln.U(T))
    log('# the producers are the router\'s own; each walk is re-run through v4_fast.walk\'s events')
    log('#   hook. RULED_OK %s. the control: ws5r %s = %.2f, expected %.2f'
        % (K.RULED_OK, K.CONTROL_TS, R[5][ln.K(K.CONTROL_TS)], K.CONTROL_DB))
    log('')
    log('| the signal | side | by | its walk started | detail |')
    log('|---|---|---|---|---|')
    for s in sigs:
        log('| %s | %s | %s | %s | %s |'
            % (ln.U(s['bar']), 'HIGH' if s['side'] > 0 else 'LOW', s['mech'],
               ln.U(s['src']), s['why']))

    for s in sigs:
        ev = []
        stf = None
        if s['mech'] == 'core':
            w = CA.armed_at(CL, s['src'], s['side'])
            stf = K.CORE_LIN_ENTRY_TF if w == 'arm2' else CA.start_tf(CL, s['src'], s['side'])
        else:
            r = K.walkable_run(R, int(s['why'].split('fire ')[1][:19] and ln.K(
                s['why'].split('fire ')[1][:19])), s['side'])
            stf = r[0] if r else None
        if stf is None:
            continue
        v, exh = F.walk(R, stf, s['side'], s['src'], B, events=ev)
        log('')
        log('## %s %s, walk from ws%d starting %s -> %s %s'
            % (s['mech'], 'HIGH' if s['side'] > 0 else 'LOW', stf, ln.U(s['src']), v,
               ln.U(exh) if exh is not None else '-'))
        log('')
        log('| the baton bar | from | to | the receiver r value | its reversal stamp | second walk |')
        log('|---|---|---|---|---|---|')
        for e in ev:
            log('| %s | ws%d | ws%d | %.2f %s | %s | %s |'
                % (ln.U(e['pas']), e['frm'], e['to'], e['r_to'],
                   _tag(e['r_to'], s['side']),
                   ln.U(e['rev_to']) if e['rev_to'] is not None else 'none',
                   ln.U(e['p2']) if e['p2'] is not None else '-'))

    #   THE 5-SECOND ROWS. Every bar from the earliest walk start to the signal bar, so the
    #   convergence is read off the lines rather than inferred from the three verdicts.
    frm = min(int(s['src']) for s in sigs)
    tfs = sorted(set([1, 2, 3, 4, 5, 6] ) & set(R))
    log('')
    log('# THE 5-SECOND ROWS, %s .. %s. r values on the SWEEP config (rsi %d, stc %d, k_len %d).'
        % (ln.U(frm), ln.U(T), RS.K0, RS.R0, RS.S0))
    #   THE TUPLE ORDER IS LEGACY AND MISLABELLED ELSEWHERE. RS.(K0, R0, S0) is (R_RSI, R_STC,
    #   R_KLEN) = (5, 8, 7), so K0 is the RSI and S0 is the k_len. out/net.md's columns say
    #   `k | rsi | stc` and hold (rsi, stc, k_len); that mislabel is live and is not fixed here.
    log('# a value is tagged against the LOW side, which is the side all these signals carry.')
    log('')
    log('| the bar | ' + ' | '.join('ws%dr' % t for t in tfs) + ' |')
    log('|---|' + '---|' * len(tfs))
    for k in range(frm, int(T) + 1):
        log('| %s | ' % ln.U(k)
            + ' | '.join('%.2f %s' % (R[t][k], _tag(R[t][k], sigs[0]['side'])) for t in tfs) + ' |')
    if dest != '-':
        out.close()


if __name__ == '__main__':
    main(sys.argv[1], ln.K(sys.argv[2]), ln.K(sys.argv[3]), ln.K(sys.argv[4]))
