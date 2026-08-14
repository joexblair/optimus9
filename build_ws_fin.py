#!/usr/bin/env python3
"""build_ws_fin — IO for the ws_fin_9of12 SIGNAL. Joe 0813: "make your analysis data durable in a
db table, so that we can troubleshoot optimally".

SRP. The producer is optimus9.analysis.jig.ws_fin_9of12 (pure). Joe 0813: "this needs to be
produced in the jig". This file supplies the g30 clock, calls the producer, adds the domTF verdict,
and writes the table. No confluence logic lives here.

TWO MECHANICS, KEPT APART. Joe 0813: "don't mix up domTF with the finisher momentum calcs - they
are completely separated".
    domTF     TF8..33 r lines, momo window K_WINDOW x TF minutes. The momentum LAYER.
              Its verdict is FREE / BLOCKED and it is the only thing computed here.
    finisher  ws1r..ws6r. NOT computed in this file. Its window/step/slope knobs are unset.

RPL IS IN THE CHAIN, and only for domTF. momo_g imports build_exhv2, which imports build_exhaust /
build_rplwalk2 / rpl_walk, and that import alone costs minutes. Task #6 removes it.

    python3 build_ws_fin.py
"""
import sys
import datetime as dt
from datetime import timezone

import numpy as np

from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.compute.line_config import LineStore, KLine, BBLine, override
from optimus9.orchestration.rpl_cache import cache_jig_perline
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP
from optimus9.analysis import ws_strat as WS
from optimus9.analysis.jig import (ws_fin_9of12, WSF_N, WSF_HANDICAP, WSF_VOTE_HOLD,
                                   WSF_VOTE_STICKY, WSF_REQUIRE, WSF_LINE_XWOB,
                                   stall_mask, domtf_handover)
from optimus9.compute import momo_gated as MG
from optimus9.compute.momo_gated import momo_g, momo_window

MG.MOMO_FIXED_SAMPLES = 21   # KNOB, Joe 0814. Every domTF line's momentum fit uses 21 sample
#                              points across its own 4 x timeframe window, so the gap scales with
#                              the line (2.6 min on ws13r, 5.4 min on ws27r) instead of the count.
from optimus9.compute import momo_core as MC
import build_momo_landed as B          # domTF constants only: TFS, R_SPEC, K_WINDOW 4

DOMTF_MIN = 13      # KNOB, Joe 0813: "8 has proven that it is too low to be of value when we're in
DOMTF_MAX = 27      # a large leg (between 17:00 and 21:00) ... make the domTF range 13 to 27".
                    # The shortest and longest timeframe, in minutes, the domTF layer may use.
                    # B.TFS stays 8..33 — momo_landed depends on it.
DOMTF_TFS = [t for t in B.TFS if DOMTF_MIN <= t <= DOMTF_MAX]

RESCUE_REJECTED_CURL = True
# KNOB, Joe 0813. A line can find a bend and have it thrown away because the bend points AGAINST the
# move — either the slope points the wrong way, or the curve bends the wrong way. Asked about the
# other direction the same line is then rejected on level, because a line sitting near 0 cannot
# register as carrying an upward move at any slack. So the bend is computed and discarded twice and
# the line reports as nothing in both directions.
# Joe 0813, asked whether such a bend should be read as a vote the other way: "yes" / "if other lines
# are backing the curl line, it has considerable weight".
# Found at 08-04 07:21:50: ws16r rejected on slope +0.080, ws17r on curvature +27.879, ws18r on
# curvature +25.914 — all three reading as nothing while holding a measured upward bend.
# THE BACKING REQUIREMENT IS JOE'S EXISTING ONE: a rescued vote joins the same NESTED_OPPOSITION_MIN
# count, so it only ever acts when other lines are opposing alongside it.

DOMTF_HTF_BAND = (22, 27)   # KNOB, Joe 0814: "from 22-27 (semi arbitrary)" / "until we've
#                             understood the results, let's keep it static". When a line in this
#                             band has recently curled into the move, only this band may end the
#                             domTF turn.
CURL_RECENCY_TF_BARS = 2    # KNOB, Joe 0814 "{knob:2 TF bars}", confirmed as two bars of that
#                             line's OWN timeframe: 44 min on ws22r, 54 min on ws27r.
STALL_N = 6                 # KNOB. Joe 0810: "3 samples that have not exceeded the maxim".
#                             Joe 0814 raised it to 6 — at 3 the stall is looser than the cross on
#                             every line (49.4-57.5% of bars against 33.6-47.8%) and won 48 of 51
#                             handovers. At 6 it is 33.7-46.5%, level with the cross.
#                             Samples, not minutes — 15.5 min on ws13r to 32.5 min on ws27r.
#                             THE STALL EXISTS TO CATCH WHAT THE CROSS MISSES. Joe 0814: "the
#                             reason for having stall, is to catch the moments that a x cross
#                             misses, eg TF25, 08-01 ~12:55".
HANDOVER_XWOB = 4           # bars the fast partner must hold on the far side of its r line.

NESTED_OPPOSITION = True
NESTED_OPPOSITION_MIN = 3   # KNOB, Joe 0813: "there has to be a domino effect for the logic to be
                            # stable - ie more than 2 r lines must print a reversal or curl".
                            # More than 2 = at least 3. Counted among the timeframes SHORTER than
                            # the longest supporter. Adjacency is NOT required — Joe's own wording
                            # defines it as a count, not as neighbours.
# KNOB, Joe 0813: "if a higher TF is showing bullish momo/curl, and it's matryoshka lines have
# curled to a bearish posture, then the verdict must be 'FREE'".
# Read as: take the LONGEST timeframe supporting the move. If ANY shorter timeframe is running or
# bending the OTHER way, domTF does not hold the finishers.
# MY CHOICES, not Joe's: "bearish posture" = the existing opposite-direction state is momo or curl;
# "matryoshka lines" = every timeframe shorter than the longest supporter; ONE opposing line is
# enough. Found on 08-04 03:53:00, where ws27r bends up while ws9r/ws10r/ws12r/ws13r/ws14r run
# down. Joe named ws15r/16r/17r/18r there; those read `none` both ways, so the machinery cannot
# see them — what he is reading on those is an 11 to 20 point fall from a peak 45-53 min earlier.

# TOP_TF_VETO (longest supporter shorter than longest opposer) was built 0813 and SUPERSEDED the
# same day by NESTED_OPPOSITION below, which is the rule Joe specified. It is not in the code.

LINES = ([f'{g}{s}' for g in ('gcws15', 'gcws30') for s in ('b', 'm', 'Mage', 'r')]
         + [f'ws1{s}' for s in ('b', 'm', 'Mage', 'r')])
HANDI = set(f'{g}{s}' for g in ('gcws15', 'gcws30') for s in ('b', 'm', 'Mage'))
COL = {n: 'wsf_' + n.replace('gcws', 'g') for n in LINES}
X_SPEC = dict(length=5, mult=0.35, src='close')   # the fast partner. Identical at every timeframe
#                                                   that has one in indicator_configs.

# THE g30 MARKER SIGNAL. Joe 0813, verbatim: "confirmed b crossing from oob to ib, with an xwob".
# XWOB only — no OOBW dwell filter, no ws1 gate. ws_strat.candidates() is exactly that.
G30_LEVEL = 'g30_marker'          # Joe 0813 named it
XWOB = 2

# THE WINDOW. Joe named 08-04 00:00:00 -> 12:22:00 for the report. Both ends stamped on every row.
START = dt.datetime(2026, 8, 4, 0, 0, 0, tzinfo=timezone.utc)
END = dt.datetime(2026, 8, 5, 0, 0, 0, tzinfo=timezone.utc)   # Joe 0813: extend to 08-05 00:00

u = lambda t: dt.datetime.fromtimestamp(int(t) / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

DDL = '''CREATE TABLE IF NOT EXISTS ws_fin_9of12 (
    wsf_pk        BIGINT AUTO_INCREMENT PRIMARY KEY,
    wsf_created   DATETIME DEFAULT CURRENT_TIMESTAMP,
    wsf_n         SMALLINT NOT NULL,     -- WSF_N, votes needed. 9 of 12
    wsf_handicap  SMALLINT NOT NULL,     -- WSF_HANDICAP 0 => gcws b/m/Mage vote at hi/lo
    wsf_hold      SMALLINT NOT NULL,     -- WSF_VOTE_HOLD. 0 = off
    wsf_sticky    SMALLINT NOT NULL,     -- WSF_VOTE_STICKY. 0 = off
    wsf_hi        DOUBLE NOT NULL, wsf_lo DOUBLE NOT NULL,
    wsf_win_from  VARCHAR(19) NOT NULL, wsf_win_to VARCHAR(19) NOT NULL,
    wsf_g30_level VARCHAR(20) NOT NULL,  -- Joe 0813: g30_marker = confirmed b oob->ib + xwob
    wsf_require   VARCHAR(64) NOT NULL,  -- lines that MUST vote. Joe 0813: gcws30b
    wsf_line_xwob VARCHAR(64) NOT NULL,  -- per-line hold. Joe 0813: ws1Mage:4, ws1b:4 (4 bars = 20 s)
    wsf_ms        BIGINT NOT NULL,       -- THE SIGNAL BAR = the g30 bar
    wsf_utc       VARCHAR(19) NOT NULL,
    wsf_qual_ms   BIGINT NOT NULL,       -- the 9of12 qualification bar that armed it
    wsf_qual_utc  VARCHAR(19) NOT NULL,
    wsf_wait_s    INT NOT NULL,          -- qual -> signal, seconds
    wsf_absorbed  SMALLINT NOT NULL,     -- earlier qualifications replaced before this one fired
    wsf_side      TINYINT NOT NULL,      -- +1 = 9+ OOB-HIGH at qual bar, -1 = OOB-LOW
    wsf_hi_n      SMALLINT NOT NULL, wsf_lo_n SMALLINT NOT NULL, wsf_n_side SMALLINT NOT NULL,
    wsf_g30_side  TINYINT NOT NULL,      -- the g30 crossing's own side
    wsf_g30_dwell INT NOT NULL,          -- its OOB dwell in 5 s bars
    wsf_voters    VARCHAR(255) NOT NULL, wsf_abstain VARCHAR(255) NOT NULL,
    -- domTF, evaluated AT THE SIGNAL BAR at dr = wsf_side. TF8..33, window K_WINDOW x TF minutes
    wsf_domtf     VARCHAR(8) NOT NULL,   -- FREE | BLOCKED
    wsf_domtf_tfs VARCHAR(255),          -- the TFs in momo|curl, empty when FREE
    -- the handover knobs. IN THE UNIQUE KEY: changing one produces a different walk, and both
    -- walks must be able to sit in the table at once for an A/B.
    wsf_stall_n     SMALLINT NOT NULL DEFAULT 0,   -- STALL_N, lattice samples with no new extreme
    wsf_ho_xwob     SMALLINT NOT NULL DEFAULT 0,   -- HANDOVER_XWOB, grid bars the fast partner holds
    wsf_curl_tfbars SMALLINT NOT NULL DEFAULT 0,   -- CURL_RECENCY_TF_BARS, bars of the line's own TF
    wsf_htf_band    VARCHAR(8) NOT NULL DEFAULT '',-- DOMTF_HTF_BAND, e.g. 22-27
    -- the handover: the bar the domTF turn ends. jig.domtf_handover
    wsf_ho_utc    VARCHAR(19),           -- NULL when domTF is FREE at the signal
    wsf_ho_min    DOUBLE,                -- signal -> handover, minutes
    wsf_ho_tf     SMALLINT NOT NULL DEFAULT 0,   -- the line that ended the turn
    wsf_ho_how    VARCHAR(6),            -- cross | stall
    wsf_htf_curl  VARCHAR(64),           -- lines in the 22-27 band that recently curled into the
    --                                      move; when non-empty the race was restricted to them
    wsf_ho_pool   VARCHAR(64),           -- the lines that were actually in the race
    -- the twelve line values AT THE QUALIFICATION BAR
    wsf_g15b      DOUBLE, wsf_g15m    DOUBLE, wsf_g15Mage DOUBLE, wsf_g15r DOUBLE,
    wsf_g30b      DOUBLE, wsf_g30m    DOUBLE, wsf_g30Mage DOUBLE, wsf_g30r DOUBLE,
    wsf_ws1b      DOUBLE, wsf_ws1m    DOUBLE, wsf_ws1Mage DOUBLE, wsf_ws1r DOUBLE,
    wsf_v_g15b    TINYINT, wsf_v_g15m TINYINT, wsf_v_g15Mage TINYINT, wsf_v_g15r TINYINT,
    wsf_v_g30b    TINYINT, wsf_v_g30m TINYINT, wsf_v_g30Mage TINYINT, wsf_v_g30r TINYINT,
    wsf_v_ws1b    TINYINT, wsf_v_ws1m TINYINT, wsf_v_ws1Mage TINYINT, wsf_v_ws1r TINYINT,
    UNIQUE KEY uq_wsf (wsf_n, wsf_handicap, wsf_hold, wsf_sticky, wsf_g30_level,
                       wsf_stall_n, wsf_ho_xwob, wsf_curl_tfbars, wsf_htf_band, wsf_ms),
    KEY (wsf_ms), KEY (wsf_side), KEY (wsf_domtf))'''

WALK_DDL = '''CREATE TABLE IF NOT EXISTS ws_fin_walk (
    wfw_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    -- THE REPORT, one row per printed line, columns as printed. A render of ws_fin_9of12 written
    -- in the same pass, so it cannot drift from the walk it renders.
    -- the knob identity. Same rule as ws_fin_9of12: every knob that changes the rows is in the key.
    wfw_n_lines     SMALLINT NOT NULL,      -- WSF_N, lines that must qualify. 9 of 12
    wfw_handicap    SMALLINT NOT NULL,      -- WSF_HANDICAP, points off the boundary. 0
    wfw_hold        SMALLINT NOT NULL,      -- WSF_VOTE_HOLD. 0 = off
    wfw_sticky      SMALLINT NOT NULL,      -- WSF_VOTE_STICKY. 0 = off
    wfw_g30_level   VARCHAR(20) NOT NULL,   -- G30_LEVEL. g30_marker
    wfw_stall_n     SMALLINT NOT NULL,      -- STALL_N, lattice samples with no new extreme. 6
    wfw_ho_xwob     SMALLINT NOT NULL,      -- HANDOVER_XWOB, grid bars the fast partner holds. 4
    wfw_curl_tfbars SMALLINT NOT NULL,      -- CURL_RECENCY_TF_BARS, bars of the line's own TF. 2
    wfw_htf_band    VARCHAR(8) NOT NULL,    -- DOMTF_HTF_BAND. 22-27
    wfw_win_from    VARCHAR(19) NOT NULL, wfw_win_to VARCHAR(19) NOT NULL,
    -- the printed columns, left to right
    wfw_row         SMALLINT NOT NULL,      -- #, position in the chronological walk
    wfw_g30_marker  VARCHAR(19) NOT NULL,   -- g30_marker, the signal bar
    wfw_qual        VARCHAR(19) NOT NULL,   -- qual, the 9of12 qualification bar
    wfw_wait_s      INT NOT NULL,           -- wait, qual to signal, seconds
    wfw_side        VARCHAR(5) NOT NULL,    -- side, LONG or SHORT
    wfw_n           SMALLINT NOT NULL,      -- n, lines qualifying on the signal's side
    wfw_abs         SMALLINT NOT NULL,      -- abs, earlier qualifications replaced before this one
    wfw_domtf       VARCHAR(8) NOT NULL,    -- domTF, FREE or BLOCKED
    wfw_max_tf      SMALLINT NOT NULL,      -- max TF, longest blocking line. 0 when FREE
    wfw_hands_over  VARCHAR(24) NOT NULL,   -- domTF hands over, as printed. empty when FREE
    wfw_min         DOUBLE,                 -- +min, signal to handover, minutes. NULL when FREE
    UNIQUE KEY uq_wfw (wfw_n_lines, wfw_handicap, wfw_hold, wfw_sticky, wfw_g30_level,
                       wfw_stall_n, wfw_ho_xwob, wfw_curl_tfbars, wfw_htf_band, wfw_row),
    KEY (wfw_g30_marker), KEY (wfw_domtf))'''

WALK_COLS = ['wfw_n_lines', 'wfw_handicap', 'wfw_hold', 'wfw_sticky', 'wfw_g30_level',
             'wfw_stall_n', 'wfw_ho_xwob', 'wfw_curl_tfbars', 'wfw_htf_band',
             'wfw_win_from', 'wfw_win_to', 'wfw_row', 'wfw_g30_marker', 'wfw_qual', 'wfw_wait_s',
             'wfw_side', 'wfw_n', 'wfw_abs', 'wfw_domtf', 'wfw_max_tf', 'wfw_hands_over',
             'wfw_min']


VCOLS = [COL[n] for n in LINES]
FCOLS = ['wsf_v_' + COL[n][4:] for n in LINES]
COLS = (['wsf_n', 'wsf_handicap', 'wsf_hold', 'wsf_sticky', 'wsf_hi', 'wsf_lo',
         'wsf_win_from', 'wsf_win_to', 'wsf_g30_level', 'wsf_require', 'wsf_line_xwob',
         'wsf_ms', 'wsf_utc',
         'wsf_qual_ms', 'wsf_qual_utc', 'wsf_wait_s', 'wsf_absorbed', 'wsf_side',
         'wsf_hi_n', 'wsf_lo_n', 'wsf_n_side', 'wsf_g30_side', 'wsf_g30_dwell',
         'wsf_voters', 'wsf_abstain', 'wsf_domtf', 'wsf_domtf_tfs',
         'wsf_stall_n', 'wsf_ho_xwob', 'wsf_curl_tfbars', 'wsf_htf_band',
         'wsf_ho_utc', 'wsf_ho_min', 'wsf_ho_tf', 'wsf_ho_how',
         'wsf_htf_curl', 'wsf_ho_pool'] + VCOLS + FCOLS)


AB = '--ab' in sys.argv     # print the restricted vs unrestricted race, write nothing


def main():
    db = DatabaseManager(**get_db_config())
    db.connect()
    sysr = db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l, hi_boundary h, '
                      'lo_boundary lo FROM optimus9_system WHERE sys_pk=1', fetch=True)[0]
    HI, LO = float(sysr['h']), float(sysr['lo'])
    ls = LineStore(db)
    ovr = {n: (*ls.resolve(n), ls.value_mode(n)) for n in set(LINES + list(WS.LINES))}
    for tf in DOMTF_TFS:
        ovr[f'r{tf}'] = override(tf * 60, KLine(**B.R_SPEC), 'emerging')
        ovr[f'x{tf}'] = override(tf * 60, BBLine(**X_SPEC), 'emerging')
    J = cache_jig_perline(END_MS, HOURS, WARMUP, ovr,
                          pxs_cfg={'src': sysr['s'], 'len': sysr['l']}, rebuild=False)
    ts = np.asarray(J.ts)
    W = J.W
    V = {n: np.asarray(W.line(n), float) for n in LINES}
    R = {tf: np.asarray(W.line(f'r{tf}'), float) for tf in DOMTF_TFS}
    Xl = {tf: np.asarray(W.line(f'x{tf}'), float) for tf in DOMTF_TFS}
    # the fast partner must cross to the far side of its r line and hold HANDOVER_XWOB bars, and
    # the r line must be back inside the boundaries. One mask per line per direction.
    def _runlen(m):
        m = np.asarray(m, bool); out = np.zeros(len(m), np.int64); c = 0
        for i in range(len(m)):
            c = c + 1 if m[i] else 0
            out[i] = c
        return out
    CROSS = {+1: {tf: _runlen(Xl[tf] < R[tf]) >= HANDOVER_XWOB for tf in DOMTF_TFS},
             -1: {tf: _runlen(Xl[tf] > R[tf]) >= HANDOVER_XWOB for tf in DOMTF_TFS}}
    INSIDE = {tf: (R[tf] > LO) & (R[tf] < HI) for tf in DOMTF_TFS}

    i0 = int(np.searchsorted(ts, int(START.timestamp() * 1000)))
    i1 = int(np.searchsorted(ts, int(END.timestamp() * 1000)))
    # the stall, asked at every bar of every domTF line, on that line's own momentum lattice
    LAT = {}
    for tf in DOMTF_TFS:
        with momo_window(B.K_WINDOW * tf):
            LAT[tf] = (int(MC.MOMO_STEP_BARS), int(MC.MOMO_SAMPLES))
    STALL = {dr: {tf: stall_mask(R[tf], dr, STALL_N, *LAT[tf]) for tf in DOMTF_TFS}
             for dr in (+1, -1)}
    print('  lattice  ' + '  '.join(f'{tf}:{LAT[tf][0]}x{LAT[tf][1]}' for tf in DOMTF_TFS), flush=True)

    # the curl, asked at every bar of the HTF band only. Joe 0814: "IF a domTF HTF has recently
    # {knob:2 TF bars} curled towards dr". CURLED[dr][tf][i] = curl into dr somewhere in the last
    # CURL_RECENCY_TF_BARS bars OF THAT LINE'S OWN TIMEFRAME.
    HTFS = [tf for tf in DOMTF_TFS if DOMTF_HTF_BAND[0] <= tf <= DOMTF_HTF_BAND[1]]
    CURLED = {+1: {}, -1: {}}
    for tf in HTFS:
        back = int(CURL_RECENCY_TF_BARS * tf * 12)      # 2 TF bars -> grid bars
        with momo_window(B.K_WINDOW * tf):
            for dr in (+1, -1):
                c = np.zeros(len(ts), bool)
                for i in range(i0 - back, i1 + 1):
                    if i >= 0:
                        c[i] = momo_g(R[tf], dr, i)[0] == 'curl'
                CURLED[dr][tf] = np.array(
                    [c[max(0, i - back):i + 1].any() for i in range(len(ts))], bool)
        print(f'  curl recency ws{tf}r  {back} bars = {back / 12:.0f} min   '
              f'in window: +1 {int(CURLED[1][tf][i0:i1 + 1].sum())} bars  '
              f'-1 {int(CURLED[-1][tf][i0:i1 + 1].sum())}', flush=True)


    # THE g30 CLOCK — candidate level, computed from cache bar 0 so a dwell may start before i0
    cand = WS.candidates(np.asarray(W.line('gcws30b'), float), HI, LO, XWOB,
                         min_ib=WS.MIN_IB_DWELL)
    G = {int(e['conf']): e for e in cand}
    g30_pairs = sorted((b, int(G[b]['side'])) for b in G)
    print(f'g30 marker signals: {len(g30_pairs):,} on the tape, '
          f'{sum(1 for b, _ in g30_pairs if i0 <= b <= i1):,} in the window', flush=True)

    ev, q = ws_fin_9of12(W, HI, LO, g30_pairs, i0=i0, i1=i1)
    print(f'{len(ev):,} ws_fin_9of12 signals   '
          f'hi {sum(1 for e in ev if e["side"] > 0)}  lo {sum(1 for e in ev if e["side"] < 0)}',
          flush=True)
    print(f'knobs: WSF_N {WSF_N} | WSF_HANDICAP {WSF_HANDICAP} | VOTE_HOLD {WSF_VOTE_HOLD} | '
          f'VOTE_STICKY {WSF_VOTE_STICKY} | hi {HI:.0f} / lo {LO:.0f}', flush=True)

    rows, ab, rep = [], [], {}
    for e in ev:
        w, qb, sd = e['bar'], e['qual_bar'], e['side']
        vals, flags, voted, absent = [], [], [], []
        for n in LINES:
            v = float(V[n][qb])
            h_, l_ = (HI - WSF_HANDICAP, LO + WSF_HANDICAP) if n in HANDI else (HI, LO)
            ok = (v >= h_) if sd > 0 else (v <= l_)
            vals.append(v)
            flags.append(int(ok))
            (voted if ok else absent).append(n)
        blk, opp = [], []
        for tf in DOMTF_TFS:                    # domTF, at the SIGNAL bar, dr = the event side
            with momo_window(B.K_WINDOW * tf):
                st, _s, _r2, _r = momo_g(R[tf], sd, w)
                op, _s2, _r22, _r3 = momo_g(R[tf], -sd, w)
            if st in ('momo', 'curl'):
                blk.append(tf)
            if op in ('momo', 'curl'):
                opp.append(tf)
            elif RESCUE_REJECTED_CURL:
                with momo_window(B.K_WINDOW * tf):        # a bend found FOR the move, then rejected
                    raw, rsl, _r2, _rw = MC.momo(R[tf], sd, w)
                    if raw == 'curl' and st == 'none':
                        nb = MC.MOMO_WINDOW_MIN * 12
                        yy = R[tf][w - nb + 1:w + 1] if w - nb + 1 >= 0 else None
                        if yy is not None and np.isfinite(yy).all():
                            qa = np.polyfit(np.linspace(0.0, 1.0, len(yy)), yy, 2)[0]
                            aligned = (rsl > 0) if sd > 0 else (rsl < 0)
                            curved = (qa > 0) if sd > 0 else (qa < 0)
                            if not aligned or not curved:   # the bend points the OTHER way
                                opp.append(tf)
        if NESTED_OPPOSITION and blk and \
                sum(1 for o in opp if o < max(blk)) >= NESTED_OPPOSITION_MIN:
            blk = []                            # a nested shorter line has taken the other side
        # THE HANDOVER. Only a blocked signal has a turn to wait out.
        ho_i = ho_tf = 0; ho_how = None; curled = []; pool = []
        if blk:
            curled = [tf for tf in HTFS if CURLED[sd][tf][w]]
            ho_i, ho_tf, ho_how = domtf_handover(
                blk, curled, DOMTF_HTF_BAND, CROSS[sd], INSIDE,
                lambda tf, i: bool(STALL[sd][tf][i]), w, i1)
            band = [tf for tf in blk if DOMTF_HTF_BAND[0] <= tf <= DOMTF_HTF_BAND[1]]
            pool = band if (curled and band) else list(blk)

        if AB and blk:      # diagnostic only, never stored: the race WITHOUT the HTF restriction
            f_i, f_tf, f_how = domtf_handover(blk, [], DOMTF_HTF_BAND, CROSS[sd], INSIDE,
                                              lambda tf, i: bool(STALL[sd][tf][i]), w, i1)
            ab.append((len(rows) + 1, u(ts[w])[11:], curled, pool, f_i, f_tf, f_how,
                       ho_i, ho_tf, ho_how))

        rep[w] = {'blk': list(blk), 'ho_i': ho_i, 'ho_tf': ho_tf, 'ho_how': ho_how}

        g = G[w]
        rows.append(tuple([WSF_N, WSF_HANDICAP, WSF_VOTE_HOLD, WSF_VOTE_STICKY, HI, LO,
                           u(ts[i0]), u(ts[i1]), G30_LEVEL, ','.join(WSF_REQUIRE),
                           ','.join(f'{k}:{v}' for k, v in sorted(WSF_LINE_XWOB.items())),
                           int(ts[w]), u(ts[w]), int(ts[qb]), u(ts[qb]),
                           int((int(ts[w]) - int(ts[qb])) / 1000), e['absorbed'], sd,
                           e['hi_n'], e['lo_n'], e['hi_n'] if sd > 0 else e['lo_n'],
                           int(g['side']), int(g['oob']),
                           ','.join(voted)[:255], ','.join(absent)[:255],
                           'BLOCKED' if blk else 'FREE',
                           ','.join(str(t) for t in blk)[:255],
                           STALL_N, HANDOVER_XWOB, CURL_RECENCY_TF_BARS,
                           f'{DOMTF_HTF_BAND[0]}-{DOMTF_HTF_BAND[1]}',
                           u(ts[ho_i]) if ho_i else None,
                           (int(ts[ho_i]) - int(ts[w])) / 60000.0 if ho_i else None,
                           int(ho_tf), ho_how,
                           ','.join(str(t) for t in curled)[:64],
                           ','.join(str(t) for t in pool)[:64]] + vals + flags))

    if AB:
        print(f"\n  the HTF-curl restriction. {len(ab)} blocked signals, "
              f"{sum(1 for a in ab if a[2])} restricted\n")
        print("     #  g30_marker  22-27 curled   first past the post      restricted to the band"
              "     later by")
        ch = 0
        for n_, t_, cu, po, fi, ftf, fh, hi_, htf, hh in ab:
            if not cu:
                continue
            d = (int(ts[hi_]) - int(ts[fi])) / 60000.0 if (hi_ and fi) else None
            ch += bool(d)
            print(f"  {n_:>4}  {t_}  {','.join(str(x) for x in cu):<13} "
                  f"{(u(ts[fi])[11:] + ' ws' + str(ftf) + 'r ' + fh) if fi else 'none':<24}"
                  f"{(u(ts[hi_])[11:] + ' ws' + str(htf) + 'r ' + hh) if hi_ else 'none':<26}"
                  f"{d:>+8.1f}m" if d is not None else "")
        print(f"\n  changed the handover bar on {ch} of {sum(1 for a in ab if a[2])} restricted")
        return 0

    db.execute(DDL)
    # SCHEMA MOVED 0813 — the object changed from the qualification to the combined signal, so the
    # table gains g30 / qual / domTF columns. ADD COLUMN keeps an existing table's rows.
    have = {r['Field'] for r in db.execute('SHOW COLUMNS FROM ws_fin_9of12', fetch=True)}
    ADD = [('wsf_g30_level', "VARCHAR(20) NOT NULL DEFAULT ''"),
           ('wsf_require', "VARCHAR(64) NOT NULL DEFAULT ''"),
           ('wsf_line_xwob', "VARCHAR(64) NOT NULL DEFAULT ''"),
           ('wsf_qual_ms', 'BIGINT NOT NULL DEFAULT 0'),
           ('wsf_qual_utc', "VARCHAR(19) NOT NULL DEFAULT ''"),
           ('wsf_wait_s', 'INT NOT NULL DEFAULT 0'),
           ('wsf_absorbed', 'SMALLINT NOT NULL DEFAULT 0'),
           ('wsf_g30_side', 'TINYINT NOT NULL DEFAULT 0'),
           ('wsf_g30_dwell', 'INT NOT NULL DEFAULT 0'),
           ('wsf_domtf', "VARCHAR(8) NOT NULL DEFAULT ''"),
           ('wsf_domtf_tfs', 'VARCHAR(255)'),
           ('wsf_stall_n', 'SMALLINT NOT NULL DEFAULT 0'),
           ('wsf_ho_xwob', 'SMALLINT NOT NULL DEFAULT 0'),
           ('wsf_curl_tfbars', 'SMALLINT NOT NULL DEFAULT 0'),
           ('wsf_htf_band', "VARCHAR(8) NOT NULL DEFAULT ''"),
           ('wsf_ho_utc', 'VARCHAR(19)'), ('wsf_ho_min', 'DOUBLE'),
           ('wsf_ho_tf', 'SMALLINT NOT NULL DEFAULT 0'), ('wsf_ho_how', 'VARCHAR(6)'),
           ('wsf_htf_curl', 'VARCHAR(64)'), ('wsf_ho_pool', 'VARCHAR(64)')]
    for nm, spec in ADD:
        if nm not in have:
            db.execute(f'ALTER TABLE ws_fin_9of12 ADD COLUMN {nm} {spec}')
            print(f'  + column {nm}', flush=True)

    # the 122 rows written earlier today hold the QUALIFICATION, which is no longer the event.
    # They carry wsf_g30_level = '' and are removed by this DELETE, same knob-keyed pattern as
    # build_momo_landed / build_handoff.
    # DELETE KEYED ON THE KNOBS AND THE g30 LEVEL, NOT THE WINDOW. The table's unique key is
    # (n, handicap, hold, sticky, g30_level, ms) and carries no window column, so a delete keyed on
    # the window leaves the previous run's rows in place and the insert collides. A window change
    # supersedes the earlier rows rather than sitting alongside them.
    # keyed on the knobs, not the window — the unique key is not the window. Every knob in the
    # key is here, so a run at a different STALL_N lands alongside instead of on top.
    db.execute('DELETE FROM ws_fin_9of12 WHERE wsf_n=%s AND wsf_handicap=%s AND wsf_hold=%s '
               'AND wsf_sticky=%s AND wsf_g30_level=%s AND wsf_stall_n=%s AND wsf_ho_xwob=%s '
               'AND wsf_curl_tfbars=%s AND wsf_htf_band=%s',
               (WSF_N, WSF_HANDICAP, WSF_VOTE_HOLD, WSF_VOTE_STICKY, G30_LEVEL,
                STALL_N, HANDOVER_XWOB, CURL_RECENCY_TF_BARS,
                f'{DOMTF_HTF_BAND[0]}-{DOMTF_HTF_BAND[1]}'))
    if rows:
        db.executemany(f'INSERT INTO ws_fin_9of12 ({",".join(COLS)}) VALUES '
                       f'({",".join(["%s"] * len(COLS))})', rows)
    print(f'ws_fin_9of12 : {len(rows):,} rows, {len(COLS)} stamped columns', flush=True)

    # THE REPORT AS A TABLE. Same pass, same values, so it cannot drift from the walk above.
    # EVERY row of the walk, FREE and BLOCKED. Cutting to the blocked rows would be a truncation
    # nobody asked for, and the blocked rows are one WHERE clause away.
    band = f'{DOMTF_HTF_BAND[0]}-{DOMTF_HTF_BAND[1]}'
    ident = [WSF_N, WSF_HANDICAP, WSF_VOTE_HOLD, WSF_VOTE_STICKY, G30_LEVEL,
             STALL_N, HANDOVER_XWOB, CURL_RECENCY_TF_BARS, band]
    wrows = []
    for k, e in enumerate(ev, 1):
        w, qb, sd = e['bar'], e['qual_bar'], e['side']
        blk_s = rep[w]['blk']
        mx = max(blk_s) if blk_s else 0
        ho = (f"{u(ts[rep[w]['ho_i']])[11:]} ws{rep[w]['ho_tf']}r {rep[w]['ho_how']}"
              if rep[w]['ho_i'] else '')
        wrows.append(tuple(ident + [
            u(ts[i0]), u(ts[i1]), k, u(ts[w]), u(ts[qb]),
            int((int(ts[w]) - int(ts[qb])) / 1000),
            'SHORT' if sd > 0 else 'LONG',
            e['hi_n'] if sd > 0 else e['lo_n'], e['absorbed'],
            'BLOCKED' if blk_s else 'FREE', mx, ho,
            (int(ts[rep[w]['ho_i']]) - int(ts[w])) / 60000.0 if rep[w]['ho_i'] else None]))
    db.execute(WALK_DDL)
    db.execute('DELETE FROM ws_fin_walk WHERE wfw_n_lines=%s AND wfw_handicap=%s AND wfw_hold=%s '
               'AND wfw_sticky=%s AND wfw_g30_level=%s AND wfw_stall_n=%s AND wfw_ho_xwob=%s '
               'AND wfw_curl_tfbars=%s AND wfw_htf_band=%s', tuple(ident))
    db.executemany(f'INSERT INTO ws_fin_walk ({",".join(WALK_COLS)}) VALUES '
                   f'({",".join(["%s"] * len(WALK_COLS))})', wrows)
    print(f'ws_fin_walk  : {len(wrows):,} rows, {len(WALK_COLS)} stamped columns', flush=True)

    # keyed on THIS run's knobs. Without them the count sums every walk in the table.
    r = db.execute('SELECT wsf_domtf d, COUNT(*) n, SUM(wsf_side=1) hi, SUM(wsf_side=-1) lo '
                   'FROM ws_fin_9of12 WHERE wsf_g30_level=%s AND wsf_stall_n=%s AND wsf_ho_xwob=%s '
                   'AND wsf_curl_tfbars=%s AND wsf_htf_band=%s GROUP BY 1',
                   (G30_LEVEL, STALL_N, HANDOVER_XWOB, CURL_RECENCY_TF_BARS,
                    f'{DOMTF_HTF_BAND[0]}-{DOMTF_HTF_BAND[1]}'), fetch=True)
    print('\nby domTF verdict:')
    for x in r:
        print(f"  {x['d']:<8} {x['n']:>4}   hi {int(x['hi'])}  lo {int(x['lo'])}")
    db.disconnect()


if __name__ == '__main__':
    sys.exit(main())
