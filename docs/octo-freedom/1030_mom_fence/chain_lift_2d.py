"""THE CHAIN DRIVER. One file, annotated as it changes - his 1101 rule, not a fork per question.

HIS 1101 INSTRUCTION, verbatim: *"make sure your running the updated script.  remember that you now
only use one script and annotate changes, instead of building a new script for every update"*. It
replaced `days_0903.py` and `chain_0903.py`, which each hardcoded their own open and window and had
begun to drift. Both were deleted on his word *"4 is delete, so long as we don't lose the 08-14
1407"* - that walk comes from `baton_l2_0814.py`, which this does not touch.

EVERYTHING A QUESTION NEEDS IS AN ARGUMENT OR AN ENV VAR, so a new question needs no new file:

    W_WIN_START  the window's first bar          default 2026-08-30 00:00:00
    W_WIN_END    its last bar                    default 2026-08-31 23:59:55
    W_OPEN       the handed-in open bar          default '' = take it from the lin2-reentry signal
    W_SIDE       LONG or SHORT, with W_OPEN      default SHORT
    W_MAE_CAP    'on' turns the 1.1% stop on     default off
    W_WALKS      'day:leg,day:leg' or 'none'     default the six legs he first asked for
    W_RESIG      'on' gives a stop its way back  default off - see below

THE KNOBS COME FROM THE BANK. Every value this once passed in by hand - the 75/25 fence, the ws30
ladder, the lift-off latch release - was banked on 1031, so the run needs no W_V4_* overrides and
the ruled check passes on its own. An override is now an experiment and v4_knobs says so.

THE OPEN IS HANDED IN WHEN W_OPEN IS SET, his instruction on every walk he has named. Without it
the open comes off the lin2-reentry signal at 2026-08-29 23:53:50, the path legs_live.py and the
week A/B use. The side is never derived from price.

W_RESIG AND THE STOP. v4_chain.legs goes FLAT at a stop, so a stop needs a way back in. The only
one wired is v4_sig_lin2_reentry - the ws5Mage reentry - and his 1101 update opens with *"delete
the current ws5Mage reentry (from spec and code)"*. So W_RESIG defaults OFF: with the stop on and
no way back in, the chain reports to its FIRST STOP and ends. That is the machine's true state with
the old reentry deleted and his new one pending. W_RESIG=on restores the old path for an A/B only.

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
#   NOTHING IS FORCED HERE ANY MORE. These three were set by hand when they were off the bank;
#   all three are now the banked defaults, so setting them would hide a later bank move from the
#   ruled check. LIN2_PSEUDO_MIN_TF 99, LIN2_LATCH_EXFNC_ON 1 and LIN2_B1_HOLD 0 all come from
#   v4_knobs.*

#   THE WINDOW IS SETTABLE so the same driver can settle a knob on a wider window without a
#   second copy of the loop. His 1030: *"settle (sweep) the floor (the control's net%) on a
#   wider window"*. The open stays the handed-in 2026-08-29 23:53:55 SHORT either way.
A = ln.K(os.environ.get('W_WIN_START', '2026-08-30 00:00:00'))
B = ln.K(os.environ.get('W_WIN_END', '2026-08-31 23:59:55'))
_OPEN_AT = os.environ.get('W_OPEN', '')
_OPEN_SIDE = +1 if os.environ.get('W_SIDE', 'SHORT').upper() == 'LONG' else -1
close, phi, plo = prices()
E = RS.load((RS.K0, RS.R0, RS.S0))
CL = LL.arm_lines(E)
MG = LL.mage()                     # ws1..ws{L2_MOM_MAXTF}
B1 = np.asarray(CL['b'], float)
BD = PX.Board(E, E, MG=MG, MGE=MG, PS=None)
assert max(MG) == int(K.L2_MOM_MAXTF), 'the Mage ladder top does not match the knob'

#   W_OPEN HANDS THE OPEN IN DIRECTLY - a bar and a side, his own route on every walk he names.
#   Without it the open comes off the 2026-08-29 23:53:50 lin2-reentry signal, which is the path
#   the banked 2-day numbers were measured on.
if _OPEN_AT:
    OPEN_DIR = 'LONG' if _OPEN_SIDE > 0 else 'SHORT'
    OPEN = (ln.K(_OPEN_AT), _OPEN_SIDE)
    SIG = None
    assert ln.U(OPEN[0]) == _OPEN_AT, 'W_OPEN is not a tape bar: %s' % _OPEN_AT
else:
    SIG = [g for g in L2R.signals(B1, MG) if g['bar'] == ln.K('2026-08-29 23:53:50')]
    assert len(SIG) == 1, ('the 23:53:50 lin2-reentry signal is not in the list at this ladder -'
                           ' %d matches' % len(SIG))
    OPEN_DIR = SG.direction(int(SIG[0]['side']))
    OPEN = (SG.fire_bar(SIG[0]), SG.target_side(OPEN_DIR))
    assert ln.U(OPEN[0]) == '2026-08-29 23:53:55', 'the handed-in open moved: %s' % ln.U(OPEN[0])

#   THE 1.1% STOP, OFF BY DEFAULT. His 1030: *"are you sweeping using mae1.1? that will impact
#   the results if your sweep"*. It was off in every arm run before this.
#   IT NEEDS THE SIGNAL LIST. v4_chain.legs goes FLAT at a stop - his own first line for
#   lin2-reentry is *"there is no trade open (either because of a STOP, or because the machine is
#   cold-starting)"* - and the way back in is the next lin2-reentry signal. Without that list a
#   stop ENDS the chain, which would read as a shorter chain rather than as a stop.
CAP = float(K.LIN2_MAE_CAP) if os.environ.get('W_MAE_CAP') == 'on' else None
#   THE WAY BACK IN IS OFF BY DEFAULT since his 1101 update deleted the ws5Mage reentry. With the
#   stop on and resig None the chain reports to its first stop and ends - the machine's true state
#   while his new re-entry is pending. W_RESIG=on restores the old path for an A/B only.
RESIG = (L2R.signals(B1, MG)
         if (CAP is not None and os.environ.get('W_RESIG') == 'on') else None)
lg, zero, op = CH.legs(CL, BD, close, phi, plo, A, B, MG=MG, B1=B1, open_at=OPEN,
                       mae_cap=CAP, resig=RESIG)

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

#   EVERY VALUE IN THIS HEADER COMES FROM THE KNOB, none is typed. The old title read
#   "LADDER ws1..ws20" from when that was the arm, and on 1101 - with L2_MOM_MAXTF banked at 30 and
#   printed one line below it - Joe read the stale title and said *"I see that ws20 is the maxTF"*.
#   A hardcoded number in a header outlives the thing it describes.
print('# THE CHAIN - FENCE %.0f/%.0f, LADDER ws1..ws%d, THE LATCH RELEASED ON %s'
      % (K.RMOM_FNC, 100.0 - K.RMOM_FNC, K.L2_MOM_MAXTF,
         str(K.LIN2_EXFNC_LATCH_REL).upper()))
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
print('# the open is %s %s, handed in - %s'
      % (ln.U(OPEN[0]), OPEN_DIR,
         'W_OPEN, his own bar and side' if SIG is None
         else "the router's fire bar off the lin2-reentry signal %s" % ln.U(SIG[0]['bar'])))
print('# the way back in after a stop: %s'
      % ('the ws5Mage reentry, W_RESIG=on - an A/B of a mech his 1101 update deleted'
         if RESIG else 'NONE - the chain ends at its first stop'))
print('# the baton fence test reads: %s. the stop is %s. drag %.4f%% per round trip, its own'
      ' column and its own total.'
      % (BD.baton_src(),
         'OFF' if CAP is None else ('ON at LIN2_MAE_CAP %.2f%%, with %d lin2-reentry signals as the'
                                    ' way back in' % (CAP, len(RESIG or ()))),
         CH.DRAG_PCT))
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
if _w == 'none':
    WANT = []          # the summary only - a sweep arm has no use for the row traces
elif _w:
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
print('| legs in the chain over the window | %d |' % len(lg))
#   ONE ROW PER DAY THE WINDOW SPANS, not two typed dates. The old pair read
#   "legs opening on 2026-08-30" and "...08-31" whatever window was passed in.
for _d in sorted({ln.U(int(x['opn']))[:10] for x in lg}):
    print('| legs opening on %s | %d |' % (_d, sum(1 for x in lg if x['day'] == _d)))
print('| seconds to compute | %.1f |' % (time.time() - T0))
