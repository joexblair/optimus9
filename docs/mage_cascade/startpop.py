"""startpop - Joe 0918: the 83-day OOS test with STARTED in place of ARRIVED. 30m and 45m only.

  STARTED   each of ws3r..ws12r carries its own SOURCE OOB = the oob side it last touched,
            walking back with no cap.  +1 = hi 85, -1 = lo 15, 0 = never touched either.
  nsame     how many of ws3r..ws12r share ws1Mage's source oob            0..10
  nopp      how many came from the OPPOSITE oob (set out toward ws1Mage)  0..10
  fwd       (px[b+mins*12] - px[b]) / px[b] * 100 * dr       12 bars = 1 min at the 5 s grid
            POSITIVE = price ran on toward ws1Mage's extreme (continuation)
            NEGATIVE = it turned away (reversal)
"""
exec(open('arrive.py').read().split('fin=np.isfinite(Mst)')[0])
import numpy as np, pickle
RSRC=np.vstack([ffill_side(R[t]) for t in range(3,13)])       # 10 x n, per-line source oob
nsame=(RSRC==DR[None,:]).sum(axis=0).astype(np.int16)
nopp =(RSRC==-DR[None,:]).sum(axis=0).astype(np.int16)
nnone=(RSRC==0).sum(axis=0).astype(np.int16)
fin=np.isfinite(Mst).all(axis=0)&np.isfinite(Rst).all(axis=0)&np.isfinite(PXT)
base=oob1&(DR!=0)&fin
prev=np.zeros(n,bool); prev[1:]=base[:-1]
samedr=np.zeros(n,bool); samedr[1:]=(DR[1:]==DR[:-1])
entry=base&~(prev&samedr)
hold=np.ones(n,bool)
for k in range(1,3):
    h=np.zeros(n,bool); h[:n-k]=base[k:]&(DR[k:]==DR[:n-k]); hold&=h
A0,A1=int(np.searchsorted(ts,ms(D0))),int(np.searchsorted(ts,ms(D1)))
e=np.flatnonzero(entry&hold); e=e[(e>=A0)&(e<A1)&(e+max(MINS)*BPM<=n-1)]
rows=[]
for b in e:
    b=int(b); dd=int(DR[b]); P0=float(PXT[b])
    rows.append(dict(b=b,day=T(b)[:10],dr=dd,nsame=int(nsame[b]),nopp=int(nopp[b]),nnone=int(nnone[b]),
        nr=int(nr[b]), mvote=int(mvote[b]),
        f30=float((PXT[b+30*BPM]-P0)/P0*100.0*dd), f45=float((PXT[b+45*BPM]-P0)/P0*100.0*dd)))
pickle.dump(rows,open('startpop.pkl','wb'))
F30=np.array([r['f30'] for r in rows]); F45=np.array([r['f45'] for r in rows])
NS=np.array([r['nsame'] for r in rows]); NO=np.array([r['nopp'] for r in rows])
NR=np.array([r['nr'] for r in rows]);    NN=np.array([r['nnone'] for r in rows])
MV=np.array([r['mvote'] for r in rows])
DRv=np.array([r['dr'] for r in rows]); B=np.array([r['b'] for r in rows]); DAY=np.array([r['day'] for r in rows])
def eff(m):
    bb=np.sort(B[m]); return 1+int((np.diff(bb)>1440).sum()) if len(bb) else 0
def L(p,lab,m):
    k=int(m.sum())
    if k==0: print('%s|%s|0|0|-|-|-|-|-'%(p,lab)); return
    ds=sorted(set(DAY[m])); dc=sum(1 for x in ds if F30[m&(DAY==x)].mean()>0)
    print('%s|%s|%d|%d|%+.3f|%+.3f|%.0f%%|%d|%.0f%%'%(p,lab,k,eff(m),
      F30[m].mean(),F45[m].mean(),100*(F30[m]>0).mean(),len(ds),100*dc/len(ds)))
H='|events|clusters|30m|45m|cont% 30m|days|days cont'
print('events %d   days %d   lines with no source yet: max %d of 10'%(len(rows),len(set(DAY)),NN.max()))
print()
print('A|STARTED - how many of ws3r..ws12r share ws1Mage source oob'+H)
for k in range(0,11): L('A','nsame = %d of 10'%k,NS==k)
print('A|')
for k in range(1,11): L('A','nsame >= %d of 10'%k,NS>=k)
print()
print('B|STARTED FROM THE OPPOSITE OOB - they set out toward ws1Mage extreme'+H)
for k in range(0,11): L('B','nopp = %d of 10'%k,NO==k)
print('B|')
for k in range(1,11): L('B','nopp >= %d of 10'%k,NO>=k)
print()
print('C|THE TWO TENSES SIDE BY SIDE'+H)
L('C','ALL',np.ones(len(rows),bool))
L('C','ARRIVED      nr > 0',NR>0)
L('C','not arrived  nr = 0',NR==0)
L('C','STARTED same nsame >= 8',NS>=8)
L('C','STARTED same nsame <= 2',NS<=2)
L('C','STARTED opp  nopp >= 8',NO>=8)
L('C','STARTED opp  nopp <= 2',NO<=2)
print('C|')
L('C','nopp >= 8 AND nr = 0   they set out, none made it',(NO>=8)&(NR==0))
L('C','nopp >= 8 AND nr > 0   they set out, some made it',(NO>=8)&(NR>0))
L('C','nsame >= 8 AND nr = 0',(NS>=8)&(NR==0))
L('C','nsame >= 8 AND nr > 0',(NS>=8)&(NR>0))
print()
print('D|BY dr'+H)
for lab,m in (('nopp >= 8, dr +1',(NO>=8)&(DRv>0)),('nopp >= 8, dr -1',(NO>=8)&(DRv<0)),
              ('nsame >= 8, dr +1',(NS>=8)&(DRv>0)),('nsame >= 8, dr -1',(NS>=8)&(DRv<0))):
    L('D',lab,m)
print()
print('E|STARTED r AGAINST THE ws5..ws12 MAGE VOTE'+H)
for lab,m in (('nopp >= 8 + mvote >= 6',(NO>=8)&(MV>=6)),('nopp >= 8 + mvote <= 2',(NO>=8)&(MV<=2)),
              ('nsame >= 8 + mvote >= 6',(NS>=8)&(MV>=6)),('nsame >= 8 + mvote <= 2',(NS>=8)&(MV<=2))):
    L('E',lab,m)
