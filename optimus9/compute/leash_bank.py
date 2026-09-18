"""leash_bank — the stretchy leash's exit timestamps, banked.

Joe 0917 asked for seven columns: # | source | dr | ACTIONABLE | signal | rows | moment first.

`signal` is Joe's name for the exit stamp, 0918. It is NOT always a ws1mage-rev event bar: on the
lookback route the rule prints the moment's END ROW, which the event only QUALIFIES. Measured over
the banked 121: 98 are a ws1mage_rev sig bar, 23 are the moment end row. One column, two kinds.
Each timestamp is stored twice, `_utc` and `_ms`, exactly as wsf_dtf_v3 stores wdv_utc / wdv_ms —
the UTC column is for reading, the ms column is what a walk joins on.

ONE JOB: persistence. The rule lives in coil_exit.py, the coil in stretchy_leash.py, the moments in
coil_moment.py. Nothing here decides anything.

THE UNIQUE KEY carries every knob that can move a row:
    wsl_knobs     the `stretchy_leash` in-key knobs, plus the config version they came from
    wsl_v3_knobs  the wsf_dtf_v3 key the moments were read from
    wsl_win       the walk window
    wsl_first_ms  the moment's first bar
A run at different knobs, a different source key, or a different window lands BESIDE the old rows.
Nothing is ever updated in place and nothing is dropped.
"""
TABLE = 'wsf_leash'

DDL = f'''CREATE TABLE IF NOT EXISTS {TABLE} (
    wsl_pk        BIGINT AUTO_INCREMENT PRIMARY KEY,
    wsl_knobs     VARCHAR(160) NOT NULL,   -- stretchy_leash in-key knobs + config version
    wsl_v3_knobs  VARCHAR(160) NOT NULL,   -- the wsf_dtf_v3 key the moments came from
    wsl_win       VARCHAR(48)  NOT NULL,   -- 'from..to', the walk window
    wsl_n         INT          NOT NULL,   -- Joe's '#', the moment's ordinal in the window
    wsl_source    VARCHAR(8)   NOT NULL,   -- CONFIRM | END
    wsl_dr        TINYINT      NOT NULL,
    wsl_act_utc   DATETIME(3)  NOT NULL,   -- ACTIONABLE, the exit bar
    wsl_act_ms    BIGINT       NOT NULL,
    wsl_sig_utc   DATETIME(3)  NULL,       -- `signal`: the exit stamp. sig bar OR the qualified moment end row
    wsl_sig_ms    BIGINT       NULL,
    wsl_rows      INT          NOT NULL,   -- rows in the confluence moment
    wsl_first_utc DATETIME(3)  NOT NULL,   -- moment first
    wsl_first_ms  BIGINT       NOT NULL,
    UNIQUE KEY uq_wsl (wsl_knobs, wsl_v3_knobs, wsl_win, wsl_first_ms),
    KEY k_act (wsl_act_ms),
    KEY k_sig (wsl_sig_ms))'''

COLS = ('wsl_knobs', 'wsl_v3_knobs', 'wsl_win', 'wsl_n', 'wsl_source', 'wsl_dr',
        'wsl_act_utc', 'wsl_act_ms', 'wsl_sig_utc', 'wsl_sig_ms', 'wsl_rows',
        'wsl_first_utc', 'wsl_first_ms')


def knob_string(C):
    """The stretchy_leash knobs that are in_key, as one stable string. Config version included so a
    knob change at a new version can never collide with the old rows."""
    keys = sorted(k for k, m in C.meta.items()
                  if m['wdc_section'] == 'stretchy_leash' and m['wdc_in_key'])
    body = '_'.join('%s%s' % (k, C.meta[k]['wdc_value'].replace('"', '').replace(' ', ''))
                    for k in keys)
    return 'v%d_%s' % (C.version, body)


def bank(db, rows, knobs, v3_knobs, win):
    """Insert `rows` if this (knobs, v3_knobs, win) is not already banked.

    `rows` is a list of dicts with the COLS fields minus the four key columns.
    -> (written, existing). Never updates, never deletes.
    """
    db.execute(DDL)
    n = db.execute(f'SELECT COUNT(*) c FROM {TABLE} WHERE wsl_knobs=%s AND wsl_v3_knobs=%s '
                   f'AND wsl_win=%s', (knobs, v3_knobs, win), fetch=True)[0]['c']
    if n:
        return 0, n
    db.executemany(
        f"INSERT INTO {TABLE} ({','.join(COLS)}) VALUES ({','.join(['%s'] * len(COLS))})",
        [(knobs, v3_knobs, win, r['n'], r['source'], r['dr'], r['act_utc'], r['act_ms'],
          r['sig_utc'], r['sig_ms'], r['rows'], r['first_utc'], r['first_ms']) for r in rows])
    return len(rows), 0
