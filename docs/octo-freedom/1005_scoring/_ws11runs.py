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
D='2026-09-25'; DR=+1
db=DatabaseManager(**get_db_config()); db.connect()
BK={t:momo_bank(db,t) for t in (11,12)}; db.disconnect()
PAR={}
for t in (11,12):
    with momo_config(BK[t]):
        with momo_window(int(BK[t]['k_window'])*t):
            PAR[t]=(int(MC.MOMO_STEP_BARS),int(MC.MOMO_SAMPLES))
ST={t:stall_mask(SC.Rl[t],DR,int(SC.LG['stall_n']),*PAR[t]) for t in (11,12)}
print('\n# THE STALL LATTICE PER TF')
print('| TF | k_window | step bars | step s | samples | lattice span bars | lattice span min | STALL_N | min flat to fire (STALL_N * step) |')
print('|---|---|---|---|---|---|---|---|---|')
for t in (11,12):
    st,sm=PAR[t]; n=int(SC.LG['stall_n'])
    print('| ws%d | %s | %d | %d | %d | %d | %.1f | %d | %d bars = %.1f min |'%(
        t,BK[t]['k_window'],st,st*5,sm,st*sm,st*sm*5/60.0,n,n*st,n*st*5/60.0))
a,b=SC.K('%s 20:30:00'%D),SC.K('%s 21:05:00'%D)
for t in (11,):
    print('\n# ws%d r FLAT RUNS >= 3 bars, %s 20:30 .. 21:05'%(t,D))
    print('| from | to | bars | seconds | value | stalled anywhere in the run? |')
    print('|---|---|---|---|---|---|')
    s=None
    for k in range(a+1,b+2):
        same = k<=b and abs(float(SC.Rl[t][k])-float(SC.Rl[t][k-1]))<1e-9
        if same and s is None: s=k-1
        elif not same and s is not None:
            n=k-s
            if n>=3:
                print('| %s | %s | %d | %d | %.2f | %s |'%(SC.U(s),SC.U(k-1),n,n*5,
                      float(SC.Rl[t][s]),'Y' if ST[t][s:k].any() else '**no**'))
            s=None
    print('\n# ws%d STALL ONSETS in the same window'%t)
    print('| ts | ws%d r |'%t); print('|---|---|')
    for k in range(a,b+1):
        if ST[t][k] and not ST[t][k-1]: print('| %s | %.2f |'%(SC.U(k),float(SC.Rl[t][k])))
