"""wob_sweep_exit — sweep the exit-cross debounce for best PnL. Joe 0803 09:35.

    Joe: "find the best wob for the best pnl"

CONTEXT. exit_s6x.py used the RAW sign change of (s6x - s6M) and fired 9 crosses/hour each way where Joe
reads 2-3. Measured: the median cross holds 7 bars = 35 s, and 49.5% reverse within 30 s. So roughly
two-thirds of those exits fired on a flicker. cross_wob at 24 bars = 120 s reproduces Joe's visual rate.

SWEPT   wob 1..72 bars (1 = raw, no debounce)   x   stop 0 / 0.30 / 0.40 / 0.60   x   4 entry sets
EXIT    rising edge of cross_wob(s6x - s6M, 0, dir, wob), AND both s6x and s6M out of bounds on the
        breach side at that bar. hi breach -> crossunder; lo -> crossover.
LINES   s4M bb 37|0.70 @4   s6M bb 37|0.70 @6   s6x bb 5|0.37 @6   s1M bb 37|0.83 @1
TERMINAL no cross before the data ends -> exit at the last bar. No horizon.
GROSS   no fees, no slippage, no funding.
"""
import os, sys, datetime as dt
os.environ.setdefault('RPL_TF_CEILING', '6')
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
import optimus9.orchestration.rpl_walk as R
from optimus9.analysis.jig import Jig, bbline, _Causal
from optimus9.compute.indicator_computer import IndicatorComputer as IC
W0=int(dt.datetime(2026,7,21,tzinfo=dt.timezone.utc).timestamp()*1000)
W1=int(dt.datetime(2026,7,31,tzinfo=dt.timezone.utc).timestamp()*1000)
DWELL=6; WOBS=[1,5,9,12,18,24,36,48,72]
STOPS=[0.0,0.30,0.40,0.60,0.80,1.00,1.25,1.50,2.00,3.00]   # Joe 0803: widen to bound the left tail
ovr={}
ovr.update(bbline('p4',4.0,length=37,mult=0.70,src='close'))
ovr.update(bbline('m6',6.0,length=37,mult=0.70,src='close'))
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
cau=_Causal(None); dd=X6-M6
OH=(X6>=HI)&(M6>=HI); OL=(X6<=LO)&(M6<=LO)
EXITS={}
for w in WOBS:
    cd=cau.cross_wob(dd,0.0,-1,w); cu=cau.cross_wob(dd,0.0,1,w)
    EXITS[(w,1)]=(cd&~np.r_[False,cd[:-1]])&OH      # hi breach -> crossunder, both oob hi
    EXITS[(w,-1)]=(cu&~np.r_[False,cu[:-1]])&OL
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
RL={'hi':runlen(S1>=HI-15),'lo':runlen(S1<=LO+15)}
def mk(alt=None,hold=None,loose=False):
    """alt: require the previous OOB to be the OPPOSITE side.
    loose (Joe 0803): also keep a SAME-side repeat if s4Mage traversed past 50 between the end of the
    previous excursion and the start of this one — hi needs M4 strictly below 50, lo strictly above."""
    out=[]
    for x,y,side in QUAL:
        if not (W0<=ts[x]<W1): continue
        if alt is not None:
            e=[p for p in alt if p[0]<x]
            if not e: continue
            pstart,pend,pside=e[-1]
            if pside==side:
                if not loose: continue
                seg=M4[pend:x+1]
                crossed=(seg<50).any() if side=='hi' else (seg>50).any()
                if not crossed: continue
        if hold is not None and (x-1<0 or RL[side][x-1]<hold): continue
        out.append((x,1 if side=='hi' else -1))
    return out
# cross-exit bar per (set-member, wob), computed ONCE; the stop is then a lookup on the running extreme
_CROSSBAR={}
def crossbar(x,sgn,w):
    k=(x,sgn,w)
    if k not in _CROSSBAR:
        ev=EXITS[(w,sgn)]
        nz=np.flatnonzero(ev[x+1:])
        _CROSSBAR[k]=(x+1+int(nz[0])) if len(nz) else (n-1)
    return _CROSSBAR[k]

def sim(EX,w,stop):
    rets=[];hold=[];st=0
    for x,sgn in EX:
        p0=px[x]; e=crossbar(x,sgn,w)
        seg=px[x+1:e+1]
        if len(seg)==0:
            rets.append(0.0); hold.append(0); continue
        hit=-1
        if stop>0:
            stp=p0*(1-sgn*stop/100)
            run=np.minimum.accumulate(seg) if sgn>0 else np.maximum.accumulate(seg)
            bad=(run<=stp) if sgn>0 else (run>=stp)
            nz=np.flatnonzero(bad)
            if len(nz): hit=int(nz[0])
        if hit>=0:
            rets.append(-stop); st+=1; hold.append(hit+1)
        else:
            rets.append(sgn*(px[e]-p0)/p0*100.0); hold.append(e-x)
    r=np.array(rets)
    return len(r),r.sum(),r.mean(),float(np.median(r)),100*(r>0).mean(),st,float(np.median(hold))*5/60
SETS={'baseline':mk(),'ALT-strict':mk(alt=QUAL),'ALT-loose50':mk(alt=QUAL,loose=True),
      'ALTstrict+hold':mk(alt=QUAL,hold=120),'ALTloose+hold':mk(alt=QUAL,loose=True,hold=120)}
ROWS=[]
for nm,EX in SETS.items():
    for w in WOBS:
        for s_ in STOPS:
            c,su,me,md,wr,stp_,hm=sim(EX,w,s_)
            ROWS.append((nm,w,s_,c,su,me,md,wr,stp_,hm))
SPAN_MIN=(ts[-1]-ts[0])/60000.0
def line(r):
    conc=r[3]*r[9]/SPAN_MIN
    return '%-14s %4d %5.2f %5d %9.2f %8.3f %8.3f %6.1f%% %6d %8.1f %7.2fx' % (r+(conc,))
print('%-14s %4s %5s %5s %9s %8s %8s %7s %6s %8s %8s' %
      ('set','wob','stop','n','SUM %','mean %','med %','win%','stops','med min','concur'))
print('--- TOP 12 by TOTAL PnL ---')
for r in sorted(ROWS,key=lambda z:-z[4])[:10]: print(line(r))
print('--- TOP 12 by MEAN per trade ---')
for r in sorted(ROWS,key=lambda z:-z[5])[:10]: print(line(r))
for nm in ('ALT-strict','ALT-loose50','ALTloose+hold'):
    print('--- %s, every wob, no stop ---' % nm)
    for r in [x for x in ROWS if x[0]==nm and x[2]==0.0]: print(line(r))
print('--- set sizes: %s ---' % ', '.join('%s=%d'%(k,len(v)) for k,v in SETS.items()))
