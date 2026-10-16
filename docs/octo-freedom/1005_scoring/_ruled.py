"""THE RULED SET — every knob Joe has ruled, its ruled value, and the words that ruled it. 1013.

WHY THIS FILE EXISTS. Joe 1013: *"this is concerning - now I don't know if all of our good work is
in-use, or if you're accidentally picking oudated logic"* / *"does this mean that when I say 'bank',
you're not fixing the config as 'confirmed and in-use'?"*. He was right. Every ruling of his lived
as an env-var DEFAULT, "bank" moved the spec doc and the commit message but not the default, and a
run that did not pass the env var silently used the superseded mech. The 2026-07-18 18:12:00 chain
walk is what that looks like: it armed on ws2Mage, which he replaced on 1011, and the SHORT never
armed at all.

HOW IT WORKS. `check()` compares the values a run is ACTUALLY using against this table and returns
the mismatches. `_chain10` prints the result as its first lines, so an off-ruled run says so before
it reports a single number - the same job the LIVE control row does for the line cache.

THE COVERAGE IS PRINTED, ON PURPOSE. There are 65 knob reads across the 1005_scoring modules and
this table covers the ones whose ruling is quoted in the repo. A table that silently claimed to
cover all 65 would be the same failure in a new coat, so the count goes in the output.

EVERY ENTRY CARRIES THE QUOTE. No entry is added from memory - if the words are not in the repo or
in the conversation, the knob does not go in here, it stays uncovered and the count says so.
"""

# knob -> (ruled value, when he ruled it, his words)
RULED = {
    'W_BP_ON': ('1', 'Joe 1016', 'bake the bounce-pred knobs, and the current state'),
    'W_BP_OFF_A': ('60', 'Joe 1016',
                   "landing on the 5TF seam gives us the most accurate picture of the lines, and "
                   "keeps us clear of the 'emerging bar jump at TF seam' issue / this leans us "
                   'towards using clean 5 minute bars'),
    'W_BP_OFF_B': ('120', 'Joe 1016',
                   'the 10 minute delay needed to mesaure the action of the higher TF\'s journey '
                   'is a necessary sacrifice of gross'),
    'W_BP_TRIG_TF': ('5', 'Joe 1016',
                     'it will only fire when ws5Mage is oob, and will fire on each ws5Mage '
                     'reversing until `continuance` is no longer printed'),
    'W_BP_LADDER_HI': ('30', 'Joe 1016', 'all TFs, thanks. step=1'),
    'W_BP_LADDER_LO': ('1', 'Joe 1016', 'all TFs, thanks. step=1'),
    'W_OCTO2_BP_PRIORITY': ('1', 'Joe 1016',
                            'bounce-pred has prioirty over turn-predictor'),
    # ---- THE 1016 BANK. Joe: *"g15 ws5/fwd/ex/xwob1/step1 +173.9969%. bank this as our state and make the machine live. no mom-xfer"*
    'W_OCTO2_GRID': ('g15ib', 'Joe 1016', 'g15 ws5/fwd/ex/xwob1/step1 +173.9969%. bank this as our state and make the machine live. no mom-xfer'),
    'W_G15_SIDE': ('ws5', 'Joe 1016',
                   'instead of a fixed width, collect samples on each g15Mage crossing back to '
                   'ib (on the target side)'),
    'W_G15_PAIR': ('fwd', 'Joe 1016', 'g15 ws5/fwd/ex/xwob1/step1 +173.9969%. bank this as our state and make the machine live. no mom-xfer'),
    'W_G15_FENCE': ('ex', 'Joe 1016', 'g15 ws5/fwd/ex/xwob1/step1 +173.9969%. bank this as our state and make the machine live. no mom-xfer'),
    'W_G15_XWOB': ('1', 'Joe 1016', 'g15 ws5/fwd/ex/xwob1/step1 +173.9969%. bank this as our state and make the machine live. no mom-xfer'),
    'W_G15_STEP': ('1', 'Joe 1016', 'g15 ws5/fwd/ex/xwob1/step1 +173.9969%. bank this as our state and make the machine live. no mom-xfer'),
    # MOM-XFER IS OFF BY HIS RULING, not by omission. Measured first: its best arm netted
    # +157.3814% against the banked g15 grid's +173.9969%, and he ruled it out.
    'W_MX_ON': ('0', 'Joe 1016', 'no mom-xfer'),
    # ---- `veto-on-momentum`, Joe 1016. HIS NAME, HIS MECH. The two VALUES are MINE and stated in
    # _vetomom.py; he named the filters, not the numbers.
    'W_VOM_ON': ('1', 'Joe 1016',
                'your "it is a veto on the close. The verdict\'s power to close the opposite '
                'side is suspended" is the correct view'),
    'W_VOM_TFS': ('3,4,5', 'Joe 1016',
                 'lost momentum is signalled by {knob:ws3-6} leading AWAY from oob and carrying '
                 'the ib tag, in a matryoshka pattern'),
    # THE TWO VALUES INSIDE veto-on-momentum ARE MINE, ruled here as MINE so the coverage count
    # does not pretend Joe set them. He named the filters; the numbers came from the measurement.
    'W_VOM_MIN_OUT': ('60', 'MINE 1016',
                      'the measured knee in his pass-50 claim: the no-50 rate runs 36.7% at 1 min, '
                      '23.4% at 2 min, 9.3% at 5 min, 6.3% at 10 min - 5 min is where it halves '
                      'and flattens. HIS CLAIM, which the filter confirmed: "it is very rare for a '
                      'ws4r and ws5r line to leave its source oob and then reverse and return to '
                      'source oob without passing 50 first"'),
    'W_VOM_LOOKBACK': ('240', 'MINE 1016',
                       'how far back the three departures may sit. At 5 min only 1 event of 2799 '
                       'matched; at 60 min the pattern fires on 9.50% of events; 20 min gives '
                       '36 = 1.29%. TWEAKABLE, and the fire count is thin at 35 over 94 days'),
    'W_VOM_XWOB': ('4', 'Joe 0911', 'use these values, reversal:2, boundary:4. both are knobs'),
    'W_CONJ_GATE_SLACK': ('4', 'Joe 1016',
                          'I agree. bake it along with all of the mechs that create the 7.9887'),
    'W_CONJ_K': ('5', 'Joe 1016',
                 'K=5 is preffered so that when ws3 does not print a divergence, we are still '
                 'exhibiting safe behaviour'),
    'W_CONJ_ROLES': ('g15Mage:latch,g30Mage:latch,ws1Mage:member+gate,ws2Mage:patch,'
                     'ws3Mage:patch+anchor', 'Joe 1015/1016',
                     "you should see the reversal happen in a cascade from g15Mage to ws2-3Mage "
                     "as they each cross from oob to ib / include ws2Mage. the logic: if ws3 is "
                     "printing a divergence, ws2 is naturally going to follow it / let's make the "
                     "flip from `missing` to `in` a one-way trip for g15. add also g30 to the "
                     "same regime / the turn signal can only fire if ws1Mage is same-side oob"),
    'W_CONJ_PATCH': ('1', 'Joe 1016',
                     'create a mech that needs 1) and 2) to qualify, then patches conjuncture so '
                     "that ws3Mage's input is made true"),
    'W_CONJ_TRAJ_LB': ('18', 'Joe 1016',
                       'the strengh has increased from 11135 to 18387 in 1.5 minutes'),
    'W_CONJ_TRAJ_MIN': ('25.0', 'Joe 1016',
                        "you'll need a minimum angle, which I won't be able to supply. use the "
                        'value that created the mech, + slack, we can tweak it later'),
    'CONJ_XCRS_LB': ('36', 'Joe 1016',
                     'lookback from conjunction firing. from your numbers, I think 3 is better '
                     'than 2. xwob needs to be confirmed'),
    'W_CONJ_XCRS_XWOB': ('8', 'Joe 1015', 'using an xwob8'),
    'W_CONJ_STANDDOWN': ('48', 'Joe 1016',
                         'require a 4 minute standdown after a trade is printed'),
    'W_CONJ_CAP': ('2', 'Joe 1015', 'max 2 same-target trades at any given time'),
    'W_LINEAGE_ROLE': ('confluence', 'Joe 1015', 'lineage is confluence only'),
    'W_ARM': ('cp', 'Joe 1011',
              'replace the current ws2Mage lineage walk qualifier with ws1-cp'),
    'W_ARM_TF': ('1', 'Joe 1009',
                 "exit-armed needs ws2Mage crossing into oob ... this is a constant thorn in our "
                 "side. let's swap ws2Mage with ws1Mage"),
    'W_KICK': ('off', 'Joe 1010', 'W_KICK off'),
    'W_LOOP_EXH': ('on_stall', 'Joe 1010',
                   'this is only true if the lineage walks to the loop-tf'),
    'W_LOOP_TF': ('10', 'Joe 1013', "we'll keep loop-tf at 10"),
    'W_CEIL': ('30', 'Joe 1013', 'ws30 is the ceiling'),
    'W_CP_DWELL': ('4', 'Joe 1012', 'add a 4 bar dwell to ws1cp'),
    'W_IB_DWELL': ('2', 'Joe 1013', 'bank, commit and push, make this machine live'),
    'W_CP_MODE': ('both', 'Joe 1012',
                  'we need mode 2 baked in so that jumpstart can fire on the 14:33 ws1-cp'),
    'W_STALL_N': ('6', 'Joe 1012', 'add the knob, sweep with 7 to 11'),
    'LIN_LASTMILE_KCKSTRT_TFCAP': ('7', 'Joe 1013', "let's fix the cap at 7"),
    'W_EXT_N': ('4', 'Joe 1013', 'if n >=4 then ride ws{mom_cont_tf}r until it is stalled'),
    'W_EXT_TF': ('10', 'Joe 1013', 'for 07-18 10:40, mom-cont-tf=10, n=4'),
    'W_EXT_LINE': ('dws', 'Joe 1013', "your proposal is good, let's bank it"),
    'W_EXT_FENCE': ('0', 'Joe 1013', 'the ws{mom-cont-tf}r stall can fire infence'),
    'W_EXT_EXIT': ('stall', 'Joe 1013', 'the numbers are fine. bank them as knobs'),
    'W_LOOP_END': ('oob', 'Joe 1013',
                   'lineage last-mile loops to ws1 on ws{loop-tf}r oob'),
    'W_MAE_STOP': ('1.1', 'Joe 1013',
                   "stops at 1.1 - we don't need 2.5 MAE now, that was for a different era"),
    # ---- THIS LAP'S SIX LOOP SWITCHES. Joe 1013: *"each of those changes are a knob - please
    # bank them in spec"*. The names are mine; every value is his.
    'W_LOOP_RIDER_GATE': ('0', 'Joe 1013',
                          'delete this. ws{loop-tf}r oob is the only qualification needed'),
    'W_LOOP_ONCE': ('1', 'Joe 1013', "the 'rider reset to ws1' is a one-time event"),
    'W_LOOP_JUMP_OFF': ('1', 'Joe 1013',
                        'if the loop cycles from loop-tf to ws1, the jumpstart is disabled'),
    'W_LOOP_CLEAR_OOB': ('1', 'Joe 1013', 'repair as needed'),
    'W_LOOP_CLOSE': ('1', 'Joe 1013',
                     'if it cannot, then EXHAUSTION is printed immediately and the walk ends'),
    'W_IB_SYNC': ('0', 'Joe 1014', 'set the sync tolerance to 0 and keep it as a knob'),
    # ---- THE CHAIN RESTART. His mech, his name 'restart-chain-on-loop-tf-oob'.
    'W_RESTART': ('1', 'Joe 1013', "A confirmed - build it and run the chain"),
    'W_RESTART_MAGE_DWELL': ('24', 'Joe 1013', 'ws1Mage has been IB for >24 bars'),
    'W_RESTART_AWAY_TFS': ('1,2,3', 'Joe 1013', "ws1-3r are printing 'away'"),
    'W_HTF_GATE': ('1', 'Joe 1013',
                   'if a trade closes when ws{>=30}r is oob, only open trades that are towards '
                   'the oob HTF line'),
    'W_HTF_X_WOB': ('48', 'Joe 1013',
                    'the restriction ends when ws30r is IB after ws60x-crosses r with a 48 wob'),
    'W_HTF_TFS': ('30,45,60,90', 'Joe 1013', 'ws{>=30}r'),
    'LG_TAPE_END': ('2026-10-05', 'Joe 1013',
                    'I need full state in the live machine without needing multiple versions of '
                    'the same arg'),
}

# W_ARM='lastmile' deliberately moves two of these. Joe 1013 ruled the mode itself, so inside it
# these are the ruled values and the check must not cry drift on them.
# KNOBS THE MACHINE READS WITH NO RULING OF JOE'S BEHIND THE VALUE. Banked here so the inventory is
# complete and so a sweep knows what is still open. Several have his words in a module docstring
# rather than a ruling on the number; those are marked with the docstring's source.
UNRULED = {
    'W_IB_REVWALK': ('60', "the 5-minute grace window. 'let's test this before I decide on the "
                           "grace window' - never decided, cost 0.2284% gross on three legs"),
    'W_IB_WOB': ('24', "the ws1Mage IB-cross hold. his 1012 mech, the 24 is mine"),
    'W_IB_CEIL': ('30', "the in-fence scan ceiling. his ladder is 'g5 to ws24, then 30,45,60,90'; "
                        "the cut at 30 is mine"),
    'W_IB_G30': ('1', "the g30Mage delegation. his 1013 'confirm the ws1cp-ib event is using "
                      "g30Mage as the line that crosses into ib'"),
    'W_IB_G30_BARS': ('6', 'bars past ws1Mage running extreme; mine'),
    'W_EXT_WS30': ('1', "his ws30 mode, 'let ws30 fire the hold and ride it' - the switch is mine"),
    'LIN_LASTMILE_MAX_GAP': ('24', "his 'set it to 24'"),
    'LINFIN_WALK_AWAY_MIN': ('2', 'mine, anchored to the three winners sitting at exactly 1'),
    'W_HTF_X_TF': ('60', "his 'ws60x-crosses r'; the knob name is mine"),
    'W_HTF_IB_TF': ('30', "his 'the restriction ends when ws30r is IB'"),
    'W_HTF_REN_WOB': ('0', 'the re-enable has no hold because he specified none'),
    'W_CP_XWOB': ('2', 'mine'),
    'W_NOX': ('1', 'the x-cross exit off; his 1009 "drop x-cross"'),
    'W_EXH_WHO': ('holders', 'mine'),
}

RULED_LASTMILE = {
    'W_KICK': ('high', 'Joe 1013', 'fires kickstart at the last-mile handoff'),
    'W_NO_GT12': ('1', 'Joe 1013', 'walk the last mile using lineage'),
    'W_PASS': ('crossing_to_ib', 'Joe 1013',
               "the new mode is 'crossing to ib' ... lineage-last-mile will baton pass on rider-tf "
               'returning to ib'),
    'W_ARM': ('lastmile', 'Joe 1013',
              "create a last-mile mode that doesn't rely on ws1cp and fires kickstart at the "
              'last-mile handoff'),
}

TOTAL_KNOB_READS = 65      # measured across _chain10 / _extmom / _momtrue / _ibmech / _gcgate / score39


def table(lastmile=False):
    t = dict(RULED)
    if lastmile:
        t.update(RULED_LASTMILE)
    return t


def check(active, lastmile=False):
    """active: {knob: the value the run is REALLY using}. -> [(knob, active, ruled, who, words)]"""
    out = []
    for k, (v, who, q) in table(lastmile).items():
        a = active.get(k)
        if a is None:
            continue
        if str(a).strip() != str(v).strip():
            out.append((k, str(a), str(v), who, q))
    return sorted(out)


def line(active, lastmile=False):
    """The one-or-more lines `_chain10` prints before anything else."""
    t = table(lastmile)
    seen = [k for k in t if k in active]
    off = check(active, lastmile)
    head = ('RULED CHECK — %d of %d knob reads are covered by the ruled set, %d of them read here'
            % (len(t), TOTAL_KNOB_READS, len(seen)))
    if not off:
        return [head + '; every one MATCHES its ruling']
    rows = [head + '; %d OFF-RULED:' % len(off)]
    for k, a, v, who, q in off:
        rows.append('  OFF-RULED  %-28s running %-16s ruled %-16s %s: "%s"'
                    % (k, a, v, who, q))
    return rows
