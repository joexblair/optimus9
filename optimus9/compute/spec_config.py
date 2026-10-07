"""spec_config — one knob table per spec, read from the DB. Joe 1006: *"anything that's currently
hardcoded in lazy-g and octo-freedom can go into their respective config tables now"*, and his
original instruction 0911, already quoted in v3_config.py: *"all hard-coded values need to be in the
db. create a config table for our spec"*.

ONE ROW PER KNOB, the shape `wsf_dtf_v3_config` has been carrying since 0911. Each row holds its own
provenance, which a wide table cannot:

    owner   'joe'  = Joe set the value.  'mine' = I picked it and he has not ruled it.
    fitted  1 = the value was chosen by SCORING AGAINST JOE'S LABELS. A fitted knob is not a
            measurement and must be re-declared as fitted every time it is quoted.
    in_key  1 = the knob changes rows, so it belongs inside the producer's knob string.
    source  Joe's words, or file:line for a value inherited from an existing producer.

VERSIONED. `version` is in the unique key, so changing a knob lands BESIDE the old value instead of
overwriting it, and an old run stays reproducible.

    from optimus9.compute.spec_config import spec_config
    C = spec_config(db, 'lazy_g_config')
    C['lin_hop']            # 2
    C.version               # 1
    C.key()                 # 'lazy_g_config.v1' - what goes in a producer's knob key
    C.fitted('swing')       # False -> say so when you quote it

WHY THE KNOB KEY CARRIES THE VERSION, NOT THE VALUES. 20+ in_key knobs spelled into one string
overflows os_knob_key VARCHAR(190) and is unreadable in Excel. The version resolves to the exact
knob set with one query, cannot drift from it, and changing any in_key knob forces a new version -
so a new version IS a new key. Joe reads `lazy_g_config.v1`; the values are one SELECT away.

v3_config.py IS NOT TOUCHED. 17 files import it and the live rig is one of them. Collapsing the two
readers is MVP2 work, task #25.
"""
import json

_CAST = {'int': int, 'float': float, 'str': str, 'json': json.loads}


def ddl(table, prefix):
    """CREATE TABLE IF NOT EXISTS for a spec config table. `prefix` is the column prefix, e.g. 'lgc'."""
    p = prefix
    return f'''CREATE TABLE IF NOT EXISTS {table} (
    {p}_pk       BIGINT AUTO_INCREMENT PRIMARY KEY,
    {p}_version  INT          NOT NULL,   -- in the unique key. A change lands beside, never over
    {p}_section  VARCHAR(32)  NOT NULL,   -- which part of the spec owns it
    {p}_key      VARCHAR(48)  NOT NULL,   -- the knob's name
    {p}_value    VARCHAR(255) NOT NULL,   -- the value, as text. {p}_type says how to read it
    {p}_type     VARCHAR(12)  NOT NULL,   -- int | float | str | json
    {p}_units    VARCHAR(32)  NULL,       -- bars, minutes, seconds, steps, r-points, timeframe, pct
    {p}_owner    VARCHAR(8)   NOT NULL,   -- 'joe' or 'mine'
    {p}_fitted   TINYINT      NOT NULL,   -- 1 = chosen by scoring against Joe's labels
    {p}_in_key   TINYINT      NOT NULL,   -- 1 = the knob changes rows
    {p}_source   VARCHAR(255) NOT NULL,   -- Joe's words, or file:line
    {p}_note     VARCHAR(255) NULL,
    UNIQUE KEY uq_{p} ({p}_version, {p}_key),
    KEY k_{p}_sec ({p}_version, {p}_section))'''


class SpecConfig(dict):
    """knob -> typed value, with the row metadata kept beside it."""

    def __init__(self, table, version, rows):
        super().__init__({r['k']: _CAST[r['t']](r['v']) for r in rows})
        self.table, self.version = table, version
        self.meta = {r['k']: r for r in rows}

    def key(self):
        """What a producer puts in its knob string. A knob change forces a new version."""
        return '%s.v%d' % (self.table, self.version)

    def fitted(self, k):
        return bool(self.meta[k]['fitted'])

    def owner(self, k):
        return self.meta[k]['owner']

    def in_key(self):
        """-> {knob: value} for every row flagged in_key, so a producer can print what it used."""
        return {k: self[k] for k in self if self.meta[k]['in_key']}

    def section(self, s):
        return {k: self[k] for k in self if self.meta[k]['section'] == s}


def spec_config(db, table, prefix=None, version=None):
    """Read a spec's knobs. `version` None reads the HIGHEST version. A SWEEP MUST PASS ONE."""
    p = prefix or ''.join(w[0] for w in table.split('_')[:-1]) + 'c'
    if version is None:
        r = db.execute('SELECT MAX(%s_version) v FROM %s' % (p, table), fetch=True)
        version = r[0]['v'] if r and r[0]['v'] is not None else None
    if version is None:
        raise LookupError('%s is empty - seed it before reading it' % table)
    rows = db.execute(
        'SELECT %s_key k, %s_value v, %s_type t, %s_units u, %s_owner owner, %s_fitted fitted, '
        '%s_in_key in_key, %s_section section, %s_source source FROM %s WHERE %s_version=%%s'
        % (p, p, p, p, p, p, p, p, p, table, p), (int(version),), fetch=True)
    if not rows:
        raise LookupError('%s has no rows at version %s' % (table, version))
    return SpecConfig(table, int(version), rows)
