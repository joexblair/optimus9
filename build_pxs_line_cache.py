"""build_pxs_line_cache - every wsf line rebuilt on the SMOOTHED price instead of close.

WHY. Joe 0904, after the dema 2 vs 4 test showed the lines never move: "can you build a
wsf_pxs_momo_flip_rep table that's created by all lines using src=pxs instead of src=close?" and
then "agreed on option (b). for now, build the pxs-based line cache in its own folder. we only
need 08-04 to 08-06 for now, plus the warmup".

OPTION (b), HIS CHOICE, AND WHY IT NEEDS NO SHARED CODE CHANGE. `pxs` is not a source.
IndicatorComputer.build_source (indicator_computer.py:159) accepts close, open, high, low, hl2,
hlc3, ohlc4, hlcc4 and raises on anything else. Every wsf line already names `close` - measured
0904, 70 of 70 ws/gcws lines. So swapping the base frame's `close` COLUMN for the smoothed price
makes every one of those lines read pxs, with the spec, the source string and every producer
untouched. Option (a) - teaching build_source a new source - would have reached all 175 live
lines, 75 of which are not ws lines at all.

THE INJECTION POINT IS THE SANCTIONED ONE. bias_machine.py:111 takes base_cache=(base, ts, px),
described there as the "sweep hook: reuse a pre-loaded base tape". sweep_eval.py:25 already uses
it. Nothing here reaches past that hook.

THE SPECS ARE NOT COPIED. GROUPS and the five shared specs are imported from build_ws_line_bar,
which reads them from mech_line_config's wsf rows. A second copy here is how report_domtf_walk
forked from momo_g_why; this file will not repeat that.

ITS OWN FOLDER, Joe 0904. .rpl_cache/lines_pxs and .rpl_cache/tape_pxs, beside the close-based
cache and never overlapping it. _line_key carries no source term, so a shared folder would have
let the pxs lines overwrite the close lines under the same filename - measured 0904, that is
exactly how the first dema test produced a false null.

THE WINDOW, Joe 0904: "we only need 08-04 to 08-06 for now, plus the warmup". END is 08-06 00:00
and HOURS is 48, which puts 08-04 00:00 at the start of the live span. WARMUP is left at the
project's 1114 hours - his "plus the warmup".

THE DEMA. Read live from optimus9_system, close/2 today. Joe named `pxs`, and that is what pxs
means; he has not asked for a different length here.

WRITES NOTHING to any database table and never touches the close-based cache.

    python3 build_pxs_line_cache.py            build it
    python3 build_pxs_line_cache.py --show     what is on disk
"""
import os
import sys
import time
import datetime as dt
from datetime import timezone

import numpy as np

from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.compute.line_config import mech_lines, override
from optimus9.compute.indicator_computer import IndicatorComputer as IC
from optimus9.orchestration import rpl_cache
from optimus9.orchestration.rpl_cache import _line_key, _tape_key
from optimus9.orchestration.build_ws_lines import WARMUP
# build_ws_line_bar parses sys.argv[1] AS A DATE at module level, so importing it from a script
# that carries its own flags blows up on the flag. Blank argv across the import only.
_argv = sys.argv
sys.argv = _argv[:1]
from build_ws_line_bar import GROUPS, KINDS
sys.argv = _argv
import bias_machine as bm

# THE WINDOW. Joe 0905: "increase the line-cache to the end of 08-06". END is 08-07 00:00 so the
# tape carries 08-06 23:59:55, and HOURS 72 puts 08-04 00:00 at the start of the live span.
import pxs_mode as _PXM         # one definition of the window and the folder rule
PXS_END, PXS_END_MS = _PXM.PXS_END, _PXM.PXS_END_MS
PXS_HOURS, PXS_WARMUP = _PXM.PXS_HOURS, _PXM.PXS_WARMUP
dema_arg, dirs = _PXM.dema_arg, _PXM.dirs

# ONE FOLDER PER DEMA. Joe 0905: "rebuild the line-cache using dema=4". _line_key carries neither
# a source nor a dema term, so two dema values write the SAME filename for the same spec - that is
# how the 0904 dema test produced a false null. The folder is the only thing keeping them apart.

BATCH_MAX = rpl_cache.BATCH_MAX


def specs(db):
    """The five shared wsf specs at every group, exactly as build_ws_line_bar builds them."""
    SPEC = {}
    for grp in mech_lines(db, 'wsf'):
        if grp['role'] not in SPEC:
            _tf, sp, mode = grp['override']
            SPEC[grp['role']] = (sp, mode)
    missing = [k for k in KINDS if k not in SPEC]
    if missing:
        raise SystemExit(f'mech_line_config has no wsf row for {missing}')
    ovr = {}
    for g, tf_s in GROUPS:
        for k in KINDS:
            sp, mode = SPEC[k]
            ovr[f'{g}{k}'] = override(tf_s, sp, mode)
    return SPEC, ovr


def show(LINE_DIR, TAPE_DIR):
    for d, what in ((LINE_DIR, 'lines'), (TAPE_DIR, 'tape')):
        n = len(os.listdir(d)) if os.path.isdir(d) else 0
        sz = sum(os.path.getsize(os.path.join(d, f)) for f in os.listdir(d)) / 1e6 if n else 0
        print(f'  {what:<6} {d}   {n} files   {sz:,.0f} MB')


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    sysr = db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l FROM optimus9_system '
                      'WHERE sys_pk=1', fetch=True)[0]
    dema = dema_arg()
    if dema is None:
        dema = int(sysr['l'])       # the live value when --dema is not given
    LINE_DIR, TAPE_DIR = dirs(dema)
    if '--show' in sys.argv:
        show(LINE_DIR, TAPE_DIR); db.disconnect(); return 0
    os.makedirs(LINE_DIR, exist_ok=True); os.makedirs(TAPE_DIR, exist_ok=True)
    assert f'lines_pxs_d{dema}' in LINE_DIR and f'tape_pxs_d{dema}' in TAPE_DIR, \
        'refusing to write anywhere but this dema\'s pxs folders'
    pxs_cfg = {'src': sysr['s'], 'len': dema}
    SPEC, ovr = specs(db)
    print(f'  window   end {PXS_END:%Y-%m-%d %H:%M} UTC   hours {PXS_HOURS}   warmup {PXS_WARMUP}')
    print(f'  pxs      dema src {pxs_cfg["src"]!r} len {pxs_cfg["len"]}   (live optimus9_system)')
    print('  the five shared wsf specs, read from mech_line_config:')
    for k in KINDS:
        print(f'    {k:<5} {SPEC[k][0]}   value mode {SPEC[k][1]}')
    print(f'  {len(ovr)} lines over {len(GROUPS)} groups', flush=True)

    # THE BASE, LOADED ONCE, THEN ITS close COLUMN REPLACED BY THE SMOOTHED PRICE.
    t0 = time.time()
    W0 = bm.BiasWindow(db, PXS_END_MS, lookback=PXS_HOURS + PXS_WARMUP, warmup=PXS_WARMUP,
                       line_overrides={})
    base = W0.base.copy()
    evt = base['volume'].to_numpy(dtype=float) > 0
    pxs = rpl_cache._px_smooth_evt(base, evt, pxs_cfg['src'], pxs_cfg['len'])
    close_before = base['close'].to_numpy(dtype=float).copy()
    base['close'] = pxs
    moved = int(np.count_nonzero(close_before != pxs))
    print(f'  base loaded in {time.time()-t0:.0f}s   {len(base):,} bars   '
          f'close replaced by pxs on {moved:,} of {len(base):,} bars   '
          f'max abs move {np.abs(pxs - close_before).max():.8f}', flush=True)
    ts0 = np.asarray(W0.ts)

    tp = os.path.join(TAPE_DIR, _tape_key(PXS_END_MS, PXS_HOURS, PXS_WARMUP, pxs_cfg) + '.npz')
    np.savez(tp, __ts__=np.asarray(ts0, np.int64), __evt__=evt, __pxs__=pxs)
    print(f'  tape written {os.path.basename(tp)}', flush=True)

    names = list(ovr)
    todo = [n for n in names
            if not os.path.exists(os.path.join(LINE_DIR, _line_key(PXS_END_MS, PXS_HOURS,
                                                                   PXS_WARMUP, ovr[n]) + '.npy'))]
    print(f'  {len(todo)} of {len(names)} lines to build', flush=True)
    for bi in range(0, len(todo), BATCH_MAX):
        batch = todo[bi:bi + BATCH_MAX]
        t1 = time.time()
        W = bm.BiasWindow(db, PXS_END_MS, lookback=PXS_HOURS + PXS_WARMUP, warmup=PXS_WARMUP,
                          line_overrides={n: ovr[n] for n in batch},
                          base_cache=(base, ts0, np.asarray(W0.px, float)))
        for n in batch:
            p = os.path.join(LINE_DIR, _line_key(PXS_END_MS, PXS_HOURS, PXS_WARMUP, ovr[n]) + '.npy')
            tmp = p + f'.{os.getpid()}.tmp'
            np.save(tmp, np.asarray(W.line(n), float))
            os.replace(tmp + ('.npy' if not tmp.endswith('.npy') else ''), p)
        print(f'    batch {bi//BATCH_MAX + 1}: {len(batch)} lines in {time.time()-t1:.0f}s',
              flush=True)
    db.disconnect()
    u = lambda t: dt.datetime.fromtimestamp(int(t)/1000, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    print(f'  tape {u(ts0[0])} -> {u(ts0[-1])}, {len(ts0):,} bars')
    show(LINE_DIR, TAPE_DIR)
    return 0


if __name__ == '__main__':
    sys.exit(main())
