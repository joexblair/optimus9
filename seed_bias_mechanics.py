"""seed_bias_mechanics.py — idempotent DB seed for #37 bro-cross indicator sets (docs/bias_mechanics_design.md).
Creates indicator_series (hbhl/hblo/hbhi), versioned indicator_configs (hb16 reconfig + 3 BB sets + gcs15),
lp_config lp_bro_wob. Re-runnable. Run seed_value_modes.py first (indicator_value_modes dimension)."""
import sys; sys.path.insert(0,'/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
db=DatabaseManager(**get_db_config()); db.connect()
DT='2026-06-25 00:00:00'
db.execute("""INSERT INTO indicator_series (is_pk,is_prefix) VALUES (13,'hbhl'),(14,'hblo'),(15,'hbhi')
   ON DUPLICATE KEY UPDATE is_prefix=VALUES(is_prefix)""")
COLS="ic_pk,ic_is_pk,ic_itf_pk,ic_il_pk,ic_line_type,ic_live_after_dt,ic_src,ic_high_boundary,ic_low_boundary,ic_bb_len,ic_bb_mult,ic_k_len,ic_rsi_len,ic_stc_len,ic_ivm_pk"
specs=[
 (8,20,2,'bb','close',19,0.64,None,None,None),
 (8,20,3,'k','hlc3',None,None,7,74,29),
 (13,20,2,'bb','hl2',19,0.64,None,None,None),
 (13,20,1,'bb','ohlc4',13,0.68,None,None,None),
 (14,20,2,'bb','low',19,0.64,None,None,None),
 (14,20,1,'bb','low',13,0.68,None,None,None),
 (15,20,2,'bb','high',19,0.64,None,None,None),
 (15,20,1,'bb','high',13,0.68,None,None,None),
 (6,2,2,'bb','ohlc4',37,0.72,None,None,None),
 (6,2,1,'bb','hlc3',10,0.40,None,None,None),
 (6,2,6,'k','close',None,None,5,6,6),
]
nxt=db.execute("SELECT MAX(ic_pk) m FROM indicator_configs",fetch=True)[0]['m']+1
rows=[(nxt+i,iss,itf,il,lt,DT,src,85.0,15.0,bl,bm,k,r,s,1) for i,(iss,itf,il,lt,src,bl,bm,k,r,s) in enumerate(specs)]
db.executemany(f"INSERT INTO indicator_configs ({COLS}) VALUES ({','.join(['%s']*15)})",rows)
db.execute("INSERT INTO lp_config (name,val,note) VALUES ('lp_bro_wob',12,'bro-cross M/m wobslay tol (5s bars)') ON DUPLICATE KEY UPDATE val=VALUES(val),note=VALUES(note)")
print(f"inserted {len(rows)} configs (ic_pk {nxt}-{nxt+len(rows)-1}) + 3 series + lp_bro_wob")
db.disconnect()