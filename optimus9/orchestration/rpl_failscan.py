"""FULL-TAPE FAILURE SCAN (Joe 0723) — the confluence work-list.

The sweep's soft-spots only ever see the fixed 10-day OOS block, so the failure-window candidate pool is small and
static. This scans the CURRENT cornered elite across EVERY 24h window of the whole tape, ranks by net, and banks the
result. The worst windows are where the mechanics genuinely don't cover — i.e. where confluences need building.

Banked to `rpl_failscan` (append-only, snapshot per invocation tagged with the config's cycle/round), so it EVOLVES
as IS windows are swapped out over evo cycles. The pulse reads the latest snapshot as an appendix.

Run:  PYTHONPATH=/home/joe/thecodes python3 -m optimus9.orchestration.rpl_failscan
"""
import json
import numpy as np
import optimus9.orchestration.rpl_evo_sweep as e
import optimus9.orchestration.rpl_walk as R
from optimus9.compute.swing_detect import find_pivots

WIN_MS = 24 * 3600 * 1000
SCAN = [(int(R.end_ms - off * e.DAY), int(R.end_ms - off * e.DAY + WIN_MS)) for off in range(2, int(e.POOL_DAYS))]

def _legs(flips, ets, epx):
    out = []
    for a, b in zip(flips, flips[1:]):
        i = int(np.searchsorted(ets, a['ts'])); j = int(np.searchsorted(ets, b['ts']))
        seg = epx[i:j + 1]; ep = epx[i]
        if len(seg) < 2 or ep <= 0 or not np.isfinite(ep): continue
        piv = find_pivots(seg, e.SWING_PCT)
        if not piv: out.append((0.0, 0.0, int(a['rc']))); continue
        pv = np.array([seg[p[0]] for p in piv], float); hi = np.nanmax(pv); lo = np.nanmin(pv)
        if a['dir'] == 'bull': mfe = (hi - ep) / ep * 100; mae = (ep - lo) / ep * 100
        else: mfe = (ep - lo) / ep * 100; mae = (hi - ep) / ep * 100
        out.append((mfe, mae, int(a['rc'])))
    return out

def snapshot(db=None, snap=None, cycle=0, quiet=False):
    """Score the CURRENT DB elite (per objective) across the whole tape and bank to rpl_failscan — the cornered
    elite's failure windows are the confluence work-list. Callable two ways:
      - standalone via main() (opens its own connection, prints the worst-5 per objective)
      - from the sweep at PHASE-CONVERGENCE (pass the live `db` + `cycle`, quiet=True)
    Engine state (R.L0 / knobs) is saved+restored around each objective via e._enter, so it is safe to call
    mid-run — the sweep's elite state is untouched on return. Returns (snap_tag, {objective: n_tradeable_windows})."""
    import time as _t
    own = db is None
    d = e._db() if own else db
    d.execute('''CREATE TABLE IF NOT EXISTS rpl_failscan (
        fs_id INT AUTO_INCREMENT PRIMARY KEY, fs_run VARCHAR(24), fs_snap VARCHAR(24),
        fs_cycle INT, fs_round INT, fs_objective VARCHAR(8), fs_isdays INT,
        fs_win_start BIGINT, fs_net DOUBLE, fs_mfe DOUBLE, fs_mae DOUBLE, fs_trades INT,
        fs_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    snap = snap or _t.strftime('%m-%d %H:%M')
    counts = {}
    for o in ('rc', 'climb'):
        q = d.execute("SELECT re_round,re_config FROM rpl_evo WHERE re_scope='panel' AND re_objective=%s "
                      "ORDER BY re_round DESC LIMIT 1", (o,), fetch=True)
        if not q:
            if not quiet: print(f'{o}: no elite yet')
            continue
        rnd = q[0]['re_round']; cfg = q[0]['re_config']
        cfg = json.loads(cfg) if isinstance(cfg, str) else cfg
        restore, ets, epx = e._enter(cfg)
        rows = []
        try:
            for (s, en) in SCAN:
                legs = _legs(R.run_chain('bear', s, persist=False, end=en), ets, epx)
                sel = [(m, a) for (m, a, rc) in legs if (rc if o == 'rc' else not rc)]
                if len(sel) < 2: continue                       # need real activity to judge the window
                nets = [m - a for m, a in sel]
                rows.append((e.RUN_ID, snap, int(cycle), rnd, o, e.IS_DAYS, int(s),
                             float(np.median(nets)), float(np.median([m for m, _ in sel])),
                             float(np.median([a for _, a in sel])), len(sel)))
        finally:
            restore()
        if rows:
            d.executemany('INSERT INTO rpl_failscan (fs_run,fs_snap,fs_cycle,fs_round,fs_objective,fs_isdays,'
                          'fs_win_start,fs_net,fs_mfe,fs_mae,fs_trades) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', rows)
        counts[o] = len(rows)
        if not quiet:
            worst = sorted(rows, key=lambda r: r[7])[:5]
            print(f'\n=== {o.upper()} full-tape scan (elite r{rnd}, {len(rows)}/{len(SCAN)} tradeable windows) ===')
            for r in worst:
                print(f"  {_t.strftime('%b-%d', _t.gmtime(r[6] / 1000))}  net {r[7]:+.3f}  MFE {r[8]:+.3f} MAE {r[9]:+.3f}  ({r[10]} trades)")
    if own:
        d.disconnect()
    return snap, counts


def main():
    snapshot()

if __name__ == '__main__':
    main()
