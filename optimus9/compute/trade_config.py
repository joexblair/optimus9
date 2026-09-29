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

V = 2                       # the live version. v1 is kept so its banked trades stay reproducible

_COMMON = [
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
]

# THE ONLY DIFFERENCE BETWEEN THE TWO VERSIONS IS THE GATE WINDOW.
#   v1  the original: 3.5 min each side, and a run measured forward with no bound. NOT causal
#   v2  Joe 0929: "drop the forward and simply say: if I see the `r` lines correctly positioned (or
#       the #1 mode that allows for divergence), inside of the last {knob:7} minutes, then rule#1 is
#       qualified"
_BY_VERSION = {
    1: [('rule1_back_min', '3.5', 'minutes BACK -> 42 bars', 'the original half-window'),
        ('rule1_fwd_min', '3.5', 'minutes FORWARD -> 42 bars. NOT CAUSAL', 'the original half-window'),
        ('rule1_run_clamp', 'none', 'a run walks forward unbounded. NOT CAUSAL', 'the v1 build')],
    2: [('rule1_back_min', '7.0', 'minutes BACK -> 84 bars',
         'Joe 0929: "inside of the last {knob:7} minutes"'),
        ('rule1_fwd_min', '0', 'minutes FORWARD. causal',
         'Joe 0929: "let us drop the forward"'),
        ('rule1_run_clamp', 'window', 'a run stops at the window edge. causal',
         'Joe 0929: everything causal')],
}
SEED = _COMMON + _BY_VERSION[V]


def key(cfg):
    """The stable key string for a config version. Goes in every banked trade row."""
    return 'wtc_v%d_%s_%s' % (cfg['_version'], cfg['leash_instance'], cfg['gate'].replace('.', ''))


def seed(db, version=V):
    """Write `version` if it is not there. -> rows written."""
    db.execute(DDL)
    n = db.execute("SELECT COUNT(*) c FROM %s WHERE wtc_version=%%s" % TABLE,
                   (version,), fetch=True)[0]['c']
    if n:
        return 0
    rows = _COMMON + _BY_VERSION[version]
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
