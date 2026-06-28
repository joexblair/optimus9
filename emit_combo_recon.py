"""
emit_combo_recon — recon Pine for a specific combo (the 8-line fold at its k_lens).
Combined-state completions are labelled with the LINE that completed + its bls state;
ALL raw 5s PKs are printed (green long / red short, ungated); trades are full-opaque
red/green shading + L/S labels; bny30 gate shaded grey when closed. Header = per-line
k_len. Emits top + #22 for comparison. Gate = both (M OR p), len-58, 36h.
"""
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

NAMES = ['b6b', 'hb15b', 'hb9b', 'hs15r', 'hs9r', 's18b', 's30r', 's90b']
COMBOS = [('1', '7,3,5,2,2,17,4,17'), ('22', '7,4,4,2,2,17,4,17')]
LOOKBACK_H, SWING, PKLB = 18, 0.9, 11   # 18h keeps labels < TV's 500 cap & PK arrays compiler-slim
log = get_logger('ComboRecon')
Q = chr(34)


def arr(xs):
    return f"array.from({','.join(str(x) for x in xs)})" if xs else "array.new<int>(0)"


def arr_str(xs):
    return f"array.from({','.join(Q + x + Q for x in xs)})" if xs else "array.new<string>(0)"


def emit(rank, combo, vals, tsm, combined, states_m, pk_all, oobm, trades):
    N, MIN_DWELL = len(tsm), 8   # completions (3) always; 0/1/2 need a real dwell — keeps < TV's 500 cap
    # combined-state journey → label every state (0/1/2/3) with the line(s) at that state,
    # debounced (completes always kept; flickery idle/breach/curl dwells dropped)
    b3t, b3s, b3v = [], [], []
    i = 0
    while i < N:
        j = i
        while j < N and combined[j] == combined[i]:
            j += 1
        s = int(combined[i])
        if s == 3 or (j - i) >= MIN_DWELL:
            if s == 0:   # all lines idle — show the one(s) that just reset to 0 (drove the idle)
                lines = [NAMES[k] for k in range(len(NAMES)) if states_m[k][i] == 0 and (i == 0 or states_m[k][i - 1] != 0)]
            else:        # lines sitting at the combined (min-nonzero) state
                lines = [NAMES[k] for k in range(len(NAMES)) if states_m[k][i] == s]
            lab = ('/'.join(lines) if lines else '?') + f':{s}'
            b3t.append(int(tsm[i])); b3s.append(lab); b3v.append(s)
        i = j
    pu = [int(tsm[i]) for i in range(N) if pk_all[i] == 1]
    pdn = [int(tsm[i]) for i in range(N) if pk_all[i] == -1]
    tL = [int(tsm[t['open_i']]) for t in trades if t['dir'] == 1]
    tS = [int(tsm[t['open_i']]) for t in trades if t['dir'] == -1]
    closed = (oobm == 0)
    gtog = [int(tsm[i]) for i in range(1, N) if closed[i] != closed[i - 1]]
    init = bool(closed[0])
    span = f"{datetime.fromtimestamp(tsm[0]/1000, tz=timezone.utc):%m-%d %H:%M}–{datetime.fromtimestamp(tsm[-1]/1000, tz=timezone.utc):%m-%d %H:%M}"
    settings = '\n'.join(f'//{NAMES[k]}: {vals[k]}' for k in range(len(NAMES)))
    pine = f'''//@version=5
//combo #{rank}: {combo}   (gate both · len-58 · {LOOKBACK_H}h · {span})
{settings}
indicator("BL recon combo #{rank} [{combo}]", overlay=true, max_labels_count=500)
showGate = input.bool(true, "Shade when bny30 gate closed (IB)")
showPk   = input.bool(true, "all raw 5s PKs (green long / red short)")
showB3   = input.bool(true, "bls3 completion labels (line:state)")
stcol(s) => s == 1 ? color.yellow : s == 2 ? color.orange : s == 3 ? color.lime : color.silver
ms = int(time)
b3t = {arr(b3t)}
var string[] b3s = {arr_str(b3s)}
var int[] b3v = {arr(b3v)}
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
// combined-state journey — line(s) at each state, coloured (1 ylw · 2 org · 3 lime · 0 silver)
if showB3 and array.includes(b3t, ms)
    bi = array.indexof(b3t, ms)
    label.new(bar_index, high, array.get(b3s, bi), color=stcol(array.get(b3v, bi)),
              textcolor=color.black, style=label.style_label_down, size=size.small)
// ALL raw 5s PKs — green long / red short
plotshape(showPk and array.includes(pu, ms), style=shape.triangleup,   location=location.belowbar, color=color.new(color.green, 0), size=size.tiny, title="pk long")
plotshape(showPk and array.includes(pd, ms), style=shape.triangledown, location=location.abovebar, color=color.new(color.red, 0),   size=size.tiny, title="pk short")
// TRADES — opaque shading + L/S label
if array.includes(tL, ms)
    label.new(bar_index, low, "L", color=color.new(color.green, 0), textcolor=color.white, style=label.style_label_up, size=size.small)
if array.includes(tS, ms)
    label.new(bar_index, high, "S", color=color.new(color.red, 0), textcolor=color.white, style=label.style_label_down, size=size.small)
bgcolor(showGate and gc ? color.new(color.gray, 0) : na, title="bny30 closed")
bgcolor(array.includes(tL, ms) ? color.new(color.green, 0) : na, title="trade long")
bgcolor(array.includes(tS, ms) ? color.new(color.red, 0)   : na, title="trade short")
'''
    fn = f'/home/joe/thecodes/bl_recon_combo{rank}.pine'
    open(fn, 'w').write(pine)
    log.info(f'  {fn}: {len(b3t)} bls3-labels · {len(pu)+len(pdn)} PKs (all) · {len(tL)}L+{len(tS)}S trades')


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    det = BLDetect(db, lookback_hours=LOOKBACK_H, warmup_hours=12)
    base, ts, win_start, _, px = det._setup()
    oob = bny30_oob_side(base)
    gi, gd = pine_aligned_signals(base, db, GCA5M_RAW, gate=True, gate_bb=True, gate_k=True)
    raw_pk = np.zeros(len(ts), np.int8); raw_pk[gi] = gd                     # gated → trades
    ai, ad = pine_aligned_signals(base, db, GCA5M_RAW, gate=False)           # ungated → arrows
    pk_all = np.zeros(len(ts), np.int8); pk_all[ai] = ad
    db.disconnect()
    M = ts >= win_start
    tsm = ts[M].astype('int64'); oobm = oob[M]; pkm = raw_pk[M]; pkm_all = pk_all[M]; pxm = np.asarray(px, float)[M]
    pivots = sorted(find_pivots(pxm, SWING))
    fam_by = {f['name']: f for f in det._families}
    for rank, combo in COMBOS:
        vals = [int(x) for x in combo.split(',')]
        states = [det._run_family({**fam_by[n], 'k': {**fam_by[n]['k'], 'k_len': vals[k]}}, base, ts)[3]['state']
                  for k, n in enumerate(NAMES)]
        states_m = [s[M] for s in states]
        combined = _refold(states)[M]
        trades = walk(combined, pkm, pxm, pivots, PKLB)
        emit(rank, combo, vals, tsm, combined, states_m, pkm_all, oobm, trades)


if __name__ == '__main__':
    main()
