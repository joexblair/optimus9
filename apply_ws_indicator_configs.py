"""apply_ws_indicator_configs — register the ws / gcws line families in indicator_configs. Joe 0805.

Joe's spec, verbatim:

    ws{TF}Mage: 37|0.9|close        gcws{gcTF}Mage: 37|0.9|close
    ws{TF}m:     6|0.4|close        gcws{gcTF}m:     6|0.4|close
    ws{TF}x:     5|0.35|close       gcws{gcTF}x:     5|0.35|close
    ws{TF}b:    48|0.98|close       gcws{gcTF}b:    48|0.98|close
    ws{TF}r:     7|5|8|close        gcws{gcTF}r:     7|5|8|close

    TF   = [1,2,3,4,5,6,8,15,22] minutes
    gcTF = [15,30] seconds

45 + 10 = 55 rows. IDEMPOTENT — re-running inserts nothing new (the ic unique key is
(is,itf,il,live_after_dt); series/lines use INSERT IGNORE on their own unique keys).

FIELD ORDER. Joe writes a k-line k_len|rsi|stc|src and a bb-line length|mult|src. That is
optimus9.compute.line_config.KLine / BBLine field order, and this file hands those NAMED objects
to the writer rather than positional tuples, so the k-line transpose bug it documents cannot recur.

THREE SCHEMA ADDITIONS this needs (Joe 0805, stated before the run):
  1. indicator_series  += 'ws', 'gcws'         — new prefixes, no collision with the 16 existing
  2. indicator_lines   += 'x'                  — never existed in the DB; every x line in the repo
                                                 (s1x, s30x, gcs5x) is an in-memory override key only
  3. indicator_lines.il_suffix varchar(3)->(4) += 'Mage'
     Joe wrote the name as ws{TF}Mage. il_suffix was 3 chars, so 'Mage' did not fit. The widen is
     non-destructive (no existing suffix is 4 chars) and creates no s*Mage rows, so nothing that
     resolves today changes. The alternative — suffix 'M', names ws4M — would not be the name Joe
     wrote. See docs/quirks_to_remember.md:23 for the name = prefix||label||suffix rule.

TIMEFRAMES. All 11 itf_pk already exist; nothing is added to indicator_timeframes. Each is pinned by
(itf_label, itf_seconds) NOT by label alone — label '5' exists three times (5s / 300s / 600s) and
label '15' twice (15s / 900s). Picking by label alone would silently build the wrong TF.

    python3 apply_ws_indicator_configs.py [--dry]
"""
import sys

from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.compute.line_config import KLine, BBLine

LIVE_AFTER = '2026-08-05 00:00:00'   # ic_live_after_dt. Must be <= now() or vw_indicator_configs_live
#                                      hides the row. New series, so no prior version to supersede.
HI, LO = 85.00, 15.00                # ic_high_boundary / ic_low_boundary — the table default, and the
#                                      value on all 69 existing s/gcs rows.
IVM = 2                              # ic_ivm_pk -> indicator_value_modes 2 = 'emerging' (still-forming
#                                      intrabar value). 1 = 'closed'. Every 2026-07-10 s-series row is 2.

# Joe's five lines. Name -> (il_suffix, config). The suffix is what lands in indicator_lines.
LINES = [('Mage', BBLine(length=37, mult=0.90, src='close')),
         ('m',    BBLine(length=6,  mult=0.40, src='close')),
         ('x',    BBLine(length=5,  mult=0.35, src='close')),
         ('b',    BBLine(length=48, mult=0.98, src='close')),
         ('r',    KLine(k_len=7, rsi=5, stc=8, src='close'))]

# (is_prefix, [(itf_label, itf_seconds)]). itf_seconds is carried so the lookup is unambiguous.
FAMILIES = [('ws',   [('1', 60), ('2', 120), ('3', 180), ('4', 240), ('5', 300),
                      ('6', 360), ('8', 480), ('15', 900), ('22', 1320)]),
            ('gcws', [('15', 15), ('30', 30)])]

NEW_SUFFIXES = {'x': 'crossing line', 'Mage': 'major variant, Mage-named'}


def main(dry=False):
    db = DatabaseManager(**get_db_config()); db.connect()

    # 1. widen il_suffix so 'Mage' fits, then the two reference tables.
    width = db.execute("SELECT CHARACTER_MAXIMUM_LENGTH n FROM information_schema.COLUMNS "
                       "WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='indicator_lines' "
                       "AND COLUMN_NAME='il_suffix'", fetch=True)[0]['n']
    if width < 4:
        print(f'ALTER indicator_lines.il_suffix varchar({width}) -> varchar(4)')
        if not dry:
            db.execute('ALTER TABLE indicator_lines MODIFY il_suffix '
                       'VARCHAR(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL')
    else:
        print(f'il_suffix already varchar({width}) — no ALTER')

    for pre, _ in FAMILIES:
        if not dry:
            db.execute('INSERT IGNORE INTO indicator_series (is_prefix) VALUES (%s)', (pre,))
        print(f'series {pre!r}')
    for suf, desc in NEW_SUFFIXES.items():
        if not dry:
            db.execute('INSERT IGNORE INTO indicator_lines (il_suffix, il_description) VALUES (%s,%s)',
                       (suf, desc))
        print(f'line suffix {suf!r} — {desc}')

    if dry:
        db.disconnect()
        print('\n--dry: reference rows not written, so the config rows cannot be resolved. Stop.')
        return

    # 2. resolve the pks ONCE.
    S = {r['is_prefix']: r['is_pk'] for r in db.execute('SELECT is_pk,is_prefix FROM indicator_series',
                                                        fetch=True)}
    L = {r['il_suffix']: r['il_pk'] for r in db.execute('SELECT il_pk,il_suffix FROM indicator_lines',
                                                        fetch=True)}
    T = {(r['itf_label'], r['itf_seconds']): r['itf_pk']
         for r in db.execute('SELECT itf_pk,itf_label,itf_seconds FROM indicator_timeframes', fetch=True)}

    rows, names = [], []
    for pre, tfs in FAMILIES:
        for label, secs in tfs:
            itf = T[(label, secs)]
            for suf, cfg in LINES:
                bb = isinstance(cfg, BBLine)
                rows.append((S[pre], itf, L[suf], 'bb' if bb else 'k', LIVE_AFTER, cfg.src, HI, LO,
                             cfg.length if bb else None,
                             float(cfg.mult) if bb else None,
                             None if bb else cfg.k_len,
                             None if bb else cfg.rsi,
                             None if bb else cfg.stc,
                             IVM))
                names.append(f'{pre}{label}{suf}')

    n = db.executemany(
        'INSERT IGNORE INTO indicator_configs (ic_is_pk,ic_itf_pk,ic_il_pk,ic_line_type,ic_live_after_dt,'
        'ic_src,ic_high_boundary,ic_low_boundary,ic_bb_len,ic_bb_mult,ic_k_len,ic_rsi_len,ic_stc_len,'
        'ic_ivm_pk) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', rows)
    print(f'\nindicator_configs: {len(rows)} rows offered, {n} written')

    # 3. read them back through the view the whole system resolves lines with.
    got = db.execute("SELECT ind_name, itf_seconds, ic_line_type, ic_src, ic_bb_len, ic_bb_mult, "
                     "ic_k_len, ic_rsi_len, ic_stc_len, value_mode FROM vw_indicator_configs_live "
                     "WHERE ind_name LIKE 'ws%%' OR ind_name LIKE 'gcws%%' ORDER BY itf_seconds, ind_name",
                     fetch=True)
    print(f'vw_indicator_configs_live resolves {len(got)} of {len(names)}')
    miss = set(names) - {r['ind_name'] for r in got}
    if miss:
        print('MISSING: ' + ', '.join(sorted(miss)))
    for r in got:
        spec = (f"{r['ic_bb_len']}|{r['ic_bb_mult']}|{r['ic_src']}" if r['ic_line_type'] == 'bb'
                else f"{r['ic_k_len']}|{r['ic_rsi_len']}|{r['ic_stc_len']}|{r['ic_src']}")
        print(f"  {r['ind_name']:<12} {r['itf_seconds']:>5}s  {r['ic_line_type']:<2} {spec:<18} "
              f"{r['value_mode']}")
    db.disconnect()


if __name__ == '__main__':
    main(dry='--dry' in sys.argv)
