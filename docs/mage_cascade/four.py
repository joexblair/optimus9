"""four - the 4 worked examples behind the bumps<=2 reversal, as one wide ladder table.

  A  IS   2026-09-01 17:26:20  dr +1  bumps 2  falls +61.3   <- the bar Joe read himself
  B  IS   2026-09-03 13:59:35  dr -1  bumps 1  falls +65.3
  C  OOS  2026-08-27 07:41:30  dr +1  bumps 0  falls +62.6
  D  OOS  2026-08-26 13:09:00  dr -1  bumps 0  falls +70.0

  all four sit inside the fitted gate: ws1Mage oob on the dr side, mage falls > 0, bumps <= 2.
  step = dr * -(next rung - this rung).  +ve = the ladder keeps falling away from the oob end.
"""
import os, sys, numpy as np, pandas as pd, datetime as dt
from datetime import timezone
sys.path.insert(0,'/home/joe/thecodes')
from optimus9.analysis.jig import Jig
from optimus9.compute.line_config import override, mech_lines
from optimus9.orchestration.rpl_cache import LINE_DIR, TAPE_DIR, _line_key, _tape_key
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
db=DatabaseManager(**get_db_config()); db.connect()
sy=db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l FROM optimus9_system WHERE sys_pk=1',fetch=True)[0]
SPEC={}
for g in mech_lines(db,'wsf'):
    if g['role'] not in SPEC:
        _t,s_,m_=g['override']; SPEC[g['role']]=(s_,m_)
db.disconnect()
ts=np.load(os.path.join(TAPE_DIR,_tape_key(END_MS,HOURS,WARMUP,{'src':sy['s'],'len':sy['l']})+'.npz'))['__ts__']
Ld=lambda tf,r_: np.load(os.path.join(LINE_DIR,_line_key(END_MS,HOURS,WARMUP,override(tf*60,*SPEC[r_]))+'.npy'))
M={t:Ld(t,'Mage') for t in range(1,13)}; R={t:Ld(t,'r') for t in range(1,13)}
with Jig(END_MS,hours=HOURS,warmup=WARMUP) as J:
    JT=np.asarray(J.ts,dtype=np.int64); PXS=pd.Series(np.asarray(J.px,float)).ffill().bfill().to_numpy()
PXT=PXS[np.clip(np.searchsorted(JT,ts),0,len(JT)-1)]
ms=lambda s:int(dt.datetime.strptime(s,'%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc).timestamp()*1000)
EX=[('A','IS ','2026-09-01 17:26:20',+1),
    ('B','IS ','2026-09-03 13:59:35',-1),
    ('C','OOS','2026-08-27 07:41:30',+1),
    ('D','OOS','2026-08-26 13:09:00',-1)]
HI,LO=85.0,15.0; MINS=(30,45,60,90,120); BPM=12
Q=[]
for tag,win,tstr,d in EX:
    b=int(np.searchsorted(ts,ms(tstr)))
    m=np.array([M[t][b] for t in range(1,13)],float)
    r=np.array([R[t][b] for t in range(1,13)],float)
    mst=d*-np.diff(m); rst=d*-np.diff(r[1:])
    P0=float(PXT[b])
    f={k:(PXT[b+k*BPM]-P0)/P0*100.0*d for k in MINS}
    Q.append(dict(tag=tag,win=win,t=tstr,dr=d,b=b,m=m,r=r,mst=mst,
        mfall=d*(m[0]-m[-1]), mbump=int((mst<0).sum()),
        rfall=d*(r[1]-r[-1]),  rbump=int((rst<0).sum()),
        noob=sum(1 for t in range(12) if (m[t]>=HI if d>0 else m[t]<=LO)),
        px=P0, f=f))
print('H|field|A  IS 09-01 17:26:20|B  IS 09-03 13:59:35|C  OOS 08-27 07:41:30|D  OOS 08-26 13:09:00')
def hrow(lab,fn): print('H|%s|%s'%(lab,'|'.join(fn(q) for q in Q)))
hrow('window',           lambda q:q['win'])
hrow('dr',               lambda q:'%+d'%q['dr'])
hrow('price at the bar', lambda q:'%.5f'%q['px'])
hrow('ws1Mage',          lambda q:'%.2f'%q['m'][0])
hrow('ws12Mage',         lambda q:'%.2f'%q['m'][-1])
hrow('MAGE FALLS',       lambda q:'%+.1f'%q['mfall'])
hrow('mage bumps /11',   lambda q:'%d'%q['mbump'])
hrow('ws1 oob',          lambda q:'yes')
hrow('lower TFs oob /12',lambda q:'%d'%q['noob'])
hrow('ws2r',             lambda q:'%.2f'%q['r'][1])
hrow('ws12r',            lambda q:'%.2f'%q['r'][-1])
hrow('r falls',          lambda q:'%+.1f'%q['rfall'])
hrow('r bumps /10',      lambda q:'%d'%q['rbump'])
for k in MINS: hrow('move%% %dm  (*dr)'%k, lambda q,k=k:'%+.3f'%q['f'][k])
hrow('raw price move %',  lambda q:'%+.3f'%(q['f'][60]*q['dr']))
print('H|')
print('W|tf|A Mage|A step|A r|B Mage|B step|B r|C Mage|C step|C r|D Mage|D step|D r')
for i,tf in enumerate(range(1,13)):
    cells=[]
    for q in Q:
        st = ('%+7.2f'%q['mst'][i]) if i<11 else '      -'
        if i<11 and q['mst'][i]<0: st=st+'*'
        cells += ['%.2f'%q['m'][i], st.strip(), '%.2f'%q['r'][i]]
    print('W|ws%-2d|%s'%(tf,'|'.join(cells)))
print('W|* = a step running against the fall (a bump)')
