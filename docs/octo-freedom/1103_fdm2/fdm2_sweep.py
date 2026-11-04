"""His 1104 overnight sweep: the banked re-entry's own knobs, 8 days, one process.

HIS ASK: *"prepare for an overnight sweep of our 4 days.  add 4 more random days (from the full 94
days) to the sweep.  you have 10 hours starting from now"*, and the knob list he picked: the ws6r
gate, the reversal read, the ws5r fence, the scan band, and the last-to-fire set with and without
the ib close.

THE MECH IS NOT IMPLEMENTED HERE. v4_fdm_reentry.signals produces the opens and v4_fdm2.legs walks
them - the same two calls fdm2_chain makes. This file only sets knobs, slices days and scores.

THE RULED CONFIG IS ROW 1 OF EVERY DAY, his standing rule that an off-ruled run is not the machine.
Its numbers must match the banked single-day runs, and the sweep prints them first so a drift is
visible before any arm is read.

W_V4_EXPERIMENT=1 IS REQUIRED: 47 of the 48 configs are off-ruled by construction.

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
    import v4_signal as SG
    import ln
finally:
    sys.stderr = _e

OUT = os.environ.get('W_FDM2_SWEEP_OUT', 'sweep_1104.md')
DAYS = [x.strip() for x in io.open(os.environ['W_FDM2_SWEEP_DAYS'], encoding='utf-8')
        if x.strip()]

#   ── the grid, his five knobs. THE RULED VALUE IS FIRST IN EVERY LIST ──────────────────────────
GRID = (
    ('FDM_RE_WS6_GATE', ('ex2080', 'oob')),
    ('FDM_RE_REV_READ', ('closed_prev', 'emerging')),
    ('FDM_RE_WS5_FNC', (20.0, 25.0, 15.0)),
    ('FDM_RE_SCAN_HI', (12, 30)),
    ('FDM_RE_FIRE_IB', (1, 0)),
)
RULED = {n: v[0] for n, v in GRID}
NAMES = [n for n, _ in GRID]
CFGS = [dict(zip(NAMES, c)) for c in itertools.product(*[v for _, v in GRID])]
assert CFGS[0] == RULED, 'the ruled config is not the first row of the sweep'

LN = F2.load()
TAPE = len(LN['close']) - 1
BANKED = {n: getattr(K, n) for n in NAMES}
for n, v in BANKED.items():
    assert v == RULED[n], 'the code default for %s is %r, the sweep calls %r ruled' % (n, v, RULED[n])

W = io.open(OUT, 'w', encoding='utf-8')


def say(line=''):
    W.write(line + '\n')
    W.flush()


def score_day(day, sigs):
    """The machine on one day, from the first re-entry signal in it. -> dict or None."""
    a, b = ln.K(day + ' 00:00:00'), ln.K(day + ' 23:59:55')
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


say('# his 1104 sweep | the banked re-entry\'s own knobs | %d configs x %d days = %d runs'
    % (len(CFGS), len(DAYS), len(CFGS) * len(DAYS)))
say('# TAPE %d bars, ends %s' % (len(LN['close']), ln.U(TAPE)))
say('# THE STOP IS ON at FDM_MAE_CAP %.2f%%, drag %.4f%% round trip per leg'
    % (float(K.FDM_MAE_CAP), F2.DRAG_PCT))
say('# ROW 1 OF EVERY DAY IS THE RULED CONFIG: %s'
    % ', '.join('%s %s' % (n, RULED[n]) for n in NAMES))
say('# every other row is off-ruled, W_V4_EXPERIMENT=1')
say()
say('| the knob | ruled | the arms swept |')
say('|---|---|---|')
for n, vs in GRID:
    say('| %s | %s | %s |' % (n, vs[0], ', '.join(str(x) for x in vs)))
say()
say('| the day | the config | ws6r gate | reversal read | ws5r fence | scan hi | ib in the set |'
    ' signals in the day | legs | stopped | gross %% | drag %% | net %% | MAE %% | MFE %% |'
    ' the first signal |')
say('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')

T0 = time.time()
ROWS = []
for ci, cfg in enumerate(CFGS):
    for n in NAMES:
        setattr(K, n, cfg[n])
    try:
        sigs = RE.signals(LN['B1'], LN['CPR'], G=LN['G30B'], EMR=LN['EMR'])
    except AssertionError as ex:
        say('| - | %d | %s | REFUSED: %s |' % (ci, ' | '.join(str(cfg[n]) for n in NAMES), ex))
        continue
    for day in DAYS:
        s = score_day(day, sigs)
        row = dict(cfg, day=day, ci=ci)
        if s is None:
            row.update(n=0, stops=0, gross=0.0, drag=0.0, net=0.0, mae=0.0, mfe=0.0,
                       first='-', nsig=0)
        else:
            row.update(n=s['n'], stops=s['stops'], gross=s['gross'], drag=s['drag'],
                       net=s['net'], mae=s['mae'], mfe=s['mfe'],
                       first=ln.U(s['first']), nsig=s['sigs'])
        ROWS.append(row)
        say('| %s | %d | %s | %s | %g | %d | %d | %d | %d | %d | %+.3f | -%.3f | %+.3f | %.3f |'
            ' %.3f | %s |'
            % (day, ci, cfg['FDM_RE_WS6_GATE'], cfg['FDM_RE_REV_READ'], cfg['FDM_RE_WS5_FNC'],
               cfg['FDM_RE_SCAN_HI'], cfg['FDM_RE_FIRE_IB'], row['nsig'], row['n'], row['stops'],
               row['gross'], row['drag'], row['net'], row['mae'], row['mfe'], row['first']))
    el = time.time() - T0
    say('# config %d of %d done, %.1f min elapsed, %.1f min projected total'
        % (ci + 1, len(CFGS), el / 60.0, el / 60.0 / (ci + 1) * len(CFGS)))

for n in NAMES:
    setattr(K, n, BANKED[n])

say()
say('| the config | ws6r gate | reversal read | ws5r fence | scan hi | ib in the set | days with'
    ' a trade | legs | stopped | gross %% | drag %% | net %% | MFE captured |')
say('|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for ci, cfg in enumerate(CFGS):
    rs = [r for r in ROWS if r['ci'] == ci]
    if not rs:
        continue
    nl = sum(r['n'] for r in rs)
    mfe = sum(r['mfe'] for r in rs)
    say('| %d | %s | %s | %g | %d | %d | %d of %d | %d | %d | %+.3f | -%.3f | %+.3f | %s |'
        % (ci, cfg['FDM_RE_WS6_GATE'], cfg['FDM_RE_REV_READ'], cfg['FDM_RE_WS5_FNC'],
           cfg['FDM_RE_SCAN_HI'], cfg['FDM_RE_FIRE_IB'],
           sum(1 for r in rs if r['n']), len(rs), nl, sum(r['stops'] for r in rs),
           sum(r['gross'] for r in rs), sum(r['drag'] for r in rs), sum(r['net'] for r in rs),
           ('%.1f%% of MFE' % (sum(r['net'] for r in rs) / mfe * 100.0)) if mfe > 0 else '-'))
say()
say('# %.1f min total' % ((time.time() - T0) / 60.0))
W.close()
print('wrote %s' % OUT)
