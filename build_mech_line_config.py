"""build_mech_line_config — the dynamic line config table. Creates it, the live view, and seeds it.

Joe 0819: "earlier on, I suggested a new IC table that would apply configs dynamically - ie the line
configs are defined once, and the code spreads the config across the mech's TFs. this should be
written up somewhere; if its not then build it (SRP) from scratch".

It was not written up. One sentence existed, in docs/260805_handover.md line 212: "Joe 0805 floated
a dynamic IC table instead; the cost was never measured." Nothing else.

WHAT THIS REPLACES. `indicator_configs` holds 70 rows for the ws and gcws families carrying FIVE
distinct configs - the same config written out once per timeframe. And the timeframes domTF needs,
13 to 27 minutes, are not in that table at all: `build_ws_fin.py` hardcodes them as
`override(tf * 60, KLine(**B.R_SPEC), 'emerging')`. Both problems have the same shape, and one row
per (mechanic, role, timeframe band) fixes both.

NOTHING IS DELETED. `indicator_configs` and its 70 rows are untouched - Joe 0819 answered D3 that
way, and the bias machine, bl and arm all read that view. This table serves wsf and domTF only.

VERSIONING SERVES TWO MASTERS, Joe 0819: "we're using versioning in 2 ways: backtesting/sweeping,
and live-config. consider both scenarios, and build whatever is needed to satisfy both".
  mlc_version        the config's IDENTITY. It goes in the unique key, so two versions land
                     alongside each other. A run records the version it used.
  mlc_live_after_dt  which version the LIVE system uses right now, resolved by the view.

  A SWEEP MUST PASS A VERSION AND MUST NOT READ THE VIEW. If a sweep reads the live view and the
  live config changes while it runs, the run silently changes underneath it and nothing on the rows
  says so.

THE BOUNDARY IS AN OFFSET, NOT A PAIR. Joe 0819 answered D6: "boundary changes per mechanic or role
can be expressed as a single number in the mech's config table. eg, if config_boundary = 3, then the
boundary is represented as 100 - {o9_system.lo_boundary} - config_boundary = 82/18". So the fences
stay in `optimus9_system` and this table carries how far inside them a mechanic sits.

THE BAND IS IN SECONDS, Joe 0819 answered D2 that way. The line names disagree on units - `ws1r` is
60 seconds, `gcws15r` is 15 SECONDS - and seconds removes that trap.

NOT SEEDED. The ws4-8 and ws1-3 momentum bands the ws-finisher walk uses. D12 - whether they live
here, in the walk, or hardcoded - has not been ruled on.
"""
import sys

from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.compute.line_config import mech_lines

DDL = '''CREATE TABLE IF NOT EXISTS mech_line_config (
    mlc_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    -- THE KEY. mechanic + role + band + version.
    mlc_mech    VARCHAR(16) NOT NULL,   -- which mechanic. 'wsf' or 'domtf'
    mlc_role    VARCHAR(8)  NOT NULL,   -- r | x | m | b | Mage
    mlc_tf_lo   INT NOT NULL,           -- band low,  seconds
    mlc_tf_hi   INT NOT NULL,           -- band high, seconds, inclusive
    mlc_tf_step INT NOT NULL,           -- seconds between timeframes inside the band. 60 = every minute
    mlc_version INT NOT NULL,           -- the config's identity. A SWEEP reads this, never the view
    -- WHICH VERSION IS LIVE
    mlc_live_after_dt DATETIME NOT NULL,-- the live view takes the greatest one at or before now()
    -- THE CONFIG
    mlc_line_type ENUM('bb','k') NOT NULL,
    mlc_src       VARCHAR(10) NOT NULL, -- price source. 'close'
    mlc_bb_len    SMALLINT UNSIGNED,    -- Bollinger length. NULL on a k line
    mlc_bb_mult   DECIMAL(8,4),         -- Bollinger multiplier. NULL on a k line
    mlc_k_len     SMALLINT UNSIGNED,    -- K-chain: Joe writes it k_len | rsi | stc | src
    mlc_rsi_len   SMALLINT UNSIGNED,
    mlc_stc_len   SMALLINT UNSIGNED,
    mlc_value_mode VARCHAR(16) NOT NULL,-- 'emerging' or 'closed'. Decides whether the line is causal
    -- THE FENCES
    mlc_hi_boundary DECIMAL(6,2) NOT NULL,  -- from optimus9_system. 85
    mlc_lo_boundary DECIMAL(6,2) NOT NULL,  -- from optimus9_system. 15
    mlc_boundary_offset DECIMAL(6,2) NOT NULL DEFAULT 0,
    --  how far INSIDE the fences this mechanic sits. 0 -> 85/15. 5 -> 80/20. Joe 0819
    mlc_note VARCHAR(255) NOT NULL DEFAULT '',
    UNIQUE KEY uq_mlc (mlc_mech, mlc_role, mlc_tf_lo, mlc_tf_hi, mlc_version),
    KEY k_mech (mlc_mech), KEY k_live (mlc_live_after_dt))'''

VIEW = '''CREATE OR REPLACE VIEW vw_mech_line_config_live AS
    SELECT c.* FROM mech_line_config c
    WHERE c.mlc_live_after_dt = (
        SELECT MAX(c2.mlc_live_after_dt) FROM mech_line_config c2
        WHERE c2.mlc_mech = c.mlc_mech AND c2.mlc_role = c.mlc_role
          AND c2.mlc_tf_lo = c.mlc_tf_lo AND c2.mlc_tf_hi = c.mlc_tf_hi
          AND c2.mlc_live_after_dt <= NOW())'''

# Joe 0819 gave these five verbatim. Every one already matches what indicator_configs holds on
# every ws timeframe, so this is a move, not a change.
#   role   line type, config
CFG = {'m':    ('bb', dict(bb_len=6,  bb_mult=0.40)),      # 6|0.4|close
       'Mage': ('bb', dict(bb_len=38, bb_mult=0.93)),      # 38|0.93|close
       'x':    ('bb', dict(bb_len=5,  bb_mult=0.35)),      # 5|0.35|close
       'b':    ('bb', dict(bb_len=49, bb_mult=0.95)),      # 49|0.95|close
       'r':    ('k',  dict(k_len=7, rsi_len=5, stc_len=8))}  # 7|5|8|close

# mechanic -> (roles, band low minutes, band high minutes, note)
#   wsf   : ws1r..ws8r and their partners. The ws-finisher spec, TF1 to TF8.
#   domtf : DOMTF_MIN 13 to DOMTF_MAX 27 in build_ws_fin.py. r and x only - that is what the walk
#           builds today via override(tf * 60, ...).
SEED = [('wsf',   ['r', 'x', 'm', 'b', 'Mage'],  1,  8, 'ws-finisher, TF1 to TF8'),
        ('domtf', ['r', 'x'],                   13, 27, 'DOMTF_MIN 13 to DOMTF_MAX 27')]

COLS = ['mlc_mech', 'mlc_role', 'mlc_tf_lo', 'mlc_tf_hi', 'mlc_tf_step', 'mlc_version',
        'mlc_live_after_dt', 'mlc_line_type', 'mlc_src', 'mlc_bb_len', 'mlc_bb_mult',
        'mlc_k_len', 'mlc_rsi_len', 'mlc_stc_len', 'mlc_value_mode',
        'mlc_hi_boundary', 'mlc_lo_boundary', 'mlc_boundary_offset', 'mlc_note']


def main():
    version = 1
    live_after = '2026-01-01 00:00:00'      # version 1 is live from before any tape we hold
    db = DatabaseManager(**get_db_config()); db.connect()
    sysr = db.execute('SELECT hi_boundary hi, lo_boundary lo FROM optimus9_system WHERE sys_pk=1',
                      fetch=True)[0]
    HI, LO = float(sysr['hi']), float(sysr['lo'])
    print(f'  fences from optimus9_system: {HI:.0f} / {LO:.0f}', flush=True)

    db.execute(DDL)
    db.execute(VIEW)
    n = db.execute('SELECT COUNT(*) c FROM mech_line_config WHERE mlc_version=%s',
                   (version,), fetch=True)[0]['c']
    if n:
        print(f'  version {version} already holds {n} rows - deleting and reseeding', flush=True)
        db.execute('DELETE FROM mech_line_config WHERE mlc_version=%s', (version,))

    rows = []
    for mech, roles, lo_min, hi_min, note in SEED:
        for role in roles:
            kind, p = CFG[role]
            rows.append((mech, role, lo_min * 60, hi_min * 60, 60, version, live_after,
                         kind, 'close',
                         p.get('bb_len'), p.get('bb_mult'),
                         p.get('k_len'), p.get('rsi_len'), p.get('stc_len'),
                         'emerging', HI, LO, 0, note))
    db.executemany(f'INSERT INTO mech_line_config ({",".join(COLS)}) VALUES '
                   f'({",".join(["%s"] * len(COLS))})', rows)
    print(f'  mech_line_config : {len(rows)} rows written at version {version}', flush=True)

    print('\n  what one row expands to:', flush=True)
    for mech in ('wsf', 'domtf'):
        got = mech_lines(db, mech)
        roles = sorted({g["role"] for g in got})
        tfs = sorted({g['tf_seconds'] // 60 for g in got})
        print(f'    {mech:<6} {len(got):>3} lines   roles {roles}   timeframes {tfs[0]} to {tfs[-1]} min '
              f'  fences {got[0]["hi"]:.0f}/{got[0]["lo"]:.0f}', flush=True)
    db.disconnect()
    return 0


if __name__ == '__main__':
    sys.exit(main())
