"""seed_bias_producer.py — the bias-producer registry (data-driven on/off, the tg_active pattern).
build_bias_state feeds only bp_active=1 rows. UI-shaped (name + label + active) for the bl_review
settings UI. bl_state is ALSO gated upstream by bl_lines.bl_is_active; this is the one-place toggle."""
import sys; sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
db = DatabaseManager(**get_db_config()); db.connect()
db.execute('''CREATE TABLE IF NOT EXISTS bias_producer (
    bp_pk INT AUTO_INCREMENT PRIMARY KEY,
    bp_name VARCHAR(24) UNIQUE,
    bp_label VARCHAR(48),
    bp_seq INT DEFAULT 0,
    bp_active TINYINT DEFAULT 1)''')
db.execute('''INSERT INTO bias_producer (bp_name, bp_label, bp_seq, bp_active) VALUES
    ('pk','PK bias',1,1), ('bro_cross','Bro-cross',2,1), ('bl_state','BL state-change',3,1)
    ON DUPLICATE KEY UPDATE bp_label=VALUES(bp_label), bp_seq=VALUES(bp_seq)''')
print('bias_producer:', [dict(r) for r in db.execute('SELECT bp_name,bp_label,bp_active FROM bias_producer ORDER BY bp_seq', fetch=True)])
db.disconnect()
