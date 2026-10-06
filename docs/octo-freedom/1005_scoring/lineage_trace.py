"""Joe's 1006 lineage, as a TIME walk. Trace every state change on ws1..ws12 across his window."""
import os, sys, io, contextlib
os.environ.setdefault('LG_DAY','2026-09-25')
_b = io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC, baton as BT
import numpy as np

DAY='2026-09-25'; S='10:00:00'; E='11:30:00'
C = BT.compute(DAY+' 00:00:00', DAY+' 23:59:55', 'octosig/%s.out'%DAY, warn=False)
k0, k1 = SC.K('%s %s'%(DAY,S)), SC.K('%s %s'%(DAY,E))
TF = list(range(1,13))

def band(t,k,d):
    v=float(SC.Rl[t][k])
    if not np.isfinite(v): return '?'
    if d>0: return 'O' if v>=85.0 else ('x' if v>=83.0 else '.')
    return 'O' if v<=15.0 else ('x' if v<=17.0 else '.')

EV=[]
prev={}
for k in range(k0, k1+1):
    j=k-C.A; d=int(C.D[j])
    for t in TF:
        mt=bool(C.MT12[t][j]); bd=band(t,k,d)
        st=bool(C.ST[t][j]) if t in C.ST else None
        cur=(mt,bd,st)
        if t in prev and prev[t]!=cur:
            pm,pb,ps = prev[t]
            if pm!=mt: EV.append((k,t,'mom-true ON' if mt else 'mom-true OFF', float(SC.Rl[t][k]),d))
            if pb!=bd: EV.append((k,t,'band %s -> %s'%(pb,bd), float(SC.Rl[t][k]),d))
            if ps!=st and st is not None: EV.append((k,t,'STALLED' if st else 'unstalled', float(SC.Rl[t][k]),d))
        prev[t]=cur

print('# FULL EVENT TRACE  %s %s .. %s   ws1..ws12   %d events'%(DAY,S,E,len(EV)))
print('| ts | TF | event | r | dr |'); print('|---|---|---|---|---|')
for k,t,e,v,d in EV:
    print('| %s | ws%d | %s | %.2f | %+d |'%(SC.U(k),t,e,v,d))

print('\n# JOE\'S THREE STEPS, CHECKED')
for tss, claim in (('10:24:00','ws1 printing mom-true'),
                   ('10:32:00','ws2 is oob and ws4 is mom-true'),
                   ('10:44:00','ws4 is oob and ws6 is mom-true')):
    k=SC.K('%s %s'%(DAY,tss)); j=k-C.A; d=int(C.D[j])
    print('\n## %s  (dr %+d)   Joe: %s'%(tss,d,claim))
    print('| TF | r | band | mom-true | stalled |'); print('|---|---|---|---|---|')
    for t in TF:
        st = ('Y' if C.ST[t][j] else '-') if t in C.ST else 'n/a'
        print('| ws%d | %.2f | %s | %s | %s |'%(t,float(SC.Rl[t][k]),band(t,k,d),
                                                'Y' if C.MT12[t][j] else '-', st))
