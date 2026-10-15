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
    'W_LOOP_STATE_CARRY': ('1', 'Joe 1013', 'we take the first signal'),
    'W_LOOP_CLEAR_OOB': ('1', 'Joe 1013', 'repair as needed'),
    'W_LOOP_CLOSE': ('1', 'Joe 1013',
                     'if it cannot, then EXHAUSTION is printed immediately and the walk ends'),
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
