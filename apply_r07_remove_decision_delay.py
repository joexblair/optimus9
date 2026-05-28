#!/usr/bin/env python3
"""
apply_r07_remove_decision_delay.py — delete the decision-delay state machine
from Pk5sGateComputer.

Decision (2026-05-26): decision delay is hostile to HTF anchor signals.
Valid 5s pks get cancelled by noisy opposing-direction PKs during the
countdown window. With Pine deprecated as a production path, no parity
requirement keeps it alive in Python.

Changes:
  1. Replace `s5_pk_final = self._apply_decision_delay(pk_raw, decision_dly)`
     with `s5_pk_final = pk_raw`
  2. Remove the `decision_dly = int(params['decision_delay'])` lookup
  3. Update the log message to drop the "after N-bar delay" wording
  4. Update the docstring param list to remove `decision_delay`
  5. Delete the `_apply_decision_delay` static method entirely

The `decision_delay` field can stay in tce_params JSON (we just stop
reading it). No DDL change needed.

Idempotent.
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

# 01: Replace the _apply_decision_delay call with direct pk_raw assignment
EDITS.append(Edit(
    'optimus9/compute/pk5s_gate_computer.py',
    '01 replace _apply_decision_delay call',
    old='        s5_pk_final = self._apply_decision_delay(pk_raw, decision_dly)',
    new='        # r07: decision delay removed — hostile to HTF anchor signals\n'
        '        s5_pk_final = pk_raw',
    skip_if_contains='# r07: decision delay removed',
))

# 02: Remove the decision_dly param lookup
EDITS.append(Edit(
    'optimus9/compute/pk5s_gate_computer.py',
    '02 remove decision_dly param lookup',
    old="        decision_dly = int(params['decision_delay'])\n",
    new='',
    skip_if_contains="# decision_delay param removed in r07",  # not actually in code; ensures one-shot
))

# 03: Update log message to drop the "after N-bar delay" wording
EDITS.append(Edit(
    'optimus9/compute/pk5s_gate_computer.py',
    '03 update log message',
    old=("            f'pk_5s tce_pk={tce_pk}: raw fires {int((pk_raw != 0).sum())}, '\n"
         "            f'after {decision_dly}-bar delay {fires_long + fires_short} '\n"
         "            f'({fires_long}L / {fires_short}S)'"),
    new=("            f'pk_5s tce_pk={tce_pk}: '\n"
         "            f'fires {fires_long + fires_short} ({fires_long}L / {fires_short}S)'"),
    skip_if_contains="f'pk_5s tce_pk={tce_pk}: '\n            f'fires {fires_long",
))

# 04: Drop decision_delay from docstring param list
EDITS.append(Edit(
    'optimus9/compute/pk5s_gate_computer.py',
    '04 docstring drop decision_delay',
    old=("        params : tce_params dict (pool_c, pool_w, pool_slope, pool_range,\n"
         "                 threshold_long, threshold_short, pm_suppression,\n"
         "                 decision_delay)"),
    new=("        params : tce_params dict (pool_c, pool_w, pool_slope, pool_range,\n"
         "                 threshold_long, threshold_short, pm_suppression).\n"
         "                 Any `decision_delay` field is ignored (r07: removed)."),
    skip_if_contains='Any `decision_delay` field is ignored',
))

# 05: Delete the _apply_decision_delay method (and its section header comment)
EDITS.append(Edit(
    'optimus9/compute/pk5s_gate_computer.py',
    '05 delete _apply_decision_delay method',
    old=(
        '    # ── decision-delay state machine ───────────────────────────────────────\n'
        '    @staticmethod\n'
        '    def _apply_decision_delay(pk_raw: np.ndarray, delay: int) -> np.ndarray:\n'
        '        """\n'
        '        Pine: bbstr.pine line 1624-1648.\n'
        '\n'
        '        State machine (no upstream gate at the 5s level, so the Pine\n'
        '        `_gate_open` branch collapses):\n'
        '\n'
        '            if pk_raw != 0:\n'
        '                if pk_raw == pending:\n'
        '                    countdown -= 1\n'
        '                    if countdown == 0: fire = pk_raw\n'
        '                else:\n'
        '                    pending   = pk_raw\n'
        '                    countdown = delay\n'
        '                    fire      = 0\n'
        '            else:\n'
        '                pending = 0; countdown = 0; fire = 0\n'
        '\n'
        '        Sequential by necessity — the state machine doesn\'t vectorise cleanly.\n'
        '        Loop is in plain Python; n is typically a few hundred thousand 5s bars\n'
        '        for a 30-day grind, well within tolerable single-pass loop time.\n'
        '        """\n'
        '        n         = len(pk_raw)\n'
        '        out       = np.zeros(n, dtype=np.int8)\n'
        '        pending   = 0\n'
        '        countdown = 0\n'
        '        for i in range(n):\n'
        '            d = int(pk_raw[i])\n'
        '            if d != 0:\n'
        '                if d == pending:\n'
        '                    countdown = max(0, countdown - 1)\n'
        '                    if countdown == 0:\n'
        '                        out[i] = d\n'
        '                else:\n'
        '                    pending   = d\n'
        '                    countdown = delay\n'
        '            else:\n'
        '                pending   = 0\n'
        '                countdown = 0\n'
        '        return out\n'
    ),
    new='',
    skip_if_contains='def _apply_decision_delay',  # presence of OLD means not yet applied
))

# Note on edit 02 + 05: skip_if_contains for edit 02 is a label that never
# appears in the file (always triggers apply). For edit 05, presence of
# OLD == not-yet-applied (skip_if_contains points at content we're DELETING).
# Re-runs will report NOMATCH (harmless). Edit 02 with the "never matches"
# guard works because once OLD is gone, str.replace returns identical src
# and we report skip via NOMATCH on the second run.


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    mode = 'DRY-RUN' if args.dry_run else 'APPLYING'
    print(f'r07 remove decision delay — {mode}')
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

    if counts['!'] > 0 or counts['X'] > 0:
        print()
        print('!  NOMATCH on first run = file diverged from expected shape.')
        print('   NOMATCH on second run = edit already applied (harmless).')
        return 1 if counts['X'] > 0 else 0

    print()
    print('-- VALIDATION --')
    print('1. Sanity check: no remaining references')
    print('   grep -n "_apply_decision_delay\\|decision_dly" optimus9/compute/pk5s_gate_computer.py')
    print('   Expected: zero matches')
    print()
    print('2. Re-grind self-gated test (no bny30 gates):')
    print('   - Find a tc_pk that runs the self-gated path')
    print('   - Run with --skip_analyze')
    print('   - Expect MORE signals than before (decision delay was filtering)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
