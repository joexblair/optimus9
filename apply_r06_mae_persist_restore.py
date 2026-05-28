#!/usr/bin/env python3
"""
apply_r06_mae_persist_restore.py — restore MAE persistence in both
_persist_self_gated and _persist_gated.

CONTEXT:
A VS Code revert dropped this back to the pre-r06 state — both methods had
6-column pk_outcomes INSERTs (with pko_max_adverse_pct + pko_bars_to_max_adverse)
and now they have only 4. OutcomeWalker still computes MAE correctly and
the outcome dicts still carry the keys; they're just being dropped at
persistence time.

This script restores both INSERTs to the 6-column form AND extends the
executemany row tuples to include the MAE values.

Both edits are identical (same SQL, same tuple shape) and appear in both
methods, so we apply each edit twice — once for each occurrence.

Idempotent: re-running is a no-op (skip guards on each edit).
"""

import argparse
import pathlib
import sys


class Edit:
    """Same-pattern edit that may need to apply MULTIPLE times in one file."""
    def __init__(self, path, name, old, new, skip_marker, count=1):
        self.path = pathlib.Path(path)
        self.name = name
        self.old  = old
        self.new  = new
        self.skip_marker = skip_marker
        self.count = count  # how many times this pattern should appear after apply

    def apply(self, dry_run):
        if not self.path.exists():
            return f'X MISSING  {self.path}'
        src = self.path.read_text()

        # Check if already applied — skip_marker present `count` times means done
        if src.count(self.skip_marker) >= self.count:
            return f'-  skip     {self.name} (already applied {self.count}x)'

        # Count old occurrences — must match what we expect to replace
        occurrences = src.count(self.old)
        if occurrences == 0:
            return f'!  NOMATCH  {self.name}'
        if occurrences != self.count:
            return f'!  COUNT_MISMATCH  {self.name} (found {occurrences}, expected {self.count})'

        if dry_run:
            return f'.  dry-run  {self.name} ({occurrences} replacements)'

        # Replace ALL occurrences (count=2 here for both _persist methods)
        new_src = src.replace(self.old, self.new)
        self.path.write_text(new_src)
        return f'+  applied  {self.name} ({occurrences} replacements)'


EDITS = []

# ─── Edit 1: out_sql INSERT — 4 cols → 6 cols ──────────────────────────────
# Appears twice (once in each persist method) and we want both replaced.
EDITS.append(Edit(
    'optimus9/orchestration/optimizer_runner.py',
    '01 out_sql INSERT restore MAE columns',
    old=(
        "        out_sql = '''INSERT INTO pk_outcomes\n"
        "            (pko_pks_pk, pko_max_profit_pct, pko_bars_to_stop, pko_bars_to_max_profit)\n"
        "            VALUES (%s,%s,%s,%s)'''"
    ),
    new=(
        "        out_sql = '''INSERT INTO pk_outcomes\n"
        "            (pko_pks_pk, pko_max_profit_pct, pko_bars_to_stop, pko_bars_to_max_profit,\n"
        "             pko_max_adverse_pct, pko_bars_to_max_adverse)\n"
        "            VALUES (%s,%s,%s,%s,%s,%s)'''"
    ),
    skip_marker='pko_max_adverse_pct, pko_bars_to_max_adverse',
    count=2,
))

# ─── Edit 2: executemany tuple — 4 values → 6 values ───────────────────────
# Also appears twice. Same shape both times per the grep.
EDITS.append(Edit(
    'optimus9/orchestration/optimizer_runner.py',
    '02 executemany tuple include MAE values',
    old=(
        "        self._db.executemany(out_sql, [\n"
        "            (first_id + i,\n"
        "             dv(o['max_profit_pct']),\n"
        "             o['bars_to_stop'],\n"
        "             o['bars_to_max_profit'])\n"
        "            for i, o in enumerate(outcomes)\n"
        "        ])"
    ),
    new=(
        "        self._db.executemany(out_sql, [\n"
        "            (first_id + i,\n"
        "             dv(o['max_profit_pct']),\n"
        "             o['bars_to_stop'],\n"
        "             o['bars_to_max_profit'],\n"
        "             dv(o.get('max_adverse_pct')),\n"
        "             o.get('bars_to_max_adverse'))\n"
        "            for i, o in enumerate(outcomes)\n"
        "        ])"
    ),
    skip_marker="dv(o.get('max_adverse_pct'))",
    count=2,
))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    mode = 'DRY-RUN' if args.dry_run else 'APPLYING'
    print(f'r06 MAE persist restore — {mode}')
    print('=' * 70)

    counts = {'!': 0, '-': 0, '+': 0, '.': 0, 'X': 0}
    for edit in EDITS:
        status = edit.apply(args.dry_run)
        print(status)
        prefix = status[0]
        if prefix in counts:
            counts[prefix] += 1

    print('=' * 70)
    print(
        f"Total: {len(EDITS)} edits  |  "
        f"applied: {counts['+'] + counts['.']}  "
        f"skipped: {counts['-']}  "
        f"nomatch/count_mismatch: {counts['!']}  "
        f"missing: {counts['X']}"
    )

    if counts['!'] > 0 or counts['X'] > 0:
        print()
        print('!  Some edits did not apply. The file may have diverged from the')
        print('   shape we grepped earlier. Inspect manually before retrying.')
        return 1

    print()
    print('Sanity check after apply:')
    print('  grep -c "pko_max_adverse_pct, pko_bars_to_max_adverse" optimus9/orchestration/optimizer_runner.py')
    print('  # Expected: 2  (one per _persist method)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
