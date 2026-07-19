"""Thin CLI over rpl_walk.run_walk: run one flip walk, tee the events, persist to DB.
Usage: python3 -m optimus9.orchestration.rpl_s8cycle <walk> [depth] [dwell]   (defaults from DB baseline)."""
import sys, hashlib
from optimus9 import DatabaseManager
from optimus9.config import get_db_config
from optimus9.db.rpl_event_store import RplEventStore
import optimus9.orchestration.rpl_walk as R

WALK = sys.argv[1] if len(sys.argv) > 1 else '12_02'
depth = int(sys.argv[2]) if len(sys.argv) > 2 else None
dwell = int(sys.argv[3]) if len(sys.argv) > 3 else None
ev, meta = R.run_walk(WALK, depth, dwell, tee=True)

REV = hashlib.md5(open(R.__file__, 'rb').read()).hexdigest()[:12]
db = DatabaseManager(**get_db_config()); db.connect(); st = RplEventStore(db)
for r in db.execute("SELECT rr_pk FROM rpl_run WHERE rr_walk=%s", (WALK,), fetch=True): db.execute("DELETE FROM rpl_run WHERE rr_pk=%s", (r['rr_pk'],))
b = ev[-1][0] if ev else meta['conf']
run_pk = st.register_run(meta['flip'], meta['conf'], b, meta['rc_pk'], engine_rev=REV, walk=WALK, notes=f"{meta['bias']} climb -> {meta['flip']} flip")
st.log_events(run_pk, [{'ts': t, 'stage': e, 'tf': r, 'note': nt} for t, e, r, nt in ev])
db.disconnect()
print(f"  persisted walk {WALK} run_pk={run_pk} events={len(ev)}")
