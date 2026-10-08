"""THE >ws12 DELEGATION GATE — ws60r's TRAJECTORY, VALIDATED AGAINST THE NEXT PIVOT. 1008.

Joe 1008, verbatim:
  *"presently, whenever ws12r crosses to oob we automatically delegate to the >12 oob mech.
    sometimes, the delegation is a bad move: pxs does not continue the trend (the mechs
    expectation), and reverses. to gate the delegation, we can look at ws60r's trajectory (per the
    traj spec). if ws60r's trajectory matches the oob side that ws12r is crossed into (ie -dr,
    ws12r low oob, ws60r traj is down / +dr, ws12r high oob, ws60r traj is up), then we open the
    delegation gate
    -you cam validate the gated delegation logic using swing_detect's next pivot - if the
    hypothesis is correct, the next pivot will be matching ws60r's trajectory (up or down)"*

THE TRAJ SPEC, used verbatim, from 1007_ws12_baton.md: *"trajectory is the sign of (ws1r now - ws1r
at its last step change), the same reading as §13's step_dir, so it needs no lookback window"*. Here
it is read on ws60r. No window, no cap.

NOTHING IS BUILT INTO THE CHAIN. This is the validation Joe asked for and nothing else.

FOUR THINGS WERE UNSPECIFIED. None is decided - each is a COLUMN or an ARM so the data answers it:

  1  WHICH BAR the trajectory is read on. The code has TWO ws12r-oob events, 6+ minutes apart:
       the CROSSING bar      - where `ceil` extends to ws23
       the HANDOVER bar      - where the consecutive oob run passes oob_gate_bars 72, and where the
                               >ws12 mech actually takes the exit
     Joe's words name the crossing (*"crosses to oob"*) and his target names the delegation
     (*"gate the delegation"*). BOTH bars are measured, side by side.

  2  dr OR THE LEG'S SIDE. Joe's words are dr (*"-dr, ws12r low oob"*), so dr is the headline.
     `run_leg` gates on the LEG's own direction, which is not the tape dr, so that is reported too.

  3  swing_detect's pct. The function defaults 0.9; the linelab spec's core is 1.0. Both are run.

  4  TRAJECTORY ZERO - ws60r has no step change at or before the bar, or the step is flat. It gets
     its OWN row. It is not folded into either side.

THE HIT TEST, as Joe states it: traj UP -> the next pivot is an 'H'; traj DOWN -> the next pivot is
an 'L'. The gate-CLOSED rows are printed beside the gate-OPEN rows, because a hit rate with no base
rate is not a measurement.
"""
import os, sys, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.compute.swing_detect import find_pivots
import _chain10 as C

SC, PX, box, U = C.SC, C.PX, C.box, C.SC.U
N = len(SC.ts)
DRv = (SC.DR if hasattr(SC, 'DR') else SC.DRv)[:N]
R12 = C.R[C.TRIG_TF]
R60 = np.asarray(SC.LD(60 * 60, 'r'), float)[:N]
HI, LO = SC.HI, SC.LO
GATE = C.GATE_BARS
DAYOF = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                                  datetime.timezone.utc).strftime('%Y-%m-%d')
print('# tape %d bars, %s -> %s   ws%dr is the trigger, oob %.0f/%.0f, oob_gate_bars %d'
      % (N, U(0), U(N - 1), C.TRIG_TF, LO, HI, GATE), flush=True)

# ---- the traj spec, verbatim: the sign of (value now - value at its last step change)
def step_dir(v, k):
    cur = float(v[k])
    if not np.isfinite(cur): return 0
    j = k
    while j > 0 and (not np.isfinite(v[j - 1]) or float(v[j - 1]) == cur):
        j -= 1
    if j <= 0: return 0
    prev = float(v[j - 1])
    return 1 if cur > prev else (-1 if cur < prev else 0)

TRAJ60 = np.zeros(N, np.int8)
_cur = np.nan; _prev = np.nan
for k in range(N):                      # one forward pass, same answer as step_dir per bar
    v = float(R60[k])
    if np.isfinite(v):
        if not np.isfinite(_cur):
            _cur = v
        elif v != _cur:
            _prev = _cur; _cur = v
    TRAJ60[k] = 0 if not np.isfinite(_prev) else (1 if _cur > _prev else (-1 if _cur < _prev else 0))
_bad = [k for k in range(2000, N, 97) if TRAJ60[k] != step_dir(R60, k)]
assert not _bad, 'the forward TRAJ60 pass disagrees with step_dir at %d bars, first %d' \
                 % (len(_bad), _bad[0] if _bad else -1)
print('# TRAJ60 built and checked against step_dir at %d sampled bars'
      % len(range(2000, N, 97)), flush=True)

# ---- every ws12r crossing INTO oob, on the tape dr side and on each side outright
EV = []
for k in range(1, N):
    for side, label in ((+1, 'hi oob'), (-1, 'lo oob')):
        now = (float(R12[k]) >= HI) if side > 0 else (float(R12[k]) <= LO)
        was = (float(R12[k - 1]) >= HI) if side > 0 else (float(R12[k - 1]) <= LO)
        if now and not was:
            run = 0
            j = k
            while j < N and (((float(R12[j]) >= HI) if side > 0 else (float(R12[j]) <= LO))):
                j += 1
            run = j - k
            EV.append(dict(k=k, side=side, label=label, dr=int(DRv[k]), run=run,
                           hand=(k + GATE + 1) if run > GATE + 1 else None,
                           traj_x=int(TRAJ60[k]),
                           traj_h=int(TRAJ60[k + GATE + 1]) if run > GATE + 1 else None))
print('# %d ws12r oob crossings; %d reach the %d-bar handover'
      % (len(EV), sum(1 for e in EV if e['hand']), GATE), flush=True)

# ---- swing_detect's pivots, both pct readings
PIV = {}
for pct in (0.9, 1.0):
    pv = find_pivots(PX, pct)
    # "the next pivot after bar k" = the FIRST pivot whose bar is strictly greater than k. So the
    # bars that share a next pivot are the half-open run [previous pivot's bar, this pivot's bar).
    # THE FIRST CODING WALKED k BACKWARDS with a single decreasing pointer; once that pointer fell
    # to -1 at the tape end it never recovered, so nxt_i stayed -1 for every bar and all eight
    # tables printed EMPTY. It produced no error and no wrong number - just nothing.
    nxt_i = np.full(N, -1, np.int64); nxt_k = np.zeros(N, np.int8)
    _s = 0
    for _b, _kd in pv:
        if _b > _s:
            nxt_i[_s:_b] = _b
            nxt_k[_s:_b] = 1 if _kd == 'H' else -1
        _s = _b
    assert (nxt_i[:pv[-1][0]] >= 0).all(), 'a bar before the last pivot has no next pivot'
    PIV[pct] = (pv, nxt_i, nxt_k)
    print('# swing_detect pct %.1f -> %d pivots' % (pct, len(pv)), flush=True)

mn = lambda a, b: (int(SC.ts[b]) - int(SC.ts[a])) / 60000.0

def table(pct, bar, trajkey, drmode, blk='all'):
    """bar: 'x' the crossing, 'h' the handover. drmode: 'dr' uses the tape dr, 'side' the oob side."""
    pv, nxt_i, nxt_k = PIV[pct]
    rows = collections.defaultdict(lambda: [0, 0, 0.0, 0.0])   # n, hits, sum minutes, sum pivot move
    for e in EV:
        b = e['k'] if bar == 'x' else e['hand']
        if b is None: continue
        if blk != 'all' and DAYOF(b) not in BLK[blk]: continue
        tj = e[trajkey]
        if tj is None: continue
        # JOE'S RULE IS A THREE-WAY CONJUNCTION, not a two-way one. Verbatim: *"-dr, ws12r low
        # oob, ws60r traj is down / +dr, ws12r high oob, ws60r traj is up"*. The 'dr' and 'side'
        # arms below each test only ONE half of it, so drmode 'joe' is the rule as written.
        if drmode == 'joe':
            if e['dr'] == 0: key = 'dr is 0 at the crossing'
            elif e['side'] != e['dr']: key = 'the oob side is AGAINST dr'
            elif tj == 0: key = 'ws60r traj is 0'
            elif tj == e['dr']:
                key = 'GATE OPEN — dr, the oob side and ws60r traj all agree'
            else:
                key = 'gate closed — dr and the oob side agree, ws60r traj is against'
        else:
            want = e['dr'] if drmode == 'dr' else e['side']
            if drmode == 'dr' and want == 0: key = 'dr is 0 at the crossing'
            elif tj == 0: key = 'ws60r traj is 0'
            elif tj == want: key = 'GATE OPEN — traj matches'
            else: key = 'gate closed — traj against'
        ni = nxt_i[b]
        if ni < 0: continue
        hit = 1 if (tj > 0 and nxt_k[b] > 0) or (tj < 0 and nxt_k[b] < 0) else 0
        r = rows[key]
        r[0] += 1; r[1] += hit; r[2] += mn(b, int(ni))
        p0 = float(PX[b]); p1 = float(PX[int(ni)])
        r[3] += (p1 - p0) / p0 * 100.0 * (1 if tj > 0 else (-1 if tj < 0 else 0))
    order = ['GATE OPEN — traj matches', 'gate closed — traj against', 'ws60r traj is 0',
             'dr is 0 at the crossing']
    if drmode == 'joe':
        order = ['GATE OPEN — dr, the oob side and ws60r traj all agree',
                 'gate closed — dr and the oob side agree, ws60r traj is against',
                 'ws60r traj is 0', 'the oob side is AGAINST dr', 'dr is 0 at the crossing']
    return [(k, str(rows[k][0]), str(rows[k][1]),
             '%.1f%%' % (100.0 * rows[k][1] / rows[k][0]) if rows[k][0] else '—',
             '%.1f' % (rows[k][2] / rows[k][0]) if rows[k][0] else '—',
             '%+.4f' % (rows[k][3] / rows[k][0]) if rows[k][0] else '—')
            for k in order if rows[k][0]]

HDR = ('the gate', 'crossings', 'next pivot matches traj', 'hit rate',
       'mean min to that pivot', 'mean pxs move to it, signed by traj')
_days = sorted({DAYOF(k) for k in range(0, N, 2000)})
BLK = {'all': set(_days), 'fit': set(_days[:47]), 'hold': set(_days[47:])}
print('\n# the fit / hold split is the same one every sweep uses: days 1-47 and 48-95 of %d'
      % len(_days))

for drmode, dlab in (('joe', 'JOE\'S RULE AS WRITTEN — dr, the oob side and ws60r traj all agree'),
                     ('dr', 'ws60r traj vs THE TAPE dr only'),
                     ('side', 'ws60r traj vs THE oob SIDE only, dr ignored')):
    for bar, trajkey, blab in (('x', 'traj_x', 'at the CROSSING bar'),
                               ('h', 'traj_h', 'at the HANDOVER bar, crossing + %d' % (GATE + 1))):
        for pct in (0.9, 1.0):
            print('\n# %s, %s, swing_detect %.1f%%' % (dlab, blab, pct))
            box(HDR, table(pct, bar, trajkey, drmode))
            if drmode == 'joe' and bar == 'h':
                for blk in ('fit', 'hold'):
                    print('#   the %s half alone' % blk)
                    box(HDR, table(pct, bar, trajkey, drmode, blk))
print('\n- "hit rate" = the next swing_detect pivot after that bar is an H when ws60r traj is UP,')
print('  or an L when it is DOWN. Joe: "the next pivot will be matching ws60r\'s trajectory".')
print('- the gate-closed row IS the base rate. A hit rate with no base rate is not a measurement.')
print('- "mean pxs move to it, signed by traj" is + when price moved the way the traj pointed.')
