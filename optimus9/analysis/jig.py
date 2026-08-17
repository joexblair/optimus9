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

    def pk_state(self, line_slope, price_slope, slope_floor):
        """Slope-sign divergence state — delegates to the production seam Pk5sGateComputer._pk_state_from_slopes
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
