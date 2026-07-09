"""exit_curl_ab.py — A/B the exit cascade: current (gate s7r BREACH, unlatch s5r slope-flip) vs the coarse-curl
variant (gate s7r breach-then-OOB-curl, unlatch s5r coarse-curl), Joe 0708. Both s7r+s5r use the jig coarse-curl
(sample emerging at a fixed seam, peak/trough one seam after). Sweep the seams (s7r gate {105,210}s · s5r unlatch
{75,150}s). Scored on MAE/MFE + win, but the ARBITER is the v2_walk compounding PnL. Baseline is validated to
reproduce lr_exit_v2 exactly before any sweep. Writes the report to the Telegram stop-hook file.
Run:  python3 exit_curl_ab.py"""
import datetime as dtm
from datetime import timezone
import os
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
import bias_machine as bm
from optimus9.analysis.lr import lr_config
from sweep_eval import BASE_BIAS
from optimus9.analysis.lr_v2 import (v2_walk_ad, lr_exit_v2, strand_rescue, _finish, _finisher_signal, _slope_flip)

SPAN_D = 42
START, LEV, MAX_LOT, COST = 500.0, 5.0, 66000, 0.20
GATE_SEAMS = [60000, 105000, 210000]    # s7r: 1min, 1.75min, 3.5min  (60 = finer, off-TF per Joe)
UNLATCH_SEAMS = [40000, 75000, 150000]  # s5r: 40s, 1.25min, 2.5min   (40 = finer, off-TF)
SUM_FILE = os.path.expanduser("~/.claude/hooks/last_summary.txt")


def coarse_curl(ts, vals, seam, direction, with_val=False):
    """Mirror of jig.causal.curl on jig.causal.coarse: sample the EMERGING line at `seam`, then a causal
    peak(dir=-1)/trough(dir=+1) fires one seam AFTER the turn. Returns {ts:turnval} or {ts}."""
    mask = (ts % seam) == 0
    ts_c = ts[mask]; c = np.asarray(vals, float)[mask]
    out = {} if with_val else set()
    for k in range(2, len(c)):
        hit = (direction == 1 and c[k - 1] < c[k] and c[k - 1] <= c[k - 2]) or \
              (direction == -1 and c[k - 1] > c[k] and c[k - 1] >= c[k - 2])
        if hit:
            if with_val:
                out[int(ts_c[k])] = float(c[k - 1])
            else:
                out.add(int(ts_c[k]))
    return out


def curl_exit(W, cfg, entries, gate_mode, unlatch_mode, seam_gate, seam_unlatch, gate_fam='s7', tp=None, trail=None, trail_arm=0.0):
    """lr_exit_v2 (predict off) with the gate + unlatch signals swappable. gate_mode: breach | curl (breach then
    s7r OOB coarse-curl). unlatch_mode: flip | curl (s5r coarse-curl). tp = take-profit % (limit fill at +tp).
    trail = trailing-stop %: once in profit, track the peak favourable excursion and exit `trail` below it — rides
    winners (the level follows the peak up) and cuts on a `trail` pullback. All checked each bar; first hit wins."""
    ts, px, n = np.asarray(W.ts), W.px, len(W.ts)
    hi, lo = cfg.hi, cfg.lo
    s5m, s5r = W.line('s5m'), W.line('s5r')
    gr = W.line(f'{gate_fam}r')
    rev5 = _slope_flip(s5r)
    s30hi, s30lo = _finisher_signal(W, cfg, 's30M', 's30m', 's30r', 19, 30)
    s15hi, s15lo = _finisher_signal(W, cfg, 's15M', 's15m', 's15r', 19, 15)
    gcurl = {d: coarse_curl(ts, gr, seam_gate, d, with_val=True) for d in (1, -1)} if gate_mode == 'curl' else None
    ucurl = {d: coarse_curl(ts, s5r, seam_unlatch, d) for d in (1, -1)} if unlatch_mode == 'curl' else None
    rows = []
    for tms, es, bd, tj in entries:
        entry_px = float(px[tj]); arm = gate = unlatch = xk = None; breached = False; peak = 0.0
        ek = None; reason = 'end'
        for k in range(tj + 1, n):
            fav = (px[k] - entry_px) / entry_px * 100.0 * bd
            if fav <= -cfg.sl:
                ek = k; reason = 'SL'; break
            if tp is not None and fav >= tp:
                ek = k; reason = 'TP'; break
            peak = max(peak, fav)
            if trail is not None and peak >= trail_arm and peak > 0 and (peak - fav) >= trail:
                ek = k; reason = 'TRAIL'; break                  # only trails once peak reached +trail_arm%
            if xk is not None:
                if k >= xk:
                    ek = k; reason = 'exit'; break
            elif arm is None:
                if (s5m[k] <= lo) if bd == -1 else (s5m[k] >= hi):
                    arm = k
            elif gate is None:
                s7b = (gr[k] <= lo) if bd == -1 else (gr[k] >= hi)
                if gate_mode == 'breach':
                    if s7b:
                        gate = k
                else:                                            # breach THEN s7r OOB coarse-curl
                    if s7b:
                        breached = True
                    tk = int(ts[k])
                    if breached and tk in gcurl[es]:
                        tv = gcurl[es][tk]
                        if (tv >= hi) if bd == 1 else (tv <= lo):
                            gate = k
            elif unlatch is None:
                hit = (rev5[k] == es) if unlatch_mode == 'flip' else (int(ts[k]) in ucurl[es])
                if hit:
                    unlatch = k
                    xk = _finish(s30hi, s30lo, s15hi, s15lo, bd, arm, unlatch, n)
                    if xk is not None and k >= xk:
                        ek = k; reason = 'exit'; break
        if ek is None:
            ek = n - 1
        exit_px = float(px[ek])
        ret = tp if reason == 'TP' else ((peak - trail) if reason == 'TRAIL'
              else (-cfg.sl if reason == 'SL' else (exit_px - entry_px) / entry_px * 100.0 * bd))
        rows.append((tms, int(ts[ek]), bd, entry_px, exit_px, round(ret, 3), reason))
    return rows


def trades_from(W, lr, ent, exits):
    resc = strand_rescue(W, lr, ent, exits)
    ts, px = np.asarray(W.ts), np.asarray(W.px, float)
    tr = []
    for (tms, exms, bd, epx, xpx, r, reason) in resc:
        e = int(np.searchsorted(ts, int(tms))); x = int(np.searchsorted(ts, int(exms)))
        if x <= e or x >= len(px):
            continue
        seg = (px[e:x + 1] - px[e]) / px[e] * 100.0 * bd
        ret = float(r) if reason in ('TP', 'TRAIL') else float(seg[-1])   # TP/trail fill at their level; else close
        tr.append((float(px[e]), ret, float(np.nanmin(seg)), float(np.nanmax(seg))))
    return tr


def pnl(tr, stop):
    acct = START
    for (epx, ret, mae, mfe) in tr:
        if acct <= 0:
            return 0.0
        r = -stop if (stop is not None and mae <= -stop) else ret
        acct += min(MAX_LOT, acct * LEV / epx) * epx * (r - COST) / 100.0
    return max(acct, 0.0)


def score(tr):
    rets = np.array([t[1] for t in tr]); maes = np.array([t[2] for t in tr]); mfes = np.array([t[3] for t in tr])
    best = max(pnl(tr, s) for s in [None] + [round(0.2 + 0.05 * k, 2) for k in range(37)])
    return dict(n=len(tr), win=float(np.mean(rets > COST)), mae_med=float(np.median(maes)),
                mfe_med=float(np.median(mfes)), nostop=pnl(tr, None), best=best)


def main():
    dev = DatabaseManager(**get_db_config()); dev.connect()
    now = int(dtm.datetime.now(timezone.utc).timestamp() * 1000)
    W = bm.BiasWindow(dev, now, lookback=SPAN_D * 24, warmup=48, cfg=bm.BiasConfig(**BASE_BIAS), lean=True)
    lr = lr_config(dev)
    ent = v2_walk_ad(W, lr)

    # VALIDATION GATE: curl_exit(breach,flip) must reproduce lr_exit_v2(predict off) exactly.
    base_ref = lr_exit_v2(W, lr, ent, predict=False)
    base_new = curl_exit(W, lr, ent, 'breach', 'flip', GATE_SEAMS[0], UNLATCH_SEAMS[0])
    if base_ref != base_new:
        print("VALIDATION FAILED: curl_exit baseline != lr_exit_v2 — abort"); dev.disconnect(); return
    print("baseline validated (curl_exit==lr_exit_v2). entries=%d over %dw" % (len(ent), SPAN_D // 7))

    GW, UW = 105000, 40000                              # curl winner from the seam sweep
    runs = [('BASELINE breach+flip', 'breach', 'flip', {}),
            ('curl@105/40 no-trail', 'curl', 'curl', {})]
    for ta in (0.3, 0.5, 0.7):                          # only trail once peak reaches +ta%
        for tr in (0.3, 0.5, 0.7):
            runs.append(('curl arm%.1f/trail%.1f' % (ta, tr), 'curl', 'curl', {'trail_arm': ta, 'trail': tr}))

    rows = []
    for label, gm, um, kw in runs:
        s = score(trades_from(W, lr, ent, curl_exit(W, lr, ent, gm, um, GW, UW, **kw)))
        rows.append((label, s))
    base_pnl = rows[0][1]['best']
    rows_sorted = sorted(rows, key=lambda r: -r[1]['best'])

    lines = ["EXIT TRAIL sweep on curl-winner gate@105/s5r@40 — v2_walk %dw (%d entries) | arbiter=PnL(best-stop)" % (SPAN_D // 7, len(ent)),
             "%-24s %5s %6s %7s %7s %9s" % ("variant", "n", "win%", "MAEmd", "MFEmd", "PnL$")]
    for label, s in rows_sorted:
        tag = " *base" if label.startswith('BASELINE') else " %+.1f%%" % (100 * (s['best'] / base_pnl - 1))
        lines.append("%-24s %5d %5.1f %7.3f %7.3f %9.0f%s" %
                     (label[:24], s['n'], 100 * s['win'], s['mae_med'], s['mfe_med'], s['best'], tag))
    win = rows_sorted[0]
    lines.append("WINNER: %s  PnL $%.0f  (baseline $%.0f, %+.1f%%)" %
                 (win[0], win[1]['best'], base_pnl, 100 * (win[1]['best'] / base_pnl - 1)))
    report = "\n".join(lines)
    print("\n" + report)
    open(SUM_FILE, "w").write(report)
    dev.disconnect()


if __name__ == "__main__":
    main()
