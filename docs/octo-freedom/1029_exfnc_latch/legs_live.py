"""THE LEG REPORT, ALL FOUR LINES LIVE, THE EX-FENCE LATCH ON, ws1b HOLD 0.

His report format, 1028-1029:
    | ts | event | baton candidates | pxs | pct for THIS leg |
    each leg starts at its own open; no 'min from this open' column.

THE SETTINGS, all his:
    prev-close            OUT of the walk entirely - ws1b, ws1r, ws1Mage, ws2Mage are live
    the ex-fence latch    ON, hold 4 bars = 20 s
    the pseudo-closed line  not in this arm
    the ws1b hold         0 - *"let's use wob 0 until we sweep"*
    the open              2026-08-29 23:53:55 SHORT, the router's fire bar off the 23:53:50 signal
    the 1.1% stop         off
"""
import os, sys, io, time
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

K.LIN2_PSEUDO_MIN_TF = 99
K.LIN2_LATCH_EXFNC_ON = 1
K.LIN2_B1_HOLD = 0

A, B = ln.K('2026-08-30 00:00:00'), ln.K('2026-08-30 23:59:55')
close, phi, plo = prices()
E = RS.load((RS.K0, RS.R0, RS.S0))
CL = LL.arm_lines(E)
MG = LL.mage()      # ws1..ws{L2_MOM_MAXTF} - the knob owns the top rung
B1 = np.asarray(CL['b'], float)
BD = PX.Board(E, E, MG=MG, MGE=MG, PS=None)

SIG = [g for g in L2R.signals(B1, MG) if g['bar'] == ln.K('2026-08-29 23:53:50')]
assert len(SIG) == 1, 'the 23:53:50 signal is not in the list'
OPEN_DIR = SG.direction(int(SIG[0]['side']))
OPEN = (SG.fire_bar(SIG[0]), SG.target_side(OPEN_DIR))
ALLSIG = L2R.signals(B1, MG)


def tag(tf):
    return ('ws' if BD.state_src(int(tf)) == 'pseudo' else 'cws') + str(int(tf))


def cand_col(r):
    cd, b = r.get('cands'), r.get('bar')
    if cd is None or b is None:
        return '-'
    if cd == ():
        return 'none offered'
    return ', '.join('%s: %.2f' % (tag(t), BD.value(int(t), int(b))) for t in cd)


def event(r):
    st = r['stage']
    why = str(r['why']).replace('|', '\\|')
    rd = r.get('rider')
    head = st if not rd else '%s rider %s' % (st, tag(rd))
    pre = '**CADENCE:** ' if str(r.get('ctype') or '') in CADENCE_TYPES else ''
    return '%s%s - %s' % (pre, head, why)


#   THE BARRAGE SIGNALS, both sides, produced once over the whole window. The column reports the
#   most recent one at or before each row's bar, so it never reads forward.
import v4_l2_cadence as CAD
BARR = {}
for sd in (-1, +1):
    BARR[sd] = sorted(int(r[0]) for r in CAD.barrage(BD, sd, 0, len(close) - 1))


def barrage_col(bar, side):
    """The barrage on this leg's side at or before `bar`. -> a cell."""
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
        bits.append('counter-side %s' % ln.U(opp[-1])[11:])
    return ' / '.join(bits)


def latched_col(bar, side):
    """Every line whose ex-fence latch is on at `bar`, on this leg's side. -> a cell."""
    on = [t for t in range(1, int(K.L2_MOM_MAXTF) + 1)
          if t in BD.tfs and BD.baton_ex_fence(t, int(bar), int(side))]
    if not on:
        return 'none'
    return '%d: %s' % (len(on), ','.join('ws%d' % t for t in on))


#   WHICH ROWS ARE CADENCE MARKERS. A row carries a cadence type when a cadence fired on its bar.
#   'between' is not one - it names a bar BETWEEN cadences - and the retest gate is.
CADENCE_TYPES = ('t1', 't2', 'barrage', 'cws1b counter-oob', 'retest')

lg, zero, op = CH.legs(CL, BD, close, phi, plo, A, B, MG=MG, B1=B1, open_at=OPEN, resig=ALLSIG)
sc = CH.score(lg)

print('# THE LEG REPORT - ALL FOUR LINES LIVE, THE EX-FENCE LATCH ON, ws1b HOLD 0')
print('# WINDOW %s .. %s | TAPE %d bars | RULED_OK %s' % (ln.U(A), ln.U(B), len(close), K.RULED_OK))
print('# prev-close is OUT of the walk: ws1b, ws1r, ws1Mage and ws2Mage are all the live read.')
print('# the ex-fence latch hold is %d bars = %d s. the ws1b hold is %d - his "wob 0 until we'
      ' sweep".' % (K.LIN2_EXFNC_LATCH_WOB, K.LIN2_EXFNC_LATCH_WOB * 5, K.LIN2_B1_HOLD))
print('# the open is %s %s, the router fire bar off the lin2-reentry signal %s.'
      % (ln.U(OPEN[0]), OPEN_DIR, ln.U(SIG[0]['bar'])))
print('# the 1.1%% stop is OFF. drag %.4f%% per round trip, its own column and its own total.'
      % CH.DRAG_PCT)
print('# baton candidates: every candidate timeframe offered at that bar with its value.')
print('# "none offered" is a hand-over attempt with no candidate inside lin_hop %d.'
      % K.L2_LIN_HOP)
print('# exfnc ltchd: every ws1..ws%d line whose ex-fence latch is ON at that bar, on this leg\'s'
      ' side.' % K.L2_MOM_MAXTF)
print('# barrage: the most recent barrage on this leg\'s side at or before that bar, and the'
      ' counter-side one when it is newer.')
print('# a row whose bar carried a cadence starts **CADENCE:**.')
print('')

for n, x in enumerate(lg, 1):
    opn, side, ex = x['opn'], x['side'], x['exit']
    d = 'LONG' if side > 0 else 'SHORT'
    o = float(close[opn])

    def pct(px):
        return side * (float(px) - o) / o * 100.0

    bits = ['## leg %d of %d - %s %s' % (n, len(lg), ln.U(opn)[:10], d),
            'opens %s' % ln.U(opn)]
    if ex is None:
        bits.append('NO EXIT to the window end')
    else:
        bits.append('exits %s on %s' % (ln.U(ex), x['ctype']))
        bits.append('MAE %.4f' % x['mae'])
        bits.append('MFE %.4f' % x['mfe'])
        bits.append('realised %+.4f' % x['rel'])
        bits.append('held %.1f min' % x['held_min'])
    bits.append('CONTINUITY: %s'
                % ('the chain opens here' if n == 1 else
                   ('1 bar after leg %d exit %s' % (n - 1, ln.U(lg[n - 2]['exit'])))))
    print('   '.join(bits))
    print('')
    print('| ts | event | baton candidates | exfnc ltchd | barrage | pxs |'
          ' pct for THIS leg |')
    print('|---|---|---|---|---|---|---|')
    out = [(opn, '>>> THIS LEG OPENS %s' % d, '-', o)]
    for r in x['rows']:
        if r.get('bar') is None:
            out.append((opn, 'NOTE %s - %s' % (r['stage'], str(r['why']).replace('|', '\\|')),
                        '-', o))
            continue
        out.append((int(r['bar']), event(r), cand_col(r), float(close[int(r['bar'])])))
    if ex is not None:
        lo, hi = int(opn), int(ex)
        H = np.asarray(phi[lo:hi + 1], float); L = np.asarray(plo[lo:hi + 1], float)
        if side > 0:
            ab, ap = lo + int(np.nanargmin(L)), float(np.nanmin(L))
            vb, vp = lo + int(np.nanargmax(H)), float(np.nanmax(H))
        else:
            ab, ap = lo + int(np.nanargmax(H)), float(np.nanmax(H))
            vb, vp = lo + int(np.nanargmin(L)), float(np.nanmin(L))
        out.append((ab, 'the ADVERSE extreme - MAE %.4f' % abs(pct(ap)), '-', ap))
        out.append((vb, 'the favourable extreme - MFE %.4f' % pct(vp), '-', vp))
        out.append((int(ex), 'THIS LEG CLOSES on %s, realised %+.4f' % (x['ctype'], x['rel']),
                    '-', float(close[int(ex)])))
    for bar, ev, cc, px in sorted(out, key=lambda z: z[0]):
        print('| %s | %s | %s | %s | %s | %.6f | %+.4f |'
              % (ln.U(bar), ev, cc, latched_col(bar, side), barrage_col(bar, side), px, pct(px)))
    print('')

print('## the MAE / MFE aggregate over every leg')
print('')
print('| leg | the open | dir | the exit | ended by | held min | the rider chain | MAE % | MFE % |'
      ' realised % | drag % | net % |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|')
for n, x in enumerate(lg, 1):
    ch = []
    for r in x['rows']:
        rd = r.get('rider')
        if rd and (not ch or ch[-1] != rd):
            ch.append(rd)
    chs = ' > '.join('ws%d' % t for t in ch) if ch else '-'
    d = 'LONG' if x['side'] > 0 else 'SHORT'
    if x['exit'] is None:
        print('| %d | %s | %s | - | no exit | - | %s | - | - | - | - | - |'
              % (n, ln.U(x['opn']), d, chs))
        continue
    print('| %d | %s | %s | %s | %s | %.1f | %s | %.4f | %+.4f | %+.4f | %.4f | %+.4f |'
          % (n, ln.U(x['opn']), d, ln.U(x['exit']), x['ctype'], x['held_min'], chs, x['mae'],
             x['mfe'], x['rel'], CH.DRAG_PCT, x['rel'] - CH.DRAG_PCT))
print('| TOTAL %d legs | | | | | %.1f | | %.4f | %+.4f | %+.4f | %.4f | %+.4f |'
      % (sc['n'], sc['held'], sc['mae'], sc['mfe'], sc['rel'], sc['drag'], sc['net']))
print('')
print('| the read | value |')
print('|---|---|')
print('| legs with an exit | %d of %d |' % (sc['n'], len(lg)))
print('| legs net-positive after drag | %d of %d |' % (sc['win'], sc['n']))
print('| exits on the barrage | %d |' % sc['barr'])
print('| MFE collected | %s |' % ('%.1f%%' % (sc['rel'] / sc['mfe'] * 100.0)
                                  if sc['mfe'] > 0 else 'n/a'))
print('| summed drag in its own right | %.4f%% over %d round trips |' % (sc['drag'], sc['n']))
print('| legs with no bars, exit before open | %d |' % len(zero))
print('| seconds to compute | %.1f |' % (time.time() - T0))
