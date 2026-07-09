"""optimus9.compute.compute_flags — inject DB-sourced behavioural flags into the pure compute layer.

`IndicatorComputer` is "Pure computation. No I/O." by contract, so it cannot read its own knobs. This module
is the ONE seam that reads them from `lp_config` and sets them. Single responsibility: config -> compute.

Call `load(db)` once per process, after the DB connects and BEFORE any window/line is built (lines are
computed at window-build time, so a flag flipped afterwards has no effect on an existing window).

Knobs (lp_config, `val` is a double -> numeric codes):
  lp_align_close_stamp   0 = legacy bar-OPEN stamp (mid-window base bars see their own window's future;
                             backtest-only leak, see docs/causal_lookahead_register.md A4)
                         1 = bar-CLOSE stamp (base bar sees the last COMPLETED HTF bar; Pine lookahead_off)
"""
import logging

from optimus9.compute.indicator_computer import IndicatorComputer

log = logging.getLogger(__name__)

DEFAULTS = {'lp_align_close_stamp': 0.0}


def _read(db):
    """lp_config name->val for the compute knobs; missing rows fall back to DEFAULTS."""
    out = dict(DEFAULTS)
    names = tuple(DEFAULTS)
    rows = db.execute(
        "SELECT name, val FROM lp_config WHERE name IN (%s)" % ','.join(['%s'] * len(names)),
        names, fetch=True) or []
    for r in rows:
        out[r['name']] = float(r['val'])
    return out


def load(db):
    """Read the compute knobs from lp_config and apply them. Returns the applied dict."""
    k = _read(db)
    IndicatorComputer.ALIGN_CLOSE_STAMP = bool(int(k['lp_align_close_stamp']))
    log.info("compute flags: ALIGN_CLOSE_STAMP=%s", IndicatorComputer.ALIGN_CLOSE_STAMP)
    return k
