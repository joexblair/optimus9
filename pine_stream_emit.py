"""
pine_stream_emit.py (Joe 0624) — per-stream bias emit with first-trade stats. One .pine per stream
(s3min · s6min · s12min · s12maj) for the current window (0611 00:00 -> 0618 00:00). Each shows:
  - bias updates (label: call · side · a{anchor} f{floater})
  - line to the anchor (dashed anchor->floater)
  - first-trade stats appended (po / ma  ✓won/✗lost), loose stop (mae_allow=2.0) so MAE is the true drawdown.

  python3 pine_stream_emit.py            # all four
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import datetime as dtm
from datetime import timezone
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm

STREAMS = {  # name: BiasConfig kwargs · colour · label style
    's3min':  dict(cfg=dict(osc='s3m', trigger_tf=6),                          color='color.aqua',    style='label.style_label_down'),
    's6min':  dict(cfg=dict(osc='s12m', trigger_tf=6, osc_from_trigger=True),  color='color.lime',    style='label.style_label_down'),
    's12min': dict(cfg=dict(osc='s12m', trigger_tf=12),                        color='color.orange',  style='label.style_label_up'),
    's12maj': dict(cfg=dict(osc='s12M', trigger_tf=12),                        color='color.fuchsia', style='label.style_label_up'),
}
R1 = int(dtm.datetime(2026, 6, 18, 0, 0, tzinfo=timezone.utc).timestamp() * 1000)
R0 = R1 - 168 * bm.H
def dts(t): return dtm.datetime.fromtimestamp(t / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M')
arr = lambda v: 'array.from(' + ', '.join(v) + ')'

db = DatabaseManager(**get_db_config()); db.connect()
for name, s in STREAMS.items():
    cfg = bm.BiasConfig(gate='oob', entry_order='seq', s3_variant='m', xm45=False, mae=0.4, target=0.9,
                        floater_anchor='last', verdict='pk', trigger_src='hlc3', **s['cfg'])
    W = bm.BiasWindow(db, R1, cfg=cfg); bclose = W.base['close'].to_numpy()
    pls = {int(p['pk_t']): p for p in W.placements(W.signals(), 2.0, 0.9, s3_lookback=2) if R0 <= p['pk_t'] < R1}
    ups = [u for u in W.signals() if R0 <= u['t'] < R1 and u['call'] in ('BULL', 'BEAR')]
    rows = []
    for u in ups:
        anc_px = round(float(bclose[u['anc_bar']]), 5); flt_px = round(float(bclose[u['flt_bar']]), 5)
        ft = int(W.ts[u['flt_bar']]); p = pls.get(int(u['t']))
        stat = f"{p['potential']:+.2f} / {p['mae']:+.2f} {'✓' if p['hit'] else '✗'}" if p else "no trade"
        ar = '▲' if u['call'] == 'BULL' else '▼'; sd = 'HI' if u['side'] == 1 else 'LO'
        rows.append((u['t'], anc_px, flt_px, ft, f"{name} {ar}{u['call']} {sd}\\na{u['anc']:.0f} f{u['flt']:.0f}\\n{stat}"))
    nw = sum(1 for u in ups if pls.get(int(u['t'])) and pls[int(u['t'])]['hit'])
    print(f"  {name:7s}: {len(ups)} bias updates · {nw} first-trade wins")
    body = f'''//@version=5
indicator("stream {name} ({dts(R0)[5:10]}->{dts(R1)[5:10]})", overlay = true, max_labels_count = 500, max_lines_count = 500)
b_t  = {arr([str(t) for t, ap, fp, ft, tx in rows])}
b_ap = {arr([f"{ap:.5f}" for t, ap, fp, ft, tx in rows])}
b_fp = {arr([f"{fp:.5f}" for t, ap, fp, ft, tx in rows])}
b_ft = {arr([str(ft) for t, ap, fp, ft, tx in rows])}
b_tx = {arr(['"' + tx + '"' for t, ap, fp, ft, tx in rows])}
var bool done = false
if barstate.islast and not done
    done := true
    for i = 0 to array.size(b_t) - 1
        label.new(array.get(b_t, i), array.get(b_ap, i), array.get(b_tx, i), xloc = xloc.bar_time, yloc = yloc.price, style = {s['style']}, color = {s['color']}, textcolor = color.white, size = size.normal)
        line.new(array.get(b_t, i), array.get(b_ap, i), array.get(b_ft, i), array.get(b_fp, i), xloc = xloc.bar_time, color = color.new({s['color']}, 40), width = 1, style = line.style_dashed)
'''
    open(f'/home/joe/thecodes/pine_stream_{name}.pine', 'w').write(body)
db.disconnect()
print(f"range {dts(R0)} -> {dts(R1)} · 4 .pine files written")
