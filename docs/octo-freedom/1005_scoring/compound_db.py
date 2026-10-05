"""The complete compound PnL table, banked to MySQL. Joe 1005:
"now let's see the complete table showing the compound pnl, in a db table. for each trade decide the
leverage that will be applied in accordance with safe practices. account starts at 888 dollars"
"drop the pyramid max"

CONFIG, all of it carried in the row's unique key (knobs-in-the-key):
  side rule   dr-bias, NO stage 2 flip   (section 5: the flip costs 2.5 pp over 9 days)
  stop        0.80 % of entry             (Joe 1005, the better of the two he named: +47.1 vs +37.9)
  swing       0.70 %                      find_pivots on __pxs__, places the exit pivot
  cost        0.1975 % per trade          2 x 5.50 bps taker + 8.75 bps slippage at 22,000 coins
  pyramid     NO CAP                      Joe 1005, "drop the pyramid max"
  start       888.00 USD                  Joe 1005
  window      09-25 .. 10-03, 9 days, 298 octo-sig -> 151 confluences

THE LEVERAGE RULE — MY DECISION, ANCHORED, AND IT IS A VALUE SO IT IS NAMED NOT HIDDEN:
  The worst case per trade is KNOWN BEFORE ENTRY and is not an estimate: the 0.80 % stop plus the
  0.1975 % cost = 0.9975 % of notional. So a risk budget converts straight to leverage.
  budget   RISK_PCT = 2.0 % of equity, the classic 2 %-risk-per-trade convention. An external named
           standard, not a preference of mine, and swept below so Joe can move it.
  share    with the pyramid cap dropped, concurrency is unbounded, so a constant 2 % PER LEG would
           let N live legs stack to N x 2 %. Instead the budget is DIVIDED at the moment of entry:
               risk_i = RISK_PCT / (n_live_at_open + 1)
               lev_i  = risk_i / 0.9975
           n_live_at_open is causal - it is the count of legs still open at this bar, known then.
           A leg entering alone gets the full 2 %; entering alongside one live leg, 1 %; alongside
           two, 0.667 %. It never reaches zero, so no trade is silently dropped - Joe dropped the cap.
  size     notional_i = equity_at_open x lev_i. Dollar size therefore GROWS as equity compounds
           while the leverage stays bounded - that is the "increase over time" ramp.

BOOKKEEPING: a trade is sized off equity AT ITS OPEN and its P&L is applied AT ITS CLOSE. Equity
changes only at closes. Reported alongside: CONSTANT-LEG sizing (every leg takes the full 2 %), the
sneaky-1 precedent, so the two are comparable.
"""
import os as _os
import re
_HERE = _os.path.dirname(_os.path.abspath(__file__))
import sys, io, os, contextlib, json
import numpy as np
sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
exec(open(_os.path.join(_HERE, 'ninedays.py')).read().split('ALL = {}')[0])
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

STOP = 0.95; SWING = 0.70; COST = 0.1975; START = 888.00; RISK_PCT = 1.5
# Destination table. Override with LG_TABLE so an out-of-sample window banks ALONGSIDE the
# in-sample one instead of into it:  LG_TABLE=lazyg_compound_oos LG_TAPE_END=2026-10-05 ...
TABLE = _os.environ.get('LG_TABLE', 'lazyg_compound')
assert re.fullmatch(r'[a-z0-9_]{1,60}', TABLE), 'LG_TABLE must be a bare lower-case identifier'
Q = lambda sql: sql.replace('__TBL__', TABLE)   # one sentinel, no quote-delimiter traps
WORST = STOP + COST                      # 0.9975 % of notional, the known per-trade worst case
SIDE_RULE = 'dr-bias'; PYR = 0           # 0 = no cap

UNRES = []

def rows_at(stop, flip_on=False):
    out = []
    for day in DAYS:
        A0, A1 = S.K(day + ' 00:00:00'), S.K(day + ' 23:59:55')
        for ln in open(_os.path.join(_HERE, 'octosig') + '/%s.out' % day):
            if not ln.startswith('R|') or ln.startswith('R|run'): continue
            f = ln.rstrip('\n').split('|')
            if len(f) < 7: continue
            k = S.K(day + ' ' + f[2])
            if not (A0 <= k <= A1): continue
            m = S.mtd(k); d = m['d']
            if m['route'] != 'mtd.r1': continue
            dd = S.branchD(d, m['ex'])
            if not dd['fire']: continue
            grade = 'with-trend' if dd['away'] else 'against-trend'
            de = (-d if grade == 'with-trend' else d) if flip_on else d
            mfe, mae, j = S.score(k, de, H, L)
            # UNRESOLVED: no favourable swing pivot after this bar inside the tape (happens on the
            # tape's LAST day). Excluded and counted — never scored 0, which would be a truncation.
            if mfe is None:
                UNRES.append((day, f[2])); continue
            entry = float(PX[k]); seg = PX[k:j + 1]
            adv = (seg - entry) / entry * 100.0 if de > 0 else (entry - seg) / entry * 100.0
            hit = np.flatnonzero(np.isfinite(adv) & (adv >= stop))
            ex = k + int(hit[0]) if hit.size else j
            out.append({'day': day, 'lbl': f[2], 'dr': d, 'grade': grade,
                        'side': 'SHORT' if de > 0 else 'LONG',
                        'entry_px': entry, 'exit_px': float(PX[ex]),
                        'open_ms': int(ts[k]), 'close_ms': int(ts[ex]),
                        'hold_m': (ts[ex] - ts[k]) / 60000.0,
                        'mfe': mfe, 'mae': mae, 'stopped': bool(hit.size),
                        'gross': -stop if hit.size else mfe,
                        'net': (-stop if hit.size else mfe) - COST})
    out.sort(key=lambda x: (x['open_ms'], x['close_ms']))
    return out

T = rows_at(STOP)

# ---- concurrency census (no cap)
mx = 0
for x in T:
    n = sum(1 for y in T if y['open_ms'] <= x['open_ms'] < y['close_ms'])
    x['n_live'] = sum(1 for y in T if y is not x and y['open_ms'] <= x['open_ms'] < y['close_ms'])
    mx = max(mx, n)

def walk(rows, mode, risk_pct):
    """mode 'shared' = budget divided by live legs · 'constant' = full budget per leg."""
    ev = []
    for i, x in enumerate(rows): ev.append((x['open_ms'], 0, i)); ev.append((x['close_ms'], 1, i))
    ev.sort()
    eq = START; peak = START; dd = 0.0
    pos = {}; out = [None] * len(rows); n = 0
    for _t, kind, i in ev:
        x = rows[i]
        if kind == 0:
            share = risk_pct if mode == 'constant' else risk_pct / (n + 1)
            lev = share / WORST
            pos[i] = {'eq_open': eq, 'lev': lev, 'notional': eq * lev, 'risk_usd': eq * share / 100.0,
                      'n_live': n}
            n += 1
        else:
            p = pos.pop(i); n -= 1
            pnl = p['notional'] * x['net'] / 100.0
            eq += pnl
            peak = max(peak, eq); dd = max(dd, (peak - eq) / peak)
            out[i] = dict(p, pnl=pnl, eq_close=eq, dd=dd)
    return out, eq, dd

SH, eq_sh, dd_sh = walk(T, 'shared', RISK_PCT)
CO, eq_co, dd_co = walk(T, 'constant', RISK_PCT)

# ---- DB: NEW table, nothing dropped, every knob in the unique key
db = DatabaseManager(**get_db_config()); db.connect()
db.execute(Q('''CREATE TABLE IF NOT EXISTS __TBL__ (
    lc_pk          BIGINT AUTO_INCREMENT PRIMARY KEY,
    lc_side_rule   VARCHAR(16)  NOT NULL,     -- dr-bias | stage2-flip
    lc_stop_pct    DECIMAL(6,4) NOT NULL,     -- 0.8000 = the 0.80 % stop on entry price
    lc_swing_pct   DECIMAL(6,4) NOT NULL,     -- 0.7000 = find_pivots swing that places the exit
    lc_cost_pct    DECIMAL(6,4) NOT NULL,     -- 0.1975 = round-trip drag at 22,000 coins
    lc_pyr_max     TINYINT      NOT NULL,     -- 0 = no concurrency cap (Joe 1005)
    lc_risk_pct    DECIMAL(6,4) NOT NULL,     -- 2.0000 = risk budget per entry, % of equity
    lc_size_mode   VARCHAR(10)  NOT NULL,     -- shared | constant
    lc_start_usd   DECIMAL(14,4) NOT NULL,    -- 888.0000
    lc_seq         INT          NOT NULL,     -- 1..n, chronological by open
    lc_day         DATE         NOT NULL,
    lc_octosig     VARCHAR(8)   NOT NULL,     -- the signal time, HH:MM:SS
    lc_open_ms     BIGINT       NOT NULL,
    lc_close_ms    BIGINT       NOT NULL,
    lc_dr          TINYINT      NOT NULL,
    lc_side        VARCHAR(5)   NOT NULL,
    lc_grade       VARCHAR(16)  NOT NULL,     -- with-trend | against-trend (branch D mage-cascade)
    lc_entry_px    DECIMAL(16,8) NOT NULL,
    lc_exit_px     DECIMAL(16,8) NOT NULL,
    lc_hold_min    DECIMAL(10,2) NOT NULL,
    lc_mfe_pct     DECIMAL(10,4) NOT NULL,
    lc_mae_pct     DECIMAL(10,4) NOT NULL,
    lc_stopped     TINYINT      NOT NULL,
    lc_gross_pct   DECIMAL(10,4) NOT NULL,
    lc_drag_pct    DECIMAL(10,4) NOT NULL,     -- the round-trip drag charged to THIS trade, % of notional
    lc_net_pct     DECIMAL(10,4) NOT NULL,     -- gross - drag
    lc_gross_usd   DECIMAL(16,4) NOT NULL,     -- notional x gross%
    lc_drag_usd    DECIMAL(16,4) NOT NULL,     -- notional x drag%  <- the dollars the exchange takes
    lc_n_live      TINYINT      NOT NULL,     -- legs already open at this entry bar (causal)
    lc_lev         DECIMAL(8,4) NOT NULL,     -- the leverage applied to THIS trade
    lc_eq_open     DECIMAL(16,4) NOT NULL,
    lc_notional    DECIMAL(16,4) NOT NULL,
    lc_risk_usd    DECIMAL(16,4) NOT NULL,
    lc_pnl_usd     DECIMAL(16,4) NOT NULL,
    lc_eq_close    DECIMAL(16,4) NOT NULL,
    lc_dd_pct      DECIMAL(8,4) NOT NULL,     -- running peak-to-trough drawdown, %
    UNIQUE KEY uq_lc (lc_side_rule, lc_stop_pct, lc_swing_pct, lc_cost_pct, lc_pyr_max,
                      lc_risk_pct, lc_size_mode, lc_start_usd, lc_open_ms),
    INDEX (lc_day), INDEX (lc_size_mode))'''))

have = {r['c'] for r in db.execute('''SELECT COLUMN_NAME c FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME=%s''', (TABLE,), fetch=True)}
for col, ddl in (('lc_drag_pct',  'DECIMAL(10,4) NOT NULL DEFAULT 0 AFTER lc_gross_pct'),
                 ('lc_gross_usd', 'DECIMAL(16,4) NOT NULL DEFAULT 0 AFTER lc_net_pct'),
                 ('lc_drag_usd',  'DECIMAL(16,4) NOT NULL DEFAULT 0 AFTER lc_gross_usd')):
    if col not in have:
        db.execute('ALTER TABLE %s ADD COLUMN %s %s' % (TABLE, col, ddl))
        print('# ALTER: added %s' % col)

ins = []
for mode, A in (('shared', SH), ('constant', CO)):
    for i, x in enumerate(T):
        p = A[i]
        ins.append((SIDE_RULE, STOP, SWING, COST, PYR, RISK_PCT, mode, START, i + 1,
                    x['day'], x['lbl'], x['open_ms'], x['close_ms'], x['dr'], x['side'], x['grade'],
                    x['entry_px'], x['exit_px'], round(x['hold_m'], 2), round(x['mfe'], 4),
                    round(x['mae'], 4), int(x['stopped']), round(x['gross'], 4), COST,
                    round(x['net'], 4), round(p['notional'] * x['gross'] / 100.0, 4),
                    round(p['notional'] * COST / 100.0, 4),
                    p['n_live'], round(p['lev'], 4), round(p['eq_open'], 4), round(p['notional'], 4),
                    round(p['risk_usd'], 4), round(p['pnl'], 4), round(p['eq_close'], 4),
                    round(p['dd'] * 100, 4)))
db.executemany(Q('''INSERT INTO __TBL__
 (lc_side_rule,lc_stop_pct,lc_swing_pct,lc_cost_pct,lc_pyr_max,lc_risk_pct,lc_size_mode,lc_start_usd,
  lc_seq,lc_day,lc_octosig,lc_open_ms,lc_close_ms,lc_dr,lc_side,lc_grade,lc_entry_px,lc_exit_px,
  lc_hold_min,lc_mfe_pct,lc_mae_pct,lc_stopped,lc_gross_pct,lc_drag_pct,lc_net_pct,lc_gross_usd,
  lc_drag_usd,lc_n_live,lc_lev,lc_eq_open,lc_notional,lc_risk_usd,lc_pnl_usd,lc_eq_close,lc_dd_pct)
 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
 ON DUPLICATE KEY UPDATE lc_lev=VALUES(lc_lev), lc_eq_open=VALUES(lc_eq_open),
  lc_notional=VALUES(lc_notional), lc_risk_usd=VALUES(lc_risk_usd), lc_pnl_usd=VALUES(lc_pnl_usd),
  lc_eq_close=VALUES(lc_eq_close), lc_dd_pct=VALUES(lc_dd_pct), lc_n_live=VALUES(lc_n_live),
  lc_drag_pct=VALUES(lc_drag_pct), lc_gross_usd=VALUES(lc_gross_usd),
  lc_drag_usd=VALUES(lc_drag_usd)'''), ins)
n_sh = db.execute(Q("SELECT COUNT(*) c FROM __TBL__ WHERE lc_size_mode='shared'"), fetch=True)[0]['c']
n_co = db.execute(Q("SELECT COUNT(*) c FROM __TBL__ WHERE lc_size_mode='constant'"), fetch=True)[0]['c']
print('# BANKED: ' + TABLE + ' — %d rows written this run, %d shared + %d constant in the table'
      % (len(ins), n_sh, n_co))
print('# config: %s · stop %.2f%% · swing %.2f%% · cost %.4f%% · pyramid NO CAP · risk %.1f%% · start $%.2f'
      % (SIDE_RULE, STOP, SWING, COST, RISK_PCT, START))
print('# max concurrent legs with the cap dropped: %d' % mx)
if UNRES:
    print('# UNRESOLVED and EXCLUDED, %d: no favourable swing pivot inside the tape — %s'
          % (len(UNRES), ', '.join('%s %s' % r for r in UNRES)))
print()
print('## THE COMPLETE TABLE — shared budget, read back from ' + TABLE)
q = db.execute(Q("""SELECT lc_seq,lc_day,lc_octosig,lc_dr,lc_side,lc_grade,lc_stopped,lc_hold_min,
       lc_gross_pct,lc_drag_pct,lc_net_pct,lc_n_live,lc_lev,lc_eq_open,lc_notional,lc_risk_usd,
       lc_gross_usd,lc_drag_usd,lc_pnl_usd,lc_eq_close,lc_dd_pct
  FROM __TBL__ WHERE lc_size_mode='shared' AND lc_risk_pct=%s AND lc_start_usd=%s
  ORDER BY lc_seq"""), (RISK_PCT, START), fetch=True)
print('| # | day | octo-sig | dr | side | grade | exit | hold min | gross % | drag % | net % | legs live | LEV | equity open $ | notional $ | risk $ | gross $ | drag $ | P&L $ | equity close $ | DD % |')
print('|' + '---|' * 21)
for r in q:
    print('| %d | %s | %s | %+d | %s | %s | %s | %.1f | %+.3f | -%.4f | %+.3f | %d | **%.2fx** | %.2f | %.2f | %.2f | %+.2f | **-%.2f** | **%+.2f** | **%.2f** | %.2f |'
          % (r['lc_seq'], str(r['lc_day'])[5:], r['lc_octosig'], r['lc_dr'], r['lc_side'],
             'wt' if r['lc_grade'] == 'with-trend' else 'at', 'STOP' if r['lc_stopped'] else 'pivot',
             r['lc_hold_min'], r['lc_gross_pct'], r['lc_drag_pct'], r['lc_net_pct'], r['lc_n_live'],
             r['lc_lev'], r['lc_eq_open'], r['lc_notional'], r['lc_risk_usd'], r['lc_gross_usd'],
             r['lc_drag_usd'], r['lc_pnl_usd'], r['lc_eq_close'], r['lc_dd_pct']))

print()
print('## SUMMARY')
print('| sizing mode | trades | start $ | final $ | return % | max DD % | peak lev | min lev | mean lev | worst trade $ | best trade $ |')
print('|' + '---|' * 11)
for mode, A, e, d in (('shared budget', SH, eq_sh, dd_sh), ('constant per leg', CO, eq_co, dd_co)):
    lv = [p['lev'] for p in A]; pl = [p['pnl'] for p in A]
    print('| %s | %d | %.2f | **%.2f** | **%+.2f** | %.2f | %.2fx | %.2fx | %.2fx | %+.2f | %+.2f |'
          % (mode, len(A), START, e, (e / START - 1) * 100, d * 100, max(lv), min(lv),
             float(np.mean(lv)), min(pl), max(pl)))

print()
print('## PER DAY — shared budget, sliced by the LAST CLOSE on that day (not the open day)')
print('| day | trades | equity close $ | day P&L $ | day % | DD so far % |')
print('|' + '---|' * 6)
prev = START
for day in DAYS:
    idx = [i for i, x in enumerate(T) if x['day'] == day]
    if not idx: continue
    last = max(idx, key=lambda i: T[i]['close_ms'])
    e = SH[last]['eq_close']; dd = max(SH[i]['dd'] for i in idx)
    print('| %s | %d | %.2f | %+.2f | %+.2f %% | %.2f |' % (day[5:], len(idx), e, e - prev,
          (e / prev - 1) * 100, dd * 100))
    prev = e

print()
print('## DRAG — what the round trip actually cost, read back from ' + TABLE)
dq = db.execute(Q('''SELECT lc_day d, COUNT(*) n, SUM(lc_gross_usd) g, SUM(lc_drag_usd) dr,
       SUM(lc_pnl_usd) p, SUM(lc_notional) nt
  FROM __TBL__ WHERE lc_size_mode='shared' AND lc_risk_pct=%s AND lc_start_usd=%s
  GROUP BY lc_day ORDER BY lc_day'''), (RISK_PCT, START), fetch=True)
print('| day | trades | notional traded $ | gross P&L $ | drag paid $ | net P&L $ | drag as %% of gross |'.replace('%%','%'))
print('|' + '---|' * 7)
tg = td = tp = tn = 0.0
for r in dq:
    g = float(r['g']); dr = float(r['dr']); p = float(r['p']); nt = float(r['nt'])
    tg += g; td += dr; tp += p; tn += nt
    print('| %s | %d | %.2f | %+.2f | **-%.2f** | %+.2f | %s |'
          % (str(r['d'])[5:], r['n'], nt, g, dr, p,
             ('%.1f %%' % (100.0 * dr / abs(g))) if g else 'n/a'))
print('| **' + SPAN + '** | %d | **%.2f** | **%+.2f** | **-%.2f** | **%+.2f** | **%.1f %%** |'
      % (sum(r['n'] for r in dq), tn, tg, td, tp, 100.0 * td / abs(tg)))
print()
print('- drag per trade: $%.2f mean, $%.2f min, $%.2f max (it is %.4f %% of notional, so it grows with equity)'
      % (td / max(1, len(SH)), min(float(p['notional']) * COST / 100 for p in SH),
         max(float(p['notional']) * COST / 100 for p in SH), COST))
print('- drag as a share of the $%.2f account growth: %.1f %% — $%.2f paid to make $%.2f'
      % (eq_sh - START, 100.0 * td / (eq_sh - START), td, eq_sh - START))

print()
print('## WHAT THE DRAG COSTS COMPOUNDED — same trades, drag set to zero')
print('| variant | final $ | return % | delta $ | delta pp |')
print('|' + '---|' * 5)
def walk_nodrag(rows, mode, risk_pct, cost):
    ev = []
    for i, x in enumerate(rows): ev.append((x['open_ms'], 0, i)); ev.append((x['close_ms'], 1, i))
    ev.sort()
    eq = START; pos = {}; n = 0
    for _t, kind, i in ev:
        x = rows[i]
        if kind == 0:
            share = risk_pct if mode == 'constant' else risk_pct / (n + 1)
            pos[i] = eq * share / WORST; n += 1
        else:
            nt = pos.pop(i); n -= 1
            eq += nt * (x['gross'] - cost) / 100.0
    return eq
for lab, c in (('as traded, drag %.4f %%' % COST, COST), ('drag 0.0000 %% (no fees, no slippage)', 0.0)):
    e = walk_nodrag(T, 'shared', RISK_PCT, c)
    print('| %s | %.2f | %+.2f | %+.2f | %+.2f |' % (lab.replace('%%','%'), e, (e / START - 1) * 100,
          e - eq_sh, (e / START - 1) * 100 - (eq_sh / START - 1) * 100))

print()
print('## RISK BUDGET SWEEP — the one value I chose, so here is the curve around it')
print('| risk per entry % | implied lev when alone | final $ shared | DD % shared | final $ constant | DD % constant |')
print('|' + '---|' * 6)
for rp in (0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 8.0, 10.0):
    _a, e1, d1 = walk(T, 'shared', rp); _b, e2, d2 = walk(T, 'constant', rp)
    print('| %.1f | %.2fx | %.2f | %.2f | %.2f | %.2f |' % (rp, rp / WORST, e1, d1 * 100, e2, d2 * 100))
db.disconnect()
