"""
seed_bias_lines.py — put the bias-machine lines into indicator_configs (Joe 0620, "start clean").
Idempotent: ensures series (mo/xm) + the 45s timeframe, then inserts the 12 bias line configs.
s30M/s30r are NEW VERSIONS (live_after 2026-06-20) that supersede the epoch prod rows via the view;
the rest are fresh (series·line·TF) combos. Boundaries default 85/15 = bias OOB. Re-run safe.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import datetime as dtm
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

LIVE_AFTER = '2026-06-20 00:00:00'
# (prefix, suffix, itf_label, itf_seconds, line_type, src, bb_len, bb_mult, rsi_len, stc_len, k_len)
DEFS = [
    ('s',  'm', '12', 720, 'bb', 'hlc3',  10, 0.40, None, None, None),   # s12m  (trigger + osc)
    ('s',  'M', '14', 420, 'bb', 'ohlc4', 74, 0.73, None, None, None),   # s14M  (pk gate)
    ('s',  'm', '14', 420, 'bb', 'hlc3',  20, 0.77, None, None, None),   # s14m
    ('s',  'r', '14', 420, 'k',  'hl2',   None, None, 12, 12, 10),       # s14r
    ('s',  'm', '3',  180, 'bb', 'ohlc4', 10, 0.40, None, None, None),   # s3m   (entry m)
    ('s',  'M', '30', 30,  'bb', 'ohlc4', 37, 0.72, None, None, None),   # s30M  supersedes ic18 (0.83)
    ('s',  'm', '30', 30,  'bb', 'hlc3',  10, 0.40, None, None, None),   # s30m
    ('s',  'r', '30', 30,  'k',  'close', None, None, 6, 6, 5),          # s30r  supersedes ic17 (10|12|3)
    ('mo', 'm', '12', 720, 'bb', 'close', 7, 0.64, None, None, None),    # mo12m
    ('xm', 'm', '45', 45,  'bb', 'ohlc4', 111, 0.99, None, None, None),  # xm45m
    ('xm', 'M', '45', 45,  'bb', 'hlcc4', 222, 0.92, None, None, None),  # xm45M
    ('xm', 'r', '45', 45,  'k',  'close', None, None, 40, 96, 12),       # xm45r
    ('s',  'r', '3',  180, 'k',  'close', None, None, 6, 6, 5),          # s3r  = GEN_R @180 (entry variant r)
    ('s',  'M', '3',  180, 'bb', 'ohlc4', 37, 0.72, None, None, None),   # s3M  = S30M  @180 (entry variant M)
    ('s',  'r', '6',  360, 'k',  'close', None, None, 6, 6, 5),          # s6r  = GEN_R @360 (default osc ruler)
    # s22 — the real bias decider (TF22 = 1320s, closed). s22M mult 0.83 (per M_MULT_BY_TF).
    ('s',  'm', '22', 1320, 'bb', 'hlc3', 10, 0.40, None, None, None),   # s22m
    ('s',  'M', '22', 1320, 'bb', 'ohlc4', 37, 0.83, None, None, None),  # s22M
    ('s',  'r', '22', 1320, 'k',  'hl2',  None, None, 6, 6, 5),          # s22r
    # blp14 — emerging clone of s14 (TF7 = 420s). Same params; built emerging (f_bb_lookahead) by the engine.
    ('blp', 'm', '14', 420, 'bb', 'hlc3', 20, 0.77, None, None, None),   # blp14m  (= s14m)
    ('blp', 'M', '14', 420, 'bb', 'ohlc4', 74, 0.73, None, None, None),  # blp14M  (= s14M)
    ('blp', 'r', '14', 420, 'k',  'hl2',  None, None, 12, 12, 10),       # blp14r  (= s14r)
]

db = DatabaseManager(**get_db_config()); db.connect()
Q = lambda sql, p=None, f=False: db.execute(sql, p or (), fetch=f)


def one(sql, p):
    r = Q(sql, p, True)
    return r[0] if r else None


added = {'series': [], 'itf': [], 'config': [], 'skip': []}
for prefix, suffix, label, seconds, lt, src, bbl, bbm, rsi, stc, kl in DEFS:
    s = one('SELECT is_pk FROM indicator_series WHERE is_prefix=%s', (prefix,))
    if not s:
        Q('INSERT INTO indicator_series (is_prefix) VALUES (%s)', (prefix,)); added['series'].append(prefix)
        s = one('SELECT is_pk FROM indicator_series WHERE is_prefix=%s', (prefix,))
    il = one('SELECT il_pk FROM indicator_lines WHERE il_suffix=%s', (suffix,))
    itf = one('SELECT itf_pk FROM indicator_timeframes WHERE itf_label=%s AND itf_seconds=%s', (label, seconds))
    if not itf:
        Q('INSERT INTO indicator_timeframes (itf_label, itf_seconds) VALUES (%s,%s)', (label, seconds))
        added['itf'].append(f'{label}/{seconds}s')
        itf = one('SELECT itf_pk FROM indicator_timeframes WHERE itf_label=%s AND itf_seconds=%s', (label, seconds))
    is_pk, il_pk, itf_pk = s['is_pk'], il['il_pk'], itf['itf_pk']
    exists = one('''SELECT ic_pk FROM indicator_configs
                    WHERE ic_is_pk=%s AND ic_il_pk=%s AND ic_itf_pk=%s AND ic_live_after_dt=%s''',
                 (is_pk, il_pk, itf_pk, LIVE_AFTER))
    if exists:
        added['skip'].append(f'{prefix}{label}{suffix}'); continue
    Q('''INSERT INTO indicator_configs
         (ic_is_pk, ic_il_pk, ic_itf_pk, ic_line_type, ic_live_after_dt, ic_src,
          ic_bb_len, ic_bb_mult, ic_rsi_len, ic_stc_len, ic_k_len)
         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
      (is_pk, il_pk, itf_pk, lt, LIVE_AFTER, src, bbl, bbm, rsi, stc, kl))
    added['config'].append(f'{prefix}{label}{suffix}')

print('series added :', added['series'] or '—')
print('itf added    :', added['itf'] or '—')
print('configs added:', added['config'] or '—')
print('configs skip :', added['skip'] or '—')
db.disconnect()
