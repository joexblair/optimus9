#!/usr/bin/env python3
"""MECH GOAL - a mech spec states its goal at the top, before anything else.

HIS 1108 IDEA: *"every mech should state it's goal at the beginning of the spec"*, and
*"add that as a hook so that I don't forget this important idea and I'll slowly update the
existing mech's that we're using, in my own time"*.

WHAT IT PROVED, the same day: he gave the goal of `fdm2-rline-enhance` as one sentence -
*"the goal of this work is to improve the verdict timestamps in fdm2-xcv"* - and five of the six
open rules fell straight out of it. The rules had been sitting open as questions for him.

THE RULE: a spec doc carries its goal BEFORE its first section. Either a `GOAL` heading is the
first `##`, or a line beginning `GOAL` appears above the first `##`.

IT NEVER BLOCKS. He is updating the existing docs in his own time, so this reports and stops
there. It also cannot tell a mech spec from a research note, so it says which judgement is his.

Runs as a PostToolUse hook on Write|Edit, so the notice lands at the edit, not at the end of a
turn - the same shape as his-words.py.
"""
import json
import os
import re
import sys

ROOT = '/home/joe/thecodes'
DOCS = os.path.join(ROOT, 'docs/octo-freedom')
HEAD = re.compile(r'^##\s*(.+?)\s*$', re.M)
GOAL = re.compile(r'^\s*(##\s*)?GOAL\b', re.I)


def main():
    try:
        ev = json.load(sys.stdin)
    except Exception:
        return 0
    p = (ev.get('tool_response') or {}).get('filePath') \
        or (ev.get('tool_input') or {}).get('file_path') or ''
    if not p.endswith('.md'):
        return 0
    p = os.path.realpath(p)
    if not p.startswith(DOCS + os.sep):
        return 0
    try:
        text = open(p, errors='replace').read()
    except Exception:
        return 0
    #   EVERYTHING ABOVE THE FIRST SECTION. No line count is used - "the beginning" is the span
    #   before the document's first `##`, which needs no number to define.
    m = HEAD.search(text)
    top = text[:m.start()] if m else text
    if any(GOAL.match(x) for x in top.splitlines()):
        return 0
    if m and GOAL.match('## ' + m.group(1)):
        return 0
    rel = os.path.relpath(p, ROOT)
    print(json.dumps({'hookSpecificOutput': {
        'hookEventName': 'PostToolUse',
        'additionalContext':
            '%s has no GOAL above its first section.\n'
            'HIS 1108 IDEA: every mech spec states its goal at the beginning. On 1108 his one'
            ' sentence of goal settled five of six open rules by itself.\n'
            'If this doc IS a mech spec, put a GOAL line or a ## GOAL section above the first'
            ' section and tell him you did. If it is a research note, a handover or a census,'
            ' say so in one line and leave it - the judgement is his, and he is updating the'
            ' existing docs in his own time. NOTHING IS BLOCKED.' % rel}}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
