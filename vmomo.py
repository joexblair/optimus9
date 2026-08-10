"""vectorised momo — must match build_exhv2.momo() exactly."""
import os,sys
os.environ.setdefault('RPL_TF_CEILING','4'); sys.path.insert(0,'/home/joe/thecodes')
import numpy as np, build_exhv2 as B

def vmomo(r, dr):
    """(state[n] int8, slope[n], r2[n], rw[n]) for every bar. state 0=none 1=sideways 2=curl 3=momo.
    Line-for-line vectorisation of build_exhv2.momo() at :113-162."""
    n=len(r); S=B.MOMO_SAMPLES; SB=B.MOMO_STEP_BARS
    span=(S-1)*SB
    slope=np.full(n,np.nan); r2=np.full(n,np.nan)
    idx=np.arange(span,n)
    if len(idx):
        cols=np.stack([r[idx-(S-1-k)*SB] for k in range(S)],axis=1)   # (m,S) oldest->newest
        ok=np.isfinite(cols).all(axis=1)
        x=np.arange(S,dtype=float); xm=x.mean(); sxx=((x-xm)**2).sum()
        ym=cols.mean(axis=1)
        sl=((cols-ym[:,None])*(x-xm)).sum(axis=1)/sxx
        ic=ym-sl*xm
        res=((cols-(sl[:,None]*x+ic[:,None]))**2).sum(axis=1)
        tot=((cols-ym[:,None])**2).sum(axis=1)
        rr=np.where(tot>1e-12,1-res/np.where(tot>1e-12,tot,1),0.0)
        slope[idx]=np.where(ok,sl,np.nan); r2[idx]=np.where(ok,rr,np.nan)
    rw=r.copy()
    st=np.zeros(n,np.int8)                       # default none
    have=np.isfinite(slope)&np.isfinite(r2)&np.isfinite(rw)
    trk=np.clip(np.where(have,r2,0.0)*np.minimum(1.0,np.abs(np.where(have,slope,0.0))/max(1e-9,B.MOMO_SLOPE_MIN)),0.0,1.0)
    slack=B.LEVEL_SLACK*trk
    level=(rw>=50-slack) if dr>0 else (rw<=50+slack)
    flat=np.abs(slope)<B.MOMO_SLOPE_MIN
    aligned=(slope>0) if dr>0 else (slope<0)
    # non-flat branch
    momo=have&(~flat)&level&aligned&(r2>=B.MOMO_R2_MIN)
    st[momo]=3
    # flat branch: level False -> none ; else sideways unless curl
    cand=have&flat&level
    st[cand]=1                                   # sideways by default
    nb=B.MOMO_WINDOW_MIN*12
    ci=np.flatnonzero(cand)
    ci=ci[ci-nb+1>=0]
    if len(ci):
        xx=np.linspace(0.0,1.0,nb)
        A=np.vstack([xx**2,xx,np.ones(nb)]).T
        pinv=np.linalg.pinv(A)
        # CHUNKED: the full stack is len(ci) x 720 floats. At 300k candidates that is 1.7 GB, so the
        # quadratic runs in blocks. Chunking changes nothing about the result - each row is independent.
        CH=20000
        for a0 in range(0,len(ci),CH):
            blk=ci[a0:a0+CH]
            W=np.stack([r[i-nb+1:i+1] for i in blk],axis=0)
            good=np.isfinite(W).all(axis=1)
            if not good.any(): continue
            C=W[good]@pinv.T
            qa,qb=C[:,0],C[:,1]
            nz=np.abs(qa)>1e-12
            vtx=np.where(nz,-qb/(2*np.where(nz,qa,1)),np.nan)
            arc=np.abs(qa)*0.25
            curl=nz&(vtx>B.CURL_VTX_LO)&(vtx<B.CURL_VTX_HI)&(arc>=B.CURL_ARC_MIN)
            gi=blk[good]
            st[gi[curl]]=2
    return st,slope,r2,rw
