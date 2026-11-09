"""THE NEW towards/away mech, Joe 1109. -> for each r line ws4..ws30, at each 5 s bar: TO, AW or no read.

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

  ws{TF}e         BB%B len 3, mult 0.5, src close, emerging, ws4..ws30, from its row in the dynamic config
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
  e-samples       ws{TF}e crossing race:{boundary, ws{TF}Mage, ws{TF}r} - under 85 / Mage / r on a HIGH
                  target-side, over 15 / Mage / r on a LOW one. r and Mage are closed-prev (RACE_READ), e is
                  emerging.
                  HIS 3A: no hold - the sample is ws{TF}r's emerging value on the cross bar. HIS 4B: only the
                  first of the three counts; the race re-opens once e crosses back over that same line the
                  other way. Each trade's race starts open.
  scenario 2      the line has not reached ex-20/80. *"if a ws{TF}r line prints two infence samples (built
                  by the e-cross sampling) which are within 2% of each other"* - HIS 7A: the latest two
                  samples this trade, within PAIR_PTS 2.0 r-points - and *"IF there are >1 r lines within
                  {knob:5} TFs **under** this TF, that are printing away while in ex-fence, or printing away
                  after having left ex-fence (during this trade)"* - those are scenario-1 lines reading AW.
                  HIS 8A: tested on the bar of the second sample only. HIS 9B: the stored extremum is the more
                  target-side of the two samples. The line is AW from that bar and stays so while it has not
                  gone past the extremum (*"the same logic as the existing build"*).

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
    import ln
    from optimus9.analysis import jig as JIG
    from optimus9.analysis.jig import Jig
    from optimus9.compute.line_config import override, mech_lines
    from optimus9.orchestration.build_ws_lines import HOURS, WARMUP
    from optimus9.orchestration import rpl_cache as RC
    from optimus9.config import get_db_config
    from optimus9 import DatabaseManager
finally:
    sys.stderr = _e
import ta_knobs as TK

KNOBS = TK.check()                              # BANKED 1109: an off-ruled run refuses here, before any work

TFS = list(range(TK.TF_LO, TK.TF_HI + 1))
NONE, TO, AW = 0, 1, 2                          # the state codes. NONE = no trade open, or no r value
SIDE = {+1: 'HIGH', -1: 'LOW'}
RACE = TK.RACE                                  # his race:{boundary,Mage,r}
assert set(RACE) <= {'boundary', 'Mage', 'r'} and RACE, 'RACE names a line the race does not know: %r' % (RACE,)
assert TK.RACE_READ in ('closed_prev', 'emerging') and TK.SUPERSEDE in ('strict', 'inclusive')


#   THE e LINES ARE IN THE LINE CACHE, HIS 1109 *"update the cache"*. Keyed by spec like every cached line,
#   so a missing one is built and nothing already there is touched. 1109: 27 new files, 0 existing files
#   changed, every cached array equal to the in-memory build (max diff 0, NaN positions equal).
#   CONTROL, the known-good numbers from that check - a hash-keyed cache can serve a real but wrong array:
E_CONTROL_SUM = 2174735698.786861        # nansum over ws4e..ws30e, whole tape
E_CONTROL_AT = ('2026-08-25 03:28:00', 30, 99.629759)    # ws30e at that bar


def _e_ovr():
    """ws4e..ws30e overrides from the dynamic config table. -> {name: override}."""
    _s = sys.stderr; sys.stderr = io.StringIO()
    db = DatabaseManager(**get_db_config()); db.connect()
    rows = mech_lines(db, TK.E_MECH, version=TK.E_VERSION)
    db.disconnect(); sys.stderr = _s
    ovr = {}
    for d in rows:
        assert d['role'] == 'e' and d['tf_seconds'] % 60 == 0, d
        ovr['ws%de' % (d['tf_seconds'] // 60)] = d['override']
    assert sorted(int(k[2:-1]) for k in ovr) == TFS, 'the config table row does not cover ws%d..ws%d' % (TFS[0], TFS[-1])
    return ovr


def e_cached():
    """ws4e..ws30e from the LINE CACHE, building only a missing one. -> {tf: array}."""
    ovr = _e_ovr()
    pxs = {'src': ln._sy['s'], 'len': ln._sy['l']}
    assert os.path.exists(os.path.join(RC.TAPE_DIR, RC._tape_key(ln.EM, HOURS, WARMUP, pxs) + '.npz')), \
        'the tape file is missing - the cache call would write a new one'
    C = RC.cache_jig_perline(ln.EM, HOURS, WARMUP, ovr, pxs_cfg=pxs)
    out = {int(n[2:-1]): np.asarray(C.W.line(n), float)[:ln.N] for n in ovr}
    s = sum(float(np.nansum(out[t])) for t in TFS)
    when, tf, v = E_CONTROL_AT
    assert abs(s - E_CONTROL_SUM) <= 1e-9 * abs(E_CONTROL_SUM) and abs(out[tf][ln.K(when)] - v) < 1e-6, \
        'the cached e lines differ from the 1109 known-good numbers (%.6f, %.6f)' % (s, out[tf][ln.K(when)])
    return out


def e_lines():
    """ws4e..ws30e built IN MEMORY, with a ws30Mage control row. -> {tf: array}. The cache check's reference."""
    ovr = _e_ovr()
    ovr['ws30Mage_control'] = override(1800, ln.SPEC['Mage'][0], 'emerging')
    with Jig(ln.EM, hours=HOURS, warmup=WARMUP, overrides=ovr) as j:
        assert len(j.ts) >= ln.N and (np.asarray(j.ts, np.int64)[:ln.N] == ln.ts).all(), 'the e grid is off the tape'
        got = {n: np.asarray(j.W.line(n), float)[:ln.N] for n in ovr}
    c, ref = got.pop('ws30Mage_control'), np.asarray(ln.line('ws30Mage'), float)
    assert (np.isnan(c) == np.isnan(ref)).all() and np.nanmax(np.abs(c - ref)) == 0.0, \
        'the ws30Mage control row does not match the cached ws30Mage - the e lines cannot be trusted'
    return {t: got['ws%de' % t] for t in TFS}


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
    return dict(EMR=EMR, CPR=CPR, EMM=EMM, CPM=CPM, E=e_cached())


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
    """Lift-off's target-side reversals on the emerging r. -> (stamps, pivots, values), stamp-ascending."""
    lp = JIG.lift_off_pivot(LN['EMR'][t], side, K.LIFT_PTS, K.gap_for(t), K.LIFT_TOL, K.LIFT_WOB)
    lb = sorted(lp)
    st = np.asarray([K.lift_stamp(int(b)) for b in lb], int)
    pv = np.asarray([lp[b] for b in lb], int)
    return st, pv, LN['EMR'][t][pv] if len(pv) else np.zeros(0)


def race_crosses(e, X, side):
    """ws{TF}e against one race line. -> (forward, back) bool arrays: the target-side cross, and the cross back."""
    a, b, oa, ob = e[:-1], e[1:], X[:-1], X[1:]
    fin = np.isfinite(a) & np.isfinite(b) & np.isfinite(oa) & np.isfinite(ob)
    with np.errstate(invalid='ignore'):
        if side > 0:                             # HIGH target-side: e crosses UNDER
            fw, bk = (a >= oa) & (b < ob), (a <= oa) & (b > ob)
        else:                                    # LOW target-side: e crosses OVER
            fw, bk = (a <= oa) & (b > ob), (a >= oa) & (b < ob)
    pad = np.zeros(1, bool)
    return np.concatenate([pad, fw & fin]), np.concatenate([pad, bk & fin])


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


def run(LN, trades):
    """The mech over the whole tape. -> (STATE {tf: int8 array}, detail).

    detail['reach'][t][k]   the bar ws{t}r reached ex-20/80 in trade k, or the trade's close if it never did
    detail['s1'][t][k]      scenario 1's voting extrema: [(stamp, pivot, value, AW to)]
    detail['samples'][t][k] the e-samples: [(bar, value, the race line(s) crossed)]
    detail['s2'][t][k]      scenario 2's triggers: [(bar, extremum, the AW lines under, AW to)]
    """
    N = ln.N
    AW1 = {t: np.zeros(N, bool) for t in TFS}
    det = {k: {t: {} for t in TFS} for k in ('reach', 's1', 'samples', 's2')}
    det['ties'] = 0
    EXF = {(t, s): exf_mask(LN, t, s) for t in TFS for s in (-1, +1)}
    LIFT = {(t, s): lift_extrema(LN, t, s) for t in TFS for s in (-1, +1)}
    #   scenario 1, every line first - scenario 2 reads the lines under it
    for t in TFS:
        r = LN['EMR'][t]
        for k, (o, c, s) in enumerate(trades):
            f = np.flatnonzero(EXF[(t, s)][o:c])
            reach = o + int(f[0]) if f.size else c
            det['reach'][t][k] = reach
            st, pv, val = LIFT[(t, s)]
            i0, i1 = np.searchsorted(st, o), np.searchsorted(st, c)
            ev = [(int(st[i]), int(pv[i]), float(val[i])) for i in range(i0, i1)
                  if pv[i] >= o and bool(vote(val[i], s))]
            out = []
            for i, (a, p, x) in enumerate(ev):
                assert a >= reach, 'a voting extremum stamped before its line reached ex-20/80'
                end = ev[i + 1][0] if i + 1 < len(ev) else c
                z = first_past(r, a, end, x, s)
                AW1[t][a:z] = True
                out.append((a, p, x, z))
            det['s1'][t][k] = out
    STATE = {}
    for t in TFS:
        r, e = LN['EMR'][t], LN['E'][t]
        under = [u for u in range(max(TK.TF_LO, t - TK.UNDER), t)]
        AW2 = np.zeros(N, bool)
        for s in (-1, +1):
            edge = np.full(N, K.OOB_HI if s > 0 else K.OOB_LO, float)
            cp = TK.RACE_READ == 'closed_prev'
            line_of = {'boundary': edge, 'Mage': LN['CPM' if cp else 'EMM'][t], 'r': LN['CPR' if cp else 'EMR'][t]}
            FB = [race_crosses(e, line_of[nm], s) for nm in RACE]
            FW, BK = [f for f, _ in FB], [b for _, b in FB]
            evb = np.flatnonzero(np.any(FW, 0) | np.any(BK, 0))
            for k, (o, c, ts) in enumerate(trades):
                if ts != s:
                    continue
                reach = det['reach'][t][k]
                is_open, win, smp = True, (), []
                for b in evb[np.searchsorted(evb, o):np.searchsorted(evb, reach)]:
                    if is_open:
                        hit = tuple(n for n in range(len(RACE)) if FW[n][b])
                        if hit:
                            det['ties'] += len(hit) > 1
                            smp.append((int(b), float(r[b]), '+'.join(RACE[n] for n in hit)))
                            win, is_open = hit, False
                    elif any(BK[n][b] for n in win):
                        is_open = True
                det['samples'][t][k] = smp
                trig = []
                for i in range(1, len(smp)):
                    (b, v, _), (_, vp, _) = smp[i], smp[i - 1]
                    if not (np.isfinite(v) and np.isfinite(vp)) or vote(v, s) or vote(vp, s):
                        continue
                    if abs(v - vp) > TK.PAIR_PTS:
                        continue
                    aw = [u for u in under if AW1[u][b]]
                    if len(aw) > TK.UNDER_GT:               # his ">1"
                        trig.append([b, min(v, vp) if s < 0 else max(v, vp), aw])
                for i, g in enumerate(trig):
                    end = trig[i + 1][0] if i + 1 < len(trig) else reach
                    z = first_past(r, g[0], end, g[1], s)
                    AW2[g[0]:z] = True
                    g.append(z)
                det['s2'][t][k] = [tuple(g) for g in trig]
        st = np.zeros(N, np.int8)
        for k, (o, c, s) in enumerate(trades):
            st[o:c] = TO
        st[(st == TO) & (AW1[t] | AW2)] = AW
        st[~np.isfinite(r)] = NONE
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
                print('   s1 stamp %s pivot %s %.2f AW to %s' % (ln.U(x[0]), ln.U(x[1]), x[2], ln.U(min(x[3], ln.N - 1))))
            for x in det['samples'][t][k]:
                print('   sample %s %.2f %s' % (ln.U(x[0]), x[1], x[2]))
            for x in det['s2'][t][k]:
                print('   s2 trigger %s extremum %.2f under-AW %s AW to %s'
                      % (ln.U(x[0]), x[1], ','.join('ws%d' % u for u in x[2]), ln.U(min(x[3], ln.N - 1))))
