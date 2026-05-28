#!/usr/bin/env python3
"""
apply_r06_srp_pk_refactor.py — replace PKDetector with PKSignalDetector +
PKStateComputer + PKGateFilter (SRP-clean, transition semantics, Pine-aligned).

Folds in run.py's config.py migration at the same time.

Pre-reqs (drop these into optimus9/compute/ BEFORE running this script):
  - optimus9/compute/pk_state_computer.py
  - optimus9/compute/pk_gate_filter.py
  - optimus9/compute/pk_signal_detector.py

Edits applied:
  01-02. optimus9/__init__.py             — re-exports
  03-04. report_manager.py                — import + instantiation
  05-07. optimizer_runner.py              — import + type hint + docstring
  08-11. run.py                           — bulk import, TODO removal, _db() config migration
  12.    Delete optimus9/compute/pk_detector.py

Usage:
  python3 apply_r06_srp_pk_refactor.py --dry-run
  python3 apply_r06_srp_pk_refactor.py
  python3 validate_srp_refactor.py
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
            return f'-  skip     {self.name}'
        if self.old not in src:
            return f'!  NOMATCH  {self.name}'
        if dry_run:
            return f'.  dry-run  {self.name}'
        self.path.write_text(src.replace(self.old, self.new, 1))
        return f'+  applied  {self.name}'


EDITS = []

# 01: optimus9/__init__.py — replace import line 37
EDITS.append(Edit(
    'optimus9/__init__.py',
    '01 __init__.py import',
    old='from .compute.pk_detector import PKDetector\n',
    new=('from .compute.pk_state_computer  import PKStateComputer\n'
         'from .compute.pk_gate_filter     import PKGateFilter\n'
         'from .compute.pk_signal_detector import PKSignalDetector\n'),
    skip_if_contains='from .compute.pk_signal_detector import PKSignalDetector',
))

# 02: __all__ entry
EDITS.append(Edit(
    'optimus9/__init__.py',
    '02 __init__.py __all__',
    old="    'PKDetector',\n",
    new=("    'PKStateComputer',\n"
         "    'PKGateFilter',\n"
         "    'PKSignalDetector',\n"),
    skip_if_contains="'PKSignalDetector',",
))

# 03: report_manager.py import
EDITS.append(Edit(
    'optimus9/orchestration/report_manager.py',
    '03 report_manager.py import',
    old='from ..compute.pk_detector import PKDetector\n',
    new=('from ..compute.pk_state_computer  import PKStateComputer\n'
         'from ..compute.pk_gate_filter     import PKGateFilter\n'
         'from ..compute.pk_signal_detector import PKSignalDetector\n'),
    skip_if_contains='from ..compute.pk_signal_detector import PKSignalDetector',
))

# 04: report_manager.py line 155 instantiation
EDITS.append(Edit(
    'optimus9/orchestration/report_manager.py',
    '04 report_manager.py instantiation',
    old="            PKDetector(float(config['ic_high_boundary']), float(config['ic_low_boundary'])),",
    new=("            PKSignalDetector(\n"
         "                state_computer = PKStateComputer(\n"
         "                    high_b = float(config['ic_high_boundary']),\n"
         "                    low_b  = float(config['ic_low_boundary']),\n"
         "                ),\n"
         "                gate_filter = PKGateFilter(),\n"
         "            ),"),
    skip_if_contains='PKSignalDetector(',
))

# 05: optimizer_runner.py import
EDITS.append(Edit(
    'optimus9/orchestration/optimizer_runner.py',
    '05 optimizer_runner.py import',
    old='from ..compute.pk_detector import PKDetector',
    new='from ..compute.pk_signal_detector import PKSignalDetector',
    skip_if_contains='from ..compute.pk_signal_detector import PKSignalDetector',
))

# 06: optimizer_runner.py constructor type hint
EDITS.append(Edit(
    'optimus9/orchestration/optimizer_runner.py',
    '06 optimizer_runner.py ctor type hint',
    old='    def __init__(self, db: DatabaseManager, detector: PKDetector,',
    new='    def __init__(self, db: DatabaseManager, detector: PKSignalDetector,',
    skip_if_contains='detector: PKSignalDetector,',
))

# 07: optimizer_runner.py docstring
EDITS.append(Edit(
    'optimus9/orchestration/optimizer_runner.py',
    '07 optimizer_runner.py docstring',
    old='        line per combo, calls PKDetector to find PK patterns within the',
    new='        line per combo, calls PKSignalDetector to find PK transitions within the',
    skip_if_contains='calls PKSignalDetector to find PK transitions',
))

# 08: run.py bulk import
EDITS.append(Edit(
    'run.py',
    '08 run.py bulk import',
    old='    PKDetector,\n',
    new=('    PKStateComputer,        # noqa: F401\n'
         '    PKGateFilter,           # noqa: F401\n'
         '    PKSignalDetector,       # noqa: F401\n'),
    skip_if_contains='    PKSignalDetector,       # noqa: F401',
))

# 09: run.py remove stale TODO
EDITS.append(Edit(
    'run.py',
    '09 run.py remove stale TODO',
    old=("  • Patch PKDetector's 1-bar window discrepancy once next clean centroid\n"
         "    is locked in (see PKDetector docstring for current rationale)\n"),
    new='',
    skip_if_contains='Patch PKDetector',  # if absent, edit done OR was never there
))

# 10: run.py _db() use config
EDITS.append(Edit(
    'run.py',
    '10 run.py _db() use get_db_config',
    old=('def _db() -> DatabaseManager:\n'
         '    db = DatabaseManager(\n'
         "        host     = os.environ.get('PK_DB_HOST',     'localhost'),\n"
         "        user     = os.environ.get('PK_DB_USER',     'root'),\n"
         "        password = os.environ.get('PK_DB_PASS',     'yourpassword'),\n"
         "        database = os.environ.get('PK_DB_NAME',     'pk_optimizer'),\n"
         "        port     = int(os.environ.get('PK_DB_PORT', 3306)),\n"
         '    )\n'
         '    db.connect()\n'
         '    return db'),
    new=('def _db() -> DatabaseManager:\n'
         '    db = DatabaseManager(**get_db_config())\n'
         '    db.connect()\n'
         '    return db'),
    skip_if_contains='DatabaseManager(**get_db_config())',
))

# 11: run.py add get_db_config import
EDITS.append(Edit(
    'run.py',
    '11 run.py add get_db_config import',
    old='from optimus9 import (',
    new=('from optimus9.config import get_db_config\n'
         'from optimus9 import ('),
    skip_if_contains='from optimus9.config import get_db_config',
))


def delete_pk_detector(dry_run):
    p = pathlib.Path('optimus9/compute/pk_detector.py')
    if not p.exists():
        return '-  skip     12 pk_detector.py already gone'
    if dry_run:
        return '.  dry-run  12 would delete pk_detector.py'
    p.unlink()
    return '+  applied  12 deleted pk_detector.py'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    mode = 'DRY-RUN' if args.dry_run else 'APPLYING'
    print(f'r06 SRP PK refactor + config.py migration — {mode}')
    print('=' * 70)

    counts = {'!': 0, '-': 0, '+': 0, '.': 0, 'X': 0}
    for edit in EDITS:
        status = edit.apply(args.dry_run)
        print(status)
        prefix = status[0]
        if prefix in counts:
            counts[prefix] += 1

    delete_status = delete_pk_detector(args.dry_run)
    print(delete_status)
    counts[delete_status[0]] = counts.get(delete_status[0], 0) + 1

    print('=' * 70)
    print(
        f"Total: {len(EDITS) + 1} edits  |  "
        f"applied: {counts['+'] + counts['.']}  "
        f"skipped: {counts['-']}  "
        f"nomatch: {counts['!']}  "
        f"missing: {counts['X']}"
    )

    if counts['!'] > 0 or counts['X'] > 0:
        print()
        print('!  Some edits reported NOMATCH/MISSING. Inspect manually.')
        return 1

    print()
    print('-- NEXT --')
    print('  python3 validate_srp_refactor.py')
    return 0


if __name__ == '__main__':
    sys.exit(main())
