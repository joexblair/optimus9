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
WIDE = K.SP_TFS == 'wide'  # the TF set. 'wide' = his six PLUS ws1Mage and ws2Mage - the set
#                            every banking measurement was run on. HIS 1024 list was the six and
#                            the extra two were mine; HIS 1108 ruling *"bank the current config and
#                            make it the machine"* makes all eight his


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
            ('SP_TFS', K.SP_TFS, 'wide = his six plus ws1Mage and ws2Mage - RULED 1108, *"bank '
                                 'the current config and make it the machine"*')]     # how a pivot is chosen from the index.
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
        _CX[key] = oob_ib_cross(mage(tf), K.OOB_HI, K.OOB_LO, xwob)
    return _CX[key]


def mage(tf):
    """One Mage line by name. -> array. ws1Mage .. ws30Mage AND the sub-wsf names.

    HIS 1108 asked for *"TF1,2,3 and gcws30"*. `ln.line` parses ws{tf}{role} and multiplies the
    digits by 60, so `ln.line('gcws30Mage')` cannot resolve a 30 s line at all - it raises on the
    digit scan. v4_live_lines.sub_line is the resolver that reads the production LineStore spec, so
    a sub-wsf name comes back as the same array the live tree reads. One place decides which
    resolver a name needs, so no caller has to know.
    """
    tf = str(tf)
    if tf.startswith('ws') and tf[2].isdigit():
        return np.asarray(ln.line(tf), float)
    import v4_live_lines as _LL
    return np.asarray(_LL.sub_line(tf), float)


def legs(tf, xwob=None, mode=None):
    """The legs one Mage brackets with its OWN crosses. -> list of (open, close, side).

    `mode` picks HOW the crosses are paired, and the DEFAULT IS THE BANKED RULE so no existing
    caller moves:
      None / 'banked'  every cross opens a leg and it closes on the FIRST opposite cross. The legs
                       overlap. This is what every v4 and fdm3 read has always used.
      'last_cross'     HIS 1118 fdm3 MODE, in his words: *"I thought sweep-pivots went from 'last
                       cross to ib' to opposing side 'last-cross to ib'"*. Each RUN of same-side
                       crosses collapses to its last, so the legs tile end to end and never
                       overlap. HIS 1118: *"don't rebuild it - create a mode for this new mech so
                       that the existing pivots remain untouched in any now or future fdm3-oracle
                       updates"*. On ws2Mage it yields 1564 legs, which is the pseudo trade count,
                       because towards_away's pivot builder already collapses same-side runs this
                       way.
    Both modes pair CONFIRM bars, not cross bars - the first bar a cross is knowable.

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
    xwob = XWOB if xwob is None else xwob
    mode = 'banked' if mode is None else mode
    assert mode in ('banked', 'last_cross'), mode
    key = (tf, xwob, mode)
    if key in _LEG:
        return _LEG[key]
    if mode == 'last_cross':
        #   HIS 1118 MODE: keep only the LAST cross of each same-side run, then consecutive pairs
        #   are the legs. They tile - one leg's close is the next one's open - and never overlap.
        _xc = crosses(tf, xwob)
        _last = [_xc[i] for i in range(len(_xc))
                 if i + 1 == len(_xc) or int(_xc[i + 1][2]) != int(_xc[i][2])]
        _out = [(int(_last[i][1]), int(_last[i + 1][1]), int(_last[i][2]))
                for i in range(len(_last) - 1)]
        assert all(_out[i][1] == _out[i + 1][0] for i in range(len(_out) - 1)), \
            'his last_cross legs must tile, one leg closing where the next opens'
        assert all(_out[i][2] != _out[i + 1][2] for i in range(len(_out) - 1)), \
            'two of his last_cross legs in a row share a side'
        _LEG[key] = _out
        return _out
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


def pooled_pivots(tf, dwell_s, xwob=None, reads=('Mage', 'b')):
    """HIS 1118 FOUR-READ PIVOTS. -> list of (confirm bar, cross bar, side), alternating.

    HIS WORDS, in order: *"bake the 4 lines into the sweep-pivots machine: every test uses all
    lines to decide if dwell is qualified"*, then on how they combine *"1, the longest"*, and on
    how the crosses group *"2, it shouldn't matter - we're going from a 'final' cross to ib, to
    the next 'final' cross to ib"*.

    THE FOUR READS of ws{tf}: Mage emerging, Mage closed-prev, b emerging, b closed-prev. Every
    one of them contributes its own oob->ib crosses, each carrying the DWELL - how long that read
    held out of bounds immediately before the cross.
    THE RULE: pool all four, split into runs of consecutive SAME-SIDE crosses, and a run qualifies
    when the LONGEST dwell inside it reaches `dwell_s`. The pivot is that run's FINAL cross to ib.
    Runs that fail are dropped, and two surviving runs that then touch on the same side merge,
    again taking the last.
    NO TIME TOLERANCE is needed: the group is a same-side run, which is what he ruled.

    WHY FOUR READS. The emerging line flickers in and out of the fence, so a real 2.4 minute oob
    run measures as 0.1 on it while closed-prev measures the same move as 3.0. Taking the longest
    lets the steady read supply the dwell and the fast read supply the bar.
    """
    import v4_closed_prev as CP
    import ln as _ln
    xwob = XWOB if xwob is None else xwob
    key = ('pooled', tf, xwob, int(dwell_s), reads)
    if key in _LEG:
        return _LEG[key]
    ev = []
    for role in reads:
        em = np.asarray(_ln.line('ws%d%s' % (int(tf), role)), float)
        for lab, arr in (('em', em), ('cp', np.asarray(CP.series(em, int(tf) * 60), float))):
            for c, cf, sd in oob_ib_cross(arr, K.OOB_HI, K.OOB_LO, xwob):
                n, i = 0, int(c) - 1
                while i >= 0 and np.isfinite(arr[i]) and (
                        (arr[i] >= K.OOB_HI) if sd > 0 else (arr[i] <= K.OOB_LO)):
                    n += 1
                    i -= 1
                ev.append((int(c), int(cf), int(sd), n * 5))
    ev.sort()
    runs, cur = [], []
    for e in ev:
        if cur and e[2] == cur[0][2]:
            cur.append(e)
        else:
            if cur:
                runs.append(cur)
            cur = [e]
    if cur:
        runs.append(cur)
    out = []
    for r in runs:
        if max(x[3] for x in r) < int(dwell_s):
            continue
        last = r[-1]
        if out and out[-1][2] == last[2]:
            out[-1] = (last[1], last[0], last[2])       # same side again: take the later one
        else:
            out.append((last[1], last[0], last[2]))
    assert all(out[i][2] != out[i + 1][2] for i in range(len(out) - 1)), \
        'two of his pooled pivots in a row share a side'
    assert all(out[i][0] <= out[i + 1][0] for i in range(len(out) - 1)), 'the pivots are not in order'
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
