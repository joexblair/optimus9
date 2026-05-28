#!/usr/bin/env python3
"""
apply_r06_mae_capture.py — adds Max Adverse Excursion (MAE) to per-signal outcomes.

Changes:
  1. outcome_walker.walk_outcome() — additionally tracks max_adverse_pct
     and bars_to_max_adverse during the per-bar walk. Returned in the dict.
  2. (Manual) ALTER TABLE pk_outcomes ADD COLUMN pko_max_adverse_pct DOUBLE NULL
     — SQL printed at end for Joe to run.
  3. Best-effort edit to optimizer_runner.py to persist the new column.
     If the find target doesn't match the local file, prints what needs
     manual editing.

Idempotent. Safe to re-run.

Usage:
  python3 apply_r06_mae_capture.py           # apply
  python3 apply_r06_mae_capture.py --dry-run # preview
"""

import argparse
import pathlib
import sys


class Edit:
    def __init__(self, path: str, name: str, old: str, new: str,
                 skip_if_contains: str = None) -> None:
        self.path = pathlib.Path(path)
        self.name = name
        self.old  = old
        self.new  = new
        self.skip_if_contains = skip_if_contains

    def apply(self, dry_run: bool) -> str:
        if not self.path.exists():
            return f'✗ MISSING  {self.path}'
        src = self.path.read_text()
        marker = self.skip_if_contains or self.new[:60].strip()
        if marker in src:
            return f'⊝ skip     {self.name} (already applied)'
        if self.old not in src:
            return f'⚠ NOMATCH  {self.name} (old text not found)'
        if dry_run:
            return f'· dry-run  {self.name}'
        self.path.write_text(src.replace(self.old, self.new, 1))
        return f'✓ applied  {self.name}'


# ─── EDITS ──────────────────────────────────────────────────────────────────

EDITS = []

# 01 — outcome_walker.py: replace the whole walk function body to add MAE tracking
EDITS.append(Edit(
    'optimus9/compute/outcome_walker.py',
    '01 outcome_walker: add MAE tracking',
    old=(
        '    entry = float(close[entry_idx])\n'
        '    end   = len(close) - 1\n'
        '\n'
        '    if direction == 1:\n'
        '        stop_level = entry * (1.0 - stop_pct / 100.0)\n'
        '    else:\n'
        '        stop_level = entry * (1.0 + stop_pct / 100.0)\n'
        '\n'
        '    best_price         = entry\n'
        '    max_profit_pct     = 0.0\n'
        '    bars_to_max_profit = None\n'
        '    bars_to_stop       = None\n'
        '\n'
        '    for j in range(entry_idx + 1, end + 1):\n'
        '        c = float(close[j])\n'
        '\n'
        '        if direction == 1:\n'
        '            if c > best_price:\n'
        '                best_price         = c\n'
        '                max_profit_pct     = (best_price / entry - 1.0) * 100.0\n'
        '                bars_to_max_profit = j - entry_idx\n'
        '            if c <= stop_level:\n'
        '                bars_to_stop = j - entry_idx\n'
        '                break\n'
        '        else:\n'
        '            if c < best_price:\n'
        '                best_price         = c\n'
        '                max_profit_pct     = (entry / best_price - 1.0) * 100.0\n'
        '                bars_to_max_profit = j - entry_idx\n'
        '            if c >= stop_level:\n'
        '                bars_to_stop = j - entry_idx\n'
        '                break\n'
        '\n'
        '    return {\n'
        "        'max_profit_pct':     round(max_profit_pct, 6),\n"
        "        'bars_to_max_profit': bars_to_max_profit,\n"
        "        'bars_to_stop':       bars_to_stop,\n"
        '    }\n'
    ),
    new=(
        '    entry = float(close[entry_idx])\n'
        '    end   = len(close) - 1\n'
        '\n'
        '    if direction == 1:\n'
        '        stop_level = entry * (1.0 - stop_pct / 100.0)\n'
        '    else:\n'
        '        stop_level = entry * (1.0 + stop_pct / 100.0)\n'
        '\n'
        '    # Favourable excursion tracking\n'
        '    best_price          = entry\n'
        '    max_profit_pct      = 0.0\n'
        '    bars_to_max_profit  = None\n'
        '\n'
        '    # Adverse excursion tracking (r06 260522) — magnitude of worst\n'
        '    # against-direction excursion during the trade window. Used for\n'
        '    # per-signal dd_pct in Pine strategy labels + general MAE analysis.\n'
        '    worst_price         = entry\n'
        '    max_adverse_pct     = 0.0\n'
        '    bars_to_max_adverse = None\n'
        '\n'
        '    bars_to_stop        = None\n'
        '\n'
        '    for j in range(entry_idx + 1, end + 1):\n'
        '        c = float(close[j])\n'
        '\n'
        '        if direction == 1:\n'
        '            # Favourable\n'
        '            if c > best_price:\n'
        '                best_price         = c\n'
        '                max_profit_pct     = (best_price / entry - 1.0) * 100.0\n'
        '                bars_to_max_profit = j - entry_idx\n'
        '            # Adverse (LONG: price falling against us)\n'
        '            if c < worst_price:\n'
        '                worst_price         = c\n'
        '                max_adverse_pct     = (entry / worst_price - 1.0) * 100.0\n'
        '                bars_to_max_adverse = j - entry_idx\n'
        '            # Stop\n'
        '            if c <= stop_level:\n'
        '                bars_to_stop = j - entry_idx\n'
        '                break\n'
        '        else:\n'
        '            # Favourable\n'
        '            if c < best_price:\n'
        '                best_price         = c\n'
        '                max_profit_pct     = (entry / best_price - 1.0) * 100.0\n'
        '                bars_to_max_profit = j - entry_idx\n'
        '            # Adverse (SHORT: price rising against us)\n'
        '            if c > worst_price:\n'
        '                worst_price         = c\n'
        '                max_adverse_pct     = (worst_price / entry - 1.0) * 100.0\n'
        '                bars_to_max_adverse = j - entry_idx\n'
        '            # Stop\n'
        '            if c >= stop_level:\n'
        '                bars_to_stop = j - entry_idx\n'
        '                break\n'
        '\n'
        '    return {\n'
        "        'max_profit_pct':      round(max_profit_pct, 6),\n"
        "        'bars_to_max_profit':  bars_to_max_profit,\n"
        "        'max_adverse_pct':     round(max_adverse_pct, 6),\n"
        "        'bars_to_max_adverse': bars_to_max_adverse,\n"
        "        'bars_to_stop':        bars_to_stop,\n"
        '    }\n'
    ),
    skip_if_contains="'max_adverse_pct':",
))

# 02a — optimizer_runner.py: extend the pk_outcomes INSERT statement
EDITS.append(Edit(
    'optimus9/orchestration/optimizer_runner.py',
    '02a optimizer_runner: extend pk_outcomes INSERT with MAE columns',
    old=(
        "        out_sql = '''INSERT INTO pk_outcomes\n"
        "            (pko_pks_pk, pko_max_profit_pct, pko_bars_to_stop, pko_bars_to_max_profit)\n"
        "            VALUES (%s,%s,%s,%s)'''\n"
    ),
    new=(
        "        out_sql = '''INSERT INTO pk_outcomes\n"
        "            (pko_pks_pk, pko_max_profit_pct, pko_bars_to_stop, pko_bars_to_max_profit,\n"
        "             pko_max_adverse_pct, pko_bars_to_max_adverse)\n"
        "            VALUES (%s,%s,%s,%s,%s,%s)'''\n"
    ),
    skip_if_contains='pko_max_adverse_pct, pko_bars_to_max_adverse',
))

# 02b — optimizer_runner.py: extend the row tuple to include MAE values
EDITS.append(Edit(
    'optimus9/orchestration/optimizer_runner.py',
    '02b optimizer_runner: extend outcome row tuple with MAE values',
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
    skip_if_contains="dv(o['max_adverse_pct'])",
))


# ─── MAIN ───────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    print(f'r06 260522 MAE capture — {"DRY-RUN" if args.dry_run else "APPLYING"}')
    print('=' * 70)

    nomatches = 0
    skipped   = 0
    applied   = 0
    missing   = 0

    for edit in EDITS:
        status = edit.apply(args.dry_run)
        print(status)
        if status.startswith('⚠'):
            nomatches += 1
        elif status.startswith('⊝'):
            skipped += 1
        elif status.startswith('✓') or status.startswith('·'):
            applied += 1
        elif status.startswith('✗'):
            missing += 1

    print('=' * 70)
    print(f'Total: {len(EDITS)} edits  |  '
          f'applied: {applied}  skipped: {skipped}  '
          f'nomatch: {nomatches}  missing: {missing}')

    # ── Manual next steps printed every run for visibility ─────────────────
    print()
    print('━━━ MANUAL STEPS — required before re-grinding ━━━━━━━━━━━━━━━━━━━━━')
    print()
    print('1. Database DDL — add MAE columns to pk_outcomes:')
    print()
    print("   ALTER TABLE pk_outcomes")
    print("     ADD COLUMN pko_max_adverse_pct    DOUBLE NULL")
    print("       AFTER pko_bars_to_stop,")
    print("     ADD COLUMN pko_bars_to_max_adverse INT    NULL")
    print("       AFTER pko_max_adverse_pct;")
    print()
    print('2. If edit 02 (optimizer_runner) reported NOMATCH, paste the')
    print('   _persist_self_gated method so I can match the actual local')
    print('   INSERT statement and regenerate this script.')
    print()
    print('3. After (1) + (2) succeed, the new grind for gca5m will capture')
    print('   MAE automatically. No further code changes needed for the grind.')
    print()

    if nomatches > 0:
        print('⚠  Some edits did not find their target. Inspect and report back.')
        return 1
    if missing > 0:
        print('✗  Some files were missing. Check paths.')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
