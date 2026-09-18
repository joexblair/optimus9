"""oosbump - Joe 0918: OOS the mage-cascade read, and validate the BUMP COUNT against the
resulting market direction at 30/45/60/90/120 minutes.

  window   OOS = 2026-06-10 00:00:00 -> 2026-09-01 00:00:00, entirely BEFORE the 09-01..09-06
           in-sample window the gate was built on. Tape runs 06-05 12:00 -> 09-07 23:59:55.

  the read (Joe's own process, Mage primary):
    mfall  dr * (ws1Mage - ws12Mage)   > 0 = the ladder falls away from the oob end
    mbump  Mage steps running against that line, out of 11
    oob1   ws1Mage oob on the dr side  (oob is always 15/85)

  event    an EPISODE: a maximal run of consecutive bars holding (oob1 AND mfall>0) at one dr.
           Scored at the episode's FIRST bar - that is the bar the read fires on. mbump is read
           at that same first bar.

  score    fwd = (px[b + mins*12] - px[b]) / px[b] * 100 * dr        12 bars = 1 min at 5 s
           NEGATIVE = price moved against dr = the direction the falling cascade implies.
"""
import os, sys, numpy as np, pandas as pd, datetime as dt
from datetime import timezone
sys.path.insert(0,'/home/joe/thecodes')
import walk_mom_models as W
from optimus9.analysis.jig import Jig
from optimus9.compute.line_config import override, mech_lines
from optimus9.orchestration.rpl_cache import LINE_DIR, TAPE_DIR, _line_key, _tape_key
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

D0,D1 = '2026-06-10 00:00:00','2026-09-01 00:00:00'
LATCH_TF, LATCH_W = 13, 8
HI,LO = 85.0,15.0
MINS = (30,45,60,90,120)
BPM  = 12                      # bars per minute on the 5 s grid

db=DatabaseManager(**get_db_config()); db.connect()
sy=db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l FROM optimus9_system WHERE sys_pk=1',fetch=True)[0]
spec={}
for g in mech_lines(db,'wsf'):
    if g['role'] not in spec:
        _t,s_,m_=g['override']; spec[g['role']]=(s_,m_)
db.disconnect()

ts=np.load(os.path.join(TAPE_DIR,_tape_key(END_MS,HOURS,WARMUP,{'src':sy['s'],'len':sy['l']})+'.npz'))['__ts__']
Ln=lambda tf,r_: np.load(os.path.join(LINE_DIR,_line_key(END_MS,HOURS,WARMUP,override(tf*60,*spec[r_]))+'.npy'))
M={t:Ln(t,'Mage') for t in range(1,13)}
R={t:Ln(t,'r')    for t in range(1,13)}
M13=Ln(LATCH_TF,'m'); n=len(ts)
with Jig(END_MS,hours=HOURS,warmup=WARMUP) as J:
    JT=np.asarray(J.ts,dtype=np.int64); PXS=pd.Series(np.asarray(J.px,float)).ffill().bfill().to_numpy()
PXT=PXS[np.clip(np.searchsorted(JT,ts),0,len(JT)-1)]
ms=lambda s:int(dt.datetime.strptime(s,'%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc).timestamp()*1000)
T =lambda i: dt.datetime.fromtimestamp(int(ts[i])/1000,tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
MHI,MLO=W.MAGE_HI,W.MAGE_LO

def dr_latch_wob(m1,mx,i0,i1,wob):
    out=np.zeros(len(m1),np.int8); cur=0; up=0; dn=0
    for k in range(int(i0),int(i1)+1):
        a,b=float(m1[k]),float(mx[k])
        if a==a and b==b:
            up = up+1 if (a>=MHI and b>=MHI) else 0
            dn = dn+1 if (a<=MLO and b<=MLO) else 0
            if up>=wob: cur=+1
            elif dn>=wob: cur=-1
        out[k]=cur
    return out
DR=dr_latch_wob(M[1],M13,0,n-1,LATCH_W)

# ── the read, vectorised over every bar ────────────────────────────────────────────────────
Mst=np.vstack([M[t] for t in range(1,13)])          # 12 x n, ws1Mage .. ws12Mage
Rst=np.vstack([R[t] for t in range(2,13)])          # 11 x n, ws2r .. ws12r  (ws1r ignored)
d=DR.astype(float)
mfall = d*(Mst[0]-Mst[-1])
rfall = d*(Rst[0]-Rst[-1])
msteps = -np.diff(Mst,axis=0)*d                      # 11 x n, >0 = that step continues the fall
rsteps = -np.diff(Rst,axis=0)*d                      # 10 x n
mbump = (msteps<0).sum(axis=0).astype(np.int16)
rbump = (rsteps<0).sum(axis=0).astype(np.int16)
oob1  = np.where(d>0, Mst[0]>=HI, np.where(d<0, Mst[0]<=LO, False))
noob  = np.where(d>0,(Mst>=HI),np.where(d<0,(Mst<=LO),False)).sum(axis=0).astype(np.int16)

A0,A1=int(np.searchsorted(ts,ms(D0))),int(np.searchsorted(ts,ms(D1)))
fin=np.isfinite(Mst).all(axis=0)&np.isfinite(Rst).all(axis=0)&np.isfinite(PXT)
cond = oob1 & (mfall>0) & (DR!=0) & fin

# ── episodes: first bar of each maximal constant-dr run of `cond` ─────────────────────────
prev=np.zeros(n,bool); prev[1:]=cond[:-1]
samedr=np.zeros(n,bool); samedr[1:]=(DR[1:]==DR[:-1])
start = cond & ~(prev & samedr)
cand=np.flatnonzero(start)
cand=cand[(cand>=A0)&(cand<A1)]
MAXH=max(MINS)*BPM
cand=cand[cand+MAXH<=n-1]

rows=[]
for b in cand:
    b=int(b); dd=int(DR[b]); P0=float(PXT[b])
    e=dict(b=b,t=T(b),dr=dd,mbump=int(mbump[b]),rbump=int(rbump[b]),noob=int(noob[b]),
           mfall=float(mfall[b]),rfall=float(rfall[b]),
           m1=float(Mst[0,b]),m12=float(Mst[-1,b]),r2=float(Rst[0,b]),r12=float(Rst[-1,b]))
    for k in MINS: e['f%d'%k]=float((PXT[b+k*BPM]-P0)/P0*100.0*dd)
    rows.append(e)

bars_in = int(cond[A0:A1].sum())
print('OOS window            %s -> %s' % (D0,D1))
print('bars in window        %d' % (A1-A0))
print('bars holding the read %d   (ws1Mage oob on the dr side AND mage falls > 0)' % bars_in)
print('EPISODES              %d   (maximal constant-dr runs, scored at the first bar)' % len(rows))
print('dr +1 %d      dr -1 %d' % (sum(1 for r in rows if r['dr']>0),sum(1 for r in rows if r['dr']<0)))
import pickle; pickle.dump(rows,open('oosbump.pkl','wb'))
