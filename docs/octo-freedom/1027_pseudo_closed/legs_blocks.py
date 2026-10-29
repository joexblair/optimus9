"""THE CHAIN'S LEGS AS BLOCKS, ON THE PSEUDO BOARD. Joe 1028:

    "each leg can start at the end of the previous leg. ie leg 2's first row is
     '08-30 00:21 >>> THIS LEG OPENS SHORT' / drop 'min from this open' / add a 'baton candidates'
     column that prints 'ws?: 82, ws?:80, etc' / print the next 3 trades / create a summary report
     that shows 1 row per leg. include maemfe and net per row, tallied at the bottom"

HIS THREE CHANGES from legs3_blocks.py:
    1  NO INCOMING ROWS. A leg's block starts at its own open. The chain's continuity is in the
       block header and in the summary, not in repeated rows.
    2  `min from THIS open` is gone.
    3  `baton candidates` is a new column: every candidate TF offered at that bar with its r value
       on the board that answered it, as `ws5: 63.61, ws6: 68.77`.

BLOCKS_FROM / N_LEGS are his asks: the first 3, then the next 3. The summary covers every leg
walked, not just the blocks printed.

THE BOARD: ws1..ws3 keep their current reads; ws4 upward read PSEUDO-CLOSED for the ex-fence state
and for the value quoted. LIN2_PSEUDO_MIN_TF 4, his value.

THE EXHAUST BAR IS THE REV-TRADE BAR: the leg closes there and the opposite side opens at that
bar + 1. `realised` is priced at that fill bar, which is one bar after the block's last row.
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
N_LEGS = int(os.environ.get('W_LEGS', '6'))         # his ask: the first 3, then the next 3
BLOCKS_FROM = int(os.environ.get('W_BLOCKS_FROM', '4'))
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
    return 'rev lift-off %s / pseudo %s' % (last_rev('lift', tf, sd, bar),
                                            last_rev('pseudo', tf, sd, bar))


def tag(tf):
    return ('ws' if BD.state_src(int(tf)) == 'pseudo' else 'cws') + str(int(tf))


def cand_col(r):
    """his new column: every candidate TF offered at this bar with its r value."""
    cd = r.get('cands')
    b = r.get('bar')
    if cd is None or b is None:
        return '-'
    if cd == ():
        return 'none offered'
    return ', '.join('%s: %.2f' % (tag(t), BD.value(int(t), int(b))) for t in cd)


def event(r, sd):
    st = r['stage']
    why = str(r['why']).replace('|', '\\|')
    rd = r.get('rider')
    head = st if not rd else '%s rider %s' % (st, tag(rd))
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


def ended_by(lg):
    ex = [r for r in lg['rows'] if r['stage'] == 'EXHAUST']
    if not ex:
        return 'no exhaust'
    return str(ex[-1].get('ctype') or 'retest')


print('# THE CHAIN\'S LEGS AS BLOCKS, %s' % DAY)
print('# TAPE %d bars | LG_TAPE_END %s | RULED_OK %s'
      % (len(close), os.environ['LG_TAPE_END'], K.RULED_OK))
print('# BLOCKS printed: legs %d..%d. SUMMARY: every leg walked, %d of them.'
      % (BLOCKS_FROM, len(legs), len(legs)))
print('# BOARD: ws1..ws%d keep their reads (cws); ws%d.. read PSEUDO (ws) for ex-fence and for the'
      ' quoted value. LIN2_PSEUDO_MIN_TF %d.' % (MINTF - 1, MINTF, MINTF))
print('# BARRAGE: LIN2_BARRAGE_MIN_TF %d, LINES %d, TOL %ds, MIN_TF_MODE %r - the pine-emit'
      ' settings.' % (K.LIN2_BARRAGE_MIN_TF, K.LIN2_BARRAGE_LINES, K.LIN2_BARRAGE_TOL_S,
                      K.LIN2_BARRAGE_MIN_TF_MODE))
print('# EACH LEG STARTS AT ITS OWN OPEN. The previous leg\'s rows are not repeated - his 1028')
print('#   ruling. The open is 1 bar after the previous exhaust, which is the rev-trade bar.')
print('# baton candidates: every candidate TF offered at that bar with its r value on the board')
print('#   that answered it. "none offered" is a NO PASS with no candidate inside lin_hop %d.'
      % K.L2_LIN_HOP)
print('# realised is priced at the fill bar = exhaust + 1, one bar after the block\'s last row.')
print('# ex-fence is the %.0f/%.0f fence from RMOM_FNC; oob is 15/85.'
      % (100 - K.RMOM_FNC, K.RMOM_FNC))
print('')

for n, lg in enumerate(legs, 1):
    if n < BLOCKS_FROM:
        continue
    opn, sd, ex = lg['opn'], lg['side'], lg['exit']
    dirn = 'LONG' if sd > 0 else 'SHORT'
    ab, ap, vb, vp = mae_mfe(opn, ex, sd)
    bits = ['## leg %d of %d - %s %s' % (n, len(legs), DAY, dirn), 'opens %s' % ln.U(opn)]
    if ex is None:
        bits.append('NO EXHAUST to the window end')
    else:
        bits.append('exits %s on %s' % (ln.U(ex), ended_by(lg)))
        bits.append('MAE %.4f' % abs(pct(opn, sd, ap)))
        bits.append('MFE %.4f' % pct(opn, sd, vp))
        bits.append('realised %+.4f' % pct(opn, sd, float(close[int(ex) + 1])))
        bits.append('held %.1f min' % ((ex - opn) * 5 / 60.0))
    bits.append('CONTINUITY: %s' % ('the first leg - opens at the window start' if n == 1 else
                                    'UNBROKEN - 1 bar after leg %d exhaust %s'
                                    % (n - 1, ln.U(legs[n - 2]['exit']))))
    print('   '.join(bits))
    print('')
    print('| ts | event | baton candidates | pxs | pct for THIS leg |')
    print('|---|---|---|---|---|')
    out = [(opn, '>>> THIS LEG OPENS %s' % dirn, '-', float(close[opn]))]
    for r in lg['rows']:
        if r.get('bar') is None:
            out.append((opn, 'NOTE %s - %s' % (r['stage'], str(r['why']).replace('|', '\\|')),
                        '-', float(close[opn])))
            continue
        out.append((int(r['bar']), event(r, sd), cand_col(r), float(close[int(r['bar'])])))
    if ex is not None:
        out.append((ab, 'the ADVERSE extreme - MAE %.4f' % abs(pct(opn, sd, ap)), '-', ap))
        out.append((vb, 'the favourable extreme - MFE %.4f' % pct(opn, sd, vp), '-', vp))
        out.append((int(ex), 'THIS LEG CLOSES on %s, realised %+.4f'
                    % (ended_by(lg), pct(opn, sd, float(close[int(ex) + 1]))), '-',
                    float(close[int(ex)])))
    for bar, ev, cc, px in sorted(out, key=lambda x: x[0]):
        print('| %s | %s | %s | %.6f | %+.4f |' % (ln.U(bar), ev, cc, px, pct(opn, sd, px)))
    print('')

# ---- the summary, one row per leg -------------------------------------------------------------
print('## the summary - one row per leg, every leg walked')
print('')
print('| leg | the open | dir | the exit | ended by | held min | the rider chain | MAE % |'
      ' MFE % | realised % | drag % | net % |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|')
T = dict(mae=0.0, mfe=0.0, rel=0.0, drg=0.0, n=0, mins=0.0, win=0)
for n, lg in enumerate(legs, 1):
    opn, sd, ex = lg['opn'], lg['side'], lg['exit']
    dirn = 'LONG' if sd > 0 else 'SHORT'
    seen, chain = set(), []
    for r in lg['rows']:
        rd = r.get('rider')
        if rd and (not chain or chain[-1] != tag(rd)):
            chain.append(tag(rd))
    ch = ' > '.join(chain) if chain else '-'
    if ex is None:
        print('| %d | %s | %s | - | no exhaust | - | %s | - | - | - | - | - |'
              % (n, ln.U(opn), dirn, ch))
        continue
    ab, ap, vb, vp = mae_mfe(opn, ex, sd)
    mae, mfe = abs(pct(opn, sd, ap)), pct(opn, sd, vp)
    rel = pct(opn, sd, float(close[int(ex) + 1]))
    mins = (ex - opn) * 5 / 60.0
    print('| %d | %s | %s | %s | %s | %.1f | %s | %.4f | %+.4f | %+.4f | %.4f | %+.4f |'
          % (n, ln.U(opn), dirn, ln.U(ex), ended_by(lg), mins, ch, mae, mfe, rel, DRAG,
             rel - DRAG))
    T['mae'] += mae; T['mfe'] += mfe; T['rel'] += rel; T['drg'] += DRAG
    T['n'] += 1; T['mins'] += mins; T['win'] += 1 if rel - DRAG > 0 else 0
print('| TOTAL %d legs | | | | | %.1f | | %.4f | %+.4f | %+.4f | %.4f | %+.4f |'
      % (T['n'], T['mins'], T['mae'], T['mfe'], T['rel'], T['drg'], T['rel'] - T['drg']))
if T['n']:
    print('| MEAN per leg | | | | | %.1f | | %.4f | %+.4f | %+.4f | %.4f | %+.4f |'
          % (T['mins'] / T['n'], T['mae'] / T['n'], T['mfe'] / T['n'], T['rel'] / T['n'],
             T['drg'] / T['n'], (T['rel'] - T['drg']) / T['n']))
print('')
print('| the read | value |')
print('|---|---|')
print('| legs with an exhaust | %d of %d |' % (T['n'], len(legs)))
print('| legs net-positive after drag | %d of %d |' % (T['win'], T['n']))
print('| MFE collected | %s |' % ('%.1f%%' % (T['rel'] / T['mfe'] * 100.0)
                                  if T['mfe'] > 0 else 'n/a - summed MFE is not positive'))
print('| drag as a share of summed MFE | %s |'
      % ('%.1f%%' % (T['drg'] / T['mfe'] * 100.0) if T['mfe'] > 0 else 'n/a'))
print('| summed drag in its own right | %.4f%% over %d round trips |' % (T['drg'], T['n']))
print('')
print('| ended by | legs | summed realised % | summed net % |')
print('|---|---|---|---|')
by = {}
for n, lg in enumerate(legs, 1):
    if lg['exit'] is None:
        continue
    k = ended_by(lg)
    rel = pct(lg['opn'], lg['side'], float(close[int(lg['exit']) + 1]))
    d = by.setdefault(k, [0, 0.0])
    d[0] += 1; d[1] += rel
for k in sorted(by):
    print('| %s | %d | %+.4f | %+.4f |' % (k, by[k][0], by[k][1], by[k][1] - by[k][0] * DRAG))
