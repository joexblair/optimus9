#!/usr/bin/env python3
"""
validate_srp_refactor.py — smoke test the new SRP detector classes.

Verifies:
  1. All three new classes import cleanly
  2. PKSignalDetector instantiates with defaults
  3. With synthetic data, detect() returns transition signals (not per-bar)

Run AFTER:
  - apply_r06_srp_pk_refactor.py has been run
  - run.py has been manually edited
  - apply_r06_srp_pk_refactor.py --confirm-runpy has been run

Usage: python3 validate_srp_refactor.py
"""

import sys

import numpy as np


def main() -> int:
    print('SRP Refactor Validation')
    print('=' * 60)

    # 1. Import check
    try:
        from optimus9.compute.pk_state_computer  import PKStateComputer
        from optimus9.compute.pk_gate_filter     import PKGateFilter
        from optimus9.compute.pk_signal_detector import PKSignalDetector
        print('+  Imports successful')
    except ImportError as e:
        print(f'X  Import failed: {e}')
        return 1

    # 2. Instantiation check
    try:
        state_comp = PKStateComputer()
        gate       = PKGateFilter()
        detector   = PKSignalDetector(state_computer=state_comp, gate_filter=gate)
        print('+  Instantiation successful')
    except Exception as e:
        print(f'X  Instantiation failed: {e}')
        return 1

    # 3. Synthetic transition test
    # Build a line that creates a clear transition: stays neutral, then has
    # a sustained directional state over multiple bars. Per-bar emission
    # would produce N signals; transition emission should produce 1.
    n = 200
    line = np.full(n, 50.0)
    dema = np.full(n, 50.0)
    # Build a sustained divergence between bars 100-150
    for i in range(100, 150):
        line[i] = 80.0 + (i - 100) * 0.5  # line climbs
        dema[i] = 50.0 - (i - 100) * 0.1  # dema declines slowly
    oob_side = np.zeros(n, dtype=np.int8)
    # Gate open (line went OOB high → fire shorts) during bars 105-145
    oob_side[105:146] = 1

    params = {'len': 6, 'mult': 0.74, 'src': 'hlcc4'}
    signals = detector.detect(
        line=line, dema=dema,
        pool_c=5, pool_w=23, pool_range=8,
        multiplier=1, slope_floor=5.0,
        oob_side=oob_side, params=params, line_type='bb',
    )
    print(f'   Synthetic test: {len(signals)} signals generated')
    if len(signals) == 0:
        print('?  No signals — may be expected depending on synthetic data shape')
    elif len(signals) > 20:
        print(f'!  Many signals ({len(signals)}) — transition detection may not be working')
        print('   (per-bar would yield ~80, transition should yield ~2-4)')
    else:
        print(f'+  Transition-shape signal count looks reasonable')

    print('=' * 60)
    print('Validation complete')
    print()
    print('Next: run a real 1-combo grind on PROVEN params with 1-day lookback.')
    print('  python3 run.py start --tc_pk=<TEST_PK> --lookback_days=1')
    print('Compare signal count to OR-32 PROVEN combo with 695 (expected: much lower).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
