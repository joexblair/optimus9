"""
seed_finisher_v2.py (Joe 0704) — hoist the Mage-anchored finisher_v2 dials into lp_config (no-hardcode).
Idempotent: inserts only if absent (won't clobber a tuned value).
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

DIALS = [
    ('lp_fin_mage_wob', 0.0, 'finisher_v2: Mage-reversal wobslay n for qualify + trigger (0=slope-flip; sweep 0-3)'),
    ('lp_fin_s30M_oob', 1.0, 'finisher_v2: require M OOB in s{TF}a qualify (1=strict m&M-OOB · 0=m-only, M just reverses)'),
    ('lp_fin_lb', 42.0, 'finisher_v2: qualify search look-BACK from gate-open, base 5s bars (7x30s = 42)'),
    ('lp_fin_fwd', 12.0, 'finisher_v2: qualify search look-FWD past gate-open, base 5s bars (2x30s = 12)'),
]
db = DatabaseManager(**get_db_config()); db.connect()
for name, val, note in DIALS:
    if not db.execute("SELECT 1 FROM lp_config WHERE name=%s", (name,), fetch=True):
        db.execute("INSERT INTO lp_config (name, val, note) VALUES (%s, %s, %s)", (name, val, note))
print('finisher_v2 dials:', db.execute(
    "SELECT name, val FROM lp_config WHERE name LIKE 'lp_fin_%' ORDER BY name", fetch=True))
db.disconnect()
