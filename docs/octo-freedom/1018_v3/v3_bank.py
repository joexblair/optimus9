"""Bank the octo-v3 test-point chain for one leg into v3_testpoint / v3_testpoint_line.

Joe 1018: *"you'll store everything in a db table that you'll consolidate into the spec"*.
The first leg he walked: the 2026-09-02 LONG, its 23:15:30 test-point and its 00:00:40 successor.
"""
import os, sys, io, contextlib
import numpy as np
sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1005_scoring')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1018_v3')
with contextlib.redirect_stdout(io.StringIO()):
    import score39 as SC
import v3_collect as V
from optimus9.compute import build_momo_cache as B
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

OPEN = SC.K('2026-09-02 22:16:30')
SIDE = +1                      # the LONG hunts the HIGH oob. Joe 1016, set once at the open
TPS = ['2026-09-02 23:15:30', '2026-09-03 00:00:40']

db = DatabaseManager(**get_db_config()); db.connect()
db.execute(V.DDL_TP); db.execute(V.DDL_LINE)
tape = V.Tape(SC, B.CACHE)
PX = tape.PX
adv = lambda a, z: float(np.nanmax(-(PX[a:z+1] - PX[a]) / PX[a] * 100.0))
fav = lambda a, z: float(np.nanmax((PX[a:z+1] - PX[a]) / PX[a] * 100.0))

rows = []
for seq, t in enumerate(TPS, 1):
    tp = SC.K(t)
    leg, nbars = V.dwell_bar(tape.B, SIDE, tp, V.OOB_DWELL, tape, tp)
    k, c, s = V.ib_cross(tape.M[V.MIN_TF], SIDE, tp - 1, V.TP_XWOB, tape, until=tp + 1)
    row, lad = V.collect(tape, SC.U(OPEN), SIDE, seq, tp, SC.U(tp + V.TP_XWOB - 1),
                         SC.U(leg) if leg is not None else None, nbars)
    nk, nc, ns = V.ib_cross(tape.M[V.MIN_TF], SIDE, row['step1_bar'] or tp, V.TP_XWOB, tape)
    row['next_tp'] = SC.U(nk) if nk is not None else None
    row['next_side'] = int(ns) if ns is not None else None
    row['held'] = int(ns == SIDE) if ns is not None else None
    end = nk if nk is not None else tp
    row['mae_open'], row['mfe_open'] = adv(OPEN, end), fav(OPEN, end)
    row['mae_tp'], row['mfe_tp'] = adv(tp, end), fav(tp, end)
    for q in ('oob_leg_bar',):
        pass
    for q in ('tp_bar', 'extrema_bar', 'step1_bar', 'step1_known'):
        if row.get(q) is not None and not isinstance(row[q], str):
            row[q] = SC.U(int(row[q]))
    cols = ['trade_open','side','seq','oob_leg_bar','oob_leg_bars','tp_bar','tp_known','tp_mage',
            'tp_b','extrema_bar','extrema_val','extrema_back','rider_tf','rider_src','mrider_tf',
            'r_oob','r_exfnc','mage_oob','mage_exfnc','mrider_qual','momtrue','race_winner',
            'race_order','step1_bar','step1_known','step2_p1_tf','step2_p1_r','step2_p2_tf',
            'step2_p2_r','step2_ok','print','mrider_at_s1','predict','next_tp','next_side','held',
            'mae_open','mfe_open','mae_tp','mfe_tp']
    vals = [('LONG' if SIDE > 0 else 'SHORT') if q == 'side' else row.get(q) for q in cols]
    knob = [V.MIN_TF, V.RMOM_FNC, V.MAGE_FNC, V.OOB_DWELL, V.TP_XWOB, V.STEP1_WOB, V.WSF_HI]
    names = ['v3tp_'+q for q in cols] + ['v3tp_min_tf','v3tp_rmom_fnc','v3tp_mage_fnc',
             'v3tp_oob_dwell','v3tp_tp_xwob','v3tp_step1_wob','v3tp_wsf_hi']
    ph = ','.join(['%s'] * len(names))
    upd = ','.join('%s=VALUES(%s)' % (n, n) for n in names)
    db.execute('INSERT INTO v3_testpoint (%s) VALUES (%s) ON DUPLICATE KEY UPDATE %s'
               % (','.join(names), ph, upd), tuple(vals + knob))
    tid = db.execute('SELECT v3tp_id id FROM v3_testpoint WHERE v3tp_trade_open=%s AND v3tp_seq=%s '
                     'AND v3tp_min_tf=%s AND v3tp_rmom_fnc=%s AND v3tp_mage_fnc=%s AND '
                     'v3tp_oob_dwell=%s AND v3tp_tp_xwob=%s AND v3tp_step1_wob=%s AND v3tp_wsf_hi=%s',
                     (SC.U(OPEN), seq) + tuple(knob), fetch=True)[0]['id']
    for lab, (bar, lrows) in lad.items():
        for q in lrows:
            db.execute(
                'INSERT INTO v3_testpoint_line (v3tpl_tp_id,v3tpl_at,v3tpl_bar,v3tpl_tf,v3tpl_r,'
                'v3tpl_r_oob,v3tpl_r_exfnc,v3tpl_mage,v3tpl_mage_oob,v3tpl_mage_exf,v3tpl_mrider_q,'
                'v3tpl_momtrue) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY '
                'UPDATE v3tpl_r=VALUES(v3tpl_r),v3tpl_r_oob=VALUES(v3tpl_r_oob),'
                'v3tpl_r_exfnc=VALUES(v3tpl_r_exfnc),v3tpl_mage=VALUES(v3tpl_mage),'
                'v3tpl_mage_oob=VALUES(v3tpl_mage_oob),v3tpl_mage_exf=VALUES(v3tpl_mage_exf),'
                'v3tpl_mrider_q=VALUES(v3tpl_mrider_q),v3tpl_momtrue=VALUES(v3tpl_momtrue)',
                (tid, lab, SC.U(bar), q['tf'], q['r'], int(q['r_oob']), int(q['r_exfnc']),
                 q['mage'], int(q['mage_oob']), int(q['mage_exf']), int(q['mrider_q']),
                 None if q['momtrue'] is None else int(q['momtrue'])))
    rows.append((tid, row))

print('| the knob | value |')
print('|---|---|')
for n, v in (('v3_min_tf', V.MIN_TF), ('v3_rmom_fnc', V.RMOM_FNC), ('v3_mage_fnc', V.MAGE_FNC),
             ('oob dwell', V.OOB_DWELL), ('tp xwob', V.TP_XWOB), ('step1 wob', V.STEP1_WOB),
             ('wsf hi', V.WSF_HI), ('MAE race', V.MAE_RACE)):
    print('| %s | %s |' % (n, v))
print()
print('# v3_testpoint - the banked chain')
print('| id | seq | oob leg | the test-point | extrema | rider | mrider | race winner | step1 | step2 | the print | mrider@s1 | predict | next tp | same side |')
print('|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|')
for tid, r in rows:
    print('| %d | %d | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |'
          % (tid, r['seq'], r['oob_leg_bar'], r['tp_bar'], r['extrema_bar'],
             'ws%d'%r['rider_tf'] if r['rider_tf'] else '-',
             'ws%d'%r['mrider_tf'] if r['mrider_tf'] else 'none',
             'ws%d'%r['race_winner'] if r['race_winner'] else '-',
             r['step1_bar'] or '-', 'YES' if r['step2_ok'] else 'no', r['print'] or '-',
             'ws%d'%r['mrider_at_s1'] if r['mrider_at_s1'] else 'none',
             r['predict'] or '-', r['next_tp'] or '-',
             ('YES' if r['held'] else 'NO - exit') if r['held'] is not None else '-'))
print()
print('| id | seq | MAE from open | MFE from open | MAE from tp | MFE from tp | MAE > %.1f |' % V.MAE_RACE)
print('|---|---|---|---|---|---|---|')
for tid, r in rows:
    print('| %d | %d | %.4f | %.4f | %.4f | %.4f | %s |'
          % (tid, r['seq'], r['mae_open'], r['mfe_open'], r['mae_tp'], r['mfe_tp'],
             'YES' if r['mae_open'] > V.MAE_RACE else 'no'))
n = db.execute('SELECT COUNT(*) c FROM v3_testpoint_line', fetch=True)[0]['c']
print()
print('| the ladder rows banked | %d |' % n)
db.disconnect()
