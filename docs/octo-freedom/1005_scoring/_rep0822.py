"""THE TWO QUEUED REPORTS, on the current spec. 1009.

Joe 1009, the two asks:
  1 *"show me the first 2 trades in their own timestamp-rows tables that show the events from the
     opening of the incoming trade to the final closure of either A-trade or B-trade"*
  2 *"btw I want A and B trades included for 08-22"*

and the format, from his own paste: FIVE columns - ts / min from A's open / event / pxs / pct for A -
with the event column WRAPPING under itself, the other four blank on a continuation row.

THE SPEC THIS RUNS ON, all of it Joe's and all of it current:
  the open      the start of ws12r's CURRENT mom-true run at the oob crossing (momo OR curl,
                `momo_g`, strip-mom-at-fence off). Falls back to the newest rising edge when ws12r
                is not mom-true at the crossing - 72.1% of events take the run start.
  the side      the oob side. HIGH oob -> LONG, LOW oob -> SHORT
  the walk      W_NOX=1 - the lineage walk's x-cross is DISABLED. Joe 1009: *"x-cross is troublesome
                at the moment, it's on my list for us after the sweep - let's disable x-cross for
                now"*. `final stalled` is the walk's only exit.
  the mech      W_DGATE=traj. The exhaustion override inside the 1/4 seam (36 bars), ws60r at the
                dwell-ending, B on ws12r's own stall or x-cross after it. XWOB_WS12X 4.
  A's close     IS B's open. One position at a time.

A IS THE INCOMING TRADE. In this population nothing precedes it - the open is a line event, not a
previous leg's exit - so A's open bar is the top of every table.
"""
import os, sys, datetime, textwrap
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
from _momtrue import momtrue_mask, rising, STATES
from optimus9.orchestration.build_ws_lines import HOURS, WARMUP

assert C.DGATE == 'traj', 'run with W_DGATE=traj'
assert C.NOX, 'run with W_NOX=1'
# THE CEILING IS A TEST PARAMETER HERE. Joe 1009: *"for this test, ceiling must be 12"* - so the
# baton cannot climb above ws12 and the walk is confined to the trigger TF and below. `ceil_hi` 23
# is the banked value and `_chain10` loads it from the config, so it is overridden here, not there.
# With X_CEIL == BASE_HI the ceiling branch is guarded off entirely, so no CEILING line prints.
C.CEIL_HI = int(os.environ.get('X_CEIL', C.CEIL_HI))
SC, U = C.SC, C.SC.U
PXa = C.PX; N = len(SC.ts); TF = C.TRIG_TF
R12 = C.R[TF]; HI, LO = SC.HI, SC.LO
DAY = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                               datetime.timezone.utc).strftime('%Y-%m-%d')
mn = lambda a, b: (int(SC.ts[b]) - int(SC.ts[a])) / 60000.0
D0, D1 = SC.K('2026-08-22 00:00:00'), SC.K('2026-08-22 23:59:55')
EW = 63      # the event column's width before it wraps

def wrapbox(hdr, rows, widths):
    """box() with the LAST-BUT-TWO column wrapped. One record per row; a continuation row leaves
    every other column blank, so the record reads down, never across."""
    w = list(widths)
    def line(l, m, r):
        return l + m.join('─' * (x + 2) for x in w) + r
    def put(cells, pad=' '):
        return '│ ' + ' │ '.join(c.ljust(x) if i != 0 else c.ljust(x)
                                 for i, (c, x) in enumerate(zip(cells, w))) + ' │'
    print(line('┌', '┬', '┐'))
    print(put([h.center(x) for h, x in zip(hdr, w)]))
    print(line('├', '┼', '┤'))
    for r in rows:
        parts = textwrap.wrap(r[2], EW) or ['']
        for i, p in enumerate(parts):
            print(put([r[0] if i == 0 else '', r[1] if i == 0 else '', p,
                       r[3] if i == 0 else '', r[4] if i == 0 else '']))
    print(line('└', '┴', '┘'))

MT = momtrue_mask(C.RL[TF], TF, C.BANK[TF], SC.EM, HOURS, WARMUP, 'gated', N)
RE = {d: rising(MT[d]) for d in (+1, -1)}
LAST = {}; RUN0 = {}
for d in (+1, -1):
    a = np.full(N, -1, np.int64); last = -1
    b = np.full(N, -1, np.int64); st = -1
    for k in range(N):
        if RE[d][k]: last = k
        a[k] = last
        if MT[d][k]:
            if st < 0: st = k
            b[k] = st
        else:
            st = -1; b[k] = -1
    LAST[d] = a; RUN0[d] = b
print('# mom-true (%s) masks ready. W_NOX %s, W_DGATE %s, exhaustion %d bars = %.1f min, '
      'XWOB_WS12X %d, oob_gate_bars %d, stop %.2f'
      % ('+'.join(STATES), C.NOX, C.DGATE, C.EXH_BARS, C.EXH_BARS * 5 / 60.0, C.XW12,
         C.GATE_BARS, C.MAE_STOP), flush=True)
print('# ceil_hi %d (banked 23; Joe 1009 set 12 for this test), base ceiling ws%d'
      % (C.CEIL_HI, C.BASE_HI), flush=True)

r = np.asarray(R12[:N], float)
EV = []
for k in range(max(1, D0), D1 + 1):
    for side in (+1, -1):
        if ((r[k] >= HI) if side > 0 else (r[k] <= LO)) and \
           not ((r[k - 1] >= HI) if side > 0 else (r[k - 1] <= LO)):
            mt = bool(MT[side][k])
            o = int(RUN0[side][k]) if mt else int(LAST[side][k])
            EV.append((k, side, o, mt)); break
print('# %d ws12r oob events on 08-22' % len(EV), flush=True)

def score(k, d, xk, why):
    p0 = float(PXa[k]); sgn = 1 if d > 0 else -1
    seg = PXa[k:xk + 1]; ok = np.isfinite(seg) & (seg > 0)
    rel = np.where(ok, (seg - p0) / p0 * 100.0 * sgn, 0.0)
    return dict(real=(float(PXa[xk]) - p0) / p0 * 100.0 * sgn,
                mae=(C.MAE_STOP if why == 'mae breach' else -float(rel.min())),
                mfe=(0.0 if why == 'mae breach' else float(rel.max())),
                rawmfe=float(rel.max()))
BFLIP = ('ws%dr exhaustion' % TF, 'ws%dr reversal on stalled' % TF,
         'ws%dr reversal on x-cross' % TF)

TR = []; seen = set()
for ev, side, o, mt in EV:
    if o < 0 or (o, side) in seen: continue
    seen.add((o, side))
    a = C.run_leg(o, side)
    if a[0] is None: continue
    sa = score(o, side, a[0], a[1])
    b = sb = None
    if a[1] in BFLIP:
        bb = C.run_leg(a[0], -side)
        if bb[0] is not None:
            b = bb; sb = score(a[0], -side, bb[0], bb[1])
    TR.append(dict(ev=ev, side=side, open=o, mt=mt, a=a, sa=sa, b=b, sb=sb))
print('# %d distinct pseudo trades on 08-22\n' % len(TR), flush=True)

# ---- REPORT 1: the first two, bar by bar
for n, t in enumerate(TR[:2], 1):
    o, side, ev, a = t['open'], t['side'], t['ev'], t['a']
    p0 = float(PXa[o]); sgn = 1 if side > 0 else -1
    pct = lambda j: '%+.4f' % ((float(PXa[j]) - p0) / p0 * 100.0 * sgn)
    rl = lambda j: '%+.1f' % mn(o, j)
    print('\n# TRADE %d of %d — A opens %s %s, the ws%dr oob event is %s'
          % (n, min(2, len(TR)), U(o), 'LONG' if side > 0 else 'SHORT', TF, U(ev)))
    rows = [(U(o), '+0.0',
             'A-TRADE OPENS %s — the start of ws%dr\'s current mom-true run%s'
             % ('LONG' if side > 0 else 'SHORT', TF,
                '' if t['mt'] else ' (ws%dr NOT mom-true at the event; this is the newest rising '
                                   'edge before it)' % TF),
             '%.6f' % p0, '+0.0000')]
    evs = list(a[5])
    evs.append((ev, '### ws%dr CROSSES INTO %s oob at %.2f — THE INTERCHANGE. the dwell clock '
                    'starts; exhaustion window to %s, dwell-ending %s'
                % (TF, 'HIGH' if side > 0 else 'LOW', float(r[ev]),
                   U(min(N - 1, ev + C.EXH_BARS)), U(min(N - 1, ev + C.GATE_BARS + 1)))))
    for j, lbl in sorted(evs, key=lambda z: z[0]):
        if j > a[0]: continue
        rows.append((U(j), rl(j), lbl, '%.6f' % float(PXa[j]), pct(j)))
    rows.append((U(a[0]), rl(a[0]), 'A-TRADE CLOSES on %s — realised %+.4f, MAE %.4f, MFE %.4f'
                 % (a[1], t['sa']['real'], t['sa']['mae'], t['sa']['mfe']),
                 '%.6f' % float(PXa[a[0]]), pct(a[0])))
    if t['b'] is not None:
        bb, sb = t['b'], t['sb']
        rows.append((U(a[0]), rl(a[0]), 'B-TRADE OPENS %s at the same bar'
                     % ('LONG' if -side > 0 else 'SHORT'), '%.6f' % float(PXa[a[0]]), pct(a[0])))
        for j, lbl in bb[5]:
            rows.append((U(j), rl(j), 'B: %s' % lbl, '%.6f' % float(PXa[j]), pct(j)))
        rows.append((U(bb[0]), rl(bb[0]),
                     'B-TRADE CLOSES on %s — realised %+.4f, MAE %.4f, MFE %.4f'
                     % (bb[1], sb['real'], sb['mae'], sb['mfe']),
                     '%.6f' % float(PXa[bb[0]]), pct(bb[0])))
    else:
        rows.append((U(a[0]), rl(a[0]),
                     'NO B-TRADE — A exited on %s, which is not an exhaustion or a ws%dr reversal'
                     % (a[1], TF), '%.6f' % float(PXa[a[0]]), pct(a[0])))
    wrapbox(('ts', '+min', 'event', 'pxs', 'pct for A'), rows, [8, 7, EW, 8, 8])

# ---- REPORT 2: every 08-22 A and B
print('\n\n# EVERY 08-22 PSEUDO TRADE — A, with its B directly under it')
rows = []
for n, t in enumerate(TR, 1):
    o, side, a, sa = t['open'], t['side'], t['a'], t['sa']
    rows.append((str(n), 'A', 'LONG' if side > 0 else 'SHORT', U(o), DAY(o), U(t['ev']),
                 '%.2f' % float(r[t['ev']]), 'HIGH' if side > 0 else 'LOW',
                 'run start' if t['mt'] else 'older edge',
                 '%.1f' % mn(o, t['ev']), 'YES' if a[0] >= t['ev'] else 'no',
                 U(a[0]), a[1], '%.1f' % mn(o, a[0]), '%.4f' % sa['mae'], '%.4f' % sa['mfe'],
                 '%.4f' % sa['rawmfe'], '%+.4f' % sa['real']))
    if t['b'] is not None:
        bb, sb = t['b'], t['sb']
        rows.append((str(n), 'B', 'LONG' if -side > 0 else 'SHORT', U(a[0]), DAY(a[0]),
                     "— A's close", '—', '—', '—', '—', '—',
                     U(bb[0]), bb[1], '%.1f' % mn(a[0], bb[0]), '%.4f' % sb['mae'],
                     '%.4f' % sb['mfe'], '%.4f' % sb['rawmfe'], '%+.4f' % sb['real']))
C.box(('#', 'A / B', 'side', 'opens', "open's day", 'the ws12r oob event', 'ws12r there',
       'oob side', 'the open is', 'lead min', 'reached its event', 'closes', 'why', 'hold min',
       'MAE', 'MFE scored', 'MFE raw', 'realised'), rows)
na = sum(1 for x in rows if x[1] == 'A'); nb = sum(1 for x in rows if x[1] == 'B')
C.box(('the measure', 'value'),
      [('ws12r oob events on 08-22', str(len(EV))),
       ('distinct pseudo trades — A', str(na)),
       ('of them, a B opened', str(nb)),
       ('A reached its own event', str(sum(1 for x in rows if x[1] == 'A' and x[10] == 'YES'))),
       ('summed A realised — NOT a P&L, the trades overlap',
        '%+.4f' % sum(float(x[17]) for x in rows if x[1] == 'A')),
       ('summed B realised — same caveat',
        '%+.4f' % sum(float(x[17]) for x in rows if x[1] == 'B'))])
