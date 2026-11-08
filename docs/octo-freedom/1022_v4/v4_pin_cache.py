"""The developing-stoch PIN per r line, cached off disk the way the r lines themselves are.

GOAL: hand `fdm2-rline-enhance` the two arrays it needs - where each ws{tf}r line is BLIND, and the
developing RSI still moving under it - without a Jig run on every read. HIS 1108 GO:
*"I said to wire it as a race"*. The mech is `docs/octo-freedom/1108_rline_enhance.md`.

WHY A JIG RUN IS UNAVOIDABLE, measured 1108: a 5 s base frame rebuilt from `klines_hl.npz` does NOT
reproduce the cached r lines - ws30 differs by up to 14.3, ws27 by 51.8 and ws5 by 34.7 - because
the lines compute on the Jig's EVENT tape (filler-invisible) and are remapped back onto the full
grid. So the pin is read through `BiasWindow.pin`, which uses that same tape and remap, and the
result is cached per line spec exactly as `cache_jig_perline` caches the lines.

ONE FILE PER TF, holding `pin` and `rsi_d`. The key is the LINE's own spec with a `pin` tag in
front, so it moves when the r config moves and can never be served for the wrong config.

usage: v4_pin_cache.py           # build every missing TF, then print what is cached
"""
import datetime as dt
import io
import os
import sys
import time

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')

import ln
import v4_knobs as K
#   THE SWALLOW COVERS THE NOISY IMPORTS ONLY - and `finally` restores stderr whatever happens, so
#   a refusal from v4_knobs.check() still reaches the terminal.
_e = sys.stderr
sys.stderr = io.StringIO()
try:
    from optimus9.compute.line_config import override, KLine
    from optimus9.orchestration.build_ws_lines import HOURS, WARMUP
    from optimus9.orchestration.rpl_cache import CACHE_DIR, _line_key
    from optimus9.analysis.jig import Jig
finally:
    sys.stderr = _e

EM = int(dt.datetime.strptime('2026-10-05', '%Y-%m-%d')
         .replace(tzinfo=dt.timezone.utc).timestamp() * 1000)
PIN_DIR = os.path.join(CACHE_DIR, 'pins')
TFS = list(range(1, 31))
BATCH = 24


def spec(tf):
    """The r line's own override at the BANKED config - the same call v4_rcfg_sweep.spec makes.

    Built through the named form so it cannot transpose: `KLine` names what each slot means, and
    K.R_KLEN / K.R_RSI / K.R_STC are the banked 7 / 5 / 8.
    """
    return override(tf * 60, KLine(k_len=int(K.R_KLEN), rsi=int(K.R_RSI), stc=int(K.R_STC),
                                   src='close'), 'emerging')


def path(tf):
    """Where this TF's pin arrays live. The key carries the LINE spec, tagged `pin`. -> str."""
    return os.path.join(PIN_DIR, _line_key(EM, HOURS, WARMUP, ('pin',) + spec(tf)) + '.npz')


def build(tfs=None, log=print):
    """Build every missing TF's pin arrays through one Jig context per batch. -> the count built."""
    os.makedirs(PIN_DIR, exist_ok=True)
    want = list(tfs) if tfs else TFS
    miss = [t for t in want if not os.path.exists(path(t))]
    log('# %d TFs wanted, %d already cached, %d to build' % (len(want), len(want) - len(miss),
                                                             len(miss)))
    t0 = time.time()
    for i in range(0, len(miss), BATCH):
        chunk = miss[i:i + BATCH]
        ovr = {'pin%d' % t: spec(t) for t in chunk}
        _s = sys.stderr
        sys.stderr = io.StringIO()
        try:
            with Jig(EM, hours=HOURS, warmup=WARMUP, overrides=ovr) as j:
                for t in chunk:
                    pn, rsi_d = j.W.pin('pin%d' % t)
                    #   ATOMIC WRITE, temp then rename, so a parallel worker cannot read a torn
                    #   file - the same discipline cache_jig_perline uses for a line array.
                    tmp = path(t) + '.%d.tmp' % os.getpid()
                    np.savez(tmp, pin=np.asarray(pn, float), rsi_d=np.asarray(rsi_d, float))
                    os.replace(tmp + ('.npz' if not tmp.endswith('.npz') else ''), path(t))
        finally:
            sys.stderr = _s
        log('# built %d of %d, %.0f s elapsed' % (min(i + BATCH, len(miss)), len(miss),
                                                  time.time() - t0))
    if miss:
        log('# the build took %.0f s' % (time.time() - t0))
    return len(miss)


def load(tfs=None):
    """The cached pin arrays, trimmed to the project grid. -> {tf: (pin, rsi_d)}.

    It does NOT build. A missing TF raises, because a silent rebuild inside a read is how a report
    ends up measuring a different config from the one it names.
    """
    out = {}
    for t in (list(tfs) if tfs else TFS):
        p = path(t)
        assert os.path.exists(p), 'ws%dr has no cached pin - run v4_pin_cache.py' % t
        z = np.load(p, mmap_mode='r')
        out[t] = (np.asarray(z['pin'], float)[:ln.N], np.asarray(z['rsi_d'], float)[:ln.N])
    return out


if __name__ == '__main__':
    build()
    d = load()
    print()
    print('| the line | bars with a pin value | pinned HIGH | pinned LOW | free or degenerate |')
    print('|---|---|---|---|---|')
    for t in sorted(d):
        pn = d[t][0]
        f = np.isfinite(pn)
        print('| ws%dr | %d of %d | %d | %d | %d |'
              % (t, int(f.sum()), len(pn), int((pn[f] == 1).sum()), int((pn[f] == -1).sum()),
                 int((pn[f] == 0).sum())))
