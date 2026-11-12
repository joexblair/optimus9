"""ws{TF}e - ONE HOME for the line, shared by lift-off's e-cross reversal and the towards/away mech.

Joe 1109: *"build a new BB%B line named `e`, eg ws30e, with len 3, mult 0.5, src close. apply to ws4-ws30"* /
*"use the dynamic indicator config table: it saves you from creating 27 single lines"* / *"the common/shared
artifact is the newly built ws{TF}e"* / *"update the cache"*.

    the config    ONE row of mech_line_config: mechanic E_MECH 'towards-away', role 'e', version E_VERSION 2 -
                  BB%B 3|0.5|close, emerging, 60..1800 s every 60 s. docs/mech_line_config_spec.md. HIS 1110:
                  *"add ws1-3 to towards/away and liftoff, and update webUI"* - version 2 adds ws1e..ws3e;
                  version 1 (ws4..ws30) is sweep-only since 1110 (its live date moved to 2099)
    the arrays    the line cache (rpl_cache), keyed by spec like every cached line. A missing one is built;
                  nothing already there is touched
    the control   two known-good numbers from the 1109 check (cached = fresh in-memory build, max diff 0),
                  asserted on every load - a hash-keyed cache can serve a real but wrong array

Env overrides W_WSE_<NAME>. The towards/away knobs pin E_MECH and E_VERSION in their own ruled registry.
"""
import io
import os
import sys

import numpy as np

E_MECH = os.environ.get('W_WSE_E_MECH', 'towards-away')
E_VERSION = int(os.environ.get('W_WSE_E_VERSION', 2))
TF_LO, TF_HI = (4 if E_VERSION == 1 else 1), 30   # the row's band - asserted against the row on load
E_CONTROL_SUM = 2174735698.786861                # nansum over ws4e..ws30e, whole tape, 1109
E_CONTROL_AT = ('2026-08-25 03:28:00', 30, 99.629759)    # ws30e at that bar, 1109
E_CONTROL_SUM_1_3 = 241557997.374598           # nansum over ws1e..ws3e, whole tape, 1110 (cached = in-memory, diff 0)

_LINES = {}


def lines():
    """ws{TF_LO}e..ws30e from the line cache, building only a missing one. -> {tf: array}. Cached per process."""
    if _LINES:
        return _LINES
    import ln
    from optimus9.compute.line_config import mech_lines
    from optimus9.orchestration.build_ws_lines import HOURS, WARMUP
    from optimus9.orchestration import rpl_cache as RC
    from optimus9.config import get_db_config
    from optimus9 import DatabaseManager
    _s = sys.stderr; sys.stderr = io.StringIO()
    try:
        db = DatabaseManager(**get_db_config()); db.connect()
        rows = mech_lines(db, E_MECH, version=E_VERSION)
        db.disconnect()
    finally:
        sys.stderr = _s
    ovr = {}
    for d in rows:
        assert d['role'] == 'e' and d['tf_seconds'] % 60 == 0, d
        ovr['ws%de' % (d['tf_seconds'] // 60)] = d['override']
    tfs = sorted(int(k[2:-1]) for k in ovr)
    assert tfs == list(range(TF_LO, TF_HI + 1)), 'the ws{TF}e row covers %s, not ws%d..ws%d' % (tfs, TF_LO, TF_HI)
    pxs = {'src': ln._sy['s'], 'len': ln._sy['l']}
    assert os.path.exists(os.path.join(RC.TAPE_DIR, RC._tape_key(ln.EM, HOURS, WARMUP, pxs) + '.npz')), \
        'the tape file is missing - the cache call would write a new one'
    C = RC.cache_jig_perline(ln.EM, HOURS, WARMUP, ovr, pxs_cfg=pxs)
    out = {int(n[2:-1]): np.asarray(C.W.line(n), float)[:ln.N] for n in ovr}
    s = sum(float(np.nansum(out[t])) for t in range(4, 31))
    when, tf, v = E_CONTROL_AT
    if E_MECH == 'towards-away' and E_VERSION in (1, 2):
        assert abs(s - E_CONTROL_SUM) <= 1e-9 * abs(E_CONTROL_SUM) and abs(out[tf][ln.K(when)] - v) < 1e-6, \
            'the cached e lines differ from the 1109 known-good numbers (%.6f, %.6f)' % (s, out[tf][ln.K(when)])
    if E_MECH == 'towards-away' and E_VERSION == 2 and E_CONTROL_SUM_1_3 is not None:
        s3 = sum(float(np.nansum(out[t])) for t in (1, 2, 3))
        assert abs(s3 - E_CONTROL_SUM_1_3) <= 1e-9 * abs(E_CONTROL_SUM_1_3), \
            'the cached ws1e..ws3e differ from the 1110 known-good number (%.6f)' % s3
    _LINES.update(out)
    return _LINES


def build_in_memory(tfs):
    """ws{tf}e for `tfs` built IN MEMORY, never cached, with a ws30Mage control row. -> {tf: array}.

    The reference the cache is checked against when a line is added - his 1109 cache check, repeated 1110.
    """
    import ln
    from optimus9.analysis.jig import Jig
    from optimus9.compute.line_config import override, BBLine
    from optimus9.orchestration.build_ws_lines import HOURS, WARMUP
    ovr = {'ws%de' % t: override(int(t) * 60, BBLine(3, 0.5, 'close').as_tuple(), 'emerging') for t in tfs}
    ovr['ws30Mage_control'] = override(1800, ln.SPEC['Mage'][0], 'emerging')
    with Jig(ln.EM, hours=HOURS, warmup=WARMUP, overrides=ovr) as j:
        got = {n: np.asarray(j.W.line(n), float)[:ln.N] for n in ovr}
    c, ref = got.pop('ws30Mage_control'), np.asarray(ln.line('ws30Mage'), float)
    assert (np.isnan(c) == np.isnan(ref)).all() and np.nanmax(np.abs(c - ref)) == 0.0, 'the control row differs'
    return {int(t): got['ws%de' % t] for t in tfs}
