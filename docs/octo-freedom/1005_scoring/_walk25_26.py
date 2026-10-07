"""09-25 and 09-26: every trade as a chronological event list, with the MFE bar."""
import os, io, contextlib, re, sys
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.compute import momo_core as MC
from optimus9.compute.momo_config import momo_bank, momo_config
from optimus9.compute.momo_gated import momo_window, momo_g_why
from optimus9.analysis.jig import stall_mask
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
import time as _t; _T0=_t.time()
_P=lambda m: print('# [%6.1fs] %s'%(_t.time()-_T0,m), flush=True)
_P('importing score39 ...')
_b=io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC
import lineage_walk as LW
_P('ready')

OPEN_GRADES=('with-trend','no r block'); TRADE='no r block'
DAYS=('2026-09-14,2026-09-17,2026-09-25,2026-09-26,2026-09-27,2026-09-28,2026-09-29,'
      '2026-09-30,2026-10-01,2026-10-02,2026-10-03,2026-10-04').split(',')
SHOW=('2026-09-25','2026-09-26')
LIN_TF,LIN_HOP=SC.TF,int(SC.LG['lin_hop']); STALL_N=int(SC.LG['stall_n'])
H,L=SC.pivots(float(SC.LG['swing'])); PX=SC.PX
db=DatabaseManager(**get_db_config()); db.connect()
BANK={t:momo_bank(db,t) for t in LIN_TF}; db.disconnect()
ST={}
for t in LIN_TF:
    with momo_config(BANK[t]):
        with momo_window(int(BANK[t]['k_window'])*t):
            step,samples=int(MC.MOMO_STEP_BARS),int(MC.MOMO_SAMPLES)
    for dd in (-1,+1): ST[(t,dd)]=stall_mask(SC.Rl[t],dd,STALL_N,step,samples)
_mtc={}
def mt(t,k,d):
    key=(t,k,d)
    if key in _mtc: return _mtc[key]
    with momo_config(BANK[t]):
        with momo_window(int(BANK[t]['k_window'])*t):
            v=momo_g_why(SC.Rl[t],int(d),int(k))[0] in ('momo','curl')
    _mtc[key]=v; return v
_P('producers ready')
sigs=[]
for day in DAYS:
    p=os.path.join('octosig','%s.out'%day)
    if not os.path.exists(p): continue
    for ln in open(p):
        if not ln.startswith('R|'): continue
        f=ln.rstrip('\n').split('|')
        if len(f)<7 or not re.match(r'^\d\d:\d\d:\d\d$',f[2]): continue
        k=SC.K('%s %s'%(day,f[2])); d=int(SC.DRv[k])
        if d==0: continue
        r=SC.classify(k,f[2]); D=r.get('D') or {}
        ex=int(r['m']['ex']) if r['m'].get('ex') is not None else k
        g=D.get('why') if D.get('why')=='no r block' else r['grade']
        sigs.append(dict(day=day,sig=f[2],k=k,open_k=max(k,int(r['kw']),ex),dr=d,grade=g,
                         openable=(g in OPEN_GRADES)))
sigs.sort(key=lambda x:x['k'])
arms=[s for s in sigs if not s['openable']]
_P('%d octo-sigs'%len(sigs))
U=SC.U
for day in SHOW:
    for t in [s for s in sigs if s['grade']==TRADE and s['day']==day]:
        side='LONG' if t['dr']>0 else 'SHORT'
        arm=next((s for s in arms if s['k']>t['open_k']),None)
        w=LW.walk(SC.Rl,SC.DRv,lambda tt,kk,d=t['dr']: mt(tt,kk,d),
                  lambda tt,kk,d=t['dr']: bool(ST[(tt,d)][kk]),
                  arm['k'],t['dr'],SC.HI,SC.LO,SC.TAPE_LAST,LIN_TF,LIN_HOP,side) if arm else None
        xk=w['exit_k'] if w else None
        p0=float(PX[t['open_k']])
        # the MFE bar over the ACTUAL holding window
        mfe_k=mfe_v=None
        if xk is not None:
            seg=PX[t['open_k']:xk+1]; idx=np.arange(t['open_k'],xk+1)
            ok=np.isfinite(seg)&(seg>0); seg,idx=seg[ok],idx[ok]
            j=int(seg.argmax()) if side=='LONG' else int(seg.argmin())
            mfe_k=int(idx[j]); mfe_v=(float(seg[j])-p0)/p0*100.0*(1 if side=='LONG' else -1)
        ev=[(t['open_k'],'OPEN  %s'%side,'%.6f'%p0)]
        if arm: ev.append((arm['k'],'exit-armed  (octo-sig %s, %s)'%(arm['sig'],arm['grade']),'%.6f'%float(PX[arm['k']])))
        if w and w['start_k'] is not None: ev.append((w['start_k'],'ws1 momentum - lineage starts','%.6f'%float(PX[w['start_k']])))
        for kk,rd in (w['chain'][1:] if w else []): ev.append((kk,'baton -> ws%d oob'%rd,'%.6f'%float(PX[kk])))
        if mfe_k is not None: ev.append((mfe_k,'MFE  %+.4f'%mfe_v,'%.6f'%float(PX[mfe_k])))
        if xk is not None: ev.append((xk,'EXIT  %s  (rider ws%s)'%(w['why'],w['rider']),'%.6f'%float(PX[xk])))
        ev.sort(key=lambda x:x[0])
        real=((float(PX[xk])-p0)/p0*100.0*(1 if side=='LONG' else -1)) if xk is not None else None
        print('\n## %s  trade %s  %s   realised %s'%(day,t['sig'],side,
              ('%+.4f'%real) if real is not None else '—'))
        print('| ts | +min | event | pxs |'); print('|---|---|---|---|')
        for kk,lbl,px in ev:
            print('| %s | %+.1f | %s | %s |'%(U(kk),(int(SC.ts[kk])-int(SC.ts[t['open_k']]))/60000.0,lbl,px))
