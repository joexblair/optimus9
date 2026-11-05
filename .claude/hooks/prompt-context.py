#!/usr/bin/env python3
"""UserPromptSubmit: Joe's convo style, plus the phrase lists the Stop hook blocks on.

HIS 1105 RULING, verbatim: *"keep the block, add the phrase list to the UserPromptSubmit hook, and
gate FORWARD on a number-in-the-sentence test"* - *"taken"*. The Stop hook fires AFTER the response
is on screen, so a block there makes the whole reply print again. This puts the same lists in front
of me BEFORE I write, so the block is the exception rather than the routine.

THE LISTS ARE IMPORTED FROM jargon-check.py, NOT COPIED. One source of truth: a copy would drift the
moment he adds a word, and then the reminder and the block would disagree.
"""
import importlib.util
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
STYLE = HERE.parent / 'joes-convo-style.md'


def _jargon():
    """jargon-check.py as a module. Its name has a dash, so importlib does the loading."""
    spec = importlib.util.spec_from_file_location('jargon_check', HERE / 'jargon-check.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)          # __name__ is not __main__, so main() does not run
    return m


def main():
    out = []
    try:
        out.append(STYLE.read_text())
    except OSError as e:
        out.append('# Joe\'s convo style could not be read: %s' % e)
    try:
        j = _jargon()
    except Exception as e:                                  # noqa: BLE001 - never fail the prompt
        out.append('\n# the jargon lists could not be read: %s' % e)
    else:
        out.append('\n'.join([
            '',
            '# The Stop hook blocks on these. Do not write them in the first place.',
            '',
            'The jargon check is a **Stop** hook, so it fires once the reply is already on screen',
            'and a block makes the whole reply print again. Avoiding these costs nothing; tripping',
            'one costs Joe a re-print.',
            '',
            '## my own shorthand - rewrite in plain words, or gloss inline (role + value + units)',
            '',
            ', '.join(sorted(j.MINE)),
            '',
            '## forward reads - ONLY flagged when a number sits in the same sentence',
            '',
            'A sentence that carries a timestamp or a value must be true AT the bar it describes.',
            'A hold of H bars may read the event bar and the H-1 bars after it, nothing further.',
            '',
            ', '.join(sorted(j.FORWARD)),
            '',
            '## nouns that need saying WHICH one - "the <word>", "this <word>", "that <word>"',
            '',
            ', '.join(sorted(j.AMBIG_NOUNS)),
            '',
            'Put the qualifier before the noun - "the fdm2 leg walk", "the repaired producer" - or',
            'gloss it in the same sentence.',
            '',
        ]))
    print(json.dumps({'hookSpecificOutput': {
        'hookEventName': 'UserPromptSubmit',
        'additionalContext': '\n'.join(out)}}))


if __name__ == '__main__':
    main()
