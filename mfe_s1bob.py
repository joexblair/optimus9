"""mfe_s1bob — the 07-21..07-31 excursion count, filtered on s1Mage bobbing the bias side. Joe 0803 07:55.

    Joe: "filter on s1Mage bobbing on the bias side. ie for a lo breach s4Mage, require s1Mage to have
    been loosely/fuzzy lo oob for > 2 minutes"

BASELINE it filters (mfe_0721.py): 776 s4Mage OOB excursions with dwell > 30 s, of which 326 = 42.0%
ran MFE > 0.75% in the breach direction to the next swing_detect 1% pivot.

THREE THINGS WERE UNSPECIFIED AND ALL THREE ARE SWEPT, NOT CHOSEN
  fuzzy    the boundary relaxed by T: lo side s1M <= LO + T, hi side s1M >= HI - T.  T = 0,5,10,15,20
  "> 2 min" at least 24 bars WORTH of fuzzy-oob inside a trailing window W. W = 24,48,120 bars = 2/4/10
           min. At W=24 that is continuous; at W=120 it is bobbing — 2 minutes of touches inside 10.
  s1M mult Joe set 0.83 for gcs15/gcs30/s5/s6; the rsd set that contains s1 is 0.7. BOTH are run.
  All measured strictly BEFORE the s4Mage crossing bar, so the filter is causal.
"""
import os, sys, datetime as dt
os.environ.setdefault('RPL_TF_CEILING', '4')
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import optimus9.orchestration.rpl_walk as R
from optimus9.analysis.jig import Jig, bbline
from optimus9.compute.indicator_computer import IndicatorComputer as IC
from optimus9.compute.swing_detect import find_pivots
u = lambda m: dt.datetime.fromtimestamp(int(m)/1000, dt.timezone.utc).strftime('%m-%d %H:%M')
W0 = int(dt.datetime(2026,7,21,tzinfo=dt.timezone.utc).timestamp()*1000)
W1 = int(dt.datetime(2026,7,31,tzinfo=dt.timezone.utc).timestamp()*1000)
DWELL, PCT, BAR, NEED = 6, 1.0, 0.75, 24        # NEED = 24 bars = 2 min worth

ovr = {}
ovr.update(bbline('m4', 4.0, length=37, mult=0.70, src='close'))
ovr.update(bbline('s1a', 1.0, length=37, mult=0.70, src='close'))
ovr.update(bbline('s1b', 1.0, length=37, mult=0.83, src='close'))
with Jig(W1, hours=int((W1-W0)/3600000), warmup=24, overrides=ovr) as j:
    ts = np.asarray(j.ts, np.int64); base = j.W.base
    evt = base['volume'].to_numpy(dtype=float) > 0
    src = IC.build_source(base, R.PXS_CFG['src']); ei = np.flatnonzero(evt)
    px = np.full(len(src), np.nan); px[ei] = IC.dema(src[ei], int(R.PXS_CFG['len']))
    f = np.isfinite(px); ix = np.where(f, np.arange(len(px)), 0); np.maximum.accumulate(ix, out=ix)
    px = px[ix]; px[:int(np.argmax(f))] = px[int(np.argmax(f))]
    M4 = np.asarray(j.W.line('m4'), float)
    S1 = {0.70: np.asarray(j.W.line('s1a'), float), 0.83: np.asarray(j.W.line('s1b'), float)}
n = len(ts); HI, LO = R.HI, R.LO
piv = find_pivots(px, pct=PCT); pv = np.array([p[0] for p in piv], int)
EX = []
for side, sgn in (('hi',1), ('lo',-1)):
    o = (M4 >= HI) if side=='hi' else (M4 <= LO)
    idx = np.flatnonzero(o)
    runs=[]; a=idx[0]; prev=idx[0]
    for i in idx[1:]:
        if i != prev+1: runs.append((a,prev)); a=i
        prev=i
    runs.append((a,prev))
    for x,y in runs:
        if (y-x+1) <= DWELL or not (W0 <= ts[x] < W1): continue
        nx = pv[pv > x]
        if not len(nx): continue
        p0=px[x]; seg=px[x:int(nx[0])+1]
        mfe = ((np.nanmax(seg)-p0) if sgn>0 else (p0-np.nanmin(seg)))/p0*100.0
        EX.append((int(x), side, sgn, float(mfe)))
base_m = np.array([e[3] for e in EX])
print('BASELINE  excursions %d   MFE > %.2f%%: %d (%.1f%%)   median %.3f%%'
      % (len(EX), BAR, int((base_m>BAR).sum()), 100*(base_m>BAR).mean(), np.median(base_m)))
print('\n%-6s %-4s %-4s %8s %10s %10s %10s' % ('mult','T','W','kept','of 776','hit>0.75','median'))
for mult in (0.70, 0.83):
    s1 = S1[mult]
    for T in (0,5,10,15,20):
        fz_hi = s1 >= HI - T; fz_lo = s1 <= LO + T
        for W in (24,48,120):
            c_hi = np.convolve(fz_hi.astype(np.int32), np.ones(W,np.int32), 'full')[:n]
            c_lo = np.convolve(fz_lo.astype(np.int32), np.ones(W,np.int32), 'full')[:n]
            keep=[]
            for x, side, sgn, mfe in EX:
                b = x-1                                    # strictly BEFORE the crossing
                if b < W: continue
                cnt = (c_hi if side=='hi' else c_lo)[b]
                if cnt >= NEED: keep.append(mfe)
            if len(keep) < 15: continue
            k = np.array(keep)
            print('%-6.2f %-4d %-4d %8d %9.1f%% %9.1f%% %9.3f%%'
                  % (mult, T, W, len(k), 100*len(k)/len(EX), 100*(k>BAR).mean(), np.median(k)))
