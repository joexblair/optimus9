"""
Tests for ClusterScoring._score_combo — the swing-zone attribution.
near_swing = Σ over VIABLE (in-zone) entries that WON; total_net = net over ALL.
Outcomes are hand-fed to isolate the zone logic from walk_to_first_cross.
"""
import numpy as np

from optimus9.analysis.cluster_scoring import ClusterScoring


def _cs():
    return ClusterScoring.__new__(ClusterScoring)        # no DB for _score_combo


# one up-leg 0→4 peaking at 101.5; bar 6 a shallow (in-stop) pullback at 101.2
CLOSE = np.array([100.0, 100.5, 100.8, 101.0, 101.5, 101.0, 101.2, 101.0], float)
LEG_UP = [{'start': 0, 'end': 4, 'dir': 1, 'amp_pct': 1.5}]


def test_pre_and_post_winners_only_in_near_total_all():
    # (1,+1) PRE winner; (2,-1) off-swing loser; (6,+1) POST winner in-band
    outc = {(1, 1): (0.9, True), (2, -1): (-0.4, False), (6, 1): (0.9, True)}
    near, total = _cs()._score_combo([(1, 1), (2, -1), (6, 1)],
                                     CLOSE, LEG_UP, 0.4, outc)
    assert round(near, 4) == 1.8           # the two in-zone winners only
    assert round(total, 4) == 1.4          # all three: 0.9 - 0.4 + 0.9


def test_in_zone_loser_excluded_from_near_but_hits_total():
    # (1,+1) is PRE (in-zone) but a LOSER → not a catch, but still drags total
    outc = {(1, 1): (-0.4, False)}
    near, total = _cs()._score_combo([(1, 1)], CLOSE, LEG_UP, 0.4, outc)
    assert near == 0.0                     # winners-only → not counted
    assert round(total, 4) == -0.4         # net still sees the loss


def test_post_entry_outside_stop_band_excluded():
    close = CLOSE.copy(); close[6] = 100.9          # 0.6% below peak > 0.4 stop
    outc = {(6, 1): (0.9, True)}
    near, total = _cs()._score_combo([(6, 1)], close, LEG_UP, 0.4, outc)
    assert near == 0.0                     # outside post band → not viable
    assert round(total, 4) == 0.9          # still counts in total_net


def test_only_first_two_post_pks_counted():
    outc = {(5, 1): (0.9, True), (6, 1): (0.9, True), (7, 1): (0.9, True)}
    close = np.array([100, 100.5, 100.8, 101, 101.5, 101.3, 101.2, 101.1], float)
    near, _ = _cs()._score_combo([(5, 1), (6, 1), (7, 1)], close, LEG_UP, 0.4, outc)
    assert round(near, 4) == 1.8           # first 2 post-peak only, not all three


def test_no_legs_no_catches():
    outc = {(1, 1): (0.9, True)}
    near, total = _cs()._score_combo([(1, 1)], CLOSE, [], 0.4, outc)
    assert near == 0.0 and round(total, 4) == 0.9
