"""build_r3 — bank s3r (and s3x/s3M) over the s46_window range. Joe 0804.

WHY. Joe 0804: "use a LTF r to finish the job: when s15r has fallen below {sweep 20.0}, delegate the
curl-pred to s3r. s3r's curl will be easier and faster to detect if you reduce the sampling to 1 per
pxs event". The line bank (build_s46_lines.py) is TFS = (15, 22, 30) — there is no r3.

SCOPE. NOT the full tape. The s46_window rows run 07-27 -> 07-29 and the longest measured span from
momo activation to the r extreme is 2,710 bars = 3.8 h, so 07-24 -> 08-01 covers every row plus its
forward span. A bb 37 at TF3 needs 37*3 = 111 min of lead-in, so the warmup here is generous.
Building one TF over 8 days is cheap; the 100 GB problem in build_s46_lines.py's docstring is a
TF30-over-75-days problem, not this.

R_SPEC FOR TF3 — BOTH VARIANTS BANKED, not chosen for you:
    r3a   R_SPEC[4]  = k_len 7  | rsi 6 | stc 11 | close   — the nearest existing rung to TF3
    r3b   R_SPEC[15] = k_len 10 | rsi 4 | stc 11 | close   — what build_s46_lines clones to 22 and 30
Sweep decides. They differ only in k_len and rsi.

    python3 build_r3.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('RPL_TF_CEILING', '30')
import datetime as dt
import numpy as np

TAPE0 = dt.datetime(2026, 7, 24, tzinfo=dt.timezone.utc)      # covers 07-27 entries + 3.8 h spans
TAPE1 = dt.datetime(2026, 8, 1, tzinfo=dt.timezone.utc)
WARM_H = 12                                                    # bb 37 @ TF3 needs 111 min; 12 h is ample
OUT = os.environ.get('CLAUDE_JOB_DIR', '/tmp') + '/tmp'
MS = lambda d: int(d.timestamp() * 1000)


def main():
    import build_exhv2 as X
    from optimus9.analysis.jig import Jig, bbline, kline
    XS, MSP = X.LINE_SPEC['x'][1], X.LINE_SPEC['M'][1]
    ovr = {}
    ovr.update(kline('Lr3a', 3.0, **X.R_SPEC[4]))              # k_len 7 | rsi 6 | stc 11
    ovr.update(kline('Lr3b', 3.0, **X.R_SPEC[15]))             # k_len 10 | rsi 4 | stc 11
    ovr.update(bbline('Lx3', 3.0, **XS))
    ovr.update(bbline('LM3', 3.0, **MSP))
    hrs = int((TAPE1 - TAPE0).total_seconds() / 3600) + WARM_H + 2
    print('r3 build  %s -> %s   hours %d  (warmup lead-in %d h)'
          % (TAPE0.strftime('%m-%d'), TAPE1.strftime('%m-%d'), hrs, WARM_H))
    with Jig(MS(TAPE1), hours=hrs, warmup=180, overrides=ovr) as j:
        ts = np.asarray(j.ts, np.int64)
        D = {'ts': ts,
             'r3a': np.asarray(j.W.line('Lr3a'), float),
             'r3b': np.asarray(j.W.line('Lr3b'), float),
             'x3': np.asarray(j.W.line('Lx3'), float),
             'M3': np.asarray(j.W.line('LM3'), float),
             'evt': (j.W.base['volume'].to_numpy(dtype=float) > 0).astype(np.int8)}
    lo = int(np.searchsorted(ts, MS(TAPE0)))                   # drop the warmup lead-in
    D = {k: v[lo:] for k, v in D.items()}
    p = OUT + '/r3.npz'
    np.savez_compressed(p, **D)
    u = lambda ms: dt.datetime.utcfromtimestamp(ms / 1000).strftime('%m-%d %H:%M:%S')
    print('  wrote %s' % p)
    print('  bars %d   %s -> %s' % (len(D['ts']), u(int(D['ts'][0])), u(int(D['ts'][-1]))))
    print('  evt %d = %.1f%%' % (D['evt'].sum(), 100 * D['evt'].mean()))
    for k in ('r3a', 'r3b', 'x3', 'M3'):
        v = D[k]; f = np.isfinite(v)
        print('  %-4s finite %5.1f%%   min %7.2f  median %7.2f  max %7.2f'
              % (k, 100 * f.mean(), np.nanmin(v), np.nanmedian(v), np.nanmax(v)))


if __name__ == '__main__':
    main()
