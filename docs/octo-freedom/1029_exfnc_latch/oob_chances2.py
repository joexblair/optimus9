"""THE oob LATCH'S CHANCES, USING THE WALK'S OWN REVERSAL WINDOW.

MY FIRST SCAN OVERCOUNTED. It asked whether the rider had reversed since the LEG OPENED. The walk
asks whether it reversed since the PREVIOUS cadence it evaluated - `reversed_in(rider, side, last,
bar)`, where `last` moves forward at every bar the walk acts on. The wider window reported 34 of 39
cadence bars as reversed and 22 chances, while the A/B over the same day came out identical on
every figure. The A/B is the authority; the scan was wrong.

THIS READS THE WALK'S OWN VALUE. The cadence row already prints it: *"rider cws{n} {v},
no-longer-exfence {yes/no}, reversed {yes/no}"*. So the walk is run once and its own rows are
parsed - no second copy of the rule.

A CHANCE is a cadence row where the walk says reversed yes AND the two oob reads disagree.
"""
import os, sys, io, re, time
import numpy as np
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln, v4_knobs as K, v4_rcfg_sweep as RS
import v4_live_lines as LL, v4_l2_proxy as PX, v4_chain as CH
import v4_signal as SG, v4_sig_lin2_reentry as L2R
from v4_backstop_trades import prices
sys.stderr = _e
T0 = time.time()

close, phi, plo = prices()
E = RS.load((RS.K0, RS.R0, RS.S0))
CL = LL.arm_lines(E); MG = LL.mage(12)
B1 = np.asarray(CL['b'], float)
SIG = [g for g in L2R.signals(B1, MG) if g['bar'] == ln.K('2026-08-29 23:53:50')]
assert len(SIG) == 1
OPEN_DIR = SG.direction(int(SIG[0]['side']))
OPEN = (SG.fire_bar(SIG[0]), SG.target_side(OPEN_DIR))
ALLSIG = L2R.signals(B1, MG)
RX = re.compile(r'rider cws(\d+) ([-\d.]+), no-longer-exfence (yes|no), reversed (yes|no)')

print('# THE oob LATCH\'S CHANCES, ON THE WALK\'S OWN REVERSAL WINDOW')
print('# the walk asks whether the rider reversed since the PREVIOUS cadence it acted on.')
print('# my first scan asked since the LEG OPENED, which overcounted - it said 22 chances while')
print('#   the A/B over the same day was identical on every figure.')
print('# the value below is the walk\'s own, parsed from its cadence row.')
print('')


def scan(A, B, label, per_row):
    K.LIN2_LATCH_OOB_ON = 0
    bd = PX.Board(E, E, MG=MG, MGE=MG, PS=None)
    lg, zero, op = CH.legs(CL, bd, close, phi, plo, A, B, MG=MG, B1=B1, open_at=OPEN,
                           resig=ALLSIG)
    rows, n_cad, n_rev, n_dis, n_ch = [], 0, 0, 0, 0
    for i, x in enumerate(lg, 1):
        side = x['side']
        for r in x['rows']:
            b = r.get('bar')
            if b is None or r['stage'] != 'CADENCE':
                continue
            m = RX.search(str(r['why']))
            if not m:
                continue
            rd, rv, noex, rev = int(m.group(1)), float(m.group(2)), m.group(3), m.group(4)
            n_cad += 1
            revd = rev == 'yes'
            K.LIN2_LATCH_OOB_ON = 0
            ov = bool(bd.baton_oob(rd, b, side))
            K.LIN2_LATCH_OOB_ON = 1
            od = bool(bd.baton_oob(rd, b, side))
            K.LIN2_LATCH_OOB_ON = 0
            if revd:
                n_rev += 1
            if ov != od:
                n_dis += 1
            ch = revd and ov != od
            if ch:
                n_ch += 1
            rows.append((i, b, rd, rv, noex, revd, ov, od, ch))
    print('## %s' % label)
    print('')
    if per_row:
        print('| leg | the cadence bar | the rider | its value | no longer ex-fence? |'
              ' reversed, per the walk | oob by value | oob at depth | A CHANCE? |')
        print('|---|---|---|---|---|---|---|---|---|')
        for i, b, rd, rv, noex, revd, ov, od, ch in rows:
            print('| %d | %s | ws%d | %.2f | %s | %s | %s | %s | %s |'
                  % (i, ln.U(b), rd, rv, noex, 'YES' if revd else 'no',
                     'yes' if ov else 'no', 'yes' if od else 'no', 'YES' if ch else 'no'))
        if not rows:
            print('| - | no cadence row with a rider in this window | | | | | | | |')
        print('')
    print('| the read | value |')
    print('|---|---|')
    print('| legs walked | %d |' % len(lg))
    print('| cadence rows with a rider | %d |' % n_cad)
    print('| of those, the walk says the rider reversed | %d |' % n_rev)
    print('| of those, the two oob reads disagree | %d |' % n_dis)
    print('| CHANCES - reversed AND the reads disagree | **%d** |' % n_ch)
    print('')
    return n_ch, n_cad


c1, t1 = scan(ln.K('2026-08-30 00:00:00'), ln.K('2026-08-30 23:59:55'),
              '2026-08-30, every cadence row', True)
c2, t2 = scan(ln.K('2026-08-30 00:00:00'), ln.K('2026-09-06 23:59:55'),
              '2026-08-30 to 09-06, the counts only', False)
print('| the read | value |')
print('|---|---|')
print('| chances on 2026-08-30, out of %d cadence rows | %d |' % (t1, c1))
print('| chances over 2026-08-30 to 09-06, out of %d | %d |' % (t2, c2))
print('| does the A/B result agree | %s |'
      % ('yes - 0 chances on 08-30 is why the two arms came out identical' if c1 == 0
         else 'NO - %d chances on 08-30 yet the A/B was identical. Something else is wrong.' % c1))
print('| the wider A/B | %s |'
      % ('is worth running - the mech has %d chances there' % c2 if c2 > 0
         else 'cannot test the mech - no chances in that window either'))
print('| seconds to compute | %.1f |' % (time.time() - T0))
