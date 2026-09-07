"""pxs_mode - the one switch that puts a producer on the smoothed price instead of close.

WHY IT IS ONE FILE. Joe 0905: "this is experimental, so you should be able to easily flip
everything back to src=`close` if the pxs results are not favourable". Seven producers have to
move together and move back together. A flag in each of them would be seven things to remember;
this is one.

HOW A PRODUCER USES IT

    import pxs_mode as PX
    ...
    db.execute(DDL.replace('wsf_line_bar', PX.t('wsf_line_bar')))
    rows = db.execute(f'SELECT ... FROM {PX.t("ws_line_bar")} WHERE ...')

`PX.ON` is False unless --pxs4 is on the command line, and every t() then returns the name
unchanged. That is the flip back: drop the flag and the producer is byte-for-byte the close
build. NO BRANCH WRITES A CLOSE TABLE WHEN ON, AND NONE WRITES A pxs4 TABLE WHEN OFF.

THE TABLE NAMES follow the one name Joe gave, `wsf_pxs4_event_mark` (0905): `pxs4_` is inserted
after the leading ws / wsf token. So wsf_line_bar -> wsf_pxs4_line_bar, ws_line_bar ->
ws_pxs4_line_bar. t() applies that rule rather than a table carrying a hand-written twin name.

THE WINDOW AND THE FOLDERS live here too, so build_pxs_line_cache and every consumer read one
definition. build_pxs_line_cache imports these; nothing here imports it, which is what keeps the
import graph acyclic - build_ws_line_bar imports this module, and build_pxs_line_cache imports
build_ws_line_bar.

    Joe 0904: "we only need 08-04 to 08-06 for now, plus the warmup"
    Joe 0905: "increase the line-cache to the end of 08-06"
"""
import os
import sys
import datetime as dt
from datetime import timezone

from optimus9.orchestration import rpl_cache
from optimus9.orchestration.build_ws_lines import WARMUP as _WARMUP

# THE WINDOW. END 08-07 00:00 so the tape carries 08-06 23:59:55; HOURS 72 puts 08-04 00:00 at
# the start of the live span; WARMUP is the project's own 1114 hours, unchanged.
# EXTENDED 0905 so 08-06 IS A FULL DAY. This codebase's convention is that a day runs 00:00:00
# through the NEXT day's 00:00:00 inclusive - 17,281 rows. An END of 08-07 00:00 gave a last bar of
# 08-06 23:59:55, so 08-06 came out at 17,280 and every downstream producer that stacks or indexes
# a day's array failed on it. END 08-08 00:00 is the minimum that makes Joe's "08-04 to 08-06 (full
# days)" true. The old 72-hour line files keep their own filenames - _line_key carries the window -
# so the flip-report rows banked against them are still reproducible.
PXS_END = dt.datetime(2026, 8, 8, 0, 0, tzinfo=timezone.utc)
PXS_END_MS = int(PXS_END.timestamp() * 1000)
PXS_HOURS = 96
PXS_WARMUP = _WARMUP

DEMA = 4                       # Joe 0905 "rebuild the line-cache using dema=4"

# THE MOMENTUM BANK THE pxs4 CHAIN BUILDS AT. Joe 0906 chose option (b): build the pxs4 line bar
# at the knobs the WALK filters on, so the only difference between the pxs4 and close event sets
# is the price. The walk's SIG hard-codes kw4 / r2 0.5 / slope 1 - the values before Joe's 0903
# "bake it in" - and momo_config held only version 1 (kw6 / r2 0.7 / slope 1.2). Version 0 was
# ADDED 0906 carrying the pre-0903 numbers; it is not live, because momo_bank picks the HIGHEST
# version whose live-after date has passed, and that is still 1.
BANK_VERSION = 0
TAG = f'pxs{DEMA}'             # the token inserted into a table name, and the row marker


def dema_arg(argv=None):
    """--dema N, or None. Named separately so build_pxs_line_cache can build any dema."""
    a = argv if argv is not None else sys.argv
    return int(a[a.index('--dema') + 1]) if '--dema' in a else None


def dirs(dema):
    """ONE FOLDER PER DEMA. _line_key carries neither a source nor a dema term, so two dema values
    write the SAME filename for the same spec - that is how the 0904 dema test produced a false
    null. The folder is the only thing keeping them apart."""
    return (os.path.join(rpl_cache.CACHE_DIR, f'lines_pxs_d{dema}'),
            os.path.join(rpl_cache.CACHE_DIR, f'tape_pxs_d{dema}'))


ON = '--pxs4' in sys.argv
LINE_DIR, TAPE_DIR = dirs(DEMA)


def t(name):
    """The table this producer should read or write. Unchanged unless --pxs4 is on.

    ws_line_bar   -> ws_pxs4_line_bar
    wsf_x_cross   -> wsf_pxs4_x_cross
    wsf_event_mark-> wsf_pxs4_event_mark      the name Joe gave, which sets the rule
    """
    if not ON:
        return name
    for head in ('wsf_', 'ws_'):
        if name.startswith(head):
            return f'{head}{TAG}_{name[len(head):]}'
    raise ValueError(f'{name!r} does not start with ws_ or wsf_ - no pxs4 name rule for it')


_ALL = ('ws_line_bar', 'ws_line_cross', 'ws_fin_9of12', 'ws_fin_walk', 'ws_fin_tagshrink',
        'wsf_line_bar', 'wsf_bar_tf', 'wsf_x_cross', 'wsf_ingredient', 'wsf_exhaust_event',
        'wsf_event_ingredient', 'wsf_event_signal', 'wsf_trade', 'wsf_event_mark',
        'v_ws_fin_walk')


# FOREIGN KEY AND INDEX NAMES ARE SCHEMA-GLOBAL IN MySQL, not table-scoped. A pxs4 table
# declaring `CONSTRAINT fk_wei_event` collides with the close table's constraint of the same name:
# 1826 (HY000) Duplicate foreign key constraint name. Measured 0905 on the walk's DDL.
_CONSTRAINTS = ('fk_wei_event', 'fk_wei_ingredient', 'fk_wes_event', 'fk_wtr_open', 'fk_wtr_close')


def sql(text):
    """Rewrite every table, view and constraint name in a SQL string. For DDL held as a module
    constant, where wrapping each name in t() would mean rewriting the whole statement. Longest
    name first so ws_fin_9of12 is not half-matched by a shorter prefix."""
    if not ON:
        return text
    for n in sorted(_ALL, key=len, reverse=True):
        if n.startswith('v_'):
            text = text.replace(n, f'v_{TAG}_' + n[2:])
        else:
            text = text.replace(n, t(n))
    for c in sorted(_CONSTRAINTS, key=len, reverse=True):
        text = text.replace(c, f'{c}_{TAG}')
    return text


class _DB:
    """A DatabaseManager whose SQL goes through sql() first, so a producer routes every table name
    with one line instead of a wrapper at every call site. Attribute lookups fall through, so
    connect / disconnect / anything else behave normally."""

    def __init__(self, db):
        self._db = db

    def execute(self, s, *a, **k):
        return self._db.execute(sql(s), *a, **k)

    def executemany(self, s, rows, *a, **k):
        return self._db.executemany(sql(s), rows, *a, **k)

    def __getattr__(self, n):
        return getattr(self._db, n)


def wrap(db):
    """db = PX.wrap(db) right after connect(). A no-op in close mode."""
    return _DB(db) if ON else db


def load_lines(src, ovr):
    """(ts, get) for the pxs cache. `get(name)` returns that line's array. `ovr` must be built from
    the same specs build_pxs_line_cache used, or the filename will not exist."""
    import numpy as np
    from optimus9.orchestration.rpl_cache import _line_key, _tape_key
    ts = np.load(os.path.join(TAPE_DIR, _tape_key(PXS_END_MS, PXS_HOURS, PXS_WARMUP,
                 {'src': src, 'len': DEMA}) + '.npz'))['__ts__']
    def get(name):
        return np.load(os.path.join(LINE_DIR, _line_key(PXS_END_MS, PXS_HOURS, PXS_WARMUP,
                                                        ovr[name]) + '.npy'))
    return ts, get


def pxs_base(db, src=None, dema=None):
    """(base, ts, px) where base's `close` column IS the smoothed price. The one definition of the
    swap - build_pxs_line_cache and every producer that needs the frame rather than the lines call
    this, so the two cannot drift."""
    import numpy as np
    import bias_machine as bm
    from optimus9.orchestration import rpl_cache as _rc
    if src is None:
        src = db.execute('SELECT pxsmooth_dema_src s FROM optimus9_system WHERE sys_pk=1',
                         fetch=True)[0]['s']
    W0 = bm.BiasWindow(db, PXS_END_MS, lookback=PXS_HOURS + PXS_WARMUP, warmup=PXS_WARMUP,
                       line_overrides={})
    base = W0.base.copy()
    evt = base['volume'].to_numpy(dtype=float) > 0
    base['close'] = _rc._px_smooth_evt(base, evt, src, dema or DEMA)
    return base, np.asarray(W0.ts), np.asarray(W0.px, float)


class _Frame:
    """Stands in for the jig where a producer only needs .base and .ts. A context manager so the
    `with` block it replaces keeps its shape."""

    def __init__(self, base, ts):
        self.base, self.ts = base, ts

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def frame(db, src=None):
    """The pxs base frame, wrapped so `with PX.frame(db) as j:` mirrors `with Jig(...) as j:`."""
    base, ts, _px = pxs_base(db, src)
    return _Frame(base, ts)


class _LineReader:
    """Stands in for the jig's W where a producer passes the whole window object down. Only .line()
    is used by wsf_qualify / ws_fin_9of12 - checked, not assumed - so only .line() is provided."""

    def __init__(self, get):
        self._get = get

    def line(self, name):
        return self._get(name)


def line_reader(src, ovr):
    """(ts, W) for the pxs cache, where W.line(name) matches the jig's reader surface."""
    ts, get = load_lines(src, ovr)
    return ts, _LineReader(get)


def banner():
    """One line every pxs4 producer prints, so a run can never be mistaken for a close run."""
    return (f'  PXS4 MODE: lines from {os.path.basename(LINE_DIR)}, tables prefixed {TAG}, '
            f'window {PXS_END:%Y-%m-%d %H:%M} hours {PXS_HOURS} warmup {PXS_WARMUP}'
            if ON else '  close mode: the normal tables and the close line cache')
