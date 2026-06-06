"""
Idempotent seeder for BL candidate lines — reads a CSV.

    python3 seed_bl_lines.py seeds.csv

CSV columns (header row optional, order fixed; leave a cell blank if N/A):
    line, tf_seconds, len, multi, rsilen, stochlen, src
e.g.
    b30M,30,19,0.64,,,hl2
    b30b,30,7,,74,29,hlc3
    mnm9m,240,18,0.73,,,ohlc4

Per line it creates, only if missing (dup-checked on the COLLATED name, e.g. mnm9m):
  • a new indicator_timeframes row if needed — rule: itf_seconds = tf column,
    itf_label = the number in the line name (mnm9 → (240,'9'), s90 → (30,'90')).
  • one indicator_configs row (settings stored exact; bb→bb_len/mult, k→k/rsi/stc).
  • one bl_lines row. Role is inferred (K→breach mask7 pk=family-M-BB; BB→support),
    overridden by ROLE_OVERRIDES below for BB-type breaches (e.g. mnm9m).
"""
import sys, csv, re
sys.path.insert(0, '/home/joe/thecodes')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager

# collated-name breach/support overrides: name → (role, exit_mask, pk_line | None)
ROLE_OVERRIDES = {
    'mnm9m': ('breach', 1, None),    # BB-type breach: OOB→1, IB→3, no curl, no exit4 pk
}
NAME_RE = re.compile(r'^([a-z]+)(\d+)([a-zA-Z]+)$')   # prefix · label(number) · suffix
BASE = "'2000-01-01'"


def load_csv(path):
    out = []
    with open(path, newline='') as f:
        for row in csv.reader(f):
            if not row or not row[0].strip():
                continue
            nm = row[0].strip()
            if not NAME_RE.match(nm):
                continue                              # header / junk row
            cell = lambda i: (row[i].strip() if i < len(row) and row[i].strip() else None)
            out.append(dict(name=nm, tf=int(cell(1)), length=cell(2), multi=cell(3),
                            rsi=cell(4), stc=cell(5), src=cell(6)))
    return out


def main(path) -> int:
    db = DatabaseManager(**get_db_config()); db.connect()
    Q = lambda sql, p=(), f=False: db.execute(sql, p, fetch=f)
    series = {r['is_prefix']: r['is_pk'] for r in Q('SELECT is_pk,is_prefix FROM indicator_series', f=True)}
    suffix = {r['il_suffix']: r['il_pk'] for r in Q('SELECT il_pk,il_suffix FROM indicator_lines', f=True)}

    def itf_pk(secs, label):
        r = Q('SELECT itf_pk FROM indicator_timeframes WHERE itf_seconds=%s AND itf_label=%s',
              (secs, str(label)), f=True)
        if r:
            return r[0]['itf_pk']
        Q('INSERT INTO indicator_timeframes (itf_seconds,itf_label) VALUES (%s,%s)', (secs, str(label)))
        print(f'  + itf ({secs}s, label {label})')
        return Q('SELECT itf_pk FROM indicator_timeframes WHERE itf_seconds=%s AND itf_label=%s',
                 (secs, str(label)), f=True)[0]['itf_pk']

    rows = load_csv(path)
    ic_of, parsed = {}, {}
    for r in rows:
        pre, lab, suf = NAME_RE.match(r['name']).groups()
        is_bb = r['multi'] is not None
        parsed[r['name']] = (pre, lab, suf, is_bb)
        isp, ilp, itf = series[pre], suffix[suf], itf_pk(r['tf'], lab)
        ex = Q('SELECT ic_pk FROM indicator_configs WHERE ic_is_pk=%s AND ic_il_pk=%s AND ic_itf_pk=%s',
               (isp, ilp, itf), f=True)
        if ex:
            ic_of[r['name']] = ex[0]['ic_pk']; print(f"  = {r['name']} exists (ic_pk {ex[0]['ic_pk']})"); continue
        kl, rsi, stc = (None, None, None) if is_bb else (r['length'], r['rsi'], r['stc'])
        bl, bm       = (r['length'], r['multi']) if is_bb else (None, None)
        Q(f"""INSERT INTO indicator_configs
              (ic_is_pk,ic_il_pk,ic_itf_pk,ic_line_type,ic_live_after_dt,ic_src,
               ic_high_boundary,ic_low_boundary,ic_k_len,ic_rsi_len,ic_stc_len,ic_bb_len,ic_bb_mult)
              VALUES (%s,%s,%s,%s,{BASE},%s,85,15,%s,%s,%s,%s,%s)""",
          (isp, ilp, itf, 'bb' if is_bb else 'k', r['src'], kl, rsi, stc, bl, bm))
        ic_of[r['name']] = Q('SELECT ic_pk FROM indicator_configs WHERE ic_is_pk=%s AND ic_il_pk=%s AND ic_itf_pk=%s',
                             (isp, ilp, itf), f=True)[0]['ic_pk']
        print(f"  + {r['name']} (ic_pk {ic_of[r['name']]}, {'bb' if is_bb else 'k'})")

    def family_bb(pre, lab):                          # the M (else m) BB of a family → exit4 pk
        for suf in ('M', 'm'):
            for nm, (p, l, s, bb) in parsed.items():
                if p == pre and l == lab and s == suf and bb:
                    return nm
        return None

    for nm, ic in ic_of.items():
        pre, lab, suf, is_bb = parsed[nm]
        if nm in ROLE_OVERRIDES:
            role, mask, pknm = ROLE_OVERRIDES[nm]
        elif not is_bb:                               # K line → breach
            role, mask, pknm = 'breach', 7, family_bb(pre, lab)
        else:                                         # BB line → support
            role, mask, pknm = 'support', None, None
        if Q('SELECT bl_pk FROM bl_lines WHERE bl_ic_pk=%s', (ic,), f=True):
            print(f'  = bl_lines[{nm}] exists'); continue
        pkic = ic_of.get(pknm) if pknm else None
        Q("""INSERT INTO bl_lines (bl_ic_pk,bl_role,bl_exit_mask,bl_pk_ic_pk,bl_is_active,bl_live_after_date)
             VALUES (%s,%s,%s,%s,1,NOW())""", (ic, role, mask, pkic))
        print(f'  + bl_lines[{nm}] {role} mask={mask} pk={pknm}')

    db.disconnect(); return 0


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: python3 seed_bl_lines.py <seeds.csv>'); raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
