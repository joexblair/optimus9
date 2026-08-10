"""emit_ad_pine — s46_window trades + the reverse trigger, as TF2 bgcolors. Joe 0803 03:20.

    Joe: "drop our current window into a db table ... then update the ad_entries pine"
    Joe 0803, on the streams: "use yellow (long) and blue (short) bgcolors to show me when '(s4m
    crossing boundary while s4Mage stays OOB and s6Mage is IB)' is triggered"

PURE READER. Every trade and trigger comes from s46_window and s46_revtrig. No jig, no line rebuild,
no entry logic re-derived here - that lives in build_s46.py / build_s46_window.py. This file only maps
rows to colours.

FOUR STREAMS, one TF2 bucket each (120,000 ms = 2 min).
    GREEN   trade entry LONG    s4Mage breached HI  (sw_dr +1)
    RED     trade entry SHORT   s4Mage breached LO  (sw_dr -1)
    YELLOW  reverse trigger implying LONG   - s4m crossed UP   out of LO  (rv_cage 'lo')
    BLUE    reverse trigger implying SHORT  - s4m crossed DOWN out of HI  (rv_cage 'hi')

ORDER IS PRIORITY. _bgcolor_frag is LOCKED to a single bgcolor(bg) (jig.py:547), so on a shared bucket
the LAST matching stream wins. Trigger streams are emitted after trade streams, because the trigger is
the thing being inspected.

COLOUR OF THE REVERSE = THE DIRECTION IT IMPLIES, not the cage. A lo cage means s4m is spiking UP, which
implies a LONG, so lo -> YELLOW and hi -> BLUE. Joe 0803 left "direction of s4M" open; flip the two
colour strings if the cage side was meant.

THE CONFIG BEHIND s46_window (recorded here so the chart legend cannot drift from it)
    ENTRY   wob 1 - the boundary cross bar itself, causal.
    EXIT    s6x (bb 5|0.35|close @TF6) crossing s6Mage (bb 37|0.90|close @TF6), s6x OOB within 6 min,
            the cross held 3 bars = 15 s (Joe 0803: "3 is good").
    GATES   items 5 and 14 are BAKED INTO s46_window - every row here already passed them:
              5   in-bounds stretch before the excursion > 24 bars = 120 s
              14  s1Mage within 15 board points of the breach boundary for > 24 bars = 120 s
            item 6 (same-side s2m) stays a column; --s2m applies it. item 13 (ALT) is a column and is
            NOT applied - measured vacuous at 13,622 of 13,622 runs.

    python3 emit_ad_pine.py [--out ad_entries.pine] [--s2m]
"""
import sys, os, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from optimus9.analysis.jig import _Score
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

TF2 = 120_000            # bgcolor bucket, ms - Joe 0803: "on a TF2 pane"
def main(argv):
    g = lambda f, d: (argv[argv.index(f) + 1] if f in argv else d)
    out = g('--out', 'ad_entries.pine')
    use_s2m = '--s2m' in argv
    where = 'sw_s2m_ok=1' if use_s2m else '1=1'

    d = DatabaseManager(**get_db_config()); d.connect()
    TR = d.execute('SELECT sw_entry_ms,sw_dr,sw_mae,sw_exit_ms,sw_entry_utc FROM s46_window '
                   'WHERE %s ORDER BY sw_entry_ms' % where, fetch=True)
    if not TR:
        raise SystemExit('s46_window has no rows for: %s' % where)
    a, b = TR[0]['sw_entry_ms'], TR[-1]['sw_entry_ms']
    RV = d.execute('SELECT rv_ms,rv_cage FROM s46_revtrig WHERE rv_ms>=%s AND rv_ms<=%s ORDER BY rv_ms',
                   (a, b), fetch=True)
    tot = d.execute('SELECT COUNT(*) n FROM s46_window', fetch=True)[0]['n']
    d.disconnect()

    lg = [r['sw_entry_ms'] for r in TR if r['sw_dr'] == 1]
    sh = [r['sw_entry_ms'] for r in TR if r['sw_dr'] == -1]
    yl = [r['rv_ms'] for r in RV if r['rv_cage'] == 'lo']
    bl = [r['rv_ms'] for r in RV if r['rv_cage'] == 'hi']
    streams = [
        {'name': 'trade_long', 'ts': _Score.bucket_spans(lg, TF2), 'color': 'color.green',
         'meaning': 'TRADE entry LONG   - s4Mage breached HI'},
        {'name': 'trade_short', 'ts': _Score.bucket_spans(sh, TF2), 'color': 'color.red',
         'meaning': 'TRADE entry SHORT  - s4Mage breached LO'},
        {'name': 'rev_long', 'ts': _Score.bucket_spans(yl, TF2), 'color': 'color.yellow',
         'meaning': 'REVERSE trigger -> LONG  (s4m up out of LO)'},
        {'name': 'rev_short', 'ts': _Score.bucket_spans(bl, TF2), 'color': 'color.blue',
         'meaning': 'REVERSE trigger -> SHORT (s4m down out of HI)'},
    ]
    maes = [r['sw_mae'] for r in TR]
    gate = '5 + 14 (baked in)' + (' + 6 same-side s2m' if use_s2m else '')
    legend = [
        's46_window trades + reverse trigger  -  LEGEND', '',
        '  BGCOLOR, one TF2 bucket each. Later stream wins a shared bucket.',
        '    GREEN   TRADE entry LONG    s4Mage breached HI          %d' % len(streams[0]['ts']),
        '    RED     TRADE entry SHORT   s4Mage breached LO          %d' % len(streams[1]['ts']),
        '    YELLOW  REVERSE -> LONG     s4m crossed UP out of LO    %d' % len(streams[2]['ts']),
        '    BLUE    REVERSE -> SHORT    s4m crossed DOWN out of HI  %d' % len(streams[3]['ts']),
        '    bucket %d ms = %g s = TF2 - read this on a TF2 chart' % (TF2, TF2 / 1000.0), '',
        'SOURCE    s46_window (%d of %d rows, gates: %s) + s46_revtrig. This file computes nothing.'
        % (len(TR), tot, gate),
        'GATE 5    in-bounds stretch before the excursion > 24 bars = 120 s',
        'GATE 14   s1Mage (bb 37|0.83|close @TF1) within 15 board points of the breach boundary for',
        '          > 24 bars = 120 s before entry',
        'ENTRY     wob 1 - the s4Mage boundary cross bar itself. Causal: no dwell filter, so nothing',
        '          about the run\'s future length is read.',
        'EXIT      s6x (bb 5|0.35|close @TF6) crossing s6Mage (bb 37|0.90|close @TF6), s6x OOB on the',
        '          breach side within the last 72 bars = 6 min. s6Mage level NOT tested.',
        'EXIT WOB  the cross must hold 3 bars = 15 s; the exit is the 3rd bar.',
        'REVERSE   s4m leaves OOB AND s4Mage still OOB same side AND s6Mage IB. Colour = the direction',
        '          it IMPLIES, not the cage.',
        'DIR       hi breach = LONG.', '',
        'WINDOW    %s -> %s   |   %d trades, %d LONG / %d SHORT'
        % (TR[0]['sw_entry_utc'], TR[-1]['sw_entry_utc'], len(TR),
           sum(1 for r in TR if r['sw_dr'] == 1), sum(1 for r in TR if r['sw_dr'] == -1)),
        'MAE       mean %.3f%%  median %.3f%%  max %.3f%%   |   %d distinct exits, %.2f entries per exit'
        % (sum(maes) / len(maes), sorted(maes)[len(maes) // 2], max(maes),
           len(set(r['sw_exit_ms'] for r in TR)),
           len(TR) / len(set(r['sw_exit_ms'] for r in TR))),
    ]
    nbg = _Score(None).emit_bgcolor(streams, out, 's46_window trades + reverse trigger',
                                    notes='\n'.join(legend))
    print('%s  ->  %d painted TF2 buckets' % (out, nbg))
    print('  trades   %d of %d   (gate: %s)   LONG %d / SHORT %d'
          % (len(TR), tot, gate, len(lg), len(sh)))
    print('  triggers %d   yellow %d / blue %d' % (len(RV), len(yl), len(bl)))
    ux = set(r['sw_exit_ms'] for r in TR)
    print('  MAE mean %.3f%%  median %.3f%%  max %.3f%%   |   %d exits, %.2f n/exit'
          % (sum(maes) / len(maes), sorted(maes)[len(maes) // 2], max(maes), len(ux), len(TR) / len(ux)))


if __name__ == '__main__':
    main(sys.argv[1:])
