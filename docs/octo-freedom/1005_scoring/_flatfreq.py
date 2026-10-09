"""HOW OFTEN WOULD #7 FIRE — the flat-tail frequency at a ws12r oob dwell-ending. 1009.

Joe 1009: *"it's unlikley that we will see a flat line for ws60 because ws12 has been travelling:
the matryoshkaic nature says that the ws12r oob stretch (currently 6 minutes) is 2 samples of
ws60r's decision table that are lagging the ws12r oob, let alone ws12r running flat after it's
oob / if the coin flip let's us down too often, I'll have a rethink"*.

So the exposure to #7's measured-null premise is just its FIRING RATE, and that is measurable now.

MEASURED at every ws12r oob dwell-ending over 95 days, on the sampling the mech will use:
  the samples   block extremes, block = 60 bars = 5 min (Joe 1009: "5 minutes stays")
  flat          two consecutive samples EXACTLY equal (Joe 1009: "exactly equal")
  the tail      swept over 1, 2, 3, 6 and 12 samples, because TRAJ_TAIL_TF_SAMP is unset
  #7 fires      when EVERY sample in the tail is flat against its predecessor AND the deferral
                finds no non-flat sample inside the lookback either

Both the dr-side and the counter-dr-side sample series are built, since the block walk's extreme
depends on which side it hunts. A sample is 'flat' if it equals the previous sample on that series.

ALSO CHECKED, Joe's arithmetic: oob_gate_bars 72 = 6.0 min against a 5-min block.
"""
import os, sys, datetime, collections
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import _chain10 as C

SC, box, U = C.SC, C.box, C.SC.U
N = len(SC.ts)
R60 = np.asarray(SC.LD(60 * 60, 'r'), float)[:N]
R12 = C.R[C.TRIG_TF]
HI, LO = SC.HI, SC.LO
GATE, BLOCK = C.GATE_BARS, 60
LOOK = {2.0: int(2.0 * 60 * 60 / 5), 2.5: int(2.5 * 60 * 60 / 5)}   # TRAJ_MULTI_TF_SAMP x 60 min
DAY = lambda k: datetime.datetime.fromtimestamp(int(SC.ts[k]) / 1000,
                                               datetime.timezone.utc).strftime('%Y-%m-%d')
_days = sorted({DAY(k) for k in range(0, N, 2000)})
BLK = {'all': set(_days), 'fit': set(_days[:47]), 'hold': set(_days[47:])}
print('# oob_gate_bars %d = %.1f min. block %d bars = %.1f min -> the oob stretch spans %.2f samples'
      % (GATE, GATE * 5 / 60.0, BLOCK, BLOCK * 5 / 60.0, GATE / float(BLOCK)), flush=True)
print('# lookback TRAJ_MULTI_TF_SAMP 2.0 -> %d bars = %.0f min; 2.5 -> %d bars = %.0f min'
      % (LOOK[2.0], LOOK[2.0] * 5 / 60.0, LOOK[2.5], LOOK[2.5] * 5 / 60.0), flush=True)

def samples(k, side, nmax):
    """The block extremes behind bar k on the dr-opposed side for `side`, newest first.
    block n covers [k - n*block, k - (n-1)*block), the test bar excluded, exactly as the
    divergence's step-3 walk does it."""
    out = []
    for n in range(1, nmax + 1):
        hi = k - (n - 1) * BLOCK
        lo = max(0, k - n * BLOCK)
        if hi <= 0 or lo >= hi: break
        cand = R60[lo:hi]
        if np.all(np.isnan(cand)): continue            # Joe 0921: skip an empty block
        m = lo + int(np.nanargmin(cand) if side > 0 else np.nanargmax(cand))
        out.append((int(m), float(R60[m])))
    return out

# every ws12r oob run that reaches the dwell-ending
EV = []
k = 1
while k < N:
    for side in (+1, -1):
        now = (float(R12[k]) >= HI) if side > 0 else (float(R12[k]) <= LO)
        was = (float(R12[k - 1]) >= HI) if side > 0 else (float(R12[k - 1]) <= LO)
        if now and not was:
            j = k
            while j < N and (((float(R12[j]) >= HI) if side > 0 else (float(R12[j]) <= LO))): j += 1
            if j - k > GATE + 1: EV.append((k + GATE + 1, side))
            break
    k += 1
print('# %d dwell-endings over 95 days' % len(EV), flush=True)

NS = {2.0: LOOK[2.0] // BLOCK, 2.5: LOOK[2.5] // BLOCK}
print('# the lookback holds %d samples at 2.0 and %d at 2.5' % (NS[2.0], NS[2.5]), flush=True)

for samp in (2.0, 2.5):
    print('\n# TRAJ_MULTI_TF_SAMP %.1f — lookback %d samples' % (samp, NS[samp]))
    rows = []
    for tail in (1, 2, 3, 6, 12):
        for blk in ('all', 'fit', 'hold'):
            n = flat_tail = nondef = 0
            dep = []
            for b, side in EV:
                if b >= N: continue
                if blk != 'all' and DAY(b) not in BLK[blk]: continue
                n += 1
                sv = samples(b, side, NS[samp])
                if len(sv) < 2: continue
                vals = [v for _, v in sv]
                # the tail's samples are flat when each equals the next-older one, EXACTLY
                tf = all(vals[i] == vals[i + 1] for i in range(min(tail, len(vals) - 1)))
                if not tf: continue
                flat_tail += 1
                # the deferral: step back one sample at a time for the first non-flat pair
                d = None
                for i in range(len(vals) - 1):
                    if vals[i] != vals[i + 1]: d = i + 1; break
                if d is None: nondef += 1
                else: dep.append(d)
            rows.append(('%d samples / %.0f min' % (tail, tail * BLOCK * 5 / 60.0), blk, str(n),
                         str(flat_tail),
                         '%.1f%%' % (100.0 * flat_tail / n) if n else '—',
                         str(nondef), '%.1f%%' % (100.0 * nondef / n) if n else '—',
                         ('%.1f' % (sum(dep) / len(dep))) if dep else '—',
                         str(max(dep)) if dep else '—'))
    box(('the tail', 'block', 'dwell-endings', 'tail entirely flat', 'as %',
         '**#7 FIRES** — nothing non-flat in the whole lookback', 'as %',
         'mean samples the deferral steps back', 'worst'), rows)
print('\n- "tail entirely flat" is where the deferral is NEEDED.')
print('- "#7 FIRES" is where the deferral finds nothing either, i.e. the whole lookback is flat.')
print('  That is the only population Joe\'s ws60Mage-vs-ws60r fallback is exposed to.')
