"""THE CHAIN'S OPEN, PICKED CAUSALLY. Joe 1029: *"did you pick that time causally? if not, re-do"*.

WHAT WAS WRONG WITH 23:53:50. The bar itself is produced causally - every test in the firing mech
reads only bars at or before the firing bar. But I SELECTED it from a 23:00..00:30 span that I
chose, and I justified it by being 0.8 min from the "2353" he quoted. That is fitting to a
timestamp he gave as an estimate, which is exactly what his own rule forbids.

THE CAUSAL RULE, with no span and no cap: the chain's first open is the EARLIEST firing-mech fire
on the tape. Every later fire is blocked while a trade is open - his first condition, *"there is no
trade open"* - so the leg that is live at any later bar follows from walking the chain forward from
that first fire. Nothing is chosen; it is derived.

NO STOP IS WIRED YET (task 39), so after the first open the firing mech never fires again and the
chain simply alternates. The leg live at 2026-08-30 00:00:00 therefore depends on the whole run
from the first fire - which is a real dependency, stated rather than hidden.

THIS PRINTS, in order:
    1  the earliest fire on the tape, and the next few, so the selection can be seen
    2  the chain from that fire, every leg, to the end of 2026-08-30
    3  which leg is live at 2026-08-30 00:00:00 - the "incoming trade" his option B asks for
"""
import os, sys, io
import numpy as np
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1027_pseudo_closed')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln, v4_knobs as K, v4_rcfg_sweep as RS, v4_closed_prev as CP
import v4_l2_proxy as PX, v4_l2_cadence as CAD, v4_chain as CH
import pseudo_closed as PC
from v4_backstop_trades import prices
from optimus9.analysis.jig import oob_ib_cross
sys.stderr = _e

WA = ln.K('2026-08-30 00:00:00')
WB = ln.K('2026-08-30 23:59:55')
close, phi, plo = prices()
E = RS.load((RS.K0, RS.R0, RS.S0))
B1E = np.asarray(ln.line('ws1b'), float)
MGEM = {t: np.asarray(ln.line('ws%dMage' % t), float) for t in range(1, 13)}

print('# THE CHAIN OPEN, PICKED CAUSALLY - the earliest fire on the tape, no span, no cap')
print('# TAPE %d bars | LG_TAPE_END %s | RULED_OK %s'
      % (len(close), os.environ['LG_TAPE_END'], K.RULED_OK))
print('# KNOBS: TF %d | LINES %d | LOOKBACK %d s | XWOB %d bars'
      % (K.LIN2_CHAIN_OPEN_TF, K.LIN2_CHAIN_OPEN_LINES, K.LIN2_CHAIN_OPEN_LOOKBACK_S,
         K.LIN2_CHAIN_OPEN_XWOB))
print('# every read is EMERGING. the anchor is the extremum over [run start, FIRING BAR].')
print('')

# ---- 1. every fire on the tape, earliest first ------------------------------------------------
tf, need = int(K.LIN2_CHAIN_OPEN_TF), int(K.LIN2_CHAIN_OPEN_LINES)
hi = int(K.L2_MOM_MAXTF)
lb = int(K.LIN2_CHAIN_OPEN_LOOKBACK_S) // 5
w = max(1, int(K.LIN2_CHAIN_OPEN_XWOB))
band = list(range(tf + 1, hi + 1))
m5 = MGEM[tf]
fires = []
for c, cf, sd in oob_ib_cross(B1E, K.OOB_HI, K.OOB_LO, w):
    f = int(cf) if w > 1 else int(c)
    gate = K.oob_mask(m5, int(sd))
    if not (bool(gate[f]) or bool(gate[max(0, f - lb):f + 1].any())):
        continue
    j = f if gate[f] else None
    if j is None:
        for i in range(f, max(0, f - lb) - 1, -1):
            if gate[i]:
                j = i
                break
    if j is None:
        continue
    i = j
    while i > 0 and gate[i - 1]:
        i -= 1
    seg = m5[i:j + 1]
    if not np.isfinite(seg).any():
        continue
    k = i + (int(np.nanargmax(seg)) if sd > 0 else int(np.nanargmin(seg)))
    assert k <= f, 'the anchor is after the firing bar - that read is lookahead'
    v0 = float(m5[k])
    got = [t for t in band
           if np.isfinite(MGEM[t][k])
           and ((float(MGEM[t][k]) < v0) if sd > 0 else (float(MGEM[t][k]) > v0))]
    if len(got) >= need:
        fires.append((f, int(sd), k, v0, tuple(got)))
fires.sort()

print('## the first 12 fires on the tape, earliest first')
print('')
print('| # | the firing bar | candidate side | the trade side | the anchor bar |'
      ' ws%dMage at the anchor | lines away |' % tf)
print('|---|---|---|---|---|---|---|')
for n, (f, sd, k, v0, got) in enumerate(fires[:12], 1):
    print('| %d | %s | %s | %s | %s | %.2f | %d of %d |'
          % (n, ln.U(f), 'HIGH' if sd > 0 else 'LOW', 'SHORT' if sd > 0 else 'LONG',
             ln.U(k), v0, len(got), len(band)))
print('')
print('| the read | value |')
print('|---|---|')
print('| fires on the whole tape | %d |' % len(fires))
print('| the EARLIEST fire | %s |' % ln.U(fires[0][0]))
print('| its trade side | %s |' % ('SHORT' if fires[0][1] > 0 else 'LONG'))
print('| fires at or before %s | %d |' % (ln.U(WA), sum(1 for x in fires if x[0] <= WA)))
print('| the one I fitted to his "2353" | 2026-08-29 23:53:50 |')
print('| the one the backward scan picked | 2026-08-29 23:56:00 |')
print('')

# ---- 2. the chain from the earliest fire -----------------------------------------------------
F0 = int(fires[0][0])
TOP = max(int(K.L2_MOM_MAXTF), int(K.LIN2_BARRAGE_MAX_TF))
IDX = np.arange(F0, WB + 1)
PS = {}
for t in range(int(K.LIN2_PSEUDO_MIN_TF), TOP + 1):
    PS[t] = np.full(len(close), np.nan)
    PS[t][IDX] = PC.series(close, t, IDX)
C = CP.ladder(E)
CL = CP.arm_lines(E)
MGL = {t: CP.line('ws%dMage' % t, t * 60) for t in range(1, 13)}
BD = PX.Board(C, E, MG=MGL, MGE=MGEM, PS=PS)
lg, zero, op = CH.legs(CL, BD, close, phi, plo, F0, WB, MG=MGEM, B1=B1E)
sc = CH.score(lg)

print('## the chain from the earliest fire %s to %s' % (ln.U(F0), ln.U(WB)))
print('')
print('| leg | the open | dir | the exit | ended by | held min | MAE % | MFE % | realised % |'
      ' drag % | net % | live at 08-30 00:00:00? |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|')
live = None
for i, x in enumerate(lg, 1):
    d = 'LONG' if x['side'] > 0 else 'SHORT'
    inw = x['exit'] is not None and x['opn'] <= WA <= x['exit']
    if inw:
        live = (i, x)
    if x['exit'] is None:
        print('| %d | %s | %s | - | no exhaust | - | - | - | - | - | - | %s |'
              % (i, ln.U(x['opn']), d, 'YES' if x['opn'] <= WA else 'no'))
        continue
    print('| %d | %s | %s | %s | %s | %.1f | %.4f | %+.4f | %+.4f | %.4f | %+.4f | %s |'
          % (i, ln.U(x['opn']), d, ln.U(x['exit']), x['ctype'], x['held_min'], x['mae'],
             x['mfe'], x['rel'], CH.DRAG_PCT, x['rel'] - CH.DRAG_PCT, 'YES' if inw else 'no'))
print('| TOTAL %d legs | | | | | %.1f | %.4f | %+.4f | %+.4f | %.4f | %+.4f | |'
      % (sc['n'], sc['held'], sc['mae'], sc['mfe'], sc['rel'], sc['drag'], sc['net']))
print('')
print('| the read | value |')
print('|---|---|')
print('| the chain opens | %s, %s |' % (ln.U(op['bar']), 'SHORT' if op['side'] < 0 else 'LONG'))
print('| legs to the end of 2026-08-30 | %d |' % sc['n'])
print('| the leg LIVE at %s | %s |'
      % (ln.U(WA), ('leg %d, opened %s %s' % (live[0], ln.U(live[1]['opn']),
                                              'LONG' if live[1]['side'] > 0 else 'SHORT'))
         if live else 'none - no leg spans that bar'))
print('| zero-length legs | %d |' % len(zero))
