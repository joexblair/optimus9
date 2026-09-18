"""drcost - how many ws1Mage oob entries my dr-framed event definition threw away."""
exec(open('oosbump.py').read().split('A0,A1=int(np.searchsorted')[0])
import numpy as np
A0,A1=int(np.searchsorted(ts,ms(D0))),int(np.searchsorted(ts,ms(D1)))
fin=np.isfinite(Mst).all(axis=0)&np.isfinite(Rst).all(axis=0)&np.isfinite(PXT)
m1=Mst[0]
hi_side = m1>=HI                     # ws1Mage in the HIGH oob, raw, no dr
lo_side = m1<=LO                     # ws1Mage in the LOW  oob, raw, no dr
any_oob = (hi_side|lo_side)&fin
def entries(mask, keepdr):
    prev=np.zeros(n,bool); prev[1:]=mask[:-1]
    if keepdr:
        sd=np.zeros(n,bool); sd[1:]=(DR[1:]==DR[:-1]); st=mask&~(prev&sd)
    else:
        st=mask&~prev
    hold=np.ones(n,bool)
    for k in range(1,3):
        h=np.zeros(n,bool)
        if keepdr: h[:n-k]=mask[k:]&(DR[k:]==DR[:n-k])
        else:      h[:n-k]=mask[k:]
        hold&=h
    e=np.flatnonzero(st&hold); e=e[(e>=A0)&(e<A1)&(e+120*BPM<=n-1)]
    return e
E_all = entries(any_oob, False)                       # dr-free: ws1Mage enters EITHER oob
E_mine= entries(oob1&(DR!=0)&fin, True)               # what I built
src_hi = m1[E_all]>=HI
print('P|population|events')
print('P|ws1Mage enters EITHER oob, dr-free (source = the side it entered)|%d'%len(E_all))
print('P|  source = hi 85|%d'%int(src_hi.sum()))
print('P|  source = lo 15|%d'%int((~src_hi).sum()))
print('P|what I built: ws1Mage enters the oob ON THE dr SIDE|%d'%len(E_mine))
print('P|')
d_at=DR[E_all]
agree = np.where(src_hi, d_at>0, d_at<0)
print('P|of the dr-free entries, dr AGREES with the source side|%d  (%.0f%%)'%(int(agree.sum()),100*agree.mean()))
print('P|of the dr-free entries, dr OPPOSES the source side|%d  (%.0f%%)'%(int((~agree&(d_at!=0)).sum()),100*(~agree&(d_at!=0)).mean()))
print('P|of the dr-free entries, dr is 0 (never latched)|%d  (%.0f%%)'%(int((d_at==0).sum()),100*(d_at==0).mean()))
print('P|')
print('P|THROWN AWAY by requiring the oob side to match dr|%d  (%.0f%% of all entries)'%(
   len(E_all)-int(agree.sum()), 100*(len(E_all)-int(agree.sum()))/len(E_all)))
