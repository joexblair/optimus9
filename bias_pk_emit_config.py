"""
bias_pk_emit_config.py — emit one window's pine for a chosen bias-machine config, via the engine.

Config here = the real-1% leader: trigger 12 · exit 12 (s{etf}m+r) · gate oob · hard stop 1.0%.
Layers: pk UPDATE labels (BULL/BEAR/NEUT) + entry arrows (green up/below = long, red down/above
= short). size.small (no tiny). Picks the window whose end matches TARGET_DD.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.bl_detect import BLDetect
import bias_machine as bm

TRIG, EXIT_TF, GATE, STOP, TARGET_DD = 12, 12, 'oob', 1.0, '0607'
H = bm.H
def dd(t): return dtm.datetime.fromtimestamp(t / 1000, timezone.utc).strftime('%m%d')
def dts(t): return dtm.datetime.fromtimestamp(t / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M')

db = DatabaseManager(**get_db_config()); db.connect()
det = BLDetect(db, lookback_hours=168, warmup_hours=80); tp = det._tp
rng = db.execute(f'SELECT MIN(kc_timestamp) mn, MAX(kc_timestamp) mx FROM kline_collection WHERE kc_tp_pk={tp}', fetch=True)[0]
earliest, latest = int(rng['mn']), int(rng['mx'])
ends = []; e = latest
while e - (168 + 80) * H >= earliest:
    ends.append(e); e -= 120 * H
ends.reverse()
end = next(x for x in ends if dd(x) == TARGET_DD)

W = bm.BiasWindow(db, end); db.disconnect()
bclose = W.base['close'].to_numpy()
ups = W.ups(W.trigs(TRIG), GATE)
d = W.tf(EXIT_TF)
trades = W.run(ups, [d['m_sign'], d['r_sign']], stop=STOP)
# attach px at pk-update bar for label placement
for u in ups:
    u['px'] = round(float(bclose[W._at(u['t'])]), 5)

nb = sum(u['call'] == 'BULL' for u in ups); nr = sum(u['call'] == 'BEAR' for u in ups); nn = sum(u['call'] == 'NEUT' for u in ups)
net = sum(t['pnl'] for t in trades); wins = sum(t['pnl'] > 0 for t in trades); nstop = sum(t['mae'] <= -STOP for t in trades)
print(f'window {dts(W.W0)} → {dts(W.W1)}  (end {TARGET_DD})')
print(f'config: trig{TRIG} · exit{EXIT_TF} · {GATE} · stop {STOP}%')
print(f'  pk updates: {len(ups)} ({nb} BULL / {nr} BEAR / {nn} NEUT)')
print(f'  trades: {len(trades)} · {wins} wins · {nstop} stopped · net ${net:+.0f}')

arr = lambda v: 'array.from(' + ', '.join(v) + ')'
title = f'pk+trades trig{TRIG} exit{EXIT_TF} {GATE} stop{STOP} ({TARGET_DD})'
body = f'''//@version=5
// {title} — EMITTED via bias_machine.py. pk labels + entry arrows (green=long, red=short).
indicator("{title}", overlay = true, max_labels_count = 500)
// pk updates
t   = {arr([str(u['t']) for u in ups])}
pxv = {arr([f"{u['px']:.5f}" for u in ups])}
cl  = {arr(['"' + u['call'] + '"' for u in ups])}
sd  = {arr(['"' + ('HI' if u['side'] == 1 else 'LO') + '"' for u in ups])}
anc = {arr([f"{u['anc']:.1f}" for u in ups])}
flt = {arr([f"{u['flt']:.1f}" for u in ups])}
// entries
et  = {arr([str(x['et']) for x in trades])}
ed  = {arr(['1' if x['bd'] == 1 else '-1' for x in trades])}
var bool done = false
if barstate.islast and not done
    done := true
    for i = 0 to array.size(t) - 1
        c   = array.get(cl, i)
        col = c == "BULL" ? color.new(color.green, 0) : c == "BEAR" ? color.new(color.red, 0) : color.new(color.gray, 0)
        ar  = c == "BULL" ? "▲BULL" : c == "BEAR" ? "▼BEAR" : "■NEUT"
        label.new(array.get(t, i), array.get(pxv, i), ar + " " + array.get(sd, i) + "\\na" + str.tostring(array.get(anc, i), "#.0") + " f" + str.tostring(array.get(flt, i), "#.0"), xloc = xloc.bar_time, yloc = yloc.price, style = label.style_label_down, color = col, textcolor = color.white, size = size.small)
    for i = 0 to array.size(et) - 1
        isL = array.get(ed, i) == 1
        label.new(array.get(et, i), 0.0, "", xloc = xloc.bar_time, yloc = isL ? yloc.belowbar : yloc.abovebar, style = isL ? label.style_arrowup : label.style_arrowdown, color = isL ? color.new(color.lime, 0) : color.new(color.red, 0), size = size.small)
'''
path = '/home/joe/thecodes/bias_pk_config.pine'
open(path, 'w').write(body)
print(f'→ {path}')
