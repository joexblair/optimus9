#!/usr/bin/env python3
"""HIS WORDS - refuse a verbatim quote of Joe's that is not in the registry.

His 1031 lock-in. The failure this prevents: on 1029 I wrote the opposite-side ex-fence clear into
v4_knobs.py as something he "ruled in the same message". No such words exist anywhere in the tree.
It sat there as his ruling for two days.

THE RULE: a *"..."* quote that is not in docs/octo-freedom/his_words.md is MINE until he confirms
it. To register one, append it to that file in the same turn he says it.

Runs as a PostToolUse hook on Write|Edit, so the flag lands at the edit, not at the end of a turn.
"""
import hashlib
import json
import os
import re
import sys

ROOT = '/home/joe/thecodes'
REG = os.path.join(ROOT, 'docs/octo-freedom/his_words.md')
PAT = re.compile(r'\*"(.+?)"\*', re.S)


def norm(q):
    q = ' '.join(x.strip().lstrip('#').strip() for x in q.split('\n'))
    return ' '.join(q.split())


def key(q):
    return hashlib.sha1(norm(q).encode()).hexdigest()[:12]


def main():
    try:
        ev = json.load(sys.stdin)
    except Exception:
        return 0
    p = (ev.get('tool_response') or {}).get('filePath') \
        or (ev.get('tool_input') or {}).get('file_path') or ''
    if not p or not p.endswith(('.py', '.md')):
        return 0
    rel = os.path.relpath(p, ROOT) if p.startswith(ROOT) else p
    if not rel.startswith('docs/octo-freedom') or rel.endswith('his_words.md'):
        return 0
    try:
        known = {l.split('  ', 1)[0] for l in open(REG) if re.match(r'^[0-9a-f]{12}  ', l)}
        text = open(p, errors='replace').read()
    except Exception:
        return 0
    new = []
    for m in PAT.finditer(text):
        q = norm(m.group(1))
        if len(q) < 4 or key(q) in known:
            continue
        if q not in [x[0] for x in new]:
            new.append((q, key(q)))
    if not new:
        return 0
    lines = ['%d quote(s) attributed to Joe that are NOT in his_words.md, in %s:' % (len(new), rel)]
    for q, k in new[:8]:
        lines.append('  %s  *"%s"*' % (k, q if len(q) <= 160 else q[:157] + '...'))
    lines.append('Each one is YOURS until he confirms it. Either say in the response that it is your'
                 ' own wording, or - if he said it this turn - append it to the registry as'
                 ' "<key>  <quote>" and say you added it.')
    print(json.dumps({'hookSpecificOutput': {
        'hookEventName': 'PostToolUse', 'additionalContext': '\n'.join(lines)}}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
