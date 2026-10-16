"""`mom-xfer` as a gate on `bounce-pred`. 1016. UNRULED — MEASUREMENT ONLY, DEFAULT OFF.

JOE'S INSTRUCTION, 1016: *"locate the mom-xfer mech and test its application as a gate on
bounce-pred. there's a race-version, I think it's using ws8 ws9 ws10. sweep the 3 racers, steps
of 1"*.

WHAT I FOUND, AND ONE CORRECTION TO HIS RECALL
    the mech          `mom_xfer`, Joe 0920. A COUNT across MOMTFS (10, 11, 12) of lines that have
                      LEFT momtf_dr at the same bar, `mom_xfer.count_min` = 2.
                      seed_v3_config.py:195, docs/22_go_20260921/report_leash_momtf.py
    the race version  `XFER_TFS = (9, 8, 7)` — docs/22_go_20260921/report_leash_momtf.py:72.
                      HIS RECALL WAS ws8/ws9/ws10; the banked set is ws7/ws8/ws9. His 0929 words:
                      *"bank IND 9, and add IND8 and IND7"* and *"drop 11 and 10. MOMTFS stays
                      untouched"*. Three INDEPENDENT single-line reads - no count, no chaining,
                      no shared search floor.
    the producer      walk_mom_models.momentum_true(line, bank, WS1_CFG, dr, k, seam, tf,
                      strip_mom_at_fence=the r-momo-fence). Joe 0920 ruled the strip ON.
    mom-true          `momo` OR `curl`. Joe 1009: *"I use mom-true as shorthand for
                      momentum.momo and momentum.curl"*.

THE BANKED mom-true MASKS CANNOT BE REUSED. `_momtrue.momtrue_mask` builds with `momo_g`, which is
STRIP OFF (its own docstring records Joe's 1009 ruling for that mech). mom-xfer's producer is the
STRIP-ON call. Different function, different answer, so this file reads the strip-on call directly
and caches per (tf, bar, dr). Measured cost: 0.00015 to 0.00029 s per read, so a whole-tape mask
would be 8-16 min per racer per side - unnecessary, because a gate only reads at verdict bars.

FIVE THINGS JOE HAS NOT SPECIFIED. Every one is a knob so the sweep measures each reading instead
of me picking one:
    W_MX_TFS     the three racers, as a comma list. '7,8,9' is the banked set
    W_MX_COUNT   how many of the three must satisfy the gate. 1, 2 or 3. The COUNT version of the
                 mech uses count_min 2, but that is a count over a different set (10,11,12)
    W_MX_DIR     'left'  pass the verdict only when COUNT racers have LEFT mom-true (momentum has
                         transferred out, which is what the mech's name describes)
                 'true'  pass only when COUNT racers are STILL mom-true
    W_MX_BAR     'rev'   read the racers at the ws5Mage reversal bar
                 'known' read them at the verdict's known_at bar. Causal either way: known_at is
                         the bar the verdict is readable, so reading the racers there reads no
                         later than the verdict itself
    W_MX_DR      'event' the racer dr is the event's own side, +1 HIGH / -1 LOW
                 'trade' the racer dr is the side the event OPENS, which is the opposite - a HIGH
                         event opens a SHORT, dr +1. Per the banked dr frame: dr +1 SHORT,
                         dr -1 LONG
    W_MX_ON      0 = the gate is off, which is the DEFAULT. Nothing banked moves.

WHAT THE GATE DOES NOT DO: it never creates a verdict, never moves a bar, and never changes a
`continuance` into a `reverse`. It only withholds a verdict that bounce-pred already produced.

SRP: this file answers one question per bar - does the racer gate pass. It holds no trade state.
"""
import os
import numpy as np

ON = os.environ.get('W_MX_ON', '0') == '1'
TFS = tuple(int(x) for x in os.environ.get('W_MX_TFS', '7,8,9').split(','))
COUNT = int(os.environ.get('W_MX_COUNT', 2))
DIR = os.environ.get('W_MX_DIR', 'left')
BAR = os.environ.get('W_MX_BAR', 'rev')
DRM = os.environ.get('W_MX_DR', 'event')

assert DIR in ('left', 'true'), DIR
assert BAR in ('rev', 'known'), BAR
assert DRM in ('event', 'trade'), DRM
assert 1 <= COUNT <= 3, COUNT
assert len(TFS) == 3, TFS


class MomXfer:
    """The racer gate over one tape. Build once, then `passes`."""

    def __init__(self, sc, rl, bank, fence=None):
        import walk_mom_models as WM
        from optimus9.compute.momo_seam import seam_mask
        self.WM = WM
        self.sc = sc
        self.rl = rl                       # {tf: the ws{tf}r array}
        self.bank = bank                   # {tf: the per-TF momo bank}
        if fence is None:
            mfr = 17.0
            try:
                mfr = float(sc.LG['momo_fence_r'])
            except Exception:
                pass
            fence = (mfr, 100.0 - mfr)
        self.fence = fence                 # STRIP-MOM-AT-FENCE, Joe 0920
        self.seam = {}
        self._c = {}
        self._seam_mask = seam_mask

    def _sm(self, t):
        if t not in self.seam:
            self.seam[t] = self._seam_mask(self.sc.ts, t)
        return self.seam[t]

    def momtrue(self, t, k, d):
        """Is ws{t}r mom-true at bar k on dr d, strip ON. Cached per (t, k, d)."""
        ck = (int(t), int(k), int(d))
        if ck not in self._c:
            self._c[ck] = bool(self.WM.momentum_true(
                self.rl[t], self.bank[t], self.WM.WS1_CFG, int(d), int(k), self._sm(t), int(t),
                strip_mom_at_fence=self.fence)[0])
        return self._c[ck]

    def read(self, rev_bar, known_at, event_side):
        """-> (passes?, [the per-racer mom-true reads], the bar read, the dr read)."""
        k = int(rev_bar if BAR == 'rev' else known_at)
        d = int(event_side) if DRM == 'event' else -int(event_side)
        hits = [self.momtrue(t, k, d) for t in TFS]
        # 'left' counts the racers that are NOT mom-true - momentum has transferred out of them.
        # 'true' counts the racers that still are.
        if DIR == 'left':
            n = sum(1 for h in hits if not h)
        else:
            n = sum(1 for h in hits if h)
        return (n >= COUNT), hits, k, d

    def why(self, rev_bar, known_at, event_side):
        ok, hits, k, d = self.read(rev_bar, known_at, event_side)
        return ('mom-xfer %s: %s at %s on dr %+d, need %d of 3 -> %s'
                % (DIR, ', '.join('ws%dr %s' % (t, 'mom-true' if h else 'left')
                                  for t, h in zip(TFS, hits)),
                   self.sc.U(k), d, COUNT, 'PASS' if ok else 'BLOCK'))
