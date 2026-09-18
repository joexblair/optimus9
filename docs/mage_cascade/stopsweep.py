"""exit121 - Joe 0917: re-exit the config that ran immediately before the Mage cascade, using the
ws1mage-rev column from the 121 stretchy-leash rows.

BASELINE = past50.py trigger form 0 ("as now"), unchanged:
  dr latch ws13m wob 8 | trigger ws3r momentum-true | ws1x hunt wob 3 | ladder ceiling ws12
  exit: ws1r dr-side oob run >= 12 bars AND ws1Mage oob -> arm, then ws1Mage oob->ib wob 4
  else the dr flip closes it.

NEW EXIT = the first ws1mage-rev timestamp in the 121 rows, STRICTLY AFTER the open, at the
trade's OWN dr. No matching event before the cycle ends -> the dr flip, as the baseline does.

--- original header ---
latchwob - Joe 0917: dr latch with a wob of 8 bars, across ws13m / ws14m / ws15m / ws16m.
Rule set otherwise as walk9: trigger ws3r momentum-true, ws1x wob 3, exit arm = the 2nd
divergence fire on ws1r at a gcws30Mage dr-side oob->ib wob 2 crossing kept when the hi tf r is
outside 17/83 on the dr side or flat on 40/60, exit = ws1Mage dr-side oob->ib wob 6, else dr flip.
"""
import os, sys, numpy as np, pandas as pd, datetime as dt
from datetime import timezone
sys.path.insert(0,'/home/joe/thecodes')
import walk_mom_models as W
from optimus9.analysis.jig import Jig, anchor_floater, AF_BLOCK, SR_SAMPLES, SR_TOL, SR_FENCE
from optimus9.compute.test_points import stretches, flat_run_at
from optimus9.compute.line_config import override, mech_lines
from optimus9.compute.momo_config import momo_bank
from optimus9.compute.momo_seam import seam_mask
from optimus9.compute.v3_config import v3_config
from optimus9.orchestration.rpl_cache import LINE_DIR, TAPE_DIR, _line_key, _tape_key
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
CFG=dict(momo_slope_min=0.05,momo_slack_ref=0.05,momo_r2_min=0.0,level_slack=40.0,momo_seam='skip_r2')
TRIG=3; CAP=12; DIV_WOB=2; OPEN_WOB=3; EXIT_WOB=6; NTH=2; LATCH_WOB=8
COINS=22000.0; DRAG=0.55; START=600.0
D0,D1='2026-09-01 00:00:00','2026-09-06 00:00:00'
db=DatabaseManager(**get_db_config()); db.connect()
C=v3_config(db)
sy=db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l FROM optimus9_system WHERE sys_pk=1',fetch=True)[0]
spec={}
for g in mech_lines(db,'wsf'):
    if g['role'] not in spec:
        _t,s_,m_=g['override']; spec[g['role']]=(s_,m_)
BK={t:momo_bank(db,t,version=1) for t in range(1,13)}
db.disconnect()
MFR=float(C['momo_fence_r']); FENCE=(MFR,100.0-MFR)
ts=np.load(os.path.join(TAPE_DIR,_tape_key(END_MS,HOURS,WARMUP,{'src':sy['s'],'len':sy['l']})+'.npz'))['__ts__']
Ln=lambda tf,r_: np.load(os.path.join(LINE_DIR,_line_key(END_MS,HOURS,WARMUP,override(tf*60,*spec[r_]))+'.npy'))
R={t:Ln(t,'r') for t in range(1,13)}; M={t:Ln(t,'Mage') for t in range(1,13)}
X1=Ln(1,'x'); n=len(ts)
ms=lambda s:int(dt.datetime.strptime(s,'%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc).timestamp()*1000)
us=lambda i: dt.datetime.fromtimestamp(int(ts[i])/1000,tz=timezone.utc).strftime('%H:%M:%S')
iw=int(np.searchsorted(ts,ms('2026-06-06 00:00:00')))
SEAM={t:seam_mask(ts,t) for t in range(1,13)}
with Jig(END_MS,hours=HOURS,warmup=WARMUP) as J:
    JT=np.asarray(J.ts,dtype=np.int64); PXS=pd.Series(np.asarray(J.px,float)).ffill().bfill().to_numpy()
    G30=np.asarray(J.causal.line('gcws30Mage'),float)
idx=np.clip(np.searchsorted(JT,ts),0,len(JT)-1)
PXT=PXS[idx]; G=G30[idx]
mt=lambda t,b,dr: W.momentum_true(R[t],BK[t],CFG,dr,b,SEAM[t],t)[0]
HI,LO=W.OOB_HI,W.OOB_LO
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
def mage1_cross(d,k,lim):
    o=(M[1]>=HI) if d>0 else (M[1]<=LO)
    for i in range(int(k),int(lim)):
        if o[i]: continue
        j=i-1;c=0
        while j>=0 and o[j]: c+=1; j-=1
        if c>=EXIT_WOB: return i
    return None
def x_open(b,lim,dr):
    run=0
    for i in range(b+1,lim):
        v=X1[i]
        if not np.isfinite(v): continue
        if (v<=LO) if dr>0 else (v>=HI): run+=1; continue
        if run>=OPEN_WOB: return i
        run=0
    return None
def divs(k0,k1,dr,hi):
    sh = dr>0; out=[]
    for i in range(int(k0),int(k1)):
        v=G[i]
        if not np.isfinite(v): continue
        if (v>=HI) if sh else (v<=LO): continue
        j=i-1;c=0
        while j>=0 and np.isfinite(G[j]) and ((G[j]>=HI) if sh else (G[j]<=LO)): c+=1; j-=1
        if c<DIV_WOB: continue
        d=anchor_floater(R[1],PXT,dr,i,block=AF_BLOCK,mid=50.0)
        if d is None or not d['fired']: continue
        hv=R[hi][i]
        outside=np.isfinite(hv) and ((hv>=FENCE[1]) if dr>0 else (hv<=FENCE[0]))
        if outside or flat_run_at(R[hi],i,dr,SR_FENCE,SR_SAMPLES,SR_TOL) is not None: out.append(i)
    return out
A0,A1=int(np.searchsorted(ts,ms(D0))),int(np.searchsorted(ts,ms(D1)))
def run(tf,wob):
    DRs=dr_latch_wob(M[1],Ln(tf,'m'),iw,n-1,wob)
    CYC=[s for s in stretches(DRs,iw,n) if s[1]>A0 and s[0]<A1]
    T=[]
    for F,Fp,dr in CYC:
        trig=None
        for i in range(F,Fp):
            if mt(TRIG,i,dr): trig=i; break
        if trig is None: continue
        xc=[u for u in range(TRIG+1,CAP+1) if mt(u,trig,dr)]
        hi=max(xc) if xc else TRIG
        ob=x_open(trig,Fp,dr)
        if ob is None: continue
        D=divs(trig,Fp,dr,hi)
        arm=D[NTH-1] if len(D)>=NTH else None
        if arm is None: eb,why=Fp,'dr flip'
        else:
            cb=mage1_cross(dr,max(ob,arm),Fp)
            eb,why=(cb,'ws1Mage') if cb is not None else (Fp,'dr flip')
        P0,PX=float(PXT[ob]),float(PXT[eb])
        T.append(dict(ob=ob,eb=eb,dr=dr,why=why,P0=P0,move=(PX-P0)/P0*100.0*dr,ndiv=len(D)))
    T.sort(key=lambda x:x['ob'])
    return CYC,T
import numpy as np
LATCH_TF=13; LATCH_W=8; R1_DWELL=12; M1_WOB=4
def new_exit(ob,lim,dr):
    r_oob=(R[1]>=HI) if dr>0 else (R[1]<=LO)
    m_oob=(M[1]>=HI) if dr>0 else (M[1]<=LO)
    run=0; arm=None
    for i in range(int(ob),int(lim)):
        run = run+1 if r_oob[i] else 0
        if run>=R1_DWELL and m_oob[i]: arm=i; break
    if arm is None: return None,None
    for i in range(arm,int(lim)):
        if m_oob[i]: continue
        j=i-1;c=0
        while j>=0 and m_oob[j]: c+=1; j-=1
        if c>=M1_WOB: return arm,i
    return arm,None
def trigger(F,Fp,dr,form):
    crossed = (form!='b')
    for i in range(F,Fp):
        if form=='b' and not crossed and i>0:
            a,b=R[TRIG][i-1],R[TRIG][i]
            if np.isfinite(a) and np.isfinite(b):
                ok = (a<=50 and b>50) if dr>0 else (a>=50 and b<50)
                if ok: crossed=True
        if not mt(TRIG,i,dr): continue
        if form=='a':
            j=i
            while j-1>=0 and j-1>=F-4000 and mt(TRIG,j-1,dr): j-=1
            if j<F: continue
        if form=='b' and not crossed: continue
        return i
    return None
def run3(form):
    DRs=dr_latch_wob(M[1],Ln(LATCH_TF,'m'),iw,n-1,LATCH_W)
    CYC=[s for s in stretches(DRs,iw,n) if s[1]>A0 and s[0]<A1]
    T=[]
    for F,Fp,dr in CYC:
        trig=trigger(F,Fp,dr,form)
        if trig is None: continue
        ob=x_open(trig,Fp,dr)
        if ob is None: continue
        arm,cb=new_exit(ob,Fp,dr)
        eb,why=(cb,'ws1Mage') if (arm is not None and cb is not None) else (Fp,'dr flip')
        P0,PX=float(PXT[ob]),float(PXT[eb])
        seg=(PXT[ob:eb+1]-P0)/P0*100.0*dr
        T.append(dict(F=F,trig=trig,ob=ob,eb=eb,dr=dr,why=why,P0=P0,move=float(seg[-1]),
                      mae=float(-seg.min()),mfe=float(seg.max())))
    T.sort(key=lambda x:x['ob']); return CYC,T

# ── the 121 stretchy-leash rows, from the packaged producers ─────────────────────────────────
from optimus9.compute.v3_config import v3_config as _v3c
import report_coil_exit as RCE
_db=DatabaseManager(**get_db_config()); _db.connect()
_C=_v3c(_db)
_knobs=_db.execute("SELECT wdv_knobs k FROM wsf_dtf_v3 GROUP BY 1 ORDER BY MAX(wdv_ms) DESC LIMIT 1",fetch=True)[0]['k']
_ts,_rows=RCE.walk(_db,_C,_knobs,D0,D1)
_db.disconnect()
EV={+1:[],-1:[]}
for r in _rows:
    if r['rev'] is not None: EV[r['mo']['dr']].append(int(r['rev']))
for d in EV: EV[d]=sorted(set(EV[d]))
print('  ws1mage-rev exit events from the 121 rows:  dr +1  %d      dr -1  %d      total %d'
      % (len(EV[+1]),len(EV[-1]),len(EV[+1])+len(EV[-1])))

def rev_exit(ob,dr):
    """Joe 0917: NO dr-flip fallback. The first ws1mage-rev strictly after `ob` at this dr,
    wherever it lands - the cycle end no longer closes the trade."""
    a=EV[dr]; i=np.searchsorted(a,int(ob)+1,'left')
    return a[i] if i<len(a) else None

CY,T=run3(0)
print()
print('  BASELINE  past50 form 0   window %s -> %s   cycles %d   trades %d' % (D0[:10],D1[:10],len(CY),len(T)))
OUT=[]
NOEX=[]
LAST=len(ts)-1
for t in T:
    rb=rev_exit(t['ob'],t['dr'])
    if rb is None:
        NOEX.append(t); eb=LAST; why='STILL OPEN'      # Joe 0917: realtime cannot filter entries
    else:
        eb=rb; why='ws1mage-rev'
    P0=t['P0']; seg=(PXT[t['ob']:eb+1]-P0)/P0*100.0*t['dr']
    OUT.append(dict(t=t,eb2=eb,why2=why,move2=float(seg[-1]),mae2=float(-seg.min()),mfe2=float(seg.max())))
import datetime as _dt
U=lambda i: _dt.datetime.fromtimestamp(int(ts[i])/1000,tz=timezone.utc).strftime('%m-%d %H:%M:%S')
print()
print('MD|#|dr|OPEN|base EXIT|base why|base move%|base MAE%|base MFE%|rev EXIT|rev why|rev move%|rev MAE%|rev MFE%|delta move%|hold base min|hold rev min')
for i,o in enumerate(OUT,1):
    t=o['t']
    print('MD|%d|%+d|%s|%s|%s|%.3f|%.3f|%.3f|%s|%s|%.3f|%.3f|%.3f|%+.3f|%.1f|%.1f'%(
        i,t['dr'],U(t['ob']),U(t['eb']),t['why'],t['move'],t['mae'],t['mfe'],
        U(o['eb2']),o['why2'],o['move2'],o['mae2'],o['mfe2'],o['move2']-t['move'],
        (ts[t['eb']]-ts[t['ob']])/60000.0,(ts[o['eb2']]-ts[t['ob']])/60000.0))
b=np.array([o['t']['move'] for o in OUT]); r=np.array([o['move2'] for o in OUT])
hb=np.array([(ts[o['t']['eb']]-ts[o['t']['ob']])/60000.0 for o in OUT])
hr=np.array([(ts[o['eb2']]-ts[o['t']['ob']])/60000.0 for o in OUT])
print()
print('SUM|rule|trades|sum move%%|mean%%|moves>0|net of drag|mean MAE%%|mean MFE%%|mean hold min')
for lab,mv,mae,mfe,h in (('baseline',b,[o['t']['mae'] for o in OUT],[o['t']['mfe'] for o in OUT],hb),
                         ('ws1mage-rev',r,[o['mae2'] for o in OUT],[o['mfe2'] for o in OUT],hr)):
    print('SUM|%s|%d|%+.3f|%+.3f|%d|%+.3f|%.3f|%.3f|%.1f'%(lab,len(mv),mv.sum(),mv.mean(),(mv>0).sum(),
          mv.sum()-DRAG*len(mv),float(np.mean(mae)),float(np.mean(mfe)),float(h.mean())))
print('SUM|trades with NO ws1mage-rev after the open - STILL OPEN at the tape end: %d' % len(NOEX))
ov=0
sq=sorted(OUT,key=lambda o:o['t']['ob'])
for i,o in enumerate(sq):
    if i+1<len(sq) and o['eb2']>sq[i+1]['t']['ob']: ov+=1
print('SUM|trades still open when the NEXT trade opens (overlap): %d of %d' % (ov,len(OUT)))
hh=np.array([(ts[o['eb2']]-ts[o['t']['ob']])/60000.0 for o in OUT])
print('SUM|hold min on the rev route: min %.1f  p25 %.1f  med %.1f  p75 %.1f  max %.1f' %
      (hh.min(),np.percentile(hh,25),np.median(hh),np.percentile(hh,75),hh.max()))
print('SUM|baseline routes: ws1Mage %d, dr flip %d' % (sum(1 for o in OUT if o['t']['why']=='ws1Mage'),
                                                       sum(1 for o in OUT if o['t']['why']=='dr flip')))

print()
print('STOP|stop%|trades|stopped|sum move%|mean%|moves>0|net of drag|worst move%|sum coins USDT|end bal|return%')
base=[(o['move2'],o['mae2'],o['t']['P0']) for o in OUT]
def sweep(S):
    mv=[]; nst=0
    for m,mae,P0 in base:
        if S is not None and mae>=S: mv.append((-S,P0)); nst+=1
        else: mv.append((m,P0))
    a=np.array([x[0] for x in mv]); bal=START
    for m,P0 in mv: bal+=COINS*P0*(m-DRAG)/100.0
    return a,nst,bal
GRID=[None]+[round(x*0.25,2) for x in range(1,21)]
for S in GRID:
    a,nst,bal=sweep(S)
    pnl=sum(COINS*P0*(m-DRAG)/100.0 for m,P0 in [(x,y) for x,(_,_,y) in zip(a,base)])
    print('STOP|%s|%d|%d|%+.3f|%+.3f|%d|%+.3f|%+.3f|%+.2f|%.2f|%+.1f' %
          ('none' if S is None else ('%.2f'%S),len(a),nst,a.sum(),a.mean(),(a>0).sum(),
           a.sum()-DRAG*len(a),a.min(),pnl,bal,100*(bal/START-1)))
print()
print('MAE|rev MAE%% distribution over the %d trades' % len(base))
mae=np.array([x[1] for x in base])
for q in (50,60,70,75,80,85,90,95,99):
    print('MAE|p%d|%.3f' % (q,np.percentile(mae,q)))
print('MAE|max|%.3f' % mae.max())
for thr in (0.5,1.0,1.5,2.0,3.0,5.0,10.0):
    print('MAE|over %.1f%%|%d of %d = %.1f%%' % (thr,(mae>=thr).sum(),len(mae),100*(mae>=thr).mean()))
