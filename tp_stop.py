"""tp_stop — TP x stop grid over the s4M / s6M excursion sets. Joe 0803 08:40.

    Joe: "from all of these datasets, which TP would produce the most return if we had a 0.3 or 0.4 stop"

PATH SIMULATION, not MFE. MFE is the best excursion and says nothing about whether a stop was hit first.
Each excursion is walked bar by bar from the crossing:
    stop checked FIRST at each bar, then TP  — one pxs value per bar so there is no intra-bar ambiguity;
                                               checking the stop first is the conservative order
    terminal: if neither is hit by the next swing_detect 1% pivot, exit AT the pivot price
    return  : +TP on a win, -STOP on a loss, else the realised move to the pivot. GROSS - no fees,
              no slippage, no funding.
SETS: s4Mage and s6Mage producers, each unfiltered and with its best well-populated s1Mage hold filter.
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
TPS=[0.4,0.75,1.0,1.5,2.0,2.5,3.0,4.0,5.0,7.0,10.0]   # extended: the first grid's optimum sat on its own cap at 2.0
STOPS=[0.3,0.4]
ovr={}
for nm,tf,mu in (('p4',4.0,0.70),('p6',6.0,0.70),('s1a',1.0,0.70),('s1b',1.0,0.83)):
    ovr.update(bbline(nm,tf,length=37,mult=mu,src='close'))
with Jig(W1,hours=int((W1-W0)/3600000),warmup=24,overrides=ovr) as j:
    ts=np.asarray(j.ts,np.int64); base=j.W.base
    evt=base['volume'].to_numpy(dtype=float)>0
    src=IC.build_source(base,R.PXS_CFG['src']); ei=np.flatnonzero(evt)
    px=np.full(len(src),np.nan); px[ei]=IC.dema(src[ei],int(R.PXS_CFG['len']))
    f=np.isfinite(px); ix=np.where(f,np.arange(len(px)),0); np.maximum.accumulate(ix,out=ix)
    px=px[ix]; px[:int(np.argmax(f))]=px[int(np.argmax(f))]
    P={'s4':np.asarray(j.W.line('p4'),float),'s6':np.asarray(j.W.line('p6'),float)}
    S1={0.70:np.asarray(j.W.line('s1a'),float),0.83:np.asarray(j.W.line('s1b'),float)}
n=len(ts); HI,LO=R.HI,R.LO
pv=np.array([p[0] for p in find_pivots(px,pct=PCT)],int)
def runlen(mask):
    idx=np.arange(len(mask)); rst=np.where(mask,0,idx+1)
    return (idx+1)-np.maximum.accumulate(rst)
def excursions(M):
    out=[]
    for side,sgn in (('hi',1),('lo',-1)):
        o=(M>=HI) if side=='hi' else (M<=LO)
        idx=np.flatnonzero(o); runs=[]; a=idx[0]; prev=idx[0]
        for i in idx[1:]:
            if i!=prev+1: runs.append((a,prev)); a=i
            prev=i
        runs.append((a,prev))
        for x,y in runs:
            if (y-x+1)<=DWELL or not (W0<=ts[x]<W1): continue
            nx=pv[pv>x]
            if len(nx): out.append((int(x),side,sgn,int(nx[0])))
    return out
def sim(EX,tp,stop):
    rets=[]; wins=losses=timeout=0
    for x,side,sgn,pend in EX:
        p0=px[x]; tpp=p0*(1+sgn*tp/100); stp=p0*(1-sgn*stop/100)
        done=False
        for i in range(x+1,pend+1):
            v=px[i]
            if (v<=stp) if sgn>0 else (v>=stp):
                rets.append(-stop); losses+=1; done=True; break
            if (v>=tpp) if sgn>0 else (v<=tpp):
                rets.append(tp); wins+=1; done=True; break
        if not done:
            rets.append(sgn*(px[pend]-p0)/p0*100.0); timeout+=1
    r=np.array(rets)
    return len(r), r.sum(), r.mean(), wins, losses, timeout, 100*wins/max(1,len(r))
SETS={}
for pk in ('s4','s6'):
    EX=excursions(P[pk]); SETS['%s unfiltered'%pk]=EX
    mult,T,H = (0.83,15,120) if pk=='s4' else (0.70,15,120)
    RL={'hi':runlen(S1[mult]>=HI-T),'lo':runlen(S1[mult]<=LO+T)}
    SETS['%s + s1hold %s/%d/%d'%(pk,mult,T,H)]=[e for e in EX if e[0]-1>=0 and RL[e[1]][e[0]-1]>=H]
for nm,EX in SETS.items():
    print('\n=== %s   n=%d ===' % (nm,len(EX)))
    print('  %-6s %-6s %6s %10s %9s %7s %7s %7s %7s' % ('stop','TP','n','SUM %','mean %','wins','loss','timeout','win%'))
    best=None
    for stop in STOPS:
        for tp in TPS:
            c,s_,m_,w,l,t_,wr = sim(EX,tp,stop)
            if best is None or s_>best[0]: best=(s_,stop,tp)
            print('  %-6.2f %-6.2f %6d %10.2f %9.3f %7d %7d %7d %6.1f%%' % (stop,tp,c,s_,m_,w,l,t_,wr))
    print('  BEST: stop %.2f  TP %.2f  ->  %.2f%% total' % (best[1],best[2],best[0]))
