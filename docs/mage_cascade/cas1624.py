"""cas1726 - the Mage cascade at 2026-09-01 17:26:20, trade #14 of the 122 report, dr +1."""
import os, sys, numpy as np, datetime as dt
sys.path.insert(0,'/home/joe/thecodes')
from optimus9.compute.ride_to_max import cascade
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
T=lambda i: dt.datetime.fromtimestamp(int(ts[i])/1000,dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
b=int(np.searchsorted(ts,int(dt.datetime(2026,9,2,16,24,30,tzinfo=dt.timezone.utc).timestamp()*1000)))
DR=1
print('BAR|%s   bar index %d   dr %+d   sneaky-1 at dr +1 = LONG' % (T(b),b,DR))
c=cascade(M,b,DR)
print('CAS|drop %.1f   wrong %d of 11 steps   spread %.1f' % (c['drop'],c['wrong'],c['spread']))
print('CAS|gate in the banked sneaky-1 verdict was drop >= 50')
print()
print('LAD|tf|ws{tf}Mage|ws{tf}r|step to next (dr-signed, +ve = falls away from dr)')
v=c['v']; st=DR*-np.diff(v)
for i,tf in enumerate(range(1,13)):
    s=('%+7.2f' % st[i]) if i<len(st) else '      -'
    print('LAD|ws%-2d|%8.2f|%8.2f|%s%s' % (tf,M[tf][b],R[tf][b],s,'   <- against' if i<len(st) and st[i]<0 else ''))
print()
print('WIN|the cascade drop over the surrounding 30 min, every minute')
for k in range(-15,16):
    j=b+k*12
    if j<0 or j>=len(ts): continue
    cc=cascade(M,j,DR)
    if cc is None: continue
    mark=''
    if k==0: mark='   <- OPEN 17:26:20'
    print('WIN|%s|%+6.1f|%d|%.1f%s' % (T(j)[11:],cc['drop'],cc['wrong'],cc['spread'],mark))
