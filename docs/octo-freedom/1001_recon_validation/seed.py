"""CAUSALITY.md:35-39 says warmup_from(12:00:00) on 09-01 = 1,187 bars = 98.9 min, and seeding 3 h
earlier gives a bit-identical day. Check both against the repo code, unmutated.
"""
import json
import sys

sys.argv = ['day.py']
import day  # noqa: E402  (loads the rig once, exactly as the acceptance test does)
import muts  # noqa: E402
import numpy as np  # noqa: E402

am, lw = muts.install()
ts = day.ts
k12 = int(np.searchsorted(ts, day.ms0 + 12 * 3600 * 1000))
wf = am.warmup_from(day.mage, k12)
print(json.dumps(dict(check='warmup_from(12:00:00)', bars_back=k12 - wf, minutes=(k12 - wf) * 5 / 60.0,
                      seed_utc=day.U(wf))))

rev = {d: lw.rev_lookback_mask(day.legs[d]['sig'], day.legs[d]['sig_conf'], day.rig.n,
                               day.KNOBS['rev_lookback']) for d in (1, -1)}
base_mech, _ = lw.walk(day.lad, day.mage, day.rig.DR, day.rig.CC, day.mom_at, day.fr_at, rev,
                       day.k0, day.k1, **day.KNOBS)
wf0 = am.warmup_from(day.mage, day.k0)
for label, s in (('3 h before 00:00', day.k0 - 2160), ('warmup_from(00:00:00)', wf0),
                 ('24 h before 00:00', day.k0 - 17280)):
    mech, _ = lw.walk(day.lad, day.mage, day.rig.DR, day.rig.CC, day.mom_at, day.fr_at, rev,
                      s, day.k1, **day.KNOBS)
    inday = [k for k in mech if k >= day.k0]
    a, b = set(base_mech), set(inday)
    # is the arm live at 00:00:00 on the seeded walk?
    live, arm, adr = am.run(day.mage, day.rig.DR, s, day.k0, day.KNOBS['arm_fence'], day.KNOBS['arm_wob'])
    print(json.dumps(dict(seed=label, seed_bar_utc=day.U(s), bars_before_midnight=day.k0 - s,
                          mech_in_day=len(inday), mech_cold_midnight=len(base_mech),
                          only_seeded=len(b - a), only_cold=len(a - b),
                          arm_live_at_midnight=bool(live[day.k0]),
                          arm_bar_at_midnight=(day.U(int(arm[day.k0])) if live[day.k0] else None))))
