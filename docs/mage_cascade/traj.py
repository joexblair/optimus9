"""traj - Joe 0918: the SOURCE OOB of ws1Mage defines the heading. Check where each r rung sits
relative to that same source oob, for A B C D."""
import os, sys, numpy as np, datetime as dt
from datetime import timezone
sys.path.insert(0,'/home/joe/thecodes')
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
ms=lambda s:int(dt.datetime.strptime(s,'%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc).timestamp()*1000)
HI,LO=85.0,15.0
EX=[('A','2026-09-01 17:26:20',+1,'IS '),('B','2026-09-03 13:59:35',-1,'IS '),
    ('C','2026-08-27 07:41:30',+1,'OOS'),('D','2026-08-26 13:09:00',-1,'OOS')]
Q=[]
for tag,tstr,d,win in EX:
    b=int(np.searchsorted(ts,ms(tstr)))
    m=np.array([M[t][b] for t in range(1,13)],float); r=np.array([R[t][b] for t in range(1,13)],float)
    src = HI if d>0 else LO
    at = (r>=HI) if d>0 else (r<=LO)                       # r rung sitting at the SOURCE oob
    hi_tf = slice(2,12)                                     # ws3r .. ws12r, the overarching lines
    reach = (r[hi_tf].max()-src) if d>0 else (src-r[hi_tf].min())   # +ve = reached it, -ve = short of it
    Q.append(dict(tag=tag,win=win,t=tstr,dr=d,m=m,r=r,src=src,at=at,reach=reach,
        best=(r[hi_tf].max() if d>0 else r[hi_tf].min()),
        nat=int(at.sum()), nat_hi=int(at[hi_tf].sum()),
        mtraj='%.2f -> %.2f'%(m[0],m[-1]), rtraj='%.2f -> %.2f'%(r[1],r[-1])))
print('T|field|A  09-01 17:26:20|B  09-03 13:59:35|C  08-27 07:41:30|D  08-26 13:09:00')
def row(lab,f): print('T|%s|%s'%(lab,'|'.join(f(q) for q in Q)))
row('window',            lambda q:q['win'])
row('dr',                lambda q:'%+d'%q['dr'])
row('ws1Mage',           lambda q:'%.2f'%q['m'][0])
row('SOURCE OOB',        lambda q:'hi 85' if q['dr']>0 else 'lo 15')
row('Mage raw ws1->ws12',lambda q:q['mtraj'])
row('Mage heading',      lambda q:'away from hi' if q['dr']>0 else 'away from lo')
row('r raw ws2->ws12',   lambda q:q['rtraj'])
row('r heading vs SOURCE',lambda q:('AWAY from %s'%('hi' if q['dr']>0 else 'lo')) if ((q['r'][1]>q['r'][-1]) if q['dr']>0 else (q['r'][1]<q['r'][-1])) else ('TOWARD %s'%('hi' if q['dr']>0 else 'lo')))
row('r rungs AT source oob /12',   lambda q:'%d'%q['nat'])
row('  of those, ws3r..ws12r',     lambda q:'%d'%q['nat_hi'])
row('closest ws3r..ws12r gets',    lambda q:'%.2f'%q['best'])
row('distance to the source oob',  lambda q:('%+.2f reached' if q['reach']>=0 else '%+.2f SHORT')%q['reach'])
row('raw price at 60m',            lambda q:'')
print('T|')
print('U|tf|A r|A at hi85|B r|B at lo15|C r|C at hi85|D r|D at lo15')
for i,tf in enumerate(range(1,13)):
    c=[]
    for q in Q: c += ['%.2f'%q['r'][i], 'AT' if q['at'][i] else '-']
    print('U|ws%-2d|%s'%(tf,'|'.join(c)))
