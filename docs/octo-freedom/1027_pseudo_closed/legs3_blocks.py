"""THE FIRST 3 LEGS ON THE PSEUDO BOARD, IN THE 1008 BLOCK FORMAT. Joe 1028:

    "| ts | min from THIS open | event | pxs | pct for THIS leg |  we'll stick to this format for
     now / create the 3 legs please"

The column set is his, from docs/octo-freedom/1008_walk24_blocks.txt. Five columns, one record per
row, chronological ascending. Rendered as markdown - his 1011 rule keeps box-drawing out of a
report.

THE INCOMING LEG IS ON THE SAME TIMELINE, as in 1008: a leg's block carries the previous leg's
walk events at NEGATIVE minutes so the chain's continuity is visible in the block itself.

ONE DIFFERENCE FROM 1008, and it is the chain's own banked rule, not a choice made here: in this
chain the exhaust bar IS the rev-trade bar, the open trade closes there, and the opposite side
opens at that bar + 1 (5 s later). 1008 was built on a mech where the open bar and the exit bar
were the same bar. So the INCOMING LEG CLOSES row and the THIS LEG OPENS row are 5 s apart.

THE BOARD: ws1..ws3 keep their current reads; ws4 upward read PSEUDO-CLOSED for the ex-fence state
and for the value quoted in an event. LIN2_PSEUDO_MIN_TF 4, his value.

BOTH REVERSAL TIMES: his ruling was two columns. This column set has no room for them, so where a
walk event's reason IS a reversal the event text names the lift-off time and the pseudo time
together. The ladder-rows report (legs3v2.py) still carries them as columns.
"""
import os, sys, io
import numpy as np
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1027_pseudo_closed')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln, v4_knobs as K, v4_rcfg_sweep as RS, v4_closed_prev as CP
import v4_l2_proxy as PX, v4_lineage2 as L2
import pseudo_closed as PC
from optimus9.analysis.jig import lift_off
from v4_backstop_trades import prices
sys.stderr = _e

DAY = '2026-08-30'
A, B = ln.K('%s 00:00:00' % DAY), ln.K('%s 23:59:55' % DAY)
MINTF, TOP = int(K.LIN2_PSEUDO_MIN_TF), int(K.L2_MOM_MAXTF)
N_LEGS = 3                      # his ask: "the first 3 legs"
DRAG = 0.1975                   # % round trip, o9-live drag_pct: 11.0 bps fee + 8.75 bps slippage

close, phi, plo = prices()
E = RS.load((RS.K0, RS.R0, RS.S0))
C = CP.ladder(E)
CL = CP.arm_lines(E)
MGL = {t: CP.line('ws%dMage' % t, t * 60) for t in range(1, 13)}
MGE = {t: ln.line('ws%dMage' % t) for t in range(1, 13)}
IDX = np.arange(A, B + 1)
PS = {}
for t in range(MINTF, TOP + 1):
    PS[t] = np.full(len(close), np.nan)
    PS[t][IDX] = PC.series(close, t, IDX)
BD = PX.Board(C, E, MG=MGL, MGE=MGE, PS=PS)

REV = {}
for t in range(1, TOP + 1):
    for sd in (-1, +1):
        REV[('lift', t, sd)] = sorted(int(K.lift_stamp(int(b))) for b in
                                      lift_off(np.asarray(E[t], float), sd, K.LIFT_PTS,
                                               K.gap_for(t), K.LIFT_TOL, int(K.LIFT_WOB)))
        src = PS[t] if t in PS else np.asarray(C[t], float)
        REV[('pseudo', t, sd)] = sorted(int(K.lift_stamp(int(b))) for b in
                                        lift_off(src, sd, K.LIFT_PTS, K.gap_for(t), K.LIFT_TOL,
                                                 int(K.LIFT_WOB)))


def last_rev(kind, tf, sd, bar):
    r = [x for x in REV[(kind, int(tf), int(sd))] if x <= int(bar)]
    return ln.U(r[-1]) if r else 'none'


def revtext(tf, sd, bar):
    """the two reversal times his ruling asked for, folded into the event text."""
    return 'rev lift-off %s / pseudo %s' % (last_rev('lift', tf, sd, bar),
                                            last_rev('pseudo', tf, sd, bar))


def tag(tf):
    return ('ws' if BD.state_src(int(tf)) == 'pseudo' else 'cws') + str(int(tf))


def event(r, sd):
    """the walk row as one event string. the why already carries the line values."""
    st = r['stage']
    why = str(r['why']).replace('|', '\\|')
    rd = r.get('rider')
    cd = r.get('cands')
    bits = [st]
    if rd:
        bits.append('rider %s' % tag(rd))
    if cd:
        bits.append('candidates %s' % ','.join(tag(x) for x in cd))
    elif cd == ():
        bits.append('candidates none')
    head = ' '.join(bits)
    if rd and r.get('bar') is not None and st in ('RIDER', 'BATON', 'LATCH1', 'EXHAUST', 'HOLD'):
        why = '%s; %s' % (why, revtext(rd, sd, r['bar']))
    return '%s - %s' % (head, why)


# ---- the chain -------------------------------------------------------------------------------
legs, side, frm, prev_exhaust = [], +1, int(A), None
while len(legs) < N_LEGS:
    v, bar, rows = L2.walk(CL, BD, close, side, frm, B)
    opn = int(A) if prev_exhaust is None else int(prev_exhaust) + 1
    legs.append(dict(opn=opn, side=side, verdict=v, exit=bar, rows=rows))
    if bar is None:
        break
    prev_exhaust = int(bar)
    frm, side = int(bar), -side


def pct(opn, sd, px):
    o = float(close[int(opn)])
    return sd * (float(px) - o) / o * 100.0


def mae_mfe(opn, ex, sd):
    """the adverse and favourable extremes on the highs and lows, inside [open, exit]."""
    if ex is None:
        return (None, None, None, None)
    lo, hi = int(opn), int(ex)
    H = np.asarray(phi[lo:hi + 1], float)
    L = np.asarray(plo[lo:hi + 1], float)
    if sd > 0:
        ia, pa = int(np.nanargmin(L)), float(np.nanmin(L))
        iv, pv = int(np.nanargmax(H)), float(np.nanmax(H))
    else:
        ia, pa = int(np.nanargmax(H)), float(np.nanmax(H))
        iv, pv = int(np.nanargmin(L)), float(np.nanmin(L))
    return (lo + ia, pa, lo + iv, pv)


print('# THE FIRST %d LEGS, %s - the 1008 block format' % (N_LEGS, DAY))
print('# TAPE %d bars | LG_TAPE_END %s | RULED_OK %s'
      % (len(close), os.environ['LG_TAPE_END'], K.RULED_OK))
print('# BOARD: ws1..ws%d keep their reads; ws%d.. read PSEUDO for ex-fence and for the quoted'
      ' value. LIN2_PSEUDO_MIN_TF %d.' % (MINTF - 1, MINTF, MINTF))
print('# BARRAGE: LIN2_BARRAGE_MIN_TF %d, LINES %d, TOL %ds, MIN_TF_MODE %r - the pine-emit'
      ' settings.' % (K.LIN2_BARRAGE_MIN_TF, K.LIN2_BARRAGE_LINES, K.LIN2_BARRAGE_TOL_S,
                      K.LIN2_BARRAGE_MIN_TF_MODE))
print('# THE EXHAUST BAR IS THE REV-TRADE BAR: the leg closes there, the opposite side opens at')
print('#   that bar + 1. So INCOMING LEG CLOSES and THIS LEG OPENS are 5 s apart, not the same bar.')
print('# pct for THIS leg is measured from THIS leg open on THIS leg side. Incoming rows read')
print('#   NEGATIVE where price was already beyond this open.')
print('# ex-fence is the %.0f/%.0f fence from RMOM_FNC; oob is 15/85. ws1..ws3 are cws (closed),'
      ' ws4+ are ws (pseudo).' % (100 - K.RMOM_FNC, K.RMOM_FNC))
print('')

for n, lg in enumerate(legs, 1):
    opn, sd, ex = lg['opn'], lg['side'], lg['exit']
    dirn = 'LONG' if sd > 0 else 'SHORT'
    ab, ap, vb, vp = mae_mfe(opn, ex, sd)
    bits = ['## leg %d of %d - %s %s' % (n, len(legs), DAY, dirn),
            'opens %s' % ln.U(opn)]
    if ex is None:
        bits.append('NO EXHAUST to the window end')
    else:
        bits.append('exits %s on %s' % (ln.U(ex), lg['verdict']))
        bits.append('MAE %.4f at %+.1f min' % (abs(pct(opn, sd, ap)), (ab - opn) * 5 / 60.0))
        bits.append('MFE %.4f at %+.1f min' % (pct(opn, sd, vp), (vb - opn) * 5 / 60.0))
        bits.append('realised %+.4f' % pct(opn, sd, float(close[int(ex) + 1])))
    bits.append('CONTINUITY: %s' % ('the first leg - opens at the window start'
                                    if n == 1 else
                                    'UNBROKEN - 1 bar after leg %d exhaust %s'
                                    % (n - 1, ln.U(legs[n - 2]['exit']))))
    print('   '.join(bits))
    print('')
    print('| ts | min from THIS open | event | pxs | pct for THIS leg |')
    print('|---|---|---|---|---|')

    out = []
    if n == 1:
        out.append((opn - 1, 'no incoming leg - the chain has no trade open before leg 1',
                    float(close[opn - 1])))
    else:
        p = legs[n - 2]
        pdir = 'LONG' if p['side'] > 0 else 'SHORT'
        out.append((p['opn'], 'INCOMING LEG OPENS %s' % pdir, float(close[p['opn']])))
        for r in p['rows']:
            if r.get('bar') is None:
                continue
            out.append((int(r['bar']), 'incoming: %s' % event(r, p['side']),
                        float(close[int(r['bar'])])))
        out.append((int(p['exit']), 'INCOMING LEG CLOSES on %s, realised %+.4f'
                    % (p['verdict'], pct(p['opn'], p['side'], float(close[int(p['exit']) + 1]))),
                    float(close[int(p['exit'])])))
    out.append((opn, '>>> THIS LEG OPENS %s' % dirn, float(close[opn])))
    for r in lg['rows']:
        if r.get('bar') is None:
            out.append((opn, 'NOTE %s - %s' % (r['stage'], str(r['why']).replace('|', '\\|')),
                        float(close[opn])))
            continue
        out.append((int(r['bar']), event(r, sd), float(close[int(r['bar'])])))
    if ex is not None:
        out.append((ab, 'the ADVERSE extreme - MAE %.4f' % abs(pct(opn, sd, ap)), ap))
        out.append((vb, 'the favourable extreme - MFE %.4f' % pct(opn, sd, vp), vp))
        out.append((int(ex), 'THIS LEG CLOSES on %s, realised %+.4f'
                    % (lg['verdict'], pct(opn, sd, float(close[int(ex) + 1]))),
                    float(close[int(ex)])))
    for bar, ev, px in sorted(out, key=lambda x: x[0]):
        print('| %s | %+.1f | %s | %.6f | %+.4f |'
              % (ln.U(bar), (bar - opn) * 5 / 60.0, ev, px, pct(opn, sd, px)))
    print('')

print('## the MAE / MFE aggregate over the %d legs' % len(legs))
print('')
print('| leg | the open | dir | the exit | MAE % | MFE % | realised % | drag % | net % |')
print('|---|---|---|---|---|---|---|---|---|')
tot = dict(mae=0.0, mfe=0.0, rel=0.0, drg=0.0, n=0)
for n, lg in enumerate(legs, 1):
    opn, sd, ex = lg['opn'], lg['side'], lg['exit']
    if ex is None:
        print('| %d | %s | %s | - | - | - | - | - | - |'
              % (n, ln.U(opn), 'LONG' if sd > 0 else 'SHORT'))
        continue
    ab, ap, vb, vp = mae_mfe(opn, ex, sd)
    mae, mfe = abs(pct(opn, sd, ap)), pct(opn, sd, vp)
    rel = pct(opn, sd, float(close[int(ex) + 1]))
    print('| %d | %s | %s | %s | %.4f | %+.4f | %+.4f | %.4f | %+.4f |'
          % (n, ln.U(opn), 'LONG' if sd > 0 else 'SHORT', ln.U(ex), mae, mfe, rel, DRAG,
             rel - DRAG))
    tot['mae'] += mae; tot['mfe'] += mfe; tot['rel'] += rel; tot['drg'] += DRAG; tot['n'] += 1
print('| TOTAL %d legs | | | | %.4f | %+.4f | %+.4f | %.4f | %+.4f |'
      % (tot['n'], tot['mae'], tot['mfe'], tot['rel'], tot['drg'], tot['rel'] - tot['drg']))
if tot['n']:
    print('| MEAN per leg | | | | %.4f | %+.4f | %+.4f | %.4f | %+.4f |'
          % (tot['mae'] / tot['n'], tot['mfe'] / tot['n'], tot['rel'] / tot['n'],
             tot['drg'] / tot['n'], (tot['rel'] - tot['drg']) / tot['n']))
print('')
print('| the read | value |')
print('|---|---|')
print('| legs with an exhaust | %d of %d |' % (tot['n'], len(legs)))
print('| MFE collected | %s |' % ('%.1f%%' % (tot['rel'] / tot['mfe'] * 100.0)
                                  if tot['mfe'] > 0 else 'n/a - summed MFE is not positive'))
print('| drag as a share of summed MFE | %s |'
      % ('%.1f%%' % (tot['drg'] / tot['mfe'] * 100.0) if tot['mfe'] > 0 else 'n/a'))
