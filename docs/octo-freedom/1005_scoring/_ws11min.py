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
db=DatabaseManager(**get_db_config()); db.connect()
BK=momo_bank(db,T); db.disconnect()
with momo_config(BK):
    with momo_window(int(BK['k_window'])*T):
        step,samples=int(MC.MOMO_STEP_BARS),int(MC.MOMO_SAMPLES)
n=int(SC.LG['stall_n'])
ST=stall_mask(SC.Rl[T],DR,n,step,samples)
print('\n# ws%d STALL LATTICE   step %d bars = %d s   samples %d   span %d bars = %.1f min   STALL_N %d'
      %(T,step,step*5,samples,step*samples,step*samples*5/60.0,n))
print('# minimum flat to fire = STALL_N * step = %d bars = %.1f min'%(n*step,n*step*5/60.0))
a,b=SC.K('%s 20:36:00'%D),SC.K('%s 21:05:00'%D)
print('\n# ws%d r PER MINUTE, %s 20:36:00 .. 21:05:00   dr %+d'%(T,D,DR))
print('| ts | ws11 r | change | stalled |'); print('|---|---|---|---|')
prev=None
for k in range(a,b+1,12):                       # 12 bars = 60 s at the 5 s grid
    v=float(SC.Rl[T][k])
    ch='' if prev is None else '%+.2f'%(v-prev)
    print('| %s | %.2f | %s | %s |'%(SC.U(k),v,ch,'**Y**' if ST[k] else '-'))
    prev=v
