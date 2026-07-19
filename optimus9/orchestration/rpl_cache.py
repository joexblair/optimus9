"""Warmup cache for rpl analysis. The Jig warmup recomputes ~180 emerging line arrays each run; the line
CONFIGS (overrides) are identical across walks and polarity re-runs, so the arrays are stable. Cache them
keyed on (end_ms, hours, warmup, override-config repr) -> logic-only edits skip the warmup. Cache
invalidates automatically the moment any line config changes (the repr is in the key).

Returns a JigCache mimicking the jig read surface the flow uses: .ts, .W.line(name),
.causal.cross_wob(array,...). cross_wob is the SANCTIONED producer (jig._Causal) called with an array
input (which it explicitly supports) - not a fork. Lines are the jig's own emerging output, cached."""
import os, hashlib, numpy as np
from optimus9.analysis.jig import Jig, _Causal

CACHE_DIR = os.path.join(os.path.dirname(__file__), '.rpl_cache')   # gitignored derived data; regenerates

def cache_key(end_ms, hours, warmup, ovr):
    h = hashlib.md5(); h.update(f'{end_ms}|{hours}|{warmup}'.encode())
    for name in sorted(ovr): h.update(f'{name}={ovr[name]!r}'.encode())
    return h.hexdigest()[:16]

class _W:
    def __init__(self, d): self._d = d
    def line(self, name): return self._d[name]

class _Cau:
    """Delegates cross_wob to the real jig._Causal (array input => no jig state touched)."""
    def cross_wob(self, line, level, direction, n): return _Causal(None).cross_wob(line, level, direction, n)

class JigCache:
    def __init__(self, d): self.ts = d['__ts__']; self.W = _W(d); self.causal = _Cau()
    def __enter__(self): return self
    def __exit__(self, *a): return False

def cache_jig(end_ms, hours, warmup, ovr, rebuild=False):
    """Drop-in for `with Jig(...) as j:` -> `with cache_jig(...) as j:`. Builds+saves on miss, loads on hit."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    p = os.path.join(CACHE_DIR, cache_key(end_ms, hours, warmup, ovr) + '.npz')
    if os.path.exists(p) and not rebuild:
        d = np.load(p); return JigCache({k: d[k] for k in d.files})
    with Jig(end_ms, hours=hours, warmup=warmup, overrides=ovr) as j:
        out = {'__ts__': np.asarray(j.ts, np.int64)}
        for name in ovr: out[name] = np.asarray(j.W.line(name), float)
    np.savez(p, **out)
    return JigCache(out)
