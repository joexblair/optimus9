#!/usr/bin/env python3
"""
export_gate_windows.py — export merged gate-open windows for a tc_pk to CSV.

For tc_pk=18 (gca5m_PROVEN_test) the gates are bny30M and bny30p. A "gate
window" is a contiguous run of bars where either gate is OOB. Overlapping
or adjacent windows from the two gates are merged into a single row.

The reconstruction here uses the SET of timestamps where at least one PK
signal fired across all combos in the or_pk — this is approximately the
gate-open bar set (subject to: a gate-open bar with no qualifying PK
pattern in any combo across all 55K combos won't appear; in practice
this is a small minority for a dense grind).

Output: gate_windows_or<N>.csv with columns:
    gate_open_utc        - ISO 8601 timestamp when gate opened
    gate_close_utc       - ISO 8601 timestamp when gate closed
    duration_seconds     - window duration

Usage:
    python3 export_gate_windows.py --or_pk=32
    python3 export_gate_windows.py --or_pk=32 --output_dir=/tmp
"""

import argparse
import csv
import sys
from datetime import datetime, timezone
from pathlib import Path

from optimus9.config              import get_db_config
from optimus9.db.database_manager import DatabaseManager


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Export merged gate-open windows for an or_pk'
    )
    parser.add_argument('--or_pk',      type=int, required=True)
    parser.add_argument('--output_dir', type=str, default='.')
    parser.add_argument('--bar_seconds', type=int, default=5,
                        help='Bar duration in seconds (default 5 for 5s strategy)')
    args = parser.parse_args()

    db = DatabaseManager(**get_db_config())
    db.connect()
    try:
        print(f'Querying distinct gate-open timestamps for or_pk={args.or_pk}...')
        rows = db.execute(
            '''SELECT DISTINCT pks_timestamp AS ts_ms
               FROM pk_signals
               WHERE pks_or_pk = %s
               ORDER BY pks_timestamp ASC''',
            (args.or_pk,), fetch=True,
        )
        if not rows:
            print(f'No signals found for or_pk={args.or_pk}')
            return 1

        timestamps = sorted({int(r['ts_ms']) for r in rows})
        print(f'Loaded {len(timestamps)} distinct gate-open bar timestamps')

        # Merge contiguous bars into windows
        bar_ms     = args.bar_seconds * 1000
        gap_factor = 2  # allow tiny gaps within a window (e.g. 1-bar PK skip)
        windows    = _merge_to_windows(timestamps, bar_ms, gap_factor)
        print(f'Merged into {len(windows)} gate-open windows')

        # Write CSV
        output_path = Path(args.output_dir) / f'gate_windows_or{args.or_pk}.csv'
        with output_path.open('w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['gate_open_utc', 'gate_close_utc', 'duration_seconds'])
            for open_ms, close_ms in windows:
                open_iso  = _ms_to_iso(open_ms)
                close_iso = _ms_to_iso(close_ms)
                dur_sec   = (close_ms - open_ms) // 1000
                writer.writerow([open_iso, close_iso, dur_sec])

        print(f'\nWrote: {output_path}')
        if windows:
            total_open_sec = sum((c - o) // 1000 for o, c in windows)
            first_open  = _ms_to_iso(windows[0][0])
            last_close  = _ms_to_iso(windows[-1][1])
            print(f'Coverage: {first_open}  →  {last_close}')
            print(f'Total open time: {total_open_sec:,} seconds ({total_open_sec / 3600:.1f} hours)')
            print(f'Avg window length: {total_open_sec / len(windows):.1f} seconds')
        return 0
    finally:
        db.disconnect()


def _merge_to_windows(timestamps: list, bar_ms: int, gap_factor: int) -> list:
    """Collapse contiguous (within gap_factor bars) timestamps into [open, close] pairs."""
    if not timestamps:
        return []
    max_gap_ms = bar_ms * gap_factor
    windows    = []
    open_ms    = timestamps[0]
    prev_ms    = timestamps[0]
    for ts in timestamps[1:]:
        if ts - prev_ms > max_gap_ms:
            windows.append((open_ms, prev_ms + bar_ms))
            open_ms = ts
        prev_ms = ts
    windows.append((open_ms, prev_ms + bar_ms))
    return windows


def _ms_to_iso(ms: int) -> str:
    dt = datetime.fromtimestamp(ms / 1000, tz=timezone.utc)
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


if __name__ == '__main__':
    sys.exit(main())
