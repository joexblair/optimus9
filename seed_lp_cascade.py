import sys; sys.path.insert(0,'/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
db=DatabaseManager(**get_db_config()); db.connect()
DT='2026-06-26 00:00:00'
# 1. s6m line: s-series(is_pk 2), TF6(itf_pk 6=360s), minor(il_pk 1), BB 10|0.4 close, closed(ivm 1)
exists=db.execute("SELECT ic_pk FROM vw_indicator_configs_live WHERE ind_name='s6m'", fetch=True)
if not exists:
    nxt=db.execute("SELECT MAX(ic_pk) m FROM indicator_configs",fetch=True)[0]['m']+1
    db.execute("""INSERT INTO indicator_configs
        (ic_pk,ic_is_pk,ic_itf_pk,ic_il_pk,ic_line_type,ic_live_after_dt,ic_src,ic_high_boundary,ic_low_boundary,ic_bb_len,ic_bb_mult,ic_ivm_pk)
        VALUES (%s,2,6,1,'bb',%s,'close',85.0,15.0,10,0.4,1)""",(nxt,DT))
s6m=db.execute("SELECT ic_pk FROM vw_indicator_configs_live WHERE ind_name='s6m'", fetch=True)[0]['ic_pk']
# 2. trade_gate reconfig: s6m -> s30a -> xm45a -> gcs15a (s30a pins the entry to a real OOB extreme)
db.execute("DELETE FROM trade_gate_line"); db.execute("DELETE FROM trade_gate")
db.execute("INSERT INTO trade_gate (tg_pk,tg_seq,tg_name,tg_op,tg_active) VALUES (1,1,'s6m','AND',1),(2,2,'s30a','AND',1),(3,3,'xm45a','AND',1),(4,4,'gcs15a','AND',1)")
gl=[(1,s6m),(2,46),(2,47),(2,48),(3,51),(3,50),(3,52),(4,79),(4,80),(4,81)]   # s6m | s30 M/m/r | xm45 M/m/r | gcs15 M/m/r
db.executemany("INSERT INTO trade_gate_line (tgl_tg_pk,tgl_ic_pk) VALUES (%s,%s)", gl)
# 3. lp_xm45_wob
db.execute("INSERT INTO lp_config (name,val,note) VALUES ('lp_xm45_wob',2,'xm45min wobble_slayer turn length (5s bars) — the lp-cascade entry trigger') ON DUPLICATE KEY UPDATE val=VALUES(val),note=VALUES(note)")
print(f"s6m ic_pk={s6m}")
print("trade_gate:", [dict(r) for r in db.execute("SELECT tg_seq,tg_name,tg_active FROM trade_gate ORDER BY tg_seq", fetch=True)])
print("s6m resolves:", db.execute("SELECT ind_name,ic_line_type,ic_src,ic_bb_len,ic_bb_mult,itf_seconds FROM vw_indicator_configs_live WHERE ind_name='s6m'", fetch=True))
db.disconnect()
