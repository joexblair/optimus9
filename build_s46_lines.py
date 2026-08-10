"""build_s46_lines — CHUNKED line bank for the full ~12wk tape. Joe 0804.

WHY CHUNKED. One jig pass at TF30 over 75 days does not fit in memory - the 96 h recon held 5.2 GB,
so the full tape would need ~100 GB. Each chunk builds 4 days of data behind 2 days of warmup lead-in
(48 h >> the 18.5 h a bb 37 at TF30 needs) and writes an npz. Chunks are stitched by ts, so the
stitched arrays are bit-identical to a single pass over the same bars.

WHAT IT BANKS, per 5 s bar
    ts                     the 5 s grid
    x{tf}                  bb  4|0.37|close   @TF15 / TF22 / TF30   (exhv2 LINE_SPEC['x'])
    M{tf}                  bb 37|0.70|close   @TF15 / TF22 / TF30   (exhv2 LINE_SPEC['M'])
    r{tf}                  kline 10|4|11|close @TF15 / TF22 / TF30  (exhv2 R_SPEC[15], cloned to 22/30)
    g{tf}_p / g{tf}_n      build_exhv2.momo() state at dr +1 / -1, as int8
                             0 none | 1 momo | 2 curl | 3 sideways
    evt                    volume > 0, the EVENT BAR flag. Joe 0804: "you're testing for crossovers in
                           volatile emerging bars" - the decile census put the busiest tenth of the
                           tape at a 42.5% blip rate vs 24.1% in the quietest, d10/d1 = 1.77 across
                           every window from 1 to 22 min. Event-time wobble needs this.

build_exhv2.momo() is CALLED, never copied - a second copy would fork MOMO_WINDOW_MIN / CURL_ARC_MIN.

    python3 build_s46_lines.py --chunk 0          # one chunk
    python3 build_s46_lines.py --stitch           # merge every chunk npz into one

TODO (Joe 0805, LOW PRIORITY): THESE BANKS SHOULD BE IN THE DATABASE, NOT npz IN A SCRATCH DIR.
    They live at $CLAUDE_JOB_DIR/tmp/ and are wiped on cleanup. optimus9/analysis/s46_momo.py
    (item 13) CANNOT RUN without lines_all.npz. Joe 0805: "move the npz lines to build_s46_lines,
    note that they need to be databased - low priority".

    Two sibling banks belong here and are currently separate root-level files:
      build_r7512.py  r15/r22 at k_len 7 | rsi 5 | stc 12 + their momo states, 07-24 -> 08-01.
                      Feeds item 13's variant A (oob duty) and variant B (both duties).
      build_r3.py     s3r at TWO R_SPEC variants + s3x/s3M, 07-24 -> 08-01.
                      From the FAILED curl-pred experiment (Joe 0805 retired it). Keep or drop.

    Folding them in means TFS and the R_SPEC becoming per-bank parameters rather than module
    constants, since this file hardcodes TFS = (15, 22, 30) and RSP = X.R_SPEC[15].
"""
import sys, os, glob, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('RPL_TF_CEILING', '30')
import numpy as np

TAPE0 = dt.datetime(2026, 5, 18, tzinfo=dt.timezone.utc)
TAPE1 = dt.datetime(2026, 8, 1, tzinfo=dt.timezone.utc)
CHUNK_D = 4                      # days of data per chunk
WARM_D = 2                       # days of warmup lead-in per chunk
TFS = (15, 22, 30)
OUT = os.environ.get('CLAUDE_JOB_DIR', '/tmp') + '/tmp'
NCHUNK = int(np.ceil((TAPE1 - TAPE0).days / CHUNK_D))
MS = lambda d: int(d.timestamp() * 1000)


def build(ci):
    import build_exhv2 as X
    from optimus9.analysis.jig import Jig, bbline, kline
    a = TAPE0 + dt.timedelta(days=ci * CHUNK_D)
    b = min(TAPE1, a + dt.timedelta(days=CHUNK_D))
    if a >= b:
        return None
    XS, MSP = X.LINE_SPEC['x'][1], X.LINE_SPEC['M'][1]
    RSP = X.R_SPEC[15]
    ovr = {}
    for tf in TFS:
        ovr.update(bbline('Lx%d' % tf, float(tf), **XS))
        ovr.update(bbline('LM%d' % tf, float(tf), **MSP))
        ovr.update(kline('Lr%d' % tf, float(tf), **RSP))
    hrs = (CHUNK_D + WARM_D) * 24 + 2
    with Jig(MS(b), hours=hrs, warmup=180, overrides=ovr) as j:
        ts = np.asarray(j.ts, np.int64)
        D = {'ts': ts}
        for tf in TFS:
            D['x%d' % tf] = np.asarray(j.W.line('Lx%d' % tf), float)
            D['M%d' % tf] = np.asarray(j.W.line('LM%d' % tf), float)
            D['r%d' % tf] = np.asarray(j.W.line('Lr%d' % tf), float)
        D['evt'] = (j.W.base['volume'].to_numpy(dtype=float) > 0).astype(np.int8)
    lo = int(np.searchsorted(ts, MS(a)))          # keep only this chunk's own data range
    ST = {'none': 0, 'momo': 1, 'curl': 2, 'sideways': 3}
    for tf in TFS:
        for tag, dr in (('p', 1), ('n', -1)):
            s = np.zeros(len(ts), np.int8)
            r = D['r%d' % tf]
            for i in range(lo, len(ts)):
                s[i] = ST.get(X.momo(r, dr, i)[0], 0)
            D['g%d_%s' % (tf, tag)] = s
    keep = slice(lo, len(ts))
    out = {k: (v[keep] if k != 'ts' else v[keep]) for k, v in D.items()}
    p = '%s/lines_%02d.npz' % (OUT, ci)
    np.savez_compressed(p, **out)
    print('chunk %02d  %s -> %s  %d bars  -> %s'
          % (ci, a.strftime('%m-%d'), b.strftime('%m-%d'), len(out['ts']), p))
    return p


def stitch():
    fs = sorted(glob.glob('%s/lines_*.npz' % OUT))
    if not fs:
        raise SystemExit('no chunks in %s' % OUT)
    D = [np.load(f) for f in fs]
    keys = list(D[0].keys())
    out = {}
    for k in keys:
        out[k] = np.concatenate([d[k] for d in D])
    o = np.argsort(out['ts'], kind='stable')
    for k in keys:
        out[k] = out[k][o]
    _, u = np.unique(out['ts'], return_index=True)
    for k in keys:
        out[k] = out[k][u]
    gaps = np.diff(out['ts'])
    p = '%s/lines_all.npz' % OUT
    np.savez_compressed(p, **out)
    print('stitched %d chunks -> %d bars   %s -> %s   gap min %d max %d ms (5000 = contiguous)'
          % (len(fs), len(out['ts']),
             dt.datetime.fromtimestamp(out['ts'][0]/1000, dt.timezone.utc).strftime('%m-%d %H:%M'),
             dt.datetime.fromtimestamp(out['ts'][-1]/1000, dt.timezone.utc).strftime('%m-%d %H:%M'),
             gaps.min(), gaps.max()))
    for k in keys:
        if k in ('ts', 'evt') or k.startswith('g'):
            continue
        v = out[k]
        print('  %-6s finite %6.2f%%  min %9.2f  max %9.2f'
              % (k, 100.0*np.isfinite(v).mean(), np.nanmin(v), np.nanmax(v)))
    print('  evt density %.3f (fraction of 5 s bars carrying an event)' % out['evt'].mean())
    for tf in TFS:
        for tag in ('p', 'n'):
            g = out['g%d_%s' % (tf, tag)]
            print('  g%-2d_%s  none %5.1f%%  momo %5.1f%%  curl %5.1f%%  sideways %5.1f%%'
                  % (tf, tag, 100*(g == 0).mean(), 100*(g == 1).mean(),
                     100*(g == 2).mean(), 100*(g == 3).mean()))
    return p


if __name__ == '__main__':
    av = sys.argv[1:]
    if '--stitch' in av:
        stitch()
    elif '--nchunk' in av:
        print(NCHUNK)
    else:
        build(int(av[av.index('--chunk') + 1]))
