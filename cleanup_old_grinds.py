#!/usr/bin/env python3
"""
cleanup_old_grinds_v2.py — delete pk_signals + pk_outcomes + optimizer_runs
per or_pk in a range. No pre-inventory; just attempts deletes in order
and reports rowcount per batch.

Compared to v1: no SELECT COUNT(*) inventory phase (which was hitting
slow execution against the 120GB table). Goes straight to DELETE,
which uses the same index but reports rowcount after — faster and
the rowcount info is "free" from the operation itself.

Usage:
    python3 cleanup_old_grinds_v2.py                       # delete or_pk 1-27
    python3 cleanup_old_grinds_v2.py --max_or_pk=32        # custom cutoff
    python3 cleanup_old_grinds_v2.py --start_at=15         # resume from or_pk=15
    python3 cleanup_old_grinds_v2.py --keep_or_pks=32      # delete all EXCEPT or_pk=32

Run order per or_pk:
  1. SET FOREIGN_KEY_CHECKS = 0
  2. DELETE FROM pk_outcomes WHERE pks_or_pk = N (via JOIN to pk_signals)
  3. DELETE FROM pk_signals WHERE pks_or_pk = N
  4. DELETE FROM optimizer_runs WHERE or_pk = N
  5. SET FOREIGN_KEY_CHECKS = 1
"""

import argparse
import sys
import time

from optimus9.config              import get_db_config
from optimus9.db.database_manager import DatabaseManager


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--min_or_pk',   type=int, default=1)
    parser.add_argument('--max_or_pk',   type=int, default=27)
    parser.add_argument('--start_at',    type=int, default=None,
                        help='Resume from this or_pk (skips lower)')
    parser.add_argument('--keep_or_pks', type=str, default='')
    args = parser.parse_args()

    keep_set = set()
    if args.keep_or_pks:
        keep_set = {int(x.strip()) for x in args.keep_or_pks.split(',') if x.strip()}

    start_at = args.start_at if args.start_at is not None else args.min_or_pk

    db = DatabaseManager(**get_db_config())
    db.connect()
    try:
        print(f'Range: or_pk={start_at} .. {args.max_or_pk}')
        if keep_set:
            print(f'Keeping: {sorted(keep_set)}')
        print('=' * 70)

        confirm = input('Proceed with deletion? Type "yes": ')
        if confirm.strip().lower() != 'yes':
            print('Aborted.')
            return 1
        print()

        total_sigs_deleted = 0
        total_outs_deleted = 0
        total_runs_deleted = 0

        for or_pk in range(start_at, args.max_or_pk + 1):
            if or_pk in keep_set:
                print(f'  or_pk={or_pk:>3}: skip (kept)')
                continue

            start = time.time()
            outs, sigs, runs = _delete_or_pk(db, or_pk)
            elapsed = time.time() - start

            if outs == 0 and sigs == 0 and runs == 0:
                print(f'  or_pk={or_pk:>3}: empty ({elapsed:.1f}s)')
                continue

            total_outs_deleted += outs
            total_sigs_deleted += sigs
            total_runs_deleted += runs

            print(f'  or_pk={or_pk:>3}: '
                  f'-{outs:>8,} outs  '
                  f'-{sigs:>8,} sigs  '
                  f'-{runs} runs  '
                  f'({elapsed:.1f}s)')

        print('=' * 70)
        print(
            f'TOTAL: {total_outs_deleted:,} outcomes, '
            f'{total_sigs_deleted:,} signals, '
            f'{total_runs_deleted} run rows'
        )
        print()
        print('To reclaim disk (slow — rebuilds tables):')
        print('  OPTIMIZE TABLE pk_signals;')
        print('  OPTIMIZE TABLE pk_outcomes;')
        return 0
    finally:
        db.disconnect()


def _delete_or_pk(db, or_pk: int):
    """Returns (outs_deleted, sigs_deleted, runs_deleted) rowcounts."""
    db.execute('SET FOREIGN_KEY_CHECKS = 0', fetch=False)
    try:
        # Need to capture rowcount from each DELETE. DatabaseManager's execute()
        # may or may not return it — try cursor approach if execute() doesn't.
        # Falling back to the cursor pattern for reliable rowcount visibility.

        cursor = db._conn.cursor()
        try:
            cursor.execute(
                '''DELETE po FROM pk_outcomes po
                   JOIN pk_signals ps ON ps.pks_pk = po.pko_pks_pk
                   WHERE ps.pks_or_pk = %s''',
                (or_pk,)
            )
            outs = cursor.rowcount

            cursor.execute(
                'DELETE FROM pk_signals WHERE pks_or_pk = %s',
                (or_pk,)
            )
            sigs = cursor.rowcount

            cursor.execute(
                'DELETE FROM optimizer_runs WHERE or_pk = %s',
                (or_pk,)
            )
            runs = cursor.rowcount
        finally:
            cursor.close()

        return outs, sigs, runs
    finally:
        db.execute('SET FOREIGN_KEY_CHECKS = 1', fetch=False)


if __name__ == '__main__':
    sys.exit(main())
