"""build_all_wsf_flatruns - spec_label 22_go_20260921.  Joe 0922: "create a db table:
'all_wsf_flatruns'. dump the full 5 days into it", then "drop it and rebuild in the report shape".

REBUILT 0927 IN JOE'S Sheet2 SHAPE.  Joe 0927: "I need to update all_wsf_flatruns. for each row, I
need 3 more rows that provide tactical data" / "it's important that the new data is stacked under
each existing row" / "convert the columns to string, and print the time using hh:mm".

FIVE ROWS PER wsl_sig_utc, `awf_kind` says which, `awf_n` orders them:

  1 flatrun   awf_ws1..awf_ws12 = the FIRST flat-run bar at or after sig_utc - 8 min, as `hh:mm`
  2 dir       the Mage line's incoming direction over five CONSECUTIVE bands, newline-stacked,
              the bands scaled by TF, all five two-point
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

THE BANDS ARE A BASE SET SCALED BY TF - Joe 0927: *"let's remix the 1,2,4,8,16 logic / 1) create a
base set of values: [0.75, 1.5, 3, 6, 12] / 2) apply the lookback using base-set * TF -- eg for ws12,
the lookbacks will be 9, 18, 36, 72, 144"*.  He asked for it because static brackets hid what he was
after: *"what I'm looking for in the direction row is contrast between the TFs. now I see that using
static brackets for all TFs is unlikley to show me anything useful."*

  the five edges are the base set DESCENDING, times the TF, in minutes before sig_utc
  sig_utc closes the last band, so five edges plus sig_utc give five consecutive bands
  the LAST MILE - `0.75 x TF -> sig_utc` - is the BOTTOM line of the stack.  Joe 0927 stated the
  assumption and it holds.

  ws1   12     6     3     1.5   0.75  minutes  ->  144  72  36  18  9     bars
  ws12  144    72    36    18    9     minutes  ->  1728 864 432 216 108   bars

EVERY EDGE LANDS ON A WHOLE BAR.  0.75 min is 9 bars exactly at the 5 s grid, so base x TF x 12 is
always an integer.  Nothing is rounded.

THE LAST MILE IS TWO-POINT, LIKE THE OTHER FOUR - Joe 0927: *"revert the last mile to two-point.
after I've reviewed, we can decide if we still need to apply the poisioning fix"*.

  THE EXTREMA VERSION IS KEPT IN `side_extrema` BUT NOT CALLED.  It was built on Joe's 0927 word
  *"apply this mech to the last mile only (0.75 to 0)"* with the extrema dr-SIDE - *"extrema is dr
  specific : minimum for -1dr"* - and it COLLAPSED.  The dr-side extreme is by definition the
  furthest point in the dr direction inside the window, so extreme -> sig_utc has only one possible
  answer: at dr -1 it reads UP or `-`, never DN; at dr +1 DN or `-`, never UP.

  MEASURED over the 242 rows x 12 TFs: 0 UP at dr +1, 0 DN at dr -1, and the bottom line was
  IDENTICAL across all twelve TFs on 224 of 242 rows, never carrying more than 2 distinct values.
  The label had become a restatement of the row's dr.  Joe spotted it by eye: *"my eyeballing sees
  the bottom line of dir as monotonic (ws1 to ws12) for every sig_utc"*.

  THE TWO-POINT READING CARRIES A TF GRADIENT, which is what the base-set scaling was for. Measured
  on the 121 v7 rows, the share of last miles moving TOWARDS dr:

    ws1 30.6%   ws2 50.4%   ws3 59.5%   ws4 71.1%   ws5 81.0%   ws6 91.7%
    ws7 87.6%   ws8 90.9%   ws9 95.9%   ws10 97.5%  ws11 95.9%  ws12 95.9%

  ws1 leans AGAINST dr at 68.6%, which is the signature of a turn having just happened - Joe's
  suspected poisoning, since `wsl_sig_utc` is a gcws30Mage `sig` cross on 98 of 121 rows and a
  ws1Mage reversal precedes it. ws2 and ws3 are the only TFs whose last mile is genuinely two-way.
  THE POISONING FIX IS NOT APPLIED - Joe is reviewing the two-point build first.

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
BASE=(12,6,3,1.5,0.75)                   # Joe's base set, DESCENDING, minutes; x TF below
def bands(tf):
    """The five (earlier bars, later bars) pairs for one TF. 0 bars IS sig_utc."""
    e=[int(round(b*tf*12)) for b in BASE]+[0]
    return [(e[i],e[i+1]) for i in range(5)]
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

def side_extrema(v,k,back,dr):
    """The dr-SIDE extreme of `v` over the closed window [k-back, k]. dr -1 -> the minimum,
    dr +1 -> the maximum. A tie goes to the EARLIEST bar, where the line first turned.

    NOT CALLED - see the docstring. Kept because Joe may return to the poisoning fix."""
    a=max(0,int(k)-int(back)); seg=np.asarray(v[a:int(k)+1],float)
    i=int(np.argmin(seg)) if int(dr)<0 else int(np.argmax(seg))
    return a+i, float(seg[i])

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
print('B|base set %s x TF minutes|labels UP DN -'%' '.join('%g'%b for b in BASE))
print('B|ws1 bars %s|ws12 bars %s|all five bands two-point'%(bands(1),bands(12)))
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
            BD=bands(t)
            if k-BD[0][0]<0:
                dr_.append(None); short+=1
            else:
                v=[sgn(MG[t][k-a],MG[t][k-b]) for a,b in BD]
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
