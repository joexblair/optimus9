"""s3s4_gate_walk.py — extract s3s4 gate-open events, last 2 days, with es side (Joe 0707).

For walking the new causal-arm-delay events (arm_delay_walk) against the existing s3s4 gate. Uses the canonical
dial-in (lr_config) gate mechanic: v2_arm (RAW arms, no look-ahead arm_delay) -> gate_open -> reason a/b/c. Writes
`s3s4_gate_walk` (utc_dt = gate-open bar · es · reason). NO pnl. Run:  python3 s3s4_gate_walk.py
"""
import time, datetime as dtm
from datetime import timezone
import numpy as np

import bias_machine as bm
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.lr import lr_config
from sweep_eval import BASE_BIAS
from optimus9.analysis.lr_v2 import v2_arm, gate_open

WALK_DAYS = 2


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    lr = lr_config(dev)
    now = int(time.time() * 1000)
    W = bm.BiasWindow(dev, now, lookback=96, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS))
    ts = np.asarray(W.ts)
    cutoff = now - WALK_DAYS * 86400000

    gates = gate_open(W, lr, v2_arm(W, lr))                          # [(arm_i, es, bd, open_k, reason, cap)]
    rows = []
    for (i, es, bd, open_k, reason, cap) in gates:
        t = int(ts[open_k])
        if t < cutoff:
            continue
        dt = dtm.datetime.fromtimestamp(t / 1000, timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        rows.append((dt, int(es), reason))
    rows.sort(key=lambda x: x[0])

    dev.execute("DROP TABLE IF EXISTS s3s4_gate_walk")
    dev.execute("""CREATE TABLE s3s4_gate_walk (
        id INT AUTO_INCREMENT PRIMARY KEY, utc_dt DATETIME, es TINYINT, reason VARCHAR(2))""")
    dev.executemany("INSERT INTO s3s4_gate_walk (utc_dt,es,reason) VALUES (%s,%s,%s)", rows)
    from collections import Counter
    print("wrote %d gate-open events -> s3s4_gate_walk (last %dd)" % (len(rows), WALK_DAYS))
    print("  by reason:", dict(Counter(r[2] for r in rows)), " | by es:", dict(Counter(r[1] for r in rows)))
    for r in rows[:12]:
        print("   ", r[0], "es=%+d" % r[1], "reason=%s" % r[2])
    dev.disconnect()


if __name__ == "__main__":
    main()
