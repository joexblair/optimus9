"""
seed_r_hl2.py (Joe 0704) — re-spec s15r/s30r to the canonical finisher r-line: k 5·6·6·hl2, EMERGING.
DB was out of spec (s15r k3·10·12·close, s30r k5·6·6·close). Aligns to lp_cascade_spec ("r-lines 5|6|6;
s15r/s30r src=hl2"). Versioned via ic_live_after_dt. Idempotent — skips a line already at spec.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

db = DatabaseManager(**get_db_config()); db.connect()
IS_S, IL_R, EMERG, HI, LO = 2, 6, 2, 85.0, 15.0           # s-series · r line · emerging · 85/15
TARGETS = [('s15r', 2), ('s30r', 3)]                      # (name, itf_pk): itf 2=15s, 3=30s


def live(name):
    r = db.execute("SELECT ic_line_type,ic_src,ic_k_len,ic_rsi_len,ic_stc_len,value_mode "
                   "FROM pk_optimizer.vw_indicator_configs_live WHERE ind_name=%s", (name,), fetch=True)
    return r[0] if r else None


for name, itf in TARGETS:
    m = live(name)
    if m and m['ic_line_type'] == 'k' and int(m['ic_k_len']) == 5 and int(m['ic_rsi_len']) == 6 \
            and int(m['ic_stc_len']) == 6 and m['ic_src'] == 'hl2' and m['value_mode'] == 'emerging':
        print('%s  already at spec' % name); continue
    db.execute('''INSERT INTO indicator_configs (ic_is_pk,ic_il_pk,ic_itf_pk,ic_line_type,ic_live_after_dt,ic_src,
        ic_high_boundary,ic_low_boundary,ic_bb_len,ic_bb_mult,ic_k_len,ic_rsi_len,ic_stc_len,ic_ivm_pk,ic_wobble)
        VALUES (%s,%s,%s,'k',(CURDATE()-INTERVAL 1 DAY),'hl2',%s,%s,NULL,NULL,5,6,6,%s,NULL)''',
        (IS_S, IL_R, itf, HI, LO, EMERG))
    print('%s  re-spec (k 5·6·6·hl2, emerging)' % name)

print('--- r-lines live now ---')
for name, _ in TARGETS:
    print(' %-6s %s' % (name, live(name)))
db.disconnect()
