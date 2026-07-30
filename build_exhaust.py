"""build_exhaust — the current_tf EXHAUSTION MARKER dataset (Joe 0728/0729).

    "use the current_tf exhaustion cross (race: cross first 1/4 seam r, or cross boundary) as the marker.
     create that dataset first and drop it into a db table for me, before you start your new walk...
     I'm happy to take the rich version, ie the dataset you'll use for the walk"

THE MARKER — a three-way race on current_tf, in the exhaustion direction
    leg r   x crosses r         r OOB but NOT established: dwell < 1/4 seam (the cross lands INSIDE the
                                first 1/4 seam). Joe 0729, branch 1: "if x crosses r in the first 1/4 seam".
    leg M   x crosses Mage      same gate. Joe 0728: "the same waiting-for-r logic would apply if x crossed
                                Mage" — adopted 0729 so it can be analysed here.
    leg b   x crosses boundary  UNCONDITIONAL. Joe 0729 branch 2, "the missing code" — _climb_to_prov only
                                ever exhausts on the r cross, never the boundary.

1/4 SEAM = TF minutes / 4 = TF*15 seconds = TF*3 emerging 5s bars. Joe: "first 1/4 seam of the TF (ie 15
minutes for TF60)" -> TF60 = 180 bars = 900s.

WHY A NON-ESTABLISHED r IS THE EXHAUSTION (Joe 0729, and the direction I had BACKWARDS at first):
  r goes OOB, then HOLDS past the 1/4 seam  -> established     -> CONTINUATION, climb higher
  r goes OOB, x crosses back INSIDE it      -> never establishes -> EXHAUSTION, route to the delegate
r is a lagging line; it integrates prior bars before reaching OOB. A cross inside the window means x turned
BEFORE r finished registering the move that pushed it OOB - r arrives reporting a condition x has already
left, so the extreme is behind the bar, not ahead of it. "Established" qualifies CONTINUATION, not a valid
exhaustion. Gating legs r/M on dwell >= 1/4 seam (my first build) made leg r almost never fire and put every
rpl_micro exhaustion out of reach.

DWELL CLOCK starts when r goes OOB, NOT when the TF becomes current_tf — the spec describes r establishing
ITSELF ("r established OOB, ie oob longer than the first 1/4 TF seam"), a property of r, not of the climb.
Continuous: any bar where r returns IB resets it.

TWO BARS PER MARKER. cross_wob confirms only after the crossed side holds wob_n bars and the consumer takes
the rising edge, so the confirmed bar is always wob_n-1 (=8 bars, 40s) after the real crossing. Joe caught
this when a quoted "cross of 15" showed x=43.4. Line values must be read at the RAW bar; a live system can
only act at the CONFIRMED bar. Both stored.

EVERY CANDIDATE IS STORED, not just the race winner, so the race can be re-scored — including with leg M
removed — without re-walking.

TF FLOOR = 22. Joe 0729: "TF2 is not part of RPL... RPL starts at TF22, anything below that is handled by
s4Mage and s15/s22" — and (0728) "s15s22 is the bridge between s4 and RPL". So current_tf, whose exhaustion
this marks, is never below 22. The DELEGATE may still sit lower (catch_many_tf=16, delegate_tf_floor=1);
that is the delegate's business, not the marker's.

    python3 build_exhaust.py [--ceiling 120] [--floor 22] [--persist]
"""
import sys, datetime as dt
import numpy as np
import build_rpl_6of9 as B                      # brings the pinned MINI config + the June engine
import optimus9.orchestration.rpl_walk as R
import optimus9.orchestration.rpl_evo_sweep as SW
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

DDL = '''CREATE TABLE IF NOT EXISTS rpl_exhaust (
    xh_pk         BIGINT AUTO_INCREMENT PRIMARY KEY,
    xh_created    DATETIME DEFAULT CURRENT_TIMESTAMP,
    xh_tf         INT,                  -- the TF this marker is on (as current_tf)
    xh_bias       VARCHAR(4),           -- climb polarity: bull -> hi boundary, bear -> lo
    xh_leg        VARCHAR(1),           -- r | M | b   (which leg of the race produced it)
    -- the REAL crossing bar. read line values HERE.
    xh_raw_ms     BIGINT, xh_raw_utc VARCHAR(19),
    xh_x          FLOAT, xh_r FLOAT, xh_mage FLOAT, xh_thr FLOAT,   -- thr = the line actually crossed
    -- the CONFIRMED bar: wob_n-1 bars later; the earliest a live system could act
    xh_conf_ms    BIGINT, xh_conf_utc VARCHAR(19),
    xh_conf_x     FLOAT, xh_conf_r FLOAT, xh_lag_s INT,
    -- the 1/4-seam gate
    xh_seam_q_s   INT,                  -- TF*15: the 1/4 seam for this TF, seconds
    xh_r_oob      TINYINT,              -- was r OOB at the raw bar
    xh_dwell_s    INT,                  -- r's CONTINUOUS OOB dwell at the raw bar, seconds
    xh_established TINYINT,             -- dwell >= seam_q -> CONTINUATION. legs r/M require the OPPOSITE
                                        -- (dwell < seam_q, the cross inside the first 1/4 seam); leg b ignores it
    -- ORIGIN-SIDE dwell, stored NOT applied. The engine's x-cross-pred debounces the origin via
    -- xcp_origin_dwell (XCPD, currently 4) precisely to kill one-bar spikes into the crossed side; Joe's
    -- marker spec does not mention it either way, so it is recorded as a column and left to the consumer.
    -- xh_jump quantifies it: how far past the line the first bar of the run lands.
    xh_origin_bars INT,                 -- bars x held the PRE-cross side immediately before the raw bar
    xh_jump       FLOAT,                -- x - thr at the raw bar: how far past the line the first bar lands
    -- the r-OOB episode this marker sits in (NULL when r was not OOB — only leg b can do that)
    xh_ep_start_ms BIGINT,              -- start of x's OOB episode on this TF: THE race key, all 3 legs
    xh_r_ep_ms    BIGINT,               -- start of r's OOB episode (context for legs r/M; not the race key)
    xh_ep_seq     INT,
    xh_race_first TINYINT,              -- first marker of any leg within the episode
    INDEX (xh_tf, xh_bias, xh_leg), INDEX (xh_raw_ms), INDEX (xh_established), INDEX (xh_race_first))'''


def rebuild_cache(ceiling):
    """Research-only cache at a higher TF ceiling (Joe 0729: "research only cache"). rpl_config.tf_ceiling is
    NOT touched — R.TFS is reassigned at runtime and the pinned MINI line config rebuilt over the wider range."""
    if ceiling == max(R.TFS):
        print('cache already at ceiling %d' % ceiling)
        return
    print('rebuilding research cache: TF ceiling %d -> %d ...' % (max(R.TFS), ceiling))
    R.TFS = list(range(1, ceiling + 1))
    SW._apply_knobs(B.MINI)
    R.L0 = SW._build_line_L0(B.MINI)
    print('  E keys %d..%d, %d bars' % (min(R.L0['E']), max(R.L0['E']), R.L0['n']))


RPL_FLOOR = 22          # Joe 0729: RPL starts at TF22; below that is s4Mage + s15/s22
# Joe 0729: "our data is synthetic before 05-18 ... the 5s bars before 05-18 are ok for warmup, but not ok
# for analysis". So the FULL tape still feeds the lines (warmup), but no marker is emitted before this.
ANALYSIS_START = int(dt.datetime(2026, 5, 18, tzinfo=dt.timezone.utc).timestamp() * 1000)


def markers(ceiling=120, floor=RPL_FLOOR):
    L = R.L0; S = L['src']; ts = L['ts']; E = L['E']
    utc = lambda ms: dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    LAG = R.WOBN - 1
    rows = []
    for bias in ('bull', 'bear'):
        p = R._polar(bias)
        for TF in range(floor, ceiling + 1):
            x, r, M = E[TF]['x'], E[TF]['r'], E[TF]['M']
            qbars = TF * 3                                   # 1/4 seam in emerging 5s bars (TF*15s / 5s)
            oob = p['oob_climb'](r)
            idx = np.arange(len(r))
            rst = np.where(oob, 0, idx + 1)
            dwell = (idx + 1) - np.maximum.accumulate(rst)   # consecutive OOB bars ending at i
            dwell = np.where(oob, dwell, 0)
            est = oob & (dwell >= qbars)             # ESTABLISHED -> continuation (climb), NOT exhaustion
            inseam = oob & (dwell < qbars)           # inside the first 1/4 seam -> THE exhaustion gate
            ep_start = np.where(oob, idx - dwell + 1, -1)    # first bar of the current r-OOB episode
            # THE RACE EPISODE (Joe 0729): x's OWN OOB episode on current_tf, shared by all three legs.
            # Keying the race on r's OOB episode silently re-imposed "r must be OOB" on leg b, which is
            # unconditional by spec — so every boundary cross with r IB was recorded but could never WIN.
            # That, not the band search or the ladder, is why rpl_exh_applied dropped so many. Joe: "to get
            # to this stage in the RPL walk, r has been recently predicted - meaning it's likley to come
            # near to OOB, if not all the way OOB".
            xoob = p['oob_climb'](x)
            _xr = np.where(xoob, 0, idx + 1)
            xdw = (idx + 1) - np.maximum.accumulate(_xr)
            xstart = np.where(xoob, idx - xdw + 1, -1)
            xep = np.maximum.accumulate(np.where(xoob, xstart, -1))   # most recent x-OOB run start
            legs = (('r', r, True), ('M', M, True), ('b', np.full(len(r), p['CB'], float), False))
            for leg, line, gated in legs:
                delta = x - line
                conf = S.causal.cross_wob(delta, 0.0, p['WOB_DIR'], R.WOBN)
                # origin-side run length: bars delta held the PRE-cross side, ending at each bar. Stored, not
                # applied — see the DDL note. Same producer the engine uses for XCPD, opposite direction.
                orig = (delta < 0) if p['WOB_DIR'] > 0 else (delta > 0)
                _rs = np.where(orig, 0, idx + 1)
                orun = (idx + 1) - np.maximum.accumulate(_rs)
                for k in np.flatnonzero(conf & ~np.roll(conf, 1)):
                    k = int(k)
                    kr = max(0, k - LAG)                     # the REAL crossing bar
                    if ts[kr] < ANALYSIS_START:              # synthetic tape: warmup only, never analysis
                        continue
                    if gated and not inseam[kr]:      # r OOB but still INSIDE its first 1/4 seam
                        continue
                    rows.append(dict(
                        tf=TF, bias=bias, leg=leg,
                        raw=int(ts[kr]), x=float(x[kr]), r=float(r[kr]), mage=float(M[kr]),
                        thr=float(line[kr]),
                        conf=int(ts[k]), cx=float(x[k]), cr=float(r[k]), lag=(k - kr) * 5,
                        qs=TF * 15, oob=int(bool(oob[kr])), dw=int(dwell[kr]) * 5,
                        est=int(bool(est[kr])),
                        ob=int(orun[kr - 1]) if kr > 0 else 0,
                        jump=float(delta[kr]),
                        eps=int(ts[xep[kr]]) if xep[kr] >= 0 else None,
                        reps=int(ts[ep_start[kr]]) if ep_start[kr] >= 0 else None))
    # race: within each (TF, bias, X-OOB episode) order the markers and flag the first of any leg
    rows.sort(key=lambda w: (w['tf'], w['bias'], w['eps'] if w['eps'] is not None else -1, w['raw']))
    seq = {}
    for w in rows:
        key = (w['tf'], w['bias'], w['eps'])
        seq[key] = seq.get(key, 0) + 1
        w['seq'] = seq[key]
        w['first'] = int(seq[key] == 1 and w['eps'] is not None)
    return rows


def main(argv):
    ceiling = 120; floor = RPL_FLOOR
    for i, a in enumerate(argv):
        if a == '--ceiling' and i + 1 < len(argv):
            ceiling = int(argv[i + 1])
        if a == '--floor' and i + 1 < len(argv):
            floor = int(argv[i + 1])
    rebuild_cache(ceiling)
    rows = markers(ceiling, floor)
    print('\n%d markers  (TF %d..%d, both biases, from %s — synthetic tape excluded)'
          % (len(rows), floor, ceiling, utc_(ANALYSIS_START)[:10]))
    for leg, nm in (('r', 'x x r  (1/4-seam gated)'), ('M', 'x x Mage (1/4-seam gated)'), ('b', 'x x boundary (ungated)')):
        s = [w for w in rows if w['leg'] == leg]
        w1 = [w for w in s if w['first']]
        print('  leg %s  %-28s %8d markers   %6d race-winners' % (leg, nm, len(s), len(w1)))
    fw = [w for w in rows if w['first']]
    print('\n  race winners by leg: %s'
          % {l: sum(1 for w in fw if w['leg'] == l) for l in ('r', 'M', 'b')})
    d = [w['dw'] for w in rows if w['leg'] in 'rM']
    if d:
        print('  gated legs — r dwell at the cross (s): med %.0f  p10 %.0f  max %.0f'
              % (np.median(d), np.percentile(d, 10), max(d)))
    print('  cross_wob lag: %ds on every marker (wob_n=%d)' % ((R.WOBN - 1) * 5, R.WOBN))

    if '--persist' in argv:
        db = DatabaseManager(**get_db_config()); db.connect(); db.execute(DDL)
        db.execute('DELETE FROM rpl_exhaust')
        # NaN -> NULL. The warmup region leaves lines NaN, and the driver interpolates float('nan') as a
        # bare `nan` token, which MySQL parses as a column name (1054 Unknown column 'nan').
        def _n(v):
            return None if (isinstance(v, float) and not np.isfinite(v)) else v
        db.executemany('''INSERT INTO rpl_exhaust (xh_tf,xh_bias,xh_leg,xh_raw_ms,xh_raw_utc,xh_x,xh_r,
            xh_mage,xh_thr,xh_conf_ms,xh_conf_utc,xh_conf_x,xh_conf_r,xh_lag_s,xh_seam_q_s,xh_r_oob,
            xh_dwell_s,xh_established,xh_origin_bars,xh_jump,xh_ep_start_ms,xh_r_ep_ms,xh_ep_seq,xh_race_first)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
            [tuple(_n(v) for v in (w['tf'], w['bias'], w['leg'], w['raw'], utc_(w['raw']), w['x'], w['r'],
              w['mage'], w['thr'], w['conf'], utc_(w['conf']), w['cx'], w['cr'], w['lag'], w['qs'], w['oob'],
              w['dw'], w['est'], w['ob'], w['jump'], w['eps'], w['reps'], w['seq'], w['first'])) for w in rows])
        db.disconnect()
        print('\npersisted %d rows to rpl_exhaust' % len(rows))
    return rows


utc_ = lambda ms: dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

if __name__ == '__main__':
    main(sys.argv[1:])
