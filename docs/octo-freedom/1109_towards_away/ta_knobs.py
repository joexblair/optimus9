"""The new towards/away mech's knobs, BANKED. Joe 1109: *"bank the towards/away update"* and *"collect all knobs,
including any that aren't specifically called out as knobs"*.

BANKED MEANS THE DEFAULT MOVES AND AN OFF-RULED RUN REFUSES - his standing rule, in v4_knobs' own form. A run with
any knob below off its ruled value refuses unless it declares itself an experiment with W_TA_EXPERIMENT=1, and
check() returns every knob so the caller prints them first. Env overrides are W_TA_<NAME>.

THE FULL LIST - these knobs, the rules fixed in code, and the knobs read from their own homes - is in the spec,
docs/octo-freedom/1109_towards_away.md, section KNOBS. Read from their own homes, never re-declared here:
    v4_knobs        FDM_FNC_2080 20, FDM_EXF_READ 'either', FDM_EXF_EM_BARS 12 (the ex-20/80 reader)
                    LIFT_PTS 6, GAP_PER_TF 2.8, LIFT_TOL 2.0, LIFT_WOB 8 (lift-off) and OOB_LO 15 / OOB_HI 85
                    SP_XWOB 18 and the other SP_* (sweep-pivots, which makes the ws2Mage pivots)
    mech_line_config  the ws{TF}e line itself: BB%B len 3, mult 0.5, src close, emerging, every 60 s, ws4..ws30
"""
import os

EXPERIMENT = os.environ.get('W_TA_EXPERIMENT', '0') == '1'


def _knob(name, default, cast=float):
    return cast(os.environ.get('W_TA_' + name, str(default)))


#   THE LINES. HIS 1109 answer 10A: ws4r to ws30r, the lines that have an e line
TF_LO = _knob('TF_LO', 4, int)
TF_HI = _knob('TF_HI', 30, int)

#   ws{TF}e's row in mech_line_config, the dynamic config table: mechanic 'towards-away', role 'e', version 1
E_MECH = _knob('E_MECH', 'towards-away', str)
E_VERSION = _knob('E_VERSION', 1, int)

#   THE e RACE. His race:{boundary,Mage,r}, in the order a tie is reported. RACE_READ is the read of the r and
#   Mage it races to - 'closed_prev', the standard race (v4_fdm2.x_race), or 'emerging'
RACE = tuple(_knob('RACE', 'boundary,Mage,r', str).split(','))
RACE_READ = _knob('RACE_READ', 'closed_prev', str)

#   SCENARIO 2. His `{knob:5}` - the TFs under this TF that are read; his ">1" - more than this many must be AW;
#   his "within 2% of each other", answer 7A - 2.0 r-points between the latest two samples
UNDER = _knob('UNDER', 5, int)
UNDER_GT = _knob('UNDER_GT', 1, int)
PAIR_PTS = _knob('PAIR_PTS', 2.0)

#   SUPERSEDE. How a line goes past its stored extremum toward the target-side: 'strict' (past it) or
#   'inclusive' (at or past it). MINE - under his 9B the second sample can BE the stored extremum, and
#   'inclusive' would end that AW on the bar it starts
SUPERSEDE = _knob('SUPERSEDE', 'strict', str)

#   THE PSEUDO TRADES. HIS 1109: *"use ws2Mage pivots"*, the last pivot of each same-side run
PIVOT_LINE = _knob('PIVOT_LINE', 'ws2Mage', str)

#   THE RULED REGISTRY: knob -> (ruled value, units, provenance). check() compares the live value to it.
RULED = {
    'TF_LO': (4, 'TF', 'his 10A "ws4r to ws30r"; *"apply to ws4-ws30"*'),
    'TF_HI': (30, 'TF', 'his 10A'),
    'E_MECH': ('towards-away', 'config row', 'MINE - the mechanic name of the row; his words for the mech'),
    'E_VERSION': (1, 'config version', '*"no action.  leave it on len3"* - version 1 is len 3'),
    'RACE': (('boundary', 'Mage', 'r'), 'race lines', 'his race:{boundary,Mage,r}'),
    'RACE_READ': ('closed_prev', 'read', 'the standard race, v4_fdm2.x_race - my read (e), not corrected'),
    'UNDER': (5, 'TFs', 'his {knob:5}'),
    'UNDER_GT': (1, 'lines', 'his ">1"'),
    'PAIR_PTS': (2.0, 'r-points', 'his "within 2%", answer 7A'),
    'SUPERSEDE': ('strict', 'rule', 'MINE'),
    'PIVOT_LINE': ('ws2Mage', 'line', '*"use ws2Mage pivots"*'),
}


def live():
    """-> {knob: live value}, every knob in RULED."""
    g = globals()
    return {k: g[k] for k in RULED}


def check():
    """THE RULED CHECK. Refuses an off-ruled run unless W_TA_EXPERIMENT=1. -> [(knob, live, ruled, ok)]."""
    lv = live()
    rows = [(k, lv[k], RULED[k][0], lv[k] == RULED[k][0]) for k in RULED]
    off = [r for r in rows if not r[3]]
    if off and not EXPERIMENT:
        raise SystemExit('REFUSED - towards/away knobs off the bank: %s. Set W_TA_EXPERIMENT=1 to run them.'
                         % ', '.join('%s=%r (ruled %r)' % (k, v, rv) for k, v, rv, _ in off))
    return rows
