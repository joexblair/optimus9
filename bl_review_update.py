"""
bl_review_update.py (Joe 0620) — refresh the bl_review table against the CURRENT active breach set.
bl_review reads bl_states and keys gate-opens off the full-set combined_state, so it needs the WHOLE
active set in bl_states (not a scoped subset). Pipeline: full bl_detect.report() (all active breaches)
→ build_review(db). Window 0611–0615 (END 0616 00:00). Calls build_review directly to sidestep the
run.py:634 stop_pct/stop_px display KeyError. Info-labelled at each junction.
"""
import sys, time; sys.path.insert(0, '/home/joe/thecodes')
import datetime as dtm
from datetime import timezone
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.bl_detect import BLDetect
from optimus9.analysis.bl_review import build_review
from alchemy_report import build_bias_state, add_pl_cascade_events, add_bro_cross_events, add_pk_bias_events, paint_bias_state
from logger import get_logger

log = get_logger('bl_review_update'); t0 = time.perf_counter()
el = lambda: f'{time.perf_counter() - t0:5.1f}s'
END = int(dtm.datetime(2026, 6, 16, tzinfo=timezone.utc).timestamp() * 1000)   # window [0611, 0616)

db = DatabaseManager(**get_db_config()); db.connect()
det = BLDetect(db, lookback_hours=120, warmup_hours=48)                        # ALL active breaches (no scoping)
log.info(f'[{el()}] full bl_detect — {len(det._families)} active breaches: {[f["name"] for f in det._families]}')
det.report(end_ms=END)
log.info(f'[{el()}] bl_states repopulated (full set) — building review ...')
rows = build_review(db)
gates = sum(1 for o in rows if o['stop_px'] is not None)
W, bs = build_bias_state(db, END)                                             # window + merged bias (bls3 + pk)
n_cas = add_pl_cascade_events(db, W, bs, END)                                  # decoupled lp cascade: pl_cas_start/end
n_bro = add_bro_cross_events(db, W, END)                                       # alchemy overlay: bro_x_bias flips
n_pk = add_pk_bias_events(db, W, END)                                          # alchemy overlay: pk_bias updates
n_bias = paint_bias_state(db, bs, END)                                        # bias_state := merged BiasState (bls3 + pk + bro-cross)
log.info(f'[{el()}] DONE — bl_review {len(rows)} rows · {gates} gate-opens · {n_cas} pl_cas · {n_bro} bro_x_bias · {n_pk} pk_bias · {n_bias} bias segments')
print(f'bl_review updated: {len(rows)} rows, {gates} gate-opens, {n_cas} pl_cas, {n_bro} bro_x_bias, {n_pk} pk_bias, {n_bias} bias segments')
db.disconnect()
