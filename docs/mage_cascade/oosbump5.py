import pickle, numpy as np
rows=pickle.load(open('oosbump3.pkl','rb'))
MINS=(30,45,60,90,120)
F={k:np.array([r['f%d'%k] for r in rows]) for k in MINS}
MB=np.array([r['mbump'] for r in rows]); MF=np.array([r['mfall'] for r in rows])
DRv=np.array([r['dr'] for r in rows]); B=np.array([r['b'] for r in rows]); DAY=np.array([r['day'] for r in rows])
def eff(m):
    bb=np.sort(B[m]); return 1+int((np.diff(bb)>1440).sum()) if len(bb) else 0
def L(lab,m):
    k=int(m.sum())
    if k==0: print('C|%s|0|0|||||' % lab); return
    print('C|%s|%d|%d|%+.3f|%+.3f|%+.3f|%+.3f|%+.3f|%.0f%%' %
      (lab,k,eff(m),F[30][m].mean(),F[45][m].mean(),F[60][m].mean(),F[90][m].mean(),F[120][m].mean(),
       100*(F[120][m]<0).mean()))
print('C|the two dr sides, every bump bucket|events|clusters|30m|45m|60m|90m|120m|hit% 120m')
for d,nm in ((+1,'dr +1'),(-1,'dr -1')):
    for k in (0,1,2,3,4,5,6,7,8,9,10):
        L('%s  bumps = %d'%(nm,k),(MF>0)&(MB==k)&(DRv==d))
    print('C|')
