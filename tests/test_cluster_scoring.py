"""
Tests for ClusterScoring._score_combo — swing-zone attribution + counts.
Returns (swing_capture, total_net, won, decided):
  swing_capture = Σ over VIABLE (in-zone) entries that WON
  total_net     = net over ALL signals
  won / decided = win counts over ALL signals (decided = won + stopped)
Outcomes are hand-fed to isolate the zone logic from walk_to_first_cross.
"""
import numpy as np

from optimus9.analysis.cluster_scoring import ClusterScoring


def _cs():
    return ClusterScoring.__new__(ClusterScoring)        # no DB for _score_combo


# one up-leg 0→4 peaking at 101.5; bar 6 a shallow (in-stop) pullback at 101.2
CLOSE = np.array([100.0, 100.5, 100.8, 101.0, 101.5, 101.0, 101.2, 101.0], float)
LEG_UP = [{'start': 0, 'end': 4, 'dir': 1, 'amp_pct': 1.5}]


def test_capture_winners_only_total_all_and_counts():
    # (1,+1) PRE winner; (2,-1) off-swing loser; (6,+1) POST winner in-band
    outc = {(1, 1): (0.9, True), (2, -1): (-0.4, False), (6, 1): (0.9, True)}
    cap, total, won, dec = _cs()._score_combo([(1, 1), (2, -1), (6, 1)],
                                              CLOSE, LEG_UP, 0.4, outc)
    assert round(cap, 4) == 1.8            # the two in-zone winners only
    assert round(total, 4) == 1.4          # all three: 0.9 - 0.4 + 0.9
    assert won == 2 and dec == 3           # 2 won, 1 stopped → decided 3


def test_in_zone_loser_excluded_from_capture_but_hits_total():
    outc = {(1, 1): (-0.4, False)}
    cap, total, won, dec = _cs()._score_combo([(1, 1)], CLOSE, LEG_UP, 0.4, outc)
    assert cap == 0.0                      # winners-only → not counted
    assert round(total, 4) == -0.4         # net still sees the loss
    assert won == 0 and dec == 1


def test_undecided_not_in_decided():
    outc = {(1, 1): (0.0, None)}            # never resolved within horizon
    cap, total, won, dec = _cs()._score_combo([(1, 1)], CLOSE, LEG_UP, 0.4, outc)
    assert cap == 0.0 and total == 0.0 and won == 0 and dec == 0


def test_post_entry_outside_stop_band_excluded():
    close = CLOSE.copy(); close[6] = 100.9          # 0.6% below peak > 0.4 stop
    outc = {(6, 1): (0.9, True)}
    cap, total, _, _ = _cs()._score_combo([(6, 1)], close, LEG_UP, 0.4, outc)
    assert cap == 0.0                      # outside post band → not viable
    assert round(total, 4) == 0.9          # still counts in total_net


def test_only_first_two_post_pks_counted():
    outc = {(5, 1): (0.9, True), (6, 1): (0.9, True), (7, 1): (0.9, True)}
    close = np.array([100, 100.5, 100.8, 101, 101.5, 101.3, 101.2, 101.1], float)
    cap, *_ = _cs()._score_combo([(5, 1), (6, 1), (7, 1)], close, LEG_UP, 0.4, outc)
    assert round(cap, 4) == 1.8            # first 2 post-peak only, not all three


def test_no_legs_no_catches():
    outc = {(1, 1): (0.9, True)}
    cap, total, won, dec = _cs()._score_combo([(1, 1)], CLOSE, [], 0.4, outc)
    assert cap == 0.0 and round(total, 4) == 0.9 and won == 1 and dec == 1
