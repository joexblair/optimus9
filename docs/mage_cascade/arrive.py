"""arrive - Joe 0918.

TEST 1  THE ARRIVAL TEST.  Do the overarching r lines reach ws1Mage's SOURCE OOB?
  source oob   hi 85 when dr +1 (ws1Mage sits at hi), lo 15 when dr -1.  oob is always 15/85.
  overarching  ws3r .. ws12r.  Joe 0918: "the lines above ws1,2".  ws1r ignored, ws2r is lower.
  nr           how many of ws3r..ws12r are AT the source oob, 0..10
  reach        dr+1: max(ws3r..ws12r) - 85    dr-1: 15 - min(ws3r..ws12r).   +ve = arrived

TEST 2  THE MAGE SOURCE-OOB VOTE, ws5Mage .. ws12Mage.
  a line's SOURCE OOB = the oob side it last touched, walking back with no cap.
    +1 = hi 85 was its last touch, -1 = lo 15, 0 = it has not touched either yet
  mvote        how many of ws5Mage..ws12Mage carry the SAME source oob as ws1Mage, 0..8
  mat          how many of ws5Mage..ws12Mage are AT that source oob right now, 0..8

SIGN  fwd = (px[b+mins*12] - px[b]) / px[b] * 100 * dr.
  POSITIVE = price ran on toward ws1Mage's extreme  = continuation
  NEGATIVE = price turned away from it              = reversal
"""
exec(open('oosbump.py').read().split('A0,A1=int(np.searchsorted')[0])
import numpy as np, pickle
DWELL=3
def ffill_side(v):
    s=np.zeros(len(v),np.int8); s[v>=HI]=1; s[v<=LO]=-1
    idx=np.where(s!=0,np.arange(len(s)),0); np.maximum.accumulate(idx,out=idx)
    return s[idx]
SRC={t:ffill_side(M[t]) for t in range(1,13)}          # per-line source oob, last touch, no cap
Rst3=np.vstack([R[t] for t in range(3,13)])            # ws3r .. ws12r, the overarching lines
d=DR.astype(float)
rmax=np.nanmax(Rst3,axis=0); rmin=np.nanmin(Rst3,axis=0)
reach=np.where(d>0, rmax-HI, np.where(d<0, LO-rmin, np.nan))
nr   =np.where(d>0,(Rst3>=HI),np.where(d<0,(Rst3<=LO),False)).sum(axis=0).astype(np.int16)
Mv=np.vstack([SRC[t] for t in range(5,13)])            # ws5Mage .. ws12Mage source oob sides
mvote=(Mv==DR[None,:]).sum(axis=0).astype(np.int16)
Mat=np.vstack([M[t] for t in range(5,13)])
mat =np.where(d>0,(Mat>=HI),np.where(d<0,(Mat<=LO),False)).sum(axis=0).astype(np.int16)
fin=np.isfinite(Mst).all(axis=0)&np.isfinite(Rst).all(axis=0)&np.isfinite(PXT)
base=oob1&(DR!=0)&fin
prev=np.zeros(n,bool); prev[1:]=base[:-1]
samedr=np.zeros(n,bool); samedr[1:]=(DR[1:]==DR[:-1])
entry=base&~(prev&samedr)
hold=np.ones(n,bool)
for k in range(1,DWELL):
    h=np.zeros(n,bool); h[:n-k]=base[k:]&(DR[k:]==DR[:n-k]); hold&=h
A0,A1=int(np.searchsorted(ts,ms(D0))),int(np.searchsorted(ts,ms(D1)))
MAXH=max(MINS)*BPM
e=np.flatnonzero(entry&hold); e=e[(e>=A0)&(e<A1)&(e+MAXH<=n-1)]
rows=[]
for b in e:
    b=int(b); dd=int(DR[b]); P0=float(PXT[b])
    q=dict(b=b,t=T(b),day=T(b)[:10],dr=dd,mbump=int(mbump[b]),rbump=int(rbump[b]),
           mfall=float(mfall[b]),rfall=float(rfall[b]),
           nr=int(nr[b]),reach=float(reach[b]),mvote=int(mvote[b]),mat=int(mat[b]))
    for k in MINS: q['f%d'%k]=float((PXT[b+k*BPM]-P0)/P0*100.0*dd)
    rows.append(q)
pickle.dump(rows,open('arrive.pkl','wb'))
print('events %d   days %d   dr +1 %d   dr -1 %d'%(len(rows),len(set(r['day'] for r in rows)),
   sum(1 for r in rows if r['dr']>0),sum(1 for r in rows if r['dr']<0)))
