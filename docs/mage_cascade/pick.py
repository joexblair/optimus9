"""pick - candidates for the 4 worked examples. SAME event in both windows:
   ws1Mage enters oob on the dr side, holds 3 bars. mfall>0. bumps <= 2 (the gate that reversed).
   IS  = 2026-09-01 -> 2026-09-06
   OOS = 2026-08-26 -> 2026-08-31  (late, so the TV window does not have to move far)
"""
exec(open('oosbump.py').read().split('A0,A1=int(np.searchsorted')[0])
import numpy as np, pickle
DWELL=3
fin=np.isfinite(Mst).all(axis=0)&np.isfinite(Rst).all(axis=0)&np.isfinite(PXT)
base=oob1&(DR!=0)&fin
prev=np.zeros(n,bool); prev[1:]=base[:-1]
samedr=np.zeros(n,bool); samedr[1:]=(DR[1:]==DR[:-1])
entry=base&~(prev&samedr)
hold=np.ones(n,bool)
for k in range(1,DWELL):
    h=np.zeros(n,bool); h[:n-k]=base[k:]&(DR[k:]==DR[:n-k]); hold&=h
MAXH=max(MINS)*BPM
def grab(d0,d1):
    a,b1=int(np.searchsorted(ts,ms(d0))),int(np.searchsorted(ts,ms(d1)))
    e=np.flatnonzero(entry&hold); e=e[(e>=a)&(e<b1)&(e+MAXH<=n-1)]
    out=[]
    for b in e:
        b=int(b); dd=int(DR[b]); P0=float(PXT[b])
        q=dict(b=b,t=T(b),dr=dd,mbump=int(mbump[b]),rbump=int(rbump[b]),noob=int(noob[b]),
               mfall=float(mfall[b]),rfall=float(rfall[b]))
        for k in MINS: q['f%d'%k]=float((PXT[b+k*BPM]-P0)/P0*100.0*dd)
        out.append(q)
    return out
IS=grab('2026-09-01 00:00:00','2026-09-06 00:00:00')
OS=grab('2026-08-26 00:00:00','2026-08-31 00:00:00')
pickle.dump(dict(IS=IS,OS=OS),open('pick.pkl','wb'))
def stat(lab,rs):
    m=[r for r in rs if r['mfall']>0 and r['mbump']<=2]
    bb=np.sort([r['b'] for r in m]); cl=1+int((np.diff(bb)>1440).sum()) if len(bb) else 0
    print('S|%s|%d|%d|%+.3f|%+.3f|%+.3f|%+.3f|%+.3f'%(lab,len(m),cl,
      *[np.mean([r['f%d'%k] for r in m]) for k in MINS]))
print('S|set (mfall>0, bumps<=2)|events|clusters|30m|45m|60m|90m|120m')
stat('IS 09-01 -> 09-06',IS)
stat('OOS 08-26 -> 08-31',OS)
print()
for lab,rs in (('IS',IS),('OS',OS)):
    m=[r for r in rs if r['mfall']>0 and r['mbump']<=2]
    m.sort(key=lambda r:r['f60'])
    print('P|%s  bumps<=2 sorted by 60m  (n=%d)'%(lab,len(m)))
    print('P|time|dr|bumps|falls|rbump|rfall|lowerTFs oob|30m|45m|60m|90m|120m')
    for r in m:
        print('P|%s|%+d|%d|%+.1f|%d|%+.1f|%d|%+.3f|%+.3f|%+.3f|%+.3f|%+.3f'%(r['t'],r['dr'],r['mbump'],
          r['mfall'],r['rbump'],r['rfall'],r['noob'],r['f30'],r['f45'],r['f60'],r['f90'],r['f120']))
    print('P|')
