"""
pine1_groups_emit.py (Joe 0625) — top-IS confluence groups winning/failing on the current window.

The 16 groups = top 8 (+IS lift = 'successful-flip' predictors) + bottom 8 (-IS lift = 'continuation'
predictors), W=792 bars (3x22m), from snf_conf_bars. For each s3m flip in the current window
(0611 00:00 -> 0618 00:00), any of the 16 groups whose lines are all OOB-same-side within W gets a
label: the group lines + their values, a blank line, then the CLASS + the realised outcome
(WON +0.9 / FAIL with mfe+mae). Label coloured by class (teal=success-flip, maroon=continuation).
Diagnostic: eyeball whether the IS classifications survive on the (mostly OOS) current window.
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import datetime as dtm
from datetime import timezone
import numpy as np, itertools
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from bias_machine import _sign
def ms(dt): return int(dt.replace(tzinfo=timezone.utc).timestamp() * 1000)
def dts(t): return dtm.datetime.fromtimestamp(t / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M')
W = 792
db = DatabaseManager(**get_db_config()); db.connect()

# ── 1. the 16 groups (top +/-8 IS lift at W) from snf_conf_bars ──
tf = {r['ind_name']: r['tf'] for r in db.execute("SELECT ind_name, itf_seconds tf FROM vw_indicator_configs_live WHERE itf_seconds>=180 AND ind_name REGEXP '[a-z]+[0-9]+[mMr]$'", fetch=True)}
rows = db.execute('SELECT flip_id, wi, pnl, line, bars_since FROM snf_conf_bars', fetch=True)
fl = {}
for r in rows: fl.setdefault(r['flip_id'], {'wi': r['wi'], 'pnl': r['pnl'], 'bs': {}})['bs'][r['line']] = r['bars_since']
IS = [f for f in fl.values() if f['wi'] < 5]
for f in IS: f['c'] = set(L for L, b in f['bs'].items() if b <= W)
bIS = np.mean([f['pnl'] for f in IS])
gp = {}
for sz in (3, 4):
    for g in itertools.combinations(sorted(tf), sz):
        if not any(tf[x] > 180 for x in g): continue
        gs = set(g); pis = [f['pnl'] for f in IS if gs <= f['c']]
        if len(pis) >= 15: gp[g] = np.mean(pis) - bIS
srt = sorted(gp.items(), key=lambda kv: -kv[1])
groups = [(set(g), 'SUCCESS-FLIP') for g, _ in srt[:8]] + [(set(g), 'CONTINUATION') for g, _ in srt[-8:]]
glines = sorted(set().union(*[g for g, _ in groups]))
print(f'16 groups locked (W={W}). lines involved: {len(glines)}')

# ── 2. current window: s3m flips + placements + line OOB/value at each flip ──
R1 = ms(dtm.datetime(2026, 6, 18, 0, 0)); R0 = R1 - 168 * bm.H
cfg = bm.BiasConfig(osc='s3m', trigger_tf=6, gate='oob', entry_order='seq', s3_variant='m', xm45=False,
                    mae=0.4, target=0.9, floater_anchor='last', verdict='pk', trigger_src='hlc3')
Wd = bm.BiasWindow(db, R1, cfg=cfg); ts = Wd.ts; n = len(ts); px = Wd.px
pls = Wd.placements(Wd.signals(), cfg.mae, cfg.target, s3_lookback=2)
pm = {int(p['pk_t']): p for p in pls if R0 <= p['pk_t'] < R1}
last = {}; valarr = {}
for L in glines:
    try: s = _sign(Wd._line(L)); v = Wd._line(L)
    except Exception: continue
    last[L] = {d: np.maximum.accumulate(np.where(s == d, np.arange(n), -1)) for d in (1, -1)}; valarr[L] = v
# flat label list: (t, py, text, class)
labs = []
for u in Wd.signals():
    if u['call'] not in ('BULL', 'BEAR') or not (R0 <= u['t'] < R1): continue
    p = pm.get(int(u['t']))
    if p is None: continue
    d = 1 if u['call'] == 'BULL' else -1; j = int(np.searchsorted(ts, int(u['t']))) - 1
    out = f"WON +0.9" if p['hit'] else f"FAIL mfe{p['potential']:+.2f} mae{p['mae']:+.2f}"
    for g, cls in groups:
        if all(L in last and last[L][d][j] >= 0 and (j - last[L][d][j]) <= W for L in g):
            lv = ' '.join(f"{L}{valarr[L][j]:.0f}" for L in sorted(g))
            labs.append((int(u['t']), float(px[j]), f"{lv}\\n\\n{cls} · {out}", cls))
db.disconnect()
nwin = sum(1 for cls in ('SUCCESS-FLIP', 'CONTINUATION') for t, py, tx, c in labs if c == cls)
print(f"range {dts(R0)} -> {dts(R1)} · {len(labs)} group-firings ({sum(1 for *_ ,c in labs if c=='SUCCESS-FLIP')} success / {sum(1 for *_ ,c in labs if c=='CONTINUATION')} continuation)")

# ── 3. pine ──
arr = lambda v: 'array.from(' + ', '.join(v) + ')'
nl = chr(10)
title = f'pine1 — top-IS groups ({dts(R0)[5:10]}->{dts(R1)[5:10]}) W={W}'
body = f'''//@version=5
indicator("{title}", overlay = true, max_labels_count = 500, max_lines_count = 500)
g_t  = {arr([str(t) for t, py, tx, c in labs])}
g_py = {arr([f"{py:.5f}" for t, py, tx, c in labs])}
g_tx = {arr(['"' + tx + '"' for t, py, tx, c in labs])}
g_cl = {arr(['1' if c == 'SUCCESS-FLIP' else '0' for t, py, tx, c in labs])}
var bool done = false
if barstate.islast and not done
    done := true
    for i = 0 to array.size(g_t) - 1
        succ = array.get(g_cl, i) == 1
        label.new(array.get(g_t, i), array.get(g_py, i), array.get(g_tx, i), xloc = xloc.bar_time, yloc = yloc.price, style = succ ? label.style_label_up : label.style_label_down, color = succ ? color.new(color.teal, 0) : color.new(color.maroon, 0), textcolor = color.white, size = size.small)
'''
path = '/home/joe/thecodes/pine1_groups.pine'
open(path, 'w').write(body)
print(f'→ {path}')
