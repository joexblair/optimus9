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

# --- per-line cache (A, 0721): each line keyed on its OWN resolved spec (incl. TF), so a config change rebuilds
# only the lines that changed and reuses the rest. Full 360-line builds OOM; build missing lines in memory-safe
# batches (each Jig context ~23s fixed cost). Enables the cycle-group line sweep + coin dial-in. ---
LINE_DIR = os.path.join(CACHE_DIR, 'lines')
TAPE_DIR = os.path.join(CACHE_DIR, 'tape')
BATCH_MAX = 24                                     # lines per Jig build (memory-safe; full 360 OOMs on 18GB)

def _line_key(end_ms, hours, warmup, spec):
    return hashlib.md5(f'{end_ms}|{hours}|{warmup}|{spec!r}'.encode()).hexdigest()[:20]

def _tape_key(end_ms, hours, warmup, pxs_cfg):
    return hashlib.md5(f'{end_ms}|{hours}|{warmup}|pxs={pxs_cfg!r}'.encode()).hexdigest()[:20]

def cache_jig_perline(end_ms, hours, warmup, ovr, pxs_cfg=None, rebuild=False):
    """Per-line cached build. Same JigCache surface as cache_jig, but each line is cached by its own spec so
    a partial config change only rebuilds the changed lines. ts/evt/pxs cached once at tape level."""
    os.makedirs(LINE_DIR, exist_ok=True); os.makedirs(TAPE_DIR, exist_ok=True)
    lp = {n: os.path.join(LINE_DIR, _line_key(end_ms, hours, warmup, ovr[n]) + '.npy') for n in ovr}
    tp = os.path.join(TAPE_DIR, _tape_key(end_ms, hours, warmup, pxs_cfg) + '.npz')
    missing = [n for n in ovr if rebuild or not os.path.exists(lp[n])]
    need_tape = rebuild or not os.path.exists(tp)
    if missing or need_tape:
        batches = [missing[i:i + BATCH_MAX] for i in range(0, len(missing), BATCH_MAX)] or [[]]
        for bi, batch in enumerate(batches):
            if not batch and not (need_tape and bi == 0): continue
            with Jig(end_ms, hours=hours, warmup=warmup, overrides={n: ovr[n] for n in batch}) as j:
                for n in batch:                                    # atomic write (temp+rename) so parallel workers can't tear a file
                    tmp = lp[n] + f'.{os.getpid()}.tmp'; np.save(tmp, np.asarray(j.W.line(n), float))
                    os.replace(tmp + ('.npy' if not tmp.endswith('.npy') else ''), lp[n])
                _index(end_ms, hours, warmup, {n: ovr[n] for n in batch}, lp)
                if need_tape and bi == 0:
                    evt = j.W.base['volume'].to_numpy(dtype=float) > 0
                    td = {'__ts__': np.asarray(j.ts, np.int64), '__evt__': evt}
                    if pxs_cfg: td['__pxs__'] = _px_smooth_evt(j.W.base, evt, pxs_cfg['src'], int(pxs_cfg['len']))
                    np.savez(tp, **td); need_tape = False
    # READ-ONLY MEMORY MAP, not a copy. Joe 1003 approved it on the measurement: 40 files /
    # 513 MB loaded in 0.005 s against 0.315 s, and 0 MB resident against 513 MB. The arrays
    # are never mutated by any consumer (checked), and mmap makes them read-only, so an
    # attempt to write RAISES instead of silently corrupting a cached line.
    d = {n: np.load(lp[n], mmap_mode='r') for n in ovr}
    td = np.load(tp); d['__ts__'] = td['__ts__']; d['__evt__'] = td['__evt__']
    if '__pxs__' in td.files: d['__pxs__'] = td['__pxs__']
    return JigCache(d)

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
    """Delegates the ARRAY-ONLY producers to the real jig._Causal (array input => no jig state touched).
    Methods that read self.j are deliberately NOT exposed - they would fail at call time on _Causal(None).
    Any new array-only producer in _Causal needs a line here, or the cached path raises AttributeError."""
    def cross_wob(self, line, level, direction, n): return _Causal(None).cross_wob(line, level, direction, n)
    def clean_dirty(self, *a, **k): return _Causal(None).clean_dirty(*a, **k)
    def reversal(self, line, wob): return _Causal(None).reversal(line, wob)

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

INDEX_PATH = os.path.join(CACHE_DIR, 'build_index.jsonl')

def _index(end_ms, hours, warmup, ovr, lp):
    """Append one line per built file: which tape generation and which line it is. Joe 1003.

    WHY. The filename is an md5 of (end_ms, hours, warmup, spec), so a file cannot be traced back to
    the tape window it belongs to. The cache was 1,543 files / 19.56 GB with at least three
    generations live and no way to tell them apart, let alone prune. This costs one short line per
    file and makes every future build identifiable.

    Append-only and never read during a build, so it can never break one. Duplicate keys are
    harmless; `cache_generations()` dedupes.
    """
    import datetime as dt, json
    try:
        with open(INDEX_PATH, 'a') as fh:
            for n in sorted(ovr):
                fh.write(json.dumps({
                    'key': os.path.basename(lp[n]).replace('.npy', ''), 'name': n,
                    'end_ms': int(end_ms),
                    'end_utc': dt.datetime.fromtimestamp(int(end_ms) / 1000, dt.timezone.utc)
                                 .strftime('%Y-%m-%d %H:%M'),
                    'hours': int(hours), 'warmup': int(warmup), 'spec': repr(ovr[n]),
                }) + '\n')
    except OSError:
        pass                                   # the index is a convenience; never fail a build for it


def cache_generations():
    """What the line cache holds, by tape generation. -> list of dicts, newest end first.

    Files built before 1003 are not in the index - they are reported as `unindexed`, and the only way
    to identify them is to recompute keys for candidate (end_ms, spec) pairs.
    """
    import glob, json
    rows = []
    if os.path.exists(INDEX_PATH):
        with open(INDEX_PATH) as fh:
            for ln in fh:
                try: rows.append(json.loads(ln))
                except ValueError: pass
    on_disk = {os.path.basename(f).replace('.npy', '') for f in glob.glob(os.path.join(LINE_DIR, '*.npy'))}
    gens = {}
    seen = set()
    for r in rows:
        if r['key'] in seen: continue
        seen.add(r['key'])
        g = gens.setdefault((r['end_utc'], r['hours'], r['warmup']),
                            {'end_utc': r['end_utc'], 'hours': r['hours'], 'warmup': r['warmup'],
                             'files': 0, 'bytes': 0, 'names': []})
        if r['key'] in on_disk:
            g['files'] += 1
            g['names'].append(r['name'])
            try: g['bytes'] += os.path.getsize(os.path.join(LINE_DIR, r['key'] + '.npy'))
            except OSError: pass
    out = sorted(gens.values(), key=lambda g: g['end_utc'], reverse=True)
    un = on_disk - seen
    if un:
        b = 0
        for k in un:
            try: b += os.path.getsize(os.path.join(LINE_DIR, k + '.npy'))
            except OSError: pass
        out.append({'end_utc': 'unindexed (built before 1003)', 'hours': '-', 'warmup': '-',
                    'files': len(un), 'bytes': b, 'names': []})
    return out


def main():
    """python3 -m optimus9.orchestration.rpl_cache -- what the line cache holds, by tape generation."""
    print('%-32s %7s %7s %8s %10s' % ('tape generation', 'hours', 'warmup', 'files', 'GB'))
    tot_f = tot_b = 0
    for g in cache_generations():
        print('%-32s %7s %7s %8d %10.2f' % (g['end_utc'], g['hours'], g['warmup'], g['files'],
                                            g['bytes'] / 1e9))
        tot_f += g['files']; tot_b += g['bytes']
    print('%-32s %7s %7s %8d %10.2f' % ('TOTAL', '', '', tot_f, tot_b / 1e9))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
