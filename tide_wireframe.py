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

    excl = run_mode('exclusive')                                # the spec exit (predict-true -> R1, else R2)
    si = lambda a, k: (int(a[k]) if np.isfinite(a[k]) else 0)
    pts = lambda k, d: ('T' if pred10[k] == d else 'F')

    # ── STANDARD REPORT (Joe 0707). MAE/MFE = ENTRY-QUALITY (to next swing, EXIT-INDEPENDENT); exit_route = context. ──
    def report(label, trades):
        print("=== %s ===" % label)
        print("window range:  %s -> %s" % (hm(cutoff), hm(now)))
        print("raw signals: %d | entries: %d | medMAE %.2f | medMFE %.2f | mfe side entry: %d"
              % (len(ent), len(entries), (np.median(eq_mae) if eq else 0), (np.median(eq_mfe) if eq else 0), sum(eq_side)))
        print("finisher-miss = %d (both=%d, s15=%d, s30=%d), confluence-lost=%d, arm-delayed=%d (delayed, not dropped)."
              % (att['miss_both'] + att['miss15'] + att['miss30'], att['miss_both'], att['miss15'], att['miss30'],
                 att.get('reval_fail', 0), att['ad_delayed']))
        print("\ntop 5 MAE trades\ndatetime | MAE | MFE | exit_route")
        for k in sorted(range(len(trades)), key=lambda j: -eq_mae[j])[:5]:
            print("%s | %.2f | %.2f | %s" % (trades[k][0], eq_mae[k], eq_mfe[k], trades[k][6]))
        print("\nbottom 5 MFE trades\ndatetime | MAE | MFE | exit_route")
        for k in sorted(range(len(trades)), key=lambda j: eq_mfe[j])[:5]:
            print("%s | %.2f | %.2f | %s" % (trades[k][0], eq_mae[k], eq_mfe[k], trades[k][6]))

    report("tide wireframe — strict s15a AND s30a finisher", excl)

    # ── auto-pine via jig.score.emit_labels (entry + exit labels; green=long / red=short) ──
    labels = []
    for t in excl:
        e, x = t[9], t[10]; side = t[2]; lng = side == 'long'; d = 1 if lng else -1
        labels.append({'ts': int(ts[e]), 'y': float(px[e]), 'green': lng, 'up': True,
                       'text': "%s IN %s\\ns3r%d s4r%d\\ns5M%d s7M%d s2M%d\\ns10r%d pred:%s"
                       % ('LONG' if lng else 'SHORT', hm(ts[e])[6:], si(L['s3r'], e), si(L['s4r'], e),
                          si(L['s5M'], e), si(L['s7M'], e), si(L['s2M'], e), si(L['s10r'], e), pts(e, d))})
        labels.append({'ts': int(ts[x]), 'y': float(px[x]), 'green': lng, 'up': False,
                       'text': "%s OUT %s %dm\\nMAE%.1f MFE%.1f\\ns10r%d s5r%d pred:%s"
                       % (t[6], hm(ts[x])[6:], t[3], t[4], t[5], si(L['s10r'], x), si(L['s5r'], x), pts(x, d))})
    npine = J.score.emit_labels(labels, "/home/joe/thecodes/tide_races.pine",
                                "tide races %s->%s (%dh)" % (hm(cutoff), hm(now), WINDOW_H))
    print("\n-> tide_races.pine (%d labels)" % npine)


if __name__ == "__main__":
    main()
