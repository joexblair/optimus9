"""
bl_bls3_exits_emit.py (Joe 0620) — run bl_detect over 0611–0615 and emit transfer/0611_0615_bls3_exits.csv:
the b6p + hb9p EXITS (per-line state transitions into bls:3) with columns UTC · line_name · breach_line · px_smooth.
report() purges + repopulates bl_states for the SCOPED breach set; we filter the returned rows to the two lines.
Starting point for Joe's bias↔BL fold logic (he interleaves bias-mechanism rows between the bls3 states in Excel).
Info labels at each critical junction (elapsed-timed) for debug.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import datetime as dtm, time
from datetime import timezone
import csv
from collections import defaultdict
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.bl_detect import BLDetect
from logger import get_logger

log = get_logger('bl_bls3_emit')
t0 = time.perf_counter()
el = lambda: f'{time.perf_counter() - t0:5.1f}s'

END   = int(dtm.datetime(2026, 6, 16, tzinfo=timezone.utc).timestamp() * 1000)   # 0616 00:00 → window [0611,0616)
LINES = ('b6p', 'hb9p', 'hb16p')
log.info(f'[{el()}] START — window [0611,0616) UTC · lines={LINES} · end_ms={END}')

db = DatabaseManager(**get_db_config()); db.connect()
log.info(f'[{el()}] db connected — constructing BLDetect (lookback=120h, warmup=48h)')
det = BLDetect(db, lookback_hours=120, warmup_hours=48)
det._families = [f for f in det._families if f['name'] in LINES]   # only b6p + hb9p — per-line state is
det._fam = max(det._families, key=lambda f: f['tf_seconds'])       # family-independent; c_bls not needed
if len(det._families) != len(LINES):
    log.warning(f'[{el()}] expected {LINES} but scoped to {[f["name"] for f in det._families]} — check bl_lines active set')
log.info(f'[{el()}] families scoped to {[f["name"] for f in det._families]} (primary={det._fam["name"]})')

log.info(f'[{el()}] running report() — compute + purge/repopulate bl_states (fast multi-row insert) ...')
rows = det.report(end_ms=END)
log.info(f'[{el()}] report() done — {len(rows)} rows persisted to bl_states')
db.disconnect()

byline = defaultdict(list)
for r in rows:
    if r['line_name'] in LINES:
        byline[r['line_name']].append(r)
log.info(f'[{el()}] filtered rows per line: { {k: len(v) for k, v in byline.items()} }')

out = []
for ln, rs in byline.items():
    rs.sort(key=lambda r: r['bar_ms'])
    prev = None
    for r in rs:
        if r['state'] == 3 and prev != 3:              # transition INTO state 3 = the exit event
            out.append(r)
        prev = r['state']
out.sort(key=lambda r: r['bar_ms'])
log.info(f'[{el()}] exits (state→3) per line: { {ln: sum(1 for r in out if r["line_name"] == ln) for ln in LINES} }')

path = '/home/joe/thecodes/transfer/0611_0615_bls3_exits.csv'
with open(path, 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['UTC', 'line_name', 'breach_line', 'px_smooth'])
    for r in out:
        utc = dtm.datetime.fromtimestamp(r['bar_ms'] / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        w.writerow([utc, r['line_name'], r['breach_line'], r['px_smooth']])
log.info(f'[{el()}] DONE — wrote {len(out)} exits → {path}')
print('exits:', len(out), {ln: sum(1 for r in out if r['line_name'] == ln) for ln in LINES}, '→', path)
