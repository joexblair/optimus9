"""lineage2 chained across days, to count t3 firings. Joe 1026: *"can you see it anywhere in 08-30
to 09-03?"*

A walk's t3 depends on its rider, which depends on the walk, so t3 cannot be scanned without
walking. The chain is his own rev-trade shape: walk to EXHAUST, flip the side, start the next walk
at exhaust + 1.

THE FIRST SIDE IS AN INPUT, not a derivation - there is no trade open before the first walk. Both
are run so the choice cannot carry the answer.

EXPLAIN MODE. Joe 1026: *"at 08-30 1512, do you see any baton-pass candidates? are any of these
timestamps able to pass the baton?"* Extra arguments are bars to open up. For each, the chain finds
the walk that contains it, the rider the walk held there, and prints the per-TF candidate scan -
the two tests the spec names, `ex v4mom-fnc` and `towards`, one row per rung, plus whether the rung
is reachable under lin_hop. Nothing is recomputed outside the walk: the rider and the side come
from the chain's own rows.

usage: l2_chain.py <start> <end> ['YYYY-MM-DD HH:MM:SS' ...]
"""
import os, sys, time, collections
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
import ln, v4_knobs as K, v4_rcfg_sweep as RS, v4_core_arm as CA, v4_l2_proxy as PX, v4_lineage2 as L2, v4_closed_prev as CP
import v4_sweep_pivots as SP
import numpy as np
from v4_backstop_trades import prices

A, B = ln.K(sys.argv[1]), ln.K(sys.argv[2])
WANT = [ln.K(x) for x in sys.argv[3:]]
#   THE RUNG-BY-RUNG TABLE IS 12 ROWS PER BAR, so it is printed only for the bars named in
#   L2_DEEP. Every requested bar still gets its summary row on both chains.
DEEP = [ln.K(x) for x in os.environ.get('L2_DEEP', '').split(',') if x.strip()]
E = RS.load((RS.K0, RS.R0, RS.S0)); C = CP.ladder(E)
#   THE CAUSAL MAGE LADDER for the cascade, Joe 1027. Same last-closed rule as the r set.
MGL = {t: CP.line('ws%dMage' % t, t * 60) for t in range(1, 13)}
#   THE EMERGING MAGE LADDER for the barrage's ws1Mage oob->ib cross, 1027. The closed
#   one stays the cascade's; the proxy owns which read answers which question.
MGE = {t: ln.line('ws%dMage' % t) for t in range(1, 13)}
BD = PX.Board(C, E, MG=MGL, MGE=MGE); CL = CP.arm_lines(E)
close, PHI, PLO = prices()


def esc(t):
    """A cell's own pipes escaped. The CADENCE `why` carries a literal '|' between the cadence
    and the rider, which splits the markdown cell it is printed in."""
    return str(t).replace('|', '\\|')

print('# lineage2 chained, %s .. %s' % (ln.U(A), ln.U(B)))
print('# t3 needs max(%d, round(%s x the ex-fence population)) reversals, matryoshka ws7..rider-1'
      % (K.L2_T3_MIN_MATRY, K.L2_T3_FRAC))
print('# gate %s | lin_hop %d lifted only at t1/t2 | RULED_OK %s'
      % (BD.gate_mode(), K.L2_LIN_HOP, K.RULED_OK))

for first in (+1, -1):
    t0 = time.time()
    walks, rows_all, side, frm = [], [], first, A
    while frm < B:
        v, bar, rows = L2.walk(CL, BD, close, side, frm, B)
        walks.append((frm, side, v, bar, rows))
        rows_all += [(side, r) for r in rows]
        if bar is None:
            break
        frm, side = int(bar) + 1, -side
    el = time.time() - t0
    cad = collections.Counter()
    for sd, r in rows_all:
        if r['stage'] in ('CADENCE', 'RIDER', 'NO RIDER') and r['why'][:2] in ('t1', 't2', 't3'):
            cad[r['why'][:2]] += 1
        if r['stage'] in ('CADENCE', 'RIDER', 'NO RIDER', 'EXHAUST') and r['why'][:5] == 'latch':
            cad['la'] += 1
    print('')
    print('## first side %s  (%.1fs)' % ('HIGH' if first > 0 else 'LOW', el))
    print('')
    print('| the read | value |'); print('|---|---|')
    print('| walks | %d |' % len(walks))
    print('| verdicts EXHAUST | %d |' % sum(1 for w in walks if w[2] == 'EXHAUST'))
    print('| verdicts NO ARM | %d |' % sum(1 for w in walks if w[2] == 'NO ARM'))
    print('| verdicts NO VERDICT | %d |' % sum(1 for w in walks if w[2] == 'NO VERDICT'))
    print('| verdicts DIV REV-TRADE | %d |' % sum(1 for w in walks if w[2] == 'DIV REV-TRADE'))
    for ty in ('t1', 't2', 't3'):
        print('| %s cadence events | %d |' % (ty, cad.get(ty, 0)))
    #   v4-arm-lineage-retest: one RETEST row per armed walk, so the three outcomes partition them.
    rt = [(sd, r) for sd, r in rows_all if r['stage'] == 'RETEST']
    print('| walks that reached a RETEST row | %d |' % len(rt))
    print('|   the gate shut, cws1r not oob at the arm | %d |'
          % sum(1 for _s, r in rt if 'is not oob' in r['why']))
    print('|   the gate shut, cws2r/cws3r not both in the fence | %d |'
          % sum(1 for _s, r in rt if 'not both inside' in r['why']))
    print('|   the gate opened | %d |' % sum(1 for _s, r in rt if 'the gate opens' in r['why']))
    print('|   the gate opened, no oob->ib cross to the data end | %d |'
          % sum(1 for _s, r in rt if 'no cws1r oob->ib' in r['why']))
    rtr = [(sd, r) for sd, r in rows_all if r.get('ctype') == 'retest']
    print('| the gate cadence ENDED the walk | %d |'
          % sum(1 for _s, r in rtr if r['stage'] == 'EXHAUST'))
    print('| the gate cadence RE-SCANNED a rider | %d |'
          % sum(1 for _s, r in rtr if r['stage'] == 'RIDER'))
    print('| BATON passes | %d |' % sum(1 for _s, r in rows_all if r['stage'] == 'BATON'))
    print('| LATCH1 armed | %d |' % sum(1 for _s, r in rows_all if r['stage'] == 'LATCH1'))
    print('| cadences taking NO ACTION on the mage-cascade | %d |'
          % sum(1 for _s, r in rows_all if r['stage'] == 'NO ACTION'))
    print('| latch cadence events | %d |' % cad.get('la', 0))
    print('| cws1b counter-oob cadence events | %d |'
          % sum(1 for _s, r in rows_all
                if r['stage'] in ('CADENCE', 'RIDER', 'NO RIDER', 'EXHAUST')
                and 'cws1b counter-oob' in r['why']))
    #   THE DIV BRANCH, by what anchor_floater actually said - PM separated from no reading
    dv = [r for _s, r in rows_all if r['stage'] == 'DIV']
    NAMES = {1: 'a divergence, SHORT', -1: 'a divergence, LONG', 2: 'PM, trend SHORT',
             -2: 'PM, trend LONG', 0: 'inside AF_SLOPE_FLOOR', None: 'no reading'}
    print('')
    if dv:
        print('| the DIV branch read | arms |'); print('|---|---|')
        import collections as _c
        tal = _c.Counter(r.get('state') for r in dv)
        for k2 in (1, -1, 2, -2, 0, None):
            if k2 in tal:
                print('| %s | %d |' % (NAMES[k2], tal[k2]))
        print('| all DIV arms | %d |' % len(dv))
        print('|   of those, a REV-TRADE verdict | %d |'
              % sum(1 for w in walks if w[2] == 'DIV REV-TRADE'))
    if rtr:
        print('')
        print('| the gate cadence | side | what it did | why |')
        print('|---|---|---|---|')
        for sd, r in rtr:
            print('| %s | %s | %s | %s |' % (ln.U(r['bar']), 'HIGH' if sd > 0 else 'LOW',
                                             r['stage'], esc(r['why'])))
    #   THE REV-TRADES, Joe 1027: *"I'll wait for the actual rev-trade timestamps, and the
    #   timestamps that created them"*. The chain's rev-trade IS the exhaust: walk N carrying target
    #   side S exhausts at bar E, the open trade closes, and the opposite side opens at E + 1. So
    #   trade N spans [the previous exhaust + 1, this exhaust + 1] and its direction is LONG when S
    #   is HIGH - the banked `v4_signal.target_side` reading, a LONG hunts the HIGH oob.
    print('')
    print('## THE REV-TRADES, and the bars that created each one')
    print('')
    #   SWEEP-PIVOTS ON EVERY REV-TRADE, Joe 1027: *"add sweep-pivots maemfe columns"*.
    #   MAE / MFE run the trade's own span, entry to close. The sweep-pivot leg is the SCALE, not
    #   the exit: `given %` is the favourable move already behind at the exhaust bar, `leg MFE %` is
    #   the pivot-to-leg-end excursion, and `share` is given / leg.
    #   SP.swing's `side` IS THE OOB SIDE THE LEG LEFT and its favourable direction is -side, so a
    #   LONG (target side HIGH, +1) is passed -1. Same mapping v4_reentry's scoring used.
    #   MARKDOWN, his 1011 banked format. The box-drawn version he pasted on 1027 was his own
    #   copy of THIS table - *"that was my copy paste of your dynamic table. no table changes are
    #   required"* - so nothing about the drawing moves.
    print('| # | the open | dir | the arm | the cadence that ended it |'
          ' the exhaust = the rev-trade bar | the verdict |'
          ' MAE % | MFE % | capped | SP TF | the pivot | leg MFE % | ended by |')
    print('#   THE EXHAUST BAR *IS* THE REV-TRADE BAR. An exhaust is only ever declared at a')
    print('#   cadence event bar, so every bar in that column is a cadence bar. The trade closes')
    print('#   there and the opposite side opens at that bar + 1, which is the NEXT row\'s open.')
    print('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
    trades = []
    sprows = []
    prev = int(A)
    for n, (frm0, sd, v, bar, rows) in enumerate(walks, 1):
        if bar is None:
            continue
        arm = [r for r in rows if r['stage'] == 'ARM']
        ex = [r for r in rows if r['stage'] == 'EXHAUST']
        ctype = (ex[0].get('ctype') or '-') if ex else '-'
        if ex and ctype == '-':
            w = ex[0]['why']
            for name in ('t1', 't2', 't3', 't4', 'latch', 'cws1b counter-oob', 'retest',
                         'barrage'):
                if name in w:
                    ctype = name
                    break
        trades.append((n, prev + 1, sd, bar, rows))
        en, cl = int(prev) + 1, int(bar) + 1
        d = 1 if sd > 0 else -1
        p0 = float(close[en])
        hh = float(np.nanmax(PHI[en:cl + 1])); ll = float(np.nanmin(PLO[en:cl + 1]))
        mfe = ((hh - p0) if d > 0 else (p0 - ll)) / p0 * 100.0
        mae = ((ll - p0) if d > 0 else (p0 - hh)) / p0 * 100.0
        sw = SP.swing(int(bar), -int(sd), close)
        #   HIS CAP, 1027: *"if MAE > 1.1, cap mae at 1.1 and print 0 in mfe"*. The trade would have
        #   been closed at the cap, so it never reached its favourable excursion. REPORT ONLY.
        cap = float(K.LIN2_MAE_CAP)
        capped = abs(mae) > cap
        if capped:
            mae, mfe = -cap, 0.0
        #   WHICH BRANCH ENDED IT: a mage-cascade mismatch, or the cadence's own board review.
        mm = [r for r in rows if r['stage'] == 'EXHAUST' and r.get('mismatch')]
        #   WHICH MECH ENDED IT. The barrage is its own cadence type and its own exhaust branch,
        #   so it is named rather than folded into the board review.
        if ctype == 'barrage':
            endby = 'the barrage'
        elif mm:
            endby = 'the mage-cascade mismatch'
        else:
            endby = 'the board review'
        _no_sp = sw is None or sw.get('close') is None
        print('| %d | %s | %s | %s | %s | %s | %s | %+.3f | %+.3f | %s | %s | %s | %s | %s |'
              % (n, ln.U(prev + 1), 'LONG' if sd > 0 else 'SHORT',
                 ln.U(arm[0]['bar']) if arm and arm[0]['bar'] is not None else 'no arm',
                 ctype, ln.U(bar), v, mae, mfe, 'YES' if capped else '-',
                 '-' if _no_sp else sw['tf'],
                 'no sweep-pivot scale' if _no_sp else ln.U(int(sw['pivot'])),
                 '-' if _no_sp else '%.3f' % sw['mfe_pct'],
                 endby))
        sprows.append((mae, mfe, None if sw is None else sw.get('share'), capped, bool(mm),
                       ctype))
        prev = int(bar)
    if sprows:
        M = [r[0] for r in sprows]; F = [r[1] for r in sprows]
        sh = [r[2] for r in sprows if r[2] is not None]
        print('')
        print('| the read | value |'); print('|---|---|')
        print('| trades capped at MAE %.2f%% | %d of %d |'
              % (float(K.LIN2_MAE_CAP), sum(1 for r in sprows if r[3]), len(sprows)))
        print('| ended by a mage-cascade mismatch | %d |' % sum(1 for r in sprows if r[4]))
        print('| ended by the barrage | %d |' % sum(1 for r in sprows if r[5] == 'barrage'))
        print('| ended by the cadence board review | %d |'
              % sum(1 for r in sprows if not r[4] and r[5] != 'barrage'))
        print('| the mismatch action | %s |' % K.LIN2_MISMATCH_ACTION)
        print('')
        print('| the read | value |'); print('|---|---|')
        print('| rev-trades | %d |' % len(sprows))
        print('| sum MAE %% | %+.3f |' % sum(M)); print('| sum MFE %% | %+.3f |' % sum(F))
        print('| median MAE %% | %+.3f |' % sorted(M)[len(M) // 2])
        print('| median MFE %% | %+.3f |' % sorted(F)[len(F) // 2])
        print('| worst MAE %% | %+.3f |' % min(M)); print('| best MFE %% | %+.3f |' % max(F))
        print('| MFE > abs(MAE) | %d of %d |'
              % (sum(1 for r in sprows if r[1] > abs(r[0])), len(sprows)))
        print('| sweep-pivot knobs | %s |'
              % ', '.join('%s %s' % (n5, v5) for n5, v5, _d in SP.knobs()))

    #   EVERY LATCH 1 FIRE, one per row, Joe 1027: *"when you show me the updated trade chain,
    #   highlight when this latch 1 fires"*. It arms on EVERY cadence bar whose divergence state
    #   opposes the target side, including the bars where the cadence itself takes no action - that
    #   last part is a reading of MINE, not his.
    l1all = [(n, sd, r) for n, _op, sd, _b, rows in trades
             for r in rows if r['stage'] == 'LATCH1']
    print('')
    if not l1all:
        print('NO LATCH 1 FIRE in the window.')
    else:
        print('| the latch 1 bar | trade | dir | rider | the cadence it armed on | the state |')
        print('|---|---|---|---|---|---|')
        for n, sd, r in l1all:
            w = r['why']
            cad = w.split(' cadence')[0].replace('latch 1 at the ', '') if ' cadence' in w else '-'
            st = w.split('divergence state ')[-1] if 'divergence state ' in w else '-'
            print('| %s | %d | %s | %s | %s | %s |'
                  % (ln.U(r['bar']), n, 'LONG' if sd > 0 else 'SHORT',
                     ('cws%d' % r['rider']) if r.get('rider') else '-', cad, st))

    for n, op, sd, bar, rows in trades:
        print('')
        print('### trade %d - %s %s, every bar that made it' % (n, ln.U(op),
                                                                'LONG' if sd > 0 else 'SHORT'))
        print('')
        print('| the bar | stage | rider | why |')
        print('|---|---|---|---|')
        for r in rows:
            print('| %s | %s | %s | %s |'
                  % (ln.U(r['bar']) if r['bar'] is not None else '-', r['stage'],
                     ('cws%d' % r['rider']) if r.get('rider') else '-', esc(r['why'])))

    #   TASK 27 NEEDS THE ROWS, not the counts: every latch-1 arm, every latch cadence, and every
    #   cws1b counter-oob cadence, so each mech can be validated where it fired.
    for lab, pick in (
            ('LATCH 1 armed', lambda r: r['stage'] == 'LATCH1'),
            ('the LATCH cadence', lambda r: r['why'][:5] == 'latch'),
            ('the cws1b counter-oob cadence', lambda r: 'cws1b counter-oob' in r['why'])):
        rows = [(sd, r) for sd, r in rows_all if pick(r)]
        print('')
        if not rows:
            print('NO %s in the window.' % lab)
            continue
        print('| %s | side | rider | stage | why |' % lab)
        print('|---|---|---|---|---|')
        for sd, r in rows:
            print('| %s | %s | %s | %s | %s |'
                  % (ln.U(r['bar']) if r['bar'] is not None else '-',
                     'HIGH' if sd > 0 else 'LOW',
                     ('cws%d' % r['rider']) if r.get('rider') else '-',
                     r['stage'], esc(r['why'])))

    t3rows = [(sd, r) for sd, r in rows_all if r['why'][:2] == 't3']
    print('')
    if t3rows:
        print('| the t3 bar | side | stage | why |'); print('|---|---|---|---|')
        for sd, r in t3rows:
            print('| %s | %s | %s | %s |' % (ln.U(r['bar']), 'HIGH' if sd > 0 else 'LOW',
                                             r['stage'], esc(r['why'])))
    else:
        print('NO t3 EVENT in the window.')

    if not WANT:
        continue
    print('')
    print('## the baton-pass candidates at the bars Joe named, first side %s'
          % ('HIGH' if first > 0 else 'LOW'))
    print('')
    print('| the bar | the walk | side | the rider | the rows the walk wrote there | '
          'candidates inside lin_hop %d | candidates on the whole board |' % K.L2_LIN_HOP)
    print('|---|---|---|---|---|---|---|')
    deep = []
    for w in WANT:
        hit = [x for x in walks if x[0] <= w and (x[3] is None or w <= x[3])]
        if not hit:
            print('| %s | - | - | - | no walk covers this bar | - | - |' % ln.U(w))
            continue
        frm0, sd, _v, _bar, rows = hit[0]
        rider = None
        for r in rows:
            if r['bar'] is None or int(r['bar']) > w:
                continue
            if 'to' in r:
                rider = int(r['to'])
            elif r.get('rider') is not None:
                rider = int(r['rider'])
        here = [r for r in rows if r['bar'] is not None and int(r['bar']) == w]
        #   THE RIDER AT THE DECISION, not after it. The reconstruction above walks the rows and
        #   takes `to` when a BATON fired, which is the rider the walk held AFTER the pass - so a
        #   bar whose cadence passed the baton came back with no candidates above the new rider.
        #   When the walk wrote a CADENCE row at this bar, that row's own rider is the answer.
        cad_here = [r for r in here if r['stage'] in ('CADENCE', 'EXHAUST')
                    and r.get('rider') is not None]
        if cad_here:
            rider = int(cad_here[0]['rider'])
        hop = None if rider is None else rider + int(K.L2_LIN_HOP)
        cap = L2.candidates(BD, sd, w, rider or 0, cap=hop) if rider is not None else []
        board = L2.candidates(BD, sd, w, rider or 0) if rider is not None else []
        print('| %s | %s | %s | %s | %s | %s | %s |'
              % (ln.U(w), ln.U(frm0), 'HIGH' if sd > 0 else 'LOW',
                 'cws%d' % rider if rider is not None else 'none',
                 esc('; '.join('%s %s' % (r['stage'], r['why']) for r in here)) or 'none',
                 ', '.join('ws%d' % t for t in cap) or 'none',
                 ', '.join('ws%d' % t for t in board) or 'none'))
        if w in DEEP:
            deep.append((w, sd, rider, hop))
    for w, sd, rider, hop in deep:
        print('')
        print('### %s - every rung, side %s, rider %s'
              % (ln.U(w), 'HIGH' if sd > 0 else 'LOW',
                 'cws%d' % rider if rider is not None else 'none'))
        print('')
        print('| the rung | cws{TF}r closed | ex-fence %.0f/%.0f | towards the side | above the '
              'rider | inside lin_hop | a candidate |'
              % (100.0 - K.RMOM_FNC, K.RMOM_FNC))
        print('|---|---|---|---|---|---|---|')
        for t in range(1, int(K.L2_MOM_MAXTF) + 1):
            if t not in BD.tfs:
                continue
            exf = BD.ex_fence(t, w, sd)
            tw = L2.towards(BD, t, w, sd)
            ab = rider is not None and t > rider
            ih = hop is not None and t <= hop
            print('| ws%d | %.2f | %s | %s | %s | %s | %s |'
                  % (t, BD.value(t, w), 'yes' if exf else 'no', 'yes' if tw else 'no',
                     'yes' if ab else 'no', 'yes' if ih else 'no',
                     'yes' if (exf and tw and ab and ih) else 'no'))
