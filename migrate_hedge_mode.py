"""migrate_hedge_mode.py — add fx_position.position_idx for hedge mode (Joe 0708). Idempotent.
Default target = o9_live_test (build/validate). For the CUTOVER, run with `o9_live` ONLY when the loop
is stopped (the running one-way engine holds old code in memory — a live migration + old code is a mixed
schema). Usage:  python3 migrate_hedge_mode.py [db_name]   (default o9_live_test)"""
import sys
from optimus9.config import get_db_config
from optimus9 import DatabaseManager


def main():
    dbn = sys.argv[1] if len(sys.argv) > 1 else "o9_live_test"
    cfg = get_db_config(); cfg["database"] = dbn
    db = DatabaseManager(**cfg); db.connect()
    cols = [r["Field"] for r in db.execute("SHOW COLUMNS FROM fx_position", fetch=True)]
    if "position_idx" in cols:
        print("%s: position_idx already present — no-op" % dbn)
    else:
        db.execute("ALTER TABLE fx_position ADD COLUMN position_idx TINYINT NOT NULL DEFAULT 1 AFTER side")
        db.execute("ALTER TABLE fx_position ADD INDEX (symbol, position_idx, status)")
        print("%s: added fx_position.position_idx (1=long,2=short) + per-leg index" % dbn)
    db.disconnect()


if __name__ == "__main__":
    main()
