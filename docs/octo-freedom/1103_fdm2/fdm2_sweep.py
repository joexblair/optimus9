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

GRID = {'knobs': KNOB_GRID, 'rtrip': RTRIP_GRID, 'bmult': BMULT_GRID}[MODE]
NAMES = [n for n, _ in GRID]
CFGS = [dict(zip(NAMES, c)) for c in itertools.product(*[v for _, v in GRID])]
RULED = {n: v[0] for n, v in GRID}
assert CFGS[0] == RULED, 'the ruled config is not the first row of the sweep'
KNOB_NAMES = [n for n, _ in KNOB_GRID]
BANKED = {n: getattr(K, n) for n in KNOB_NAMES}
for n in KNOB_NAMES:
    assert BANKED[n] == dict(KNOB_GRID)[n][0], \
        'the code default for %s is %r, the sweep calls %r ruled' % (n, BANKED[n],
                                                                    dict(KNOB_GRID)[n][0])

_LINE_SPEC_B = ln.SPEC['b']


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
for ci, cfg in enumerate(CFGS):
    if MODE == 'knobs':
        for n in NAMES:
            setattr(K, n, cfg[n])
        if LN is None:
            LN = arrays(cfg)
    else:
        LN = arrays(cfg)
    tape_end = len(LN['close']) - 1
    try:
        sigs = RE.signals(LN['B1'], LN['CPR'], G=LN['G30B'], EMR=LN['EMR'])
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
