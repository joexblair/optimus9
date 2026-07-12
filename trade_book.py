"""trade_book.py — the FULL per-trade record for the arm->gate->trade->TP flow. (Joe 0711)

Supersedes `persist_trades.py` / `two_path_trades`, which persisted 11 columns and threw the rest away —
every troubleshooting question then needed a 40-minute re-run.  This writes EVERY field the harness already
computes: the hunt, the arm, the gate branch, the finisher, the entry, the excursions on BOTH legs, the exit
and its reason, the post-exit excursion, and the line context at the entry bar.

DEDUP AT THE PRODUCER (the bug this fixes): several arms can converge on the SAME finisher bar, and the old
producer wrote one row each — one real fill counted up to 3x (11 dupes / 163 rows = 7%).  A trade is keyed on
(trade bar, side).  Converging arms are MERGED: earliest arm/hunt kept, paths and gate branches unioned,
`tb_n_arms` records how many collapsed.

Causal, no caps.  Every read goes through the jig.
Diagnostic-only (NOT live-legal, score-side): tb_post_mae/tb_post_mfe scan 60 min PAST the exit to ask
"did we leave money on the table" — never fed back into a decision.

Config: T4 stack-climb arm on the 10..25 ladder, r=close|k_len8|rsi6, divergence L24 K2, exit rung 5 (es5).
  python3 trade_book.py 2026-05-17 2026-05-22 2026-05-27 2026-05-31 2026-06-10 2026-06-14    (day RANGES)
"""
import sys, datetime as dtm
from datetime import timezone
import numpy as np
from optimus9.analysis.jig import Jig
from optimus9.analysis.lr_v2 import s_qualify, fin_unlatch, gate_open
from optimus9.compute.pk5s_gate_computer import Pk5sGateComputer
import arm_walk as AW
from optimus9 import DatabaseManager
from optimus9.config import get_db_config

_pk_state = Pk5sGateComputer._pk_state_from_slopes
COST = 0.20
HI, LO = 85.0, 15.0
CFG_TAG = 'ship_0711'

DTFS = AW.DEFAULT_TFS
BANDS = AW.parse_bands(AW.DEFAULT_BANDS)
TFS_ARM = list(range(10, 26))
HUNT_TF = 10
L_DIV, K_DIV, FLOOR = 24, 2, 0.5
RSRC, RKLEN, RRSI = 'close', 8, 6
ITF_R = {2: 120, 3: 180, 4: 240}
VOL_LB = 360          # 30 min of 5s bars — realized-range context at the entry
POST_FWD = 720        # 60 min of 5s bars — post-exit excursion (diagnostic only)


def ovr():
    o = AW.overrides(list(range(5, 26)), 7, 0.50)
    o['gcs5M'] = (5, ('bb', 37, 0.6, 'ohlc4'), 'emerging')
    o['s15M'] = (15, ('bb', 37, 0.6, 'ohlc4'), 'emerging')
    o['s2Mage'] = (60, ('bb', 37, 0.72, 'hlcc4'), 'emerging')
    o['es5r'] = (300, ('k', 5, 6, 5, 'close'), 'emerging')
    o['es5m'] = (300, AW.S5M_OVERRIDE, 'emerging')
    o['es5Mage'] = (300, ('bb', 37, 0.7, 'ohlc4'), 'emerging')
    for tf, itf in ITF_R.items():
        o[f's{tf}r'] = (itf, ('k', RRSI, 6, RKLEN, RSRC), 'emerging')
    return o


def day(dstr):
    d0 = dtm.datetime.strptime(dstr, '%Y-%m-%d').replace(tzinfo=timezone.utc)
    t0 = int(d0.timestamp() * 1000)
    t1 = int((d0 + dtm.timedelta(hours=23, minutes=59)).timestamp() * 1000)

    with Jig(t1 + 6 * 3600_000, hours=30, warmup=90, overrides=ovr()) as j:
        W, cfg, C = j.W, j.cfg, j.causal
        ts, px = np.asarray(j.ts, np.int64), np.asarray(j.px, float)
        n = len(ts)
        dt = lambda k: dtm.datetime.fromtimestamp(ts[int(k)] / 1000, timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        secs = lambda a, b: int((ts[int(b)] - ts[int(a)]) / 1000)

        q15hi, q15lo = s_qualify(W, cfg, 's15m', 's15M', 's15r', cfg.s15r_lb)
        q30hi, q30lo = s_qualify(W, cfg, 's30m', 's30M', 's30r', cfg.s30r_lb)

        R = {i: C.line(f's{i}r') for i in (2, 3, 4, 5)}
        anyoob = np.zeros(n, bool)
        for i in (2, 3, 4, 5):
            anyoob |= (R[i] >= HI) | (R[i] <= LO)
        vl = np.zeros(n); vs = np.zeros(n)
        ps = np.zeros(n); ps[L_DIV:] = px[L_DIV:] - px[:-L_DIV]
        for i in (2, 3, 4, 5):
            ls = np.zeros(n); ls[L_DIV:] = R[i][L_DIV:] - R[i][:-L_DIV]
            st = _pk_state(ls, ps, FLOOR)
            vl += (st == 1.0); vs += (st == -1.0)
        dg = np.zeros(n)
        dg[anyoob & (vl >= K_DIV)] = -1
        dg[anyoob & (vs >= K_DIV)] = 1

        # realized 30-min high-low range at each bar — entry-context (volatility) column
        vol = np.zeros(n)
        for k in range(VOL_LB, n):
            w = px[k - VOL_LB:k + 1]
            vol[k] = (w.max() - w.min()) / w[-1] * 100

        # ---- arms: one per (arm bar, es), earliest hunt kept -------------------------------------
        arms = {}
        for (kh, es) in AW.hunts(j, HUNT_TF, t0, t1):
            r = AW.walk_stack(AW.board(j, TFS_ARM, es, 0.0, BANDS), kh, n - 1)
            if r and (r[0], es) not in arms:
                arms[(r[0], es)] = (r[1], kh)          # apex_tf, hunt bar

        # ---- trades: keyed on (trade bar, side); converging arms MERGE ---------------------------
        book = {}
        for (kA, es), (apex, kh) in sorted(arms.items()):
            bd = -es
            cap = AW.arm_cancel(j, HUNT_TF, kA, es, stay=True, win=60)
            q15 = q15hi if bd == -1 else q15lo
            q30 = q30hi if bd == -1 else q30lo

            g = gate_open(W, cfg, [(kA, es, bd, cap, 'arm')])
            okb, gkb = (g[0][3], g[0][4]) if g else (None, None)
            tB = fin_unlatch(q15, q30, okb, cap, cfg.fin_lb, cfg.fin_fwd) if okb is not None else None

            oka = next((b for b in range(kA, cap) if dg[b] == es and dg[b - 1] != es), None)
            tA = fin_unlatch(q15, q30, oka, cap, cfg.fin_lb, cfg.fin_fwd) if oka is not None else None

            cand = {}
            if tB is not None and tB < cap: cand[tB] = ('s3s4', gkb, okb)
            if tA is not None and tA < cap:
                if tA in cand:
                    cand[tA] = ('s3s4+div', f'{gkb}+div', min(okb, oka))
                else:
                    cand[tA] = ('div', 'div', oka)

            for kT, (path, gk, gbar) in cand.items():
                key = (int(kT), bd)
                if key in book:
                    b = book[key]
                    b['paths'] = '+'.join(sorted(set(b['paths'].split('+')) | set(path.split('+'))))
                    b['gates'] = '+'.join(sorted(set(b['gates'].split('+')) | set(gk.split('+'))))
                    b['n_arms'] += 1
                    if kA < b['kA']:
                        b.update(kA=kA, kh=kh, apex=apex, cap=cap)
                    b['gbar'] = min(b['gbar'], gbar)
                else:
                    book[key] = dict(kA=kA, kh=kh, apex=apex, cap=cap, es=es, bd=bd,
                                     paths=path, gates=gk, gbar=gbar, n_arms=1)

        # ---- exit + excursions -------------------------------------------------------------------
        rows = []
        for (kT, bd), b in sorted(book.items()):
            es_tp = -b['es']
            B_tp = AW.board(j, DTFS, es_tp, 0.0, BANDS, names={5: 'es5'})
            bd_tp = -es_tp
            q15t = q15hi if bd_tp == -1 else q15lo
            q30t = q30hi if bd_tp == -1 else q30lo

            trace = []
            kx = AW.take_profit_ad(B_tp, kT, n - 1, q15t, q30t, trace=trace)
            if kx is None:
                kx, xkind = b['cap'], 'cap'
            else:
                xkind = trace[-1][0] if trace else 'arm'

            e = px[kT]
            leg = bd * (px[kT:kx + 1] - e) / e * 100
            mae = -float(np.nanmin(np.minimum(leg, 0.0)))
            mfe = float(np.nanmax(np.maximum(leg, 0.0)))
            k_mae = int(kT + np.nanargmin(leg))
            k_mfe = int(kT + np.nanargmax(leg))

            # the arm leg: arm -> entry, in the eventual trade direction
            aleg = bd * (px[b['kA']:kT + 1] - px[b['kA']]) / px[b['kA']] * 100
            a_mae = -float(np.nanmin(np.minimum(aleg, 0.0))) if len(aleg) else 0.0
            a_mfe = float(np.nanmax(np.maximum(aleg, 0.0))) if len(aleg) else 0.0

            # post-exit 60 min, in the trade direction (DIAGNOSTIC: did the exit leave money behind?)
            ke = min(n - 1, kx + POST_FWD)
            pleg = bd * (px[kx:ke + 1] - px[kx]) / px[kx] * 100
            p_mae = -float(np.nanmin(np.minimum(pleg, 0.0))) if len(pleg) else 0.0
            p_mfe = float(np.nanmax(np.maximum(pleg, 0.0))) if len(pleg) else 0.0

            gross = bd * (px[kx] - e) / e * 100
            rows.append((
                CFG_TAG, dstr, dt(b['kh']), HUNT_TF, dt(b['kA']), int(b['apex']), dt(b['cap']), b['n_arms'],
                dt(b['gbar']), b['gates'], dt(kT), 'L' if bd == 1 else 'S', b['paths'], float(e),
                secs(b['kh'], b['kA']), secs(b['kA'], kT), secs(b['gbar'], kT), secs(kT, kx),
                round(a_mae, 3), round(a_mfe, 3),
                round(mae, 3), round(mfe, 3), secs(kT, k_mae), secs(kT, k_mfe), int(k_mfe < k_mae),
                dt(kx), float(px[kx]), xkind,
                round(p_mae, 3), round(p_mfe, 3),
                round(gross, 3), round(gross - COST, 3),
                round(float(R[2][kT]), 1), round(float(R[3][kT]), 1),
                round(float(R[4][kT]), 1), round(float(R[5][kT]), 1),
                int(vl[kT]), int(vs[kT]), round(float(vol[kT]), 3),
            ))
    return rows


DDL = """CREATE TABLE IF NOT EXISTS trade_book(
  tb_pk INT AUTO_INCREMENT PRIMARY KEY,
  tb_cfg VARCHAR(24), tb_day DATE,
  tb_hunt_dt DATETIME, tb_hunt_tf INT,
  tb_arm_dt DATETIME, tb_apex_tf INT, tb_cancel_dt DATETIME, tb_n_arms INT,
  tb_gate_dt DATETIME, tb_gate_kind VARCHAR(12),
  tb_trade_dt DATETIME, tb_side CHAR(1), tb_paths VARCHAR(12), tb_entry_px DOUBLE,
  tb_hunt_arm_s INT, tb_arm_trade_s INT, tb_gate_trade_s INT, tb_held_s INT,
  tb_arm_mae FLOAT, tb_arm_mfe FLOAT,
  tb_mae FLOAT, tb_mfe FLOAT, tb_mae_s INT, tb_mfe_s INT, tb_mfe_first TINYINT,
  tb_exit_dt DATETIME, tb_exit_px DOUBLE, tb_exit_kind VARCHAR(10),
  tb_post_mae FLOAT, tb_post_mfe FLOAT,
  tb_gross FLOAT, tb_net FLOAT,
  tb_r2 FLOAT, tb_r3 FLOAT, tb_r4 FLOAT, tb_r5 FLOAT,
  tb_votes_l INT, tb_votes_s INT, tb_vol30 FLOAT,
  KEY k_day (tb_cfg, tb_day), KEY k_trade (tb_trade_dt))"""

COLS = ("tb_cfg,tb_day,tb_hunt_dt,tb_hunt_tf,tb_arm_dt,tb_apex_tf,tb_cancel_dt,tb_n_arms,"
        "tb_gate_dt,tb_gate_kind,tb_trade_dt,tb_side,tb_paths,tb_entry_px,"
        "tb_hunt_arm_s,tb_arm_trade_s,tb_gate_trade_s,tb_held_s,tb_arm_mae,tb_arm_mfe,"
        "tb_mae,tb_mfe,tb_mae_s,tb_mfe_s,tb_mfe_first,tb_exit_dt,tb_exit_px,tb_exit_kind,"
        "tb_post_mae,tb_post_mfe,tb_gross,tb_net,tb_r2,tb_r3,tb_r4,tb_r5,"
        "tb_votes_l,tb_votes_s,tb_vol30")

if __name__ == '__main__':
    rng = sys.argv[1:]
    days = []
    for i in range(0, len(rng), 2):
        a = dtm.date.fromisoformat(rng[i]); b = dtm.date.fromisoformat(rng[i + 1])
        days += [(a + dtm.timedelta(days=k)).isoformat() for k in range((b - a).days + 1)]

    d = DatabaseManager(**get_db_config()); d.connect()
    d.execute(DDL)
    ph = ','.join(['%s'] * len(COLS.split(',')))
    tot = 0
    for dd in days:
        try:
            r = day(dd)
            d.execute("DELETE FROM trade_book WHERE tb_cfg=%s AND tb_day=%s", (CFG_TAG, dd))
            if r:
                d.executemany(f"INSERT INTO trade_book ({COLS}) VALUES ({ph})", r)
            tot += len(r)
            print(f"{dd}: {len(r):>2} trades  net {sum(x[31] for x in r):+7.2f}  "
                  f"(merged arms: {sum(x[7] - 1 for x in r)})", flush=True)
        except Exception as e:
            print(f"{dd}: ERR {type(e).__name__}: {e}", flush=True)
    n = d.execute("SELECT COUNT(*) c FROM trade_book WHERE tb_cfg=%s", (CFG_TAG,), fetch=True)[0]['c']
    d.disconnect()
    print(f"\ntrade_book holds {n} rows for cfg={CFG_TAG} ({tot} written this run)")
