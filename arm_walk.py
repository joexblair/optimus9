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


class Board:
    """Everything the walk reads, computed once per window."""

    def __init__(self, jig, tfs, es, tol, bands, wob=1):
        C = jig.causal
        self.C, self.tfs, self.es, self.wob = C, tfs, es, wob
        self.ts = np.asarray(jig.ts, np.int64)
        self.px = jig.px
        anchor = (int(self.ts[0]) // DAY) * DAY
        self.s5m = C.line('s5m')
        self.seam5 = (self.ts % 300_000) == 0
        self.seam = {tf: tf * 60 // curl_div(tf, bands) for tf in tfs}
        self.pred = {tf: C.predict_set(f's{tf}', tol=tol, maj='Mage') for tf in tfs}
        self.moob = {tf: C.mini_oob(f's{tf}') for tf in tfs}
        self.r = {tf: C.line(f's{tf}r') for tf in tfs}
        self.m = {tf: C.line(f's{tf}m') for tf in tfs}
        self.oob = {tf: (self.r[tf] >= HI) if es == 1 else (self.r[tf] <= LO) for tf in tfs}
        self.pseam = {tf: ((self.ts - anchor) % ((tf * 60 // 3) * 1000)) == 0 for tf in tfs}
        self.curl = {tf: {int(np.searchsorted(self.ts, t))
                          for t in C.curl(*C.coarse(f's{tf}r', self.seam[tf] * 1000), -es)} for tf in tfs}

    def side(self, k):
        return 1 if self.s5m[k] >= HI else (-1 if self.s5m[k] <= LO else 0)

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
