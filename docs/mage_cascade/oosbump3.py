"""oosbump3 - Joe 0918: OOS bump-count validation against forward market direction.

EVENT   ws1Mage ENTERS oob on the dr side and HOLDS for dwell 3 bars (= 15 s).
        dwell 3 is the jig's own ws1mage_rev `dwell_ok` leg, reused - not a new number.
        The cascade is read AT the entry bar.  No mfall filter on the event: mfall and
        mbump are columns, so every bump count shows up.
SCORE   fwd = (px[b + mins*12] - px[b]) / px[b] * 100 * dr        12 bars = 1 min at 5 s
        NEGATIVE = price moved AGAINST dr = the direction a falling cascade implies.
"""
exec(open('oosbump.py').read().split('A0,A1=int(np.searchsorted')[0])
import numpy as np, pickle, datetime as _dt
DWELL=3
A0,A1=int(np.searchsorted(ts,ms(D0))),int(np.searchsorted(ts,ms(D1)))
fin=np.isfinite(Mst).all(axis=0)&np.isfinite(Rst).all(axis=0)&np.isfinite(PXT)
base = oob1 & (DR!=0) & fin
prev=np.zeros(n,bool); prev[1:]=base[:-1]
samedr=np.zeros(n,bool); samedr[1:]=(DR[1:]==DR[:-1])
entry = base & ~(prev & samedr)
hold=np.ones(n,bool)
for k in range(1,DWELL):
    h=np.zeros(n,bool); h[:n-k]=base[k:]&(DR[k:]==DR[:n-k]); hold&=h
MAXH=max(MINS)*BPM
e=np.flatnonzero(entry&hold); e=e[(e>=A0)&(e<A1)&(e+MAXH<=n-1)]
rows=[]
for b in e:
    b=int(b); dd=int(DR[b]); P0=float(PXT[b])
    q=dict(b=b,t=T(b),dr=dd,mbump=int(mbump[b]),rbump=int(rbump[b]),noob=int(noob[b]),
           mfall=float(mfall[b]),rfall=float(rfall[b]),
           m1=float(Mst[0,b]),m12=float(Mst[-1,b]),r2=float(Rst[0,b]),r12=float(Rst[-1,b]),
           day=T(b)[:10])
    for k in MINS: q['f%d'%k]=float((PXT[b+k*BPM]-P0)/P0*100.0*dd)
    rows.append(q)
pickle.dump(rows,open('oosbump3.pkl','wb'))
F={k:np.array([r['f%d'%k] for r in rows]) for k in MINS}
MB=np.array([r['mbump'] for r in rows]); MF=np.array([r['mfall'] for r in rows])
RB=np.array([r['rbump'] for r in rows]); RF=np.array([r['rfall'] for r in rows])
DAY=np.array([r['day'] for r in rows])
def line(lab,m):
    k=int(m.sum())
    if k==0: print('T|%s|0|||||||' % lab); return
    ds=sorted(set(DAY[m])); dn=0
    for dd in ds:
        s=m&(DAY==dd)
        if F[60][s].mean()<0: dn+=1
    print('T|%s|%d|%+.3f|%+.3f|%+.3f|%+.3f|%+.3f|%.0f%%|%d|%.0f%%' %
          (lab,k,F[30][m].mean(),F[45][m].mean(),F[60][m].mean(),F[90][m].mean(),F[120][m].mean(),
           100*(F[60][m]<0).mean(),len(ds),100*dn/len(ds)))
print('EVENTS %d   dr +1 %d   dr -1 %d   days %d' % (len(rows),(np.array([r['dr'] for r in rows])>0).sum(),
      (np.array([r['dr'] for r in rows])<0).sum(),len(set(DAY))))
print()
print('T|set|n|30m|45m|60m|90m|120m|hit% 60m|days|days neg 60m')
line('ALL ws1Mage oob entries',np.ones(len(rows),bool))
line('mage falls <= 0',MF<=0)
line('mage falls > 0',MF>0)
print('T|')
for k in range(0,12):
    line('falls>0 + bumps = %d'%k, (MF>0)&(MB==k))
print('T|')
for k in range(0,12):
    line('falls>0 + bumps <= %d'%k, (MF>0)&(MB<=k))
