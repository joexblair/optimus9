import pickle, numpy as np, collections
rows=pickle.load(open('oosbump3.pkl','rb'))
MINS=(30,45,60,90,120); BPM=12
F={k:np.array([r['f%d'%k] for r in rows]) for k in MINS}
MB=np.array([r['mbump'] for r in rows]); MF=np.array([r['mfall'] for r in rows])
DRv=np.array([r['dr'] for r in rows]); DAY=np.array([r['day'] for r in rows])
B=np.array([r['b'] for r in rows]); RF=np.array([r['rfall'] for r in rows])
NOOB=np.array([r['noob'] for r in rows])
def eff(m):
    """clusters: events separated by more than 120 min (1440 bars) of each other"""
    bb=np.sort(B[m]);  return 1+int((np.diff(bb)>1440).sum()) if len(bb) else 0
def L(lab,m):
    k=int(m.sum())
    if k==0: print('A|%s|0|0|||||' % lab); return
    print('A|%s|%d|%d|%+.3f|%+.3f|%+.3f|%+.3f|%+.3f|%.0f%%' %
      (lab,k,eff(m),F[30][m].mean(),F[45][m].mean(),F[60][m].mean(),F[90][m].mean(),F[120][m].mean(),
       100*(F[120][m]<0).mean()))
print('A|set|events|clusters|30m|45m|60m|90m|120m|hit% 120m')
for k in range(0,11): L('falls>0 + bumps = %d'%k,(MF>0)&(MB==k))
print('A|')
L('falls>0 + bumps >= 8',(MF>0)&(MB>=8))
L('falls>0 + bumps >= 8, dr +1',(MF>0)&(MB>=8)&(DRv>0))
L('falls>0 + bumps >= 8, dr -1',(MF>0)&(MB>=8)&(DRv<0))
L('falls>0 + bumps <= 7',(MF>0)&(MB<=7))
L('falls>0 + bumps <= 7, dr +1',(MF>0)&(MB<=7)&(DRv>0))
L('falls>0 + bumps <= 7, dr -1',(MF>0)&(MB<=7)&(DRv<0))
print('A|')
for q in (2,3,4,5):
    L('falls>0 + bumps >= 8 + lower TFs oob >= %d'%q,(MF>0)&(MB>=8)&(NOOB>=q))
print('A|')
for q in (0,10,20,30,40):
    L('bumps >= 8 + falls >= %d'%q,(MF>=q)&(MB>=8))
print()
# ── per-day contribution of the bumps>=8 set, to find outlier days ────────────────────────
m=(MF>0)&(MB>=8)
dd=collections.defaultdict(list)
for i in np.flatnonzero(m): dd[DAY[i]].append(F[120][i])
tot=F[120][m].sum()
print('D|day|events|mean 120m|sum 120m|share of total sum')
for d,v in sorted(dd.items(), key=lambda x:np.sum(x[1]))[:8]:
    print('D|%s|%d|%+.3f|%+.3f|%.0f%%' % (d,len(v),np.mean(v),np.sum(v),100*np.sum(v)/tot))
print('D|...')
for d,v in sorted(dd.items(), key=lambda x:np.sum(x[1]))[-5:]:
    print('D|%s|%d|%+.3f|%+.3f|%.0f%%' % (d,len(v),np.mean(v),np.sum(v),100*np.sum(v)/tot))
print('D|TOTAL|%d|%+.3f|%+.3f|100%%' % (m.sum(),F[120][m].mean(),tot))
nd=sum(1 for d,v in dd.items() if np.mean(v)<0)
print('D|days with a negative mean 120m: %d of %d' % (nd,len(dd)))
# drop the single best and single worst day
srt=sorted(dd.items(), key=lambda x:np.sum(x[1]))
keep=set(dd)-{srt[0][0],srt[-1][0]}
km=m&np.isin(DAY,list(keep))
print('D|bumps>=8 with the best and worst day removed: n %d  120m %+.3f' % (km.sum(),F[120][km].mean()))
