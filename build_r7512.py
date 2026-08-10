"""build_r7512 — bank s15r/s22r at 7|5|12 plus their momo states. Joe 0805.

WHY. Joe 0805: "wind the s15r and s22r configs down so that we receive more near-oob hits ...
apply 7|5|12". Current is R_SPEC[15] = k_len 10 | rsi 4 | stc 11, cloned to TF22 by
build_s46_lines.py:48. 7|5|12 is already your s3r/s4r convention (build_past50.py:62-64).

TWO VARIANTS THIS FEEDS (Joe 0805)
  A  SEPARATED  momo keeps 10|4|11 (the existing bank); the oob-hunting line is 7|5|12 (this bank)
  B  UNIFIED    7|5|12 on BOTH duties — momo states from THIS bank

So this file banks the LINES and the MOMO STATES on them. Variant A uses only the lines; variant B
uses both.

momo() is CALLED per bar, never copied — build_s46_lines.py:20. A second copy would fork
MOMO_WINDOW_MIN / CURL_ARC_MIN. vmomo.py exists and is vectorised, but the existing g15/g22 states
were produced by the per-bar call, so this matches them.

SCOPE. 07-24 -> 08-01 with 12 h warmup, mirroring build_r3.py. The s46_window rows run 07-27 ->
07-29 and the longest measured span from momo activation to the r extreme is 2,710 bars = 3.8 h.

    python3 build_r7512.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('RPL_TF_CEILING', '30')
import datetime as dt
import numpy as np

TAPE0 = dt.datetime(2026, 7, 24, tzinfo=dt.timezone.utc)
TAPE1 = dt.datetime(2026, 8, 1, tzinfo=dt.timezone.utc)
WARM_H = 12
TFS = (15, 22)
RSPEC = dict(k_len=7, rsi=5, stc=12, src='close')     # Joe 0805, Joe's notation k_len|rsi|stc
OUT = os.environ.get('CLAUDE_JOB_DIR', '/tmp') + '/tmp'
MS = lambda d: int(d.timestamp() * 1000)


def main():
    import build_exhv2 as X
    from optimus9.analysis.jig import Jig, kline
    ovr = {}
    for tf in TFS:
        ovr.update(kline('Wr%d' % tf, float(tf), **RSPEC))
    hrs = int((TAPE1 - TAPE0).total_seconds() / 3600) + WARM_H + 2
    print('7|5|12 build  %s -> %s   hours %d' % (TAPE0.strftime('%m-%d'), TAPE1.strftime('%m-%d'), hrs))
    with Jig(MS(TAPE1), hours=hrs, warmup=180, overrides=ovr) as j:
        ts = np.asarray(j.ts, np.int64)
        D = {'ts': ts,
             'evt': (j.W.base['volume'].to_numpy(dtype=float) > 0).astype(np.int8)}
        for tf in TFS:
            D['r%d' % tf] = np.asarray(j.W.line('Wr%d' % tf), float)
    lo = int(np.searchsorted(ts, MS(TAPE0)))
    D = {k: v[lo:] for k, v in D.items()}
    ts = D['ts']
    ST = {'none': 0, 'momo': 1, 'curl': 2, 'sideways': 3}
    for tf in TFS:
        r = D['r%d' % tf]
        for tag, dr in (('p', 1), ('n', -1)):
            s = np.zeros(len(ts), np.int8)
            for i in range(len(ts)):
                s[i] = ST.get(X.momo(r, dr, i)[0], 0)
            D['g%d_%s' % (tf, tag)] = s
            print('  g%d_%s  none %5.1f%%  momo %5.1f%%  curl %5.1f%%  sideways %5.1f%%'
                  % (tf, tag, 100 * (s == 0).mean(), 100 * (s == 1).mean(),
                     100 * (s == 2).mean(), 100 * (s == 3).mean()), flush=True)
    p = OUT + '/r7512.npz'
    np.savez_compressed(p, **D)
    u = lambda ms: dt.datetime.utcfromtimestamp(ms / 1000).strftime('%m-%d %H:%M:%S')
    print('  wrote %s' % p)
    print('  bars %d   %s -> %s' % (len(ts), u(int(ts[0])), u(int(ts[-1]))))
    for tf in TFS:
        v = D['r%d' % tf]
        print('  r%-3d finite %5.1f%%  min %6.2f  median %6.2f  max %6.2f'
              % (tf, 100 * np.isfinite(v).mean(), np.nanmin(v), np.nanmedian(v), np.nanmax(v)))


if __name__ == '__main__':
    main()
