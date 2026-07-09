"""seed_st5.py (Joe 0706) — clone the s5 line set to a new 'st' series (st5m/st5M/st5r) for a TF-sweep experiment.

st5* clone s5* exactly (st5m 8|0.40|ohlc4 · st5M 37|0.83|ohlc4 · st5r 5|6|6|close, emerging, 85/15), but point
at a DEDICATED itf (label '5') whose seconds the sweep edits — so real s5 (itf_pk 22) is never touched.
Idempotent: reuses the dedicated itf/series/configs if already present. Reads back via W.line to prove clean.
"""
import sys, time
sys.path.insert(0, '/home/joe/thecodes')
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from sweep_eval import BASE_BIAS

dev = DatabaseManager(**get_db_config()); dev.connect()

# 1) series 'st'
r = dev.execute("SELECT is_pk FROM indicator_series WHERE is_prefix='st'", fetch=True)
if r:
    st_is = r[0]['is_pk']
else:
    dev.execute("INSERT INTO indicator_series (is_prefix) VALUES ('st')")
    st_is = dev.execute("SELECT is_pk FROM indicator_series WHERE is_prefix='st'", fetch=True)[0]['is_pk']
print("series 'st' is_pk =", st_is)

# 2) dedicated itf (label '5') — reuse the one st5M already points at, else create a fresh one
ex = dev.execute("SELECT ic_itf_pk FROM indicator_configs WHERE ic_is_pk=%s AND ic_il_pk=2 AND ic_line_type='bb'",
                 (st_is,), fetch=True)
if ex:
    st_itf = ex[0]['ic_itf_pk']
else:
    dev.execute("INSERT INTO indicator_timeframes (itf_label, itf_seconds) VALUES ('5', 360)")  # 6min; sweep edits secs
    st_itf = dev.execute("SELECT itf_pk FROM indicator_timeframes ORDER BY itf_pk DESC LIMIT 1", fetch=True)[0]['itf_pk']
print("dedicated itf_pk =", st_itf, "(edit its seconds to sweep)")

# 3) clone s5m/s5M/s5r → st5m/st5M/st5r
LINES = [
    dict(il=1, lt='bb', src='ohlc4', bb_len=8,  bb_mult=0.40, k=None, rsi=None, stc=None),  # st5m
    dict(il=2, lt='bb', src='ohlc4', bb_len=37, bb_mult=0.83, k=None, rsi=None, stc=None),  # st5M
    dict(il=6, lt='k',  src='close', bb_len=None, bb_mult=None, k=5,  rsi=6,  stc=6),        # st5r
]
for L in LINES:
    e = dev.execute("SELECT ic_pk FROM indicator_configs WHERE ic_is_pk=%s AND ic_itf_pk=%s AND ic_il_pk=%s "
                    "AND ic_line_type=%s AND ic_ivm_pk=2", (st_is, st_itf, L['il'], L['lt']), fetch=True)
    if e:
        print("  il %d already seeded (ic_pk=%s)" % (L['il'], e[0]['ic_pk'])); continue
    dev.execute("INSERT INTO indicator_configs (ic_is_pk,ic_itf_pk,ic_il_pk,ic_line_type,ic_live_after_dt,ic_src,"
                "ic_high_boundary,ic_low_boundary,ic_bb_len,ic_bb_mult,ic_k_len,ic_rsi_len,ic_stc_len,ic_ivm_pk,ic_wobble)"
                " VALUES (%s,%s,%s,%s,'2026-07-03',%s,85,15,%s,%s,%s,%s,%s,2,NULL)",
                (st_is, st_itf, L['il'], L['lt'], L['src'], L['bb_len'], L['bb_mult'], L['k'], L['rsi'], L['stc']))
    print("  il %d seeded" % L['il'])

live = dev.execute("SELECT ind_name, itf_seconds FROM vw_indicator_configs_live WHERE ind_name IN "
                   "('st5m','st5M','st5r') ORDER BY ind_name", fetch=True)
print("live:", {x['ind_name']: x['itf_seconds'] for x in live})

# read-back via W.line — sane range + not-NaN proves no cfg-tuple malform (clone is s5's exact bb config, only TF differs)
W = bm.BiasWindow(dev, int(time.time() * 1000), lookback=336, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS), lean=True)
for nm in ('s5M', 'st5M', 'st5m', 'st5r'):
    v = np.asarray(W.line(nm), float); fin = v[~np.isnan(v)]
    print("  %-5s min=%.1f max=%.1f nan=%d/%d" % (nm, fin.min(), fin.max(), np.isnan(v).sum(), len(v)))
dev.disconnect()
