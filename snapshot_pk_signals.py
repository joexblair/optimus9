#!/usr/bin/env python3
"""
snapshot_pk_signals.py — dump pk_signals rows for an or_pk to a CSV with
deterministic ordering, for use as a validation checkpoint against future
refactors.

Usage:
    # Capture reference (e.g. before Phase A vectorization)
    python3 snapshot_pk_signals.py --or_pk=44 --output=or44_reference.csv

    # After refactor + re-grind:
    python3 snapshot_pk_signals.py --or_pk=<NEW> --output=or<NEW>_actual.csv

    # Compare:
    diff <(sort or44_reference.csv) <(sort or<NEW>_actual.csv) | head -50

Ordering is by (len, src, slope_floor, pool, timestamp) so two grinds of
the same param ranges produce identical-ordered output. pks_pk varies
across runs (auto-increment), so it is EXCLUDED from output.
"""

import argparse
import csv
import sys

from optimus9.config              import get_db_config
from optimus9.db.database_manager import DatabaseManager


# Columns dumped. pks_pk excluded (auto-increment, varies across runs).
# pks_or_pk excluded (the filter, redundant).
_COLUMNS = [
    'pks_timestamp',
    'pks_dir',
    'pks_pool',
    'pks_state',
    'pks_line_value',
    'pks_slope',
    'pks_slope_diff',
    'pks_dema_slope',
    'pks_dema_value',
    'pks_len',
    'pks_mult',
    'pks_src',
    'pks_pool_c',
    'pks_pool_w',
    'pks_pool_range',
    'pks_slope_floor',
    'pks_multiplier',
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--or_pk',  type=int, required=True)
    parser.add_argument('--output', type=str, required=True)
    args = parser.parse_args()

    db = DatabaseManager(**get_db_config())
    db.connect()
    try:
        # Verify the run exists and get expected count
        meta = db.execute(
            '''SELECT COUNT(*) AS c FROM pk_signals WHERE pks_or_pk = %s''',
            (args.or_pk,), fetch=True,
        )
        expected = int(meta[0]['c']) if meta else 0
        if expected == 0:
            print(f'No signals found for or_pk={args.or_pk}', file=sys.stderr)
            return 1
        print(f'or_pk={args.or_pk}: {expected:,} signals to snapshot')

        col_csv = ', '.join(_COLUMNS)
        rows = db.execute(
            f'''SELECT {col_csv}
                FROM pk_signals
                WHERE pks_or_pk = %s
                ORDER BY pks_len, pks_src, pks_slope_floor,
                         pks_pool_c, pks_pool_w, pks_pool, pks_timestamp''',
            (args.or_pk,), fetch=True,
        )
        if not rows:
            print('Query returned no rows (unexpected after count check)', file=sys.stderr)
            return 1

        with open(args.output, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=_COLUMNS)
            writer.writeheader()
            for r in rows:
                writer.writerow({k: r[k] for k in _COLUMNS})

        print(f'Wrote {len(rows):,} rows to {args.output}')
        if len(rows) != expected:
            print(f'!  count mismatch: query returned {len(rows):,}, '
                  f'expected {expected:,}', file=sys.stderr)
            return 1
        return 0
    finally:
        db.disconnect()


if __name__ == '__main__':
    sys.exit(main())
