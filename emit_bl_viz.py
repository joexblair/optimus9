"""Emit ONE Pine overlay (last 36h) that labels selected BL lines' state machines with
real Pine labels — text = "<line>:<bls>" (bls 0/1/2/3), coloured by state — so you can
eyeball each line's breach→curl→complete journey against price/swings in TV.

Improves the old per-day plotchar viz: real label.new (not chars), per-LINE (not just the
combined fold), 36h window, and the bny30-gate shading behind an in-chart toggle.

Config below: LINES (which lines to label), COMBO (k_len per line — default = gate-M best
pick), GATE_BB/GATE_K (which bny30 components shade + gate the PK/trades)."""
import sys
import numpy as np
from datetime import datetime, timezone
sys.path.insert(0, '/home/joe/thecodes')
import logging
for nm in ('BybitKlineClient', 'BLDetect', 'KlineLoader', 'DatabaseManager'):
    logging.getLogger(nm).setLevel('ERROR')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.bl_detect import BLDetect, GCA5M_RAW
from optimus9.orchestration.gate_signal_sweep import bny30_oob_side, pine_aligned_signals
from optimus9.orchestration.bl_group_grind import _refold
from optimus9.analysis.bl_grind import walk
from optimus9.compute.swing_detect import find_pivots
from logger import get_logger

# ── config ──────────────────────────────────────────────────────────────────
LINES        = ['s18b', 'hb9b']          # the BL lines to label (name:bls). swap freely.
# 36h debounced label counts (lower = cleaner viz): s18b 20 · hb15b 42 · hb9b 63 · b6b 101
# · s90b 227 · hs15r 271 · hs9r 465 · s30r 1302 (the 30s/hs lines churn — unviewable as labels).
COMBO        = {'b6b': 4, 'hb15b': 3, 'hb9b': 5, 'hs15r': 2,   # gate-M best pick (k_len/line)
                'hs9r': 2, 's18b': 12, 's30r': 4, 's90b': 17}
LOOKBACK_H   = 36
GATE_BB, GATE_K = True, False            # gate-M. (True,True)=both · (False,True)=p
SWING_PCT, PK_LOOKBACK = 0.9, 11
OUT = '/home/joe/thecodes/bl_viz_2line.pine'
log = get_logger('BLViz')


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    det = BLDetect(db, lookback_hours=LOOKBACK_H, warmup_hours=12)
    for f in det._families:                                   # apply the combo's k_len
        if f['name'] in COMBO:
            f['k'] = {**f['k'], 'k_len': int(COMBO[f['name']])}
    base, ts, win_start, _, px = det._setup()
    states = {f['name']: det._run_family(f, base, ts)[3]['state'] for f in det._families}
    combined = _refold([states[f['name']] for f in det._families])
    oob = bny30_oob_side(base, use_bb=GATE_BB, use_k=GATE_K)
    pk_idx, pk_dirs = pine_aligned_signals(base, db, GCA5M_RAW, gate=True,
                                           gate_bb=GATE_BB, gate_k=GATE_K)
    raw_pk = np.zeros(len(ts), np.int8); raw_pk[pk_idx] = pk_dirs
    db.disconnect()

    M = ts >= win_start
    tsm = ts[M].astype('int64'); combm = combined[M]; oobm = oob[M]
    pkm = raw_pk[M]; pxm = np.asarray(px, float)[M]
    sm = {k: v[M] for k, v in states.items()}
    N = len(tsm)
    pivots = sorted(find_pivots(pxm, SWING_PCT))
    trades = walk(combm, pkm, pxm, pivots, PK_LOOKBACK)

    MIN_DWELL = 6           # bars (30s): debounce the idle↔breach flicker; a 0/1 segment
    def trans(st):          # shorter than this is dropped. curl(2)/complete(3) ALWAYS kept.
        out, i = [], 0
        while i < N:
            j = i
            while j < N and st[j] == st[i]:
                j += 1
            s = int(st[i])
            if s in (2, 3) or (j - i) >= MIN_DWELL:
                out.append((int(tsm[i]), s))
            i = j
        return out

    counts = sorted((len(trans(sm[f['name']])), f['name'], f['tf_seconds']) for f in det._families)
    log.info('debounced labels/line (36h): '
             + ' · '.join(f"{nm}(TF{tf}s)={c}" for c, nm, tf in counts))

    pu = [int(tsm[i]) for i in range(N) if pkm[i] == 1]
    pdn = [int(tsm[i]) for i in range(N) if pkm[i] == -1]
    tL = [int(tsm[t['open_i']]) for t in trades if t['dir'] == 1]
    tS = [int(tsm[t['open_i']]) for t in trades if t['dir'] == -1]
    closed = (oobm == 0)
    gtog = [int(tsm[i]) for i in range(1, N) if closed[i] != closed[i - 1]]
    init = bool(closed[0])

    def arr(xs):
        return f"array.from({','.join(str(x) for x in xs)})" if xs else "array.new<int>(0)"

    # per-line label blocks (alternate above/below so two lines don't collide)
    blocks = []
    for k, name in enumerate(LINES):
        tr = trans(sm[name])
        above = (k % 2 == 0)
        blocks.append(f'''
{name}_t = {arr([t for t, _ in tr])}
{name}_s = {arr([s for _, s in tr])}
if array.includes({name}_t, ms)
    s_{name} = array.get({name}_s, array.indexof({name}_t, ms))
    label.new(bar_index, {'high' if above else 'low'}, "{name}:" + str.tostring(s_{name}),
              color=stcol(s_{name}), textcolor=color.white, size=size.small,
              style=label.style_label_{'down' if above else 'up'})''')

    gate_title = 'M' if (GATE_BB and not GATE_K) else 'p' if (GATE_K and not GATE_BB) else 'both'
    span = f"{datetime.fromtimestamp(tsm[0]/1000, tz=timezone.utc):%m-%d %H:%M}–{datetime.fromtimestamp(tsm[-1]/1000, tz=timezone.utc):%m-%d %H:%M}"
    pine = f'''//@version=5
indicator("BL viz {','.join(LINES)} · gate-{gate_title} · {span}", overlay=true, max_labels_count=500)
showGate   = input.bool(true,  "Shade when bny30 gate closed (IB)")
showPk     = input.bool(true,  "5s PK triangles")
showTrades = input.bool(true,  "Trade-open shading")
stcol(s) => s == 1 ? color.yellow : s == 2 ? color.orange : s == 3 ? color.lime : color.gray
ms = int(time)
{''.join(blocks)}

// ── context: PK fires, trades, and the bny30 gate (optional) ──
pu = {arr(pu)}
pd = {arr(pdn)}
tL = {arr(tL)}
tS = {arr(tS)}
gt = {arr(gtog)}
var bool gc = {str(init).lower()}
var int  gci = 0
while gci < array.size(gt)
    if array.get(gt, gci) > ms
        break
    gc := not gc
    gci += 1
plotshape(showPk and array.includes(pu, ms), style=shape.triangleup,   location=location.belowbar, color=color.new(color.lime, 0),    size=size.tiny, title="pk long")
plotshape(showPk and array.includes(pd, ms), style=shape.triangledown, location=location.abovebar, color=color.new(color.fuchsia, 0), size=size.tiny, title="pk short")
bgcolor(showGate and gc ? color.new(color.white, 90) : na, title="bny30 closed")
bgcolor(showTrades and array.includes(tL, ms) ? color.new(color.green, 75) : na, title="trade long")
bgcolor(showTrades and array.includes(tS, ms) ? color.new(color.red, 75)   : na, title="trade short")
'''
    open(OUT, 'w').write(pine)
    nlab = sum(len(trans(sm[n])) for n in LINES)
    log.info(f'{OUT}: {N} bars ({LOOKBACK_H}h) · lines {LINES} · {nlab} state-labels · '
             f'{len(pu)+len(pdn)} pks · {len(trades)} trades · gate-{gate_title} ({len(gtog)} toggles)')


if __name__ == '__main__':
    main()
