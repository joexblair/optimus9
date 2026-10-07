"""Seed ws12_baton_config v1 — Joe's >ws12 baton mech, every knob durable. 1007.

Joe 1007: *"I'm good with dwelling the dip ... which is going to happen after we bank, commit and
push, specs and knobs durable"*.

A NEW TABLE, NOT NEW ROWS IN lazy_g_config. Two reasons, both mine and both structural:
  1  `SpecConfig.key()` is '<table>.v<version>' - the VERSION, not a hash of the values. Adding
     in_key rows at lazy_g_config v1 would silently change what v1 means, and the 397 banked
     octosig_rulings rows carry 'lazy_g_config.v1' in their knob key. Those rows would then claim a
     provenance they were never measured under.
  2  SRP. This is Joe's >ws12 baton mech, not the lazy-g routing stack. `spec_config` is generic
     and `octo_freedom_config` is the precedent for a second per-spec table.

THE SPEC THIS SERVES: docs/octo-freedom/1007_ws12_baton.md.

EVERY VALUE'S PROVENANCE IS IN `source`. Two rows are owner 'mine' and say so:
  rrev_wob     carried over from lazy_g_config rev.rev_wob. Joe ruled the Mage reversal wob, never
               r's own.
  x_rev_xwob   a MEASURED knee on ONE leg, fitted=1.
Two rows are OFF with the measurement that put them there:
  div_floor    Joe proposed a floor 1007. Measured INVERTED on leg 8 and left at 0.
  floater_oob  Joe proposed it 1007. UNTESTED - 25 of 25 floaters were already oob, so the filter
               removed nothing and the leg cannot say whether it helps.
"""
import sys
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
from optimus9.compute.spec_config import ddl, spec_config

TABLE, PFX, VER = 'ws12_baton_config', 'wbc', 1   # 'wbc' is what spec_config infers from the table name

# section, key, value, type, units, owner, fitted, in_key, source, note
ROWS = [
 # ---- the ceiling rule, Joe 1007
 ('ceiling','ceil_trig_tf','12','int','timeframe','joe',0,1,
  'Joe 1007 "if ws12r crosses into oob, then extend the max TF to ws23"',
  'the line whose oob CROSSING extends the ceiling'),
 ('ceiling','ceil_hi','23','int','timeframe','joe',0,1,
  'Joe 1007 "extend the max TF to ws23"','the extended ceiling; the resting one is lazy_g band_hi 12'),
 ('ceiling','ceil_scope','leg','str',None,'joe',0,1,
  'Joe 1007 "this is a per leg mech"','latches for the rest of the leg, resets at the next open'),

 # ---- the gate, Joe 1007
 ('gate','oob_gate_bars','72','int','bars','joe',0,1,
  'Joe 1007 "apply this logic after ws12r is oob for >6 minutes"','6 min at the 5 s grid; STRICTLY more than'),
 ('gate','oob_gate_run','consecutive','str',None,'mine',0,1,
  'MINE 1007 - Joe said "oob for >6 minutes" and did not say whether a gap resets it',
  'leg 8 measured: a single 10 s gap at 08:26:20 split the run and moved the gate 2.4 min later'),

 # ---- branch 1, the trade signal
 ('signal','sig_window_bars','72','int','bars','joe',0,1,
  'Joe 1007 "if ws12x-crosses ws12r inside the first 6 minutes, the cross is the trade signal"',None),
 ('signal','sig_dir','counter-dr','str',None,'joe',0,1,
  'Joe 1007 "counter-dr. eg if +dr, x crosses under"',None),

 # ---- branch 2, the ws1Mage 50 dip
 ('dip','dip_mid','50.0','float','r-points','joe',0,1,
  'Joe 1007 "wait for ws1Mage to dip over/under 50. if +dr, then Mage will cross under 50, inverted for -dr"',
  'the signal that pressure is weakening'),
 ('dip','dip_dwell_bars','12','int','bars','joe',0,1,
  'Joe 1007 "we use a dwell > 12 bars"',
  'MEASURED on leg 8: runs are 9,1,1,7,44,513,1,1 bars, so any value 9..43 gives the same answer'),
 ('dip','dip_confirm','dwell-1','str',None,'mine',0,1,
  "MINE 1007, carried from jig.oob_ib_cross's conf convention",
  'the dip is knowable at dip + dwell - 1, not at the dip bar. 55 s on leg 8, changes no row there'),

 # ---- branch 2, the divergence
 ('div','div_lines','ws1r,ws2r','str',None,'joe',0,1,
  'Joe 1007 "drop ws1mage-rev and replace it with ws1r-reversing for the ws1 divergence test, and ws2r-reversing for its divergence test"',
  'each line is tested at ITS OWN r reversal'),
 ('div','div_combine','OR','str',None,'joe',0,1,'Joe 1007 "OR"',
  'leg 8: ws1r never fired, so under AND there is no exit at all'),
 ('div','div_floor','0','float','r-points','joe',0,1,
  'Joe 1007 proposed "we require a floor for the divergence". 0 = OFF.',
  'REJECTED on leg 8: the target abs d_osc is 20.94 and the false early ones are 28.57/41.36/45.35'),
 ('div','floater_oob','0','int','bool','joe',0,1,
  'Joe 1007 proposed "we require the floater to be oob". 0 = OFF.',
  'UNTESTED: 25 of 25 leg-8 floaters were already oob. anchor_floater filters on 50, NOT 85/15'),

 # ---- the r reversal detector
 ('rev','rrev_wob','2','int','steps','mine',0,1,
  'MINE 1007 - carried from lazy_g_config rev.rev_wob. Joe ruled the MAGE reversal wob, never r\'s',
  'sets how many r reversals exist at all: 144 on ws1r and 135 on ws2r in leg 8\'s 135 min'),

 # ---- the x-cross that precedes the reversal
 ('xcross','x_rev_xwob','8','int','bars','mine',1,1,
  'MEASURED knee 1007: spurious crosses reach 0 at 6 bars on ws1 and 8 on ws2, so 8 clears both',
  'at 8 the cross LEADS the reversal by a 5 s median on ws2 and 10 s on ws1 - Joe: "BBs lead Ks"'),

 # ---- the mage-rev tests
 ('mage_rev','dr_aligned','1','int','bool','joe',0,1,
  'Joe 1007 "all mage-rev tests are dr aligned: +dr requires a hi oob Mage"',
  'rules what jig.ws1mage_rev left open: its `rev` array is direction-unfiltered by design'),
 ('mage_rev','sig_lookback_bars','24','int','bars','joe',0,1,
  'Joe 0925 "re the lookback allowance, I agree but it should be longer - make it 2 minutes"; rule2_walked.signal documents it as the banked value, SS22.17',
  'IN NO CONFIG TABLE BEFORE THIS. jig.mage_rev_walk defaults to 0; entry_ab.py:102 passes 48'),

 # ---- the review stop
 ('stop','mae_stop_pct','1.1','float','pct','joe',0,1,
  'Joe 1007 "stop the chain when MAE is >1.1" / "for each run, stop the chain when MAE is >1.1 and start again on the next octo-sig"',
  'per LEG, from that leg\'s own open. The leg closes AT the breach bar'),
]


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    db.execute(ddl(TABLE, PFX))
    n = db.execute('SELECT COUNT(*) n FROM %s WHERE %s_version=%%s' % (TABLE, PFX),
                   (VER,), fetch=True)[0]['n']
    if n and '--force' not in sys.argv:
        print('# %s v%d already has %d rows. --force to replace.' % (TABLE, VER, n)); return
    if n:
        db.execute('DELETE FROM %s WHERE %s_version=%%s' % (TABLE, PFX), (VER,))
        print('# replaced %d rows at v%d' % (n, VER))
    db.executemany(
        'INSERT INTO %s (%s_version,%s_section,%s_key,%s_value,%s_type,%s_units,%s_owner,'
        '%s_fitted,%s_in_key,%s_source,%s_note) VALUES (%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s,%%s)'
        % ((TABLE,) + (PFX,) * 11),
        [(VER,) + r for r in ROWS])
    C = spec_config(db, TABLE)
    print('# seeded %s -> %d knobs, key %s' % (TABLE, len(C), C.key()))
    print('| section | knob | value | units | owner | fitted | in_key |')
    print('|---|---|---|---|---|---|---|')
    for k in sorted(C, key=lambda x: (C.meta[x]['section'], x)):
        m = C.meta[k]
        print('| %s | %s | %s | %s | %s | %s | %s |'
              % (m['section'], k, C[k], m['u'] or '', m['owner'], m['fitted'], m['in_key']))
    db.disconnect()


if __name__ == '__main__':
    main()
