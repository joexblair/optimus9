"""load_wsf_validation - Joe's marks from the transfer csv into wsf_event_mark.

Joe 0830: "260830_0804_wsf_validation.csv is ready in the transfer folder ~/thecodes/transfer".

HIS KEY, verbatim, 0830:
    "1 = good , blank = 153 poor signals"
    "the 0 at 11:53:15 = poor signal"
    "consolidation and large bull leg are context. consolidation detection is a mech that we don't
     have yet - I gave it as context becuse the matrix values might not make sense"

So the file carries TWO verdicts, not three. 1 is good; blank and 0 are both poor. They are stored
as Joe's own words - `good` and `poor` - not as 1/0/blank. A three-valued column that means two
things is a trap for the next reader, and wem_verdict is VARCHAR(16). MINE, STATED.

CONTEXT IS NOT A VERDICT. `consolidation` and `large bull leg` go to wem_words untouched. Joe calls
them context and says consolidation detection is a mech that does not exist yet, so they are a
reading of the tape, not a judgement of the event.

THE TIMESTAMPS ARE EXCEL SERIALS and drift by a fraction of a second. Each is taken as a fraction
of a day, converted to seconds, and snapped to the 5 s grid. Every one of the 210 rows matched a
banked event bar on the first pass; the script stops if any row fails to match rather than loading
a partial set.

A VERDICT ALREADY WRITTEN IS NEVER OVERWRITTEN. Joe 0827: "no deletes". A second load onto a row
that already carries a verdict is refused and the row is listed.
"""
import csv
import os
import sys
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from build_wsf_walk_events import SIG

CSV = os.path.expanduser('~/thecodes/transfer/260830_0804_wsf_validation.csv')
DAY = '2026-08-04'
SRC_RUN = None      # RUN SCOPE. None = the highest run at SIG


def bar(serial):
    """an Excel serial -> the bar it names, snapped to the 5 s grid."""
    s = int(round((float(serial) % 1) * 86400 / 5.0) * 5)
    return f'{DAY} {s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}'


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    run = SRC_RUN
    if run is None:
        run = db.execute('SELECT MAX(wem_run) r FROM wsf_event_mark WHERE wem_knobs=%s',
                         (SIG,), fetch=True)[0]['r']
        if run is None:
            print(f'  no rows in wsf_event_mark at {SIG}'); db.disconnect(); return 1
        run = int(run)

    rows = list(csv.DictReader(open(CSV, encoding='utf-8-sig')))
    marks = {}
    for r in rows:
        v = (r['wem_verdict'] or '').strip()
        marks[bar(r['wem_utc'])] = ('good' if v == '1' else 'poor',
                                    (r['wem_words'] or '').strip() or None)

    have = {str(x['u']): x['v'] for x in db.execute(
        'SELECT wem_utc u, wem_verdict v FROM wsf_event_mark WHERE wem_knobs=%s AND wem_run=%s',
        (SIG, run), fetch=True)}
    missing = sorted(b for b in marks if b not in have)
    if missing:
        print(f'  STOPPING: {len(missing)} csv rows have no event at that bar in run {run}.')
        for b in missing[:10]:
            print(f'    {b[11:]}')
        db.disconnect(); return 1
    already = sorted(b for b in marks if have.get(b) is not None)
    if already:
        print(f'  STOPPING: {len(already)} rows already carry a verdict. Joe 0827: "no deletes".')
        for b in already[:10]:
            print(f'    {b[11:]}  currently {have[b]}')
        db.disconnect(); return 1

    db.executemany('UPDATE wsf_event_mark SET wem_verdict=%s, wem_words=%s '
                   'WHERE wem_knobs=%s AND wem_run=%s AND wem_utc=%s',
                   [(v, w, SIG, run, b) for b, (v, w) in marks.items()])
    n = db.execute('SELECT wem_verdict v, COUNT(*) c FROM wsf_event_mark WHERE wem_knobs=%s '
                   'AND wem_run=%s GROUP BY 1 ORDER BY 1', (SIG, run), fetch=True)
    print(f'\n  loaded {len(marks)} marks onto run {run}')
    print(f'  from {os.path.basename(CSV)}\n')
    print(f"  {'wem_verdict':<14}{'events':>8}")
    for x in n:
        print(f"  {str(x['v']):<14}{x['c']:>8}")
    w = db.execute('SELECT COALESCE(wem_words, %s) w, COUNT(*) c FROM wsf_event_mark '
                   'WHERE wem_knobs=%s AND wem_run=%s GROUP BY 1 ORDER BY 1',
                   ('(none)', SIG, run), fetch=True)
    print(f"\n  {'wem_words':<20}{'events':>8}")
    for x in w:
        print(f"  {x['w']:<20}{x['c']:>8}")
    db.disconnect()
    return 0


if __name__ == '__main__':
    sys.exit(main())
