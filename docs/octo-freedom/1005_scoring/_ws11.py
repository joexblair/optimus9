import os, io, contextlib, sys
import numpy as np
sys.path.insert(0,'/home/joe/thecodes')
from optimus9.compute import momo_core as MC
from optimus9.compute.momo_config import momo_bank, momo_config
from optimus9.compute.momo_gated import momo_window
from optimus9.analysis.jig import stall_mask
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
import time as _t; _T0=_t.time()
_P=lambda m: print('# [%5.1fs] %s'%(_t.time()-_T0,m), flush=True)
_P('importing score39 ...')
_b=io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC
_P('ready')
D='2026-09-25'; DR=+1                      # the 19:49:55 trade is LONG, dr +1
STALL_N=int(SC.LG['stall_n'])
db=DatabaseManager(**get_db_config()); db.connect()
ST={}
for t in (11,12):
    BK=momo_bank(db,t)
    with momo_config(BK):
        with momo_window(int(BK['k_window'])*t):
            step,samples=int(MC.MOMO_STEP_BARS),int(MC.MOMO_SAMPLES)
    ST[t]=stall_mask(SC.Rl[t],DR,STALL_N,step,samples)
db.disconnect()
a,b=SC.K('%s 20:30:00'%D), SC.K('%s 21:05:00'%D)
print('\n# ws11 STALL ONSETS, %s 20:30:00 .. 21:05:00, dr %+d'%(D,DR))
print('| ts | ws11 r | ws11 stalled | ws12 r | ws12 oob? | ws12 stalled |')
print('|---|---|---|---|---|---|')
prev=bool(ST[11][a-1])
for k in range(a,b+1):
    s11=bool(ST[11][k])
    if s11 and not prev:
        v12=float(SC.Rl[12][k])
        print('| **%s** | %.2f | **ONSET** | %.2f | %s | %s |'%(SC.U(k),float(SC.Rl[11][k]),v12,
              'YES' if v12>=SC.HI else 'no','Y' if ST[12][k] else '-'))
    prev=s11
print('\n# THE BATON BARS AND THE EXIT, with both lines')
for lbl,ts in (('baton -> ws11 oob','20:32:35'),('MFE','20:34:30'),
               ('baton -> ws12 oob','20:36:10'),('EXIT final stalled','20:57:40')):
    k=SC.K('%s %s'%(D,ts))
    print('| %s | %s | ws11 r %.2f  stalled %s | ws12 r %.2f  oob %s  stalled %s |'%(
        ts,lbl,float(SC.Rl[11][k]),'Y' if ST[11][k] else '-',
        float(SC.Rl[12][k]),'Y' if float(SC.Rl[12][k])>=SC.HI else 'n','Y' if ST[12][k] else '-'))
