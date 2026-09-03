"""build_wsf_event_mark_ab — the momentum column on Joe's marked events, at two knob sets.

Joe 0903: "wsf_event_mark is our current state - let's get an AB on that" and "duplicate the table
before re-keying".

WHY A DUPLICATE. wsf_event_mark keys on (wem_knobs, wem_run, wem_utc, wem_dr). The momentum knobs
are not in that key and fill_momo only writes rows whose momentum column is NULL, so a second
reading would overwrite the first and the two could not be told apart. This table adds the momentum
knob set to the key so both readings live side by side.

wsf_event_mark IS NOT TOUCHED. Joe 0827, no deletes. Its rows, including the 210 that carry Joe's
own verdict, stay exactly as they are.

THE TWO SIDES.
  A  kw4_sl1_r20.5    the knobs the momentum column was filled at, before the 0903 bake-in.
                      momo_core.py records "PREVIOUS: 0.50 / 1.0"; build_momo_landed.py records
                      "WAS 4". Only those three moved - the other eight are unchanged, so they are
                      taken from the live bank rather than written down again.
  B  kw6_sl1.2_r20.7  domtf v1, the bank Joe baked in on 0903. FITTED to eight eyeballed 08-04
                      pivots on ws20r, not measured.

A IS RECOMPUTED, NOT COPIED. It is computed from the same code path as B and then checked against
what wsf_event_mark already holds. If they match, the label on the banked column is proven rather
than assumed.

    python3 build_wsf_event_mark_ab.py
"""
import os
import sys
import datetime as dt
from datetime import timezone

import numpy as np

from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.compute.line_config import KLine, override
from optimus9.compute.momo_config import momo_bank, momo_config
from optimus9.compute.momo_gated import momo_g_why, momo_window
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP
from optimus9.orchestration.rpl_cache import LINE_DIR, TAPE_DIR, _line_key, _tape_key
import build_momo_landed as B
from build_wsf_event_mark import MOMO_TFS, MOMO_SHORT

SRC = 'wsf_event_mark'
DST = 'wsf_event_mark_ab'
A_LABEL = 'kw4_sl1_r20.5'
B_LABEL = 'kw6_sl1.2_r20.7'
A_OVERRIDE = {'k_window': 4, 'momo_slope_min': 1.0, 'momo_r2_min': 0.50}


def reading(db, bank, rows, R, ts):
    """the 30/45/60 momentum reading for every row, at `bank`. Same path fill_momo uses."""
    ms = lambda d: int(d.replace(tzinfo=timezone.utc).timestamp() * 1000)
    idx = {}
    for r in rows:
        j = int(np.searchsorted(ts, ms(r['u'])))
        if j < len(ts) and int(ts[j]) == ms(r['u']):
            idx[r['pk']] = j
    st = {}
    for tf in MOMO_TFS:
        with momo_config(bank), momo_window(bank['k_window'] * tf):
            for r in rows:
                if r['pk'] not in idx:
                    continue
                st.setdefault(r['pk'], {})[tf] = momo_g_why(
                    R[tf], int(r['dr']), idx[r['pk']], quad=True)[0]
    return {pk: ' / '.join(MOMO_SHORT[st[pk][tf]] for tf in MOMO_TFS) for pk in st}


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    cols = db.execute(f'SHOW COLUMNS FROM {SRC}', fetch=True)
    body = ',\n  '.join(f"{c['Field']} {c['Type']}"
                        + ('' if c['Null'] == 'YES' else ' NOT NULL')
                        for c in cols if c['Field'] != 'wem_pk')
    db.execute(f'''CREATE TABLE IF NOT EXISTS {DST} (
  ab_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
  wem_momo_knobs VARCHAR(40) NOT NULL,   -- the momentum knob set the reading was computed at
  {body},
  UNIQUE KEY uq_ab (wem_momo_knobs, wem_knobs, wem_run, wem_utc, wem_dr),
  KEY ix_ab_verdict (wem_verdict))''')

    src = db.execute(f'SELECT * FROM {SRC} ORDER BY wem_utc, wem_dr', fetch=True)
    rows = [{'pk': r['wem_pk'], 'u': r['wem_utc'], 'dr': r['wem_dr']} for r in src]
    print(f'  {SRC}: {len(src)} rows', flush=True)

    sy = db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l FROM optimus9_system '
                    'WHERE sys_pk=1', fetch=True)[0]
    ts = np.load(os.path.join(TAPE_DIR, _tape_key(END_MS, HOURS, WARMUP,
                 {'src': sy['s'], 'len': sy['l']}) + '.npz'))['__ts__']
    R = {tf: np.load(os.path.join(LINE_DIR, _line_key(END_MS, HOURS, WARMUP,
         override(tf * 60, KLine(**B.R_SPEC), 'emerging')) + '.npy')) for tf in MOMO_TFS}

    bank_b = momo_bank(db, MOMO_TFS[0])
    bank_a = dict(bank_b, **A_OVERRIDE)
    bank_a['mech'] = 'pre-0903'; bank_a['version'] = 0
    print(f"  A {A_LABEL}: k_window {bank_a['k_window']} slope {bank_a['momo_slope_min']} "
          f"r2 {bank_a['momo_r2_min']}", flush=True)
    print(f"  B {B_LABEL}: k_window {bank_b['k_window']} slope {bank_b['momo_slope_min']} "
          f"r2 {bank_b['momo_r2_min']}   ({bank_b['mech']} v{bank_b['version']})", flush=True)

    va = reading(db, bank_a, rows, R, ts)
    vb = reading(db, bank_b, rows, R, ts)

    # PROVE THE LABEL ON THE BANKED COLUMN. A is recomputed; it must reproduce what is already there.
    banked = {r['wem_pk']: r['wem_momo_30_45_60'] for r in src}
    diff = [pk for pk in va if banked.get(pk) != va[pk]]
    print(f'  A recomputed vs the column already banked in {SRC}: '
          f'{len(va) - len(diff)} of {len(va)} identical, {len(diff)} differ', flush=True)

    names = [c['Field'] for c in cols if c['Field'] != 'wem_pk']
    ins = ['wem_momo_knobs'] + names
    out = []
    for lab, v in ((A_LABEL, va), (B_LABEL, vb)):
        for r in src:
            rec = [lab] + [v.get(r['wem_pk']) if n == 'wem_momo_30_45_60' else r[n] for n in names]
            out.append(tuple(rec))
    db.executemany(f'INSERT IGNORE INTO {DST} ({",".join(ins)}) '
                   f'VALUES ({",".join(["%s"] * len(ins))})', out)
    n = db.execute(f'SELECT COUNT(*) n FROM {DST}', fetch=True)[0]['n']
    print(f'  {DST}: {n} rows ({len(src)} events x 2 knob sets)', flush=True)
    db.disconnect()
    return 0


if __name__ == '__main__':
    sys.exit(main())
