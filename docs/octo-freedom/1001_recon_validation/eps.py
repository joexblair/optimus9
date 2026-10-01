import sys, json
sys.argv=['day.py']
import day, muts
am, lw = muts.install()
for label, s in (('cold 00:00', day.k0), ('seeded 24 h earlier', day.k0-17280)):
    live, arm, adr = am.run(day.mage, day.rig.DR, s, day.k1, day.KNOBS['arm_fence'], day.KNOBS['arm_wob'])
    eps = am.episodes(live, arm, adr, s, day.k1)
    inday = [e for e in eps if e[1] > day.k0]          # episodes live at some bar of 09-01
    print(json.dumps(dict(seed=label, episodes_touching_0901=len(inday),
        first=[day.U(inday[0][0]), day.U(inday[0][1]) if inday[0][1] <= day.k1 else 'open', inday[0][2]],
        second=[day.U(inday[1][0]), day.U(inday[1][1]), inday[1][2]])))
