"""
bias_pk_emit_s6r.py — emit the ALT-anchor pk approach (s6r-reversal anchor) for 0601→0605.

Anchor: s6m reversal (TF6) arms; wait for s6r to reverse; anchor = s6r extreme over that swing.
Floater = prev same-side anchor. Gate = oob (s14M|s14r). pk fires at the s6r reversal.
Pine layers: pk detail labels (call · side · a{anc} f{flt}) · entry arrows (green long / red short)
· placement result per trade (potential% + ✓/✗ vs the 0.3-MAE / 0.9-target metric).
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.bl_detect import BLDetect
import bias_machine as bm

ANCHOR_TF = 6                                                # pk detection TF (s6 vs s12 …)
R0 = int(dtm.datetime(2026, 6, 1, 0, 0, tzinfo=timezone.utc).timestamp() * 1000)
R1 = int(dtm.datetime(2026, 6, 6, 0, 0, tzinfo=timezone.utc).timestamp() * 1000)
def dts(t): return dtm.datetime.fromtimestamp(t / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M')

db = DatabaseManager(**get_db_config()); db.connect()
W = bm.BiasWindow(db, R1); db.disconnect()
bclose = W.base['close'].to_numpy()
MAE_ALLOW, TARGET = 0.4, 0.9
ups = [u for u in W.ups_s6r_anchor('oob', ANCHOR_TF) if R0 <= u['t'] < R1]
pls = [p for p in W.placements(ups, MAE_ALLOW, TARGET) if R0 <= p['et'] < R1]
seen_void = set(); disp = []                                  # one VOID label per collided bar
for u in ups:
    if u['call'] == 'VOID':
        if u['t'] in seen_void:
            continue
        seen_void.add(u['t'])
    disp.append(u)
ups = disp
for u in ups:
    u['px'] = round(float(bclose[W._at(u['t'])]), 5)

nb = sum(u['call'] == 'BULL' for u in ups); nr = sum(u['call'] == 'BEAR' for u in ups)
nn = sum(u['call'] == 'NEUT' for u in ups); nv = sum(u['call'] == 'VOID' for u in ups)
hit = sum(p['hit'] for p in pls)
print(f'range {dts(R0)} → {dts(R1)}  (window {dts(W.W0)}→{dts(W.W1)})  · MAE {MAE_ALLOW} target {TARGET}')
print(f'  pk updates: {len(ups)} ({nb} BULL / {nr} BEAR / {nn} NEUT / {nv} VOID)')
print(f'  placements: {len(pls)} · correct {hit} ({hit/len(pls):.0%})' if pls else '  placements: 0')

arr = lambda v: 'array.from(' + ', '.join(v) + ')'
title = f'pk s{ANCHOR_TF}r-anchor 0601-0605'
body = f'''//@version=5
// {title} — ALT anchor (s{ANCHOR_TF}r-reversal). EMITTED via bias_machine.py.
indicator("{title}", overlay = true, max_labels_count = 500)
// pk updates
t   = {arr([str(u['t']) for u in ups])}
pxv = {arr([f"{u['px']:.5f}" for u in ups])}
cl  = {arr(['"' + u['call'] + '"' for u in ups])}
sd  = {arr(['"' + ('HI' if u['side'] == 1 else 'LO') + '"' for u in ups])}
anc = {arr([f"{u['anc']:.1f}" for u in ups])}
flt = {arr([f"{u['flt']:.1f}" for u in ups])}
// placements (entry arrows + result)
et  = {arr([str(p['et']) for p in pls])}
ed  = {arr(['1' if p['bd'] == 1 else '-1' for p in pls])}
po  = {arr([f"{p['potential']:.2f}" for p in pls])}
hb  = {arr(['1' if p['hit'] else '0' for p in pls])}
var bool done = false
if barstate.islast and not done
    done := true
    for i = 0 to array.size(t) - 1
        c = array.get(cl, i)
        if c == "VOID"
            label.new(array.get(t, i), array.get(pxv, i), "⛔ VOID test me", xloc = xloc.bar_time, yloc = yloc.price, style = label.style_label_down, color = color.new(color.orange, 0), textcolor = color.black, size = size.small)
        else
            col = c == "BULL" ? color.new(color.green, 0) : c == "BEAR" ? color.new(color.red, 0) : color.new(color.gray, 0)
            ar  = c == "BULL" ? "▲BULL" : c == "BEAR" ? "▼BEAR" : "■NEUT"
            label.new(array.get(t, i), array.get(pxv, i), ar + " " + array.get(sd, i) + "\\na" + str.tostring(array.get(anc, i), "#.0") + " f" + str.tostring(array.get(flt, i), "#.0"), xloc = xloc.bar_time, yloc = yloc.price, style = label.style_label_down, color = col, textcolor = color.white, size = size.small)
    for i = 0 to array.size(et) - 1
        isL = array.get(ed, i) == 1
        win = array.get(hb, i) == 1
        label.new(array.get(et, i), 0.0, "", xloc = xloc.bar_time, yloc = isL ? yloc.belowbar : yloc.abovebar, style = isL ? label.style_arrowup : label.style_arrowdown, color = isL ? color.new(color.lime, 0) : color.new(color.red, 0), size = size.small)
        label.new(array.get(et, i), 0.0, str.tostring(array.get(po, i), "#.0#") + (win ? " ✓" : " ✗"), xloc = xloc.bar_time, yloc = isL ? yloc.belowbar : yloc.abovebar, style = isL ? label.style_label_up : label.style_label_down, color = win ? color.new(color.teal, 0) : color.new(color.maroon, 0), textcolor = color.white, size = size.small)
'''
path = f'/home/joe/thecodes/bias_pk_s{ANCHOR_TF}.pine'
open(path, 'w').write(body)
print(f'→ {path}')
