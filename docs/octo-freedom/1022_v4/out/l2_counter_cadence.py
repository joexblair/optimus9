"""A MEASUREMENT, NOT A BUILD. Joe 1026, asked as a question: *"if I said 'create a cadence when
cws1b crosses to counter target-side oob (eg 08-30 1921)', when would it fire in 08-30 to 09-03 and
what would the board look like at that cadence?"*

Nothing in v4_l2_cadence or v4_lineage2 is changed. This file detects the cross and reports where it
lands inside the walks AS THEY RUN TODAY, with the full board at each bar.

THE CROSS: cws1b, CLOSED, entering the oob on the side OPPOSITE the walk's target side. oob is
15/85 always, so a HIGH-target walk watches cws1b <= 15.0 and a LOW-target walk cws1b >= 85.0.
His example lands exactly: 2026-08-30 19:21:00, cws1b 26.38 -> 14.16, inside the HIGH-target walk
that armed 18:33:00.

NO WOB. He named no dwell, so the bar reported is the raw cross bar - the first bar at or past the
fence. A wob would be a value I picked.

THE WALK DIVERGES THE MOMENT THE CADENCE ACTS. These are the bars the cadence would fire on given
today's walks; a cadence that passed a baton or exhausted would move every row after it.

usage: l2_counter_cadence.py <out|-> <start> <end> <first side: high|low>
"""
import os, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
import ln, v4_knobs as K, v4_rcfg_sweep as RS, v4_core_arm as CA
import v4_l2_proxy as PX, v4_lineage2 as L2, v4_closed_prev as CP
from v4_backstop_trades import prices

dest, A, B = sys.argv[1], ln.K(sys.argv[2]), ln.K(sys.argv[3])
first = +1 if sys.argv[4].lower().startswith('h') else -1
out = sys.stdout if dest == '-' else open(dest, 'w', buffering=1)
log = lambda s: out.write(s + '\n')
esc = lambda t: str(t).replace('|', '\\|')

E = RS.load((RS.K0, RS.R0, RS.S0))
C = CP.ladder(E)
CL = CP.arm_lines(E)
#   THE CAUSAL MAGE LADDER for the cascade, Joe 1027. Same last-closed rule as the r set.
MGL = {t: CP.line('ws%dMage' % t, t * 60) for t in range(1, 13)}
BD = PX.Board(C, E, MG=MGL)
close, _h, _l = prices()
b1 = np.asarray(CL['b'], float)


def crosses(side, frm, to):
    """cws1b entering the oob COUNTER to `side`, between frm and to inclusive. -> [bar]."""
    m = K.oob_mask(b1, -int(side))
    cr = np.flatnonzero(m[1:] & ~m[:-1]) + 1
    return [int(x) for x in cr if int(frm) <= x <= int(to)]


walks, side, frm = [], first, A
while frm < B:
    v, bar, rows = L2.walk(CL, BD, close, side, frm, B)
    walks.append({'frm': frm, 'side': side, 'v': v, 'bar': bar, 'rows': rows})
    if bar is None:
        break
    frm, side = int(bar) + 1, -side

log('# cws1b CROSSING TO THE COUNTER TARGET-SIDE OOB - where it lands in the walks. %s .. %s,'
    % (ln.U(A), ln.U(B)))
log('#   first side %s. A MEASUREMENT: no cadence is built, nothing in the walk is changed.'
    % ('HIGH' if first > 0 else 'LOW'))
log('# the cross: cws1b CLOSED entering oob %.0f/%.0f on the side opposite the target. No wob.'
    % (K.OOB_LO, K.OOB_HI))
log('# L2_T3_ON %d | L2_LIN_HOP %d | L2_MOM_MAXTF %d | ex-fence %.0f/%.0f | RULED_OK %s'
    % (K.L2_T3_ON, K.L2_LIN_HOP, K.L2_MOM_MAXTF, 100.0 - K.RMOM_FNC, K.RMOM_FNC, K.RULED_OK))
log('# the control: ws5r %s = %.2f, expected %.2f'
    % (K.CONTROL_TS, E[5][ln.K(K.CONTROL_TS)], K.CONTROL_DB))
log('')

#   THE ARM IS THE FLOOR. A cadence before the arm has no rider and no walk to act on, which is the
#   same floor t1/t2/t3 already use in the walk.
fires = []
for w in walks:
    arm = [r for r in w['rows'] if r['stage'] == 'ARM']
    if not arm or w['bar'] is None:
        continue
    a0, e0 = int(arm[0]['bar']), int(w['bar'])
    for k in crosses(w['side'], a0, e0):
        rider = None
        for r in w['rows']:
            if r['bar'] is None or int(r['bar']) > k:
                continue
            if 'to' in r:
                rider = int(r['to'])
            elif r.get('rider') is not None:
                rider = int(r['rider'])
        fires.append({'bar': k, 'w': w, 'arm': a0, 'exh': e0, 'rider': rider})

log('| the read | value |')
log('|---|---|')
log('| walks in the window | %d |' % len(walks))
log('| walks that armed and exhausted | %d |'
    % sum(1 for w in walks if w['bar'] is not None
          and any(r['stage'] == 'ARM' for r in w['rows'])))
log('| cadence firings, arm..exhaust | %d |' % len(fires))
log('| walks with at least one firing | %d |' % len(set(id(f['w']) for f in fires)))
log('| firings with no rider | %d |' % sum(1 for f in fires if f['rider'] is None))
log('')

#   `last` is what the walk measures a reversal since. It advances on the rows that set it in the
#   walk - BATON, HOLD, a rider pickup, NO RIDER - and starts at the arm.
_SETS_LAST = ('BATON', 'HOLD', 'RIDER', 'NO RIDER', 'NO PASS')
for f in fires:
    lb = [int(r['bar']) for r in f['w']['rows']
          if r['bar'] is not None and r['stage'] in _SETS_LAST and int(r['bar']) <= f['bar']]
    f['last'] = max(lb) if lb else f['arm']

log('| the cadence bar | the walk armed | target side | cws1b closed | the rider | the rider r |'
    ' rider ex-fence | rider oob | rider reversed since %s | candidates on the whole board |'
    ' candidates inside lin_hop %d | what the cadence would do | the walk exhausts today |'
    % ('the last decision', K.L2_LIN_HOP))
log('|---|---|---|---|---|---|---|---|---|---|---|---|---|')
tally = {}
for f in fires:
    sd, rd = f['w']['side'], f['rider']
    hop = None if rd is None else rd + int(K.L2_LIN_HOP)
    brd = L2.candidates(BD, sd, f['bar'], rd) if rd is not None else []
    cap = L2.candidates(BD, sd, f['bar'], rd, cap=hop) if rd is not None else []
    rv = BD.value(rd, f['bar']) if rd is not None else float('nan')
    exf = BD.ex_fence(rd, f['bar'], sd) if rd is not None else False
    oob = BD.oob(rd, f['bar'], sd) if rd is not None else False
    revd = BD.reversed_in(rd, sd, f['last'], f['bar']) if rd is not None else False
    #   THE SAME VERDICT RULE THE WALK ALREADY USES at a cadence. Which cap a NEW cadence reads is
    #   unruled, so both arms are printed; the verdict below uses the whole board.
    if brd:
        did = 'BATON -> ws%d' % max(brd)
    elif oob:
        did = 'HOLD - the rider is oob'
    elif exf and not revd:
        did = 'HOLD - ex-fence and not reversed'
    elif revd and not oob:
        did = 'EXHAUST, t4 tag'
    else:
        did = 'EXHAUST'
    f['did'] = did
    tally[did.split(' -')[0].split(',')[0]] = tally.get(did.split(' -')[0].split(',')[0], 0) + 1
    log('| %s | %s | %s | %.2f | %s | %.2f | %s | %s | %s | %s | %s | %s | %s |'
        % (ln.U(f['bar']), ln.U(f['arm']), 'HIGH' if sd > 0 else 'LOW', b1[f['bar']],
           'cws%d' % rd if rd is not None else 'none', rv,
           'yes' if exf else 'no', 'yes' if oob else 'no', 'yes' if revd else 'no',
           ', '.join('ws%d' % t for t in brd) or 'none',
           ', '.join('ws%d' % t for t in cap) or 'none', did, ln.U(f['exh'])))
log('')
log('| what the cadence would do | firings |')
log('|---|---|')
for k2 in sorted(tally):
    log('| %s | %d |' % (k2, tally[k2]))
log('')
log('| the read | value |')
log('|---|---|')
_e = [f for f in fires if f['did'].startswith('EXHAUST')]
log('| firings that would EXHAUST the walk | %d |' % len(_e))
log('| of those, earlier than the walk exhausts today | %d |'
    % sum(1 for f in _e if f['bar'] < f['exh']))
if _e:
    _d = sorted((f['exh'] - f['bar']) * 5 for f in _e)
    log('| median seconds earlier | %d |' % _d[len(_d) // 2])
    log('| the largest, seconds earlier | %d |' % _d[-1])

for f in fires:
    sd, rd, k = f['w']['side'], f['rider'], f['bar']
    hop = None if rd is None else rd + int(K.L2_LIN_HOP)
    log('')
    log('## %s - the board, target side %s, rider %s, cws1b %.2f'
        % (ln.U(k), 'HIGH' if sd > 0 else 'LOW',
           'cws%d' % rd if rd is not None else 'none', b1[k]))
    log('')
    log('| the rung | cws{TF}r closed | ex-fence | oob | towards the side | above the rider |'
        ' inside lin_hop | a candidate |')
    log('|---|---|---|---|---|---|---|---|')
    for t in range(1, int(K.L2_MOM_MAXTF) + 1):
        if t not in BD.tfs:
            continue
        exf = BD.ex_fence(t, k, sd)
        tw = L2.towards(BD, t, k, sd)
        ab = rd is not None and t > rd
        ih = hop is not None and t <= hop
        log('| ws%d | %.2f | %s | %s | %s | %s | %s | %s |'
            % (t, BD.value(t, k), 'yes' if exf else 'no', 'yes' if BD.oob(t, k, sd) else 'no',
               'yes' if tw else 'no', 'yes' if ab else 'no', 'yes' if ih else 'no',
               'yes' if (exf and tw and ab and ih) else 'no'))
if dest != '-':
    out.close()
