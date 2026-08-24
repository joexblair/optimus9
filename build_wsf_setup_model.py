"""build_wsf_setup_model — the SETUP MODEL dataset. Joe's template, banked as rows.

Joe 0824: "store the template report as the first dataset, and add this new 00:13 dataset to expand
your knowledge ... going forward, I'll be working with you on training the model at each of the
validated dtf-free timestamps".

TWO TABLES, TWO GRAINS.
    wsf_setup_board   one row per SETUP x LINE. The 20 wsf-model-report columns, ws1..ws8.
    wsf_setup         one row per SETUP. The derived counts, Joe's verdict, his own words.

NOTHING IS RECOMPUTED. Both read wsf_line_bar and wsf_bar_tf, the same join report_wsf_bar.py uses,
so a setup row is a query over banked data.

THE FEATURES ARE JOE'S, NOT MINE. Section 3.5 of docs/wsf_setup_model.md is already the model:
"domTF-override := a confluence of THREE: 1. ws8r reversing, 2. the count of lines printing heading
`away`, 3. the count of lines printing `r IB`", plus the fourth he rates above it - weak-mage-tf
NONE with all eight Mage lines out of bounds.

Section 3.12 adds the matryoshka order, Joe 0824: "a lower TF (~1 to ~4) r line will always stall or
curl before the higher TFs ... the LTFs are leading the way". So WHICH lines are away is stored, not
only how many.

NO THRESHOLD IS SET ON ANY FEATURE. Joe 0823: "no two `setup`s will be exactly the same so you must
learn in ranges, not in the specifics". The ranges come from his labels. This file stores; it scores
nothing.

    python3 build_wsf_setup_model.py
"""
import sys

from optimus9.config import get_db_config
from optimus9 import DatabaseManager

WIN_FROM = '2026-08-04 00:00:00'
KNOBS = 'kw4_fs21_sn6_hi85_lo15_r20.5_sl1_arc4_sk13.9_cr0.4_mkstate_mf17_xw4'
WMT_TF_LO = 2
HI, LO = 85.0, 15.0
MFR_HI, MFR_LO = 83.0, 17.0   # momo-fence-r, Joe's wsf fence. `heading` and "past the fence" use it
LTF = (1, 2, 3, 4)            # Joe 0824: "a lower TF (~1 to ~4)"
HTF = (5, 6, 7, 8)

# THE LABELLED SETUPS. Joe's verdict is the label; everything else is derived from banked rows.
#   (utc, dr, verdict, strength, notes)
SETUPS = [
 ('2026-08-04 08:02:50', +1, 'SHORT', 'strong',
  "Joe's template, spec 1.6: 'these are a strong bearish reversal' / 'both 08:00:55 and 8:02:50 are "
  "strong setups (ws8r reversing, many aways, many ltf `r IB`s), and would be a candidate for "
  "overriding domTF BLOCK'"),
 ('2026-08-04 00:13:00', +1, 'SHORT', 'unrated',
  "the 2nd dtf-free delegation. Joe 0824: 'your decision is correct: dr +1 = SHORT trade signal'. "
  "ws8r reads sideways with a blank last-verdict - the template's reversal marker is absent"),
 ('2026-08-04 00:14:50', +1, 'SHORT', 'unrated',
  "the 3rd dtf-free delegation. Joe 0824 agreed the verdict: 'I agree'. THE STATE IS wsf-momoc, "
  "settled by Joe: 'I overrode the wsf-exhaust state for 00:14:50, and I printed wsf-momoc'. The "
  "derived wss_state agrees with him. ws7r is the only line the report calls curl, and gate 2 "
  "rejects it: its bend points against dr - which is why Joe's note reads 'wsf-momoc on the "
  "non-existant #2 gate'. All eight bends on the board end downward. ws8r reads sideways with a "
  "blank last-verdict, 890 s dwell - the template's reversal marker is absent, same as 00:13:00"),
 ('2026-08-04 00:52:30', -1, 'hold and walk', 'unrated',
  "the 4th dtf-free delegation, and the FIRST on dr -1. Joe 0824 confirmed the state: 'your verdict "
  "is correct - good work' on wsf-exhaust. Verdict is 'hold and walk' because wsf has no direction "
  "of its own here - the stub: gcws30Mage 58.95, ws1Mage 36.56, ws2Mage 30.23, none outside the "
  "80/20 fence. THE LESSON, Joe verbatim: 'the HTF r lines are all low on the board while verdict "
  "is none, after verdict being momo -- this equates to r has dropped to the ~floor (momo), and has "
  "nowhere to go (none)'. ws5 8.10, ws6 3.30, ws7 8.55, ws8 15.82, all last-verdict momo"),
]

DDL_BOARD = '''CREATE TABLE IF NOT EXISTS wsf_setup_board (
    wsb_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    wsb_utc DATETIME NOT NULL, wsb_dr TINYINT NOT NULL, wsb_tf SMALLINT NOT NULL,
    wsb_r DOUBLE, wsb_heading VARCHAR(8), wsb_r_ib TINYINT,
    wsb_verdict VARCHAR(10), wsb_stalled TINYINT, wsb_gate50 DOUBLE, wsb_blocked50 TINYINT,
    wsb_last_verdict VARCHAR(10), wsb_dwell INT,
    wsb_mage DOUBLE, wsb_mage_oob TINYINT, wsb_weak_mage TINYINT,
    wsb_stoch_now DOUBLE, wsb_stoch_out DOUBLE, wsb_sat_bars SMALLINT, wsb_sat_left SMALLINT,
    wsb_rsi DOUBLE, wsb_rsi_lo DOUBLE, wsb_rsi_hi DOUBLE,
    -- SECTION 3.17, added 0824. r is the SEVEN-BAR MEAN of stoch, so the change r takes at this
    -- line's next bar close is fixed already: (stoch now - stoch out) / 7, in r units per bar.
    wsb_r_move DOUBLE,
    UNIQUE KEY uq_wsb (wsb_utc, wsb_dr, wsb_tf))'''

DDL_SETUP = '''CREATE TABLE IF NOT EXISTS wsf_setup (
    wss_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    wss_utc DATETIME NOT NULL, wss_dr TINYINT NOT NULL,
    -- JOE'S LABEL. Everything above the line is derived; this is not.
    wss_verdict  VARCHAR(16) NOT NULL,     -- SHORT | LONG | hold and walk
    wss_strength VARCHAR(16) NOT NULL,     -- Joe's own word. 'unrated' until he gives one
    wss_notes    VARCHAR(500) NOT NULL DEFAULT '',
    -- SECTION 3.5, condition 1: ws8r reversing
    wss_ws8_heading VARCHAR(8), wss_ws8_verdict VARCHAR(10), wss_ws8_last VARCHAR(10),
    wss_ws8_dwell INT, wss_ws8_past_fence DOUBLE,   -- Joe: "close to the fence", 1.50 at 08:02:50
    -- SECTION 3.5, condition 2: the count of lines printing `away`
    wss_away_n SMALLINT, wss_away_tfs VARCHAR(32),
    -- SECTION 3.5, condition 3: the count of lines printing `r IB`
    wss_rib_n SMALLINT, wss_rib_tfs VARCHAR(32),
    -- SECTION 3.5, the FOURTH and Joe rates it superior
    wss_weak_mage_tf SMALLINT, wss_all_mage_oob TINYINT,
    -- SECTION 3.12, the matryoshka order. Joe 0824: "the LTFs are leading the way"
    wss_toward_n SMALLINT, wss_toward_tfs VARCHAR(32),
    wss_away_max_tf SMALLINT, wss_toward_min_tf SMALLINT,
    wss_ltf_away_n SMALLINT, wss_htf_toward_n SMALLINT, wss_away_dwell_max INT,
    -- the state, from the wsf-model-report footer
    wss_state VARCHAR(16),
    -- SECTION 3.17, added 0824. Joe: "does anything in the stoch/sat/rsi columns confluence your
    -- decision?" These two are EXACT, not thresholded - stoch out is literally 0.00 or 100.00.
    -- stoch out is the reading leaving the seven-bar window at this line's next close.
    wss_only_rise_n SMALLINT,   -- lines where stoch out = 0: nothing can pull r down, r can only rise
    wss_only_fall_n SMALLINT,   -- lines where stoch out = 100: nothing can lift r, r can only fall
    UNIQUE KEY uq_wss (wss_utc, wss_dr))'''

Q = """SELECT b.wbt_tf tf, b.wbt_r r, b.wbt_mage mg, b.wbt_mage_oob_tol mt, b.wbt_weak_mage_tf wmt,
              l.wflb_verdict u, l.wflb_stalled sl, l.wflb_slope sp, l.wflb_mfr_out ob,
              l.wflb_fit fi, l.wflb_level lv, l.wflb_verdict_dwell vdw, l.wflb_last_verdict lv2,
              b.wbt_stoch_now sn, b.wbt_stoch_out so, b.wbt_sat_bars sb, b.wbt_sat_left sl2,
              b.wbt_rsi rsi, b.wbt_rsi_lo rlo, b.wbt_rsi_hi rhi
         FROM wsf_bar_tf b
         JOIN wsf_line_bar l ON l.wflb_utc=b.wbt_utc AND l.wflb_tf=b.wbt_tf AND l.wflb_dr=b.wbt_dr
        WHERE b.wbt_win_from=%s AND b.wbt_utc=%s AND b.wbt_dr=%s AND l.wflb_knobs=%s
              AND b.wbt_wmt_tf_lo=%s ORDER BY b.wbt_tf"""

LEVEL_SLACK, SLOPE_MIN = 13.9, 1.0


def heading(out_fence, slope):
    """report_wsf_bar.heading, unchanged. A line past its fence has made its cross already."""
    if out_fence:
        return 'away'
    return 'toward' if slope > 0 else 'away' if slope < 0 else 'flat'


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    db.execute(DDL_BOARD); db.execute(DDL_SETUP)
    # CREATE TABLE IF NOT EXISTS will not add a column to a table that already exists, so the
    # columns added on 0824 are added here for anyone whose tables predate them.
    for tbl, col, typ in (('wsf_setup_board', 'wsb_r_move', 'DOUBLE'),
                          ('wsf_setup', 'wss_only_rise_n', 'SMALLINT'),
                          ('wsf_setup', 'wss_only_fall_n', 'SMALLINT')):
        if not db.execute(f"SHOW COLUMNS FROM {tbl} LIKE '{col}'", fetch=True):
            db.execute(f'ALTER TABLE {tbl} ADD COLUMN {col} {typ}')
            print(f'  added {tbl}.{col}', flush=True)
    for utc, dr, verdict, strength, notes in SETUPS:
        rows = db.execute(Q, (WIN_FROM, utc, dr, KNOBS, WMT_TF_LO), fetch=True)
        if not rows:
            print(f'  {utc} dr {dr:+d}: no banked rows. SKIPPED', flush=True); continue
        db.execute('DELETE FROM wsf_setup_board WHERE wsb_utc=%s AND wsb_dr=%s', (utc, dr))
        db.execute('DELETE FROM wsf_setup WHERE wss_utc=%s AND wss_dr=%s', (utc, dr))
        board = []; H = {}
        for x in rows:
            tf = int(x['tf']); rv = float(x['r']); sp = float(x['sp'])
            h = heading(bool(x['ob']), sp)
            trk = max(0.0, min(1.0, float(x['fi']) * min(1.0, abs(sp) / SLOPE_MIN)))
            gate = (50 - LEVEL_SLACK * trk) if dr > 0 else (50 + LEVEL_SLACK * trk)
            H[tf] = dict(h=h, rib=int(LO < rv < HI), u=x['u'], lv2=x['lv2'],
                         dwell=int(x['vdw']), r=rv, mt=int(x['mt']))
            board.append((utc, dr, tf, rv, h, int(LO < rv < HI), x['u'], int(x['sl']), gate,
                          0 if int(x['lv']) else 1, x['lv2'], int(x['vdw']), float(x['mg']),
                          int(x['mt']), 0, x['sn'], x['so'], x['sb'], x['sl2'],
                          x['rsi'], x['rlo'], x['rhi'],
                          None if (x['sn'] is None or x['so'] is None)
                          else (float(x['sn']) - float(x['so'])) / 7.0))
        wmt = rows[0]['wmt']
        board = [b[:14] + (1 if (wmt and int(b[2]) == int(wmt)) else 0,) + b[15:] for b in board]
        db.executemany(
            'INSERT INTO wsf_setup_board (wsb_utc,wsb_dr,wsb_tf,wsb_r,wsb_heading,wsb_r_ib,'
            'wsb_verdict,wsb_stalled,wsb_gate50,wsb_blocked50,wsb_last_verdict,wsb_dwell,wsb_mage,'
            'wsb_mage_oob,wsb_weak_mage,wsb_stoch_now,wsb_stoch_out,wsb_sat_bars,wsb_sat_left,'
            'wsb_rsi,wsb_rsi_lo,wsb_rsi_hi,wsb_r_move) VALUES ('
            + ','.join(['%s'] * 23) + ')', board)
        # ROUNDED TO 6 PLACES, AND THAT IS NOT A KNOB. stoch is (RSI - RSI lo) / (RSI hi - RSI lo)
        # x 100, so it is EXACTLY 0 when the outgoing RSI was the window's low and EXACTLY 100 when
        # it was the window's high. The division leaves float residue: 08-04 00:52:30 ws5 stored
        # 1.4168726029049243e-14 instead of 0, and 08:02:50 ws6 stored 99.99999999999999 instead of
        # 100. Raw equality missed both. The nearest genuine values in the same boards are 42.41 and
        # 50.00, so six places is seven orders clear of any real reading and seven orders above the
        # residue. It recovers the intended number; it does not choose a level.
        only_rise = sum(1 for x in rows if x['so'] is not None and round(float(x['so']), 6) == 0.0)
        only_fall = sum(1 for x in rows if x['so'] is not None and round(float(x['so']), 6) == 100.0)

        away = sorted(t for t in H if H[t]['h'] == 'away')
        tow = sorted(t for t in H if H[t]['h'] == 'toward')
        rib = sorted(t for t in H if H[t]['rib'])
        w8 = H.get(8, {})
        # "close to the fence" is measured against momo-fence-r, the fence `heading` uses.
        # ws8r 84.50 at 08:02:50 is 1.50 past 83 - Joe's own number in section 3.4.
        past = (abs(w8.get('r', 0) - (MFR_HI if dr > 0 else MFR_LO))
                if w8 and ((w8['r'] >= MFR_HI) if dr > 0 else (w8['r'] <= MFR_LO)) else None)
        mom = [t for t in H if H[t]['u'] in ('momo', 'curl')]
        sg = db.execute("SELECT wsf_domtf d FROM ws_fin_9of12 WHERE wsf_utc=%s "
                        "AND wsf_ho_rule='median' AND wsf_line_hcap='ws1b:1'", (utc,), fetch=True)
        state = ('wsf-momo-none' if (sg and sg[0]['d'] == 'BLOCKED')
                 else 'wsf-momoc' if mom else 'wsf-exhaust')
        db.execute(
            'INSERT INTO wsf_setup (wss_utc,wss_dr,wss_verdict,wss_strength,wss_notes,'
            'wss_ws8_heading,wss_ws8_verdict,wss_ws8_last,wss_ws8_dwell,wss_ws8_past_fence,'
            'wss_away_n,wss_away_tfs,wss_rib_n,wss_rib_tfs,wss_weak_mage_tf,wss_all_mage_oob,'
            'wss_toward_n,wss_toward_tfs,wss_away_max_tf,wss_toward_min_tf,wss_ltf_away_n,'
            'wss_htf_toward_n,wss_away_dwell_max,wss_state,wss_only_rise_n,wss_only_fall_n)'
            ' VALUES (' + ','.join(['%s'] * 26) + ')',
            (utc, dr, verdict, strength, notes[:500],
             w8.get('h'), w8.get('u'), w8.get('lv2'), w8.get('dwell'), past,
             len(away), ','.join(map(str, away)), len(rib), ','.join(map(str, rib)),
             wmt, int(all(H[t]['mt'] for t in H)),
             len(tow), ','.join(map(str, tow)),
             max(away) if away else None, min(tow) if tow else None,
             sum(1 for t in away if t in LTF), sum(1 for t in tow if t in HTF),
             max((H[t]['dwell'] for t in away), default=None), state,
             only_rise, only_fall))
        print(f'  {utc[11:]} dr {dr:+d}  {verdict:<5} : 8 board rows, 1 setup row', flush=True)

    print(f"\n  {'setup':<10}{'dr':>4}{'verdict':>15}{'away':>6}{'away tfs':>14}{'r IB':>6}"
          f"{'rIB tfs':>16}{'toward':>8}{'ltf away':>10}{'htf toward':>12}"
          f"{'weak-mage':>11}{'all oob':>9}{'state':>13}{'only rise':>11}{'only fall':>11}", flush=True)
    for r in db.execute('SELECT * FROM wsf_setup ORDER BY wss_utc', fetch=True):
        print(f"  {str(r['wss_utc'])[11:]:<10}{r['wss_dr']:>+4}{r['wss_verdict']:>15}"
              f"{r['wss_away_n']:>6}{r['wss_away_tfs']:>14}{r['wss_rib_n']:>6}"
              f"{r['wss_rib_tfs']:>16}{r['wss_toward_n']:>8}{r['wss_ltf_away_n']:>10}"
              f"{r['wss_htf_toward_n']:>12}{str(r['wss_weak_mage_tf'] or 'NONE'):>11}"
              f"{('yes' if r['wss_all_mage_oob'] else ''):>9}{r['wss_state']:>13}"
              f"{r['wss_only_rise_n']:>11}{r['wss_only_fall_n']:>11}", flush=True)
    db.disconnect()
    return 0


if __name__ == '__main__':
    sys.exit(main())
