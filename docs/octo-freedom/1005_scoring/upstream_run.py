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

# ============================= WHAT ACTUALLY REACHES AN OCTO-SIG =============================
# MEASURED 1005, and it corrected my own 32-knob census: `report_leash_walk` calls exactly TWO
# jig/momentum entry points -- `flat_run_at` (line 194) and `ws1mage_rev` (line 197). It never calls
# anchor_floater, sideways_reversal, wsf_qualify, ws_fin_9of12 or weak_mage_tf, so SR_*, WSF_*, WMT_*
# and AF_BLOCK CANNOT move a signal. They were in my census because they are Jig knobs, not because
# they are on this mech's path.
#
# AND: `ws1mage_rev(g1, sig_mage, hi, lo, dwell=WS1MR_DWELL, rev_wob=WS1MR_REV_WOB, hold=WS1MR_HOLD,
# gate='rev')` binds those as POSITIONAL DEFAULTS at def time -- __defaults__ == (3, 2, 4, 'rev').
# `setattr(jig, 'WS1MR_DWELL', v)` reaches NOTHING. Four cells banked identical values before this
# was caught. The fix patches the function's __defaults__ tuple, which both the jig module and
# report_leash_walk's direct import see, because it is the same function object.
_W1 = UP.RLW.ws1mage_rev
_W1_BASE = list(_W1.__defaults__)            # (dwell, rev_wob, hold, gate)
def set_w1(idx, val):
    d = list(_W1_BASE); d[idx] = val; _W1.__defaults__ = tuple(d)
def reset_w1(): _W1.__defaults__ = tuple(_W1_BASE)

MOMO_KEYS = ('mmc_momo_slope_min','mmc_momo_slack_ref','mmc_momo_r2_min','mmc_momo_window_min',
             'mmc_momo_step_min','mmc_momo_fixed_samples','mmc_k_window','mmc_level_slack',
             'mmc_curl_arc_min','mmc_curl_vtx_lo','mmc_curl_vtx_hi','mmc_curl_r2_min')

# knob, lo, hi, step, where   where in {'w1d','w1r','w1h','rlw','momo'}
GRIDS = [
 ('WS1MR_DWELL',    1,    12,   1,    'w1d'),
 ('WS1MR_REV_WOB',  1,    6,    1,    'w1r'),
 ('WS1MR_HOLD',     1,    12,   1,    'w1h'),
 ('MOMO_SAMPLES',   2,    8,    1,    'rlw'),
 ('MOMO_TOL',       0.50, 5.00, 0.05, 'rlw'),
 ('mmc_momo_slope_min',     0.10, 5.00, 0.05, 'momo'),
 ('mmc_momo_slack_ref',     0.10, 5.00, 0.05, 'momo'),
 ('mmc_momo_r2_min',        0.00, 1.00, 0.05, 'momo'),
 ('mmc_momo_window_min',    15,   120,  5,    'momo'),
 ('mmc_momo_step_min',      1,    15,   1,    'momo'),
 ('mmc_momo_fixed_samples', 5,    41,   2,    'momo'),
 ('mmc_k_window',           1,    12,   1,    'momo'),
 ('mmc_level_slack',        0.0,  20.0, 0.5,  'momo'),
 ('mmc_curl_arc_min',       0.0,  15.0, 0.5,  'momo'),
 ('mmc_curl_vtx_lo',        0.00, 0.50, 0.05, 'momo'),
 ('mmc_curl_vtx_hi',        0.50, 1.00, 0.05, 'momo'),
 ('mmc_curl_r2_min',        0.00, 1.00, 0.05, 'momo'),
]
INT = {'WS1MR_DWELL','WS1MR_REV_WOB','WS1MR_HOLD','MOMO_SAMPLES',
       'mmc_momo_window_min','mmc_momo_step_min','mmc_momo_fixed_samples','mmc_k_window'}
W1IDX = {'w1d': 0, 'w1r': 1, 'w1h': 2}

def grid(lo, hi, st):
    n = int(round((hi - lo) / st)) + 1
    return [round(lo + i * st, 6) for i in range(n)]

def apply_knob(name, where, val):
    if where in W1IDX: set_w1(W1IDX[where], val)
    elif where == 'rlw': setattr(UP.RLW, name, val)
    else: MOMO_OVR[name] = val

def reset_all():
    reset_w1(); MOMO_OVR.clear()
    UP.RLW.MOMO_SAMPLES = _RLW_BASE['MOMO_SAMPLES']; UP.RLW.MOMO_TOL = _RLW_BASE['MOMO_TOL']
_RLW_BASE = {'MOMO_SAMPLES': UP.RLW.MOMO_SAMPLES, 'MOMO_TOL': UP.RLW.MOMO_TOL}

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
    print('# shard %d/%d | %d knobs | %d cells | FIT %d days TEST %d days'
          % (SHARD, NSHARD, len(mine), sum(len(grid(a,b,c)) for _n,a,b,c,_w in mine), len(FIT), len(TEST)), flush=True)
    base = None
    for name, lo, hi, st, where in mine:
        if where == 'momo':   cur = float(_REAL_BANK(db, 5)[name])
        elif where in W1IDX:  cur = float(_W1_BASE[W1IDX[where]])
        else:                 cur = float(_RLW_BASE[name])
        for val in grid(lo, hi, st):
            v = int(val) if name in INT else float(val)
            t0 = time.time()
            reset_all(); apply_knob(name, where, v)
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
