"""
seed_arm_delay.py (Joe 0704) — hoist the arm-delay knobs into lp_config + set the shipped stop to 0.7%.
lp_arm_wob (s5Mage reversal wobslay for the delay) · lp_arm_bigleg (1=on) · lp_fin_both (1=both finisher
windows). Idempotent for the inserts; lp_lr_sl is UPDATED to 0.7 (Joe: the arm-delay shipped stop).
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

DIALS = [
    ('lp_arm_wob', 2.0, 'arm-delay: s5Mage-reversal wobslay n for the big-leg delay (sweep; start 2)'),
    ('lp_arm_bigleg', 1.0, 'arm-delay: 1=delay the arm to the s5Mage reversal on big legs · 0=off'),
    ('lp_fin_both', 1.0, 'finisher: 1=both windows (lookback+forward, union) · 0=lookback only'),
]
db = DatabaseManager(**get_db_config()); db.connect()
for name, val, note in DIALS:
    if not db.execute("SELECT 1 FROM lp_config WHERE name=%s", (name,), fetch=True):
        db.execute("INSERT INTO lp_config (name, val, note) VALUES (%s, %s, %s)", (name, val, note))
db.execute("UPDATE lp_config SET val=0.7 WHERE name='lp_lr_sl'")                 # shipped stop = 0.7% (Joe 0704)
print('arm-delay + stop dials:', db.execute(
    "SELECT name, val FROM lp_config WHERE name IN ('lp_arm_wob','lp_arm_bigleg','lp_fin_both','lp_lr_sl') ORDER BY name", fetch=True))
db.disconnect()
