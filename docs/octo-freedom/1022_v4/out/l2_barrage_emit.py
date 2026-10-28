"""THE BARRAGE, painted on a TF1 pane. Joe 1027: *"in the jig, there is a green/red bgcolor pine
emit that uses arrays. for the list of barrages, create a pine emit that can be loaded on my TF1
pane"*.

It is the SAME producer the chain and out/l2_barrage.py call - `v4_l2_cadence.barrage`. This file
only paints, so a chart and a report can never disagree about which bars are barrages.

THE EMIT IS THE JIG'S, UNTOUCHED: `jig.score.emit_bgcolor`, whose format is locked by his 0731
ruling. Four named streams, each with its own `input.bool` toggle, `array.binary_search` on `time`,
one `bgcolor(bg)`. ORDER IS PRIORITY - the last matching stream paints over the earlier ones, which
is why the cadence bars are last.

    s_barrage_span_low    color.yellow   the ws1Mage cross bar through the cadence bar, LOW side
    s_barrage_span_high   color.blue     the same span, HIGH side
    s_barrage_low         color.green    the CADENCE bar, LOW target side
    s_barrage_high        color.red      the CADENCE bar, HIGH target side

ONE MAPPING IN HERE IS MINE: LOW target side -> green, HIGH -> red. He asked for the green/red
emit and named no side for either colour. It is arbitrary between the two, so it is written into
the toggle labels and the header notes - the chart says which is which without this file.

THE CADENCE BAR IS DOUBLED - its own TF1 bucket plus the next one - so a single-bar event is
visible at TF1. That is his own precedent from `emit_ws5_fifo.py`: *"the SPAN END is painted,
DOUBLED: the TF1 bar it ends on plus the one after it."*

THE SPAN IS THE DETECTION WINDOW, not a trade. It runs from the ws1Mage oob->ib cross to the
cadence bar, so it covers the ws1r reversal and every barrage line's reversal inside it. Toggle it
off and only the cadence bars remain.

NO HORIZON AND NO TRADE SIDE. Nothing past the cadence bar is painted, and no leg, pivot or
excursion is drawn - those live in the report, where they carry their own caveats.

THE .pine FILE IS GITIGNORED (`*.pine`, repo root) - this emitter is the durable artefact and the
.pine is regenerated from it.

usage: l2_barrage_emit.py [<start> <end>]     default 2026-08-30 .. 2026-09-06
"""
import os, sys, io
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import ln, v4_knobs as K, v4_rcfg_sweep as RS
import v4_closed_prev as CP, v4_l2_proxy as PX, v4_l2_cadence as CAD
from optimus9.analysis.jig import _Score
sys.stderr = _e

FROM_UTC = sys.argv[1] if len(sys.argv) > 2 else '2026-08-30 00:00:00'
TO_UTC = sys.argv[2] if len(sys.argv) > 2 else '2026-09-06 23:59:55'
BUCKET_MS = 60_000                                 # TF1 - the pane he loads it on
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'l2_barrage.pine')

A, B = ln.K(FROM_UTC), ln.K(TO_UTC)
E = RS.load((RS.K0, RS.R0, RS.S0))
BD = PX.Board(CP.ladder(E), E, MGE={t: ln.line('ws%dMage' % t) for t in range(1, 13)})
TS = ln.ts                                         # the 5 s epoch-ms grid

rows = []
for sd in (-1, +1):
    for bar, _ty, why in CAD.barrage(BD, sd, A, B):
        #   the cross bar comes back out of the producer's own `why`, so this file parses the one
        #   string the producer wrote rather than re-deriving the cross
        hhmmss = why.split('oob->ib ')[1].split(',')[0]
        day = ln.U(int(bar))[:10]
        cross = ln.K('%s %s' % (day, hhmmss))
        if cross > int(bar):                       # the cross sits on the previous UTC day
            cross = ln.K('%s %s' % (ln.U(int(bar) - 17280)[:10], hhmmss))
        assert cross <= int(bar), 'the ws1Mage cross is after the cadence it produced'
        rows.append((int(bar), int(sd), int(cross), why))
rows.sort()

_b = lambda m: (int(m) // BUCKET_MS) * BUCKET_MS

span_lo, span_hi, cad_lo, cad_hi = [], [], [], []
for bar, sd, cross, _why in rows:
    #   THE SPAN: every TF1 bucket from the cross bar to the cadence bar inclusive
    a, b2 = _b(int(TS[cross])), _b(int(TS[bar]))
    span = list(range(a, b2 + BUCKET_MS, BUCKET_MS))
    (span_lo if sd < 0 else span_hi).extend(span)
    #   THE CADENCE, DOUBLED - his emit_ws5_fifo precedent
    (cad_lo if sd < 0 else cad_hi).extend((b2, b2 + BUCKET_MS))

streams = [                                        # ORDER IS PRIORITY - later paints over earlier
    {'name': 'barrage_span_low', 'ts': _Score.bucket_spans(span_lo, BUCKET_MS),
     'color': 'color.yellow'},
    {'name': 'barrage_span_high', 'ts': _Score.bucket_spans(span_hi, BUCKET_MS),
     'color': 'color.blue'},
    {'name': 'barrage_low', 'ts': _Score.bucket_spans(cad_lo, BUCKET_MS), 'color': 'color.green'},
    {'name': 'barrage_high', 'ts': _Score.bucket_spans(cad_hi, BUCKET_MS), 'color': 'color.red'},
]

nlo = sum(1 for r in rows if r[1] < 0)
notes = [
    'THE BARRAGE, lineage2. spec: docs/octo-freedom/1022_v4/v4_lineage2.md section 16',
    'the rule is v4_l2_cadence.barrage - the SAME producer the chain calls. this file only paints.',
    '',
    'a barrage cadence fires when ALL of:',
    '  1 ws1Mage crosses from oob to ib on the target side',
    '  2 ws1r reverses on the SAME side within LIN2_BARRAGE_TOL_S %d s of that cross'
    % K.LIN2_BARRAGE_TOL_S,
    '  3 at least LIN2_BARRAGE_LINES %d r lines reverse on that side between the cross and the'
    % K.LIN2_BARRAGE_LINES,
    '    ws1r reversal, counted over ws1..ws%d' % K.L2_MOM_MAXTF,
    '  4 one of those lines is at or above LIN2_BARRAGE_MIN_TF %d' % K.LIN2_BARRAGE_MIN_TF,
    'the tolerance and the line count are MEASURED off his 2026-08-30 02:29 instance. MIN_TF 9 is',
    '  his ruling "dropping 0229 is ok - 0234 picked it up" and it excludes that same instance.',
    '',
    'THE PAINTED BAR IS THE CADENCE BAR: the last contributing reversal\'s STAMP, which is',
    '  LIFT_WOB %d bars = %d s after the raw ws1r reversal. nothing is painted before every'
    % (K.LIFT_WOB, (int(K.LIFT_WOB) - 1) * 5),
    '  reversal in the count is confirmed, so no bar here is knowable later than it is drawn.',
    'the cadence bar is DOUBLED - its TF1 bucket plus the next - so a one-bar event shows at TF1.',
    '',
    'green  = the cadence bar, LOW target side      (%d of %d)' % (nlo, len(rows)),
    'red    = the cadence bar, HIGH target side     (%d of %d)' % (len(rows) - nlo, len(rows)),
    'yellow = the detection window, LOW side: the ws1Mage cross bar through the cadence bar',
    'blue   = the detection window, HIGH side',
    'the side->colour mapping is MINE, not his - he named no side for either colour.',
    '',
    'IN THE CHAIN a barrage cadence EXHAUSTS the walk - his "both - a cadence keeps the walk\'s',
    '  transactions uniform, and exhaust will fire". LIN2_BARRAGE_ON %d.' % K.LIN2_BARRAGE_ON,
    'NO HORIZON, NO TRADE SIDE: nothing past the cadence bar is drawn and no leg or excursion is',
    '  painted. those are in out/l2_barrage_%s_%s.md with their own caveats.'
    % (FROM_UTC[5:10].replace('-', ''), TO_UTC[5:10].replace('-', '')),
    '',
    'range %s -> %s UTC. %d cadences on %d TF1 bars. RULED_OK %s.'
    % (FROM_UTC, TO_UTC, len(rows), sum(len(s['ts']) for s in streams), K.RULED_OK),
]

total = _Score(None).emit_bgcolor(streams, OUT, 'barrage %s to %s (TF1)'
                                  % (FROM_UTC[:10], TO_UTC[:10]), notes=notes)
print('  %s' % OUT)
print('  %d cadences: %d LOW, %d HIGH | %d TF1 bars painted'
      % (len(rows), nlo, len(rows) - nlo, total))
print('')
print('| the cadence bar | the target side | the ws1Mage cross | the TF1 bars painted |')
print('|---|---|---|---|')
for bar, sd, cross, _why in rows:
    a, b2 = _b(int(TS[cross])), _b(int(TS[bar]))
    print('| %s | %s | %s | %d |' % (ln.U(bar), 'HIGH' if sd > 0 else 'LOW', ln.U(cross),
                                     (b2 - a) // BUCKET_MS + 2))
