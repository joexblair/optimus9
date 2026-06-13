"""
emit_s30r_recon — Pine recon for s30r over the last 12h: the bls WALK (4-state, as a
coloured background band), the EXIT MASK fires (exit1/2/3, mask=7), and the raw 5s PKs
(green long / red short, ungated). Single line = s30r as configured (production
k_len/rsi/stc + s30M support exit). Swap params at S30R_OVERRIDE to chart a grind combo.

Walk is emitted as sparse state TRANSITIONS + a Pine pointer that carries the current
state forward (compiler-slim — no 8640-bar literal array).
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
from optimus9.orchestration.gate_signal_sweep import pine_aligned_signals
from logger import get_logger

LOOKBACK_H = 12
S30R_OVERRIDE = {'k_len': 5, 'rsi_len': 17, 'stc_len': 9, 'src': 'hlcc4'}   # 11-window champion
log = get_logger('S30rRecon')
Q = chr(34)


def arr(xs):
    return f"array.from({','.join(str(x) for x in xs)})" if xs else "array.new<int>(0)"


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    det = BLDetect(db, lookback_hours=LOOKBACK_H, warmup_hours=12)
    base, ts, win_start, _, _ = det._setup()
    s30r = [f for f in det._families if f['name'] == 's30r'][0]
    if S30R_OVERRIDE:
        s30r = {**s30r, 'k': {**s30r['k'], **S30R_OVERRIDE}}
    r = det._run_family(s30r, base, ts)[3]
    state = np.asarray(r['state']).astype(int)
    bdir = np.asarray(r['breach_dir']).astype(int)
    e1 = np.asarray(r['exit1']).astype(bool); e2 = np.asarray(r['exit2']).astype(bool); e3 = np.asarray(r['exit3']).astype(bool)
    ai, ad = pine_aligned_signals(base, db, GCA5M_RAW, gate=False)     # raw (ungated) PKs
    pk = np.zeros(len(ts), np.int8); pk[ai] = ad
    db.disconnect()

    M = ts >= win_start
    tsm = ts[M].astype('int64'); st = state[M]; bd = bdir[M]
    e1m, e2m, e3m = e1[M], e2[M], e3[M]; pkm = pk[M]; N = len(tsm)

    # bls walk → sparse transitions (+ side at breach)
    trans = [i for i in range(1, N) if st[i] != st[i - 1]]
    stt = [int(tsm[i]) for i in trans]
    stv = [int(st[i]) for i in trans]
    # labels at transitions: "s30r:N" with side arrow when entering a breach
    ltt = [int(tsm[i]) for i in trans]
    lls = []
    for i in trans:
        side = '↓' if bd[i] < 0 else ('↑' if bd[i] > 0 else '')
        lls.append(f's30r:{int(st[i])}{side if st[i] == 1 else ""}')
    e1t = [int(tsm[i]) for i in range(N) if e1m[i]]
    e2t = [int(tsm[i]) for i in range(N) if e2m[i]]
    e3t = [int(tsm[i]) for i in range(N) if e3m[i]]
    pu = [int(tsm[i]) for i in range(N) if pkm[i] == 1]
    pdn = [int(tsm[i]) for i in range(N) if pkm[i] == -1]
    span = (f"{datetime.fromtimestamp(tsm[0]/1000, tz=timezone.utc):%m-%d %H:%M}–"
            f"{datetime.fromtimestamp(tsm[-1]/1000, tz=timezone.utc):%m-%d %H:%M} UTC")
    cfg = S30R_OVERRIDE or {k: s30r['k'][k] for k in ('k_len', 'rsi_len', 'stc_len')}
    labs = f"array.from({','.join(Q + s + Q for s in lls)})" if lls else "array.new<string>(0)"

    # lines IN USE by the s30r machine (the walk + exits) — so the chart says what to apply on TV
    def _fmt(c):
        return (f"K len{c['k_len']} rsi{c['rsi_len']} stc{c['stc_len']} src={c['src']} {c['tf_seconds']}s"
                if c.get('kind') == 'k' else
                f"BB len{c['bb_len']} mult{c['bb_mult']} src={c['src']} {c['tf_seconds']}s")
    inuse = [('s30r breach', s30r['k'])]
    for role, key in (('pred mini', 'predictor_min'), ('pred Major', 'predictor_maj'),
                      ('exit support', 'exit_support'), ('exit3 support', 'exit3_support')):
        if s30r.get(key):
            inuse.append((role, s30r[key]))
    tc = ['    table.cell(t,0,0,"line",text_color=color.white,bgcolor=color.new(color.gray,10),text_size=size.small)',
          '    table.cell(t,1,0,"apply on TV  (OOB 85/15)",text_color=color.white,bgcolor=color.new(color.gray,10),text_size=size.small)']
    for i, (role, c) in enumerate(inuse):
        tc.append(f'    table.cell(t,0,{i+1},"{role}",text_color=color.silver,text_size=size.small)')
        tc.append(f'    table.cell(t,1,{i+1},"{_fmt(c)}",text_color=color.aqua,text_size=size.small)')
    tcells = '\n'.join(tc)

    pine = f'''//@version=5
// s30r recon — bls walk · exit mask (1/2/3) · raw 5s PKs   |   {span}
// s30r cfg: {cfg}   (12h · {N} bars)
indicator("s30r recon — walk·exit·pk", overlay=true, max_labels_count=500)
showWalk = input.bool(true, "bls walk band (1 ylw · 2 org · 3 lime)")
showExit = input.bool(true, "exit mask fires (x1/x2/x3)")
showPk   = input.bool(true, "raw 5s PKs (green long / red short)")
showCfg  = input.bool(true, "lines-in-use table (top-right)")
var table t = table.new(position.top_right, 2, {len(inuse)+1}, border_width=1, frame_color=color.gray, frame_width=1)
if showCfg and barstate.islast
{tcells}
ms = int(time)
stt = {arr(stt)}
var int[] stv = {arr(stv)}
ltt = {arr(ltt)}
var string[] lls = {labs}
e1 = {arr(e1t)}
e2 = {arr(e2t)}
e3 = {arr(e3t)}
pu = {arr(pu)}
pd = {arr(pdn)}
// carry the bls state forward across sparse transitions
var int cur = {int(st[0])}
var int si = 0
while si < array.size(stt)
    if array.get(stt, si) > ms
        break
    cur := array.get(stv, si)
    si += 1
bgcolor(showWalk and cur==1 ? color.new(color.yellow, 80) : showWalk and cur==2 ? color.new(color.orange, 78) : showWalk and cur==3 ? color.new(color.lime, 80) : na, title="bls walk")
// state-transition labels
if array.includes(ltt, ms)
    li = array.indexof(ltt, ms)
    label.new(bar_index, high, array.get(lls, li), color=color.new(color.gray, 30), textcolor=color.white, style=label.style_label_down, size=size.small)
// exit mask fires
plotshape(showExit and array.includes(e1, ms), style=shape.xcross,  location=location.abovebar, color=color.aqua,   size=size.tiny, title="exit1")
plotshape(showExit and array.includes(e2, ms), style=shape.xcross,  location=location.abovebar, color=color.fuchsia, size=size.tiny, title="exit2")
plotshape(showExit and array.includes(e3, ms), style=shape.diamond, location=location.abovebar, color=color.white,   size=size.tiny, title="exit3 (complete)")
// raw 5s PKs
plotshape(showPk and array.includes(pu, ms), style=shape.triangleup,   location=location.belowbar, color=color.new(color.green, 0), size=size.tiny, title="pk long")
plotshape(showPk and array.includes(pd, ms), style=shape.triangledown, location=location.abovebar, color=color.new(color.red, 0),   size=size.tiny, title="pk short")
'''
    tag = f"k{cfg['k_len']}r{cfg['rsi_len']}s{cfg['stc_len']}"
    fn = f'/home/joe/thecodes/s30r_recon_{tag}.pine'
    open(fn, 'w').write(pine)
    log.info(f'{fn}: {len(trans)} transitions · exits {len(e1t)}/{len(e2t)}/{len(e3t)} (1/2/3) · '
             f'{len(pu)+len(pdn)} PKs · {N} bars ({span})')


if __name__ == '__main__':
    main()
