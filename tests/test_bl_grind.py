"""Behaviour-by-example DoD for bl_grind.walk — the pk-lookback trigger + stop metric.
Each test pins one semantic; correct the test if a semantic is wrong, then the code."""
from optimus9.analysis.bl_grind import walk, gated_vs_ungated

PIV = [(12, 'H'), (15, 'L'), (18, 'H')]                  # swing pivots on px


def _px():
    p = [100.0] * 20
    p[12], p[15], p[18] = 103, 99, 102
    return p


def _base():
    # bls3 at bar 10; a curated short pk (raw_pk=-1) at bar 5
    comb = [0] * 20; comb[10] = 3
    pk = [0] * 20;   pk[5] = -1
    return comb, pk


def test_bls3_with_pk_opens_trade():
    comb, pk = _base()
    t = walk(comb, pk, _px(), PIV, pk_lookback=11)
    assert len(t) == 1
    assert t[0]['open_i'] == 10 and t[0]['dir'] == -1    # entered at bls3, in line with the short pk
    assert t[0]['stop_pct'] == 3.0                        # next 'H'=12: |103-100|/100


def test_no_pk_in_lookback_no_trade():
    comb, _ = _base()
    assert walk(comb, [0] * 20, _px(), PIV, pk_lookback=11) == []


def test_pk_outside_lookback_no_trade():
    comb, _ = _base()
    pk = [0] * 20; pk[3] = -1                             # bar 3, outside a 5-bar window ending at 10
    assert walk(comb, pk, _px(), PIV, pk_lookback=5) == []
    pk = [0] * 20; pk[8] = -1                             # bar 8, inside it
    assert len(walk(comb, pk, _px(), PIV, pk_lookback=5)) == 1


def test_no_bls3_no_trade():
    _, pk = _base()
    assert walk([0] * 20, pk, _px(), PIV, pk_lookback=11) == []


def test_most_recent_pk_sets_direction():
    # two pks in the lookback: short at 5, long at 8 → the most recent (long) wins
    comb, pk = _base()
    pk[8] = 1
    t = walk(comb, pk, _px(), PIV, pk_lookback=11)
    assert len(t) == 1 and t[0]['dir'] == 1              # long → next trough 'L'=15
    assert t[0]['stop_pct'] == 1.0                        # |99-100|/100


def test_gated_vs_ungated_stop():
    # curated pks at 5 and 16; only bar 5 precedes the bls3 at 10
    comb, pk = _base()
    pk[16] = -1
    r = gated_vs_ungated(comb, pk, _px(), PIV, pk_lookback=11)
    assert r['gated']['n'] == 1                           # one bls3-confirmed trade
    assert r['ungated']['n'] == 2                         # every curated pk, BL gate removed
    assert 'avg_stop' in r['gated']                       # the #6 headline
