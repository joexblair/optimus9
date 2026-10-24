"""THE WALK, AND WHO OWNS IT. Joe 1024:

    no other mech can meddle with the walk once walk has "started working with a mech"

    let's send a signal out from each mech to the walk, and those signals will be born of the
    qualifiers... that allows the walk to discard any mech signal except the one its holding, until
    rev-trade

ONE RESPONSIBILITY: take walk requests, let ONE claim the walk, run it, and emit the router signal.
It knows no mech's qualifiers - it reads `start_tf`, `anchor` and `immediate` off the request.

WHAT IT REPLACED. Each mech called `v4_fast.walk` itself, so three independent walks ran over the
same bars. Nothing meddled - `walk` is pure - they DUPLICATED: on 2026-09-01, 14 of 37 qualifier
events shared a signal bar, and the router then discarded the losers by alphabetical mech NAME.
The exclusivity now sits where the walk is, and the router sees one signal per walk.

THE SIGNAL BAR IS `max(the exhaust, the request bar)`, in one place for all three mechs. It is
Joe's 1023 backstop ruling generalised: the fire can land after the reversal the walk started
from, and a signal may not predate the condition that produced it. For both core arms the exhaust
is at or after the arm, so the max is the exhaust.

TWO READINGS ARE MINE AND STATED, because each of his rulings leaves exactly one consistent option:

    THE HOLD RELEASES ON THE WALK'S OWN EXHAUST, not on the router's action. *"until rev-trade"*
    and *"router doesn't feedback"* cannot both hold if the walk waits to learn what the router
    did - the router may DROP the signal on the pyramid test and no rev-trade would ever occur, so
    the walk would be held for the rest of the tape. The exhaust IS the rev-trade event this walk
    produces, so the hold runs to the exhaust bar inclusive and the next bar is free.

    A WALK THAT DOES NOT EXHAUST CLAIMS NOTHING. 'NO REVERSAL', 'NO IB CROSS' and the rest resolve
    to no rev-trade, so holding on one would block every later request with nothing coming to
    release it. On 2026-09-01 that is 2 of 37 requests - the 23:48:00 core arm1 and the 17:39:05
    backstop, which has no walkable run at all.

`scope` IS REQUIRED AND HAS NO DEFAULT. One walk globally, or one per side - the two give different
trades and the choice is Joe's. On 2026-09-01, 10 of 18 lockouts under the global reading are
cross-side, so it is not a detail.
"""
import io
import sys

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
import v4_knobs as K
import v4_fast as F
import v4_signal as SG
import v4_walk_req as WR
_e = sys.stderr; sys.stderr = io.StringIO()
import ln
sys.stderr = _e

#   the walk layer names the arm; the ROUTER layer does not need to. `v4_signal.MECHS` stays
#   ('core', 'backstop', 'saviour') and the arm travels in the report's detail column.
TO_SIGNAL = {'core arm1': 'core', 'core arm2': 'core', 'ws5rbackstop': 'backstop'}


def run(reqs, R, A, B, scope, journal=None):
    """Walk requests in, router signals out. -> list of signals, bar-ordered.

        reqs    every request from every mech, in any order
        scope   'global' - one walk at a time, either side
                'side'   - one walk at a time per side
        journal an optional list; one row per request with what the walk did with it

    REQUESTS ARE SERVED IN BAR ORDER, and within a bar by the mech's name - which is alphabetical
    and therefore arbitrary. That tie-break is UNRULED and it decides which mech claims the walk
    when two qualify on the same bar.
    """
    assert scope in ('global', 'side'), 'walk scope %r is not a mode' % (scope,)
    out, until = [], {}
    for q in sorted(reqs, key=lambda z: (z['bar'], z['mech'])):
        key = 'all' if scope == 'global' else int(q['side'])
        row = {'bar': q['bar'], 'side': q['side'], 'mech': q['mech'],
               'start_tf': q['start_tf'], 'anchor': q['anchor'], 'why': q['why']}
        if key in until and int(q['bar']) <= until[key]:
            row['verdict'] = 'DISCARDED'
            row['held_by'] = until[key]
            _keep(journal, row)
            continue

        if q['immediate'] and not K.oob(R[q['start_tf']][q['anchor']], q['side']):
            v, exh = 'IMMEDIATE', int(q['anchor'])    # v4core arm2's rule, carried on the request
        else:
            v, exh = F.walk(R, q['start_tf'], q['side'], q['anchor'], B)
        row['walk'] = v
        if v not in ('EXHAUST', 'IMMEDIATE') or exh is None:
            row['verdict'] = 'NO CLAIM'               # nothing to hold - see the module docstring
            _keep(journal, row)
            continue

        bar = max(int(exh), int(q['bar']))
        assert bar >= int(q['bar']), 'a signal landed before the request that produced it'
        until[key] = bar                              # held to the exhaust bar INCLUSIVE
        row['verdict'] = 'CLAIMED'
        row['signal'] = bar
        _keep(journal, row)
        why = q['why'] if v == 'IMMEDIATE' else '%s, exh %s' % (q['why'], SG.why_time(exh))
        if v == 'IMMEDIATE':
            why = '%s NOT oob - immediate exhaust' % q['why']
        out.append(SG.signal(bar, q['side'], TO_SIGNAL[q['mech']], q['bar'], why))
    out.sort(key=lambda z: (z['bar'], z['side']))
    return out


def _keep(journal, row):
    if journal is not None:
        journal.append(row)
