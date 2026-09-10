"""build_wsf_dtf_v3 — the wsf-dtf-v3 report and the table behind it. Joe 0910 named the report.

THE ROW. One row per (line, dr run): the FIRST bar in that dr run where the line's r is
`sideways` AND outside the fence. Joe 0909: "keep the first sideways event per dr flip".

dr        ws1Mage AND ws13m both oob, SAME side, latched. Previous dr holds until then.
fence     25 / 75 (Joe 0910 raised it from 30/70)
lines     ws1..ws23. Joe 0910 set ws5..ws23 ("increase the max r lines to ws23") then added
          the low end ("add the ws1,2,3,4 r lines to the report"). THE RANGE IS IN KNOBS.
window    the WALK is 08-25 00:00:00 -> 08-28 00:00:00. Joe 0910 "extend the report to 08-27
          (full days)"; a day runs 00:00:00 through the NEXT day's 00:00:00 inclusive.
          The verdict/dr warm-up starts 08-23 so the 21-sample lattice and the dr latch are warm.
momo      the report body uses a 10-minute lattice span and momo_slope_min 0.4.
          FITTED, NOT MEASURED - both were chosen by sweeping until ws7r read `sideways` at
          Joe's eyeballed ~05:36 on 08-25. Re-declare that every time these numbers are quoted.

COLUMNS Joe specified, in his order:
  utc, line, backstop utc, dr run, dr, r, top mom TF, top, top+1, top backstop, prev mom,
  run bars, +1..+4 TF,
  then mage mask and the two HTF momentum columns on the right.

  top backstop the SAME mech as `backstop utc`, read off ws{top mom TF} instead of ws{line}.
               NULL when top mom TF is 0. Joe 0910: "add a column that behaves the same as
               'wdv_backstop_utc'. this new column will print the x-cross timestamp of the
               wdv_top_mom_tf TF". The column name is a placeholder - Joe has not named it.
  backstop utc THE BACKSTOP. Joe 0910 named it: "change `race utc` to `backstop utc`". The value
               is the impending ws{line} x-cross-race - the first race confirmation strictly after
               the row's bar, at the row's dr. The mech is build_wsf_x_cross's verbatim:
               the race is the FIRST of x crossing its Mage, its b, or the boundary (85 at dr +1,
               15 at dr -1); x must hold the far side XCROSS_XWOB = 5 bars (a run spanning 20 s),
               and must have
               been on the near side before it crossed. dr +1 the x crosses DOWN under its target,
               dr -1 it crosses UP over. build_wsf_x_cross itself only carries TF 1..12 (Joe 0826
               "wsf is limited to TF12"), so this column computes the race off the cached role
               lines rather than reading that table. That table is not touched.

  top mom TF   the HIGHEST timeframe in 5..23 with a momo or curl verdict at that bar's dr.
               0 means none of them held momentum. It is not a timeframe number.
  top / top+1  that timeframe's r, and the next timeframe up. '-' when top mom TF is 0.
  prev mom     when top mom TF is 0, the most recent EARLIER bar that had one, as
               '{TF} {verdict} -{minutes ago}'. '-' when top mom TF is non-zero.
  +1..+4 TF    the next four timeframes ascending from the row's own line, r at the row's bar,
               as '{r} ({TF})' - Joe 0910 replaced the earlier '{TF}:{r}'. '-' above ws23.
  mage mask    THE SIGN MASK, the mech from build_wsf_event_mark.sign_mask (the surviving
               implementation - flip_report.py, which filled wsf_momo_flip_rep's mask columns,
               is absent from the repo). One character per ADJACENT PAIR in the sequence:
               '+' the lower timeframe's Mage is above the higher's, '-' below, '0' equal,
               '.' a line is missing. Joe 0910 set the sequence: gcws30 then ws1..ws18,
               19 tags = 18 pairs.
  htf mom bank / htf mom fit
               which of ws120, ws90, ws60, ws45, ws30 are momentum-true, as '120, 30'.
               Joe 0910 asked for BOTH settings as two columns:
                 bank  each line at momo_config v1 for its own timeframe - span k_window 6 x TF,
                       so ws30 reads 180 min and ws120 reads 720 min. "The mech as it is."
                 fit   all five at the report's own 10-min span and slope_min 0.4.

THE KNOB SET IS ONE COLUMN, shaped like wsf_event_mark.wem_knobs and wsf_momo_flip_rep.wmf_knobs.
Every knob that moves a row is inside wdv_knobs, and it is the first part of the unique key, so
the next knob change lands BESIDE this one instead of overwriting it.

    python3 build_wsf_dtf_v3.py            build and bank
    python3 build_wsf_dtf_v3.py --show     print what is banked, newest knob set first
"""
import sys
import os
import time
import datetime as dt
from datetime import timezone

import numpy as np

from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.compute.line_config import override, mech_lines
from optimus9.compute.momo_config import momo_bank, momo_config
from optimus9.compute.momo_gated import momo_g_why, momo_window
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP
from optimus9.orchestration.rpl_cache import LINE_DIR, TAPE_DIR, _line_key, _tape_key

TFS      = list(range(1, 24))          # the report body. Joe 0910 added ws1..ws4 to the
#                                        ws5..ws23 he set earlier; the range is in KNOBS
HTF      = [120, 90, 60, 45, 30]       # the two HTF momentum columns, printed high to low
MASK_SEQ = ['g30'] + [str(t) for t in range(1, 19)]   # 19 tags -> 18 pairs. Joe 0910
FL, FH   = 25.0, 75.0                  # the fence. Joe 0910
XRACE    = 5                           # x-cross-race hold, bars. A 5-bar run spans 20 s.
#                                        XCROSS_XWOB in build_wsf_x_cross, same value
SPAN     = 10                          # lattice span, minutes. FITTED
SLOPE    = 0.4                         # momo_slope_min. FITTED
BANKV    = 1                           # momo_config version for the banked-bank HTF column
WARM     = '2026-08-23 00:00:00'
W0, W1   = '2026-08-25 00:00:00', '2026-08-28 00:00:00'

# THE TIMEFRAME RANGE IS A KNOB THAT MOVES ROWS - `prev mom` on every row scans TFS, so a
# wider range can change it on rows that already existed. It goes in the string, and the
# 565 rows banked 0910 stay at the earlier string, which with no tf prefix means ws5..ws23.
KNOBS = (f'v3_tf{TFS[0]}.{TFS[-1]}_sp{SPAN}_sl{SLOPE}_f{FL:g}.{FH:g}'
         f'_drws1Mage.ws13m_bv{BANKV}')

DDL = '''CREATE TABLE IF NOT EXISTS wsf_dtf_v3 (
    wdv_pk        BIGINT AUTO_INCREMENT PRIMARY KEY,
    wdv_knobs     VARCHAR(160) NOT NULL,  -- every knob that moves a row. First part of the key
    wdv_utc       DATETIME     NOT NULL,  -- the row bar, exact
    wdv_ms        BIGINT       NOT NULL,  -- the same bar in epoch ms, for ordering
    wdv_line      INT          NOT NULL,  -- the timeframe whose r went sideways, minutes
    wdv_backstop_utc DATETIME NULL,       -- THE BACKSTOP, Joe 0910. The IMPENDING ws{wdv_line}
    --   x-cross-RACE: the first
    --   race confirmation STRICTLY AFTER this row's bar, at this row's dr. The race is the first
    --   of three to cross - x crossing its Mage, its b, or the boundary - the mech verbatim from
    --   build_wsf_x_cross. Hold 5 bars on the far side - a 5-bar run spans 20 s - and x must
    --   have been on the near side first. NULL = none before the cache ends.
    --   THE HOLD OF 5 IS NOT IN THE UNIQUE KEY:
    --   a different race xwob overwrites this column instead of landing beside it. Joe 0910
    wdv_dr_run    INT          NOT NULL,  -- which dr run inside the window, 1-based
    wdv_dr        TINYINT      NOT NULL,  -- +1 or -1 at the row bar
    wdv_r         DOUBLE       NOT NULL,  -- that line's r at the row bar
    wdv_top_mom_tf INT         NOT NULL,  -- highest TF in 5..23 momentum-true. 0 = none
    wdv_top       DOUBLE       NULL,      -- r of wdv_top_mom_tf. NULL when it is 0
    wdv_top1      DOUBLE       NULL,      -- r of wdv_top_mom_tf + 1. NULL when 0 or above ws23
    wdv_top_backstop_utc DATETIME NULL,    -- THE SAME MECH AS wdv_backstop_utc, read off
    --   ws{wdv_top_mom_tf} instead of ws{wdv_line}: the first x-cross-RACE confirmation STRICTLY
    --   AFTER this row's bar, at this row's dr. NULL when wdv_top_mom_tf is 0 - 0 means no
    --   timeframe held momentum, it is not a timeframe number and there is no ws0 line.
    --   PLACEHOLDER NAME, Joe has not named this column. Joe 0910
    wdv_prev_mom  VARCHAR(32)  NULL,      -- '{TF} {verdict} -{mins}m'. NULL when top_mom_tf != 0
    wdv_run_bars  INT          NOT NULL,  -- length of the sideways run this row opens, 5 s bars
    wdv_nx1       VARCHAR(16)  NULL,      -- '{r} ({TF})' for the row's line + 1. Joe 0910
    wdv_nx2       VARCHAR(16)  NULL,
    wdv_nx3       VARCHAR(16)  NULL,
    wdv_nx4       VARCHAR(16)  NULL,
    wdv_mage_mask VARCHAR(24)  NULL,      -- 18 pairs, gcws30 v ws1 ... ws17 v ws18
    wdv_htf_bank  VARCHAR(32)  NULL,      -- eg '120, 30' at the banked banks
    wdv_htf_fit   VARCHAR(32)  NULL,      -- the same five lines at the report's fitted settings
    UNIQUE KEY u_row (wdv_knobs, wdv_utc, wdv_line),
    KEY k_ms (wdv_ms), KEY k_line (wdv_line, wdv_dr))'''

# wdv_backstop_utc is NOT in this list. It is written by fill_race(), which main() calls after the
# insert - one implementation of the backstop, not two.
COLS = ['wdv_knobs', 'wdv_utc', 'wdv_ms', 'wdv_line', 'wdv_dr_run', 'wdv_dr', 'wdv_r',
        'wdv_top_mom_tf', 'wdv_top', 'wdv_top1', 'wdv_prev_mom', 'wdv_run_bars',
        'wdv_nx1', 'wdv_nx2', 'wdv_nx3', 'wdv_nx4', 'wdv_mage_mask',
        'wdv_htf_bank', 'wdv_htf_fit']


def sign_mask(vals, seq):
    """[MECH from build_wsf_event_mark.sign_mask] One character per adjacent pair in `seq`."""
    out = []
    for lo, hi in zip(seq, seq[1:]):
        a, b = vals.get(lo), vals.get(hi)
        out.append('.' if a is None or b is None else '+' if a > b else '-' if a < b else '0')
    return ''.join(out)


def race_bars(x, MG, B, bound, dr, xwob=None):
    """Per bar: did the ws{tf} x-cross-RACE confirm here, at direction `dr`.

    [MECH verbatim from build_wsf_x_cross.held / far_side.] The race is the FIRST of three to
    cross - x against its Mage, its b, or the boundary. Each target is run independently and the
    race fires when ANY of them confirms.

      far side   dr +1 -> x BELOW the target; dr -1 -> x ABOVE it
      the hold   x must sit on the far side for `xwob` consecutive 5 s bars. It confirms on the
                 bar the run REACHES xwob, not the bar it started
      near first x must have been on the NEAR side at some earlier finite bar. A line standing on
                 the far side since the start never crossed
      NaN        zeroes the run but does NOT clear the fired latch and does NOT set was-near.
                 Only a near-side bar clears the latch, so one far-side stretch broken by NaN
                 still fires only once

    Returns a bool array, one per bar."""
    xwob = XRACE if xwob is None else xwob
    n = len(x)
    out = np.zeros(n, bool)
    for t in (MG, B, np.full(n, float(bound))):
        valid = np.isfinite(x) & np.isfinite(t)
        f = (x < t) if dr > 0 else (x > t)
        far, near = valid & f, valid & ~f
        if not near.any():
            continue
        idx = np.arange(n)
        # run = consecutive far bars, zeroed by a near bar or a NaN bar
        reset = np.where(~far, idx + 1, 0)
        run = (idx + 1) - np.maximum.accumulate(reset)
        # only after the first near-side bar can a run count at all
        run = np.where(idx >= int(np.flatnonzero(near)[0]), run, 0)
        cand = np.flatnonzero(run == xwob)
        if not len(cand):
            continue
        # the fired latch: within one stretch with no near bar, only the FIRST run==xwob counts
        last_near = np.maximum.accumulate(np.where(near, idx, -1))
        prev = -1
        for i in cand:
            ln = last_near[i]
            if ln > prev:            # a near bar has happened since the last fire
                out[i] = True
                prev = i
    return out


def fill_race(db):
    """Fill wdv_backstop_utc and wdv_top_backstop_utc on rows already banked.

    Both are the SAME mech - see race_bars. wdv_backstop_utc reads ws{wdv_line}; wdv_top_backstop_utc
    reads ws{wdv_top_mom_tf} and is NULL when that is 0. Neither moves a row, so both are written in
    place at whatever knob set the row already carries, across every bank in the table."""
    have = {c['Field'] for c in db.execute('SHOW COLUMNS FROM wsf_dtf_v3', fetch=True)}
    if 'wdv_top_backstop_utc' not in have:
        db.execute('ALTER TABLE wsf_dtf_v3 ADD COLUMN wdv_top_backstop_utc DATETIME NULL '
                   'AFTER wdv_top1')
        print('  added wdv_top_backstop_utc after wdv_top1', flush=True)
    if 'wdv_backstop_utc' not in have:
        if 'wdv_race_utc' in have:      # Joe 0910 renamed it. CHANGE keeps every value in place
            db.execute('ALTER TABLE wsf_dtf_v3 CHANGE COLUMN wdv_race_utc wdv_backstop_utc DATETIME NULL')
            print('  renamed wdv_race_utc -> wdv_backstop_utc, values kept', flush=True)
        else:
            db.execute('ALTER TABLE wsf_dtf_v3 ADD COLUMN wdv_backstop_utc DATETIME NULL AFTER wdv_line')
            print('  added wdv_backstop_utc after wdv_line', flush=True)
    sy = db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l, hi_boundary hi, '
                    'lo_boundary lo FROM optimus9_system WHERE sys_pk=1', fetch=True)[0]
    HI, LO = float(sy['hi']), float(sy['lo'])
    SPEC = {}
    for g in mech_lines(db, 'wsf'):
        if g['role'] not in SPEC:
            _t, s_, m_ = g['override']; SPEC[g['role']] = (s_, m_)
    rows = db.execute('SELECT wdv_pk, wdv_ms, wdv_line, wdv_dr, wdv_top_mom_tf FROM wsf_dtf_v3 '
                      'ORDER BY wdv_line, wdv_ms', fetch=True)
    ts = np.load(os.path.join(TAPE_DIR, _tape_key(END_MS, HOURS, WARMUP,
                 {'src': sy['s'], 'len': sy['l']}) + '.npz'))['__ts__']
    L = lambda tf, role: np.load(os.path.join(LINE_DIR, _line_key(END_MS, HOURS, WARMUP,
                         override(tf * 60, *SPEC[role])) + '.npy'))
    print(f'  {len(rows):,} rows   race hold {XRACE} bars, a run spanning {(XRACE - 1) * 5} s   '
          f'boundary {HI:g} / {LO:g}', flush=True)
    # every timeframe either column has to resolve. top_mom_tf 0 is not a timeframe - it is
    # excluded here and lands as NULL below.
    need = ({int(r['wdv_line']) for r in rows}
            | {int(r['wdv_top_mom_tf']) for r in rows if int(r['wdv_top_mom_tf']) > 0})
    IX, hit = {}, {}
    for tf in sorted(need):
        X, MG, B = L(tf, 'x'), L(tf, 'Mage'), L(tf, 'b')
        IX[tf] = {d: np.flatnonzero(race_bars(X, MG, B, HI if d > 0 else LO, d)) for d in (+1, -1)}
        hit[tf] = {d: len(IX[tf][d]) for d in (+1, -1)}

    def nxt(tf, d, i0):
        """The first race confirmation STRICTLY after bar i0 on ws{tf} at direction d."""
        a = IX[tf][d]
        q = int(np.searchsorted(a, i0, side='right'))
        return (dt.datetime.fromtimestamp(int(ts[a[q]]) / 1000, tz=timezone.utc)
                .strftime('%Y-%m-%d %H:%M:%S')) if q < len(a) else None

    upd = []
    for r in rows:
        d = int(r['wdv_dr'])
        if d == 0:
            continue
        i0 = int(np.searchsorted(ts, int(r['wdv_ms'])))
        t = int(r['wdv_top_mom_tf'])
        upd.append((nxt(int(r['wdv_line']), d, i0),
                    nxt(t, d, i0) if t > 0 else None,
                    int(r['wdv_pk'])))
    db.executemany('UPDATE wsf_dtf_v3 SET wdv_backstop_utc=%s, wdv_top_backstop_utc=%s '
                   'WHERE wdv_pk=%s', upd)
    print(f'  wrote {len(upd):,} rows, both backstop columns', flush=True)
    for tf in sorted(hit):
        print(f'    ws{tf:<3} race confirmations on the cache: dr +1 {hit[tf][+1]:>6,}   '
              f'dr -1 {hit[tf][-1]:>6,}', flush=True)



def show(db):
    rows = db.execute('SELECT wdv_knobs k, COUNT(*) n, MIN(wdv_utc) a, MAX(wdv_utc) b '
                      'FROM wsf_dtf_v3 GROUP BY wdv_knobs ORDER BY MAX(wdv_pk) DESC', fetch=True)
    for r in rows:
        print(f"  {r['k']}   {r['n']:,} rows   {r['a']} -> {r['b']}")
    if not rows:
        print('  wsf_dtf_v3 is empty')


def main():
    t0 = time.time()
    db = DatabaseManager(**get_db_config()); db.connect()
    db.execute(DDL)
    if '--show' in sys.argv:
        show(db); db.disconnect(); return 0
    sy = db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l, hi_boundary hi, '
                    'lo_boundary lo FROM optimus9_system WHERE sys_pk=1', fetch=True)[0]
    HI, LO = float(sy['hi']), float(sy['lo'])
    SPEC = {}
    for g in mech_lines(db, 'wsf'):
        if g['role'] not in SPEC:
            _t, s_, m_ = g['override']; SPEC[g['role']] = (s_, m_)
    BK = {tf: momo_bank(db, tf, version=BANKV) for tf in set(TFS) | set(HTF)}
    from optimus9.orchestration.build_ws_lines import line_names, overrides, PREFIXES
    OVR = overrides(db, line_names(db, PREFIXES))
    db.disconnect()

    ts = np.load(os.path.join(TAPE_DIR, _tape_key(END_MS, HOURS, WARMUP,
                 {'src': sy['s'], 'len': sy['l']}) + '.npz'))['__ts__']
    u = lambda i: dt.datetime.fromtimestamp(int(ts[i]) / 1000, tz=timezone.utc)
    ms = lambda x: int(dt.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
                       .replace(tzinfo=timezone.utc).timestamp() * 1000)
    L = lambda tf, role: np.load(os.path.join(LINE_DIR, _line_key(END_MS, HOURS, WARMUP,
                         override(tf * 60, *SPEC[role])) + '.npy'))
    R = {tf: L(tf, 'r') for tf in set(TFS) | set(HTF)}
    MG = {str(tf): L(tf, 'Mage') for tf in range(1, 19)}
    MG['g30'] = np.load(os.path.join(LINE_DIR, _line_key(END_MS, HOURS, WARMUP,
                        OVR['gcws30Mage']) + '.npy'))
    G1, M13 = MG['1'], L(13, 'm')

    i0 = int(np.searchsorted(ts, ms(WARM)))
    A = int(np.searchsorted(ts, ms(W0))); B = int(np.searchsorted(ts, ms(W1)))
    print(f'  {KNOBS}', flush=True)
    print(f'  warm-up {WARM} -> walk {W0} to {W1} = {B - A + 1:,} bars', flush=True)

    DR = np.zeros(len(ts), np.int8); cur = 0
    for k in range(i0 - 200000, B + 1):
        a, b = float(G1[k]), float(M13[k])
        if a == a and b == b:
            if a >= HI and b >= HI: cur = +1
            elif a <= LO and b <= LO: cur = -1
        DR[k] = cur
    segs = []; s = A
    for k in range(A + 1, B + 1):
        if DR[k] != DR[k - 1]: segs.append((s, k - 1, int(DR[s]))); s = k
    segs.append((s, B, int(DR[s])))
    print(f'  dr at start {int(DR[A]):+d}   dr runs in the walk: {len(segs)}', flush=True)

    CODE = {'none': 0, 'sideways': 1, 'curl': 2, 'momo': 3}
    ST = {}
    for tf in TFS:
        bk = dict(BK[tf]); bk['momo_slope_min'] = SLOPE
        a = np.zeros(len(ts), np.int8)
        with momo_config(bk), momo_window(SPAN):
            for k in range(i0, B + 1):
                d = int(DR[k])
                if d: a[k] = CODE[momo_g_why(R[tf], d, k, quad=True)[0]]
        ST[tf] = a
        print(f'    ws{tf}r verdicts  {time.time() - t0:.0f}s', flush=True)

    HB, HFt = {}, {}
    for tf in HTF:
        bk = BK[tf]
        a = np.zeros(len(ts), np.int8)
        with momo_config(bk), momo_window(bk['k_window'] * tf):
            for k in range(A, B + 1):
                d = int(DR[k])
                if d: a[k] = CODE[momo_g_why(R[tf], d, k, quad=True)[0]]
        HB[tf] = a
        bk2 = dict(bk); bk2['momo_slope_min'] = SLOPE
        c = np.zeros(len(ts), np.int8)
        with momo_config(bk2), momo_window(SPAN):
            for k in range(A, B + 1):
                d = int(DR[k])
                if d: c[k] = CODE[momo_g_why(R[tf], d, k, quad=True)[0]]
        HFt[tf] = c
        print(f'    ws{tf}r HTF both settings  {time.time() - t0:.0f}s', flush=True)

    TOP = np.zeros(len(ts), np.int8); TOPV = {}
    PREV = {}; last = None
    for k in range(i0, B + 1):
        for tf in reversed(TFS):
            if ST[tf][k] >= 2:
                TOP[k] = tf; TOPV[k] = 'momo' if ST[tf][k] == 3 else 'curl'; break
        if TOP[k]: last = k
        PREV[k] = last

    outside = lambda v: v == v and (v < FL or v > FH)
    rows = []
    for tf in TFS:
        S = {k for k in range(A, B + 1) if ST[tf][k] == 1 and outside(float(R[tf][k]))}
        for si, (a_, b_, d) in enumerate(segs, 1):
            f = next((k for k in range(a_, b_ + 1) if k in S), None)
            if f is None: continue
            e = f
            while e + 1 <= b_ and (e + 1) in S: e += 1
            rows.append((f, tf, si, e))
    rows.sort()

    out = []
    for f, tf, si, e in rows:
        t = int(TOP[f])
        tv = float(R[t][f]) if t else None
        t1 = float(R[t + 1][f]) if t and (t + 1) <= 23 else None
        if t: pm = None
        else:
            pk = PREV[f]
            pm = (f'{int(TOP[pk])} {TOPV[pk]} -{(ts[f] - ts[pk]) / 60000.0:.1f}m'
                  if pk is not None else 'none in region')
        nx = []
        for j in range(1, 5):
            t2 = tf + j
            nx.append(f'{float(R[t2][f]):.1f} ({t2})' if t2 <= 23 else None)
        mask = sign_mask({tag: (float(MG[tag][f]) if float(MG[tag][f]) == float(MG[tag][f])
                                else None) for tag in MASK_SEQ}, MASK_SEQ)
        hb = ', '.join(str(x) for x in HTF if HB[x][f] >= 2) or None
        hf = ', '.join(str(x) for x in HTF if HFt[x][f] >= 2) or None
        out.append((KNOBS, u(f).strftime('%Y-%m-%d %H:%M:%S'), int(ts[f]), tf, si, int(DR[f]),
                    round(float(R[tf][f]), 1), t,
                    None if tv is None else round(tv, 1), None if t1 is None else round(t1, 1),
                    pm, e - f + 1, nx[0], nx[1], nx[2], nx[3], mask, hb, hf))

    db = DatabaseManager(**get_db_config()); db.connect()
    n = db.execute('SELECT COUNT(*) c FROM wsf_dtf_v3 WHERE wdv_knobs=%s', (KNOBS,),
                   fetch=True)[0]['c']
    if n:
        print(f'  {n:,} rows already banked at these knobs - nothing written', flush=True)
    else:
        db.executemany(f"INSERT INTO wsf_dtf_v3 ({','.join(COLS)}) "
                       f"VALUES ({','.join(['%s'] * len(COLS))})", out)
        print(f'  banked {len(out):,} rows into wsf_dtf_v3', flush=True)
    fill_race(db)
    db.disconnect()

    print(f'\n=== wsf-dtf-v3 ===', flush=True)
    hdr = (f"  {'utc':<20}{'line':<7}{'dr run':>7}{'dr':>4}{'r':>8}{'top mom TF':>12}{'top':>8}"
           f"{'top+1':>8}  {'prev mom':<18}{'run bars':>9}  {'+1 TF':<10}{'+2 TF':<10}"
           f"{'+3 TF':<10}{'+4 TF':<10}{'mage mask':<21}{'htf mom bank':<18}{'htf mom fit':<18}")
    print(hdr, flush=True)
    for r in out:
        (_, utc, _, tf, si, dr, rv, t, tv, t1, pm, rb, n1, n2, n3, n4, mask, hb, hf) = r
        print(f"  {utc:<20}ws{tf}r".ljust(29) + f"{si:>5}{dr:>+4d}{rv:>8.1f}{t:>12}"
              f"{('-' if tv is None else f'{tv:.1f}'):>8}"
              f"{('-' if t1 is None else f'{t1:.1f}'):>8}  {(pm or '-'):<18}{rb:>9}  "
              f"{(n1 or '-'):<10}{(n2 or '-'):<10}{(n3 or '-'):<10}{(n4 or '-'):<10}"
              f"{mask:<21}{(hb or '-'):<18}{(hf or '-'):<18}", flush=True)
    print(f'\n  rows {len(out)}   {time.time() - t0:.0f}s', flush=True)
    return 0


if __name__ == '__main__':
    if '--race' in sys.argv:
        _db = DatabaseManager(**get_db_config()); _db.connect()
        fill_race(_db); _db.disconnect(); sys.exit(0)
    sys.exit(main())
