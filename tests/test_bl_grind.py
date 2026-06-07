"""Behaviour-by-example DoD for bl_grind.walk — the trade trigger + scoring.
Each test pins one semantic; correct the test if a semantic is wrong, then the code."""
from optimus9.analysis.bl_grind import walk, gated_vs_ungated, _dir_from_bny30

PIV = [(5, 'H'), (8, 'L'), (12, 'H'), (15, 'L')]      # swing pivots on px


def _px():
    p = [100.0] * 20
    p[4], p[5], p[8], p[12], p[15] = 100, 102, 98, 103, 99
    return p


def test_armed_pk_opens_a_short():
    # bls3 at bar 3 → first armed pk at bar 4 (bny30 OOB-hi) → short, scored to next peak
    comb = [0] * 20; comb[3] = 3
    pk = [0] * 20;   pk[4] = 1
    oob = [0] * 20;  oob[4] = 1
    t = walk(comb, pk, _px(), oob, PIV, arm_timeout=12)
    assert len(t) == 1
    assert t[0]['open_i'] == 4 and t[0]['dir'] == -1
    assert t[0]['stop_pct'] == 2.0                       # next 'H'=5: |102-100|/100
    assert t[0]['profit_pct'] == round(abs(98 - 102) / 102 * 100, 3)  # leg 5→8


def test_no_pk_within_timeout_no_trade():
    comb = [0] * 20; comb[3] = 3
    pk = [0] * 20;   pk[18] = 1                           # pk beyond the arm
    oob = [0] * 20;  oob[18] = 1
    assert walk(comb, pk, _px(), oob, PIV, arm_timeout=12) == []


def test_bny30_closed_no_trade():
    comb = [0] * 20; comb[3] = 3
    pk = [0] * 20;   pk[4] = 1
    oob = [0] * 20                                       # gate closed everywhere
    assert walk(comb, pk, _px(), oob, PIV, arm_timeout=12) == []


def test_no_bls3_no_trade():
    comb = [0] * 20                                      # never completes (no →3)
    pk = [0] * 20;   pk[4] = 1
    oob = [0] * 20;  oob[4] = 1
    assert walk(comb, pk, _px(), oob, PIV, arm_timeout=12) == []


def test_direction_polarity():
    assert _dir_from_bny30(+1) == -1                     # OOB-hi → short
    assert _dir_from_bny30(-1) == +1                     # OOB-lo → long


def test_long_scores_to_trough():
    comb = [0] * 20; comb[3] = 3
    pk = [0] * 20;   pk[4] = 1
    oob = [0] * 20;  oob[4] = -1                          # OOB-lo → long → next trough 'L'=8
    t = walk(comb, pk, _px(), oob, PIV, arm_timeout=12)
    assert len(t) == 1 and t[0]['dir'] == 1
    assert t[0]['stop_pct'] == 2.0                       # |98-100|/100


def test_gate_filters_vs_ungated():
    # two armed-eligible pks (bars 4, 10); only bar 4 follows a bls3
    comb = [0] * 20; comb[3] = 3
    pk = [0] * 20;   pk[4] = 1; pk[10] = 1
    oob = [0] * 20;  oob[4] = 1; oob[10] = 1
    r = gated_vs_ungated(comb, pk, _px(), oob, PIV, arm_timeout=12)
    assert r['gated']['n'] == 1                          # only the armed pk
    assert r['ungated']['n'] == 2                        # every pk, gate removed
