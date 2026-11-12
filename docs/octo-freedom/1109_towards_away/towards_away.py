"""THE NEW towards/away mech, Joe 1109. -> for each r line ws1..ws30, at each 5 s bar: TO, AW or no read.

HIS 1110: *"add ws1-3 to towards/away and liftoff, and update webUI"* - the lines were ws4..ws30 (his 1109 10A).

GOAL: a better towards/away mech, every decision anchored on the trade's target-side. His one-sentence goal is
not stated yet - see the spec.

BANKED AND LIVE, Joe 1109: *"bank the towards/away update. commit push all files. update the spec, make notes
about the webUI build, and make the machine live."* LIVE in his sense: this is the towards/away mech we develop
on. The spec is docs/octo-freedom/1109_towards_away.md - every knob, every rule fixed in code, and the web UI.
The knobs are ta_knobs.py, banked: an off-ruled run refuses unless W_TA_EXPERIMENT=1.

HIS 1109, the anchor: *"target-side is the anchor for all towards/away decisions"*. SRP, his 1109 correction:
*"here's the poorly placed note - it is a separate update for lift-off mech, and does not apply to
towards/away mech.   the common/shared artifact is the newly built ws{TF}e"*. So nothing here changes
lift-off. This mech CONSUMES lift-off's reversals, as they are.

THE PIECES, in firing order:

  ws{TF}e         BB%B len 3, mult 0.5, src close, emerging, ws1..ws30 (version 2), from its row in the dynamic config
                  table (mech_line_config: 'towards-away', role 'e', version 1), your indicator config spec.
                  IN THE LINE CACHE since 1109 (*"update the cache"*), read through rpl_cache by its spec key
                  and checked against the 1109 known-good numbers on every load.
  the pseudo trade  sweep-pivots' ws2Mage pivots. HIS 1109: *"use the last/later pivot time to create the
                  psuedo rev-trade signal"*. A trade opens at the last pivot of one same-side run and closes
                  at the last pivot of the next run. Its target-side is the side of the run it closes on, so
                  a trade opened at a HIGH run's last pivot has a LOW target-side. LOOKAHEAD, on purpose: a
                  pivot is only fixed when its leg closes - his *"noted - it's not a realtime tool"*.
  auto-towards    *"at the start of a trade, an r line is automatically tagged as towards"*, and it stays so
                  while it has not reached ex-20/80 on the target side this trade. ex-20/80 is the banked
                  reader: closed-prev at or beyond 20/80, OR the emerging extreme of the last 12 bars = 60 s.
                  Reached once, it counts for the rest of the trade (*"after having left ex-fence (during
                  this trade)"*).
  scenario 1      the line reached ex-20/80. HIS ANSWER 6: *"the extremum is set by lift-offs reversal, which
                  uses emerging"*. Each target-side lift-off reversal on the emerging r stores its pivot's
                  value, at the reversal's stamp (lift bar + LIFT_WOB 8 - 1 = 35 s). *"extremum can be stored
                  while an r line is infence, but it has no vote for the `away` line verdict in scenario 1"* -
                  so only an extremum whose value is ex-20/80 votes. The latest voting extremum makes the line
                  AW from its stamp; the line stays AW while its emerging value has not gone past that
                  extremum toward the target side, and is TO from the first bar it has.
                  HIS 1110 LIFT-OFF UPDATE adds lift-off's e-CROSS reversals (jig.lift_off_e, v4_lift_e): the
                  extremum is ws{TF}r at his walk-back bar, printed on the first following lift-off sample
                  closer to 50, no hold. It votes only when ex-20/80 (his 5A) and is stored only when MORE
                  extreme than the stored one, or when none is stored (his 3B). A natural reversal still
                  replaces the stored one as the latest.
  e-samples       ws{TF}e crossing race:{boundary, ws{TF}Mage, ws{TF}r} - under 85 / Mage / r on a HIGH
                  target-side, over 15 / Mage / r on a LOW one. r and Mage are closed-prev (RACE_READ), e is
                  emerging.
                  HIS 3A: no hold. HIS 4B: only the first of the three counts; the race re-opens once e
                  crosses back over that same line the other way. Each trade's race starts open.
                  HIS 1110 4A, *"one e-sample **method** everywhere"*: the sample is ws{TF}r at his walk back to
                  look forward bar on ws{TF}e (48-bar steps, his 1A) - lift-off's own e-sample - knowable on
                  the cross bar. Until 1110 it was ws{TF}r on the cross bar.
  scenario 2      the line has not reached ex-20/80. *"if a ws{TF}r line prints two infence samples (built
                  by the e-cross sampling) which are within 2% of each other"* - HIS 7A: the latest two
                  samples this trade, within PAIR_PTS 2.0 r-points - and *"IF there are >1 r lines within
                  {knob:5} TFs **under** this TF, that are printing away while in ex-fence, or printing away
                  after having left ex-fence (during this trade)"* - those are scenario-1 lines reading AW.
                  HIS 8A: tested on the bar of the second sample only. HIS 9B: the stored extremum is the more
                  target-side of the two samples. The line is AW from that bar and stays so while it has not
                  gone past the extremum (*"the same logic as the existing build"*).
  the flip at 50  HIS 1110, *"the AW/TO logic needs refining"*: *"if a line has printed an extremum and is tagged as
                  away"* / *"if the line has returned past 50 (ie crossed to the counter target-side)"* / *"if the
                  line returns to the target-side of 50, the tag flips from away to toward"*. HIS ANSWERS: the r read
                  is emerging (FLIP50_READ); scenario 1 AND scenario 2; an AW that starts with r already on the far
                  side of 50 already counts; after the flip the extremum is retired, TO until a newer one is stored
                  (the same as going past it). Strictly past 50 both ways - no bar on the tape sits at exactly 50.00
                  on ws1r..ws30r, emerging or closed-prev, so the choice moves nothing.

THE 1112 UPDATE, HIS *"I want to see the flip from TO to AW based on the x and e cross."* Each piece has its own knob in
ta_knobs; all of them off is the bank before it, exactly (spec section 12).
  the 50 reset    HIS *"when ws3r passed under 50 (the counter-side of 50), that 2124 extremum should be nulled until a
                  new one is built."* A pass to the counter side of 50 (emerging r, FLIP50_READ) ends the hunt and
                  nulls its ex-20/80 reach; the first bar back on the target side starts a fresh hunt - scenario 2
                  samples again, and only samples at or after that bar pair. A new reach shuts the hunt again. The
                  trade's open always starts the first hunt (his *"the mech says that all lines are reset to TO when a
                  trade opens"*). Scenario 1 stores a voting extremum only inside a reached hunt, pivot inside it.
  the sample      HIS *"e or x creates a timestamp when it crosses the first racer.  that timestamp is when you sample
                  ws3r"* / *"the missing piece that you need: the ws{any TF}e or x extremum is contained to the latest
                  target-side oob excursion"*: ws{TF}r at the crossing line's most extreme bar of its latest run at or
                  beyond 85 (HIGH) / 15 (LOW), clipped at the hunt's start (SAMPLE_AT 'excursion'). ws{TF}x race wins
                  sample too, one sequence with e's (SAMPLE_X). Lift-off's own e path keeps its walk back.
  void            HIS *"values from the counter side of 50 are void"*: such a sample is skipped; the next pairs with the
                  last valid one (VOID50).
  the row rule    HIS *"if there >=3 TFs printing a x or e cross in the same row, the under-lines test is automatically
                  qualified"* / *"ws1 to ws6, and >=2 TFs must print x and e in the same row"* (ROWX).
  the x/e path    HIS *"the pre x/e cross sample is the extremum and the test for AW(inf) follows the existing flow"*:
                  an X and an E race win of the line in one ws1 bar, where no pair fired on the later one; the
                  extremum is the latest natural lift-off pivot stamped inside the hunt before the earlier one;
                  in-fence, not void, the under-lines test or the row rule; AW from the later cross (XE_PATH).

MINE, each one flagged here and in the report:
    - an extremum is superseded by going STRICTLY past it (knob SUPERSEDE 'strict'). Equal is not past: under
      9B the second sample can be the stored extremum itself, and 'inclusive' would end the AW on the bar it starts.
    - once superseded, an extremum is retired: the line reads TO until a newer one is stored. His answer 6
      sets the extremum by a reversal, so nothing else replaces it.
    - a newer scenario-2 pair that qualifies while the line is already AW replaces the stored extremum.
    - a reversal votes only when its pivot is inside the trade (at or after the open) - the existing
      detector's own span, [the trade's open, the bar].
    - two race lines crossed on the same bar are one sample; the race re-opens when e crosses back over
      either of them.
    - the sample's in-fence test is its own value: not ex-20/80 on the target side.
    - a line with no emerging r value at the bar (each line's warm-up) has no read.

NOT USED: `fdm2-rline-enhance` - his pin, *"I think no, but I'm pinning this here for possible testing.
Joe to decide if/when to test"*.

CAUSAL inside a trade: every read at bar b uses bars at or before b. THE TRADES THEMSELVES ARE NOT CAUSAL -
see the pseudo trade above.

usage:  python3 towards_away.py 2026-08-24 13:50 14:06     the per-minute states for that window, for Joe's eyes
"""
import io
import os
import sys
import time

os.environ.setdefault('LG_TAPE_END', '2026-10-05')
V4 = '/home/joe/thecodes/docs/octo-freedom/1022_v4'
sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, V4)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np

_cwd = os.getcwd()
os.chdir(V4)                                    # the tape is cwd-sensitive - every run prints its bar count
_e = sys.stderr
sys.stderr = io.StringIO()
try:
    import v4_knobs as K
    import v4_closed_prev as CP
    import v4_rcfg_sweep as RS
    import v4_sweep_pivots as SP
    import v4_backstop_trades as BT
    import v4_fdm2 as F2
    import v4_ws_e as WSE
    import v4_lift_e as LE
    import ln
    from optimus9.analysis import jig as JIG
finally:
    sys.stderr = _e
import ta_knobs as TK

KNOBS = TK.check()                              # BANKED 1109: an off-ruled run refuses here, before any work

TFS = list(range(TK.TF_LO, TK.TF_HI + 1))
NONE, TO, AW = 0, 1, 2                          # the state codes. NONE = no trade open, or no r value
R50 = {'emerging': 'EMR', 'closed_prev': 'CPR'}[TK.FLIP50_READ]   # the r read his flip at 50 uses
SIDE = {+1: 'HIGH', -1: 'LOW'}
assert TK.SUPERSEDE in ('strict', 'inclusive')
assert TK.SAMPLE_AT in ('walkback', 'excursion'), TK.SAMPLE_AT


#   THE e LINES live in v4_ws_e (the line cache, with its 1109 known-good control numbers), and the e-sample
#   method - the race and his walk back to look forward - in v4_lift_e, shared with lift-off. HIS 1110 4A:
#   *"one e-sample **method** everywhere"*.


def pseudo_trades():
    """The ws2Mage pivots and the pseudo trades they make. -> (pivots [(bar, side)], trades [(open, close, side)]).

    A pivot is per_tf's own: the most extreme close inside a sweep-pivots leg, low on a leg opened by a LOW
    cross. Legs overlap, so several pivots can share a side in a row - HIS *"there are multiple ws2Mage
    pivots per side"*. The LAST of each same-side run is the pseudo rev-trade signal.
    """
    close = BT.prices()[0]
    side_of = {}
    for o, z, s in SP.legs(TK.PIVOT_LINE):
        seg = close[o:z + 1]
        j = o + int(np.nanargmin(seg) if s < 0 else np.nanargmax(seg))
        side_of.setdefault(j, set()).add(-1 if s < 0 else +1)
    assert all(len(v) == 1 for v in side_of.values()), 'one bar is both a LOW and a HIGH pivot'
    piv = sorted((j, v.pop()) for j, v in side_of.items())
    sig = [piv[i] for i in range(len(piv)) if i + 1 == len(piv) or piv[i + 1][1] != piv[i][1]]
    trades = []
    for k, (b, s) in enumerate(sig):
        c = sig[k + 1][0] if k + 1 < len(sig) else ln.N
        trades.append((int(b), int(c), -int(s)))
    assert all(trades[k][2] != trades[k + 1][2] for k in range(len(trades) - 1)), 'two trades in a row share a side'
    return piv, trades


def load():
    """Every array the mech reads, once. -> dict."""
    E = RS.load((RS.K0, RS.R0, RS.S0))           # the emerging r lines, the same arrays the r-pred UI reads
    EMR = {t: np.asarray(E[t], float) for t in TFS}
    for t in TFS:                                # CONTROL: the stored ws r line, exactly
        assert np.array_equal(EMR[t], np.asarray(ln.line('ws%dr' % t), float), equal_nan=True), t
    CPR = {t: np.asarray(CP.series(EMR[t], t * 60), float) for t in TFS}
    EMM = {t: np.asarray(ln.line('ws%dMage' % t), float) for t in TFS}
    CPM = {t: np.asarray(CP.series(EMM[t], t * 60), float) for t in TFS}
    return dict(EMR=EMR, CPR=CPR, EMM=EMM, CPM=CPM, E=WSE.lines())


def exf_mask(LN, t, side):
    """The banked ex-20/80 reader at every bar. -> bool array. v4_fdm2.ex2080_line, vectorised."""
    e = K.side_edge(K.FDM_FNC_2080, side)
    mode = str(K.FDM_EXF_READ)
    with np.errstate(invalid='ignore'):
        cp = (LN['CPR'][t] >= e) if side > 0 else (LN['CPR'][t] <= e)
        em = (LN['EMR'][t] >= e) if side > 0 else (LN['EMR'][t] <= e)
    n = max(1, int(K.FDM_EXF_EM_BARS))
    c = np.concatenate([[0], np.cumsum(em, dtype=np.int64)])
    i = np.arange(len(em))
    win = (c[i + 1] - c[np.maximum(0, i - n + 1)]) > 0
    return {'either': cp | win, 'closed_prev': cp, 'emerging': win}[mode]


def vote(v, side):
    """Is an extremum's value ex-20/80 on `side`. -> bool (array in, array out)."""
    return F2.ex2080(np.asarray(v, float), side)


def lift_extrema(LN, t, side):
    """Lift-off's NATURAL target-side reversals on the emerging r. -> (stamps, pivots, values), stamp-ascending."""
    lp = JIG.lift_off_pivot(LN['EMR'][t], side, K.LIFT_PTS, K.gap_for(t), K.LIFT_TOL, K.LIFT_WOB)
    lb = sorted(lp)
    st = np.asarray([K.lift_stamp(int(b)) for b in lb], int)
    pv = np.asarray([lp[b] for b in lb], int)
    return st, pv, LN['EMR'][t][pv] if len(pv) else np.zeros(0)


def lift_extrema_e(LN, t, side):
    """Lift-off's e-CROSS reversals (his 1110 update) on the emerging r. -> (stamps, pivots, values).

    The pivot is his walk-back bar, so the value is *"the ws{TF}r value at that time"*. Empty when the
    lift-off e path is switched off (v4_lift_e LIFT_E_ON 0).
    """
    ep = LE.get(t, len(LN['EMR'][t]), side)
    ev = [] if ep is None else JIG.lift_off_e(LN['EMR'][t], side, K.LIFT_PTS, K.gap_for(t), K.LIFT_TOL,
                                             K.LIFT_WOB, ep)
    st = np.asarray([x[0] for x in ev], int)
    pv = np.asarray([x[1] for x in ev], int)
    return st, pv, LN['EMR'][t][pv] if len(pv) else np.zeros(0)


def beyond(seg, x, side):
    """Past `x` toward the target side, by SUPERSEDE: 'strict' past it, 'inclusive' at or past it. -> bool array."""
    with np.errstate(invalid='ignore'):
        if TK.SUPERSEDE == 'inclusive':
            return (seg >= x) if side > 0 else (seg <= x)
        return (seg > x) if side > 0 else (seg < x)


def first_past(r, a, z, x, side):
    """The first bar in [a, z) where r has gone past `x` toward the target side (SUPERSEDE), else z."""
    g = np.flatnonzero(beyond(r[a:z], x, side))
    return a + int(g[0]) if g.size else z


def first_back50(r50, a, z, side):
    """HIS 1110 FLIP AT 50: the first bar in [a, z) where r is back on the target side of FLIP50_LEVEL after a bar
    on the far side (above it on a LOW target-side, below it on a HIGH one), else z. A far-side bar at `a` itself
    counts - his answer, an AW that starts on the far side already counts. Strict both ways. z when FLIP50 is 0."""
    if not TK.FLIP50:
        return z
    seg, lv = r50[a:z], TK.FLIP50_LEVEL
    with np.errstate(invalid='ignore'):
        f = np.flatnonzero(seg > lv if side < 0 else seg < lv)
        if not f.size:
            return z
        g = np.flatnonzero(seg[f[0] + 1:] < lv if side < 0 else seg[f[0] + 1:] > lv)
    return a + int(f[0]) + 1 + int(g[0]) if g.size else z


def hunts(r50, o, c, s):
    """HIS 1112 THE 50 RESET: the trade's hunts. -> [(start, end)], bar order.

    A pass is a bar strictly on the counter side of FLIP50_LEVEL (under it on a HIGH target-side) whose bar before is
    not. It ends the hunt it falls in and nulls that hunt's ex-20/80 reach. The first bar strictly back on the target
    side after it starts a fresh hunt - his *"so it starts hunting for an infence extremum while its trying to reach
    exfence"*. The bars between are no hunt. The trade's open always starts the first hunt, wherever r is - his
    *"the mech says that all lines are reset to TO when a trade opens"*. One hunt, [o, c), when RESET50 is 0.
    """
    if not TK.RESET50:
        return [(o, c)]
    lv = TK.FLIP50_LEVEL
    seg = r50[o:c]
    with np.errstate(invalid='ignore'):
        far = (seg > lv) if s < 0 else (seg < lv)
        near = (seg < lv) if s < 0 else (seg > lv)
    P = np.flatnonzero(far[1:] & ~far[:-1]) + 1                   # the passes, as offsets from o
    Q = np.flatnonzero(near)                                       # the target-side bars
    out, a = [], 0
    while True:
        k = int(np.searchsorted(P, a, side='right'))
        if k == len(P):
            out.append((o + a, c))
            return out
        p = int(P[k])
        out.append((o + a, o + p))
        m = int(np.searchsorted(Q, p, side='right'))
        if m == len(Q):
            return out
        a = int(Q[m])


def oob_runs(line, side):
    """The crossing line's target-side oob runs, for excursion_peak. -> (last oob bar at or before each bar, or -1;
    the first bar of the run each oob bar sits in). At or beyond OOB_HI on a HIGH side, OOB_LO on a LOW one."""
    with np.errstate(invalid='ignore'):
        oob = (line >= K.OOB_HI) if side > 0 else (line <= K.OOB_LO)
    idx = np.arange(len(line))
    last = np.maximum.accumulate(np.where(oob, idx, -1))
    start = oob & ~np.concatenate([[False], oob[:-1]])
    return last, np.maximum.accumulate(np.where(start, idx, -1))


def excursion_peak(line, runs, a, b, side):
    """HIS 1112 *"the missing piece that you need: the ws{any TF}e or x extremum is contained to the latest target-side
    oob excursion"*. -> the bar of the line's most extreme value in its latest oob run that has a bar in [a, b], clipped
    at a (his answer: an excursion before the hunt's start gives nothing), or None. The first bar on a tie."""
    last, first = runs
    z = int(last[b])
    if z < a:
        return None
    st = max(int(first[z]), a)
    seg = line[st:z + 1]
    return st + int(np.nanargmax(seg) if side > 0 else np.nanargmin(seg))


def void50(v, side):
    """HIS 1112 *"values from the counter side of 50 are void"*: strictly on the counter side of FLIP50_LEVEL. -> bool.
    Never void when VOID50 is 0."""
    if not TK.VOID50 or not np.isfinite(v):
        return False
    return v < TK.FLIP50_LEVEL if side > 0 else v > TK.FLIP50_LEVEL


def row_rule(LN):
    """HIS 1112 THE ROW RULE, ready to ask. -> f(b, side) -> (qualifies, TFs crossing, TFs with X and E), or None
    when ROWX is 0.

    *"if there >=3 TFs printing a x or e cross in the same row, the under-lines test is automatically qualified"* /
    *"ws1 to ws6, and >=2 TFs must print x and e in the same row"*. PRINTING is the web UI's cross row: ws{TF}e and
    ws{TF}x race wins over the whole tape, on the row's target-side. The row is the ws1 bar holding b, and only its
    crosses at or before b count - a later cross in the row has not printed on bar b.
    """
    if not TK.ROWX:
        return None
    TS = np.asarray(ln.ts, np.int64)
    first = np.flatnonzero((TS % 60000) == 0)
    cum = {}
    for t in range(TK.ROWX_TF_LO, TK.ROWX_TF_HI + 1):
        for s in (-1, +1):
            race = LE.race(t, s)
            for lab, line in (('X', np.asarray(ln.line('ws%dx' % t), float)), ('E', LN['E'][t])):
                hit = np.zeros(ln.N, np.int32)
                hit[[b for b, _ in JIG.e_race_wins(line, race, s)]] = 1
                cum[(t, s, lab)] = np.concatenate([[0], np.cumsum(hit)])

    def ask(b, s):
        k = int(np.searchsorted(first, b, side='right')) - 1
        a = int(first[k]) if k >= 0 else 0
        n_any = n_both = 0
        for t in range(TK.ROWX_TF_LO, TK.ROWX_TF_HI + 1):
            hx = cum[(t, s, 'X')][b + 1] > cum[(t, s, 'X')][a]
            he = cum[(t, s, 'E')][b + 1] > cum[(t, s, 'E')][a]
            n_any += hx or he
            n_both += hx and he
        return n_any >= TK.ROWX_MIN and n_both >= TK.ROWX_BOTH, n_any, n_both
    return ask


def run(LN, trades):
    """The mech over the whole tape. -> (STATE {tf: int8 array}, detail).

    detail['reach'][t][k]   the bar ws{t}r first reached ex-20/80 in trade k, or the trade's close if it never did
    detail['hunts'][t][k]   HIS 1112 the trade's hunts: [(start, end, reach)] - reach is None when the hunt ended
                            without one (a pass to the counter side of 50, or the close)
    detail['s1'][t][k]      scenario 1's voting extrema: [(stamp, pivot, value, 'lift'|'e', stored?)]
    detail['samples'][t][k] the samples: [(cross bar, ws{t}r sample, race line(s), sample bar, 'E'|'X', hunt, void?)]
    detail['s2'][t][k]      scenario 2's triggers: [(bar, extremum, the AW lines under, AW to, 'pair'|'xe', row rule)]
    """
    N = ln.N
    AW1 = {t: np.zeros(N, bool) for t in TFS}
    det = {k: {t: {} for t in TFS} for k in ('reach', 'hunts', 's1', 'samples', 's2')}
    det['ties'] = 0
    EXF = {(t, s): exf_mask(LN, t, s) for t in TFS for s in (-1, +1)}
    LIFT = {(t, s): lift_extrema(LN, t, s) for t in TFS for s in (-1, +1)}
    LIFTE = {(t, s): lift_extrema_e(LN, t, s) for t in TFS for s in (-1, +1)}
    ROW = row_rule(LN)
    more = lambda v, x, s: (v > x) if s > 0 else (v < x)          # v more extreme than x on side s
    #   scenario 1, every line first - scenario 2 reads the lines under it
    for t in TFS:
        r, r50 = LN['EMR'][t], LN[R50][t]
        end = lambda a, z, x, s: min(first_past(r, a, z, x, s), first_back50(r50, a, z, s))
        for k, (o, c, s) in enumerate(trades):
            #   HIS 1112 THE 50 RESET: each hunt has its own ex-20/80 reach; a pass to the counter side nulls it
            H = []
            for a, z in hunts(r50, o, c, s):
                f = np.flatnonzero(EXF[(t, s)][a:z])
                H.append((a, z, a + int(f[0]) if f.size else None))
            det['hunts'][t][k] = H
            det['reach'][t][k] = next((h[2] for h in H if h[2] is not None), c)
            ev = []
            for kind, (st, pv, val) in (('lift', LIFT[(t, s)]), ('e', LIFTE[(t, s)])):
                for i in range(np.searchsorted(st, o), np.searchsorted(st, c)):
                    #   HIS "no vote" (and 1110 5A for the e path): only an ex-20/80 extremum votes. It is stored only
                    #   while its hunt has reached ex-20/80, and its pivot is inside that hunt - HIS 1112, a value from
                    #   before the return over 50 is wiped
                    h = next((h for h in H if h[0] <= st[i] < h[1]), None)
                    if h is None or pv[i] < h[0] or not bool(vote(val[i], s)):
                        continue
                    assert h[2] is not None and st[i] >= h[2], 'a voting extremum stamped before its line reached ex-20/80'
                    ev.append((int(st[i]), 0 if kind == 'lift' else 1, int(pv[i]), float(val[i]), kind))
            ev.sort()
            out, cur, seg = [], None, None
            for a, _, p, x, kind in ev:
                if cur is not None:
                    z = end(seg, a, cur, s)
                    AW1[t][seg:z] = True
                    if z < a:
                        cur = None                          # passed, or flipped at 50: retired, TO until a newer one is stored
                #   a natural reversal replaces it ("latest"); an e reversal only when MORE extreme than the
                #   stored one, or when none is stored - HIS 1110 3B
                take = kind == 'lift' or cur is None or more(x, cur, s)
                if take:
                    cur, seg = x, a
                elif cur is not None:
                    seg = a
                out.append((a, p, x, kind, take))
            if cur is not None:
                z = end(seg, c, cur, s)
                AW1[t][seg:z] = True
            det['s1'][t][k] = out
    TS = np.asarray(ln.ts, np.int64)
    first = np.flatnonzero((TS % 60000) == 0)                      # the ws1 bars - the web UI's rows
    STATE = {}
    for t in TFS:
        r, r50 = LN['EMR'][t], LN[R50][t]
        under = [u for u in range(max(TK.TF_LO, t - TK.UNDER), t)]
        lines = {'E': LN['E'][t]}
        if TK.SAMPLE_X:
            lines['X'] = np.asarray(ln.line('ws%dx' % t), float)
        AW2 = np.zeros(N, bool)
        for s in (-1, +1):
            race = LE.race(t, s)
            prep = {lab: JIG.e_race_prep(line, race, s) for lab, line in lines.items()}
            runs = {lab: oob_runs(line, s) for lab, line in lines.items()} if TK.SAMPLE_AT == 'excursion' else None
            lst, lpv, lval = LIFT[(t, s)]

            def under_test(b):
                """The existing >1 of the 5 lines under reading AW, or HIS 1112 row rule. -> (passes, AW lines, row)."""
                aw = [u for u in under if AW1[u][b]]
                rw = ROW(b, s) if ROW is not None else (False, 0, 0)
                return len(aw) > TK.UNDER_GT or rw[0], aw, rw[0]

            for k, (o, c, ts) in enumerate(trades):
                if ts != s:
                    continue
                smp, trig = [], []
                for hi, (ha, hz, hr) in enumerate(det['hunts'][t][k]):
                    zz = hr if hr is not None else hz                  # the hunt samples until its reach
                    #   HIS 1110 4A / 1112: each race win of the hunt's own race - it starts open at the hunt's start -
                    #   is a sample. X before E on one bar, the cross row's order
                    hs = []
                    for lab, line in lines.items():
                        for b, hit in JIG.e_race_wins(line, race, s, a=ha, z=zz, prep=prep[lab]):
                            det['ties'] += len(hit) > 1
                            if TK.SAMPLE_AT == 'excursion':
                                w = excursion_peak(line, runs[lab], ha, b, s)
                            else:
                                w = JIG.e_walk_back(line, b, s, TK.E_STEP)
                            v = float(r[w]) if w is not None else float('nan')
                            hs.append((int(b), v, '+'.join(race[n][0] for n in hit), w, lab, hi, void50(v, s)))
                    hs.sort(key=lambda x: (x[0], x[4] != 'X'))
                    smp += hs
                    #   the pairs: each valid sample with the last valid one before it in this hunt (void skipped)
                    ok = [x for x in hs if not x[6]]
                    tb = set()
                    for i in range(1, len(ok)):
                        (b, v, _, _, _, _, _), (_, vp, _, _, _, _, _) = ok[i], ok[i - 1]
                        if not (np.isfinite(v) and np.isfinite(vp)) or vote(v, s) or vote(vp, s):
                            continue
                        if abs(v - vp) > TK.PAIR_PTS:
                            continue
                        good, aw, rw = under_test(b)
                        if good:
                            trig.append([b, min(v, vp) if s < 0 else max(v, vp), aw, 'pair', rw, hi])
                            tb.add(b)
                    #   HIS 1112 THE x AND e PATH: an X and an E in one ws1 bar, at the later of the two; the extremum is
                    #   the latest natural lift-off pivot stamped inside this hunt before the earlier one. Only where no
                    #   pair fired on that bar - his "if this occurs"
                    if TK.XE_PATH and TK.SAMPLE_X:
                        rows = {}
                        for x in hs:
                            rk = int(np.searchsorted(first, x[0], side='right')) - 1
                            rows.setdefault(rk, {}).setdefault(x[4], x[0])
                        for rk in sorted(rows):
                            if len(rows[rk]) < 2:
                                continue
                            b1, b2 = min(rows[rk].values()), max(rows[rk].values())
                            if b2 in tb:
                                continue
                            i = int(np.searchsorted(lst, b1)) - 1           # the latest stamp before b1
                            while i >= 0 and lpv[i] < ha:
                                i -= 1
                            if i < 0 or lst[i] < ha:
                                continue
                            v = float(lval[i])
                            if not np.isfinite(v) or vote(v, s) or void50(v, s):
                                continue
                            good, aw, rw = under_test(b2)
                            if good:
                                trig.append([b2, v, aw, 'xe', rw, hi])
                det['samples'][t][k] = smp
                #   each trigger's AW runs to the next trigger, its hunt's reach, or the close - and ends sooner on
                #   going past its extremum or the flip at 50
                trig.sort(key=lambda g: g[0])
                lim = {hi: (hr if hr is not None else c) for hi, (_, _, hr) in enumerate(det['hunts'][t][k])}
                rows = []
                for i, g in enumerate(trig):
                    nxt = min(trig[i + 1][0] if i + 1 < len(trig) else c, lim[g[5]])
                    z = min(first_past(r, g[0], nxt, g[1], s), first_back50(r50, g[0], nxt, s))
                    AW2[g[0]:z] = True
                    rows.append((g[0], g[1], g[2], z, g[3], g[4]))
                det['s2'][t][k] = rows
        st = np.zeros(N, np.int8)
        for k, (o, c, s) in enumerate(trades):
            st[o:c] = TO
        st[(st == TO) & (AW1[t] | AW2)] = AW
        st[~np.isfinite(r)] = NONE
        #   HIS 1109 *"at the start of a trade, an r line is automatically tagged as towards"*, and 1110 *"make sure
        #   the update doesn't impact the "all lines start with TO at the beginning of a trade""*
        assert not any(st[o] == AW for o, c, s in trades), ('a line reads AW on a trade\'s open bar', t)
        STATE[t] = st
    return STATE, det

def build():
    """-> (LN, pivots, trades, STATE, detail), with the controls run."""
    LN = load()
    piv, trades = pseudo_trades()
    rng = np.random.default_rng(1109)            # CONTROL: the vectorised reader against v4_fdm2's own
    for t in (4, 11, 30):
        for s in (-1, +1):
            m = exf_mask(LN, t, s)
            for b in rng.integers(0, ln.N, 400):
                assert bool(m[b]) == F2.ex2080_line(LN, t, int(b), s), ('ex-20/80 reader differs', t, s, b)
    STATE, det = run(LN, trades)
    return LN, piv, trades, STATE, det


def trade_at(trades, bar):
    """The index of the trade open at `bar`, or None."""
    o = np.asarray([x[0] for x in trades])
    k = int(np.searchsorted(o, bar, side='right')) - 1
    return k if k >= 0 and bar < trades[k][1] else None


if __name__ == '__main__':
    T0 = time.time()
    print('bars %d, %s .. %s' % (ln.N, ln.U(0), ln.U(ln.N - 1)))
    print('knobs ' + ' '.join('%s=%s' % kv for kv in TK.live()))
    LN, piv, trades, STATE, det = build()
    print('pivots %d, pseudo trades %d, ties %d, built in %.1f s' % (len(piv), len(trades), det['ties'], time.time() - T0))
    if len(sys.argv) >= 4:
        a, z = ln.K(sys.argv[1] + ' ' + sys.argv[2] + ':00'), ln.K(sys.argv[1] + ' ' + sys.argv[3] + ':00')
        k = trade_at(trades, a)
        o, c, s = trades[k]
        print('trade %s .. %s, target-side %s' % (ln.U(o), ln.U(c), SIDE[s]))
        print('| row | ' + ' | '.join('ws%d' % t for t in TFS) + ' |')
        for b in range(a, z + 1, 12):
            print('| %s | ' % ln.U(b) + ' | '.join('%s %.1f' % ({TO: 'TO', AW: 'AW', NONE: '-'}[int(STATE[t][b])], LN['EMR'][t][b])
                                                   for t in TFS) + ' |')
        for t in TFS:
            print('ws%dr reach %s' % (t, ln.U(det['reach'][t][k]) if det['reach'][t][k] < c else 'never'))
            for x in det['s1'][t][k]:
                print('   s1 %s stamp %s pivot %s %.2f %s' % (x[3], ln.U(x[0]), ln.U(x[1]), x[2],
                                                          'stored' if x[4] else 'not more extreme - not stored'))
            for x in det['samples'][t][k]:
                print('   sample %s %.2f %s walk-back %s' % (ln.U(x[0]), x[1], x[2], ln.U(x[3]) if x[3] is not None else '-'))
            for x in det['s2'][t][k]:
                print('   s2 trigger %s extremum %.2f under-AW %s AW to %s'
                      % (ln.U(x[0]), x[1], ','.join('ws%d' % u for u in x[2]), ln.U(min(x[3], ln.N - 1))))
