import os, io, contextlib, re, sys
import numpy as np
_e=sys.stderr; sys.stderr=io.StringIO()
from optimus9.compute.momo_config import momo_bank, momo_config
from optimus9.compute.momo_gated import momo_window, momo_g_why
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
sys.stderr=_e
_b=io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC
import lineage_walk as LW
OPEN=('with-trend','no r block')
DAYS=('2026-09-14,2026-09-17,2026-09-25,2026-09-26,2026-09-27,2026-09-28,2026-09-29,'
      '2026-09-30,2026-10-01,2026-10-02,2026-10-03,2026-10-04').split(',')
LIN=SC.TF
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
        sigs.append(dict(day=day,sig=f[2],k=k,entry=max(k,int(r['kw']),ex),ex=ex,dr=d,grade=g,
                         openable=(g in OPEN)))
sigs.sort(key=lambda x:x['k'])
op=[s for s in sigs if s['openable']]; tr=[s for s in sigs if not s['openable']]
bad=[]
for t in op:
    n=next((s for s in tr if s['k']>t['entry']),None)
    if not n: continue
    if LW.rider_at(SC.Rl,n['ex'],n['dr'],SC.HI,SC.LO,LIN) is None:
        bad.append((t,n))
seen=set(); uniq=[]
for t,n in bad:
    if (n['day'],n['sig']) in seen: continue
    seen.add((n['day'],n['sig'])); uniq.append(n)
# ws1 mom-true, computed directly for the bars we need
db=DatabaseManager(**get_db_config()); db.connect()
BK=momo_bank(db,1); db.disconnect()
R1=SC.Rl[1]
def mt1(bar,d):
    with momo_config(BK):
        with momo_window(int(BK['k_window'])*1):
            return momo_g_why(R1,int(d),int(bar))[0] in ('momo','curl')
print('# THE %d DISTINCT OCTO-SIGS WHOSE LADDER IS EMPTY AT THEIR g5extrema'%len(uniq))
print('# ladder = r on the dr side: O >= oob, x between the fences, . in-fence')
print('\n| day | octo-sig | g5extrema | dr | grade | r ladder ws1..ws12 | ws1 r | ws1 mom-true? | bars fwd to ws1 mom-true |')
print('|---|---|---|---|---|---|---|---|---|')
for n in uniq:
    exb,d=n['ex'],n['dr']
    lad=''
    for t in LIN:
        v=float(SC.Rl[t][exb])
        lad += ('O' if v>=SC.HI else ('x' if v>=83.0 else '.')) if d>0 else \
               ('O' if v<=SC.LO else ('x' if v<=17.0 else '.'))
    now=mt1(exb,d)
    fwd='0' if now else '—'
    if not now:
        for j in range(exb+1,min(exb+2000,SC.TAPE_LAST)+1):
            if int(SC.DRv[j])!=d: fwd='dr flip @%d'%(j-exb); break
            if mt1(j,d): fwd=str(j-exb); break
    print('| %s | %s | %s | %+d | %s | `%s` | %.2f | %s | %s |'%(n['day'],n['sig'],SC.U(exb),d,
          n['grade'],lad,float(R1[exb]),'YES' if now else 'no',fwd))
