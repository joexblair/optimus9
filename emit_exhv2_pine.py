"""exhv2 pine emit, TF4-aligned, double-printed bgcolor.
  SIGNAL  red = short (eff bias bull, hi breach) | green = long (eff bias bear)
  WALK    blue = hi-side s4Mage OOB              | yellow = lo-side
Walk streams paint first, signal streams over them - so a bar carrying both shows the signal colour.
Every timestamp bucketed to its TF4 bar (240000 ms), which is what TradingView will match on a TF4 chart."""
import datetime as dt
import build_rpl_6of9 as B
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

TF4 = 240_000
OUT = 'exhv2_tf4.pine'
u = lambda m: dt.datetime.fromtimestamp(m / 1000, dt.timezone.utc).strftime('%m-%d %H:%M')
d = DatabaseManager(**get_db_config()); d.connect()
R = d.execute("""SELECT v2_sig_ms, v2_walk_ms, v2_eff_bias, v2_walk_side, v2_action, v2_branch, v2_conf_utc
                 FROM rpl_exhv2 WHERE v2_sig_ms IS NOT NULL ORDER BY v2_conf_ms""", fetch=True)
d.disconnect()
bucket = lambda ms: (int(ms) // TF4) * TF4
sig_r = [bucket(x['v2_sig_ms']) for x in R if x['v2_eff_bias'] == 'bull']    # hi breach -> SHORT
sig_g = [bucket(x['v2_sig_ms']) for x in R if x['v2_eff_bias'] == 'bear']    # lo breach -> LONG
wlk_b = [bucket(x['v2_walk_ms']) for x in R if x['v2_walk_side'] == 'hi']
wlk_y = [bucket(x['v2_walk_ms']) for x in R if x['v2_walk_side'] == 'lo']
streams = [
    {'name': 'walk_hi',  'ts': wlk_b, 'color': 'color.blue'},
    {'name': 'walk_lo',  'ts': wlk_y, 'color': 'color.yellow'},
    {'name': 'sig_short', 'ts': sig_r, 'color': 'color.red'},
    {'name': 'sig_long',  'ts': sig_g, 'color': 'color.green'},
]
nEX = sum(1 for x in R if x['v2_action'] == 'EXIT')
notes = ('exhv2 | red=SHORT sig  green=LONG sig  blue=walk hi-OOB  yellow=walk lo-OOB | TF4 | '
         '%d events, signal = A ungated (first s15x X s15m at/after the walk, no gate) on ALL rows | '
         '%d are act=EXIT and still coloured by direction - flagged | lines x 4|0.37 m 6|0.45 '
         'M 37|0.7 r s4 7|6|11 s15,s22 10|4|11 | dwell 240s | slack 13.9' % (len(R), nEX))
total = B.J3.score.emit_bgcolor(streams, OUT, 'exhv2 signals + walks (TF4)', notes=notes)
print('%s  ->  %d painted bars' % (OUT, total))
for nm, v in (('sig red  (short)', sig_r), ('sig green (long)', sig_g),
              ('walk blue (hi)  ', wlk_b), ('walk yellow (lo)', wlk_y)):
    print('  %-18s %3d rows -> %3d distinct TF4 bars' % (nm, len(v), len(set(v))))
allts = sig_r + sig_g + wlk_b + wlk_y
print('  span %s .. %s' % (u(min(allts)), u(max(allts))))
ov = set(sig_r + sig_g) & set(wlk_b + wlk_y)
print('  TF4 bars carrying BOTH a walk and a signal: %d (signal paints over)' % len(ov))
