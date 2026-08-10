"""htf_oppose — can an opposing HTF Mage-vs-r read avoid the losing trades? Joe 0803 10:05.

    Joe: "if an HTF line's momo is opposing the trades direction, how many of the negative (our ~minus 2.9
    trades) can we avoid?"

THE TEST. At the ENTRY bar, for each HTF rung, is the Mage on the wrong side of its own r for the trade's
direction:  LONG (hi breach) opposed when Mage < r ;  SHORT (lo breach) opposed when Mage > r.
Skip the trade when opposed. Mage-vs-r is Joe's own later formulation ("maybe the momo bar is Mage
crossing r towards bias"); momo() with its level gate at 50 fired on 40 rungs out of 40 and cannot
discriminate.

BOTH SIDES OF THE LEDGER ARE REPORTED. A filter that removes losers by removing everything is not a
filter, so losers avoided is shown against winners lost, with the resulting mean/median/total.

ENTRY  s4Mage OOB, dwell > 30 s     EXIT  s6x X s6M, wob 72, both lines OOB, NO STOP
LINES  s4M bb37|0.70@4  s6M bb37|0.70@6  s6x bb5|0.37@6  HTF Mage bb37|0.83  r = R.LN['r']
"""
import os, sys, datetime as dt
os.environ.setdefault('RPL_TF_CEILING', '120')
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import optimus9.orchestration.rpl_walk as R
from optimus9.analysis.jig import Jig, bbline, _Causal
from optimus9.compute.indicator_computer import IndicatorComputer as IC
W0=int(dt.datetime(2026,7,21,tzinfo=dt.timezone.utc).timestamp()*1000)
W1=int(dt.datetime(2026,7,31,tzinfo=dt.timezone.utc).timestamp()*1000)
DWELL=6; WOB=72; RUNGS=[15,22,30,45,60,90,120]
ovr={}
ovr.update(bbline('p4',4.0,length=37,mult=0.70,src='close'))
ovr.update(bbline('m6',6.0,length=37,mult=0.70,src='close'))
ovr.update(bbline('x6',6.0,length=5, mult=0.37,src='close'))
ovr.update(bbline('s1b',1.0,length=37,mult=0.83,src='close'))
for t in RUNGS:
    ovr.update(bbline('M%d'%t,float(t),length=37,mult=0.83,src='close'))
    ovr.update(R._mk('r%d'%t,float(t),R.LN['r']))
with Jig(W1,hours=int((W1-W0)/3600000),warmup=60,overrides=ovr) as j:
    ts=np.asarray(j.ts,np.int64); base=j.W.base
    evt=base['volume'].to_numpy(dtype=float)>0
    src=IC.build_source(base,R.PXS_CFG['src']); ei=np.flatnonzero(evt)
    px=np.full(len(src),np.nan); px[ei]=IC.dema(src[ei],int(R.PXS_CFG['len']))
    f=np.isfinite(px); ix=np.where(f,np.arange(len(px)),0); np.maximum.accumulate(ix,out=ix)
    px=px[ix]; px[:int(np.argmax(f))]=px[int(np.argmax(f))]
    M4=np.asarray(j.W.line('p4'),float); M6=np.asarray(j.W.line('m6'),float)
    X6=np.asarray(j.W.line('x6'),float); S1=np.asarray(j.W.line('s1b'),float)
    MG={t:np.asarray(j.W.line('M%d'%t),float) for t in RUNGS}
    RL_={t:np.asarray(j.W.line('r%d'%t),float) for t in RUNGS}
n=len(ts); HI,LO=R.HI,R.LO
cau=_Causal(None); dd=X6-M6
OH=(X6>=HI)&(M6>=HI); OL=(X6<=LO)&(M6<=LO)
cd=cau.cross_wob(dd,0.0,-1,WOB); cu=cau.cross_wob(dd,0.0,1,WOB)
EV={1:(cd&~np.r_[False,cd[:-1]])&OH, -1:(cu&~np.r_[False,cu[:-1]])&OL}
def runs_of(m):
    idx=np.flatnonzero(m)
    if not len(idx): return []
    out=[];a=idx[0];p=idx[0]
    for i in idx[1:]:
        if i!=p+1: out.append((a,p)); a=i
        p=i
    out.append((a,p)); return out
ALLR=[]
for side in ('hi','lo'):
    for x,y in runs_of((M4>=HI) if side=='hi' else (M4<=LO)): ALLR.append((int(x),int(y),side))
ALLR.sort(); QUAL=[r for r in ALLR if (r[1]-r[0]+1)>DWELL]
def runlen(m):
    idx=np.arange(len(m)); rst=np.where(m,0,idx+1)
    return (idx+1)-np.maximum.accumulate(rst)
RLS={'hi':runlen(S1>=HI-15),'lo':runlen(S1<=LO+15)}
def mk(alt=None,hold=None):
    out=[]
    for x,y,side in QUAL:
        if not (W0<=ts[x]<W1): continue
        if alt is not None:
            e=[p for p in alt if p[0]<x]
            if not e or e[-1][2]==side: continue
        if hold is not None and (x-1<0 or RLS[side][x-1]<hold): continue
        out.append((x,1 if side=='hi' else -1))
    return out
def trade(x,sgn):
    ev=EV[sgn]; nz=np.flatnonzero(ev[x+1:])
    e=(x+1+int(nz[0])) if len(nz) else (n-1)
    return sgn*(px[e]-px[x])/px[x]*100.0
for setname,EX in (('baseline',mk()),('ALT-strict',mk(alt=QUAL))):
    T=[(x,sgn,trade(x,sgn)) for x,sgn in EX]
    r0=np.array([t[2] for t in T]); L0=int((r0<0).sum())
    print('\n=== %s   n=%d  losers %d  total %.2f%%  mean %.3f%%  worst %.3f%% ==='
          % (setname,len(T),L0,r0.sum(),r0.mean(),r0.min()))
    print('  %-6s %6s %8s %9s %9s %9s %9s %9s' %
          ('rung','kept','of n','losers av','winners lost','total %','mean %','worst %'))
    for t_ in RUNGS:
        keep=[]; 
        for x,sgn,ret in T:
            if not (np.isfinite(MG[t_][x]) and np.isfinite(RL_[t_][x])): continue
            opposed = (MG[t_][x] < RL_[t_][x]) if sgn>0 else (MG[t_][x] > RL_[t_][x])
            if not opposed: keep.append(ret)
        if len(keep)<10: continue
        k=np.array(keep)
        lost_w=int((r0>0).sum())-int((k>0).sum()); av_l=L0-int((k<0).sum())
        print('  s%-5d %6d %7.0f%% %9s %12s %9.2f %9.3f %9.3f'
              % (t_,len(k),100*len(k)/len(T),'%d/%d'%(av_l,L0),'%d/%d'%(lost_w,int((r0>0).sum())),
                 k.sum(),k.mean(),k.min()))
    print('  --- COMPLEMENT: take ONLY the trades where the HTF Mage OPPOSES ---')
    print('  %-6s %6s %8s %9s %9s %9s %9s' % ('rung','kept','of n','losers','loss%','total %','mean %'))
    for t_ in RUNGS:
        opp=[]
        for x,sgn,ret in T:
            if not (np.isfinite(MG[t_][x]) and np.isfinite(RL_[t_][x])): continue
            o=(MG[t_][x]<RL_[t_][x]) if sgn>0 else (MG[t_][x]>RL_[t_][x])
            if o: opp.append(ret)
        if len(opp)<10: continue
        k=np.array(opp)
        print('  s%-5d %6d %7.0f%% %9d %8.0f%% %9.2f %9.3f'
              % (t_,len(k),100*len(k)/len(T),int((k<0).sum()),100*(k<0).mean(),k.sum(),k.mean()))
