#!/usr/bin/env python3
"""
apply_r07_vectorize_pk_classes.py — replace PKStateComputer and
PKSignalDetector with their vectorized numpy implementations.

Drop-in: same interface, same output shape, same signal dict keys.
Internal implementations rewritten for ~10x speedup on the grind.

Pre-reqs (drop into optimus9/compute/ BEFORE running):
  - optimus9/compute/pk_state_computer.py  (vectorized version)
  - optimus9/compute/pk_signal_detector.py (vectorized version)

This script doesn't actually edit the .py files — they're file replacements
done at the cp step above. This script's job is to:
  1. Verify imports still work after the swap
  2. Print the next-step validation sequence

If you've already copied the new files in, just run this for verification.

Usage:
  python3 apply_r07_vectorize_pk_classes.py
"""

import sys


def main() -> int:
    print('r07 PKStateComputer + PKSignalDetector vectorization')
    print('=' * 70)
    print()
    print('Step 1: verify imports')
    try:
        from optimus9 import PKStateComputer, PKGateFilter, PKSignalDetector
        sc = PKStateComputer(high_b=85.0, low_b=15.0)
        gf = PKGateFilter()
        d  = PKSignalDetector(state_computer=sc, gate_filter=gf)
        print(f'+  Imports successful')
        print(f'+  Instantiation successful')
    except Exception as e:
        print(f'X  Import or instantiation failed: {e}')
        return 1

    print()
    print('Step 2: verify pandas dependency')
    try:
        import pandas as pd
        print(f'+  pandas {pd.__version__} available')
    except ImportError:
        print('X  pandas not available — PKStateComputer.compute() will fail')
        return 1

    print()
    print('-- NEXT --')
    print('Snapshot the or_pk=44 reference (if not done already):')
    print('  python3 snapshot_pk_signals.py --or_pk=44 --output=or44_reference.csv')
    print()
    print('Then re-grind the same config to validate:')
    print('  python3 run.py start --tc_pk=99 --lookback_days=1 --skip_analyze')
    print()
    print('Snapshot the new run:')
    print('  python3 snapshot_pk_signals.py --or_pk=<NEW> --output=or<NEW>_vectorized.csv')
    print()
    print('Compare in Excel — align on timestamps, expect overlapping rows to match exactly.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
