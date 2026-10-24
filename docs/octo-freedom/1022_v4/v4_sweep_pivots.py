"""`sweep-pivots` - Joe 1024 named it. The swing scale for a sweep, with no pivot pct to set.

WHY IT EXISTS. Joe 1024: *"getting swings correctly dialed is the most load-bearing mech in a
sweep - if we can't rely on them then we produce false results"*, and then *"I'm going to hand it
back to you and find a way to dynamically set it. fixing a pct has never completley served us -
now I feel like we have a way to automate it"*.

HIS MECH, verbatim across two messages:

    *"I'd be looking more at Mages crossing to ib across various TFs, maybe (ws3Mage, ws5Mage,
    ws10Mage, ws15, ws20, ws30). we can reliably predict that a mage crossing from oob to ib will
    always land on the MFE side."*

    *"given that a sweep allows full lookahead, you can collect the swings and pivots from all of
    the noted Mages. when you have an event to test, see how many per-Mage-pivots are closest to
    the event. if you have multiple TF's Mages pivots that align with the event, then your likely
    at a larger swing and can use the higher TFs swing to more accurately gauge the MFE (instead
    of using a small swings MFE)"*

HIS CLAIM, MEASURED AND SUPPORTED. Anchored on the PRIOR pivot - his correction, *"it should be
the prior pivot, if we're following my 'opens on the MFE side' view"* - 82% to 93% of Mage
oob->ib crosses open on the favourable side of the move's start, across every TF and every pivot
pct from 0.5 to 2.2. Measured FORWARD it had read 43% to 59%, because the next pivot is where the
move ENDS and that scored the cross against its own destination.

THE LADDER IS REAL, and it is why there is no pct here. Each Mage TF's own consecutive
opposite-side crosses bracket a leg, and the medians are monotone over the 94 days:

    ws1Mage 0.375%   ws2Mage 0.606%   ws3Mage 0.751%   ws5Mage 1.007%
    ws10Mage 1.477%  ws15Mage 1.831%  ws20Mage 2.198%  ws30Mage 2.633%

A single fixed pct can only ever match one rung - the equivalents run 0.3% to 1.5% - which is
what *"fixing a pct has never completley served us"* is, in numbers.

THE ONE KNOB, and it is a timing tolerance rather than a swing size. `ALIGN_S` 300 s, Joe 1024
*"agreed on 300s"*, from this measurement over 5,323 events:

    window   no marking TF     mean TFs marking
    60 s     3558 = 66.8%      0.46 of 8
    180 s     806 = 15.1%      1.97 of 8
    300 s     386 =  7.3%      2.42 of 8
    600 s      81 =  1.5%      3.08 of 8
    900 s      22 =  0.4%      3.47 of 8

TOLERANCE-FREE CONTAINMENT WAS MEASURED AND REJECTED. Asking instead whether the event falls
inside the leg a same-side cross opened needs no window at all, and ws30Mage then becomes the
highest marker on 2,350 of 5,323 events - 44.1% - because its legs run 14,157 s. The rung wins by
being wide, not by matching. Recorded here so nobody re-proposes it as the clean version.

LOOKAHEAD IS ALLOWED HERE AND ONLY HERE. Joe: *"given that a sweep allows full lookahead"*. A leg
is closed by a cross AFTER the event, so `scale` and `mfe` read the future on purpose. They are
SCORING, and no mech step may call them - `v4_test_script`'s stage guard asserts that separately.
"""
import os

import numpy as np

import ln
import v4_knobs as K
from optimus9.analysis.jig import oob_ib_cross

# ── his TF list, and the two lines that are MINE ────────────────────────────────────────────────
TFS_HIS = ('ws3Mage', 'ws5Mage', 'ws10Mage', 'ws15Mage', 'ws20Mage', 'ws30Mage')
TFS_WIDE = ('ws1Mage', 'ws2Mage') + TFS_HIS
#   His 1024 list is the six. ws1Mage and ws2Mage are my addition and they are NOT a detail: at
#   ALIGN_S 300 they are the highest marking TF on 13.1% and 27.9% of events, 41.0% together. The
#   default is HIS six; `wide=True` is the variant, reported beside it and never as the baseline.

# ── THE KNOBS LIVE IN v4_knobs, NOT HERE. Joe 1024: *"if there's knobs, make sure they're
#    visible"*. v4_knobs is the one home, it refuses an off-ruled run, and `v4_sweep_pivots.knobs()`
#    prints them so any driver can log the set it ran under. Every `why` below is the MEASUREMENT
#    that set the value, not a preference.
PICK = K.SP_PICK          # 'lowest_pct' - his 1024 rule: the highest TF printing the lowest pct
BAND = K.SP_BAND          # 0.0 pct points - 53.6% of 37,178 pct gaps are EXACTLY 0, p50 = 0.0000
CONTAIN = bool(K.SP_CONTAIN)   # 0 - ON drops 2,198 of 5,323 events and triples the pivot distance
XWOB = K.SP_XWOB          # 18 bars = 90 s - his *"introduce a wob 18"*
ALIGN_S = K.SP_ALIGN_S    # 300 s - his *"agreed on 300s"*. UNREAD under PICK 'lowest_pct'
WIDE = K.SP_TFS == 'wide'  # the TF set. 'wide' = his six PLUS my ws1Mage and ws2Mage - the set
#                            every banking measurement was run on, and the one item awaiting his
#                            word. His 1024 list was the six


def _tfs(wide=None):
    """The TF set. `None` means the BANKED set, K.SP_TFS - so a caller cannot run an unbanked
    set by leaving the argument out."""
    return TFS_WIDE if (WIDE if wide is None else wide) else TFS_HIS


def knobs():
    """-> the knob set this module is running under, as (name, value, why) rows.

    So a driver can print what it ran under instead of a reader having to trust a docstring.
    """
    return [('SP_PICK', PICK, 'the highest TF printing the lowest pct - his 1024 rule'),
            ('SP_BAND', BAND, 'the near-same band, pct points. 53.6% of gaps are exactly 0'),
            ('SP_CONTAIN', int(CONTAIN), 'off - ON drops 2198 of 5323 events'),
            ('SP_XWOB', XWOB, 'bars IB must hold for a Mage cross - his wob 18'),
            ('SP_ALIGN_S', ALIGN_S, 'seconds, read ONLY by the window arm'),
            ('SP_TFS', K.SP_TFS, 'wide = his six plus ws1Mage and ws2Mage - AWAITING HIS WORD')]     # how a pivot is chosen from the index.
#   'lowest_pct' Joe 1024: *"start at the lowest TF and scan upwards. you should find a series of
#              TFs printing the near-same distance from their own pivot to the event. the TF
#              swing/pivot to pick should be the highest TF printing the lowest pct (between pivot
#              and event)"*. The criterion is the PRICE distance from each TF's OWN pivot to the
#              event, not the time distance. TFs that agree on a pivot bar print an IDENTICAL pct,
#              so the rule picks the highest TF of the agreeing group and needs NO tolerance - the
#              *"near-same"* group resolves itself.
#   'nearest'  Joe 1024: *"pre-build the pivot data for all of the in-use Mages, then pick the
#              pivot from the index based on same direction and closeness to the prior pivot"*.
#              Closeness RANKS, it does not gate, so every event gets a pivot and ALIGN_S is not
#              read at all. This is the default because *"they all need to be rated"*.
#   'window'   the earlier form: a TF marks the event only within ALIGN_S, then the HIGHEST marking
#              TF wins. Kept because it is what the 300 s agreement was made against, and because
#              it is the only form that uses the confluence count.

_CX = {}
_IDX = {}
_LEG = {}
_LEGMAP = {}


def index(wide=None, xwob=None):
    """THE PRE-BUILT PIVOT INDEX across every in-use Mage. -> (bars, sides, tfs), bar-sorted.

    Joe 1024: *"pre-build the pivot data for all of the in-use Mages, then pick the pivot from the
    index"*. One pass per TF, cached, so a 5,323-event scoring run does not rebuild anything.
    `tfs` holds the TF's position in the ladder, so a higher number is a higher timeframe.
    """
    tfs = _tfs(wide)
    key = (tuple(tfs), XWOB if xwob is None else xwob)
    if key not in _IDX:
        b, sd, ti = [], [], []
        for n, t in enumerate(tfs):
            for _, f, s in crosses(t, xwob):
                b.append(int(f)); sd.append(int(s)); ti.append(n)
        o = np.argsort(np.asarray(b, int), kind='stable')
        _IDX[key] = (np.asarray(b, int)[o], np.asarray(sd, int)[o], np.asarray(ti, int)[o], tfs)
    return _IDX[key]


def crosses(tf, xwob=None):
    """Every oob->ib cross of one Mage. -> list of (cross, confirm, side).

    `side` is the side of the oob run the line LEFT: +1 it was high, -1 it was low. `confirm` is
    cross + xwob - 1, the first bar the cross is knowable. Cached per (tf, xwob).
    """
    xwob = XWOB if xwob is None else xwob
    key = (tf, xwob)
    if key not in _CX:
        v = np.asarray(ln.line(tf), float)
        _CX[key] = oob_ib_cross(v, K.OOB_HI, K.OOB_LO, xwob)
    return _CX[key]


def legs(tf, xwob=None):
    """The legs one Mage brackets with its OWN crosses. -> list of (open, close, side).

    A leg opens on a cross and closes on the next OPPOSITE-side cross of the same line. Both ends
    are mechanism-defined, which is the whole point - no pct and no horizon. `side` is the opening
    cross's side, so a leg opened by a LOW cross is a leg the price rises through.

    EVERY cross opens a leg. The first version paired only ADJACENT crosses and skipped any cross
    followed by another on the same side, so those crosses had no leg at all and `scale` reported
    them as unmarked. On the 18-event check that silently dropped 7 events whose marking cross was
    90 to 410 s away - inside ALIGN_S - and printed them as "none marks it". Consecutive same-side
    crosses are a line re-entering oob and leaving again; each of them still opens a leg that runs
    to the next opposite boundary, so the legs OVERLAP and that is correct.
    """
    key = (tf, XWOB if xwob is None else xwob)
    if key in _LEG:
        return _LEG[key]
    xc = crosses(tf, xwob)
    out, nxt = [], {}
    for i in range(len(xc) - 1, -1, -1):              # one backward pass, not a nested scan
        s0 = int(xc[i][2])
        o = nxt.get(-s0)
        if o is not None:
            out.append((int(xc[i][1]), o, s0))
        nxt[s0] = int(xc[i][1])
    out.sort()
    _LEG[key] = out
    return out


def marks(tf, bar, side, align_s=None, xwob=None):
    """Does this Mage mark `bar` on `side`. -> the confirm bar of its nearest same-side cross, or None.

    *"see how many per-Mage-pivots are closest to the event"*. Nearest in EITHER direction: a
    cross before the event is the move's own start and a cross after it is the same boundary seen
    late, so excluding one side would answer a different question.
    """
    align_s = ALIGN_S if align_s is None else align_s
    c = np.array([f for _, f, s in crosses(tf, xwob) if s == side])
    if not len(c):
        return None
    i = int(np.argmin(np.abs(c - bar)))
    return int(c[i]) if abs(int(c[i]) - bar) * 5 <= align_s else None


def scale(bar, side, wide=None, align_s=None, xwob=None):
    """The swing scale for one event. -> dict or None.

    *"if you have multiple TF's Mages pivots that align with the event, then your likely at a
    larger swing and can use the higher TFs swing"* - so the HIGHEST marking TF wins, and the leg
    it returns is that TF's own.

    -> {'tf', 'n_marking', 'marking', 'cross', 'open', 'close', 'leg_pct'} or None when no TF
    marks the event inside `align_s`. None is reported, never substituted: 386 of 5,323 events are
    unscorable at 300 s and that is 7.3% of the population, not a rounding error.
    """
    tfs = _tfs(wide)
    if PICK == 'nearest':
        b, sd, ti, names = index(wide, xwob)
        m = sd == side
        if not m.any():
            return None
        bb, tt = b[m], ti[m]
        d = np.abs(bb - bar)
        best = int(d.min())
        cand = np.flatnonzero(d == best)                 # ties: the HIGHEST TF, his confluence rule
        j = int(cand[int(np.argmax(tt[cand]))])
        tf, cross = names[int(tt[j])], int(bb[j])
        hit = [(names[int(t)], int(x)) for x, t in zip(bb[d <= best], tt[d <= best])]
    else:
        hit = [(t, marks(t, bar, side, align_s, xwob)) for t in tfs]
        hit = [(t, c) for t, c in hit if c is not None]
        if not hit:
            return None
        tf, cross = hit[-1]                              # tfs is ordered low -> high
    for o, z, s in legs(tf, xwob):
        if o == cross:
            return {'tf': tf, 'n_marking': len(hit), 'marking': [t for t, _ in hit],
                    'cross': cross, 'open': o, 'close': z, 'leg_pct': None}
    return {'tf': tf, 'n_marking': len(hit), 'marking': [t for t, _ in hit],
            'cross': cross, 'open': cross, 'close': None, 'leg_pct': None}


def per_tf(bar, side, close_px, wide=None, xwob=None):
    """Each in-use Mage's own pivot for this event, and the pct from it. -> list, lowest TF first.

    Per TF: its same-side cross nearest the event opens a leg; that leg's extremum on `side` is
    the TF's pivot; `pct` is the favourable-signed move from the pivot to the event. A TF appears
    only if its cross opens a closed leg, and - under CONTAIN - only if the EVENT falls inside it.
    """
    tfs = _tfs(wide)
    out = []
    for n, t in enumerate(tfs):
        c = np.array([f for _, f, s in crosses(t, xwob) if s == side])
        if not len(c):
            continue
        cross = int(c[int(np.argmin(np.abs(c - bar)))])
        lg = legs(t, xwob)
        key = (t, XWOB if xwob is None else xwob)
        if key not in _LEGMAP:
            _LEGMAP[key] = {o: (o, z) for o, z, _ in lg}
        leg = _LEGMAP[key].get(cross)
        if leg is None:
            continue
        o, z = leg
        seg = np.asarray(close_px[o:z + 1], float)
        if not np.isfinite(seg).any():
            continue
        j = o + int(np.nanargmin(seg) if side < 0 else np.nanargmax(seg))
        p0 = float(close_px[j])
        if CONTAIN and not (o <= bar <= z):
            continue
        out.append({'tf': t, 'rung': n, 'cross': cross, 'open': o, 'close': z, 'pivot': j,
                    'pct': (float(close_px[bar]) - p0) / p0 * 100.0 * (-side),
                    'lag_s': (bar - j) * 5})
    return out


def swing(bar, side, close_px, wide=None, align_s=None, xwob=None):
    """The event's swing, measured inside the scale's own leg. -> dict or None.

        pivot      the leg's extremum on `side` - the LOW of a leg a LOW cross opened
        mfe_pct    the favourable excursion from the pivot to the leg's end
        given_pct  the favourable move already behind at the event bar
        share      given / mfe. How much of the swing the event gave away

    `close_px` is passed in rather than read here, so this module never loads a price series of
    its own and the one the caller scored with is the one used.
    """
    if PICK == 'lowest_pct':
        cands = per_tf(bar, side, close_px, wide, xwob)
        if not cands:
            return None
        lo = min(abs(c['pct']) for c in cands)
        tie = [c for c in cands if abs(c['pct']) <= lo + BAND]
        sc = max(tie, key=lambda c: c['rung'])          # the HIGHEST TF of the agreeing group
        sc = dict(sc, n_marking=len(tie), marking=[c['tf'] for c in tie], leg_pct=None)
    else:
        sc = scale(bar, side, wide, align_s, xwob)
    if sc is None or sc['close'] is None:
        return None
    o, z, fav = sc['open'], sc['close'], -side
    seg = np.asarray(close_px[o:z + 1], float)
    if not np.isfinite(seg).any():
        return None
    j = o + int(np.nanargmin(seg) if side < 0 else np.nanargmax(seg))
    p0 = float(close_px[j])
    if fav > 0:                                      # a LOW-opened leg rises off its low
        mfe = (float(np.nanmax(seg)) - p0) / p0 * 100.0
    else:                                            # a HIGH-opened leg falls off its high
        mfe = (p0 - float(np.nanmin(seg))) / p0 * 100.0
    given = (float(close_px[bar]) - p0) / p0 * 100.0 * fav
    return dict(sc, pivot=j, mfe_pct=mfe, given_pct=given,
                share=(given / mfe) if mfe > 0 else None,
                lag_s=(bar - j) * 5)
