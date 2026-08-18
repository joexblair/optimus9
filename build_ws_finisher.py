"""build_ws_finisher — the weak-mage-tf at every ws_fin_9of12 signal, and rule C.

Joe 0817 opened the ws-finisher spec. NOTHING FROM domTF IS USED HERE except the domTF state
column, taken as given from v_ws_fin_walk. Joe 0817: "don't spend time validating my domTF claims:
I'm manually validating against the raw data from the v_ws_fin_walk view".

  the weak-mage-tf  scan ws1Mage up to ws8Mage. The first that has NOT been out of bounds at any
                    bar inside the lookback. jig.weak_mage_tf.

  rule C            Joe 0817: "if weak-mage-tf == None and domTF state is FREE, fire a trade
                    signal".

Writes ws_fin_weak_mage: one row per signal, plus one column per timeframe holding how long ago
that line was last out of bounds. The rows where no weak-mage-tf is found are the stub Joe asked
for — they are not dropped.
"""
import sys
import datetime as dt
from datetime import timezone

import numpy as np

from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.jig import weak_mage_tf, WMT_TFS, WMT_LOOKBACK_S, WMT_SAME_SIDE

WIN_FROM = '2026-08-04 00:00:00'
WIN_TO   = '2026-08-05 00:00:00'
GRID_S   = 5


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    sysr = db.execute('SELECT hi_boundary h, lo_boundary lo FROM optimus9_system WHERE sys_pk=1',
                      fetch=True)[0]
    HI, LO = float(sysr['h']), float(sysr['lo'])
    look = WMT_LOOKBACK_S // GRID_S + 1

    cols = ','.join(f'wlb_ws{t}Mage m{t}' for t in WMT_TFS)
    bars = db.execute(f'SELECT wlb_ms,wlb_utc,{cols} FROM ws_line_bar '
                      'WHERE wlb_utc >= %s AND wlb_utc <= %s ORDER BY wlb_ms',
                      (WIN_FROM, WIN_TO), fetch=True)
    idx = {str(b['wlb_utc']): k for k, b in enumerate(bars)}
    MAGE = {t: np.array([b[f'm{t}'] if b[f'm{t}'] is not None else np.nan for b in bars], float)
            for t in WMT_TFS}
    print(f'  ws_line_bar: {len(bars):,} bars.  lookback {WMT_LOOKBACK_S} s = {look} bars '
          f'(the signal bar included)', flush=True)

    # the view's columns are the report's own headings, so they need quoting
    # `side` in the view is the numeric bias, dr. Nothing here converts it to a word.
    sig = db.execute('SELECT g30_marker g, side dr, domTF d FROM v_ws_fin_walk ORDER BY `#`',
                     fetch=True)
    print(f'  v_ws_fin_walk: {len(sig):,} signals', flush=True)

    db.execute('''CREATE TABLE IF NOT EXISTS ws_fin_weak_mage (
        wfm_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
        wfm_lookback_s SMALLINT NOT NULL,   -- WMT_LOOKBACK_S, seconds
        wfm_same_side  TINYINT NOT NULL,    -- WMT_SAME_SIDE. 1 = only the signal's own side counts
        wfm_hi DOUBLE NOT NULL, wfm_lo DOUBLE NOT NULL,
        wfm_utc  DATETIME NOT NULL,         -- the ws_fin_9of12 signal bar
        wfm_dr   TINYINT NOT NULL,          -- the bias. +1 / -1
        wfm_domtf VARCHAR(8) NOT NULL,      -- FREE or BLOCKED, taken as given from v_ws_fin_walk
        wfm_weak_tf SMALLINT,               -- the weak-mage-tf. NULL when every line was out
        wfm_fires   TINYINT NOT NULL,       -- rule C: weak-mage-tf is NULL and domTF is FREE
        wfm_tf1_ago SMALLINT, wfm_tf2_ago SMALLINT, wfm_tf3_ago SMALLINT, wfm_tf4_ago SMALLINT,
        wfm_tf5_ago SMALLINT, wfm_tf6_ago SMALLINT, wfm_tf7_ago SMALLINT, wfm_tf8_ago SMALLINT,
        --  _ago = seconds since that line was last out of bounds. NULL = never, inside the window
        wfm_tf1 DOUBLE, wfm_tf2 DOUBLE, wfm_tf3 DOUBLE, wfm_tf4 DOUBLE,
        wfm_tf5 DOUBLE, wfm_tf6 DOUBLE, wfm_tf7 DOUBLE, wfm_tf8 DOUBLE,
        --  the Mage value at the signal bar
        UNIQUE KEY uq_wfm (wfm_lookback_s, wfm_same_side, wfm_hi, wfm_lo, wfm_utc),
        KEY (wfm_weak_tf), KEY (wfm_fires))''')

    rows, miss = [], 0
    for s in sig:
        k = idx.get(str(s['g']))
        if k is None:
            miss += 1; continue
        w, det = weak_mage_tf(MAGE, HI, LO, k, look, int(s['dr']))
        fires = 1 if (w is None and s['d'] == 'FREE') else 0
        ago = [None if det[t][2] is None else det[t][2] * GRID_S for t in WMT_TFS]
        val = [None if not np.isfinite(det[t][0]) else det[t][0] for t in WMT_TFS]
        rows.append(tuple([WMT_LOOKBACK_S, 1 if WMT_SAME_SIDE else 0, HI, LO, str(s['g']),
                           int(s['dr']), s['d'], w, fires] + ago + val))
    C = (['wfm_lookback_s', 'wfm_same_side', 'wfm_hi', 'wfm_lo', 'wfm_utc', 'wfm_dr',
          'wfm_domtf', 'wfm_weak_tf', 'wfm_fires']
         + [f'wfm_tf{t}_ago' for t in WMT_TFS] + [f'wfm_tf{t}' for t in WMT_TFS])
    db.execute('DELETE FROM ws_fin_weak_mage WHERE wfm_lookback_s=%s AND wfm_same_side=%s '
               'AND wfm_hi=%s AND wfm_lo=%s AND wfm_utc >= %s AND wfm_utc <= %s',
               (WMT_LOOKBACK_S, 1 if WMT_SAME_SIDE else 0, HI, LO, WIN_FROM, WIN_TO))
    db.executemany(f'INSERT INTO ws_fin_weak_mage ({",".join(C)}) VALUES '
                   f'({",".join(["%s"] * len(C))})', rows)
    if miss:
        print(f'  {miss} signals had no ws_line_bar row and were skipped', flush=True)
    n_none = sum(1 for r in rows if r[7] is None)
    n_fire = sum(1 for r in rows if r[8])
    print(f'  ws_fin_weak_mage : {len(rows):,} rows', flush=True)
    print(f'    no weak-mage-tf found : {n_none}', flush=True)
    print(f'    rule C fires          : {n_fire}', flush=True)
    db.disconnect()
    return 0


if __name__ == '__main__':
    sys.exit(main())
