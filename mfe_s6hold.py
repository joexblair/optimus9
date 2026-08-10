"""mfe_s6hold — same, EXCURSION PRODUCER IS s6Mage (Joe 0803 08:25: replace s4Mage with s6Mage, same config). Joe 0803 08:10.

    Joe: "find the best MFE mean and median"

FOLLOWS THE CONTINUITY FINDING. In mfe_s1bob.py the fuzziness tolerance T barely moved the result while
the window W moved it monotonically — 2 minutes of CONTINUOUS fuzzy-oob beat 2 minutes of touches spread
over 4 or 10. So the primary knob here is the UNBROKEN RUN length H, swept far wider, with T swept
alongside to confirm it stays irrelevant.

    HOLD = the unbroken run of s1Mage fuzzy-oob on the bias side, ending at the bar BEFORE the s4Mage
           crossing. Require run >= H bars. Causal — nothing at or after the crossing is read.
    fuzzy  lo side s1M <= LO + T ; hi side s1M >= HI - T
    H      6..720 bars = 30 s .. 60 min       T  0,5,10,15,20,30       s1M mult  0.70 and 0.83

Ranked by MFE mean and by MFE median. n is printed on every row so thin cells are visible rather than
hidden behind a good average.
"""
import os, sys, datetime as dt
os.environ.setdefault('RPL_TF_CEILING', '4')
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import optimus9.orchestration.rpl_walk as R
from optimus9.analysis.jig import Jig, bbline
from optimus9.compute.indicator_computer import IndicatorComputer as IC
from optimus9.compute.swing_detect import find_pivots
W0 = int(dt.datetime(2026,7,21,tzinfo=dt.timezone.utc).timestamp()*1000)
W1 = int(dt.datetime(2026,7,31,tzinfo=dt.timezone.utc).timestamp()*1000)
DWELL, PCT, BAR = 6, 1.0, 0.75

ovr = {}
ovr.update(bbline('m4', 6.0, length=37, mult=0.70, src='close'))
ovr.update(bbline('s1a', 1.0, length=37, mult=0.70, src='close'))
ovr.update(bbline('s1b', 1.0, length=37, mult=0.83, src='close'))
with Jig(W1, hours=int((W1-W0)/3600000), warmup=24, overrides=ovr) as j:
    ts=np.asarray(j.ts,np.int64); base=j.W.base
    evt=base['volume'].to_numpy(dtype=float)>0
    src=IC.build_source(base,R.PXS_CFG['src']); ei=np.flatnonzero(evt)
    px=np.full(len(src),np.nan); px[ei]=IC.dema(src[ei],int(R.PXS_CFG['len']))
    f=np.isfinite(px); ix=np.where(f,np.arange(len(px)),0); np.maximum.accumulate(ix,out=ix)
    px=px[ix]; px[:int(np.argmax(f))]=px[int(np.argmax(f))]
    M4=np.asarray(j.W.line('m4'),float)
    S1={0.70:np.asarray(j.W.line('s1a'),float), 0.83:np.asarray(j.W.line('s1b'),float)}
n=len(ts); HI,LO=R.HI,R.LO
pv=np.array([p[0] for p in find_pivots(px,pct=PCT)],int)
EX=[]
for side,sgn in (('hi',1),('lo',-1)):
    o=(M4>=HI) if side=='hi' else (M4<=LO)
    idx=np.flatnonzero(o); runs=[]; a=idx[0]; prev=idx[0]
    for i in idx[1:]:
        if i!=prev+1: runs.append((a,prev)); a=i
        prev=i
    runs.append((a,prev))
    for x,y in runs:
        if (y-x+1)<=DWELL or not (W0<=ts[x]<W1): continue
        nx=pv[pv>x]
        if not len(nx): continue
        p0=px[x]; seg=px[x:int(nx[0])+1]
        mfe=((np.nanmax(seg)-p0) if sgn>0 else (p0-np.nanmin(seg)))/p0*100.0
        EX.append((int(x),side,float(mfe)))
bm=np.array([e[2] for e in EX])
print('BASELINE n %d   MFE mean %.3f%%   median %.3f%%   hit>%.2f%% %.1f%%'
      % (len(EX), bm.mean(), np.median(bm), BAR, 100*(bm>BAR).mean()))
def runlen(mask):
    idx=np.arange(len(mask)); rst=np.where(mask,0,idx+1)
    return (idx+1)-np.maximum.accumulate(rst)
ROWS=[]
for mult in (0.70,0.83):
    s1=S1[mult]
    for T in (0,5,10,15,20,30):
        RL={'hi':runlen(s1>=HI-T), 'lo':runlen(s1<=LO+T)}
        for H in (6,12,24,36,48,72,120,180,240,360,480,720):
            keep=[m for x,side,m in EX if x-1>=0 and RL[side][x-1]>=H]
            if len(keep)<20: continue
            k=np.array(keep)
            ROWS.append((mult,T,H,len(k),k.mean(),float(np.median(k)),100*(k>BAR).mean()))
for label,key in (('MEAN',4),('MEDIAN',5)):
    print('\nTOP 10 by MFE %s' % label)
    print('  %-5s %-3s %-5s %6s %9s %9s %9s' % ('mult','T','H bars','n','mean%','median%','hit>0.75'))
    for r in sorted(ROWS,key=lambda z:-z[key])[:10]:
        print('  %-5.2f %-3d %-5d %6d %9.3f %9.3f %8.1f%%'
              % (r[0],r[1],r[2],r[3],r[4],r[5],r[6]))
