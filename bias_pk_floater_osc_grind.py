"""
bias_pk_floater_osc_grind.py — test the bias_review_notes ideas across the windows (Joe 0619).

Two axes, from the 0612 06:00 review note:
  • osc     {s12m (current) · mo12m = BB 7|0.64|close}   — anchor/floater value source only;
            the TRIGGER stays s12m reversal (trigs(12) reads GEN_M@TF12 regardless of _osc).
  • floater {fixed±2 (current min/max scan) · disabled}  — disabled = flt_half=0, i.e. no scan,
            floater = raw osc value at g[S]'s bar (the prior same-side reversal). "no fallback,
            just capture the in-test oscillator value at the moment of s12m's reversal."
= 4 configs. Entry held at the cascade winner seq/m/xm45-off. Scores placement (MAE 0.4 / target 0.9)
per window; baseline cell (s12m·fixed) must reproduce the existing seq/m ~43% or something differs.
Same window generator as bias_pk_cascade_grind.py so rows are directly comparable. Writes bias_pk_flosc.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.bl_detect import BLDetect
import bias_machine as bm

H = bm.H; MAE, TARGET, FLOOR = 0.4, 0.9, 120
def dd(t): return dtm.datetime.fromtimestamp(t / 1000, timezone.utc).strftime('%m%d')
# (osc_label, line_cfg, flt_label, flt_half)
OSCS = [('s12m', bm.GEN_M), ('mo12m', bm.MO12m)]
FLTS = [('fixed', 2), ('disabled', 0)]
CFGS = [(ol, oc, fl, fh) for (ol, oc) in OSCS for (fl, fh) in FLTS]

db = DatabaseManager(**get_db_config()); db.connect()
det = BLDetect(db, lookback_hours=168, warmup_hours=80); tp = det._tp
rng = db.execute(f'SELECT MIN(kc_timestamp) mn, MAX(kc_timestamp) mx FROM kline_collection WHERE kc_tp_pk={tp}', fetch=True)[0]
earliest, latest = int(rng['mn']), int(rng['mx'])
ends = []; e = latest
while e - (168 + 80) * H >= earliest:
    ends.append(e); e -= 120 * H
ends.reverse()
print(f'{len(ends)} windows · {len(CFGS)} configs (osc × floater) · trigger s12m · entry seq/m/xm45-off')

res = {(ol, fl): [] for (ol, oc, fl, fh) in CFGS}; win_ends = []
db2 = DatabaseManager(**get_db_config()); db2.connect()
for wi, end in enumerate(ends):
    W = bm.BiasWindow(db2, end); win_ends.append(W.W1)
    W.set_entry('seq', 'm', False)
    for (ol, oc, fl, fh) in CFGS:
        W.set_osc(W._aligned(720, oc), 144)            # osc swap (trigger still s12m via trigs(12))
        ups = W.ups(W.trigs(12), 'oob', flt_half=fh)   # flt_half=0 ⇒ floater = raw osc at g[S], no scan
        pls = W.placements(ups, MAE, TARGET)
        res[(ol, fl)].append((sum(p['hit'] for p in pls), len(pls)))
    print(f'  window {wi+1}/{len(ends)} → {dd(W.W1)} done')
db2.disconnect()

rows = []
for (ol, oc, fl, fh) in CFGS:
    for wi, (cc, n) in enumerate(res[(ol, fl)]):
        rows.append([dtm.datetime.fromtimestamp(win_ends[wi]/1000, timezone.utc).strftime('%Y-%m-%d %H:%M'),
                     ol, fl, cc, n])
db.execute('DROP TABLE IF EXISTS bias_pk_flosc')
db.execute('''CREATE TABLE bias_pk_flosc (pk BIGINT AUTO_INCREMENT PRIMARY KEY, window_end DATETIME,
    osc VARCHAR(8), floater VARCHAR(10), correct INT, total INT)''')
db.executemany('INSERT INTO bias_pk_flosc (window_end,osc,floater,correct,total) VALUES (%s,%s,%s,%s,%s)', rows)
db.disconnect()

print(f'\nLEADERBOARD — rolled placement rate ({len(ends)} windows):')
print(f'  {"osc":>6} {"floater":>9} | {"rate":>5} {"correct":>7} {"trades":>6} {">=40% wins":>10}')
lb = []
for (ol, fl) in res:
    cc = sum(x[0] for x in res[(ol, fl)]); nn = sum(x[1] for x in res[(ol, fl)])
    posw = sum(1 for (a, b) in res[(ol, fl)] if b and a / b >= 0.40)
    lb.append((cc / nn if nn else 0, cc, nn, posw, ol, fl))
for rate, cc, nn, posw, ol, fl in sorted(lb, reverse=True):
    flag = '  ← baseline' if (ol, fl) == ('s12m', 'fixed') else ''
    print(f'  {ol:>6} {fl:>9} | {rate:>5.0%} {cc:>7} {nn:>6} {posw:>3}/{len(ends)}{flag}')
print(f'\n→ db table bias_pk_flosc ({len(rows)} rows)')
