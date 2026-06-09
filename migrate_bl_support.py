"""
Idempotent migration for the BL support model (BRD bl_line_brd.md, BR-A/B/C).

  1. add bl_lines.bl_support_ic_pk + bl_exit3_support_ic_pk (the exit-support links;
     breach→support by ic_pk, so a shared support like hb9M is referenced, not duped).
  2. populate each active breach's exit support (+ hb15b's cross-family exit3 = hb9M)
     from the xlsx-confirmed mapping below.
  3. deactivate the over-seeded `support` rows not named in the xls (prediction now
     sources its mini/Major from the SET, so those rows are no longer read).

Run:  python3 migrate_bl_support.py
Safe to re-run. Prediction predictor_min/maj are resolved at runtime from the set
(see bl_detect._load_families) — NOT seeded here.
"""
import re, sys
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

# breach -> exit support (default = exit1+exit3) ; exit3 override (cross-family) | None
EXIT_SUPPORT = {
    's90b': ('s90m',  None),     # exit support is the MINI, per xls — not the Major
    'hb9b': ('hb9M',  None),
    'hs9r': ('hs9m',  None),
    'hs15r':('hs15m', None),
    's18b': ('s18m',  None),
    'b6b':  ('b6M',   None),
    's30r': ('s30M',  None),
    'hb15b':('hb15M', 'hb9M'),   # exit1/2 ← hb15M, exit3 ← hb9M ("not a typo")
}
# over-seeded support rows to retire (every set's OTHER BB, dumped by the blanket seeder)
RETIRE = ['b30m', 'b6m', 'hb15m', 'hb9m', 'hs15M', 'hs9M', 's18M', 's30m', 's90M']
NAME_RE = re.compile(r'^([a-z]+)(\d+)([a-zA-Z]+)$')


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    Q = lambda sql, p=(), f=False: db.execute(sql, p, fetch=f)

    # 1) columns (idempotent)
    cols = [c['Field'] for c in Q('SHOW COLUMNS FROM bl_lines', f=True)]
    for col in ('bl_support_ic_pk', 'bl_exit3_support_ic_pk'):
        if col not in cols:
            Q(f'ALTER TABLE bl_lines ADD COLUMN {col} BIGINT DEFAULT NULL')
            print(f'  + column {col}')
        else:
            print(f'  = column {col} exists')

    # name -> ic_pk (decompose prefix/label/suffix; assert uniqueness for the BL lines)
    rows = Q('''SELECT ic.ic_pk, s.is_prefix p, itf.itf_label l, il.il_suffix s
                FROM indicator_configs ic
                JOIN indicator_series s      ON s.is_pk   = ic.ic_is_pk
                JOIN indicator_lines il      ON il.il_pk  = ic.ic_il_pk
                JOIN indicator_timeframes itf ON itf.itf_pk = ic.ic_itf_pk''', f=True)
    by_name = {}
    for r in rows:
        by_name.setdefault(f"{r['p']}{r['l']}{r['s']}", []).append(r['ic_pk'])

    def ic_of(name):
        pks = by_name.get(name, [])
        if len(pks) != 1:
            raise RuntimeError(f'{name}: expected 1 ic_pk, found {pks}')
        return pks[0]

    # breach name -> bl_pk (active breach rows)
    brows = Q('''SELECT bl.bl_pk, CONCAT(s.is_prefix,itf.itf_label,il.il_suffix) nm
                 FROM bl_lines bl
                 JOIN indicator_configs ic ON ic.ic_pk=bl.bl_ic_pk
                 JOIN indicator_series s ON s.is_pk=ic.ic_is_pk
                 JOIN indicator_lines il ON il.il_pk=ic.ic_il_pk
                 JOIN indicator_timeframes itf ON itf.itf_pk=ic.ic_itf_pk
                 WHERE bl.bl_is_active=1 AND bl.bl_role='breach' ''', f=True)
    breach_pk = {r['nm']: r['bl_pk'] for r in brows}

    # 2) populate
    print('\n  populate exit supports:')
    for nm, (sup, ex3) in EXIT_SUPPORT.items():
        if nm not in breach_pk:
            print(f'    ! {nm}: no active breach row — skipped'); continue
        sup_pk = ic_of(sup); ex3_pk = ic_of(ex3) if ex3 else None
        Q('UPDATE bl_lines SET bl_support_ic_pk=%s, bl_exit3_support_ic_pk=%s WHERE bl_pk=%s',
          (sup_pk, ex3_pk, breach_pk[nm]))
        print(f'    {nm:<6} exit_support={sup}({sup_pk})' + (f'  exit3={ex3}({ex3_pk})' if ex3 else ''))

    # 3) retire over-seeded support rows
    print('\n  retire over-seeded support rows:')
    for nm in RETIRE:
        n = Q('''UPDATE bl_lines bl
                 JOIN indicator_configs ic ON ic.ic_pk=bl.bl_ic_pk
                 JOIN indicator_series s ON s.is_pk=ic.ic_is_pk
                 JOIN indicator_lines il ON il.il_pk=ic.ic_il_pk
                 JOIN indicator_timeframes itf ON itf.itf_pk=ic.ic_itf_pk
                 SET bl.bl_is_active=0
                 WHERE bl.bl_role='support' AND bl.bl_is_active=1
                   AND CONCAT(s.is_prefix,itf.itf_label,il.il_suffix)=%s''', (nm,))
        print(f'    {nm:<6} deactivated')

    # 4) review dump
    print('\n=== active breach rows after migration ===')
    final = Q('''SELECT CONCAT(s.is_prefix,itf.itf_label,il.il_suffix) nm,
                   bl.bl_support_ic_pk sup, bl.bl_exit3_support_ic_pk ex3, bl.bl_exit_mask mask
                 FROM bl_lines bl
                 JOIN indicator_configs ic ON ic.ic_pk=bl.bl_ic_pk
                 JOIN indicator_series s ON s.is_pk=ic.ic_is_pk
                 JOIN indicator_lines il ON il.il_pk=ic.ic_il_pk
                 JOIN indicator_timeframes itf ON itf.itf_pk=ic.ic_itf_pk
                 WHERE bl.bl_is_active=1 AND bl.bl_role='breach' ORDER BY nm''', f=True)
    pk2name = {pk: n for n, pks in by_name.items() for pk in pks}
    for r in final:
        sup = pk2name.get(r['sup'], r['sup']); ex3 = pk2name.get(r['ex3'], r['ex3']) if r['ex3'] else '-'
        print(f"  {r['nm']:<6} mask={r['mask']} exit_support={sup:<6} exit3={ex3}")
    asup = Q("SELECT COUNT(*) c FROM bl_lines WHERE bl_role='support' AND bl_is_active=1", f=True)[0]['c']
    print(f"\n  active support rows remaining: {asup} (xls-named keepers; now unread, kept as documentation)")
    db.disconnect()


if __name__ == '__main__':
    main()
