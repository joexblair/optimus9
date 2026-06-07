"""Behaviour-by-example DoD for bl_grind.walk — the lookback trade trigger + stop metric.
Each test pins one semantic; correct the test if a semantic is wrong, then the code."""
from optimus9.analysis.bl_grind import walk, gated_vs_ungated, _dir_from_bny30

PIV = [(12, 'H'), (15, 'L'), (18, 'H')]                  # swing pivots on px


def _px():
    p = [100.0] * 20
    p[12], p[15], p[18] = 103, 99, 102
    return p


def _base():
    # bls3 at bar 10, bny30 OOB-hi (→short), an in-line short pk at bar 5
    comb = [0] * 20; comb[10] = 3
    oob = [0] * 20;  oob[10] = 1
    pk = [0] * 20;   pk[5] = -1
    return comb, pk, oob


def test_bls3_with_inline_pk_opens_trade():
    comb, pk, oob = _base()
    t = walk(comb, pk, _px(), oob, PIV, pk_lookback=11)
    assert len(t) == 1
    assert t[0]['open_i'] == 10 and t[0]['dir'] == -1    # entered at the bls3 bar, short
    assert t[0]['stop_pct'] == 3.0                        # next 'H'=12: |103-100|/100


def test_no_pk_in_lookback_no_trade():
    comb, pk, oob = _base()
    pk = [0] * 20                                         # no pk at all
    assert walk(comb, pk, _px(), oob, PIV, pk_lookback=11) == []


def test_pk_wrong_direction_no_trade():
    comb, pk, oob = _base()
    pk = [0] * 20; pk[5] = 1                              # long pk, not in line with the short gate
    assert walk(comb, pk, _px(), oob, PIV, pk_lookback=11) == []


def test_pk_outside_lookback_no_trade():
    comb, pk, oob = _base()
    pk = [0] * 20; pk[3] = -1                             # in-line but bar 3, outside a 5-bar window
    assert walk(comb, pk, _px(), oob, PIV, pk_lookback=5) == []
    pk = [0] * 20; pk[8] = -1                             # in-line and inside the 5-bar window
    assert len(walk(comb, pk, _px(), oob, PIV, pk_lookback=5)) == 1


def test_bny30_closed_no_trade():
    comb, pk, oob = _base()
    oob = [0] * 20                                        # gate closed everywhere
    assert walk(comb, pk, _px(), oob, PIV, pk_lookback=11) == []


def test_no_bls3_no_trade():
    comb, pk, oob = _base()
    comb = [0] * 20                                       # never completes
    assert walk(comb, pk, _px(), oob, PIV, pk_lookback=11) == []


def test_direction_polarity():
    assert _dir_from_bny30(+1) == -1                      # OOB-hi → short
    assert _dir_from_bny30(-1) == +1                      # OOB-lo → long


def test_gated_vs_ungated_stop():
    # in-line short pks at 5 and 16 (both bny30-open); only bar 5 precedes the bls3 at 10
    comb, pk, oob = _base()
    pk[16] = -1; oob[5] = 1; oob[16] = 1
    r = gated_vs_ungated(comb, pk, _px(), oob, PIV, pk_lookback=11)
    assert r['gated']['n'] == 1                           # one bls3-confirmed trade
    assert r['ungated']['n'] == 2                         # every in-line pk, gate removed
    assert 'avg_stop' in r['gated']                       # the #6 headline
