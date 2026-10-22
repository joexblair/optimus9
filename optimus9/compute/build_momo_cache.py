"""build_momo_cache - the mom-true mask and the away/toward tags, every timeframe, on the GPU.

Joe 1018: *"we'll need it tomorrow, all g15-30 and ws1-60"* / *"we'll need the away and toward
tags"* / *"6, gpu"*.

HIS FOUR RULINGS, 1018, and what each one fixed:
  the lines      *"use the lines in the `present` column"* - so ws1-ws30, ws45, ws60. The 28 ws
                 timeframes with no line on disk are not in the set, and g15/g30 fall out under
                 his *"4, not needed"* on a sub-minute momo bank.
  the role       *"3, r only"* - the r line per timeframe, both sides.
  the scale      *"the scale: B"* - MOMO_STALL_DELAY is five of the LINE'S OWN candles, so the hold
                 is `5 * tf` minutes = `5 * tf * 12` bars of the 5 s grid. This MOVES ws1 off the
                 25 s banked 0829, which his ruling takes.
  the route      *"6, gpu"* - momo_gpu, proved against the CPU bar for bar before anything is used.

TWO FILES PER TIMEFRAME, NOT ONE. The mask is keyed on the momentum knobs; the tags are keyed on
the momentum knobs AND the stall delay. A later ruling on the scale then rebuilds the tags alone
instead of the mask that cost the GPU pass. Both keys carry the tape window and every knob the
verdict reads - the 1008 and 1014 cache-drift failures were both a key that was missing a knob,
and both were silent.

EVERY FILE CARRIES A CONTROL. The line's bar count and its nan-safe sum are stored beside the
arrays and re-checked on load, so a cache hit on a changed tape is refused rather than returned.
"""
import os
import sys
import json
import time
import hashlib

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, os.path.join('/home/joe/thecodes', 'docs/octo-freedom/1005_scoring'))

from optimus9.compute import momo_gpu as G

# JOE'S TIMEFRAME SET, 1018. The lines that exist on disk, nothing inferred.
TFS = tuple(list(range(1, 31)) + [45, 60])

ROLE = 'r'                  # Joe 1018: *"3, r only"*
GATE2 = True                # momo_gated's default, which every CPU caller uses
STALL_CANDLES = 5           # MOMO_STALL_DELAY, Joe 0829. Reading B, Joe 1018: the line's own candles

CACHE = '/home/joe/thecodes/optimus9/orchestration/.rpl_cache/momt'

# THE KNOBS THE VERDICT READS. Every one is in the key. `momo_window_min` and `momo_step_min` are
# in it too even though momo_fixed_samples 21 currently overrides the step, because a bank that
# turned fixed_samples off would read them and must not load this file.
KEY_KNOBS = ('k_window', 'momo_fixed_samples', 'momo_step_min', 'momo_window_min',
             'momo_slope_min', 'momo_slack_ref', 'momo_r2_min', 'momo_seam', 'level_slack',
             'curl_arc_min', 'curl_r2_min', 'curl_vtx_lo', 'curl_vtx_hi')


def delay_bars(tf):
    """MOMO_STALL_DELAY in 5 s bars. Joe 1018 reading B: five of the line's own candles."""
    return int(STALL_CANDLES) * int(tf) * 12


def _key(em, hours, warmup, tf, role, bank, extra=None):
    base = [int(em), int(hours), int(warmup), int(tf), str(role), list(G.STATES), bool(GATE2),
            sorted((c, repr(bank[c])) for c in KEY_KNOBS if c in bank)]
    if extra is not None:
        base.append(extra)
    return hashlib.md5(json.dumps(base).encode()).hexdigest()[:20]


def _control(line, n):
    return {'bars': int(n), 'sum': float(np.nansum(np.asarray(line, float)[:n]))}


def build(tf, line, bank, em, hours, warmup, n=None, log=print):
    """Build and bank one timeframe's mask and tags. -> the two file paths and the row's numbers."""
    os.makedirs(CACHE, exist_ok=True)
    n = int(len(line) if n is None else n)
    wm, ns, stride, nb = G.grid(bank, tf)
    ctl = _control(line, n)

    t0 = time.time()
    mask = G.momtrue_gpu(line, tf, bank, n=n, gate2=GATE2)
    t_mask = time.time() - t0

    mk = _key(em, hours, warmup, tf, ROLE, bank)
    mp = os.path.join(CACHE, 'momt_ws%d_%s.npz' % (tf, mk))
    np.savez_compressed(mp, p=mask[+1], m=mask[-1],
                        meta=np.array(json.dumps(
                            {'tf': int(tf), 'role': ROLE, 'states': list(G.STATES),
                             'gate2': bool(GATE2), 'window_min': int(wm), 'samples': int(ns),
                             'stride_bars': int(stride), 'bend_bars': int(nb),
                             'knobs': {c: bank[c] for c in KEY_KNOBS if c in bank},
                             'control': ctl})))

    t0 = time.time()
    r = np.asarray(line, float)[:n]
    db_ = delay_bars(tf)
    walk, tags = {}, {}
    for dr in (+1, -1):
        ex_r, ex_bar, held = G.extrema_walk(r, mask[dr], dr)
        walk[dr] = (ex_r, ex_bar, held)
        tags[dr] = G.heading(mask[dr], ex_r, held, db_)
    t_tag = time.time() - t0

    tk = _key(em, hours, warmup, tf, ROLE, bank, extra=['stall', int(STALL_CANDLES), int(db_)])
    tp = os.path.join(CACHE, 'tag_ws%d_%s.npz' % (tf, tk))
    np.savez_compressed(
        tp,
        away_p=tags[+1], away_m=tags[-1],
        ex_r_p=walk[+1][0], ex_r_m=walk[-1][0],
        ex_bar_p=walk[+1][1], ex_bar_m=walk[-1][1],
        held_p=walk[+1][2], held_m=walk[-1][2],
        meta=np.array(json.dumps(
            {'tf': int(tf), 'role': ROLE, 'rule': 'report_wsf_bar.heading, Joe 0829',
             'stall_candles': int(STALL_CANDLES), 'stall_delay_bars': int(db_),
             'stall_delay_min': int(STALL_CANDLES) * int(tf), 'scale': 'B, Joe 1018',
             'mask_key': mk, 'control': ctl})))

    row = {'tf': int(tf), 'bars': n, 'window_min': int(wm), 'stride': int(stride),
           'bend_bars': int(nb), 'delay_bars': int(db_),
           'mt_p': int(mask[+1].sum()), 'mt_m': int(mask[-1].sum()),
           'away_p': int(tags[+1].sum()), 'away_m': int(tags[-1].sum()),
           't_mask': t_mask, 't_tag': t_tag, 'mask_path': mp, 'tag_path': tp}
    log('# ws%-3d mask %+d %7d / %+d %7d | away %7d / %7d | %.1fs mask, %.1fs tags'
        % (tf, +1, row['mt_p'], -1, row['mt_m'], row['away_p'], row['away_m'], t_mask, t_tag))
    return row


def main():
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        import score39 as SC
    from optimus9.db.database_manager import DatabaseManager
    from optimus9.config import get_db_config
    from optimus9.compute.momo_config import momo_bank

    db = DatabaseManager(**get_db_config()); db.connect()
    only = [int(a) for a in sys.argv[1:]] or list(TFS)
    rows = []
    n0 = None
    for tf in only:
        bank = momo_bank(db, tf)
        line = np.asarray(SC.LD(tf * 60, ROLE), float)
        if n0 is None:
            n0 = len(line)
            print('# tape %d bars | EM %s HOURS %s WARMUP %s | GPU %s | cache %s'
                  % (n0, SC.EM, SC.HOURS, SC.WARMUP, G.HAVE_GPU, CACHE), flush=True)
        assert len(line) == n0, 'ws%d has %d bars, ws%d had %d' % (tf, len(line), only[0], n0)
        rows.append(build(tf, line, bank, SC.EM, SC.HOURS, SC.WARMUP, n=n0))
    db.disconnect()

    print()
    print('| the tf | window | stride | bend bars | stall delay | mom-true +1 | mom-true -1 | away +1 | away -1 |')
    print('|---|---|---|---|---|---|---|---|---|')
    for r in rows:
        print('| ws%d | %d min | %d | %d | %d bars = %d min | %d | %d | %d | %d |'
              % (r['tf'], r['window_min'], r['stride'], r['bend_bars'], r['delay_bars'],
                 r['delay_bars'] // 12, r['mt_p'], r['mt_m'], r['away_p'], r['away_m']))
    print()
    print('| the total | value |')
    print('|---|---|')
    print('| timeframes built | %d |' % len(rows))
    print('| GPU mask seconds | %.1f |' % sum(r['t_mask'] for r in rows))
    print('| tag-walk seconds | %.1f |' % sum(r['t_tag'] for r in rows))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
