exec(open('oosbump.py').read().split('A0,A1=int(np.searchsorted')[0])
import numpy as np, pickle
rows=pickle.load(open('oosbump3.pkl','rb'))
MB=np.array([r['mbump'] for r in rows]); MF=np.array([r['mfall'] for r in rows])
DRv=np.array([r['dr'] for r in rows]); B=np.array([r['b'] for r in rows])
def lad(lab,m):
    bb=B[m]
    mm=[float(np.nanmean(Mst[t][bb])) for t in range(12)]
    rr=[float(np.nanmean(Rst[t][bb])) for t in range(11)]
    print('L|%s|n=%d'%(lab,m.sum()))
    print('L|  Mage ws1..ws12  '+' '.join('%.1f'%v for v in mm))
    print('L|  r    ws2..ws12  '+' '.join('%.1f'%v for v in rr))
lad('dr -1, falls>0, bumps >= 8',(MF>0)&(MB>=8)&(DRv<0))
lad('dr -1, falls>0, bumps <= 7',(MF>0)&(MB<=7)&(DRv<0))
lad('dr +1, falls>0, bumps >= 8',(MF>0)&(MB>=8)&(DRv>0))
lad('dr +1, falls>0, bumps <= 7',(MF>0)&(MB<=7)&(DRv>0))
