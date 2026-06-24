"""
alchemy_snf_emit.py (Joe 0623-24) — modular pine emit for the alchemy window: SnF pks + bias
update labels (with anchor→floater lines) + the FIRST-TRADE module (placements: entry arrow +
{potential} ✓/✗ vs the MAE/target metric), ported from bias_pk_emit so the alchemy view is combined.

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

STREAMS = {  # the four streams, emitted through this one modular path: python3 alchemy_snf_emit.py [name]
    's3min':  dict(osc='s3m',  trigger_tf=6),
    's6min':  dict(osc='s12m', trigger_tf=6, osc_from_trigger=True),   # self-triggered GEN_M@TF6
    's12min': dict(osc='s12m', trigger_tf=12),
    's12maj': dict(osc='s12M', trigger_tf=12),
}
STREAM = sys.argv[1] if len(sys.argv) > 1 else 's12min'
CFG = bm.BiasConfig(gate='oob', entry_order='seq', s3_variant='m', xm45=False, mae=0.4,
                    target=0.9, floater_anchor='last', verdict='pk', **STREAMS[STREAM])
R1 = int(dtm.datetime(2026, 6, 18, 0, 0, tzinfo=timezone.utc).timestamp() * 1000)   # 0611 00:00 → 0618 00:00 (matches the alchemy/bl_review work)
R0 = R1 - 168 * bm.H                                                                # warmup runs behind R0 via the BiasWindow lookback
def dts(t): return dtm.datetime.fromtimestamp(t / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M')

db = DatabaseManager(**get_db_config()); db.connect()
W = bm.BiasWindow(db, R1, cfg=CFG); db.disconnect()
bclose = W.base['close'].to_numpy()
ups_all = W.signals()
pls_all = W.placements(ups_all, CFG.mae, CFG.target)        # first trade after each bias update
ups = [u for u in ups_all if R0 <= u['t'] < R1]
pls = [p for p in pls_all if R0 <= p['et'] < R1]
for u in ups:
    u['px'] = round(float(bclose[u['anc_bar']]), 5)
    u['fpx'] = round(float(bclose[u['flt_bar']]), 5)
    u['ft'] = int(W.ts[u['flt_bar']])
nb = sum(u['call'] == 'BULL' for u in ups); nr = sum(u['call'] == 'BEAR' for u in ups); nn = sum(u['call'] == 'NEUT' for u in ups)
print(f"range {dts(R0)} → {dts(R1)}  ·  osc={CFG.osc} trig=s{CFG.trigger_tf}m {CFG.gate}")
print(f"  warmup: base {dts(int(W.ts[0]))} → R0 = {(R0 - int(W.ts[0])) / 86400000:.1f}d behind the scored start")
hit = sum(p['hit'] for p in pls)
print(f"  snf pks / bias updates: {len(ups)} ({nb} BULL / {nr} BEAR / {nn} NEUT)")
print(f"  first trades: {len(pls)} · correct {hit} ({hit/len(pls):.0%})" if pls else "  first trades: 0")

arr = lambda v: 'array.from(' + ', '.join(v) + ')'
title = f'alchemy snf+bias — {STREAM} (trig s{CFG.trigger_tf}m) ({dts(R0)[5:10]}→{dts(R1)[5:10]})'
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
// ── first trades (entry arrow + result {{potential}} ✓/✗) ──
et  = {arr([str(p['et']) for p in pls])}
ed  = {arr(['1' if p['bd'] == 1 else '-1' for p in pls])}
po  = {arr([f"{p['potential']:.2f}" for p in pls])}
hb  = {arr(['1' if p['hit'] else '0' for p in pls])}
ma  = {arr([f"{p['mae']:.2f}" for p in pls])}
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
        label.new(array.get(et, i), 0.0, str.tostring(array.get(po, i), "#.0#") + " / " + str.tostring(array.get(ma, i), "#.0#") + (win ? " ✓" : " ✗"), xloc = xloc.bar_time, yloc = isL ? yloc.belowbar : yloc.abovebar, style = isL ? label.style_label_up : label.style_label_down, color = win ? color.new(color.teal, 0) : color.new(color.maroon, 0), textcolor = color.white, size = size.normal)
'''
path = f'/home/joe/thecodes/alchemy_snf_{STREAM}.pine'
open(path, 'w').write(body)
print(f'→ {path}')
