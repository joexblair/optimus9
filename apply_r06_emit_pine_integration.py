#!/usr/bin/env python3
"""
apply_r06_emit_pine_integration.py — wires the Pine emitter into
analyze_manager's CLI as the optional --emit_pine flag.

After this applies:
  python3 -m optimus9.analysis.analyze_manager --or_pk=32 --emit_pine
  → runs analysis, writes analysis_or32.csv, then emits bbstr_or32_strategy.pine

Also supports standalone usage via emit_pine_strategy.py (already in place).

Idempotent: re-running after apply is safe.

Pre-reqs:
  - optimus9/emit/pine_strategy_emitter.py is in place (the class file)
  - optimus9/emit/__init__.py exists (this script creates an empty one)
  - optimus9/analysis/analyze_manager.py is the local production version
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


# ─── 01: Create optimus9/emit/__init__.py if missing ─────────────────────
def ensure_emit_init(dry_run):
    init_path = pathlib.Path('optimus9/emit/__init__.py')
    if init_path.exists():
        return '-  skip     01 optimus9/emit/__init__.py (already exists)'
    if dry_run:
        return '.  dry-run  01 would create optimus9/emit/__init__.py'
    init_path.parent.mkdir(parents=True, exist_ok=True)
    init_path.write_text('')
    return '+  applied  01 created optimus9/emit/__init__.py'


EDITS = []

# ─── 02: Add --emit_pine flag to argparse ─────────────────────────────────
EDITS.append(Edit(
    'optimus9/analysis/analyze_manager.py',
    '02 add --emit_pine flag',
    old=(
        "    parser.add_argument('--parallel',     type=int,   default=1,\n"
        "                        help='Number of parallel worker processes '\n"
        "                             '(default 1). Use 6 for the standard 6-or_pk '\n"
        "                             'batch on a 16-core machine.')\n"
        "    args = parser.parse_args()\n"
    ),
    new=(
        "    parser.add_argument('--parallel',     type=int,   default=1,\n"
        "                        help='Number of parallel worker processes '\n"
        "                             '(default 1). Use 6 for the standard 6-or_pk '\n"
        "                             'batch on a 16-core machine.')\n"
        "    parser.add_argument('--emit_pine',    action='store_true',\n"
        "                        help='After analysis completes, emit Pine v6 '\n"
        "                             'strategy for the PROVEN combo of each or_pk.')\n"
        "    args = parser.parse_args()\n"
    ),
    skip_if_contains="parser.add_argument('--emit_pine'",
))

# ─── 03: Add emit call after analyze_many ─────────────────────────────────
EDITS.append(Edit(
    'optimus9/analysis/analyze_manager.py',
    '03 add PineStrategyEmitter call after analysis',
    old=(
        "        AnalyzeManager(db).analyze_many(\n"
        "            or_pks,\n"
        "            parallel=args.parallel,\n"
        "            min_signals=args.min_signals,\n"
        "            top_n=args.top_n,\n"
        "            top_stage1=args.top_stage1,\n"
        "            dd_threshold=args.dd_threshold,\n"
        "            output_dir=args.output_dir,\n"
        "        )\n"
        "    finally:\n"
        "        db.disconnect()\n"
    ),
    new=(
        "        AnalyzeManager(db).analyze_many(\n"
        "            or_pks,\n"
        "            parallel=args.parallel,\n"
        "            min_signals=args.min_signals,\n"
        "            top_n=args.top_n,\n"
        "            top_stage1=args.top_stage1,\n"
        "            dd_threshold=args.dd_threshold,\n"
        "            output_dir=args.output_dir,\n"
        "        )\n"
        "\n"
        "        if args.emit_pine:\n"
        "            from ..emit.pine_strategy_emitter import PineStrategyEmitter\n"
        "            emitter = PineStrategyEmitter(db)\n"
        "            for or_pk in or_pks:\n"
        "                emitter.emit(or_pk, output_dir=args.output_dir)\n"
        "    finally:\n"
        "        db.disconnect()\n"
    ),
    skip_if_contains="from ..emit.pine_strategy_emitter import PineStrategyEmitter",
))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    mode = 'DRY-RUN' if args.dry_run else 'APPLYING'
    print(f'r06 260524 emit_pine integration - {mode}')
    print('=' * 70)

    # Special step: ensure __init__.py exists
    status = ensure_emit_init(args.dry_run)
    print(status)

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

    if counts['!'] > 0 or counts['X'] > 0:
        print()
        print('!  Some edits did not apply. Inspect manually or paste affected sections.')
        return 1

    print()
    print('-- NEXT STEPS --')
    print('1. Place pine_strategy_emitter.py in optimus9/emit/:')
    print('   cp /mnt/c/Users/Administrator/thecodes/pine_strategy_emitter.py optimus9/emit/')
    print('2. Place emit_pine_strategy.py at repo root (already in place if you')
    print('   already cp\'d it earlier).')
    print('3. Combined run:')
    print('   python3 -m optimus9.analysis.analyze_manager --or_pk=32 --emit_pine')
    print('4. Or standalone (if AM already ran):')
    print('   python3 emit_pine_strategy.py --or_pk=32')
    return 0


if __name__ == '__main__':
    sys.exit(main())
