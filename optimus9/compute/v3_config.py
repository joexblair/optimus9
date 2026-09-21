"""v3_config — the wsf-dtf-v3 spec's knobs, read from the DB. Joe 0911: "all hard-coded values need
to be in the db. create a config table for our spec".

ONE ROW PER KNOB, not one wide row. The spec is still forming, and a wide table needs a DDL change
every time Joe names a knob. Each row also carries its OWN provenance, which a wide table cannot:

    wdc_owner   'joe'  = Joe set the value.  'mine' = I picked it and he has not ruled it.
    wdc_fitted  1 = the value was chosen by SCORING AGAINST JOE'S LABELS. A fitted knob is not a
                measurement and must be re-declared as fitted every time it is quoted.
    wdc_source  Joe's words, or file:line for a value inherited from an existing producer.

VERSIONED like every other bank. `wdc_version` is in the unique key, so changing a knob lands
BESIDE the old value instead of overwriting it, and an old run stays reproducible.

    from optimus9.compute.v3_config import v3_config
    C = v3_config(db)                 # the live version, as a dict
    span = C['momo_span_min']         # 10
    C.fitted('momo_span_min')         # True  -> say so when you quote it
"""
import json

TABLE = 'wsf_dtf_v3_config'

DDL = f'''CREATE TABLE IF NOT EXISTS {TABLE} (
    wdc_pk       BIGINT AUTO_INCREMENT PRIMARY KEY,
    wdc_version  INT          NOT NULL,   -- in the unique key. A change lands beside, never over
    wdc_section  VARCHAR(32)  NOT NULL,   -- which part of the spec owns it
    wdc_key      VARCHAR(48)  NOT NULL,   -- the knob's name
    wdc_value    VARCHAR(255) NOT NULL,   -- the value, as text. wdc_type says how to read it
    wdc_type     VARCHAR(12)  NOT NULL,   -- int | float | str | json
    wdc_units    VARCHAR(32)  NULL,       -- bars, minutes, seconds, steps, r-points, ...
    wdc_owner    VARCHAR(8)   NOT NULL,   -- 'joe' or 'mine'
    wdc_fitted   TINYINT      NOT NULL,   -- 1 = chosen by scoring against Joe's labels
    wdc_in_key   TINYINT      NOT NULL,   -- 1 = it is inside a bank's knob string / unique key
    wdc_source   VARCHAR(255) NOT NULL,   -- Joe's words, or file:line
    wdc_note     VARCHAR(255) NULL,
    UNIQUE KEY uq_wdc (wdc_version, wdc_key),
    KEY k_sec (wdc_version, wdc_section))'''

_CAST = {'int': int, 'float': float, 'str': str, 'json': json.loads}


class V3Config(dict):
    """A dict of knob -> typed value, with the row metadata kept beside it."""

    def __init__(self, rows):
        super().__init__({r['wdc_key']: _CAST[r['wdc_type']](r['wdc_value']) for r in rows})
        self.meta = {r['wdc_key']: r for r in rows}
        self.version = rows[0]['wdc_version'] if rows else None

    def fitted(self, key):
        """True when this value was chosen by scoring against Joe's labels. SAY SO when you quote it."""
        return bool(self.meta[key]['wdc_fitted'])

    def owner(self, key):
        """'joe' or 'mine'. A 'mine' knob is re-flagged in every report that depends on it."""
        return self.meta[key]['wdc_owner']

    def source(self, key):
        return self.meta[key]['wdc_source']

    def section(self, name):
        return {k: self[k] for k, r in self.meta.items() if r['wdc_section'] == name}

    def fitted_keys(self):
        return sorted(k for k, r in self.meta.items() if r['wdc_fitted'])

    def mine_keys(self):
        return sorted(k for k, r in self.meta.items() if r['wdc_owner'] == 'mine')

    def with_overrides(self, **kw):
        """A SECOND INSTANCE of this config, with some knobs moved. -> a new V3Config.

        Joe 0920 asked for a separate stretchy-leash instance at coil_lines ["ws2","ws3"] with every
        other knob ported unchanged. The config is versioned globally - v3_config(db) takes
        MAX(version) - so there was no way to run two instances at once without bumping the version
        and moving every other producer with it.

        SRP: the knobs are this object's concern, so the override lives here and not in a producer.
        The ROW METADATA is rewritten too, not just the typed value, because leash_bank.knob_string
        builds the unique key from meta[k]['wdc_value']. An override that moved the value but not
        the metadata would bank the second instance UNDER THE FIRST INSTANCE'S KEY and the write
        would be silently refused as already-banked.

        Values arrive in the same shape as the caller would read them back - a list for a json
        knob, an int for an int knob - and are re-serialised into wdc_value.
        """
        rows = []
        for k, r in self.meta.items():
            d = dict(r)
            if k in kw:
                v = kw[k]
                d['wdc_value'] = json.dumps(v) if d['wdc_type'] == 'json' else str(v)
            rows.append(d)
        unknown = set(kw) - set(self.meta)
        if unknown:
            raise KeyError('no such knob: %s' % ', '.join(sorted(unknown)))
        return V3Config(rows)


def v3_config(db, version=None):
    """The spec's knobs at `version`, or the highest version banked."""
    db.execute(DDL)
    if version is None:
        r = db.execute(f'SELECT MAX(wdc_version) v FROM {TABLE}', fetch=True)
        version = r[0]['v'] if r and r[0]['v'] is not None else None
    if version is None:
        raise RuntimeError(f'{TABLE} is empty - run seed_v3_config.py')
    rows = db.execute(f'SELECT * FROM {TABLE} WHERE wdc_version=%s ORDER BY wdc_section, wdc_key',
                      (version,), fetch=True)
    if not rows:
        raise RuntimeError(f'{TABLE} has no rows at version {version}')
    return V3Config(rows)
