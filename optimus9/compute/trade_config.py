"""trade_config — the knobs the trade walk reads, in the DB, versioned, in its OWN table.

WHY NOT `wsf_dtf_v3_config`.  Spec §21.6: `leash_bank.knob_string` puts the wsf_dtf_v3 config version
INSIDE `wsl_knobs`, and the v7/v8 in the 121-row leash bank IS that version. Adding a knob there would
bump it to v11, and the next leash bank write would land at `v11_...` and split off from the rows every
report in this chain reads. §21.6: *"That consequence is Joe's to sanction, so nothing was written."*
He has not sanctioned it.

Joe 0929 asked for the knobs in the DB - *"db the knobs, configs, etc"* - so they go in a table of
their own. Nothing here touches `wsf_dtf_v3_config` and no banked row is orphaned. MINE, stated.

EVERY VALUE IS JOE'S, and each row carries where he said it.

`wtc_key` IS THE TRADE BANK'S KEY.  A knob change writes a new version and the trades land BESIDE the
old ones, never over them.
"""
TABLE = 'wsf_trade_config'

DDL = '''CREATE TABLE IF NOT EXISTS %s (
    wtc_pk      BIGINT AUTO_INCREMENT PRIMARY KEY,
    wtc_version INT          NOT NULL,
    wtc_name    VARCHAR(40)  NOT NULL,
    wtc_value   VARCHAR(40)  NOT NULL,
    wtc_units   VARCHAR(80)  NULL,
    wtc_source  VARCHAR(200) NOT NULL,
    UNIQUE KEY uq_wtc (wtc_version, wtc_name))''' % TABLE

V = 3

SEED = [
    ('rule1_fence_lo', '27.0', 'r points', 'Joe 0923: "the fence is 27:73"'),
    ('rule1_fence_hi', '73.0', 'r points', 'Joe 0923: "the fence is 27:73"'),
    ('oob_lo', '15.0', 'r points', 'Joe 0913: "oob is alwasy 15/85"'),
    ('oob_hi', '85.0', 'r points', 'Joe 0913: "oob is alwasy 15/85"'),
    ('div_tf', '1', 'the line the divergence runs on, ws1r', "Joe 0924, his own line set"),
    ('scenario_lines', 'ws2r,ws3r,gcws30r', 'the scenario leg oob set', "Joe 0924, his own list"),
    ('latch_tf', '13', 'the second latch line is ws13m',
     'Joe 0925: "dr-flip taken off the ws1Mage + ws13m latch"'),
    ('latch_wob', '8', 'bars = 40 s at the 5 s grid',
     'Joe 0926: "we have to stick on 8 - there is too many t s affected"'),
    ('mage_fence_lo', '25.0', 'the Mage fence the latch uses', 'build_wsf_dtf_v3'),
    ('mage_fence_hi', '75.0', 'the Mage fence the latch uses', 'build_wsf_dtf_v3'),
    ('leash_instance', 'v7', 'which wsf_leash coil_lines set the signals come from',
     'Joe 0929: "v7"'),
    ('gate', 'rule1_gate.open', 'the banked gate: the rule#1 leg OR the scenario leg',
     'Joe 0929: "using the gate that you validated in our shared sheet, col L"'),
    ('same_bar_priority', 'dr-flip', 'which fires when a sig_utc lands on a flip bar',
     'Joe 0929: "same bar priority: dr-flip"'),
    ('mae_cap', '0.70', 'PERCENT of the entry price. The adverse excursion that ends the trade',
     'Joe 0929: "confirming 0.7% stop", then "retain 0.7% as the stop" on the re-walked ladder'),
    ('stop_same_bar_priority', 'stop', 'which fires when the stop lands on an opposing sig_utc bar',
     'Joe 0929: "use stop"'),
]

# THE GATE WINDOW IS BACKWARD-ONLY. Joe 0929: "the -3.5 and + 3.5 logic is what's making it
# non-causal, so let's drop the forward and simply say: if I see the `r` lines correctly positioned
# (or the #1 mode that allows for divergence), inside of the last {knob:7} minutes, then rule#1 is
# qualified". There WAS a v1 carrying the old 3.5/3.5 window for the A/B; Joe 0929 dropped it once
# he had the numbers - "no V3, just v2", then "drop v1 config and its 166 rows".
_GATE_WINDOW = [
    ('rule1_back_min', '7.0', 'minutes BACK -> 84 bars',
     'Joe 0929: "inside of the last {knob:7} minutes"'),
    ('rule1_fwd_min', '0', 'minutes FORWARD. causal', 'Joe 0929: "let us drop the forward"'),
    ('rule1_run_clamp', 'window', 'a run stops at the window edge. causal',
     'Joe 0929: everything causal'),
]
SEED = SEED + _GATE_WINDOW


WALK_V = 4
"""THE `leash_walk` MECH'S OWN VERSION. `V` STAYS 3 AND NOTHING ON THE v7 CHAIN MOVES.

Joe 1001 ruled the walk is the strategy — *"there is no surviving mech that relies on `brk`, because
our verified strategy uses `WALK FIRES FROM` as our one and only signal"*. It is a DIFFERENT mech, so
by this module's own contract it gets its own version and its rows land beside v3's rather than over
them.

`V` is deliberately NOT bumped. `key()` reads `cfg['_version']`, so bumping it would move the key
every existing caller banks under — `sweep_v3_signal`, `measure_live_stop`, `build_wsf_trades` all
load `TC.V`. MINE, AND STATED: bumping `V` to 4 when the walk REPLACES the v7 chain as the default is
Joe's call, not a side effect of adding knobs. Until he makes it, `load(db, TC.WALK_V)` is explicit.

v4 CARRIES v3's ROWS PLUS THE WALK'S OWN. The walk still reads `rule1_*`, `oob_*`, `latch_*`,
`mage_fence_*` and `mae_cap` — it shares the gate, the dr latch and the stop with v3 — so v4 is v3
plus `_WALK`, not a replacement set.
"""

_WALK = [
    ('arm_line', 'ws5Mage', 'the line the arm watches',
     'Joe 0930: "I think that trigger is ws5Mage + dwell"'),
    ('arm_fence_lo', '25.0', 'Mage points. NOT oob, which is 15/85',
     'Joe 0930, on the wob sweep that selected it over 15/85'),
    ('arm_fence_hi', '75.0', 'Mage points', 'Joe 0930, same sweep'),
    ('arm_wob', '6', 'bars = 30 s at the 5 s grid. CONSECUTIVE bars oob on the dr side',
     'Joe 0930: "great. apply the suggested wobs and rebuild the table"'),
    ('arm_same_dr', '1', 'the arm dr MUST equal the signal dr',
     'Joe 1001: "you were right to require same dr. update the mech"'),
    ('walk_min_tf', '7', 'ws7. the lowest TF whose DEPARTURE counts toward `fall`',
     'Joe 1001: "those settings are good for now"'),
    ('walk_fall', '3', 'distinct departures from the momTF bucket needed to qualify the race',
     'Joe 0930: "Requiring three makes the race wait until the bucket has genuinely turned over"'),
    ('walk_race', '1', 'flat-run STARTS needed inside the lookback',
     'Joe 1001: "those settings are good for now"'),
    ('walk_frmin', '4', 'ws4. the lowest TF whose FLAT-RUN enters the race pool',
     'Joe 1001: "no need to sweep - those settings are good for now"'),
    ('walk_lb_bars', '48', 'bars = 4 min. the race lookback, TRAILING and inclusive of k',
     'Joe 0930: "allow for flat-runs that have completed their race in a {knob:4 minute} lookback"'),
    ('walk_ladder_lo', '4', 'ws4. the walk ladder, ascending', 'Joe 0930, the mech-dev ladder'),
    ('walk_ladder_hi', '23', 'ws23', 'Joe 0930, the mech-dev ladder'),
    ('walk_dr_line_a', 'ws1Mage', 'the dr latch pair, first line',
     'Joe 1001: "it needs to use whatever built my validated WALK FIRES FROM timestamps"'),
    ('walk_dr_line_b', 'ws13m', 'the dr latch pair, second line. HARDCODED as ws13 in Rig, NOT '
     'read from latch_tf', 'Joe 1001, same ruling. sweep_v3_signal.py:98'),
    ('walk_dr_fence_lo', '15.0', 'r points. THIS IS oob 15/85, NOT the Mage fence 25/75',
     'Joe 1001, same ruling. sweep_v3_signal.py:104 - hardcoded 15.0'),
    ('walk_dr_fence_hi', '85.0', 'r points. oob, not the Mage fence',
     'Joe 1001, same ruling. sweep_v3_signal.py:103 - hardcoded 85.0'),
    ('walk_dr_wob', '0', 'bars. NO wob - it latches on the FIRST bar both lines agree',
     'Joe 1001, same ruling. sweep_v3_signal.py:99-106 has no wob'),
    ('walk_rule1_back_min', '5.0', 'minutes BACK -> 60 bars. the walk only, NOT rule1_back_min',
     'Joe 1001, asked 5 or 7 for this row: "5". Overrides 7.0 for the walk. NEVER OOS d'),
]

SEED_V4 = SEED + _WALK


def key(cfg):
    """The stable key string for a config version. Goes in every banked trade row.

    THE STOP IS IN THE KEY AS WELL AS IN THE TABLE. Joe 0929-late asked for both - first *"put the
    cap in the key"*, then *"move MAE_CAP to the DB"*. The key makes the cap readable without
    joining to the config table; `wtc_version` is what actually guarantees the knob set.

    A config with no `mae_cap` row gives the bare key, which is the UNCAPPED mech - v2 and earlier.
    """
    k = 'wtc_v%d_%s_%s' % (cfg['_version'], cfg['leash_instance'], cfg['gate'].replace('.', ''))
    cap = cfg.get('mae_cap')
    return k if cap is None else '%s_mae%.2f' % (k, float(cap))


def seed(db, version=V):
    """Write `version` if it is not there. -> rows written.

    v3 ADDS `mae_cap` AND `stop_same_bar_priority` TO v2's 16 ROWS. It is a new version and not an
    edit of v2 because this module's own contract says so: *"A knob change writes a new version and
    the trades land BESIDE the old ones, never over them."* v2's rows stay in the table as the
    uncapped mech's knob set; `load(db, 2)` still reads them.
    """
    if version == V:
        rows = SEED
    elif version == WALK_V:
        rows = SEED_V4                    # the leash_walk mech - see WALK_V's note
    else:
        raise ValueError('%s holds versions %d and %d. Joe 0929 dropped v1.'
                         % (TABLE, V, WALK_V))
    db.execute(DDL)
    n = db.execute("SELECT COUNT(*) c FROM %s WHERE wtc_version=%%s" % TABLE,
                   (version,), fetch=True)[0]['c']
    if n:
        return 0
    db.executemany("INSERT INTO %s (wtc_version,wtc_name,wtc_value,wtc_units,wtc_source) "
                   "VALUES (%%s,%%s,%%s,%%s,%%s)" % TABLE,
                   [(version, a, b, c, d) for a, b, c, d in rows])
    return len(rows)


def load(db, version=V):
    """-> {name: value} with `_version`. Values stay strings; the caller casts."""
    db.execute(DDL)
    rows = db.execute("SELECT wtc_name,wtc_value FROM %s WHERE wtc_version=%%s" % TABLE,
                      (version,), fetch=True)
    if not rows:
        raise ValueError('%s has no version %d - run seed()' % (TABLE, version))
    out = {r['wtc_name']: r['wtc_value'] for r in rows}
    out['_version'] = version
    return out
