#!/bin/bash
# bny30p A/B validation: champion-anchored small sweep, two arms on the SAME random windows.
#   Arm A (with-p)    — draws fresh windows, includes bny30p in the bias.
#   Arm B (without-p) — replays A's windows, bny30M-only bias.
# Champion configs + small sweeps · lookbacks 16/33/56 · c_bls solo · curl-gate dropped · 30s bias.
set -e
cd /home/joe/thecodes
LOG=/home/joe/optimus9-docs-handover/logs
PRESERVE='from optimus9.config import get_db_config; from optimus9 import DatabaseManager; import sys; db=DatabaseManager(**get_db_config()); db.connect(); t=sys.argv[1]; db.execute(f"DROP TABLE IF EXISTS {t}"); db.execute(f"CREATE TABLE {t} AS SELECT * FROM bl_dialin_results"); print(t, db.execute(f"SELECT COUNT(*) c FROM {t}", fetch=True)[0]["c"], "rows"); db.disconnect()'

echo "=== ARM A: with bny30p ($(date -u +%H:%M)) ==="
python3 -u bl_dialin.py --champion --withp --budget 7 > "$LOG/grind_withp.log" 2>&1
python3 -u -c "$PRESERVE" bl_dialin_results_withp

echo "=== ARM B: without bny30p / M-only ($(date -u +%H:%M)) ==="
python3 -u bl_dialin.py --champion --budget 7 --replay > "$LOG/grind_withoutp.log" 2>&1
python3 -u -c "$PRESERVE" bl_dialin_results_withoutp

echo "=== BOTH ARMS DONE ($(date -u +%H:%M)) ==="
