import io, contextlib, sys
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
D='2026-09-25'; DR=+1; T=11
STALL_N=int(SC.LG['stall_n'])
db=DatabaseManager(**get_db_config()); db.connect()
BK=momo_bank(db,T); db.disconnect()
with momo_config(BK):
    with momo_window(int(BK['k_window'])*T):
        step,samples=int(MC.MOMO_STEP_BARS),int(MC.MOMO_SAMPLES)
ST=stall_mask(SC.Rl[T],DR,STALL_N,step,samples)
print('\n# ws%d STALL LATTICE'%T)
print('| knob | value | in bars | in seconds |'); print('|---|---|---|---|')
print('| k_window (bank) | %s | | |'%BK['k_window'])
print('| momo_window = k_window * tf | %d | | |'%(int(BK['k_window'])*T))
print('| MOMO_STEP_BARS | %d | %d | %d |'%(step,step,step*5))
print('| MOMO_SAMPLES | %d | | |'%samples)
print('| STALL_N (lazy_g_config) | %d | | |'%STALL_N)
print('| lattice span = step * samples | | %d | %d  (%.1f min) |'%(step*samples,step*samples*5,step*samples*5/60.0))
a,b=SC.K('%s 20:32:00'%D),SC.K('%s 21:00:00'%D)
print('\n# ws%d r BAR BY BAR, %s 20:32:00 .. 21:00:00   dr %+d'%(T,D,DR))
print('| ts | ws11 r | change | flat run (bars) | stalled |')
print('|---|---|---|---|---|')
run=0; prev=None
for k in range(a,b+1):
    v=float(SC.Rl[T][k])
    ch = '' if prev is None else ('%+.2f'%(v-prev))
    run = run+1 if (prev is not None and abs(v-prev)<1e-9) else 0
    print('| %s | %.2f | %s | %d | %s |'%(SC.U(k),v,ch,run,'**Y**' if ST[k] else '-'))
    prev=v
