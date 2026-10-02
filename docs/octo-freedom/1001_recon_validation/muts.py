"""Mutation table for arm_state.py / leash_walk.py. Each is ONE textual change, applied alone.

(id, module, old, new, what it breaks). `old` must occur exactly once in the module source.
PROBES add counters only - behaviour unchanged - so dead-code claims can be counted on real bars.
"""
import os
import sys
import types

REPO = '/home/joe/thecodes'
SRC = {
    'arm_state': open(os.path.join(REPO, 'optimus9/compute/arm_state.py')).read(),
    'leash_walk': open(os.path.join(REPO, 'optimus9/compute/leash_walk.py')).read(),
}

MUTS = [
    # ---- arm_state ------------------------------------------------------------------------------
    ('A1', 'arm_state', "            self.arm_dr = 0\n            self._run = 0\n",
     "            self.arm_dr = 0\n",
     'MID cross no longer resets _run'),
    ('A2', 'arm_state',
     "        if mage_prev is not None and (mage_k - self.mid) * (mage_prev - self.mid) < 0:",
     "        if False:",
     'MID cross cancel removed entirely'),
    ('A3', 'arm_state', "* (mage_prev - self.mid) < 0:", "* (mage_prev - self.mid) <= 0:",
     'MID cross test inclusive (touching 50 cancels)'),
    ('A4', 'arm_state',
     "if oob and (self._run == 0 or dr_prev is None or int(dr_prev) == d):", "if oob:",
     'dr-consistency clause removed'),
    ('A5', 'arm_state',
     "oob = False if d == 0 else ((mage_k >= self.hi) if d > 0 else (mage_k <= self.lo))",
     "oob = (mage_k >= self.hi) if d > 0 else (mage_k <= self.lo)",
     'dr 0 guard removed'),
    ('A6', 'arm_state', "if self._run >= self.wob and not self.live:",
     "if self._run >= self.wob:",
     'arm bar re-set on every bar of the run (not the first)'),
    ('A7', 'arm_state', "if self._run >= self.wob and not self.live:",
     "if self._run > self.wob and not self.live:",
     'arm one bar late (run > wob)'),
    ('A8', 'arm_state', "((mage_k >= self.hi) if d > 0 else (mage_k <= self.lo))",
     "((mage_k > self.hi) if d > 0 else (mage_k < self.lo))",
     'fence test strict instead of inclusive'),
    ('A9', 'arm_state', "        return self.live, self.arm, self.arm_dr\n",
     "        if self.live and d != 0:\n            self.arm_dr = d\n"
     "        return self.live, self.arm, self.arm_dr\n",
     'arm_dr re-read from the bar dr while live (not carried)'),
    ('A10', 'arm_state', "        if self._k is not None and k != self._k + 1:\n            raise ValueError('ArmState",
     "        if False:\n            raise ValueError('ArmState",
     'consecutive-bar guard removed'),
    ('A11', 'arm_state', "            return j\n        j -= 1", "            return int(floor)\n        j -= 1",
     'warmup_from always returns floor (maximally loose)'),
    ('A12', 'arm_state', "            return j\n        j -= 1", "            return j + 1\n        j -= 1",
     'warmup_from one bar late (skips the cross bar)'),
    ('A13', 'arm_state', "            out[-1][1] = int(k)\n", "            out[-1][1] = int(k) - 1\n",
     'episodes end_bar = last live bar instead of first non-live'),
    # ---- leash_walk -----------------------------------------------------------------------------
    ('L1', 'leash_walk',
     "        if self._turn is None or self._qual is None:\n            return False\n"
     "        if k < max(self._turn, self._qual):",
     "        if self._qual is None:\n            return False\n        if k < self._qual:",
     'turn requirement removed'),
    ('L2', 'leash_walk', "and k > arm_bar:", "and k >= arm_bar:",
     'turn may land ON the arm bar (strictly-after bound removed)'),
    ('L3', 'leash_walk', "if float(cc_k) * arm_dr < float(cc_prev) * arm_dr:",
     "if float(cc_k) * arm_dr > float(cc_prev) * arm_dr:",
     'turn = coil ticks UP'),
    ('L4', 'leash_walk', "if float(cc_k) * arm_dr < float(cc_prev) * arm_dr:",
     "if float(cc_k) < float(cc_prev):",
     'turn ignores the arm dr sign'),
    ('L5', 'leash_walk', "            if t in self._departed:\n                continue\n", "",
     'qualify: a departed TF can depart again (not first-departure-only)'),
    ('L6', 'leash_walk', "self._elig = [t for t in self.ladder if t >= self.min_tf]",
     "self._elig = [t for t in self.ladder if t > self.min_tf]",
     'qualify: min_tf exclusive'),
    ('L7', 'leash_walk', "if self._ndep == self.fall:", "if self._ndep == self.fall + 1:",
     'qualify: fall off by one'),
    ('L8', 'leash_walk', "if self._ndep == self.fall:", "if self._ndep >= self.fall:",
     'qualify bar overwritten by every later departure'),
    ('L9', 'leash_walk', "            elif t in self._seen_mom:", "            else:",
     'qualify: departure without having been momentum-true'),
    ('L10', 'leash_walk', "self._pool = [t for t in self.ladder if t >= self.frmin]",
     "self._pool = [t for t in self.ladder if t > self.frmin]",
     'race pool: frmin exclusive'),
    ('L11', 'leash_walk', "if f and not self._fr_prev.get(t, False):", "if f:",
     'race: every flat-run bar counts as a start (level, not rising edge)'),
    ('L12', 'leash_walk', "        self._fr_prev = {}\n",
     "        self._fr_prev = getattr(self, '_fr_prev', None) or {}\n",
     'race: rising-edge memory carried across episodes'),
    ('L13', 'leash_walk', "        self._fr_starts = []\n",
     "        self._fr_starts = getattr(self, '_fr_starts', None) or []\n",
     'race: flat-run starts carried across episodes'),
    ('L14', 'leash_walk', "if sum(1 for x in self._fr_starts if lo <= x <= k) < self.race:",
     "if sum(1 for x in self._fr_starts if lo < x <= k) < self.race:",
     'race window exclusive of k - lb'),
    ('L15', 'leash_walk', ") < self.race:", ") <= self.race:",
     'race count off by one'),
    ('L16', 'leash_walk', "if sum(1 for x in self._fr_starts if lo <= x <= k) < self.race:",
     "if sum(1 for x in self._fr_starts if max(lo, self._turn, self._qual) <= x <= k) < self.race:",
     'race starts must be at or after scan (the docstring DO-NOT-FIX)'),
    ('L17', 'leash_walk', "        return bool(rev_ok)", "        return True",
     'rev leg ignored'),
    ('L18', 'leash_walk', "        if k < max(self._turn, self._qual):\n            return False\n", "",
     'k < max(turn, qual) clause removed'),
    ('L19', 'leash_walk', "            self._cur_arm = int(arm_bar)\n            self._reset_episode()",
     "            self._cur_arm = int(arm_bar)",
     'per-episode reset skipped on a new arm'),
    ('L20', 'leash_walk', "        if self._k is not None and k != self._k + 1:\n            raise ValueError('LeashWalk",
     "        if False:\n            raise ValueError('LeashWalk",
     'consecutive-bar guard removed'),
    ('L21', 'leash_walk', "a = max(int(c_), int(s_))", "a = int(s_)",
     'rev mask true from the CROSS bar (ignores sig_conf)'),
    ('L22', 'leash_walk', "b = min(int(n) - 1, int(s_) + int(lookback))",
     "b = min(int(n) - 1, int(s_) + int(lookback) - 1)",
     'rev lookback one bar short'),
    ('L23', 'leash_walk', "b = min(int(n) - 1, int(s_) + int(lookback))",
     "b = min(int(n) - 1, int(c_) + int(lookback))",
     'rev lookback anchored on sig_conf instead of the cross bar'),
    ('L24', 'leash_walk', "    adr = w.arm.arm_dr if w.arm.live else int(d_k)",
     "    adr = int(d_k)",
     'walk(): mom/fr/rev read on the bar dr, not the arm dr'),
]

PROBES = [
    # counts only - no behaviour change
    ('P_ltmax', 'leash_walk',
     "        if k < max(self._turn, self._qual):\n            return False\n",
     "        if k < max(self._turn, self._qual):\n            _PROBE['ltmax'] += 1\n            return False\n"),
    ('P_drcons', 'arm_state',
     "        if oob and (self._run == 0 or dr_prev is None or int(dr_prev) == d):",
     "        if oob and self._run > 0 and dr_prev is not None and int(dr_prev) != d:\n"
     "            _PROBE['drcons'] += 1\n"
     "        if oob and (self._run == 0 or dr_prev is None or int(dr_prev) == d):"),
    ('P_midrun', 'arm_state',
     "            self.arm_dr = 0\n            self._run = 0\n",
     "            self.arm_dr = 0\n"
     "            if self._run > 0:\n                _PROBE['midrun_nonzero'] += 1\n"
     "                _d = int(dr_k)\n"
     "                _o = False if _d == 0 else ((mage_k >= self.hi) if _d > 0 else (mage_k <= self.lo))\n"
     "                if _o:\n                    _PROBE['midrun_changes_outcome'] += 1\n"
     "            _PROBE['midcross'] += 1\n"
     "            self._run = 0\n"),
]


def mutated_source(mod, old, new):
    s = SRC[mod]
    c = s.count(old)
    if c != 1:
        raise RuntimeError('%s: old string occurs %d times' % (mod, c))
    return s.replace(old, new)


def install(arm_src=None, lw_src=None, probe=None):
    """Exec arm_state then leash_walk from source into sys.modules. -> (arm_mod, lw_mod)."""
    import optimus9.compute  # noqa: F401  (package must exist)
    pk = sys.modules['optimus9.compute']
    out = []
    for name, src in (('arm_state', arm_src or SRC['arm_state']),
                      ('leash_walk', lw_src or SRC['leash_walk'])):
        full = 'optimus9.compute.' + name
        m = types.ModuleType(full)
        m.__file__ = os.path.join(REPO, 'optimus9/compute/%s.py' % name)
        m._PROBE = probe if probe is not None else {}
        sys.modules[full] = m
        setattr(pk, name, m)
        exec(compile(src, m.__file__, 'exec'), m.__dict__)
        out.append(m)
    return out


def build(ids):
    """Sources for a set of mutation/probe ids applied together (probes only combine)."""
    arm, lw = SRC['arm_state'], SRC['leash_walk']
    table = {m[0]: m for m in MUTS}
    table.update({p[0]: (p[0], p[1], p[2], p[3], 'probe') for p in PROBES})
    for i in ids:
        _, mod, old, new, _ = table[i]
        if mod == 'arm_state':
            c = arm.count(old)
            assert c == 1, (i, c)
            arm = arm.replace(old, new)
        else:
            c = lw.count(old)
            assert c == 1, (i, c)
            lw = lw.replace(old, new)
    return arm, lw
