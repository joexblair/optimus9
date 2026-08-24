"""build_domtf_x_excursion — one row per x-line excursion, so Joe can pick the estimated times.

Joe 0823: "I need ws27x and ws20x data to pick the estimated times. here are the columns:
--ws27x low reversal <-there's a tool in the jig that produces reversals
--ws27x low oob X ib / --ws27x high ib X oob / --ws27x high reversal / --ws27x high oob X ib
--ws27x low ib x oob / -then print the same columns for ws20x / -print this to a db table for 08-04"

and on the shape, verbatim: "no - one row per excursion. populate the fields with a timestamp".

WHAT AN EXCURSION IS. One trip past a fence and back: the line crosses from in bounds to out of
bounds, turns, and crosses back in. Three timestamps per row. A LOW excursion fills the first three
columns, a HIGH excursion the last three, which is the layout Joe drew.

EVERY PRODUCER IS IMPORTED. Joe 0822: "import, don't duplicate/split/fork".
    ws_strat.states      the per-bar membership and the unbroken run counts. Joe 0823 on the
                         in-bounds-to-out-of-bounds crossing: "ib x oob must exist: it's how the
                         wsf g30_marker is generated" - correct, states() is where it lives.
    Jig.reversal         "boundary-agnostic reversal ... +1 up-turn / -1 down-turn confirmed after
                         `wob` consecutive same-direction steps"

JOE'S THREE VALUES, 0823:
    REV_WOB  6   "arbitrary value for wob and xwob = 6"
    XWOB     6   same
    low reversal = an UP-turn, high reversal = a DOWN-turn. Joe 0823: "on that reading 'low
                 reversal' is an up-turn, 'high reversal' a down-turn" - confirmed as his reading.

CROSSINGS ARE STAMPED AT THE CONFIRMATION BAR - the first bar the crossing is knowable, after the
6-bar hold. That is jig.oob_ib_cross's own `conf` and what build_ws_momo.py stamps. The raw bar is
6 bars earlier by construction. Not a choice: it is the repo's precedent, and conflating the two put
six wsf-exhaust rows wrong on 0822.

MORE THAN ONE REVERSAL. An excursion can contain several turns of the matching sign. The row
carries the FIRST, and `rev_n` says how many there were, so a row that had more than one says so
rather than hiding it.
"""
import sys
import datetime as dt
from datetime import timezone

import numpy as np

from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.compute.line_config import LineStore, BBLine, override
from optimus9.orchestration.rpl_cache import cache_jig_perline
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP
from optimus9.analysis import ws_strat as WS

WIN_FROM = '2026-08-04 00:00:00'
WIN_TO   = '2026-08-05 00:00:00'
LINES    = [27, 20, 14]        # Joe 0823: ws27x, then ws20x. ws14x added 0823 on his ask
X_SPEC   = dict(length=5, mult=0.35, src='close')
REV_WOB  = 6               # KNOB, Joe 0823: "arbitrary value for wob and xwob = 6"
XWOB     = 6               # KNOB, same
WSF_LINES = ([f'{g}{s}' for g in ('gcws15', 'gcws30') for s in ('b', 'm', 'Mage', 'r')]
             + [f'ws1{s}' for s in ('b', 'm', 'Mage', 'r')])

DDL = '''CREATE TABLE IF NOT EXISTS domtf_x_excursion (
    dxe_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    dxe_knobs   VARCHAR(96)  NOT NULL,  -- every knob that changes a row, one string
    dxe_line    VARCHAR(8)   NOT NULL,  -- ws27x | ws20x
    dxe_side    VARCHAR(4)   NOT NULL,  -- low | high
    dxe_seq     INT          NOT NULL,  -- position within this line, 1-based, chronological
    -- Joe's layout: a LOW excursion fills the first three, a HIGH excursion the last three
    dxe_lo_ibxoob  DATETIME,            -- in bounds crossed to LOW out of bounds, confirmed
    dxe_lo_rev     DATETIME,            -- the low reversal - an UP-turn - inside the excursion
    dxe_lo_oobxib  DATETIME,            -- LOW out of bounds crossed back to in bounds, confirmed
    dxe_hi_ibxoob  DATETIME,            -- in bounds crossed to HIGH out of bounds, confirmed
    dxe_hi_rev     DATETIME,            -- the high reversal - a DOWN-turn - inside the excursion
    dxe_hi_oobxib  DATETIME,            -- HIGH out of bounds crossed back to in bounds, confirmed
    dxe_rev_n   SMALLINT NOT NULL DEFAULT 0,  -- matching turns inside the excursion. >1 = the row
    --   carries the first of several. Declared so a pick is never silent
    dxe_open    TINYINT  NOT NULL DEFAULT 0,  -- 1 = still out of bounds when the window ended
    UNIQUE KEY uq_dxe (dxe_knobs, dxe_line, dxe_seq),
    KEY k_side (dxe_side))'''

COLS = ['dxe_knobs', 'dxe_line', 'dxe_side', 'dxe_seq',
        'dxe_lo_ibxoob', 'dxe_lo_rev', 'dxe_lo_oobxib',
        'dxe_hi_ibxoob', 'dxe_hi_rev', 'dxe_hi_oobxib', 'dxe_rev_n', 'dxe_open']


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    sysr = db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l, hi_boundary h, '
                      'lo_boundary lo FROM optimus9_system WHERE sys_pk=1', fetch=True)[0]
    HI, LO = float(sysr['h']), float(sysr['lo'])
    ls = LineStore(db)
    ovr = {n: (*ls.resolve(n), ls.value_mode(n)) for n in set(WSF_LINES + list(WS.LINES))}
    for tf in LINES:
        ovr[f'x{tf}'] = override(tf * 60, BBLine(**X_SPEC), 'emerging')
    J = cache_jig_perline(END_MS, HOURS, WARMUP, ovr,
                          pxs_cfg={'src': sysr['s'], 'len': sysr['l']}, rebuild=False)
    ts = np.asarray(J.ts)
    i0 = int(np.searchsorted(ts, int(dt.datetime.fromisoformat(WIN_FROM)
                                     .replace(tzinfo=timezone.utc).timestamp() * 1000)))
    i1 = int(np.searchsorted(ts, int(dt.datetime.fromisoformat(WIN_TO)
                                     .replace(tzinfo=timezone.utc).timestamp() * 1000)))
    u = lambda k: dt.datetime.fromtimestamp(int(ts[k]) / 1000, timezone.utc
                                            ).strftime('%Y-%m-%d %H:%M:%S')
    knobs = f'w{WIN_FROM[5:7]}{WIN_FROM[8:10]}_hi{HI:.0f}_lo{LO:.0f}_rw{REV_WOB}_xw{XWOB}'
    print(f'  window {WIN_FROM} -> {WIN_TO}   fences {HI:.0f}/{LO:.0f}   '
          f'reversal wob {REV_WOB}   crossing xwob {XWOB}', flush=True)

    db.execute(DDL)
    had = db.execute('SELECT COUNT(*) c FROM domtf_x_excursion WHERE dxe_knobs=%s',
                     (knobs,), fetch=True)[0]['c']
    if had:
        print(f'  deleting {had} rows already stored at these knobs', flush=True)
        db.execute('DELETE FROM domtf_x_excursion WHERE dxe_knobs=%s', (knobs,))

    rows = []
    for tf in LINES:
        name = f'ws{tf}x'
        v = np.asarray(J.W.line(f'x{tf}'), float)
        S = WS.states(v, HI, LO, XWOB)                 # THE producer. Joe 0823: ib x oob lives here
        rev = np.asarray(J.causal.reversal(v, REV_WOB))
        # a crossing is CONFIRMED on the rising edge of its run reaching XWOB
        def conf_edge(run):
            held = np.asarray(run) >= XWOB
            return held & ~np.r_[False, held[:-1]]
        into = {-1: conf_edge(S['lo_run']), +1: conf_edge(S['hi_run'])}
        back = conf_edge(S['ib_run'])
        seq = 0
        for side in (-1, +1):
            for a in np.flatnonzero(into[side]):
                if not (i0 <= a <= i1):
                    continue
                b = next((k for k in range(a + 1, i1 + 1) if back[k]), None)
                end = b if b is not None else i1
                # the matching turn: an UP-turn inside a LOW excursion, a DOWN-turn inside a HIGH one
                want = +1 if side < 0 else -1
                turns = [k for k in range(a, end + 1) if rev[k] == want]
                seq += 1
                r = [knobs, name, 'low' if side < 0 else 'high', seq,
                     None, None, None, None, None, None, len(turns), int(b is None)]
                base = 4 if side < 0 else 7
                r[base] = u(a)
                r[base + 1] = u(turns[0]) if turns else None
                r[base + 2] = u(b) if b is not None else None
                rows.append(tuple(r))
        # renumber chronologically within the line
    out = []
    for tf in LINES:
        name = f'ws{tf}x'
        mine = [r for r in rows if r[1] == name]
        mine.sort(key=lambda r: (r[4] or r[7]))
        for n, r in enumerate(mine, 1):
            out.append(tuple(r[:3]) + (n,) + tuple(r[4:]))
    db.executemany(f'INSERT INTO domtf_x_excursion ({",".join(COLS)}) VALUES '
                   f'({",".join(["%s"] * len(COLS))})', out)
    for tf in LINES:
        n = sum(1 for r in out if r[1] == f'ws{tf}x')
        lo = sum(1 for r in out if r[1] == f'ws{tf}x' and r[2] == 'low')
        print(f'  ws{tf}x : {n} excursions   low {lo}   high {n - lo}', flush=True)
    print(f'\n  domtf_x_excursion : {len(out)} rows at knobs {knobs}', flush=True)
    db.disconnect()
    return 0


if __name__ == '__main__':
    sys.exit(main())
