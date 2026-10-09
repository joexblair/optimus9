"""`traj` FOR A SLOW LINE — the mech, Joe 1008/1009. ONE JOB, no DB, no scoring, no thresholds.

THE SPEC, every clause traced to Joe's words:

  the samples       the line read back in blocks of `block` bars. Joe 1009: *"I think 5 minutes
                    stays - it will catch more data to evaluate. this is also a knob"*.
                    Block n covers [k - n*block, k - (n-1)*block), so the test bar is EXCLUDED,
                    exactly as the divergence's step-3 walk does it. An empty block is SKIPPED,
                    not a stop - Joe 0921.
  the lookback      `look_n` samples. Joe 1008: *"({knob:2,'TRAJ_MULTI_TF_SAMP'} * TF-width)"*.
  the tail          `tail_n` samples, Joe's *"last mile"*, labelled TRAJ_TAIL_TF_SAMP.
  the reversal      Joe 1009: *"the first sample that broke the prior direction, then confirmed on
                    the following sample"*, and Joe 1008: *"if the reversal happened 25 minutes
                    before the event, then the tail is reduced to 25 minutes"*. So the reversal
                    TRUNCATES the tail. Implemented as: walk the sample diffs newest-first, take
                    the run of same-signed diffs, and the run's far end IS the reversal.
  flat              Joe 1009: *"exactly equal"*. No tolerance, so no `min_travel`.
                    Joe 1008: *"fix the sampling, drop min_travel"* - there is no magnitude knob.
  a flat tail       Joe 1008: *"if the tail is flat ... the mech needs to defer to the earlier
                    samples"*. MINE, Joe 1009 *"unsure - your preference"*: step the tail's far end
                    back ONE sample at a time until the diff is non-flat, bounded by the lookback.
  a flat lookback   returns 0. The caller decides - Joe's #7 ws60Mage-vs-ws60r fallback lives in
                    the caller, not here, because it reads a second line.

THREE THINGS ARE MINE AND ARE STATED SO THEY CAN BE OVERTURNED

  `kind`      what ONE sample IS. Joe's 0924 mech hunted the dr-OPPOSED extreme per block, but that
              needs a direction handed in, and this mech must FIND the direction. Two readings are
              built and neither is chosen:
                'close'    the line's value at the block's most recent bar - "sampling the line"
                'extreme'  the block's min or max on the side the caller names, Joe 0924's shape
  an UNCONFIRMED newest move   a run of length 1 is not a confirmed reversal by Joe's own clause,
              so the tail is NOT truncated there; the run is extended through it into the prior one.
  flats inside a run   a flat diff neither continues nor breaks a direction, so it is transparent
              when the run is measured.

CAUSAL. Every bar read is strictly before `k`.
"""
import numpy as np

_sign = lambda x: 0 if x == 0 else (1 if x > 0 else -1)


def sample_series(line, k, block, look_n, kind='close', side=0):
    """The sample series behind bar `k`, NEWEST FIRST. -> [(bar, value), ...]

    kind 'close'    the value at the block's most recent bar
    kind 'extreme'  the block's min when side > 0, its max when side < 0 (Joe 0924's shape)
    """
    line = np.asarray(line, float)
    k = int(k); block = max(1, int(block))
    out = []
    for n in range(1, int(look_n) + 1):
        hi = k - (n - 1) * block
        lo = max(0, k - n * block)
        if hi <= 0 or lo >= hi: break
        seg = line[lo:hi]
        if np.all(np.isnan(seg)): continue              # Joe 0921: skip, do not stop
        if kind == 'close':
            j = hi - 1
            while j >= lo and not np.isfinite(line[j]): j -= 1
            if j < lo: continue
            out.append((int(j), float(line[j])))
        else:
            m = lo + int(np.nanargmin(seg) if side > 0 else np.nanargmax(seg))
            out.append((int(m), float(line[m])))
    return out


def traj(line, k, block, tail_n, look_n, kind='close', side=0):
    """Which way is this line travelling at bar `k`. -> a dict, never None.

    keys: dir (+1 up, -1 down, 0 none), tail_used, reversal_bar, run, travel, deferred, samples
    """
    s = sample_series(line, k, block, look_n, kind, side)
    base = {'dir': 0, 'tail_used': 0, 'reversal_bar': None, 'run': 0, 'travel': float('nan'),
            'deferred': 0, 'samples': s}
    if len(s) < 2:
        return base
    v = [x[1] for x in s]
    d = [_sign(v[i] - v[i + 1]) for i in range(len(v) - 1)]   # newest-first, newer minus older

    # ---- the run of same-signed diffs from the newest. Flats are transparent.
    first = next((i for i, x in enumerate(d) if x != 0), None)
    if first is None:
        return base                                   # every sample equal across the lookback
    run_dir = d[first]
    run = first + 1
    while run < len(d) and d[run] in (0, run_dir):
        run += 1
    # an UNCONFIRMED newest move - a run holding one non-flat diff - is not a confirmed reversal,
    # so it does not truncate the tail; keep walking through the prior run.
    if sum(1 for i in range(run) if d[i] != 0) < 2:
        j = run
        while j < len(d) and d[j] == 0: j += 1
        if j < len(d):
            pd = d[j]
            while j < len(d) and d[j] in (0, pd): j += 1
            run = j
    base['run'] = run
    base['reversal_bar'] = s[run][0] if run < len(s) else s[-1][0]

    # ---- the tail, truncated by the reversal
    t = min(int(tail_n), run)
    # ---- the deferral: step the far end back one sample at a time while the span is flat
    while t < len(v) - 1 and v[0] == v[t]:
        t += 1
        base['deferred'] += 1
    if t >= len(v): t = len(v) - 1
    base['tail_used'] = t
    base['travel'] = v[0] - v[t]
    base['dir'] = _sign(base['travel'])
    return base
