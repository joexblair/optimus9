"""
Pairwise/coalition voting — exploration spike (r07 design riff, 2026-05-29).

NOT production code. Sandbox for testing the sub-vote hypothesis:
  Path A (hierarchical): probes vote within line -> line proposes or abstains
                         -> SnF across line proposals.
  Path B (flat):         all active probes vote in one pairwise contest.

SnF: Support = coalition agreement (with bonus); Friction = lack of agreement
(neutral probes + intra-line losers/abstainers). Signal fires iff Support>Friction.
"""
from typing import Optional

# ── DIALS (each is an open design question) ───────────────────────────
MULT          = 1.5    # multiline_weighting_mult — per-member coalition bonus
FRICTION_STR  = 1.0    # how strongly neutral/abstaining weight drags
PM_PROPOSES   = False  # if True: PM_LONG -> L coalition; if False: PM -> N (friction)

# ── inputs ────────────────────────────────────────────────────────────
# 3 lines × 2 probes; one probe zeroed -> 5 active probes, 5 distinct weights.
WEIGHTS = {
    ('line1', 'close'): 10,
    ('line1', 'wide'):   8,
    ('line2', 'close'):  5,
    ('line2', 'wide'):   3,
    ('line3', 'close'):  2,
    ('line3', 'wide'):   0,   # zeroed -> line3 is a single-probe voter
}
LINES         = ['line1', 'line2', 'line3']
ACTIVE_PROBES = [k for k, w in WEIGHTS.items() if w > 0]

# ── core voting machinery ─────────────────────────────────────────────
def normalise(d: str) -> str:
    """Map PM states under the current PM_PROPOSES rule."""
    if d in ('PML', 'PMS'):
        return {'PML': 'L', 'PMS': 'S'}[d] if PM_PROPOSES else 'N'
    return d

def coalition_strength(weights: list) -> float:
    """Sum with per-member coalition bonus when 2+ members."""
    if len(weights) >= 2:
        return sum(w * MULT for w in weights)
    return sum(weights)

def vote(voters: list) -> tuple:
    """voters: list of (weight, dir) where dir in {L,S,N,PML,PMS}.
    Returns (winner|None, winning_support, friction)."""
    norm = [(w, normalise(d)) for w, d in voters]
    longs    = [w for w, d in norm if d == 'L']
    shorts   = [w for w, d in norm if d == 'S']
    neutrals = [w for w, d in norm if d == 'N']
    sup_L    = coalition_strength(longs)
    sup_S    = coalition_strength(shorts)
    friction = sum(neutrals) * FRICTION_STR
    if sup_L == sup_S:
        return (None, 0, friction)
    winner = 'L' if sup_L > sup_S else 'S'
    return (winner, max(sup_L, sup_S), friction)

def fires(outcome: tuple) -> Optional[str]:
    """A vote fires its winning direction only if Support > Friction."""
    winner, sup, fric = outcome
    return winner if (winner and sup > fric) else None

# ── two interpretations ───────────────────────────────────────────────
def hierarchical(probe_dirs: dict) -> Optional[str]:
    """Path A: probes vote within line -> line proposes or abstains -> SnF."""
    line_proposals = []
    abstain_weight = 0
    for line in LINES:
        line_probes = [(WEIGHTS[(line, lab)], probe_dirs[(line, lab)])
                       for lab in ('close', 'wide')
                       if WEIGHTS[(line, lab)] > 0]
        if not line_probes:
            continue
        inner = vote(line_probes)
        winner = fires(inner)
        if winner is None:
            # Line abstains -> its total weight contributes to outer friction.
            abstain_weight += sum(w for w, _ in line_probes)
        else:
            # Line proposes its winner with its winning_support strength.
            line_proposals.append((inner[1], winner))
    longs  = [s for s, d in line_proposals if d == 'L']
    shorts = [s for s, d in line_proposals if d == 'S']
    sup_L  = coalition_strength(longs)
    sup_S  = coalition_strength(shorts)
    friction = abstain_weight * FRICTION_STR
    if sup_L == sup_S:
        return None
    winner = 'L' if sup_L > sup_S else 'S'
    return winner if max(sup_L, sup_S) > friction else None

def flat(probe_dirs: dict) -> Optional[str]:
    """Path B: all active probes vote in one contest."""
    voters = [(WEIGHTS[k], probe_dirs[k]) for k in ACTIVE_PROBES]
    return fires(vote(voters))

# ── sweep ─────────────────────────────────────────────────────────────
def sweep_with_shorts(n_short: int) -> dict:
    """First n_short active probes go S, rest L (in WEIGHTS dict order)."""
    return {k: ('S' if i < n_short else 'L') for i, k in enumerate(ACTIVE_PROBES)}

def print_run(title: str):
    print(f"\n=== {title}  (MULT={MULT}, FRICTION_STR={FRICTION_STR}, PM_PROPOSES={PM_PROPOSES}) ===")
    hdr = f"  split  | l1c(10) l1w(8) l2c(5) l2w(3) l3c(2)  |  flat  | hier "
    print(hdr); print('-' * len(hdr))
    for n in range(0, 6):
        dirs = sweep_with_shorts(n)
        probe_view = ' '.join(f' {dirs[k]:^4}' for k in ACTIVE_PROBES)
        print(f"  {5-n}L,{n}S  |{probe_view}  |  {str(flat(dirs)):^4}  |  {str(hierarchical(dirs)):^4}")

print_run("MAIN SWEEP — clean L/S split, shorts assigned in weight order")

# ── targeted: intra-line disagreement (where A vs B should diverge) ───
print("\n=== INTRA-LINE DISAGREEMENT (the hidden sub-vote bites here) ===")
scenarios = [
    # (name, probe_dirs)
    ("L1 split 10L/8S, L2 both L, L3=L",  {('line1','close'):'L',('line1','wide'):'S',
                                            ('line2','close'):'L',('line2','wide'):'L',
                                            ('line3','close'):'L',('line3','wide'):'L'}),
    ("L1 split 10L/8S, L2 both L, L3=S",  {('line1','close'):'L',('line1','wide'):'S',
                                            ('line2','close'):'L',('line2','wide'):'L',
                                            ('line3','close'):'S',('line3','wide'):'L'}),
    ("L1 split, L2 split, L3=S (chaos)",  {('line1','close'):'L',('line1','wide'):'S',
                                            ('line2','close'):'L',('line2','wide'):'S',
                                            ('line3','close'):'S',('line3','wide'):'L'}),
    ("All L except L3c neutral (friction)", {('line1','close'):'L',('line1','wide'):'L',
                                            ('line2','close'):'L',('line2','wide'):'L',
                                            ('line3','close'):'N',('line3','wide'):'L'}),
]
for name, dirs in scenarios:
    probe_view = ' '.join(f' {dirs[k]:^3}' for k in ACTIVE_PROBES)
    print(f"  {probe_view}  flat={str(flat(dirs)):>4}  hier={str(hierarchical(dirs)):>4}   ({name})")

# ── PM scenarios — toggle PM_PROPOSES to compare ──────────────────────
print("\n=== PM ROLE — PM_LONG joins long coalition vs PM acts as friction ===")
pm_scenarios = [
    ("L1c=L, L1w=PML, L2 both L, L3=S",   {('line1','close'):'L',('line1','wide'):'PML',
                                            ('line2','close'):'L',('line2','wide'):'L',
                                            ('line3','close'):'S',('line3','wide'):'L'}),
    ("L1 both PML, L2 split, L3=S",       {('line1','close'):'PML',('line1','wide'):'PML',
                                            ('line2','close'):'L',('line2','wide'):'S',
                                            ('line3','close'):'S',('line3','wide'):'L'}),
    ("Trend-cont scenario: 4 PMLs + 1 S",  {('line1','close'):'PML',('line1','wide'):'PML',
                                            ('line2','close'):'PML',('line2','wide'):'PML',
                                            ('line3','close'):'S',('line3','wide'):'L'}),
]
for proposes in (True, False):
    PM_PROPOSES = proposes
    print(f"\n  PM_PROPOSES={proposes}")
    for name, dirs in pm_scenarios:
        probe_view = ' '.join(f' {dirs[k]:^3}' for k in ACTIVE_PROBES)
        print(f"  {probe_view}  flat={str(flat(dirs)):>4}  hier={str(hierarchical(dirs)):>4}   ({name})")
