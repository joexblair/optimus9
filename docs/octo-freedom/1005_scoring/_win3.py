"""THE `dev-cache`. 1016. JOE NAMED IT: *"when I need this rebuilt for another window,
I'll refer to it as our `dev-cache`"*.

A WINDOW CACHE. Joe: *"I'll be asking a lot of questions about the data. is it
possible to cache all of the "moving parts" in the 3 day window?"*

WHY: every question currently costs a ~250 s `machine` build plus a 94-day walk. This banks one
window's arrays and derived state to a single npz so a question is an array lookup.

THE TRAP, AND HOW THIS AVOIDS IT. The lines MUST be built on the FULL tape and then SLICED. Building
them on a 3-day tape gives every line a different warmup and silently different values - the same
class of fault as the cwd-sensitive tape (score39 resolves a shorter tape outside this directory)
and the 1008 hash-keyed cache that loaded real-but-wrong arrays. So: full build, then slice, and the
key carries the tape window and the banked knobs. A CONTROL VALUE is stored and checked on load; a
mismatch rebuilds rather than returns.

WHAT IS CACHED - EVERYTHING, not a chosen subset. Joe 1016: *"be as detailed as you can - use the
mechs to guide you"*. So the contents are driven by what each mech reads and emits, and every
intermediate is banked, not just the final events. Selecting a subset is where I would guess wrong
about the next question; the window is 51,840 bars so keeping it all costs nothing.

RAW, sliced from the full-tape build
    the grid            ts (ms), px, close
    the r ladder        ws1r .. ws30r
    the Mage ladder     ws1Mage .. ws30Mage, plus g5Mage, g15Mage, g30Mage
    the x ladder        ws1x .. ws30x
    the klines          kc_high, kc_low on the tape grid - NOT in the scoring tape, DB only
    the fences          oob 85/15, the ex-fence 83/17, the measured tick 0.000010

PER-LINE STATE, every timeframe, because a question about one line should not need a rebuild
    oob masks           per r and per Mage, at the oob fence AND the ex-fence
    reversal masks      `lr_v2._mage_rev` per Mage line - the mech only ever used ws5, but the
                        cascade questions reach for g15 to ws3
    ib-cross lists      `jig.oob_ib_cross` per r and per Mage, both fences, xwob 1 and 4.
                        Each row is (cross bar, confirmation bar, side) - the confirmation bar is
                        what makes it causal
    mom-true masks      ws5r .. ws15r with STRIP-MOM-AT-FENCE ON, both sides. This is the EXPENSIVE
                        read - 0.00015 to 0.00029 s per bar - and it is mom-xfer's own producer,
                        which is why it is banked even though Joe ruled that gate off

BOUNCE-PRED, the fixed grid - `_bouncepred.py`
    per ws5Mage reversal bar and per side: the verdict, known_at, the median second difference,
    the lines-positive count, AND THE 30-VALUE PER-LINE DIFF VECTOR. The vector is the raw material
    behind every verdict; without it a question about why a verdict landed needs a rebuild

THE BANKED GRID - `_bp_g15.py`
    per g15Mage ib-cross and per side: the verdict, known_at, median, lines positive, the pair's two
    bars, and the per-line diff vector. Banked for BOTH pairings (fwd and back) and BOTH side
    readings (ws5 and opp), so the ruled-out variants can still be questioned without a rebuild

THE CONJUNCTION - `_conj.py`
    per bar and per side: the strength, the members in span, the latched set, the patch verdict,
    and the gate state (is ws1Mage same-side oob, and whether the 4-bar slack admitted it)
    per fire: the member list, the patched flag, and `cross_for`'s answer - the x-cross bar, its
    confirmation bar, and whether the search ran backward or forward

LINEAGE - `_lineage_conf.py`
    the verdict per bar per side: carrying / exhausted / blocked, plus its sentence. It returns no
    bar, by design, so lineage cannot become an entry or an exit

PRICE STRUCTURE
    the swing pivots at the banked pct - the exit board
    per trade: MAE and MFE over the hold, and the price path extremes

THE WALK
    the octo2 event rows, the walk rows (THE CHAIN), the closed trades with source, exit_reason and
    MAE/MFE, what was open at the end, and every event the mom-xfer gate would have withheld

THE EVENT CAUSATION CHAIN - added 1016 after Joe's first test of this cache: *"I need to see the
timestamped events that created 08-22 02:07 / if there's inadequate data in the cache to build the
table, add it now and uppdate the dev-cache spec"*. Every bar was reachable but only as TEXT inside
the event note, so a causation question needed a regex. `event_chain` holds them as fields:
    bar / side / source
    fire_bar        the conjunction fire, None on the ws5Mage-oob path
    xcross          the x-cross bar, xcross_conf the bar it was CONFIRMED, xcross_dir back/forward
    hold_from       the bar bounce-pred's hold started from, None if unheld
    reversal_bar    the sample bar the passing verdict was measured at
    lookahead_bars  the event bar MINUS the fire bar. NEGATIVE means the event is stamped before
                    the information that produced it - the first test of this cache found one

THE GATE SLACK DETAIL - `conj_gate_slack_bar_dr+1` / `dr-1` give WHICH bar inside the 4-bar slack
was same-side oob, or -1 if none. The gate bool alone could not answer that

THE CONTROL
    the window's px sum and the octo2 event count, re-checked on every load. A mismatch REBUILDS
    rather than returning real-but-wrong arrays - that is the 1008 fault this guards

SRP: this file banks and loads a window. It computes no mech of its own - every derived array comes
from the module that owns it.
"""
import hashlib
import json
import os

import numpy as np

CACHE = os.environ.get('W_WIN3_CACHE', '/home/joe/.claude/jobs/6eb9931e/tmp/win3')


def key(a, b, knobs):
    """The cache key. Carries the window AND the banked knob values, so a knob change rebuilds."""
    h = hashlib.sha1(json.dumps({'a': int(a), 'b': int(b), 'k': knobs},
                                sort_keys=True).encode()).hexdigest()[:20]
    return h


def build(sc, o, a, b, kl_hi=None, kl_lo=None, log=print, run_leg=None,
          rl=None, bank=None, swing_pct=0.9, mom_tfs=tuple(range(5, 16))):
    """Slice the window out of a FULL-tape build and bank every mech's state. -> dict.

    `sc` is the full-tape score39 handle, `o` a built `octo2.Octo2`, `a`/`b` the window bars.
    `run_leg` is `_chain10.run_leg` - lineage needs it, and it is read ONLY at event bars because
    each call is a walk. `rl`/`bank` are `_chain10.RL`/`BANK` for the strip-ON mom-true reads.
    """
    import time
    import _bouncepred as BP
    import _bp_g15 as G15
    import _lineage_conf as LC
    from optimus9.analysis.jig import oob_ib_cross, mage_ladder_diff, mage_band_split
    from optimus9.analysis.lr_v2 import _mage_rev
    a, b = int(a), int(b)
    n = b - a + 1
    sl = slice(a, b + 1)
    T0 = time.time()
    P = lambda z: log('# [%5.0fs] %s' % (time.time() - T0, z))
    HI, LO = float(sc.HI), float(sc.LO)
    EXH, EXL = 83.0, 17.0
    d = {'a': a, 'b': b, 'n': n,
         'ts': np.asarray(sc.ts, np.int64)[sl],
         'px': np.asarray(sc.PX, float)[sl],
         'hi_fence': HI, 'lo_fence': LO, 'ex_hi': EXH, 'ex_lo': EXL, 'tick': 0.000010,
         'window_from': sc.U(a), 'window_to': sc.U(b), 'swing_pct': float(swing_pct)}
    if getattr(sc, 'CLOSE', None) is not None:
        d['close'] = np.asarray(sc.CLOSE, float)[sl]
    P('window %s .. %s = %d bars' % (sc.U(a), sc.U(b), n))

    # ---- RAW: the three ladders, full tape then sliced
    R = {}; MG = {}; X = {}
    for t in range(1, 31):
        R[t] = np.asarray(sc.LD(t * 60, 'r'), float)
        MG[t] = np.asarray(sc.LD(t * 60, 'Mage'), float)
        X[t] = np.asarray(sc.LD(t * 60, 'x'), float)
        d['ws%dr' % t] = R[t][sl]; d['ws%dMage' % t] = MG[t][sl]; d['ws%dx' % t] = X[t][sl]
    G = {}
    for sec in (5, 15, 30):
        G[sec] = np.asarray(sc.LD(sec, 'Mage'), float)
        d['g%dMage' % sec] = G[sec][sl]
    P('ladders sliced: ws1-ws30 r / Mage / x, plus g5 g15 g30 Mage')

    if kl_hi is not None:
        d['kc_high'] = np.asarray(kl_hi, float)[sl]
        d['kc_low'] = np.asarray(kl_lo, float)[sl]
        P('klines sliced onto the tape grid')

    # ---- PER-LINE STATE: oob masks, reversal masks, ib-cross lists
    for t in range(1, 31):
        for nm, arr in (('r', R[t]), ('Mage', MG[t])):
            d['ws%d%s_oob' % (t, nm)] = ((arr >= HI) | (arr <= LO))[sl]
            d['ws%d%s_exoob' % (t, nm)] = ((arr >= EXH) | (arr <= EXL))[sl]
        d['ws%dMage_rev' % t] = (_mage_rev(MG[t], int(sc.LG['rev_wob'])) != 0)[sl]
    for sec in (5, 15, 30):
        d['g%dMage_oob' % sec] = ((G[sec] >= HI) | (G[sec] <= LO))[sl]
        d['g%dMage_exoob' % sec] = ((G[sec] >= EXH) | (G[sec] <= EXL))[sl]
        d['g%dMage_rev' % sec] = (_mage_rev(G[sec], int(sc.LG['rev_wob'])) != 0)[sl]
    P('oob masks at both fences, and reversal masks, for every r / Mage / g line')

    def xlist(arr, fh, fl, xw):
        return np.array([(k - a, c - a, sd) for k, c, sd in oob_ib_cross(arr, fh, fl, xw)
                         if a <= k <= b and a <= c <= b], np.int64).reshape(-1, 3)
    for fn, fh, fl in (('oob', HI, LO), ('ex', EXH, EXL)):
        for xw in (1, 4):
            for t in range(1, 31):
                d['ws%dr_ib_%s_x%d' % (t, fn, xw)] = xlist(R[t], fh, fl, xw)
                d['ws%dMage_ib_%s_x%d' % (t, fn, xw)] = xlist(MG[t], fh, fl, xw)
            for sec in (5, 15, 30):
                d['g%dMage_ib_%s_x%d' % (sec, fn, xw)] = xlist(G[sec], fh, fl, xw)
    P('ib-cross lists: every r / Mage / g line x 2 fences x xwob 1 and 4')

    # ---- MOM-TRUE, STRIP ON. The expensive read, and mom-xfer's own producer.
    if rl is not None and bank is not None:
        import walk_mom_models as WM
        from optimus9.compute.momo_seam import seam_mask
        mfr = float(sc.LG['momo_fence_r']) if 'momo_fence_r' in sc.LG else 17.0
        FENCE = (mfr, 100.0 - mfr)
        for t in mom_tfs:
            sm = seam_mask(sc.ts, t)
            for dr in (+1, -1):
                m = np.zeros(n, bool)
                for i, j in enumerate(range(a, b + 1)):
                    m[i] = bool(WM.momentum_true(rl[t], bank[t], WM.WS1_CFG, dr, j, sm, t,
                                                 strip_mom_at_fence=FENCE)[0])
                d['ws%dr_momtrue_strip_dr%+d' % (t, dr)] = m
            P('mom-true strip ON: ws%dr both sides' % t)

    # ---- BOUNCE-PRED, the fixed grid, at every ws5Mage reversal, with the 30-line diff vector
    m5 = o.bp.trig
    oob5 = (m5 >= HI) | (m5 <= LO)
    d['ws5Mage_oob_entry'] = np.array(
        [j - a for j in range(a + 1, b + 1) if oob5[j] and not oob5[j - 1]], np.int64)
    d['ws5Mage_oob_entry_side'] = np.array(
        [1 if m5[j] >= HI else -1 for j in range(a + 1, b + 1)
         if oob5[j] and not oob5[j - 1]], np.int64)
    rows = []; vecs = []
    for j in range(a, b + 1):
        if o.bp.rev[j] == 0:
            continue
        for side in (+1, -1):
            r = o.bp.verdict(j, side)
            if r is None:
                continue
            v, ka, med, pos, _why = r
            aa, bb = BP.read_bars(j)
            _m, _p, dv = mage_ladder_diff(o.bp.mg, j, aa - j, bb - j, o.bp.tfs)
            rows.append((j - a, side, 1 if v == BP.CONTINUANCE else 0, ka - a, med, pos))
            vecs.append(dv)
    d['bp_fixed'] = np.array(rows, float).reshape(-1, 6)
    d['bp_fixed_diffvec'] = np.array(vecs, float).reshape(-1, len(o.bp.tfs))
    d['bp_ladder_tfs'] = np.array(o.bp.tfs, np.int64)
    P('bounce-pred fixed grid: %d verdicts, each with its %d-line diff vector'
      % (len(rows), len(o.bp.tfs)))

    # ---- THE BANKED GRID, both pairings and both side readings, so the ruled-out ones stay askable
    for side_m in ('ws5', 'opp'):
        for pair_m in ('fwd', 'back'):
            G15.SIDE, G15.PAIR = side_m, pair_m
            h = G15.BouncePredG15(sc, bp=o.bp)
            rr = []; vv = []
            for side in (+1, -1):
                xs = h.cross[h.sample_side(side)]
                for i, (k, c) in enumerate(xs):
                    if not (a <= k <= b):
                        continue
                    res = h.verdict_at(i, side)
                    if res is None:
                        continue
                    cb, v, ka, med, pos, _w = res
                    j2 = i + G15.STEP if pair_m == 'fwd' else i - G15.STEP
                    ka2 = xs[j2][0]
                    _m, _p, dv = mage_ladder_diff(h.mg, min(cb, ka2), 0, abs(ka2 - cb), h.tfs)
                    rr.append((cb - a, side, 1 if v == BP.CONTINUANCE else 0, ka - a, med, pos,
                               ka2 - a))
                    vv.append(dv)
            d['g15grid_%s_%s' % (side_m, pair_m)] = np.array(rr, float).reshape(-1, 7)
            d['g15grid_%s_%s_diffvec' % (side_m, pair_m)] = np.array(vv, float).reshape(-1,
                                                                                        len(h.tfs))
            P('g15 grid %s/%s: %d verdicts' % (side_m, pair_m, len(rr)))
    G15.SIDE, G15.PAIR = 'ws5', 'fwd'                      # back to the banked reading

    # ---- THE CONJUNCTION. gate_ok every bar; strength and patch at the fires, which is where the
    # expensive anchor_floater read lives.
    for side in (+1, -1):
        d['conj_gate_dr%+d' % side] = np.array(
            [o.conj.gate_ok(j, side) for j in range(a, b + 1)], bool)
    P('conjunction gate state, every bar, both sides')
    fires = []
    for side in (+1, -1):
        for j, mem, patched in o.conj.fires(a, side, until=b):
            st = o.conj.strength(j, side)
            pk, pw = o.conj.patch_ok(j, side)
            c, cf, dirn = o.conj.cross_for(j, side, o.x5, o.m5)
            fires.append({'bar': j - a, 'side': side, 'members': list(mem),
                          'patched': bool(patched), 'strength': None if st is None else float(st),
                          'patch_ok': bool(pk), 'patch_why': pw,
                          'xcross': None if c is None else int(c) - a,
                          'xcross_conf': None if cf is None else int(cf) - a, 'xcross_dir': dirn})
    d['conj_fires'] = fires
    P('conjunction: %d fires with strength, patch verdict and x-cross' % len(fires))

    # ---- PRICE STRUCTURE
    # THE BANKED CONVENTION IS score39.pivots - `find_pivots` returns [(index, kind)] with kind
    # 'H' or 'L', and score39 splits it. Use its producer, do not re-split here.
    Hs, Ls = sc.pivots(float(swing_pct))
    d['pivot_H'] = np.array([int(z) - a for z in np.asarray(Hs) if a <= z <= b], np.int64)
    d['pivot_L'] = np.array([int(z) - a for z in np.asarray(Ls) if a <= z <= b], np.int64)
    P('swing pivots at %.2f%%: %d highs, %d lows'
      % (swing_pct, len(d['pivot_H']), len(d['pivot_L'])))

    # ---- THE WALK
    ev = o.events(a, b)
    d['events'] = [(int(x[0]) - a, int(x[1]), str(x[2]), str(x[3])) for x in ev]
    # THE STRUCTURED CAUSATION CHAIN PER EVENT. Added 1016 after Joe's first dev-cache test:
    # *"I need to see the timestamped events that created 08-22 02:07"*. The bars were all
    # reachable but only as TEXT inside the note, so every causation question needed a regex.
    # These are the same bars as structured fields, so the chain is a lookup.
    #   fire_bar      the conjunction fire, or None on the ws5Mage-oob path
    #   xcross        the x-cross bar, and xcross_conf the bar it was CONFIRMED
    #   xcross_dir    'back' or 'forward' - which way cross_for searched
    #   hold_from     the bar bounce-pred's hold started from, or None if unheld
    #   reversal_bar  the sample bar the passing verdict was measured at
    # lookahead_bars IS COMPUTED HERE AND KEPT: event bar - fire bar. A NEGATIVE value means the
    # event is stamped BEFORE the information that produced it. The first test of this cache found
    # one: 2026-08-24 10:28:05 sits 26 bars = 130 s before its own fire at 10:30:15, on a BACKWARD
    # x-cross that was not held by bounce-pred. REPORTED TO JOE, NOT FIXED - the fix moves the
    # banked number.
    import re as _re
    chain = []
    for bar, side, src, note in ev:
        g = lambda pat: (_re.search(pat, note).group(1) if _re.search(pat, note) else None)
        fb = g(r'the fire was (\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)')
        hf = g(r'held from (\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)')
        rb = g(r'the reversal was (\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)')
        fbar = None if fb is None else int(sc.K(fb))
        xc = xcc = xd = None
        if fbar is not None:
            for y in o.conj.fires(max(a - 1, 0), int(side), until=b):
                if y[0] == fbar:
                    _c, _cf, _dn = o.conj.cross_for(fbar, int(side), o.x5, o.m5)
                    xc = None if _c is None else int(_c) - a
                    xcc = None if _cf is None else int(_cf) - a
                    xd = _dn
                    break
        chain.append({'bar': int(bar) - a, 'side': int(side), 'source': str(src),
                      'fire_bar': None if fbar is None else fbar - a,
                      'xcross': xc, 'xcross_conf': xcc, 'xcross_dir': xd,
                      'hold_from': None if hf is None else int(sc.K(hf)) - a,
                      'reversal_bar': None if rb is None else int(sc.K(rb)) - a,
                      'lookahead_bars': None if fbar is None else int(bar) - fbar})
    d['event_chain'] = chain
    _la = [c for c in chain if c['lookahead_bars'] is not None and c['lookahead_bars'] < 0]
    P('event chain banked; %d of %d events stamped BEFORE their own fire'
      % (len(_la), sum(1 for c in chain if c['fire_bar'] is not None)))
    # THE GATE SLACK DETAIL. Joe's gate reads ws1Mage same-side oob with a 4-bar slack; the bool
    # does not say WHICH bar in the slack admitted it, which the first test also wanted.
    import _conj as _CJ
    for side in (+1, -1):
        g1 = o.conj.mg['ws1Mage'] if hasattr(o.conj, 'mg') and 'ws1Mage' in getattr(
            o.conj, 'mg', {}) else np.asarray(sc.LD(60, 'Mage'), float)
        oobm = (g1 >= HI) if side > 0 else (g1 <= LO)
        slack = int(_CJ.GATE_SLACK)
        adm = np.full(n, -1, np.int64)
        for i, j in enumerate(range(a, b + 1)):
            for q in range(j, max(j - slack, 0) - 1, -1):
                if oobm[q]:
                    adm[i] = q - a
                    break
        d['conj_gate_slack_bar_dr%+d' % side] = adm
    d['conj_gate_slack'] = slack
    P('gate slack bars banked: which bar in the %d-bar slack was same-side oob' % slack)
    wrows, live = o.walk(a, b)
    tr = []
    PX = np.asarray(sc.PX, float)
    for bar, side, src, note, closed, op, nl in wrows:
        for t in closed:
            e, x, dr = int(t['entry']), int(t['exit']), int(t['dr'])
            seg = PX[e:x + 1]
            ep = float(PX[e])
            adv = (seg - ep) / ep * 100.0 if dr > 0 else (ep - seg) / ep * 100.0
            fav = -adv
            tr.append({'entry': e - a, 'exit': x - a, 'dr': dr,
                       'source': str(t['source']), 'exit_reason': str(t['exit_reason']),
                       'gross': float(o.gross(t)),
                       'mae': float(max(0.0, np.nanmax(adv))),
                       'mfe': float(max(0.0, np.nanmax(fav)))})
    d['trades'] = tr
    d['open_at_end'] = [{'entry': int(t['entry']) - a, 'dr': int(t['dr']),
                         'source': str(t['source'])} for t in live]
    # THE WALK ROWS, banked because they are THE CHAIN and they are not reconstructible from
    # events + trades alone: an event that took no row because of the standdown and one whose open
    # the cap blocked look identical once the row is gone.
    d['walk_rows'] = [{'bar': int(bar) - a, 'side': int(side), 'source': str(src),
                       'note': str(note),
                       'closes': [(int(t['entry']) - a, int(t['dr'])) for t in closed],
                       'opens': None if op is None else int(op['dr']),
                       'open_after': int(nl)} for bar, side, src, note, closed, op, nl in wrows]
    P('%d events, %d closed trades with MAE/MFE, %d still open' % (len(ev), len(tr), len(live)))

    # ---- LINEAGE, at the event bars only - each read is a walk
    if run_leg is not None:
        ln = []
        for bar, side, src, note in ev:
            for ts in (+1, -1):
                v, why = LC.read(run_leg, int(bar), ts)
                ln.append({'bar': int(bar) - a, 'trade_side': ts, 'verdict': v, 'why': why})
        d['lineage_at_events'] = ln
        P('lineage read at %d event bars, both trade sides' % len(ev))

    # ---- what the mom-xfer gate WOULD have withheld, had it been on
    d['mx_blocked'] = [(int(x[0]) - a, int(x[1]), str(x[2]), str(x[3])) for x in o.mx_blocked]

    d['_control_px_sum'] = float(np.nansum(d['px']))
    d['_control_n_events'] = len(ev)
    d['_control_n_trades'] = len(tr)
    P('done')
    return d


def save(d, k, log=print):
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, 'win3_%s.npz' % k)
    arrays = {q: v for q, v in d.items() if isinstance(v, np.ndarray)}
    meta = {q: v for q, v in d.items() if not isinstance(v, np.ndarray)}
    np.savez_compressed(p, _meta=np.array([json.dumps(meta)]), **arrays)
    log('# cached %s (%.1f MB)' % (p, os.path.getsize(p) / 1e6))
    return p


def load(k, log=print):
    """-> the dict, or None. The CONTROL is re-checked here; a mismatch returns None."""
    p = os.path.join(CACHE, 'win3_%s.npz' % k)
    if not os.path.exists(p):
        return None
    z = np.load(p, allow_pickle=False)
    d = {q: z[q] for q in z.files if q != '_meta'}
    d.update(json.loads(str(z['_meta'][0])))
    got = float(np.nansum(d['px']))
    if abs(got - float(d['_control_px_sum'])) > 1e-6:
        log('# *** CONTROL MISMATCH: px sum %.6f vs banked %.6f - REBUILDING ***'
            % (got, float(d['_control_px_sum'])))
        return None
    log('# loaded %s | %d bars | %d events | control OK' % (p, int(d['n']),
                                                            int(d['_control_n_events'])))
    return d
