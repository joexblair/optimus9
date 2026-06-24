"""
pine_wins_emit.py (Joe 0625) — re-framed WINS pine. The osc-stream's WINNING s3-cascade flips
(hit +0.9) in the current window (0611 00:00 -> 0618 00:00), coloured green = CLEAN (MAE shallower
than 0.5) / red = DEEP (dived past -0.5 before winning). Each label lists the LP lines that were
OOB-same-side within W=792 at the flip + their values, plus the realised MAE. Loose stop
(mae_allow=2.0) so the true win-MAE shows.

  python3 pine_wins_emit.py        # s3m (osc=s3m, trig s6m)
  python3 pine_wins_emit.py s6m    # s6m self-triggered (osc_from_trigger @ TF6)
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from bias_machine import _sign

STREAM = sys.argv[1] if len(sys.argv) > 1 else 's3m'
CFG = {'s3m': dict(osc='s3m', trigger_tf=6),
       's6m': dict(osc='s12m', trigger_tf=6, osc_from_trigger=True)}[STREAM]   # s6m = self-triggered GEN_M@TF6
def ms(dt): return int(dt.replace(tzinfo=timezone.utc).timestamp() * 1000)
def dts(t): return dtm.datetime.fromtimestamp(t / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M')
W = 792
R1 = ms(dtm.datetime(2026, 6, 18, 0, 0)); R0 = R1 - 168 * bm.H

db = DatabaseManager(**get_db_config()); db.connect()
lines = [r['ind_name'] for r in db.execute("SELECT ind_name FROM vw_indicator_configs_live WHERE itf_seconds>=180 AND ind_name REGEXP '[a-z]+[0-9]+[mMr]$'", fetch=True) if r['ind_name'] != 's3m']
cfg = bm.BiasConfig(gate='oob', entry_order='seq', s3_variant='m', xm45=False, mae=0.4, target=0.9,
                    floater_anchor='last', verdict='pk', trigger_src='hlc3', **CFG)
Wd = bm.BiasWindow(db, R1, cfg=cfg); ts = Wd.ts; n = len(ts); px = Wd.px
pls = {int(p['pk_t']): p for p in Wd.placements(Wd.signals(), 2.0, 0.9, s3_lookback=2) if R0 <= p['pk_t'] < R1}
last = {}; val = {}
for L in lines:
    try: s = _sign(Wd._line(L)); v = Wd._line(L)
    except Exception: continue
    last[L] = {d: np.maximum.accumulate(np.where(s == d, np.arange(n), -1)) for d in (1, -1)}; val[L] = v
labs = []
for u in Wd.signals():
    if u['call'] not in ('BULL', 'BEAR') or not (R0 <= u['t'] < R1): continue
    p = pls.get(int(u['t']))
    if p is None or not p['hit']: continue                     # WINS only
    d = 1 if u['call'] == 'BULL' else -1; j = int(np.searchsorted(ts, int(u['t']))) - 1
    clean = abs(p['mae']) < 0.5
    pres = [L for L in lines if L in last and last[L][d][j] >= 0 and (j - last[L][d][j]) <= W]
    lv = ' '.join(f"{L}{val[L][j]:.0f}" for L in sorted(pres)) or "(none)"
    labs.append((int(u['t']), float(px[j]), f"{lv}\\nmae{p['mae']:+.2f}", clean))
db.disconnect()
nc = sum(1 for *_ , c in labs if c)
print(f"{STREAM}: {len(labs)} WIN flips · {nc} clean (green) / {len(labs) - nc} deep (red) · range {dts(R0)} -> {dts(R1)}")

arr = lambda v: 'array.from(' + ', '.join(v) + ')'
title = f'wins {STREAM} ({dts(R0)[5:10]}->{dts(R1)[5:10]}) green=clean red=deep'
body = f'''//@version=5
indicator("{title}", overlay = true, max_labels_count = 500, max_lines_count = 500)
w_t  = {arr([str(t) for t, py, tx, c in labs])}
w_py = {arr([f"{py:.5f}" for t, py, tx, c in labs])}
w_tx = {arr(['"' + tx + '"' for t, py, tx, c in labs])}
w_cl = {arr(['1' if c else '0' for t, py, tx, c in labs])}
var bool done = false
if barstate.islast and not done
    done := true
    for i = 0 to array.size(w_t) - 1
        clean = array.get(w_cl, i) == 1
        label.new(array.get(w_t, i), array.get(w_py, i), array.get(w_tx, i), xloc = xloc.bar_time, yloc = yloc.price, style = clean ? label.style_label_up : label.style_label_down, color = clean ? color.new(color.green, 0) : color.new(color.red, 0), textcolor = color.white, size = size.small)
'''
path = f'/home/joe/thecodes/pine_wins_{STREAM}.pine'
open(path, 'w').write(body)
print(f'→ {path}')
