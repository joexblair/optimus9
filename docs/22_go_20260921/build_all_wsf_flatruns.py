"""build_all_wsf_flatruns - spec_label 22_go_20260921.  Joe 0922: "create a db table:
'all_wsf_flatruns'. dump the full 5 days into it", then "drop it and rebuild in the report shape".

ONE ROW PER wsl_sig_utc.  awf_ws1..awf_ws12 each hold ONE timestamp: the FIRST flat-run bar at or
after sig_utc - 8 minutes.  The 8-minute lookback is Joe's - "to ensure I don't miss any flat runs
before sig_utc" - so a cell earlier than awf_sig_utc is a run that fired before the signal.
Forward search is unbounded; NULL means none before the tape end.

Producer: flat_run_at(r, j, dr, r-momo-fence 17/83, samples 3, tol 2.0), at the row's own wsl_dr.
Both banked wsf_leash instances are covered: v7 = coil_lines[gcws30,ws1], v8 = coil_lines[ws2,ws3].

REBUILT 0922.  The first version of this table banked every contiguous flat run - 9,406 rows at a
grain Joe did not ask for.  Joe: "drop it and rebuild in the report shape".
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
INST={'v7':'v7_coil_lines[gcws30,ws1]_confirm_lag_s180_exit_anchornamed_bar_gap_fill1_lookback_s240_support_min23',
      'v8':'v8_coil_lines[ws2,ws3]_confirm_lag_s180_exit_anchornamed_bar_gap_fill1_lookback_s240_support_min23'}
KNOBS='fence%g.%g_samples%d_tol%g_back%d'%(FENCE[0],FENCE[1],SAMPLES,TOL,BACK)
WIN='2026-09-01..2026-09-06'
WS=','.join('awf_ws%-2d DATETIME(3) NULL,'%t for t in TFS)
DDL='''CREATE TABLE IF NOT EXISTS %s (
    awf_pk       BIGINT AUTO_INCREMENT PRIMARY KEY,
    awf_knobs    VARCHAR(80) NOT NULL,
    awf_win      VARCHAR(48) NOT NULL,
    awf_inst     VARCHAR(8)  NOT NULL,
    awf_dr       TINYINT     NOT NULL,
    awf_sig_utc  DATETIME(3) NOT NULL,
    awf_sig_ms   BIGINT      NOT NULL,
    awf_first_ms BIGINT      NOT NULL,
    %s
    UNIQUE KEY uq_awf (awf_knobs, awf_win, awf_inst, awf_first_ms),
    KEY k_sig (awf_sig_ms))'''%(TABLE,'\n    '.join('awf_ws%d DATETIME(3) NULL,'%t for t in TFS))
COLS=['awf_knobs','awf_win','awf_inst','awf_dr','awf_sig_utc','awf_sig_ms','awf_first_ms']+['awf_ws%d'%t for t in TFS]
db=DatabaseManager(**get_db_config()); db.connect()
if '--drop' in sys.argv:
    db.execute("DROP TABLE IF EXISTS %s"%TABLE); print('B|dropped %s'%TABLE)
db.execute(DDL); print('B|created %s|knobs %s|win %s'%(TABLE,KNOBS,WIN))
pay=[]; pre=0; blank=0
for inst,kn in INST.items():
    rows=db.execute("SELECT wsl_dr,wsl_sig_utc,wsl_sig_ms,wsl_first_ms FROM wsf_leash WHERE wsl_knobs=%s "
                    "AND wsl_sig_ms IS NOT NULL ORDER BY wsl_sig_ms",(kn,),fetch=True)
    for r in rows:
        k=int(np.searchsorted(ts,int(r['wsl_sig_ms']))); d=int(r['wsl_dr']); s0=max(0,k-BACK)
        cells=[]
        for t in TFS:
            j=next((q for q in range(s0,len(ts)) if flat_run_at(RA[t],q,d,FENCE,SAMPLES,TOL) is not None),None)
            if j is None: cells.append(None); blank+=1
            else:
                cells.append(U(j))
                if j<k: pre+=1
        pay.append(tuple([KNOBS,WIN,inst,d,U(k),int(ts[k]),int(r['wsl_first_ms'])]+cells))
n=db.execute("SELECT COUNT(*) c FROM %s WHERE awf_knobs=%%s AND awf_win=%%s"%TABLE,
             (KNOBS,WIN),fetch=True)[0]['c']
if n:
    print('B|%d rows already banked at this key - nothing written'%n); db.disconnect(); raise SystemExit
db.executemany("INSERT INTO %s (%s) VALUES (%s)"%(TABLE,','.join(COLS),','.join(['%s']*len(COLS))),pay)
print('B|banked %d rows|cells %d|fired before sig_utc %d|NULL %d'%(len(pay),len(pay)*12,pre,blank))
q=db.execute("SELECT awf_inst i, COUNT(*) n, MIN(awf_sig_utc) lo, MAX(awf_sig_utc) hi FROM %s "
             "GROUP BY 1"%TABLE,fetch=True)
for x in q: print('S|%s|rows %d|%s -> %s'%(x['i'],x['n'],x['lo'],x['hi']))
print('S|columns: %s'%', '.join(c['Field'] for c in db.execute("SHOW COLUMNS FROM %s"%TABLE,fetch=True)))
db.disconnect()
