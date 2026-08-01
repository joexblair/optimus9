"""report_momo_slip - query rpl_momo_slip. DB-only, no rebuild, no build imports (~1 s).

Compares four fire rules at a given momo_ride_oob_slip. Joe 0801: "s15's trigger is stashed and s22r's
momentum is tested. if s22 momo is false, allow s15's trigger to fire."

  today      A ungated - the first s15x X s15m cross at/after the walk bar
  slip       first cross with ms_gap <= slip              (either r line, whichever is closer)
  other      the line INSIDE the slip is the trigger; the OTHER line's momentum is tested. Joe's
             wording read literally.
  neither    ms_gap <= slip AND NEITHER line reads momo at that cross bar. Stricter - it also holds
             while the triggering line's own climb continues.

    python3 report_momo_slip.py [--slip 2.0] [--rows]
"""
import sys
import numpy as np
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

FIRE = {
    'slip':  "ms_cross_line = 's15' AND ms_gap <= %(s)f",
    # 'stash' = Joe's spec read literally: the line INSIDE the slip is the trigger, and the OTHER line
    # is the one whose momentum is tested. Testing the trigger against itself holds it while its own
    # climb continues, which walked 0522 14:15 from 16:30 to 0524 00:48.
    'other':  ("ms_cross_line = 's15' AND ("
               "(ms_gap15 <= ms_gap22 AND ms_gap15 <= %(s)f AND ms_s22_state <> 'momo')"
               " OR (ms_gap22 <  ms_gap15 AND ms_gap22 <= %(s)f AND ms_s15_state <> 'momo'))"),
    'neither': "ms_cross_line = 's15' AND ms_gap <= %(s)f AND ms_s15_state <> 'momo' AND ms_s22_state <> 'momo'",
}
RULES = ('slip', 'other', 'neither')

# Joe 0801, the patch - stateful, so it runs in Python over the ordered cross list, not in SQL:
#   IF s15 triggers when s22momo has bias-aligned momentum
#   THEN stash s15 trigger / walk forward
#   IF s15x triggers AND s4M is oob AND s4r is oob (all same-side) THEN fire
# same-side = the WALK side, which is also the bias-OOB side the slip test uses.
# When s22 is not momo at the s15 trigger, or s22 is itself the slip line, the patch does not apply
# and the plain slip fire stands.
# patch   = Joe's rule verbatim: fire on s4M oob AND s4r oob, same side. No s15r term at the fire.
# patchM  = the same with the s4r condition REMOVED - the permissive bound. A divergence test on s4r
#           replacing 's4r is oob' must land between patchM (any s4r) and patch (s4r fully OOB).
# (need_s4r, fire cross line).  STASH is always the s15x X s15m cross meeting the slip with s22 momo.
PATCH = {'p4.Mr': (True, 's4'), 'p4.M': (False, 's4'),
         'p15.Mr': (True, 's15'), 'p15.M': (False, 's15')}


HI, LO = 85.0, 15.0


def gap4(r, col):
    """r-units short of the walk-side boundary for an s4 line at this cross bar. <= 0 means OOB."""
    v = r[col]
    return (HI - v) if r['ms_eff_bias'] == 'bull' else (v - LO)


def rule_patch(rows, slip, need_s4r, fire_line, mslip=0.0, rslip=0.0):
    """mslip = the same slip idea applied to the s4Mage OOB test (Joe 0801: "test it before dropping
    s4r"). mslip 0 = the hard 85/15. rslip does the same for s4r; 0 = the hard boundary."""
    s15 = [r for r in rows if r['ms_cross_line'] == 's15']
    for r in s15:
        if r['ms_gap'] is None or r['ms_gap'] > slip:
            continue
        if r['ms_gap15'] is not None and r['ms_gap15'] <= slip and r['ms_s22_state'] == 'momo':
            for r2 in rows:                          # fire-line crosses at or after the stash bar
                if r2['ms_cross_line'] != fire_line or r2['ms_cross_ms'] < r['ms_cross_ms']:
                    continue
                if gap4(r2, 'ms_s4m_val') <= mslip and (
                        not need_s4r or gap4(r2, 'ms_s4r_val') <= rslip):
                    return r2
            return None
        return r                                     # patch does not apply - plain slip fire
    return None


def pick(d, where, slip):
    """one row per event: the first cross satisfying `where`."""
    q = '''SELECT s.* FROM rpl_momo_slip s
           JOIN (SELECT ms_v2_pk pk, MIN(ms_cross_ms) cm FROM rpl_momo_slip
                 WHERE %s GROUP BY ms_v2_pk) f
             ON f.pk = s.ms_v2_pk AND f.cm = s.ms_cross_ms
           WHERE s.ms_cross_line = 's15' ''' % (where % {'s': slip})
    return d.execute(q, fetch=True)


def today(d):
    return d.execute('SELECT * FROM rpl_momo_slip WHERE ms_is_sig = 1', fetch=True)


def agg(rows, n_all):
    mf = [r['ms_mfe'] for r in rows if r['ms_mfe'] is not None]
    ma = [r['ms_mae'] for r in rows if r['ms_mae'] is not None]
    rt = [r['ms_ratio'] for r in rows if r['ms_ratio'] is not None]
    lg = [r['ms_lag_min'] for r in rows]
    f = lambda v, q: float(np.percentile(v, q)) if v else float('nan')
    m = lambda v: float(np.median(v)) if v else float('nan')
    a = lambda v: float(np.mean(v)) if v else float('nan')
    return dict(n=len(rows), miss=n_all - len(rows), mae=m(ma), maem=a(ma), mae75=f(ma, 75),
                mae90=f(ma, 90), maex=(max(ma) if ma else float('nan')), mfe=m(mf), mfem=a(mf),
                rt=m(rt), rtm=a(rt), lag=m(lg), lagx=(max(lg) if lg else float('nan')))


def main(argv):
    slip = float(argv[argv.index('--slip') + 1]) if '--slip' in argv else 2.0
    d = DatabaseManager(**get_db_config()); d.connect()
    n_all = d.execute('SELECT COUNT(DISTINCT ms_v2_pk) c FROM rpl_momo_slip', fetch=True)[0]['c']
    allr = d.execute('SELECT * FROM rpl_momo_slip ORDER BY ms_v2_pk, ms_cross_ms', fetch=True)
    BY = {}
    for r in allr:
        BY.setdefault(r['ms_v2_pk'], []).append(r)
    sets = [('today   ', today(d))]
    for k in RULES:
        sets.append(('%-8s' % k, pick(d, FIRE[k], slip)))
    if '--msweep' in argv:
        print('')
        print('momo_ride_oob_slip = %.1f   s4Mage slip SWEEP, s4r condition RETAINED (hard 85/15)'
              % slip)
        print('')
        print('  fire  mslip |   n  nofire | MAE med  MAE mean  MAE p75  MAE p90  MAE max | MFE med'
              '  MFE mean | ratio med  ratio mean | lag med  lag max')
        print('  ' + '-' * 146)
        for fl in ('s15', 's4'):
            for m in (0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50):
                rr = [x for x in (rule_patch(v, slip, True, fl, m) for v in BY.values())
                      if x is not None]
                a = agg(rr, n_all)
                print('  %-4s %5.1f |  %2d   %4d  | %7.2f  %8.2f  %7.2f  %7.2f  %7.2f | %7.2f  %8.2f'
                      ' | %9.2f  %10.2f | %7.1f %8.1f'
                      % (fl, m, a['n'], a['miss'], a['mae'], a['maem'], a['mae75'], a['mae90'],
                         a['maex'], a['mfe'], a['mfem'], a['rt'], a['rtm'], a['lag'], a['lagx']))
            print('  ' + '-' * 146)
        d.disconnect(); return
    P = {}
    for k, (need, fl) in PATCH.items():
        P[k] = [x for x in (rule_patch(v, slip, need, fl) for v in BY.values()) if x is not None]
        sets.append(('%-8s' % k, P[k]))
    print('')
    print('momo_ride_oob_slip = %.1f    %d momo events    swing_detect 1.00%%' % (slip, n_all))
    print('')
    print('  rule     |   n  nofire | MAE med  MAE mean  MAE p75  MAE p90  MAE max | MFE med  MFE mean'
          ' | ratio med  ratio mean | lag med  lag max')
    print('  ' + '-' * 140)
    for nm, rows in sets:
        a = agg(rows, n_all)
        print('  %s |  %2d   %4d  | %7.2f  %8.2f  %7.2f  %7.2f  %7.2f | %7.2f  %8.2f | %9.2f  %10.2f'
              ' | %7.1f %8.1f'
              % (nm, a['n'], a['miss'], a['mae'], a['maem'], a['mae75'], a['mae90'], a['maex'],
                 a['mfe'], a['mfem'], a['rt'], a['rtm'], a['lag'], a['lagx']))
    print('  ' + '-' * 140)

    if '--rows' in argv:
        base = {r['ms_v2_pk']: r for r in today(d)}
        M = {k: {r['ms_v2_pk']: r for r in pick(d, FIRE[k], slip)} for k in RULES}
        for k in PATCH:
            M[k] = {r['ms_v2_pk']: r for r in P[k]}
        COLS = ('slip', 'p15.M', 'p4.M')
        miss = [pk for pk, r in base.items() if r['ms_ratio'] is not None and r['ms_ratio'] < 1.0]
        print('')
        print(' signal      | today ratio | slip  fire        ratio | p15.M fire        ratio'
              ' | p4.M  fire        ratio')
        print('-' * 122)
        for pk in sorted(miss, key=lambda p: base[p]['ms_cross_ms']):
            b = base[pk]; seg = ''
            for k in COLS:
                r = M[k].get(pk)
                seg += '| %-14s %8s ' % (r['ms_cross_utc'] if r else '   none    ',
                                         ('%.2f' % r['ms_ratio']) if (r and r['ms_ratio'] is not None)
                                         else '-')
            print(' %-11s | %11.2f %s' % (b['ms_sig_utc'], b['ms_ratio'], seg))
        print('-' * 122)
    d.disconnect()


if __name__ == '__main__':
    main(sys.argv[1:])
