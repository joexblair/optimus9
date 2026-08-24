"""build_wsf_line_bar — the per-bar measurement bank for the ws-finisher lines, 08-04.

Joe 0818: "create durable data for 08-04. I'll be asking a lot of data related questions, so it's
important for tables built with everything you'll need to respond quickly to my requests".

ONE ROW PER LINE, PER DIRECTION, PER BAR. ws1r to ws8r, read both up and down, every 5-second bar
of the 08-04 window. 8 x 2 x 17,281 = 276,496 rows.

WHY BOTH DIRECTIONS. Joe 0818 settled that a wsf state row holds one line, one state, one
direction — but which direction a line is read in between wsf9of12 signals is still open. Storing
both means a direction question never forces a rebuild.

WHAT IS NOT IN HERE. No wsf-momoc and no wsf-exhaust column. wsf-momoc needs the direction rule
and wsf-exhaust needs the reverse, and neither is settled. This table stores the INGREDIENTS -
the stall, the verdicts, the bend, the boundary - so any rule can be applied later by query
instead of by rebuild.

CURL IS UNGATED HERE. Joe 0818: "wsf states are a continuous flow, to be queried when wsf9of12
fires. for this reason, curl cannot be gated". `wflb_ungated` is the wsf verdict. `wflb_gated` is
stored alongside for comparison only - it is what domTF uses, not what wsf uses.

THE STALL LATTICE is momo_window(K_WINDOW x tf) at MOMO_FIXED_SAMPLES 21, which is what
build_ws_fin.py runs. The wsf sampling width is Joe's held task #60; it is in the unique key, so a
run at a different width lands alongside instead of on top.
"""
import sys
import datetime as dt
from datetime import timezone
import os

import numpy as np

from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.compute.line_config import KLine, override
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP
from optimus9.orchestration.rpl_cache import LINE_DIR, TAPE_DIR, _line_key, _tape_key
from optimus9.compute import momo_gated as MG
from optimus9.compute.momo_gated import momo_g_why, momo_window
from optimus9.compute import momo_core as MC
from optimus9.analysis.jig import _stall_rows
import build_momo_landed as B

WIN_FROM = '2026-08-04 00:00:00'
WIN_TO   = '2026-08-05 00:00:00'
TFS      = list(range(1, 9))     # ws1r to ws8r. The spec: both states apply to ws{tf}r, TF1 to TF8
DRS      = (+1, -1)              # read upward and read downward
STALL_N  = 6                     # lattice samples in a row with no new extreme. build_ws_fin.py's value
MOMO_FENCE_R = 17
# momo-fence-r, Joe 0820: "create a new fence: momo-fence-r  100-{knob:17}". So the band is
# 100 - 17 = 83 at the top and 17 at the bottom. A line LEAVES it by going at or past 83 on an
# upward read, or at or below 17 on a downward read - same side as the line is read, matching every
# other test on this path.
# IT IS NOT GLOBAL. Joe 0820: "I don't want it to be global". The 85/15 fence in optimus9_system is
# untouched and `wflb_oob` still reports against it. This knob belongs to the ws-finisher's momentum
# rule alone, and it is in the unique key.
MOMO_XWOB = 4
# xwob, Joe 0821: "add an {knob:4} xwob to the fence exit and recreate the data". Joe's own knob,
# already defined in build_momo_landed.py:51 as "5 s pxs bars the tagged line must hold outside the
# fence". 4 bars = 20 seconds.
#
# WHY. Measured on 08-04: 627 fence exits on momentum-carrying lines, of which 78 (12.4%) lasted a
# SINGLE bar and 179 (28.5%) lasted 15 seconds or less. ws7r crossed the 83 edge six times between
# 01:52 and 01:57; five reverted within 65 s and the sixth, at 01:57:15, held 765 s. Without a hold
# the walk fired on the 5-second flicker at 01:53:15 and latched, swallowing the real exit.
#
# THE SEMANTICS ARE jig.momo_landed's, not a fork: the run counts CONSECUTIVE bars outside, and it
# only counts if the line was INSIDE on the bar before it went out. A line already outside does not
# land on that standing position - it waits for a return inside and a fresh exit.
MOMO_KILL = 'state'
# Joe 0820: "IF a momentum-true r line crosses into oob or stalls THEN it's momentum = false (or
# none). this needs to show up in the `verdict` column."
#   'state'  the line IS out of bounds on its side, or IS stalled -> the verdict is none.
#   'moment' only the bar the line crossed, or the bar the stall began -> the verdict is none.
#   'off'    no override; the verdict is the producer's own.
# THE READING IS 'state' BECAUSE JOE WROTE "it's momentum = false", which describes the line's
# condition, not a one-bar event. Measured on 08-04: 'state' turns 52,359 rows to none, 'moment'
# turns 2,138. It is in the unique key, so a run at another reading lands alongside instead of
# on top.
FIXED    = 21                    # MOMO_FIXED_SAMPLES. build_ws_fin.py sets this at import
GRID_S   = 5

DDL = '''CREATE TABLE IF NOT EXISTS wsf_line_bar (
    wflb_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    -- THE KNOBS. All of these are in the unique key: change one and every row changes.
    wflb_win_from      DATETIME NOT NULL,  -- window start
    wflb_tf            SMALLINT NOT NULL,  -- timeframe 1 to 8. The line is ws{tf}r
    wflb_dr            TINYINT  NOT NULL,  -- direction the line is read in. +1 upward, -1 downward
    wflb_utc           DATETIME NOT NULL,  -- the bar, 5-second grid
    wflb_k_window      SMALLINT NOT NULL,  -- K_WINDOW 4. momentum window = K_WINDOW x tf, minutes
    wflb_fixed_samples SMALLINT NOT NULL,  -- MOMO_FIXED_SAMPLES 21, points in the straight-line fit
    wflb_stall_n       SMALLINT NOT NULL,  -- STALL_N 6, lattice samples with no new extreme
    wflb_hi            DOUBLE   NOT NULL,  -- high boundary 85
    wflb_lo            DOUBLE   NOT NULL,  -- low boundary 15
    wflb_r2_min        DOUBLE   NOT NULL,  -- MOMO_R2_MIN 0.50, straight-line fit floor
    wflb_slope_min     DOUBLE   NOT NULL,  -- MOMO_SLOPE_MIN 1.0, slope floor
    wflb_arc_min       DOUBLE   NOT NULL,  -- CURL_ARC_MIN 4.0, arc floor
    wflb_slack         DOUBLE   NOT NULL,  -- LEVEL_SLACK 13.9
    wflb_curl_r2_min   DOUBLE   NOT NULL,  -- CURL_R2_MIN 0.40, the bend's own fit floor
    -- THE MEASUREMENTS
    wflb_r          DOUBLE,             -- ws{tf}r value at the bar
    wflb_stalled    TINYINT NOT NULL,   -- jig.stall_mask. 1 = STALL_N samples with no new extreme
    wflb_since      SMALLINT,           -- lattice samples since a new extreme. NULL = lattice unusable
    wflb_ungated    VARCHAR(8) NOT NULL,-- momo(): momo | curl | sideways | none.  THE WSF VERDICT
    wflb_gated      VARCHAR(8) NOT NULL,-- momo_g(): the same with the direction gates. domTF's verdict
    wflb_reason     VARCHAR(48),        -- why the gated verdict landed where it did
    wflb_slope      DOUBLE,             -- straight-line slope over the fit points
    wflb_fit        DOUBLE,             -- straight-line r-squared
    wflb_level      TINYINT,            -- the tracking-weighted level gate passed
    wflb_aligned    TINYINT,            -- the slope points the same way the line is being read
    wflb_flat       TINYINT,            -- slope size under MOMO_SLOPE_MIN
    wflb_bend       DOUBLE,             -- the quadratic's leading coefficient over the window
    wflb_arc        DOUBLE,             -- bend size x 0.25
    wflb_vtx        DOUBLE,             -- turning point. 0 = window start, 1 = window end
    wflb_bendfit    DOUBLE,             -- the bend's own r-squared
    wflb_bend_align TINYINT,            -- the bend points the same way the line is being read
    wflb_curl_ends  VARCHAR(4),         -- which way the line is heading AFTER the turning point.
                                        --  up   = the bend opens upward, a minimum: fell, now rises
                                        --  down = the bend opens downward, a maximum: rose, now falls
                                        -- Joe 0818: "how will you know which way the curl ends?"
                                        -- Every row whose verdict is curl has its turning point inside
                                        -- the window (CURL_VTX_LO/HI 0.05-0.95), so the turn is always
                                        -- already behind the bar and this is where the line is going now.
    wflb_oob        TINYINT NOT NULL,   -- at or beyond the boundary on the direction's side
    wflb_step_bars  SMALLINT,           -- lattice step, grid bars between points
    wflb_samples    SMALLINT,           -- lattice points
    wflb_signal     TINYINT NOT NULL,   -- 1 = this bar is a wsf9of12 signal bar in v_ws_fin_walk
    wflb_momo_kill  VARCHAR(8) NOT NULL DEFAULT 'off',  -- KNOB. Which reading of Joe 0820's rule
    --   ran: 'state', 'moment' or 'off'. In the unique key.
    wflb_momo_xwob  SMALLINT NOT NULL DEFAULT 0,        -- KNOB. 5 s bars held outside the fence
    --   before an exit counts. Joe 0821. In the unique key.
    wflb_momo_fence_r SMALLINT NOT NULL DEFAULT 0,      -- KNOB. momo-fence-r as Joe writes it:
    --   the band is 100 minus this at the top and this at the bottom. 17 -> 83/17. In the unique key.
    wflb_mfr_out    TINYINT,            -- 1 = the line IS outside momo-fence-r on the side it is
    --   read, at this bar. RAW. Separate from wflb_oob, which reports against the global 85/15.
    wflb_mfr_xwob   TINYINT,            -- 1 = the CONFIRMED exit: outside for MOMO_XWOB consecutive
    --   bars, with the run started from inside. This is what the momentum rule reads.
    wflb_mfr_run    SMALLINT,           -- how many consecutive bars it has been outside, 0 inside
    wflb_last_verdict VARCHAR(8),       -- the verdict this line held BEFORE the current one.
    --   Joe 0820: "ws8 is `away` and close to the fence. verdict is 'none', last-verdict was
    --   'momo'. this indicates that ws8r has recently reversed". NULL until the first change.
    wflb_verdict_dwell INT,             -- seconds since wflb_verdict last changed on this line.
    --   0 on the bar it changed. Joe 0820: "report the seconds that have past since the verdict
    --   changed". It counts from the window start, so the first bars of the day undercount.
    wflb_verdict    VARCHAR(8),         -- THE VERDICT AFTER Joe 0820's rule. This is what the report
    --   shows. `wflb_ungated` above stays as the producer's own output, untouched, so the raw
    --   measurement and the rule applied to it are both on the row.
    wflb_knobs VARCHAR(160) NOT NULL DEFAULT '',
    --   THE KNOB SIGNATURE. MySQL caps a unique key at 16 parts and this mechanic has 17 knobs, so
    --   the key carries one deterministic string instead of the columns. Every knob column stays on
    --   the row and stays queryable; the signature exists only so a knob change lands ALONGSIDE the
    --   old rows instead of overwriting them, which is what the key was for.
    UNIQUE KEY uq_wflb (wflb_win_from, wflb_tf, wflb_dr, wflb_utc, wflb_knobs),
    KEY k_bar (wflb_utc), KEY k_line (wflb_tf, wflb_dr), KEY k_stall (wflb_stalled),
    KEY k_ungated (wflb_ungated), KEY k_signal (wflb_signal))'''

COLS = ['wflb_win_from', 'wflb_tf', 'wflb_dr', 'wflb_utc', 'wflb_k_window', 'wflb_fixed_samples',
        'wflb_stall_n', 'wflb_hi', 'wflb_lo', 'wflb_r2_min', 'wflb_slope_min', 'wflb_arc_min',
        'wflb_slack', 'wflb_curl_r2_min',
        'wflb_r', 'wflb_stalled', 'wflb_since', 'wflb_ungated', 'wflb_gated', 'wflb_reason',
        'wflb_slope', 'wflb_fit', 'wflb_level', 'wflb_aligned', 'wflb_flat',
        'wflb_bend', 'wflb_arc', 'wflb_vtx', 'wflb_bendfit', 'wflb_bend_align', 'wflb_curl_ends',
        'wflb_oob', 'wflb_step_bars', 'wflb_samples', 'wflb_signal',
        'wflb_knobs',
        'wflb_momo_kill', 'wflb_momo_fence_r', 'wflb_momo_xwob', 'wflb_mfr_out',
        'wflb_mfr_xwob', 'wflb_mfr_run', 'wflb_verdict',
        'wflb_last_verdict', 'wflb_verdict_dwell']


def wsf_verdict(ungated, out_fence, stalled, was_out, was_stalled, mode=MOMO_KILL):
    """[PRODUCER · Joe 0820] The momentum verdict after the ws-finisher's own rule.

    Joe 0820, corrected: "IF a momentum-true r line leaves momo-fence-r or stalls THEN its momentum
    = false (or none)." Momentum-true means the producer said momo or curl - Joe 0817: "(curl or
    momo) create wsf-momoc".

    `out_fence` is against momo-fence-r (83/17), NOT against the 85/15 boundary. Joe 0820: "we need
    to shrink the fence ... but I don't want it to be global."

    This lives HERE and not in momo_core, because momo_core is shared with domTF, the s46 path and
    RPL, none of which Joe has asked to change. `wflb_ungated` keeps the producer's own answer."""
    if mode == 'off' or ungated not in ('momo', 'curl'):
        return ungated
    if mode == 'state':
        return 'none' if (out_fence or stalled) else ungated
    if mode == 'moment':
        return 'none' if ((out_fence and not was_out)
                          or (stalled and not was_stalled)) else ungated
    raise ValueError(f'unknown MOMO_KILL mode {mode!r}')


def _f(x):
    """None for a value MySQL cannot store as a DOUBLE."""
    if x is None:
        return None
    x = float(x)
    return x if np.isfinite(x) else None


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    sysr = db.execute('SELECT pxsmooth_dema_src src, pxsmooth_dema_len len, '
                      'hi_boundary hi, lo_boundary lo FROM optimus9_system WHERE sys_pk=1',
                      fetch=True)[0]
    PXS = {'src': sysr['src'], 'len': sysr['len']}
    HI, LO = float(sysr['hi']), float(sysr['lo'])
    MFR_HI, MFR_LO = 100.0 - MOMO_FENCE_R, float(MOMO_FENCE_R)   # momo-fence-r, Joe 0820
    sig_bars = {str(x['g']) for x in db.execute(
        'SELECT g30_marker g FROM v_ws_fin_walk WHERE g30_marker >= %s AND g30_marker <= %s',
        (WIN_FROM, WIN_TO), fetch=True)}
    print(f'  boundaries {HI:.0f} / {LO:.0f}   wsf9of12 signal bars in the window: {len(sig_bars)}',
          flush=True)

    MG.MOMO_FIXED_SAMPLES = FIXED
    ts = np.load(os.path.join(TAPE_DIR, _tape_key(END_MS, HOURS, WARMUP, PXS) + '.npz'))['__ts__']
    i0 = int(np.searchsorted(ts, int(dt.datetime.fromisoformat(WIN_FROM)
                                     .replace(tzinfo=timezone.utc).timestamp() * 1000)))
    i1 = int(np.searchsorted(ts, int(dt.datetime.fromisoformat(WIN_TO)
                                     .replace(tzinfo=timezone.utc).timestamp() * 1000)))
    nbar = i1 - i0 + 1
    print(f'  window {WIN_FROM} -> {WIN_TO}   {nbar:,} bars at {GRID_S} s', flush=True)

    def u(ms):
        return dt.datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    utcs = [u(int(x)) for x in ts[i0:i1 + 1]]
    sigflag = [1 if x in sig_bars else 0 for x in utcs]

    db.execute(DDL)
    have = {c['Field'] for c in db.execute('SHOW COLUMNS FROM wsf_line_bar', fetch=True)}
    for col, spec in (('wflb_momo_kill', "VARCHAR(8) NOT NULL DEFAULT 'off'"),
                      ('wflb_momo_fence_r', 'SMALLINT NOT NULL DEFAULT 0'),
                      ('wflb_mfr_out', 'TINYINT'),
                      ('wflb_momo_xwob', 'SMALLINT NOT NULL DEFAULT 0'),
                      ('wflb_mfr_xwob', 'TINYINT'),
                      ('wflb_mfr_run', 'SMALLINT'),
                      ('wflb_verdict_dwell', 'INT'),
                      ('wflb_last_verdict', 'VARCHAR(8)'),
                      ('wflb_verdict', 'VARCHAR(8)')):
        if col not in have:
            db.execute(f'ALTER TABLE wsf_line_bar ADD COLUMN {col} {spec}')
            print(f'  added column {col} to the existing table', flush=True)
    if 'wflb_knobs' not in have:
        db.execute("ALTER TABLE wsf_line_bar ADD COLUMN wflb_knobs VARCHAR(160) NOT NULL DEFAULT ''")
        print('  added column wflb_knobs', flush=True)
    idx = db.execute("SHOW INDEX FROM wsf_line_bar WHERE Key_name='uq_wflb' "
                     "AND Column_name='wflb_knobs'", fetch=True)
    if not idx:
        db.execute('ALTER TABLE wsf_line_bar DROP INDEX uq_wflb, ADD UNIQUE KEY uq_wflb '
                   '(wflb_win_from, wflb_tf, wflb_dr, wflb_utc, wflb_knobs)')
        print('  unique key rebuilt on the knob signature - the 16-part limit was reached',
              flush=True)
    KNOB = (WIN_FROM, None, None, None, B.K_WINDOW, FIXED, STALL_N, HI, LO,
            MC.MOMO_R2_MIN, MC.MOMO_SLOPE_MIN, MC.CURL_ARC_MIN, MC.LEVEL_SLACK, MG.CURL_R2_MIN)
    KNOBSIG = (f'kw{B.K_WINDOW}_fs{FIXED}_sn{STALL_N}_hi{HI:g}_lo{LO:g}_r2{MC.MOMO_R2_MIN:g}_'
               f'sl{MC.MOMO_SLOPE_MIN:g}_arc{MC.CURL_ARC_MIN:g}_sk{MC.LEVEL_SLACK:g}_'
               f'cr{MG.CURL_R2_MIN:g}_mk{MOMO_KILL}_mf{MOMO_FENCE_R}_xw{MOMO_XWOB}')
    print(f'  knob signature: {KNOBSIG}', flush=True)
    where = 'wflb_win_from=%s AND wflb_knobs=%s'
    kv = (WIN_FROM, KNOBSIG)
    n_del = db.execute('SELECT COUNT(*) c FROM wsf_line_bar WHERE ' + where, kv, fetch=True)[0]['c']
    if n_del:
        print(f'  deleting {n_del:,} rows already stored at these knobs', flush=True)
        db.execute('DELETE FROM wsf_line_bar WHERE ' + where, kv)

    total = 0
    for tf in TFS:
        r = np.load(os.path.join(LINE_DIR,
                                 _line_key(END_MS, HOURS, WARMUP,
                                           override(tf * 60, KLine(**B.R_SPEC), 'emerging')) + '.npy'))
        with momo_window(B.K_WINDOW * tf):
            step, samples = int(MC.MOMO_STEP_BARS), int(MC.MOMO_SAMPLES)
        span = (samples - 1) * step
        lat = np.stack([r[i - span:i + 1:step] for i in range(i0, i1 + 1)])   # the stall lattice
        for dr in DRS:
            mask, since = _stall_rows(lat, dr, STALL_N)
            rows = []
            with momo_window(B.K_WINDOW * tf):
                prev_mfr = prev_st = 0      # the bar before the window, for the 'moment' reading
                run = 0                     # consecutive bars outside momo-fence-r
                was_inside = False          # the run only counts if it started from inside
                prev_v, dwell, last_v = None, 0, None   # dwell seconds, and the verdict before it
                for k, i in enumerate(range(i0, i1 + 1)):
                    gat, why, f = momo_g_why(r, dr, i, quad=True)
                    ung = MC.verdict(f)[0]
                    qa = f.get('qa')
                    rv = float(r[i])
                    oob = int(rv >= HI if dr > 0 else rv <= LO)
                    mfr = int(rv >= MFR_HI if dr > 0 else rv <= MFR_LO)   # RAW: outside right now
                    if not mfr:
                        was_inside = True; run = 0
                    elif was_inside:
                        run += 1
                    mfrx = int(run >= MOMO_XWOB)          # the CONFIRMED exit
                    vd = wsf_verdict(ung, mfrx, int(bool(mask[k])), prev_mfr, prev_st)
                    if vd != prev_v:
                        if prev_v is not None:
                            last_v = prev_v      # what it held before this change
                        dwell = 0
                    else:
                        dwell += GRID_S
                    rows.append((
                        WIN_FROM, tf, dr, utcs[k], B.K_WINDOW, FIXED, STALL_N, HI, LO,
                        MC.MOMO_R2_MIN, MC.MOMO_SLOPE_MIN, MC.CURL_ARC_MIN, MC.LEVEL_SLACK,
                        MG.CURL_R2_MIN,
                        _f(rv), int(bool(mask[k])),
                        None if int(since[k]) < 0 else int(since[k]),
                        ung, gat, why,
                        _f(f['slope']), _f(f['r2']), int(f['level']), int(f['aligned']),
                        int(f['flat']),
                        _f(qa), None if qa is None else _f(abs(float(qa)) * 0.25),
                        _f(f.get('vtx')), _f(f.get('quad_r2')),
                        None if f.get('quad_aligned') is None else int(f['quad_aligned']),
                        # only on a curl row. Joe 0818 caught 'up' printed on a `none` row -
                        # the bend is fitted on every bar, but "which way the curl ends" is
                        # meaningless where the verdict never reached the curl test.
                        None if (ung != 'curl' or qa is None) else
                        ('up' if float(qa) > 0 else 'down' if float(qa) < 0 else None),
                        oob, step, samples, sigflag[k],
                        KNOBSIG,
                        MOMO_KILL, MOMO_FENCE_R, MOMO_XWOB, mfr, mfrx, run, vd, last_v, dwell))
                    prev_mfr, prev_st, prev_v = mfrx, int(bool(mask[k])), vd
            db.executemany(f'INSERT INTO wsf_line_bar ({",".join(COLS)}) VALUES '
                           f'({",".join(["%s"] * len(COLS))})', rows)
            total += len(rows)
            d = 'upward' if dr > 0 else 'downward'
            print(f'  ws{tf}r read {d:<8}: {len(rows):,} rows   lattice {samples} points '
                  f'{step} bars apart = {step * GRID_S} s, span {span * GRID_S} s   '
                  f'stalled {int(mask.sum()):,}', flush=True)

    print(f'\n  wsf_line_bar : {total:,} rows written', flush=True)
    db.disconnect()
    return 0


if __name__ == '__main__':
    sys.exit(main())
