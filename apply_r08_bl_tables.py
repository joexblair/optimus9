#!/usr/bin/env python3
"""
apply_r08_bl_tables.py — Stage 1 of the BL HTF-PK milestone: de-hardcode the BL
lines + stand up the supporting config tables. Idempotent — safe to re-run.

Creates / seeds:
  • indicator_configs rows  : hb9b/M/m @ TF9 (itf 7), s18b/m @ TF6-as-TF18 (itf 10)
  • pk_pools (+ pk_pools_live view) : per-series PK pool, versioned by pkp_live_after_date
        hb9 pool = pool_c 5 / pool_w 22 / pool_range 4 / slope_floor 13 / mult 1, votes 5,2
  • bl_lines : which lines are BL lines (role breach/anchor), per-line exit_mask + PK ref
        hb9b breach (mask 7 → exits 1/2/3, pk → hb9M) · hb9M/hb9m anchor
  • bl_config.blc_live_after_date + triggers (bl_config, bl_lines): stamp live_after_date
        = NOW() when is_active is set to 1 (interactive activate + versioned audit)

Lines are read by analysis/bl_detect.py (_load_family); tuning by _load_config.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from optimus9.config import get_db_config
from optimus9.db.database_manager import DatabaseManager


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    X = db.execute
    BASE = "'2000-01-01 00:00:00'"

    # ── indicator_configs (idempotent on is/il/itf) ──────────────────────────
    LINES = [  # is, il, itf, type, src, k_len, rsi, stc, bb_len, bb_mult
        (8, 3, 7,  'k',  'hlc3',  5, 74, 29,  None, None),   # hb9b
        (8, 2, 7,  'bb', 'hl2',   None, None, None, 19, 0.78),  # hb9M
        (8, 1, 7,  'bb', 'ohlc4', None, None, None, 13, 0.78),  # hb9m
        (2, 3, 10, 'k',  'close', 12, 66, 147, None, None),  # s18b (TF6 behaves as TF18)
        (2, 1, 10, 'bb', 'hl2',   None, None, None, 51, 0.83),  # s18m
    ]
    for isp, ilp, itf, lt, src, kl, rsi, stc, bl, bm in LINES:
        if X("SELECT ic_pk FROM indicator_configs WHERE ic_is_pk=%s AND ic_il_pk=%s AND ic_itf_pk=%s",
             (isp, ilp, itf), fetch=True):
            continue
        X(f"""INSERT INTO indicator_configs
            (ic_is_pk,ic_il_pk,ic_itf_pk,ic_line_type,ic_live_after_dt,ic_src,
             ic_high_boundary,ic_low_boundary,ic_k_len,ic_rsi_len,ic_stc_len,ic_bb_len,ic_bb_mult)
            VALUES (%s,%s,%s,%s,{BASE},%s,85,15,%s,%s,%s,%s,%s)""",
          (isp, ilp, itf, lt, src, kl, rsi, stc, bl, bm))
    icpk = lambda i, l, t: X("SELECT ic_pk FROM indicator_configs WHERE ic_is_pk=%s AND ic_il_pk=%s AND ic_itf_pk=%s",
                             (i, l, t), fetch=True)[0]['ic_pk']
    hb9b, hb9M, hb9m = icpk(8, 3, 7), icpk(8, 2, 7), icpk(8, 1, 7)

    # ── pk_pools + live view (mirrors indicator_configs_live) ────────────────
    X("""CREATE TABLE IF NOT EXISTS pk_pools (
        pkp_pk BIGINT AUTO_INCREMENT PRIMARY KEY, pkp_is_pk BIGINT NOT NULL,
        pkp_live_after_date DATETIME NOT NULL DEFAULT '2000-01-01',
        pkp_pool_c INT, pkp_pool_w INT, pkp_pool_range INT, pkp_slope_floor FLOAT,
        pkp_multiplier INT, pkp_weight_close INT, pkp_weight_wide INT)""")
    X("""CREATE OR REPLACE VIEW pk_pools_live AS
        SELECT p.*, s.is_prefix FROM pk_pools p JOIN indicator_series s ON s.is_pk=p.pkp_is_pk
        WHERE p.pkp_live_after_date = (SELECT MAX(p2.pkp_live_after_date) FROM pk_pools p2
            WHERE p2.pkp_is_pk=p.pkp_is_pk AND p2.pkp_live_after_date <= NOW())""")
    if not X("SELECT pkp_pk FROM pk_pools WHERE pkp_is_pk=8", fetch=True):
        X(f"""INSERT INTO pk_pools (pkp_is_pk,pkp_live_after_date,pkp_pool_c,pkp_pool_w,
            pkp_pool_range,pkp_slope_floor,pkp_multiplier,pkp_weight_close,pkp_weight_wide)
            VALUES (8,{BASE},5,22,4,13,1,5,2)""")

    # ── bl_lines ─────────────────────────────────────────────────────────────
    X("""CREATE TABLE IF NOT EXISTS bl_lines (
        bl_pk BIGINT AUTO_INCREMENT PRIMARY KEY, bl_ic_pk BIGINT NOT NULL,
        bl_role VARCHAR(16) NOT NULL, bl_exit_mask INT, bl_pk_ic_pk BIGINT,
        bl_is_active TINYINT DEFAULT 0, bl_live_after_date DATETIME DEFAULT '2000-01-01')""")
    for ic, role, mask, pkic in [(hb9b, 'breach', 7, hb9M), (hb9M, 'anchor', None, None),
                                 (hb9m, 'anchor', None, None)]:
        if X("SELECT bl_pk FROM bl_lines WHERE bl_ic_pk=%s", (ic,), fetch=True):
            continue
        X("""INSERT INTO bl_lines (bl_ic_pk,bl_role,bl_exit_mask,bl_pk_ic_pk,bl_is_active,bl_live_after_date)
             VALUES (%s,%s,%s,%s,1,NOW())""", (ic, role, mask, pkic))

    # ── bl_config live-date column + triggers (bl_config, bl_lines) ───────────
    if 'blc_live_after_date' not in [c['Field'] for c in X("SHOW COLUMNS FROM bl_config", fetch=True)]:
        X("ALTER TABLE bl_config ADD COLUMN blc_live_after_date DATETIME DEFAULT '2000-01-01'")
    for nm, tbl, act, dt in (('blc', 'bl_config', 'blc_is_active', 'blc_live_after_date'),
                             ('bl',  'bl_lines',  'bl_is_active',  'bl_live_after_date')):
        X(f"DROP TRIGGER IF EXISTS {nm}_live_ins")
        X(f"CREATE TRIGGER {nm}_live_ins BEFORE INSERT ON {tbl} FOR EACH ROW "
          f"SET NEW.{dt} = IF(NEW.{act}=1, NOW(), NEW.{dt})")
        X(f"DROP TRIGGER IF EXISTS {nm}_live_upd")
        X(f"CREATE TRIGGER {nm}_live_upd BEFORE UPDATE ON {tbl} FOR EACH ROW "
          f"SET NEW.{dt} = IF(NEW.{act}=1 AND OLD.{act}<>1, NOW(), NEW.{dt})")

    print("apply_r08_bl_tables: done (idempotent).")
    db.disconnect()


if __name__ == '__main__':
    main()
