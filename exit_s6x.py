"""exit_s6x — the s6x X s6Mage exit, replacing the non-causal pivot. Joe 0803 09:15.

    Joe: "exit: use s6x crossing s6Mage (crossunder for hi breach)"

WHY THIS MATTERS MORE THAN ANY FILTER SO FAR. Every total reported tonight used the next swing_detect 1%
pivot as the exit, and find_pivots only confirms a pivot AFTER price has retraced 1% from the extreme — so
those numbers assumed an exit that cannot be seen coming. A line cross is observable at its own bar. This
is the first fully causal run.

    hi breach  exit when s6x crosses UNDER s6Mage
    lo breach  exit when s6x crosses OVER  s6Mage
    detector   raw sign change of (s6x - s6M), Joe 0803. No wobble tolerance.
    stop       checked first at each bar, 0.30 and 0.40
    no TP      every optimum in tp_stop.py and tp_alt.py had the TP unreachable with zero wins
    terminal   no cross before the data ends -> exit at the last bar. NO HORIZON.

LINES  s6x  bb  5 | 0.37 | close @ TF 6   R.LN['x']
       s6M  bb 37 | 0.83 | close @ TF 6   Joe 0803
       s4M  bb 37 | 0.70 | close @ TF 4   the excursion producer
       s1M  bb 37 | 0.83 | close @ TF 1   the hold filter
"""
import os, sys, datetime as dt
os.environ.setdefault('RPL_TF_CEILING', '6')
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import optimus9.orchestration.rpl_walk as R
from optimus9.analysis.jig import Jig, bbline
from optimus9.compute.indicator_computer import IndicatorComputer as IC
W0=int(dt.datetime(2026,7,21,tzinfo=dt.timezone.utc).timestamp()*1000)
W1=int(dt.datetime(2026,7,31,tzinfo=dt.timezone.utc).timestamp()*1000)
DWELL=6; STOPS=[0.0,0.3,0.4,0.6]      # 0.0 = no stop, for reference
ovr={}
ovr.update(bbline('p4',4.0,length=37,mult=0.70,src='close'))
ovr.update(bbline('m6',6.0,length=37,mult=0.70,src='close'))   # Joe 0803: s6Mage mult 0.83 -> 0.70
ovr.update(bbline('x6',6.0,length=5, mult=0.37,src='close'))
ovr.update(bbline('s1b',1.0,length=37,mult=0.83,src='close'))
with Jig(W1,hours=int((W1-W0)/3600000),warmup=24,overrides=ovr) as j:
    ts=np.asarray(j.ts,np.int64); base=j.W.base
    evt=base['volume'].to_numpy(dtype=float)>0
    src=IC.build_source(base,R.PXS_CFG['src']); ei=np.flatnonzero(evt)
    px=np.full(len(src),np.nan); px[ei]=IC.dema(src[ei],int(R.PXS_CFG['len']))
    f=np.isfinite(px); ix=np.where(f,np.arange(len(px)),0); np.maximum.accumulate(ix,out=ix)
    px=px[ix]; px[:int(np.argmax(f))]=px[int(np.argmax(f))]
    M4=np.asarray(j.W.line('p4'),float); M6=np.asarray(j.W.line('m6'),float)
    X6=np.asarray(j.W.line('x6'),float); S1=np.asarray(j.W.line('s1b'),float)
n=len(ts); HI,LO=R.HI,R.LO
dd=X6-M6; sg=np.sign(np.nan_to_num(dd,nan=0.0))
xdn_raw=np.r_[False,(sg[1:]<0)&(sg[:-1]>=0)]      # s6x crosses UNDER s6M
xup_raw=np.r_[False,(sg[1:]>0)&(sg[:-1]<=0)]      # crosses OVER
# Joe 0803: "require both x and Mage to be OOB before the cross". Both lines must be past the boundary
# on the breach side AT the cross bar, so a cross that happens mid-board does not count as an exit.
oob_hi=(X6>=HI)&(M6>=HI); oob_lo=(X6<=LO)&(M6<=LO)
xdn=xdn_raw&oob_hi; xup=xup_raw&oob_lo
print('s6x X s6M raw crosses: under %d over %d   BOTH-OOB gated: under %d over %d   of %d bars'
      % (int(xdn_raw.sum()),int(xup_raw.sum()),int(xdn.sum()),int(xup.sum()),n))
print('bars with both x+M oob: hi %d  lo %d' % (int(oob_hi.sum()),int(oob_lo.sum())))
def runs_of(mask):
    idx=np.flatnonzero(mask)
    if not len(idx): return []
    out=[];a=idx[0];prev=idx[0]
    for i in idx[1:]:
        if i!=prev+1: out.append((a,prev)); a=i
        prev=i
    out.append((a,prev)); return out
ALLR=[]
for side in ('hi','lo'):
    for x,y in runs_of((M4>=HI) if side=='hi' else (M4<=LO)): ALLR.append((int(x),int(y),side))
ALLR.sort(); QUAL=[r for r in ALLR if (r[1]-r[0]+1)>DWELL]
def runlen(mask):
    idx=np.arange(len(mask)); rst=np.where(mask,0,idx+1)
    return (idx+1)-np.maximum.accumulate(rst)
RL={'hi':runlen(S1>=HI-15),'lo':runlen(S1<=LO+15)}
def mk(alt=None, hold=None):
    out=[]
    for x,y,side in QUAL:
        if not (W0<=ts[x]<W1): continue
        if alt is not None:
            e=[p for p in alt if p[0]<x]
            if not e or e[-1][2]==side: continue
        if hold is not None and (x-1<0 or RL[side][x-1]<hold): continue
        out.append((x,side,1 if side=='hi' else -1))
    return out
def sim(EX,stop):
    rets=[];st=cr=term=0; holds=[]
    for x,side,sgn in EX:
        p0=px[x]; stp=p0*(1-sgn*stop/100) if stop>0 else None
        ev = xdn if sgn>0 else xup
        done=False
        for i in range(x+1,n):
            v=px[i]
            if stp is not None and ((v<=stp) if sgn>0 else (v>=stp)):
                rets.append(-stop); st+=1; holds.append(i-x); done=True; break
            if ev[i]:
                rets.append(sgn*(v-p0)/p0*100.0); cr+=1; holds.append(i-x); done=True; break
        if not done:
            rets.append(sgn*(px[-1]-p0)/p0*100.0); term+=1; holds.append(n-1-x)
    r=np.array(rets); h=np.array(holds)*5/60.0
    return len(r),r.sum(),r.mean(),float(np.median(r)),100*(r>0).mean(),st,cr,term,float(np.median(h))
SETS={'baseline':mk(),'ALT-qual':mk(alt=QUAL),'ALT-any':mk(alt=ALLR),
      'ALT-qual + s1hold120':mk(alt=QUAL,hold=120)}
for nm,EX in SETS.items():
    print('\n=== %s   n=%d ===' % (nm,len(EX)))
    print('  %-5s %6s %9s %9s %9s %7s %6s %6s %6s %8s' %
          ('stop','n','SUM %','mean %','med %','win%','stops','cross','term','med min'))
    for s_ in STOPS:
        c,su,me,md,wr,stp_,cr_,tm_,hm=sim(EX,s_)
        print('  %-5.2f %6d %9.2f %9.3f %9.3f %6.1f%% %6d %6d %6d %8.1f'
              % (s_,c,su,me,md,wr,stp_,cr_,tm_,hm))
