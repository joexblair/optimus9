"""
seed_s1mage.py (Joe 0704) — create s1Mage (s1M, 60s) as a real line + normalise s2M (120s) so the gate's
reversal line becomes a sweep knob (s1M 60s vs s2M 120s). Both bb 37·0.72·hlcc4, EMERGING. Versioned.
The gate reads s1M by default (== the old s2M@60 override; identical values, now a proper DB line).
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

db = DatabaseManager(**get_db_config()); db.connect()
IS_S, IL_M, EMERG, HI, LO = 2, 2, 2, 85.0, 15.0
# ind_name → itf_pk (60s=4, 120s=21). Both bb 37·0.72·hlcc4.
LINES = {'s1M': 4, 's2M': 21}


def live(name):
    r = db.execute("SELECT ic_line_type,ic_src,ic_bb_len,ic_bb_mult,value_mode FROM vw_indicator_configs_live WHERE ind_name=%s", (name,), fetch=True)
    return r[0] if r else None


for name, itf in LINES.items():
    m = live(name)
    if m and m['ic_line_type'] == 'bb' and int(m['ic_bb_len']) == 37 and float(m['ic_bb_mult']) == 0.72 \
            and m['ic_src'] == 'hlcc4' and m['value_mode'] == 'emerging':
        print('%-5s ok' % name); continue
    db.execute('''INSERT INTO indicator_configs (ic_is_pk,ic_il_pk,ic_itf_pk,ic_line_type,ic_live_after_dt,ic_src,
        ic_high_boundary,ic_low_boundary,ic_bb_len,ic_bb_mult,ic_k_len,ic_rsi_len,ic_stc_len,ic_ivm_pk,ic_wobble)
        VALUES (%s,%s,%s,'bb',(CURDATE()-INTERVAL 1 DAY),'hlcc4',%s,%s,37,0.72,NULL,NULL,NULL,%s,NULL)''',
        (IS_S, IL_M, itf, HI, LO, EMERG))
    print('%-5s seeded (bb 37·0.72·hlcc4 emerging)' % name)

print('--- gate Mage lines ---')
for name in ('s1M', 's2M'):
    v = live(name); print(' %-5s bb %s·%s·%s vm=%s' % (name, v['ic_bb_len'], v['ic_bb_mult'], v['ic_src'], v['value_mode']))
db.disconnect()
