"""handoff_routing — the handoff routing machine. Joe 0914 named it.

Joe's question that produced it: *"will it flow cleanly if I replace route 1's 'If not, place a
trade instead' with 'if not, delegate to the handoff routing machine'?"* - and then *"if so, build
a machine that handles both routes"*.

IT FLOWS, AND IT COLLAPSES THE TWO ROUTES INTO ONE. Joe 0914: *"route 1 would only open up if
ws4Mage and ws4r have exited their respective boundaries, ie that would be the first test in any
case"*. So there are not two routes with two entry points. There is ONE decision with a first test
and a fallback:

    1. THE ws4 PAIR TEST      ws4Mage out of bounds on the dr side, held for `mage_dwell` bars
                              AND ws4r outside momo-fence-r on the dr side, held for `r_wob`+1 bars
                              -> hand to dtf.                        (spec 17.2a branch A)
    2. THE HIGHER-LINE SCAN   otherwise, scan ws5 up to the wsf ceiling for momentum-true.
                              Any one line is enough - Joe 0914 C-2.
                              -> hand to dtf.
    3. OTHERWISE              -> the trade machine.                   (spec 17.2a branch B)

The consolidation Joe described on 0914 - *"ws[1,2,3,4]Mage are all not oob because the market is
consolidating"* - is not a separate route. It is step 1 failing, which is what step 2 is for.

SRP: this module DECIDES A ROUTE. It does not detect a ride end, it does not ride a line, it does
not place a trade, and it owns no threshold - every knob arrives from `wsf_dtf_v3_config`.

CAUSAL, with one stated delay. Every test reads bars at or before `k`, EXCEPT the divergence, whose
anchors are the 24 bars AFTER the test-point (spec 17.1 step 6). When the divergence is what
carries a line, the decision is knowable at the divergence's firing bar, up to 120 s later. The
returned `known_at` carries that bar so a caller never acts earlier than it may.
"""
import numpy as np

from optimus9.compute import momo_expiry as EX
import optimus9.compute.momo_core as X
from optimus9.compute.momo_config import momo_config
from optimus9.compute.momo_gated import momo_window, curl_gates


def _run_back(line, k, dr, lo, hi):
    """Length of the consecutive run ending at k with the line past the fence on the dr side."""
    n = 0
    for j in range(int(k), -1, -1):
        v = line[j]
        if not np.isfinite(v):
            break
        if EX.beyond(v, dr, lo, hi):
            n += 1
        else:
            break
    return n


def ws4_pair(m4, r4, k, dr, C):
    """Spec 17.2a branch A. ws4Mage out of bounds AND ws4r outside momo-fence-r, each held.

    ONE TEST PER LINE. Joe 0914 withdrew the both-lines-oob wording: "ahh - I did make a mistake
    when I said oob for them both".
    """
    o_lo, o_hi = float(C['oob_lo']), float(C['oob_hi'])
    m_lo, m_hi = EX.fence_edges(C['momo_fence_r'])
    m_run = _run_back(m4, k, dr, o_lo, o_hi)
    r_run = _run_back(r4, k, dr, m_lo, m_hi)
    m_ok = m_run >= int(C['mage_dwell'])
    r_ok = r_run >= int(C['r_wob']) + 1          # a wob of n spans n+1 bars
    return (m_ok and r_ok), {'mage': float(m4[k]), 'mage_run': m_run, 'mage_ok': m_ok,
                             'r': float(r4[k]), 'r_run': r_run, 'r_ok': r_ok}


def momentum_true(r, bank, cfg, k, dr, seam_dr, span_min):
    """The spec 17.1 step 10 verdict. `momo`, or a curl facing dr.

    Returns (is_true, verdict). The seam fact is measured elsewhere and handed in, per SRP.
    """
    b = dict(bank)
    b.update({q: cfg[q] for q in ('momo_slope_min', 'momo_slack_ref', 'momo_r2_min',
                                  'level_slack', 'momo_seam')})
    with momo_config(b), momo_window(span_min):
        f = X.momo_fit(r, dr, k, quad=True)
        f['seam_dr'] = bool(seam_dr)
        st, _ = X.verdict(f)
        if st == 'curl':
            ok, _ = curl_gates(f, gate2=True)
            st = 'curl' if ok else 'none'
    return st in ('momo', 'curl'), st


def route(k, dr, L, banks, seams, cfg, C, DR, divergence=None, span_min=10):
    """Where does this bar go - dtf, or the trade machine.

    k           the bar
    dr          +1 or -1
    L           {'r2'..'r12', 'm4', ...} the lines, on the 5 s grid
    banks       {tf: momo bank}
    seams       {tf: seam mask} - the dr-facing-seam fact per line
    cfg         the momentum config: momo_slope_min, momo_slack_ref, momo_r2_min, level_slack,
                momo_seam. Joe 0914 C-3: the ws2-ws4 config, used unchanged at every timeframe
    C           wsf_dtf_v3_config
    DR          the dr latch series, for the expiry's look-back bound
    divergence  optional callable(k, dr) -> firing bar or None. Runs ONLY for a line the verdict
                says none, per spec 17.1 step 6

    -> {'route': 'dtf'|'trade', 'why': str, 'known_at': bar, 'lines': [...], 'ws4': {...}}
    """
    lo = int(C['ride_tf_hi'])     # the highest timeframe the machine rides. Joe 0914, eyeballed
    hi = int(C['band_wsf_hi'])    # how far the scan reaches above it. Joe 0914 C-1: ws12
    i0 = EX.last_dr_change(DR, k)

    ok, ws4 = ws4_pair(L['m4'], L['r4'], k, dr, C)
    if ok:
        return {'route': 'dtf', 'why': 'the ws4 pair test passed', 'known_at': int(k),
                'lines': [], 'ws4': ws4, 'dr_from': int(i0)}

    live, known = [], int(k)
    for tf in range(lo + 1, hi + 1):
        r = L.get('r%d' % tf)
        if r is None:
            continue
        bitten, arm, bite, clear = EX.expired(r, k, dr, i0, C['momo_fence_r'], C['fence'],
                                              C['xwob'], C['return_bars'])
        if bitten:
            continue                                   # spec 18: expired, cannot be momentum-true
        t, st = momentum_true(r, banks[tf], cfg, k, dr, seams.get(tf, False), span_min)
        at = int(k)
        if not t and divergence is not None:
            fired = divergence(k, dr)
            if fired is not None:
                t, st, at = True, 'divergence', int(fired)
        if t:
            live.append({'tf': tf, 'r': float(r[k]), 'verdict': st, 'known_at': at})
            known = max(known, at)
    if live:
        return {'route': 'dtf', 'why': 'ws%d..ws%d carries momentum' % (lo + 1, hi),
                'known_at': known, 'lines': live, 'ws4': ws4, 'dr_from': int(i0)}
    return {'route': 'trade', 'why': 'the ws4 pair failed and no line above it carries momentum',
            'known_at': int(k), 'lines': [], 'ws4': ws4, 'dr_from': int(i0)}
