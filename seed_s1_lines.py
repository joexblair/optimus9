"""seed_s1_lines.py (Joe 0706) — seed s1m + s1r into indicator_configs for the s1a-gate test.

s1m = bb 6|0.56|close @60s (il 'm')  ·  s1r = k 5|6|6|close @60s (il 'r')  — both emerging, boundaries 85/15.
Clones s1M's series/timeframe/value-mode pks (is_pk 2, itf_pk 4=60s, ivm_pk 2=emerging). Reads back via
W.line to prove no cfg-tuple malform (the known trap). Idempotent: skips if the config already exists.
"""
import sys, time
sys.path.insert(0, '/home/joe/thecodes')
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from sweep_eval import BASE_BIAS

dev = DatabaseManager(**get_db_config()); dev.connect()

pref = dev.execute("SELECT is_prefix FROM indicator_series WHERE is_pk=2", fetch=True)
print("is_pk=2 prefix =", pref[0]['is_prefix'] if pref else None, "(expect 's')")

# (ind, cols...) — clone s1M pks: is_pk=2, itf_pk=4(60s), ivm_pk=2(emerging)
rows = [
    ('s1m', dict(ic_is_pk=2, ic_itf_pk=4, ic_il_pk=1, ic_line_type='bb', ic_live_after_dt='2026-07-03',
                 ic_src='close', ic_high_boundary=85, ic_low_boundary=15, ic_bb_len=6, ic_bb_mult=0.56,
                 ic_k_len=None, ic_rsi_len=None, ic_stc_len=None, ic_ivm_pk=2, ic_wobble=None)),
    ('s1r', dict(ic_is_pk=2, ic_itf_pk=4, ic_il_pk=6, ic_line_type='k', ic_live_after_dt='2026-07-03',
                 ic_src='close', ic_high_boundary=85, ic_low_boundary=15, ic_bb_len=None, ic_bb_mult=None,
                 ic_k_len=5, ic_rsi_len=6, ic_stc_len=6, ic_ivm_pk=2, ic_wobble=None)),
]
for name, c in rows:
    ex = dev.execute("SELECT ic_pk FROM indicator_configs WHERE ic_is_pk=%s AND ic_itf_pk=%s AND ic_il_pk=%s "
                     "AND ic_line_type=%s AND ic_ivm_pk=%s",
                     (c['ic_is_pk'], c['ic_itf_pk'], c['ic_il_pk'], c['ic_line_type'], c['ic_ivm_pk']), fetch=True)
    if ex:
        print("%s already seeded (ic_pk=%s) — skip" % (name, ex[0]['ic_pk'])); continue
    cols = list(c.keys()); ph = ','.join(['%s'] * len(cols))
    dev.execute("INSERT INTO indicator_configs (%s) VALUES (%s)" % (','.join(cols), ph), tuple(c[k] for k in cols))
    print("%s seeded" % name)

live = dev.execute("SELECT ind_name FROM vw_indicator_configs_live WHERE ind_name IN ('s1m','s1r','s1M') ORDER BY ind_name", fetch=True)
print("live now:", [x['ind_name'] for x in live])

# read back via W.line — sanity: 0..100 range, not all-NaN, OOB near the 07-05 15:01 top
W = bm.BiasWindow(dev, int(time.time() * 1000), lookback=336, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS), lean=True)
ts = np.array(W.ts)
for nm in ('s1M', 's1m', 's1r'):
    v = np.asarray(W.line(nm), float)
    fin = v[~np.isnan(v)]
    print("  %-4s  min=%.1f max=%.1f  nan=%d/%d" % (nm, fin.min(), fin.max(), np.isnan(v).sum(), len(v)))
import calendar
def ms(s): return calendar.timegm(time.strptime(s, '%Y-%m-%d %H:%M:%S')) * 1000
k = int(np.argmin(np.abs(ts - ms('2026-07-05 15:01:00'))))
print("  @07-05 15:01 (near the top):  s1M=%.1f s1m=%.1f s1r=%.1f (expect all OOB-hi >=85)" % (
    W.line('s1M')[k], W.line('s1m')[k], W.line('s1r')[k]))
dev.disconnect()
