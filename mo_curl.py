"""mo_curl.py — the PRICE OF A CURL. (Joe 0714)

Supersedes the episode framing in mo_push.py, which was modelling the wrong unit.

  THE UNIT IS THE CURL, not the episode. The curl is what the BB pressure directly CAUSES; the episode
  outcome is a coin toss many bars downstream (every feature there capped at ~0.15 AUC power).

  THE MEASURABLE IS THE COST. Joe: "a K line always wants to reach its target OOB, so it will not easily
  bend to opposing BB movements." So the quantity is HOW MUCH PRESSURE IT TOOK TO BEND IT.
      cost #1  = pressure to curl K TOWARD its target OOB.   Cheap.
      cost #2  = pressure to curl K AWAY  from its target.   Expensive.
  THE ONE TEST EVERYTHING RESTS ON:  is cost#1 < cost#2, WITHIN EACH ZONE?  If not, the model is dead.

  THE REVERSAL SIGNAL. K is heading for its target and curls AWAY — but it only cost a #1-sized push.
  The target has flipped; the market shifted (Joe's 07-11 21:45).

  TARGET, defined everywhere (Joe):
      K travelling lo -> hi   : target = hi
      K sitting IN hi         : target = hi   (it ARRIVED; an away-push must brew to eject it)
      K leaves hi, heads lo   : target = lo
  The target flips ONLY when K leaves the OOB it occupied.

  NO HANDOVER, NO OOB VARIANT. The push that EJECTS K from its target OOB IS the push that carries it
  toward the other side — same force, same bars, only the frame changes. So at the target flip the carried
  counter is SIGN-INVERTED, not reset and not handed off. mo_push.py started each episode at zero, which
  THREW THE EJECT-PUSH AWAY; by this model it is not prologue, it is the opening balance of the traversal.

  FALSIFIABLE: a large eject-push should predict a fast, successful traversal. If big eject-pushes are
  followed by FAILED traversals, the carry idea is wrong.

  ZONES (Joe: "different amounts of pressure at different places of the board") — banded by K's distance
  to its TARGET boundary, so the axis is his, not one I invented. Negative distance = inside the target OOB.

  BB mo{tf}m: bb 7|0.64|close   ·   K mo{tf}b: k 5|74|29|hlc3   ·   K mo{tf}r: k 7|5|7|ohlc4
  python3 mo_curl.py [days] [warmup_hours]        (default 32d, 600h)
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
KVARS = {'b': dict(k_len=5, rsi=74, stc=29, src='hlc3'),
         'r': dict(k_len=7, rsi=5, stc=7, src='ohlc4')}
DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 32
WARM = int(sys.argv[2]) if len(sys.argv) > 2 else 600

DDL = """CREATE TABLE mo_curl(
  mc_pk INT AUTO_INCREMENT PRIMARY KEY, mc_tf INT, mc_kvar CHAR(1), mc_dt DATETIME,
  mc_event VARCHAR(6),                       -- 'curl' | 'exit'
  mc_target TINYINT, mc_curl_dir TINYINT,    -- curl_dir: +1 TOWARD target (#1) · -1 AWAY (#2)
  mc_k FLOAT, mc_bb FLOAT, mc_dist FLOAT, mc_zone VARCHAR(10),
  mc_cost_bars INT, mc_cost_net INT, mc_cost_mag FLOAT,   -- the pressure that PRODUCED this curl
  mc_carried_net INT, mc_carried_mag FLOAT,               -- exits: the eject-push, sign-inverted
  mc_out VARCHAR(8), mc_out_bars INT,                     -- exits: did the traversal REACH the target?
  KEY k_q (mc_tf, mc_kvar, mc_event, mc_zone))"""

COLS = ("mc_tf,mc_kvar,mc_dt,mc_event,mc_target,mc_curl_dir,mc_k,mc_bb,mc_dist,mc_zone,"
        "mc_cost_bars,mc_cost_net,mc_cost_mag,mc_carried_net,mc_carried_mag,mc_out,mc_out_bars")


def zone_of(dist):
    if dist < 0:
        return 'IN_OOB'
    if dist < 15:
        return 'CLOSE'
    if dist < 35:
        return 'APPROACH'
    return 'MID'


def overrides():
    o = {}
    for tf in TFS:
        o.update(bbline(f'mo{tf}m', tf, **BB))
        for v, cfg in KVARS.items():
            o.update(kline(f'mo{tf}{v}', tf, **cfg))
    return o


end_ms = int(dtm.datetime.now(timezone.utc).timestamp() * 1000)
print(f'{DAYS}d · {WARM}h warmup · TFs {TFS} · K {list(KVARS)}', flush=True)

rows = []
with Jig(end_ms, hours=DAYS * 24, warmup=WARM, overrides=overrides()) as j:
    C = j.causal
    ts = np.asarray(j.ts, np.int64)
    win0 = end_ms - DAYS * 24 * 3600_000
    dt = lambda t: dtm.datetime.fromtimestamp(int(t) / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    for tf in TFS:
        m = (ts % (tf * 60 * 1000)) == 0
        bts = ts[m]
        bb = C.line(f'mo{tf}m')[m]
        n = len(bts)

        for kvar in KVARS:
            k = C.line(f'mo{tf}{kvar}')[m]
            side = np.where(k >= HI, 1, np.where(k <= LO, -1, 0))
            curls = {}
            for dirn in (+1, -1):
                for t in C.curl(bts, k, dirn):
                    curls[int(np.searchsorted(bts, t))] = dirn

            # seed the target from the first OOB touch
            first = next((i for i in range(n) if side[i] != 0), None)
            if first is None:
                continue
            occ, home = side[first], side[first]
            net = cost_bars = 0
            mag = 0.0
            pend = []                                          # exits awaiting their traversal outcome

            for i in range(first + 1, n):
                tgt = occ if occ != 0 else -home                # THE TARGET, everywhere
                prev_side = side[i - 1]

                # ---- the OOB EXIT: the target FLIPS, and the carried push is SIGN-INVERTED ----------
                if prev_side != 0 and side[i] == 0:
                    home, occ = prev_side, 0
                    net, mag = -net, -mag                       # same force, new frame (Joe: no handover)
                    tgt = -home
                    if bts[i] >= win0:
                        pend.append(dict(idx=i, tgt=tgt, cnet=net, cmag=mag))
                elif side[i] != 0:
                    if occ == 0:                                # ARRIVED at an OOB
                        for p in [x for x in pend if x['tgt'] == side[i]]:
                            p['out'], p['bars'] = 'REACH', i - p['idx']
                        for p in [x for x in pend if x['tgt'] != side[i]]:
                            p['out'], p['bars'] = 'FAILED', i - p['idx']
                        pend = [x for x in pend if 'out' not in x]
                    occ, home = side[i], side[i]

                dv = float(bb[i] - bb[i - 1])
                net += int(np.sign(dv)) * tgt
                mag += dv * tgt
                cost_bars += 1

                if i in curls and bts[i] >= win0:
                    cdir = int(curls[i] * tgt)                  # +1 TOWARD target (#1) · -1 AWAY (#2)
                    dist = float(HI - k[i]) if tgt == 1 else float(k[i] - LO)
                    # GROUND TRUTH for a reversal call: from this curl, which OOB does K reach FIRST?
                    #   the AWAY side  -> the target really did flip. REVERSAL.
                    #   the target     -> no reversal; K resumed its path.
                    nxt = next((side[q] for q in range(i + 1, n) if side[q] != 0), 0)
                    out = ('REVERSAL' if nxt == -tgt else 'RESUMED') if nxt else None
                    obars = next((q - i for q in range(i + 1, n) if side[q] != 0), None)
                    rows.append((tf, kvar, dt(bts[i]), 'curl', int(tgt), cdir,
                                 float(k[i]), float(bb[i]), round(dist, 2), zone_of(dist),
                                 cost_bars, int(net), round(mag, 3), None, None, out, obars))
                if i in curls:
                    net, cost_bars = 0, 0                       # the curl IS the pressure being spent
                    mag = 0.0

            for p in pend:                                      # unresolved at the tape end
                p['out'], p['bars'] = None, None
            for p in [x for x in pend]:
                pass

        print(f'  mo{tf} done', flush=True)

    # ---- the EXIT rows (the eject-push -> traversal outcome test) ---------------------------------
    for tf in TFS:
        m = (ts % (tf * 60 * 1000)) == 0
        bts = ts[m]
        bb = C.line(f'mo{tf}m')[m]
        n = len(bts)
        for kvar in KVARS:
            k = C.line(f'mo{tf}{kvar}')[m]
            side = np.where(k >= HI, 1, np.where(k <= LO, -1, 0))
            curls = set()
            for dirn in (+1, -1):
                curls |= {int(np.searchsorted(bts, t)) for t in C.curl(bts, k, dirn)}
            first = next((i for i in range(n) if side[i] != 0), None)
            if first is None:
                continue
            occ, home = side[first], side[first]
            net = 0
            mag = 0.0
            open_exits = []
            for i in range(first + 1, n):
                tgt = occ if occ != 0 else -home
                if side[i - 1] != 0 and side[i] == 0:
                    home, occ = side[i - 1], 0
                    net, mag = -net, -mag
                    tgt = -home
                    if bts[i] >= win0:
                        open_exits.append([i, tgt, net, mag, float(k[i]), float(bb[i])])
                elif side[i] != 0:
                    if occ == 0:
                        for e in open_exits:
                            out = 'REACH' if e[1] == side[i] else 'FAILED'
                            dist = float(HI - e[4]) if e[1] == 1 else float(e[4] - LO)
                            rows.append((tf, kvar, dt(bts[e[0]]), 'exit', int(e[1]), 0,
                                         e[4], e[5], round(dist, 2), zone_of(dist),
                                         None, None, None, int(e[2]), round(e[3], 3), out, i - e[0]))
                        open_exits = []
                    occ, home = side[i], side[i]
                dv = float(bb[i] - bb[i - 1])
                net += int(np.sign(dv)) * tgt
                mag += dv * tgt
                if i in curls:
                    net, mag = 0, 0.0

d = DatabaseManager(**get_db_config()); d.connect()
d.execute("DROP TABLE IF EXISTS mo_curl")
d.execute(DDL)
d.executemany(f"INSERT INTO mo_curl ({COLS}) VALUES (" + ",".join(["%s"] * 17) + ")", rows)
d.disconnect()

cu = [r for r in rows if r[3] == 'curl']
ex = [r for r in rows if r[3] == 'exit']
print(f'\nmo_curl: {len(cu)} curls · {len(ex)} OOB exits')
