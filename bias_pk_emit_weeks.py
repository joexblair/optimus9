"""
bias_pk_emit_weeks.py — emit two array-based Pine overlays, best vs worst week, for the +18106 config.

Config (the +18106 exit-sweep winner): trigger s6m (anchor on 6-min reversals) · s14M-vs50 gate ·
exit = opposite s30a+s30M wob with s12m AND s12r both OOB (with-r, exitTF12). 33K lots · 0.11% fee.
Emits TWO layers per chart:
  • pk UPDATES — every gated s6m reversal: BULL/BEAR/NEUT from s6r anchor-vs-floater (label above bar).
  • TRADES — entry→exit line (green win / red loss), entry L/S tag, exit $pnl. Entry = next aligned
    s30 wob after a BULL/BEAR update; exit = opposite s30 wob with s12m & s12r OOB (else eod).
Best week ends 2026-06-17 (+10598), worst ends 2026-05-18 (-4009).  → bias_pk_best.pine / _worst.pine.
Apply on a chart that HAS bars in the window (May → use a higher TF; TV drops 15s history that far back).
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import datetime as dtm
from datetime import timezone
import numpy as np
import logging
for n in ('BybitKlineClient', 'BLDetect', 'KlineLoader', 'DatabaseManager'):
    logging.getLogger(n).setLevel('ERROR')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.bl_detect import BLDetect
from optimus9.compute.indicator_computer import IndicatorComputer as IC

OOB_HI, OOB_LO, NEUTRAL_BAND, TRIG_TF, EXIT_TF, H = 85.0, 15.0, 2.2, 6, 12, 3600_000
COINS, FEE_RT = 33_000, 0.11
def sgn(v): return 1 if v >= OOB_HI else (-1 if v <= OOB_LO else 0)

def updates_for(end):
    db = DatabaseManager(**get_db_config()); db.connect()
    det = BLDetect(db, lookback_hours=168, warmup_hours=80)
    base, ts, ws, _, px = det._setup(end); db.disconnect()
    W1 = min(int(ts[-1]), end); W0 = W1 - 168 * H
    bclose = base['close'].to_numpy()
    def BB(fr, s, L, m): return IC.f_bb(IC.build_source(fr, s), L, m)
    def KK(fr, s, r, st, k): return IC.f_k(IC.build_source(fr, s), r, st, k)
    def AL(v, fr): return IC.align_to_base(v, fr, base)
    at = lambda t: int(np.searchsorted(ts, t, side='right')) - 1
    f7 = IC.resample(base, 420); s14M = AL(BB(f7, 'ohlc4', 74, 0.72), f7)
    f6r = IC.resample(base, 360); s6r = AL(KK(f6r, 'close', 6, 6, 5), f6r)
    f8 = IC.resample(base, TRIG_TF * 60); s8 = BB(f8, 'hlc3', 10, 0.4); t8 = f8['timestamp'].to_numpy() + TRIG_TF * 60_000
    fX = IC.resample(base, EXIT_TF * 60); sXm = AL(BB(fX, 'hlc3', 10, 0.4), fX); sXr = AL(KK(fX, 'close', 6, 6, 5), fX)
    MS = np.where(sXm >= OOB_HI, 1, np.where(sXm <= OOB_LO, -1, 0))   # s12m OOB side (exit gate)
    RS = np.where(sXr >= OOB_HI, 1, np.where(sXr <= OOB_LO, -1, 0))   # s12r OOB side (the "+r")
    # s30a + s30M wobslays (both sides) — entry & exit candidates
    f30 = IC.resample(base, 30); t30 = f30['timestamp'].to_numpy() + 30_000
    s30m_b = BB(f30, 'hlc3', 10, 0.40); s30M_b = BB(f30, 'ohlc4', 37, 0.72); s30r_b = KK(f30, 'close', 6, 6, 5)
    hw, lw = [], []
    for i in range(2, len(s30M_b)):
        a, b, c = s30M_b[i-2], s30M_b[i-1], s30M_b[i]
        if a != a or b != b or c != c: continue
        if a >= OOB_HI and c < b < a and s30m_b[i-2] >= OOB_HI and s30r_b[i-2] >= OOB_HI: sd = 1
        elif a <= OOB_LO and c > b > a and s30m_b[i-2] <= OOB_LO and s30r_b[i-2] <= OOB_LO: sd = -1
        else: continue
        tw = int(t30[i]); j = at(tw)
        if j >= 0: (hw if sd == 1 else lw).append((tw, j))
    hw.sort(); lw.sort()
    HT = np.array([t for t, j in hw]); HJ = np.array([j for t, j in hw])
    LT = np.array([t for t, j in lw]); LJ = np.array([j for t, j in lw])

    def s6rext(jr, S):
        bv = s6r[jr]
        for step in (-1, 1):
            k2 = jr
            while 0 <= k2 + step < len(s6r):
                v = s6r[k2 + step]
                if v != v: break
                if (S == -1 and v >= 50) or (S == 1 and v <= 50): break
                k2 += step
                if (S == 1 and v > bv) or (S == -1 and v < bv): bv = v
        return bv
    trigs = []
    for k in range(2, len(s8)):
        a, b, c = s8[k-2], s8[k-1], s8[k]
        if a != a or b != b or c != c: continue
        S = -1 if (b <= OOB_LO and b < a and b < c) else (1 if (b >= OOB_HI and b > a and b > c) else 0)
        if S == 0: continue
        rt = int(t8[k-1]); j = at(rt)
        if j >= 0: trigs.append(dict(t=rt, j=j, s=S, s6r=s6r[j]))
    g = {1: None, -1: None}
    for w in trigs:
        sd = w['s']; ok = (sd == 1 and w['s6r'] > 50) or (sd == -1 and w['s6r'] < 50)
        w['res'] = w['s6r'] if ok else g[sd]
        if ok: g[sd] = w['s6r']
    ups, last = [], {1: None, -1: None}
    for W in trigs:
        S = W['s']; flt = last[S]; last[S] = W
        if (s14M[W['j']] > 50.0) != (S == 1) or W['res'] is None or flt is None or not (W0 <= W['t'] <= W1): continue
        fv = s6rext(flt['j'], S)
        call = 'NEUT' if abs(W['res'] - fv) <= NEUTRAL_BAND else ('BULL' if W['res'] > fv else 'BEAR')
        ups.append(dict(t=W['t'], side=S, call=call, anc=round(W['res'], 1), flt=round(fv, 1),
                        px=round(float(bclose[W['j']]), 5)))
    # ── trades: entry = next aligned s30 wob after a BULL/BEAR update; exit = opposite s30 wob w/ s12m&s12r OOB ──
    trades, seen = [], set()
    for u in ups:
        if u['call'] == 'NEUT': continue
        bd = 1 if u['call'] == 'BULL' else -1
        ET, EJ = (HT, HJ) if -bd == 1 else (LT, LJ)            # entry side = -bd (BEAR→hi, BULL→lo)
        ei = int(np.searchsorted(ET, u['t'], side='right'))
        if ei >= len(EJ): continue
        ej = int(EJ[ei]); et = int(ET[ei])
        if ej in seen: continue
        seen.add(ej)
        XT, XJ = (HT, HJ) if bd == 1 else (LT, LJ)             # exit side = bd (opposite the entry)
        xi = int(np.searchsorted(XT, et, side='right')); xj = xt = None
        while xi < len(XJ):
            jj = int(XJ[xi])
            if MS[jj] == bd and RS[jj] == bd: xj = jj; xt = int(XT[xi]); break
            xi += 1
        eod = xj is None
        if eod: xj = len(px) - 1; xt = W1
        ep, xp = float(px[ej]), float(px[xj])
        pnl = COINS * ep * (bd * (xp - ep) / ep * 100 - FEE_RT) / 100.0
        trades.append(dict(et=et, ep=round(ep, 5), xt=xt, xp=round(xp, 5), bd=bd, pnl=pnl, eod=eod))
    return ups, trades, W0, W1

def emit(ups, trades, path, title):
    arr = lambda v: 'array.from(' + ', '.join(v) + ')'
    body = f'''//@version=5
// {title} — pk UPDATES + TRADES (trigger s6m · vs50 gate · exit s12m+s12r). EMITTED.
indicator("{title}", overlay = true, max_labels_count = 500, max_lines_count = 500)
// --- pk updates ---
t   = {arr([str(u['t']) for u in ups])}
pxv = {arr([f"{u['px']:.5f}" for u in ups])}
cl  = {arr(['"' + u['call'] + '"' for u in ups])}
sd  = {arr(['"' + ('HI' if u['side'] == 1 else 'LO') + '"' for u in ups])}
anc = {arr([f"{u['anc']:.1f}" for u in ups])}
flt = {arr([f"{u['flt']:.1f}" for u in ups])}
// --- entries (arrow: green up/below = long, red down/above = short) ---
et  = {arr([str(x['et']) for x in trades])}
ed  = {arr(['1' if x['bd'] == 1 else '-1' for x in trades])}
var bool done = false
if barstate.islast and not done
    done := true
    for i = 0 to array.size(t) - 1
        c   = array.get(cl, i)
        col = c == "BULL" ? color.new(color.green, 0) : c == "BEAR" ? color.new(color.red, 0) : color.new(color.gray, 0)
        ar  = c == "BULL" ? "▲BULL" : c == "BEAR" ? "▼BEAR" : "■NEUT"
        label.new(array.get(t, i), array.get(pxv, i), ar + " " + array.get(sd, i) + "\\na" + str.tostring(array.get(anc, i), "#.0") + " f" + str.tostring(array.get(flt, i), "#.0"), xloc = xloc.bar_time, yloc = yloc.price, style = label.style_label_down, color = col, textcolor = color.white, size = size.small)
    for i = 0 to array.size(et) - 1
        isL = array.get(ed, i) == 1
        label.new(array.get(et, i), 0.0, "", xloc = xloc.bar_time, yloc = isL ? yloc.belowbar : yloc.abovebar, style = isL ? label.style_arrowup : label.style_arrowdown, color = isL ? color.new(color.lime, 0) : color.new(color.red, 0), size = size.small)
'''
    open(path, 'w').write(body)

for lbl, y, mo, d in (('best', 2026, 6, 17), ('worst', 2026, 5, 18)):
    end = int(dtm.datetime(y, mo, d, 1, 24, tzinfo=timezone.utc).timestamp() * 1000)
    ups, trades, W0, W1 = updates_for(end)
    nb = sum(u['call'] == 'BULL' for u in ups); nr = sum(u['call'] == 'BEAR' for u in ups); nn = sum(u['call'] == 'NEUT' for u in ups)
    nt = len(trades); nw = sum(x['pnl'] > 0 for x in trades); neod = sum(x['eod'] for x in trades)
    net = sum(x['pnl'] for x in trades)
    path = f'/home/joe/thecodes/bias_pk_{lbl}.pine'
    emit(ups, trades, path, f'pk+trades {lbl} wk')
    wk = dtm.datetime.fromtimestamp(W1/1000, timezone.utc).strftime('%m%d')
    print(f'{lbl:>5} wk (end {wk}): {len(ups)} pk ({nb}B/{nr}b/{nn}N)  ·  {nt} trades {nw}W ({100*nw//max(nt,1)}%) '
          f'net ${net:+.0f} · {neod} eod  → {path}')
