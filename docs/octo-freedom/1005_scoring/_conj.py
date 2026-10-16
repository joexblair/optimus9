"""THE CONJUNCTION MECH. 1016. Joe's design, built from his rulings only.

SRP: this file owns the matr-rev conjunction - its membership, its span, the ws3Mage patch and the
x-cross lookback that consumes it. It opens no trade and closes none. `_ibmech` stamps the cps,
`_chain10` walks, `jig.oob_ib_cross` produces the crossings; none of them know this exists.

THE CONJUNCTION, Joe 1015: *"you should see the reversal happen in a cascade from g15Mage to
ws2-3Mage as they each cross from oob to ib"*. His five lines, each confirming its own oob->ib
cross, all inside a span of each other. The event is stamped at the bar the k-th confirms.
  THE GATE, Joe 1015: *"the turn signal can only fire if ws1Mage is same-side oob"*. Read at the
  fire bar, on the turn's own side.

THE ws3Mage PATCH, Joe 1016: *"create a mech that needs 1) and 2) to qualify, then patches
conjuncture so that ws3Mage's input is made true"*, where 1) is ws3Mage blocking the conjunction
verdict and 2) a ws3r divergence anchored on ws3Mage's reversal.
  HIS RULINGS ON THE FOUR FORKS, 1016, after they were measured and put to him:
    1 *"C"* - ws3Mage is still oob while at least one other member has confirmed inside the span.
      READING A - four of five confirmed with ws3Mage the only gap - was MEASURED AND REJECTED:
      it never holds once in the 2026-07-22 23:10 to 23:30 hold that motivated the mech, where the
      most that ever confirm together is three. It does hold 6530 bars elsewhere in the 12 days.
    2 *"trajectory was the call I made. you'll need a minimum angle, which I won't be able to
      supply. use the value that created the mech, + slack, we can tweak it later"*
    3 *"until conjunction fires"* - the patch holds ws3Mage's input true until then.
    4 *"lookback from conjunction firing. from your numbers, I think 3 is better than 2. xwob needs
      to be confirmed"*

THE TRAJECTORY IS THE DIVERGENCE'S STRENGTH, d_osc / |d_px| from `jig.anchor_floater` on ws3r,
anchored at a ws3Mage reversal. The LEVEL reading was rejected by Joe in favour of the slope,
because the level fires 0.67 min into a 12.5-min hold and stays on for all 17 reversals.

TWO CHOICES ARE MINE AND ARE STATED:
  THE ANGLE'S UNIT IS A PERCENTAGE, not an absolute rise. The strength spans 11135 to 171786 inside
  one 20-minute window, so an absolute rise of 3770 means different things at different levels; a
  percentage is scale-free. Joe gave no unit.
  THE SLACK IS 25.0% against the 30.6% that created the mech - the 2026-07-22 23:19:30 turn rose
  16103 from 12333 over 1.5 min. 25.0 is his value loosened by 5.6 points, which is the "+ slack"
  he asked for. TWEAKABLE, as he said.

CAUSAL. Every read is at or before the bar it reports. The conjunction's fire bar is the k-th
CONFIRMATION, which is already `jig.oob_ib_cross`'s knowable bar. The trajectory compares the
current bar against one W_CONJ_TRAJ_LB bars back. The x-cross lookback only ever reaches BACKWARD
from a bar that has already arrived, and the cross it returns has already met its own xwob hold -
Joe 1016: *"xwob needs to be confirmed"*.
"""
import os
import numpy as np

from optimus9.analysis.jig import oob_ib_cross, anchor_floater

# ---- THE KNOBS. the names are mine; the values are Joe's where marked.
#
# W_CONJ_ROLES - ONE KNOB THAT MOVES A LINE BETWEEN ROLES. Joe 1016: *"create knobs that are more
# than just a simple number. think, how can I swap Mage line's participation in a mech"*.
# The form is a comma list of `line:role+role`, and the roles are:
#     member  the line must confirm its own oob->ib cross inside the span. the plain role
#     latch   once it has confirmed inside the search it stays IN - a one-way trip. Joe 1016 put
#             g15Mage and g30Mage here: *"g15Mage is constantly on the move ... let's make the flip
#             from `missing` to `in` a one-way trip for g15. add also g30 to the same regime"*
#     patch   the line is made true when the patch qualifies. Joe 1016 put ws3Mage and ws2Mage here
#     anchor  the patch's divergence and oob test are read on THIS line. exactly one line
#     gate    the line must be same-side oob at the fire bar. Joe 1015's turn-signal gate
# A line may hold several roles. `latch` and `patch` both imply `member` - they are ways of being
# in, not separate populations. `gate` and `anchor` are independent of being a member.
#
# TO SWAP A LINE'S PARTICIPATION, change one entry. Examples, none of them in use:
#     ws3Mage:patch+anchor -> ws4Mage:patch+anchor     moves the patch up a timeframe
#     ws1Mage:member+gate  -> ws1Mage:member           drops the gate without touching membership
#     g15Mage:latch        -> g15Mage:member           puts g15Mage back on the strict rule
#     ...,ws4Mage:member                               adds a sixth line
# THE DEFAULT STRING REPRODUCES THE 1016 BEHAVIOUR EXACTLY. Verified against the 07-22 chain.
ROLES_SPEC = os.environ.get(
    'W_CONJ_ROLES',
    'g15Mage:latch,g30Mage:latch,ws1Mage:member+gate,ws2Mage:patch,ws3Mage:patch+anchor')

_VALID = ('member', 'latch', 'patch', 'anchor', 'gate')


def _parse_roles(spec):
    """'ws3Mage:patch+anchor,...' -> ([lines in order], {line: {roles}}). Order is the spec's."""
    order, roles = [], {}
    for item in spec.split(','):
        item = item.strip()
        if not item:
            continue
        if ':' not in item:
            nm, rs = item, {'member'}
        else:
            nm, rhs = item.split(':', 1)
            rs = {z.strip() for z in rhs.split('+') if z.strip()}
        nm = nm.strip()
        bad = rs - set(_VALID)
        assert not bad, 'W_CONJ_ROLES: %r has unknown role(s) %s. the roles are %s' % (
            nm, sorted(bad), ', '.join(_VALID))
        assert nm not in roles, 'W_CONJ_ROLES names %r twice' % (nm,)
        order.append(nm)
        roles[nm] = rs or {'member'}
    assert order, 'W_CONJ_ROLES is empty'
    anchors = [nm for nm in order if 'anchor' in roles[nm]]
    assert len(anchors) == 1, (
        "W_CONJ_ROLES needs exactly one `anchor` line - the patch reads one line's reversal "
        "and one line's r. got %s" % (anchors or 'none'))
    gates = [nm for nm in order if 'gate' in roles[nm]]
    assert len(gates) <= 1, (
        'W_CONJ_ROLES has %d `gate` lines; Joe 1015 named one - ws1Mage' % len(gates))
    return order, roles


ORDER, ROLES = _parse_roles(ROLES_SPEC)
MEMBERS = tuple(ORDER)
PATCH_LINES = tuple(nm for nm in ORDER if 'patch' in ROLES[nm])
LATCH_LINES = tuple(nm for nm in ORDER if 'latch' in ROLES[nm])
PATCH_ANCHOR = next(nm for nm in ORDER if 'anchor' in ROLES[nm])
GATE_LINE = next((nm for nm in ORDER if 'gate' in ROLES[nm]), None)
# THE OLD PER-LIST KNOBS STILL OVERRIDE, for a one-off run that does not want to write a whole
# role string. They are read AFTER the roles so an explicit env var always wins.
if 'W_CONJ_MEMBERS' in os.environ:
    MEMBERS = tuple(os.environ['W_CONJ_MEMBERS'].split(','))
if 'W_CONJ_PATCH_LINES' in os.environ:
    PATCH_LINES = tuple(os.environ['W_CONJ_PATCH_LINES'].split(','))
if 'W_CONJ_LATCH_LINES' in os.environ:
    LATCH_LINES = tuple(z for z in os.environ['W_CONJ_LATCH_LINES'].split(',') if z)
if 'W_CONJ_PATCH_ANCHOR' in os.environ:
    PATCH_ANCHOR = os.environ['W_CONJ_PATCH_ANCHOR']
if 'W_CONJ_GATE_LINE' in os.environ:
    GATE_LINE = os.environ['W_CONJ_GATE_LINE'] or None

K = int(os.environ.get('W_CONJ_K', 5))                  # Joe 1015: "they each" = all five
SPAN = int(os.environ.get('W_CONJ_SPAN', 60))           # 5.0 min. UNRULED - the open gap 14
XWOB_MEM = int(os.environ.get('W_CONJ_XWOB_MEM', 4))    # boundary_xwob, Joe 0911 "boundary:4"
PATCH = os.environ.get('W_CONJ_PATCH', '1') == '1'      # the ws3Mage patch, Joe 1016
TRAJ_LB = int(os.environ.get('W_CONJ_TRAJ_LB', 18))     # 1.5 min, Joe's window
TRAJ_MIN = float(os.environ.get('W_CONJ_TRAJ_MIN', 25.0))   # percent. MINE: his 30.6% + slack
XCRS_LB = int(os.environ.get('CONJ_XCRS_LB', 36))       # 3.0 min, Joe 1016 "3 is better than 2"
XCRS_XWOB = int(os.environ.get('W_CONJ_XCRS_XWOB', 8))  # Joe 1015 gave xwob8 for the race
# THE ws1Mage GATE'S SLACK. Joe 1015's gate is *"the turn signal can only fire if ws1Mage is
# same-side oob"*, read AT the fire bar - which is slack 0, the default here. Nothing is loosened
# unless one of these is set. The two units are NOT the same rule and are measured separately:
#   BARS   the gate line was oob on the side within this many bars at or before the fire
#   POINTS the gate line is within this many points of its own oob fence at the fire
# MEASURED over 2026-07-11 to 07-22, K=5: slack 0 gives the LOW side 0 of 40 fires on a price
# pivot; slack 4 gives 25 of 190, 13.2%, and costs the HIGH side 25.6% -> 24.7%. Points is worse
# at every comparable looseness.
# BANKED AT 4 BARS, Joe 1016: *"I agree. bake it along with all of the mechs that create the
# 7.9887"*. On the 2026-07-22 six-leg chain slack 0 gives +5.9609% and holds three legs overnight;
# slack 4 gives +7.9887%. THE DEFAULT HAS MOVED and `_ruled.py` refuses an off-ruled run.
GATE_SLACK = int(os.environ.get('W_CONJ_GATE_SLACK', 4))
GATE_PTS = float(os.environ.get('W_CONJ_GATE_PTS', 0.0))

assert K <= len(MEMBERS), 'W_CONJ_K %d exceeds the %d members' % (K, len(MEMBERS))
assert TRAJ_LB >= 1 and XCRS_LB >= 1 and XCRS_XWOB >= 1


def _secs(name):
    """'g15Mage' -> 15 seconds. 'ws3Mage' -> 180 seconds. LD's first argument is SECONDS."""
    body = name[:-4] if name.endswith('Mage') else name
    if body.startswith('ws'):
        return int(body[2:]) * 60
    if body.startswith('g'):
        return int(body[1:])
    raise ValueError('cannot read a timeframe out of %r' % (name,))


class Conj:
    """The conjunction over one tape. Build once, then `fires` and `cross_for`."""

    def __init__(self, sc):
        n = len(sc.ts)
        self.n = n
        self.sc = sc
        self.hi, self.lo = float(sc.HI), float(sc.LO)
        self.px = np.asarray(sc.PX, float)[:n]
        self.mg = {}
        self.conf = {+1: {}, -1: {}}
        for nm in MEMBERS:
            v = np.asarray(sc.LD(_secs(nm), 'Mage'), float)[:n]
            self.mg[nm] = v
            for side in (+1, -1):
                self.conf[side][nm] = np.array(sorted(
                    cf for c, cf, sd in oob_ib_cross(v, self.hi, self.lo, XWOB_MEM)
                    if (sd > 0) == (side > 0)))
        # the ANCHOR line's own r and Mage, for the divergence and the oob test
        self.pr = np.asarray(sc.LD(_secs(PATCH_ANCHOR), 'r'), float)[:n]
        self.pm = self.mg[PATCH_ANCHOR]
        self.m1 = (self.mg[GATE_LINE] if GATE_LINE in self.mg else
                   np.asarray(sc.LD(_secs(GATE_LINE), 'Mage'), float)[:n]) \
            if GATE_LINE else None
        self._str = {}

    # ---- the member test
    def _in_span(self, nm, j, side):
        """Has member `nm` confirmed its oob->ib cross within SPAN bars at or before `j`?"""
        a = self.conf[side][nm]
        if not len(a):
            return False
        i = int(np.searchsorted(a, j, 'right')) - 1
        return i >= 0 and (j - a[i]) < SPAN

    def strength(self, j, side):
        """The divergence's strength at bar `j`: d_osc / |d_px| from `jig.anchor_floater` on the
        patched line's r. -> None when the divergence does not fire. CAUSAL - anchor_floater reads
        only bars <= j."""
        key = (j, side)
        if key in self._str:
            return self._str[key]
        dr = -1 if side < 0 else +1
        af = anchor_floater(self.pr, self.px, dr, int(j))
        out = None
        if af is not None and af['fired'] and af['d_px']:
            ok = (af['d_osc'] > 0 and af['d_px'] < 0) if dr < 0 else \
                 (af['d_osc'] < 0 and af['d_px'] > 0)
            if ok:
                out = abs(af['d_osc']) / abs(af['d_px'])
        self._str[key] = out
        return out

    def patch_ok(self, j, side):
        """Joe's two conditions at bar `j`. -> (bool, why).

        1 READING C: the patched line is still oob on `side` AND at least one other member has
          confirmed inside the span.
        2 the divergence's strength has risen at least TRAJ_MIN percent over TRAJ_LB bars.
        """
        if not PATCH:
            return False, 'the patch is off'
        v = float(self.pm[j])
        oob = (v >= self.hi) if side > 0 else (v <= self.lo)
        if not oob:
            return False, '%s is not oob on the %s side' % (PATCH_ANCHOR,
                                                            'high' if side > 0 else 'low')
        others = [nm for nm in MEMBERS
                  if nm not in PATCH_LINES and self._in_span(nm, j, side)]
        if not others:
            return False, 'no other member has confirmed inside the span'
        now = self.strength(j, side)
        then = self.strength(j - TRAJ_LB, side) if j - TRAJ_LB >= 0 else None
        if now is None or then is None or then <= 0:
            return False, 'the divergence does not fire at both ends of the trajectory window'
        rise = 100.0 * (now / then - 1.0)
        if rise < TRAJ_MIN:
            return False, 'the trajectory rose %.1f%%, under the %.1f%% minimum' % (rise, TRAJ_MIN)
        return True, ('%s oob at %.2f, %d other member(s) in span, the trajectory rose %.1f%%'
                      % (PATCH_ANCHOR, v, len(others), rise))

    def fires(self, frm, side, until=None):
        """Every conjunction fire bar strictly after `frm`, on `side`. -> [(bar, members, patched)].

        A fire is a bar where the in-span count FIRST reaches K, with ws1Mage oob on `side` at that
        bar - Joe's gate.

        THREE WAYS A MEMBER IS IN:
          its own oob->ib confirmation inside the span
          the PATCH, Joe 1016 - both of PATCH_LINES are made true when `patch_ok` holds on the
            anchor. Not latched: he ruled it holds *"until conjunction fires"*, so it is re-read
            per bar and the first bar it carries the count to K is the fire
          the LATCH, Joe 1016 - once a LATCH_LINES member has confirmed inside this search, it
            stays in. One-way, scoped to the search

        CAUSAL: the count at `frm` is evaluated first and carried, so a conjunction already in
        effect at `frm` does not re-fire. That bug cost a whole leg on 2026-07-22. The latch starts
        EMPTY at `frm`, so nothing before the trade's open can latch a member in.
        """
        frm = int(frm)
        end = int(self.n - 1 if until is None else until)
        out = []
        latched = set()

        def count(j, latched):
            got, mem, patched = 0, [], False
            pend = []
            for nm in MEMBERS:
                if self._in_span(nm, j, side):
                    got += 1
                    mem.append(nm)
                    if nm in LATCH_LINES:
                        latched.add(nm)
                elif nm in latched:
                    got += 1
                    mem.append(nm + ' (latched)')
                elif nm in PATCH_LINES:
                    pend.append(nm)
            # A SPEED GUARD, NOT A RULE: the patch is only tested when it could carry the count to
            # K. `anchor_floater` is the expensive call and a 12-day scan is otherwise unusable.
            # got + len(pend) < K means the patch cannot reach K even if every pending line passes,
            # so skipping it cannot change any verdict.
            if pend and got + len(pend) >= K and self.patch_ok(j, side)[0]:
                for nm in pend:
                    got += 1
                    mem.append(nm + ' (patched)')
                patched = True
            return got, mem, patched

        prev, _m, _p = count(frm, latched)
        for j in range(frm + 1, end + 1):
            got, mem, patched = count(j, latched)
            if got >= K and prev < K:
                if self.gate_ok(j, side):
                    out.append((j, mem, patched))
            prev = got
        return out

    def gate_ok(self, j, side):
        """Joe 1015's gate on GATE_LINE, with the two slack units off by default. CAUSAL - the
        bars form looks only backward. No gate line means no gate."""
        if GATE_LINE is None or self.m1 is None:
            return True
        v = float(self.m1[j])
        if (v >= self.hi) if side > 0 else (v <= self.lo):
            return True
        if GATE_PTS > 0.0:
            near = (v >= self.hi - GATE_PTS) if side > 0 else (v <= self.lo + GATE_PTS)
            if near:
                return True
        if GATE_SLACK > 0:
            a = max(0, j - GATE_SLACK)
            w = self.m1[a:j + 1]
            if bool((w >= self.hi).any() if side > 0 else (w <= self.lo).any()):
                return True
        return False

    def trace(self, frm, side, until=None):
        """Per-bar rows for a report. -> [(bar, count, [members in], [missing], patched, latched)].

        THE SAME CODE PATH AS `fires` - a report must not re-implement the count, because a
        diagnostic that drifts from the mech is worse than none. 1016: it drifted once already.
        """
        frm = int(frm)
        end = int(self.n - 1 if until is None else until)
        rows = []
        latched = set()
        for j in range(frm, end + 1):
            got, mem, patched = 0, [], False
            pk = None
            for nm in MEMBERS:
                if self._in_span(nm, j, side):
                    got += 1
                    mem.append(nm)
                    if nm in LATCH_LINES:
                        latched.add(nm)
                elif nm in latched:
                    got += 1
                    mem.append(nm + ' (latched)')
                elif nm in PATCH_LINES:
                    if pk is None:
                        pk = self.patch_ok(j, side)[0]
                    if pk:
                        got += 1
                        mem.append(nm + ' (patched)')
                        patched = True
            base = [m.split(' ')[0] for m in mem]
            miss = [nm for nm in MEMBERS if nm not in base]
            gate = self.gate_ok(j, side)
            rows.append((j, got, mem, miss, patched, sorted(latched), gate))
        return rows

    def cross_for(self, fire, side, x, target):
        """The x-cross this conjunction selects. -> (cross bar, conf bar, 'back' or 'forward').

        Joe 1016: *"lookback from conjunction firing ... 3 is better than 2. xwob needs to be
        confirmed"*. So the window is the XCRS_LB bars ENDING at `fire`, and a cross counts only
        if its own XCRS_XWOB hold completed at or before `fire`. The LATEST such cross wins, being
        the one nearest the conjunction. When none is found the search runs FORWARD from `fire`,
        which is the behaviour before this knob existed.
            side +1 the conjunction is HIGH-side, so the exit x-cross is an UNDER-cross
            side -1 the conjunction is LOW-side, so it is an OVER-cross
        """
        fire = int(fire)
        over = side < 0
        on = (x > target) if over else (x < target)

        def held(k):
            e = min(k + XCRS_XWOB, self.n)
            return bool(on[k:e].all())

        best = None
        for k in range(max(1, fire - XCRS_LB), fire + 1):
            if not (on[k] and not on[k - 1]):
                continue
            cf = k + XCRS_XWOB - 1
            if cf > fire or not held(k):
                continue
            best = (k, cf, 'back')
        if best is not None:
            assert best[1] <= fire, 'the lookback returned a cross that is not yet confirmed'
            return best
        for k in range(max(1, fire), self.n):
            if not (on[k] and not on[k - 1]):
                continue
            if held(k):
                return k, k + XCRS_XWOB - 1, 'forward'
        return None, None, None
