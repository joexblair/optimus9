import pickle, numpy as np
rows=pickle.load(open('arrive.pkl','rb'))
MINS=(30,45,60,90,120)
F={k:np.array([r['f%d'%k] for r in rows]) for k in MINS}
NR=np.array([r['nr'] for r in rows]); RCH=np.array([r['reach'] for r in rows])
MV=np.array([r['mvote'] for r in rows]); MAT=np.array([r['mat'] for r in rows])
DRv=np.array([r['dr'] for r in rows]); B=np.array([r['b'] for r in rows]); DAY=np.array([r['day'] for r in rows])
MB=np.array([r['mbump'] for r in rows]); MF=np.array([r['mfall'] for r in rows])
ARR=NR>0
def eff(m):
    bb=np.sort(B[m]); return 1+int((np.diff(bb)>1440).sum()) if len(bb) else 0
def L(p,lab,m):
    k=int(m.sum())
    if k==0: print('%s|%s|0|0|-|-|-|-|-|-|-'%(p,lab)); return
    ds=sorted(set(DAY[m])); dn=sum(1 for x in ds if F[60][m&(DAY==x)].mean()>0)
    print('%s|%s|%d|%d|%+.3f|%+.3f|%+.3f|%+.3f|%+.3f|%.0f%%|%d|%.0f%%'%(p,lab,k,eff(m),
      F[30][m].mean(),F[45][m].mean(),F[60][m].mean(),F[90][m].mean(),F[120][m].mean(),
      100*(F[60][m]>0).mean(),len(ds),100*dn/len(ds)))
H='|events|clusters|30m|45m|60m|90m|120m|cont% 60m|days|days cont'
print('A|THE ARRIVAL TEST - OOS 06-10 -> 09-01, 12992 ws1Mage oob entries'+H)
L('A','ALL',np.ones(len(rows),bool))
L('A','ARRIVED  - at least one of ws3r..ws12r at the source oob',ARR)
L('A','SHORT    - none of ws3r..ws12r reach it',~ARR)
print('A|')
L('A','ARRIVED, dr +1',ARR&(DRv>0)); L('A','ARRIVED, dr -1',ARR&(DRv<0))
L('A','SHORT,   dr +1',(~ARR)&(DRv>0)); L('A','SHORT,   dr -1',(~ARR)&(DRv<0))
print()
print('B|BY HOW MANY OF ws3r..ws12r ARRIVE'+H)
for k in range(0,11): L('B','nr = %d'%k,NR==k)
print()
print('C|BY DISTANCE TO THE SOURCE OOB  (reach, +ve = past it)'+H)
for lo,hi,lab in ((-100,-40,'short by more than 40'),(-40,-30,'short by 30 to 40'),(-30,-20,'short by 20 to 30'),
                  (-20,-10,'short by 10 to 20'),(-10,-5,'short by 5 to 10'),(-5,0,'short by 0 to 5'),
                  (0,5,'past by 0 to 5'),(5,10,'past by 5 to 10'),(10,100,'past by more than 10')):
    L('C',lab,(RCH>=lo)&(RCH<hi))
print()
print('D|THE MAGE SOURCE-OOB VOTE, ws5Mage..ws12Mage sharing ws1Mage source oob'+H)
for k in range(0,9): L('D','mvote = %d of 8'%k,MV==k)
print('D|')
for k in range(0,9): L('D','mvote >= %d of 8'%k,MV>=k)
print()
print('E|THE VOTE AS CONFLUENCE ON ARRIVAL'+H)
for lab,m in (('ARRIVED + mvote >= 6',ARR&(MV>=6)),('ARRIVED + mvote 3 to 5',ARR&(MV>=3)&(MV<=5)),
              ('ARRIVED + mvote <= 2',ARR&(MV<=2)),
              ('SHORT + mvote >= 6',(~ARR)&(MV>=6)),('SHORT + mvote 3 to 5',(~ARR)&(MV>=3)&(MV<=5)),
              ('SHORT + mvote <= 2',(~ARR)&(MV<=2))):
    L('E',lab,m)
print()
print('F|ws5Mage..ws12Mage AT the source oob right now (mat), for contrast'+H)
for k in range(0,9): L('F','mat = %d of 8'%k,MAT==k)
