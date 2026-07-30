"""build_xpred_lab — persist the x-cross-pred research grid so analysis is a SELECT, not a re-walk.

The question: can we predict x crossing r before it happens?
TRIAL   = an x-OOB run clipped to a TF seam (Joe 0728: test while x is OOB, stop at the seam, restart next
          seam if x is still OOB).
FORM a  = h moving toward zero for n consecutive emerging bars.   h = x - r
FORM b  = |h| contracting for n consecutive emerging bars.
n       = int(TF_min * 12 * frac) — a fraction of the TF bar, COUNTED IN EMERGING 5s BARS.

One row per (trial x form x frac), including trials where no prediction fired (xl_pred_ms NULL), so the
base rate — "share of trials containing a cross at all" — is queryable without re-running anything.
No caps: the ever-cross columns run to end of tape.

    python3 build_xpred_lab.py [TF ...]      # default 15
"""
import sys, datetime as dt
import numpy as np
import build_rpl_6of9 as B
import optimus9.orchestration.rpl_walk as R
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

WIN_S = int(dt.datetime(2026, 6, 12, tzinfo=dt.timezone.utc).timestamp() * 1000)
WIN_E = int(dt.datetime(2026, 6, 14, tzinfo=dt.timezone.utc).timestamp() * 1000)
FRACS = [(1, 40), (1, 30), (1, 20), (1, 15), (1, 10), (1, 6), (1, 4), (1, 2)]

DDL = '''CREATE TABLE IF NOT EXISTS rpl_xpred_lab (
    xl_pk          BIGINT AUTO_INCREMENT PRIMARY KEY,
    xl_created_dt  DATETIME DEFAULT CURRENT_TIMESTAMP,
    xl_tf          INT,                       -- the TF under test
    xl_side        INT,                       -- +1 x hi-OOB (cross DOWN through r) / -1 lo-OOB (cross UP)
    xl_form        VARCHAR(2),                -- 'a' toward-zero | 'b' |h| contracting
    xl_frac_num    INT, xl_frac_den INT,      -- the fraction of the TF bar
    xl_n_bars      INT,                       -- resolved run length, emerging 5s bars
    -- trial (an x-OOB run clipped to a TF seam)
    xl_trial_ms    BIGINT, xl_trial_utc VARCHAR(19),
    xl_trial_end_ms BIGINT,
    xl_trial_bars  INT,                       -- trial length in emerging bars
    xl_h_open      FLOAT,                     -- h at trial start
    xl_h_absmin    FLOAT,                     -- closest x got to r inside the trial
    xl_x_open      FLOAT, xl_r_open FLOAT,
    -- prediction (NULL when the form never fired in this trial)
    xl_pred_ms     BIGINT, xl_pred_utc VARCHAR(19),
    xl_pred_idx    INT,                       -- bars into the trial
    xl_x           FLOAT, xl_r FLOAT, xl_h FLOAT,
    xl_h_slope     FLOAT,                     -- h change over the qualifying run
    xl_s2r         FLOAT,
    xl_px_pred     FLOAT,
    -- confirmation
    xl_cross_in_trial TINYINT,                -- did x cross r later in the SAME trial
    xl_cross_ms    BIGINT, xl_cross_utc VARCHAR(19),
    xl_lag_s       INT,                       -- prediction -> in-trial cross
    xl_cross_ever_ms BIGINT,                  -- next cross at any later bar (no cap, to end of tape)
    xl_lag_ever_s  INT,
    xl_px_cross    FLOAT,
    INDEX (xl_tf, xl_side, xl_form), INDEX (xl_frac_den), INDEX (xl_cross_in_trial))'''

E = R.L0['E']; gts = B.gts
HI, LO = R.HI, R.LO
utc = lambda ms: dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
pxs = R.L0.get('pxs')


def build(tf):
    a, b = int(np.searchsorted(gts, WIN_S)), int(np.searchsorted(gts, WIN_E))
    x, r = E[tf]['x'], E[tf]['r']
    h = x - r
    s2r = R.L0['s2r']
    bar = gts // (tf * 60000)
    nbar = tf * 12
    rows = []
    for side in (1, -1):
        oob = (x >= HI) if side > 0 else (x <= LO)
        below = (h < 0) if side > 0 else (h > 0)
        cross = below & ~np.r_[False, below[:-1]]          # completed x-r cross toward the trade side
        ck = np.flatnonzero(cross)
        trials = []
        k = a
        while k < b:
            if oob[k]:
                s = k
                while k + 1 < b and oob[k + 1] and bar[k + 1] == bar[s]:
                    k += 1
                trials.append((s, k))
            k += 1
        for s, e in trials:
            seg = h[s:e + 1]
            if len(seg) < 2:
                continue
            sg = (seg < 0) if side > 0 else (seg > 0)
            jin = np.flatnonzero(sg & ~np.r_[sg[0], sg[:-1]])
            prev = np.r_[seg[0], seg[:-1]]
            base = dict(tf=tf, side=side, tms=int(gts[s]), tend=int(gts[e]), tbars=e - s + 1,
                        hopen=float(h[s]), habs=float(np.abs(seg).min()),
                        xopen=float(x[s]), ropen=float(r[s]))
            for form in ('a', 'b'):
                if form == 'a':
                    cond = ((seg - prev) < 0) if side > 0 else ((seg - prev) > 0)
                    cond = cond & ((seg > 0) if side > 0 else (seg < 0))
                else:
                    cond = (np.abs(seg) < np.abs(prev)) & ((seg > 0) if side > 0 else (seg < 0))
                idx = np.arange(len(seg)); rst = np.where(cond, 0, idx + 1)
                rl = (idx + 1) - np.maximum.accumulate(rst)
                for num, den in FRACS:
                    n = max(1, int(nbar * num / den))
                    fire = np.flatnonzero((rl >= n) & ~np.r_[False, (rl >= n)[:-1]])
                    row = dict(base, form=form, num=num, den=den, n=n)
                    if len(fire):
                        k0 = int(fire[0]); g = s + k0
                        jj = jin[jin > k0]
                        ever = ck[ck > g]
                        row.update(pms=int(gts[g]), pidx=k0, X=float(x[g]), Rr=float(r[g]), H=float(h[g]),
                                   slope=float(seg[k0] - seg[max(0, k0 - n)]), s2=float(s2r[g]),
                                   pxp=float(pxs[g]) if pxs is not None else None,
                                   cit=1 if len(jj) else 0,
                                   cms=int(gts[s + int(jj[0])]) if len(jj) else None,
                                   lag=int((jj[0] - k0) * 5) if len(jj) else None,
                                   ems=int(gts[int(ever[0])]) if len(ever) else None,
                                   elag=int((gts[int(ever[0])] - gts[g]) / 1000) if len(ever) else None,
                                   pxc=float(pxs[s + int(jj[0])]) if (len(jj) and pxs is not None) else None)
                    rows.append(row)
    return rows


if __name__ == '__main__':
    tfs = [int(v) for v in sys.argv[1:] if v.isdigit()] or [15]
    d = DatabaseManager(**get_db_config()); d.connect(); d.execute(DDL)
    for tf in tfs:
        d.execute('DELETE FROM rpl_xpred_lab WHERE xl_tf=%s', (tf,))
        rows = build(tf)
        d.executemany('''INSERT INTO rpl_xpred_lab (xl_tf,xl_side,xl_form,xl_frac_num,xl_frac_den,xl_n_bars,
            xl_trial_ms,xl_trial_utc,xl_trial_end_ms,xl_trial_bars,xl_h_open,xl_h_absmin,xl_x_open,xl_r_open,
            xl_pred_ms,xl_pred_utc,xl_pred_idx,xl_x,xl_r,xl_h,xl_h_slope,xl_s2r,xl_px_pred,
            xl_cross_in_trial,xl_cross_ms,xl_cross_utc,xl_lag_s,xl_cross_ever_ms,xl_lag_ever_s,xl_px_cross)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
            [(w['tf'], w['side'], w['form'], w['num'], w['den'], w['n'],
              w['tms'], utc(w['tms']), w['tend'], w['tbars'], w['hopen'], w['habs'], w['xopen'], w['ropen'],
              w.get('pms'), utc(w['pms']) if w.get('pms') else None, w.get('pidx'),
              w.get('X'), w.get('Rr'), w.get('H'), w.get('slope'), w.get('s2'), w.get('pxp'),
              w.get('cit'), w.get('cms'), utc(w['cms']) if w.get('cms') else None, w.get('lag'),
              w.get('ems'), w.get('elag'), w.get('pxc')) for w in rows])
        print('TF%-3d %d rows (%d trials x 2 forms x %d fracs)' % (tf, len(rows), len(rows) // (2 * len(FRACS)), len(FRACS)))
    d.disconnect()
