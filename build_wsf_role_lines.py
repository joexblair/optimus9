"""build_wsf_role_lines — the wsf role lines (r, x, m, Mage, b) at timeframes the registry does
not carry. Joe 0908.

WHY THIS EXISTS. build_ws_lines builds what `vw_indicator_configs_live` declares — 70 ws/gcws
names, which covers ws1..ws10, ws12 and ws15 but nothing above that and nothing at ws11, ws13,
ws14, ws16, ws17, ws18. Every question asked of the higher timeframes this session needed lines
that were never registered, and they were built one ad-hoc script at a time. This is those scripts,
merged, so the cache is reproducible from the repo instead of from a scratchpad.

WHAT IT DOES NOT DO. It does not touch the registry. These lines are NOT indicator configs; they
are the wsf ROLE specs (read live from mech_lines) applied at a timeframe. If a timeframe is ever
registered properly, delete its entry here rather than leaving two sources for the same line.

THE SPECS COME FROM mech_lines(db, 'wsf'), not from literals, so a role respec moves these lines
with every other wsf line. The one exception is `r`, which build_momo_landed owns as R_SPEC and
which mech_lines reports identically — asserted at import so the two cannot drift silently.

THE CACHE KEY is build_ws_lines' END_MS / HOURS / WARMUP. Move the window there and this script
rebuilds against the new key on its next run; the old files keep their own names and are not
touched. Nothing here deletes.

WHAT IS IN SCOPE, and what it cost at END 2026-09-08 00:00 / HOURS 40 / WARMUP 1114:
    ws30/45/60/90/120       r, x, m, Mage, b    25 lines
    ws11,12,13,14,16,17,18  r, x, Mage, b       28 lines
    ws6,7,8,9,10,15         Mage, b             12 lines
    = 65 lines. 53 were built by this script's passes on 0908; the other 12 are ws6..ws10 and
    ws15 Mage/b, which the registry already carries and which were already cached.
    Each file is 1,632,960 bars x 8 B = 13.06 MB. A full build of the 53 took 138 s.

A CLEAN RUN PRINTS "to build 0". That is the check that the cache on disk matches this file.

    python3 build_wsf_role_lines.py [--rebuild]
"""
import os
import sys
import time

from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.compute.line_config import KLine, override, mech_lines
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP, TAPE_END
from optimus9.orchestration.rpl_cache import cache_jig_perline, LINE_DIR, _line_key
import build_momo_landed as B

# THE TIMEFRAMES AND THE ROLES EACH ONE NEEDS. Kept as data, not as a loop body, so adding a
# timeframe is one line and the record of what was built stays readable.
# 'r' is the momentum line; 'x' is its fast partner; 'Mage', 'b' and the 85/15 boundary are the
# three x-cross race targets (build_wsf_x_cross.py:15-17); 'm' is the fourth x-cross target Joe
# added 0906.
WANTED = {
    **{tf: ('r', 'x', 'm', 'Mage', 'b') for tf in (30, 45, 60, 90, 120)},
    **{tf: ('r', 'x', 'Mage', 'b') for tf in (11, 12, 13, 14, 16, 17, 18)},
    **{tf: ('Mage', 'b') for tf in (6, 7, 8, 9, 10, 15)},
}


def role_specs(db):
    """{role: (spec_tuple, value_mode)} from the wsf mech, first row per role wins — the same
    read every producer in this chain uses."""
    out = {}
    for g in mech_lines(db, 'wsf'):
        if g['role'] not in out:
            _tf, spec, mode = g['override']
            out[g['role']] = (spec, mode)
    return out


def overrides_for(specs):
    """{name: (tf_seconds, spec, value_mode)} for every (timeframe, role) in WANTED."""
    ovr = {}
    for tf, roles in WANTED.items():
        for role in roles:
            o = override(tf * 60, *specs[role])
            if role == 'r':
                # build_momo_landed owns R_SPEC and every reader in this session built ws{tf}r
                # through it. Assert rather than trust: a silent divergence would put a DIFFERENT
                # ws{tf}r in the cache than every consumer expects.
                # COMPARE THE NORMALISED OVERRIDE, NOT THE RAW SPECS. KLine is a namedtuple in
                # (k_len, rsi, stc, src) order and the mech's spec is a plain tuple in
                # ('k', rsi, stc, k_len, src) order; override() folds both into the second shape.
                # Comparing the two inputs directly reports a difference that does not exist.
                assert o == override(tf * 60, KLine(**B.R_SPEC), specs['r'][1]), (
                    f'ws{tf}r from the wsf role {o} != from build_momo_landed.R_SPEC '
                    f'{override(tf * 60, KLine(**B.R_SPEC), specs["r"][1])}')
            ovr[f'ws{tf}{role}'] = o
    return ovr


def main(rebuild=False):
    t0 = time.time()
    db = DatabaseManager(**get_db_config())
    db.connect()
    row = db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l FROM optimus9_system LIMIT 1',
                     fetch=True)[0]
    pxs = {'src': row['s'], 'len': row['l']}
    ovr = overrides_for(role_specs(db))
    db.disconnect()

    have = set(os.listdir(LINE_DIR)) if os.path.isdir(LINE_DIR) else set()
    todo = sorted(n for n in ovr
                  if rebuild or _line_key(END_MS, HOURS, WARMUP, ovr[n]) + '.npy' not in have)
    print(f'end {TAPE_END:%Y-%m-%d %H:%M} UTC  hours {HOURS}  warmup {WARMUP}  '
          f'span {HOURS + 2 * WARMUP} h', flush=True)
    print(f'  {len(ovr)} role lines across {len(WANTED)} timeframes   to build {len(todo)}',
          flush=True)
    if todo:
        print(f'  {todo}', flush=True)

    cache_jig_perline(END_MS, HOURS, WARMUP, ovr, pxs_cfg=pxs, rebuild=rebuild)

    have = set(os.listdir(LINE_DIR))
    miss = [n for n in ovr if _line_key(END_MS, HOURS, WARMUP, ovr[n]) + '.npy' not in have]
    print(f'  cached {len(ovr) - len(miss)}/{len(ovr)}   missing {miss}   '
          f'in {time.time() - t0:.0f}s', flush=True)
    return 1 if miss else 0


if __name__ == '__main__':
    sys.exit(main(rebuild='--rebuild' in sys.argv))
