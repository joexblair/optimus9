"""started - what the r lines' SOURCE oob is, against what my arrival test actually measured."""
exec(open('arrive.py').read().split('fin=np.isfinite(Mst)')[0])
import numpy as np
RSRC={t:ffill_side(R[t]) for t in range(1,13)}     # each r line's own source oob, last touch, no cap
EX=[('A','2026-09-01 17:26:20',+1,'IS '),('B','2026-09-03 13:59:35',-1,'IS '),
    ('C','2026-08-27 07:41:30',+1,'OOS'),('D','2026-08-26 13:09:00',-1,'OOS')]
Q=[]
for tag,tstr,dd,win in EX:
    b=int(np.searchsorted(ts,ms(tstr)))
    Q.append(dict(tag=tag,win=win,dr=dd,b=b,
        v=[float(R[t][b]) for t in range(3,13)],
        s=[int(RSRC[t][b]) for t in range(3,13)],
        at=[bool((R[t][b]>=HI) if dd>0 else (R[t][b]<=LO)) for t in range(3,13)]))
print('S|r line|A value|A AT|A STARTED|B value|B AT|B STARTED|C value|C AT|C STARTED|D value|D AT|D STARTED')
for i,tf in enumerate(range(3,13)):
    c=[]
    for q in Q:
        s=q['s'][i]; c += ['%.2f'%q['v'][i], 'AT' if q['at'][i] else '-', 'hi' if s>0 else ('lo' if s<0 else '-')]
    print('S|ws%-2dr|%s'%(tf,'|'.join(c)))
print('S|')
def row(lab,f): print('S|%s|%s'%(lab,'|'.join(f(q) for q in Q)))
row('dr',lambda q:'%+d'%q['dr'])
row('ws1Mage source oob',lambda q:'hi' if q['dr']>0 else 'lo')
row('ARRIVED  count AT source oob /10',lambda q:'%d'%sum(q['at']))
row('STARTED  count whose SOURCE = ws1Mage source /10',
    lambda q:'%d'%sum(1 for s in q['s'] if s==q['dr']))
row('STARTED  count from the OPPOSITE oob /10',
    lambda q:'%d'%sum(1 for s in q['s'] if s==-q['dr']))
row('no source yet /10',lambda q:'%d'%sum(1 for s in q['s'] if s==0))
