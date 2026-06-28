"""
cf15_pine_emit.py (Joe 0628) — paint the cf15_walk trades on TradingView as bgcolors, so the clean
winners read separately from the >0.5%-MAE drawdowns, split by direction:

  WON    (mfe >= WON_TARGET  AND  mae <= MAE_LIMIT) → green (long) / red  (short)
  RISKY  (mae >  MAE_LIMIT, takes PRIORITY)         → yellow(long) / blue (short)   # drew past 0.5%, won or not
  scratch (neither) → uncoloured

Thresholds are params (no hardcode): default WON_TARGET=0.7 (the costed-edge target), MAE_LIMIT=0.5.
Time match is bar-containment, so it paints whatever chart TF you load it on.

  python3 cf15_pine_emit.py            # 0.7 / 0.5
  python3 cf15_pine_emit.py 0.9 0.5    # WON_TARGET MAE_LIMIT
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

WON_TARGET = float(sys.argv[1]) if len(sys.argv) > 1 else 0.7
MAE_LIMIT = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5

db = DatabaseManager(**get_db_config()); db.connect()
rows = db.execute('SELECT trade_ms, trade_dir, mae, mfe FROM cf15_walk ORDER BY trade_ms', fetch=True)
db.disconnect()

# colour index: 0 green=WON long · 1 red=WON short · 2 yellow=RISKY long · 3 blue=RISKY short
ts, ci = [], []
n_won = n_risky = n_scratch = 0
for r in rows:
    d = int(r['trade_dir'])                     # +1 long / -1 short
    mae, mfe = float(r['mae']), float(r['mfe'])
    if mae > MAE_LIMIT:                          # RISKY first — the >0.5% drawdown is the risk view, won or not
        c = 2 if d > 0 else 3; n_risky += 1
    elif mfe >= WON_TARGET:                      # clean WON
        c = 0 if d > 0 else 1; n_won += 1
    else:
        n_scratch += 1; continue                # scratch — uncoloured
    ts.append(int(r['trade_ms'])); ci.append(c)

arr = lambda v: 'array.from(' + ', '.join(map(str, v)) + ')'
title = (f'cf15 trades  WON(mfe>={WON_TARGET}) green/red=long/short  RISKY(mae>{MAE_LIMIT}) yellow/blue=long/short')
body = f'''//@version=5
indicator("{title}", overlay = true)
t_arr  = {arr(ts)}
ci_arr = {arr(ci)}
dur = timeframe.in_seconds() * 1000
bg = color(na)
for i = 0 to array.size(t_arr) - 1
    tt = array.get(t_arr, i)
    if tt >= time and tt < time + dur
        cidx = array.get(ci_arr, i)
        bg := cidx == 0 ? color.new(color.green, 0) : cidx == 1 ? color.new(color.red, 0) : cidx == 2 ? color.new(color.yellow, 0) : color.new(color.blue, 0)
        break
bgcolor(bg)
'''
path = '/home/joe/thecodes/cf15_trades.pine'
open(path, 'w').write(body)
print(f'cf15_walk: {len(rows)} trades → {n_won} WON (green/red) · {n_risky} RISKY mae>{MAE_LIMIT} (yellow/blue) · {n_scratch} scratch')
print(f'→ {path}')
