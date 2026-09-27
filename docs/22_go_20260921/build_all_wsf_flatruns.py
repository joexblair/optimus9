"""build_all_wsf_flatruns - spec_label 22_go_20260921.  Joe 0922: "create a db table:
'all_wsf_flatruns'. dump the full 5 days into it", then "drop it and rebuild in the report shape".

REBUILT 0927 IN JOE'S Sheet2 SHAPE.  Joe 0927: "I need to update all_wsf_flatruns. for each row, I
need 3 more rows that provide tactical data" / "it's important that the new data is stacked under
each existing row" / "convert the columns to string, and print the time using hh:mm".

FIVE ROWS PER wsl_sig_utc, `awf_kind` says which, `awf_n` orders them:

  1 flatrun   awf_ws1..awf_ws12 = the FIRST flat-run bar at or after sig_utc - 8 min, as `hh:mm`
  2 dir       the Mage line's incoming direction over five CONSECUTIVE bands, newline-stacked
  3 mage      ws{t}Mage at sig_utc
  4 r         ws{t}r at sig_utc
  5 xcross    the NEAREST ws{t}x cross of ws{t}r to sig_utc, looking back AND forward, as `hh:mm`

THE x-CROSS ROW IS JOE'S, 0927: *"the timestamp of the nearest (lookback or lookforth)
ws{awf_ws{TF}}x-cross-r"*.

  the direction is BANKED and dr-signed - dr +1: x crosses UNDER its target. dr -1: x crosses OVER.
  the search is UNBOUNDED in both directions; NULL means no cross anywhere on the tape.

  MINE, stated: on an exact tie in distance the LOOKBACK bar wins, because it is the causal side.

  THE FORWARD HALF IS LOOKAHEAD BY CONSTRUCTION, and that is Joe's instruction - "lookforth". It is
  fine in a diagnostic table and must never reach a signal path. The cell does not say which side it
  came from; a back cross and a forward cross at the same `hh:mm` are indistinguishable in it.

THE FIVE BANDS ARE JOE'S, 0927: *"for the 5 incoming directions, test using these bands: 16 to 8 /
8 to 4 / 4 to 2 / 2 to 1 / 1 to sig_utc"*.  Each cell is `Mage[the later edge] - Mage[the earlier
edge]`, 12 bars = 1 min at the 5 s grid.

  `UP`  the later edge is higher      `DN`  lower      `-`  bit-identical
Joe 0927 set all three labels.  Ties are real: measured 86 of 14,520 cells = 0.592%, on 10 of the
242 rows, concentrated in the 2->1 band with 44.

THREE READINGS WERE TESTED BEFORE JOE RULED, on his own example row 09-01 00:27:20:
  nested to sig_utc      Mage[sig] - Mage[sig - N min]                 -> UP DN DN DN DN
  the instant            Mage[sig - N min] - the bar before it         -> DN UP DN FLAT DN
  consecutive bands      16->8, 8->4, 4->2, 2->1, 1->sig               -> UP DN DN DN DN   <- Joe's
None reproduced the `UP DN - DN UP` he typed into Sheet2, and the 87.3 / 100 he typed are not that
row's ws1 either - it reads ws1Mage 96.20 and ws1r 52.09.  Joe 0927, told so: *"it's all groovy"*.
His Sheet2 cells are a FORMAT ILLUSTRATION, not expected values.

`awf_ws*` ARE VARCHAR NOW, and `hh:mm` DROPS THE SECONDS - `00:19:20` becomes `00:19`.  Nothing is
lost permanently: every cell is derived from `wsf_leash` plus `flat_run_at` over the tape, so a
rebuild recovers the exact bar.  Joe was told and approved.

`awf_kind` IS IN THE UNIQUE KEY.  Four rows now share one `awf_first_ms`, so the old key would
collide.  MINE, stated: without it a rebuild overwrites three of its own four rows.

`awf_dr` AND `awf_sig_utc` STAY REAL ON ALL FOUR ROWS.  Both are NOT NULL and they are how the four
rows stay together and sort.  Joe's Sheet2 shows `awf_dr` blank and the row's LABEL sitting in the
`awf_sig_utc` column on the three new rows - that is the REPORT's rendering, not the table's.
`report_all_wsf_flatruns.py` prints it his way.

The 8-minute flat-run lookback is Joe's - "to ensure I don't miss any flat runs before sig_utc" - so
a cell earlier than awf_sig_utc is a run that fired before the signal.  Forward search is unbounded;
NULL means none before the tape end.

Producer: flat_run_at(r, j, dr, r-momo-fence 17/83, samples 3, tol 2.0), at the row's own wsl_dr.
Both banked wsf_leash instances are covered: v7 = coil_lines[gcws30,ws1], v8 = coil_lines[ws2,ws3].

CAUSAL. Every band reads bars at or before sig_utc. The flat-run search starts 8 min before it.
"""
import sys,io,numpy as np
_o=sys.stdout; sys.stdout=io.StringIO()
import os
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'_prelude.py'))
     .read().split("k=int(np.searchsorted")[0])
sys.stdout=_o
from optimus9.compute.test_points import flat_run_at
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

TABLE='all_wsf_flatruns'; TFS=range(1,13); SAMPLES=3; TOL=2.0; BACK=96
EDGE=(16,8,4,2,1,0)                      # minutes before sig_utc; 0 IS sig_utc
BAND=[(int(EDGE[i]*12),int(EDGE[i+1]*12)) for i in range(5)]     # (earlier bars, later bars)
KINDS=(('flatrun',1),('dir',2),('mage',3),('r',4),('xcross',5))
INST={'v7':'v7_coil_lines[gcws30,ws1]_confirm_lag_s180_exit_anchornamed_bar_gap_fill1_lookback_s240_support_min23',
      'v8':'v8_coil_lines[ws2,ws3]_confirm_lag_s180_exit_anchornamed_bar_gap_fill1_lookback_s240_support_min23'}
KNOBS='fence%g.%g_samples%d_tol%g_back%d'%(FENCE[0],FENCE[1],SAMPLES,TOL,BACK)
WIN='2026-09-01..2026-09-06'
DDL='''CREATE TABLE IF NOT EXISTS %s (
    awf_pk       BIGINT AUTO_INCREMENT PRIMARY KEY,
    awf_knobs    VARCHAR(80) NOT NULL,
    awf_win      VARCHAR(48) NOT NULL,
    awf_inst     VARCHAR(8)  NOT NULL,
    awf_kind     VARCHAR(8)  NOT NULL,
    awf_n        TINYINT     NOT NULL,
    awf_dr       TINYINT     NOT NULL,
    awf_sig_utc  DATETIME(3) NOT NULL,
    awf_sig_ms   BIGINT      NOT NULL,
    awf_first_ms BIGINT      NOT NULL,
    %s
    UNIQUE KEY uq_awf (awf_knobs, awf_win, awf_inst, awf_first_ms, awf_kind),
    KEY k_sig (awf_sig_ms, awf_n))'''%(TABLE,'\n    '.join('awf_ws%d VARCHAR(32) NULL,'%t for t in TFS))
COLS=(['awf_knobs','awf_win','awf_inst','awf_kind','awf_n','awf_dr','awf_sig_utc','awf_sig_ms',
       'awf_first_ms']+['awf_ws%d'%t for t in TFS])

hhmm=lambda j: U(j)[11:16]
def sgn(a,b):
    d=float(b)-float(a)
    return 'UP' if d>0 else ('DN' if d<0 else '-')

def xcross_bars(x,r,dr):
    """Bars where ws{t}x crosses ws{t}r on the dr side. dr +1 -> x goes from at/above r to below.
    dr -1 -> from at/below r to above. The landing bar is the cross."""
    x=np.asarray(x,float); r=np.asarray(r,float)
    if dr>0:
        c=(x[:-1]>=r[:-1])&(x[1:]<r[1:])
    else:
        c=(x[:-1]<=r[:-1])&(x[1:]>r[1:])
    return np.flatnonzero(c)+1

def nearest_cross(cr,k):
    """The cross bar nearest k, looking back and forward. A tie goes to the lookback side."""
    if not len(cr): return None
    i=int(np.searchsorted(cr,k))
    back=int(cr[i-1]) if i>0 else None
    fwd=int(cr[i]) if i<len(cr) else None
    if back is None: return fwd
    if fwd is None: return back
    return back if (k-back)<=(fwd-k) else fwd

db=DatabaseManager(**get_db_config()); db.connect()
if '--drop' in sys.argv:
    db.execute("DROP TABLE IF EXISTS %s"%TABLE); print('B|dropped %s'%TABLE)
db.execute(DDL); print('B|created %s|knobs %s|win %s'%(TABLE,KNOBS,WIN))
print('B|bands %s|labels UP DN -'%' '.join('%d->%d'%(EDGE[i],EDGE[i+1]) for i in range(5)))
pay=[]; pre=0; blank=0; ties=0; short=0; nox=0; xback=0; xfwd=0; xat=0
MG={t:np.asarray(MA[t],float) for t in TFS}
RR={t:np.asarray(RA[t],float) for t in TFS}
XX={t:np.asarray(Ln(t,'x'),float) for t in TFS}
XC={}
for inst,kn in INST.items():
    rows=db.execute("SELECT wsl_dr,wsl_sig_utc,wsl_sig_ms,wsl_first_ms FROM wsf_leash WHERE wsl_knobs=%s "
                    "AND wsl_sig_ms IS NOT NULL ORDER BY wsl_sig_ms",(kn,),fetch=True)
    for r in rows:
        k=int(np.searchsorted(ts,int(r['wsl_sig_ms']))); d=int(r['wsl_dr']); s0=max(0,k-BACK)
        head=[KNOBS,WIN,inst]
        tail=[d,U(k),int(ts[k]),int(r['wsl_first_ms'])]
        for t in TFS:
            XC.setdefault((t,d), xcross_bars(XX[t],RR[t],d))
        fr=[]; dr_=[]; mg=[]; rv=[]; xc=[]
        for t in TFS:
            j=next((q for q in range(s0,len(ts)) if flat_run_at(RA[t],q,d,FENCE,SAMPLES,TOL) is not None),None)
            if j is None: fr.append(None); blank+=1
            else:
                fr.append(hhmm(j))
                if j<k: pre+=1
            if k-BAND[0][0]<0:
                dr_.append(None); short+=1
            else:
                v=[sgn(MG[t][k-a],MG[t][k-b]) for a,b in BAND]
                ties+=sum(1 for x in v if x=='-')
                dr_.append('\n'.join(v))
            mg.append('%.2f'%MG[t][k]); rv.append('%.2f'%RR[t][k])
            b=nearest_cross(XC[(t,d)],k)
            if b is None: xc.append(None); nox+=1
            else:
                xc.append(hhmm(b))
                if b<k: xback+=1
                elif b>k: xfwd+=1
                else: xat+=1
        for kind,n in KINDS:
            cells={'flatrun':fr,'dir':dr_,'mage':mg,'r':rv,'xcross':xc}[kind]
            pay.append(tuple(head+[kind,n]+tail+cells))
n=db.execute("SELECT COUNT(*) c FROM %s WHERE awf_knobs=%%s AND awf_win=%%s"%TABLE,
             (KNOBS,WIN),fetch=True)[0]['c']
if n:
    print('B|%d rows already banked at this key - nothing written'%n); db.disconnect(); raise SystemExit
db.executemany("INSERT INTO %s (%s) VALUES (%s)"%(TABLE,','.join(COLS),','.join(['%s']*len(COLS))),pay)
NK=len(KINDS)
print('B|banked %d rows = %d sig_utc x %d kinds'%(len(pay),len(pay)//NK,NK))
print('B|flatrun cells %d|fired before sig_utc %d|NULL %d'%(len(pay)//NK*12,pre,blank))
print('B|dir cells %d|ties (-) %d|rows too close to the tape start %d'%(len(pay)//NK*12,ties,short))
print('B|xcross cells %d|from the lookback %d|from the lookforth %d|at sig_utc %d|no cross on the tape %d'
      %(len(pay)//NK*12,xback,xfwd,xat,nox))
q=db.execute("SELECT awf_inst i, awf_kind kd, COUNT(*) n FROM %s GROUP BY 1,2 ORDER BY 1,3 DESC"%TABLE,fetch=True)
for x in q: print('S|%s|%s|rows %d'%(x['i'],x['kd'],x['n']))
print('S|columns: %s'%', '.join(c['Field'] for c in db.execute("SHOW COLUMNS FROM %s"%TABLE,fetch=True)))
db.disconnect()
