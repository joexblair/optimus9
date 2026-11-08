#!/usr/bin/env python3
"""ROWS NOT SHOWN - refuse a reply that talks about rows it does not put in front of him.

HIS 1108 ASK: *"can 'summarised instead of producing it' be caught by a hook? if so, lock it in"*,
after I named that pattern as the main driver of four of his corrections in three days.

WHAT IT CATCHES, and it is the sharp end rather than the whole thing: a sentence whose WORDING says
the items are somewhere else - `the other 4`, `the remaining 7`, `all but 2`, `the rest of them`,
`none of them`. Those phrases are the fingerprint of the failure, because they describe rows the
reply has chosen not to show. The three real cases on 1108:

    "24 events appear. The other 4 lost both x lines to the race bound and print nothing"
        -> his reply: *"do better with your detail - nothing in that table backs your statement"*
    7 x-crosses described as lost, with no row for any of the 7
        -> his reply: *"why wouldn't the following cadence carry the x-cross?"*. All 7 were carried.
    3 cad-walked bars said to have moved, with no per-row evidence
        -> his reply: *"I'm assuming you've kept the old timestamps"*

WHAT IT CANNOT CATCH: whether the N items a claim is about are actually NAMED in the table that is
shown. That needs reading the data, not the text. A count stated beside a full table is fine and is
not flagged.

EXEMPT: quoted spans - his words are not my summary - code fences, table rows, and a sentence that
says where the rows are (`in the table above`, `in the file`, a path).

Runs as a Stop hook, reading the last reply the same way jargon-check.py does.
"""
import json
import os
import re
import sys

#   The wording that says "these rows are elsewhere". Each one needs a number or a bare plural
#   after it, so `the rest of the morning` does not match and `the rest of them` does.
SHAPES = [
    (r'\bthe other \d+\b', 'the other N - name those N rows or show them'),
    (r'\bthe remaining \d+\b', 'the remaining N - name those N rows or show them'),
    (r'\ball but \d+\b', 'all but N - name the N that differ'),
    (r'\bthe rest (?:of them|of the \w+)\b', 'the rest - show them'),
    (r'\bnone of (?:them|the (?:others|rest))\b', 'none of them - show the rows that say so'),
    (r'\b\d+ of them\b', 'N of them - show those N rows'),
    (r'\bthe other \w+s\b', 'the other <plural> - name them or show them'),
]
#   A sentence that says WHERE the rows are has produced them, even if it does not repeat them.
POINTS_AT = re.compile(
    r'\b(?:in|see|from) the (?:table|rows|block|file|capture|output)\b|'
    r'\b(?:table|rows) (?:above|below)\b|'
    r'/[\w./-]+\.(?:txt|md|py|json|npz)\b', re.I)


def last_reply(path):
    """The assistant's final text block of the transcript. -> str."""
    if not path or not os.path.exists(path):
        return ''
    out = []
    for line in open(path, errors='replace'):
        try:
            d = json.loads(line)
        except Exception:
            continue
        if d.get('type') != 'assistant':
            continue
        txt = [b.get('text', '') for b in (d.get('message', {}).get('content') or [])
               if isinstance(b, dict) and b.get('type') == 'text']
        if any(t.strip() for t in txt):
            out = txt
    return '\n'.join(out)


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}
    text = last_reply(data.get('transcript_path'))
    if not text.strip():
        print(json.dumps({}))
        return 0
    #   TABLE ROWS COME OUT FIRST: a cell may legitimately read `the other 4` as a label.
    prose = '\n'.join(l for l in text.split('\n') if not l.lstrip().startswith('|'))
    prose = re.sub(r'```.*?```', ' ', prose, flags=re.S)
    prose = re.sub(r'`[^`]*`', ' ', prose)
    #   HIS WORDS ARE NOT MY SUMMARY - quoted spans come out, the same bound jargon-check uses.
    prose = re.sub(r'"[^"]{0,1200}"', ' ', prose)
    prose = re.sub(r'“[^”]{0,1200}”', ' ', prose)
    prose = re.sub(r'\*"[^"]{0,1200}"\*', ' ', prose)

    hits = []
    for sent in re.split(r'(?<=[.!?\n])\s+', prose):
        if POINTS_AT.search(sent):
            continue
        for rx, why in SHAPES:
            m = re.search(rx, sent, re.I)
            if m and (m.group(0).lower(), why) not in [(a.lower(), b) for a, b, _ in hits]:
                hits.append((m.group(0), why, ' '.join(sent.split())[:160]))
    if not hits:
        print(json.dumps({}))
        return 0
    lines = ['%d phrase(s) that talk about rows this reply does not show:' % len(hits)]
    for tok, why, sent in hits[:6]:
        lines.append('  %s  (%s)' % (tok, why))
        lines.append('      in: %s' % sent)
    lines.append('He cannot check a claim about rows he has not been given. Either put one row per'
                 ' item in a table in this reply, or say which file and command produce them. If'
                 ' you have not produced them yet, produce them before the claim.')
    print(json.dumps({'decision': 'block', 'reason': '\n'.join(lines)}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
