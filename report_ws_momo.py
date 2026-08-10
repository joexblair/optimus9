"""report_ws_momo — the pivot x TF table. Joe 0808.

    col A  the 1.11% swing pivot
    col B  the qualifying TFs (ws{TF}r crossed IB->OOB on the pivot's side within JUST_BEFORE_MIN)
    col C  the TF whose momo/curl fired CLOSEST to the ws1 marker nearest the pivot
    col D  the 2nd closest

Joe 0808: "add a 3rd and 4th column that shows the 2 TFs closest to (the ws1 marker that is closest
to the pivot)". The ws1 marker nearest the pivot is where the walk would be testing momentum when
the swing turns, so the TFs whose momentum fires AT that marker are the ones matched to the swing's
size; a TF that fired an hour earlier has overshot it.

    python3 report_ws_momo.py
"""
from optimus9.config import get_db_config
from optimus9 import DatabaseManager


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    cfg = db.execute('SELECT DISTINCT wm_swing_pct p, wm_just_before j FROM ws_momo', fetch=True)
    piv = db.execute('SELECT DISTINCT wm_pivot_ms m, wm_pivot_utc u, wm_pivot_kind k, wm_near_mk_utc nk,'
                     ' wm_near_mk_lead_min nl FROM ws_momo ORDER BY wm_pivot_ms', fetch=True)
    print(f'config: ' + ' | '.join(f"swing {c['p']}%  just_before {c['j']}min" for c in cfg))
    print(f'{len(piv)} pivots\n')
    print(f"{'pivot':<17} {'k':<2} {'nearest ws1 marker':<17} {'lead':>6} | {'closest TF':>10} "
          f"{'2nd':>6} | qualifying TFs")
    for p in piv:
        q = db.execute('SELECT wm_tf t FROM ws_momo WHERE wm_pivot_ms=%s AND wm_qualifies=1 '
                       'ORDER BY wm_tf', (p['m'],), fetch=True)
        c = db.execute('SELECT wm_tf t, wm_momo_state s, wm_momo_to_mk_min d, wm_momo_lead_min l '
                       'FROM ws_momo WHERE wm_pivot_ms=%s AND wm_momo_state IS NOT NULL '
                       'ORDER BY wm_momo_to_mk_min, wm_tf', (p['m'],), fetch=True)
        f = lambda i: (f"{c[i]['t']}{c[i]['s'][0]} +{c[i]['d']:.0f}m" if i < len(c) else '-')
        print(f"{p['u'][5:]:<17} {p['k']:<2} {(p['nk'] or '-')[5:]:<17} "
              f"{(f'{p['nl']:+.1f}' if p['nl'] is not None else '-'):>6} | {f(0):>10} {f(1):>6} | "
              + (','.join(str(x['t']) for x in q) or '-'))
    print('\ncol C/D read as  TF + m|c + minutes from that marker to the nearest-pivot marker')
    db.disconnect()


if __name__ == '__main__':
    main()
