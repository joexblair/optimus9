"""PSEUDO TRADES, ONE PER ws12r oob EVENT — the whole population. 1009.

Joe 1009: *"we need to test all ws12r oob events - it's a representation of the trade-chain that
we're building / we can create pseudo trades, one per ws12r oob: for each ws12r oob event, lookback
until you find a counter-dr ws2Mage crossing into IB, and open a trade"*.

Joe's two worked examples, both reproduced:
    -dr 13:33:50 ws12r  ->  the open is 12:22:00, ws2Mage 85.05 -> 70.86, 71.8 min before
    +dr 07:36:00 ws12r  ->  the open is 06:33:50, ws2Mage 14.44 -> 16.76, 62.2 min before

THE RULE AS BUILT
  the event     EVERY bar where ws12r crosses into oob, either side. Not filtered by any leg's
                direction - Joe: *"all ws12r oob events"*.
  the side      the oob side. HIGH oob -> LONG, LOW oob -> SHORT. Same convention as `goob`.
  the open      walking BACK from the event, the newest bar where ws2Mage crosses INTO in-bounds
                from the COUNTER-dr side:
                  ws12r HIGH oob -> ws2Mage rising out of LO oob through 15
                  ws12r LOW  oob -> ws2Mage falling out of HI oob through 85
  the forward   `run_leg(open, side)` - the unchanged composed mech, so the lineage walk, the
                ceiling, the dwell, the exhaustion override, ws60r and the MAE stop all apply, and
                the stop is anchored at the pseudo-open.
  the B-trade   when A exits on an exhaustion or a ws12r reversal, B is `run_leg(A_exit, -side)`.
                One position at a time, A's close is B's open.
  the end       A, then B, then stop. Joe: *"until the end of the resulting decision"*.

THREE THINGS THAT ARE TRUE OF THIS POPULATION AND MUST NOT BE READ PAST

  1  THE ROWS ARE NOT ADDITIVE. 3,795 pseudo-trades overlap heavily - one trade's forward walk can
     span later ws12r events, and consecutive events often resolve to the SAME open bar. Summing
     realised across them is not a P&L. The row is a measurement of one decision, nothing more.
  2  DUPLICATES ARE REPORTED, NOT REMOVED. Two events with the same open bar AND the same side are
     the same pseudo-trade. Both the raw and the distinct counts are printed.
  3  THE OPEN CONSUMES THE ARMING EVENT. The pseudo-open is ws2Mage crossing INTO in-bounds; the
     lineage walk arms on ws2Mage crossing INTO oob. So every pseudo-trade starts with its arming
     condition just spent, and the walk cannot pick a rider until ws2Mage returns to oob. How often
     that happens before the interchange is a column, not an assumption.

W_EXH_FRAC is the knob Joe flagged for a metric-based sweep. This run holds it at 0.25.
"""
import os, sys, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C

assert C.DGATE == 'traj', 'run with W_DGATE=traj'
SC, box, U = C.SC, C.box, C.SC.U
PXa = C.PX
N = len(SC.ts); TF = C.TRIG_TF
R12, M2 = C.R[TF], C.M2
HI, LO = SC.HI, SC.LO
DAY = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                               datetime.timezone.utc).strftime('%Y-%m-%d')
mn = lambda a, b: (int(SC.ts[b]) - int(SC.ts[a])) / 60000.0
print('# W_DGATE %s  exhaustion %d bars = %.1f min (W_EXH_FRAC %.2f)  XWOB_WS12X %d  '
      'oob_gate_bars %d  stop %.2f'
      % (C.DGATE, C.EXH_BARS, C.EXH_BARS * 5 / 60.0, C.EXH_FRAC, C.XW12, C.GATE_BARS, C.MAE_STOP),
      flush=True)

# ---- every ws2Mage crossing INTO in-bounds, both sides, precomputed
m = np.asarray(M2[:N], float)
fin = np.isfinite(m)
up_ib = np.zeros(N, bool)      # rising out of LO oob through 15
dn_ib = np.zeros(N, bool)      # falling out of HI oob through 85
up_ib[1:] = fin[1:] & fin[:-1] & (m[:-1] <= LO) & (m[1:] > LO)
dn_ib[1:] = fin[1:] & fin[:-1] & (m[:-1] >= HI) & (m[1:] < HI)
last_up = np.full(N, -1, np.int64); last_dn = np.full(N, -1, np.int64)
lu = ld = -1
for k in range(N):
    if up_ib[k]: lu = k
    if dn_ib[k]: ld = k
    last_up[k] = lu; last_dn[k] = ld
print('# ws2Mage crossings into IB: %d from the LO side, %d from the HI side'
      % (int(up_ib.sum()), int(dn_ib.sum())), flush=True)

# ---- every ws12r oob crossing, either side
EV = []
r = np.asarray(R12[:N], float)
for k in range(1, N):
    for side in (+1, -1):
        now = (r[k] >= HI) if side > 0 else (r[k] <= LO)
        was = (r[k - 1] >= HI) if side > 0 else (r[k - 1] <= LO)
        if now and not was:
            # the open: the newest counter-dr ws2Mage crossing into IB at or before k
            o = int(last_up[k]) if side > 0 else int(last_dn[k])
            EV.append((k, side, o))
            break
print('# %d ws12r oob crossings; %d have an open, %d have none before them'
      % (len(EV), sum(1 for _, _, o in EV if o >= 0), sum(1 for _, _, o in EV if o < 0)),
      flush=True)

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
rows = []
for n, (ev, side, o) in enumerate(EV):
    if o < 0: continue
    a = C.run_leg(o, side)
    if a[0] is None: continue
    sa = score(o, side, a[0], a[1])
    armed = next((j for j, l in a[5] if l.startswith('exit-armed')), None)
    b = None; sb = None
    if a[1] in BFLIP:
        b = C.run_leg(a[0], -side)
        if b[0] is not None: sb = score(a[0], -side, b[0], b[1])
    rows.append(dict(ev=ev, side=side, open=o, armed=armed,
                     axk=a[0], awhy=a[1], ahand=a[4], **{'a' + k2: v for k2, v in sa.items()},
                     bxk=(b[0] if b else None), bwhy=(b[1] if b else None),
                     **({'b' + k2: v for k2, v in sb.items()} if sb else {})))
    if n % 400 == 0: print('#   %d of %d ...' % (n, len(EV)), flush=True)
print('# %d pseudo trades scored' % len(rows), flush=True)

_days = sorted({DAY(k) for k in range(0, N, 2000)})
BLK = {'all': set(_days), 'fit': set(_days[:47]), 'hold': set(_days[47:])}
dist = {(x['open'], x['side']) for x in rows}
print('\n# THE POPULATION')
box(('the measure', 'all 95 days', 'fit', 'hold'),
    [(lab, str(f(rows)), str(f([x for x in rows if DAY(x['ev']) in BLK['fit']])),
      str(f([x for x in rows if DAY(x['ev']) in BLK['hold']])))
     for lab, f in (('ws12r oob events scored', len),
                    ('DISTINCT pseudo trades — same open bar and side',
                     lambda z: len({(x['open'], x['side']) for x in z})),
                    ('A opened LONG — ws12r high oob', lambda z: sum(1 for x in z if x['side'] > 0)),
                    ('A opened SHORT — ws12r low oob', lambda z: sum(1 for x in z if x['side'] < 0)),
                    ('the walk ARMED before the interchange',
                     lambda z: sum(1 for x in z if x['armed'] is not None and x['armed'] <= x['ev'])),
                    ('A exited on an exhaustion or reversal — B opened',
                     lambda z: sum(1 for x in z if x['awhy'] in BFLIP)),
                    ('A delegated to >ws12r oob',
                     lambda z: sum(1 for x in z if x['ahand'] is not None)))])

print('\n# A-TRADE BY EXIT REASON')
w = collections.Counter(x['awhy'] for x in rows)
box(('A\'s exit', 'trades', 'as %', 'mean MAE', 'mean MFE scored', 'mean realised',
     'MFE/MAE', 'mean hold min'),
    [(k2, str(c), '%.1f%%' % (100.0 * c / len(rows)),
      '%.4f' % np.mean([x['amae'] for x in rows if x['awhy'] == k2]),
      '%.4f' % np.mean([x['amfe'] for x in rows if x['awhy'] == k2]),
      '%+.4f' % np.mean([x['areal'] for x in rows if x['awhy'] == k2]),
      '%.4f' % (sum(x['amfe'] for x in rows if x['awhy'] == k2)
                / sum(x['amae'] for x in rows if x['awhy'] == k2))
      if sum(x['amae'] for x in rows if x['awhy'] == k2) else '—',
      '%.1f' % np.mean([mn(x['open'], x['axk']) for x in rows if x['awhy'] == k2]))
     for k2, c in w.most_common()])

bb = [x for x in rows if x.get('bwhy')]
if bb:
    print('\n# THE B-TRADES — %d of %d events' % (len(bb), len(rows)))
    wb = collections.Counter(x['bwhy'] for x in bb)
    box(('B\'s exit', 'trades', 'as %', 'mean MAE', 'mean MFE scored', 'mean realised', 'MFE/MAE'),
        [(k2, str(c), '%.1f%%' % (100.0 * c / len(bb)),
          '%.4f' % np.mean([x['bmae'] for x in bb if x['bwhy'] == k2]),
          '%.4f' % np.mean([x['bmfe'] for x in bb if x['bwhy'] == k2]),
          '%+.4f' % np.mean([x['breal'] for x in bb if x['bwhy'] == k2]),
          '%.4f' % (sum(x['bmfe'] for x in bb if x['bwhy'] == k2)
                    / sum(x['bmae'] for x in bb if x['bwhy'] == k2))
          if sum(x['bmae'] for x in bb if x['bwhy'] == k2) else '—')
         for k2, c in wb.most_common()])
    print('\n# A AND B TOGETHER, on the %d events where B opened' % len(bb))
    box(('block', 'events', 'mean A realised', 'mean B realised', 'mean A+B',
         'A+B positive', 'A MFE/MAE', 'B MFE/MAE'),
        [(blk, str(len(z)),
          '%+.4f' % np.mean([x['areal'] for x in z]),
          '%+.4f' % np.mean([x['breal'] for x in z]),
          '%+.4f' % np.mean([x['areal'] + x['breal'] for x in z]),
          '%d of %d' % (sum(1 for x in z if x['areal'] + x['breal'] > 0), len(z)),
          '%.4f' % (sum(x['amfe'] for x in z) / sum(x['amae'] for x in z))
          if sum(x['amae'] for x in z) else '—',
          '%.4f' % (sum(x['bmfe'] for x in z) / sum(x['bmae'] for x in z))
          if sum(x['bmae'] for x in z) else '—')
         for blk in ('all', 'fit', 'hold')
         for z in [[x for x in bb if DAY(x['ev']) in BLK[blk]]] if z])
