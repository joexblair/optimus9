import os, sys, collections
import numpy as np
sys.path.insert(0,'/home/joe/thecodes'); sys.path.insert(0,'/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END','2026-10-05')
import ln, v4_knobs as K, v4_core_arm as CA, v4_reentry as RE, v4_signal as SG, v4_sweep_pivots as SP
from v4_backstop_trades import prices
HI=int(K.L2_MOM_MAXTF); A,B=ln.K(sys.argv[1]), ln.K(sys.argv[2])
MG={t: CA.mage_ladder(HI)[t] for t in range(5,HI+1)}
close,hi,lo=prices()
tr=[]; sigs=RE.produce(MG,A,B,trace=tr)
print('# v4_reentry on the CLOSED cws ladder, %s .. %s.'%(ln.U(A),ln.U(B)))
print('# the test: how many of cws6..cws%d stayed IB for the WHOLE cws5Mage oob run,'%HI)
print('#   against L2_RE_IB_MIN %d. His 1026 correction.'%K.L2_RE_IB_MIN)
print('# RULED_OK %s. sweep-pivots: '%K.RULED_OK + ', '.join('%s %s'%(n,v) for n,v,_ in SP.knobs()))
print('')
c=collections.Counter(len(r['stayed']) for r in tr)
print('| rungs that stayed IB | oob runs | would fire at L2_RE_IB_MIN %d? |'%K.L2_RE_IB_MIN)
print('|---|---|---|')
for n in sorted(c):
    print('| %d of 7 | %d | %s |'%(n,c[n],'yes' if n>=int(K.L2_RE_IB_MIN) else 'no'))
print('| TOTAL | %d | %d fire |'%(len(tr),sum(v for n,v in c.items() if n>=int(K.L2_RE_IB_MIN))))
print('')
print('# EACH SIGNAL, SCORED. entry = the signal bar + 1. exit = the sweep-pivot leg\'s own end.')
print('#   MAE/MFE from the entry, signed by the trade direction. given % = the favourable move')
print('#   already behind at the signal. share = given / leg MFE.')
print('')
print('| the signal | side | dir | the entry | rungs IB | which | TF | the pivot | the exit | MAE % | MFE % | given % | leg MFE % | share |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
byk={(r['bar'],r['side']):r for r in tr}
rows=[]
for s in sigs:
    sb,sd=int(s['bar']),int(s['side']); en=SG.fire_bar(s); dirn=SG.direction(sd); d=1 if dirn=='LONG' else -1
    r=byk[(sb,sd)]
    sw=SP.swing(sb,sd,close)
    if sw is None or sw.get('close') is None:
        print('| %s | %s | %s | %s | %d | ws%s | - | - | no sweep-pivot scale | - | - | - | - | - |'%(
          ln.U(sb),'HIGH' if sd>0 else 'LOW',dirn,ln.U(en),len(r['stayed']),
          ','.join(str(t) for t in r['stayed']))); continue
    ex=int(sw['close']); p0=float(close[en])
    h=float(np.nanmax(hi[en:ex+1])); l=float(np.nanmin(lo[en:ex+1]))
    mfe=((h-p0) if d>0 else (p0-l))/p0*100.0; mae=((l-p0) if d>0 else (p0-h))/p0*100.0
    rows.append((mae,mfe,sw.get('share')))
    print('| %s | %s | %s | %s | %d | ws%s | %s | %s | %s | %+.3f | %+.3f | %+.3f | %.3f | %s |'%(
      ln.U(sb),'HIGH' if sd>0 else 'LOW',dirn,ln.U(en),len(r['stayed']),
      ','.join(str(t) for t in r['stayed']),sw['tf'],ln.U(int(sw['pivot'])),ln.U(ex),
      mae,mfe,sw['given_pct'],sw['mfe_pct'],
      ('%.3f'%sw['share']) if sw.get('share') is not None else '-'))
print('')
if rows:
    M=[x[0] for x in rows]; F=[x[1] for x in rows]
    print('| the read | value |'); print('|---|---|')
    print('| signals | %d |'%len(rows))
    print('| sum MAE %% | %+.3f |'%sum(M)); print('| sum MFE %% | %+.3f |'%sum(F))
    print('| median MAE %% | %+.3f |'%sorted(M)[len(M)//2]); print('| median MFE %% | %+.3f |'%sorted(F)[len(F)//2])
    print('| worst MAE %% | %+.3f |'%min(M)); print('| best MFE %% | %+.3f |'%max(F))
    print('| MFE > abs(MAE) | %d of %d |'%(sum(1 for a,b,_ in rows if b>abs(a)),len(rows)))
