"""CORRECTED READING. "1 min tolerance instead of a dwell" = each of the three lines is oob on the
dr side at SOME bar inside a rolling 60 s window - a line already oob still counts.
My first pass read it as the three CROSSINGS falling within 60 s; that drops #6 itself, whose
ws2r crossed at 09-02 18:08:00, 7 min before ws3r at 18:15:00. So that reading is wrong.
The event bar is the LAST bar of the earliest qualifying window. MINE, stated."""
import sys,io,os,numpy as np
_HERE=os.path.dirname(os.path.abspath(__file__))
_PRELUDE=os.path.join(_HERE,'..','22_go_20260921','_prelude.py')
_o=sys.stdout; sys.stdout=io.StringIO()
exec(open(_PRELUDE).read().split("k=int(np.searchsorted")[0])
from optimus9.analysis.jig import ws1mage_rev
sys.stdout=_o
from optimus9.compute.swing_detect import find_pivots
M13=Ln(13,'m'); DRs=dr_latch_wob(M[1],M13,iw,n-1,LATCH_W)
CY=[s for s in stretches(DRs,iw,n)]
LO,HI=15.0,85.0; W=12; H33=33*12
R={t:np.asarray(RA[t],float) for t in (1,2,3)}
MRV={t:ws1mage_rev(MA[t],G,HI,LO,dwell=int(_C['dwell']),rev_wob=int(_C['rev_wob']),
                   hold=int(_C['boundary_xwob'])) for t in (1,2,3)}
PIV=find_pivots(PXT,2.0)
def mrev(t,dr,frm):
    L=MRV[t]; d=L[dr]['dwell_ok']; r=L[dr]['rev']; s=L[dr]['sig']; sc=L[dr]['sig_conf']
    a=d[d>=frm]
    if not len(a): return None
    a=int(a[0]); b=r[r>=a]
    if not len(b): return None
    b=int(b[0]); m=np.flatnonzero(s>b)
    return int(sc[m[0]]) if len(m) else None
a0=int(np.searchsorted(ts,ms('2026-09-01 00:00:00'))); b0=int(np.searchsorted(ts,ms('2026-09-06 00:00:00')))
print('H|all-three-oob, 1 min tolerance = a rolling %d bar = %d s window|oob %g/%g on the stretch dr side'%(W,W*5,LO,HI))
print('H|event bar = the LAST bar of the earliest qualifying window (MINE)|swing_detect find_pivots(px, 2.0)|px check +%d bars = 33 min'%H33)
print('E|#|event bar|dr|last oob bar per line (order)|span s|ws1mage-rev|ws2mage-rev|ws3mage-rev|earliest mage-rev|next swing pivot|kind|min after|px at mage-rev|px +33min|px move %|dr flip')
ev=0
for s0,e0,dr in CY:
    if e0<a0 or s0>b0: continue
    s0=max(s0,a0); e0=min(e0,b0)
    O={t:(((R[t][s0:e0+1]<=LO) if dr<0 else (R[t][s0:e0+1]>=HI))) for t in (1,2,3)}
    L=e0-s0+1
    last={t:np.full(L,-1,int) for t in (1,2,3)}
    for t in (1,2,3):
        c=-1
        for i in range(L):
            if O[t][i]: c=i
            last[t][i]=c
    ok=np.array([all(last[t][i]>=0 and (i-last[t][i])<=W for t in (1,2,3)) for i in range(L)])
    starts=np.flatnonzero(ok & ~np.concatenate(([False],ok[:-1])))
    for i in starts:
        i=int(i); ev+=1
        k=s0+i
        trio=sorted((s0+last[t][i],t) for t in (1,2,3))
        mv={t:mrev(t,dr,k) for t in (1,2,3)}
        good=[v for v in mv.values() if v is not None and v<=e0]
        em=min(good) if good else None
        nxt=next(((p,kd) for p,kd in PIV if em is not None and p>em),(None,None))
        j=min(em+H33,len(PXT)-1) if em is not None else None
        print('E|%d|%s|%+d|%s|%d|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s'
              %(ev,U(k),dr,' '.join('ws%d@%s'%(t,U(b)[11:]) for b,t in trio),
                (trio[-1][0]-trio[0][0])*5,
                U(mv[1])[5:] if mv[1] else 'none',U(mv[2])[5:] if mv[2] else 'none',
                U(mv[3])[5:] if mv[3] else 'none',U(em)[5:] if em else 'NONE',
                U(nxt[0])[5:] if nxt[0] else '-',nxt[1] or '-',
                '%.1f'%((nxt[0]-em)*5/60.0) if nxt[0] else '-',
                '%.8f'%PXT[em] if em else '-','%.8f'%PXT[j] if j else '-',
                '%+.3f'%(100.0*(PXT[j]-PXT[em])/PXT[em]) if em else '-',U(e0)[11:]))
print('C|events %d'%ev)
