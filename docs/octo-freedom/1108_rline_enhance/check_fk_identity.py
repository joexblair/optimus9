#!/usr/bin/env python3
"""Prove the 1108 extraction left the developing K line bit-identical, and show the pin reader.

WHY A SYNTHETIC FRAME: the identity has to be checkable without a DB, a Jig or the 1.6 M bar tape,
so a refactor of `_k_developing` can be verified in seconds instead of a tape load. The frame is a
fixed-seed random walk, 3 days at the 5 s grid - long enough for a 30-minute line to warm up.

usage: check_fk_identity.py            # compares against the stored baseline, writes it if absent
"""
import os
import sys

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from synth_frame import frame                                        # noqa: E402
from optimus9.compute.indicator_computer import IndicatorComputer as IC   # noqa: E402

TFS = (1800, 1740, 1680, 1620, 300, 60)
KLEN, RSI, STC, SRC = 7, 5, 8, 'close'
BASELINE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fk_baseline.npz')


def main():
    base = frame()
    now = {'tf%d' % t: np.asarray(IC.f_k_lookahead(base, t, KLEN, RSI, STC, SRC), float)
           for t in TFS}
    if not os.path.exists(BASELINE):
        np.savez(BASELINE, **now)
        print('baseline written - %d lines' % len(now))
        return 0
    was = np.load(BASELINE)
    print('| the tf | the developing K line | max abs diff | the NaN pattern |')
    print('|---|---|---|---|')
    ok = True
    for t in TFS:
        k = 'tf%d' % t
        b, a = np.asarray(was[k], float), now[k]
        same_nan = np.array_equal(np.isnan(b), np.isnan(a))
        m = np.isfinite(b) & np.isfinite(a)
        d = float(np.max(np.abs(b[m] - a[m]))) if m.any() else -1.0
        good = (d == 0.0 and same_nan)
        ok = ok and good
        print('| ws%d | %s | %g | %s |' % (t // 60, 'IDENTICAL' if good else 'DIFFERS', d,
                                           'same' if same_nan else 'CHANGED'))
    print()
    pin, rsi_d = IC.f_k_pin(base, 1800, KLEN, RSI, STC, SRC)
    f = np.isfinite(pin)
    print('| the pin reader on ws30 | value |')
    print('|---|---|')
    print('| bars with a pin value | %d of %d |' % (int(f.sum()), len(pin)))
    print('| pinned HIGH, +1 - the RSI is at or above the closed window max | %d |'
          % int((pin[f] == 1).sum()))
    print('| pinned LOW, -1 - at or below the min | %d |' % int((pin[f] == -1).sum()))
    print('| free or degenerate, 0 - do not substitute | %d |' % int((pin[f] == 0).sum()))
    print()
    print('the extraction is bit-identical' if ok else 'THE EXTRACTION CHANGED THE LINE')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
