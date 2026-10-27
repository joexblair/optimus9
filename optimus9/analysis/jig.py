"""jig.py — the test-jig facade (Joe 0707). ONE object over a pinned window that exposes the STANDARD test
requirements, so analysis scripts stop hand-rolling what the engine already packages (the recurring drift tax:
fin_unlatch, s_qualify, lr_walk mfe_side, MAE-to-exit-vs-swing).

TWO namespaces — the split is the guardrail, not tidiness:
  jig.causal.*  — LIVE-LEGAL. Everything a strategy may use (klines, lines, finishers, arm/gate events, predict,
                  coarse-sample, curl). Every method DELEGATES to the real producer; it never re-implements logic.
  jig.score.*   — HARNESS / SCORING, NON-CAUSAL. find_pivots swings, lr_walk entry-quality (mae/mfe-to-swing +
                  mfe_side), report + pine emit. Reaching for jig.score.* inside a strategy is the tell you've
                  crossed into look-ahead.

DELEGATION RULE (absolute): the jig only CALLS existing producers. If something isn't packaged yet, split the
producer first, then expose it here — never fork the logic into the jig.

LINE CONFIGS — build them BY NAME (kline/bbline below). Joe's notation is k_len|rsi|stc|src; the DB tuple is
('k', rsi, stc, k_len, src) — a DIFFERENT order, and transposing it is SILENT (the line still computes and is a
DIFFERENT line: TV-verified MAE 0.03 right, 9.33 transposed). optimus9.compute.line_config is the only module
that knows the layout. If you are typing ('k', ...) you are doing it wrong.
"""
import copy
import os
import numpy as np
import bias_machine as bm
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.lr import lr_config, lr_walk
from optimus9.analysis.lr_v2 import (s_qualify, s_qualify_parts, v2_arm, gate_open, _mage_rev, _rolling_any,
                                     _curl_detect, fin_unlatch_nof9, fin_box_qualified)
from optimus9.compute.breaching_line import predict_breach, FENCE_HI, FENCE_LO
from optimus9.compute.line_config import KLine, BBLine, override as _override   # noqa: F401
from optimus9.compute.indicator_computer import IndicatorComputer as IC   # px_smooth's DEMA
from optimus9.compute.swing_detect import find_pivots, legs, swing_mask
from sweep_eval import BASE_BIAS


def kline(name, tf_min, *, k_len, rsi, stc, src='close', value_mode='emerging'):
    """A K-line override, BY NAME. The only sanctioned way to build one — you cannot transpose it.

        overrides = {**kline('s45r', 45, k_len=7, rsi=5, stc=7, src='ohlc4')}
        with Jig(end_ms, hours=24, overrides=overrides) as j: ...

    Joe's notation is k_len | rsi | stc | src; the DB tuple is ('k', rsi, stc, k_len, src) — REVERSED, and
    transposing it is SILENT (the line still computes, and is a different line: TV MAE 0.03 vs 9.33).
    optimus9.compute.line_config is the only module that knows that. Nothing else may hand-build a tuple."""
    return {name: _override(tf_min * 60, KLine(k_len=k_len, rsi=rsi, stc=stc, src=src), value_mode)}


def bbline(name, tf_min, *, length, mult, src='close', value_mode='emerging'):
    """A Bollinger-position override, BY NAME. Notation and tuple agree here (length|mult|src), but this is
    the one door so a caller never has to know which configs are safe to hand-build and which are not."""
    return {name: _override(tf_min * 60, BBLine(length=length, mult=mult, src=src), value_mode)}


# ── EMERGING BAR GRID (Joe 0806) ────────────────────────────────────────────────────────────────
# "build the capacity to set the emerging bar size by choosing a fraction: 1/{12,6,5,4,3,2}".
# The fraction is of ONE MINUTE, so the grid is 60/frac seconds:
#     1/12 = 5s (the base grid) | 1/6 = 10s | 1/5 = 12s | 1/4 = 15s | 1/3 = 20s | 1/2 = 30s
# Everything in the project is computed on the 5s grid; these producers COARSEN it. A coarse bar's
# EMERGING value is the value at its LAST constituent 5s bar — the same "what realtime sees" rule
# indicator_value_modes calls 'emerging'. Causal: a coarse bar never reads past its own last 5s bar.
BAR_FRACTIONS = (12, 6, 5, 4, 3, 2)          # of one minute
FRAC_SECONDS = {f: 60 // f for f in BAR_FRACTIONS}


def emerging_grid(ts, frac):
    """(bucket_id per 5s bar, index of each bucket's LAST 5s bar). frac from BAR_FRACTIONS.

    Buckets are wall-clock aligned on the epoch, so a 15s bucket always starts at :00/:15/:30/:45 —
    the same seam the pine emit floors onto. A trailing partial bucket keeps its last seen bar."""
    if frac not in FRAC_SECONDS:
        raise ValueError(f'frac {frac!r} not in {BAR_FRACTIONS}')
    ms = FRAC_SECONDS[frac] * 1000
    ts = np.asarray(ts, np.int64)
    bid = ts // ms
    last = np.flatnonzero(np.r_[bid[1:] != bid[:-1], True])   # last 5s bar of each bucket
    return bid, last


def coarsen(line, ts, frac):
    """A 5s-grid array sampled onto the emerging bar grid: one value per coarse bar, taken at that
    bar's LAST 5s bar. Returns (values, index-into-ts). The consumer counts wob in COARSE bars."""
    _, last = emerging_grid(ts, frac)
    return np.asarray(line, float)[last], last


def px_smooth(ts, px, evt=None, length=2, frac=12):
    """[PRODUCER · Joe 0806] px_smooth on an emerging bar grid of 60/frac seconds, returned on the
    FULL 5s grid (forward-filled), so it drops in wherever the 5s px_smooth is used today.

        ts      5s-grid timestamps, ms
        px      the price source on the 5s grid (close)
        evt     event mask (volume > 0). A coarse bar is an event bar if ANY of its 5s bars traded —
                the filler-invisible rule carried up a level. None = every bar is an event bar.
        length  DEMA length in COARSE bars (optimus9_system.pxsmooth_dema_len, currently 2)
        frac    BAR_FRACTIONS member. 12 -> 5s reproduces the existing behaviour.

    Producer = IC.dema, as rpl_cache._px_smooth_evt uses. No fork."""
    ts = np.asarray(ts, np.int64); px = np.asarray(px, float)
    bid, last = emerging_grid(ts, frac)
    cpx = px[last]                                            # emerging close of each coarse bar
    if evt is not None:
        evt = np.asarray(evt, bool)
        cev = np.zeros(len(last), bool)                       # any 5s bar in the bucket traded
        np.logical_or.at(cev, np.searchsorted(bid[last], bid), evt)
    else:
        cev = np.ones(len(last), bool)
    out = np.full(len(cpx), np.nan)
    ei = np.flatnonzero(cev & np.isfinite(cpx))
    if len(ei):
        out[ei] = IC.dema(cpx[ei], int(length))
    m = np.isfinite(out)                                      # ffill across non-event coarse bars
    if m.any():
        ix = np.where(m, np.arange(len(out)), 0); np.maximum.accumulate(ix, out=ix)
        out = out[ix]; out[:int(np.argmax(m))] = out[int(np.argmax(m))]
    return out[np.searchsorted(bid[last], bid)]               # back onto the full 5s grid


def mage_ladder_diff(mg, j, off_a, off_b, tfs):
    """[PRODUCER - Joe 1016] THE SECOND DIFFERENCE ACROSS A MAGE LADDER, in points.

    JOE'S OBSERVATION, 1016, which is the whole mechanic: *"can you see that T23's 10 diff is
    noticably higher the its 7.5 diff, while the T50's 10 diff is near or slightly lower than its
    7.5 diff?"* - measured on 2026-07-22, T23 = 00:23 and T50 = 01:08, across ws30 down to ws1 at
    step 1 (*"all TFs, thanks. step=1"*). The two populations were DISJOINT on all 30 lines: T23
    +2.95 to +9.11, T50 -1.78 to +2.30.

    A RATIO OF THE TWO DIFFS IS REJECTED. It divides by the earlier diff, so a near-zero
    denominator blows it up - at the ws5Mage reversals it spanned -6.12 to +10.37 and separated
    nothing. Joe 1016: *"could ratio be the wrong way to measure this?"* It is. The second
    difference in POINTS is the measure.

    THE OFFSETS ARE THE CALLER'S, and Joe 1016 ruled they should land on a 5-minute seam: *"landing
    on the 5TF seam gives us the most accurate picture of the lines, and keeps us clear of the
    'emerging bar jump at TF seam' issue"*. His own +7.5 min is not a 5-minute multiple; the
    seam-aligned +5/+10 pair separates T23 from T50 completely where +7.5/+10 does not.

      mg       {tf: the Mage line}, on the 5 s grid
      j        the bar the reading is ABOUT
      off_a    the earlier offset, in bars
      off_b    the later offset, in bars
      tfs      the ladder, in the order the caller wants reported

    -> (the median second difference, the count of lines positive, the per-line array)
    CAUSAL WITH A STATED DELAY: this reads j + off_b, so the reading is knowable at j + off_b and
    never earlier. The caller owns that delay.
    """
    d = np.array([mg[t][int(j) + int(off_b)] - mg[t][int(j) + int(off_a)] for t in tfs], float)
    return float(np.median(d)), int((d > 0).sum()), d


# ── mage-cascade (JOE'S NAME, JOE'S MECH) ──────────────────────────────────────────────────────
# Joe 1017 ruled every part of this. His words are here verbatim; read them before changing a line.
#
# THE BAR. *"I'd prefer the cascade to test from a single timestamp taken at the most recent mage
# extrema"* / *"we sample on a single bar, not many bars"*. EVERY line is read at ONE bar.
#   WHAT THIS REPLACES, kept because it was mine and unruled: `_openvote._bucket_close` read each
#   of the 13 lines at its own timeframe's close, so one verdict spanned up to 9 minutes of tape
#   and the lag was not even monotone in TF - at 2026-08-23 18:55:15 ws5Mage was 20 s old while
#   ws4Mage below it was 200 s old. Joe asked *"is this in the mech's spec?"* It was not. The spec
#   (`docs/mage_cascade_findings.md`, `ride_to_max.cascade`) always read ONE bar.
#
# FINDING THE BAR, Joe 1017: *"to find the extrema, look back from the event bar in 4 minute gaps
# until you see an extrema, then step back another 4 minutes to validate the extrema / extrema must
# be same-side as the event's side (not the events' SHORT or LONG verdict)"*, then *"the true max.
# the sample bar has no relevence to mage-cascade - it is point in time to find an extrema in front
# of it"*.
#   so TWO stages: the coarse walk back finds a SAMPLE bar, and the extrema is the line's true
#   extreme FORWARD of it. The 4-minute gap is what kills the noise - a bare slope flip at
#   `WS1MR_REV_WOB` 2 fires on 21.9% of all 1,632,960 tape bars, one every 22.9 s.
#   THE FORWARD SEARCH ENDS AT THE EVENT BAR. STRUCTURAL AND STATED: it is the only bound that
#   invents no window and keeps every read at or before the event bar.
#   ONE EXTREMA, NOT MANY. Joe: *"the whole point of walking back to look forward for the extrema
#   is to confirm the only extrema it can see"*. Checked: from event bars 2026-08-23 19:02:05 and
#   19:05:35 the sample bars differ (18:58:05 and 18:57:35, since the grid is anchored on the event
#   bar) and the extrema is the SAME bar both times - 2026-08-23 18:58:35, ws1Mage 119.14.
#
# THE CLUSTER, Joe 1017: *"mage cascade allows for a subset to print a run at the lower or higher
# end of the wsf TFs. so long as there are 4 or more consecutive TFs printing a rising or falling
# pattern, at the lower end or higher end of wsf range (eg ws1 to ws4), then the cascade's verdict
# is true"* / *"it would start at 1 for a low cluster, or end at TF 12 for a high cluster. clusters
# in the middle (eg from 3 to 7) are discarded"* / *"lower TF runs always outrank the higher TFs in
# the mage cascade"*.
#
# THE BUMPS, Joe 1017: *"this doesn't seem to allow for the bumps. a wider zoom is needed / example
# ws1,ws2,ws3,ws4, ws5 / samples 100, 88, 90, 81, 70 / my read of the current flow would disqualify
# the lower TF verdict, whereas I would mark it is SHORT"*.
#   FOUR candidate mechanics were measured against his example and against four real bars. His
#   example passed ALL FOUR, so it did not discriminate. The real bars split them: a 1-counter-step
#   budget INVERTED the verdict to `up` at 2026-08-23 19:05:35 (the +0.61 bump at ws3->ws4 spends
#   the budget already used on ws1->ws2); a 3-point tolerance and a signed-cumulative test both
#   failed at 19:02:05 and 19:05:35; a 10-point tolerance swallowed all 12 lines on every bar. The
#   wider zoom was the only one stable across all four. Joe then set the width: *"I don't know the
#   width yet - we'll adjust when I'm tuning. keep it tight for now - let it show itself as a
#   misdiagnosis of another trade, then we can adjust the width"*.
#
# NO dr, Joe 1017: *"dr isn't involved. we're taking a snapshot on one bar, making a direction
# verdict (up, down, neither), and providing the verdict for consumption"*. This producer never
# sees a trade side. A consumer maps the direction onto its own side.
#
# THE RANGE, Joe 1017: *"wsf is ws1 to ws12 / sub-wsf is g5 to g30 / dtf is >12"*, and on g30:
# *"g30: printed in the table, not a rung in the cluster walk -confirmed"*. His earlier 1017
# *"add g30 to it as the default mode"* is superseded for the WALK and kept for the PRINT.
MC_GAP   = 48   # bars between coarse samples = 4 min at the 5 s grid. JOE'S OWN NUMBER, 1017.
MC_ZOOM  = 2    # rungs each cluster step compares across. Joe 1017: *"keep it tight for now"* - 2
#                 is the tightest width that admits a bump at all; 1 is the no-bump walk.
MC_MIN   = 4    # lines a cluster must cover. *"4 or more consecutive TFs"*, then *"4 lines"*.
MC_TF_LO = 1    # wsf's floor. A low cluster must START here.
MC_TF_HI = 12   # wsf's ceiling. A high cluster must END here.


def mage_cascade_bar(line, bar, side, mode='extrema', gap=MC_GAP, grid=None):
    """[PRODUCER - Joe 1017] THE ONE BAR the mage cascade reads. -> (bar, why) or None.

      line   the extrema source on the 5 s grid. ws1Mage today - Joe 1017: *"in our current state,
             the most recent mage extrema is captured from ws1Mage"*. The TF is the CALLER'S, so
             his *"future where the TF will need to be dynamic"* needs no change in here.
      bar    the event bar.
      side   the EVENT'S side, +1 high / -1 low. Joe 1017: *"extrema must be same-side as the
             event's side (not the events' SHORT or LONG verdict)"*.
      mode   'extrema'  his walk, then the true extreme forward of the sample bar.
             'grid'     `bar` snapped DOWN to a `grid`-bar lattice. MINE, and Joe 1017 kept it:
                        *"I don't want to discount your grid-width build - it needs further
                        testing, which I'll do when I'm working on the trade list"*. `grid`
                        defaults to `gap`, so the mode carries no number of its own.
             'event'    `bar` itself, the control.

    The walk is UNBOUNDED - it runs back to the start of the tape if it must. No cap, Joe's
    standing rule. Returns None when no same-side turn exists before the tape starts.
    CAUSAL: asserted, not commented - a returned bar may never exceed `bar`.
    """
    line = np.asarray(line, float)
    bar = int(bar)
    side = int(side)
    assert side in (+1, -1), 'side is the EVENT side: +1 high, -1 low'
    gap = int(gap)
    assert gap >= 1, 'the coarse gap is in bars'
    if mode == 'event':
        k, why = bar, 'the event bar itself'
    elif mode == 'grid':
        g = int(gap if grid is None else grid)
        k = (bar // g) * g
        why = 'snapped down to the %d-bar lattice, %d bars back' % (g, bar - k)
    elif mode == 'extrema':
        prev = float(line[bar])
        cand, i = None, 1
        while bar - i * gap >= 0:
            j = bar - i * gap
            v = float(line[j])
            d = (v - prev) * side
            if d > 0.0:
                cand = j
            elif cand is not None:
                break
            prev = v
            i += 1
        if cand is None:
            return None
        seg = line[cand:bar + 1]
        if not np.isfinite(seg).any():
            return None
        o = int(np.nanargmax(seg) if side > 0 else np.nanargmin(seg))
        k = cand + o
        why = ('the %s-side extrema %.2f, %d bars back | the coarse sample bar was %d bars back, '
               '%d x %d-bar steps' % ('high' if side > 0 else 'low', float(line[k]), bar - k,
                                      bar - cand, (bar - cand) // gap, gap))
    else:
        raise ValueError('mode is extrema, grid or event')
    assert 0 <= k <= bar, 'the mage-cascade bar ran past the event bar'
    return int(k), why


def _mc_run(v, zoom, from_low):
    """The longest same-direction run ANCHORED at one end of `v`. -> (lines, dir, frm, to).

    `from_low` True anchors at index 0 and walks up; False anchors at the last index and walks
    down. Each step compares a line with the line `zoom` rungs along, which is Joe's wider zoom.
    A step of exactly 0.0 does NOT break a run - `ride_to_max.cascade`'s own test is `steps < 0`,
    so a flat step was already not counted against.
    """
    n = len(v)
    best = (1, 0, 0, 0)
    for sgn in (+1, -1):
        m = 0
        if from_low:
            i = 0
            while i + zoom < n and sgn * (v[i + zoom] - v[i]) >= 0.0:
                m += 1
                i += 1
            lines = m + zoom if m else 1
            frm, to = 0, lines - 1
        else:
            i = n - 1 - zoom
            while i >= 0 and sgn * (v[i + zoom] - v[i]) >= 0.0:
                m += 1
                i -= 1
            lines = m + zoom if m else 1
            frm, to = n - lines, n - 1
        if lines > best[0]:
            best = (lines, sgn if m else 0, frm, to)
    return best


def mage_cascade(mg, bar, tf_lo=MC_TF_LO, tf_hi=MC_TF_HI, zoom=MC_ZOOM, min_lines=MC_MIN,
                 extra=None):
    """[PRODUCER - Joe 1017] THE MAGE CASCADE at ONE bar. -> dict, or None if a line is not finite.

      mg         {tf: the Mage line} on the 5 s grid, covering tf_lo..tf_hi
      bar        the ONE bar every line is read at - `mage_cascade_bar` picks it
      tf_lo/hi   wsf, ws1 to ws12. A low cluster STARTS at tf_lo, a high cluster ENDS at tf_hi, and
                 a cluster touching neither end is discarded.
      zoom       rungs each cluster step compares across
      min_lines  lines a cluster must cover to count
      extra      {name: line} printed beside the ladder and NEVER walked - g30Mage's place

    -> v          the ladder, tf_lo..tf_hi, read at `bar`
       steps      the adjacent per-rung moves, for the printed table
       low, high  {'lines','dir','frm','to','counts'}. `dir` +1 rising with TF, -1 falling, 0 flat.
                  `frm`/`to` are TIMEFRAMES, not indices.
       verdict    'up', 'down' or 'neither'. The LOW cluster wins when both count.
       drop       the end-to-end diff, mg[tf_lo] - mg[tf_hi]. Joe 1017, asked whether the run
                  replaces it: *"no, it sits beside"*. It gates nothing in here.
       extra      {name: value at `bar`}
       why        the trace
    NO dr IN OR OUT. A consumer maps `verdict` onto its own trade side.
    """
    bar = int(bar)
    tfs = list(range(int(tf_lo), int(tf_hi) + 1))
    v = np.array([mg[t][bar] for t in tfs], float)
    if not np.isfinite(v).all():
        return None
    zoom = int(zoom)
    assert 1 <= zoom < len(v), 'the zoom width must fit inside the ladder'
    lo_n, lo_d, lo_a, lo_b = _mc_run(v, zoom, True)
    hi_n, hi_d, hi_a, hi_b = _mc_run(v, zoom, False)
    low = {'lines': lo_n, 'dir': lo_d, 'frm': tfs[lo_a], 'to': tfs[lo_b],
           'counts': bool(lo_n >= min_lines and lo_d != 0)}
    high = {'lines': hi_n, 'dir': hi_d, 'frm': tfs[hi_a], 'to': tfs[hi_b],
            'counts': bool(hi_n >= min_lines and hi_d != 0)}
    win = low if low['counts'] else (high if high['counts'] else None)
    verdict = 'neither' if win is None else ('up' if win['dir'] > 0 else 'down')
    nm = lambda t: 'ws%d' % t
    why = ('%s | the low cluster %s to %s, %d lines, %s%s | the high cluster %s to %s, %d lines, '
           '%s%s | the end-to-end diff %+.2f | zoom %d rungs, min %d lines'
           % (verdict,
              nm(low['frm']), nm(low['to']), low['lines'],
              'rising' if low['dir'] > 0 else ('falling' if low['dir'] < 0 else 'flat'),
              ' COUNTS' if low['counts'] else '',
              nm(high['frm']), nm(high['to']), high['lines'],
              'rising' if high['dir'] > 0 else ('falling' if high['dir'] < 0 else 'flat'),
              ' COUNTS' if high['counts'] else '',
              float(v[0] - v[-1]), zoom, int(min_lines)))
    return {'v': v, 'tfs': tfs, 'steps': np.diff(v), 'low': low, 'high': high,
            'verdict': verdict, 'drop': float(v[0] - v[-1]),
            'extra': {} if not extra else {k: float(a[bar]) for k, a in extra.items()},
            'why': why}



# ── the matryoshka test (JOE'S WORD, 1017: *"the matryoshka effect"*) ──────────────────────────
# JOE'S PREMISE, 1017 verbatim, which is the whole reason this producer exists:
#   *"the 'entire r line' means that r is one single line spread across many TFs. the entire r line
#    is coarse at the higher TF levels, and microscopic at the lower TF levels. this is why the
#    higher TF r follows the lower TF r"*
# So this is NOT three independent lines voting. It is one line read at three resolutions, and the
# coarse read lags the fine read. Joe 1017 on what that fixes: *"ws1r is penalised in the first 'r
# test', but in the new second test ws1r has served to prove the entire r line is reversing"*.
#
# HIS TEST 2, 1017 verbatim:
#   *"if ws2r has proven that it will follow ws1r, by following ws1r's walk, the trajectory is
#    confluenced"*
#   *"if ws2r reverses against ws1r's trajectory (example 08-24 00:16), no action can be taken.
#    this needs to be a stub - I want to know if this fires"*  <- WITHDRAWN 1017, his words kept
#    beside the withdrawal and never rewritten. He built it as a stub, I measured it on the 41
#    trade signals of 2026-08-22 to 2026-08-24, and he dropped it: *"drop ... it doesn't work well
#    when the market is voliatile (23:37 and 08:22)"*. The evidence: of the 4 signals it fired on,
#    2026-08-22 03:01:35 had a 0 s lag and 2026-08-24 08:22:25 a 5 s lag - the two lines bending
#    opposite ways on the same bar, which is volatility, not ws2r leaving an established walk.
#    THE CODE IS GONE, not disabled. There is no `against` state and no knob that restores one.
#    CONSEQUENCE, STRUCTURAL AND STATED: with the opposite bend no longer a verdict, it can no
#    longer veto a later agreeing bend either. So the walk looks for ws2r's first bend that MATCHES
#    the fine line's direction, and an opposite bend in between is simply passed over.
#
# NO LEVEL, NO FENCE ON THE HIGHER LINE, Joe 1017: *"for a ws1cp event, there will always be ws1r
# oob to 'start the trajectory walk'. any TF higher than ws1 will turn to follow ws1, but that
# higher TF does not need to be ex-fence. be sure this is baked in to avoid future issues"*.
# Measured on 2026-08-23: ws1r bends at r 76.33, ws2r at 74.42, ws3r at 63.93, ws4r at 50.14 - not
# one of them at a fence, and ws3r never went above the ex-fence 83 at all that episode.
#
# CAUSAL, Joe 1017: *"your view of the arrival is non-causal. we can only work with the data at the
# edge of the walk"*. Every read here is at or before `bar`, asserted.
#
# THIS PRODUCER DOES NOT COMPUTE A TRAJECTORY. It takes the two direction series the caller already
# has. SRP, and it keeps `optimus9` free of an import from the `docs/` tree where `traj` lives.


# ── away / toward, read from the TRADE's target side (Joe 1027 settled the perspective) ────────
AT_MID = 50.0     # kept for the callers that still pass a perspective value. NOT the perspective.


def away_toward(mage_dir, persp_mage, prev=None, mid=AT_MID):
    """[PRODUCER - Joe 1019, perspective settled 1027] The away/toward tag for ONE timeframe at ONE
    bar. -> 'away'|'toward'.

      mage_dir     the TF's OWN Mage trajectory direction at the bar, +1 / -1 / 0
      persp_mage   THE TARGET SIDE, +1 HIGH / -1 LOW. A value > `mid` is read as HIGH for the
                   callers that still pass a level; a bare +1 / -1 works too.
      prev         the tag at the previous bar, used when mage_dir is 0
      mid          the split used only when `persp_mage` is passed as a level

    THE PERSPECTIVE IS THE TRADE'S TARGET SIDE. Joe 1027, correcting this for the third time:
    *"I've already corrected this twice, please delete the ws1Mage note. the actual toward/away
    perspective comes from the open (or invisible-incoming, if no trade is open) trade: use the
    target-side"*. So there is no ws1Mage read here and no per-TF read either - ONE side, taken
    from the open trade, or from the incoming one when none is open.

    THE RULE:

        target side HIGH  ->  climbing = toward, falling = away
        target side LOW   ->  climbing = away,   falling = toward

    THE DIRECTION IS STILL PER TF, and it comes from that TF's MAGE, not its r. Joe 1019: *"Mage is
    the best source of direction - there's no lag"*.

    A FLAT MAGE HOLDS THE PREVIOUS TAG. Joe 1019: *"35 - hold the previous tag"*.

    WHAT THIS REPLACED, recorded in order: first a rule of mine that took the side whose `held`
    counter was smaller, which read ws5r backwards because `held` is staleness and not direction;
    then a per-TF perspective, which he withdrew; then ws1Mage's side, which he withdrew on 1027
    and asked to be DELETED rather than annotated. The target side is the perspective.
    """
    d = int(mage_dir)
    if d == 0:
        return prev
    high = float(persp_mage) > float(mid)
    if high:
        return 'toward' if d > 0 else 'away'
    return 'away' if d > 0 else 'toward'


def away_toward_series(persp_mage, dirs, mid=AT_MID):
    """`away_toward` over a whole line. -> a list of 'away'|'toward'|None, one per bar.

    `persp_mage` is ws{min_tf}Mage's series - the perspective - and `dirs` is the TF's own Mage
    direction series. None appears only before the first non-flat bar.
    """
    persp_mage = np.asarray(persp_mage, float)
    dirs = np.asarray(dirs, np.int8)
    assert len(persp_mage) == len(dirs), 'the perspective and the direction series must share the grid'
    out = [None] * len(dirs)
    prev = None
    for j in range(len(dirs)):
        prev = away_toward(int(dirs[j]), float(persp_mage[j]), prev, mid)
        out[j] = prev
    return out


def r_matryoshka(d_lo, d_hi, bar):
    """[PRODUCER - Joe 1017] Is the coarse r line following the fine one's walk? -> dict.

      d_lo   the FINE line's trajectory direction per bar, +1 / -1 / 0. ws1r today.
      d_hi   the COARSE line's, same length. ws2r today.
      bar    the bar the question is about.

    -> state   'follows'   the coarse line has bent the SAME way, at or after the fine line's bend
               'not yet'   it has not yet bent that way
               'no walk'   the fine line has no bend at or before `bar`
       walk_bar / walk_dir  the fine line's most recent bend and its direction - the walk's start
       hi_bar               the coarse line's first MATCHING bend at or after it, or None
       lag                  bars from the fine bend to that matching bend, or None
       why                  the trace

    A BEND is a change of direction in the series, flats transparent - the same reading `traj`
    itself uses for a reversal. The walk is the fine line's MOST RECENT bend, so the test always
    asks about the walk in progress and never an older one.
    """
    d_lo = np.asarray(d_lo, np.int8)
    d_hi = np.asarray(d_hi, np.int8)
    bar = int(bar)
    assert len(d_lo) == len(d_hi), 'the two direction series must share the grid'

    def bends(d, upto):
        """(bar, from, to) per direction change at or before `upto`. Flats are transparent."""
        out, prev = [], 0
        for i in range(0, upto + 1):
            v = int(d[i])
            if v == 0:
                continue
            if prev != 0 and v != prev:
                out.append((i, prev, v))
            prev = v
        return out

    bl = bends(d_lo, bar)
    if not bl:
        return {'state': 'no walk', 'walk_bar': None, 'walk_dir': 0, 'hi_bar': None,
                'lag': None, 'why': 'the fine line has not bent at or before the bar'}
    wb, _wf, wd = bl[-1]
    # the coarse line's first bend MATCHING the walk, at or after it. An opposite bend in between
    # is passed over - see the WITHDRAWN note above.
    bh = [z[0] for z in bends(d_hi, bar) if z[0] >= wb and z[2] == wd]
    if not bh:
        hb, lag, state = None, None, 'not yet'
        why = ('the fine line bent %+d at bar %d; the coarse line has not bent %+d since'
               % (wd, wb, wd))
    else:
        hb = bh[0]
        lag = hb - wb
        state = 'follows'
        why = ('the fine line bent %+d at bar %d; the coarse line bent %+d at bar %d, %d bars '
               'later - FOLLOWS' % (wd, wb, wd, hb, lag))
    assert wb <= bar and (hb is None or hb <= bar), 'a matryoshka read ran past the bar'
    return {'state': state, 'walk_bar': wb, 'walk_dir': int(wd), 'hi_bar': hb,
            'lag': lag, 'why': why}


def mage_band_split(mg, j, lower_tfs, upper_tfs):
    """[PRODUCER - Joe 1015, DISABLED AS AN AUTHORITY] the non-oob band read.

    JOE 1015: *"don't use oob. if the TF lines less than ws5Mage (g5 to ws4) print mostly higher
    values, and the TF lines greater than ws5Mage (ws6 to ws60) print mostly lower values, then the
    next move is downward. -the inverse is true ... I _think_ this method only works when ws5Mage
    is infence"*. HIS MODE ON MY MEASUREMENT - he 1016: *"no - it's ours. you brought it to the
    table, and I offered mode for it"*.

    DISABLED AS A TRADE AUTHORITY, Joe 1016: *"disable it"*. Measured in-use across the six banked
    2026-07-22 legs: as an ENTRY GATE it blocks two of them including the day's best and costs
    -2.6831%; as an EXIT at the majority threshold it costs -4.8229%; at the band's extreme it
    costs -1.5245% and is not implementable because the extreme is only knowable afterwards. Its
    strongest DISAGREEMENT of the day, 23 of 84 against the 14:14:55 SHORT, was on the day's best
    leg. IT REMAINS A GOOD READ AT A BAR. It is not an authority over a trade.

    -> (the lower group's median, the upper group's median, pairs with the lower line above,
        the total pairs)
    CAUSAL - one bar.
    """
    lo = [float(mg[t][int(j)]) for t in lower_tfs]
    up = [float(mg[t][int(j)]) for t in upper_tfs]
    pw = sum(1 for a in lo for b in up if a > b)
    return float(np.median(lo)), float(np.median(up)), pw, len(lo) * len(up)


def oob_ib_cross(line, hi, lo, xwob):
    """[PRODUCER · Joe 0806] OOB -> IB crossings of one line on whatever grid it is handed.

    OOB = v >= hi or v <= lo; IB = lo < v < hi STRICTLY (jig.sign / lr_v2 s_qualify_reset).
    A cross is CONFIRMED once IB has held `xwob` consecutive bars; returned per cross as
    (cross_idx, conf_idx, side) where cross = the first IB bar, conf = cross + xwob - 1 = the first
    bar the cross is KNOWABLE, side = +1 the run was hi, -1 lo. Causal."""
    v = np.asarray(line, float)
    oh, ol = v >= hi, v <= lo
    ib = (v > lo) & (v < hi)
    idx = np.arange(len(ib))
    run = (idx + 1) - np.maximum.accumulate(np.where(ib, 0, idx + 1))
    held = run >= max(1, int(xwob))
    conf = held & ~np.r_[False, held[:-1]]
    out = []
    for c in np.flatnonzero(conf):
        k = c - (int(xwob) - 1); z = k - 1
        if z < 0:
            continue
        if oh[z]:   out.append((int(k), int(c), 1))
        elif ol[z]: out.append((int(k), int(c), -1))
    return out


# ── ws1mage-rev (Joe 0911 named it) ────────────────────────────────────────────────────────────
WS1MR_DWELL   = 3     # 5s bars ws1Mage's oob run must REACH. MINE - the smallest run strictly
#                       longer than the 10 s dwell Joe rejected 0910. Joe has not ruled a value.
WS1MR_REV_WOB = 2     # KNOB. STEPS for the ws1Mage reversal. Joe 0910, reaffirmed 0911.
WS1MR_HOLD    = 4     # KNOB. bars IB must hold for the boundary cross. Joe 0911: "use these
#                       values, reversal:2, boundary:4. both are knobs". A wob here is a KNOWLEDGE
#                       delay, not lookahead - `sig` is the cross bar, `sig_conf` the bar it becomes
#                       knowable, and a truncation test confirms neither moves once reported.


def ws1mage_rev(g1, sig_mage, hi, lo, dwell=WS1MR_DWELL, rev_wob=WS1MR_REV_WOB,
                hold=WS1MR_HOLD, gate='rev'):
    """[PRODUCER · Joe 0911 named it `ws1mage-rev`] The three legs of the mechanic, as index arrays
    per dr. Joe 0910 on the chain it came from: "that's the best outcome - bank it and add to the
    spec. this new mech doesn't have a specific job at present".

      dwell_ok  bars where ws1Mage's CONSECUTIVE-oob run has REACHED `dwell` bars. oob is the
                dr-side boundary: >= hi at dr +1, <= lo at dr -1. The run counts through bars
                before any caller's start, so a line already oob on arrival qualifies at once.
      rev       bars where ws1Mage reverses - _mage_rev(g1, rev_wob), EITHER direction. `rev_wob`
                counts STEPS between bars, so a run of n steps spans n x 5 s across n + 1 bars.
                Direction is NOT filtered: Joe said "ws1 Mage reversing" and never ruled on it.
                Empty at gate='off'.
      sig       bars where `sig_mage` crosses the dr-side boundary OUT OF BOUNDS -> IN BOUNDS.
                DELEGATES to oob_ib_cross, which requires the landing bar to be IB on BOTH sides.
                A line that leaps from beyond one boundary to beyond the other does not cross.
      sig_conf  the bar each `sig` becomes KNOWABLE = cross + hold - 1. Equal to `sig` at hold 1.
                oob_ib_cross returns both and BOTH ARE CAUSAL; the hold delays knowledge, it does
                not read forward. Carry sig_conf wherever a consumer needs to act on the event.

    `g1` is ws1Mage. `sig_mage` is the line that controls the cross - gcws30Mage or gcws15Mage.
    A caller walks forward from its own bar: first dwell_ok >= its bar, then (at gate='rev') the
    first rev at or after that, then the first sig STRICTLY after the anchor.

    Causal - every leg reads only bars <= itself. Returns {dr: {'dwell_ok','rev','sig'}}."""
    g1 = np.asarray(g1, float); sm = np.asarray(sig_mage, float)
    idx = np.arange(len(g1))
    rev = np.flatnonzero(_mage_rev(g1, rev_wob) != 0) if gate == 'rev' else np.empty(0, int)
    oib = oob_ib_cross(sm, hi, lo, hold)
    out = {}
    for dr in (+1, -1):
        oob = (g1 >= hi) if dr > 0 else (g1 <= lo)
        run = (idx + 1) - np.maximum.accumulate(np.where(oob, 0, idx + 1))
        pair = sorted((k, c) for k, c, sd in oib if sd == dr)
        out[dr] = {'dwell_ok': np.flatnonzero(run >= max(1, int(dwell))),
                   'rev': rev,
                   'sig': np.array([k for k, _ in pair], dtype=int),
                   'sig_conf': np.array([c for _, c in pair], dtype=int)}
    return out


def mage_rev_walk(legs, dr, frm, sig_lookback=0):
    """[Joe 0925] The ORDERED walk over `ws1mage_rev`'s legs, in one place. -> sig_conf or None.

    `legs` is one `ws1mage_rev(...)` result. `frm` is the caller's own bar.

      1  the first `dwell_ok` at or after `frm`         — the arming leg
      2  the first `rev`      at or after that          — THE ANCHOR, the Mage line reversing
      3  the first `sig`      after the anchor          — the gcws30Mage cross, and its `sig_conf`

    Joe 0925 confirmed the order: *"if 'anchor' means the Mage line reversing, and `first sig`
    means g30, then that's the correct mech"*.

    `sig_lookback` IS JOE'S LOOKBACK ALLOWANCE, 0925: *"re the lookback allowance, I agree but it
    should be longer - make it 2 minutes"*. A `sig` may be taken from up to `sig_lookback` bars
    BEFORE the anchor. It defaults to 0, which is the behaviour every banked figure was measured
    under, including `report_coil_exit`'s 121 `wsf_leash` rows.

    WHY IT EXISTS. Measured 09-02 18:15:00: `dwell_ok` 18:15:00, the anchor 18:15:05, and a
    gcws30Mage `sig` at 18:15:00 — ONE BAR, 5 s, before the anchor. Under a strict "after the
    anchor" the walk skipped it and took the next one at 18:37:30, 22.5 minutes later. At
    `sig_lookback` 24 bars = 2 min the print is 18:15:15 instead of 18:37:45.

    THE `sig >= dwell_ok` FLOOR IS GONE — Joe 0926, asked directly: *"drop it"*. It was mine and
    unruled. It made the allowance unreachable whenever the qualifying cross sat before the arming
    bar, which is the common case: measured 09-01 03:40:05, the gcws30Mage cross at 03:38:25 was
    rejected at EVERY lookback value while the floor stood, because `dwell_ok` was 03:40:05.

    THE SELECTION IS THE EARLIEST QUALIFYING `sig`, NOT THE ONE NEAREST THE ANCHOR, and it is
    UNRULED. Joe 0926 asked whether the choice courts lookahead. It does not: the walk fires at the
    anchor bar and every candidate is already in the past, so both selections read history only.
    What is true of BOTH is that the emitted `sig_conf` is stamped before the bar the decision is
    made on — 03:38:40 decided at 03:40:35. That is a back-stamp, and the floor Joe set on 0926,
    *"it has to be >= utc - agreed lookback"*, is what contains it.

    DROPPING THE FLOOR CHANGES NOTHING AT `sig_lookback` 0. The test is `sig > anchor - lookback`,
    and at 0 that is `sig > anchor`; the anchor is at or after `dwell_ok`, so every sig that passes
    already passed the old floor. Every banked figure stands.

    MEASURED IMPACT at 24 bars. The 11 wsf_leash IS rows: the ws3mage-rev from each detect bar
    moves on NONE of them. The 28 `strat-3-r-oob` episodes: 3 move, all earlier —
    09-02 18:15:00 by -22.5 min, 09-03 16:52:00 by -1.1 min, 09-03 19:52:00 by -3.2 min.

    CAUSAL. Every bar read is at or after `frm`, and `sig_conf` already carries its own hold.
    """
    L = legs[int(dr)]
    d, r, s, sc = L['dwell_ok'], L['rev'], L['sig'], L['sig_conf']
    a = d[d >= int(frm)]
    if not len(a):
        return None
    a = int(a[0])
    b = r[r >= a]
    if not len(b):
        return None
    b = int(b[0])
    lb = max(0, int(sig_lookback))
    m = np.flatnonzero(s > b - lb) if lb else np.flatnonzero(s > b)
    return int(sc[m[0]]) if len(m) else None


# ── divergence (Joe 0912) ──────────────────────────────────────────────────────────────────────
def divergence(osc, px, hi, lo, i0=0, i1=None):
    """*** PSEUDO-DISABLED, Joe 1026. DO NOT CALL THIS. USE `anchor_floater`. ***

    Joe 1026: *"I instructed to not use jig.divergence. pseudo-disable jig.divergence: make the
    return a non-sensical result so that the docstring will be read."* It now returns an all-NaN
    `sig` and a sentinel `episodes`, so any caller fails instead of quietly getting a number.

    WHY. `divergence` is STEP 4 ONLY - the comparison. It cannot choose what to compare, so called
    on its own it invents its own episode pair from a fence, which is not the mech. The selection
    is Joe's four-step 0912 spec and it lives in `anchor_floater`: the anchor at bar k, the pivot,
    then the floater. THE DIVERGENCE READ IS `anchor_floater`, and its `state` is the one result:
    +1 a divergence supporting a SHORT, -1 supporting a LONG, +/-2 PM, 0 inside the noise band.

    WHAT THIS COST, measured 1026 on the live-seam run: asked for the bearish divergence at the
    2026-10-26 21:51 cadence, this function returned NOTHING across eight argument variants - two
    price series x four fence pairs, 292 to 825 episodes each. `anchor_floater(ws1r, close, +1, k)`
    returned state +1 at all four markers, anchor 51.94 against a floater of 100.00 at 21:38:00,
    d_osc -48.06 against d_px +0.000230. Eight tables of "none" were measuring the wrong function.

    THE ORIGINAL DOCSTRING FOLLOWS, unchanged, because the mechanic it describes is still the one
    `anchor_floater` step 4 performs.

    [PRODUCER · lifted from divergence_exit.div_sig 0706, split onto the jig 0912 on Joe's word]

    THE EXTREMA DIVERGENCE. Joe 0912: "the jig has an updated version that relies on 2 lookbacks
    based on extremas". The two lookbacks are two CONSECUTIVE SAME-SIDE OOB EPISODES, each
    contributing its own extreme - not a fixed bar offset.

      episode     a contiguous run of bars with osc >= hi (high side) or osc <= lo (low side)
      its extreme the max of osc inside the run on the high side, the min on the low side, and the
                  PRICE at that same bar
      the pair    this episode's extreme against the PREVIOUS same-side episode's extreme
      bearish +1  high side: price makes a HIGHER high while osc makes a LOWER high
      bullish -1  low side:  price makes a LOWER low  while osc makes a HIGHER low
      confirmed   at the EPISODE END - the last oob bar. Causal: nothing is read past that bar

    `hi` and `lo` are REQUIRED, not defaulted. div_sig hardcoded 85/15 for the s5m book; which
    fence this mechanic uses is the caller's, and it decides whether any episode exists at all.

    `px` is the price at each bar. docs/o9-live/divergence_research.md:201 - "DEMA-smoothing the
    price slope DESTROYS it (MAE 0.15 -> 0.35-0.85). The raw price slope is correct." So pass RAW
    close, not px_smooth.

    -> (sig, episodes)
       sig       float array, +1 / -1 / 0 per bar, nonzero only on a confirming episode-end bar
       episodes  [(side, start, end, extreme_bar, osc_at_extreme, px_at_extreme, fired)] in bar
                 order, so a caller can show BOTH lookbacks behind any signal."""
    #   THE PSEUDO-DISABLE. Returns before any work, so nothing here can be reached by accident.
    #   NaN != 0.0 is True, so a caller testing `sig != 0` sees every bar fire and then fails on
    #   int(nan) - loud, not silent. The episodes sentinel breaks any tuple unpack.
    return (np.full(len(np.asarray(osc, float)), np.nan),
            [('PSEUDO-DISABLED 1026 - read this function\'s docstring and use anchor_floater',)])

    osc = np.asarray(osc, float); px = np.asarray(px, float)
    n = len(osc); i1 = n - 1 if i1 is None else i1
    sig = np.zeros(n); eps_all = []
    for side, thr, cmp_price, cmp_osc in ((1, hi, np.greater, np.less),
                                          (-1, lo, np.less, np.greater)):
        oob = (osc >= thr) if side == 1 else (osc <= thr)
        eps = []
        i = i0
        while i <= i1:
            if oob[i]:
                j = i
                while j <= i1 and oob[j]:
                    j += 1
                rr = osc[i:j]
                if np.all(np.isnan(rr)):
                    i = j; continue
                m = int(np.nanargmax(rr) if side == 1 else np.nanargmin(rr))
                eps.append([side, i, j - 1, i + m, float(rr[m]), float(px[i + m]), 0])
                i = j
            else:
                i += 1
        for k in range(1, len(eps)):
            _, _, eb, _, rc, pc, _ = eps[k]
            _, _, _, _, rp, pp, _ = eps[k - 1]
            if cmp_price(pc, pp) and cmp_osc(rc, rp):
                sig[eb] = float(side); eps[k][6] = int(side)
        eps_all += eps
    eps_all.sort(key=lambda e: e[2])
    return sig, [tuple(e) for e in eps_all]


# ── the anchor/floater divergence front end (Joe 0912) ─────────────────────────────────────────
AF_BLOCK = int(os.environ.get('W_AF_BLOCK', 60))
#                  KNOB. bars in ONE step-3 lookback block = 300 s = 5 minutes at the 5 s grid.
#                  Joe 0912: "step 3 then looks back to 17:27, 17:22, etc (in one code loop)".
# AF_ANCHOR_MID - does step 1 REJECT an anchor on the pivot's side of 50. BANKED False, Joe 1017.
#   HIS DIAGNOSIS, verbatim: *"the 'side of 50' has accidently bled into the current state where
#   the genuine bullish divergence is unable to fire / the point of 'must pass 50' was to prevent
#   an early return to same-side (divergence test side), like the example you can see at 08-25
#   20:37. the past 50 mech can't block an anchor if it's already past 50"*.
#   He is right, and 2026-08-25 20:37 is exactly what the rule was built for: ws1r crosses UP
#   through 50 at 20:37:15 (45.68 -> 53.50) and back DOWN at 20:37:50 (52.19 -> 48.11) - a 35 s,
#   7-bar poke - then stays below 50 for the next 12 minutes. That is a step-2 problem, a pivot run
#   with no substance, and it never had anything to do with where the ANCHOR sits.
#   WHAT IT COST: at 2026-08-26 04:00:45 ws1r is 68.83, so a bullish read at dr -1 returned None
#   on the first line of the body, before price or the floater were looked at at all.
#   HE RULED SHAPE A: with the gate off, step 2's 50 rule already does the right thing by itself -
#   it walks back from k-1, so the anchor's OWN run above 50 becomes the pivot, and the floater
#   walk then has to find a genuinely separate sub-50 excursion. That is the protection the rule
#   was for, kept, with no further surgery.
#   True RESTORES the old rejection, so the non-fires recorded in `wsf_dtf_v3_spec.md`,
#   `1015_ongoing_momentum.md` and `1015_mechs_ledger.md` stay reproducible.
AF_ANCHOR_MID = os.environ.get('W_AF_ANCHOR_MID', '0') == '1'
# ── THE PIVOT MUST BE A PASSAGE, NOT A POKE. Joe 1017, after reading the 2026-08-26 04:00:45 ws3r
# walk: *"what this uncovers is that the 43.82 was captured before the 'past 50' fired, which
# breaks the rule. was there a pinhole through 50 that I don't see?"* - there was. Measured: five
# 50-crossings in ten minutes, and the pivot the walk took was 2026-08-26 03:58:40..03:58:55 -
# FOUR BARS, 20 s, 0.52 points above 50. The same shape as the 2026-08-25 20:37 example he named
# earlier: ws1r up through 50 at 20:37:15 and back down at 20:37:50, a 35 s poke, then 12 minutes
# below.
#   HE DELEGATED THE VALUES: *"your call on the value - whatever allows ws3r to genuinely cross
#   past 50 before finding the 03:29 low extrema"* / *"I think seperate knobs are good"*.
# AF_PIVOT_WIDTH - bars the pivot run must HOLD past `mid`. 12 bars = 60 s = one full ws1 bar of
#   persistence, which is why it is 12 and not a round number. Rejects the 4-bar pinhole above and
#   the 6-bar / 30 s run at 2026-08-26 03:43:30.
# AF_PIVOT_DEPTH - r POINTS past `mid` the run must reach. 2.0 is this file's own `SR_TOL`, from
#   Joe 0912's *"tolerance ~2%"* read as r points. Rejects a 0.52-point graze.
# AF_STOP_N - CONSECUTIVE non-improving blocks before the step-3 walk stops. Joe 1017 chose this
#   shape over requiring the floater to be a turn: *"B - no lookback cap"*. 2 is the minimum that
#   reaches his named 03:29 low of 16.52 with the pivot above; at 1 the walk stops on a 43.82
#   knife-edge mid-descent. An EMPTY block still does not count - Joe 0921, *"skipped, not a
#   stop"*.
#   NO DISTANCE CAP. His words. The walk runs to bar 0 if the series keeps making new extremes.
# 1 / 0.0 / 1 restores the pre-1017 behaviour, so the non-fires recorded in `wsf_dtf_v3_spec.md`,
# `1015_ongoing_momentum.md` and `1015_mechs_ledger.md` stay reproducible.
AF_PIVOT_WIDTH = int(os.environ.get('W_AF_PIVOT_WIDTH', 12))
AF_PIVOT_DEPTH = float(os.environ.get('W_AF_PIVOT_DEPTH', 2.0))
AF_STOP_N = int(os.environ.get('W_AF_STOP_N', 2))
# AF_SLOPE_FLOOR - the NOISE BAND, in r points, on |d_osc - d_px_scaled|. 0.0 = no band, which is
#   the no-op default and the only value that invents nothing. NOT RULED: `pk_state`'s caller has
#   always supplied a floor and Joe has not given one for this producer. At 0.0 `state` is never 0
#   unless d_osc or d_px is exactly 0.
AF_SLOPE_FLOOR = float(os.environ.get('W_AF_SLOPE_FLOOR', 0.0))


def anchor_floater(r, px, dr, k, block=AF_BLOCK, mid=50.0,
                   xn=None, dwell_bars=None, oob=None, anchor_mid=AF_ANCHOR_MID,
                   pivot_width=AF_PIVOT_WIDTH, pivot_depth=AF_PIVOT_DEPTH,
                   stop_n=AF_STOP_N, slope_floor=AF_SLOPE_FLOOR):
    """[PRODUCER · Joe 0912] *** THE DIVERGENCE READ. THIS IS "DIVERGENCE". ***

    Joe 1026: *"make sure that jig.anchor_floater has a 'divergence' tag so that we use the same
    language"*. When anything in this project says DIVERGENCE, it means THIS function and its
    `state`. `jig.divergence` is step 4 alone and is pseudo-disabled; it cannot choose what to
    compare, so it is not the read.

    THE FOUR STEPS that choose what goes into the divergence machine.

    JOE'S VERBATIM SPEC, 0912:
      "whenever a divergence test is requested
       -1. capture the current value of r, capture the current dr
       -2. look back to find the r extrema which is facing the opposing step 1's dr, and on the
           other side of 50 from the r value taken in step 1
       -3. look back from step 2, find the r extrema that is on the same side as step 1's dr. this
           r extrema is the floater, and the step 1 r value is the anchor
       -4 feed the andchor and floater timestamps and vaules into the divergence machine
       eg if 08-25 17:34 is the anchor (dr 1), the step 2 lookback will find a dr -1 extrema at
       ~17:32:30, and the step 3 lookback will find the dr 1 floater at ~17:29"

    JOE'S VERBATIM ON STEP 3 BEING A BACKWARD LOOP, 0912:
      "step 3 then looks back to 17:27, 17:22, etc (in one code loop) until it has proven that it
       has gone past the extrema. the extrema and the timestamp are then apparent"

    JOE'S VERBATIM ON WHY THE LOOP STOPS THERE, 0912:
      "divergences rely on the previous peak for comparison against the current moment. when k is
       printing a smaller vlaue than the last k 'bump', we know that the momentum is not as strong"
      "the same goes for a trough, if the anchor is also a trough"

    The comparator is the PREVIOUS bump, never the biggest bump in history. Walking past the first
    quiet block would substitute an older bump and break the comparison. Already in the 0711 survey
    (docs/o9-live/divergence_research.md) as Axis B option 1 - "compare the two most recent
    same-type extremes" - and Finding 2 - "vs the previous same-kind turn".

    CAUSAL. Every bar read is <= `k`. No fence: the 85/15 in `divergence` plays no part here.

      step 1  the anchor is bar `k`: r[k], px[k], and `dr`. NO SIDE TEST - Joe 1017 ruled the 50
              gate off here, see `AF_ANCHOR_MID`. It used to return None when r[k] sat on the
              pivot's side of 50, on the reasoning that step 2 was then self-contradictory. It is
              not: step 2 walks back from k-1, so the anchor's own run becomes the pivot and the
              floater walk still has to clear 50 to find its extreme. `anchor_mid=True` restores
              the rejection.
      step 2  the pivot. TWO RULES LIVE HERE - see REPLACED 0921 below.

              THE DWELL RULE, Joe 0921, used when `xn` is given: "instead of relying on r passing
              50, use ws{tf+1}x dwelling in dr-opposing oob, for tf*{knob:1}". Walk back to the
              most recent CONTIGUOUS run of `xn` bars in the dr-OPPOSING oob - at or below oob[0]
              at dr +1, at or above oob[1] at dr -1 - that is at least `dwell_bars` long. The
              pivot is that run's `xn` EXTREME: its min at dr +1, its max at dr -1. Joe 0921 chose
              the extreme over the run's first or last bar. Returns None when no run qualifies.

              THE 50 RULE, the original, used when `xn` is None. Walk back to the most recent
              CONTIGUOUS run of bars on the other side of 50, and take that run's extreme facing
              the opposing dr. MINE, and unruled: Joe named a timestamp (~17:32:30), not a rule.
      step 3  the floater. From the pivot walk BACKWARD in blocks of `block` bars. Each block
              yields its best dr-side value - the max at dr +1, the min at dr -1, counting only
              bars on the dr side of 50. Keep the running best. Stop at the first block that adds
              no new best. Block 1 is bars [pivot - block, pivot), so THE PIVOT BAR ITSELF IS
              EXCLUDED. The 50 filter is JOE'S, verbatim: "find the r extrema that is on the same
              side as step 1's dr". MINE and unruled: a tie stops the loop (strictly-better only)
              and a flat top keeps its EARLIEST bar.

              A BLOCK HOLDING NO dr-SIDE BAR IS SKIPPED, not a stop. Joe 0921 - it used to end the
              walk, which is not in his "until it has proven that it has gone past the extrema".
              The walk now ends only at a non-improving block or the tape start.
      step 4  the comparison, which is all `divergence` does at an episode end:
                dr +1, the anchor is a high -> bearish when px rises and r falls
                dr -1, the anchor is a low  -> bullish when px falls and r rises

    -> None, or a dict:
         anchor  (k, r, px)          floater (bar, r, px)
         pivot   (bar, r, px)        blocks  [(from, to, best, best_bar, new_best)] in walk order
         d_osc   r anchor minus r floater      d_px  px anchor minus px floater
         fired   +1 bearish / -1 bullish / 0 none
         state   THE ONE RESULT, Joe 1018: *"it should be a mech inside of anchor_floater - single
                 point of consumption, one result"*. THE SIGN NAMES THE TRADE SIDE THE READING
                 SUPPORTS; THE MAGNITUDE SAYS WHETHER IT IS A DIVERGENCE OR A PRICE MATCH:
                   +1  a DIVERGENCE whose direction supports a SHORT
                   -1  a DIVERGENCE whose direction supports a LONG
                   +2  PM - price and osc AGREE, the trend continuing in the direction that
                       supports a SHORT
                   -2  PM - the trend continuing in the direction that supports a LONG
                    0  inside the noise band, AF_SLOPE_FLOOR
                 So `state`'s sign compares directly against a BANKED trade side, +1 SHORT / -1
                 LONG, and `abs(state)` says which kind of reading it is.
                 *** THIS IS THE OPPOSITE SIGN CONVENTION TO `pk_state`. *** There, +1 is "bull,
                 line rising", which supports a LONG. `pk5s_gate_computer`, `pk_vote_machine` and
                 `bias_machine.verdict_pk` all use that one. ANYTHING CARRYING A VALUE BETWEEN THE
                 TWO MUST FLIP IT. Joe 1018 on why this is spelled out: *"we have to be careful and
                 precise with our durable data"*.
         pm      True when abs(state) == 2. PM IS NOT AN ABSENCE OF EVIDENCE - the PK spec's own
                 rule is that *"PM (price-matched) votes suppress the opposing bucket"*, 40% in
                 `pk_vote_machine.aggregate`. It used to collapse into `fired` 0 alongside the
                 noise band, which threw the distinction away: at 2026-08-26 10:35:05 all three r
                 lines read PM - d_osc +18.93/+47.59/+45.24 against d_px +0.00379/+0.00320/+0.00288,
                 every pair agreeing - and a consumer reading `fired` saw three zeros.

    REPLACED 0921. `xn`, `dwell_bars` and `oob` switch step 2 to the dwell rule. They default to
    None so sideways_reversal, jig.causal.anchor_floater and stopsweep.py - none of which holds an
    x line - keep the 50 rule and are untouched. TWO STEP-2s NOW LIVE IN ONE PRODUCER, and that is
    a fidelity gap, not a design: Joe replaced step 2, and every caller that cannot supply `xn` is
    still running the rule he replaced."""
    r = np.asarray(r, float); px = np.asarray(px, float)
    k = int(k); dr = int(dr); block = max(1, int(block))
    if k < 1 or not np.isfinite(r[k]):
        return None
    if anchor_mid and ((r[k] <= mid) if dr > 0 else (r[k] >= mid)):
        return None
    if xn is not None:                                  # THE DWELL RULE, Joe 0921
        x = np.asarray(xn, float)
        need = max(1, int(dwell_bars))
        o_lo, o_hi = float(oob[0]), float(oob[1])
        opp = (x <= o_lo) if dr > 0 else (x >= o_hi)
        j = k - 1
        p = None
        while j >= 0:
            if not opp[j]:
                j -= 1
                continue
            e = j
            while e >= 0 and opp[e]:
                e -= 1
            e += 1
            if j - e + 1 >= need:
                seg = x[e:j + 1]
                if not np.all(np.isnan(seg)):
                    p = e + int(np.nanargmin(seg) if dr > 0 else np.nanargmax(seg))
                    break
            j = e - 1
        if p is None:
            return None
    else:                                               # THE 50 RULE, the original
        # THE RUN MUST BE A PASSAGE. It used to take the FIRST contiguous run found walking back,
        # however thin - see AF_PIVOT_WIDTH / AF_PIVOT_DEPTH. Now a run that fails either test is
        # stepped over and the walk continues to the next one.
        other = (r < mid) if dr > 0 else (r > mid)
        j, p = k - 1, None
        while j >= 0:
            if not other[j]:
                j -= 1
                continue
            e = j
            while e >= 0 and other[e]:
                e -= 1
            e += 1
            seg = r[e:j + 1]
            if not np.all(np.isnan(seg)):
                dep = ((mid - float(np.nanmin(seg))) if dr > 0
                       else (float(np.nanmax(seg)) - mid))
                if (j - e + 1) >= int(pivot_width) and dep >= float(pivot_depth):
                    p = e + int(np.nanargmin(seg) if dr > 0 else np.nanargmax(seg))
                    break
            j = e - 1
        if p is None:
            return None
    same = (r > mid) if dr > 0 else (r < mid)
    best = np.nan; bi = None; blocks = []; n = 0; bad = 0
    while True:
        n += 1
        b_hi = p - (n - 1) * block
        b_lo = max(0, p - n * block)
        if b_hi <= 0 or b_lo >= b_hi:
            break
        cand = np.where(same[b_lo:b_hi], r[b_lo:b_hi], np.nan)
        if np.all(np.isnan(cand)):
            blocks.append((b_lo, b_hi, float('nan'), None, 0))
            continue                                    # Joe 0921: skip, do not stop
        m = b_lo + int(np.nanargmax(cand) if dr > 0 else np.nanargmin(cand))
        new = (bi is None) or ((r[m] > best) if dr > 0 else (r[m] < best))
        if new:
            best = float(r[m]); bi = m; bad = 0
        blocks.append((b_lo, b_hi, float(r[m]), int(m), int(new)))
        if not new:
            # AF_STOP_N CONSECUTIVE non-improving blocks, not one. A single block that fails to
            # improve used to end the walk, which stopped it on a non-extreme 4.75 min from the
            # pivot while the real low sat 5.9 blocks further back.
            bad += 1
            if bad >= int(stop_n):
                break
    if bi is None:
        return None
    d_osc = float(r[k]) - float(r[bi])
    d_px = float(px[k]) - float(px[bi])
    if dr > 0:
        fired = 1 if (d_px > 0 and d_osc < 0) else 0
    else:
        fired = -1 if (d_px < 0 and d_osc > 0) else 0
    # ---- THE ONE RESULT. `fired` is kept unchanged for every existing caller; `state` is the
    # field a new consumer reads. See the `state` entry in the docstring for the sign convention
    # and for why it is the OPPOSITE of `pk_state`'s.
    if d_osc == 0.0 or d_px == 0.0 or abs(d_osc) <= float(slope_floor):
        state = 0
    elif fired != 0:
        state = int(fired)                              # the signs DISAGREE -> a divergence, +-1
    else:
        # the signs AGREE -> PM. Its side is the one the CONTINUING trend supports: price rising
        # supports a LONG, price falling supports a SHORT.
        state = -2 if d_px > 0 else 2
    return {'anchor': (k, float(r[k]), float(px[k])),
            'pivot': (int(p), float(r[p]), float(px[p])),
            'floater': (int(bi), float(r[bi]), float(px[bi])),
            'blocks': blocks, 'd_osc': d_osc, 'd_px': d_px, 'fired': int(fired),
            'state': int(state), 'pm': bool(abs(state) == 2)}


# ── sideways / reversal from a flat sample run + divergence (Joe 0912 hypothesis) ───────────────
SR_SAMPLES = 3      # Joe 0912: ">= 3 samples printing the same values". A sample is ONE 5 s bar -
#                     the per-sample table he read the hypothesis off was 61 rows over 5 minutes.
SR_TOL     = 2.0    # MINE, and unruled. Joe 0912 wrote "tolerance ~2%". Read as 2% of r's 0..100
#                     scale = 2.0 r POINTS across the run, not 2% of the r value.
SR_TEST    = 24     # Joe 0912: "we test for divergence for the next 2 minutes" = 120 s = 24 bars.
SR_FENCE   = (40.0, 60.0)   # THE MID-ZONE FENCE. Joe 0912: "let's modify the dr side of 50 rule.
#                     instead of 50, create a mid-zone-fence of 40:60. the sideways signal must be
#                     on the dr side of the fences edge". dr +1 reads the HIGH side, so the run
#                     must sit ABOVE 60; dr -1 reads the LOW side, so the run must sit BELOW 40.
#                     STRICTLY outside the edge - the same strictness the 50 test used.


# ── the oob-anchored divergence fire bar. JOE 1017, his "option 2" ────────────────────────────
# HIS SPEC, verbatim, offered as one of three replacements for a 4,065 s ib-return wait on the
# 2026-08-23 19:05 SHORT:
#   *"2) wait for the next high-side g30Mage oob, and use that bar as the anchor for a divergence
#    test / --if the divergence test is bearish, then open the SHORT at 19:26"*
# and the ruling after it was measured over all 40 trades of 2026-08-22 to 2026-08-24:
#   *"bank A"* - A being *"wait for option 2, no fallback"*, which he confirmed is the only causal
#   reading: *"is this causal? ... no"* to a fallback that needs the exit bar to choose.
#
# THE SIDE IS THE TRADE'S, from his own words *"because this a SHORT ... wait for the next
# high-side g30Mage oob"*. The EVENT-side variant was measured beside it and is NOT the default:
# trade side took 34 of 40 trades for +14.5689% net at his 1.60 cap, event side took 30 for
# +12.2153%.
#
# MEASURED AGAINST THE OTHER TWO OPTIONS, all 40 trades, 1.60 MAE cap, cap-loss reading:
#   option 1, fire at the decision event when the matryoshka test says follows  -3.1004%, 15 trades
#   option 2, THIS, trade side                                                 +14.5689%, 34 trades
#   option 3, ws1r reverse + ws1x crossing [boundary, r, Mage] xwob 5           -6.9125%, 40 trades
#   octo2 as it stood, firing at the decision event every time                  +1.4405%, 40 trades
# Option 1 was exactly a no-op on the trades it kept - +0.0000 pp against octo2 - because it fires
# where octo2 already fires. Option 3 lost at every cap value swept.
#
# WHAT IT COSTS, reported to him and not hidden: the wait reaches 4,390 s on 2026-08-22 05:15:00,
# which is LONGER than the ib-return delay he rejected. Median 972 s, 8 of 34 over 2,500 s. And 6
# of 40 signals never fire before their exit, worth +8.2009% that this mech gives up.
#
# CAUSAL: the returned bar is the FIRST bar at or after `frm` that satisfies both conditions, and
# every read is at or before it. A caller enters AT that bar and never earlier. Asserted.
# THE NAME IS MINE, the mech is unnamed - Joe has called it only "option 2".


def next_oob_divergence(line, r, px, frm, side, dr, hi, lo, until=None):
    """[PRODUCER - Joe 1017] The first oob-anchored bearish/bullish divergence at or after `frm`.

      line   the line whose oob crossing anchors the test. g30Mage today; the TF is the caller's.
      r      the r line `anchor_floater` picks its anchor and floater from. ws1r today.
      px     RAW close for the divergence - `divergence`'s own docstring requires it, not px_smooth
      frm    the decision event bar. The scan starts strictly AFTER it.
      side   which oob boundary `line` must cross INTO: +1 the high, -1 the low
      dr     the direction the divergence must fire, in the BANKED frame: +1 SHORT, -1 LONG
      hi/lo  the oob fence. REQUIRED, never defaulted - it decides whether an episode exists.
      until  the last bar the scan may reach. None runs to the end of the line. NO CAP OF MY OWN.

    -> (the bar, the trace) or None.
    """
    line = np.asarray(line, float)
    n = len(line)
    end = (n - 1) if until is None else min(int(until), n - 1)
    frm = int(frm)
    side = int(side)
    dr = int(dr)
    assert side in (+1, -1), 'side is the oob boundary to cross into: +1 high, -1 low'
    assert dr in (+1, -1), 'dr is the BANKED frame: +1 SHORT, -1 LONG'
    thr = float(hi) if side > 0 else float(lo)
    for k in range(frm + 1, end + 1):
        v, p = float(line[k]), float(line[k - 1])
        crossed = (v >= thr and p < thr) if side > 0 else (v <= thr and p > thr)
        if not crossed:
            continue
        af = anchor_floater(r, px, dr, k)
        if af is None or int(af.get('fired', 0)) != dr:
            continue
        assert k > frm and k <= end, 'the divergence fire bar ran outside the scan'
        return int(k), ('the %s-side oob at %.2f anchors a divergence firing %+d'
                        % ('high' if side > 0 else 'low', v, dr))
    return None

def sideways_reversal(r, px, dr, i0=0, i1=None, samples=SR_SAMPLES, tol=SR_TOL,
                      test=SR_TEST, block=AF_BLOCK, mid=50.0, fence=SR_FENCE, first=False):
    """[PRODUCER · Joe 0912 hypothesis, NOT YET SCORED] Momentum `sideways`, and a NEW `reversal`
    state, built from a flat run of r samples plus the anchor/floater divergence test.

    JOE'S VERBATIM, 0912:
      "if we see >= 3 samples printing the same values (tolerance ~2%) on the dr side of 50, and we
       test for divergence for the next 2 minutes, then we can create a reliable momentum sideways
       or reversal signal"
      "reversal is a new state. I'm not 100% sure that we need it yet, but it will help me while we
       develop the science"

      sideways  the bar where a run of consecutive bars REACHES `samples` bars with every bar on
                the dr side of the MID-ZONE FENCE `fence` - above its high edge at dr +1, below its
                low edge at dr -1 - and the run's max minus its min <= `tol`. Fires ONCE per run,
                on the bar the run reaches `samples`. MINE: Joe said ">= 3", which is a state; the
                bar that state becomes knowable is the third.

                Joe 0912 replaced a plain 50 here with the 40:60 fence. `mid` is untouched and
                stays 50 - it is the divergence machine's own boundary, used by `anchor_floater`
                for steps 1, 2 and 3, and Joe did not change that.
      reversal  the first bar in the `test` bars AFTER the sideways bar where `anchor_floater`
                fires with that bar as the anchor. MINE: the window is bars sideways+1 through
                sideways+test, so the sideways bar itself is not an anchor.

    Nothing here reads past the bar it reports on. `anchor_floater` is causal and the flat run is
    backward-looking, so both states are live-legal.

    -> [(sideways_bar, reversal_bar or None, run_lo, run_hi, run_span, af or None)] in bar order,
       where run_lo..run_hi is the flat run at the moment it fired, run_span is its max minus its
       min in r points, and `af` is the full anchor_floater dict behind a reversal.

    `first=True` returns after the first event and stops scanning. Joe 0912 bounded the walk there:
    a walk ends at its first sideways, or at its reversal when one fires inside the `test` window."""
    r = np.asarray(r, float); px = np.asarray(px, float)
    n = len(r); i1 = n - 1 if i1 is None else int(i1)
    i0 = int(i0); samples = max(2, int(samples)); test = max(0, int(test))
    f_lo, f_hi = (float(fence[0]), float(fence[1])) if fence else (mid, mid)
    side = (r > f_hi) if dr > 0 else (r < f_lo)
    out = []; armed = True
    for k in range(max(i0, samples - 1), i1 + 1):
        lo = k - samples + 1
        w = r[lo:k + 1]
        if not (side[lo:k + 1].all() and np.all(np.isfinite(w))):
            armed = True
            continue
        span = float(np.max(w) - np.min(w))
        if span > tol:
            armed = True
            continue
        if not armed:
            continue
        armed = False
        rev = None; af = None
        for t in range(k + 1, min(i1, k + test) + 1):
            d = anchor_floater(r, px, dr, t, block=block, mid=mid)
            if d is not None and d['fired']:
                rev = t; af = d
                break
        out.append((int(k), rev, int(lo), int(k), span, af))
        if first:
            break
    return out


def momo_landed(R, tagged, hi, lo, fence, xwob, i0=0, i1=None,
                clear_on='hi_tf_counter_curl', counter_curl=None, reset_at=None):
    """[PRODUCER · Joe 0810] Walk the ws1 markers and emit a `momo_landed` event when a
    momentum-tagged r line crosses out of the fence and holds.

    Joe's spec:
        -without using lookahead, walk the ws1 markers
        --at each marker, tag the TF{8 to 33}r lines that qualify for `momentum` (momo or curl)
        --keep walking the markers (causal)
        --IF a momentum tagged line has xwob {knob:4} crossed out of the fence_momo_landed fence
        ---create a timestamped 'momo_landed' event

    Joe 0810, the four rules that were not in the written spec:
        dr          the ws1 MARKER's own side. oob-lo -> dr = bear = -1, oob-hi -> +1. Every marker
                    has a side by construction, so there is no undirected case. (gcws30b was the
                    first answer; it has no side at 78.5% of markers, so Joe moved it to ws1.)
        xwob        5 s pxs bars
        tag life    ALL tags are cleared when a momo_landed event is printed   <-- DISABLED 0810
        direction   the line must exit on the side the momentum points

    THE CLEAR, Joe 0810: "disable the current 'clear' mechanism: instead of clearing on 'first
    momentum line exiting fence', now it will be 'highest TF momentum line curling against bias'".

        clear_on='landed'              the original. a momo_landed event clears every tag.
        clear_on='hi_tf_counter_curl'  the replacement, and the default. On every bar, the HIGHEST
                                       TF among the live tags is tested for a curl against its own
                                       `dr`; when it curls, every tag clears.

    MY READINGS on the replacement, not stated by Joe:
        WHAT CURLS      `counter_curl(tf, dr, bar) -> bool`, supplied by the caller (same SRP as
                        `tagged`: the verdict needs momo_gated, which imports build_exhv2). The
                        caller runs momo_g with the OPPOSITE dr and asks for 'curl' — the same
                        gated test Joe defined on 0805, pointed the other way.
        WHICH LINE      the highest TF among the CURRENTLY LIVE tags, recomputed each bar as the
                        set changes. Not a fixed TF33.
        WHEN            EVERY bar, not only at markers. The old clear fired at landings, which land
                        on any bar; keeping the cadence means only the trigger changes.
        THE EFFECT      unchanged — ALL tags clear. Joe replaced the trigger, not the effect.

    CONSEQUENCE, flagged: a landing no longer ends the marker's tag set, so one marker can now
    produce several landings, and a line that re-enters the fence and exits again can land twice.

    ARGS
        R       {tf_minutes: r array on the 5 s grid}
        tagged  {marker_bar: {tf: dr}} — the lines that qualified for momentum at that marker.
                Computed by the CALLER, because the momentum verdict needs momo_gated, which
                imports build_exhv2. Keeping that out of here is SRP and keeps the jig light; the
                verdicts are also independent of the walk, so precomputing them is still causal.
        fence   the knob. 20 -> fence_momo_landed = [20, 80]
        xwob    consecutive 5 s bars the line must hold outside the fence

    "CROSSED OUT" NEEDS A CROSSING. MY READING, not stated by Joe: the outside-run must START at or
    after the tag — the line has to be INSIDE the fence on the bar before it goes out. A line already
    outside when it is tagged does not land on that standing position; it waits for a return inside
    and a fresh exit. The looser reading (hold xwob outside, crossing or not) is one condition away.

    Returns a list of dicts, one per event:
        bar     the bar the hold completes — the first bar the event is KNOWABLE
        cross   the bar the line went outside the fence
        tf      the line
        dr      the direction it was tagged with
        marker  the marker bar that tagged it
        val     the r value at `bar`
    Causal: every read is at or before its own bar."""
    lo_f, hi_f = float(fence), 100.0 - float(fence)
    n = len(next(iter(R.values())))
    i1 = n if i1 is None else int(i1)
    xw = max(1, int(xwob))
    if clear_on not in ('landed', 'hi_tf_counter_curl'):
        raise ValueError('clear_on must be landed | hi_tf_counter_curl, got %r' % clear_on)
    if clear_on == 'hi_tf_counter_curl' and counter_curl is None:
        raise ValueError('clear_on=hi_tf_counter_curl needs a counter_curl(tf, dr, bar) callable')
    live = {}                       # tf -> {'dr':, 'marker':, 'run':, 'cross':, 'was_inside':}
    out, clears, live_log = [], [], {}
    reset_at = set() if reset_at is None else set(reset_at)
    for i in range(i0, i1):
        # A domTF-climb ACTIVATION is a fresh start, not an addition. Joe 0812: "the domTF climb
        # BEGINS with the highest TF which has a (dr aligned) curl or momo state" — a prior tag set
        # surviving the activation would keep dominance and the named line would never lead.
        if i in reset_at:
            live.clear()
        for tf, dr in tagged.get(i, {}).items():
            live[tf] = {'dr': int(dr), 'marker': i, 'run': 0, 'cross': None, 'was_inside': False}
        if not live:
            continue
        live_log[i] = {tf: t['dr'] for tf, t in live.items()}
        fired = None
        for tf, t in list(live.items()):
            v = R[tf][i]
            if not np.isfinite(v):
                t['run'] = 0; t['cross'] = None; continue
            outside = (v > hi_f) if t['dr'] > 0 else (v < lo_f)
            if not outside:
                t['was_inside'] = True; t['run'] = 0; t['cross'] = None; continue
            if not t['was_inside']:
                continue            # standing outside since the tag — no crossing yet
            if t['run'] == 0:
                t['cross'] = i
            t['run'] += 1
            if t['run'] >= xw and not (clear_on == 'landed' and fired is not None):
                fired = {'bar': i, 'cross': t['cross'], 'tf': tf, 'dr': t['dr'],
                         'marker': t['marker'], 'val': float(v)}
                out.append(fired)
                # RE-ARM. Under 'landed' the clear made this unreachable. Under the replacement the
                # tag survives its own landing, so without a reset the line would re-fire on every
                # following bar. was_inside=False keeps the "crossed out needs a crossing" rule:
                # it has to return inside the fence and exit again. MY READING, not stated by Joe.
                t['run'] = 0; t['cross'] = None; t['was_inside'] = False
        if clear_on == 'landed':
            if fired is not None:
                live.clear()        # the original: a momo_landed event clears every tag
            continue
        # the replacement: the HIGHEST TF among the live tags, curling against its own dr
        htf = max(live)
        if counter_curl(htf, live[htf]['dr'], i):
            clears.append({'bar': i, 'tf': htf, 'dr': live[htf]['dr'],
                           'n_cleared': len(live), 'tfs': sorted(live)})
            live.clear()
    return out, clears, live_log


def _ffb(x):
    """Forward-then-back fill NaN (find_pivots stalls on the DEMA-warmup NaN; every caller cleans first)."""
    x = np.asarray(x, float).copy(); m = np.isfinite(x)
    if not m.any():
        return x
    idx = np.where(m, np.arange(len(x)), 0); np.maximum.accumulate(idx, out=idx)
    x = x[idx]; f = int(np.argmax(m)); x[:f] = x[f]
    return x


class _Causal:
    """LIVE-LEGAL reads — delegate to the real producers, honour value_mode (emerging = causal)."""
    def __init__(self, j):
        self.j = j

    def line(self, name):
        return np.asarray(self.j.W.line(name), float)                       # W.line = THE value_mode-honoured read

    def sign(self, name):
        v = self.line(name)                                                 # OOB sign: +1 hi / -1 lo / 0 in-band
        return np.where(v >= self.j.hi, 1, np.where(v <= self.j.lo, -1, 0))

    def finishers(self, tf, r_lb=None):
        """s{tf}a via the packaged s_qualify -> (qhi, qlo). qhi=short-side, qlo=long-side. r_lb defaults to
        cfg.{tf}r_lb (s15/s30); for tf without a DB lookback (e.g. s2) pass r_lb=."""
        lb = r_lb if r_lb is not None else getattr(self.j.cfg, '%sr_lb' % tf, None)
        if lb is None:
            raise ValueError("no r_lb for %s — pass r_lb=" % tf)
        return s_qualify(self.j.W, self.j.cfg, '%sm' % tf, '%sM' % tf, '%sr' % tf, lb)

    def finisher_pair(self, box=12, tf_a='s15', tf_b='s30', r_lb_a=None, r_lb_b=None):
        """CAUSAL co-occurrence event: at bar k, True iff BOTH s{tf_a}a and s{tf_b}a fired within the trailing box
        [k-box, k]. box in 5s bars (default 12 = 2x30s, the finisher tolerance). Returns (hi, lo) per-bar bools.
        This is the s30a+s15a EVENT — feed it to a consumer; don't re-bake the conjunction in a window inline."""
        ah, al = self.finishers(tf_a, r_lb_a); bh, bl = self.finishers(tf_b, r_lb_b)
        hi = _rolling_any(ah, box) & _rolling_any(bh, box)
        lo = _rolling_any(al, box) & _rolling_any(bl, box)
        return hi, lo

    def finisher_parts(self, tf, r_lb=None):
        """The per-bar COMPONENTS of s{tf}a (s_qualify_parts) for N-of-9: dict of per-side bools
        m_hi/lo, Moob_hi/lo (Mage OOB), Mrev_hi/lo (Mage reversed), rlb_hi/lo (r OOB within r_lb back).
        r_lb defaults to cfg.{tf}r_lb; pass r_lb= for a tf without a DB lookback (e.g. s2)."""
        lb = r_lb if r_lb is not None else getattr(self.j.cfg, '%sr_lb' % tf, None)
        if lb is None:
            raise ValueError("no r_lb for %s — pass r_lb=" % tf)
        return s_qualify_parts(self.j.W, self.j.cfg, '%sm' % tf, '%sM' % tf, '%sr' % tf, lb)

    def fin_unlatch_6of9(self, arm, cap, side, q15, q30, sets=(('gcs5', 29), ('s15', None), ('s30', None)),
                         N=6, box_lb=None, tol=None, bind_tol=6, anchor='breach'):
        """Two-stage arm-unlatch entry (Joe 0710):
          QUALIFIER  fin_box_qualified — s15a AND s30a in the box [arm-box_lb, arm+tol]. Validates the trade.
          TRIGGER    fin_unlatch_nof9 — the >=N-of-9 confluence at/after the arm, bound within bind_tol.
        gcs5a is only in the TRIGGER (preens the entry delay), never the qualifier.  Returns the trade bar or None.
        sets = ((set_name, r_lb_override), ...); r_lb None -> cfg.{set}r_lb.  box_lb/tol None -> cfg.fin_lb/fin_fwd."""
        blb = self.j.cfg.fin_lb if box_lb is None else box_lb
        tl = self.j.cfg.fin_fwd if tol is None else tol
        if not fin_box_qualified(q15, q30, arm, blb, tl):          # QUALIFIER owns box_lb/tol
            return None
        parts = {s: self.finisher_parts(s, r_lb=rlb) for (s, rlb) in sets}
        return fin_unlatch_nof9(parts, arm, cap, side, N=N, bind_tol=bind_tol, anchor=anchor)  # cap = the arm cancel

    def rpl_fin_6of9(self, arm, cap, side, sets=(('s1', 19), ('s2', 19), ('s15', 19)),
                     N=6, bind_tol=6, anchor='breach'):
        """[RPL·0726] The >=N-of-9 finisher the s3s4 gate hands off to (replaces the s30 latch finisher in the lab
        chain). PURE fin_unlatch_nof9 TRIGGER — NO box qualifier: the s3s4 gate IS the qualifier, so `arm` is the
        gate-open bar (no q15/q30 box). sets = the s1a/s2a/s15a bundles, each -> finisher_parts (= s_qualify_parts:
        {m OOB, Mage OOB, r-in-lookback}). r_lb None -> cfg.{set}r_lb; s1/s2 have NO cfg lookback -> the sets tuple
        must carry an explicit own-TF-bar count (as gcs5 carries 29 in fin_unlatch_6of9). cap = the arm cancel;
        the trigger scans arm..cap. side +1 hi / -1 lo. Returns the trade bar or None."""
        parts = {s: self.finisher_parts(s, r_lb=rlb) for (s, rlb) in sets}
        return fin_unlatch_nof9(parts, arm, cap, side, N=N, bind_tol=bind_tol, anchor=anchor)

    def s_qualify_reset(self, side, bundle='s3a'):
        """[RPL·0729] Joe: "reset if all s3 lines are IB, or if any line is in the opposite OOB".
        Per-bar bool = the s{bundle} qualify latch must DROP at this bar. Its own producer, not an
        expression inside s3a_cross (SRP; same lift as delegate_tf out of _climb_to_prov).
          side  : the qualify's side, +1 hi / -1 lo. OPPOSITE OOB is therefore lo for +1, hi for -1.
          IB    : strictly inside the boundary, lo < v < hi — the "all quiet" reset.
        Reads the bundle's own three lines (m / M / r). Causal: per-bar values only, no lookahead."""
        hi, lo = self.j.cfg.hi, self.j.cfg.lo
        L = [self.line(bundle + c) for c in ('m', 'M', 'r')]
        all_ib = np.logical_and.reduce([(v > lo) & (v < hi) for v in L])
        opp = np.logical_or.reduce([(v <= lo) for v in L] if side > 0 else [(v >= hi) for v in L])
        return all_ib | opp

    def s3a_cross(self, side, r_lb, wob, bundle='s3a', x='s3x', reset=False, s4r_support=None,
                  unlatch=None):
        """[RPL·0727] The s3a PRE-FINISHER event (Joe): the standard s{bundle} qualify — Mage-reversal + m OOB +
        M OOB + r-in-lookback, via s_qualify — followed by a wob-debounced cross of line `x` through the bundle's
        m toward the TRADE direction. Delegates both halves (s_qualify, cross_wob); nothing re-implemented here.
          side  : the exhaustion side, +1 hi / -1 lo. Trade dir = -side, so a lo exhaustion (LONG) wants x to
                  cross OVER m, a hi exhaustion (SHORT) wants x to cross UNDER m.
          r_lb  : the qualify's r-lookback, in the r-line's OWN TF bars (s2a/s3a carry it explicitly, e.g. 19).
          wob   : cross debounce in EMERGING 5s bars (Joe: wobs are 5s, tolerances/lookbacks are TF-relative).
        Returns a per-bar bool: a cross CONFIRMED at this bar with a qualify already latched at/before it.
        Causal. Which cross to act on is the CALLER's orchestration — this only defines the event.

        OPT-IN (Joe 0729; both default OFF so the live chain is byte-identical to before):
          reset        : True -> the qualify latch DROPS on s_qualify_reset (all bundle lines IB, or any in
                         the OPPOSITE OOB). Without it the latch is a cummax over the whole tape and never
                         resets — measured 0729: first latch 37.6 days before the test window, 100% of raw
                         cross edges fire, 492 events/day, while the qualify itself is true on 1.7% of bars.
          s4r_support  : line name (e.g. 's4r') whose SAME-SIDE OOB, over the SAME r_lb window, also
                         satisfies the qualify's r term. Joe: "s3a to rely on s4r when it can't see s3r
                         inside of its r-lookback" — for a leg that coasts into the pivot, leaving the
                         bundle's own r waving mid-board. r_lb stays in the BUNDLE r's TF bars (Joe: "for
                         this specific event, use s3r's lookback range").
          unlatch      : per-bar bool; True DROPS the latch at that bar. Joe: "s3a+x-cross as a latch that
                         unlatches when fin_6of9 fires" — the caller owns what fires, this owns the latch."""
        qhi, qlo = self.finishers(bundle, r_lb=r_lb)
        q = (qhi if side > 0 else qlo).copy()
        if s4r_support:                       # ONLY the r term is relaxed; the other three are untouched
            p = self.finisher_parts(bundle, r_lb=r_lb)
            ns = not bool(self.j.cfg.fin_s30M_oob)
            hi, lo = self.j.cfg.hi, self.j.cfg.lo
            if side > 0:
                base, own = p['Mrev_hi'] & p['m_hi'] & (p['Moob_hi'] | ns), p['rlb_hi']
            else:
                base, own = p['Mrev_lo'] & p['m_lo'] & (p['Moob_lo'] | ns), p['rlb_lo']
            sup = self.line(s4r_support)
            rlb = r_lb * (self.j.W._ls.resolve(bundle + 'r')[0] // 5)      # bundle r's own TF bars -> base bars
            sup_ok = _rolling_any(sup >= hi if side > 0 else sup <= lo, rlb)
            q = base & (own | sup_ok)
        drop = np.zeros(len(q), bool)
        if reset:
            drop |= self.s_qualify_reset(side, bundle)
        if unlatch is not None:
            drop |= np.asarray(unlatch, bool)
        latched = _latch_with_reset(q, drop) if drop.any() else (np.maximum.accumulate(q.astype(np.int8)) > 0)
        d = -1 if side > 0 else 1                                          # trade dir = reversal of the exhaustion
        conf = self.cross_wob(self.line(x) - self.line(bundle + 'm'), 0.0, d, wob)
        edge = conf & ~np.r_[False, conf[:-1]]                             # rising edge = the confirmation bar
        return edge & latched

    def arms(self):
        return v2_arm(self.j.W, self.j.cfg)                                 # [(i, es, bd, cap, src)]

    def gates(self, arms=None):
        return gate_open(self.j.W, self.j.cfg, arms if arms is not None else self.arms())

    def predict(self, k, m, M, tol=0.0):
        return predict_breach(k, m, M, self.j.hi, self.j.lo, FENCE_HI, FENCE_LO, tol)

    def predict_set(self, prefix, tol=0.0, maj='M'):
        """Predicted-breach direction for a whole line SET, by name: predict_set('s3') reads s3r/s3m/s3M.
        maj='Mage' for the sets whose Major is named s{n}Mage. `tol` is the sweepable value-point allowance
        (0.0 = spec).  Ungated — the "test while the mini is OOB" gate is the CONSUMER's (see mini_oob);
        lr_v2.gate_signals keeps them separate for the same reason."""
        return self.predict(self.line(prefix + 'r'), self.line(prefix + 'm'),
                            self.line(prefix + maj), tol)

    def mini_oob(self, prefix):
        """+1/-1/0 OOB sign of the set's mini — the gate lr_v2.gate_signals applies to a prediction
        ('test r predict while s{n}m is OOB'). Kept separate from predict_set (SRP)."""
        return self.sign(prefix + 'm')

    def reversal(self, line, wob):
        """Boundary-agnostic reversal of a line (lr_v2._mage_rev): +1 up-turn / -1 down-turn confirmed after `wob`
        consecutive same-direction steps (wob<=0 = first slope-flip). Causal — fires from steps <= the bar."""
        return np.asarray(_mage_rev(np.asarray(line, float), wob))

    def ws1mage_rev(self, sig_mage='gcws30Mage', g1='ws1Mage', hi=None, lo=None, **kw):
        """`ws1mage-rev` (Joe 0911 named it). Delegates to the module producer. Lines by NAME by
        default - ws1Mage and gcws30Mage - or pass arrays. hi/lo default to the jig's own
        boundaries. See the producer for the three legs and every knob."""
        g = self.line(g1) if isinstance(g1, str) else g1
        m = self.line(sig_mage) if isinstance(sig_mage, str) else sig_mage
        return ws1mage_rev(g, m, self.j.cfg.hi if hi is None else hi,
                           self.j.cfg.lo if lo is None else lo, **kw)

    def clean_dirty(self, r, x, side, hi, lo, fh, fl, wob, mode='exhv2', spend_bars=None):
        """[PRODUCER · Joe 0731] The clean/dirty flag on one r line. Causal, no lookahead.

        A line is DIRTY when its move is spent and has not re-formed. It exists to stop an r-pred firing
        on a line retreating from OOB back down through the FH..HI band - the same band a genuine
        pre-breach prediction occupies.

          dirty <- the line has LEFT ITS FENCE and a spend fires
          clean <- EITHER of two scenarios, both first-class (verbatim for RPL and exhv2):
                     1. x crosses BACK through r. A higher TF spent the line early; price swung back and
                        x travelled back out to OOB to collect the swing.
                     2. r returns to the FH/FL fence.
          lines start DIRTY - at bar 0 a line already outside its fence cannot be told from a retreat.

        mode selects the SPEND only; everything else is shared.
          'rpl'    spend_bars = bar indices of applied exhaustions (GLOBAL - any TF, matching bias).
          'exhv2'  spend = THIS line's own x crossing r or the boundary. Line-local, no exhaustion.
                   Joe 0731: "'exhaustion' only applies to RPL. The definition needs to state 'an x
                   crossing boundary or r'."

        side: +1 bull (fence FH, boundary HI, spends DOWNWARD) / -1 bear (FL, LO, spends UPWARD).
        Every crossing is cross_wob-debounced at `wob` - raw r>=FH flickers exactly as predict_breach does.
        Returns the boolean dirty[] over the full tape."""
        r = np.asarray(r, float); x = np.asarray(x, float)
        d = -1 if side > 0 else 1                       # bull spends downward through r / the boundary
        out = self.cross_wob(r - (fh if side > 0 else fl), 0.0, 1 if side > 0 else -1, wob)
        edge = lambda delta, k: (lambda c: c & ~np.r_[False, c[:-1]])(self.cross_wob(delta, 0.0, k, wob))
        if mode == 'rpl':
            spend = np.zeros(len(r), bool)
            if spend_bars is not None and len(spend_bars):
                spend[np.asarray(spend_bars, int)] = True
        elif mode == 'exhv2':
            spend = edge(x - r, d) | edge(x - (hi if side > 0 else lo), d)
        else:
            raise ValueError('clean_dirty mode must be rpl or exhv2, got %r' % mode)
        back = ~out & np.r_[False, out[:-1]]            # r re-entered the fence
        recov = edge(x - r, -d) | back                  # x back through r, OR fence re-entry
        return ~_latch_with_reset(recov, spend & out)   # starts dirty; set-wins-on-ties via the latch

    def cross_wob(self, line, level, direction, n):
        """Wobble-debounced boundary crossover ('crossover_wob', from the CP1 hs30x arm, hand-rolled there).
        direction=-1: `line` crossed UNDER `level`; +1: crossed OVER. The cross is CONFIRMED once the line has
        held the crossed side for `n` consecutive 5s bars — a single bar back across resets the run (demands a
        clean cross; not a bump-tolerance). Returns per-bar bool = confirmed-in-effect; the consumer takes the
        RISING EDGE for the confirmation moment. Causal (reads only <= the bar). `line` = name or value array."""
        v = self.line(line) if isinstance(line, str) else np.asarray(line, float)
        side = (v < level) if direction < 0 else (v > level)
        idx = np.arange(len(side))                        # vectorised run-length (was a per-bar Python loop, ~13x):
        reset = np.where(side, 0, idx + 1)                # consecutive-True count ending at i = (i+1) minus the
        run = (idx + 1) - np.maximum.accumulate(reset)    # last False position. Bit-identical incl NaN (NaN cmp -> False).
        return run >= max(1, int(n))

    def seen_within(self, cond, n):
        """[PRODUCER · Joe 0803] Was `cond` true at ANY bar in the trailing `n` 5s bars, inclusive of this one.

        The COMPLEMENT of cross_wob's run test: cross_wob asks "held for n bars", this asks "true at least
        once in n bars". Both are causal — neither reads past the bar.

        Joe 0803 asked for it by name on the s6 exit: "could the answer be to look back 6 minutes for the
        OOB s6m ?". The exit gate had been testing s6m OOB AT the cross bar, which cannot fire while s6Mage
        is in bounds — for s6m to cross DOWN through an s6Mage sitting at 65 it must fall to 65, which is
        under HI. A trailing look-back decouples the two.

        `cond` = boolean array (or a line name, compared truthy is meaningless, so array only).
        Returns per-bar bool. n<=1 degenerates to `cond` itself."""
        c = np.asarray(cond, bool)
        k = max(1, int(n))
        if k == 1:
            return c.copy()
        cs = np.concatenate([[0], np.cumsum(c.astype(np.int64))])
        i = np.arange(len(c))
        return (cs[i + 1] - cs[np.maximum(0, i - k + 1)]) > 0

    def divergence(self, osc, px, hi, lo, i0=0, i1=None):
        """*** PSEUDO-DISABLED, Joe 1026. USE `anchor_floater` - THE DIVERGENCE READ. ***
        The module producer returns an all-NaN sig and a sentinel episodes list; read its docstring.
        Delegates to the module producer.
        Two lookbacks based on EXTREMAS: consecutive same-side OOB episodes, each contributing its
        own extreme, confirmed at the episode end. `osc` and `px` are arrays (px = RAW close);
        `hi`/`lo` are the episode fence and are required. -> (sig, episodes). See the producer."""
        return divergence(osc, px, hi, lo, i0=i0, i1=i1)

    def anchor_floater(self, r, px, dr, k, **kw):
        """THE DIVERGENCE READ - Joe's four-step anchor/floater selection at bar `k`. When this
        project says DIVERGENCE it means this and its `state`, not the pseudo-disabled
        `jig.divergence`. Delegates to `anchor_floater`.
        `r` and `px` are arrays on this jig's grid - pass jig.causal.line('ws1r') and RAW close."""
        return anchor_floater(r, px, dr, k, **kw)

    def sideways_reversal(self, r, px, dr, i0=0, i1=None, **kw):
        """Joe 0912's flat-run + divergence hypothesis -> `sideways` and the new `reversal` state.
        Delegates to `sideways_reversal`. NOT YET SCORED."""
        return sideways_reversal(r, px, dr, i0=i0, i1=i1, **kw)

    def pk_state(self, line_slope, price_slope, slope_floor):
        """OBSOLETE as the divergence calc - Joe 0912: "build it in the jig, and leave notes on all
        other divergence calcs to let them know they're obsolete". Use jig.causal.divergence, which
        pairs two EXTREMAS from consecutive OOB episodes instead of a fixed bar offset. Kept because
        the live bias machine, the pine-parity path and build_dominoes_db still call the seam.

        Slope-sign divergence state — delegates to the production seam Pk5sGateComputer._pk_state_from_slopes
        (the PK / vote-machine core). sign(line_slope) != sign(price_slope) -> DIVERGENCE +1 (bull, line rising) /
        -1 (bear, line falling); signs AGREE -> PM +-2 ('Price Match', trend continuation, NOT a divergence);
        |line_slope - price_slope| <= slope_floor -> 0 (noise band). Scalars or arrays.
        Caller supplies line_slope = osc(anchor)-osc(floater), price_slope = price(anchor)-price(floater);
        the price SOURCE (raw close vs px_smooth) is the caller's choice (divergence_research.md §12: raw)."""
        from optimus9.compute.pk5s_gate_computer import Pk5sGateComputer
        return np.asarray(Pk5sGateComputer._pk_state_from_slopes(line_slope, price_slope, slope_floor), float)

    def coarse(self, name, seam_ms):
        """Sample an EMERGING line at every seam_ms boundary (e.g. 300000 = 5-min). -> (ts_c, vals)."""
        v = self.line(name); mask = (self.j.ts % seam_ms) == 0
        return self.j.ts[mask], v[mask]

    def curl(self, ts_c, c, direction, with_val=False):
        """Causal trough(direction +1)/peak(-1) on a coarse series: fires one seam AFTER the turn, past data only.
        Returns the set of 5s-timestamps at which a curl is confirmed. with_val=True -> {ts: turn_value} (the value at
        the turn point c[k-1]) so the consumer can gate a curl by which side of the board it turned on.
        Delegates to lr_v2._curl_detect — the single curl-detection impl (SRP; also used by lr_exit_v2)."""
        return _curl_detect(np.asarray(ts_c), np.asarray(c, float), direction, with_val)

    def coarse_reverse(self, name, seam_ms, floor=0.0):
        """Joe's 3-point coarse reversal (boundary-agnostic, 0715). Between two consecutive seams — anchor (1st)
        and floater (2nd) — the extreme is the max/min of the EMERGING line BETWEEN them. A PEAK reversal (-1,
        down-turn) is confirmed at the floater when the between-max protrudes past the HIGHER endpoint by more
        than `floor`; a TROUGH (+1, up-turn) when the between-min drops past the LOWER endpoint by more than
        `floor`. floor=0.0 = any protrusion (a bare wiggle counts); raise it to demand a decisive turn. Causal —
        only past data, confirmed at the floater. Per-5s-bar: nonzero only on the floater seam bar. `seam_ms` may
        be sub-bar (intra-bar seams) for a tighter, more precise reversal window. Distinct from curl() (3
        consecutive coarse samples, extreme AT a seam) — here the extreme is sub-seam."""
        v = self.line(name); ts = self.j.ts
        seams = np.flatnonzero((ts % seam_ms) == 0)
        out = np.zeros(len(ts), int)
        for si in range(1, len(seams)):
            a, f = seams[si - 1], seams[si]
            seg = v[a:f + 1]
            mx, mn = float(seg.max()), float(seg.min())
            if mx - max(v[a], v[f]) > floor:
                out[f] = -1                              # peak between -> down-reversal
            elif min(v[a], v[f]) - mn > floor:
                out[f] = 1                               # trough between -> up-reversal
        return out

    def seam_prev(self, name, seam_ms):
        """Per-5s-bar: the value of `name` at the most recent seam boundary STRICTLY BEFORE this bar.
        Causal (never reads the current seam's own sample). The seam grid is global (ts % seam_ms == 0), so a
        bar at the start of a coarse bar reads the last seam of the PREVIOUS coarse bar — no intra-bar gap and
        no special case at the open (Joe 0713).

        Companion to coarse(): coarse() gives the seam samples, seam_prev() holds the last one per bar so a
        consumer can compare a LIVE value against where the line stood one seam ago."""
        v = self.line(name); ts = self.j.ts
        seams = np.flatnonzero((ts % seam_ms) == 0)
        if not len(seams):
            return np.full(len(ts), np.nan)
        i = np.searchsorted(ts[seams], ts, side='left') - 1        # last seam with ts_seam < ts[k]
        out = np.full(len(ts), np.nan)
        ok = i >= 0
        out[ok] = v[seams[i[ok]]]
        return out

    def closed_prev(self, name, seam_ms):
        """Causal 'last CLOSED coarse value': the EMERGING value of `name` at the last 5s bar of the most
        recently COMPLETED bucket — the bar immediately BEFORE the most recent seam (seam-5s). Held forward
        through the next bucket. This is the value TradingView shows as the coarse bar's CLOSE
        (emerging_bar_open.md: emerging@(seam-5s) == TV closed), read causally.

        THREE reads of 'the coarse value', do not confuse them:
          - seam_prev(name, seam_ms)  -> emerging AT the seam = the new bucket's single-candle OPEN
                                          (the bar-open sawtooth value; NOT a close).
          - value_mode='closed' line  -> the CURRENT forming bucket's eventual close = LOOK-AHEAD
                                          (the o9-live failure, project_v2_lookahead). Never gate on it.
          - closed_prev(name, seam_ms)-> the PREVIOUS completed bucket's close, causal. Use THIS for a
                                          'last closed coarse bar' gate."""
        v = self.line(name); ts = self.j.ts
        seams = np.flatnonzero((ts % seam_ms) == 0)
        if not len(seams):
            return np.full(len(ts), np.nan)
        i = np.searchsorted(ts[seams], ts, side='left') - 1        # last seam strictly before this bar
        out = np.full(len(ts), np.nan)
        ok = (i >= 0) & (seams[np.clip(i, 0, None)] - 1 >= 0)      # need a bar before that seam
        out[ok] = v[seams[i[ok]] - 1]                              # the bucket-close bar (seam - 5s)
        return out

    def cross(self, a, b, grid_ms):
        """Causal line-vs-line CROSS on a grid: +1 where `a` crossed ABOVE `b`, -1 where it crossed BELOW,
        comparing each grid boundary to the previous one. Non-grid bars are 0.

        Distinct from sign() (a-vs-BOUNDARY) and reversal() (a-vs-its-own-slope) — this is a-vs-ANOTHER-LINE.
        `grid_ms` is the evaluation cadence and is a sweepable knob: a coarser grid filters 5s chop out of the
        cross moment (Joe 0713: "fire every 30 seconds — this improves the timing of the s1m x s1r moment").
        a/b are line NAMES or value arrays."""
        av = self.line(a) if isinstance(a, str) else np.asarray(a, float)
        bv = self.line(b) if isinstance(b, str) else np.asarray(b, float)
        ts = self.j.ts
        g = np.flatnonzero((ts % grid_ms) == 0)
        out = np.zeros(len(ts), int)
        if len(g) < 2:
            return out
        d = av[g] - bv[g]
        prev, cur = d[:-1], d[1:]
        out[g[1:]] = np.where((prev <= 0) & (cur > 0), 1, np.where((prev >= 0) & (cur < 0), -1, 0))
        return out

    def seam_since(self, cond, seam_ms):
        """Causal: at every 5s bar, True iff `cond` held at ANY bar since the CURRENT seam bucket opened
        (inclusive of the seam bar and of now). Resets at each seam.

        The running-extreme gate (Joe 0713: "test at the seams, but between the seams collect the min/max").
        seam_hold() samples the condition AT the seam and freezes it, so a breach landing mid-bucket is
        invisible until the next seam — up to a full seam-width late (5 min on TF20/4; it dropped the 18:42
        and 10:22 turns). seam_since() instead asks whether the line has touched the state at any point in
        the bucket so far, so the gate answers within one bar of the breach and still resets on the seam.

        cond is any per-bar bool: pass (sign(name) == es) and this IS the running max/min test."""
        c = np.asarray(cond, bool)
        ts = self.j.ts
        bucket = ts // int(seam_ms)                                  # which seam interval each bar is in
        new = np.concatenate([[True], bucket[1:] != bucket[:-1]])    # first bar of each bucket
        # running OR within the bucket: cumulative count of True, minus the count at the bucket's start
        cc = np.cumsum(c)
        base_idx = np.maximum.accumulate(np.where(new, np.arange(len(c)), 0))
        base = cc[base_idx] - c[base_idx]                            # count strictly before the bucket start
        return (cc - base) > 0

    def reset_since(self, event, reset):
        """Causal: True at bar k iff `reset` has occurred at or after the most recent `event` — i.e. the
        thing has been RE-ARMED since it last fired. True before any event ever occurs.

        The re-fire guard (Joe 0714): an r that has completed an OOB excursion on a side must return to
        neutral ground before it may be counted as setting up for that SAME side again. Without it, the
        mini's next dive re-predicts a breach the r has just finished making — s19r spent 87 min OOB-low,
        left at 10:26, and was re-predicted low at 10:47 from 28.4, never having crossed 50.

        event = the OOB-on-es state.  reset = the midline cross (or whatever neutral test the caller wants)."""
        e = np.asarray(event, bool)
        r = np.asarray(reset, bool)
        n = len(e)
        idx = np.arange(n)
        last_e = np.maximum.accumulate(np.where(e, idx, -1))
        last_r = np.maximum.accumulate(np.where(r, idx, -1))
        return last_r >= last_e

    def hold_at_start(self, episode, sample):
        """Causal: while `episode` is True, carry the value `sample` held on the bar the episode BEGAN.
        False outside the episode, and False for an episode already running at the tape head.

        'Was it already true when the thing started?' (Joe 0713: "previously predicted = was predicted when
        s20m went OOB"). Not a rolling memory — the state is sampled ONCE, at the breach, and latched for
        that breach's life. Reads only the episode's own start bar, so it is causal from the start bar on."""
        e = np.asarray(episode, bool)
        s = np.asarray(sample, bool)
        start = e & ~np.concatenate([[False], e[:-1]])          # IB->OOB transition
        idx = np.where(start, np.arange(len(e)), -1)
        idx = np.maximum.accumulate(idx)                        # most recent start at/before each bar
        out = np.zeros(len(e), bool)
        ok = e & (idx >= 0)
        out[ok] = s[idx[ok]]
        return out

    def grid_any(self, cond, grid_ms, n):
        """Causal: at each grid boundary, True iff `cond` held at ANY of the last `n` grid samples
        (inclusive of this one). Non-grid bars are False.

        'WAS x and now y' (Joe 0713) — a fast line can leave a state in the same step that produces the
        event you want to catch (s1m drops out of OOB on the very sample it crosses s1r), so the state test
        must look back a sample, not read the event bar. `n` is the sweepable memory: n=1 is 'is', n=2 is
        'is or was one sample ago'."""
        c = np.asarray(cond, bool)
        ts = self.j.ts
        g = np.flatnonzero((ts % grid_ms) == 0)
        out = np.zeros(len(ts), bool)
        if not len(g):
            return out
        cg = c[g]
        acc = np.zeros(len(g), bool)
        for i in range(int(n)):
            acc |= np.concatenate([np.zeros(i, bool), cg[:len(cg) - i]]) if i else cg
        out[g] = acc
        return out

    def seam_hold(self, cond, seam_ms):
        """Per-5s-bar: a per-bar condition SAMPLED at each seam boundary and HELD until the next one.
        'Tested at each intra-bar seam' (Joe 0713) — the gate has a value between seams, and that value is the
        one the seam last saw. Causal. `cond` = any per-bar array (bool/int/float)."""
        c = np.asarray(cond)
        ts = self.j.ts
        seams = np.flatnonzero((ts % seam_ms) == 0)
        if not len(seams):
            return np.zeros(len(ts), c.dtype)
        i = np.searchsorted(ts[seams], ts, side='right') - 1        # last seam with ts_seam <= ts[k]
        out = np.zeros(len(ts), c.dtype)
        ok = i >= 0
        out[ok] = c[seams[i[ok]]]
        return out


class _Score:
    """HARNESS / SCORING — NON-CAUSAL. Never call these inside a strategy."""
    def __init__(self, j):
        self.j = j

    def swings(self, price=None, pct=None):
        p = _ffb(self.j.px if price is None else price)
        return find_pivots(p, pct if pct is not None else self.j.cfg.swing_pct)

    def legs(self, pivots=None, price=None):
        p = _ffb(self.j.px if price is None else price)
        return legs(p, pivots if pivots is not None else find_pivots(p, self.j.cfg.swing_pct))

    def entry_quality(self, entries, swing_pct=None):
        """Packaged entry-quality verdict (lr_walk): MAE/MFE from entry to the next FAVOURABLE swing (exit-INDEPENDENT)
        + mfe_side (did the trade open on the MFE side of the swing?). entries = [(trade_ms, es, bd, bar_idx)] ->
        [(trade_ms, dt, es, bd, mae, mfe, mfe_ok, mfe_side, price)].

        swing_pct (0714): the SCALE the MAE/MFE is measured against — the favourable swing lr_walk walks to.
        None = cfg.swing_pct (the DB default). Pass 4.0/3.0/2.0 to score the same entries against bigger
        swings. Without this the scale is silently fixed and a swing sweep is a no-op."""
        cfg = self.j.cfg
        if swing_pct is not None and float(swing_pct) != float(cfg.swing_pct):
            cfg = copy.copy(cfg)
            cfg.swing_pct = float(swing_pct)
        return lr_walk(self.j.W, entries, cfg)

    def table(self, rows, headers, row_fmt):
        print("  ".join(headers))
        for r in rows:
            print(row_fmt % tuple(r))

    def _labels_frag(self, labels, scheme='redgreen', transp=75):
        """The label array-defs + barstate.islast loop as a pine fragment (no header). Shared by emit_labels
        (standalone) and emit_overlay (labels + bgcolor in one indicator). transp = label colour transparency
        (0 solid .. 100 invisible; default 75 so dense label sets don't hide price — Joe 0717)."""
        T = [int(l['ts']) for l in labels]; Y = [round(float(l['y']), 6) for l in labels]
        # Escape REAL newlines and quotes only — never backslashes. Pine has no multi-line string literal,
        # so a raw \n inside "..." will not parse. Callers that already pass the two characters \ n keep
        # working untouched; callers that pass a real newline now also work (Joe 0802).
        _esc = lambda s: str(s).replace('"', '\\"').replace('\n', '\\n')
        TXT = [_esc(l['text']) for l in labels]
        UP = ['true' if l.get('up') else 'false' for l in labels]
        GRN = ['true' if l.get('green') else 'false' for l in labels]
        ai = lambda v: "array.from(" + ", ".join(str(int(z)) for z in v) + ")" if v else "array.new_int(0)"
        af = lambda v: "array.from(" + ", ".join(str(z) for z in v) + ")" if v else "array.new_float(0)"
        as_ = lambda v: "array.from(" + ", ".join('"%s"' % z for z in v) + ")" if v else "array.new_string(0)"
        ab = lambda v: "array.from(" + ", ".join(v) + ")" if v else "array.new_bool(0)"
        frag = ('''f_t()   => %s
f_y()   => %s
f_txt() => %s
f_up()  => %s
f_grn() => %s
if barstate.islast
    tt = f_t()
    yy = f_y()
    tx = f_txt()
    up = f_up()
    gr = f_grn()
    for i = 0 to array.size(tt) - 1
        col = array.get(gr, i) ? color.new(color.green, 15) : color.new(color.red, 15)
        stl = array.get(up, i) ? label.style_label_up : label.style_label_down
        label.new(array.get(tt, i), array.get(yy, i), array.get(tx, i), xloc = xloc.bar_time, color = col, style = stl, textcolor = color.white, size = size.normal)
''' % (ai(T), af(Y), as_(TXT), ab(UP), ab(GRN)))
        if scheme == 'blueyellow':
            frag = frag.replace("color.new(color.green, 15) : color.new(color.red, 15)",
                                "color.new(color.yellow, 15) : color.new(color.blue, 15)")
            frag = frag.replace("textcolor = color.white",
                                "textcolor = (array.get(gr, i) ? color.black : color.white)")
        frag = frag.replace(", 15)", ", %d)" % int(transp))       # apply the label transparency
        return frag

    def emit_labels(self, labels, path, title, scheme='redgreen', transp=75):
        """Pine emit: labels = [{ts:int-ms, y:float, text:str, green:bool, up:bool}]. green->green/red bg-tone,
        up->style_label_up/down. scheme='blueyellow' recolours green->yellow(black text)/red->blue(white text)
        for an A/B overlay against the redgreen pine. transp = colour transparency (default 75). Function-wrapped
        arrays + barstate.islast loop (TV op-limit safe)."""
        body = '//@version=5\nindicator("%s", overlay = true, max_labels_count = 500)\n' % title
        body += self._labels_frag(labels, scheme, transp)
        open(path, "w").write(body)
        return len(labels)

    def _bgcolor_frag(self, streams, opacity=None, notes=None):
        """### FORMAT IS LOCKED - DO NOT CHANGE IT WITHOUT JOE'S AUTHORISATION (Joe 0731). ###
        The emitted shape is: header note -> indicator() -> one input.bool per stream -> one f_<name>()
        array function per stream -> the array calls -> `bg = color(na)` -> one `if` per stream assigning
        `bg :=` with a LITERAL transparency -> a SINGLE bgcolor(bg). Joe 0731 pasted the target block:

            bg = color(na)
            if show_s_walk_hi and array.binary_search(s_walk_hi, time) >= 0
                bg := color.new(color.blue, 0)
            if show_s_walk_lo and array.binary_search(s_walk_lo, time) >= 0
                bg := color.new(color.yellow, 0)
            if show_s_sig_short and array.binary_search(s_sig_short, time) >= 0
                bg := color.new(color.red, 47)
            if show_s_sig_long and array.binary_search(s_sig_long, time) >= 0
                bg := color.new(color.green, 0)
            bgcolor(bg)

        I have broken this TWICE in one session - once by "improving" it to per-stream bgcolor() calls,
        once by replacing the literals with an `opac` input slider. Both were reverted. Colours, stream
        order, toggle labels, the literal transparencies, the single bgcolor(bg) - none of it changes on
        my judgement.
        KNOWN AND ACCEPTED: a single `bg` var means the LAST matching `if` wins, so on a shared bar the
        later stream hides the earlier one. Order is priority. That is a property of the format, not a
        bug to fix unilaterally.

        Pine bgcolor fragment from named 5s-timestamp streams (the array-bgcolor pattern — arm_gate_emit,
        lp_cascade_emit, og_arm_emit all hand-rolled this; now it lives once here). Returns (frag, hdr, total);
        emit_bgcolor wraps it standalone, emit_overlay stacks labels on top.

        streams = [{'name': str, 'ts': [int-ms...], 'color': 'color.green'}, ...].
        Order is PRIORITY: later streams paint over earlier ones on a shared bar. Each stream gets an
        input.bool toggle. Arrays are chunked at 400 (TV op-limit) and looked up with array.binary_search
        on `time`, so the whole thing evaluates on the last bar only."""
        arr = lambda v: ("array.from(" + ", ".join(str(int(z)) for z in v) + ")") if v else "array.new_int(0)"

        def emit_arr(nm, vals):
            vals = sorted(set(int(v) for v in vals))                 # binary_search needs sorted, unique
            if len(vals) <= 400:
                return "f_%s() =>\n    %s" % (nm, arr(vals)), "%s = f_%s()" % (nm, nm), len(vals)
            chunks = [vals[i:i + 400] for i in range(0, len(vals), 400)]
            d = "\n".join("f_%s_%d() =>\n    %s" % (nm, i, arr(c)) for i, c in enumerate(chunks))
            d += "\nf_%s() =>\n    a = f_%s_0()\n" % (nm, nm)
            d += "".join("    array.concat(a, f_%s_%d())\n" % (nm, i) for i in range(1, len(chunks)))
            d += "    a"
            return d, "%s = f_%s()" % (nm, nm), len(vals)

        defs, calls, toggles, paints, total = [], [], [], [], 0
        for s in streams:
            label = s['name']
            nm = 's_' + label                                        # prefix: never collide with a Pine keyword
            d, c, cnt = emit_arr(nm, s['ts']); total += cnt
            defs.append(d); calls.append(c)
            toggles.append('show_%s = input.bool(true, "%s (%s)")' % (nm, label, s['color'].split('.')[-1]))
            # PER-STREAM LITERAL transparency. Joe 0731 pasted the target block verbatim:
            #   blue 0 | yellow 0 | red 47 | green 0
            # RED_BG_TRANSP = 47 applies to color.red ONLY (a solid red bgcolor masks the bearish candle
            # body); every other stream keeps the caller's `opacity`. NO `opac` input - I added one and
            # Joe rejected it. A stream may still override with an explicit per-stream 'opacity' key.
            op = int(s['opacity']) if s.get('opacity') is not None else (
                RED_BG_TRANSP if s['color'] == 'color.red' else (opacity or 0))
            paints.append('if show_%s and array.binary_search(%s, time) >= 0\n'
                          '    bg := color.new(%s, %d)' % (nm, nm, s['color'], op))
        frag = ("\n".join(toggles) + "\n" + "\n".join(defs) + "\n" + "\n".join(calls)
                + "\nbg = color(na)\n" + "\n".join(paints) + "\nbgcolor(bg)\n")
        # `notes` = the config the emit was BUILT from, carried into the .pine as a comment block (Joe 0713).
        # The chart is read hours later, often beside a newer run — a pine that cannot say which knobs
        # produced it is a human-error trap. The header travels with the artefact.
        hdr = ''
        if notes:
            lines = notes.split('\n') if isinstance(notes, str) else list(notes)
            hdr = "\n".join('// ' + ln for ln in lines) + "\n"
        return frag, hdr, total

    def emit_bgcolor(self, streams, path, title, opacity=None, notes=None):
        frag, hdr, total = self._bgcolor_frag(streams, opacity, notes)
        body = '//@version=5\n' + hdr + 'indicator("%s", overlay = true)\n' % title + frag
        open(path, "w").write(body)
        return total

    def emit_overlay(self, labels, streams, path, title, opacity=60, scheme='redgreen', notes=None):
        """ONE indicator = bgcolor streams (painted first) + trade labels on top. Use when the labels are the
        signal and the bgcolor is an added A/B layer (e.g. OOBW-tweak spans under the entry labels)."""
        frag, hdr, total = self._bgcolor_frag(streams, opacity, notes)
        body = ('//@version=5\n' + hdr + 'indicator("%s", overlay = true, max_labels_count = 500)\n' % title
                + frag + self._labels_frag(labels, scheme))
        open(path, "w").write(body)
        return len(labels), total

    @staticmethod
    def bucket_spans(ts_iter, bucket_ms):
        """Floor 5s timestamps onto a chart-TF bucket, deduped and sorted. bgcolor paints per CHART bar, so a
        span emitted at 5s resolution only lights the bars the chart actually has. bucket_ms = the chart TF in
        ms (240000 = TF4). Lifted here because every caller had its own copy (Joe 0802)."""
        b = int(bucket_ms)
        return sorted({(int(m) // b) * b for m in ts_iter})

    def emit_direction_overlay(self, marks, streams, path, title, mechanics=(), bucket_ms=None,
                               opacity=60, scheme='redgreen'):
        """THE TEMPLATE (Joe 0802: "bake the template into the jig").

        Two ORTHOGONAL colour channels, so neither reading is ambiguous:
          LABELS  green + label_up = LONG, red + label_down = SHORT.  Direction owns green/red ALONE.
                  Joe 0801: "a long signal firing half down a leg will look the same as a short signal"
                  unless direction is encoded, so it gets its own channel and nothing else uses it.
          BGCOLOR the per-row CALL, painted over a span. Use blue/yellow, never green/red.

        marks   = [{ts:int-ms, y:float, long:bool, lines:[str, ...]}]
                  `lines` are joined with a real newline; _labels_frag escapes it for Pine. One fact per
                  line, and put an unambiguous timestamp on one of them — a bucketed label cannot be
                  matched back to its row from the chart alone (Joe 0802).
        streams = [{'name':str, 'ts':[int-ms...], 'color':'color.blue', 'meaning':str}]
                  Order is PRIORITY: later paints over earlier. 'meaning' is required — it becomes the
                  legend. `ts` may be raw 5s stamps; pass bucket_ms and they are floored for you.
        mechanics = [str, ...] free lines appended under the legend: line specs, knobs, window.

        The header is a LEGEND-FIRST comment block with counts GENERATED from marks/streams, so it cannot
        drift from the data it describes (Joe 0802: the colour definitions were unreadable when they sat
        230 chars into a single 700-char line).

        -> (n_labels, n_painted_bars)"""
        st = [dict(s) for s in streams]
        for s in st:
            if bucket_ms:
                s['ts'] = self.bucket_spans(s['ts'], bucket_ms)
            s.setdefault('meaning', s['name'])
        nl = sum(1 for m in marks if m.get('long'))
        legend = ['%s  —  LEGEND' % title, '']
        legend.append('  BGCOLOR = the per-row call, painted over the span')
        for s in st:
            legend.append('    %-8s %-46s (%d bars)'
                          % (s['color'].replace('color.', '').upper(), s['meaning'], len(s['ts'])))
        if bucket_ms:
            legend.append('    span bucket %d ms = %g s — set this to the chart TF you read it on'
                          % (int(bucket_ms), int(bucket_ms) / 1000.0))
        legend += ['', '  LABELS = DIRECTION, and nothing else uses green/red',
                   '    GREEN + arrow up    LONG    %d rows' % nl,
                   '    RED   + arrow down  SHORT   %d rows' % (len(marks) - nl)]
        # The first row's ACTUAL text, marked as a sample. Not a format string — a format string drifts
        # from the data, a sample cannot (Joe 0802: the legend must describe what is really there).
        for k, ln in enumerate(marks[0]['lines'] if marks else []):
            legend.append('    text line %d, sample:  %s' % (k + 1, ln))
        if mechanics:
            legend += [''] + list(mechanics)

        labels = [dict(ts=int(m['ts']), y=float(m['y']), text='\n'.join(m['lines']),
                       green=bool(m.get('long')), up=bool(m.get('long'))) for m in marks]
        return self.emit_overlay(labels, st, path, title, opacity=opacity, scheme=scheme,
                                 notes='\n'.join(legend))


RED_BG_TRANSP = 47      # bgcolor red transparency (0 solid .. 100 invisible) - Joe 0731, red was hiding
                        # the bearish candle bodies. Applies to color.red bgcolor streams only.


def _latch_with_reset(q, drop):
    """[RPL·0729] Causal set/reset latch. ON from the bar `q` fires, OFF from the bar `drop` fires.
    Vectorised as "most recent set is at or after the most recent reset" — no Python loop, no lookahead.
    A bar that is both set and reset resolves to SET (>=), which cannot occur in practice: the reset is
    all-lines-IB or opposite-OOB, and the qualify requires same-side m/M OOB."""
    idx = np.arange(len(q))
    last_q = np.maximum.accumulate(np.where(q, idx, -1))
    last_d = np.maximum.accumulate(np.where(drop, idx, -1))
    return (last_q >= 0) & (last_q >= last_d)


class Jig:
    """Pinned-window test bench. Build once, reuse across a script. `overrides` = BiasWindow line_overrides for
    non-DB lines (e.g. {'s10r': (600, ('k',6,6,5,'hl2'), 'emerging')})."""
    def __init__(self, end_ms, hours=48, warmup=24, overrides=None, dev=None, bias=None):
        self._owns_dev = dev is None
        self.dev = dev or DatabaseManager(**get_db_config())
        if self._owns_dev:
            self.dev.connect()
        self.cfg = lr_config(self.dev)
        self.hi, self.lo = self.cfg.hi, self.cfg.lo
        self.end_ms = int(end_ms)
        bcfg = bias if bias is not None else bm.BiasConfig(**BASE_BIAS)
        self.W = bm.BiasWindow(self.dev, self.end_ms, lookback=hours + warmup, warmup=warmup,
                               cfg=bcfg, line_overrides=overrides or {})
        self.ts = np.asarray(self.W.ts); self.px = np.asarray(self.W.px, float); self.n = len(self.ts)
        self.hours = hours
        self.causal = _Causal(self)
        self.score = _Score(self)

    def close(self):
        if self._owns_dev:
            self.dev.disconnect()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()


def handoff(R, landings, live_log, fence, xwob, near, i0=0, i1=None, stall=None):
    """[PRODUCER · Joe 0810] Defer a momo_landed to a higher timeframe before delegating.

    Joe's spec, verbatim:
        --if ANY momentum tagged line exits the fence, we call it a handoff and delegate it to the
          finishers
        ---there is a huge problem with this - creating a race condition blocks the momentum of
           higher lines. you can see it in the large bull leg, between 08-04 16:50 and 19:50
        ---0804 17:46:15
        ----fired too early, the bull leg is still developing
        ----if ws26r's signals here, then the spec is ignoring a larger momentum TF (eg 33)
        ----if ws26r submitted to ws33r and allowed itself to be gated by ws33r, then the
            "delegation to finishers" would be gated until ws33r crosses out of the fence
        -----process: ws26r crosses out of the fence -> test for a higher TF -> IF a higher TF is
             same-side xwob:{4} "near {fence-2:knob}" the fence THEN wait for that TF to exit the
             fence -> walk forward, loop until there are no waiting HTFs -> delegate to the finishers

    ARGS
        landings  the momo_landed events, in bar order — each {'bar','cross','tf','dr','marker'}
        live_log  {bar: {tf: dr}} the live tag set per bar, from momo_landed
        near      the knob. 2 -> "near the fence" = [78,80) for dr +1, (20,22] for dr -1
        xwob      consecutive 5 s bars the HTF must hold in the near band to count as WAITING

    MY READINGS, not stated by Joe:
        WHICH HTFs   live tags with TF strictly greater than the deferring line's, same `dr`.
        NEAR         INSIDE the fence and within `near` of its edge. A line already outside has
                     exited, so it cannot be waited for.
        WAITING      `xwob` CONSECUTIVE bars in the near band, ending at the bar under test.
        EXIT         the same exit momo_landed uses — the line's own landing. Not re-derived.
        RELEASE      re-evaluated every bar. A waiting HTF that leaves the near band WITHOUT
                     exiting stops blocking. Joe's "walk forward, loop until there are no waiting
                     HTFs" implies the set is re-read as the walk proceeds; without a release a
                     retreating HTF would block the handoff for ever.
        CREDIT       the handoff carries BOTH the line that first crossed and the line whose exit
                     released it.

    THE STALL, Joe 0810: "the stall event will only be acknowledged by the dominant ws{tf}r line,
    ie the line that has been identified to delay and carry the signal further."
        `stall(tf, dr, bar) -> bool`, supplied by the caller (SRP, same as counter_curl). It is
        asked ONLY about the currently awaited HTF — the dominant line — and only while a wait is
        pending. A stall on any other line is not acknowledged.
        MY READING: an acknowledged stall RELEASES the wait and delegates. Joe did not say what the
        acknowledgement does; the dominant line having stopped advancing is the signal that it will
        not carry the move further, which is the condition the wait exists to detect.

    -> (handoffs, blocked) — handoffs are the delegations; blocked are the landings that were
       suppressed, each with the HTFs it deferred to."""
    lo_f, hi_f = float(fence), 100.0 - float(fence)
    lo_n, hi_n = lo_f + float(near), hi_f - float(near)
    n = len(next(iter(R.values())))
    i1 = n if i1 is None else int(i1)
    xw = max(1, int(xwob))

    def in_near(tf, dr, i):
        v = R[tf][i]
        if not np.isfinite(v):
            return False
        return (hi_n <= v < hi_f) if dr > 0 else (lo_f < v <= lo_n)

    def waiting(tf, dr, i):
        """xwob consecutive bars in the near band, ending at i."""
        return all(in_near(tf, dr, k) for k in range(max(0, i - xw + 1), i + 1))

    land_at = {}
    for e in landings:
        land_at.setdefault(int(e['bar']), []).append(e)

    handoffs, blocked = [], []
    pending = {}                    # dr -> {'origin': event, 'chain': [tf...], 'awaiting': tf}
    for i in range(i0, i1):
        lv = live_log.get(i, {})
        for e in land_at.get(i, []):
            dr = int(e['dr'])
            p = pending.get(dr)
            if p is not None and int(e['tf']) != p['awaiting']:
                continue            # a lower/other line landing while we wait — still suppressed
            htfs = [tf for tf, d in lv.items()
                    if int(d) == dr and tf > int(e['tf']) and waiting(tf, dr, i)]
            if htfs:
                top = max(htfs)
                if p is None:
                    p = {'origin': dict(e), 'chain': [], 'awaiting': None}
                p['chain'].append({'bar': i, 'tf': int(e['tf']), 'defer_to': top,
                                   'htfs': sorted(htfs)})
                p['awaiting'] = top
                pending[dr] = p
                blocked.append({'bar': i, 'tf': int(e['tf']), 'dr': dr, 'defer_to': top,
                                'htfs': sorted(htfs)})
                continue
            # nothing higher is waiting -> delegate
            o = p['origin'] if p is not None else dict(e)
            handoffs.append({'bar': i, 'tf': int(e['tf']), 'dr': dr,
                             'origin_bar': int(o['bar']), 'origin_tf': int(o['tf']),
                             'marker': int(e['marker']), 'val': float(R[e['tf']][i]),
                             'chain': (p['chain'] if p is not None else []),
                             'deferred_s': (int(i) - int(o['bar'])) * 5})
            pending.pop(dr, None)
        # RELEASE 1 — the STALL on the dominant line. Joe 0810.
        for dr in list(pending):
            p = pending[dr]
            tf = p['awaiting']
            if stall is not None and tf in lv and stall(tf, dr, i):
                o = p['origin']
                handoffs.append({'bar': i, 'tf': tf, 'dr': dr,
                                 'origin_bar': int(o['bar']), 'origin_tf': int(o['tf']),
                                 'marker': int(o['marker']), 'val': float(R[tf][i]),
                                 'chain': p['chain'], 'deferred_s': (int(i) - int(o['bar'])) * 5,
                                 'released': 'stall'})
                pending.pop(dr)
        # RELEASE 2: the awaited HTF is no longer waiting and has not landed -> stop blocking
        for dr in list(pending):
            p = pending[dr]
            tf = p['awaiting']
            if tf not in lv or not (in_near(tf, dr, i) or
                                    ((R[tf][i] > hi_f) if dr > 0 else (R[tf][i] < lo_f))):
                o = p['origin']
                handoffs.append({'bar': i, 'tf': tf, 'dr': dr,
                                 'origin_bar': int(o['bar']), 'origin_tf': int(o['tf']),
                                 'marker': int(o['marker']), 'val': float(R[tf][i]),
                                 'chain': p['chain'], 'deferred_s': (int(i) - int(o['bar'])) * 5,
                                 'released': 'htf_left_the_near_band'})
                pending.pop(dr)
    return handoffs, blocked


# ws_fin_9of12 knobs. REVERTED to baseline 0812. Joe: "hitting the pivots is more important than
# noise - I can always build another mechanism to reduce the noise, but I can't create a mechanism
# that increases pivot hits" and "15 minutes is not 'a few minutes' - it's ~0.4% of lost profit
# potential".
#
# The noise-reduced setting (handicap 3, vote_hold 12, vote_sticky 12) was ranked on a +/-15 min
# pivot-coverage window that I chose. Re-scored at tighter tolerances it loses pivots faster than
# baseline does:
#                    IS coverage                      OOS coverage
#   tol   +/-15   +/-5   +/-2  decay      +/-15   +/-5   +/-2  decay     fires IS / OOS
#   held  107/109 98    79     -26%       435/448 384    327   -25%      1,448 / 2,888
#   base  108/109 101   95     -12%       440/448 398    371   -16%      3,182 / 7,001
# At +/-2 the held setting gives up 16 IS and 44 OOS pivots. vote_hold / vote_sticky DISPLACE fires
# away from the pivot bar rather than only removing fires that were never near one.
#
# The hold knobs remain in the producer, defaulted OFF. Noise reduction goes in a separate mechanic.
WSF_N            = 9    # of 12
WSF_HANDICAP     = 0    # gcws b/m/Mage vote at hi / lo, the same 85 / 15 as the other six lines.
                        # WAS 7 (78 / 22) until 0813, then 0 on Joe 0813 "make it 15/85".
                        # Briefly 9 on 0814 to reach Joe's 08:59:30 target, then back to 0 — that
                        # was a shotgun. Joe 0814: "did you apply the change to g30, or did you use
                        # a shotgun?" It loosened six lines to fix two, and gcws30b, the line it was
                        # aimed at, was already voting at 91.08 on the bar that mattered.
WSF_VOTE_HOLD    = 0    # OFF
WSF_VOTE_STICKY  = 0    # OFF


def _sticky(mask, grace):
    """Hold a True across a gap of FEWER than `grace` bars. The per-line analogue of Joe's step-8
    oob dwell carrying across a sub-min_ib_dwell poke.

    CAUSAL. Walks forward carrying an off-counter: while a line that HAS been voting has been off
    for fewer than `grace` bars, the vote is held. Nothing is written backwards. An earlier draft
    filled the gap retrospectively once it ended — that reads the future and is not usable here."""
    m = np.asarray(mask, bool)
    out = np.zeros(len(m), bool)
    seen = False; off = 0
    for i in range(len(m)):
        if m[i]:
            seen = True; off = 0; out[i] = True
        elif seen:
            off += 1
            out[i] = off < int(grace)
            if not out[i]:
                seen = False
    return out


def _runlen(mask):
    """Consecutive-True count ending at each bar. Local copy — jig does not import ws_strat."""
    m = np.asarray(mask, bool).astype(np.int64)
    out = np.zeros(len(m), np.int64); c = 0
    for i in range(len(m)):
        c = c + 1 if m[i] else 0
        out[i] = c
    return out


WSF_LINE_HANDICAP = {'ws1b': 1}
# KNOB, per line. {line_name: points}. A line with a handicap votes at hi-points / lo+points instead
# of at the full boundary. Overrides WSF_HANDICAP for that line. Empty = every line at 85 / 15.
# Joe 0814: ws1b 1 point, so it votes at 84 / 16. His read named it — "my eyes see that gcws15b and
# ws1b fall short of their qualifying tartgets" — and it is the one line WSF_HANDICAP cannot reach,
# since that knob only covers the six gcws b/m/Mage lines. At 08-04 08:59:55 ws1b reads 84.83, so
# one point is the whole gap. Paired with WSF_WS1_XWOB 1 below: together they cost +16 signals on
# 08-04, where the six-line WSF_HANDICAP 9 cost +54 for the same target bar.

WSF_WS1_XWOB  = 1    # KNOB. 5 s bars. Consecutive bars ws1Mage / ws1b must hold past their
                     # boundary before they may vote. 1 = no hold, a single bar votes.
                     # WAS 4 (20 s) on Joe 0813 "use a xwob 4 on ws1Mage and ws1b". Joe 0814 took
                     # it to 1 to reach the 08-04 08:59:30 target: ws1Mage crosses to 87.18 at
                     # 08:59:55 with only one bar of the four, so its vote was held and the count
                     # stopped at 8 of 12. Joe's caveat, noted by him: this is the filter that
                     # rejected one-bar spikes, and 08:59:55 IS a one-bar spike on both lines.
WSF_LINE_XWOB = {'ws1Mage': WSF_WS1_XWOB, 'ws1b': WSF_WS1_XWOB}
# Joe 0813: "add this to the 9of12 mechanic: use a xwob 4 on ws1Mage and ws1b".
# These two lines may vote only after 4 CONSECUTIVE bars past their boundary (20 s at the 5 s grid).
# The other ten lines are unchanged. Distinct from `vote_hold`, which applies the same hold to all
# twelve. Found by Joe on the 08-04 02:24:35 event: at the counting bar 02:24:15 ws1Mage read 86.57
# having been 19.58 one bar earlier, and it held above 85 for 3 bars (15 s) before falling back; ws1b
# peaked at 108.42 for 2 bars AFTER the count. Nine votes rested on a 15-second spike.

WSF_REQUIRE = ('gcws30b',)   # Joe 0813: "for this to work reliably, 9of12 must always carry a g30b
                             # vote". A bar with n voters that excludes gcws30b is NOT a
                             # qualification. This is also what makes the dual latch self-ordering:
                             # gcws30b votes only while OOB, and unlatch#2 is its move to IB, so the
                             # two can never share a bar.


def wsf_qualify(W, hi, lo, n=WSF_N, handicap=WSF_HANDICAP, vote_hold=WSF_VOTE_HOLD,
                vote_sticky=WSF_VOTE_STICKY, require=WSF_REQUIRE, line_xwob=WSF_LINE_XWOB,
                line_handicap=WSF_LINE_HANDICAP):
    """[PRODUCER · Joe 0812] STAGE 1 of ws_fin_9of12 — "9 of 12 lines qualify".

    THIS IS NOT THE SIGNAL. Joe 0813: "9of12 event will fire on these chronological conditions:
    1st) 9 of 12 lines qualify, 2nd) g30 creates a marker signal -- these are not separate events -
    these 2 requirements combine to create the ws_fin_9of12 signal". The signal is ws_fin_9of12()
    below; this function only produces the qualification it latches on.

    Named for Joe's word, "qualify". Was called ws_fin_9of12 until 0813, when the g30 condition was
    added and the name moved to the combined producer.

    Joe's spec:
        we'll build a ws15301_9(or10)of12 event on the jig. when the event fires, the trade signal
        will print (if domTF state is FREE)
        -use these 12 lines: gcws[15,30][b,m,Mage,r] and ws1[b,m,Mage,r]
        -the gcws lines are allowed a handicap:
        --gcws[15,30][b,m,Mage] qualify for 9/10of12 if they have crossed (oob - {knob:7}) ie 22 and 78
        -r-lookback will be disabled in this mechanism

    ONE LINE, ONE VOTE (Joe D1=a). Each of the 12 lines contributes a single per-side bool: is it
    OOB on that side at THIS bar. Not the 3-conditions-per-bundle shape of s_qualify_parts.

    THE HANDICAP (Joe D2=a) applies to SIX lines only — gcws15b/m/Mage and gcws30b/m/Mage — which
    vote at hi-handicap / lo+handicap = 78 / 22. The two gcws r lines and all four ws1 lines vote at
    the full boundary, 85 / 15. Joe named the six explicitly; the r lines are not in that list.

    NO r-LOOKBACK (Joe D3=a). s_qualify_parts offers rlb_hi/lo (r OOB within r_lb back) and r_hi/lo
    (r OOB at the bar). This producer uses the at-the-bar test only — there is no lookback path.

    NO Mrev. The existing N-of-9 counts a Mage reversal; this set does not. Joe 0812: "its not
    needed for this event - we're using gcws15's granularity in place of Mrev".

    PER SIDE (Joe D4=a). hi and lo are counted separately; a mixed-side set is not a confluence.
    hn and ln are independent sums and no line can vote both ways (v >= 78 and v <= 22 cannot both
    hold), so hn + ln <= 12 and a single bar can never fire both sides.

    THIS PRODUCER EMITS NO TRADE DIRECTION. hi_fire / lo_fire are boundary counts: nine or more of
    the twelve lines past the high boundary, or past the low one. Joe 0812: "its 100% obvious that a
    LONG trade will launch from a lo oob, and inverse for SHORT. if you want to rely on +1 and -1,
    you'll find it in `dr`."
        lo_fire (9+ lines OOB-LOW)  -> LONG
        hi_fire (9+ lines OOB-HIGH) -> SHORT
    Do not label hi_fire as +1 here. The signed direction is `dr`, which already exists on the
    markers and tags; this producer is a position count and nothing else.
    RISING EDGE (Joe D6=a). The event is the bar the count first reaches n, not every bar it holds.

    THE VOTE HOLD (Joe 0812: "I want to make sure that the IB dwell and XWOB settings are honoured
    so that we can rely on ws1Mage oob and ws1b fence to contain the signals"). XWOB and
    MIN_IB_DWELL cannot reach this producer — they gate a gcws30b CROSSING, and there is no crossing
    here. Measured 08-04 00:00-12:00 at handicap 0 / 88-12 / N9: 58.5% of fires had ws1Mage past its
    threshold for less than MIN_IB_DWELL and 28% for less than XWOB; the 25th percentile was ONE bar.
    So the hold is applied to the VOTE itself:
        vote_hold    a line votes only after `vote_hold` CONSECUTIVE bars past its threshold
        vote_sticky  once voting, a line keeps its vote across a gap shorter than `vote_sticky`
                     bars — the per-line analogue of Joe's step-8 oob dwell rule
    Both default to 0 = off, which reproduces the raw position test exactly.

    ARGS
        W          the value_mode-honoured line reader (jig W)
        hi/lo      the boundaries, 85 / 15
        n          the threshold. Joe: 9 or 10 of 12
        handicap   KNOB 7. gcws b/m/Mage vote at hi-7 / lo+7
        vote_hold  KNOB. consecutive bars past the threshold before the line may vote
        vote_sticky KNOB. bars of grace a voting line keeps across a return

    -> dict:
        hi_n / lo_n      per-bar vote count, 0..12
        hi_fire / lo_fire  per-bar bool, the RISING EDGE of count >= n
        votes            {line_name: (hi_bool_array, lo_bool_array)} for the audit trail
    Causal: every read is at its own bar."""
    HANDI = [f'{g}{s}' for g in ('gcws15', 'gcws30') for s in ('b', 'm', 'Mage')]
    LINES = ([f'{g}{s}' for g in ('gcws15', 'gcws30') for s in ('b', 'm', 'Mage', 'r')]
             + [f'ws1{s}' for s in ('b', 'm', 'Mage', 'r')])
    votes, H, L = {}, [], []
    for nm in LINES:
        v = np.asarray(W.line(nm), float)
        hp = (line_handicap or {}).get(nm)
        if hp is None:
            h_, l_ = (hi - handicap, lo + handicap) if nm in HANDI else (hi, lo)
        else:
            h_, l_ = hi - hp, lo + hp
        vh, vl = (v >= h_), (v <= l_)
        if int(vote_sticky) > 0:
            vh, vl = _sticky(vh, int(vote_sticky)), _sticky(vl, int(vote_sticky))
        if int(vote_hold) > 0:
            vh = _runlen(vh) >= int(vote_hold)
            vl = _runlen(vl) >= int(vote_hold)
        xw = int((line_xwob or {}).get(nm, 0))      # Joe 0813 — per-line hold, ws1Mage / ws1b
        if xw > 0:
            vh = _runlen(vh) >= xw
            vl = _runlen(vl) >= xw
        votes[nm] = (vh, vl); H.append(vh); L.append(vl)
    hn = np.sum(H, axis=0).astype(np.int16)
    ln = np.sum(L, axis=0).astype(np.int16)
    okh, okl = hn >= int(n), ln >= int(n)
    for nm in (require or ()):                     # Joe 0813 — the mandatory voters
        okh &= votes[nm][0]
        okl &= votes[nm][1]
    return {'hi_n': hn, 'lo_n': ln,
            'hi_fire': okh & ~np.r_[False, okh[:-1]],
            'lo_fire': okl & ~np.r_[False, okl[:-1]],
            'votes': votes, 'lines': LINES, 'handicapped': HANDI,
            'required': list(require or ())}


def ws_fin_9of12(W, hi, lo, g30, n=WSF_N, handicap=WSF_HANDICAP, vote_hold=WSF_VOTE_HOLD,
                 vote_sticky=WSF_VOTE_STICKY, require=WSF_REQUIRE, line_xwob=WSF_LINE_XWOB,
                 line_handicap=WSF_LINE_HANDICAP, i0=0, i1=None):
    """[PRODUCER · Joe 0813] ws_fin_9of12 — THE SIGNAL. A DUAL LATCH.

    Joe 0813, verbatim:
        treat the 2 signals as a dual latch.
        unlatch#1: 9 of 12 lines
        unlatch#2: same-side g30b crossing to ib

        -unless there is a g30 marker signal, ws_fin_9of12 cannot fire
        -for this to work reliably, 9of12 must always carry a g30b vote
        -these are not separate events - these 2 requirements combine to create the ws_fin_9of12
         signal

    THE g30 MARKER SIGNAL. Joe 0813, verbatim: "confirmed b crossing from oob to ib, with an xwob".
    XWOB only. NO OOBW dwell filter, NO ws1 gate. In ws_strat terms that is candidates() output.
    Joe 0813 on its role: "for right now, it provides a clock for g15 and g30 activities. it is not
    a replacement for ws1 or any other mech".

    SAME SIDE. unlatch#2 must match unlatch#1's side. A hi-side qualification is released only by a
    crossing whose dwell was on the hi side.

    THE ORDER IS SELF-ENFORCING, and that is what `require` buys. gcws30b can only vote while it is
    OOB; unlatch#2 is its move to IB. The two can never be true on one bar, so unlatch#1 always
    precedes unlatch#2 without an explicit ordering rule.

    THE EVENT TIMESTAMP is the crossing's confirmation bar — the first bar both latches are open.

    ARGS
        W        the value_mode-honoured line reader (jig W)
        hi/lo    the boundaries, 85 / 15
        g30      sequence of (bar, side) for the g30 marker signals. side +1 = the dwell before the
                 crossing was on the hi side, -1 lo
        n / handicap / vote_hold / vote_sticky / require   passed to wsf_qualify
        i0 / i1  the window, as bar indices. i1 inclusive; None = to the end

    -> (events, q). events, each:
        bar        the g30 marker signal bar. THE EVENT TIMESTAMP
        qual_bar   the qualification bar that opened unlatch#1
        wait       bars from qual_bar to bar
        side       +1 / -1, shared by both latches
        hi_n/lo_n  the counts AT qual_bar
        absorbed   qualifications replaced before this one fired

    OPEN, MINE, NOT STATED BY JOE
      - a further same-side qualification before the crossing REPLACES the armed one; `absorbed`
        counts how many folded in. The payload is the state closest to the firing bar.
      - NO EXPIRY. An armed latch waits indefinitely.
      - an opposite-side qualification also replaces the armed one, since only one latch is held.
    Causal: every read is at its own bar; nothing after `bar` is consulted."""
    q = wsf_qualify(W, hi, lo, n=n, handicap=handicap, vote_hold=vote_hold,
                    vote_sticky=vote_sticky, require=require, line_xwob=line_xwob,
                    line_handicap=line_handicap)
    hf, lf = q['hi_fire'], q['lo_fire']
    i1 = (len(hf) - 1) if i1 is None else int(i1)
    gmap = {int(b): int(s) for b, s in g30}
    out, armed, absorbed = [], None, 0
    for i in range(int(i0), int(i1) + 1):
        if hf[i] or lf[i]:                              # unlatch#1
            if armed is not None:
                absorbed += 1
            armed = {'qual_bar': i, 'side': 1 if hf[i] else -1,
                     'hi_n': int(q['hi_n'][i]), 'lo_n': int(q['lo_n'][i])}
        if armed is not None and gmap.get(i) == armed['side']:   # unlatch#2, SAME SIDE
            out.append({'bar': i, 'wait': i - armed['qual_bar'], 'absorbed': absorbed, **armed})
            armed, absorbed = None, 0
    return out, q

# ─────────────────────────────────────────────────────────────────────────────────────────────────
# domTF HANDOVER — the bar the domTF turn ends and the finishers take over.
# ─────────────────────────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────────────────────────
# ws-FINISHER — the weak-mage-tf. Joe 0817. NOTHING FROM domTF BELONGS HERE.
# ─────────────────────────────────────────────────────────────────────────────────────────────────

# THE SINGLE TRUTH FOR weak-mage-tf. Joe 0831: "move it to the jig so that we have a single
# truth". Every knob and both producers live here. build_wsf_bar_tf.py and build_ws_finisher.py
# import from this block and declare nothing of their own.
WMT_TF_LO      = 2                   # KNOB. Joe 0826 "weak-mage-tf scan is now TF2 to TF12".
WMT_TF_HI      = 12                  #   WAS TF1 to TF8, Joe 0817 "confirmed: TF1 to TF8". The 0826
#                                      ruling had reached build_wsf_bar_tf.py and had NOT reached
#                                      this file until the 0831 move. ws_fin_weak_mage's 121 rows
#                                      were built at 1..8 and are kept alongside on Joe 0831 "W1,
#                                      keep alongside" - the range is now in that table's unique
#                                      key so a rebuild at 2..12 cannot overwrite them.
WMT_TFS        = list(range(WMT_TF_LO, WMT_TF_HI + 1))   # derived. Never set independently.
WMT_LOOKBACK_S = 120                 # KNOB, seconds. Joe 0817 "add a lookback tolerance to capture
#                                      Mage values that were recently oob. knob:120sec". This is
#                                      the weak-mage tolerance and NOTHING ELSE. three-mage's dr
#                                      lookback is DR_LOOKBACK_S 180 s in build_wsf_walk_events.py,
#                                      Joe 0823 "restrict the lookback to 3 minutes" - a different
#                                      knob at a different value on a different mechanic.
WMT_SAME_SIDE  = True                # FIXED at True, Joe 0831 "W3, fixed as True". Was a knob on
#                                      Joe 0817 "unsure. create a knob for it. default to
#                                      same-side". MY DEFINITION, stated 0817: a line's
#                                      out-of-bounds readings only count on the side dr points at -
#                                      the high boundary when dr is positive, the low boundary when
#                                      dr is negative. The per-bar producer still accepts the
#                                      argument; no caller passes anything but the default.


def weak_mage_tf(mage, hi, lo, bar, lookback_bars, dr, tfs=WMT_TFS, same_side=WMT_SAME_SIDE):
    """[PRODUCER · Joe 0817] The first Mage that has NOT been out of bounds recently.

    Joe 0817, the preamble:
        "Mage's purpose is to travel from source oob to target oob, in an endless loop, matching
        the ebb and flow of pxs" / "when Mage is oob, it's strength will wane. this waning is the
        moment of weakness" / "to find weakness, the code will scan the Mage values, upwards from
        TF1 to TF8, to find the first mage that is not OOB" / "the first Mage that prints an IB
        value, is the weak-mage-tf".

    THE LOOKBACK. A line that was out of bounds at any bar inside the window still counts as out.
    Joe 0817 settled the rule against four bars he read himself: 10:53:35 -> TF8, 11:34:00 -> TF2,
    08:02:50 -> TF4, 04:49:15 -> None.

    NO WEAK-MAGE-TF IS A RESULT, NOT A FAILURE. When every line from TF1 to TF8 was out of bounds
    inside the window the answer is None. Joe 0817: "no signals are created, but a stub needs to
    capture and report this when it happens", then "I agree with your 04:49 view - weak-mage-tf =
    None" and rule C: "if weak-mage-tf == None and domTF state is FREE, fire a trade signal".

        mage           {tf: array} the Mage line per timeframe, one value per grid bar
        hi / lo        the boundaries, 85 and 15
        bar            the bar to answer at. The ws_fin_9of12 signal bar
        lookback_bars  bars in the window, the bar itself included
        dr             the bias. Only read when same_side is True. Joe 0817: "dr gives us all
                       that we need for postitioning and trade direction" — this producer holds no
                       LONG/SHORT logic of its own, it reads the sign and nothing else
        tfs            the timeframes to scan, in order

    -> (weak_tf, detail). weak_tf is a timeframe or None. detail is {tf: (value_now, out_now,
       bars_since_last_out or None, the side of that last reading or None)}.
    """
    a = max(0, int(bar) - int(lookback_bars) + 1)
    detail, weak = {}, None
    for tf in tfs:
        y = np.asarray(mage[tf], float)[a:int(bar) + 1]
        if len(y) == 0 or not np.isfinite(y).all():
            detail[tf] = (float('nan'), False, None, None)
            continue
        up, dn = y >= hi, y <= lo
        if same_side:
            out = up if dr > 0 else dn
        else:
            out = up | dn
        v = float(y[-1])
        k = np.flatnonzero(out)
        if len(k):
            j = int(k[-1])
            detail[tf] = (v, bool(out[-1]), (len(y) - 1) - j, 'high' if up[j] else 'low')
        else:
            detail[tf] = (v, False, None, None)
            if weak is None:
                weak = tf
    return weak, detail


def weak_mage_tf_series(mage, hi, lo, dr, grid_s, tfs=None, lookback_s=WMT_LOOKBACK_S,
                        tf_lo=WMT_TF_LO, tf_hi=WMT_TF_HI):
    """[PRODUCER · Joe 0817, vectorised 0831] weak_mage_tf answered at EVERY bar at once.

    Same three steps as the per-bar weak_mage_tf above, and the same rulings behind them:
      1. out of bounds   ws{TF}Mage >= hi when dr is positive, <= lo when dr is negative. Joe 0817,
                         "with it ON a line's out-of-bounds readings only count on the side dr
                         points at". Same-side is FIXED here, Joe 0831 "W3, fixed as True".
      2. the tolerance   a line out of bounds at any bar inside the last `lookback_s` seconds still
                         counts as out. Joe 0817 "add a lookback tolerance to capture Mage values
                         that were recently oob. knob:120sec".
      3. the scan        the LOWEST timeframe in tf_lo..tf_hi the tolerance does not count as out.
                         Joe 0826 "weak-mage-tf scan is now TF2 to TF12".

    NO WEAK-MAGE-TF IS A RESULT, NOT A FAILURE - Joe 0817. It arrives here as 0, because the return
    is an integer array. The caller turns 0 into None on the way to the database.

        mage        {tf: array} the Mage line per timeframe, one value per grid bar, FULL LENGTH.
                    The arrays must start at the beginning of the cache, not at the window, or the
                    seconds-since-last-out counter has no history to count from.
        hi / lo     the boundaries, 85 and 15
        dr          the bias. Only its sign is read; this producer holds no LONG/SHORT logic
        grid_s      seconds per bar, 5
        tfs         the timeframes to compute rows for. Defaults to every key in `mage`. This can
                    be WIDER than tf_lo..tf_hi - wsf_bar_tf banks a row per timeframe whether or
                    not that timeframe takes part in the scan
        tf_lo/tf_hi the scan range, inclusive

    -> (oob, ago, tol, wmt), all full length.
       oob  {tf: bool array}  out of bounds at this bar
       ago  {tf: int array}   seconds since last out of bounds, -1 = never on this side yet
       tol  {tf: bool array}  counted as out under the tolerance
       wmt  int16 array       the weak-mage-tf, 0 meaning none
    """
    if tfs is None:
        tfs = sorted(mage)
    oob, ago, tol = {}, {}, {}
    n = None
    for tf in tfs:
        m = np.asarray(mage[tf], float)
        n = len(m)
        o = (m >= hi) if dr > 0 else (m <= lo)
        idx = np.arange(n)
        lasto = np.maximum.accumulate(np.where(o, idx, -1))
        oob[tf] = o
        ago[tf] = np.where(lasto < 0, -1, (idx - lasto) * grid_s)
        tol[tf] = (ago[tf] >= 0) & (ago[tf] <= lookback_s)
    wmt = np.zeros(n, np.int16)
    # walk the range DOWNWARD so the last write wins and the answer is the LOWEST timeframe the
    # tolerance does not count as out
    for tf in [t for t in tfs if tf_lo <= t <= tf_hi][::-1]:
        wmt = np.where(~tol[tf], tf, wmt)
    return oob, ago, tol, wmt


MOMO_CHECK_TFS = list(range(2, 11))
# THE LINES THE MOMENTUM CHECK COVERS. ws{TF}r, TF in minutes, 2 to 10.
#
# Joe 0816: "permanently include ws[2,3,4,5]r in the momo check". ws2r..ws6r resolve to
# k(rsi 5, stc 8, k_len 7, close) on emerging, which is exactly build_momo_landed.R_SPEC, so
# extending the range down to 2 uses the same line the check already uses at 6 and above.
#
# Joe 0816: "reduce coverage: ws2 to w10". WAS 2..27, and 6..27 before that.
#
# THIS IS NOT THE domTF RANGE. build_ws_fin.DOMTF_TFS stays 13..27 on Joe 0813 "make the domTF
# range 13 to 27". The two are separate mechanics and this constant does not touch the handover.


def stall_on_samples(y, dr, n):
    """[PRODUCER · Joe 0810, confirmed 0814] A STALL: the line has stopped making new extremes.

    Joe 0814: "my understand is STALL_N 3 means 3 samples that have not exceeded the maxim".

        y   the line's momentum SAMPLE points, oldest first, ending at the bar being tested.
            The caller builds the lattice — this producer never touches momo's constants.
        dr  the move's direction. +1 tests for no new HIGH, -1 for no new LOW.
        n   STALL_N. Consecutive samples with no new extreme.

    -> (stalled, samples_since_the_last_new_extreme). Not stalled if no sample ever made one.

    ITS DURATION IS NOT FIXED. n counts SAMPLES, and since 0814 the gap between samples scales with
    the line (2.58 min on ws13r to 5.42 min on ws27r — see M10), so n=3 is 7.7 min on the shortest
    line and 16.3 on the longest. Joe 0814: "accept it as built. if needed, we can adjust after we
    see the first results."

    NOT RESTRICTED TO A DOMINANT LINE. Joe 0810's "the stall event will only be acknowledged by the
    dominant ws{tf}r line" belongs to the handoff producer, not here. Joe 0814: "that is a
    restriction placed in a different machine. for domTF, we will wait for stall or cross from the
    line that we derive."
    """
    y = np.asarray(y, float)
    if y.ndim != 1 or len(y) < 2 or not np.isfinite(y).all():
        return False, None
    st, since = _stall_rows(y[None, :], dr, n)
    return bool(st[0]), (None if since[0] < 0 else int(since[0]))


def _stall_rows(S, dr, n):
    """The stall rule on a stack of lattices. S is (rows, samples), oldest sample first.
    -> (stalled, since). since is -1 only where the row is unusable (a NaN in the window).
    ONE implementation of the rule: stall_on_samples and stall_mask both land here.

    THE FIRST SAMPLE IS THE EXTREME WHEN NOTHING BEATS IT. Fixed 0815. `fresh` marks a sample that
    is beyond everything before it, so sample 1 can never be marked — it is the baseline the others
    are measured against. The old code read "nothing marked" as "no stall" and returned not-stalled.
    That is backwards: nothing marked means no sample got past where the window started, which is
    the LONGEST stall the window can express. Joe 0814 found it from the times alone — "02:09:25 is
    far better than 02:07:45" — 02:09:25 is gcws30r frozen at 26.63 with its low ageing out, and the
    producer was calling that the END of a stall. Measured on gcws30r 08-04 00:00-03:00 before the
    fix: 15 of 22 moments ended in this branch, and stretching the window made it worse, not better
    (the line ended 28% of stalls at a 100 s window, 0% at a 3600 s one).

    `since` now saturates at samples-1 rather than dropping to -1."""
    S = np.asarray(S, float)
    run = (np.maximum.accumulate(S, axis=1) if dr > 0 else np.minimum.accumulate(S, axis=1))
    fresh = (S[:, 1:] > run[:, :-1]) if dr > 0 else (S[:, 1:] < run[:, :-1])
    #                                  nothing marked -> the extreme IS sample 1, index 0
    last = np.where(fresh.any(axis=1), (S.shape[1] - 1) - np.argmax(fresh[:, ::-1], axis=1), 0)
    since = (S.shape[1] - 1) - last
    ok = np.isfinite(S).all(axis=1)
    return ok & (since >= int(n)), np.where(ok, since, -1)


def stall_mask(y, dr, n, step, samples):
    """[PRODUCER · Joe 0814] stall_on_samples asked at EVERY bar of a line, in one pass.

        y        the whole line, one value per grid bar.
        step     bars between lattice samples.  samples  points in the lattice.

    -> bool array, one per bar. Bars before the lattice fits are False.
    """
    y = np.asarray(y, float)
    step, samples = max(1, int(step)), max(2, int(samples))
    span = (samples - 1) * step
    out = np.zeros(len(y), bool)
    if len(y) <= span:
        return out
    idx = np.arange(span, len(y))[:, None] - (np.arange(samples - 1, -1, -1) * step)[None, :]
    out[span:], _ = _stall_rows(y[idx], dr, n)
    return out


def wsf_facing_dr(mages, hi, lo):
    """[PRODUCER · Joe 0823] "which way am I facing?" - the wsf direction at a delegation moment.

    Joe 0823, verbatim: "wsf's dr will be set by the positioing of gcws30Mage, ws1Mage and ws2Mage -
    if they are all > {100 - knob:20 fence} then dr = +1", and on the mirror: "I've described a
    fence: {100 - knob:20 fence}, therefore below 20 must be logical".

        mages   sequence of the three Mage arrays, on the 5 s grid
        hi/lo   the fence, 80 / 20 at knob 20

    -> int array, one per bar:
        +1  ALL three are above hi
        -1  ALL three are below lo
         0  they do not all agree. Joe 0823: "if the Mages don't agree then capture the moment in a
            stub and we can investigate"

    NO HOLD. Every other wsf crossing carries an xwob; this one does not, and the reason is Joe's,
    0823: "when Mages reverse, profit begins to dwindle, and a hold just increases that loss of
    profit. no holds - the lines are either all outside the fence, or not at all".

    IT DOES NOT REPLACE THE wsf9of12 SIDE. Joe 0823: "this is standalone reaction created when dtf
    delegates to wsf. wsf9of12 is a marker used by wsf to time wsf-level decisions".

    Causal: every read is at its own bar and nothing else.
    """
    M = [np.asarray(m, float) for m in mages]
    up = np.logical_and.reduce([m > float(hi) for m in M])
    dn = np.logical_and.reduce([m < float(lo) for m in M])
    return np.where(up, 1, np.where(dn, -1, 0)).astype(np.int8)


# ── lift-off (JOE'S WORD, 1022: *"you're right - I do want the lift off bar"*) ─────────────────
# WHAT IT IS. Two parts, and they are separate on purpose:
#   at_extreme   a STATE, per bar: is the line still within `tol` of its window extreme on `side`
#   lift_off     the EVENT: the bar that state stops holding - the line has left its extreme
#
# WHY IT IS NOT flat-run, and not a mode of it. Joe 1022 asked whether to build this on flat-run's
# core. The only part they share is the LATTICE - `pts` samples `gap` bars apart ending at the bar
# tested - and that lattice is already shared with stall_mask. The TESTS have nothing in common:
#   flat-run     max - min <= tol. SIDE-FREE, so it answers neither side's question
#   at_extreme   one-sided, measured from the window extreme the side cares about
# Measured, 2026-09-01 19:54:00 on ws5r: every sample in the 225 s window sat at or ABOVE the floor
# 39.81, not one dug below it, and the line was motionless at 39.81 on that bar and the one before.
# flat-run's span test FAILED it anyway, on a 42.00 that aged into the window from 19:50:15 - a
# HIGH-side value vetoing a LOW-side read. Joe: *"this is the verdict for high-side reversal. I need
# low-side data"*. That is the whole reason this producer exists.
#
# THE STATE IS TRUE FOR A FALLING LINE, AND THAT IS CORRECT HERE. On the low side the newest sample
# moves down with the floor, so `newest - min` stays near 0 the whole way down: ws5r held the state
# for 199 bars = 995 s from 19:44:50 while it fell 42 -> 14. The state carries no claim that the
# line has stopped. Only its END does, and the END is what Joe asked for. A consumer wanting "has
# stopped falling" needs a second condition and must say so.
#
# THE LIFT-OFF BAR IS THE FIRST BAR THE STATE FAILS, not the last bar it held. That bar is where the
# information exists: the line has now moved more than tol off its window extreme. CAUSAL, asserted.
#
# NOTHING IS DEFAULTED. `pts`, `gap` and `tol` are the caller's. Joe 1022: *"the sample gaps should
# be TF adjusted"*, and no gap is banked - on ws5r, gaps 5 to 11 bars all land his four targets.
def at_extreme(r, k, side, pts, gap, tol):
    """[PRODUCER - Joe 1022] Is the line within `tol` of its window extreme at bar k. -> dist, None.

        r     the line on the 5 s grid
        k     the bar being tested; the newest sample sits on it
        side  +1 reads the window HIGH, -1 reads the window LOW
        pts   samples in the window
        gap   bars between samples
        tol   how far off the extreme the line may be, in r-points

    -> the distance from the extreme in r-points when the state HOLDS, else None. 0.0 means the
    newest sample IS the window extreme, so `None` and `0.0` are different answers - test `is None`.
    """
    k, pts, gap = int(k), int(pts), int(gap)
    lo = k - (pts - 1) * gap
    if lo < 0:
        return None
    w = np.asarray(r[lo:k + 1:gap], float)
    if len(w) < pts or not np.isfinite(w).all():
        return None
    now = float(w[-1])
    dist = (float(w.max()) - now) if int(side) > 0 else (now - float(w.min()))
    return dist if dist <= float(tol) else None


def at_extreme_mask(r, side, pts, gap, tol):
    """[PRODUCER - Joe 1022] at_extreme asked at EVERY bar, in one pass. -> bool array.

    Mirrors stall_mask's contract: one value per grid bar, False where the lattice does not fit.
    """
    r = np.asarray(r, float)
    pts, gap = max(2, int(pts)), max(1, int(gap))
    span = (pts - 1) * gap
    out = np.zeros(len(r), bool)
    if len(r) <= span:
        return out
    idx = np.arange(span, len(r))[:, None] - (np.arange(pts - 1, -1, -1) * gap)[None, :]
    w = r[idx]
    ok = np.isfinite(w).all(axis=1)
    # the extremes are taken ONLY on usable rows. An all-NaN row warns under nanmax/nanmin, and a
    # warning out of a producer is noise a later reader has to re-diagnose.
    dist = np.full(len(w), np.inf)
    if ok.any():
        ww = w[ok]
        now = ww[:, -1]
        dist[ok] = (ww.max(axis=1) - now) if int(side) > 0 else (now - ww.min(axis=1))
    out[span:] = ok & (dist <= float(tol))
    return out


def lift_off(r, side, pts, gap, tol, wob):
    """[PRODUCER - Joe 1022] THE LIFT-OFF BARS: where at_extreme stops holding. -> int array.

        wob   bars the state must STAY failed, counting the lift-off bar itself. Joe 1022 set 8
              = 40 s: *"add a wob 8 to reduce the early reversals"*. A lift-off whose state
              re-pins inside the hold is not returned.

    Each returned bar is the FIRST bar the state fails after a run of bars where it held. The line
    has moved more than `tol` off its window extreme by then, and every sample that proves it sits
    at or before that bar.

    THE BAR IS NOT THE STAMP. A wob of n means the event is not KNOWABLE until bar + n - 1, which
    is the last bar of the hold and the bar a consumer may act on. This returns the lift-off bar,
    because that is when the line left its extreme; the consumer adds the wob. Joe's standing rule,
    and the two differ by 35 s at wob 8.

    NOTHING IS DEFAULTED, here or in at_extreme. pts, gap, tol and wob are all the caller's.
    """
    m = at_extreme_mask(r, side, pts, gap, tol)
    wob = max(1, int(wob))
    if not m.any():
        return np.zeros(0, int)
    off = np.flatnonzero(np.diff(m.astype(np.int8)) == -1) + 1
    assert off.size == 0 or (int(off.max()) < len(r) and not m[off].any()), \
        'a lift-off bar is one where the state still holds'
    keep = [int(b) for b in off if b + wob <= len(m) and not m[b:b + wob].any()]
    assert all(b + wob - 1 < len(m) for b in keep), 'a lift-off hold ran past the tape'
    return np.asarray(keep, int)


def stoch_out_extreme(stoch_out):
    """[PRODUCER · 0824] Is the reading LEAVING the seven-bar window at an extreme?

    r is the mean of the last SEVEN closed stoch readings, so its next step is already fixed:

        r at next close = r + (stoch now - stoch out) / 7

    stoch is (RSI - RSI lo) / (RSI hi - RSI lo) x 100, so it is EXACTLY 0 when the outgoing RSI was
    the window's low and EXACTLY 100 when it was the window's high. That makes two readings exact
    rather than thresholded:

        stoch out = 0    whatever arrives is at least as big  ->  r CANNOT FALL   -> returns +1
        stoch out = 100  whatever arrives is no bigger        ->  r CANNOT RISE   -> returns -1
        anything else                                                             -> returns 0

    This is the mechanical form of Joe's 0824 lesson: "r has dropped to the ~floor (momo), and has
    nowhere to go (none)".

    ROUNDED TO 6 PLACES, AND THAT IS NOT A KNOB. The division leaves float residue - 08-04 00:52:30
    ws5 stored 1.4168726029049243e-14 for 0 and 08:02:50 ws6 stored 99.99999999999999 for 100, and
    raw equality missed both. The nearest genuine readings on the same boards are 42.41 and 50.00,
    seven orders away. It recovers the intended number; it does not choose a level.

    Causal: one bar, one already-measured value.
    """
    if stoch_out is None:
        return 0
    v = round(float(stoch_out), 6)
    return 1 if v == 0.0 else -1 if v == 100.0 else 0


def wsf_dr_lookback(dr, nbars):
    """[PRODUCER · Joe 0823] The most recent dr the three Mage lines gave, within nbars.

    Joe 0823: "restrict the lookback to 3 minutes" - 36 bars at the 5 s grid. At a bar where the
    three lines are not all outside the fence, this is the dr wsf actually uses.

        dr      the per-bar output of wsf_facing_dr - +1, -1 or 0
        nbars   how far back to look, in bars. The bar itself counts, so the window is nbars + 1.

    -> (dr_out, lag) both int arrays, one per bar:
        dr_out  the most recent non-zero dr in the window, 0 if there is none
        lag     how many bars back it came from. 0 means the bar itself answered.
                -1 where dr_out is 0.

    Causal: bar i reads bars i-nbars to i and nothing later.
    """
    dr = np.asarray(dr, np.int8)
    n = len(dr)
    out = np.zeros(n, np.int8)
    lag = np.full(n, -1, np.int32)
    last = -1
    for i in range(n):
        if dr[i] != 0:
            last = i
        if last >= 0 and (i - last) <= int(nbars):
            out[i] = dr[last]
            lag[i] = i - last
    return out, lag


def wsf_facing_dr_held(dr, xwob):
    """[PRODUCER · Joe 0824] wsf_facing_dr() with a hold on it.

    Joe 0824, verbatim: "for each signal without lookback validation, we hold and walk until
    (xwob:4) gcws30Mge + ws1Mage + ws2Mage are oob. we set dr at that moment, then run the wsf
    model".

        dr      the per-bar output of wsf_facing_dr - +1, -1 or 0
        xwob    bars the same non-zero direction must hold. Joe 0824: 4 = 20 s at the 5 s grid

    -> int array. The direction on every bar where it has held xwob bars in a row, 0 elsewhere.
       The consumer takes the RISING EDGE for the confirmation moment.

    THE HOLD IS SEPARATE FROM JOE'S 0823 NO-HOLD RULING, and both stand. 0823 was about reading
    the facing AT a delegation moment: "no holds - the lines are either all outside the fence, or
    not at all". This is the forward WAIT for that condition to appear afterwards, which is a
    different moment and is the one Joe put an xwob on.

    Causal: bar i reads bars i-xwob+1 to i and nothing later.
    """
    dr = np.asarray(dr, np.int8)
    idx = np.arange(len(dr))
    out = np.zeros(len(dr), np.int8)
    for sign in (-1, 1):
        side = dr == sign
        reset = np.where(side, 0, idx + 1)
        run = (idx + 1) - np.maximum.accumulate(reset)
        out[run >= max(1, int(xwob))] = sign
    return out


def domtf_median(tagged):
    """[PRODUCER · Joe 0814] The line the group nominates.

    Joe 0814: "the median of the tagged domTF lines". Even count: "take the higher of the 2 TFs".

        tagged  the timeframes currently in the group.

    -> the timeframe to watch, or 0 when the group is empty.
    """
    t = sorted(int(x) for x in tagged)
    if not t:
        return 0
    return t[len(t) // 2]          # odd -> the middle. even -> the higher of the two middles.


def domtf_handover_median(tag, seed, cross_ok, inside, stall, w, i1):
    """[PRODUCER · Joe 0814] The bar the domTF turn ends, when the GROUP nominates the line.

    Task 9. One line is watched at a time — the median of the tagged group — instead of a race
    between all of them. The group is re-derived every bar and grows, so the nomination moves.

    Joe 0814 on a nominated line that never fires: "it must fire; this is why I introduced stall."
    Joe 0814 on the 22-27 restriction: "for this mech, we include all lines that land in the
    group" — the whole tagged group, uncut.

        tag       {tf: bool array} momo or curl in the signal's direction at that bar.
        seed      the group at the signal bar.
        cross_ok  {tf: bool array} the fast partner has crossed and held.
        inside    {tf: bool array} the r line is back between the boundaries.
        stall     stall(tf, bar) -> bool.
        w         the signal bar. The walk starts at w+1.  i1  the last bar.

    -> (bar, tf, how, joins, leaves). `how` is 'cross' or 'stall'. (None, 0, None, ...) if the
       window ends first.
    """
    grp = set(int(t) for t in seed)
    present = {int(t): True for t in grp}
    joins, leaves = [], []
    for i in range(int(w) + 1, int(i1) + 1):
        for tf, m in tag.items():
            on = bool(m[i]); was = present.get(int(tf), False)
            if on and not was:
                present[int(tf)] = True
                if int(tf) not in grp:
                    grp.add(int(tf)); joins.append((i, int(tf)))
            elif not on and was:
                present[int(tf)] = False; leaves.append((i, int(tf)))
        tf = domtf_median(grp)
        if not tf:
            continue
        if inside[tf][i] and cross_ok[tf][i]:
            return i, tf, 'cross', joins, leaves
        if stall(tf, i):
            return i, tf, 'stall', joins, leaves
    return None, 0, None, joins, leaves


def domtf_handover(blocking, htf_curled, htf_band, cross_ok, inside, stall, w, i1):
    """[PRODUCER · Joe 0814] The bar the domTF turn ends. A race, first past the post.

    Joe 0813: "first past the post".
    Joe 0814: "IF a domTF HTF has recently {knob:2 TF bars} curled towards dr, then the handoff
    (cross OR stall) needs to be created by the HTFs[22:27] -- if we let the smaller domTFs create
    the exit, it will be premature - the HTF curl says renewed high-level momentum."

    A BOLT-ON, NOT A REPLACEMENT. Joe 0814: "this mech isn't a replacement to the existing (and
    mostly functional) domTF mechanic - it's a bolt on." When no BLOCKING line sits inside
    htf_band the restriction DOES NOT QUALIFY and the plain race runs. Joe 0814: "you weren't
    'falling back'; you were simply not engaging the new spec because it didn't qualify (ie no
    HTF lines)." Not a fallback, not a default, not a degraded path.

        blocking    the lines whose momentum verdict at the signal bar is momo or curl in the
                    signal's direction. These are the race candidates. Joe's word, 0814 — the
                    earlier "carrying the move" was my coinage and is retired.
        htf_curled  lines INSIDE htf_band that have bent into the signal's direction within the
                    recency window. Non-empty means the restriction is offered.
        htf_band    (22, 27). Joe 0814: "from 22-27 (semi arbitrary)" and "let's keep it static".
        cross_ok    {tf: bool array} the fast partner has crossed to the far side and held.
        inside      {tf: bool array} the r line is back inside the boundaries.
        stall       stall(tf, bar) -> bool, supplied by the caller (SRP, it owns the sampling).
        w           the signal bar. The race starts at w+1.
        i1          the last bar to search.

    -> (bar, tf, how) or (None, 0, None). `how` is 'cross' or 'stall'.

    EITHER TEST ENDS THE TURN. Joe's "(cross OR stall)". The cross also requires the line to be
    back inside the boundaries; the stall does not, because a stalled line has stopped moving
    wherever it happens to sit.
    """
    lo, hi = int(htf_band[0]), int(htf_band[1])
    band = [tf for tf in blocking if lo <= tf <= hi]
    pool = band if (htf_curled and band) else list(blocking)   # empty band -> does not qualify
    if not pool:
        return None, 0, None
    for i in range(int(w) + 1, int(i1) + 1):
        for tf in pool:
            if inside[tf][i] and cross_ok[tf][i]:
                return i, tf, 'cross'
            if stall(tf, i):
                return i, tf, 'stall'
    return None, 0, None
