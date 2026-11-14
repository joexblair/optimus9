"""apply_gcws45_indicator_configs — register gcws45b and gcws45r, and build them into the line cache. Joe 1114.

Joe 1114, verbatim: *"build a gcws45b and gcws45r (45sec) lines and add them to the line cache"*.

THE CONFIG IS THE FAMILY'S, READ FROM THE DB, not written here. The live gcws15b and gcws30b rows carry
one config, the live gcws15r and gcws30r rows another; this copies that config onto the 45 s timeframe
and refuses if the 15 s and 30 s rows ever disagree, because then there is no one family config to copy.
As read 1114:

    gcws45b   bb 49|0.95|close, emerging, 85/15    = gcws15b / gcws30b (their 2026-08-06 rows)
    gcws45r   k  7|5|8|close,   emerging, 85/15    = gcws15r / gcws30r (their 2026-08-05 rows)

THE 45 s TIMEFRAME ROW ALREADY EXISTS: indicator_timeframes itf_pk 18, label '45', 45 s - xm45m/M/r
use it since 07-10. It is pinned by (label, seconds), as apply_ws_indicator_configs.py does. Nothing
is added to indicator_timeframes, indicator_series or indicator_lines.

THE BAR GRID. line_reader anchors bars on UTC midnight. 45 s divides a day (1,920 bars), so the bars
open at 00:00:00, 00:00:45, 00:01:30, 00:02:15, 00:03:00 every day, and the epoch grid is the same one.

LIVE AFTER 2026-11-14 00:00:00, the day it was registered. The only reader of ic_live_after_dt is the
view's `<= now()` filter.

THE CACHE. Only these two lines are built. cache_jig_perline builds the names it is handed that have
no file, so no cached line is rebuilt, and the tape must already be on disk or this refuses rather
than write a new one. The tape is LG_TAPE_END, defaulting to 2026-10-05 - the tape ln.py and the v4
pages read - and NOT build_ws_lines' own 2026-09-30 default.

IDEMPOTENT: INSERT IGNORE on the ic unique key (is, itf, il, live_after); a second run writes nothing
and builds nothing.

    python3 apply_gcws45_indicator_configs.py [--dry]
"""
import datetime as dt
import os
import sys

os.environ.setdefault('LG_TAPE_END', '2026-10-05')     # BEFORE build_ws_lines reads it at import

import numpy as np

from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP, TAPE_END, overrides
from optimus9.orchestration.rpl_cache import LINE_DIR, TAPE_DIR, _line_key, _tape_key, cache_jig_perline

LIVE_AFTER = '2026-11-14 00:00:00'
TF_LABEL, TF_SECONDS = '45', 45
SUFFIXES = ('b', 'r')
SAME = ('ic_line_type', 'ic_src', 'ic_high_boundary', 'ic_low_boundary', 'ic_bb_len', 'ic_bb_mult',
        'ic_k_len', 'ic_rsi_len', 'ic_stc_len', 'ic_ivm_pk', 'ic_wobble')


def main(dry=False):
    db = DatabaseManager(**get_db_config()); db.connect()

    # 1. the family config per suffix, from the live 15 s and 30 s rows
    fam = {}
    for suf in SUFFIXES:
        rows = db.execute('SELECT v.ind_name, ic.* FROM vw_indicator_configs_live v '
                          'JOIN indicator_configs ic ON ic.ic_pk = v.ic_pk '
                          'WHERE v.ind_name IN (%s, %s) ORDER BY v.itf_seconds',
                          ('gcws15' + suf, 'gcws30' + suf), fetch=True)
        assert len(rows) == 2, 'gcws15%s / gcws30%s: %d live rows, want 2' % (suf, suf, len(rows))
        a, b = rows
        diff = [k for k in SAME if a[k] != b[k]]
        assert not diff, 'gcws15%s and gcws30%s disagree on %s - no one family config' % (suf, suf, diff)
        fam[suf] = b
    itf = db.execute('SELECT itf_pk FROM indicator_timeframes WHERE itf_label = %s AND itf_seconds = %s',
                     (TF_LABEL, TF_SECONDS), fetch=True)
    assert len(itf) == 1, '%d timeframe rows for (%s, %d s), want 1' % (len(itf), TF_LABEL, TF_SECONDS)
    itf = itf[0]['itf_pk']

    names = ['gcws%s%s' % (TF_LABEL, s) for s in SUFFIXES]
    rows = [(fam[s]['ic_is_pk'], itf, fam[s]['ic_il_pk'], fam[s]['ic_line_type'], LIVE_AFTER,
             fam[s]['ic_src'], fam[s]['ic_high_boundary'], fam[s]['ic_low_boundary'], fam[s]['ic_bb_len'],
             fam[s]['ic_bb_mult'], fam[s]['ic_k_len'], fam[s]['ic_rsi_len'], fam[s]['ic_stc_len'],
             fam[s]['ic_ivm_pk'], fam[s]['ic_wobble']) for s in SUFFIXES]
    for n, r in zip(names, rows):
        print('offer %-8s itf_pk %d  %s' % (n, itf, r))
    if dry:
        db.disconnect()
        print('--dry: nothing written, nothing built')
        return
    w = db.executemany(
        'INSERT IGNORE INTO indicator_configs (ic_is_pk,ic_itf_pk,ic_il_pk,ic_line_type,ic_live_after_dt,'
        'ic_src,ic_high_boundary,ic_low_boundary,ic_bb_len,ic_bb_mult,ic_k_len,ic_rsi_len,ic_stc_len,'
        'ic_ivm_pk,ic_wobble) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', rows)
    print('indicator_configs: %d rows offered, %s written' % (len(rows), w))

    # 2. read back through LineStore, the resolver every builder uses
    ovr = overrides(db, names)
    ref = overrides(db, ['gcws30' + s for s in SUFFIXES])
    for n, s in zip(names, SUFFIXES):
        assert ovr[n][0] == TF_SECONDS, (n, ovr[n])
        assert ovr[n][1:] == ref['gcws30' + s][1:], (n, ovr[n], ref['gcws30' + s])
        print('resolves %-8s %s' % (n, ovr[n]))
    sy = db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l FROM optimus9_system WHERE sys_pk=1',
                    fetch=True)[0]
    db.disconnect()

    # 3. build the two into the cache, on a tape that is already on disk
    pxs = {'src': sy['s'], 'len': sy['l']}
    tp = os.path.join(TAPE_DIR, _tape_key(END_MS, HOURS, WARMUP, pxs) + '.npz')
    assert os.path.exists(tp), 'no tape on disk for %s - refusing to build one' % TAPE_END
    lp = {n: os.path.join(LINE_DIR, _line_key(END_MS, HOURS, WARMUP, ovr[n]) + '.npy') for n in names}
    for n in names:
        print('%-8s %s %s' % (n, os.path.basename(lp[n]), 'on disk' if os.path.exists(lp[n]) else 'to build'))
    J = cache_jig_perline(END_MS, HOURS, WARMUP, ovr, pxs_cfg=pxs)
    ts = np.asarray(J.ts)
    u = lambda t: dt.datetime.fromtimestamp(int(t) / 1000, dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    print('tape end %s, %s -> %s, %d bars' % (TAPE_END.strftime('%Y-%m-%d %H:%M'), u(ts[0]), u(ts[-1]), len(ts)))
    for n in names:
        a = np.asarray(J.W.line(n), float); f = np.isfinite(a)
        print('%-8s %d bars, %d finite, min %.2f, median %.2f, max %.2f, first finite %s'
              % (n, len(a), int(f.sum()), np.nanmin(a), np.nanmedian(a), np.nanmax(a), u(ts[int(np.argmax(f))])))


if __name__ == '__main__':
    main(dry='--dry' in sys.argv)
