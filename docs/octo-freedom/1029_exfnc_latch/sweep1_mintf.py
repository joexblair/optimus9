"""STEP 1 OF THE NET% SWEEP: LIN2_BARRAGE_MIN_TF, on 2026-08-30 .. 2026-09-06.

Joe 1029: *"LIN2_BARRAGE_MIN_TF should be step 1"*, and the target is *"net%"*.

BOTH MIN_TF_MODE ARMS ARE IN IT, because his LIN2_BARRAGE_MAX_TF 15 may have unblocked the floor
arm: the floor at 9 used to leave ws9..ws12, four lines, against LIN2_BARRAGE_LINES 6 - empty. At a
ceiling of 15 it leaves ws9..ws15, seven lines, so 6 is now satisfiable. That is measured here, not
assumed.

THE CONTROL ROW is the banked config re-run inside this driver and scored over 2026-08-30 alone,
checked against the +2.2658 net of its 6 legs in 1029_exfnc_latch/latch_off3.md. A hash-keyed cache
or a stale knob fails silently otherwise.

THE CANDIDATE LIST IS COMPUTED ONCE PER SIDE and served to every combo. That is sound, not a
shortcut: `barrage_candidates` applies NO threshold - its own docstring says the three thresholds
are applied by `barrage` on top of it "which is what lets a sweep vary them without a second copy
of the rule". It DOES depend on LIN2_PSEUDO_MIN_TF through its ex-fence read, which is fixed at 4
for this step and must be recomputed when the pseudo sweep varies it.

EVERY LEG IS SCORED, no cap and no horizon: the chain walks from the window's first bar to its last
and each leg's net is realised minus the 0.1975% round-trip drag, which keeps its own column.
"""
import os, sys, io
import numpy as np
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1027_pseudo_closed')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln, v4_knobs as K, v4_rcfg_sweep as RS, v4_closed_prev as CP
import v4_l2_proxy as PX, v4_lineage2 as L2, v4_l2_cadence as CAD, v4_chain as CH
import pseudo_closed as PC
from v4_backstop_trades import prices
sys.stderr = _e

WA, WB = ln.K('2026-08-30 00:00:00'), ln.K('2026-09-06 23:59:55')
CA, CB = ln.K('2026-08-30 00:00:00'), ln.K('2026-08-30 23:59:55')
#   THE CONTROL IS A FULL-DAY NUMBER ON THE PRODUCED OPEN, from chain_open_day.md arm A:
#   20 legs, net -0.3014%. The old control was +2.2658 over SIX legs, which was my cap on the
#   diagnostic and not the day - it would have passed a run that silently truncated the chain.
CONTROL_NET, CONTROL_LEGS = -0.3014, 20
MINTF_GRID = [0, 1, 3, 5, 7, 9, 12]
DRAG = CH.DRAG_PCT

close, phi, plo = prices()
E = RS.load((RS.K0, RS.R0, RS.S0))
C = CP.ladder(E)
CL = CP.arm_lines(E)
MGL = {t: CP.line('ws%dMage' % t, t * 60) for t in range(1, 13)}
MGE = {t: ln.line('ws%dMage' % t) for t in range(1, 13)}
TOP = max(int(K.L2_MOM_MAXTF), int(K.LIN2_BARRAGE_MAX_TF))
_prod = CAD.chain_open(MGL, WA)
assert _prod is not None, 'no chain open at or before the window start'
LO = min(int(_prod[0]), int(WA))
IDX = np.arange(LO, WB + 1)
PS = {}
for t in range(int(K.LIN2_PSEUDO_MIN_TF), TOP + 1):
    PS[t] = np.full(len(close), np.nan)
    PS[t][IDX] = PC.series(close, t, IDX)
BD = PX.Board(C, E, MG=MGL, MGE=MGE, PS=PS)

#   ONE CANDIDATE LIST PER SIDE, served to every combo - see the module docstring.
_CAND = {sd: CAD.barrage_candidates(BD, sd) for sd in (-1, +1)}
_orig_cands = CAD.barrage_candidates


def _served(BD_, side_, cand=None):
    return cand if cand is not None else _CAND[int(side_)]


CAD.barrage_candidates = _served


def one():
    """One combo: the whole chain over the window on the CURRENT knobs. -> (score, zero, opening)"""
    lg, zero, op = CH.legs(CL, BD, close, phi, plo, WA, WB, MG=MGL)
    return CH.score(lg), zero, op


print('# STEP 1 OF THE NET%% SWEEP: LIN2_BARRAGE_MIN_TF, both MIN_TF_MODE arms')
print('# WINDOW %s .. %s | TAPE %d bars | RULED_OK %s'
      % (ln.U(WA), ln.U(WB), len(close), K.RULED_OK))
print('# HELD AT BANK: LIN2_BARRAGE_MAX_TF %d, LINES %d, TOL %ds, FIT %r,'
      ' LIN2_PSEUDO_MIN_TF %d, LIN2_LATCH_EXFNC_ON %d'
      % (K.LIN2_BARRAGE_MAX_TF, K.LIN2_BARRAGE_LINES, K.LIN2_BARRAGE_TOL_S, K.LIN2_BARRAGE_FIT,
         K.LIN2_PSEUDO_MIN_TF, K.LIN2_LATCH_EXFNC_ON))
print('# DRAG %.4f%% per round trip, its own column and its own total.' % DRAG)
print('# net %% = summed realised %% minus summed drag. Every leg scored, no cap, no horizon.')
print('')

# ---- the control -----------------------------------------------------------------------------
K.LIN2_BARRAGE_MIN_TF = 9
K.LIN2_BARRAGE_MIN_TF_MODE = 'membership'
_lgc, _zc, _opc = CH.legs(CL, BD, close, phi, plo, CA, CB, MG=MGL)
cs = CH.score(_lgc)
print('## the control row - the banked config over 2026-08-30 alone')
print('')
print('| the read | expected | this run | match |')
print('|---|---|---|---|')
print('| legs | %d | %d | %s |' % (CONTROL_LEGS, cs['n'],
                                   'yes' if cs['n'] == CONTROL_LEGS else '** NO **'))
print('| net %% | %+.4f | %+.4f | %s |'
      % (CONTROL_NET, cs['net'], 'yes' if abs(cs['net'] - CONTROL_NET) < 5e-4 else '** NO **'))
print('')
if cs['n'] != CONTROL_LEGS or abs(cs['net'] - CONTROL_NET) >= 5e-4:
    print('** THE CONTROL FAILED. Every row below is suspect. **')
    print('')

# ---- the grid ---------------------------------------------------------------------------------
print('## the grid, ordered by MIN_TF then mode')
print('')
print('| min_tf | mode | legs | barrage exits | MAE %% | MFE %% | realised %% | drag %% | net %% |'
      ' net %% per leg | legs net-positive |')
print('|---|---|---|---|---|---|---|---|---|---|---|')
rows = []
for m in ('membership', 'floor'):
    for v in MINTF_GRID:
        K.LIN2_BARRAGE_MIN_TF = v
        K.LIN2_BARRAGE_MIN_TF_MODE = m
        s, z, op = one()
        rows.append((v, m, s, z, op))
for v in MINTF_GRID:
    for m in ('membership', 'floor'):
        s = [r[2] for r in rows if r[0] == v and r[1] == m][0]
        print('| %d | %s | %d | %d | %.4f | %+.4f | %+.4f | %.4f | %+.4f | %+.4f | %d |'
              % (v, m, s['n'], s['barr'], s['mae'], s['mfe'], s['rel'], s['drag'], s['net'],
                 s['net'] / s['n'] if s['n'] else 0.0, s['win']))
print('')

print('## the zero-length legs - exhaust bar BEFORE the open bar')
print('')
print('| the read | value |')
print('|---|---|')
_Z = [(z['opn'], z['exit'], z['ctype']) for _v, _m, _s, zz, _o in rows for z in zz]
print('| zero-length legs seen across every combo | %d |' % len(_Z))
print('| distinct (open, exit) pairs | %d |' % len(set((a0, b0) for a0, b0, _c in _Z)))
print('')
if _Z:
    print('| the open bar | the exit bar | ended by | times seen |')
    print('|---|---|---|---|')
    seen = {}
    for a0, b0, c0 in _Z:
        seen[(a0, b0, c0)] = seen.get((a0, b0, c0), 0) + 1
    for (a0, b0, c0) in sorted(seen):
        print('| %s | %s | %s | %d |' % (ln.U(a0), ln.U(b0), c0, seen[(a0, b0, c0)]))
    print('')
    print('| the read | value |')
    print('|---|---|')
    print('| NOT scored | they span no bars, so they carry no MAE, MFE or realised |')
    print('| NOT charged drag | whether a trade opening and closing on one cadence bar pays the'
          ' 0.1975%% is yours to rule |')
    print('| if they DID pay drag | the net of each row below would drop by 0.1975%% per'
          ' zero-length leg in that row |')
    print('')

best = max(rows, key=lambda r: r[2]['net'])
print('| the read | value |')
print('|---|---|')
print('| the highest net %% | %+.4f at min_tf %d, mode %s |' % (best[2]['net'], best[0], best[1]))
print('| the banked pair, min_tf 9 membership | %+.4f |'
      % [r[2]['net'] for r in rows if r[0] == 9 and r[1] == 'membership'][0])
fl9 = [r[2] for r in rows if r[0] == 9 and r[1] == 'floor'][0]
print('| the floor arm at min_tf 9 | %d legs, %d barrage exits, net %+.4f%% |'
      % (fl9['n'], fl9['barr'], fl9['net']))
print('| the floor arm at 9 was EMPTY at ceiling 12 | at ceiling %d it leaves ws9..ws%d, %d lines,'
      ' against LINES %d |'
      % (K.LIN2_BARRAGE_MAX_TF, K.LIN2_BARRAGE_MAX_TF, K.LIN2_BARRAGE_MAX_TF - 9 + 1,
         K.LIN2_BARRAGE_LINES))
