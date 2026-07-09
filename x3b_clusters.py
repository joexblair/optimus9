"""x3b_clusters.py — score the 0709 live session with and without the first-leg pyramid gate.

X3 measured the governor's effect on the MEAN over 42d and found it costs 22-47%. It never measured a cluster.
15 of 20 stops in the 0709 arm probe fired inside 6 clusters; the largest was 4 legs in 25s for -$438 (29% of
the run's loss). A cluster is the worst-episode event X3 could not see.

Method: replay every o9_ledger leg in open order. A leg on a side that already has an open position is an ADD.
The gate (risk.leg_further_along, reference = the side's FIRST leg) either admits or blocks it. A blocked leg
never opens, so its realized net never occurs; nothing else changes (exits are per-leg stops or whole-side
stack closes, both at prices the blocked leg did not influence).

Reports, per tolerance: legs blocked, net of blocked legs, resulting session net, max stack depth per side,
and the same for each of the 6 stop clusters.

Read-only. Run:  python3 x3b_clusters.py
"""
import datetime as dt

import numpy as np

from optimus9 import DatabaseManager
from optimus9.config import get_db_config
from optimus9.live.risk import leg_further_along

TOLS = (0.0, 0.05, 0.10, 0.20, 0.30, 0.50)
f = lambda m: dt.datetime.fromtimestamp(m / 1000, dt.timezone.utc).strftime('%H:%M:%S')


def legs(o9):
    rows = o9.execute(
        "SELECT led_id, side, qty, entry_px, exit_px, net, opened_ms, closed_ms, status, exit_order_id "
        "FROM o9_ledger ORDER BY opened_ms", fetch=True) or []
    return rows


def replay(rows, tol):
    """-> (blocked_ids, kept_net, blocked_net, depth_max). tol=None: gate off."""
    first = {}                      # side -> first_px of the CURRENT stack
    depth = {'Buy': 0, 'Sell': 0}
    dmax = 0
    blocked, kept_net, blk_net = [], 0.0, 0.0
    # a leg closes at closed_ms; process opens and closes in time order
    ev = []
    for r in rows:
        ev.append((int(r['opened_ms']), 0, r))
        if r['closed_ms']:
            ev.append((int(r['closed_ms']), 1, r))
    ev.sort(key=lambda e: (e[0], e[1]))
    live = set()
    for (t, kind, r) in ev:
        s = r['side']
        bd = 1 if s == 'Buy' else -1
        if kind == 0:
            px = float(r['entry_px'])
            if depth[s] == 0:                                  # first leg of a new stack
                first[s] = px
            elif tol is not None and not leg_further_along(bd, first[s], px, tol):
                blocked.append(r['led_id']); blk_net += float(r['net'] or 0)
                continue
            depth[s] += 1; live.add(r['led_id'])
            dmax = max(dmax, depth[s])
        else:
            if r['led_id'] not in live:
                continue                                       # it was blocked; never opened
            depth[s] -= 1; live.discard(r['led_id'])
            kept_net += float(r['net'] or 0)
    return blocked, kept_net, blk_net, dmax


def clusters(rows, gap_ms=60000):
    """Stops = single-leg exits. Group them by closed_ms proximity."""
    cnt = {}
    for r in rows:
        if r['exit_order_id']:
            cnt[r['exit_order_id']] = cnt.get(r['exit_order_id'], 0) + 1
    stops = [r for r in rows if r['closed_ms'] and cnt.get(r['exit_order_id']) == 1 and float(r['net']) < 0]
    stops.sort(key=lambda r: r['closed_ms'])
    out = []
    for r in stops:
        if out and int(r['closed_ms']) - int(out[-1][-1]['closed_ms']) <= gap_ms:
            out[-1].append(r)
        else:
            out.append([r])
    return [g for g in out if len(g) > 1]


def main():
    c = get_db_config(); c['database'] = 'o9_live'
    o9 = DatabaseManager(**c); o9.connect()
    rows = legs(o9)
    closed = [r for r in rows if r['status'] == 'closed']
    print("legs=%d (closed=%d, open=%d)  session net=%.2f\n"
          % (len(rows), len(closed), len(rows) - len(closed), sum(float(r['net'] or 0) for r in closed)))

    print("=== whole session ===")
    print("%-8s %8s %11s %11s %7s" % ("tol%", "blocked", "blocked_net", "session_net", "depth"))
    b0, k0, x0, d0 = replay(rows, None)
    print("%-8s %8d %11s %11.2f %7d" % ("off", 0, "-", k0, d0))
    for tol in TOLS:
        b, k, x, d = replay(rows, tol)
        print("%-8.2f %8d %11.2f %11.2f %7d  (%+.2f vs off)" % (tol, len(b), x, k, d, k - k0))

    print("\n=== the 6 stop clusters, gate off vs tol=0.00 ===")
    cl = clusters(rows)
    blocked0 = set(replay(rows, 0.0)[0])
    tot_saved = 0.0
    print("%-22s %5s %10s %8s %10s" % ("window", "legs", "net", "blocked", "saved"))
    for g in cl:
        net = sum(float(r['net']) for r in g)
        blk = [r for r in g if r['led_id'] in blocked0]
        saved = sum(float(r['net']) for r in blk)
        tot_saved += saved
        print("%-22s %5d %10.2f %8d %10.2f"
              % ("%s -> %s" % (f(int(g[0]['closed_ms'])), f(int(g[-1]['closed_ms']))), len(g), net, len(blk), -saved))
    print("%-22s %5s %10s %8s %10.2f" % ("TOTAL", "", "", "", -tot_saved))
    o9.disconnect()


if __name__ == "__main__":
    main()
