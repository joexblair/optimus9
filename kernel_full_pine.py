"""
kernel_full_pine.py (Joe 0630) — combined overlay: the kernel_walk trade bgcolors (WON green/red · RISKY
yellow/blue) PLUS the bro-cross bias (hb33 sets) as a thin line — red over the candles when bias==-1, green
under when bias==+1. Reads kernel_walk + kernel_bias (written by lr_kernel_walk.py). Bias is visual only.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

WON_TARGET, MAE_LIMIT = 0.7, 0.5
db = DatabaseManager(**get_db_config()); db.connect()
trades = db.execute('SELECT trade_ms, trade_dir, mae, mfe FROM kernel_walk ORDER BY trade_ms', fetch=True)
flips = db.execute('SELECT flip_ms, dir FROM kernel_bias ORDER BY flip_ms', fetch=True)
db.disconnect()

ts, ci = [], []
for r in trades:
    d = int(r['trade_dir']); mae, mfe = float(r['mae']), float(r['mfe'])
    if mae > MAE_LIMIT:
        c = 2 if d > 0 else 3
    elif mfe >= WON_TARGET:
        c = 0 if d > 0 else 1
    else:
        continue
    ts.append(int(r['trade_ms'])); ci.append(c)
ft = [int(f['flip_ms']) for f in flips]; fd = [int(f['dir']) for f in flips]

arr = lambda v: 'array.from(' + ', '.join(map(str, v)) + ')'
body = f'''//@version=5
indicator("kernel trades + bro-cross bias (hb33)", overlay = true)
t_arr  = {arr(ts)}
ci_arr = {arr(ci)}
ft_arr = {arr(ft)}
fd_arr = {arr(fd)}
dur = timeframe.in_seconds() * 1000
bg = color(na)
for i = 0 to array.size(t_arr) - 1
    tt = array.get(t_arr, i)
    if tt >= time and tt < time + dur
        cidx = array.get(ci_arr, i)
        bg := cidx == 0 ? color.new(color.green, 0) : cidx == 1 ? color.new(color.red, 0) : cidx == 2 ? color.new(color.yellow, 0) : color.new(color.blue, 0)
        break
bgcolor(bg)
var int bias = 0
for i = 0 to array.size(ft_arr) - 1
    fm = array.get(ft_arr, i)
    if fm >= time and fm < time + dur
        bias := array.get(fd_arr, i)
plot(bias == -1 ? high * 1.003 : na, color = color.new(color.red, 0), style = plot.style_linebr, linewidth = 1, title = "bro bias -1")
plot(bias ==  1 ? low  * 0.997 : na, color = color.new(color.green, 0), style = plot.style_linebr, linewidth = 1, title = "bro bias +1")
'''
path = '/home/joe/thecodes/kernel_full.pine'
open(path, 'w').write(body)
print(f'kernel_full: {len(trades)} trades · {len(flips)} bro-cross(hb33) flips → {path}')
db.disconnect() if False else None
