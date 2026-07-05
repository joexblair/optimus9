"""seed_cascade_state.py (Joe 0705) — the cascade-state REGISTRY for the o9-live UI mirror-grids + state logging.

One row per monitored cascade state: its bit (in the per-bar mask), its grid cell (row×col), its label, and a note
on the 'true rule'. The mask is built by OR-ing set bits (state true → bit set). The UI reads THIS table for the
grid layout (data-driven, no hardcoded cells) + the mask (o9_health.cascade_mask) for true/false → left(red)/right(green).

Grid: 4 deep × 5 wide, side-dependent on the arm's es. bit = (col-1)*4 + (row-1). active=0 → reserved (not computed yet).
Run: python3 seed_cascade_state.py
"""
import sys
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

# (state, col, row, label, active, true_rule) — grp derived from col; bit = (col-1)*4+(row-1)
ROWS = [
    # col1 — arm / s5 stack (Joe 0705)
    ('s5m',        1, 1, 's5m',        1, 's5m breach on es side (raw arm trigger)'),
    ('s5M',        1, 2, 's5M',        1, 's5Mage OOB on es side'),
    ('arm',        1, 3, 'arm',        1, 's5Mage reversal toward es (arm-delay-s7r release)'),
    ('s7M_rev',    1, 4, 's7M reversed',1, 's7Mage reversal toward es (tide tell)'),
    # col2 — s3s4 gate
    ('s3s4_run',   2, 1, 's3s4 run',   1, 'gate actively predict-testing (s3m/s4m OOB)'),
    ('s3s4_wait',  2, 2, 's3s4 wait',  1, 's3m+M & s4m+M all breached, awaiting r-line capture'),
    ('s3s4_gate',  2, 3, 's3s4 gate',  1, 'gate OPEN (path a/b/c)'),
    ('stale_exit', 2, 4, 'stale-exit', 1, 's2r/s3r/s4r all IB at the arm bar (AB toggle → no trade)'),
    # col3 — s15 finisher lines (r4 = precursor row)
    ('s15m',       3, 1, 's15m',       1, 's15m OOB on es side'),
    ('s15M',       3, 2, 's15M',       1, 's15M OOB on es side'),
    ('s15a',       3, 3, 's15a',       1, 's15a qualified within fin_lb of T'),
    ('s7r_predict',3, 4, 's7r predict', 1, 'predict_breach(s7r)==es'),
    # col4 — s30 finisher lines (r4 = precursor row)
    ('s30m',       4, 1, 's30m',       1, 's30m OOB on es side'),
    ('s30M',       4, 2, 's30M',       1, 's30M OOB on es side'),
    ('s30a',       4, 3, 's30a',       1, 's30a qualified within fin_lb of T'),
    ('rtr',        4, 4, 'rtr',        1, 'ready-to-reverse latch (gate path-c setup#1/#2)'),
    # col5 — s1 finisher lines (RESERVED until the 1s tape lands)
    ('s1m',        5, 1, 's1m',        0, 's1m OOB on es side (1s tape — reserved)'),
    ('s1M',        5, 2, 's1M',        0, 's1M OOB on es side (1s tape — reserved)'),
    ('s1a',        5, 3, 's1a',        0, 's1a qualified (1s tape — reserved)'),
]
GRP = {1: 'arm', 2: 'gate', 3: 's15', 4: 's30', 5: 's1'}

if __name__ == '__main__':
    db = DatabaseManager(**get_db_config()); db.connect()
    db.execute("""CREATE TABLE IF NOT EXISTS cascade_state (
        cs_pk INT AUTO_INCREMENT PRIMARY KEY,
        state VARCHAR(32) COLLATE utf8mb4_bin NOT NULL UNIQUE,   -- case-SENSITIVE: s15m != s15M

        bit TINYINT NOT NULL,
        cell_row TINYINT NOT NULL,
        cell_col TINYINT NOT NULL,
        grp VARCHAR(16) NOT NULL,
        label VARCHAR(32) NOT NULL,
        active TINYINT NOT NULL DEFAULT 1,
        true_rule VARCHAR(255) NOT NULL DEFAULT '',
        UNIQUE KEY uq_cell (cell_col, cell_row), UNIQUE KEY uq_bit (bit))""")
    for state, col, row, label, active, rule in ROWS:
        bit = (col - 1) * 4 + (row - 1)
        db.execute("""INSERT INTO cascade_state (state,bit,cell_row,cell_col,grp,label,active,true_rule)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE
            bit=VALUES(bit), cell_row=VALUES(cell_row), cell_col=VALUES(cell_col), grp=VALUES(grp),
            label=VALUES(label), active=VALUES(active), true_rule=VALUES(true_rule)""",
            (state, bit, row, col, GRP[col], label, active, rule))
    print('cascade_state seeded: %d states' % len(ROWS))
    for r in db.execute("SELECT state,bit,cell_col,cell_row,active FROM cascade_state ORDER BY cell_col,cell_row", fetch=True):
        print('  bit%-2d  c%dr%d  active=%d  %s' % (r['bit'], r['cell_col'], r['cell_row'], r['active'], r['state']))
    db.disconnect()
