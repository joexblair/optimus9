"""THE CONSOLIDATED A/B REPORT. Joe 1009: *"we can consolidate the A-trade and B-trade. every
report from now will be"* - SEVEN columns:

    ts | +min | event | pxs | pct for A | pct for B | MAE so far | MFE so far | ws60r return

ONE table per trade, A's open at the top, B's close at the bottom, one record per row.
  pct for A     filled to A's close bar inclusive, blank after it
  pct for B     blank until B's open bar, filled from there
  MAE so far    the WORST the live trade has been, open to THIS row. Measured, running.
  MFE so far    the BEST it has been, open to this row. Joe 1009: *"now I see it's information to
                tell me where I need to focus on improving exits"* - so it climbs as the trade runs
                and the exit row sits underneath whatever it reached. MFE so far minus pct is the
                give-back the exit left on the table at that bar.
                BOTH are the LIVE trade's: A's until A closes, B's from B's open.
                A STOPPED leg's CLOSING LINE instead carries MAE `mae_stop_pct` 2.50 and MFE
                0.0000 - Joe 1007's scoring rule - so on a stopped leg the closing line and these
                columns disagree ON PURPOSE.
  ws60r return  ws60r's own reading on the bars it was read, from C.DG_READ. Blank elsewhere.
                `<ws60r value> <dir> <travel>` - UP +1 / DOWN -1 / FLAT 0 is the traj direction and
                the travel is over its tail.
  +min          minutes from A's OPEN, for every row including B's, so the pair reads as one clock.

THE MAE AND MFE BARS GET THEIR OWN ROWS. Joe 1009: *"I can't reconcile MFE with 0.9229"* - the
extreme bar carries no mech event, so without a row for it the closing line's MFE has no anchor.

THE MECH, all Joe's:
  the open     the start of ws12r's CURRENT mom-true run at the oob crossing (momo OR curl)
  the side     the oob side. HIGH oob -> LONG, LOW oob -> SHORT
  the walk     W_NOX=1 - the walk's x-cross is suppressed, so `final stalled` is its only exit
  W_SQX=1      Joe 1009's rule: an oob run that ends SHORT of the dwell with a squashed walk
               x-cross in it closes A at the bar ws12r returns IN-BOUNDS - *"we use the run ends
               timestamp to keep us live-ready"* - and opens B on the opposite side
  W_DGATE=traj the exhaustion override inside the 1/4 seam, ws60r at the dwell-ending, B on
               ws12r's own stall or x-cross after it
  A's close    IS B's open. One position at a time.
"""
import os, sys, datetime, textwrap
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C
from _momtrue import momtrue_mask, rising, STATES
from optimus9.orchestration.build_ws_lines import HOURS, WARMUP

assert C.DGATE in ('traj', 'vote'), 'run with W_DGATE=traj or vote'
assert C.NOX, 'run with W_NOX=1'
C.CEIL_HI = int(os.environ.get('X_CEIL', C.CEIL_HI))
SC, U, PXa = C.SC, C.SC.U, C.PX
N = len(SC.ts); TF = C.TRIG_TF; R12 = C.R[TF]; HI, LO = SC.HI, SC.LO
DAY = os.environ.get('X_DAY', '2026-08-22')
D0, D1 = SC.K('%s 00:00:00' % DAY), SC.K('%s 23:59:55' % DAY)
mn = lambda a, b: (int(SC.ts[b]) - int(SC.ts[a])) / 60000.0
EW = 52      # the event column's width before it wraps

def wrapbox(hdr, rows, widths):
    """One record per row. The event column wraps under itself; every other column is blank on a
    continuation row, so a record reads DOWN and never across."""
    w = list(widths); EI = 2
    line = lambda l, m, r: l + m.join('-' * (x + 2) for x in w) + r
    put = lambda cs: '| ' + ' | '.join(c.ljust(x) for c, x in zip(cs, w)) + ' |'
    print(line('+', '+', '+'))
    print(put([h.center(x) for h, x in zip(hdr, w)]))
    print(line('+', '+', '+'))
    for r in rows:
        parts = textwrap.wrap(r[EI], w[EI]) or ['']
        for i, p in enumerate(parts):
            print(put([(r[c] if i == 0 else '') if c != EI else p for c in range(len(w))]))
    print(line('+', '+', '+'))

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
print('# %s — mom-true (%s). W_NOX %s, W_SQX %s, W_DGATE %s, ceil_hi %d (banked 23), '
      'exhaustion %d bars = %.1f min, XWOB_WS12X %d, oob_gate_bars %d = %.1f min, stop %.2f'
      % (DAY, '+'.join(STATES), C.NOX, C.SQX, C.DGATE, C.CEIL_HI, C.EXH_BARS,
         C.EXH_BARS * 5 / 60.0, C.XW12, C.GATE_BARS, (C.GATE_BARS + 1) * 5 / 60.0, C.MAE_STOP),
      flush=True)

r = np.asarray(R12[:N], float)
EV = []
for k in range(max(1, D0), D1 + 1):
    for side in (+1, -1):
        if ((r[k] >= HI) if side > 0 else (r[k] <= LO)) and \
           not ((r[k - 1] >= HI) if side > 0 else (r[k - 1] <= LO)):
            EV.append((k, side, int(RUN0[side][k]) if MT[side][k] else int(LAST[side][k]),
                       bool(MT[side][k]))); break
print('# %d ws%dr oob events on %s' % (len(EV), TF, DAY), flush=True)

def score(k, d, xk, why):
    """realised / MAE / MFE and THE BARS THEY SIT ON, so the report can give each one a row."""
    p0 = float(PXa[k]); sg = 1 if d > 0 else -1
    seg = np.asarray(PXa[k:xk + 1], float); ok = np.isfinite(seg) & (seg > 0)
    rel = np.where(ok, (seg - p0) / p0 * 100.0 * sg, np.nan)
    iw, ib = int(np.nanargmin(rel)), int(np.nanargmax(rel))
    stop = (why == 'mae breach')
    return dict(real=(float(PXa[xk]) - p0) / p0 * 100.0 * sg,
                mae=(C.MAE_STOP if stop else -float(rel[iw])), mfe=(0.0 if stop else float(rel[ib])),
                # THE MEASURED EXTREMES, always. Joe 1007's stop rule rewrites `mae`/`mfe` on a
                # stopped leg, and the MAE/MFE BAR ROWS must still say what the tape did at that
                # bar - a row labelled "best pxs of A's span, 0.0000" on a bar whose pct is +0.5795
                # reports the knob where the reader is looking for the measurement.
                rawmae=-float(rel[iw]), rawmfe=float(rel[ib]),
                maebar=k + iw, mfebar=k + ib, stop=stop)

BFLIP = ('ws%dr exhaustion' % TF, 'ws%dr reversal on stalled' % TF,
         'ws%dr reversal on x-cross' % TF, 'ws%dr run short on a squashed x-cross' % TF)
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
print('# %d distinct pseudo trades on %s\n' % (len(TR), DAY), flush=True)

def render(n, t):
    o, side, ev, a, sa = t['open'], t['side'], t['ev'], t['a'], t['sa']
    ac = a[0]; p0 = float(PXa[o]); sg = 1 if side > 0 else -1
    pa = lambda j: '%+.4f' % ((float(PXa[j]) - p0) / p0 * 100.0 * sg)
    rl = lambda j: '%+.1f' % mn(o, j)
    w60 = lambda j, d: C.DG_READ.get((j, d), '')

    def running(k0, d0, end):
        """the running MAE / MFE of ONE trade, bar by bar from its own open. np.minimum/maximum
        .accumulate, so row j carries the extreme over k0..j and nothing from beyond it."""
        q0 = float(PXa[k0]); s0 = 1 if d0 > 0 else -1
        seg = np.asarray(PXa[k0:end + 1], float)
        rel = np.where(np.isfinite(seg) & (seg > 0), (seg - q0) / q0 * 100.0 * s0, np.nan)
        lo = np.minimum.accumulate(np.where(np.isnan(rel), np.inf, rel))
        hi = np.maximum.accumulate(np.where(np.isnan(rel), -np.inf, rel))
        return (lambda j: '%.4f' % max(0.0, -float(lo[j - k0])),
                lambda j: '%.4f' % max(0.0, float(hi[j - k0])))
    amae, amfe = running(o, side, ac)
    print('\n# TRADE %d — A opens %s %s, the ws%dr oob event is %s'
          % (n, U(o), 'LONG' if side > 0 else 'SHORT', TF, U(ev)))
    R = []
    add = lambda j, lbl, d: R.append((U(j), rl(j), lbl, '%.6f' % float(PXa[j]),
                                      pa(j) if j <= ac else '', '',
                                      amae(j), amfe(j), w60(j, d)))
    add(o, 'A-TRADE OPENS %s — the start of ws%dr\'s current mom-true run%s'
        % ('LONG' if side > 0 else 'SHORT', TF,
           '' if t['mt'] else ' (ws%dr NOT mom-true at the event; the newest rising edge '
                              'before it)' % TF), side)
    evs = list(a[5]) + [(ev, '### ws%dr CROSSES INTO %s oob at %.2f — THE INTERCHANGE. the dwell '
                             'clock starts; exhaustion window to %s, dwell-ending %s'
                         % (TF, 'HIGH' if side > 0 else 'LOW', float(r[ev]),
                            U(min(N - 1, ev + C.EXH_BARS)), U(min(N - 1, ev + C.GATE_BARS + 1))))]
    for b_, m_, lb in sorted([(sa['maebar'], 1, 'A\'s MAE bar — worst pxs of A\'s span, %.4f'
                               % sa['rawmae']), (sa['mfebar'], 1, 'A\'s MFE bar — best pxs of A\'s '
                               'span, %.4f' % sa['rawmfe'])] + [(j, 0, l) for j, l in evs]):
        if b_ > ac: continue
        add(b_, lb, side)
    add(ac, 'A-TRADE CLOSES on %s — realised %+.4f, MAE %.4f, MFE %.4f'
        % (a[1], sa['real'], sa['mae'], sa['mfe'])
        + (' — the stop rule, not the measurement: the tape read MAE %.4f MFE %.4f'
           % (sa['rawmae'], sa['rawmfe']) if sa['stop'] else ''), side)
    if t['b'] is None:
        add(ac, 'NO B-TRADE — A exited on %s, which opens no flip' % a[1], side)
    else:
        bb, sb = t['b'], t['sb']; bo, bc = ac, bb[0]; q0 = float(PXa[bo]); bg = -sg
        pb = lambda j: '%+.4f' % ((float(PXa[j]) - q0) / q0 * 100.0 * bg)
        bmae, bmfe = running(bo, bg, bc)
        addb = lambda j, lbl: R.append((U(j), rl(j), lbl, '%.6f' % float(PXa[j]), '', pb(j),
                                        bmae(j), bmfe(j), w60(j, -side)))
        addb(bo, 'B-TRADE OPENS %s at A\'s close bar' % ('LONG' if bg > 0 else 'SHORT'))
        for b_, m_, lb in sorted([(sb['maebar'], 1, 'B\'s MAE bar — worst pxs of B\'s span, %.4f'
                                   % sb['rawmae']), (sb['mfebar'], 1, 'B\'s MFE bar — best pxs of '
                                   'B\'s span, %.4f' % sb['rawmfe'])]
                                 + [(j, 0, 'B: %s' % l) for j, l in bb[5]]):
            if b_ <= bo or b_ > bc: continue
            addb(b_, lb)
        addb(bc, 'B-TRADE CLOSES on %s — realised %+.4f, MAE %.4f, MFE %.4f'
             % (bb[1], sb['real'], sb['mae'], sb['mfe']))
    wrapbox(('ts', '+min', 'event', 'pxs', 'pct for A', 'pct for B', 'MAE so far', 'MFE so far',
             'ws60r return'), R, [8, 6, EW, 8, 9, 9, 10, 10, 22])
    print('- MAE/MFE so far are the LIVE trade\'s, measured open-to-this-row. MFE so far minus the '
          'pct column is the give-back standing at that bar.')
    gross = sa['real'] + (t['sb']['real'] if t['sb'] else 0.0)
    legs = 2 if t['b'] is not None else 1
    print('- A %+.4f%s   gross %+.4f   drag %d x 0.11 = %.4f   NET AFTER DRAG %+.4f'
          % (sa['real'], ('   B %+.4f' % t['sb']['real']) if t['sb'] else '', gross,
             legs, legs * 0.11, gross - legs * 0.11))
    print('- a stopped leg scores MAE %.4f and MFE 0.0000, the knob value — Joe 1007.'
          % C.MAE_STOP)

# X_FROM / X_NTRADE pick the slice to render, 1-based, so a later batch costs no re-run of the
# earlier ones' output. The trade NUMBER is its position in the day's distinct-trade list.
F = int(os.environ.get('X_FROM', 1)); NT = int(os.environ.get('X_NTRADE', 2))
for n, t in enumerate(TR[F - 1:F - 1 + NT], F):
    render(n, t)
