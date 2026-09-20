"""_prelude - spec_label 22_go_20260921.  The shared load for both reports in this folder:
the tape, the ws1..ws23 role lines, the momo banks, the v3 config and the dr latch.  It is the
same prelude every producer in this chain has used - stopsweep.py, read up to its first report.

  sneaky-1 caps the chain at ws4 - build_sneaky_trade_1.py line 122: `for up in range(t+1, 5)`.
  Here the chain runs to ws23, the top of the built ladder.
"""
import sys, os, numpy as np, datetime as dt
from datetime import timezone
S='/home/joe/thecodes/docs/mage_cascade'
sys.path.insert(0,'/home/joe/thecodes'); sys.path.insert(0,S)
os.chdir(S)
exec(open('stopsweep.py').read().split("print()\nprint('STOP|stop%|")[0])
import numpy as np
import walk_mom_models as Wm
from optimus9.compute.test_points import test_point, anchor as tp_anchor
from optimus9.compute.momo_config import momo_bank
from optimus9.compute.v3_config import v3_config
TOP_TF=23
_db=DatabaseManager(**get_db_config()); _db.connect()
_C=v3_config(_db)
BKa={tf:momo_bank(_db,tf,version=1) for tf in range(1,TOP_TF+1)}
_db.disconnect()
MFR=float(_C['momo_fence_r']); FENCE=(MFR,100.0-MFR)
MAGE_FENCE=(W.MAGE_LO,W.MAGE_HI); MAGE_DWELL=W.MAGE_DWELL
LOOKBACK=int(_C['tp_lookback_min'])*12
RA={tf:Ln(tf,'r') for tf in range(1,TOP_TF+1)}
MA={tf:Ln(tf,'Mage') for tf in range(1,TOP_TF+1)}
SEA={tf:seam_mask(ts,tf) for tf in range(1,TOP_TF+1)}
M13=Ln(13,'m')
DRs=dr_latch_wob(M[1],M13,iw,n-1,LATCH_W)
U=lambda i: dt.datetime.fromtimestamp(int(ts[i])/1000,tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
k=int(np.searchsorted(ts,ms('2026-09-01 09:24:00')))
F,Fp,dr=next(s for s in stretches(DRs,iw,n) if s[0]>=k)
print('H|the dr stretch|%s -> %s|dr %+d|%d bars = %.1f min'%(U(F),U(Fp),dr,Fp-F,(Fp-F)*5/60.0))
print('H|knobs|momo_fence_r %g -> r fence %g/%g|Mage fence %g/%g|MAGE_DWELL %d bars = %d s|tp_lookback %d bars = %d min'
      %(MFR,FENCE[0],FENCE[1],MAGE_FENCE[0],MAGE_FENCE[1],MAGE_DWELL,MAGE_DWELL*5,LOOKBACK,LOOKBACK//12))
print('H|chain|ws1 .. ws%d, NO CAP. sneaky-1 stops at ws4'%TOP_TF)
print()
print('A|tf|Mage anchor|test-point|how|back bars|span|clipped|r at the tp')
pool={}
for t in range(1,TOP_TF+1):
    a=tp_anchor(MA[t],dr,F,Fp,MAGE_FENCE,MAGE_DWELL)
    rec=test_point(RA[t],MA[t],dr,F,Fp,FENCE,MAGE_FENCE,MAGE_DWELL,LOOKBACK)
    if rec is None:
        print('A|ws%d|%s|none|-|-|-|-|-'%(t,U(a) if a is not None else 'no Mage anchor'))
        continue
    pool[t]=rec
    print('A|ws%d|%s|%s|%s|%d|%s|%s|%.2f'%(t,U(rec['anchor']),U(rec['bar']),rec['how'],rec['back'],
          rec['span'],rec['clipped'],float(RA[t][rec['bar']])))
print()
print('B|THE CHAIN - at each test-point, which higher TFs are momentum-true at that bar')
print('B|src|test-point|carried to|chain of momentum-true TFs above src|first break')
for t in sorted(pool):
    b=pool[t]['bar']; claims=[]
    for up in range(t+1,TOP_TF+1):
        ok,_=Wm.momentum_true(RA[up],BKa[up],CFG,dr,b,SEA[up],up)
        claims.append((up,int(ok)))
    run=[]
    for up,ok in claims:
        if ok: run.append(up)
        else: break
    carry=[up for up,ok in claims if ok]
    hi=max(carry) if carry else t
    brk=next((up for up,ok in claims if not ok),None)
    print('B|ws%d|%s|ws%d|%s|%s'%(t,U(b),hi,
          (','.join('ws%d'%u for u in carry) if carry else 'none'),
          ('ws%d'%brk) if brk else 'none - carried to ws%d'%TOP_TF))
print()
print('C|SNEAKY-1 CAP vs NO CAP')
print('C|src|hi at the ws4 cap|hi with no cap|TFs gained')
for t in sorted(pool):
    b=pool[t]['bar']
    cap=[up for up in range(t+1,5) if Wm.momentum_true(RA[up],BKa[up],CFG,dr,b,SEA[up],up)[0]]
    nocap=[up for up in range(t+1,TOP_TF+1) if Wm.momentum_true(RA[up],BKa[up],CFG,dr,b,SEA[up],up)[0]]
    print('C|ws%d|ws%d|ws%d|%d'%(t,max(cap) if cap else t,max(nocap) if nocap else t,
          (max(nocap) if nocap else t)-(max(cap) if cap else t)))
print()
print('D|the walk ends on the dr flip|%s'%U(Fp))
print('D|next dr|%+d'%int(DRs[Fp]))
