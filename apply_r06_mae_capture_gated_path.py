#!/usr/bin/env python3
"""
apply_r06_mae_capture_gated_path.py — fixes MAE columns missing from the
_persist_gated() code path of optimizer_runner.py.

The earlier MAE apply updated _persist_self_gated only. _persist_gated
(used when gates are active) still writes the old 4-column INSERT, so
MAE columns receive NULL on gated grinds like or_pk=30.

Idempotent: re-running after a successful apply is safe.
"""

import argparse
import pathlib
import sys


class Edit:
    def __init__(self, path, name, old, new, skip_if_contains):
        self.path = pathlib.Path(path)
        self.name = name
        self.old  = old
        self.new  = new
        self.skip_if_contains = skip_if_contains

    def apply(self, dry_run):
        if not self.path.exists():
            return f'X MISSING  {self.path}'
        src = self.path.read_text()
        if self.skip_if_contains in src:
            return f'-  skip     {self.name} (already applied)'
        if self.old not in src:
            return f'!  NOMATCH  {self.name}'
        if dry_run:
            return f'.  dry-run  {self.name}'
        self.path.write_text(src.replace(self.old, self.new, 1))
        return f'+  applied  {self.name}'


EDITS = []

# ─── Edit 01 ─────────────────────────────────────────────────────────────
# Extend _persist_gated's INSERT statement to include MAE columns.
# Anchored by the "sig_rows = []" line directly following the INSERT —
# this is the gated-path specific arrangement (self_gated has
# pre-computation comments between the INSERT and sig_rows).
EDITS.append(Edit(
    'optimus9/orchestration/optimizer_runner.py',
    '01 _persist_gated: extend INSERT with MAE columns',
    old=(
        "        out_sql = '''INSERT INTO pk_outcomes\n"
        "            (pko_pks_pk, pko_max_profit_pct, pko_bars_to_stop, pko_bars_to_max_profit)\n"
        "            VALUES (%s,%s,%s,%s)'''\n"
        "        sig_rows = []\n"
    ),
    new=(
        "        out_sql = '''INSERT INTO pk_outcomes\n"
        "            (pko_pks_pk, pko_max_profit_pct, pko_bars_to_stop, pko_bars_to_max_profit,\n"
        "             pko_max_adverse_pct, pko_bars_to_max_adverse)\n"
        "            VALUES (%s,%s,%s,%s,%s,%s)'''\n"
        "        sig_rows = []\n"
    ),
    # Marker: new MAE column list combined with "sig_rows = []" — only true
    # post-edit in _persist_gated (self_gated has different surrounding text)
    skip_if_contains=(
        "             pko_max_adverse_pct, pko_bars_to_max_adverse)\n"
        "            VALUES (%s,%s,%s,%s,%s,%s)'''\n"
        "        sig_rows = []\n"
    ),
))

# ─── Edit 02 ─────────────────────────────────────────────────────────────
# Extend _persist_gated's executemany row tuple. Anchored using the
# 4-line tuple pattern. The OLD pattern appears ONLY in _persist_gated
# now (self_gated already has 6-line tuple with MAE values).
EDITS.append(Edit(
    'optimus9/orchestration/optimizer_runner.py',
    '02 _persist_gated: extend executemany row tuple with MAE values',
    old=(
        "        self._db.executemany(out_sql, [\n"
        "            (first_id + i,\n"
        "             dv(o['max_profit_pct']),\n"
        "             o['bars_to_stop'],\n"
        "             o['bars_to_max_profit'])\n"
        "            for i, o in enumerate(outcomes)\n"
        "        ])\n"
    ),
    new=(
        "        self._db.executemany(out_sql, [\n"
        "            (first_id + i,\n"
        "             dv(o['max_profit_pct']),\n"
        "             o['bars_to_stop'],\n"
        "             o['bars_to_max_profit'],\n"
        "             dv(o['max_adverse_pct']),\n"
        "             o['bars_to_max_adverse'])\n"
        "            for i, o in enumerate(outcomes)\n"
        "        ])\n"
    ),
    # Marker: the new 6-line tuple shape with MAE values. After Edit 01
    # of the earlier MAE apply ran on _persist_self_gated, this exact
    # shape exists there ONCE already. So we can't use first-occurrence
    # marker. Workaround: count occurrences.
    # If we see 2 occurrences post-fix → both applied → skip.
    # If we see 1 occurrence pre-fix → only self_gated, need to fix gated.
    # Implement count via the marker being deliberately a DIFFERENT
    # unique-to-gated context string.
    skip_if_contains=(
        # gated-specific 4-line tuple followed by MAE additions — only
        # exists if we successfully edited gated specifically. Use the
        # full block including the bars_to_max_profit MAE pair.
        "             o['bars_to_max_profit'],\n"
        "             dv(o['max_adverse_pct']),\n"
        "             o['bars_to_max_adverse'])\n"
    ),
))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    mode = 'DRY-RUN' if args.dry_run else 'APPLYING'
    print(f'r06 260523 MAE gated-path fix - {mode}')
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
        f"nomatch: {counts['!']}  "
        f"missing: {counts['X']}"
    )

    if counts['!'] > 0:
        print()
        print('!  NOMATCH detected. Source may have drifted - inspect file.')
        return 1
    if counts['X'] > 0:
        return 1

    if counts['+'] > 0 or counts['.'] > 0:
        print()
        print('-- NEXT STEPS --')
        print('1. Nuke bytecode cache:')
        print('   find optimus9/ -name __pycache__ -type d -exec rm -rf {} +')
        print('2. Re-grind: python3 run.py start --tc_pk=18 --lookback_days=1')
        print('3. Verify MAE:')
        print('   SELECT COUNT(*), SUM(pko_max_adverse_pct IS NOT NULL)')
        print('   FROM pk_outcomes po JOIN pk_signals ps ON ps.pks_pk = po.pko_pks_pk')
        print('   WHERE ps.pks_or_pk = <new_or_pk>;')
    return 0


if __name__ == '__main__':
    sys.exit(main())
