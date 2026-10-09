"""ws12r MOM-TRUE, as a cached mask. 1009.

Joe 1009: *"oooh... we could open the trade on ws12r mom-true"* / *"I like the ws12 mom-true event
idea"*.

mom-true IS `momo` OR `curl`. Joe 1009: *"I use mom-true as shorthand for momentum.momo and
momentum.curl - these are the only momentum states we're reliant on, afaik"*.

CORRECTED 1009. The first mask counted only `'momo'` and dropped every `curl`. `momo_core.verdict`
returns one of four states - `momo`, `curl`, `sideways`, `none` (`momo_core.py:180-212`) - and
`momo_gated.momo_g` turns an ungated curl into `none` after Joe's 0805 curl gates. So the test is
`momo_g(...)[0] in ('momo', 'curl')`, and a curl that fails those gates is correctly excluded.

THE EVENT IS THE RISING EDGE. Joe said *"the ws12 mom-true EVENT"*, so the open bar is where ws12r
BECOMES mom-true, not any bar where it happens to be mom-true. MY READING, stated.

WHICH FUNCTION, RULED BY JOE 1009: *"we're not using it for our current builds"* - of
`strip_mom_at_fence`. So mom-true here is `momo_gated.momo_g`: Joe's 0805 curl gates ON, the
0920 strip-mom-at-fence OFF. `momo_g` does not pass the fence (`momo_gated.py:51-58`), so this is
the default with no argument.

  W_MOMT_FN 'gated'  momo_gated.momo_g  - curl gates on, strip off. JOE'S RULING, THE DEFAULT
  W_MOMT_FN 'core'   momo_core.momo     - the bare verdict, kept only as a cross-check

WHAT THE STRIP WOULD HAVE DONE, recorded because it sits right on top of this event and is now
explicitly out: it strips the mom-true tag once r passes the r-momo-fence 17/83 on the dr side. ws12r
climbs through 83 on its way to oob 85, so the strip would have expired mom-true JUST BEFORE every
oob event this mech studies. Not in play, per Joe. `docs/octo-freedom/1005_knobs.md:463` lists it as
a spec open question; this rules it for these builds only, not for that question.

On a 2,000-bar slice at bar 500,000 `momo_g` and `momo_core.momo` agreed exactly, 58 hits each.

THE CACHE IS KEYED ON THE TAPE WINDOW. A hash-keyed cache that ignores the window is how four
hours of work got voided on 1008 - the LIVE control row caught it. The key carries score39's EM,
HOURS and WARMUP plus the TF and its banked k_window, and a mismatch rebuilds rather than loads.
"""
import os, sys, time, hashlib, json
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.compute import momo_core as MC
from optimus9.compute.momo_config import momo_config
from optimus9.compute.momo_gated import momo_window, momo_g

CACHE = '/home/joe/.claude/jobs/6eb9931e/tmp/momt_cache'


STATES = ('momo', 'curl')      # Joe 1009. In the cache key, so changing it invalidates the cache.


def _key(em, hours, warmup, tf, kw, fn):
    return hashlib.md5(json.dumps([int(em), int(hours), int(warmup), int(tf), int(kw),
                                   str(fn), list(STATES)]).encode()).hexdigest()[:20]


def momtrue_mask(line, tf, bank, em, hours, warmup, fn='gated', n=None, log=print):
    """Per bar, is this line mom-true, for each side. -> {+1: bool array, -1: bool array}

    The mask is cached on disk under a key that carries the TAPE WINDOW. Causal: `momo` fits a
    window that ends at the bar it is asked about and reads nothing after it.
    """
    n = len(line) if n is None else int(n)
    os.makedirs(CACHE, exist_ok=True)
    kw = int(bank['k_window'])
    k = _key(em, hours, warmup, tf, kw, fn)
    p = os.path.join(CACHE, 'momt_%s.npz' % k)
    if os.path.exists(p):
        z = np.load(p)
        if len(z['p']) == n:
            log('# mom-true mask loaded from cache %s, %d bars' % (k, n))
            return {+1: z['p'].astype(bool), -1: z['m'].astype(bool)}
        log('# cache %s has %d bars, this tape has %d — REBUILDING' % (k, len(z['p']), n))
    f = momo_g if fn == 'gated' else MC.momo
    out = {}
    t0 = time.time()
    for d in (+1, -1):
        a = np.zeros(n, bool)
        with momo_config(bank):
            with momo_window(kw * int(tf)):
                for j in range(n):
                    v = f(line, d, j)
                    if (v[0] if isinstance(v, tuple) else v) in STATES:
                        a[j] = True
        out[d] = a
        log('# mom-true (%s) side %+d built: %d of %d bars = %.2f%%  (%.0fs)'
            % ('+'.join(STATES), d, int(a.sum()), n, 100.0 * a.sum() / n, time.time() - t0))
    np.savez_compressed(p, p=out[+1], m=out[-1])
    log('# mom-true mask cached as %s' % k)
    return out


def rising(mask):
    """The RISING EDGE of a boolean mask - the bar it becomes true."""
    r = np.zeros(len(mask), bool)
    r[1:] = mask[1:] & ~mask[:-1]
    return r
