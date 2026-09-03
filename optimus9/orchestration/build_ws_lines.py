"""build_ws_lines — build the ws / gcws line families into the rpl line cache. Joe 0805.

Joe 0805: "when the lines are built, update the line cache through to 08-05 12:00", scope = the new
series only (his call; the existing ~360-line rpl set stays on the '08-01' key, 19 GB untouched).

WHERE THE SPECS COME FROM. Nothing here hardcodes a line. The 55 names are READ from
vw_indicator_configs_live by prefix, and each spec is resolved through LineStore — the one reader
that knows the DB column order (optimus9/compute/line_config.py). Change a row in indicator_configs
and this file follows it; the spec is in the cache key, so a changed row rebuilds only that line.
Registered by apply_ws_indicator_configs.py.

WHY THIS IS NOT IN rpl_walk (Joe 0805). rpl_walk runs `cache_jig(...)` at IMPORT (line 243), so the
~20 scripts that import it would each pay for these 55 lines. Separate file, separate build.

THE TAPE. '08-05' is a NEW key, not in rpl_walk.TAPES — nothing is duplicated. If it is ever
promoted into that registry, MOVE the tuple, do not copy it: three disagreeing tape literals is the
bug rpl_walk.py:48-58 documents.

    END      2026-08-09 12:00 UTC   (Joe 0808: "extend the line cache to 08-09 12:00")
    HOURS    40    unchanged from the '08-01' key
    WARMUP   1114  DERIVED, not chosen. The jig span is HOURS + 2*WARMUP (BLDetect._setup:
                   load_start = end - (lookback + warmup)h, lookback = hours + warmup), so
                   40 + 2*1114 = 2268 h = 94.5 d, which floors EXACTLY on the kline_collection
                   start 2026-05-07 00:00. Same construction '08-01' and the earlier '08-05' used.
    ts       05-07 00:00:00 -> 08-09 11:59:55, 1,632,960 bars at the 5 s grid
    size     1,632,960 x 8 B = 13,063,680 B per line

    SUPERSEDED KEY. The 08-05 12:00 / WARMUP 1066 tape (1,563,840 bars) is still on disk — a new end
    is a new cache key, so nothing was overwritten. Every table built before 0808 was built on it.

    python3 -m optimus9.orchestration.build_ws_lines [--rebuild] [--prefix ws]
"""
import sys
import datetime as dt
from datetime import timezone

import numpy as np

from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.compute.line_config import LineStore
from optimus9.orchestration.rpl_cache import cache_jig_perline

# TAPE_END MOVED 0901, Joe: "extend the line cache. cover the ws[60,45,30,20-13] lines, from
# 08-03 to 08-18", then "V1, a" - move END_MS here, in place, one truth for all 26 importers.
# WAS 2026-08-09 12:00, which capped the cache 8.5 days short of 08-18.
# WHY 08-19 12:00 AND NOT 08-19 00:00: a day's row set in ws_line_bar runs 00:00:00 through the
# NEXT day's 00:00:00 inclusive (17,281 rows), so 08-18 needs the 08-19 00:00:00 bar. A tape ending
# at 08-19 00:00 stops at 08-18 23:59:55. 12:00 also mirrors the convention the old value used.
#
# THE TAPE IS A FIXED WIDTH, NOT CLAMPED TO THE DATA START. 1,632,960 bars = 94.5 days ending at
# END_MS. Moving END_MS forward slides the FRONT off by the same amount: the window was
# 2026-05-07 00:00 -> 2026-08-09 11:59:55 and becomes 2026-05-17 12:00 -> 2026-08-19 11:59:55.
# The old window starting on kline_collection's first row was coincidence, not a clamp.
#
# MEASURED BEFORE THE MOVE, on the 08-04 slice (17,281 bars, timestamps identical on both tapes),
# three lines built at the new END_MS against the same spec cached at the old one:
#     line       bars differing   max abs diff   OOB sign diffs   cross-85   cross-15
#     ws1r               16,880      5.684e-14                0          0          0
#     ws20Mage            6,482      5.102e-10                0          0          0
#     ws60x                   0      0.000e+00                0          0          0
# The values are NOT bit-identical - a different warmup start leaves float residue in the
# recursion. No CONSUMED reading changes: 0 sign flips against hi 85 / lo 15, 0 crossing changes.
TAPE_END = dt.datetime(2026, 8, 19, 12, 0, tzinfo=timezone.utc)
END_MS = int(TAPE_END.timestamp() * 1000)
HOURS = 40
WARMUP = 1114
PREFIXES = ('ws', 'gcws')


def line_names(db, prefixes=PREFIXES):
    """The ws/gcws names LIVE from the view — so the build cannot drift from indicator_configs."""
    out = []
    for p in prefixes:
        rows = db.execute("SELECT ind_name FROM vw_indicator_configs_live WHERE ind_name LIKE %s "
                          "ORDER BY itf_seconds, ind_name", (p + '%',), fetch=True)
        # LIKE 'ws%' also matches 'gcws...'? No — LIKE anchors at the start. But 'gcws%' is a strict
        # subset of nothing else, so the two lists are disjoint by construction.
        out += [r['ind_name'] for r in rows if r['ind_name'].startswith(p)]
    return sorted(set(out), key=out.index)


def overrides(db, names):
    """{name: (tf_seconds, cfg_tuple, value_mode)} — the shape cache_jig_perline/Jig expect.
    LineStore.resolve + LineStore.value_mode are the sanctioned readers; no tuple is hand-built."""
    ls = LineStore(db)
    return {n: (*ls.resolve(n), ls.value_mode(n)) for n in names}


def main(rebuild=False, prefixes=PREFIXES):
    db = DatabaseManager(**get_db_config()); db.connect()
    row = db.execute("SELECT pxsmooth_dema_src, pxsmooth_dema_len FROM optimus9_system LIMIT 1",
                     fetch=True)
    pxs = {'src': row[0]['pxsmooth_dema_src'], 'len': row[0]['pxsmooth_dema_len']} if row else None
    names = line_names(db, prefixes)
    ovr = overrides(db, names)
    db.disconnect()

    print(f'tape 08-09  end {TAPE_END:%Y-%m-%d %H:%M} UTC  hours {HOURS}  warmup {WARMUP}  '
          f'span {HOURS + 2 * WARMUP} h')
    print(f'{len(ovr)} lines: ' + ', '.join(names))
    for n in names:
        tf, cfg, vm = ovr[n]
        print(f'  {n:<12} {tf:>5}s  {cfg}  {vm}')

    J = cache_jig_perline(END_MS, HOURS, WARMUP, ovr, pxs_cfg=pxs, rebuild=rebuild)
    ts = np.asarray(J.ts)
    u = lambda t: dt.datetime.fromtimestamp(int(t) / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    print(f'\nts {u(ts[0])} -> {u(ts[-1])}, {len(ts):,} bars')
    print(f"{'line':<12} {'finite':>10} {'min':>8} {'median':>8} {'max':>8} {'first_finite_utc':>21}")
    for n in names:
        a = np.asarray(J.W.line(n), float)
        f = np.isfinite(a)
        fi = int(np.argmax(f)) if f.any() else -1
        print(f'{n:<12} {int(f.sum()):>10,} {np.nanmin(a):>8.2f} {np.nanmedian(a):>8.2f} '
              f'{np.nanmax(a):>8.2f} {u(ts[fi]) if fi >= 0 else "-":>21}')


if __name__ == '__main__':
    pf = tuple(sys.argv[sys.argv.index('--prefix') + 1].split(',')) if '--prefix' in sys.argv else PREFIXES
    main(rebuild='--rebuild' in sys.argv, prefixes=pf)
