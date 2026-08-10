"""sweep_s46_momo — item 13's two knobs across all 49 combinations. Joe 0805.

    fence  s = 2..8   ->  fence_lo = LO + s, fence_hi = 100 - LO - s   (s=3 gives 18/82)
    xwob      = 3..9  ->  replaces EXIT_WOB 3 once momo has armed; unarmed trades keep 3

The gated-state precompute is INDEPENDENT of both knobs, so it is hoisted out of the loop: one
4-minute pass, then 49 cheap walks. Running build_s46_event.py 49 times would repeat it 49 times.

SCORING. ret = dr * (px[exit] - px[entry]) / px[entry] * 100, minus TAKER 0.110% round trip — the
repo standard (replay.py:31 taker_bps=5.5, bias_pk_backtest.py:8, s30_exit_lever.py:7). Reported
both for all rows and under item 15 (no-pyramiding: skip any entry at or before the previous
accepted trade's exit bar), because item 13's long holds block far more entries than the 2-minute
exits they replace.

CAUSAL. Every input is the corrected one: sx_series pairs the sx_run_bars filter with the (wob-1)
shift off a single xwob argument, and the walk reads only the current bar and earlier.

    python3 -m optimus9.analysis.sweep_s46_momo [--cfg CUR]
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import numpy as np

from optimus9.analysis.s46_momo import walk, fence, FENCE_SWEEP, XWOB_SWEEP, CROSS
from optimus9.analysis.build_s46_event import sx_series, NPZ
from optimus9.compute.momo_gated import momo_g, STATE
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

TAKER = 0.110


def main(argv):
    cfg = argv[argv.index('--cfg') + 1] if '--cfg' in argv else 'CUR'
    d = np.load(NPZ[cfg]); ts = d['ts'].astype(np.int64)
    r15, r22 = d['r15'].astype(float), d['r22'].astype(float)

    db = DatabaseManager(**get_db_config()); db.connect()
    rows = db.execute('SELECT sw_n,sw_dr,sw_entry_ms FROM s46_window ORDER BY sw_n', fetch=True)
    EX = db.execute("SELECT sx_ms,sx_dir,sx_run_bars FROM s46_exit WHERE sx_line='s6x' "
                    "AND sx_lb_min<=72 ORDER BY sx_ms", fetch=True)
    PX = db.execute('SELECT px_ms,px_v FROM s46_px WHERE px_ms>=%s AND px_ms<=%s ORDER BY px_ms',
                    (int(ts[0]), int(ts[-1])), fetch=True)
    db.disconnect()
    SX = {k: [(int(r['sx_ms']), int(r['sx_run_bars'])) for r in EX if int(r['sx_dir']) == k]
          for k in (1, -1)}
    pm = np.array([r['px_ms'] for r in PX], np.int64)
    pv = np.array([r['px_v'] for r in PX], float)
    px = np.full(len(ts), np.nan); k = np.searchsorted(pm, ts)
    ok = (k < len(pm)) & (pm[np.minimum(k, len(pm) - 1)] == ts); px[ok] = pv[k[ok]]
    f = np.isfinite(px); ix = np.where(f, np.arange(len(px)), 0)
    np.maximum.accumulate(ix, out=ix); px = px[ix]

    a0 = min(int(np.searchsorted(ts, int(x['sw_entry_ms']))) for x in rows)
    print('precomputing gated states once, bars %d..%d' % (a0, len(ts) - 1), flush=True)
    ST = {}
    for tf, arr in ((15, r15), (22, r22)):
        for dd in (1, -1):
            v = np.zeros(len(ts), np.int8)
            for i in range(a0, len(ts)):
                v[i] = STATE.get(momo_g(arr, dd, i)[0], 0)
            ST[(tf, dd)] = v
    gate = {dd: ((ST[(15, dd)] == 1) | (ST[(15, dd)] == 2) |
                 (ST[(22, dd)] == 1) | (ST[(22, dd)] == 2)) for dd in (1, -1)}
    oppc = {dd: ((ST[(15, -dd)] == 2) & (ST[(22, -dd)] == 2)) for dd in (1, -1)}
    plain = {k_: sx_series(ts, SX[k_], 3) for k_ in (1, -1)}
    ent = [int(np.searchsorted(ts, int(x['sw_entry_ms']))) for x in rows]
    drs = [int(x['sw_dr']) for x in rows]

    def score(a, b, dr):
        if not np.isfinite(px[a]) or px[a] == 0 or b <= a:
            return None
        return dr * (px[b] - px[a]) / px[a] * 100.0 - TAKER

    print()
    print('net of %.3f%% round-trip taker. hold in minutes.' % TAKER)
    print('  %-5s %-5s | %4s %9s %9s %8s | %4s %9s %9s %8s'
          % ('fence', 'xwob', 'n', 'net mean', 'net sum', 'hold', 'nP', 'net mean', 'net sum', 'hold'))
    print('  %-5s %-5s | %-33s | %-33s' % ('', '', '  ALL ROWS', '  ITEM 15 no-pyramiding'))
    out = []
    for s in FENCE_SWEEP:
        for xw in XWOB_SWEEP:
            held = {k_: sx_series(ts, SX[k_], xw) for k_ in (1, -1)}
            res = []
            for a, dr in zip(ent, drs):
                ev = walk(r15, r22, dr, a, len(ts) - 1, held[dr], plain[dr], s, gate[dr], oppc[dr])
                c = [w for kind, w, _ in ev if kind == CROSS]
                if not c:
                    continue
                r_ = score(a, c[0], dr)
                if r_ is not None:
                    res.append((a, c[0], r_))
            if len(res) < 5:
                continue
            rr = np.array([x[2] for x in res])
            hold = np.array([(ts[x[1]] - ts[x[0]]) / 60000.0 for x in res])
            keep = []; last = -1
            for x in res:
                if x[0] <= last:
                    continue
                keep.append(x); last = x[1]
            kr = np.array([x[2] for x in keep])
            kh = np.array([(ts[x[1]] - ts[x[0]]) / 60000.0 for x in keep])
            out.append(dict(s=s, xw=xw, n=len(rr), mn=rr.mean(), sm=rr.sum(), hd=np.median(hold),
                            kn=len(kr), kmn=kr.mean(), ksm=kr.sum(), khd=np.median(kh)))
            print('  %-5d %-5d | %4d %+9.4f %+9.1f %8.0f | %4d %+9.4f %+9.1f %8.0f'
                  % (s, xw, len(rr), rr.mean(), rr.sum(), np.median(hold),
                     len(kr), kr.mean(), kr.sum(), np.median(kh)), flush=True)
    print()
    for lab, key, nkey in (('ALL ROWS', 'sm', 'n'), ('NO-PYRAMID', 'ksm', 'kn')):
        b = sorted(out, key=lambda z: -z[key])[:5]
        print('  best 5 by net sum, %s:' % lab)
        for o in b:
            print('    fence %d xwob %d   n %3d   net mean %+.4f   net sum %+.1f'
                  % (o['s'], o['xw'], o[nkey], o['kmn'] if key == 'ksm' else o['mn'], o[key]))


if __name__ == '__main__':
    main(sys.argv[1:])
