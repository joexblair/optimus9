"""mo_push.py — what does it take for the BB to push a determined K line off its target? (Joe 0714)

Joe's model:
  - BB lines LEAD K lines around the board; K is always chasing the faster BB.
  - A K line WANTS to reach its target OOB and will not easily bend to opposing BB movement.
  - Enough opposing BB bars — straight or sawtooth — and it bends back. Enough BB bars the other way and
    it curls back on target.
  - Rudimentary form: sum the signed per-direction bar counts.  mo30 example {on_target:2, off_target:5}.
    Joe: the summing is rudimentary — the true model will be more nuanced (board position, sideways BB,
    BB out-of-bounds, K acting as gravity).

THE EVENT (Joe): "K leaving and returning to the same side without touching the other side."
  EPISODE   K leaves an OOB zone. The side it LEFT is home; the OTHER side is its TARGET.
  resolves  at the next OOB touch:  TARGET reached -> BREACH   ·   HOME again -> FAILED

RESET ON K CURL (Joe 0714). The bar-by-bar counters reset every time K curls — because the curl IS the
pressure being spent. K bends because pressure accumulated; the curl is that bend, so the bars that
produced it are consumed. Counting on from the episode start double-counts force already discharged and
sums pressure across multiple bends as if it were one push. After a curl K is on a new trajectory, and
the only pressure that can still act on it is what has arrived SINCE it last turned. The curl is the
boundary-agnostic coarse curl (jig.curl on the mo bar grid) — the same producer every s-line curl uses.

HYPOTHESIS, NOT SETTLED (Joe 0714): "there might be momentum data that silently bleeds into the current
calculations." So the previous segment's terminal values ride alongside as FEATURES (prev_*), and the
un-reset running total (cum_net) is kept as a CONTROL — the reset itself is testable, not assumed.

Every FEATURE is causal (BB bars up to and including the current one). The LABEL is hindsight.
Base rate FIRST — a hit-rate means nothing without one (the 0714 cs-ladder lesson).

TWO K VARIANTS, one shared BB to start (Joe 0714). If no consistent model emerges, sweep the BB length —
the two models do NOT have to share a BB line.

  BB   mo{tf}m : bb 7|0.64|close
  K    mo{tf}b : k  5|74|29|hlc3      <- Joe's slow b-line
       mo{tf}r : k  7|5|7|ohlc4       <- the CURRENT s-series r (what the cascade actually breaches on)
  TFs  15 · 25 · 30 · 45               bars: the mo TF's OWN bars

  python3 mo_push.py [analysis_days] [warmup_hours]      (default 32d, 600h)
"""
import sys, datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.analysis.jig import Jig, kline, bbline
from optimus9 import DatabaseManager
from optimus9.config import get_db_config

TFS = [15, 25, 30, 45]
HI, LO = 85.0, 15.0
BB = dict(length=7, mult=0.64, src='close')
SIDEWAYS = 2.0        # |bb delta| below this = a sideways bar (Joe flagged these as distorting the count)
KVARS = {'b': dict(k_len=5, rsi=74, stc=29, src='hlc3'),      # Joe's slow b-line
         'r': dict(k_len=7, rsi=5, stc=7, src='ohlc4')}       # the current s-series r
DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 32
WARM = int(sys.argv[2]) if len(sys.argv) > 2 else 600

DDL = """CREATE TABLE mo_push(
  mp_pk INT AUTO_INCREMENT PRIMARY KEY, mp_tf INT, mp_kvar CHAR(1),
  mp_start_dt DATETIME, mp_end_dt DATETIME, mp_home TINYINT, mp_outcome VARCHAR(8),
  mp_bars INT, mp_k_start FLOAT, mp_k_end FLOAT, mp_k_extreme FLOAT,
  mp_bar INT, mp_dt DATETIME, mp_k FLOAT, mp_bb FLOAT,
  mp_bb_dir TINYINT, mp_net INT, mp_run INT, mp_off_max INT, mp_on_max INT,
  mp_curl TINYINT, mp_since_curl INT, mp_curls INT,
  mp_prev_net INT, mp_prev_off INT, mp_prev_on INT, mp_prev_bars INT, mp_cum_net INT,
  mp_mag FLOAT, mp_mag_off FLOAT, mp_mag_on FLOAT,
  mp_k_pos FLOAT, mp_bb_pos FLOAT, mp_gap FLOAT, mp_bb_oob TINYINT, mp_bb_oob_bars INT,
  mp_sideways INT, mp_k_vel FLOAT, mp_dist FLOAT, mp_mid TINYINT, mp_curl_dir TINYINT,
  UNIQUE KEY u_row (mp_tf, mp_kvar, mp_start_dt, mp_bar), KEY k_ep (mp_tf, mp_kvar, mp_outcome))"""

COLS = ("mp_tf,mp_kvar,mp_start_dt,mp_end_dt,mp_home,mp_outcome,mp_bars,mp_k_start,mp_k_end,mp_k_extreme,"
        "mp_bar,mp_dt,mp_k,mp_bb,mp_bb_dir,mp_net,mp_run,mp_off_max,mp_on_max,"
        "mp_curl,mp_since_curl,mp_curls,mp_prev_net,mp_prev_off,mp_prev_on,mp_prev_bars,mp_cum_net,"
        "mp_mag,mp_mag_off,mp_mag_on,mp_k_pos,mp_bb_pos,mp_gap,mp_bb_oob,mp_bb_oob_bars,"
        "mp_sideways,mp_k_vel,mp_dist,mp_mid,mp_curl_dir")


def overrides():
    o = {}
    for tf in TFS:
        o.update(bbline(f'mo{tf}m', tf, **BB))
        for v, cfg in KVARS.items():
            o.update(kline(f'mo{tf}{v}', tf, **cfg))
    return o


end_ms = int(dtm.datetime.now(timezone.utc).timestamp() * 1000)
print(f'mo sets {TFS} x {list(KVARS)}   ·   {DAYS}d analysis   ·   {WARM}h warmup', flush=True)

rows = []
with Jig(end_ms, hours=DAYS * 24, warmup=WARM, overrides=overrides()) as j:
    C = j.causal
    ts = np.asarray(j.ts, np.int64)
    win0 = end_ms - DAYS * 24 * 3600_000
    dt = lambda t: dtm.datetime.fromtimestamp(int(t) / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    for tf in TFS:
        m = (ts % (tf * 60 * 1000)) == 0                      # the mo TF's own bar grid
        bts = ts[m]
        bb = C.line(f'mo{tf}m')[m]                            # BB on the mo bars — SHARED by both K vars
        bdir = np.sign(np.diff(bb, prepend=bb[0]))            # sign(bb[t] - bb[t-1])   (Joe, confirmed)
        n = len(bts)

        for kvar in KVARS:
            k = C.line(f'mo{tf}{kvar}')[m]
            side = np.where(k >= HI, 1, np.where(k <= LO, -1, 0))
            # K's own curls on the mo bar grid — boundary-agnostic, both directions. The counters reset here.
            kc = {}                                    # bar -> curl direction (+1 K turns up, -1 turns down)
            for dirn in (+1, -1):
                for t in C.curl(bts, k, dirn):
                    kc[int(np.searchsorted(bts, t))] = dirn

            eps, home, start = [], 0, None
            for i in range(1, n):
                if side[i] != 0:
                    if start is not None:
                        eps.append((start, i, home, 'BREACH' if side[i] == -home else 'FAILED'))
                        start = None
                    home = side[i]
                elif home != 0 and start is None:
                    start = i
            eps = [e for e in eps if bts[e[1]] >= win0]

            for (a, b, hm, out) in eps:
                tgt = -hm                                     # the OOB K is heading FOR
                net = run = off_max = on_max = 0
                prev = 0
                since = curls = cum = 0
                p_net = p_off = p_on = p_bars = 0             # the segment that ended at the LAST curl
                mag = mag_off = mag_on = 0.0                  # MAGNITUDE, not just the sign of the bar
                sideways = bb_oob_bars = 0
                ext = float(k[a:b + 1].min() if tgt == -1 else k[a:b + 1].max())
                for i in range(a, b + 1):
                    curled = int(i in kc)
                    # curl direction RELATIVE TO THE TARGET: +1 = curled TOWARD target (cost #1, cheap)
                    #                                        -1 = curled AWAY  from it  (cost #2, dear)
                    cdir = int(kc[i] * tgt) if curled else 0
                    if curled:                                # RESET — the curl IS the pressure being spent
                        p_net, p_off, p_on, p_bars = net, off_max, on_max, since
                        net = run = off_max = on_max = 0
                        prev = 0
                        since = 0
                        curls += 1
                    if curled:
                        mag = mag_off = mag_on = 0.0
                        sideways = bb_oob_bars = 0
                    d = int(bdir[i])
                    on = d * tgt                              # +1 BB toward the target, -1 away
                    net += on
                    cum += on                                 # CONTROL: never reset
                    run = run + on if (on and np.sign(on) == np.sign(prev or on)) else on
                    prev = on if on else prev
                    off_max = min(off_max, net)
                    on_max = max(on_max, net)

                    # ---- the tangents (Joe 0714) --------------------------------------------------
                    dv = float(bb[i] - bb[i - 1]) if i else 0.0
                    sm = dv * tgt                             # signed MAGNITUDE toward the target
                    mag += sm
                    mag_off = min(mag_off, mag)
                    mag_on = max(mag_on, mag)
                    if abs(dv) < SIDEWAYS:                    # "BB lines that print sideways or near-sideways"
                        sideways += 1
                    bb_oob = int(bb[i] >= HI or bb[i] <= LO)  # "the mechanics change when BB is OOB"
                    bb_oob_bars += bb_oob
                    kpos, bpos = float(k[i]), float(bb[i])
                    gap = (bpos - kpos) * tgt                 # BB ahead of K toward the target = the PULL
                    kvel = float(k[i] - k[i - 1]) * tgt if i else 0.0
                    dist = float(HI - kpos if tgt == 1 else kpos - LO)   # how far K still has to go
                    mid = int(35 <= kpos <= 65 or 35 <= bpos <= 65)      # "most pull when either is mid-board"

                    rows.append((tf, kvar, dt(bts[a]), dt(bts[b]), int(hm), out, int(b - a),
                                 float(k[a]), float(k[b]), ext,
                                 int(i - a), dt(bts[i]), float(k[i]), float(bb[i]),
                                 d, int(net), int(run), int(off_max), int(on_max),
                                 curled, int(since), int(curls),
                                 int(p_net), int(p_off), int(p_on), int(p_bars), int(cum),
                                 round(mag, 3), round(mag_off, 3), round(mag_on, 3),
                                 round(kpos, 2), round(bpos, 2), round(gap, 2), bb_oob, int(bb_oob_bars),
                                 int(sideways), round(kvel, 3), round(dist, 2), mid, cdir))
                    since += 1
        print(f'  mo{tf} done', flush=True)

d = DatabaseManager(**get_db_config()); d.connect()
d.execute("DROP TABLE IF EXISTS mo_push")   # scratch analysis table; schema changes each iteration
d.execute(DDL)
d.executemany(f"INSERT INTO mo_push ({COLS}) VALUES (" + ",".join(["%s"] * 40) + ")", rows)
d.disconnect()

ep = {}
for r in rows:
    ep[(r[0], r[1], r[2])] = (r[5], r[6])
print(f'\nmo_push: {len(rows)} bar-rows across {len(ep)} episodes')
print(f'  {"set":<16} {"episodes":>8} {"BREACH":>7} {"FAILED":>7} {"base P(FAILED)":>15} {"med bars":>9}')
print('  ' + '-' * 68)
for kv, lab in (('b', '5|74|29'), ('r', '7|5|7')):
    for tf in TFS:
        e = [v for (t, k, _), v in ep.items() if t == tf and k == kv]
        if not e:
            continue
        o = [x[0] for x in e]
        bars = [x[1] for x in e]
        print(f'  mo{tf}{kv} {lab:<9} {len(e):>8} {o.count("BREACH"):>7} {o.count("FAILED"):>7} '
              f'{o.count("FAILED") / len(o):>15.3f} {np.median(bars):>9.0f}')
