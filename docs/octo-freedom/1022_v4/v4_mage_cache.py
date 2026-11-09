"""The Mage lines above the r ladder's top, cached off disk the way every other line is.

GOAL: give the handoff walk's ws{TF+2}Mage timer a line to read when the rider sits on ws29 or
ws30. HIS 1109: *"add ws31-33Mage"*. Without them `timer('mage')` returned None at ws29 and the
Mage chain could never carry a rider past ws28.

WHY A BUILD IS NEEDED AT ALL: `ln.line` resolves a line by its ROLE SPEC and its TF seconds, not
by a name in the config view - only ws1..ws10, ws15 and ws22 are registered there - so the cache
file for a TF nobody has asked for yet simply does not exist. ws11Mage..ws30Mage are on disk
because earlier work built them the same way.

IT REUSES `cache_jig_perline`, the one driver that owns the cache key, the batching and the atomic
write. A fresh build loop here would be a second opinion on the key.

usage: v4_mage_cache.py [tf ...]      # default 31 32 33, then print what is cached
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
_e = sys.stderr
sys.stderr = io.StringIO()
try:
    from optimus9.compute.line_config import override
    from optimus9.orchestration.build_ws_lines import HOURS, WARMUP
    from optimus9.orchestration.rpl_cache import LINE_DIR, _line_key, cache_jig_perline
finally:
    sys.stderr = _e

TFS = [int(x) for x in sys.argv[1:]] or [31, 32, 33]


def key(tf):
    """The cache path `ln.line('ws{tf}Mage')` reads. ONE source for the key - ln.py's own form."""
    return os.path.join(LINE_DIR, _line_key(ln.EM, HOURS, WARMUP,
                                            override(tf * 60, *ln.SPEC['Mage'])) + '.npy')


def main():
    ovr = {'ws%dMage' % t: override(t * 60, *ln.SPEC['Mage']) for t in TFS}
    missing = [t for t in TFS if not os.path.exists(key(t))]
    print('# %d Mage line(s) wanted, %d already cached, %d to build'
          % (len(TFS), len(TFS) - len(missing), len(missing)))
    t0 = time.time()
    if missing:
        cache_jig_perline(ln.EM, HOURS, WARMUP,
                          {'ws%dMage' % t: ovr['ws%dMage' % t] for t in missing})
        print('# the build took %.0f s' % (time.time() - t0))
    print()
    print('| the line | bars | first finite | last | min | max |')
    print('|---|---|---|---|---|---|')
    for t in TFS:
        a = ln.line('ws%dMage' % t)
        f = np.flatnonzero(np.isfinite(a))
        assert len(f), 'ws%dMage is finite nowhere' % t
        print('| ws%dMage | %d | %s | %.2f | %.2f | %.2f |'
              % (t, len(a), ln.U(int(f[0])), float(a[int(f[-1])]),
                 float(np.nanmin(a)), float(np.nanmax(a))))


main()
