"""The SEPARATE line cache for fdm3-htf-oracle - every line that page reads and no other cache holds.

HIS 1124: *"I need a parallel webservice built, named fdm3-htf-oracle.  fdm3-htf-oracle will clone fdm3-oracle, and
replace all columns except `ws1 time` with these new columns:"* / *"ws20,21,22,23,24,25,26,27,28,29,30,45,60,90,120,240"* /
*"these replacement columns will print the same data as fdm3-oracle's ws1-15 fields"*. His answers: towards/away's
lines under a line are *"The 5 minutes under it"*, and the new files go in *"A separate cache"*.

    the lines     UNDER (ws40..ws44, ws55..ws59, ws85..ws89, ws115..ws119, ws235..ws239) and ws240 get all four lines
                  towards/away and the page read: r at the page's r config (the fdm3 knob ORACLE_R_CFG, 6,6,9 on the
                  bank), Mage and x at the stored wsf row, e at the towards-away e row (BB%B 3|0.5|close). ws45, ws60,
                  ws90 and ws120 already have Mage and x in the shared line cache, so they get r and e only. b and m
                  are not built: nothing reads them while r-pred is off
    the arrays    built IN MEMORY in one Jig and written to their OWN directory under ROOT, one .npy per line and a
                  manifest. The shared line cache, the fdm3 r cache and the DB rows are never written. A directory that
                  exists is read, not rebuilt
    the control   the same Jig builds ws30 of all four lines at the same configs; each must equal the array this
                  process reads today (the fdm3 r cache's ws30r, the shared ws30Mage and ws30x, v4_ws_e's ws30e)
                  exactly, or the build refuses. On every load the manifest's per-line sums and the tape are asserted
    the switch    use() points ln.X_DIR at the directory, so ln.line and v4_ws_e.line find these names there. Only the
                  process that calls it is touched

usage: fdm3_htf_lines.py      build (or check) the cache for the banked r config and print its manifest
"""
import io
import json
import os
import sys
import time

import numpy as np

V4 = '/home/joe/thecodes/docs/octo-freedom/1022_v4'
for _p in ('/home/joe/thecodes', V4, os.path.dirname(os.path.abspath(__file__))):
    if _p not in sys.path:
        sys.path.insert(0, _p)
ROOT = '/home/joe/thecodes/optimus9/orchestration/.rpl_cache/fdm3_htf'   # beside rpl_cache/lines and fdm3_r
COLUMNS = [20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 45, 60, 90, 120, 240]   # HIS 1124, his order
UNDER = 5                                       # towards/away's lines under a line (ta_knobs UNDER), asserted on use
#   the TFs no cache holds: the 5 minutes under each column over ws30, and ws240 itself
NEW = sorted({u for t in COLUMNS if t > 30 for u in range(t - UNDER, t)} | {240})
OLD_HI = [t for t in COLUMNS if t > 30 and t not in NEW]   # ws45, ws60, ws90, ws120: Mage and x are in the shared cache


def _imports():
    _e = sys.stderr; sys.stderr = io.StringIO()
    try:
        import ln
        from optimus9.compute.line_config import override, mech_lines
        from optimus9.orchestration.build_ws_lines import HOURS, WARMUP
        from optimus9.config import get_db_config
        from optimus9 import DatabaseManager
        import fdm3_r_cache as RCC
        import v4_ws_e as WSE
    finally:
        sys.stderr = _e
    return ln, override, mech_lines, HOURS, WARMUP, get_db_config, DatabaseManager, RCC, WSE


def names():
    """Every line this cache holds. -> sorted list of names."""
    out = ['ws%d%s' % (t, role) for t in NEW for role in ('r', 'Mage', 'x', 'e')]
    out += ['ws%d%s' % (t, role) for t in OLD_HI for role in ('r', 'e')]
    return sorted(out)


def e_spec():
    """The towards-away e row's (spec, mode), read off its ws30e. -> tuple."""
    ln, override, mech_lines, HOURS, WARMUP, get_db_config, DatabaseManager, RCC, WSE = _imports()
    _e = sys.stderr; sys.stderr = io.StringIO()
    try:
        db = DatabaseManager(**get_db_config()); db.connect()
        rows = mech_lines(db, WSE.E_MECH, version=WSE.E_VERSION)
        db.disconnect()
    finally:
        sys.stderr = _e
    got = [d['override'] for d in rows if d['role'] == 'e' and d['tf_seconds'] == 1800]
    assert len(got) == 1, 'the towards-away e row has %d ws30e entries' % len(got)
    _t, spec, mode = got[0]
    return spec, mode


def path(cfg):
    """The cache directory for an r config on this tape. -> str."""
    ln = _imports()[0]
    k_len, rsi, stc = _imports()[7].parse(cfg)
    return os.path.join(ROOT, 'r%d_%d_%d_em%d_n%d' % (k_len, rsi, stc, ln.EM, ln.N))


def build(cfg):
    """Build names() at r config `cfg` in memory and write them to path(cfg). -> manifest dict."""
    ln, override, mech_lines, HOURS, WARMUP, get_db_config, DatabaseManager, RCC, WSE = _imports()
    _e = sys.stderr; sys.stderr = io.StringIO()
    try:
        from optimus9.analysis.jig import Jig
    finally:
        sys.stderr = _e
    assert ln.X_DIR is None, 'build reads the process\'s own ws30 lines as its control, so it must run before use()'
    kl = RCC._kline(*RCC.parse(cfg))
    es, em = e_spec()
    spec = {'r': (kl.as_tuple(), 'emerging'), 'Mage': ln.SPEC['Mage'], 'x': ln.SPEC['x'], 'e': (es, em)}
    ovr = {}
    for n in names():
        i = 2
        while n[i].isdigit():
            i += 1
        ovr[n] = override(int(n[2:i]) * 60, *spec[n[i:]])
    for role in spec:
        ovr['ws30%s_control' % role] = override(1800, *spec[role])
    t0 = time.time()
    with Jig(ln.EM, hours=HOURS, warmup=WARMUP, overrides=ovr) as j:
        assert len(j.ts) >= ln.N and (np.asarray(j.ts, np.int64)[:ln.N] == ln.ts).all(), 'the line grid is off the tape'
        got = {n: np.asarray(j.W.line(n), float)[:ln.N] for n in ovr}
    #   THE CONTROL: ws30 of each line at the same config, against what this process reads today
    RCC.use(cfg)
    try:
        ref = {'r': np.asarray(ln.line('ws30r'), float), 'Mage': np.asarray(ln.line('ws30Mage'), float),
               'x': np.asarray(ln.line('ws30x'), float), 'e': np.asarray(WSE.lines()[30], float)}
    finally:
        ln.R_DIR = None
    ctl = {}
    for role in spec:
        c = got.pop('ws30%s_control' % role)
        same = (np.isnan(c) == np.isnan(ref[role])).all() and np.nanmax(np.abs(c - ref[role])) == 0.0
        assert same, 'the ws30%s control does not match the array this process reads - this build cannot be trusted' % role
        ctl[role] = 'ws30%s built in the same Jig = the one this process reads, max diff 0' % role
    d = path(cfg)
    tmp = d + '.part'
    os.makedirs(tmp, exist_ok=False)
    for n in got:
        np.save(os.path.join(tmp, n + '.npy'), got[n])
    man = {'cfg': str(cfg), 'kline': str(kl), 'specs': {k: [list(v[0]), v[1]] for k, v in spec.items()},
           'columns': COLUMNS, 'new_tfs': NEW, 'old_hi': OLD_HI, 'under': UNDER,
           'em': int(ln.EM), 'hours': int(HOURS), 'warmup': int(WARMUP), 'n': int(ln.N),
           'ts0': int(ln.ts[0]), 'ts1': int(ln.ts[-1]),
           'nansum': {n: float(np.nansum(got[n])) for n in got}, 'nan': {n: int(np.isnan(got[n]).sum()) for n in got},
           'control': ctl, 'built_s': round(time.time() - t0, 1),
           'built_at': time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())}
    json.dump(man, open(os.path.join(tmp, 'manifest.json'), 'w'), indent=1)
    os.rename(tmp, d)
    return man


def check(cfg):
    """Read path(cfg)'s manifest and assert it is this config on this tape, file by file. -> manifest dict."""
    ln = _imports()[0]
    d = path(cfg)
    man = json.load(open(os.path.join(d, 'manifest.json')))
    assert man['n'] == ln.N and man['em'] == ln.EM and man['ts0'] == int(ln.ts[0]) and man['ts1'] == int(ln.ts[-1]), \
        'the fdm3-htf-oracle line cache is off this tape'
    assert sorted(man['nansum']) == names(), 'the fdm3-htf-oracle line cache does not hold the lines this page reads'
    for n in names():
        a = np.load(os.path.join(d, n + '.npy'), mmap_mode='r')
        assert len(a) == ln.N and float(np.nansum(a)) == man['nansum'][n] and int(np.isnan(a).sum()) == man['nan'][n], \
            '%s in the fdm3-htf-oracle line cache has changed' % n
    return man


def use(cfg):
    """Build the cache if it is missing, check it, and point this process's ln at it. -> (directory, manifest, built
    now). Call AFTER fdm3_r_cache.use, which owns ws1r..ws30r."""
    import ta_knobs as TK
    assert int(TK.UNDER) == UNDER, ('towards/away reads %d lines under, this cache was built for %d' % (TK.UNDER, UNDER))
    ln = _imports()[0]
    d, built = path(cfg), False
    if not os.path.isdir(d):
        r_dir, ln.R_DIR = ln.R_DIR, None
        try:
            build(cfg)
        finally:
            ln.R_DIR = r_dir
        built = True
    man = check(cfg)
    ln.X_DIR = d
    return d, man, built


if __name__ == '__main__':
    sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1109_towards_away')
    import fdm3_knobs as FK
    t0 = time.time()
    d, man, built = use(FK.ORACLE_R_CFG)
    print('%s %s in %.1f s' % ('BUILT' if built else 'checked', d, time.time() - t0))
    print('lines %d, new TFs %s, r and e only on %s' % (len(man['nansum']), man['new_tfs'], man['old_hi']))
    for n in names():
        print('%-10s NaN bars %d' % (n, man['nan'][n]))
    for k, v in man['control'].items():
        print('control %s: %s' % (k, v))
