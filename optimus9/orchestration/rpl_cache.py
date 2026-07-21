"""Warmup cache for rpl analysis. The Jig warmup recomputes ~180 emerging line arrays each run; the line
CONFIGS (overrides) are identical across walks and polarity re-runs, so the arrays are stable. Cache them
keyed on (end_ms, hours, warmup, override-config repr) -> logic-only edits skip the warmup. Cache
invalidates automatically the moment any line config changes (the repr is in the key).

Returns a JigCache mimicking the jig read surface the flow uses: .ts, .W.line(name),
.causal.cross_wob(array,...). cross_wob is the SANCTIONED producer (jig._Causal) called with an array
input (which it explicitly supports) - not a fork. Lines are the jig's own emerging output, cached."""
import os, hashlib, numpy as np
from optimus9.analysis.jig import Jig, _Causal
from optimus9.compute.indicator_computer import IndicatorComputer as IC

CACHE_DIR = os.path.join(os.path.dirname(__file__), '.rpl_cache')   # gitignored derived data; regenerates

def cache_key(end_ms, hours, warmup, ovr, pxs_cfg=None):
    h = hashlib.md5(); h.update(f'{end_ms}|{hours}|{warmup}|pxs={pxs_cfg!r}'.encode())
    for name in sorted(ovr): h.update(f'{name}={ovr[name]!r}'.encode())
    return h.hexdigest()[:16]

def _px_smooth_evt(base, evt, src, length):
    """Event-tape px_smooth: DEMA of the price src over EVENT bars only, forward-filled onto the full 5s grid
    (same filler-invisible discipline as the jig's lines). Index px_smooth (bl_detect) folds no-trade filler
    bars into the DEMA; on the event tape the smoother sees only real-trade bars. Producer = IC.dema (no fork)."""
    px = IC.build_source(base, src); ei = np.flatnonzero(evt)
    out = np.full(len(px), np.nan); out[ei] = IC.dema(px[ei], length)
    m = np.isfinite(out)
    if m.any():
        ix = np.where(m, np.arange(len(out)), 0); np.maximum.accumulate(ix, out=ix)
        out = out[ix]; out[:int(np.argmax(m))] = out[int(np.argmax(m))]   # backfill leading warmup NaN
    return out

class _W:
    def __init__(self, d): self._d = d
    def line(self, name): return self._d[name]

class _Cau:
    """Delegates cross_wob to the real jig._Causal (array input => no jig state touched)."""
    def cross_wob(self, line, level, direction, n): return _Causal(None).cross_wob(line, level, direction, n)

class JigCache:
    def __init__(self, d):
        self.ts = d['__ts__']; self.W = _W(d); self.causal = _Cau()
        self.evt = d['__evt__'] if '__evt__' in d else None
        self.pxs = d['__pxs__'] if '__pxs__' in d else None   # event-tape px_smooth (DEMA close, filler-invisible)
    def __enter__(self): return self
    def __exit__(self, *a): return False

def cache_jig(end_ms, hours, warmup, ovr, pxs_cfg=None, rebuild=False):
    """Drop-in for `with Jig(...) as j:` -> `with cache_jig(...) as j:`. Builds+saves on miss, loads on hit.
    pxs_cfg = {'src','len'} => also cache event-tape px_smooth (JigCache.pxs)."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    p = os.path.join(CACHE_DIR, cache_key(end_ms, hours, warmup, ovr, pxs_cfg) + '.npz')
    if os.path.exists(p) and not rebuild:
        d = np.load(p); return JigCache({k: d[k] for k in d.files})
    with Jig(end_ms, hours=hours, warmup=warmup, overrides=ovr) as j:
        out = {'__ts__': np.asarray(j.ts, np.int64)}
        for name in ovr: out[name] = np.asarray(j.W.line(name), float)
        out['__evt__'] = j.W.base['volume'].to_numpy(dtype=float) > 0   # event bars (real trades); index-vs-event gotcha
        if pxs_cfg: out['__pxs__'] = _px_smooth_evt(j.W.base, out['__evt__'], pxs_cfg['src'], int(pxs_cfg['len']))
    np.savez(p, **out)
    return JigCache(out)
