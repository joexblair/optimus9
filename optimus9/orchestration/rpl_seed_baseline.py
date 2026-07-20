"""Seed the rpl_config 'baseline' knob row — the flow reads THESE, nothing hardcoded."""
from optimus9 import DatabaseManager
from optimus9.config import get_db_config
from optimus9.db.rpl_event_store import RplEventStore

KNOBS = {
    'lines': {                     # name: [k_len|len, rsi|mult, stc, src]  (kline=4-tuple, bb=3-tuple)
        'r':  {'kind': 'kline', 'k_len': 7, 'rsi': 5, 'stc': 11, 'src': 'close'},
        'x':  {'kind': 'bb', 'length': 5,  'mult': 0.37, 'src': 'close'},
        'm':  {'kind': 'bb', 'length': 6,  'mult': 0.45, 'src': 'close'},
        'M':  {'kind': 'bb', 'length': 37, 'mult': 0.83, 'src': 'close'},
        's1M':  {'kind': 'bb', 'length': 37, 'mult': 0.83, 'src': 'close'},
        's1x':  {'kind': 'bb', 'length': 5,  'mult': 0.37, 'src': 'close'},
        's1m':  {'kind': 'bb', 'length': 6,  'mult': 0.45, 'src': 'close'},
        's30M': {'kind': 'bb', 'length': 37, 'mult': 0.83, 'src': 'close'},
        's1r':  {'kind': 'kline', 'k_len': 7, 'rsi': 5, 'stc': 11, 'src': 'close'},
        's30r': {'kind': 'kline', 'k_len': 7, 'rsi': 5, 'stc': 11, 'src': 'close'},
        's2r':  {'kind': 'kline', 'k_len': 7, 'rsi': 5, 'stc': 11, 'src': 'close'},
        's2m':  {'kind': 'bb', 'length': 6,  'mult': 0.45, 'src': 'close'},   # s1/s2 confirm predict_breach
        's2M':  {'kind': 'bb', 'length': 37, 'mult': 0.83, 'src': 'close'},
    },
    'tf_ceiling': 90,              # r-pred ladder top TF (min); frontier climbs 1..ceiling. 90 (0719: 60 clipped 12_03's s89 leg -> false late flip 06:03 vs true 04:54). sweepable
    'boundary': {'hi': 85.0, 'lo': 15.0},
    'fence': {'fh': 65.0, 'fl': 35.0},          # predict_breach engage band (r-pred ladder)
    'anti': 50.0,                               # anti-fence + s2r gate: side-of-50 midline
    'vmin': 8.0,                                # x-cross-pred coarse-velocity floor
    'carry_ms': 120000,                         # seam-carry window (2min)
    's2_tf_sec': 120,                           # fast current-bias filter TF
    'delegate_offset': 5,                       # flip_finisher delegates exh-5 TFs lower
    'delegate_tf_floor': 1,                      # delegate TF floor: max(floor, etf-offset). 1 (0719: TF2 exhaustion needs a real faster line, not floored at itself). sweepable
    'gcs5_r_tol': 4,                             # gcs5 reversal finisher: gcs5r may have been OOB within this many EVENT bars of the gcs5x*gcs5m cross (r drops out as the top rolls over). sweepable
    'wob_n': 9,                                 # cross_wob debounce bars for x*r flip cross. LOCKED 9 — 0720: 9->4 pulled 12_01's main-flip finisher 00:07:55->00:04:30 (wob_n is shared with the main flip provisional). s2-cycle timing lands via gcs5, not this.
    'div_net_min': 3,                           # flip_div entry: first >=N same-side votes
    'div_horizon_ms': 1800000,                  # div search window after flip (30min)
    's1s2_confirm_tol_ms': 240000,              # post-flip direction confirm: s1r & s2r same-side within this (swept: 240s hits 3/3)
    'xcp_bnd_offset': 4,                         # x-cross-pred only tests r within this of the boundary (r>HI-4 or r<LO+4). sweepable
    'xcp_tf_floor': 19,                          # look-back floor: x-cross-pred scans current_tf down to this TF. sweepable
    'override_latch_ms': 300000,                 # a higher-TF r-pred within this window (full 5s series) suppresses a lower x-cross-pred. sweepable
    'latch_depth': 5,                            # s30Mage finishing latch: points BEYOND the OOB boundary Mage must reach before latching. LOCKED 5 (0719 sweep: kills the shallow 12_01 00:04:30 poke -> 07:55; 12_02 in-band). sweepable
    'latch_dwell': 2,                            # s30Mage finishing latch: consecutive 5s bars Mage must hold past-depth before latching. LOCKED 2 (0719 sweep: 12_01 07:55, 12_02 03:30; dwell=1 -> 12_02 03:22). sweepable
    'finisher_s30r_boundary_slip': 4,            # 0720: finisher fires only when s30r sits within this of its OOB boundary (s30r>HI-4 / s30r<LO+4). Anchors the fire to a real s30r cycle. sweepable
    'finisher_s30r_near_dwell': 2,               # 0720: consecutive event bars s30r must hold within-slip before the fire counts (kills 08:55:50-type blips). sweepable
    'finisher_s1r_boundary_slip': 25,            # 0720: s1r must be within this of ITS OWN OOB boundary (s1r>HI-25 / s1r<LO+25) at the fire = the leg has reached its extreme. Rejects premature onside pokes (12_04 08:54 s1r=52). Sweep plateau 20-30. sweepable
}

db = DatabaseManager(**get_db_config()); db.connect()
st = RplEventStore(db)
pk = st.upsert_config('baseline', KNOBS, notes='rpl finisher: r-pred pulled, s30r+s1r boundary-slip gates 0720')
print(f'rpl_config baseline seeded rc_pk={pk}')
loaded = st.load_config('baseline')
print(f'readback anti={loaded["anti"]} s2_tf={loaded["s2_tf_sec"]} lines={len(loaded["lines"])}')
db.disconnect()
