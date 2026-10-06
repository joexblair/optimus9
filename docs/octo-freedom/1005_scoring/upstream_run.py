"""Upstream OAT sweep driver. One Rig per process, sharded by knob. Joe 1005: 12 h budget,
objective "best PnL with minimal loss of trades".

env: LG_SHARD, LG_NSHARD, LG_TAPE_END, LG_DAYS_FIT, LG_DAYS_TEST
Banks every cell to `lazyg_sweep_up`. NOTHING IS RANKED HERE - Joe sets what winning means.
"""
import os as _os
_HERE = _os.path.dirname(_os.path.abspath(__file__))
import sys, io, time, contextlib
import numpy as np
sys.path.insert(0, '/home/joe/thecodes'); sys.path.insert(0, _HERE)
import upstream as UP                       # does the argv patch, Rig memoisation, walk_day
import sweep as W                           # route() + legs_at() + the scoring convention
from optimus9.compute import momo_config as MC
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

FIT  = [x.strip() for x in _os.environ['LG_DAYS_FIT'].split(',')  if x.strip()]
TEST = [x.strip() for x in _os.environ['LG_DAYS_TEST'].split(',') if x.strip()]
SHARD, NSHARD = int(_os.environ.get('LG_SHARD', 0)), int(_os.environ.get('LG_NSHARD', 1))
COST = W.COST
# JOE 1005 RULED: 1.5 % risk per trade = 1.67x leverage. Pinned so the sweep optimises the MECH,
# not the leverage -- an unpinned risk axis just reports 'use max leverage'.
W.CUR['risk'] = 1.5        # and CUR['stop'] = 0.95 comes from sweep.py

# ---- momentum: wrap momo_bank so a knob can be overridden for every bank
_REAL_BANK = MC.momo_bank
MOMO_OVR = {}
def _bank(db, tf, version=None):
    d = dict(_REAL_BANK(db, tf, version)); d.update(MOMO_OVR); return d
MC.momo_bank = _bank
try:
    import optimus9.analysis.jig as _J
    if hasattr(_J, 'momo_bank'): _J.momo_bank = _bank
except Exception: pass

# ===================== THE THREE REAL KNOB STORES, ALL MEASURED 1005 =====================
# Three wrong stores were tried and discarded before these were found, each verified by A/B rather
# than by reading:
#   1. jig module constants  -> ws1mage_rev binds them as DEFAULT ARGS at def time. setattr: no-op.
#   2. the function __defaults__ -> the walk passes dwell/rev_wob/hold EXPLICITLY from rig.C.
#   3. momo_config v1 (DB)   -> walk_mom_models.momentum_true OVERWRITES 5 keys from WS1_CFG, and
#                               momo_window(SPAN_MIN=10) overrides the bank's momo_window_min 60.
# What actually moves an octo-sig:
#   rig.C   a plain dict on the CACHED Rig. Mutate between cells, no reload.
#   WS1_CFG walk_mom_models.WS1_CFG - slope_min 0.4, slack_ref 0.4, r2_min 0.7, level_slack 13.9
#   SPAN    walk_mom_models.SPAN_MIN = 10, the lattice span the chain runs at
_RIGREF = {}
def _rig():
    # the Rig is built lazily by UP.walk_day; force it so snap() has something to read
    if UP._RIG is None:
        import datetime as _dt
        ms = int(_dt.datetime(2026, 10, 4, tzinfo=_dt.timezone.utc).timestamp() * 1000)
        UP._cached_rig((ms, ms + 86400000))
    return UP._RIG

# knob, lo, hi, step, store
GRIDS = [
 # --- rig.C: the walk's own mechanics
 ('dwell',            1,    12,   1,    'C'),
 ('rev_wob',          1,    8,    1,    'C'),
 ('boundary_xwob',    1,    12,   1,    'C'),
 ('stall_n',          2,    12,   1,    'C'),
 ('momo_fence_r',     5,    30,   1,    'C'),
 ('momo_xwob',        1,    10,   1,    'C'),
 ('momo_span_min',    4,    30,   2,    'C'),
 ('oob_hi',           70.0, 95.0, 0.5,  'C'),
 ('fence_hi',         60.0, 90.0, 0.5,  'C'),
 ('fence',            35.0, 65.0, 0.5,  'C'),
 ('xwob',             1,    12,   1,    'C'),
 ('r_wob',            1,    10,   1,    'C'),
 ('count_min',        1,    8,    1,    'C'),
 ('support_min',      8,    23,   1,    'C'),
 ('return_bars',      1,    12,   1,    'C'),
 ('xrace_hold',       1,    15,   1,    'C'),
 ('mage_dwell',       2,    24,   2,    'C'),
 ('lookback_s',       60,   600,  30,   'C'),
 ('tp_lookback_min',  1,    12,   1,    'C'),
 ('ride_tf_hi',       1,    12,   1,    'C'),
 ('dwell_min_per_tf', 1,    6,    1,    'C'),
 ('confirm_lag_s',    30,   360,  30,   'C'),
 ('wmt_tf_hi',        8,    23,   1,    'C'),
 ('wmt_tf_lo',        1,    6,    1,    'C'),
 # --- WS1_CFG: the LIVE momentum knobs (momo_config's are overwritten)
 ('momo_slope_min',   0.05, 3.00, 0.05, 'W'),
 ('momo_slack_ref',   0.05, 3.00, 0.05, 'W'),
 ('momo_r2_min',      0.00, 1.00, 0.05, 'W'),
 ('level_slack',      0.0,  30.0, 0.5,  'W'),
 # --- the lattice span
 ('SPAN_MIN',         2,    30,   2,    'S'),
]
FLOATK = {'oob_hi','fence_hi','fence','momo_slope_min','momo_slack_ref','momo_r2_min','level_slack'}

def grid(lo, hi, st):
    n = int(round((hi - lo) / st)) + 1
    return [round(lo + i * st, 6) for i in range(n)]

_BASE = {}
def snap():
    r = _rig()
    for n, _a, _b, _c, w in GRIDS:
        if   w == 'C': _BASE[n] = r.C[n]
        elif w == 'W': _BASE[n] = UP.RLW.W.WS1_CFG[n]
        else:          _BASE[n] = UP.RLW.W.SPAN_MIN

def apply_knob(name, where, val):
    if   where == 'C': _rig().C[name] = val
    elif where == 'W': UP.RLW.W.WS1_CFG[name] = val
    else:              UP.RLW.W.SPAN_MIN = val

def reset_all():
    r = _rig()
    for n, _a, _b, _c, w in GRIDS:
        if   w == 'C': r.C[n] = _BASE[n]
        elif w == 'W': UP.RLW.W.WS1_CFG[n] = _BASE[n]
        else:          UP.RLW.W.SPAN_MIN = _BASE[n]
    # oob_lo and fence_lo mirror their hi partners (oob is 15/85, the fence is 25/75)
    r.C['oob_lo'] = 100.0 - r.C['oob_hi']
    r.C['fence_lo'] = 100.0 - r.C['fence_hi']

DDL = """CREATE TABLE IF NOT EXISTS lazyg_sweep_up (
    lu_pk BIGINT AUTO_INCREMENT PRIMARY KEY,
    lu_knob VARCHAR(32) NOT NULL, lu_where VARCHAR(6) NOT NULL,
    lu_val DECIMAL(12,5) NOT NULL, lu_is_cur TINYINT NOT NULL,
    lu_fit_days SMALLINT NOT NULL, lu_test_days SMALLINT NOT NULL,
    lu_fit_sig SMALLINT NOT NULL, lu_test_sig SMALLINT NOT NULL,
    lu_fit_n SMALLINT NOT NULL, lu_fit_total DECIMAL(12,4) NOT NULL,
    lu_fit_mean DECIMAL(10,5) NOT NULL, lu_fit_fin DECIMAL(16,6) NOT NULL,
    lu_fit_dd DECIMAL(8,5) NOT NULL,
    lu_test_n SMALLINT NOT NULL, lu_test_total DECIMAL(12,4) NOT NULL,
    lu_test_mean DECIMAL(10,5) NOT NULL, lu_test_fin DECIMAL(16,6) NOT NULL,
    lu_test_dd DECIMAL(8,5) NOT NULL,
    lu_growth DECIMAL(12,8) NOT NULL,     -- min(fit_fin^(1/fitdays), test_fin^(1/testdays))
    lu_retention DECIMAL(8,5) NOT NULL,   -- min(fit_n/base, test_n/base)
    lu_secs DECIMAL(8,2) NOT NULL,
    UNIQUE KEY uq_lu (lu_knob, lu_val, lu_fit_days, lu_test_days),
    INDEX (lu_knob), INDEX (lu_growth))"""

def score_set(days, sigmap):
    """route + score the walked signals with sweep.py's banked convention at CUR downstream knobs."""
    o, cl, nt = [], [], []
    Hs, Ls = W.piv(W.CUR['swing']); stop = W.CUR['stop']
    nsig = 0
    for day in days:
        for lbl in sigmap[day]:
            try: k = W.S.K(day + ' ' + lbl)
            except Exception: continue
            nsig += 1
            st, gr, d = W.route(k, W.CUR)
            if st != 'CONFLUENCE': continue
            tgt = Ls if d > 0 else Hs
            nx = tgt[tgt > k]
            if nx.size == 0: continue
            j = int(nx[0]); e = float(W.S.PX[k]); seg = W.S.PX[k:j + 1]
            adv = (seg - e) / e * 100.0 if d > 0 else (e - seg) / e * 100.0
            fav = (e - seg) / e * 100.0 if d > 0 else (seg - e) / e * 100.0
            hit = np.flatnonzero(np.isfinite(adv) & (adv >= stop))
            if hit.size: ex, g = k + int(hit[0]), -stop
            else:        ex, g = j, float(np.nanmax(fav))
            o.append(k); cl.append(ex); nt.append(g - COST)
    if not o: return nsig, 0, 0.0, 0.0, 1.0, 0.0
    o, cl, nt = np.array(o), np.array(cl), np.array(nt)
    fin, dd, n = W.grid_block(o, cl, nt, W.CUR['pyr'], [W.CUR['risk']], stop + COST)
    return nsig, len(nt), float(nt.sum()), float(nt.mean()), float(fin[0]), float(dd[0])

if __name__ == '__main__':
    db = DatabaseManager(**get_db_config()); db.connect(); db.execute(DDL)
    mine = [g for i, g in enumerate(GRIDS) if i % NSHARD == SHARD]
    snap()
    print('# shard %d/%d | %d knobs | %d cells | FIT %d days TEST %d days'
          % (SHARD, NSHARD, len(mine), sum(len(grid(a,b,c)) for _n,a,b,c,_w in mine), len(FIT), len(TEST)), flush=True)
    base = None
    for name, lo, hi, st, where in mine:
        cur = float(_BASE[name])
        for val in grid(lo, hi, st):
            v = float(val) if name in FLOATK else int(val)
            t0 = time.time()
            reset_all(); apply_knob(name, where, v)
            if name == 'oob_hi':   _rig().C['oob_lo'] = 100.0 - v
            if name == 'fence_hi': _rig().C['fence_lo'] = 100.0 - v
            sig = {}
            ok = True
            for day in FIT + TEST:
                try: sig[day] = UP.walk_day(day)
                except Exception as ex: ok = False; break
            if not ok: print('#   %s=%s WALK FAILED' % (name, v), flush=True); continue
            fs, fn, ft, fm, ffin, fdd = score_set(FIT, sig)
            ts_, tn, tt, tm, tfin, tdd = score_set(TEST, sig)
            gf = ffin ** (1.0 / len(FIT)) if ffin > 0 else 0.0
            gt = tfin ** (1.0 / len(TEST)) if tfin > 0 else 0.0
            if base is None: base = (max(1, fn), max(1, tn))
            row = (name, where, v, 1 if abs(float(v) - float(cur)) < 1e-9 else 0,
                   len(FIT), len(TEST), fs, ts_, fn, round(ft,4), round(fm,5), round(ffin,6), round(fdd,5),
                   tn, round(tt,4), round(tm,5), round(tfin,6), round(tdd,5),
                   round(min(gf, gt),8), round(min(fn/base[0], tn/base[1]),5), round(time.time()-t0,2))
            db.execute('INSERT INTO lazyg_sweep_up (lu_knob,lu_where,lu_val,lu_is_cur,lu_fit_days,'
                       'lu_test_days,lu_fit_sig,lu_test_sig,lu_fit_n,lu_fit_total,lu_fit_mean,'
                       'lu_fit_fin,lu_fit_dd,lu_test_n,lu_test_total,lu_test_mean,lu_test_fin,'
                       'lu_test_dd,lu_growth,lu_retention,lu_secs) VALUES (' + ','.join(['%s']*21) +
                       ') ON DUPLICATE KEY UPDATE lu_growth=VALUES(lu_growth)', row)
            print('#   %-22s = %-8s | fit n=%3d mean %+.4f | test n=%3d mean %+.4f | growth %.6f | ret %.3f | %.0f s'
                  % (name, v, fn, fm, tn, tm, min(gf,gt), min(fn/base[0], tn/base[1]), time.time()-t0), flush=True)
    reset_all(); db.disconnect()
    print('# SHARD %d DONE' % SHARD, flush=True)
