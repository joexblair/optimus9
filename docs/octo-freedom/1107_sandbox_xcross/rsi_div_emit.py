"""`bullish-rsi` / `bearish-rsi` as a pine bgcolor overlay, built from the events file. Joe 1107. -> .pine

HIS ASK, verbatim: *"there's a red/green blue/yellow pine emit module in the jig - please create the pine
script.  red and blue are bearish, green and yellow are bearish.  red/green is ws1r, blue/yellow is
gcws30r"*, *"double print the bgcolors - one at the ws1 event bar, and one on the following ws1 bar"*,
*"align the timestamps with ws1"*, *"don't add anything I havem't asked for"*.

    red     ws1r bearish-rsi        green   ws1r bullish-rsi
    blue    gcws30r bearish-rsi     yellow  gcws30r bullish-rsi
    "green and yellow are bearish" is read as BULLISH - red and blue already carry bearish.

IT READS rsi_div_<day>.txt, the table rsi_div.py wrote - nothing is recomputed here. The event's time
is its PRINT bar, floored onto the 1-minute ws1 bar; that bar and the next ws1 bar are painted.
Built with _Score.emit_bgcolor and _Score.bucket_spans, the banked pine emit.

Usage:  python3 rsi_div_emit.py 2026-08-25
"""
import datetime as dt
import io
import os
import re
import sys

sys.path.insert(0, '/home/joe/thecodes')
_e = sys.stderr; sys.stderr = io.StringIO()
try:
    from optimus9.analysis.jig import _Score
    from optimus9.analysis import jig as _JIG
finally:
    sys.stderr = _e

HERE = os.path.dirname(os.path.abspath(__file__))
BUCKET_MS = 60_000                     # the ws1 bar, his "align the timestamps with ws1"
TS = re.compile(r'^2026-\d\d-\d\d \d\d:\d\d:\d\d$')
COLOUR = {('ws1r', 'bearish-rsi'): 'color.red', ('ws1r', 'bullish-rsi'): 'color.green',
          ('gcws30r', 'bearish-rsi'): 'color.blue', ('gcws30r', 'bullish-rsi'): 'color.yellow'}


def ms(s):
    return int(dt.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
               .replace(tzinfo=dt.timezone.utc).timestamp() * 1000)


def main(day):
    #   THE GATE PICKS THE FILE PAIR, so the gcws30b overlay is not overwritten by the ws2b one.
    g = _JIG.RSIDIV_GATE                          # the jig's banked gate line, its one home
    tag = day if g == 'gcws30b' else '%s_%s' % (day, g)
    src = os.path.join(HERE, 'rsi_div_%s.txt' % tag)
    out = os.path.join(HERE, 'rsi_div_%s.pine' % tag)
    ts = {k: [] for k in COLOUR}
    n = {k: 0 for k in COLOUR}
    for L in open(src):
        c = [x.strip() for x in L.strip().strip('|').split('|')]
        if len(c) < 3 or not TS.match(c[0]) or (c[2], c[1]) not in COLOUR:
            continue
        a = (ms(c[0]) // BUCKET_MS) * BUCKET_MS
        ts[(c[2], c[1])] += [a, a + BUCKET_MS]          # the ws1 event bar and the following ws1 bar
        n[(c[2], c[1])] += 1
    #   ORDER IS PRIORITY, the banked order: yellow, blue, green, red - a later stream paints over.
    order = [('gcws30r', 'bullish-rsi'), ('gcws30r', 'bearish-rsi'), ('ws1r', 'bullish-rsi'), ('ws1r', 'bearish-rsi')]
    streams = [{'name': '%s_%s' % (k[0], k[1].replace('-', '_')),
                'ts': _Score.bucket_spans(ts[k], BUCKET_MS), 'color': COLOUR[k]} for k in order]
    notes = ['bullish-rsi / bearish-rsi, %s, gate %s same-side oob, from %s' % (day, g, os.path.basename(src))] + \
            ['%-6s = %s %s (%d events)' % (COLOUR[k].split('.')[-1], k[0], k[1], n[k]) for k in order] + \
            ['each event paints its ws1 bar (the print time floored to 1 minute) and the next ws1 bar']
    _Score(None).emit_bgcolor(streams, out, 'rsi divergence %s %s' % (day, g), notes=notes)
    print(out, {'%s %s' % k: n[k] for k in order})


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '2026-08-25')
