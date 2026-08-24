"""build_domtf_mage_cache — put the domTF Mage lines into the rpl line cache.

Joe 0823: "we'll need the domTF Mage lines in the cache - we'll use mage-weakness in domTF".

WHY A SEPARATE FILE. build_ws_lines.py builds the ws/gcws families by reading
vw_indicator_configs_live BY PREFIX, and the domTF timeframes 13 to 27 are not in that table at all
- which is the gap mech_line_config was created to close. So the domTF lines reach the cache the
way build_ws_fin.py already puts r and x there: the consumer declares the override and
cache_jig_perline builds it on first use.

NOTHING IS HARDCODED. The Mage spec is READ from mech_line_config's wsf Mage row and applied to the
domTF band. Joe 0822: "import, don't duplicate/split/fork".

  D1, my call: domTF Mage uses the SAME config as wsf Mage. Precedent - domtf r and x are already
      byte-identical to wsf r and x, and Joe gave the five configs 0819 as one per ROLE, not one
      per mechanic: "m: 6|0.4|close / Mage:38|0.93|close / x: 5|0.35|close / b: 49|0.95|close /
      r: 7|5|8|close".

  OPEN, and Joe's: whether mech_line_config gains a `domtf / Mage / 13-27` row, and at which
      VERSION. Nothing reads domtf from that table today - build_ws_fin.py hardcodes its two
      overrides - so there is no live consequence either way. But the table not describing what is
      built is a provenance gap, and adding to version 1 would change what version 1 expands to.
"""
import sys

import numpy as np

from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.compute.line_config import LineStore, BBLine, override, mech_lines
from optimus9.orchestration.rpl_cache import cache_jig_perline
from optimus9.orchestration.build_ws_lines import END_MS, HOURS, WARMUP
from optimus9.analysis import ws_strat as WS
import build_momo_landed as B

DOMTF_MIN, DOMTF_MAX = 13, 27      # the domTF ladder, matching build_ws_fin.py
WSF_LINES = ([f'{g}{s}' for g in ('gcws15', 'gcws30') for s in ('b', 'm', 'Mage', 'r')]
             + [f'ws1{s}' for s in ('b', 'm', 'Mage', 'r')])


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    sysr = db.execute('SELECT pxsmooth_dema_src s, pxsmooth_dema_len l '
                      'FROM optimus9_system WHERE sys_pk=1', fetch=True)[0]

    # the Mage spec, READ from the config table. One row, one role, every timeframe shares it.
    mage = next(g for g in mech_lines(db, 'wsf') if g['role'] == 'Mage')
    _, spec, mode = mage['override']
    kind, bb_len, bb_mult, src = spec
    if kind != 'bb':
        print(f'  Mage is not a bb line in the config table: {spec}'); return 1
    print(f'  Mage spec from mech_line_config : {bb_len}|{bb_mult}|{src}   value mode {mode}',
          flush=True)

    tfs = [t for t in B.TFS if DOMTF_MIN <= t <= DOMTF_MAX]
    ls = LineStore(db)
    ovr = {n: (*ls.resolve(n), ls.value_mode(n)) for n in set(WSF_LINES + list(WS.LINES))}
    for tf in tfs:
        ovr[f'Mage{tf}'] = override(tf * 60, BBLine(length=bb_len, mult=bb_mult, src=src), mode)
    print(f'  building ws{tfs[0]}Mage to ws{tfs[-1]}Mage - {len(tfs)} lines', flush=True)

    J = cache_jig_perline(END_MS, HOURS, WARMUP, ovr,
                          pxs_cfg={'src': sysr['s'], 'len': sysr['l']}, rebuild=False)
    print(f'\n  {"line":<10}{"bars":>10}{"finite":>10}{"min":>9}{"max":>9}', flush=True)
    for tf in tfs:
        v = np.asarray(J.W.line(f'Mage{tf}'), float)
        f = np.isfinite(v)
        print(f'  ws{tf}Mage{"":<3}{len(v):>10,}{int(f.sum()):>10,}'
              f'{np.nanmin(v):>9.2f}{np.nanmax(v):>9.2f}', flush=True)
    db.disconnect()
    return 0


if __name__ == '__main__':
    sys.exit(main())
