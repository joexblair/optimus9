"""seed_v3_config — every hard-coded value in the wsf-dtf-v3 chain.

V7, 0917: SIX KNOBS ADDED for the stretchy leash, section `stretchy_leash`. Joe named the mechanic
("stretchy leash", "coil", "the lookback ... is a bolt-on, not an overwrite") and set five of the
six values in this session. `support_min` is MINE - I used full support across the wsf and dtf
bands from the first confluence report and Joe worked with it, but he never named a floor. No
value moves: seeding takes them out of the scratchpad and into the bank. v1..v6 stay banked.

V5, 0915: ONE KNOB ADDED - momo_expiry.return_bars. Joe: "I agree with your natural anchor, n can
be 3 and swept (add the knob)". UNITS ARE BARS, and that is MINE: my sweep table was numbered in
wobs, where a wob of 2 spans the 3 bars of the anchor and a wob of 3 spans 4. Naming the knob in
bars makes both halves of Joe's sentence agree - the anchor IS 3, and n IS 3. It also steps around
the repo's own wob/bars split (momo_xwob and boundary_xwob are bars; ride_end.r_wob is steps).

V4, 0914: ONE KNOB ADDED - handoff.ride_tf_hi. Joe: "we're talking about the TF limit of wsf, and
where it belongs. I see it as a knob in a db table: 4 was chosen by eyeballing only, so we might
find that 5 is 'better' in a sweep". It is SEPARATE from band_subwsf and from band_wsf_hi, so a
sweep can move the ride ceiling without moving either band.

V3, 0914: FOUR KNOBS ADDED, no value changed. Two for the ride end (spec 17.2a) and two for the
momentum expiry (spec 18). Joe set all four values; the labels and the two section names are MINE
under his 0913 delegation - "I'll pass the knobs to you for labelling". v1 and v2 stay banked.

V2, 0912: momo_kill 'state' -> 'off', and chain_knobs follows it to ..._mkoff_... . Joe reversed
the 0820 demotion: "it was built for a different mechanic and will break our new spec". v1 stays
banked, so a run at the old reading is still reproducible.

Joe 0911: "all hard-coded values need to be in the db. create a config table for our spec".

NOTHING HERE IS A NEW DECISION. Every value is the one already running in the producer named in
`source`. Seeding does not move a single row; it moves where the value LIVES.

    python3 seed_v3_config.py          seed version 1
    python3 seed_v3_config.py --show   print what is banked
"""
import sys

from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.compute.v3_config import DDL, TABLE, v3_config

V = 7

# section, key, value, type, units, owner, fitted, in_key, source, note
ROWS = [
 # ── the bands, Joe 0911 ───────────────────────────────────────────────────────────────────────
 ('bands', 'band_subwsf', '["gcws30","ws1","ws2","ws3","ws4"]', 'json', 'lines', 'joe', 0, 0,
  'Joe 0911: "sub-wsf = gcws30 to ws4"', 'overlaps wsf on ws1..ws4, as Joe wrote it'),
 ('bands', 'band_wsf_lo', '1', 'int', 'timeframe', 'joe', 0, 0, 'Joe 0911: "wsf = the lines between ws1 and ws12"', None),
 ('bands', 'band_wsf_hi', '12', 'int', 'timeframe', 'joe', 0, 0,
  'Joe 0911: "ws12 is the max wsf line"; Joe 0826: "wsf is limited to TF12"', None),
 ('bands', 'band_dtf_lo', '13', 'int', 'timeframe', 'joe', 0, 0, 'Joe 0911: "ws13 belongs to dtf"', None),
 ('bands', 'band_dtf_hi', '23', 'int', 'timeframe', 'joe', 0, 0, 'Joe 0911: "dtf = ws13 to ws23"', None),

 # ── dr, spec section 2 ────────────────────────────────────────────────────────────────────────
 ('dr', 'dr_line_a', 'ws1Mage', 'str', None, 'joe', 0, 1, 'Joe 0909: "replace ws2Mage with ws1Mage"', None),
 ('dr', 'dr_line_b', 'ws13m', 'str', None, 'joe', 0, 1, 'Joe 0909', None),
 ('dr', 'dr_latched', '1', 'int', None, 'joe', 0, 1,
  'Joe 0909: "both oob, both same side. until that happens, the previous dr value holds"', None),
 ('dr', 'oob_hi', '85.0', 'float', 'r-points', 'joe', 0, 0, 'optimus9_system.hi_boundary', 'read live, mirrored here'),
 ('dr', 'oob_lo', '15.0', 'float', 'r-points', 'joe', 0, 0, 'optimus9_system.lo_boundary', 'read live, mirrored here'),

 # ── the wsf-dtf-v3 report, build_wsf_dtf_v3.py ────────────────────────────────────────────────
 ('v3_report', 'tf_lo', '1', 'int', 'timeframe', 'joe', 0, 1, 'Joe 0910: "add the ws1,2,3,4 r lines to the report"', None),
 ('v3_report', 'tf_hi', '23', 'int', 'timeframe', 'joe', 0, 1, 'Joe 0910: "increase the max r lines to ws23"', None),
 ('v3_report', 'fence_lo', '25.0', 'float', 'r-points', 'joe', 0, 1, 'Joe 0910: "increase the fence to 25/75"', None),
 ('v3_report', 'fence_hi', '75.0', 'float', 'r-points', 'joe', 0, 1, 'Joe 0910', None),
 ('v3_report', 'momo_span_min', '10', 'int', 'minutes', 'joe', 1, 1,
  'Joe 0910 chose it from a sweep: "these 2 line\'s feel less like fitting"',
  'THE SPAN, not the gap. At 21 fixed samples the gap is 30 s at EVERY timeframe'),
 ('v3_report', 'momo_slope_min', '0.4', 'float', 'r-points per sample step', 'joe', 1, 1,
  'Joe 0910, same sweep', 'overrides momo_config v1\'s 1.2'),
 ('v3_report', 'momo_bank_version', '1', 'int', None, 'joe', 0, 1, 'build_wsf_dtf_v3.py BANKV', None),
 ('v3_report', 'htf_lines', '[120,90,60,45,30]', 'json', 'timeframe', 'joe', 0, 0, 'Joe 0910', None),
 ('v3_report', 'mask_seq', '["g30","1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18"]',
  'json', None, 'joe', 0, 0, 'Joe 0910: "gcws30 then ws1..ws18"', '19 tags -> 18 adjacent pairs'),
 ('v3_report', 'xrace_hold', '5', 'int', 'bars', 'joe', 0, 0,
  'XCROSS_XWOB in build_wsf_x_cross.py', 'a 5-bar run spans 20 s. NOT in the unique key'),
 ('v3_report', 'warm_utc', '2026-08-23 00:00:00', 'str', None, 'mine', 0, 0,
  'build_wsf_dtf_v3.py WARM', 'the 21-sample lattice and the dr latch need history'),
 ('v3_report', 'win_from', '2026-08-25 00:00:00', 'str', None, 'joe', 0, 0, 'Joe 0910: "extend the report to 08-27 (full days)"', None),
 ('v3_report', 'win_to', '2026-08-28 00:00:00', 'str', None, 'joe', 0, 0, 'Joe 0910, same', None),

 # ── ws1mage-rev, jig.ws1mage_rev ──────────────────────────────────────────────────────────────
 ('ws1mage_rev', 'rev_wob', '2', 'int', 'steps', 'joe', 0, 1,
  'Joe 0911: "use these values, reversal:2, boundary:4. both are knobs"',
  'STEPS between bars. n steps span n x 5 s across n+1 bars'),
 ('ws1mage_rev', 'boundary_xwob', '4', 'int', 'bars', 'joe', 0, 1, 'Joe 0911, same message',
  'bars IB must hold. A knowledge delay, truncation-tested as NOT lookahead'),
 ('ws1mage_rev', 'dwell', '3', 'int', 'bars', 'mine', 0, 1,
  'Joe 0911: "ws1Mage needs to be oob for longer than the 03:29:20 dwell" (= 10 s)',
  'MINE - 3 bars is the smallest run strictly longer. Joe named no floor'),
 ('ws1mage_rev', 'sig_line', 'gcws30Mage', 'str', None, 'joe', 0, 1,
  'Joe 0910: "replace g30 x crossing Mage with g30Mage crossing boundary"', None),
 ('ws1mage_rev', 'sig_line_surgical', 'gcws15Mage', 'str', None, 'joe', 0, 1,
  'Joe 0910: "add a mode that uses gcws15 in place of gcws30, to make the signals more surgical"', None),

 # ── the wsf-model-report chain ────────────────────────────────────────────────────────────────
 ('wsf_chain', 'chain_knobs', 'kw6_fs21_sn6_hi85_lo15_r20.7_sl0.4_arc4_sk13.9_cr0.4_mkoff_mf17_xw4_sp10',
  'str', None, 'joe', 0, 1,
  'Joe 0911: "the key needs to reflect the settings that built the current wsf_dtf_v3 data"',
  'PROVEN: all 371 wsf_dtf_v3 rows at ws1..ws12 read sideways on it, 0 misses'),
 ('wsf_chain', 'stall_n', '6', 'int', 'lattice samples', 'joe', 0, 1, 'build_wsf_line_bar.py STALL_N, from build_ws_fin.py', None),
 ('wsf_chain', 'momo_fence_r', '17', 'int', 'r-points', 'joe', 0, 1, 'build_wsf_line_bar.py MOMO_FENCE_R', 'the 83/17 fence'),
 ('wsf_chain', 'momo_xwob', '4', 'int', 'bars', 'joe', 0, 1, 'build_wsf_line_bar.py MOMO_XWOB', None),
 ('wsf_chain', 'momo_kill', 'off', 'str', None, 'joe', 0, 1,
  'Joe 0912: "this verdict needs to be reversed - it was built for a different mechanic and will break our new spec"',
  "v1 was 'state' - Joe 0820's rule demoting a momentum-true line that is oob or stalled to none. 'off' = the producer's own verdict"),
 ('wsf_chain', 'grid_s', '5', 'int', 'seconds', 'joe', 0, 0, 'build_wsf_line_bar.py GRID_S', 'the base bar'),
 ('wsf_chain', 'xcross_target', 'r', 'str', None, 'joe', 0, 1, 'report_wsf_bar.py XCROSS_TARGET, Joe 0828',
  "'r' = x crosses its own r. 'race' = Mage, b, boundary"),
 ('wsf_chain', 'wmt_tf_lo', '2', 'int', 'timeframe', 'joe', 0, 1, 'report_wsf_bar.py WMT_TF_LO, Joe 0821 moved it from 1', None),
 ('wsf_chain', 'wmt_tf_hi', '12', 'int', 'timeframe', 'joe', 0, 1, 'report_wsf_bar.py WMT_TF_HI, Joe 0826', None),
 ('wsf_chain', 'threemage_dr', '0', 'int', None, 'joe', 0, 0,
  'Joe 0911: "drop the threemage dr mech. I\'m happy with our current dr mech"', '0 = dropped'),

 # ── the ride end, spec 17.2a, Joe 0913. Branch A hands to dtf; branch B is its negation ───────
 ('ride_end', 'mage_dwell', '12', 'int', 'bars', 'joe', 0, 0,
  'Joe 0913: "oob (15/85) with a dwell of {knob:12} (1 minute)"',
  'ws4Mage run on the dr side of 15/85 must REACH this. 12 bars = 60 s. Label mine'),
 ('ride_end', 'r_wob', '3', 'int', 'steps', 'joe', 0, 0,
  'Joe 0913: "r-momo-fence, wob {knob:3}"',
  'ws4r run outside momo-fence-r on the dr side. 3 steps SPAN 4 bars = 20 s. Label mine'),

 # ── the momentum expiry, spec 18, Joe 0914 ───────────────────────────────────────────────────
 ('momo_expiry', 'fence', '50', 'int', 'r-points', 'joe', 0, 0,
  'Joe 0914: "make the fence 50:50. add as a knob, we will sweep it later"',
  'fence knobs are 100 - the closest edge, so 50 = a 50:50 fence. SEPARATE from the flat-run '
  'signal\'s mid-zone fence, which stays 40/60 - Joe 0914 "(a)". Label and section mine'),
 ('momo_expiry', 'xwob', '5', 'int', 'bars', 'joe', 0, 0,
  'Joe 0914, answering M-2: "yes, xwob5"',
  'the line must hold past the expiry fence for this. Units BARS to match momo_xwob and '
  'boundary_xwob, the two xwob rows already here; 5 bars = 25 s. Label mine'),
 ('momo_expiry', 'return_bars', '3', 'int', 'bars', 'joe', 0, 0,
  'Joe 0915: "I agree with your natural anchor, n can be 3 and swept (add the knob)"',
  'the expiry does not bite until the line holds back inside momo-fence-r for this. ANCHORED to '
  'the flat-run signal\'s own 3 bars = 15 s - no knee in the sweep. Units bars, not wob: mine. '
  'SWEEP CANDIDATE'),

 # ── the test-point look-back, Joe 0916 ───────────────────────────────────────────────────────
 ('wsf_chain', 'tp_lookback_min', '4', 'int', 'minutes', 'joe', 0, 0,
  'Joe 0916: "idk - lets use {knob:4} minutes"',
  'at the established wsNMage oob, look BACK this far for an already-completed flat run; a hit '
  'means the test-point IS that anchor bar. 4 min = 48 bars. NO KNEE - Joe\'s choice ("idk"), not '
  'a measurement. Clipped at the dr stretch start. SWEEP CANDIDATE'),

 # ── the stretchy leash, Joe 0917. Producers: stretchy_leash.py, coil_moment.py, coil_exit.py ──
 ('stretchy_leash', 'coil_lines', '["gcws30","ws1"]', 'json', 'lines', 'joe', 0, 1,
  'Joe 0917: "note that the lower 30 sec coil will move/reverse before the 1 minute coil"',
  'the combined coil is the SUM of these lines\' coils, each dr-signed. coil = dr*((m+Mage)/2 - r)'),
 ('stretchy_leash', 'support_min', '23', 'int', 'lines', 'mine', 0, 1,
  'MINE - I used full support from the first confluence report and Joe worked with it',
  'how many of ws{band_wsf_lo}..ws{band_dtf_hi} must carry a POSITIVE coil for a row to join a '
  'moment. 23 = every line in the two bands. Joe named no floor. SWEEP CANDIDATE'),
 ('stretchy_leash', 'confirm_lag_s', '180', 'int', 'seconds', 'joe', 0, 1,
  'Joe 0917 swept it in 60 s steps, then banked the build that runs at 180: "these are good results"',
  'the coil must stay below its peak for this long before the turn-down is a release. 36 bars at '
  'the 5 s grid. 240 s scores +2.9 points of coil at the named bar and costs 2 confirmations'),
 ('stretchy_leash', 'lookback_s', '240', 'int', 'seconds', 'joe', 0, 1,
  'Joe 0917: "add a 4 minute lookback to capture ws1mage-rev when actionable fires"',
  'anchored on `named bar`. A ws1mage-rev inside it makes the named bar the actionable time. '
  '48 bars at the 5 s grid. NEVER applied to a confirmed release - Joe: "a bolt-on, not an overwrite"'),
 ('stretchy_leash', 'exit_anchor', 'named_bar', 'str', None, 'joe', 0, 1,
  'Joe 0917: "the lookback is anchored on `named bar`"',
  'the bar the lookback centres on. For a moment with no confirmed release that is the moment\'s '
  'end row - the last row still at support_min'),
 ('stretchy_leash', 'gap_fill', '1', 'int', None, 'joe', 0, 1,
  'Joe 0917: "the `events in between` are all perfect. use the first timestamp"',
  'when the lookback misses, take the FIRST ws1mage-rev strictly after the named bar and at or '
  'before the bar the moment\'s end becomes knowable. 0 = leave the actionable where it was'),

 # ── the hand-off, spec 17.2 / 19, Joe 0914 ───────────────────────────────────────────────────
 ('handoff', 'ride_tf_hi', '4', 'int', 'timeframe', 'joe', 0, 0,
  'Joe 0914: "4 was chosen by eyeballing only, so we might find that 5 is \'better\' in a sweep"',
  'the highest timeframe the machine RIDES. Separate from band_subwsf and band_wsf_hi so a sweep '
  'can move it alone. EYEBALLED by Joe, not swept. Label mine. See spec 19.2'),
]


def main(show=False):
    db = DatabaseManager(**get_db_config()); db.connect()
    db.execute(DDL)
    if show:
        C = v3_config(db)
        print(f'  {TABLE} v{C.version}: {len(C)} knobs', flush=True)
        print(f"  {'section':<14}{'key':<22}{'value':<28}{'units':<26}{'own':<6}{'fit':<5}{'key':<5}")
        for k in sorted(C.meta, key=lambda z: (C.meta[z]['wdc_section'], z)):
            m = C.meta[k]
            print(f"  {m['wdc_section']:<14}{k:<22}{m['wdc_value'][:27]:<28}{(m['wdc_units'] or '-'):<26}"
                  f"{m['wdc_owner']:<6}{('yes' if m['wdc_fitted'] else '-'):<5}"
                  f"{('yes' if m['wdc_in_key'] else '-'):<5}")
        print(f"\n  FITTED, re-declare every time quoted: {', '.join(C.fitted_keys()) or 'none'}")
        print(f"  MINE, unruled by Joe:                 {', '.join(C.mine_keys()) or 'none'}")
        db.disconnect(); return 0

    n = db.execute(f'SELECT COUNT(*) c FROM {TABLE} WHERE wdc_version=%s', (V,), fetch=True)[0]['c']
    if n:
        print(f'  {n} rows already banked at v{V} - nothing written', flush=True)
    else:
        db.executemany(
            f'INSERT INTO {TABLE} (wdc_version,wdc_section,wdc_key,wdc_value,wdc_type,wdc_units,'
            f'wdc_owner,wdc_fitted,wdc_in_key,wdc_source,wdc_note) '
            f'VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
            [(V, s_, k, v, t, u, o, f, ik, src, note) for s_, k, v, t, u, o, f, ik, src, note in ROWS])
        print(f'  banked {len(ROWS)} knobs at v{V}', flush=True)
    db.disconnect()
    return 0


if __name__ == '__main__':
    sys.exit(main('--show' in sys.argv))
