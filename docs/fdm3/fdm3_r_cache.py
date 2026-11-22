"""The SEPARATE r cache - ws1r..ws30r at a page's own r config, for that page's process alone.

HIS 1121: *"clone 8793 to 8792 and change the config of r.  the new config is K len:6, RSI len:6, stoch range: 9"* /
*"contain the r config update to 8792 only.  you'll need a separate cache"*.

    the config    the fdm3 knob ORACLE_R_CFG, 'k_len,rsi,stc' in his order, src close - BANKED 1122 at 6,6,9 with
                  8794, his *"this is good - bank it, commit push, update the docs.  make this the machine"*. 'db'
                  is the stored wsf r row off the shared line cache, off-ruled since, and this module does nothing
                  for it
    the arrays    built IN MEMORY in one Jig, then written to their OWN directory under ROOT, one .npy per line and
                  a manifest. The shared line cache (rpl_cache/lines), the DB mech_lines row and v4's R_* knobs are
                  never written. A directory that exists is read, not rebuilt
    the control   the same Jig builds ws30r at the DB row, which must equal the shared cache's ws30r exactly, or the
                  build refuses - the r2 and e builds' own rule. On every load the manifest's per-line sums and the
                  tape it was built on are asserted again, so a changed tape or a damaged file refuses
    the switch    use() points ln at the directory (ln.R_DIR), so every ln.line('ws{TF}r') in the process - the page,
                  towards/away, lift-off's e path - reads the one config. No other process is touched

usage: fdm3_r_cache.py 6,6,9      build (or check) the cache for that config and print its manifest
"""
import io
import json
import os
import sys
import time

import numpy as np

V4 = '/home/joe/thecodes/docs/octo-freedom/1022_v4'
for _p in ('/home/joe/thecodes', V4):
    if _p not in sys.path:
        sys.path.insert(0, _p)
ROOT = '/home/joe/thecodes/optimus9/orchestration/.rpl_cache/fdm3_r'   # beside rpl_cache/lines, not inside it
TFS = list(range(1, 31))                       # ws1r..ws30r, every TF towards/away and the page read


def parse(cfg):
    """'6,6,9' -> (k_len, rsi, stc); 'db' -> None."""
    if str(cfg) == 'db':
        return None
    k_len, rsi, stc = (int(v) for v in str(cfg).split(','))
    assert min(k_len, rsi, stc) >= 1, cfg
    return k_len, rsi, stc


def _kline(k_len, rsi, stc):
    _e = sys.stderr; sys.stderr = io.StringIO()
    try:
        from optimus9.compute.line_config import KLine
    finally:
        sys.stderr = _e
    return KLine(k_len=k_len, rsi=rsi, stc=stc, src='close')     # BY NAME - the legacy tuple transposes by hand


def path(cfg):
    """The cache directory for a config on this tape. -> str."""
    import ln
    k_len, rsi, stc = parse(cfg)
    return os.path.join(ROOT, 'k%d_rsi%d_stc%d_close_em%d_n%d' % (k_len, rsi, stc, ln.EM, ln.N))


def build(cfg):
    """Build ws1r..ws30r at `cfg` in memory and write them to path(cfg). -> manifest dict."""
    import ln
    _e = sys.stderr; sys.stderr = io.StringIO()
    try:
        from optimus9.analysis.jig import Jig
        from optimus9.compute.line_config import override
        from optimus9.orchestration.build_ws_lines import HOURS, WARMUP
    finally:
        sys.stderr = _e
    assert ln.R_DIR is None, 'build reads the shared ws30r as its control, so it must run before use()'
    k_len, rsi, stc = parse(cfg)
    kl = _kline(k_len, rsi, stc)
    ovr = {'ws%dr' % t: override(t * 60, kl.as_tuple(), 'emerging') for t in TFS}
    ovr['ws30r_control'] = override(1800, ln.SPEC['r'][0], 'emerging')     # the DB row, as the shared cache holds it
    t0 = time.time()
    with Jig(ln.EM, hours=HOURS, warmup=WARMUP, overrides=ovr) as j:
        assert len(j.ts) >= ln.N and (np.asarray(j.ts, np.int64)[:ln.N] == ln.ts).all(), 'the r grid is off the tape'
        got = {n: np.asarray(j.W.line(n), float)[:ln.N] for n in ovr}
    c, ref = got.pop('ws30r_control'), np.asarray(ln.line('ws30r'), float)
    assert (np.isnan(c) == np.isnan(ref)).all() and np.nanmax(np.abs(c - ref)) == 0.0, \
        'the ws30r control row does not match the shared cache\'s ws30r - this build cannot be trusted'
    d = path(cfg)
    tmp = d + '.part'
    os.makedirs(tmp, exist_ok=False)
    for t in TFS:
        np.save(os.path.join(tmp, 'ws%dr.npy' % t), got['ws%dr' % t])
    man = {'cfg': str(cfg), 'kline': str(kl), 'tuple': list(kl.as_tuple()), 'src': 'close', 'mode': 'emerging',
           'em': int(ln.EM), 'hours': int(HOURS), 'warmup': int(WARMUP), 'n': int(ln.N),
           'ts0': int(ln.ts[0]), 'ts1': int(ln.ts[-1]),
           'nansum': {str(t): float(np.nansum(got['ws%dr' % t])) for t in TFS},
           'nan': {str(t): int(np.isnan(got['ws%dr' % t]).sum()) for t in TFS},
           'control': 'ws30r at %s built in the same Jig = the shared cache ws30r, max diff 0' % (ln.SPEC['r'][0],),
           'built_s': round(time.time() - t0, 1),
           'built_at': time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())}
    json.dump(man, open(os.path.join(tmp, 'manifest.json'), 'w'), indent=1)
    os.rename(tmp, d)
    return man


def check(cfg):
    """Read path(cfg)'s manifest and assert it is this config on this tape, file by file. -> manifest dict."""
    import ln
    d = path(cfg)
    man = json.load(open(os.path.join(d, 'manifest.json')))
    k_len, rsi, stc = parse(cfg)
    want = list(_kline(k_len, rsi, stc).as_tuple())
    assert man['tuple'] == want and man['n'] == ln.N and man['em'] == ln.EM, (man['tuple'], want, man['n'], ln.N)
    assert man['ts0'] == int(ln.ts[0]) and man['ts1'] == int(ln.ts[-1]), 'the separate r cache is off this tape'
    for t in TFS:
        a = np.load(os.path.join(d, 'ws%dr.npy' % t), mmap_mode='r')
        assert len(a) == ln.N and float(np.nansum(a)) == man['nansum'][str(t)] \
            and int(np.isnan(a).sum()) == man['nan'][str(t)], 'ws%dr in the separate r cache has changed' % t
    return man


def shared_diff(cfg):
    """READ ONLY: the shared line cache may hold this config from the 1022 r-config sweep. -> {tf: max abs diff},
    None where it holds no array. Information - it never decides anything."""
    import ln
    _e = sys.stderr; sys.stderr = io.StringIO()
    try:
        from optimus9.compute.line_config import override
    finally:
        sys.stderr = _e
    k_len, rsi, stc = parse(cfg)
    kl, d, out = _kline(k_len, rsi, stc), path(cfg), {}
    for t in TFS:
        p = os.path.join(ln.LINE_DIR, ln._line_key(ln.EM, ln.HOURS, ln.WARMUP,
                                                   override(t * 60, kl.as_tuple(), 'emerging')) + '.npy')
        if not os.path.exists(p):
            out[t] = None
            continue
        a = np.asarray(np.load(p, mmap_mode='r'), float)[:ln.N]
        b = np.asarray(np.load(os.path.join(d, 'ws%dr.npy' % t), mmap_mode='r'), float)
        out[t] = float('inf') if (np.isnan(a) != np.isnan(b)).any() else float(np.nanmax(np.abs(a - b)))
    return out


def use(cfg):
    """Point this process's ln at the separate r cache for `cfg`, building it if it is missing. 'db' does nothing.
    -> (directory, manifest, built now) or None."""
    import ln
    if parse(cfg) is None:
        return None
    assert ln.R_DIR is None, 'the r cache is already switched'
    built = not os.path.isdir(path(cfg))
    if built:
        build(cfg)
    man = check(cfg)
    ln.R_DIR = path(cfg)
    return ln.R_DIR, man, built


if __name__ == '__main__':
    cfg = sys.argv[1]
    os.chdir(V4)                               # the tape is cwd-sensitive
    import ln
    print('tape bars %d' % ln.N)
    built = not os.path.isdir(path(cfg))
    if built:
        build(cfg)
    man = check(cfg)
    print('%s %s' % ('built' if built else 'checked', path(cfg)))
    print(json.dumps({k: v for k, v in man.items() if k not in ('nansum', 'nan')}, indent=1))
    print('shared line cache, same config, max abs diff per line (None = not there):', shared_diff(cfg))
