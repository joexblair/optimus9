"""arm_walk.py — the ARM DELAY SPEC 0709 walk, as one reusable causal function. (Joe 0710)

Read-only.  Every read goes through optimus9.analysis.jig.  No hand-rolled prediction, no hand-rolled curl.

  HUNT      s5m OOB is permission; the hunt starts at the s5m IB->OOB crossing.
  apex      starts at TFS[0] (TF5).
  no-op     while the apex's r has not predicted (tested only at the apex's 1/3-TF seams).
  cancel    the apex's m returns IB with no prediction  |  s5m permission drops or flips.
  CURL      once the apex's r has predicted, wait for its coarse curl.  At that curl, test the next TF up:
              predicted or breached -> sub_apex = apex; apex = HTF; keep climbing.
              neither               -> ARM.
  LATCH     (Joe 0710) two-stage, NO expiry.  Once the apex's r and the TF above it are BOTH out of
            bounds on es, they must both eventually reverse.  The first coarse curl latches stage 1;
            the second one arms.  A slow second line buys a trip over MAE and into MFE.
  TP        at the arm, scan UP from the arm TF until an r is not OOB; the last OOB TF is the TP TF.
            Follow that TF's mini to the OPPOSITE side; TP when it is OOB there and reverses.

curl_bands: seam = tf*60 // div, where div is chosen by the first band whose ceiling >= tf.
            "7:2,14:4,999:6"  ->  tf<=7 : TF/2   ·   8..14 : TF/4   ·   >14 : TF/6
"""
import numpy as np

HI, LO = 85.0, 15.0
DAY = 86_400_000
DEFAULT_TFS = [5, 6, 7, 8, 9, 10, 11, 12, 14, 16, 19, 22]
DEFAULT_BANDS = '7:2,14:4,999:6'


def parse_bands(s):
    return [(int(c), int(d)) for c, d in (p.split(':') for p in s.split(','))]


def curl_div(tf, bands):
    for ceil, div in bands:
        if tf <= ceil:
            return div
    return bands[-1][1]


# s5m override: Joe 0710 named this value explicitly and asked for it in code until it is swept and
# written to indicator_configs.  It is the ONLY hardcoded line config here — everything else is a knob.
S5M_OVERRIDE = ('bb', 8, 0.65, 'ohlc4')


def overrides(tfs, m_len, m_mult):
    o = {}
    for tf in tfs:
        s = tf * 60
        o[f's{tf}r'] = (s, ('k', 5, 6, 5, 'close'), 'emerging')
        o[f's{tf}Mage'] = (s, ('bb', 37, 0.7, 'ohlc4'), 'emerging')
        o[f's{tf}m'] = (s, (S5M_OVERRIDE if tf == 5 else ('bb', m_len, m_mult, 'ohlc4')), 'emerging')
    return o


def board(jig, tfs, es, tol, bands, wob=1, names=None):
    """Cached Board, stored ON the jig so it dies with the window. A Board computes ~3xTF emerging lines and
    the walk only ever needs one per side — building one per hunt was the whole cost of a day's run.
    `names` = optional {tf: series_prefix} so one ladder rung can read a PRIVATE line family (Joe 0711:
    the exit's TF5 reads `es5`, a clone of s5, so sweeping s5 for the ENTRY cannot move the EXIT)."""
    cache = jig.__dict__.setdefault('_arm_boards', {})
    key = (tuple(tfs), es, tol, tuple(bands), wob, tuple(sorted((names or {}).items())))
    if key not in cache:
        cache[key] = Board(jig, tfs, es, tol, bands, wob, names)
    return cache[key]


class Board:
    """Everything the walk reads, computed once per window. Owns line NAMING (`names`), so a consumer can
    re-base a rung onto a private series without forking the walk."""

    def __init__(self, jig, tfs, es, tol, bands, wob=1, names=None):
        C = jig.causal
        self.C, self.tfs, self.es, self.wob = C, tfs, es, wob
        self.names = dict(names or {})
        p = self.pfx                                                # tf -> series prefix ('s5' | 'es5' | ...)
        self.ts = np.asarray(jig.ts, np.int64)
        self.px = jig.px
        anchor = (int(self.ts[0]) // DAY) * DAY
        # the HUNT line = the ladder's bottom rung's mini (was hardcoded s5m; now follows tfs[0] and `names`)
        self.hunt_m = C.line(p(tfs[0]) + 'm')
        self.hunt_seam = (self.ts % (tfs[0] * 60 * 1000)) == 0
        self.s5m, self.seam5 = self.hunt_m, self.hunt_seam          # back-compat aliases
        self.seam = {tf: tf * 60 // curl_div(tf, bands) for tf in tfs}
        self.pred = {tf: C.predict_set(p(tf), tol=tol, maj='Mage') for tf in tfs}
        self.moob = {tf: C.mini_oob(p(tf)) for tf in tfs}
        self.r = {tf: C.line(p(tf) + 'r') for tf in tfs}
        self.m = {tf: C.line(p(tf) + 'm') for tf in tfs}
        self.oob = {tf: (self.r[tf] >= HI) if es == 1 else (self.r[tf] <= LO) for tf in tfs}
        self.pseam = {tf: ((self.ts - anchor) % ((tf * 60 // 3) * 1000)) == 0 for tf in tfs}
        self.curl = {tf: {int(np.searchsorted(self.ts, t))
                          for t in C.curl(*C.coarse(p(tf) + 'r', self.seam[tf] * 1000), -es)} for tf in tfs}

    def pfx(self, tf):
        return self.names.get(tf, f's{tf}')

    def side(self, k):
        return 1 if self.hunt_m[k] >= HI else (-1 if self.hunt_m[k] <= LO else 0)

    def first_breach(self, tf, k0, k1):
        o = self.oob[tf]
        x = np.flatnonzero(o[k0 + 1:k1] & ~o[k0:k1 - 1]) + 1
        return k0 + int(x[0]) if len(x) else None


def walk(B, kh, ke, brc_tol=1.0, curl_tol=0, cancel_on='apex', cancel_seam='bar', permission=True,
         latch=False, arm_mode='both', allib='ladder'):
    """Returns (events, armed, cancel). armed = (bar, tf, why); cancel = (bar, why).

    cancel_on   'apex' = the no-prediction cancel watches the CURRENT apex's mini
                's5m'  = it watches s5m only (the hunt line), whatever the apex is
    cancel_seam 'bar'  = tested every 5s bar
                'pseam'= tested only at the apex's 1/3-TF prediction seam
    cancel_on   'none' = the no-prediction cancel is disabled entirely
    permission  False  = the s5m permission drop no longer kills the hunt
    latch       True   = arm when the apex AND the TF above it have both gone OOB and both have curled
                         (no expiry on the first curl).  False = the same-bar backstop.
    arm_mode    'both'  = latch OR htf-quiet can arm
                'latch' = ONLY the latch arms (Joe 0710).  An htf-quiet curl is a no-op: keep walking
                          until the TF above wakes, or cancel when every ladder r has gone back IB
                          after at least one of them breached.
    """
    es, tfs = B.es, B.tfs
    apex, sub = tfs[0], None
    predicted = False
    ev = []
    brc = {tf: B.first_breach(tf, kh, ke) for tf in tfs}
    for k in range(kh, ke):
        if permission and B.seam5[k] and B.side(k) != es:
            return ev, None, (k, 's5m permission dropped')
        if not predicted:
            if B.pseam[apex][k] and B.pred[apex][k] == es:
                predicted = True; ev.append((k, apex, 'r predicted'))
            elif cancel_on != 'none':
                w = apex if cancel_on == 'apex' else B.tfs[0]
                gate = True if cancel_seam == 'bar' else bool(B.pseam[apex][k])
                if gate and B.moob[w][k] != es and B.moob[w][k - 1] == es:
                    return ev, None, (k, f's{w}m returned IB with no prediction')
            continue
        if allib != 'off' and arm_mode == 'latch':
            watch = tfs if allib == 'ladder' else [tfs[0]]
            if any(brc[t] is not None and brc[t] <= k for t in watch) and not any(B.oob[t][k] for t in watch):
                return ev, None, (k, f'all {allib} r lines returned IB')
        if k not in B.curl[apex]:
            continue
        i = tfs.index(apex)
        if i + 1 >= len(tfs):
            return ev, (k, apex, f'top of ladder TF{apex}'), None
        htf = tfs[i + 1]
        if latch:
            # stage 1 / stage 2: both OOB, both curled.  No expiry.
            if brc[apex] is not None and brc[htf] is not None:
                ca = [c for c in B.curl[apex] if brc[apex] <= c <= k]
                ch = [c for c in B.curl[htf] if brc[htf] <= c <= k]
                if ca and ch:
                    return ev, (k, apex, f'latch TF{apex}+TF{htf}'), None
        elif sub is not None and brc[sub] is not None and brc[apex] is not None \
                and abs(brc[sub] - brc[apex]) * 5 <= brc_tol * apex * 60 \
                and any(abs(k - c) <= curl_tol for c in B.curl[sub]):
            return ev, (k, apex, f'backstop TF{sub}+TF{apex}'), None
        live = (B.pred[htf][k] == es) or B.oob[htf][k]
        ev.append((k, apex, f'r curl -> s{htf}r {"live" if live else "quiet"}'))
        if live:
            sub, apex = apex, htf
            predicted = (B.pred[apex][k] == es)
        elif arm_mode != 'latch':
            return ev, (k, apex, f'htf-quiet TF{apex}'), None
    return ev, None, None


def walk_stack(B, kh, ke):
    """[T4 — the winning arm] Joe's stack climb (0711). Kickoff when the bottom TWO rungs' r are both OOB on
    es; then climb the OOB/predict stack — a rung joins if its r is OOB, or if it is predicted; stop when a
    rung offers neither, and ARM at the top of the stack. Returns (bar, apex_tf) or None.

    This lands the apex HIGH (avg TF16 on the 10..25 ladder) — 'bigger TF, bigger leg'. It beats the
    curl/reversal latch decisively on the same ladder (net +0.215 vs -0.126 /trade, 20d), because the latch
    arms on the first adjacent pair (~TF11) and never climbs.  NOTE: it arms at stack-resolution, not on a
    curl — there is no reversal timing in this rule."""
    es, tfs = B.es, B.tfs
    oob, pred = B.oob, B.pred
    if len(tfs) < 2:
        return None
    for k in range(kh, ke):
        if not (oob[tfs[0]][k] and oob[tfs[1]][k]):
            continue
        ci = 1
        while ci + 1 < len(tfs):
            nx = tfs[ci + 1]
            if oob[nx][k] or pred[nx][k] == es:
                ci += 1
            else:
                break
        return (k, tfs[ci])
    return None


def hunt_side(jig, hunt_tf):
    """(ks, sd) for the hunt line s{hunt_tf}m: its seam bars, and side(k) -> +1 hi / -1 lo / 0 in-bounds.
    ONE impl — every consumer reads this instead of re-deriving `sd` and the seam list."""
    C = jig.causal
    ts = np.asarray(jig.ts, np.int64)
    hm = C.line(f's{hunt_tf}m')
    ks = [int(k) for k in np.flatnonzero((ts % (hunt_tf * 60 * 1000)) == 0)]
    return ks, (lambda k: 1 if hm[k] >= HI else (-1 if hm[k] <= LO else 0))


def hunts(jig, hunt_tf, t0, t1):
    """The hunt seeds: s{hunt_tf}m IB->OOB crossings (at that TF's seams) inside [t0, t1] -> [(bar, es)]."""
    ts = np.asarray(jig.ts, np.int64)
    ks, sd = hunt_side(jig, hunt_tf)
    return [(ks[i], sd(ks[i])) for i in range(1, len(ks))
            if sd(ks[i]) and sd(ks[i]) != sd(ks[i - 1]) and t0 <= ts[ks[i]] <= t1]


def arm_cancel(jig, hunt_tf, kA, es, stay=True, win=60, wob=1):
    """The arm's natural cancel (CANONICAL, Joe 0711): the next OPPOSITE-side s{hunt_tf}m breach — STAYED if
    s2Mage reverses toward `es` within `win` bars after it (the sell-off that drove the breach is reversing,
    so the arm survives the twitch).  Returns the cancel bar, or the tape end.  NOT a cap — this is the arm's
    own life.  Requires s2Mage in the jig overrides (it is not a DB line)."""
    C = jig.causal
    ts = np.asarray(jig.ts, np.int64)
    n = len(ts)
    ks, sd = hunt_side(jig, hunt_tf)
    rev2M = C.reversal(C.line('s2Mage'), wob) if stay else None
    for kb in [k for k in ks if k > kA and sd(k) == -es]:
        if not stay:
            return kb
        w1 = min(kb + win, n - 1)
        if not np.any(rev2M[kb + 1:w1 + 1] == es):      # s2Mage did NOT reverse toward es -> a real cancel
            return kb
    return n - 1


def tp_tf(B, k_arm, tf):
    """Scan UP from the arm TF until an r is not OOB on es; the last OOB TF is the TP TF (Joe 0710)."""
    es = B.es
    out = tf
    for t in B.tfs[B.tfs.index(tf):]:
        r = B.r[t][k_arm]
        if (r >= HI) if es == 1 else (r <= LO):
            out = t
        else:
            break
    return out


def take_profit(B, k_arm, tf, k_max):
    """Follow s{tf}m to the OPPOSITE side of the arm; TP on its first reversal while OOB there."""
    es = B.es
    m = B.m[tf]
    far = (m <= LO) if es == 1 else (m >= HI)          # the other side of the board
    rev = B.C.reversal(m, B.wob)
    for k in range(k_arm + 1, min(k_max, len(m))):
        if far[k] and rev[k] == es:                     # turning back toward the arm side
            return k
    return None


def take_profit_ad(B_tp, entry, cap, q15_tp, q30_tp, trace=None):
    """The REAL TP (Joe 0710): the arm-delay pipeline run in the EXIT direction (B_tp.es = -es_entry),
    SEEDED on exit-side s5m breaches after the entry — NOT a single walk from the entry bar. A slow reversal
    (10:22: s5m HI breach at 13:05) only starts hunting when its s5m breach lands; walking continuously from
    the entry stalls the ladder at TF5 for hours.

    Per exit-side s5m IB->OOB crossing, walk the ladder (arm_mode='both': a fast single-TF reversal arms at
    the base TF5 when s6 is quiet; a slow one climbs and latches). At the arm, fin_unlatch_6of9 fires the
    exit: the 7x30s back-lookback (fin_box_qualified, internal) authorises, the 6of9 lines-OOB confluence
    triggers. The 6of9 anchors on the reversal as it develops (19:42: exit 20:25:30, gain +0.45%) where the
    sparse s_qualify co-fire (fin_gate) missed forward to 20:55:40 (+0.06%).

    Backstop (Joe 0710): if a base (s5m + s5r) reverses but never produces s30a+s15a, and BOTH s5m and s5r
    return in-bounds, exit immediately at that IB-return bar — the reversal fizzled; don't hold for the next.

    q15_tp/q30_tp = es_tp-side finishers (qlo for a long exit / qhi for a short exit).
    Returns the exit bar, or None.  trace (opt) = list; appended (kind, bar, tf) per hunt for diagnostics.

    Worked example: 14:01 SHORT opens · 14:05 s5r predicts · 14:15 s5r curls, s6 OOB (climb) · 14:20 s6 curls
    (apex) · 14:33:30 s30a+s15a -> exit."""
    es, tf0 = B_tp.es, B_tp.tfs[0]
    seam5, side = B_tp.hunt_seam, B_tp.side          # the bottom rung's mini (es5m when the exit is re-based)
    oob5, pred5 = B_tp.oob[tf0], B_tp.pred[tf0]
    ks = [k for k in range(entry + 1, cap) if seam5[k]]
    hunts = [ks[i] for i in range(1, len(ks)) if side(ks[i]) == es and side(ks[i]) != side(ks[i - 1])]
    for kh in hunts:
        _ev, armed, _c = walk(B_tp, kh, cap, cancel_on='none', permission=False,
                              latch=True, arm_mode='both', allib='off')
        if armed:
            # option (a): the 7x30s back-lookback (fin_box_qualified, inside fin_unlatch_6of9) authorises at
            # the arm; the 6of9 lines-OOB confluence TRIGGERS the exit. It anchors on the reversal as it
            # develops (19:42: 20:25:30) where the sparse s_qualify co-fire (fin_gate) missed to 20:55:40.
            # Symmetric with the entry: ladder -> arm -> fin_box_qualified -> fin_unlatch_6of9.
            x = B_tp.C.fin_unlatch_6of9(armed[0], cap, es, q15_tp, q30_tp, N=6)
            if x is not None:
                if trace is not None:
                    trace.append(('arm', x, armed[1]))
                return x
        # backstop: base fizzled — s5r predicted, then both s5m & s5r return IB with no finisher between.
        kp = next((k for k in range(kh, cap) if pred5[k] == es), None)
        if kp is None:
            continue
        for k in range(kp + 1, cap):
            if q15_tp[k] and q30_tp[k]:              # a finisher came — a later hunt's arm will place the exit
                break
            if side(k) != es and not oob5[k]:        # s5m off-side AND s5r back in-bounds -> fizzled
                if trace is not None:
                    trace.append(('backstop', k, tf0))
                return k
    return None
