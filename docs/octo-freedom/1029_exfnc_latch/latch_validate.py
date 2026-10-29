"""THE PER-LINE EX-FENCE LATCH: the regression, the ceiling change, and the latch's own delta.

THREE THINGS THIS PROVES, in order:

    1  REGRESSION. With LIN2_LATCH_EXFNC_ON 0 the 6 legs on 2026-08-30 must be BIT-IDENTICAL to
       the banked run in 1027_pseudo_closed/legs_blocks.md. If they are not, the routing through
       `baton_ex_fence` changed something it should not have.
    2  THE CEILING. LIN2_BARRAGE_MAX_TF 15 against the old shared L2_MOM_MAXTF 12, over his
       08-30..09-06 window, so the maxTF sweep has its own before-and-after.
    3  THE LATCH. The same 6 legs with the latch on, and the per-line latch state so the mech can
       be read rather than inferred.

THE PSEUDO BAND IS EXTENDED TO THE BARRAGE'S CEILING. The barrage at maxTF 15 reads ex-fence on
ws13, ws14 and ws15; without pseudo lines for them those reads fall back to closed. ws13 and ws14
pseudo are NOT bit-exact to the product's closed read (1440/13 = 110.77, 1440/14 = 102.86), which
is printed in the header rather than hidden.
"""
import os, sys, io
import numpy as np
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1027_pseudo_closed')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln, v4_knobs as K, v4_rcfg_sweep as RS, v4_closed_prev as CP
import v4_l2_proxy as PX, v4_lineage2 as L2, v4_l2_cadence as CAD
import pseudo_closed as PC
from v4_backstop_trades import prices
sys.stderr = _e

DAY = '2026-08-30'
A, B = ln.K('%s 00:00:00' % DAY), ln.K('%s 23:59:55' % DAY)
WA, WB = ln.K('2026-08-30 00:00:00'), ln.K('2026-09-06 23:59:55')
MINTF = int(K.LIN2_PSEUDO_MIN_TF)
TOP = max(int(K.L2_MOM_MAXTF), int(K.LIN2_BARRAGE_MAX_TF))
N_LEGS = 6
DRAG = 0.1975

close, phi, plo = prices()
E = RS.load((RS.K0, RS.R0, RS.S0))
C = CP.ladder(E)
CL = CP.arm_lines(E)
MGL = {t: CP.line('ws%dMage' % t, t * 60) for t in range(1, 13)}
MGE = {t: ln.line('ws%dMage' % t) for t in range(1, 13)}
IDX = np.arange(WA, WB + 1)
PS = {}
for t in range(MINTF, TOP + 1):
    PS[t] = np.full(len(close), np.nan)
    PS[t][IDX] = PC.series(close, t, IDX)


def board():
    return PX.Board(C, E, MG=MGL, MGE=MGE, PS=PS)


def pct(opn, sd, px):
    o = float(close[int(opn)])
    return sd * (float(px) - o) / o * 100.0


def mae_mfe(opn, ex, sd):
    lo, hi = int(opn), int(ex)
    H = np.asarray(phi[lo:hi + 1], float); L = np.asarray(plo[lo:hi + 1], float)
    if sd > 0:
        return (float(np.nanmin(L)), float(np.nanmax(H)))
    return (float(np.nanmax(H)), float(np.nanmin(L)))


def ended_by(rows):
    ex = [r for r in rows if r['stage'] == 'EXHAUST']
    return str(ex[-1].get('ctype') or 'retest') if ex else 'no exhaust'


def chain(BD):
    legs, side, frm, prev = [], +1, int(A), None
    while len(legs) < N_LEGS:
        v, bar, rows = L2.walk(CL, BD, close, side, frm, B)
        opn = int(A) if prev is None else int(prev) + 1
        legs.append(dict(opn=opn, side=side, verdict=v, exit=bar, rows=rows))
        if bar is None:
            break
        prev = int(bar); frm, side = int(bar), -side
    return legs


def summary(legs, tag):
    print('### %s' % tag)
    print('')
    print('| leg | the open | dir | the exit | ended by | held min | the rider chain | MAE % |'
          ' MFE % | realised % | drag % | net % |')
    print('|---|---|---|---|---|---|---|---|---|---|---|---|')
    T = dict(mae=0.0, mfe=0.0, rel=0.0, drg=0.0, n=0, mins=0.0, win=0)
    for n, lg in enumerate(legs, 1):
        opn, sd, ex = lg['opn'], lg['side'], lg['exit']
        dirn = 'LONG' if sd > 0 else 'SHORT'
        ch, seen = [], None
        for r in lg['rows']:
            rd = r.get('rider')
            if rd and (not ch or ch[-1] != rd):
                ch.append(rd)
        chs = ' > '.join('ws%d' % x for x in ch) if ch else '-'
        if ex is None:
            print('| %d | %s | %s | - | no exhaust | - | %s | - | - | - | - | - |'
                  % (n, ln.U(opn), dirn, chs))
            continue
        ap, vp = mae_mfe(opn, ex, sd)
        mae, mfe = abs(pct(opn, sd, ap)), pct(opn, sd, vp)
        rel = pct(opn, sd, float(close[int(ex) + 1]))
        mins = (ex - opn) * 5 / 60.0
        print('| %d | %s | %s | %s | %s | %.1f | %s | %.4f | %+.4f | %+.4f | %.4f | %+.4f |'
              % (n, ln.U(opn), dirn, ln.U(ex), ended_by(lg['rows']), mins, chs, mae, mfe, rel,
                 DRAG, rel - DRAG))
        T['mae'] += mae; T['mfe'] += mfe; T['rel'] += rel; T['drg'] += DRAG
        T['n'] += 1; T['mins'] += mins; T['win'] += 1 if rel - DRAG > 0 else 0
    print('| TOTAL %d legs | | | | | %.1f | | %.4f | %+.4f | %+.4f | %.4f | %+.4f |'
          % (T['n'], T['mins'], T['mae'], T['mfe'], T['rel'], T['drg'], T['rel'] - T['drg']))
    print('')
    return T


print('# THE PER-LINE EX-FENCE LATCH - the regression, the ceiling, and the latch delta')
print('# TAPE %d bars | LG_TAPE_END %s | RULED_OK %s'
      % (len(close), os.environ['LG_TAPE_END'], K.RULED_OK))
print('# KNOBS: LIN2_LATCH_EXFNC_ON %d | LIN2_EXFNC_LATCH_WOB %d bars = %d s |'
      ' LIN2_BARRAGE_MAX_TF %d | L2_MOM_MAXTF %d'
      % (K.LIN2_LATCH_EXFNC_ON, K.LIN2_EXFNC_LATCH_WOB, K.LIN2_EXFNC_LATCH_WOB * 5,
         K.LIN2_BARRAGE_MAX_TF, K.L2_MOM_MAXTF))
print('# PSEUDO BAND ws%d..ws%d. ws13 and ws14 pseudo are NOT bit-exact to the closed read'
      ' (1440/13 = 110.77, 1440/14 = 102.86).' % (MINTF, TOP))
print('# BARRAGE: MIN_TF %d, LINES %d, TOL %ds, MODE %r, FIT %r'
      % (K.LIN2_BARRAGE_MIN_TF, K.LIN2_BARRAGE_LINES, K.LIN2_BARRAGE_TOL_S,
         K.LIN2_BARRAGE_MIN_TF_MODE, K.LIN2_BARRAGE_FIT))
print('')

# ---- 2. the ceiling, over his 08-30..09-06 window -------------------------------------------
print('## the barrage ceiling, 2026-08-30 00:00:00 .. 2026-09-06 23:59:55')
print('')
print('| max_tf | side | cadences | first | last |')
print('|---|---|---|---|---|')
BD0 = board()
CND = {sd: CAD.barrage_candidates(BD0, sd) for sd in (-1, +1)}
tot = {}
for mt in (12, 15):
    for sd in (+1, -1):
        got = CAD.barrage(BD0, sd, WA, WB, max_tf=mt, cand=CND[sd])
        bars = sorted(int(r[0]) for r in got)
        tot[(mt, sd)] = bars
        print('| %d | %s | %d | %s | %s |'
              % (mt, 'HIGH' if sd > 0 else 'LOW', len(bars),
                 ln.U(bars[0]) if bars else '-', ln.U(bars[-1]) if bars else '-'))
for mt in (12, 15):
    print('| %d | BOTH | %d | | |' % (mt, len(tot[(mt, +1)]) + len(tot[(mt, -1)])))
print('')
print('| the read | value |')
print('|---|---|')
b12 = set(tot[(12, +1)]) | set(tot[(12, -1)])
b15 = set(tot[(15, +1)]) | set(tot[(15, -1)])
print('| cadences at max_tf 12 | %d |' % len(b12))
print('| cadences at max_tf 15 | %d |' % len(b15))
print('| kept by both | %d |' % len(b12 & b15))
print('| added by 15 | %d |' % len(b15 - b12))
print('| dropped by 15 | %d |' % len(b12 - b15))
print('')
if b15 - b12:
    print('| the bars max_tf 15 adds | |')
    print('|---|---|')
    for b in sorted(b15 - b12):
        print('| %s | |' % ln.U(b))
    print('')

# ---- 1 and 3. the legs -----------------------------------------------------------------------
print('## the 6 legs on %s' % DAY)
print('')
legs = chain(board())
T = summary(legs, 'LIN2_LATCH_EXFNC_ON %d - %s'
            % (K.LIN2_LATCH_EXFNC_ON, 'the banked machine' if not int(K.LIN2_LATCH_EXFNC_ON)
               else 'the latch arm'))

# the regression reference, from the banked run
REF = [('2026-08-30 00:00:00', 'LONG',  '2026-08-30 00:20:55', 'retest',  0.5193,  0.5906, -0.0458),
       ('2026-08-30 00:21:00', 'SHORT', '2026-08-30 02:35:20', 'barrage', 0.1172,  1.8287,  1.3703),
       ('2026-08-30 02:35:25', 'LONG',  '2026-08-30 02:46:55', 'retest',  0.1653,  0.5061,  0.1963),
       ('2026-08-30 02:47:00', 'SHORT', '2026-08-30 05:02:00', 'cws1b counter-oob',
                                                                          0.3144,  2.2062,  1.3041),
       ('2026-08-30 05:02:05', 'LONG',  '2026-08-30 05:11:00', 't1',      0.0313,  0.5066,  0.1828),
       ('2026-08-30 05:11:05', 'SHORT', '2026-08-30 07:44:00', 't1',      1.1156,  0.6725,  0.4431)]
#   THE LABEL DEPENDS ON THE ARM. At LIN2_LATCH_EXFNC_ON 0 a difference is a REGRESSION - the
#   routing broke something. At 1 it is the mech's DELTA and a difference is the point.
_ON = int(K.LIN2_LATCH_EXFNC_ON)
print('### %s 1027_pseudo_closed/legs_blocks.md'
      % ('the DELTA against' if _ON else 'the regression against'))
print('')
print('| leg | field | banked | this run | match |')
print('|---|---|---|---|---|')
bad = 0
for i, (o, d, x, eb, mae0, mfe0, rel0) in enumerate(REF):
    if i >= len(legs):
        print('| %d | the leg | present | MISSING | NO |' % (i + 1)); bad += 1; continue
    lg = legs[i]
    ap, vp = mae_mfe(lg['opn'], lg['exit'], lg['side'])
    got = [('the open', o, ln.U(lg['opn'])), ('dir', d, 'LONG' if lg['side'] > 0 else 'SHORT'),
           ('the exit', x, ln.U(lg['exit'])), ('ended by', eb, ended_by(lg['rows'])),
           ('MAE %', '%.4f' % mae0, '%.4f' % abs(pct(lg['opn'], lg['side'], ap))),
           ('MFE %', '%.4f' % mfe0, '%.4f' % pct(lg['opn'], lg['side'], vp)),
           ('realised %', '%+.4f' % rel0,
            '%+.4f' % pct(lg['opn'], lg['side'], float(close[int(lg['exit']) + 1])))]
    for f, want, have in got:
        ok = str(want) == str(have)
        if not ok:
            bad += 1
        print('| %d | %s | %s | %s | %s |' % (i + 1, f, want, have, 'yes' if ok else '** NO **'))
print('')
print('| the read | value |')
print('|---|---|')
print('| fields compared | %d |' % (len(REF) * 7))
print('| fields that differ | %d |' % bad)
if _ON:
    print('| the verdict | the latch arm is a DIFFERENT mech - a difference here is its effect,'
          ' not a fault |')
else:
    print('| REGRESSION | %s |' % ('CLEAN' if bad == 0 else '** BROKEN **'))
print('')

# ---- the latch state itself ------------------------------------------------------------------
def on_edges(st, a, b):
    """The bars the latch turns ON inside [a, b]. -> list."""
    return [i for i in range(int(a), int(b) + 1) if st[i] and not st[i - 1]]


if int(K.LIN2_LATCH_EXFNC_ON):
    BD = board()
    for sd, nm in ((-1, 'LOW'), (+1, 'HIGH')):
        print('## the latch state on %s, %s side' % (DAY, nm))
        print('')
        print('| the line | latch-ons | releases | bars latched ex-fence | bars ex-fence by VALUE |'
              ' the ratio |')
        print('|---|---|---|---|---|---|')
        for t in range(1, int(K.L2_MOM_MAXTF) + 1):
            st = BD._latch(t, sd)
            ve = K.ex_fence_mask(BD.line(t), sd)
            offs = [b for b in BD.latch_off_bars(t, sd) if A <= b <= B]
            nl = int(np.count_nonzero(st[A:B + 1])); nv = int(np.count_nonzero(ve[A:B + 1]))
            print('| ws%d | %d | %d | %d | %d | %s |'
                  % (t, len(on_edges(st, A, B)), len(offs), nl, nv,
                     '%.1fx' % (nl / nv) if nv else '-'))
        print('')
