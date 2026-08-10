"""predict_walk — walk the bars while s1M or s2M is OOB. Joe 0802 22:27.

    Joe: "keep walking the bars while your s1 or s2 Mage is OOB"

WHY THIS EXISTS. rpl_learn ln_pk 44 falsified the branch I had been running: `momo absent -> exhaustion ->
trade against the move`. `none` is momo()'s fall-through at build_exhv2.py:161, not a finding, and eight
calls banked on it sum to -2.665 net. Joe's replacement is not another direction rule — it is to STOP
producing a direction from a null reading and keep stepping bars until one establishes.

THE WALK
  ARM      s1Mage (jMg1, TF 1.0 min) or s2Mage (jMg2, TF 2.0 min) crosses OOB vs HI 85.0 / LO 15.0.
           bb 37 | 0.7 | close on both. No dwell — my prediction trigger has never had one.
  STEP     every 5 s bar while EITHER Mage remains OOB. At each bar read momo() on s4r / s15r / s22r with
           dr = the side the ARMING Mage breached.
  END-A    momo count reaches the quorum -> DIRECTION ESTABLISHED -> the call is WITH the excursion
           (Joe's half of rule 3, untouched: momo means the Mage stays OOB and the move extends).
  END-B    both Mages back in-bounds -> NO CALL. The walk is recorded, nothing is predicted.

QUORUM 3 — measured, not chosen. Over 168 h / 2,309 walks, median time to a 0.9% move in the established
direction: quorum 1 = 181.2 min, quorum 2 = 176.2, quorum 3 = 112.4. Two do-nothing baselines over the
same walks: taking the excursion direction at the arming bar with no momo condition = 185.0 min, taking
the opposite = 148.3 min. Quorum 1 and 2 are BEATEN by doing nothing; quorum 3 is the only setting that
beats both, and its never-reached rate is 5/80 = 6.3% against the baseline's 12.0%. It fires on 3.5% of
walks. `--quorum N` overrides; the sweep re-runs with `--sweep`.

DIRECTION SIGN. The arming Mage breached hi -> the excursion is UP -> an established direction is LONG.
Breached lo -> SHORT. This is the opposite mapping to the falsified branch, and it is Joe's own wording:
"if s15 and s22 have momo then s4M will stay oob for an extended period - that's an opprtuinity to pick up
a short trade" on a LOW oob. momo follows the excursion.

CAUSALITY. Every read is at the current bar over history ending there. The walk cannot look forward; it
can only fail to have established a direction yet, which is the conservative direction.

SCORING, when run over history: from the establish bar, the favourable excursion in the established
direction, against the 0.9% bar (handover §3.3 rule 1). One-sided. No horizon, no cap.

    python3 predict_walk.py                    # walk the last 24 h, report quorum 1 / 2 / 3
    python3 predict_walk.py --hours 48
    python3 predict_walk.py --quorum 2 --bank   # bank walks to rpl_pred_walk at that quorum
"""
import os, sys, time, datetime as dt
os.environ.setdefault('RPL_TF_CEILING', '4')
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_rpl_jig as J
import build_exhv2 as B
import optimus9.orchestration.rpl_walk as R
from optimus9.analysis.jig import Jig
from optimus9.compute.indicator_computer import IndicatorComputer as IC
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config

u = lambda m: dt.datetime.fromtimestamp(int(m) / 1000, dt.timezone.utc).strftime('%m-%d %H:%M:%S')
PCT = 0.9                      # handover §3.3: work = price moves >= 0.9% in the prediction's direction
STEP = 12                      # evaluate momo every 12 bars = 60 s. See the note in walk().

DDL = '''CREATE TABLE IF NOT EXISTS rpl_pred_walk (
    pw_pk BIGINT AUTO_INCREMENT PRIMARY KEY, pw_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    pw_quorum TINYINT,                                 -- the quorum this walk was run at
    pw_arm_ms BIGINT, pw_arm_utc VARCHAR(20),          -- the s1M/s2M crossing that armed it
    pw_arm_line VARCHAR(4), pw_arm_side VARCHAR(2),    -- s1M|s2M ; hi|lo
    pw_end_ms BIGINT, pw_end_utc VARCHAR(20),
    pw_end_why VARCHAR(12),                            -- established | in-bounds
    pw_bars INT, pw_minutes DOUBLE,
    pw_dir VARCHAR(5),                                 -- LONG|SHORT, NULL when it ended in-bounds
    pw_est_px DOUBLE,                                  -- pxs at the establish bar
    pw_momo_n TINYINT, pw_momo_which VARCHAR(24),      -- which of s4r/s15r/s22r read momo
    pw_fav_pct DOUBLE, pw_adv_pct DOUBLE, pw_hit09 TINYINT,
    KEY (pw_quorum), KEY (pw_arm_ms), KEY (pw_end_why))'''


def build(end_ms, hours):
    with Jig(end_ms, hours=hours, warmup=J.WIN_WARMUP, overrides=J.LINES) as j:
        ts = np.asarray(j.ts, np.int64)
        base = j.W.base
        evt = base['volume'].to_numpy(dtype=float) > 0
        src = IC.build_source(base, R.PXS_CFG['src'])
        ei = np.flatnonzero(evt)
        px = np.full(len(src), np.nan); px[ei] = IC.dema(src[ei], int(R.PXS_CFG['len']))
        fin = np.isfinite(px)
        ix = np.where(fin, np.arange(len(px)), 0); np.maximum.accumulate(ix, out=ix)
        px = px[ix]; px[:int(np.argmax(fin))] = px[int(np.argmax(fin))]
        L = {n: np.asarray(j.W.line(n), float) for n in J.LINES}
    return ts, px, L


def walk(ts, px, L, HI, LO, W0):
    """Every OOB stretch of s1M or s2M in the window, stepped forward. Returns one record per stretch with
    the momo count at each evaluated bar, so any quorum can be applied afterwards without re-walking.

    STEP = 12 bars = 60 s between momo evaluations. momo() fits 12 samples at 60-bar spacing, so its value
    cannot change materially inside 60 s, and evaluating all 5 s bars costs 12x for no extra resolution.
    This is a SAMPLING RATE on an unchanged quantity, not a cap on the walk — the walk still runs to the
    end of the stretch."""
    G1, G2 = L['jMg1'], L['jMg2']
    o1 = (G1 >= HI) | (G1 <= LO)
    o2 = (G2 >= HI) | (G2 <= LO)
    both = o1 | o2
    arm = np.flatnonzero(both & ~np.r_[False, both[:-1]])
    OUT = []
    for a in arm:
        a = int(a)
        if ts[a] < W0:
            continue
        line = 's1M' if o1[a] else 's2M'
        v = G1[a] if o1[a] else G2[a]
        side = 'hi' if v >= HI else 'lo'
        dr = 1 if side == 'hi' else -1
        e = a
        while e + 1 < len(ts) and both[e + 1]:
            e += 1
        steps = []
        for i in range(a, e + 1, STEP):
            sts = [B.momo(L[k], dr, i)[0] for k in ('jr4', 'jr15', 'jr22')]
            steps.append((i, sts))
        if steps and steps[-1][0] != e:
            steps.append((e, [B.momo(L[k], dr, e)[0] for k in ('jr4', 'jr15', 'jr22')]))
        OUT.append(dict(arm=a, end=e, line=line, side=side, dr=dr, steps=steps))
    return OUT


def resolve(w, ts, px, quorum):
    """Apply a quorum to a walked stretch. Returns the establish bar or None (ended in-bounds)."""
    for i, sts in w['steps']:
        n = sum(1 for s in sts if s == 'momo')
        if n >= quorum:
            which = ','.join(nm for nm, s in zip(('s4r', 's15r', 's22r'), sts) if s == 'momo')
            return i, n, which
    return None


def score(px, i, dr):
    """One-sided favourable excursion from bar i, in the direction dr, to the end of the built series."""
    seg = px[i:]
    up = (np.nanmax(seg) / px[i] - 1) * 100.0
    dn = (1 - np.nanmin(seg) / px[i]) * 100.0
    return (up, dn) if dr > 0 else (dn, up)


def main(argv):
    hours = int(argv[argv.index('--hours') + 1]) if '--hours' in argv else 24
    qbank = int(argv[argv.index('--quorum') + 1]) if '--quorum' in argv else None
    do_bank = '--bank' in argv
    HI, LO = R.HI, R.LO

    d = DatabaseManager(**get_db_config()); d.connect()
    end_ms = int(d.execute('SELECT MAX(kc_timestamp) m FROM kline_collection', fetch=True)[0]['m'])
    W0 = end_ms - hours * 3600000
    t0 = time.time()
    ts, px, L = build(end_ms, hours)
    print('jig build %.1f s   bars %d   HI/LO %g/%g   momo eval every %d bars = %d s'
          % (time.time() - t0, len(ts), HI, LO, STEP, STEP * 5))
    print('window %s -> %s   (the last %d h)' % (u(W0), u(end_ms), hours))

    W = walk(ts, px, L, HI, LO, W0)
    print('\nARMED WALKS  %d   (s1M or s2M crossing OOB, no dwell)' % len(W))
    print('  s1M-armed %d   s2M-armed %d   hi %d   lo %d'
          % (sum(1 for w in W if w['line'] == 's1M'), sum(1 for w in W if w['line'] == 's2M'),
             sum(1 for w in W if w['side'] == 'hi'), sum(1 for w in W if w['side'] == 'lo')))
    dur = [(w['end'] - w['arm']) * 5 / 60.0 for w in W]
    if dur:
        print('  stretch minutes: min %.1f  median %.1f  max %.1f  total %.1f'
              % (min(dur), float(np.median(dur)), max(dur), sum(dur)))

    print('\n%-8s %6s %8s %8s %9s %9s %8s %9s'
          % ('quorum', 'est', 'in-bnds', 'LONG', 'SHORT', 'fav med', 'hit 0.9%', 'net sum'))
    RES = {}
    for q in (1, 2, 3):
        est, ib, favs, advs, hits, dirs = [], 0, [], [], 0, []
        for w in W:
            r = resolve(w, ts, px, q)
            if r is None:
                ib += 1; continue
            i, n, which = r
            fav, adv = score(px, i, w['dr'])
            est.append((w, i, n, which, fav, adv))
            favs.append(fav); advs.append(adv); dirs.append('LONG' if w['dr'] > 0 else 'SHORT')
            hits += int(fav >= PCT)
        RES[q] = est
        if not est:
            print('%-8d %6d %8d %8s %9s %9s %8s %9s' % (q, 0, ib, '-', '-', '-', '-', '-')); continue
        print('%-8d %6d %8d %8d %9d %9.3f %8s %+9.3f'
              % (q, len(est), ib, dirs.count('LONG'), dirs.count('SHORT'), float(np.median(favs)),
                 '%d/%d' % (hits, len(est)), sum(f - a for f, a in zip(favs, advs))))

    q_show = qbank or 3
    print('\nWALKS AT QUORUM %d' % q_show)
    print('  %-9s %-4s %-3s %-9s %-6s %5s %-14s %8s %8s %7s'
          % ('arm', 'line', 'sd', 'establish', 'dir', 'bars', 'momo', 'fav%', 'adv%', 'hit'))
    for w in W:
        r = resolve(w, ts, px, q_show)
        if r is None:
            print('  %-9s %-4s %-3s %-9s %-6s %5d %-14s %8s %8s %7s'
                  % (u(ts[w['arm']])[6:], w['line'], w['side'], 'in-bounds', '-',
                     w['end'] - w['arm'], '-', '-', '-', '-'))
            continue
        i, n, which = r
        fav, adv = score(px, i, w['dr'])
        print('  %-9s %-4s %-3s %-9s %-6s %5d %-14s %8.3f %8.3f %7s'
              % (u(ts[w['arm']])[6:], w['line'], w['side'], u(ts[i])[6:],
                 'LONG' if w['dr'] > 0 else 'SHORT', i - w['arm'], which, fav, adv,
                 'YES' if fav >= PCT else 'no'))

    if do_bank and qbank:
        d.execute(DDL)
        d.execute('DELETE FROM rpl_pred_walk WHERE pw_quorum=%s', (qbank,))
        rows = []
        for w in W:
            r = resolve(w, ts, px, qbank)
            if r is None:
                rows.append((qbank, int(ts[w['arm']]), u(ts[w['arm']]), w['line'], w['side'],
                             int(ts[w['end']]), u(ts[w['end']]), 'in-bounds',
                             w['end'] - w['arm'], (w['end'] - w['arm']) * 5 / 60.0,
                             None, None, None, None, None, None, None))
            else:
                i, n, which = r
                fav, adv = score(px, i, w['dr'])
                rows.append((qbank, int(ts[w['arm']]), u(ts[w['arm']]), w['line'], w['side'],
                             int(ts[i]), u(ts[i]), 'established', i - w['arm'], (i - w['arm']) * 5 / 60.0,
                             'LONG' if w['dr'] > 0 else 'SHORT', float(px[i]), n, which,
                             float(fav), float(adv), int(fav >= PCT)))
        d.executemany('INSERT INTO rpl_pred_walk (pw_quorum,pw_arm_ms,pw_arm_utc,pw_arm_line,pw_arm_side,'
                      'pw_end_ms,pw_end_utc,pw_end_why,pw_bars,pw_minutes,pw_dir,pw_est_px,pw_momo_n,'
                      'pw_momo_which,pw_fav_pct,pw_adv_pct,pw_hit09) VALUES ('
                      + ','.join(['%s'] * 17) + ')', rows)
        print('\nbanked %d walks to rpl_pred_walk at quorum %d' % (len(rows), qbank))
    d.disconnect()


if __name__ == '__main__':
    main(sys.argv[1:])
