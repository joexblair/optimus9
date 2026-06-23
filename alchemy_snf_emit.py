"""
alchemy_snf_emit.py (Joe 0623) — lean modular pine emit for the alchemy window: SnF pks + bias
update labels (with anchor→floater lines). NO trade tests (that's bias_pk_emit's job).

Each pk event (pk_events = the SnF meld stream) is drawn as a label (call · side · a{anchor}
f{floater}) coloured by the bias call (BULL green / BEAR red / NEUT grey) + a dashed line from the
anchor bar to the floater bar. Config mirrors the cascade winner; window = the bias 168h scored range.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import datetime as dtm
from datetime import timezone
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm

CFG = bm.BiasConfig(osc='s12m', trigger_tf=12, gate='oob', entry_order='seq', s3_variant='m',
                    xm45=False, mae=0.4, target=0.9, floater_anchor='last', verdict='pk')
R1 = int(dtm.datetime(2026, 6, 18, 3, 37, tzinfo=timezone.utc).timestamp() * 1000)
R0 = R1 - 168 * bm.H
def dts(t): return dtm.datetime.fromtimestamp(t / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M')

db = DatabaseManager(**get_db_config()); db.connect()
W = bm.BiasWindow(db, R1, cfg=CFG); db.disconnect()
bclose = W.base['close'].to_numpy()
ups = [u for u in W.signals() if R0 <= u['t'] < R1]
for u in ups:
    u['px'] = round(float(bclose[u['anc_bar']]), 5)
    u['fpx'] = round(float(bclose[u['flt_bar']]), 5)
    u['ft'] = int(W.ts[u['flt_bar']])
nb = sum(u['call'] == 'BULL' for u in ups); nr = sum(u['call'] == 'BEAR' for u in ups); nn = sum(u['call'] == 'NEUT' for u in ups)
print(f"range {dts(R0)} → {dts(R1)}  ·  osc={CFG.osc} trig=s{CFG.trigger_tf}m {CFG.gate}")
print(f"  snf pks / bias updates: {len(ups)} ({nb} BULL / {nr} BEAR / {nn} NEUT)")

arr = lambda v: 'array.from(' + ', '.join(v) + ')'
title = f'alchemy snf+bias — osc {CFG.osc} trig s{CFG.trigger_tf}m ({dts(R0)[5:10]}→{dts(R1)[5:10]})'
body = f'''//@version=5
indicator("{title}", overlay = true, max_labels_count = 500, max_lines_count = 500)
// ── SnF pks + bias update labels (label + anchor→floater dashed line) ──
t   = {arr([str(u['t']) for u in ups])}
pxv = {arr([f"{u['px']:.5f}" for u in ups])}
cl  = {arr(['"' + u['call'] + '"' for u in ups])}
sd  = {arr(['"' + ('HI' if u['side'] == 1 else 'LO') + '"' for u in ups])}
anc = {arr([f"{u['anc']:.1f}" for u in ups])}
flt = {arr([f"{u['flt']:.1f}" for u in ups])}
ft  = {arr([str(u['ft']) for u in ups])}
fpx = {arr([f"{u['fpx']:.5f}" for u in ups])}
var bool done = false
if barstate.islast and not done
    done := true
    for i = 0 to array.size(t) - 1
        c   = array.get(cl, i)
        col = c == "BULL" ? color.new(color.green, 0) : c == "BEAR" ? color.new(color.red, 0) : color.new(color.gray, 0)
        ar  = c == "BULL" ? "▲BULL" : c == "BEAR" ? "▼BEAR" : "■NEUT"
        label.new(array.get(t, i), array.get(pxv, i), ar + " " + array.get(sd, i) + "\\na" + str.tostring(array.get(anc, i), "#.0") + " f" + str.tostring(array.get(flt, i), "#.0"), xloc = xloc.bar_time, yloc = yloc.price, style = label.style_label_down, color = col, textcolor = color.white, size = size.normal)
        line.new(array.get(t, i), array.get(pxv, i), array.get(ft, i), array.get(fpx, i), xloc = xloc.bar_time, color = color.new(color.orange, 0), width = 2, style = line.style_dashed)
'''
path = '/home/joe/thecodes/alchemy_snf.pine'
open(path, 'w').write(body)
print(f'→ {path}')
