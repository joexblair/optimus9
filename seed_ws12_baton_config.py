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
 ('gate','oob_gate_fence','15.0','float','r-points','joe',0,1,
  'Joe 1008 "we should have a knob for >12 oob". The >ws12 mech was borrowing the GLOBAL oob '
  '15/85 from lazy_g, the same shape as reent_xwob borrowing x_rev_xwob',
  'the oob fence for EVERY ws12r test in the >ws12 mech - the 72-bar gate, the branch-1 window and '
  'the ceiling trigger. Symmetric: lo = this, hi = 100 - this. 15.0 reproduces today exactly'),
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
 ('dip','dip_dwell_bars','6','int','bars','joe',0,1,
  'Joe 1008 "fence 53 + dwell 6", replacing his 1007 "we use a dwell > 12 bars". At 12 the 17:54 '
  'dip was rejected SEVEN times: the longest sub-50 run is 4 bars and the longest 47-53 run is 12, '
  'and the test is n > dwell',
  '1007 leg 8: runs 9,1,1,7,44,513,1,1 bars, so 9..43 were equivalent THERE. 6 changes leg 8 too'),
 ('dip','dip_fence','53.0','float','r-points','joe',0,1,
  'Joe 1008 "we\'ll use a small 100-{knob:53} fence, ie 47 to 53" / "fence 53 + dwell 6"',
  'the dip region is the BAND 100-53=47 to 53, not the single level dip_mid 50. Entry into the '
  'band is still dr-aligned: a LONG leg must enter from ABOVE 53, a SHORT leg from BELOW 47'),
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

 ('rev','ent_rev_wob','4','int','steps','joe',0,1,
  'Joe 1008 "sorry - typo. use 4", correcting his own "rrev_wob 5"; his read is "10:17 walked down '
  'to the reversl of ws1r at 10:21. at 10:21 it was infence - that\'s the end of the walk". 1007 SS19',
  'TURN detector for the ENTRY-OPTIMISING walk ONLY; rrev_wob 2 still serves the >ws12 divergence. '
  'at 4 the 10:17 turn lands 10:18:50 at entry +0.0891, the best of 2..40. wob 12 is the cliff'),

 # ---- the x-cross that precedes the reversal
 ('xcross','x_rev_xwob','8','int','bars','mine',1,1,
  'MEASURED knee 1007: spurious crosses reach 0 at 6 bars on ws1 and 8 on ws2, so 8 clears both',
  'at 8 the cross LEADS the reversal by a 5 s median on ws2 and 10 s on ws1 - Joe: "BBs lead Ks"'),

 # ---- the lineage walk's x-cross TARGET, swept 1008 (#61)
 ('xcross','x_tgt_role','b','str',None,'mine',1,1,
  'SWEPT 1008 (#61, 25 arms x 95 days). Joe "go for B". Ranked on the FIT half alone this arm is '
  'rank 1 of 25 at +0.7511 and then +4.0801 on the hold half',
  "the LINE the rider's x must cross. b is bb 49/0.95, the slowest of the five wsf roles; r (k "
  "5/8/7) is what the walk crossed before. CAVEAT: Spearman fit-vs-hold across the 25 arms is "
  "-0.137, so the ranking itself does not transfer"),
 ('xcross','x_tgt_tfs','next','str',None,'mine',1,1,
  'SWEPT 1008 (#61). next = h+1 only. both = h+1 AND h+2, which is what the walk used before; '
  'self = h itself, #61\'s own structure',
  'h is the rider TF. At both/fence-on the same arm scores -36.6819 on the fit half'),
 ('xcross','x_tgt_fence','0','int','bool','mine',1,1,
  'SWEPT 1008 (#61). 0 = the target line needs no in-fence test; 1 is what `bnd(t,k,d)=="."` did',
  'the only #61 result that is a PATTERN and not a pick: fence OFF means hold NET -4.9272 across '
  '12 arms against -20.3635 across the 12 with it on. It REVERSES on the fit half (-32.82 vs -22.18)'),

 # ---- the re-entry router, SEPARATED from the divergence mech 1008
 ('reentry','reent_xwob','18','int','bars','mine',1,1,
  'SWEPT 1008 over 95 days: 18 bars = 90 s. Joe 1007 ruled 6 ("xwob 6, not 8"; SS12) on ONE leg; '
  'the sweep is the wider measurement and 18 is its peak. Joe 1008 "defintely separate them" keeps '
  'this off the >ws12 mech\'s x_rev_xwob 8',
  'the ws1x return must HOLD this many bars at-or-beyond ws1r. conf = return + reent_xwob - 1. '
  'At 6 the router fires earlier and more often; at 18 it waits 90 s for the hold to prove out'),

 # ---- the mage-rev tests
 ('mage_rev','dr_aligned','1','int','bool','joe',0,1,
  'Joe 1007 "all mage-rev tests are dr aligned: +dr requires a hi oob Mage"',
  'rules what jig.ws1mage_rev left open: its `rev` array is direction-unfiltered by design'),
 ('mage_rev','sig_lookback_bars','24','int','bars','joe',0,1,
  'Joe 0925 "re the lookback allowance, I agree but it should be longer - make it 2 minutes"; rule2_walked.signal documents it as the banked value, SS22.17',
  'IN NO CONFIG TABLE BEFORE THIS. jig.mage_rev_walk defaults to 0; entry_ab.py:102 passes 48'),

 # ---- the review stop
 ('stop','mae_stop_pct','2.5','float','pct','mine',1,1,
  'SWEPT 1008 over 95 days. Joe 1007 ruled 1.1 ("stop the chain when MAE is >1.1"). At 1.1 the 331 '
  'legs the wider stop keeps alive are each charged -1.10; between them they only lose -22.64',
  "per LEG, from that leg's own open. The leg closes AT the breach bar. Joe 1008's goal is to bring "
  "this DOWN by relocating the opens that need it, so 2.5 is a staging post, not a destination"),
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
    bad = [(r[1], len(r[8]), len(r[9] or '')) for r in ROWS if len(r[8]) > 255
           or len(r[9] or '') > 255]
    if bad:
        print('# REFUSED - source/note over VARCHAR(255):')
        for k, ls, ln in bad:
            print('#   %s source %d note %d' % (k, ls, ln))
        db.disconnect(); sys.exit(1)
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
