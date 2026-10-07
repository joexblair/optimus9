"""Seed lazy_g_config v1 — every knob the lazy-g stack had hardcoded. Joe 1006: *"anything that's
currently hardcoded in lazy-g and octo-freedom can go into their respective config tables now"*.

The lazy-g stack is docs/octo-freedom/1005_scoring/: score39.py, baton.py, octosig_db.py,
lineage_walk.py. Before this seed, NONE of them read a config table - every value was a module
constant, and baton.TFS had drifted to range(3, 24) against wsf_dtf_v3_config's own
bands.band_wsf_lo = 1 / bands.band_dtf_hi = 23.

`source` records where the value came from. Where a knob mirrors one in wsf_dtf_v3_config the row
says so, so the MVP2 sunset (task #25) can prove the two agreed at the moment of the copy.
"""
import sys
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
from optimus9.compute.spec_config import ddl, spec_config

TABLE, PFX, VER = 'lazy_g_config', 'lgc', 1

# section, key, value, type, units, owner, fitted, in_key, source, note
ROWS = [
 # ---- the two r fences. oob is the block fence, momo_fence_r mirrors to the ex-fence.
 ('fences','oob_hi','85.0','float','r-points','joe',0,1,'wsf_dtf_v3_config v10 dr.oob_hi; score39.py:42 HI',None),
 ('fences','oob_lo','15.0','float','r-points','joe',0,1,'wsf_dtf_v3_config v10 dr.oob_lo; score39.py:42 LO',None),
 ('fences','momo_fence_r','17','int','r-points','joe',0,1,'wsf_dtf_v3_config v10 wsf_chain.momo_fence_r; Joe 0820 "create a new fence: momo-fence-r 100-{knob:17}"','the ex-fence is 100-17 = 83 on the high side'),

 # ---- the ladders
 ('ladder','band_lo','1','int','timeframe','joe',0,1,'wsf_dtf_v3_config v10 bands.band_wsf_lo; score39.py:63 TF','the r/Mage ladder the routing and the lineage read'),
 ('ladder','band_hi','12','int','timeframe','joe',0,1,'wsf_dtf_v3_config v10 bands.band_wsf_hi; score39.py:63 TF',None),
 ('ladder','baton_tf_lo','1','int','timeframe','joe',0,1,'Joe 1006 "we need both ws1 and ws2, and if that moves any column data then it is the price of correctness"','was hardcoded 3 in baton.py and contradicted the DB'),
 ('ladder','baton_tf_hi','23','int','timeframe','joe',0,1,'wsf_dtf_v3_config v10 bands.band_dtf_hi and v3_report.tf_hi; baton.py:46 TFS',None),

 # ---- Joe's lineage, 1006
 ('lineage','lin_hop','2','int','TF numbers','joe',0,1,'Joe 1006 "jump no more than 2 higher TFs to find the next TF with momentum" / "TF numbers. eg, ws1 can only look to ws2 and ws3"',None),
 ('lineage','lin_anchor','1','int','timeframe','joe',0,1,'Joe 1006 "I know the spec does not include ws1r at the moment, but this example shows me that we need it as an anchor"',None),
 ('lineage','walk_start','g5extrema','str',None,'joe',0,1,'Joe 1006 "09:28:05 is the g5extrema, literally the best place to test because it shows how the market is behaving from a momentum perspective"','the bar the lineage walk starts from'),

 # ---- mtd, the routing anchor
 ('mtd','mtd_walk_bars','24','int','bars','joe',0,1,'score39.py:215 MTD_WALK_BARS','2 min at the 5 s grid'),
 ('mtd','g5extrema_lookback_bars','48','int','bars','joe',0,1,'score39.py:43; equals wsf_dtf_v3_config v10 stretchy_leash.lookback_s 240 / 5','how far back mtd step 1 searches for the g5Mage extrema'),
 ('mtd','tol_g5','0','int','bars','joe',0,1,'score39.py:52 TOL',None),
 ('mtd','tol_g15','3','int','bars','joe',0,1,'score39.py:52 TOL',None),
 ('mtd','tol_g30','6','int','bars','joe',0,1,'score39.py:52 TOL',None),
 ('mtd','tol_ws1','0','int','bars','joe',0,1,'score39.py:52 TOL',None),

 # ---- branch D
 ('branch_d','claim_hop','3','int','TF numbers','joe',0,1,'Joe 1005 "A at +3 makes sense based your findings"',None),
 ('branch_d','gap_max','4','int','TF gap','joe',0,1,'score39.py:42 GAP_MAX',None),

 # ---- the baton
 ('baton','stall_n','6','int','lattice samples','joe',0,1,'wsf_dtf_v3_config v10 wsf_chain.stall_n; baton.py:46 STALL_N',None),
 ('baton','traj_min_bars','24','int','bars','joe',0,1,'baton.py:46 TRAJ_MIN_BARS',None),
 ('baton','traj_min_travel','0.0','float','r-points','joe',0,1,'baton.py:46 TRAJ_MIN_TRAVEL',None),
 ('baton','warm_bars','2160','int','bars','joe',0,0,'Joe 1004 "start the walk 3 hours earlier, regardless of if it is a o9-live loop walk or a target timestamp"','3 h at the 5 s grid. Warm-up only, so it does not change a row'),

 # ---- ws1mage-rev's reversal detector, as score39 uses it
 ('rev','rev_wob','2','int','steps','joe',0,1,'wsf_dtf_v3_config v10 ws1mage_rev.rev_wob; score39.py:42 REV_WOB',None),

 # ---- scoring. swing_detect is a BACKTEST RULER, not a causal tool - Joe 1006.
 ('scoring','swing','1.25','float','pct','joe',0,1,'Joe 1006 "swing_detect: I am fine with it being 1.25"','was 0.70. The knee sits between 1.00 and 1.25 and it is sharp'),
 ('scoring','mae_block','0.70','float','pct','joe',0,1,'octosig_db.py MAE_BLOCK','SEPARATE from swing. It has not moved'),
]

def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    db.execute(ddl(TABLE, PFX))
    n = db.execute('SELECT COUNT(*) n FROM %s WHERE %s_version=%%s' % (TABLE, PFX), (VER,), fetch=True)[0]['n']
    if n and '--force' not in sys.argv:
        print('# %s v%d already has %d rows. --force to replace.' % (TABLE, VER, n)); return
    if n:
        db.execute('DELETE FROM %s WHERE %s_version=%%s' % (TABLE, PFX), (VER,))
        print('# replaced %d rows at v%d' % (n, VER))
    db.executemany(
        'INSERT INTO %s (%s_version,%s_section,%s_key,%s_value,%s_type,%s_units,%s_owner,'
        '%s_fitted,%s_in_key,%s_source,%s_note) VALUES (%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s)'
        % ((TABLE,) + (PFX,) * 11),
        [(VER,) + r for r in ROWS])
    C = spec_config(db, TABLE)
    print('# seeded %s -> %d knobs, key %s' % (TABLE, len(C), C.key()))
    print('| section | knob | value | units | in_key |'); print('|---|---|---|---|---|')
    for k in sorted(C, key=lambda x: (C.meta[x]['section'], x)):
        m = C.meta[k]
        print('| %s | %s | %s | %s | %s |' % (m['section'], k, C[k], m['u'] or '', m['in_key']))

if __name__ == '__main__':
    main()
