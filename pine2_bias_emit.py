"""
pine2_bias_emit.py (Joe 0625) — two-stream bias emit: s3m + s12maj bias updates on the same chart,
for the current window (0611 00:00 → 0618 00:00). Each stream = its pk update labels (call · side ·
a{anchor} f{floater}) + a dashed anchor→floater line, colour-separated (s3m aqua / s12maj orange).
NO trades — just the bias guidance, so you can eyeball where each fires. Models alchemy_snf_emit.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import datetime as dtm
from datetime import timezone
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm

STREAMS = {  # name: osc line · trigger TF · colour · label style (s3m below bar / s12maj above)
    's3m':    dict(osc='s3m', tf=6,  color='color.aqua',   style='label.style_label_down'),
    's12maj': dict(osc='s12M', tf=12, color='color.orange', style='label.style_label_up'),
}
R1 = int(dtm.datetime(2026, 6, 18, 0, 0, tzinfo=timezone.utc).timestamp() * 1000)
R0 = R1 - 168 * bm.H
def dts(t): return dtm.datetime.fromtimestamp(t / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M')
arr = lambda v: 'array.from(' + ', '.join(v) + ')'

db = DatabaseManager(**get_db_config()); db.connect()
arrays, draws = [], []
for name, s in STREAMS.items():
    cfg = bm.BiasConfig(osc=s['osc'], trigger_tf=s['tf'], gate='oob', entry_order='seq', s3_variant='m',
                        xm45=False, mae=0.4, target=0.9, floater_anchor='last', verdict='pk', trigger_src='hlc3')
    W = bm.BiasWindow(db, R1, cfg=cfg); bclose = W.base['close'].to_numpy()
    ups = [u for u in W.signals() if R0 <= u['t'] < R1 and u['call'] in ('BULL', 'BEAR')]
    for u in ups:
        u['px'] = round(float(bclose[u['anc_bar']]), 5); u['fpx'] = round(float(bclose[u['flt_bar']]), 5)
        u['ft'] = int(W.ts[u['flt_bar']])
    nb = sum(u['call'] == 'BULL' for u in ups); nr = sum(u['call'] == 'BEAR' for u in ups)
    print(f"  {name:7s}: {len(ups)} bias updates ({nb} BULL / {nr} BEAR)")
    p = name
    arrays.append(f'''{p}_t  = {arr([str(u['t']) for u in ups])}
{p}_px = {arr([f"{u['px']:.5f}" for u in ups])}
{p}_cl = {arr(['"' + u['call'] + '"' for u in ups])}
{p}_sd = {arr(['"' + ('HI' if u['side'] == 1 else 'LO') + '"' for u in ups])}
{p}_an = {arr([f"{u['anc']:.1f}" for u in ups])}
{p}_fl = {arr([f"{u['flt']:.1f}" for u in ups])}
{p}_ft = {arr([str(u['ft']) for u in ups])}
{p}_fp = {arr([f"{u['fpx']:.5f}" for u in ups])}''')
    draws.append(f'''    for i = 0 to array.size({p}_t) - 1
        c = array.get({p}_cl, i)
        label.new(array.get({p}_t, i), array.get({p}_px, i), "{name} " + (c == "BULL" ? "▲" : "▼") + c + " " + array.get({p}_sd, i) + "\\na" + str.tostring(array.get({p}_an, i), "#.0") + " f" + str.tostring(array.get({p}_fl, i), "#.0"), xloc = xloc.bar_time, yloc = yloc.price, style = {s['style']}, color = {s['color']}, textcolor = color.white, size = size.small)
        line.new(array.get({p}_t, i), array.get({p}_px, i), array.get({p}_ft, i), array.get({p}_fp, i), xloc = xloc.bar_time, color = color.new({s['color']}, 40), width = 1, style = line.style_dashed)''')
db.disconnect()
print(f"range {dts(R0)} → {dts(R1)}")
title = f'pine2 — s3m + s12maj bias ({dts(R0)[5:10]}→{dts(R1)[5:10]})'
nl = chr(10)
body = f'''//@version=5
indicator("{title}", overlay = true, max_labels_count = 500, max_lines_count = 500)
// s3m = aqua (below bar) · s12maj = orange (above bar)
{nl.join(arrays)}
var bool done = false
if barstate.islast and not done
    done := true
{nl.join(draws)}
'''
path = '/home/joe/thecodes/pine2_bias.pine'
open(path, 'w').write(body)
print(f'→ {path}')
