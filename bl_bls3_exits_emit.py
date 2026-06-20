"""
bl_bls3_exits_emit.py (Joe 0620) — run bl_detect over 0611–0615 and emit transfer/0611_0615_bls3_exits.csv:
the b6p + hb9p EXITS (per-line state transitions into bls:3) with columns UTC · line_name · breach_line · px_smooth.
report() purges + repopulates bl_states for the full active breach set; we filter the returned rows to the two lines.
Starting point for Joe's bias↔BL fold logic (he interleaves bias-mechanism rows between the bls3 states in Excel).
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import datetime as dtm
from datetime import timezone
import csv
from collections import defaultdict
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.bl_detect import BLDetect

END   = int(dtm.datetime(2026, 6, 16, tzinfo=timezone.utc).timestamp() * 1000)   # 0616 00:00 → window [0611,0616)
LINES = ('b6p', 'hb9p')

db = DatabaseManager(**get_db_config()); db.connect()
det = BLDetect(db, lookback_hours=120, warmup_hours=48)
det._families = [f for f in det._families if f['name'] in LINES]   # only b6p + hb9p — per-line state is
det._fam = max(det._families, key=lambda f: f['tf_seconds'])       # family-independent; c_bls not needed → ~4.5× faster
rows = det.report(end_ms=END)
db.disconnect()

byline = defaultdict(list)
for r in rows:
    if r['line_name'] in LINES:
        byline[r['line_name']].append(r)

out = []
for ln, rs in byline.items():
    rs.sort(key=lambda r: r['bar_ms'])
    prev = None
    for r in rs:
        if r['state'] == 3 and prev != 3:          # transition INTO state 3 = the exit event
            out.append(r)
        prev = r['state']
out.sort(key=lambda r: r['bar_ms'])

path = '/home/joe/thecodes/transfer/0611_0615_bls3_exits.csv'
with open(path, 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['UTC', 'line_name', 'breach_line', 'px_smooth'])
    for r in out:
        utc = dtm.datetime.fromtimestamp(r['bar_ms'] / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        w.writerow([utc, r['line_name'], r['breach_line'], r['px_smooth']])

print('exits:', len(out), {ln: sum(1 for r in out if r['line_name'] == ln) for ln in LINES})
print('→', path)
