"""the same event + read, run on the 09-01 -> 09-06 IN-SAMPLE window, as a consistency check."""
exec(open('oosbump_is.py').read().split('A0,A1=int(np.searchsorted')[0])
import numpy as np
DWELL=3
A0,A1=int(np.searchsorted(ts,ms(D0))),int(np.searchsorted(ts,ms(D1)))
fin=np.isfinite(Mst).all(axis=0)&np.isfinite(Rst).all(axis=0)&np.isfinite(PXT)
base=oob1&(DR!=0)&fin
prev=np.zeros(n,bool); prev[1:]=base[:-1]
samedr=np.zeros(n,bool); samedr[1:]=(DR[1:]==DR[:-1])
entry=base&~(prev&samedr)
hold=np.ones(n,bool)
for k in range(1,DWELL):
    h=np.zeros(n,bool); h[:n-k]=base[k:]&(DR[k:]==DR[:n-k]); hold&=h
MAXH=max(MINS)*BPM
e=np.flatnonzero(entry&hold); e=e[(e>=A0)&(e<A1)&(e+MAXH<=n-1)]
F={k:[] for k in MINS}; MBl=[]; MFl=[]; DRl=[]; Bl=[]
for b in e:
    b=int(b); dd=int(DR[b]); P0=float(PXT[b])
    for k in MINS: F[k].append(float((PXT[b+k*BPM]-P0)/P0*100.0*dd))
    MBl.append(int(mbump[b])); MFl.append(float(mfall[b])); DRl.append(dd); Bl.append(b)
F={k:np.array(v) for k,v in F.items()}
MB=np.array(MBl); MF=np.array(MFl); DRv=np.array(DRl); B=np.array(Bl)
def eff(m):
    bb=np.sort(B[m]); return 1+int((np.diff(bb)>1440).sum()) if len(bb) else 0
def L(lab,m):
    k=int(m.sum())
    if k==0: print('I|%s|0|0|||||'%lab); return
    print('I|%s|%d|%d|%+.3f|%+.3f|%+.3f|%+.3f|%+.3f|%.0f%%'%(lab,k,eff(m),
      F[30][m].mean(),F[45][m].mean(),F[60][m].mean(),F[90][m].mean(),F[120][m].mean(),100*(F[120][m]<0).mean()))
print('I|IN-SAMPLE 09-01 -> 09-06, same event, same read|events|clusters|30m|45m|60m|90m|120m|hit% 120m')
L('ALL ws1Mage oob entries',np.ones(len(B),bool))
L('falls>0 + bumps <= 7',(MF>0)&(MB<=7))
L('falls>0 + bumps >= 8',(MF>0)&(MB>=8))
L('falls>0 + bumps >= 8, dr +1',(MF>0)&(MB>=8)&(DRv>0))
L('falls>0 + bumps >= 8, dr -1',(MF>0)&(MB>=8)&(DRv<0))
L('falls>0 + bumps <= 7, dr -1',(MF>0)&(MB<=7)&(DRv<0))
