"""emit_ws_gated — the GATED gcws30b signals as a pine bgcolor emit, on a 1-minute pane. Joe 0810.

Joe: "show me the 78 ws1 markers in a pine emit, using the red/green bgcolors, loaded on a 1min TV
pane." These are the signals the ws1 gate BLOCKED — wsw_gated = 1 — i.e. ws1Mage was not OOB, ws1b
was not outside the fence, and the 19-bar ws1b lookback found nothing.

Reads ws_strat_walk, so it always reflects the banked build. Writes its own file; the raw-marker
emit (ws_strat_walk.pine, all 361) is untouched.

    python3 emit_ws_gated.py
"""
import datetime as dt
from datetime import timezone

from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.jig import _Score

BUCKET_MS = 60_000            # 1-minute pane (Joe 0810). 15_000 is the 15s pane the raw emit uses.
OUT = 'ws_strat_blocked.pine'   # renamed 0810: ws_strat_gated.pine is Joe's working file
#                                 and carries the RELEASED set written by
#                                 build_ws_strat_walk.py. This emitter must never clobber it.
u = lambda t: dt.datetime.fromtimestamp(int(t) / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    cfg = db.execute('SELECT DISTINCT wsw_oobw o, wsw_xwob x, wsw_fence f, wsw_lb l, wsw_blen bl,'
                     ' wsw_bmult bm, wsw_mlen ml, wsw_mmult mm FROM ws_strat_walk', fetch=True)[0]
    tot = db.execute('SELECT COUNT(*) n FROM ws_strat_walk', fetch=True)[0]['n']
    rows = db.execute('SELECT wsw_cross_ms m, wsw_cross_utc u, wsw_side s, wsw_oob_bars ob,'
                      ' wsw_ws1Mage mg, wsw_ws1b b, wsw_lb_oob lo, wsw_lb_fence lf'
                      ' FROM ws_strat_walk WHERE wsw_gated=1 ORDER BY wsw_cross_ms', fetch=True)
    span = db.execute('SELECT MIN(wsw_cross_utc) a, MAX(wsw_cross_utc) b FROM ws_strat_walk',
                      fetch=True)[0]
    db.disconnect()

    hi = [r['m'] for r in rows if r['s'] > 0]
    lo = [r['m'] for r in rows if r['s'] < 0]
    print(f'{len(rows)} GATED of {tot} signals   hi {len(hi)} / lo {len(lo)}')
    print(f"{'cross':<20} {'side':>4} {'dwell':>5} {'ws1Mage':>8} {'ws1b':>7} {'lb_oob':>7} {'lb_fen':>7}")
    for r in rows:
        print(f"{r['u']:<20} {r['s']:>+4} {r['ob']:>5} {r['mg']:>8.2f} {r['b']:>7.2f} "
              f"{r['lo']:>7} {r['lf']:>7}")

    bkt = _Score(None).bucket_spans
    hb, lb_ = bkt(hi, BUCKET_MS), bkt(lo, BUCKET_MS)
    streams = [{'name': 'gated_hi', 'ts': hb, 'color': 'color.red'},
               {'name': 'gated_lo', 'ts': lb_, 'color': 'color.green'}]
    notes = (f'ws_strat GATED | red = gcws30b crossed OOB(hi) -> IB and was BLOCKED | '
             f'green = OOB(lo) -> IB and BLOCKED'
             f' | these are the {len(rows)} of {tot} signals the ws1 gate REJECTED:'
             f' ws1Mage not OOB, ws1b not outside [{cfg["f"]},{100 - cfg["f"]}],'
             f' and the {cfg["l"]}-bar ws1b lookback ({cfg["l"] * 5}s) found no ws1b OOB'
             f' | gcws30b = bb {cfg["bl"]}|{cfg["bm"]}|close @30s;'
             f' ws1Mage = bb {cfg["ml"]}|{cfg["mm"]}|close @60s'
             f' | OOB dwell > {cfg["o"]} bars of 5s ({(cfg["o"] + 1) * 5}s), XWOB {cfg["x"]}'
             f' | painted on the {BUCKET_MS // 1000}s = 1-MINUTE grid: each cross floored to its'
             f' minute open | walk {span["a"]} -> {span["b"]}'
             f' | the ACCEPTED {tot - len(rows)} are NOT here — ws_strat_walk.pine carries all {tot} raw')
    total = _Score(None).emit_bgcolor(streams, OUT, 'ws_strat GATED — ws1 rejected (1min)',
                                      notes=notes)
    print(f'\n{OUT} -> {total} painted 1-minute bars')
    print(f'  red   gated_hi  {len(hi):>3} events -> {len(hb):>3} distinct minutes')
    print(f'  green gated_lo  {len(lo):>3} events -> {len(lb_):>3} distinct minutes')
    coll = (len(hi) - len(hb)) + (len(lo) - len(lb_))
    print(f'  {coll} events share a minute with another of the same side')
    both = set(hb) & set(lb_)
    print(f'  {len(both)} minutes carry BOTH a hi and a lo gated signal — green paints over red there')


if __name__ == '__main__':
    main()
