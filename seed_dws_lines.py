"""seed_dws_lines.py — the `dws` series: dws8r, dws10r, dws15r. Joe 1012.

Joe 1012: *"create a new ic series labelled `dws`, and create dws[8,10,15]r. the r config will be
doubled so that we build more granular TF16, TF20, and TF30 r lines"* / *"double all three lengths,
emerging"*.

THE SHAPE. A dws{N}r line keeps ws{N}r's TIMEFRAME and doubles its three k-line lengths, so it is
sampled on the ws{N} grid but smoothed like a ws{2N} line - Joe's "more granular TF16/TF20/TF30".
Doubling itf_seconds instead would just reproduce ws16r/ws20r/ws30r and would not be more granular.

  ws8r   itf_pk 24, label '8',  480 s   k 7 rsi 5 stc 8   ->  dws8r   same itf, k 14 rsi 10 stc 16
  ws10r  itf_pk 28, label '10', 600 s   k 7 rsi 5 stc 8   ->  dws10r  same itf, k 14 rsi 10 stc 16
  ws15r  itf_pk  9, label '15', 900 s   k 7 rsi 5 stc 8   ->  dws15r  same itf, k 14 rsi 10 stc 16

A NEW SERIES ROW IS NEEDED. `ind_name` is composed from the series prefix + the timeframe label +
the line suffix, so 'dws' must exist in indicator_series before the configs can resolve to a name.
is_pk 17 is 'ws' and 18 is 'gcws'; the next free pk is 19.

value_mode `emerging` = ic_ivm_pk 2, Joe's ruling and the causal one. `closed` would be lookahead.

WATCH THE itf TABLE. indicator_timeframes has DUPLICATE seconds with different labels - itf_pk 27
is label '5' at 600 s and itf_pk 28 is label '10' at 600 s; itf_pk 14 is label '9' at 900 s and
itf_pk 9 is label '15' at 900 s. The LABEL makes the name, so the pk is taken from ws{N}r's own row
rather than looked up by seconds.

    python3 seed_dws_lines.py            # DRY RUN, prints the rows and writes nothing
    python3 seed_dws_lines.py --commit   # inserts
"""
import sys
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

COMMIT = '--commit' in sys.argv
PREFIX = 'dws'
SRC_LINES = ['ws8r', 'ws10r', 'ws15r']
MULT = 2                      # Joe 1012: "double all three lengths"
IVM_EMERGING = 2
LIVE_AFTER = None             # set from the source line's own ic_live_after_dt

db = DatabaseManager(**get_db_config()); db.connect()

def src_row(name):
    return db.execute(
        "SELECT c.* FROM indicator_configs c JOIN vw_indicator_configs_live v ON v.ic_pk=c.ic_pk "
        "WHERE v.ind_name=%s", (name,), fetch=True)[0]

ser = db.execute("SELECT is_pk FROM pk_optimizer.indicator_series WHERE is_prefix=%s",
                 (PREFIX,), fetch=True)
if ser:
    is_pk = ser[0]['is_pk']
    print('# indicator_series: %r already exists at is_pk %d' % (PREFIX, is_pk))
else:
    nxt = db.execute("SELECT COALESCE(MAX(is_pk),0)+1 n FROM pk_optimizer.indicator_series",
                     fetch=True)[0]['n']
    is_pk = int(nxt)
    print('# indicator_series: INSERT is_pk %d, is_prefix %r' % (is_pk, PREFIX))
    if COMMIT:
        db.execute("INSERT INTO pk_optimizer.indicator_series (is_pk,is_prefix) VALUES (%s,%s)",
                   (is_pk, PREFIX))

print()
print('| the new line | is_pk | itf_pk | il_pk | type | src | hi | lo | k_len | rsi_len | stc_len | ivm | live_after |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|---|')
plan = []
for nm in SRC_LINES:
    s = src_row(nm)
    new = 'd' + nm
    row = dict(is_pk=is_pk, itf_pk=s['ic_itf_pk'], il_pk=s['ic_il_pk'],
               lt=s['ic_line_type'], src=s['ic_src'],
               hi=s['ic_high_boundary'], lo=s['ic_low_boundary'],
               k=int(s['ic_k_len']) * MULT, r=int(s['ic_rsi_len']) * MULT,
               stc=int(s['ic_stc_len']) * MULT, ivm=IVM_EMERGING,
               live=s['ic_live_after_dt'])
    plan.append((new, row))
    print('| %s | %d | %d | %d | %s | %s | %s | %s | **%d** | **%d** | **%d** | %d | %s |'
          % (new, row['is_pk'], row['itf_pk'], row['il_pk'], row['lt'], row['src'],
             row['hi'], row['lo'], row['k'], row['r'], row['stc'], row['ivm'],
             row['live'].strftime('%Y-%m-%d')))

print()
if not COMMIT:
    print('# DRY RUN — nothing was written. Re-run with --commit to insert.')
else:
    for new, r in plan:
        db.execute('''INSERT INTO indicator_configs
            (ic_is_pk,ic_il_pk,ic_itf_pk,ic_line_type,ic_live_after_dt,ic_src,
             ic_high_boundary,ic_low_boundary,ic_bb_len,ic_bb_mult,
             ic_k_len,ic_rsi_len,ic_stc_len,ic_ivm_pk,ic_wobble)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,NULL,NULL,%s,%s,%s,%s,NULL)''',
            (r['is_pk'], r['il_pk'], r['itf_pk'], r['lt'], r['live'], r['src'],
             r['hi'], r['lo'], r['k'], r['r'], r['stc'], r['ivm']))
        print('%-8s inserted' % new)
    print()
    print('# verify through the live view:')
    for new, _ in plan:
        v = db.execute("SELECT ind_name,ic_line_type,ic_src,ic_k_len,ic_rsi_len,ic_stc_len,"
                       "itf_seconds,value_mode FROM vw_indicator_configs_live WHERE ind_name=%s",
                       (new,), fetch=True)
        print('  ', v[0] if v else '%s NOT VISIBLE in the view' % new)
    print()
    print('# next: python3 -m optimus9.orchestration.build_ws_lines --prefix dws')
db.disconnect()
