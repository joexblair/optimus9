"""THE 2-DAY CHAIN ON HIS ARM 4: fence 75/25, ladder ws1..ws20, the latch released on lift-off.

Joe 1030, picking one arm out of the four: *"do this only / 4 / 75/25 / ws1..ws20 / the line's own
lift-off / -start on 2026-08-29 23:53:55 SHORT, handed in / -print the chain for 2 days: 08-30 and
08-31 / -show me these legs as timestamped row tables: 08-30 legs 2,4,6 and 08-31 legs 2,4,6 / no
stats, just the walks and the chain summary"*.

    W_V4_RMOM_FNC=75 W_V4_L2_MOM_MAXTF=20 W_V4_LIN2_EXFNC_LATCH_REL=lift W_V4_EXPERIMENT=1

All three are off the bank, so the run is an experiment and v4_knobs prints its own deltas. The
machine's defaults are untouched.

THE OPEN IS HANDED IN, his instruction. The side is NOT derived from price: it comes through the
signal layer's own two conversions off the lin2-reentry signal at 2026-08-29 23:53:50, the same
path legs_live.py and the week A/B use.

LEGS ARE NUMBERED PER DAY, by the day each leg's own open falls on - that is how he asked for them.
"""
import io
import os
import sys
import time

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import v4_knobs as K
import v4_rcfg_sweep as RS
import v4_live_lines as LL
import v4_l2_proxy as PX
import v4_l2_cadence as CAD
import v4_chain as CH
import v4_signal as SG
import v4_sig_lin2_reentry as L2R
import ln
from v4_backstop_trades import prices
sys.stderr = _e

T0 = time.time()
K.LIN2_PSEUDO_MIN_TF = 99          # pseudo-closed is not in this arm - his 1029 bank
K.LIN2_LATCH_EXFNC_ON = 1          # the per-line ex-fence latch is ON
K.LIN2_B1_HOLD = 0                 # *"let's use wob 0 until we sweep"*

A, B = ln.K('2026-08-30 00:00:00'), ln.K('2026-08-31 23:59:55')
close, phi, plo = prices()
E = RS.load((RS.K0, RS.R0, RS.S0))
CL = LL.arm_lines(E)
MG = LL.mage()                     # ws1..ws{L2_MOM_MAXTF}
B1 = np.asarray(CL['b'], float)
BD = PX.Board(E, E, MG=MG, MGE=MG, PS=None)
assert max(MG) == int(K.L2_MOM_MAXTF), 'the Mage ladder top does not match the knob'

SIG = [g for g in L2R.signals(B1, MG) if g['bar'] == ln.K('2026-08-29 23:53:50')]
assert len(SIG) == 1, ('the 23:53:50 lin2-reentry signal is not in the list at this ladder -'
                       ' %d matches' % len(SIG))
OPEN_DIR = SG.direction(int(SIG[0]['side']))
OPEN = (SG.fire_bar(SIG[0]), SG.target_side(OPEN_DIR))
assert ln.U(OPEN[0]) == '2026-08-29 23:53:55', 'the handed-in open moved: %s' % ln.U(OPEN[0])

lg, zero, op = CH.legs(CL, BD, close, phi, plo, A, B, MG=MG, B1=B1, open_at=OPEN)

#   ── the report's columns, his format ───────────────────────────────────────────────────────
CADENCE_TYPES = ('t1', 't2', 'barrage', 'ws1b counter-oob', 'retest')
BARR = {sd: sorted(int(r[0]) for r in CAD.barrage(BD, sd, 0, len(close) - 1)) for sd in (-1, +1)}


def tag(tf):
    #   NO 'cws' PREFIX. Joe 1030: *"cws moniker: drop it"*. The arrays behind every one of
    #   these reads are the LIVE line - v4_l2_proxy._state falls back to self.E, and the pseudo
    #   branch cannot fire at LIN2_PSEUDO_MIN_TF 99. A 'c' prefix was reporting a read the fork
    #   no longer takes.
    return ('pws' if BD.state_src(int(tf)) == 'pseudo' else 'ws') + str(int(tf))


def cand_col(r):
    cd, b = r.get('cands'), r.get('bar')
    if cd is None or b is None:
        return '-'
    if cd == ():
        return 'none offered'
    return ', '.join('%s: %.2f' % (tag(t), BD.value(int(t), int(b))) for t in cd)


def event(r):
    why = str(r['why']).replace('|', '\\|')
    rd = r.get('rider')
    head = r['stage'] if not rd else '%s rider %s' % (r['stage'], tag(rd))
    pre = '**CADENCE:** ' if str(r.get('ctype') or '') in CADENCE_TYPES else ''
    return '%s%s - %s' % (pre, head, why)


def latched_col(bar, side):
    on = [t for t in range(1, int(K.L2_MOM_MAXTF) + 1)
          if t in BD.tfs and BD.baton_ex_fence(t, int(bar), int(side))]
    return 'none' if not on else '%d: %s' % (len(on), ','.join('ws%d' % t for t in on))


def barrage_col(bar, side):
    b = int(bar)
    own = [x for x in BARR[int(side)] if x <= b]
    opp = [x for x in BARR[-int(side)] if x <= b]
    bits = []
    if own and own[-1] == b:
        bits.append('FIRES HERE')
    elif own:
        bits.append('last %s, %.1f min ago' % (ln.U(own[-1])[11:], (b - own[-1]) * 5 / 60.0))
    else:
        bits.append('none yet')
    if opp and opp[-1] == b:
        bits.append('counter-side FIRES HERE')
    elif opp and (not own or opp[-1] > own[-1]):
        bits.append('counter-side %s' % ln.U(opp[-1]))
    return ' / '.join(bits)


#   ── leg numbers, per day ───────────────────────────────────────────────────────────────────
seen = {}
for x in lg:
    d = ln.U(x['opn'])[:10]
    seen[d] = seen.get(d, 0) + 1
    x['day'] = d
    x['nday'] = seen[d]

print('# THE 2-DAY CHAIN - FENCE 75/25, LADDER ws1..ws20, THE LATCH RELEASED ON LIFT-OFF')
print('# WINDOW %s .. %s | TAPE %d bars | RULED_OK %s' % (ln.U(A), ln.U(B), len(close), K.RULED_OK))
print('# RMOM_FNC %.1f -> (%.1f, %.1f) | L2_MOM_MAXTF %d | LIN2_EXFNC_LATCH_REL %r'
      % (K.RMOM_FNC, 100.0 - K.RMOM_FNC, K.RMOM_FNC, K.L2_MOM_MAXTF, K.LIN2_EXFNC_LATCH_REL))
print('# the latch turns ON at an ex-fence cross held %d bars = %d s, and is released ONLY by that'
      % (K.LIN2_EXFNC_LATCH_WOB, K.LIN2_EXFNC_LATCH_WOB * 5))
print('#   line\'s own lift-off on the same side, stamped at lift + LIFT_WOB - 1 = lift + %d bars'
      ' = %d s.' % (K.LIFT_WOB - 1, (K.LIFT_WOB - 1) * 5))
print('#   and its sampling RESTARTS at the latch-on bar - his 1030 ruling - so the lattice must'
      ' refill before any release can print.')
print('# the barrage no longer releases the latch on this arm. It is still a cadence, so the'
      ' column stays.')
print('# LIN2_COUNTER_OOB_ON %d - his 1030 *"drop the opposing oob side forced exit"*. At 0 the'
      ' ws1b counter-target-side' % K.LIN2_COUNTER_OOB_ON)
print('#   oob cadence is not produced at all, so no leg can exit on it. Its replacement is'
      ' UNRULED - his own words.')
print('# the open is %s %s, handed in - the router\'s fire bar off the lin2-reentry signal %s.'
      % (ln.U(OPEN[0]), OPEN_DIR, ln.U(SIG[0]['bar'])))
print('# the baton fence test reads: %s. the 1.1%% stop is OFF. drag %.4f%% per round trip,'
      ' its own column and its own total.' % (BD.baton_src(), CH.DRAG_PCT))
print('# ts is the bar. pxs is that bar\'s close unless the row names an extreme. pct is signed to'
      ' THIS leg.')
print('# baton candidates: every candidate timeframe offered at that bar with its value.'
      ' "none offered" = a hand-over attempt with no candidate inside lin_hop %d.' % K.L2_LIN_HOP)
print('# exfnc ltchd: every ws1..ws%d line whose ex-fence latch is ON at that bar, on this leg\'s'
      ' side.' % K.L2_MOM_MAXTF)
print('# a row whose bar carried a cadence starts **CADENCE:**.')

print('')
print('## THE CHAIN SUMMARY - one row per leg, chronological')
print('')
print('| day | leg of that day | leg of the chain | the open | dir | the exit | ended by |'
      ' held min | the rider chain | MAE % | MFE % | realised % | drag % | net % |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
tm = tf_ = tr = th = 0.0
sc = 0
for n, x in enumerate(lg, 1):
    ch = []
    for r in x['rows']:
        rd = r.get('rider')
        if rd and (not ch or ch[-1] != rd):
            ch.append(rd)
    chs = ' > '.join('ws%d' % t for t in ch) if ch else '-'
    d = 'LONG' if x['side'] > 0 else 'SHORT'
    if x['exit'] is None:
        print('| %s | %d | %d | %s | %s | - | %s | - | %s | - | - | - | - | - |'
              % (x['day'], x['nday'], n, ln.U(x['opn']), d, x['ctype'], chs))
        continue
    sc += 1
    tm += x['mae']; tf_ += x['mfe']; tr += x['rel']; th += x['held_min']
    print('| %s | %d | %d | %s | %s | %s | %s | %.1f | %s | %.4f | %+.4f | %+.4f | %.4f | %+.4f |'
          % (x['day'], x['nday'], n, ln.U(x['opn']), d, ln.U(x['exit']), x['ctype'],
             x['held_min'], chs, x['mae'], x['mfe'], x['rel'], CH.DRAG_PCT,
             x['rel'] - CH.DRAG_PCT))
print('| TOTAL | | %d scored legs | | | | | %.1f | | %.4f | %+.4f | %+.4f | %.4f | %+.4f |'
      % (sc, th, tm, tf_, tr, CH.DRAG_PCT * sc, tr - CH.DRAG_PCT * sc))
if zero:
    print('')
    print('| a leg whose exit lands before its own open - recorded, not scored | its open |'
          ' its exit | dir | ended by |')
    print('|---|---|---|---|---|')
    for z in zero:
        print('| zero-length | %s | %s | %s | %s |'
              % (ln.U(z['opn']), ln.U(z['exit']), 'LONG' if z['side'] > 0 else 'SHORT', z['ctype']))

#   ── the six walks he named ─────────────────────────────────────────────────────────────────
#   WHICH WALKS TO PRINT, settable so a question about one leg does not need a code edit.
#   W_WALKS='2026-08-31:5,2026-08-30:13' prints those two. Unset is the six he first asked for.
_w = os.environ.get('W_WALKS', '')
if _w:
    WANT = [(p.split(':')[0], int(p.split(':')[1])) for p in _w.split(',') if p.strip()]
else:
    WANT = [('2026-08-30', 2), ('2026-08-30', 4), ('2026-08-30', 6),
            ('2026-08-31', 2), ('2026-08-31', 4), ('2026-08-31', 6)]
for day, k in WANT:
    hit = [x for x in lg if x['day'] == day and x['nday'] == k]
    print('')
    if not hit:
        print('## %s leg %d - THE CHAIN HAS NO SUCH LEG. %s carries %d legs.'
              % (day, k, day, seen.get(day, 0)))
        continue
    x = hit[0]
    opn, side, ex = int(x['opn']), int(x['side']), x['exit']
    d = 'LONG' if side > 0 else 'SHORT'
    o = float(close[opn])

    def pct(px):
        return side * (float(px) - o) / o * 100.0

    head = ['## %s leg %d - %s' % (day, k, d), 'opens %s' % ln.U(opn)]
    if ex is None:
        head.append('NO EXIT to the window end')
    else:
        head.append('exits %s on %s' % (ln.U(ex), x['ctype']))
        head.append('held %.1f min' % x['held_min'])
        head.append('MAE %.4f' % x['mae'])
        head.append('MFE %.4f' % x['mfe'])
        head.append('realised %+.4f' % x['rel'])
        head.append('net %+.4f' % (x['rel'] - CH.DRAG_PCT))
    print('   '.join(head))
    print('')
    print('| ts | event | baton candidates | exfnc ltchd | barrage | pxs | pct for THIS leg |')
    print('|---|---|---|---|---|---|---|')
    out = [(opn, '>>> THIS LEG OPENS %s' % d, '-', o)]
    for r in x['rows']:
        if r.get('bar') is None:
            out.append((opn, 'NOTE %s - %s' % (r['stage'], str(r['why']).replace('|', '\\|')),
                        '-', o))
            continue
        out.append((int(r['bar']), event(r), cand_col(r), float(close[int(r['bar'])])))
    if ex is not None:
        H = np.asarray(phi[opn:int(ex) + 1], float)
        L = np.asarray(plo[opn:int(ex) + 1], float)
        if side > 0:
            ab, ap = opn + int(np.nanargmin(L)), float(np.nanmin(L))
            vb, vp = opn + int(np.nanargmax(H)), float(np.nanmax(H))
        else:
            ab, ap = opn + int(np.nanargmax(H)), float(np.nanmax(H))
            vb, vp = opn + int(np.nanargmin(L)), float(np.nanmin(L))
        out.append((ab, 'the ADVERSE extreme - MAE %.4f' % abs(pct(ap)), '-', ap))
        out.append((vb, 'the favourable extreme - MFE %.4f' % pct(vp), '-', vp))
        out.append((int(ex), 'THIS LEG CLOSES on %s, realised %+.4f, drag %.4f, net %+.4f'
                    % (x['ctype'], x['rel'], CH.DRAG_PCT, x['rel'] - CH.DRAG_PCT),
                    '-', float(close[int(ex)])))
    for bar, ev, cc, px in sorted(out, key=lambda z: z[0]):
        print('| %s | %s | %s | %s | %s | %.6f | %+.4f |'
              % (ln.U(bar), ev, cc, latched_col(bar, side), barrage_col(bar, side), px, pct(px)))

print('')
print('| the read | value |')
print('|---|---|')
print('| legs in the chain over the two days | %d |' % len(lg))
print('| legs opening on 2026-08-30 | %d |' % seen.get('2026-08-30', 0))
print('| legs opening on 2026-08-31 | %d |' % seen.get('2026-08-31', 0))
print('| legs opening on 2026-08-29 | %d |' % seen.get('2026-08-29', 0))
print('| seconds to compute | %.1f |' % (time.time() - T0))
