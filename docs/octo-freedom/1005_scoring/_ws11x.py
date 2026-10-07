import io, contextlib, sys
import numpy as np
sys.path.insert(0,'/home/joe/thecodes')
import time as _t; _T0=_t.time()
_P=lambda m: print('# [%5.1fs] %s'%(_t.time()-_T0,m), flush=True)
_P('importing score39 ...')
_b=io.StringIO()
with contextlib.redirect_stdout(_b):
    import score39 as SC
_P('score39 ready   roles available: %s'%sorted(SC.spec.keys()))
D='2026-09-25'; T=11; DR=+1
R=SC.Rl[T]
X=SC.LD(T*60,'x')
_P('ws%dx loaded, %d bars'%(T,len(X)))
a=SC.K('%s 20:25:00'%D); b=SC.K('%s 21:10:00'%D)
# 1. the ws11r oob crossing
print('\n# 1. ws%dr CROSSES TO oob (>= %.0f, dr %+d)'%(T,SC.HI,DR))
print('| ts | ws11r prev | ws11r | ws11x |'); print('|---|---|---|---|')
oob_k=None
for k in range(a,b+1):
    if float(R[k])>=SC.HI and float(R[k-1])<SC.HI:
        print('| %s | %.2f | %.2f | %.2f |'%(SC.U(k),float(R[k-1]),float(R[k]),float(X[k])))
        if oob_k is None: oob_k=k
print('\n- first oob crossing: **%s**'%(SC.U(oob_k) if oob_k else 'none in window'))
# 2. ws11x crosses UNDER ws11r, confirmed at wob 3 and wob 2
print('\n# 2. ws%dx CROSSES UNDER ws%dr after %s'%(T,T,SC.U(oob_k)))
print('| wob | cross bar | confirmed bar | +min from oob | ws11r | ws11x | gap |')
print('|---|---|---|---|---|---|---|')
for wob in (3,2):
    run=0; cross=None; done=None
    for k in range(oob_k,SC.TAPE_LAST+1):
        under = float(X[k])<float(R[k])
        if under:
            if run==0: cross=k
            run+=1
            if run>=wob: done=k; break
        else: run=0
    if done is None: print('| %d | — | — | — | | | |'%wob); continue
    print('| %d | %s | **%s** | %+.1f | %.2f | %.2f | %+.2f |'%(wob,SC.U(cross),SC.U(done),
          (int(SC.ts[done])-int(SC.ts[oob_k]))/60000.0,float(R[done]),float(X[done]),
          float(X[done])-float(R[done])))
# 3. the bars either side
print('\n# 3. ws%dr vs ws%dx PER BAR, %s .. +12 min'%(T,T,SC.U(oob_k)))
print('| ts | +min | ws11r | ws11x | x - r | x under r? |'); print('|---|---|---|---|---|---|')
for k in range(oob_k,oob_k+145):
    r_,x_=float(R[k]),float(X[k])
    print('| %s | %+.1f | %.2f | %.2f | %+.2f | %s |'%(SC.U(k),(int(SC.ts[k])-int(SC.ts[oob_k]))/60000.0,
          r_,x_,x_-r_,'**Y**' if x_<r_ else '-'))
print('\n# REFERENCE BARS for the 19:49:55 trade')
for lbl,ts in (('baton -> ws11 oob','20:32:35'),('price MFE +3.8615','20:34:30'),
               ('baton -> ws12 oob','20:36:10'),('EXIT final stalled','20:57:40')):
    k=SC.K('%s %s'%(D,ts))
    print('| %s | %s | ws11r %.2f | ws11x %.2f | x-r %+.2f |'%(ts,lbl,float(R[k]),float(X[k]),float(X[k])-float(R[k])))
