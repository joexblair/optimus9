"""momo_config — read one machine's momentum knobs, and bind them for the duration of a block.

WHY THIS FILE EXISTS. Joe 0903: "I want the settings to be global per machine, ie dtf and wsf will
have their own config". Before this, the eleven knobs were module globals shared by every caller,
so a sweep run for one machine moved the other machine's verdict with no way to see it.

SRP. momo_core decides the verdict and owns no numbers. momo_config owns where the numbers come
from and decides nothing. The table is momo_config, built by build_momo_config.py.

THE TWO CALLS. The lookup takes A TIMEFRAME, not a machine name.
    bank = momo_bank(db, 20)               # timeframe 20 minutes. version=None reads the live bank
    with momo_config(bank):
        ... every momo_g / momo_g_why / momo_fit call in here uses that band's numbers ...

WHY A TIMEFRAME AND NOT A MACHINE NAME. Joe 0903: "wsf and dtf become internal labels that apply
to different indicator groups". The bands do not overlap - wsf owns 1..12 (Joe 0826) and domtf owns
13..27 (Joe 0813) - so a line's own timeframe already says which bank applies. Joe 0903 on task
#14, "instantiate dtf and consume its lines": a timeframe is computed once, by whichever machine
owns it, and consumed by the other. It is never computed twice under two different banks.

THE FAULT THIS SHAPE REMOVES. A caller that had to NAME its machine could name the wrong one, and
on 0903 that is exactly what happened at the module-global level - wsf ran on a bank swept for
dtf's ws20r. A caller that passes the timeframe it is already holding has nothing to get wrong.

BIND ONCE, AROUND THE LOOP - not per bar. momo_bank() hits the database; momo_config() only
rebinds module attributes and is cheap.

A SWEEP MUST PASS A VERSION. Carried over verbatim from line_config.py:167, for the same reason
stated there: reading the live bank during a sweep means a live config change mid-run silently
alters the run, and nothing on the rows says so.

UNBOUND RAISES. momo_core ships with its knobs set to None. A producer that calls the verdict
without naming its machine gets a plain error naming this file, not another machine's numbers.
That is the whole point of the split, so there is deliberately no default and no fallback.

NESTING. momo_gated.momo_window() still works inside a bound block - it rebinds the window and the
sample grid and restores them, exactly as before. Bind the bank on the outside, open the window on
the inside.

SUNSET, Joe 0903. RPL ("RPL is sunsetted"), the s46 path ("s46 is dead") and build_ws_momo
("sunset build_ws_momo") do not bind a bank and are not expected to run.
"""
from contextlib import contextmanager

from optimus9.compute import momo_core as MC
from optimus9.compute import momo_gated as MG

# the eleven knobs, column name -> where the value has to land.
# 'core' and 'gated' name the module whose global the verdict actually reads at call time.
# k_window lands nowhere: the CALLER uses it to size momo_window(), it is not read inside the fit.
KNOBS = {
    'momo_slope_min':     ('core',  'MOMO_SLOPE_MIN'),
    'momo_r2_min':        ('core',  'MOMO_R2_MIN'),
    'momo_window_min':    ('core',  'MOMO_WINDOW_MIN'),
    'momo_step_min':      ('core',  'MOMO_STEP_MIN'),
    'level_slack':        ('core',  'LEVEL_SLACK'),
    'curl_arc_min':       ('core',  'CURL_ARC_MIN'),
    'curl_vtx_lo':        ('core',  'CURL_VTX_LO'),
    'curl_vtx_hi':        ('core',  'CURL_VTX_HI'),
    'momo_fixed_samples': ('gated', 'MOMO_FIXED_SAMPLES'),
    'curl_r2_min':        ('gated', 'CURL_R2_MIN'),
    'k_window':           ('caller', None),
}
_MOD = {'core': MC, 'gated': MG}


def momo_bank(db, tf, version=None):
    """The momentum knobs for the bank that owns timeframe `tf`, as a dict.

        db       a DatabaseManager
        tf       the line's own timeframe in MINUTES. The bank whose band contains it is used
        version  None reads the LIVE bank - the highest version whose live-after date has passed.
                 An integer reads that exact bank. A SWEEP MUST PASS ONE.

    -> {'mech', 'tf_lo', 'tf_hi', 'version', and the eleven knob names}

    ONE DATABASE READ PER CALL. Hold the result across the inner loop; do not call it per bar.
    """
    tf = int(tf)
    if version is None:
        rows = db.execute(
            'SELECT * FROM momo_config WHERE mmc_tf_lo <= %s AND %s <= mmc_tf_hi '
            'AND mmc_live_after_dt <= NOW() AND mmc_version = '
            '  (SELECT MAX(mmc_version) FROM momo_config WHERE mmc_live_after_dt <= NOW())',
            (tf, tf), fetch=True)
    else:
        rows = db.execute('SELECT * FROM momo_config WHERE mmc_tf_lo <= %s AND %s <= mmc_tf_hi '
                          'AND mmc_version=%s', (tf, tf, int(version)), fetch=True)
    if not rows:
        raise LookupError(
            f"momo_config has no bank covering timeframe {tf} at version={version!r}. "
            f"The banded bands are wsf 1..12 and domtf 13..27. "
            f"Run: python3 build_momo_config.py --show")
    if len(rows) > 1:
        where = ', '.join(f"{r['mmc_mech']} {r['mmc_tf_lo']}..{r['mmc_tf_hi']}" for r in rows)
        raise LookupError(
            f"momo_config has {len(rows)} banks covering timeframe {tf}: {where}. "
            f"Bands in one version must not overlap - a timeframe has to name one bank.")
    r = rows[0]
    bank = {'mech': r['mmc_mech'], 'version': int(r['mmc_version']),
            'tf_lo': int(r['mmc_tf_lo']), 'tf_hi': int(r['mmc_tf_hi'])}
    for k in KNOBS:
        bank[k] = r[f'mmc_{k}']
    # the ints stay ints - momo_window() and the sample grid index with them
    for k in ('momo_window_min', 'momo_step_min', 'momo_fixed_samples', 'k_window'):
        bank[k] = int(bank[k])
    for k in ('momo_slope_min', 'momo_r2_min', 'level_slack', 'curl_arc_min',
              'curl_vtx_lo', 'curl_vtx_hi', 'curl_r2_min'):
        bank[k] = float(bank[k])
    return bank


@contextmanager
def momo_config(bank):
    """Bind `bank`'s numbers for the duration of the block, then put back whatever was there.

    NOT THREAD-SAFE, by construction - it mutates module state, the same way momo_window() does
    and for the same reason: momo_core reads its constants at call time, so there is nowhere else
    to put them without changing every one of the verdict's call sites.
    """
    prev = {}
    for col, (where, name) in KNOBS.items():
        if where == 'caller':
            continue
        m = _MOD[where]
        prev[(where, name)] = getattr(m, name)
        setattr(m, name, bank[col])
    # DERIVED, not knobs. momo_core computes both at import from the two it now receives, so they
    # have to be recomputed here or the fit would sample on the previous bank's grid.
    prev[('core', 'MOMO_STEP_BARS')] = MC.MOMO_STEP_BARS
    prev[('core', 'MOMO_SAMPLES')] = MC.MOMO_SAMPLES
    MC.MOMO_STEP_BARS = int(bank['momo_step_min']) * 12
    MC.MOMO_SAMPLES = int(bank['momo_window_min']) // int(bank['momo_step_min'])
    prev_bound = MC._BOUND
    MC._BOUND = f"{bank['mech']} tf{bank['tf_lo']}..{bank['tf_hi']} v{bank['version']}"
    try:
        yield bank
    finally:
        for (where, name), v in prev.items():
            setattr(_MOD[where], name, v)
        MC._BOUND = prev_bound
