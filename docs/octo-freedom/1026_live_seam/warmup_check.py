"""warmup_check - is live_seam's window long enough for its 21 lines? 1026.

Joe 1026: *"validate the warmup length. we're maxing at TF12 so the cache shouldn't be too heavy -
there's notes about correct warmup sizing in the docs"*.

THE METHOD IS `1001_warmup.md`'s (0710's): build every line at load span S, all ending at the SAME
right edge, compare against a long reference at identical timestamps, report the worst |diff| over
the last hour of bars (720 bars at 5 s). The reference span is 2,268 h, the backtest Jig's span that
1001 used. The spans are 1001's columns. `px` is the global 5 s DEMA(close, 2) BiasWindow carries.

    python3 warmup_check.py '2026-10-26 21:15:05'
"""
import datetime as dt
import sys
import time

import numpy as np

import live_seam as LS

REF_H = 2268
SPANS = (14, 20, 28, 40, 56, 72, 104, 144)
LAST = 720


def build(db, ovr, end_ts, span_h):
    W = LS.bm.BiasWindow(db, int(end_ts) + LS.BAR_MS, lookback=1, warmup=span_h - 1, cfg=LS.bm.BiasConfig(),
                         line_overrides=ovr, lean=True)
    assert int(W.ts[-1]) == int(end_ts)
    out = {n: np.asarray(W._line_emerging(n), float)[-LAST:] for n in LS.NAMES}
    out['px'] = np.asarray(W.px, float)[-LAST:]
    return np.asarray(W.ts)[-LAST:], out, len(W.ts)


def main():
    end = int(dt.datetime.strptime(sys.argv[1], '%Y-%m-%d %H:%M:%S').replace(tzinfo=dt.timezone.utc)
              .timestamp() * 1000)
    db = LS.DatabaseManager(**LS.get_db_config()); db.connect()
    ovr = LS.line_overrides(db, LS._Names())
    t0 = time.time()
    rts, ref, rn = build(db, ovr, end, REF_H)
    print('reference %d h: %d bars, built in %.1f s, first bar %s' % (REF_H, rn, time.time() - t0,
                                                                     LS.utc(end - (rn - 1) * LS.BAR_MS)))
    cols = LS.NAMES + ['px']
    res = {}
    for S in SPANS:
        ts, got, n = build(db, ovr, end, S)
        assert np.array_equal(ts, rts)
        res[S] = {c: (float(np.nanmax(np.abs(got[c] - ref[c]))) if np.isfinite(got[c] - ref[c]).any() else np.nan,
                      int((np.isnan(got[c]) != np.isnan(ref[c])).sum())) for c in cols}
    print('| line | ' + ' | '.join('%d h' % S for S in SPANS) + ' |')
    print('|---|' + '---|' * len(SPANS))
    for c in cols:
        print('| %s | ' % c + ' | '.join('%.1e%s' % (res[S][c][0], '' if res[S][c][1] == 0 else
                                                    ' (%d NaN mismatch)' % res[S][c][1]) for S in SPANS) + ' |')


if __name__ == '__main__':
    main()
