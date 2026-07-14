"""gravity_study.py — does s8Mage's gravity FLIP, or MEANDER back to the side it came from? (Joe 0714)

Joe: "find a way to predict when the gravity is flipping, vs the gravity just meandering around the board
only to return to the same side.  My theory: LTF lines (s2Mage) tell you whether the price move has enough
momentum to pressure s8Mage to flip."

This is a SURVIVAL / COMPETING-RISKS problem, not a classification one. An episode has two terminations
and the question is a hazard, not a label:

  home      the last OOB side s8Mage touched (+1 hi / -1 lo)
  EPISODE   s8Mage leaves that OOB zone and wanders the board
  ends when it next touches an OOB boundary:
              same side as home      -> MEANDER   (the gravity held)
              opposite side to home  -> FLIP      (the gravity turned)

The LABEL is hindsight (score-side): which boundary it hits first.  Every FEATURE is causal — sampled at
the episode start and at fixed elapsed marks after it, so nothing reads past the bar it claims to be at.

Per-episode rows -> `gravity_episode` (`ge_`), per-mark rows -> `gravity_mark` (`gm_`).  Every slice is a
query afterwards; no re-run (ci_initiatives: persist the rows, never just the aggregate).

  python3 gravity_study.py [days] [end_YYYY-MM-DD_HH:MM]      (default 7 days, now)
"""
import sys, datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.analysis.jig import Jig
from optimus9 import DatabaseManager
from optimus9.config import get_db_config
import bias_emit as BE

CFG_TAG = 'g0714'
TF_GRAV = BE.TF_MID              # 8 — the gravity band
MARKS_MIN = [0, 5, 10, 20, 30, 45, 60, 90]      # elapsed marks into the episode, minutes (causal snapshots)
HI, LO = 85.0, 15.0

EP_DDL = """CREATE TABLE IF NOT EXISTS gravity_episode(
  ge_pk INT AUTO_INCREMENT PRIMARY KEY, ge_cfg VARCHAR(16),
  ge_start_dt DATETIME, ge_end_dt DATETIME, ge_home TINYINT, ge_outcome VARCHAR(8),
  ge_dur_min FLOAT, ge_px_start DOUBLE, ge_px_end DOUBLE, ge_px_move_pct FLOAT,
  ge_g_start FLOAT, ge_g_min FLOAT, ge_g_max FLOAT,
  ge_s2_far_oob_min FLOAT, ge_s2_home_oob_min FLOAT, ge_s2_far_first_min FLOAT,
  ge_s2_far_max FLOAT, ge_s2_net_far FLOAT,
  UNIQUE KEY u_ep (ge_cfg, ge_start_dt))"""

MK_DDL = """CREATE TABLE IF NOT EXISTS gravity_mark(
  gm_pk INT AUTO_INCREMENT PRIMARY KEY, gm_cfg VARCHAR(16),
  gm_start_dt DATETIME, gm_mark_min INT, gm_dt DATETIME,
  gm_home TINYINT, gm_outcome VARCHAR(8), gm_resolved TINYINT,
  gm_g FLOAT, gm_g_slope FLOAT, gm_g_dist50 FLOAT,
  gm_s2 FLOAT, gm_s2_far_oob_min FLOAT, gm_s2_home_oob_min FLOAT, gm_s2_far_max FLOAT,
  gm_s2_net_far FLOAT, gm_px_move_pct FLOAT,
  UNIQUE KEY u_mk (gm_cfg, gm_start_dt, gm_mark_min))"""


def run(days, end_ms):
    with Jig(end_ms, hours=days * 24, warmup=90,
             overrides=BE.overrides([1, TF_GRAV, 15])) as j:
        C = j.causal
        ts, px = np.asarray(j.ts, np.int64), np.asarray(j.px, float)
        n = len(ts)
        win0 = end_ms - days * 24 * 3600_000
        g = C.line(f's{TF_GRAV}Mage')
        s2 = C.line('s2Mage')
        gs = np.where(g >= HI, 1, np.where(g <= LO, -1, 0))          # gravity's OOB side
        s2s = np.where(s2 >= HI, 1, np.where(s2 <= LO, -1, 0))
        dt = lambda k: dtm.datetime.fromtimestamp(ts[k] / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

        # ---- episodes: leave an OOB zone, wander, touch a boundary again -------------------------
        eps = []
        home, start = 0, None
        for k in range(1, n):
            if gs[k] != 0:
                if start is not None and gs[k] != 0:
                    eps.append((start, k, home, 'FLIP' if gs[k] == -home else 'MEANDER'))
                    start = None
                home = gs[k]
            elif home != 0 and start is None:
                start = k                                            # just left the OOB zone
        eps = [e for e in eps if ts[e[0]] >= win0]

        ep_rows, mk_rows = [], []
        for (a, b, hm, out) in eps:
            far = -hm                                                # the side a FLIP would go to
            seg = slice(a, b + 1)
            s2seg, gseg = s2[seg], g[seg]
            s2sseg = s2s[seg]
            bars_far = int((s2sseg == far).sum())
            bars_home = int((s2sseg == hm).sum())
            first_far = np.flatnonzero(s2sseg == far)
            f_far = float(first_far[0] * 5 / 60) if len(first_far) else None      # min into the episode
            s2_far_max = float(s2seg.min() if far == -1 else s2seg.max())         # deepest push toward far
            s2_net_far = float(far * (s2[b] - s2[a]))                             # net travel toward far
            dur = (ts[b] - ts[a]) / 60000.0
            ep_rows.append((CFG_TAG, dt(a), dt(b), int(hm), out, round(dur, 2),
                            float(px[a]), float(px[b]), round((px[b] - px[a]) / px[a] * 100, 4),
                            float(g[a]), float(gseg.min()), float(gseg.max()),
                            round(bars_far * 5 / 60, 2), round(bars_home * 5 / 60, 2),
                            None if f_far is None else round(f_far, 2),
                            round(s2_far_max, 2), round(s2_net_far, 2)))

            # ---- causal snapshots at fixed elapsed marks (features known AT that mark) ------------
            for m in MARKS_MIN:
                k = a + int(m * 12)                                  # 12 five-second bars per minute
                if k > b or k >= n:
                    break                                            # the episode already resolved
                sl = slice(a, k + 1)
                s2c, gc = s2[sl], g[sl]
                s2sc = s2s[sl]
                slope = float(gc[-1] - gc[-13]) if k - a >= 12 else 0.0      # 1-min slope of the gravity
                fmax = float(s2c.min() if far == -1 else s2c.max())
                mk_rows.append((CFG_TAG, dt(a), int(m), dt(k), int(hm), out, 1,
                                float(g[k]), round(slope, 3), round(abs(g[k] - 50.0), 2),
                                float(s2[k]), round(int((s2sc == far).sum()) * 5 / 60, 2),
                                round(int((s2sc == hm).sum()) * 5 / 60, 2), round(fmax, 2),
                                round(float(far * (s2[k] - s2[a])), 2),
                                round((px[k] - px[a]) / px[a] * 100, 4)))
        return ep_rows, mk_rows


if __name__ == '__main__':
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    end = (dtm.datetime.strptime(sys.argv[2], '%Y-%m-%d_%H:%M').replace(tzinfo=timezone.utc)
           if len(sys.argv) > 2 else dtm.datetime.now(timezone.utc))
    ep, mk = run(days, int(end.timestamp() * 1000))

    d = DatabaseManager(**get_db_config()); d.connect()
    d.execute(EP_DDL); d.execute(MK_DDL)
    d.execute("DELETE FROM gravity_episode WHERE ge_cfg=%s", (CFG_TAG,))
    d.execute("DELETE FROM gravity_mark WHERE gm_cfg=%s", (CFG_TAG,))
    if ep:
        d.executemany("INSERT INTO gravity_episode (ge_cfg,ge_start_dt,ge_end_dt,ge_home,ge_outcome,"
                      "ge_dur_min,ge_px_start,ge_px_end,ge_px_move_pct,ge_g_start,ge_g_min,ge_g_max,"
                      "ge_s2_far_oob_min,ge_s2_home_oob_min,ge_s2_far_first_min,ge_s2_far_max,ge_s2_net_far)"
                      " VALUES (" + ",".join(["%s"] * 17) + ")", ep)
    if mk:
        d.executemany("INSERT INTO gravity_mark (gm_cfg,gm_start_dt,gm_mark_min,gm_dt,gm_home,gm_outcome,"
                      "gm_resolved,gm_g,gm_g_slope,gm_g_dist50,gm_s2,gm_s2_far_oob_min,gm_s2_home_oob_min,"
                      "gm_s2_far_max,gm_s2_net_far,gm_px_move_pct) VALUES ("
                      + ",".join(["%s"] * 16) + ")", mk)
    d.disconnect()

    o = [r[4] for r in ep]
    print(f'gravity_episode  {len(ep)} episodes over {days}d   ({o.count("FLIP")} FLIP · {o.count("MEANDER")} MEANDER)')
    print(f'gravity_mark     {len(mk)} causal snapshots')
