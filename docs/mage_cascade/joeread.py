"""joeread - Joe 0918, his own internal process. MAGE IS THE GATE. r is confluence at best.

  MAGE (primary)  lowest TF's value vs highest TF's value, a downward line between them with
                  allowance for bumps, and ws1 oob. "that's all I do for the Mages".
  r  (confluence) same shape, ws1r IGNORED - "laggy and moves a lot regardless" - and looser on
                  bumps. NEVER part of the gate. Reported so we can see if it adds anything.

  mfall  dr * (ws1Mage - ws12Mage)    the Mage endpoint line. > 0 = falls away from the oob end
  mbump  Mage steps running against that line, of 11
  oob1   ws1Mage oob on the dr side
  rfall  dr * (ws2r - ws12r)          reported only
  rbump  r steps against, of 10       reported only
"""
import os, sys, numpy as np, datetime as dt
sys.path.insert(0,'/home/joe/thecodes')
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'stopsweep.py')).read().split("print()\nprint('STOP|stop%|")[0])
MM={t:Ln(t,'Mage') for t in range(1,13)}; RR={t:Ln(t,'r') for t in range(1,13)}
HI,LO=85.0,15.0
def read(b,d):
    m=np.array([MM[t][b] for t in range(1,13)],float)
    r=np.array([RR[t][b] for t in range(2,13)],float)
    ms=d*-np.diff(m); rs=d*-np.diff(r)
    return dict(mfall=float(d*(m[0]-m[-1])), mbump=int((ms<0).sum()),
                oob1=bool((m[0]>=HI) if d>0 else (m[0]<=LO)),
                noob=sum(1 for t in range(1,13) if ((MM[t][b]>=HI) if d>0 else (MM[t][b]<=LO))),
                rfall=float(d*(r[0]-r[-1])), rbump=int((rs<0).sum()),
                m1=float(m[0]), m12=float(m[-1]), r2=float(r[0]), r12=float(r[-1]))
T=lambda i: dt.datetime.fromtimestamp(int(ts[i])/1000,dt.timezone.utc).strftime('%m-%d %H:%M:%S')
print('EX|bar|dr|ws1Mage|ws12Mage|MAGE FALLS|mage bumps /11|ws1 oob|lower TFs oob|ws2r|ws12r|r falls|r bumps /10')
for tgt in ((2026,9,1,17,26,20),(2026,9,2,16,24,30)):
    b=int(np.searchsorted(ts,int(dt.datetime(*tgt,tzinfo=dt.timezone.utc).timestamp()*1000)))
    q=read(b,1)
    print('EX|%s|%+d|%.2f|%.2f|%+.1f|%d|%s|%d|%.2f|%.2f|%+.1f|%d' %
          (T(b),1,q['m1'],q['m12'],q['mfall'],q['mbump'],q['oob1'],q['noob'],q['r2'],q['r12'],q['rfall'],q['rbump']))
R=[]
for o in OUT:
    t=o['t']; b=int(t['ob']); d=int(t['dr']); P0=float(PXT[b])
    q=read(b,d); q['ob']=b; q['dr']=d
    for mins in (30,60,120):
        j=min(len(PXT)-1,b+mins*12); q['f%d'%mins]=float((PXT[j]-P0)/P0*100.0*d)
    seg=(PXT[b:min(len(PXT)-1,b+60*12)+1]-P0)/P0*100.0*d; q['mae60']=float(-seg.min())
    R.append(q)
import numpy as _n
F60=_n.array([r['f60'] for r in R]); F120=_n.array([r['f120'] for r in R])
MF=_n.array([r['mfall'] for r in R]); MB=_n.array([r['mbump'] for r in R])
O1=_n.array([r['oob1'] for r in R]); RF=_n.array([r['rfall'] for r in R])
MAE=_n.array([r['mae60'] for r in R])
rng=_n.random.default_rng(11)
def bs(lab,m):
    k=int(m.sum())
    if k==0: return
    o60=F60[m].mean(); o120=F120[m].mean()
    idx=rng.integers(0,len(R),size=(10000,k))
    p60=(F60[idx].mean(axis=1)<=o60).mean(); p120=(F120[idx].mean(axis=1)<=o120).mean()
    print('BS|%s|%d|%+.3f|%.4f|%+.3f|%.4f|%.3f|%.0f%%' %
          (lab,k,o60,p60,o120,p120,MAE[m].mean(),100*(RF[m]>0).mean()))
print()
print('BS|THE MAGE GATE|n|fwd 60m|p|fwd 120m|p|MAE 60m|r also falls')
bs('ALL 122',_n.ones(len(R),bool))
bs('ws1 oob',O1)
bs('mage falls > 0',MF>0)
bs('ws1 oob + mage falls',O1&(MF>0))
print('BS|')
for mb in (0,1,2,3,4):
    bs('ws1 oob + mage falls + bumps<=%d'%mb, O1&(MF>0)&(MB<=mb))
print('BS|')
for X in (10,20,30,40,50):
    bs('ws1 oob + mage falls>=%d'%X, O1&(MF>=X))
