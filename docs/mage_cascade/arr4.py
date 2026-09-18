exec(open('arrive.py').read().split('fin=np.isfinite(Mst)')[0])
import numpy as np
EX=[('A','2026-09-01 17:26:20',+1,'IS '),('B','2026-09-03 13:59:35',-1,'IS '),
    ('C','2026-08-27 07:41:30',+1,'OOS'),('D','2026-08-26 13:09:00',-1,'OOS')]
print('G|field|A 09-01 17:26:20|B 09-03 13:59:35|C 08-27 07:41:30|D 08-26 13:09:00')
Q=[]
for tag,tstr,dd,win in EX:
    b=int(np.searchsorted(ts,ms(tstr))); P0=float(PXT[b])
    q=dict(tag=tag,win=win,dr=dd,nr=int(nr[b]),reach=float(reach[b]),mvote=int(mvote[b]),mat=int(mat[b]),
           src=[int(SRC[t][b]) for t in range(5,13)],
           mv=[float(M[t][b]) for t in range(5,13)])
    for k in MINS: q['f%d'%k]=float((PXT[b+k*BPM]-P0)/P0*100.0*dd)
    Q.append(q)
def row(lab,f): print('G|%s|%s'%(lab,'|'.join(f(q) for q in Q)))
row('window',lambda q:q['win']); row('dr',lambda q:'%+d'%q['dr'])
row('source oob',lambda q:'hi 85' if q['dr']>0 else 'lo 15')
row('nr  (ws3r..ws12r at source oob /10)',lambda q:'%d'%q['nr'])
row('ARRIVED?',lambda q:'yes' if q['nr']>0 else 'NO - short')
row('reach (+ve = past the source oob)',lambda q:'%+.2f'%q['reach'])
row('mvote (ws5..ws12 Mage source oob /8)',lambda q:'%d'%q['mvote'])
row('mat   (ws5..ws12 Mage AT it now /8)',lambda q:'%d'%q['mat'])
for k in MINS: row('move%% %dm (x dr)'%k, lambda q,k=k:'%+.3f'%q['f%d'%k])
print('G|')
print('V|Mage line|A value|A source|B value|B source|C value|C source|D value|D source')
for i,tf in enumerate(range(5,13)):
    c=[]
    for q in Q:
        s=q['src'][i]; c += ['%.2f'%q['mv'][i], 'hi' if s>0 else ('lo' if s<0 else '-')]
    print('V|ws%-2dMage|%s'%(tf,'|'.join(c)))
