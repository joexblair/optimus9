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
import time, datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.analysis.jig import Jig                    # the test-jig facade (causal/score) — docs/jig.md
from optimus9.analysis.lr_v2 import fin_unlatch          # packaged finisher latch (not yet a jig endpoint)

PROX = 33; MID = 50; SEAM = 300000; ARM_MAX = 1080     # arm-delay bound = 90min (knob)
WINDOW_H = 48; WARMUP_H = 24                            # trade window / warmup (hours)
hm = lambda t: time.strftime('%m-%d %H:%M', time.gmtime(int(t) / 1000))


def main():
    end = int(dtm.datetime(2026, 7, 7, 20, 0, tzinfo=timezone.utc).timestamp() * 1000)   # PINNED window end (reproducible A/B)
    J = Jig(end, hours=WINDOW_H, warmup=WARMUP_H, overrides={'s10r': (600, ('k', 6, 6, 5, 'hl2'), 'emerging')})
    cfg = J.cfg; HI, LO = J.hi, J.lo; ts = J.ts; px = J.px; n = J.n
    now = end; cutoff = now - WINDOW_H * 3600 * 1000
    L = {k: J.causal.line(k) for k in ('s2m', 's3r', 's4r', 's2M', 's5M', 's7M', 's5m', 's10r', 's5r')}
    q15h, q15l = J.causal.finishers('s15')
    q30h, q30l = J.causal.finishers('s30')
    pred10 = J.causal.predict(L['s10r'], L['s5m'], L['s5M'])
    pred5 = J.causal.predict(L['s5r'], L['s5m'], L['s5M'])         # arm-delay: s5r continuation
    rev5 = J.causal.reversal(L['s5M'], cfg.arm_wob)               # s5Mage reversal (experimental)
    s2sign = J.causal.sign('s2m')
    s5sign = J.causal.sign('s5m')
    ts_c, s10c = J.causal.coarse('s10r', SEAM); _, s5rc = J.causal.coarse('s5r', SEAM)

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

    def exit_walk(e, side, mode):
        # exit routes (your spec): predict s10r at the s5m-breach->s30a+s15a stage. R1(predict TRUE)=watch s10r, exit on
        # stall/curl -> favourable s15a. R2(predict FALSE)=when s5r curls -> s30a+s15a. mode='exclusive'=IF/ELSE (spec);
        # mode='race'=run both, earliest wins (the old bug).
        d = 1 if side == 'long' else -1
        exq = q15h if side == 'long' else q15l
        both = (q15h & q30h) if side == 'long' else (q15l & q30l)
        f15c, f30c = (q15h, q30h) if side == 'long' else (q15l, q30l)
        b2 = None; pos = e + 1
        while pos < n:
            b1 = next((k for k in range(pos, n) if s5sign[k] == d and s5sign[k - 1] != d), None)
            if b1 is None:
                break
            w1 = min(n, b1 + 43)
            a15 = np.flatnonzero(f15c[b1:w1]); a30 = np.flatnonzero(f30c[b1:w1])
            if a15.size and a30.size:
                b2 = b1 + int(max(a15[0], a30[0])); break
            pos = b1 + 1
        if b2 is None:
            return (None, 'no-exit', None)
        pt = next((k for k in range(b2, n) if pred10[k] == d), None)     # predict s10r TRUE (state) at/after the stage

        def route1():                                                   # R1: watch s10r -> stall/curl -> favourable s15a
            start = next((k for k in range(pt, n) if (L['s10r'][k] >= HI if d == 1 else L['s10r'][k] <= LO)), b2) if pt is not None else b2
            msk = ts_c >= ts[start]; tsc, s10 = ts_c[msk], s10c[msk]
            stall = {int(tsc[k]) for k in range(1, len(s10)) if (s10[k] <= s10[k - 1] if d == 1 else s10[k] >= s10[k - 1])}
            for st in sorted(J.causal.curl(tsc, s10, -d) | stall):
                x = next((k for k in range(int(np.searchsorted(ts, st)), n) if exq[k]), None)
                if x is not None:
                    return x
            return None

        def route2():                                                   # R2: s5r curl -> s30a+s15a
            msk = ts_c >= ts[b2]; tsc, s5r = ts_c[msk], s5rc[msk]
            for st in sorted(J.causal.curl(tsc, s5r, -d)):
                x = next((k for k in range(int(np.searchsorted(ts, st)), n) if both[k]), None)
                if x is not None:
                    return x
            return None

        if mode == 'exclusive':                                         # YOUR SPEC: predict-true -> R1 only, else R2 only
            if pt is not None:
                x = route1(); return (x, 's10r', b2) if x is not None else (None, 'no-exit', b2)
            x = route2(); return (x, 's5r', b2) if x is not None else (None, 'no-exit', b2)
        cand = []                                                       # OLD BUG: run both, earliest wins
        x1, x2 = route1(), route2()
        if x1 is not None:
            cand.append((x1, 's10r'))
        if x2 is not None:
            cand.append((x2, 's5r'))
        if cand:
            xx, ww = min(cand, key=lambda z: z[0]); return (xx, ww, b2)
        return (None, 'no-exit', b2)

    # build the entry set ONCE (lock OFF -> identical entries for both exit modes; isolates the exit variable)
    entries = []
    for i, side in ent:
        a = arm_delay(i, side)                                  # (a) arm-delay layered on the Mage-tide arm
        e = finish_entry(a, side)
        if e is None:
            continue
        okM = (L['s5M'][e] > MID and L['s7M'][e] > MID and L['s2M'][e] > MID) if side == 'long' \
            else (L['s5M'][e] < MID and L['s7M'][e] < MID and L['s2M'][e] < MID)   # re-validate confluence at entry
        if not okM:
            att['reval_fail'] = att.get('reval_fail', 0) + 1; continue
        entries.append((e, side))

    # ── entry quality via the jig (EXIT-INDEPENDENT): MAE/MFE to the next favourable swing + mfe_side, aligned to entries
    lr_ent = [(int(ts[e]), (1 if side == 'short' else -1), (1 if side == 'long' else -1), e) for e, side in entries]
    eq = J.score.entry_quality(lr_ent)                     # [(tms, dt, es, bd, mae, mfe, mfe_ok, mfe_side, px)]
    eq_mae = [r[4] for r in eq]; eq_mfe = [r[5] for r in eq]; eq_side = [int(r[7]) for r in eq]

    def run_mode(mode):
        out = []
        for e, side in entries:
            x, why, b2 = exit_walk(e, side, mode)
            if x is None:
                x = n - 1
            d = -1 if side == 'short' else 1
            seg = (px[e:x + 1] - px[e]) / px[e] * 100.0 * d
            mae_v = float(np.nanmin(seg)); mfe_v = float(np.nanmax(seg)); dur = round((ts[x] - ts[e]) / 60000)
            if b2 is not None and b2 > e:
                sd = (px[e:b2 + 1] - px[e]) / px[e] * 100.0 * d
                drift = round((ts[b2] - ts[e]) / 60000); maed = float(np.nanmin(sd))
            else:
                drift = 0; maed = 0.0
            out.append([hm(ts[e]), hm(ts[x]), side, dur, round(mae_v, 2), round(mfe_v, 2), why, drift, round(maed, 2), e, x])
        return out

    excl = run_mode('exclusive'); race = run_mode('race')

    def summ(name, tr):
        mae = np.array([t[4] for t in tr]); mfe = np.array([t[5] for t in tr]); dm = np.array([t[7] for t in tr])
        r1 = sum(1 for t in tr if t[6] == 's10r'); r2 = sum(1 for t in tr if t[6] == 's5r'); nx = sum(1 for t in tr if t[6] == 'no-exit')
        print("[%-21s] n=%d medMAE=%.2f medMFE=%.2f MFE/|MAE|=%.2f | R1(s10r)=%d R2(s5r)=%d no-exit=%d | MFE>=0.5%%:%d driftMed=%dm"
              % (name, len(tr), np.median(mae), np.median(mfe), np.median(mfe) / max(abs(np.median(mae)), 1e-9),
                 r1, r2, nx, int((mfe >= 0.5).sum()), int(np.median(dm))))

    print("=== tide wireframe A/B — PINNED %s -> %s (%dh) — lock OFF to isolate the exit ===" % (hm(cutoff), hm(now), WINDOW_H))
    print("entry funnel: %d Mage-tide signals -> arm-delayed=%d, finisher-miss[both=%d s15=%d s30=%d], reval-fail=%d -> %d entries"
          % (len(ent), att['ad_delayed'], att['miss_both'], att['miss15'], att['miss30'], att.get('reval_fail', 0), len(entries)))
    if eq:
        print("ENTRY QUALITY (exit-independent, to next swing): medMAE=%.2f medMFE=%.2f MFE/|MAE|=%.2f | opened-on-MFE-side %d/%d"
              % (np.median(eq_mae), np.median(eq_mfe), np.median(eq_mfe) / max(abs(np.median(eq_mae)), 1e-9), sum(eq_side), len(eq_side)))
    summ("NEW exclusive (spec)", excl)
    summ("OLD race (bug)", race)

    print("\n-- WORST-10 entries by ENTRY-QUALITY MAE (exit-independent, higher=worse; eMAE/mfeS same both modes; NEW vs OLD = the exit) --")
    print("%-11s %-5s %5s %4s | %-7s %6s %6s %-5s | %-7s %6s %6s %-5s"
          % ("entry", "side", "eMAE", "mfeS", "NEWout", "MAE", "MFE", "rte", "OLDout", "MAE", "MFE", "rte"))
    for k in sorted(range(len(entries)), key=lambda j: -eq_mae[j])[:10]:
        a_, b_ = excl[k], race[k]
        print("%-11s %-5s %5.2f %4d | %-7s %6.2f %6.2f %-5s | %-7s %6.2f %6.2f %-5s"
              % (a_[0], a_[2], eq_mae[k], eq_side[k], a_[1][6:], a_[4], a_[5], a_[6], b_[1][6:], b_[4], b_[5], b_[6]))

    onl = sum(1 for k in range(1, n) if ts[k] >= cutoff and pred10[k] == -1 and pred10[k - 1] != -1)
    onh = sum(1 for k in range(1, n) if ts[k] >= cutoff and pred10[k] == 1 and pred10[k - 1] != 1)
    print("\npredict-STATE onsets: LO=%d HI=%d | assume: lock OFF (A/B), floor=0 stall, MFE=hindsight ceiling, arm-delay wob=cfg.arm_wob" % (onl, onh))
    races = [(t[9], t[10], t[2], t[4], t[5], t[6], t[3]) for t in excl]   # pine = the NEW (spec) trades

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
