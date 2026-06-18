"""
bias_pk_emit.py — canonical modular pine emit for the CURRENT bias machine (engine-driven, ups()).

Two layers, each self-contained:
  • pk UPDATES — label (call · side · a{anchor} f{floater}) + a dashed line from the anchor to the
    floater bar. The line logic lives WITH the pk-update block (endpoints = anc_bar→flt_bar, carried
    on the pk update itself), so the floater source is always visualised alongside its label.
  • TRADE TESTS — entry arrow (green long / red short) + placement result ({potential} ✓/✗ vs the
    0.4-MAE / 0.9-target metric).

Config (edit at top): trigger TF · oscillator · gate. Default = osc s12m / trigger s12m / oob.
Supersedes bias_pk_emit_s6r.py + bias_pk_emit_config.py (those used the shelved s6r-reversal method).
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.bl_detect import BLDetect
import bias_machine as bm

TRIG_TF, OSC, GATE = 12, 's12m', 'oob'                        # osc 's6r' (default) or 's12m'
ENTRY = ('seq', 'm', False)                                  # cascade winner: sequential · s3=m · xm45 off
MAE, TARGET = 0.4, 0.9
R0 = int(dtm.datetime(2026, 5, 31, 0, 0, tzinfo=timezone.utc).timestamp() * 1000)
R1 = int(dtm.datetime(2026, 6, 4, 0, 0, tzinfo=timezone.utc).timestamp() * 1000)
def dts(t): return dtm.datetime.fromtimestamp(t / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M')

db = DatabaseManager(**get_db_config()); db.connect()
W = bm.BiasWindow(db, R1); db.disconnect()
if OSC == 's12m':
    W.set_osc(W._aligned(720, bm.GEN_M), 144)                # osc = s12m (TF12)
W.set_entry(*ENTRY)
bclose = W.base['close'].to_numpy()

ups_all = W.ups(W.trigs(TRIG_TF), GATE)
pls_all = W.placements(ups_all, MAE, TARGET)                 # full chain, then filter to range
ups = [u for u in ups_all if R0 <= u['t'] < R1]
pls = [p for p in pls_all if R0 <= p['et'] < R1]
for u in ups:
    u['px'] = round(float(bclose[u['anc_bar']]), 5)
    u['fpx'] = round(float(bclose[u['flt_bar']]), 5)
    u['ft'] = int(W.ts[u['flt_bar']])

nb = sum(u['call'] == 'BULL' for u in ups); nr = sum(u['call'] == 'BEAR' for u in ups); nn = sum(u['call'] == 'NEUT' for u in ups)
hit = sum(p['hit'] for p in pls)
print(f"range {dts(R0)} → {dts(R1)}  ·  osc={OSC} trig=s{TRIG_TF}m {GATE}  ·  MAE {MAE} target {TARGET}")
print(f"  pk updates: {len(ups)} ({nb} BULL / {nr} BEAR / {nn} NEUT)")
print(f"  trades: {len(pls)} · correct {hit} ({hit/len(pls):.0%})" if pls else "  trades: 0")

arr = lambda v: 'array.from(' + ', '.join(v) + ')'
title = f'bias pk — osc {OSC} trig s{TRIG_TF}m ({dts(R0)[5:10]}→{dts(R1)[5:10]})'
body = f'''//@version=5
indicator("{title}", overlay = true, max_labels_count = 500, max_lines_count = 500)
// ── pk UPDATES (label + anchor→floater dashed line) ──
t   = {arr([str(u['t']) for u in ups])}
pxv = {arr([f"{u['px']:.5f}" for u in ups])}
cl  = {arr(['"' + u['call'] + '"' for u in ups])}
sd  = {arr(['"' + ('HI' if u['side'] == 1 else 'LO') + '"' for u in ups])}
anc = {arr([f"{u['anc']:.1f}" for u in ups])}
flt = {arr([f"{u['flt']:.1f}" for u in ups])}
ft  = {arr([str(u['ft']) for u in ups])}
fpx = {arr([f"{u['fpx']:.5f}" for u in ups])}
// ── trade tests (entry arrow + result) ──
et  = {arr([str(p['et']) for p in pls])}
ed  = {arr(['1' if p['bd'] == 1 else '-1' for p in pls])}
po  = {arr([f"{p['potential']:.2f}" for p in pls])}
hb  = {arr(['1' if p['hit'] else '0' for p in pls])}
var bool done = false
if barstate.islast and not done
    done := true
    for i = 0 to array.size(t) - 1
        c   = array.get(cl, i)
        col = c == "BULL" ? color.new(color.green, 0) : c == "BEAR" ? color.new(color.red, 0) : color.new(color.gray, 0)
        ar  = c == "BULL" ? "▲BULL" : c == "BEAR" ? "▼BEAR" : "■NEUT"
        label.new(array.get(t, i), array.get(pxv, i), ar + " " + array.get(sd, i) + "\\na" + str.tostring(array.get(anc, i), "#.0") + " f" + str.tostring(array.get(flt, i), "#.0"), xloc = xloc.bar_time, yloc = yloc.price, style = label.style_label_down, color = col, textcolor = color.white, size = size.normal)
        line.new(array.get(t, i), array.get(pxv, i), array.get(ft, i), array.get(fpx, i), xloc = xloc.bar_time, color = color.new(color.orange, 0), width = 2, style = line.style_dashed)
    for i = 0 to array.size(et) - 1
        isL = array.get(ed, i) == 1
        win = array.get(hb, i) == 1
        label.new(array.get(et, i), 0.0, "", xloc = xloc.bar_time, yloc = isL ? yloc.belowbar : yloc.abovebar, style = isL ? label.style_arrowup : label.style_arrowdown, color = isL ? color.new(color.lime, 0) : color.new(color.red, 0), size = size.normal)
        label.new(array.get(et, i), 0.0, str.tostring(array.get(po, i), "#.0#") + (win ? " ✓" : " ✗"), xloc = xloc.bar_time, yloc = isL ? yloc.belowbar : yloc.abovebar, style = isL ? label.style_label_up : label.style_label_down, color = win ? color.new(color.teal, 0) : color.new(color.maroon, 0), textcolor = color.white, size = size.normal)
'''
path = '/home/joe/thecodes/bias_pk.pine'
open(path, 'w').write(body)
print(f'→ {path}')
