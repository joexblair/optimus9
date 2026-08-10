"""tp_alt — TP x stop grid with the ALTERNATION filter. Joe 0803 09:00.

    Joe: "filter out any s4Mage OOBs that were last OOB on the same side - eg the s4Mage must travel from
    hi OOB to low OOB"

Keep an excursion only if the PREVIOUS one was on the opposite side. Two readings of "last OOB", both run:
    QUAL  the previous DWELL-QUALIFIED excursion (>30 s), the same population being traded
    ANY   the previous OOB touch of any length, grazes included
Causal: the previous excursion is strictly in the past.

Exit rule carried from tp_stop.py: stop checked first each bar, then TP; terminal is the next 1% pivot.
CAVEAT STANDING: the pivot exit is NOT causal - find_pivots confirms only after a 1% retrace - so totals
here are an upper bound, not an executable strategy. The stop and the filter are causal; the exit is not.
"""
import os, sys, datetime as dt
os.environ.setdefault('RPL_TF_CEILING', '4')
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import optimus9.orchestration.rpl_walk as R
from optimus9.analysis.jig import Jig, bbline
from optimus9.compute.indicator_computer import IndicatorComputer as IC
from optimus9.compute.swing_detect import find_pivots
W0=int(dt.datetime(2026,7,21,tzinfo=dt.timezone.utc).timestamp()*1000)
W1=int(dt.datetime(2026,7,31,tzinfo=dt.timezone.utc).timestamp()*1000)
DWELL,PCT=6,1.0
TPS=[0.4,0.75,1.0,1.5,2.0,3.0,5.0,10.0]; STOPS=[0.3,0.4]
ovr={}
for nm,tf,mu in (('p4',4.0,0.70),('s1b',1.0,0.83)):
    ovr.update(bbline(nm,tf,length=37,mult=mu,src='close'))
with Jig(W1,hours=int((W1-W0)/3600000),warmup=24,overrides=ovr) as j:
    ts=np.asarray(j.ts,np.int64); base=j.W.base
    evt=base['volume'].to_numpy(dtype=float)>0
    src=IC.build_source(base,R.PXS_CFG['src']); ei=np.flatnonzero(evt)
    px=np.full(len(src),np.nan); px[ei]=IC.dema(src[ei],int(R.PXS_CFG['len']))
    f=np.isfinite(px); ix=np.where(f,np.arange(len(px)),0); np.maximum.accumulate(ix,out=ix)
    px=px[ix]; px[:int(np.argmax(f))]=px[int(np.argmax(f))]
    M4=np.asarray(j.W.line('p4'),float); S1=np.asarray(j.W.line('s1b'),float)
n=len(ts); HI,LO=R.HI,R.LO
pv=np.array([p[0] for p in find_pivots(px,pct=PCT)],int)
def runs_of(mask):
    idx=np.flatnonzero(mask)
    if not len(idx): return []
    out=[]; a=idx[0]; prev=idx[0]
    for i in idx[1:]:
        if i!=prev+1: out.append((a,prev)); a=i
        prev=i
    out.append((a,prev)); return out
ALLR=[]
for side in ('hi','lo'):
    for x,y in runs_of((M4>=HI) if side=='hi' else (M4<=LO)):
        ALLR.append((int(x),int(y),side))
ALLR.sort()
QUAL=[r for r in ALLR if (r[1]-r[0]+1)>DWELL]
print('OOB runs total %d   dwell-qualified %d' % (len(ALLR),len(QUAL)))
def build(prev_pool):
    out=[]
    for k,(x,y,side) in enumerate(QUAL):
        if not (W0<=ts[x]<W1): continue
        earlier=[p for p in prev_pool if p[0]<x]
        if not earlier: continue
        if earlier[-1][2]==side: continue           # same side as the previous -> drop
        nx=pv[pv>x]
        if len(nx): out.append((x,side,1 if side=='hi' else -1,int(nx[0])))
    return out
def base_set():
    out=[]
    for x,y,side in QUAL:
        if not (W0<=ts[x]<W1): continue
        nx=pv[pv>x]
        if len(nx): out.append((x,side,1 if side=='hi' else -1,int(nx[0])))
    return out
def runlen(mask):
    idx=np.arange(len(mask)); rst=np.where(mask,0,idx+1)
    return (idx+1)-np.maximum.accumulate(rst)
RL={'hi':runlen(S1>=HI-15),'lo':runlen(S1<=LO+15)}
def sim(EX,tp,stop):
    rets=[];w=l=t=0
    for x,side,sgn,pend in EX:
        p0=px[x]; tpp=p0*(1+sgn*tp/100); stp=p0*(1-sgn*stop/100); done=False
        for i in range(x+1,pend+1):
            v=px[i]
            if (v<=stp) if sgn>0 else (v>=stp): rets.append(-stop); l+=1; done=True; break
            if (v>=tpp) if sgn>0 else (v<=tpp): rets.append(tp); w+=1; done=True; break
        if not done: rets.append(sgn*(px[pend]-p0)/p0*100.0); t+=1
    r=np.array(rets); return len(r),r.sum(),r.mean(),w,l,t
SETS={'baseline (no alternation)':base_set(),
      'ALT vs previous QUALIFIED':build(QUAL),
      'ALT vs previous ANY OOB':build(ALLR)}
SETS['ALT-QUAL + s1hold 0.83/15/120']=[e for e in SETS['ALT vs previous QUALIFIED']
                                       if e[0]-1>=0 and RL[e[1]][e[0]-1]>=120]
for nm,EX in SETS.items():
    if not EX: continue
    print('\n=== %s   n=%d ===' % (nm,len(EX)))
    print('  %-5s %-6s %6s %9s %9s %6s %6s %7s' % ('stop','TP','n','SUM %','mean %','wins','loss','t-out'))
    for stop in STOPS:
        for tp in TPS:
            c,s_,m_,w,l,t_=sim(EX,tp,stop)
            print('  %-5.2f %-6.2f %6d %9.2f %9.3f %6d %6d %7d' % (stop,tp,c,s_,m_,w,l,t_))
