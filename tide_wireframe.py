"""tide_wireframe.py — ROUGH end-to-end wireframe of the tide-trigger entry + s10r exit (Joe 0707), last 24h.
Metric = MAE/MFE per trade. NOT the production producer — a skeleton to see the mechanics' shape. All simplifications
are printed at the end so Joe's eye can catch a misread. Causal/emerging throughout. Spec: docs/tide_exit_design.md.

ENTRY (long): s2m fresh LO-breach + (s3r|s4r < PROX) + (s5Mage & s7Mage > MID)  -> arm -> finisher-optimised entry.
  short = mirror (s2m HI-breach + s3r|s4r > 100-PROX + s5Mage & s7Mage < MID).
EXIT (short): re-test predict_breach(s10r,s5m,s5M) on each favourable s5m-breach after entry. TRUE(down) -> wait s10r
  breach, exit on next lo-s15a when s10r curls-up OR stops advancing (coarse 5min hl2). FALSE -> s5r curls-up ->
  exit on s30a+s15a. Both paths race; earliest exit wins. long = mirror.
"""
import sys; sys.path.insert(0, "/home/joe/thecodes")
import time
import numpy as np
import bias_machine as bm
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.lr import lr_config
from optimus9.analysis.lr_v2 import s_qualify
from optimus9.compute.breaching_line import predict_breach, FENCE_HI, FENCE_LO
from sweep_eval import BASE_BIAS

PROX = 33; MID = 50; SEAM = 300000
hm = lambda t: time.strftime('%m-%d %H:%M', time.gmtime(int(t) / 1000))


def curl_seams(ts_c, c, direction):
    out = set()
    for k in range(2, len(c)):
        if direction == 1 and c[k - 1] < c[k] and c[k - 1] <= c[k - 2]:
            out.add(int(ts_c[k]))
        if direction == -1 and c[k - 1] > c[k] and c[k - 1] >= c[k - 2]:
            out.add(int(ts_c[k]))
    return out


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    cfg = lr_config(dev); HI, LO = cfg.hi, cfg.lo
    now = int(time.time() * 1000); cutoff = now - 24 * 3600 * 1000
    ovr = {'s10r': (600, ('k', 6, 6, 5, 'hl2'), 'emerging')}
    W = bm.BiasWindow(dev, now, lookback=48, warmup=24, cfg=bm.BiasConfig(**BASE_BIAS), line_overrides=ovr)
    ts = np.asarray(W.ts); px = np.asarray(W.px, float); n = len(ts)
    L = {k: np.asarray(W.line(k), float) for k in ('s2m', 's3r', 's4r', 's5M', 's7M', 's5m', 's10r', 's5r')}
    q15h, q15l = s_qualify(W, cfg, 's15m', 's15M', 's15r', cfg.s15r_lb)
    q30h, q30l = s_qualify(W, cfg, 's30m', 's30M', 's30r', cfg.s30r_lb)
    pred10 = predict_breach(L['s10r'], L['s5m'], L['s5M'], HI, LO, FENCE_HI, FENCE_LO)
    dev.disconnect()

    s2sign = np.where(L['s2m'] >= HI, 1, np.where(L['s2m'] <= LO, -1, 0))
    s5sign = np.where(L['s5m'] >= HI, 1, np.where(L['s5m'] <= LO, -1, 0))
    cm = (ts % SEAM) == 0
    ts_c = ts[cm]; s10c = L['s10r'][cm]; s5rc = L['s5r'][cm]

    ent = []
    for i in range(1, n):
        if ts[i] < cutoff:
            continue
        if s2sign[i] == -1 and s2sign[i - 1] != -1 and (L['s3r'][i] < PROX or L['s4r'][i] < PROX) and L['s5M'][i] > MID and L['s7M'][i] > MID:
            ent.append((i, 'long'))
        if s2sign[i] == 1 and s2sign[i - 1] != 1 and (L['s3r'][i] > 100 - PROX or L['s4r'][i] > 100 - PROX) and L['s5M'][i] < MID and L['s7M'][i] < MID:
            ent.append((i, 'short'))

    att = {'lock': 0, 'miss15': 0, 'miss30': 0, 'miss_both': 0, 'traded': 0}

    def finish_entry(i, side):
        q15, q30 = (q15l, q30l) if side == 'long' else (q15h, q30h)
        w0, w1 = max(0, i - cfg.fin_lb), min(n, i + cfg.fin_fwd + 1)
        has15 = q15[w0:w1].any(); has30 = q30[w0:w1].any()
        if not has15 and not has30:
            att['miss_both'] += 1; return None
        if not has15:
            att['miss15'] += 1; return None
        if not has30:
            att['miss30'] += 1; return None
        return max(int(max(np.flatnonzero(q15[w0:w1])[-1], np.flatnonzero(q30[w0:w1])[-1])) + w0, i)

    def exit_walk(e, side):
        # Joe 0707: s10r stall/curl monitor runs ALWAYS (not gated by predict); predict is a continuous STATE. But
        # while predict is TRUE (continuation fuel) we HOLD the s10r exit until s10r has breached (wait-for-breach).
        # s5r-curl races as the alternate. earliest exit wins.
        d = -1 if side == 'short' else 1
        exq = q15l if side == 'short' else q15h
        both = (q15l & q30l) if side == 'short' else (q15h & q30h)
        cand = []
        # predict STATE: first predict-TRUE at/after entry; if present, s10r monitor only counts AFTER the s10r breach
        pt = next((k for k in range(e, n) if pred10[k] == d), None)
        if pt is not None:
            start = next((k for k in range(pt, n) if (L['s10r'][k] <= LO if d == -1 else L['s10r'][k] >= HI)), e)
        else:
            start = e
        # A: s10r stall/curl monitor (always-on), coarse from `start`
        msk = ts_c >= ts[start]; tsc, s10 = ts_c[msk], s10c[msk]
        stall = {int(tsc[k]) for k in range(1, len(s10)) if (s10[k] >= s10[k - 1] if d == -1 else s10[k] <= s10[k - 1])}
        for st in sorted(curl_seams(tsc, s10, -d) | stall):
            x = next((k for k in range(int(np.searchsorted(ts, st)), n) if exq[k]), None)
            if x is not None:
                cand.append((x, 's10mon')); break
        # B: s5r-curl, coarse from entry -> s30a+s15a
        msk = ts_c >= ts[e]; tsc, s5r = ts_c[msk], s5rc[msk]
        for st in sorted(curl_seams(tsc, s5r, -d)):
            x = next((k for k in range(int(np.searchsorted(ts, st)), n) if both[k]), None)
            if x is not None:
                cand.append((x, 's5rcurl')); break
        return min(cand, key=lambda z: z[0]) if cand else (None, 'no-exit')

    trades = []; races = []; open_until = -1
    for i, side in ent:
        if i <= open_until:
            att['lock'] += 1; continue
        e = finish_entry(i, side)
        if e is None:
            continue
        x, why = exit_walk(e, side)
        if x is None:
            x = n - 1
        att['traded'] += 1
        d = -1 if side == 'short' else 1
        seg = (px[e:x + 1] - px[e]) / px[e] * 100.0 * d
        if not seg.size:
            continue
        mae_v = float(np.nanmin(seg)); mfe_v = float(np.nanmax(seg)); dur = round((ts[x] - ts[e]) / 60000)
        trades.append((hm(ts[e]), hm(ts[x]), side, dur, round(mae_v, 2), round(mfe_v, 2), why))
        races.append((e, x, side, mae_v, mfe_v, why, dur))
        open_until = x

    print("=== tide wireframe — last 24h — %d entries qualified ===" % len(ent))
    print("attrition: lock=%d  finisher-miss[both=%d s15=%d s30=%d]  -> traded=%d"
          % (att['lock'], att['miss_both'], att['miss15'], att['miss30'], att['traded']))
    print("%-11s %-11s %-5s %5s %7s %7s  %s" % ("entry", "exit", "side", "min", "MAE%", "MFE%", "path"))
    for r in trades:
        print("%-11s %-11s %-5s %5s %7s %7s  %s" % r)
    if trades:
        mae = np.array([t[4] for t in trades]); mfe = np.array([t[5] for t in trades])
        np10 = sum(1 for t in trades if t[6] == 's10track')
        print("\nmedian MAE=%.2f  median MFE=%.2f  MFE/|MAE|=%.2f  | s10track=%d s5rcurl=%d  | MFE>=0.5%%: %d/%d"
              % (np.median(mae), np.median(mfe), np.median(mfe) / max(abs(np.median(mae)), 1e-9),
                 np10, len(trades) - np10, int((mfe >= 0.5).sum()), len(trades)))
    onl = [int(ts[k]) for k in range(1, n) if ts[k] >= cutoff and pred10[k] == -1 and pred10[k - 1] != -1]
    onh = [int(ts[k]) for k in range(1, n) if ts[k] >= cutoff and pred10[k] == 1 and pred10[k - 1] != 1]
    print("\npredict-STATE onsets (last 24h):")
    print("  LO (down/short-fuel): " + " ".join(hm(t)[6:] for t in onl))
    print("  HI (up/long-fuel):    " + " ".join(hm(t)[6:] for t in onh))
    print("""
--- WIREFRAME ASSUMPTIONS (flag any misread) ---
1. entry finisher: both q15+q30 (favourable side) within [arm-fin_lb, arm+fin_fwd]; entry = the later qualify, >=arm.
2. lock ≈ sequential no-overlap. NOT the full opposing-arm latch.
3. s10r stall/curl monitor ALWAYS on (coarse, hl2). predict = continuous STATE: if TRUE (fuel), the monitor is held
   until s10r breaches (wait-for-breach), else it runs from entry. s5r-curl races -> s30a+s15a. earliest wins.
4. floor knob = 0 (higher-or-flat = stall — hair-trigger; the real knob loosens it). curl = coarse causal, no OS gate.
5. MAE/MFE = signed favourable excursion entry->exit (%). MFE = hindsight ceiling (harness), not realised PnL.""")

    # ── pine emit: the races as labels (entry+exit, live values; green=long / red=short) ──
    si = lambda a, k: (int(a[k]) if np.isfinite(a[k]) else 0)
    T = []; Y = []; TXT = []; UP = []; GRN = []
    for (e, x, side, mae, mfe, why, dur) in races:
        lng = side == 'long'; g = 'true' if lng else 'false'
        T.append(int(ts[e])); Y.append(round(float(px[e]), 6))
        TXT.append("%s IN %s\\ns3r%d s4r%d\\ns5M%d s7M%d" % ('LONG' if lng else 'SHORT', hm(ts[e])[6:],
                    si(L['s3r'], e), si(L['s4r'], e), si(L['s5M'], e), si(L['s7M'], e)))
        UP.append('true'); GRN.append(g)
        T.append(int(ts[x])); Y.append(round(float(px[x]), 6))
        TXT.append("%s OUT %s %dm\\nMAE%.1f MFE%.1f\\ns10r%d s5r%d" % (why, hm(ts[x])[6:], dur, mae, mfe,
                    si(L['s10r'], x), si(L['s5r'], x)))
        UP.append('false'); GRN.append(g)
    ai = lambda v: "array.from(" + ", ".join(str(int(z)) for z in v) + ")"
    af = lambda v: "array.from(" + ", ".join(str(z) for z in v) + ")"
    as_ = lambda v: "array.from(" + ", ".join('"%s"' % z for z in v) + ")"
    ab = lambda v: "array.from(" + ", ".join(v) + ")"
    body = '''//@version=5
indicator("tide races (last 24h) — entry+exit labels, green=long red=short", overlay = true, max_labels_count = 500)
f_t()   => %s
f_y()   => %s
f_txt() => %s
f_up()  => %s
f_grn() => %s
if barstate.islast
    tt = f_t()
    yy = f_y()
    tx = f_txt()
    up = f_up()
    gr = f_grn()
    for i = 0 to array.size(tt) - 1
        col = array.get(gr, i) ? color.new(color.green, 15) : color.new(color.red, 15)
        stl = array.get(up, i) ? label.style_label_up : label.style_label_down
        label.new(array.get(tt, i), array.get(yy, i), array.get(tx, i), xloc = xloc.bar_time, color = col, style = stl, textcolor = color.white, size = size.small)
''' % (ai(T), af(Y), as_(TXT), ab(UP), ab(GRN))
    open("/home/joe/thecodes/tide_races.pine", "w").write(body)
    print("\n-> tide_races.pine  (%d labels = %d races x2)" % (len(T), len(races)))


if __name__ == "__main__":
    main()
