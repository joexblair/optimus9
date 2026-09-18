"""sane4 - the same tables, computed by the SAME code path, for A B C D only."""
exec(open('startpop.py').read().split('\nrows=[]')[0])
import numpy as np
EX=[('A','2026-09-01 17:26:20','IS '),('B','2026-09-03 13:59:35','IS '),
    ('C','2026-08-27 07:41:30','OOS'),('D','2026-08-26 13:09:00','OOS')]
Q=[]
for tag,tstr,win in EX:
    b=int(np.searchsorted(ts,ms(tstr))); dd=int(DR[b]); P0=float(PXT[b])
    Q.append(dict(tag=tag,win=win,b=b,t=tstr,dr=dd,
        nsame=int(nsame[b]),nopp=int(nopp[b]),nnone=int(nnone[b]),
        nr=int(nr[b]),reach=float(reach[b]),mvote=int(mvote[b]),mat=int(mat[b]),
        f30=float((PXT[b+30*BPM]-P0)/P0*100.0*dd),
        f45=float((PXT[b+45*BPM]-P0)/P0*100.0*dd)))
def row(lab,f): print('Q|%s|%s'%(lab,'|'.join(f(q) for q in Q)))
print('Q|field|A 09-01 17:26:20|B 09-03 13:59:35|C 08-27 07:41:30|D 08-26 13:09:00')
row('window',lambda q:q['win'])
row('dr',lambda q:'%+d'%q['dr'])
row('ws1Mage source oob',lambda q:'hi 85' if q['dr']>0 else 'lo 15')
row('nsame /10',lambda q:'%d'%q['nsame'])
row('nopp /10',lambda q:'%d'%q['nopp'])
row('no source yet /10',lambda q:'%d'%q['nnone'])
row('nr  ARRIVED /10',lambda q:'%d'%q['nr'])
row('reach',lambda q:'%+.2f'%q['reach'])
row('mvote /8',lambda q:'%d'%q['mvote'])
row('mat /8',lambda q:'%d'%q['mat'])
row('move% 30m (x dr)',lambda q:'%+.3f'%q['f30'])
row('move% 45m (x dr)',lambda q:'%+.3f'%q['f45'])
row('30m direction',lambda q:'continuation' if q['f30']>0 else 'reversal')
row('45m direction',lambda q:'continuation' if q['f45']>0 else 'reversal')
print('Q|')
# which population bucket each one lands in
import pickle
rows=pickle.load(open('startpop.pkl','rb'))
F30=np.array([r['f30'] for r in rows]); F45=np.array([r['f45'] for r in rows])
NS=np.array([r['nsame'] for r in rows]); NO=np.array([r['nopp'] for r in rows])
NR=np.array([r['nr'] for r in rows]); MV=np.array([r['mvote'] for r in rows])
DAYa=np.array([r['day'] for r in rows]); Ba=np.array([r['b'] for r in rows])
def stat(m):
    k=int(m.sum())
    if k==0: return '-|-|-'
    return '%d|%+.3f|%+.3f'%(k,F30[m].mean(),F45[m].mean())
print('Z|table|the bucket A B C D land in|A|B|C|D')
def zrow(tbl,fn,sel):
    print('Z|%s|%s|%s'%(tbl,fn,'|'.join(sel(q) for q in Q)))
print('Z|A  nsame bucket|bucket each lands in|%s'%'|'.join('nsame = %d'%q['nsame'] for q in Q))
print('Z|A  nsame bucket|that bucket 30m mean|%s'%'|'.join('%+.3f'%F30[NS==q['nsame']].mean() for q in Q))
print('Z|A  nsame bucket|that bucket 45m mean|%s'%'|'.join('%+.3f'%F45[NS==q['nsame']].mean() for q in Q))
print('Z|B  nopp bucket|bucket each lands in|%s'%'|'.join('nopp = %d'%q['nopp'] for q in Q))
print('Z|B  nopp bucket|that bucket 30m mean|%s'%'|'.join('%+.3f'%F30[NO==q['nopp']].mean() for q in Q))
print('Z|C  ARRIVED|bucket each lands in|%s'%'|'.join(('nr > 0' if q['nr']>0 else 'nr = 0') for q in Q))
print('Z|C  ARRIVED|that bucket 30m mean|%s'%'|'.join('%+.3f'%F30[(NR>0) if q['nr']>0 else (NR==0)].mean() for q in Q))
def ecell(q):
    if q['nopp']>=8 and q['mvote']>=6: return 'nopp>=8 + mvote>=6'
    if q['nopp']>=8 and q['mvote']<=2: return 'nopp>=8 + mvote<=2'
    if q['nsame']>=8 and q['mvote']>=6: return 'nsame>=8 + mvote>=6'
    if q['nsame']>=8 and q['mvote']<=2: return 'nsame>=8 + mvote<=2'
    return 'none of the 4 E rows'
print('Z|E  vote x started|bucket each lands in|%s'%'|'.join(ecell(q) for q in Q))
def emean(q):
    if q['nopp']>=8 and q['mvote']>=6: m=(NO>=8)&(MV>=6)
    elif q['nopp']>=8 and q['mvote']<=2: m=(NO>=8)&(MV<=2)
    elif q['nsame']>=8 and q['mvote']>=6: m=(NS>=8)&(MV>=6)
    elif q['nsame']>=8 and q['mvote']<=2: m=(NS>=8)&(MV<=2)
    else: return '-'
    return '%+.3f'%F30[m].mean()
print('Z|E  vote x started|that bucket 30m mean|%s'%'|'.join(emean(q) for q in Q))
print('Z|')
print('Z|is each example inside the 12992 event set?|%s'%'|'.join(('yes' if q['b'] in set(Ba.tolist()) else 'NO') for q in Q))
