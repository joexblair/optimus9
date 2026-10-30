#!/usr/bin/env python3
"""Checks MY last reply for things Joe will not understand, and blocks until they are fixed.

Joe 1029: *"if there's a hook that fires before you send a response, then that hook should be
checking that I'll understand what you're presenting. the obvious catches are code labels and your
shorthand"* and *"I can't build an allowlist - it's too restrictive on me"*.

SO THERE IS NO ALLOWLIST OF HIS WORDS. This inspects only MY output, two ways:

  1  CODE LABELS BY SHAPE - a knob name, an identifier, a dotted call, a file:line. No list needed;
     these have a shape no plain sentence has.
  2  MY SHORTHAND BY NAME - a small list of terms he has pulled me up on. It grows only when he
     flags one, never by my guessing.

THE GLOSS EXEMPTION, which is his own standing rule: a term is fine if its FIRST appearance is
explained within GLOSS_WINDOW characters. So `LIFT_WOB 8 bars = 40 s` passes and a bare
`LIFT_WOB` does not.

It reads the last assistant message out of the transcript the Stop hook hands it. On a hit it
returns decision 'block' with the list, which comes back to me to fix before the turn ends.
"""
import json
import os
import re
import sys

GLOSS_WINDOW = 90
#   A GLOSS IS AN EXPLANATION, not any nearby word. 'the' and 'is' were in this list first
#   and they let `LIN2_CHAIN_OPEN_XWOB` and `v4_chain.opening` through on the first test,
#   because almost any sentence contains them. It now takes an equals sign, a dash, an
#   explicit 'means', a unit, or a parenthetical.
GLOSS = re.compile(r'(=|\u2014|\bmeans\b|\bbars?\b|\bseconds?\b|\bminutes?\b|%|\()')

#   Terms HE has flagged as mine. Nothing is added here by guessing.
MINE = [
    'turn bar', 'cadence i', 'confirming bar', 'bucket', 'buckets',
    'the band', 'arm on a knob', 'the shape', 'membership arm',
    'floor arm', 'zero-length leg', 'state read', 'wob180',
]

#   READING FORWARD. Joe 1029: *"add a lookahead check that sits inside the jargon detector
#   hook"*. A text check cannot PROVE a claim is causal - it can only catch the phrasings that a
#   forward read almost always arrives in. Every hit is a question, not a verdict, and the answer
#   is always the same test: could that sentence be written at the bar it describes, with no later
#   bar in hand?
#   SEEDED FROM WHAT I ACTUALLY DID on 2026-08-29 23:53:50 - I wrote that the crossing "still
#   stands, because ws1b stays under 85 from 23:53:50 to 23:55:40", and that the trip back out
#   "lasts exactly 3 bars". Both read bars after the event they judged.
FORWARD = [
    'would have', 'went on to', 'goes on to', 'later reached', 'later reaches', 'ends up',
    'turns out', 'eventually', 'by the time', 'lasts exactly', 'lasted exactly', 'in the next',
    'over the next', 'subsequently', 'afterwards', 'after the fire', 'after the firing',
    'stays under', 'stays above', 'stays below', 'stayed under', 'stayed above', 'stayed below',
    'held until', 'until it', 'would erase', 'would have erased', 'and the last',
    'between the first', 'went back out', 'never reaches', 'never reached', 'does not return',
    'did not return', 'would still', 'still stands', 'from then on', 'thereafter',
]

#   HIS OWN WORDS. Not an allowlist of what I may say - he refused that, 1029: *"I can't build an
#   allowlist - it's too restrictive on me"*. This is the short list of terms HE uses, which the
#   shape checks would otherwise flag because they look like code. It grows only when he tells me
#   one of his words was flagged.
HIS = {'lin_hop', 'consumer', 'consumers', 'producer', 'producers', 'oob',
       'lin2_matry_wsf_takeover', 'matryoshka'}

SHAPES = [
    ('a knob or constant name', re.compile(r'\b[A-Z][A-Z0-9]*(?:_[A-Z0-9]+){1,}\b')),
    ('a code identifier', re.compile(r'\b[a-z][a-z0-9]*(?:_[a-z0-9]+){1,}\b')),
    ('a dotted call', re.compile(r'\b[A-Za-z_][A-Za-z0-9_]*\.[a-z_][A-Za-z0-9_]*\b')),
    ('a file and line', re.compile(r'\b[\w./-]+\.py:\d+\b')),
]


def last_reply(path):
    if not path or not os.path.exists(path):
        return ''
    out = ''
    with open(path, encoding='utf-8', errors='replace') as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            msg = rec.get('message') or {}
            if rec.get('type') != 'assistant' and msg.get('role') != 'assistant':
                continue
            content = msg.get('content')
            if isinstance(content, str):
                out = content
            elif isinstance(content, list):
                parts = [c.get('text', '') for c in content
                         if isinstance(c, dict) and c.get('type') == 'text']
                if any(p.strip() for p in parts):
                    out = '\n'.join(parts)
    return out


def glossed(text, token):
    i = text.find(token)
    if i < 0:
        return True
    tail = text[i + len(token): i + len(token) + GLOSS_WINDOW]
    return bool(GLOSS.search(tail))


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        data = {}
    text = last_reply(data.get('transcript_path'))
    if not text.strip():
        print(json.dumps({}))
        return
    #   code fences and inline code are where a label BELONGS - strip them before checking prose.
    prose = re.sub(r'```.*?```', ' ', text, flags=re.S)
    prose = re.sub(r'`[^`]*`', ' ', prose)

    #   QUOTED SPANS COME OUT BEFORE BOTH CHECKS. The span limit was 200 characters and a
    #   230-character quote of his own question slipped past it, so the forward-read check flagged
    #   his words. 1200 holds any quote he or I would paste and still bounds the match.
    #   QUOTED SPANS COME OUT BEFORE BOTH CHECKS. The label scan blocked on `prev_close` while it
    #   sat inside a quote of Joe's OWN words - he wrote it, so he can read it. Quoting someone is
    #   not introducing a term.
    unq = re.sub(r'"[^"]{0,1200}"', ' ', prose)
    unq = re.sub(r'\u201c[^\u201d]{0,1200}\u201d', ' ', unq)
    unq = re.sub(r"(?<![A-Za-z])'[^']{0,1200}'(?![A-Za-z])", ' ', unq)

    hits = []
    seen = set()
    for why, rx in SHAPES:
        for m in rx.finditer(unq):
            tok = m.group(0)
            if tok.lower() in seen or tok.lower() in HIS:
                continue
            if glossed(unq, tok):
                continue
            seen.add(tok.lower())
            hits.append((tok, why))
    #   The same exemption carries the forward-read scan: a phrase NAMED in quotes is being
    #   discussed, not claimed. That check blocked its own explanation on its first live run.
    low = unq.lower()
    low_fwd = low
    #   WORD BOUNDARIES, NOT A SUBSTRING. A raw `term in low` flagged 'cadence i' inside the
    #   phrase "that exit cadence instead". Every term is matched as whole words.
    for term in MINE:
        if re.search(r'\b%s\b' % re.escape(term), low) and term not in seen:
            seen.add(term)
            hits.append((term, 'my own shorthand'))
    fwd = []
    for term in FORWARD:
        if re.search(r'\b%s\b' % re.escape(term), low_fwd):
            fwd.append(term)

    if not hits and not fwd:
        print(json.dumps({}))
        return
    lines = []
    if hits:
        lines.append('%d term(s) in that reply Joe has no way to read:' % len(hits))
        lines += ['  - %s  (%s)' % (t, w) for t, w in hits[:20]]
        lines.append('Rewrite them in plain words, or gloss each one where it first appears'
                     ' (role + current value + units). Backtick a label only when the label'
                     ' itself is the subject.')
    if fwd:
        lines.append('%d phrase(s) that usually carry a read of bars AFTER the event being'
                     ' judged:' % len(fwd))
        lines += ['  - %s' % t for t in fwd[:20]]
        lines.append('For each one: could that sentence be written AT the bar it describes, with'
                     ' no later bar in hand? If not, recompute it inside the window the mech'
                     ' actually reads, or drop it. A hold of H bars may read the event bar and the'
                     ' H-1 bars after it, and nothing further.')
    print(json.dumps({'decision': 'block', 'reason': '\n'.join(lines)}))


if __name__ == '__main__':
    main()
