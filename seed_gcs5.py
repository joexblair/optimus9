"""
seed_gcs5.py (Joe 0704) — add gcs5M (was missing) + re-spec gcs5m/gcs5r to the gcs5 finisher spec (#47).
gcs5 = 5s fast finisher clone:  m bb 10·0.60·hlc3 · M bb 37·0.70·ohlc4 · r k 5·6·6·hl2 · bnd 85/15 · emerging.
Versioned via ic_live_after_dt (CURDATE()-1 DAY). Idempotent — skips a line whose live config already matches.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

db = DatabaseManager(**get_db_config()); db.connect()
IS_GCS, ITF5, EMERG, HI, LO = 6, 1, 2, 85.0, 15.0          # series=gcs · itf=5s · ivm=emerging · 85/15
IL = {'m': 1, 'M': 2, 'r': 6}                              # line pks: m/M/r


def live(name):
    r = db.execute("SELECT ic_line_type,ic_src,ic_bb_len,ic_bb_mult,ic_k_len,ic_rsi_len,ic_stc_len "
                   "FROM pk_optimizer.vw_indicator_configs_live WHERE ind_name=%s", (name,), fetch=True)
    return r[0] if r else None


def ins(il, line_type, src, bb_len, bb_mult, k_len, rsi_len, stc_len):
    db.execute('''INSERT INTO indicator_configs (ic_is_pk,ic_il_pk,ic_itf_pk,ic_line_type,ic_live_after_dt,ic_src,
        ic_high_boundary,ic_low_boundary,ic_bb_len,ic_bb_mult,ic_k_len,ic_rsi_len,ic_stc_len,ic_ivm_pk,ic_wobble)
        VALUES (%s,%s,%s,%s,(CURDATE()-INTERVAL 1 DAY),%s,%s,%s,%s,%s,%s,%s,%s,%s,NULL)''',
        (IS_GCS, il, ITF5, line_type, src, HI, LO, bb_len, bb_mult, k_len, rsi_len, stc_len, EMERG))


def eqbb(m, ln, mult, src):
    return m and m['ic_line_type'] == 'bb' and int(m['ic_bb_len']) == ln and float(m['ic_bb_mult']) == mult and m['ic_src'] == src


def eqk(m, k, rsi, stc, src):
    return m and m['ic_line_type'] == 'k' and int(m['ic_k_len']) == k and int(m['ic_rsi_len']) == rsi and int(m['ic_stc_len']) == stc and m['ic_src'] == src


if not eqbb(live('gcs5M'), 37, 0.70, 'ohlc4'):
    ins(IL['M'], 'bb', 'ohlc4', 37, 0.70, None, None, None); print('gcs5M  inserted (bb 37·0.70·ohlc4)')
else: print('gcs5M  already at spec')
if not eqbb(live('gcs5m'), 10, 0.60, 'hlc3'):
    ins(IL['m'], 'bb', 'hlc3', 10, 0.60, None, None, None); print('gcs5m  re-spec (bb 10·0.60·hlc3)')
else: print('gcs5m  already at spec')
if not eqk(live('gcs5r'), 5, 6, 6, 'hl2'):
    ins(IL['r'], 'k', 'hl2', None, None, 5, 6, 6); print('gcs5r  re-spec (k 5·6·6·hl2)')
else: print('gcs5r  already at spec')

print('--- gcs5 live now ---')
for n in ('gcs5m', 'gcs5M', 'gcs5r'):
    print(' %-7s %s' % (n, live(n)))
db.disconnect()
