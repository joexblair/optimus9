"""Seed octo_freedom_config v1 — the knobs octo-freedom still had hardcoded. Joe 1006.

octo-freedom was ALREADY almost fully DB-driven: optimus9/live/octo_inputs.py:OctoConfig reads
wsf_trade_config (walk v4 + trade v3), wsf_dtf_v3_config, lr_config, momo_config and mech_lines, and
optimus9/compute/leash_walk.py takes every knob as a constructor argument with no module constants
at all. Only four values were left in code.
"""
import sys
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
from optimus9.compute.spec_config import ddl, spec_config

TABLE, PFX, VER = 'octo_freedom_config', 'ofc', 1

ROWS = [
 ('grid','bar_ms','5000','int','milliseconds','joe',0,1,'optimus9/live/octo_freedom.py:40 BAR_MS; equals wsf_dtf_v3_config v10 wsf_chain.grid_s 5 s','the tape grid'),
 ('window','lookback_h','24','int','hours','joe',0,1,'Joe 1001 "#3 window is approved"; optimus9/live/octo_freedom.py:42, strategy.py:23 defaults',None),
 ('window','warmup_h','80','int','hours','joe',0,1,'Joe 1001 "#3 window is approved"; optimus9/live/octo_freedom.py:42, strategy.py:23 defaults',None),
 ('emit','label','octo-sig','str',None,'joe',0,0,'Joe 1001 / 1002 - what opens a trade, and what an opposing one closes it as; optimus9/live/octo_freedom.py:41','a label, so it does not change a row'),
 ('arm','mid','50.0','float','r-points','joe',0,1,'optimus9/compute/arm_state.py:35 MID','the midline the arm fence is measured from'),
]

def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    db.execute(ddl(TABLE, PFX))
    n = db.execute('SELECT COUNT(*) n FROM %s WHERE %s_version=%%s' % (TABLE, PFX), (VER,), fetch=True)[0]['n']
    if n and '--force' not in sys.argv:
        print('# %s v%d already has %d rows. --force to replace.' % (TABLE, VER, n)); return
    if n:
        db.execute('DELETE FROM %s WHERE %s_version=%%s' % (TABLE, PFX), (VER,))
    db.executemany(
        'INSERT INTO %s (%s_version,%s_section,%s_key,%s_value,%s_type,%s_units,%s_owner,'
        '%s_fitted,%s_in_key,%s_source,%s_note) VALUES (%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s)'
        % ((TABLE,) + (PFX,) * 11), [(VER,) + r for r in ROWS])
    C = spec_config(db, TABLE)
    print('# seeded %s -> %d knobs, key %s' % (TABLE, len(C), C.key()))
    print('| section | knob | value | units | in_key |'); print('|---|---|---|---|---|')
    for k in sorted(C, key=lambda x: (C.meta[x]['section'], x)):
        m = C.meta[k]
        print('| %s | %s | %s | %s | %s |' % (m['section'], k, C[k], m['u'] or '', m['in_key']))

if __name__ == '__main__':
    main()
