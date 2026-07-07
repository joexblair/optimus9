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
from optimus9.analysis.lr_v2 import s_qualify, _mage_rev, fin_unlatch
from optimus9.compute.breaching_line import predict_breach, FENCE_HI, FENCE_LO
from sweep_eval import BASE_BIAS

PROX = 33; MID = 50; SEAM = 300000; ARM_MAX = 1080     # arm-delay bound = 90min (knob)
WINDOW_H = 48; WARMUP_H = 24                            # trade window / warmup (hours)
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
    now = int(time.time() * 1000); cutoff = now - WINDOW_H * 3600 * 1000
    ovr = {'s10r': (600, ('k', 6, 6, 5, 'hl2'), 'emerging')}
    W = bm.BiasWindow(dev, now, lookback=WINDOW_H + WARMUP_H, warmup=WARMUP_H, cfg=bm.BiasConfig(**BASE_BIAS), line_overrides=ovr)
    ts = np.asarray(W.ts); px = np.asarray(W.px, float); n = len(ts)
    L = {k: np.asarray(W.line(k), float) for k in ('s2m', 's3r', 's4r', 's2M', 's5M', 's7M', 's5m', 's10r', 's5r')}
    q15h, q15l = s_qualify(W, cfg, 's15m', 's15M', 's15r', cfg.s15r_lb)
    q30h, q30l = s_qualify(W, cfg, 's30m', 's30M', 's30r', cfg.s30r_lb)
    pred10 = predict_breach(L['s10r'], L['s5m'], L['s5M'], HI, LO, FENCE_HI, FENCE_LO)
    pred5 = predict_breach(L['s5r'], L['s5m'], L['s5M'], HI, LO, FENCE_HI, FENCE_LO)   # arm-delay: s5r continuation
    rev5 = np.asarray(_mage_rev(L['s5M'], cfg.arm_wob))                                 # s5Mage reversal (experimental)
    dev.disconnect()

    s2sign = np.where(L['s2m'] >= HI, 1, np.where(L['s2m'] <= LO, -1, 0))
    s5sign = np.where(L['s5m'] >= HI, 1, np.where(L['s5m'] <= LO, -1, 0))
    cm = (ts % SEAM) == 0
    ts_c = ts[cm]; s10c = L['s10r'][cm]; s5rc = L['s5r'][cm]

    ent = []
    for i in range(1, n):
        if ts[i] < cutoff:
            continue
        if s2sign[i] == -1 and s2sign[i - 1] != -1 and (L['s3r'][i] < PROX or L['s4r'][i] < PROX) and L['s5M'][i] > MID and L['s7M'][i] > MID and L['s2M'][i] > MID:
            ent.append((i, 'long'))
        if s2sign[i] == 1 and s2sign[i - 1] != 1 and (L['s3r'][i] > 100 - PROX or L['s4r'][i] > 100 - PROX) and L['s5M'][i] < MID and L['s7M'][i] < MID and L['s2M'][i] < MID:
            ent.append((i, 'short'))

    att = {'lock': 0, 'miss15': 0, 'miss30': 0, 'miss_both': 0, 'traded': 0, 'ad_delayed': 0}

    def finish_entry(i, side):
        # PACKAGED latch (lr_v2.fin_unlatch): both s15a+s30a in the box [arm-fin_lb, arm+fin_fwd] -> trade on the
        # NEXT same-side s15a at/after the arm (the arm bar isn't the entry). s15a/s30a themselves = s_qualify.
        q15, q30 = (q15l, q30l) if side == 'long' else (q15h, q30h)
        e = fin_unlatch(q15, q30, i, n, cfg.fin_lb, cfg.fin_fwd)
        if e is None:
            w0, w1 = max(0, i - cfg.fin_lb), min(n, i + cfg.fin_fwd + 1)
            h15, h30 = q15[w0:w1].any(), q30[w0:w1].any()
            att['miss_both' if not h15 and not h30 else ('miss30' if not h30 else 'miss15')] += 1
            return None
        return e

    def arm_delay(i, side):
        # (a) layer on the Mage-tide arm: if s5r predicts the faded move CONTINUES, hold until s5Mage OOBs (mv side)
        # and reverses (exhaustion) — enter at the top/bottom, not mid-momentum. else arm now. (s5Mage rev = experimental)
        mv = -1 if side == 'long' else 1                       # the faded move: long fades a down-dip, short an up-pop
        cap = min(n, i + ARM_MAX)
        oob = next((k for k in range(i, cap) if (L['s5M'][k] <= LO if mv == -1 else L['s5M'][k] >= HI)), None)
        if oob is None:
            return i                                           # no OOB extreme to exhaust -> arm now
        a = next((k for k in range(oob, cap) if rev5[k] == -mv), None)
        if a is None:
            return i
        if any(pred5[k] == mv for k in range(i, a)):           # continuation was predicted -> the delay is justified
            att['ad_delayed'] += 1; return a
        return i

    def exit_walk(e, side):
        # CASCADE-gated (Joe 0707): the exit monitor engages only after s5m favourable-breach -> s30a+s15a. From that
        # stage the s10r stall/curl runs REGARDLESS of predict; predict (STATE) only adds wait-for-s10r-breach.
        # s5r-curl races -> s30a+s15a. earliest wins. no cascade -> no exit (held).
        d = 1 if side == 'long' else -1                                  # favourable continuation dir
        exq = q15h if side == 'long' else q15l                           # exit at the favourable extreme
        both = (q15h & q30h) if side == 'long' else (q15l & q30l)
        f15c, f30c = (q15h, q30h) if side == 'long' else (q15l, q30l)    # cascade-stage finishers
        b2 = None; pos = e + 1
        while pos < n:
            b1 = next((k for k in range(pos, n) if s5sign[k] == d and s5sign[k - 1] != d), None)   # favourable s5m breach
            if b1 is None:
                break
            w1 = min(n, b1 + 43)
            a15 = np.flatnonzero(f15c[b1:w1]); a30 = np.flatnonzero(f30c[b1:w1])
            if a15.size and a30.size:
                b2 = b1 + int(max(a15[0], a30[0])); break               # s5m breach -> s30a+s15a stage reached
            pos = b1 + 1
        if b2 is None:
            return (None, 'no-exit', None)
        # EXCLUSIVE branches (Joe 0707 fix): predict TRUE -> s10-track ONLY (s5r-curl suppressed); else -> s5r-curl.
        pt = next((k for k in range(b2, n) if pred10[k] == d), None)     # predict STATE
        if pt is not None:                                              # predict TRUE -> s10r track only
            start = next((k for k in range(pt, n) if (L['s10r'][k] >= HI if d == 1 else L['s10r'][k] <= LO)), b2)
            msk = ts_c >= ts[start]; tsc, s10 = ts_c[msk], s10c[msk]
            stall = {int(tsc[k]) for k in range(1, len(s10)) if (s10[k] <= s10[k - 1] if d == 1 else s10[k] >= s10[k - 1])}
            for st in sorted(curl_seams(tsc, s10, -d) | stall):
                x = next((k for k in range(int(np.searchsorted(ts, st)), n) if exq[k]), None)
                if x is not None:
                    return (x, 's10mon', b2)
            return (None, 'no-exit', b2)
        msk = ts_c >= ts[b2]; tsc, s5r = ts_c[msk], s5rc[msk]           # predict FALSE -> s5r-curl only
        for st in sorted(curl_seams(tsc, s5r, -d)):
            x = next((k for k in range(int(np.searchsorted(ts, st)), n) if both[k]), None)
            if x is not None:
                return (x, 's5rcurl', b2)
        return (None, 'no-exit', b2)

    trades = []; races = []; open_until = -1
    for i, side in ent:
        if i <= open_until:
            att['lock'] += 1; continue
        a = arm_delay(i, side)                                  # (a) arm-delay layered on the Mage-tide arm
        e = finish_entry(a, side)
        if e is None:
            continue
        # re-validate the Mage-tide confluence AT THE ENTRY (leg may have travelled since the arm — Joe 0707)
        okM = (L['s5M'][e] > MID and L['s7M'][e] > MID and L['s2M'][e] > MID) if side == 'long' \
            else (L['s5M'][e] < MID and L['s7M'][e] < MID and L['s2M'][e] < MID)
        if not okM:
            att['reval_fail'] = att.get('reval_fail', 0) + 1; continue
        x, why, b2 = exit_walk(e, side)
        if x is None:
            x = n - 1
        att['traded'] += 1
        d = -1 if side == 'short' else 1
        seg = (px[e:x + 1] - px[e]) / px[e] * 100.0 * d
        if not seg.size:
            continue
        mae_v = float(np.nanmin(seg)); mfe_v = float(np.nanmax(seg)); dur = round((ts[x] - ts[e]) / 60000)
        # drift window [entry, b2] vs monitored [b2, exit]
        if b2 is not None and b2 > e:
            sd = (px[e:b2 + 1] - px[e]) / px[e] * 100.0 * d
            drift_min = round((ts[b2] - ts[e]) / 60000); mae_drift = float(np.nanmin(sd))
        else:
            drift_min = 0; mae_drift = 0.0
        trades.append((hm(ts[e]), hm(ts[x]), side, dur, round(mae_v, 2), round(mfe_v, 2), why, drift_min, round(mae_drift, 2)))
        races.append((e, x, side, mae_v, mfe_v, why, dur))
        open_until = x

    print("=== tide wireframe — last %dh — %d entries qualified ===" % (WINDOW_H, len(ent)))
    print("attrition: lock=%d  finisher-miss[both=%d s15=%d s30=%d]  arm-delayed=%d  reval-fail=%d  -> traded=%d"
          % (att['lock'], att['miss_both'], att['miss15'], att['miss30'], att['ad_delayed'], att.get('reval_fail', 0), att['traded']))
    print("%-11s %-11s %-5s %5s %7s %7s %-9s %6s %8s" % ("entry", "exit", "side", "min", "MAE%", "MFE%", "path", "driftM", "MAEdrift"))
    for r in trades:
        print("%-11s %-11s %-5s %5s %7s %7s %-9s %6s %8s" % r)
    if trades:
        mae = np.array([t[4] for t in trades]); mfe = np.array([t[5] for t in trades])
        dm = np.array([t[7] for t in trades]); mad = np.array([t[8] for t in trades])
        np10 = sum(1 for t in trades if t[6] == 's10mon')
        # how much of each trade's MAE happened DURING the unmonitored drift window:
        share = [abs(t[8]) / abs(t[4]) for t in trades if t[4] < 0]
        print("\nmedian MAE=%.2f  median MFE=%.2f  MFE/|MAE|=%.2f  | s10mon=%d s5rcurl=%d  | MFE>=0.5%%: %d/%d"
              % (np.median(mae), np.median(mfe), np.median(mfe) / max(abs(np.median(mae)), 1e-9),
                 np10, len(trades) - np10, int((mfe >= 0.5).sum()), len(trades)))
        print("DRIFT WINDOW [entry->b2]: median %d min unmonitored; median %.0f%% of each trade's MAE lands in it"
              % (int(np.median(dm)), 100 * float(np.median(share)) if share else 0))
    onl = [int(ts[k]) for k in range(1, n) if ts[k] >= cutoff and pred10[k] == -1 and pred10[k - 1] != -1]
    onh = [int(ts[k]) for k in range(1, n) if ts[k] >= cutoff and pred10[k] == 1 and pred10[k - 1] != 1]
    print("\npredict-STATE onsets (last %dh):" % WINDOW_H)
    print("  LO (down/short-fuel): " + " ".join(hm(t)[6:] for t in onl))
    print("  HI (up/long-fuel):    " + " ".join(hm(t)[6:] for t in onh))
    print("""
--- WIREFRAME ASSUMPTIONS (flag any misread) ---
1. entry = Mage-tide arm (s2m breach + s3r|s4r oversold + s5M&s7M&s2M same side of MID) -> ARM-DELAY (if s5r predicts
   the faded move continues, hold to s5Mage OOB+reverse; s5Mage-rev wob=cfg.arm_wob, EXPERIMENTAL) -> finisher (both
   s15a+s30a; lookback->arm, else walk fwd 2x30s).
2. lock ≈ sequential no-overlap. NOT the full opposing-arm latch.
3. exit CASCADE-gated: s5m favourable-breach -> s30a+s15a stage; from there s10r stall/curl runs regardless of predict
   (predict STATE only adds wait-for-s10r-breach). s5r-curl races -> s30a+s15a. no cascade -> no exit (held).
4. floor knob = 0 (higher-or-flat = stall — hair-trigger; the real knob loosens it). curl = coarse causal, no OS gate.
5. MAE/MFE = signed favourable excursion entry->exit (%). MFE = hindsight ceiling (harness), not realised PnL.""")

    # ── pine emit: the races as labels (entry+exit, live values; green=long / red=short) ──
    si = lambda a, k: (int(a[k]) if np.isfinite(a[k]) else 0)
    pt = lambda k, d: ('T' if pred10[k] == d else 'F')          # s10r prediction state at bar k (favourable dir d)
    T = []; Y = []; TXT = []; UP = []; GRN = []
    for (e, x, side, mae, mfe, why, dur) in races:
        lng = side == 'long'; g = 'true' if lng else 'false'; d = 1 if lng else -1
        T.append(int(ts[e])); Y.append(round(float(px[e]), 6))
        TXT.append("%s IN %s\\ns3r%d s4r%d\\ns5M%d s7M%d s2M%d\\ns10r%d pred:%s" % ('LONG' if lng else 'SHORT',
                    hm(ts[e])[6:], si(L['s3r'], e), si(L['s4r'], e), si(L['s5M'], e), si(L['s7M'], e),
                    si(L['s2M'], e), si(L['s10r'], e), pt(e, d)))
        UP.append('true'); GRN.append(g)
        T.append(int(ts[x])); Y.append(round(float(px[x]), 6))
        TXT.append("%s OUT %s %dm\\nMAE%.1f MFE%.1f\\ns10r%d s5r%d pred:%s" % (why, hm(ts[x])[6:], dur, mae, mfe,
                    si(L['s10r'], x), si(L['s5r'], x), pt(x, d)))
        UP.append('false'); GRN.append(g)
    ai = lambda v: "array.from(" + ", ".join(str(int(z)) for z in v) + ")"
    af = lambda v: "array.from(" + ", ".join(str(z) for z in v) + ")"
    as_ = lambda v: "array.from(" + ", ".join('"%s"' % z for z in v) + ")"
    ab = lambda v: "array.from(" + ", ".join(v) + ")"
    body = ('''//@version=5
indicator("tide races (last %dh) — entry+exit labels, green=long red=short", overlay = true, max_labels_count = 500)''' % WINDOW_H + '''
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
        label.new(array.get(tt, i), array.get(yy, i), array.get(tx, i), xloc = xloc.bar_time, color = col, style = stl, textcolor = color.white, size = size.normal)
''' % (ai(T), af(Y), as_(TXT), ab(UP), ab(GRN)))
    open("/home/joe/thecodes/tide_races.pine", "w").write(body)
    print("\n-> tide_races.pine  (%d labels = %d races x2)" % (len(T), len(races)))


if __name__ == "__main__":
    main()
