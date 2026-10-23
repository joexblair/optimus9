"""A cached reversal table, so a sweep is affordable.

THE 1023 CAUSALITY REPAIR, Joe's rulings. Three things moved and all three are timing, not logic:
    the reversals  every bar the walk ACTS on is the lift-off STAMP (b + LIFT_WOB - 1), never the
                   raw lift-off bar. The ANCHOR stays the raw bar - that is what identifies WHICH
                   reversal - so only the moment of action moves. max(), never a swap.
    the ib dwell   `ib_cross` returns the CONFIRM bar (cross + need - 1), not the cross bar. The
                   hold is read on bars at or before it, so the baton passes when the dwell is
                   proven rather than when it starts. The receiver gate then reads R[nxt] at the
                   confirm bar - Joe 1023, option A.
    no reversal    *"B"*: at `pas`, "ws{nxt} never reverses" and "ws{nxt} reverses later" are the
                   SAME observation - only the future separates them. So a receiver with no
                   reversal in the data does not EXHAUST; the chain advances and cannot resolve,
                   which is NO REVERSAL and no trade. The CEILING and the ex-fence gate are both
                   readable at `pas` and still return EXHAUST.

WHY. `jig.lift_off` builds an `at_extreme_mask` over the whole 1,632,960-bar tape on every call.
The lineage walk calls it once per TF per fire, so one full-tape arm rebuilt the same masks about
3,500 times - roughly 9 minutes an arm, and a sweep of any size is then hours. The masks depend
only on (line, side, pts, gap, tol, wob), none of which varies inside an arm, so they are cached
here ONCE per arm and the walk reads a list.

PARITY IS THE POINT, AND `check()` NOW EXISTS. The 1023 audit found that this docstring claimed a
parity harness that was never written, and that the two `ib_cross` implementations really did
diverge at the window edge - 111 of 339 probes on a 07-10 bound. Both now require the whole dwell
to fit inside [frm, B], which is the only form that can be confirmed on data we have. `check()`
compares the two bar for bar, the fires and the verdicts, and is run by `__main__`.

THE CACHE KEY CARRIES THE LINE. It used to be (tf, side, knobs) with no line identity, so a
forgotten `reset()` would serve config 1's reversals for all 27 configs with no error, and the
printed control row reads the array rather than the cache so it could not catch it.
"""
import sys
import io
import hashlib

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
import ln
import v4_knobs as K
_e = sys.stderr; sys.stderr = io.StringIO()
from optimus9.analysis.jig import lift_off, mage_cascade
sys.stderr = _e

_REV = {}
_RUN = {}
_DIG = {}


def reset():
    _REV.clear(); _RUN.clear(); _DIG.clear()


def _dig(line):
    """A digest of the line itself, so the cache cannot serve another config's array.

    Keyed on id() plus the content hash: id() alone is reused after a free, and the hash alone
    costs 13 MB of bytes per call. The pair is cheap and cannot collide across live arrays.
    """
    a = np.ascontiguousarray(line, float)
    k = (id(a), a.shape[0])
    if k not in _DIG:
        _DIG[k] = hashlib.blake2b(a.tobytes(), digest_size=8).hexdigest()
    return _DIG[k]


def runs(line, tf, side):
    """the same-side oob runs of a line, cached. -> (starts, ends) arrays"""
    key = (_dig(line), tf, side, K.OOB_FNC)
    if key not in _RUN:
        m = (line >= K.OOB_HI) if side > 0 else (line <= K.OOB_LO)
        d = np.diff(np.r_[False, m, False].astype(np.int8))
        _RUN[key] = (np.flatnonzero(d == 1), np.flatnonzero(d == -1) - 1)
    return _RUN[key]


def revs(line, tf, side):
    """every oob-anchored reversal of a line, cached. -> a sorted int array of RAW lift-off bars.

    RAW, on purpose: the raw bar is the anchor and the identity of the reversal. Every caller that
    ACTS on one passes it through K.lift_stamp first.
    """
    key = (_dig(line), tf, side, K.LIFT_PTS, K.gap_for(tf), K.LIFT_TOL, K.LIFT_WOB, K.OOB_FNC)
    if key not in _REV:
        L = lift_off(line, side, K.LIFT_PTS, K.gap_for(tf), K.LIFT_TOL, K.LIFT_WOB)
        _REV[key] = np.asarray([int(b) for b in L if K.oob(line[int(b)], side)], int)
    return _REV[key]


def run_holding(line, tf, side, bar):
    """the oob run containing `bar`, or None"""
    s, e = runs(line, tf, side)
    i = int(np.searchsorted(s, bar, side='right')) - 1
    if i < 0 or bar > e[i]:
        return None
    return int(s[i]), int(e[i])


def first_rev_at_or_after(line, tf, side, frm, B):
    """the first oob-anchored reversal at or after `frm`. -> (run, raw bar, stamp)

    `frm` and `B` bound the RAW bar, which is the anchor. The stamp is the bar the walk may act on.
    """
    r = revs(line, tf, side)
    i = int(np.searchsorted(r, frm))
    if i >= len(r) or r[i] > B:
        return None, None, None
    b = int(r[i])
    return run_holding(line, tf, side, b), b, K.lift_stamp(b)


def ib_cross(line, tf, frm, B):
    """the first ib cross at or after `frm` whose dwell is PROVEN. -> (cross, confirm, need)

    `need = int(TF x LIN_IB_DWELL)` bars must be in bounds, starting at the cross bar. The CONFIRM
    bar is `cross + need - 1` and it is what a caller may act on: the dwell is a claim about bars
    the caller has not seen until then.

    THE WHOLE DWELL MUST FIT INSIDE [frm, B]. A run whose confirm bar lies past B is not confirmed
    on data we have, so it is not returned. That is the bound the 1023 audit found the two
    implementations disagreeing on.
    """
    need = K.lin_ib_dwell(tf)
    ib = (line > K.OOB_LO) & (line < K.OOB_HI)
    d = np.diff(np.r_[False, ib, False].astype(np.int8))
    s, e = np.flatnonzero(d == 1), np.flatnonzero(d == -1) - 1
    i = int(np.searchsorted(e, frm))              # the run must END at or after frm
    while i < len(s):
        k = max(int(s[i]), int(frm))
        c = k + need - 1
        if c <= int(e[i]) and c <= B:
            assert bool(ib[k:c + 1].all()), 'the ib dwell is not in bounds end to end'
            return k, c, need
        i += 1
    return None, None, 0


def walk(R, start_tf, side, A, B):
    """the baton chain, cached. -> (verdict, bar). Mirrors v4_lineage_trace.walk exactly.

    EVERY BAR ACTED ON IS A STAMP OR A CONFIRM BAR. `ST[t]` is the reversal's stamp and `pas` is an
    ib CONFIRM bar; the ex-fence gate reads R[nxt] at `pas`, which is Joe 1023 option A.
    """
    ST = {}
    for t in range(start_tf, K.TF_CEILING + 3):
        if t in R:
            _, _, ST[t] = first_rev_at_or_after(R[t], t, side, A, B)

    def hand_over(tf):
        """The bar the baton leaves `tf` on. -> bar or None.

        K.LIN_PASS 'reversal' is Joe's 1022 spec - the pass IS the rider's reversal stamp, and the
        ib walk belongs only to the hatch. 'ib' is what the code has always done.
        """
        if K.LIN_PASS == 'reversal':
            return ST[tf]
        return ib_cross(R[tf], tf, ST[tf], B)[1]

    assert K.LIN_PASS in ('ib', 'reversal'), 'LIN_PASS %r is not a mode' % (K.LIN_PASS,)
    rid = start_tf
    if ST.get(rid) is None:
        return 'NO REVERSAL', None
    pas = hand_over(rid)
    if pas is None:
        return 'NO IB CROSS', None
    while True:
        nxt = rid + 1
        if nxt > K.TF_CEILING:                     # readable at pas
            return 'EXHAUST', pas
        if not K.ex_fence(R[nxt][pas], side):      # readable at pas
            return 'EXHAUST', pas
        if ST.get(nxt) is None:                    # Joe 1023 B: not knowable at pas, so no verdict
            return 'NO REVERSAL', None
        if ST[nxt] > pas:                          # not reversed yet at pas - the normal path
            rid = nxt
            pas = hand_over(rid)
            if pas is None:
                return 'NO IB CROSS', None
            continue
        _, p2, _ = ib_cross(R[nxt], nxt, pas, B)   # HIS RULE: the second walk to ib
        if p2 is None:
            return 'NO IB CROSS', None
        assert p2 >= pas, 'the second walk resolved before the baton-pass bar'
        n2 = nxt + 1
        if n2 > K.TF_CEILING:
            return 'EXHAUST', p2
        if not K.ex_fence(R[n2][p2], side):
            return 'EXHAUST', p2
        if ST.get(n2) is None:
            return 'NO REVERSAL', None
        if ST[n2] <= p2:
            return 'EXHAUST', p2
        rid = n2
        pas = hand_over(rid)
        if pas is None:
            return 'NO IB CROSS', None


def scan(A, B, R, MG, oob_when=None):
    """the backstop, cached. Mirrors v4_backstop.scan(cascade_at='lift', oob_when) exactly.

    `oob_when` defaults to the banked K.BSTOP_OOB_WHEN. The cascade bar is always the reversal
    STAMP here, which is K.BSTOP_CASCADE_AT 'lift' - the only value this cached form implements,
    and it asserts that rather than silently ignoring the knob.
    """
    oob_when = K.BSTOP_OOB_WHEN if oob_when is None else oob_when
    assert oob_when in ('window', 'at_fire'), 'oob_when %r is not a mode' % (oob_when,)
    assert K.BSTOP_CASCADE_AT == 'lift', \
        'v4_fast.scan implements cascade_at lift only; the bank says %r' % (K.BSTOP_CASCADE_AT,)
    r5, m5 = R[5], MG[5]
    win = K.bstop_sync_bars()
    pool = list(range(1, K.BSTOP_POOL_HI + 1))
    out = []
    for side in (+1, -1):
        want = 'down' if side > 0 else 'up'
        oob = {t: ((R[t] >= K.OOB_HI) if side > 0 else (R[t] <= K.OOB_LO)) for t in pool}
        for b in revs(r5, 5, side):
            b = int(b)
            st = K.lift_stamp(b)             # one copy of the arithmetic
            if st < A or st > B:
                continue
            if not K.past_mid(m5[b], -side):
                continue
            lo, hi = max(0, b - win), min(len(r5) - 1, b + win)
            hit = None
            for t in pool:
                w = np.flatnonzero(oob[t][lo:hi + 1])
                if len(w):
                    k = int(lo + w[0])
                    if hit is None or k < hit[1]:
                        hit = (t, k)
            if hit is None:
                continue
            fire = max(st, hit[1])
            if oob_when == 'at_fire' and not any(oob[t][fire] for t in pool):
                continue
            c = mage_cascade(MG, st, zoom=K.SAV_CASCADE_ZOOM, min_lines=K.SAV_CASCADE_MIN)
            if (None if c is None else c['verdict']) != want:
                continue
            out.append({'side': side, 'rev': b, 'stamp': st, 'fire': fire, 'oob_tf': hit[0],
                        'oob_bar': hit[1], 'dir': 'SHORT' if side > 0 else 'LONG'})
    out.sort(key=lambda d: d['fire'])
    return out


# ── check() — the parity harness the docstring promised, written 1023 ──────────────────────────
def check(A, B, R, MG, oob_when='window', log=print):
    """Prove the cached forms equal the un-cached ones. -> the number of disagreements.

    Three comparisons, and a disagreement in any of them means a sweep built on this cache is
    worthless:
        the fires      scan(...) against v4_backstop.scan(..., 'lift', oob_when), field by field
        the verdicts   walk(...) against v4_lineage_trace.walk(...), per fire
        ib_cross       both implementations probed at every bar near the window edge, which is
                       where the 1023 audit found them diverging

    It imports the un-cached modules HERE rather than at module scope, so a sweep that never calls
    check() does not pay for them.
    """
    import v4_backstop as BS
    import v4_lineage_trace as LT
    bad = 0

    fast_f = scan(A, B, R, MG, oob_when)
    slow_f = BS.scan(A, B, R, MG, ln.U, 'lift', oob_when)
    if len(fast_f) != len(slow_f):
        log('| the fires | MISMATCH | fast %d, uncached %d |' % (len(fast_f), len(slow_f)))
        bad += 1
    else:
        for a, b in zip(fast_f, slow_f):
            for k in ('side', 'rev', 'stamp', 'fire', 'oob_tf', 'oob_bar', 'dir'):
                if a[k] != b[k]:
                    log('| fire %s | MISMATCH %s | fast %r, uncached %r |'
                        % (ln.U(a['fire']), k, a[k], b[k]))
                    bad += 1
        log('| the fires | OK | %d fires, every field equal |' % len(fast_f))

    nv = 0
    for d in slow_f:
        fv, fb = walk(R, 5, d['side'], d['rev'], B)
        sv, sb, _ = LT.walk(R, 5, d['side'], d['rev'], B, log=lambda *a: None)
        if (fv, fb) != (sv, sb):
            log('| verdict at %s | MISMATCH | fast %s %s, trace %s %s |'
                % (ln.U(d['fire']), fv, fb, sv, sb))
            bad += 1
        nv += 1
    log('| the verdicts | %s | %d walks compared |' % ('OK' if bad == 0 else 'see above', nv))

    probes = 0
    for t in sorted(R):
        need = K.lin_ib_dwell(t)
        for frm in list(range(max(0, B - 3 * need), B + 1)) + \
                    list(range(max(0, A), min(A + 2 * need, B) + 1)):
            f = ib_cross(R[t], t, frm, B)
            g = LT.ib_cross(R, t, frm, B)
            probes += 1
            if f != g:
                log('| ib_cross tf%d frm %d | MISMATCH | fast %r, trace %r |' % (t, frm, f, g))
                bad += 1
    log('| ib_cross at the edges | %s | %d probes |' % ('OK' if bad == 0 else 'see above', probes))
    return bad


if __name__ == '__main__':
    A, B = ln.K(sys.argv[1]), ln.K(sys.argv[2])
    ow = sys.argv[3] if len(sys.argv) > 3 else 'window'
    R = {t: ln.line('ws%dr' % t) for t in list(range(1, 4)) + list(range(5, K.TF_CEILING + 3))}
    MG = {t: ln.line('ws%dMage' % t) for t in range(1, 13)}
    reset()
    print('# control ws5r 2026-09-03 00:35:00 = %.2f (DB-ruled known-good 12.48; the BANKED k6 rsi8 stc6 line reads 6.77 there)'
          % R[5][ln.K('2026-09-03 00:35:00')])
    print('# RULED_OK %s. %s .. %s, oob_when %r' % (K.RULED_OK, ln.U(A), ln.U(B), ow))
    print()
    print('| the comparison | verdict | detail |')
    print('|---|---|---|')
    bad = check(A, B, R, MG, ow)
    print()
    print('| PARITY | %s |' % ('OK, 0 disagreements' if bad == 0 else '%d DISAGREEMENTS' % bad))
    sys.exit(1 if bad else 0)
