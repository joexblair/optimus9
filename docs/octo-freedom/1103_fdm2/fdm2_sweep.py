"""His 1104 overnight sweep: the banked re-entry, three grids, one process per grid.

HIS ASK: *"prepare for an overnight sweep of our 4 days.  add 4 more random days (from the full 94
days) to the sweep.  you have 10 hours starting from now"*, the knob list he picked, and then
*"if you want to sweep the r configs in a small range, like (stoch len:[6,7,8], rsi len:[4,5,6],
stoch range:[7,8,9]) then do so.  you might also get value from sweeping ws1b's multi"*.

THE THREE GRIDS, W_FDM2_SWEEP_GRID:
    knobs   his five re-entry knobs. The lines never change, so the arrays load ONCE
    rtrip   the r config's own trip, (rsi, stc, klen) each +/- 1 = 27 configs. Every line in the
            ladder changes, so the arrays are REBUILT per config
    bmult   ws1b's bb multiplier. Only ws1b changes, and the arrays are rebuilt per config
            because the lift tables and the closed-prev series derive from it

THE MECH IS NOT IMPLEMENTED HERE. v4_fdm_reentry.signals produces the opens and v4_fdm2.legs walks
them - the same two calls fdm2_chain makes. This file sets knobs, slices days and scores.

THE RULED CONFIG IS ROW 1 OF EVERY GRID, his standing rule that an off-ruled run is not the
machine. Its numbers must match the banked single-day runs, and a drift there voids the grid.

W_V4_EXPERIMENT=1 IS REQUIRED: every config but the first is off-ruled by construction.

THE OUTPUT IS FLUSHED PER ROW. A 10-hour budget with a crash at hour 9 must still leave every
finished row on disk.
"""
import io
import itertools
import os
import sys
import time

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
assert os.environ.get('W_V4_EXPERIMENT') == '1', \
    'the sweep runs off-ruled configs, so it needs W_V4_EXPERIMENT=1 and a ruled control row'
_e = sys.stderr; sys.stderr = io.StringIO()
try:
    import v4_knobs as K
    import v4_fdm2 as F2
    import v4_fdm_reentry as RE
    import v4_rcfg_sweep as RS
    import v4_signal as SG
    import ln
finally:
    sys.stderr = _e

MODE = os.environ.get('W_FDM2_SWEEP_GRID', 'knobs')
OUT = os.environ.get('W_FDM2_SWEEP_OUT', 'sweep_1104_%s.md' % MODE)
DAYS = [x.strip() for x in io.open(os.environ['W_FDM2_SWEEP_DAYS'], encoding='utf-8')
        if x.strip()]

#   ── the grids. THE RULED VALUE IS FIRST IN EVERY LIST, so CFGS[0] is the machine ──────────────
KNOB_GRID = (
    ('FDM_RE_WS6_GATE', ('ex2080', 'oob')),
    ('FDM_RE_REV_READ', ('closed_prev', 'emerging')),
    ('FDM_RE_WS5_FNC', (20.0, 25.0, 15.0)),
    ('FDM_RE_SCAN_HI', (12, 30)),
    ('FDM_RE_FIRE_IB', (1, 0)),
)
#   HIS RANGES, 1104: *"(stoch len:[6,7,8], rsi len:[4,5,6], stoch range:[7,8,9])"*. The banked
#   trip is (rsi 5, stc 8, klen 7) and his three ranges are each of those +/- 1, which is the grid
#   v4_rcfg_sweep already carries. The ruled trip is first.
_T = (RS.K0, RS.R0, RS.S0)
TRIPS = [_T] + [t for t in ((k, r, s) for k in (RS.K0 - 1, RS.K0, RS.K0 + 1)
                            for r in (RS.R0 - 1, RS.R0, RS.R0 + 1)
                            for s in (RS.S0 - 1, RS.S0, RS.S0 + 1)) if t != _T]
RTRIP_GRID = (('R_TRIP', tuple(TRIPS)),)
#   ws1b's own bb multiplier. 0.95 is the banked spec ('bb', 49, 0.95, 'close'); the other rungs
#   were built to disk for this sweep and nothing else reads them. gcws30b is NOT touched - it
#   resolves through sub_line, its own spec.
BMULT_GRID = (('B_MULT', (0.95, 0.85, 0.90, 1.00, 1.05)),)

#   ── HIS 1104 COVERAGE GRID: every knob the spec collects, one at a time ───────────────────────
#   THE RULED VALUE IS THE FIRST RUNG of every curve. The rungs are mine and they are stated as
#   such: he has never ruled a range for any of these, so each curve is a probe, not a proposal.
CURVE = (
    ('FDM_RE_WIN_OPEN', ('both', 'ws1b', 'gcws30b', 'first', 'sameside')),
    ('FDM_RE_WIN_CLOSE', ('ws1b', 'gcws30b')),
    ('FDM_RE_B_FNC', (5.0, 10.0, 15.0, 20.0)),
    ('FDM_RE_IB_XWOB', (1, 3, 6, 12)),
    ('FDM_RE_WS5_FNC', (20.0, 15.0, 25.0, 30.0, 35.0)),
    ('FDM_M3_FNC', (25.0, 15.0, 20.0, 30.0, 35.0)),
    ('FDM_M3_RESCUE_ON', (1, 0)),
    ('FDM_M3_RESCUE_FNC', (40.0, 30.0, 35.0, 45.0, 50.0)),
    ('FDM_FNC_2080', (20.0, 15.0, 25.0, 30.0)),
    ('FDM_STEP1_ABOVE_TF', (3, 1, 5, 8, 12)),
    ('FDM_POP_LO', (3, 1, 5, 8, 12)),
    ('FDM_X10_WOB', (24, 12, 18, 36, 48)),
    ('FDM_X10_FRM', ('cross', 'confirm')),
    ('FDM_X10_GRACE_PCT', (40.0, 20.0, 30.0, 50.0, 60.0)),
    ('FDM_X10_TRADE_PCT', (50.0, 40.0, 60.0, 70.0, 80.0)),
    ('FDM_X10_GRACE_MIN', (5.0, 2.5, 10.0, 15.0, 30.0)),
    ('FDM_REV_FROM', ('event', 'window')),
    ('FDM_MAE_CAP', (1.1, 0.8, 1.5, 2.0, 3.0)),
    ('FDM_SAV_ON', (0, 1)),
    ('LIFT_PTS', (6, 4, 8, 10)),
    ('LIFT_TOL', (2.0, 1.0, 3.0, 4.0)),
    ('LIFT_WOB', (8, 4, 6, 12, 16)),
    ('TRAJ_MIN_TRAVEL', (0.0, 0.5, 1.0, 2.0)),
    ('L2_MOM_MAXTF', (30, 20, 25)),
)
#   THESE ARE READ INSIDE v4_fdm2.load, so a rung change needs the arrays rebuilt.
RELOAD = {'LIFT_PTS', 'LIFT_TOL', 'LIFT_WOB', 'L2_MOM_MAXTF'}
CURVE_CFGS = [{'KNOB': n, 'RUNG': v} for n, vs in CURVE for v in vs]

#   ── HIS 1104 STAGE 7: *"replace ws5 and ws6 with higher TFs, and scan higher than ws12"* ──────
#   THE PAIR IS ONE SLOT, because the two knobs are not independent - the gate line must sit above
#   the reversal line. (5, 6) is his spec and stays first, so config 0 is the ruled machine.
#   THE SCAN FLOOR CARRIES BOTH READINGS of his sentence, 'gate' and 'ws13', as arms.
#   A pair whose gate sits at or above the ceiling trips the mech's own assert and prints as a
#   REFUSED row rather than being quietly dropped.
TFPAIR_GRID = (
    ('TF_PAIR', ((5, 6), (7, 8), (8, 9), (10, 11), (12, 13), (15, 16), (20, 21))),
    ('FDM_RE_SCAN_FLOOR', ('gate', 'ws13')),
    ('FDM_RE_SCAN_HI', (12, 18, 24, 30)),
    ('FDM_RE_REV_READ', ('closed_prev', 'emerging')),
)

#   ── HIS 1104 STAGE 11: the dynamic climb ─────────────────────────────────────────────────────
#   *"it might be a dynamic mech - ride upwards through the TFs until you reach a tf showing the in
#   fence r line, then open the trade"*. 'off' is the banked ws5/ws6 mech and stays config 0.
CLIMB_GRID = (
    ('FDM_RE_CLIMB', ('off', 'value', 'reversal')),
    ('FDM_RE_CLIMB_HI', (12, 20, 30)),
    ('FDM_RE_WS6_GATE', ('ex2080', 'oob')),
    ('FDM_RE_REV_READ', ('closed_prev', 'emerging')),
    ('FDM_RE_REV_TF', (5, 8, 10)),
)

#   ── STAGES 8 AND 9: the line config crossed with the reversal read ───────────────────────────
#   THE READ IS A GRID SLOT, NOT AN ENV OVERRIDE. Setting it in the environment moves the code
#   default, and the control assert refused the run for exactly that reason - config 0 has to BE
#   the banked machine or no arm can be read against it.
RTRIP2_GRID = (('R_TRIP', tuple(TRIPS)), ('FDM_RE_REV_READ', ('closed_prev', 'emerging')))
BMULT2_GRID = (('B_MULT', (0.95, 0.85, 0.90, 1.00, 1.05)),
               ('FDM_RE_REV_READ', ('closed_prev', 'emerging')))

#   ── STAGE 12: the start line's own curve, at the best config the night found ─────────────────
#   THE DATA POINTED HERE, not a new idea of mine. Across the TF-pair grid and the climb grid the
#   one slot that moved the per-leg gross was the LINE THE WALK STARTS FROM - ws8 against ws5 - and
#   neither grid gave it more than three rungs. This gives it eight, at the best config found:
#   the reversal climb, ceiling ws12, rung gate at 20/80, the live read.
#   ws5 IS FIRST so config 0 is still the banked machine's start line.
STARTLINE_GRID = (
    ('FDM_RE_REV_TF', (5, 6, 7, 8, 9, 10, 11, 12)),
    ('FDM_RE_CLIMB', ('off', 'reversal')),
)

GRID = {'knobs': KNOB_GRID, 'rtrip': RTRIP_GRID, 'bmult': BMULT_GRID, 'tfpair': TFPAIR_GRID,
        'climb': CLIMB_GRID, 'rtrip2': RTRIP2_GRID, 'bmult2': BMULT2_GRID,
        'startline': STARTLINE_GRID,
        'curve': (('KNOB', tuple(n for n, _ in CURVE)), ('RUNG', ('-',)))}[MODE]
NAMES = [n for n, _ in GRID]
if MODE == 'curve':
    CFGS = CURVE_CFGS
    RULED = CFGS[0]
else:
    CFGS = [dict(zip(NAMES, c)) for c in itertools.product(*[v for _, v in GRID])]
    RULED = {n: v[0] for n, v in GRID}
    assert CFGS[0] == RULED, 'the ruled config is not the first row of the sweep'
KNOB_NAMES = [n for n, _ in KNOB_GRID] + ['FDM_RE_REV_TF', 'FDM_RE_GATE_TF',
                                           'FDM_RE_SCAN_FLOOR', 'FDM_RE_CLIMB',
                                           'FDM_RE_CLIMB_HI']
BANKED = {n: getattr(K, n) for n in KNOB_NAMES}
#   THE CODE DEFAULT AND THE SWEEP'S "RULED" MUST AGREE, for the pair knobs too. A disagreement
#   means config 0 is not the machine and no arm in the grid can be read against it.
for n, v in (list(dict(KNOB_GRID).items())
             + [('FDM_RE_REV_TF', (5,)), ('FDM_RE_GATE_TF', (6,)),
                ('FDM_RE_SCAN_FLOOR', ('gate',)), ('FDM_RE_CLIMB', ('off',)),
                ('FDM_RE_CLIMB_HI', (12,))]):
    assert BANKED[n] == v[0], \
        'the code default for %s is %r, the sweep calls %r ruled' % (n, BANKED[n], v[0])

_LINE_SPEC_B = ln.SPEC['b']


CURVE_BANKED = {}
if MODE == 'curve':
    CURVE_BANKED = {n: getattr(K, n) for n, _ in CURVE}


def arrays(cfg):
    """The line arrays this config needs. -> the F2.load dict.

    THE LINE-AFFECTING SLOTS ARE PATCHED AT THEIR OWN HOME and F2.load is then called unchanged:
    v4_rcfg_sweep's trip slots for the r ladder, ln.SPEC['b'] for ws1b's multiplier. Nothing here
    reimplements a line read.
    """
    if 'R_TRIP' in cfg:
        RS.K0, RS.R0, RS.S0 = cfg['R_TRIP']
    if 'B_MULT' in cfg:
        sp, md = _LINE_SPEC_B
        ln.SPEC['b'] = ((sp[0], sp[1], float(cfg['B_MULT']), sp[3]), md)
    return F2.load()


def score_day(LN, day, sigs, tape_end):
    """The machine on one day, from the first re-entry signal in it. -> dict or None."""
    a, b = ln.K(day + ' 00:00:00'), min(ln.K(day + ' 23:59:55'), tape_end)
    hit = [g for g in sigs if a <= int(g['bar']) <= b]
    if not hit:
        return None
    g = hit[0]
    ts = SG.target_side(SG.direction(int(g['side'])))
    opn = SG.fire_bar(g)
    if opn > b:
        return None
    lg = F2.legs(LN, (opn, ts, 'fdm re-entry %s' % ln.U(int(g['bar']))), b, resig=sigs)
    s = F2.score(lg)
    s['first'] = int(g['bar'])
    s['sigs'] = len(hit)
    return s


W = io.open(OUT, 'w', encoding='utf-8')


def say(line=''):
    W.write(line + '\n')
    W.flush()


say('# his 1104 sweep | grid %s | %d configs x %d days = %d runs'
    % (MODE, len(CFGS), len(DAYS), len(CFGS) * len(DAYS)))
say('# THE STOP IS ON at FDM_MAE_CAP %.2f%%, drag %.4f%% round trip per leg'
    % (float(K.FDM_MAE_CAP), F2.DRAG_PCT))
say('# CONFIG 0 IS THE RULED MACHINE: %s' % ', '.join('%s %s' % (n, RULED[n]) for n in NAMES))
say('# every other config is off-ruled, W_V4_EXPERIMENT=1')
say('# the banked knobs held for every row here: %s'
    % ', '.join('%s %s' % (n, BANKED[n]) for n in KNOB_NAMES) if MODE != 'knobs' else
    '# the knobs are the grid')
say()
say('| the knob | ruled | the arms swept |')
say('|---|---|---|')
for n, vs in GRID:
    say('| %s | %s | %s |' % (n, vs[0], ', '.join(str(x) for x in vs)))
say()
say('| the day | the config | %s | signals in the day | legs | stopped | gross %% | drag %% |'
    ' net %% | MAE %% | MFE %% | the first signal |' % ' | '.join(NAMES))
say('|' + '---|' * (len(NAMES) + 11))

T0 = time.time()
ROWS = []
LN = None
_last_reload = False
for ci, cfg in enumerate(CFGS):
    if MODE == 'curve':
        #   EVERY OTHER KNOB BACK TO THE BANK before each rung, so a curve reads one knob only.
        for n, v in CURVE_BANKED.items():
            setattr(K, n, v)
        setattr(K, cfg['KNOB'], cfg['RUNG'])
        #   THE RELOAD IS NEEDED WHEN THIS RUNG NEEDS ONE *OR WHEN THE LAST ONE DID*. A reload
        #   knob leaves the arrays built at ITS last rung, so the next curve would run on arrays
        #   that do not match its own ruled values. That is exactly how the TRAJ_MIN_TRAVEL curve
        #   came out at 917 legs against the control row's 898 - it inherited LIFT_WOB 16's arrays.
        if cfg['KNOB'] in RELOAD or _last_reload or LN is None:
            LN = F2.load()
        _last_reload = cfg['KNOB'] in RELOAD
    elif MODE in ('knobs', 'tfpair', 'climb', 'startline'):
        #   TF_PAIR IS ONE SLOT HOLDING TWO KNOBS: the gate line must sit above the reversal line,
        #   so they are swept together and never as a cross.
        for n in NAMES:
            if n == 'TF_PAIR':
                K.FDM_RE_REV_TF, K.FDM_RE_GATE_TF = cfg[n]
            else:
                setattr(K, n, cfg[n])
                if n == 'FDM_RE_REV_TF':
                    #   THE GATE LINE FOLLOWS THE REVERSAL LINE, +1, which is the banked
                    #   relationship. Without this the pair assert trips on every rung but ws5.
                    K.FDM_RE_GATE_TF = int(cfg[n]) + 1
        if LN is None:
            LN = arrays(cfg)
    else:
        #   THE LINE-CONFIG GRIDS MAY ALSO CARRY KNOB SLOTS, so every name that is not a line slot
        #   is applied as a knob before the arrays are built.
        for n in NAMES:
            if n not in ('R_TRIP', 'B_MULT'):
                setattr(K, n, cfg[n])
        LN = arrays(cfg)
    tape_end = len(LN['close']) - 1
    try:
        sigs = RE.signals(LN['B1'], LN['CPR'], G=LN['G30B'], EMR=LN['EMR'], CPM=LN['CPM'])
    except AssertionError as ex:
        say('| - | %d | %s | REFUSED: %s |'
            % (ci, ' | '.join(str(cfg[n]) for n in NAMES), ex))
        continue
    for day in DAYS:
        s = score_day(LN, day, sigs, tape_end)
        row = dict(cfg, day=day, ci=ci)
        if s is None:
            row.update(n=0, stops=0, gross=0.0, drag=0.0, net=0.0, mae=0.0, mfe=0.0,
                       first='-', nsig=0)
        else:
            row.update(n=s['n'], stops=s['stops'], gross=s['gross'], drag=s['drag'],
                       net=s['net'], mae=s['mae'], mfe=s['mfe'],
                       first=ln.U(s['first']), nsig=s['sigs'])
        ROWS.append(row)
        say('| %s | %d | %s | %d | %d | %d | %+.3f | -%.3f | %+.3f | %.3f | %.3f | %s |'
            % (day, ci, ' | '.join(str(cfg[n]) for n in NAMES), row['nsig'], row['n'],
               row['stops'], row['gross'], row['drag'], row['net'], row['mae'], row['mfe'],
               row['first']))
    el = time.time() - T0
    say('# config %d of %d done, %.1f min elapsed, %.1f min projected total'
        % (ci + 1, len(CFGS), el / 60.0, el / 60.0 / (ci + 1) * len(CFGS)))

for n in KNOB_NAMES:
    setattr(K, n, BANKED[n])
for n, v in CURVE_BANKED.items():
    setattr(K, n, v)

say()
say('| the config | %s | days with a trade | legs | stopped | gross %% | drag %% | net %% |'
    ' net per leg %% | MFE %% | net over MFE |' % ' | '.join(NAMES))
say('|' + '---|' * (len(NAMES) + 9))
for ci, cfg in enumerate(CFGS):
    rs = [r for r in ROWS if r['ci'] == ci]
    if not rs:
        continue
    nl = sum(r['n'] for r in rs)
    mfe = sum(r['mfe'] for r in rs)
    net = sum(r['net'] for r in rs)
    say('| %d | %s | %d of %d | %d | %d | %+.3f | -%.3f | %+.3f | %s | %.3f | %s |'
        % (ci, ' | '.join(str(cfg[n]) for n in NAMES), sum(1 for r in rs if r['n']), len(rs),
           nl, sum(r['stops'] for r in rs), sum(r['gross'] for r in rs),
           sum(r['drag'] for r in rs), net,
           ('%+.4f' % (net / nl)) if nl else '-',
           mfe, ('%.1f%%' % (net / mfe * 100.0)) if mfe > 0 else '-'))
say()
say('# %.1f min total' % ((time.time() - T0) / 60.0))
W.close()
print('wrote %s' % OUT)
