"""
seed_lr_config.py (Joe 0628) — hoist the lr (latch-release) dials into lp_config (no-hardcode, step 3 of
applying cf15 to prod). Idempotent: inserts only if absent (won't clobber a value you've tuned).
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

DIALS = [
    ('lp_lr_floor', 8.0, 'lr: s6m reversal-magnitude floor (line-units) — near-flat vs true reversion'),
    ('lp_lr_wob_n', 4.0, 'lr: s6m wobslay bars (the reversal window)'),
    ('lp_lr_horizon', 1080.0, 'lr: setup search horizon in 5s bars (90 min) for reversal + s30a re-breach'),
    ('lp_lr_target', 0.9, 'lr: favourable swing target % -> mfe_ok'),
    ('lp_lr_swing_ms', 30000.0, 'lr: swing/price grid in ms (30s cadence for the MAE/MFE walk + pivots)'),
    ('lp_lr_swing_pct', 0.9, 'lr: ZigZag swing threshold % for find_pivots (favourable-pivot detection)'),
    ('lp_lr_bias_mid', 50.0, 'lr: bias-gate midline — the mid-check fires above/below this'),
]

db = DatabaseManager(**get_db_config()); db.connect()
for name, val, note in DIALS:
    if not db.execute("SELECT 1 FROM lp_config WHERE name=%s", (name,), fetch=True):
        db.execute("INSERT INTO lp_config (name, val, note) VALUES (%s, %s, %s)", (name, val, note))
print('lr dials in lp_config:', db.execute(
    "SELECT name, val FROM lp_config WHERE name LIKE 'lp_lr_%' ORDER BY name", fetch=True))
db.disconnect()
