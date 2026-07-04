"""
seed_ic_working.py (Joe 0704) — load the WORKING lp-cascade configs into indicator_configs, all EMERGING
(causal). Fixes: s2/3/4m/M + s3r/s4r were 'closed' (look-ahead); s2M → 60s; m-lines len 6 (s5m=8); s7m/s7M
new mults (10·0.50 / 37·0.74). Versioned via ic_live_after_dt. Idempotent (skips a line already at spec).
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

db = DatabaseManager(**get_db_config()); db.connect()
IS_S, EMERG, HI, LO = 2, 2, 85.0, 15.0
IL = {'m': 1, 'M': 2}                                         # line suffix → il pk
# WORKING bb lines: ind_name → (itf_pk, bb_len, bb_mult, src).  s2M → itf 4 (60s).
WORKING = {'s2m': (21, 6, 0.56, 'close'), 's3m': (15, 6, 0.56, 'close'), 's4m': (5, 6, 0.56, 'close'), 's5m': (22, 8, 0.40, 'ohlc4'),
           's2M': (4, 37, 0.72, 'hlcc4'), 's3M': (15, 37, 0.72, 'ohlc4'), 's4M': (5, 37, 0.72, 'ohlc4'), 's5M': (22, 37, 0.83, 'ohlc4'),
           's7m': (23, 10, 0.50, 'ohlc4'), 's7M': (23, 37, 0.74, 'ohlc4'),
           's15m': (2, 7, 0.74, 'hlcc4'), 's15M': (2, 37, 0.83, 'ohlc4'), 's30m': (3, 10, 0.60, 'hlc3'), 's30M': (3, 37, 0.83, 'ohlc4')}
FLIP = ['s3r', 's4r']                                         # k-lines: vm → emerging, keep config


def live(name):
    r = db.execute("SELECT ic_line_type,ic_src,ic_bb_len,ic_bb_mult,ic_k_len,ic_rsi_len,ic_stc_len,itf_seconds,value_mode "
                   "FROM vw_indicator_configs_live WHERE ind_name=%s", (name,), fetch=True)
    return r[0] if r else None


def cur_ic(name):
    p = db.execute("SELECT ic_pk FROM pk_optimizer.vw_indicator_configs_live WHERE ind_name=%s", (name,), fetch=True)[0]['ic_pk']
    return db.execute("SELECT ic_k_len,ic_rsi_len,ic_stc_len,ic_src,ic_line_type,ic_itf_pk FROM indicator_configs WHERE ic_pk=%s", (p,), fetch=True)[0]


def ins(il, itf, lt, src, bb_len, bb_mult, k_len, rsi, stc):
    db.execute('''INSERT INTO indicator_configs (ic_is_pk,ic_il_pk,ic_itf_pk,ic_line_type,ic_live_after_dt,ic_src,
        ic_high_boundary,ic_low_boundary,ic_bb_len,ic_bb_mult,ic_k_len,ic_rsi_len,ic_stc_len,ic_ivm_pk,ic_wobble)
        VALUES (%s,%s,%s,%s,(CURDATE()-INTERVAL 1 DAY),%s,%s,%s,%s,%s,%s,%s,%s,%s,NULL)''',
        (IS_S, il, itf, lt, src, HI, LO, bb_len, bb_mult, k_len, rsi, stc, EMERG))


for name, (itf, bl, bm_, src) in WORKING.items():
    m = live(name)
    if m and m['ic_line_type'] == 'bb' and int(m['ic_bb_len']) == bl and float(m['ic_bb_mult']) == bm_ \
            and m['ic_src'] == src and int(m['itf_seconds']) == db.execute("SELECT itf_seconds s FROM indicator_timeframes WHERE itf_pk=%s", (itf,), fetch=True)[0]['s'] \
            and m['value_mode'] == 'emerging':
        print('%-5s ok' % name); continue
    ins(IL[name[-1]], itf, 'bb', src, bl, bm_, None, None, None); print('%-5s seeded (bb %d·%s·%s emerging)' % (name, bl, bm_, src))

for name in FLIP:
    m = live(name)
    if m and m['value_mode'] == 'emerging':
        print('%-5s ok' % name); continue
    c = cur_ic(name)
    ins(6, c['ic_itf_pk'], c['ic_line_type'], c['ic_src'], None, None, c['ic_k_len'], c['ic_rsi_len'], c['ic_stc_len'])
    print('%-5s vm→emerging' % name)

print('\n--- verify: any non-emerging cascade line? ---')
for n in list(WORKING) + FLIP + ['s2r', 's5r', 's7r', 's15r', 's30r', 'gcs5M', 'gcs5m', 'gcs5r']:
    v = live(n)
    print(' %-6s %s vm=%s' % (n, ('bb %s·%s·%s' % (v['ic_bb_len'], v['ic_bb_mult'], v['ic_src'])) if v['ic_line_type'] == 'bb' else ('k %s·%s·%s·%s' % (v['ic_k_len'], v['ic_rsi_len'], v['ic_stc_len'], v['ic_src'])), v['value_mode']) + ('  <== NOT EMERGING' if v['value_mode'] != 'emerging' else ''))
db.disconnect()
