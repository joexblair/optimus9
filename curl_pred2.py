"""curl_pred2 — ROC on s3r, event-sampled, delegated after an s15r handover. Joe 0804.

Joe 0804: "you may want to use ROC. you may want to use a LTF r to 'finish' the job: when s15r has
fallen below {sweep 20.0}, delegate the curl-pred to s3r. s3r's curl will be easier and faster to
detect if you reduce the sampling to 1 per pxs event".

WHY v1 FAILED (curl_pred.py): it fired on the FIRST bar of opposing curvature anywhere between momo
activation and the extreme, so it triggered ~38% into a median 811-bar move and left 504 bars to run.
v2 fixes that by NARROWING THE WINDOW rather than tuning the detector — nothing is tested until s15r
has already travelled to the handover level, so the remaining move is short by construction.

THE CHAIN
  1 ARM        momo or curl on s15/s22, same bias           (sw_momo_activated_ms, already banked)
  2 HANDOVER   s15r reaches HOFF, direction matched          dr -1: r15 <= HOFF | dr +1: r15 >= 100-HOFF
  3 DELEGATE   from that bar, watch s3r on EVENT BARS ONLY   evt = volume > 0, 66.9% of the r3 range
  4 FIRE       ROC of s3r decelerates past -THR for WOB      consecutive EVENT samples

ROC is over ROC_N event samples: roc[i] = r3[e_i] - r3[e_i - ROC_N], in r-units per ROC_N events.
For dr -1 the line is falling so roc < 0; the turn is roc rising toward 0. THR = 0 fires exactly at
the zero-cross (i.e. AT the extreme); THR > 0 fires while still falling but decelerating, which is
what "just before the extrema" needs.

R_SPEC for TF3 is NOT chosen — r3a (R_SPEC[4]: k_len 7|rsi 6) and r3b (R_SPEC[15]: k_len 10|rsi 4)
are both swept.

Strictly causal: every index read is <= the test bar.

    python3 curl_pred2.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import datetime as dt
import numpy as np
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

JD = os.environ.get('CLAUDE_JOB_DIR', '/tmp') + '/tmp'
HOFF = (15.0, 20.0, 25.0, 30.0, 35.0)      # SWEEP: s15r handover level. Joe's example is 20.0
ROC_N = (3, 6, 12, 24)                     # SWEEP: ROC span, in EVENT samples
THR = (0.0, 0.5, 1.0, 2.0, 4.0)            # SWEEP: fire when roc >= -THR (0 = the zero-cross)
WOB = (1, 2, 3, 6)                         # SWEEP: consecutive event samples the condition must hold
VAR = ('r3a', 'r3b')                       # SWEEP: which R_SPEC TF3 uses
u = lambda ms: dt.datetime.utcfromtimestamp(ms / 1000).strftime('%m-%d %H:%M:%S')


def main():
    A = np.load(JD + '/lines_all.npz')
    B = np.load(JD + '/r3.npz')
    ts_a = A['ts'].astype(np.int64); r15 = A['r15'].astype(float)
    ts_b = B['ts'].astype(np.int64); evt = B['evt'].astype(bool)
    R3 = {v: B[v].astype(float) for v in VAR}

    db = DatabaseManager(**get_db_config()); db.connect()
    rows = db.execute('SELECT sw_n,sw_dr,sw_entry_ms,sw_exit_ms,sw_momo_activated_ms,'
                      'sw_momo_r_ext,sw_momo_r_ext_ms FROM s46_window ORDER BY sw_n', fetch=True)
    EXR = db.execute("SELECT sx_ms,sx_dir FROM s46_exit WHERE sx_line='s6x' AND sx_run_bars>=3 "
                     'ORDER BY sx_ms', fetch=True)
    db.disconnect()
    SX = {d_: np.array(sorted(int(r['sx_ms']) for r in EXR if int(r['sx_dir']) == d_), np.int64)
          for d_ in (1, -1)}
    live = [r for r in rows if r['sw_momo_activated_ms'] and r['sw_momo_r_ext_ms']]

    # ---- step 2: the handover bar per row, on the r15 grid, mapped onto the r3 grid ----
    HO = {}
    for h in HOFF:
        got = []
        for r in live:
            dr = int(r['sw_dr'])
            a = int(np.searchsorted(ts_a, int(r['sw_momo_activated_ms'])))
            xe = int(np.searchsorted(ts_a, int(r['sw_momo_r_ext_ms'])))
            if xe <= a:
                got.append(None); continue
            seg = r15[a:xe + 1]
            hit = (seg <= h) if dr < 0 else (seg >= 100.0 - h)
            w = np.flatnonzero(hit & np.isfinite(seg))
            got.append(int(ts_a[a + int(w[0])]) if len(w) else None)
        HO[h] = got
    print('armed rows %d' % len(live))
    print('  %-8s %6s   handover reached before the r extreme' % ('s15r <=', 'rows'))
    for h in HOFF:
        n = sum(1 for g in HO[h] if g is not None)
        print('  %-8.1f %6d   %.0f%%' % (h, n, 100.0 * n / len(live)))
    print()

    out = []
    for var in VAR:
        rr_all = R3[var]
        for h in HOFF:
            for rn in ROC_N:
                for th in THR:
                    for wb in WOB:
                        L1, L2 = [], []
                        for r, ho in zip(live, HO[h]):
                            if ho is None:
                                continue
                            dr = int(r['sw_dr'])
                            xe_ms = int(r['sw_momo_r_ext_ms'])
                            i0 = int(np.searchsorted(ts_b, ho))
                            i1 = int(np.searchsorted(ts_b, xe_ms))
                            if i1 <= i0 or i1 >= len(ts_b):
                                continue
                            # EVENT SAMPLES from the handover bar to the extreme bar
                            e = np.flatnonzero(evt[i0:i1 + 1]) + i0
                            if len(e) < rn + wb + 1:
                                continue
                            y = rr_all[e]
                            if not np.isfinite(y).all():
                                continue
                            roc = y[rn:] - y[:-rn]                 # r-units per rn events
                            ok = (roc >= -th) if dr < 0 else (roc <= th)
                            if wb > 1:                             # WOB consecutive event samples
                                c = np.convolve(ok.astype(int), np.ones(wb, int), 'valid') == wb
                                z = np.flatnonzero(c)
                                k = (int(z[0]) + wb - 1) if len(z) else None
                            else:
                                z = np.flatnonzero(ok)
                                k = int(z[0]) if len(z) else None
                            if k is None:
                                continue
                            fb = int(e[k + rn])                    # the firing bar, r3 grid
                            L1.append(int((xe_ms - ts_b[fb]) / 5000))
                            sm = SX[dr]
                            j = int(np.searchsorted(sm, int(ts_b[fb])))
                            if j < len(sm):
                                L2.append(int((sm[j] - ts_b[fb]) / 5000))
                        if len(L1) < 8:
                            continue
                        a1 = np.array(L1, float); a2 = np.array(L2, float)
                        out.append(dict(var=var, h=h, rn=rn, th=th, wb=wb, n=len(L1),
                                        cov=100.0 * len(L1) / len(live),
                                        med=float(np.median(a1)), p25=float(np.percentile(a1, 25)),
                                        p75=float(np.percentile(a1, 75)),
                                        neg=100.0 * float((a1 < 0).mean()),
                                        s6x=float(np.median(a2)) if len(a2) else float('nan')))
    print('FIRE LEAD, in 5 s bars. POSITIVE = fired BEFORE the r extreme. small positive is the target.')
    print('  %-5s %6s %4s %5s %4s %5s %6s %7s %7s %7s %6s %8s'
          % ('var', 's15r<=', 'rocN', 'thr', 'wob', 'n', 'cov%', 'p25', 'MEDIAN', 'p75', 'late%', 'lead-s6x'))
    for o in sorted(out, key=lambda z: (z['med'] < 0, abs(z['med'])))[:28]:
        print('  %-5s %6.1f %4d %5.1f %4d %5d %6.0f %7.0f %7.0f %7.0f %6.0f %8.0f'
              % (o['var'], o['h'], o['rn'], o['th'], o['wb'], o['n'], o['cov'],
                 o['p25'], o['med'], o['p75'], o['neg'], o['s6x']))


if __name__ == '__main__':
    main()
