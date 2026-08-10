"""sweep_s46_div — knob sweep over the banked divergence grid. MAE only. Joe 0804.

    ############################################################################
    #  DISABLED — Joe 0804: "disable, but don't remove, the divergence code"   #
    #  Runs only with --enable. Read-only over s46_div + s46_flip, so it stays #
    #  usable for re-reading the falsification; it drives nothing.             #
    ############################################################################

PURE READER over s46_div + s46_flip. Computes no lines, no entries, no exits. `pk_state` is
re-applied here from the banked raw slopes (dv_line_slope, dv_price_slope), so it stays the single
source of truth (jig `_Causal.pk_state` -> Pk5sGateComputer._pk_state_from_slopes) while
SLOPE_FLOOR and the Price-Match policy cost nothing to sweep.

THE DECISION, per entry
    votes = the lines whose pk_state CONTRADICTS the trade's own side.
      LONG entry  (s4Mage breached HI): a BEAR state (-1) contradicts it
      SHORT entry (s4Mage breached LO): a BULL state (+1) contradicts it
    votes >= VOTE_MIN  ->  FLIP: take the opposite side (Joe: "hi breach becomes SHORT")
    otherwise          ->  the trade stands as-is
    MAE is then read off s46_flip: fl_mae for a stand, fl_f_mae for a flip. Both were scored in the
    builder against s46_px with the same s6 exit rule; a flipped side takes the next OPPOSITE-
    direction s6 exit.

KNOBS
    --mult      lookback multiplier; window = MULT x TF_MAX(6) minutes            grid col
    --guard     bars before the anchor excluded from the floater search           grid col
    --voteset   Mage3 | r3 | m3 | Mage_r (Joe's 6 votes) | all9
    --votemin   contradicting votes needed to flip
    --floor     pk_state noise deadband, board points: |ls - ps| <= floor -> 0
    --pm        Price Match (+-2) DIRECTION:  abstain | with | against
                  with    a same-sign PM adds to the vote count
                  against a same-sign PM subtracts from it   (Joe 0804: "give each P a vote against D")
                  abstain PM is ignored - PM is trend continuation, not divergence
    --pmw       Price Match WEIGHT, swept. Joe 0804: "0.5 is a knob".
                  votes = D  (+/- pmw) * P     pmw 0 is identical to --pm abstain
    --keepflat  keep rows where dv_line_slope is EXACTLY 0. Default is to drop them: pk_state maps a
                flat line to -1.0 via the sign(0)=0 branch, which IS the contradicting state on a
                LONG trade, so 4,910 flat rows (99% of them the r lines pegged at 100) were being
                counted as bear votes - 8.1% of every LONG vote in the grid. Dropped at the CONSUMER;
                Pk5sGateComputer._pk_state_from_slopes is a shared production seam and is untouched.
    --win       restrict to a date window, e.g. 2026-07-29:2026-07-31
    --one       per-line card for a single entry, e.g. 2026-07-29T06:26

    python3 sweep_s46_div.py
    python3 sweep_s46_div.py --win 2026-07-29:2026-07-31
    python3 sweep_s46_div.py --one 2026-07-29T06:26 --mult 25 --guard 0
"""
import sys, os, datetime as dt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from optimus9.db.database_manager import DatabaseManager
from optimus9.config import get_db_config
from optimus9.analysis.jig import _Causal

U = lambda m: dt.datetime.fromtimestamp(int(m) / 1000, dt.timezone.utc).strftime('%m-%d %H:%M:%S')
LINES = ('s4Mage', 's5Mage', 's6Mage', 's4r', 's5r', 's6r', 's4m', 's5m', 's6m')
VOTESETS = {
    'Mage3':  ('s4Mage', 's5Mage', 's6Mage'),
    'r3':     ('s4r', 's5r', 's6r'),
    'm3':     ('s4m', 's5m', 's6m'),
    'Mage_r': ('s4Mage', 's5Mage', 's6Mage', 's4r', 's5r', 's6r'),          # Joe's "6 votes in total"
    'all9':   LINES,
}
PMS = ('abstain', 'with', 'against')
VMINS = np.arange(0.5, 9.5, 0.5)          # a fractional PMW makes the tally fractional, so step 0.5
LBL = {1.0: 'BULL', -1.0: 'BEAR', 2.0: 'PMlong', -2.0: 'PMshort', 0.0: 'noise'}
_ms = lambda x: int(dt.datetime(*[int(z) for z in x.split('-')],
                                tzinfo=dt.timezone.utc).timestamp() * 1000)


def load(win):
    d = DatabaseManager(**get_db_config()); d.connect()
    w, p = '', ()
    if win:
        a, b = win.split(':')
        w, p = ' WHERE %s>=%%s AND %s<%%s', (_ms(a), _ms(b))
    FL = d.execute('SELECT fl_entry_ms,fl_entry_utc,fl_dr,fl_mae,fl_f_mae FROM s46_flip'
                   + (w % ('fl_entry_ms', 'fl_entry_ms') if w else '') + ' ORDER BY fl_entry_ms',
                   p, fetch=True)
    DV = d.execute('SELECT dv_entry_ms,dv_mult,dv_guard,dv_line,dv_line_slope,dv_price_slope,'
                   'dv_float_ms,dv_float_val,dv_pxs_ms,dv_pxs_val,dv_anchor_val,dv_anchor_px '
                   'FROM s46_div' + (w % ('dv_entry_ms', 'dv_entry_ms') if w else ''), p, fetch=True)
    d.disconnect()
    return FL, DV


def arrays(FL, DV):
    ems = np.array([r['fl_entry_ms'] for r in FL], np.int64)
    dr = np.array([r['fl_dr'] for r in FL], np.int8)
    mae0 = np.array([r['fl_mae'] for r in FL], float)          # MAE if the trade stands
    mae1 = np.array([r['fl_f_mae'] for r in FL], float)        # MAE if it flips
    de = np.array([r['dv_entry_ms'] for r in DV], np.int64)
    keep = np.isin(de, ems)
    DV = [r for r, k in zip(DV, keep) if k]
    de = de[keep]
    eidx = np.searchsorted(ems, de)
    li = np.array([LINES.index(r['dv_line']) for r in DV], np.int8)
    return dict(ems=ems, dr=dr, mae0=mae0, mae1=mae1, FL=FL, DV=DV, eidx=eidx, li=li,
                mult=np.array([r['dv_mult'] for r in DV], np.int16),
                guard=np.array([r['dv_guard'] for r in DV], np.int16),
                ls=np.array([r['dv_line_slope'] for r in DV], float),
                ps=np.array([r['dv_price_slope'] for r in DV], float))


DISABLED = ('sweep_s46_div is DISABLED (Joe 0804: "disable, but don\'t remove, the divergence code").\n'
            'Read-only; the tables it reads are retained. Pass --enable to run it anyway.')


def main(argv):
    if '--enable' not in argv:
        raise SystemExit(DISABLED)
    g = lambda f, d: (argv[argv.index(f) + 1] if f in argv else d)
    win = g('--win', None); top = int(g('--top', '15')); one = g('--one', None)
    FL, DV = load(win)
    if not FL:
        raise SystemExit('s46_flip has no rows for window %s' % win)
    A = arrays(FL, DV)
    N = len(A['ems'])
    mults = sorted(set(int(x) for x in A['mult']))
    guards = sorted(set(int(x) for x in A['guard']))
    C = _Causal(None)

    print('population %d entries   %s -> %s' % (N, FL[0]['fl_entry_utc'], FL[-1]['fl_entry_utc']))
    print('  MAE stand-all   mean %.3f%%  median %.3f%%  max %.3f%%'
          % (A['mae0'].mean(), np.median(A['mae0']), A['mae0'].max()))
    print('  MAE flip-all    mean %.3f%%  median %.3f%%  max %.3f%%'
          % (A['mae1'].mean(), np.median(A['mae1']), A['mae1'].max()))
    print()

    if one:
        t = int(dt.datetime.strptime(one, '%Y-%m-%dT%H:%M').replace(tzinfo=dt.timezone.utc)
                .timestamp() * 1000)
        M, G, fl = int(g('--mult', '25')), int(g('--guard', '0')), float(g('--floor', '0'))
        st = C.pk_state(A['ls'], A['ps'], fl)
        k = int(np.searchsorted(A['ems'], t))
        sel = np.flatnonzero((A['eidx'] == k) & (A['mult'] == M) & (A['guard'] == G))
        print('=== %s  dr %+d  MULT %d (%d min)  GUARD %d bars  floor %g ==='
              % (U(t), A['dr'][k], M, M * 6, G, fl))
        print('  anchor px %.6f' % (A['DV'][sel[0]]['dv_anchor_px'] if len(sel) else float('nan')))
        print('  %-8s %-12s %9s %-12s %11s %9s %10s   %s'
              % ('line', 'floater', 'floatval', 'pxs extr', 'pxs val', 'anch val', 'line slope', 'state'))
        for i in sel:
            r = A['DV'][i]
            print('  %-8s %-12s %9.2f %-12s %11.6f %9.2f %10.2f   %+.1f %s'
                  % (r['dv_line'], U(r['dv_float_ms'])[6:], r['dv_float_val'], U(r['dv_pxs_ms'])[6:],
                     r['dv_pxs_val'], r['dv_anchor_val'], r['dv_line_slope'],
                     st[i], LBL.get(float(st[i]), '?')))
        contra = -1.0 if A['dr'][k] > 0 else 1.0
        print('  contradicting votes %d of %d   |   MAE stand %.3f%%   MAE flipped %.3f%%'
              % (int((st[sel] == contra).sum()), len(sel), A['mae0'][k], A['mae1'][k]))
        return

    live = np.ones(len(A['ls']), bool) if '--keepflat' in argv else (A['ls'] != 0.0)
    if '--keepflat' not in argv:
        print('  %d of %d grid rows dropped: dv_line_slope exactly 0 (flat line, not a divergence)'
              % (int((~live).sum()), len(live)))
        print()

    ap = g('--apply', None)
    if ap:              # --apply MULT,GUARD,VOTESET,VMIN,FLOOR,PM,PMW  -> the per-trade vote list
        pr = ap.split(',')
        M, G, vs, vm, fl, pm = int(pr[0]), int(pr[1]), pr[2], float(pr[3]), float(pr[4]), pr[5]
        pmw = float(pr[6]) if len(pr) > 6 else 1.0
        st = C.pk_state(A['ls'], A['ps'], fl)
        contra_row = np.where(A['dr'][A['eidx']] > 0, -1.0, 1.0)
        sel = (A['mult'] == M) & (A['guard'] == G) & live & np.isin(
            A['li'], np.array([LINES.index(x) for x in VOTESETS[vs]]))
        dv = ((st == contra_row) & sel).astype(float)
        pmv = ((st == contra_row * 2.0) & sel).astype(float)
        sgn = 1.0 if pm == 'with' else (-1.0 if pm == 'against' else 0.0)
        nD = np.bincount(A['eidx'], weights=dv, minlength=N)
        nP = np.bincount(A['eidx'], weights=pmv, minlength=N)
        tal = nD + sgn * pmw * nP
        f = tal >= vm
        mae = np.where(f, A['mae1'], A['mae0'])
        print('=== APPLY  MULT %d (%d min)  GUARD %d  %s  VMIN %g  FLOOR %g  PM %s  PMW %g ==='
              % (M, M * 6, G, vs, vm, fl, pm, pmw))
        print('  %-3s %-20s %-6s %4s %4s %8s %9s %9s %8s %s'
              % ('#', 'entry utc', 'side', 'D', 'P', 'votes', 'MAEstand', 'MAEflip', 'delta', 'flip'))
        for k in range(N):
            print('  %-3d %-20s %-6s %4d %4d %8.2f %9.3f %9.3f %+8.3f %s'
                  % (k + 1, FL[k]['fl_entry_utc'], 'LONG' if A['dr'][k] > 0 else 'SHORT',
                     int(nD[k]), int(nP[k]), tal[k], A['mae0'][k], A['mae1'][k],
                     A['mae1'][k] - A['mae0'][k], 'FLIP' if f[k] else ''))
        print('  flips %d of %d   MAE mean %.3f -> %.3f   median %.3f -> %.3f   max %.3f -> %.3f'
              % (int(f.sum()), N, A['mae0'].mean(), mae.mean(), np.median(A['mae0']),
                 np.median(mae), A['mae0'].max(), mae.max()))
        return

    floors = [float(x) for x in g('--floor', '0,10,20,30,40').split(',')]
    pmws = [float(x) for x in g('--pmw', '0,0.25,0.5,0.75,1').split(',')]
    # --isoos: chronological 50/50 by entry count. SELECT ON IS ONLY, report OOS as the consequence.
    isoos = '--isoos' in argv
    K = N // 2
    vsets = g('--voteset', ','.join(VOTESETS)).split(',')
    pms = g('--pm', ','.join(PMS)).split(',')
    contra_row = np.where(A['dr'][A['eidx']] > 0, -1.0, 1.0)
    res = []
    for fl in floors:
        st = C.pk_state(A['ls'], A['ps'], fl)
        hit = (st == contra_row)                       # the divergence that argues against the trade
        pmhit = (st == contra_row * 2.0)               # same-sign Price Match
        for M in mults:
            mm = A['mult'] == M
            for G in guards:
                mg = mm & (A['guard'] == G)
                for vs in vsets:
                    li = np.array([LINES.index(x) for x in VOTESETS[vs]])
                    sel = mg & live & np.isin(A['li'], li)
                    if not sel.any():
                        continue
                    nD = np.bincount(A['eidx'], weights=(hit & sel).astype(float), minlength=N)
                    nP = np.bincount(A['eidx'], weights=(pmhit & sel).astype(float), minlength=N)
                    for pm in pms:
                        sgn = 1.0 if pm == 'with' else (-1.0 if pm == 'against' else 0.0)
                        for pmw in (pmws if sgn else [0.0]):     # abstain: weight is meaningless
                            tal = nD + sgn * pmw * nP
                            for vm in VMINS[:len(VOTESETS[vs]) * 2]:
                                f = tal >= vm
                                nf = int(f.sum())
                                if nf == 0:
                                    continue
                                mae = np.where(f, A['mae1'], A['mae0'])
                                good = int((A['mae1'][f] < A['mae0'][f]).sum())   # flips that cut MAE
                                if isoos:
                                    fi, fo = f[:K], f[K:]
                                    ni, no = int(fi.sum()), int(fo.sum())
                                    if ni == 0 or no == 0:
                                        continue
                                    res.append((mae[:K].mean(), mae[K:].mean(), ni, no,
                                                M, G, vs, vm, fl, '%s%g' % (pm[:4], pmw),
                                                int((A['mae1'][:K][fi] < A['mae0'][:K][fi]).sum()),
                                                int((A['mae1'][K:][fo] < A['mae0'][K:][fo]).sum()),
                                                mae[:K].max(), mae[K:].max()))
                                    continue
                                res.append((mae.mean(), np.median(mae), mae.max(), nf,
                                            M, G, vs, vm, fl, '%s%g' % (pm[:4], pmw), good))
    if not res:
        print('no knob setting produced a single flip'); return
    if isoos:
        b_is, b_oos = A['mae0'][:K], A['mae0'][K:]
        print('IS  entries 1..%d      %s -> %s   MAE mean %.3f  max %.3f'
              % (K, FL[0]['fl_entry_utc'], FL[K - 1]['fl_entry_utc'], b_is.mean(), b_is.max()))
        print('OOS entries %d..%d    %s -> %s   MAE mean %.3f  max %.3f'
              % (K + 1, N, FL[K]['fl_entry_utc'], FL[-1]['fl_entry_utc'], b_oos.mean(), b_oos.max()))
        print()
        h = ('  %-5s %-5s %-7s %-5s %-5s %-9s %6s %8s %8s %6s %8s %8s'
             % ('MULT', 'GUARD', 'VOTESET', 'VMIN', 'FLR', 'PM+W', 'ISflp', 'IS MAE', 'IS max',
                'OOSflp', 'OOS MAE', 'OOS max'))
        rw = lambda r: ('  %-5d %-5d %-7s %-5g %-5g %-9s %6d %8.3f %8.3f %6d %8.3f %8.3f  %s'
                        % (r[4], r[5], r[6], r[7], r[8], r[9], r[2], r[0], r[12], r[3], r[1], r[13],
                           'OOS beats base' if r[1] < b_oos.mean() else ''))
        print('=== best IS MAE MEAN per IS flip band   (IS base %.3f  OOS base %.3f) ==='
              % (b_is.mean(), b_oos.mean()))
        print(h)
        lo = 1
        for hi in (10, 25, 50, 100, 200, K):
            band = [r for r in res if lo <= r[2] <= hi]
            if band:
                print('  -- IS flips %d..%d (%d settings)' % (lo, hi, len(band)))
                print(rw(min(band, key=lambda r: r[0])))
            lo = hi + 1
        print()
        beat = [r for r in res if r[0] < b_is.mean()]
        held = [r for r in beat if r[1] < b_oos.mean()]
        print('settings beating baseline IS: %d of %d' % (len(beat), len(res)))
        print('  of those, also beating baseline OOS: %d = %.1f%%'
              % (len(held), 100.0 * len(held) / max(1, len(beat))))
        if held:
            print('  best of those, by OOS MAE mean:')
            print(h)
            for r in sorted(held, key=lambda r: r[1])[:top]:
                print(rw(r))
        oi = np.array([r[0] for r in res]); oo = np.array([r[1] for r in res])
        print('  IS vs OOS MAE mean correlation across all %d settings: %+.3f'
              % (len(res), float(np.corrcoef(oi, oo)[0, 1])))
        return

    hdr = ('  %-5s %-5s %-7s %-5s %-5s %-9s %6s %9s %9s %9s %11s'
           % ('MULT', 'GUARD', 'VOTESET', 'VMIN', 'FLR', 'PM+W', 'flips', 'MAEmean', 'MAEmed',
              'MAEmax', 'flips cut'))
    row = lambda r: ('  %-5d %-5d %-7s %-5g %-5g %-9s %6d %9.3f %9.3f %9.3f %6d %4.0f%%'
                     % (r[4], r[5], r[6], r[7], r[8], r[9], r[3], r[0], r[1], r[2],
                        r[10], 100.0 * r[10] / r[3]))
    for name, key in (('MAE MEAN', lambda r: r[0]), ('MAE MAX', lambda r: (r[2], r[0]))):
        print('=== best by %s   (stand-all: mean %.3f  median %.3f  max %.3f) ==='
              % (name, A['mae0'].mean(), np.median(A['mae0']), A['mae0'].max()))
        print(hdr)
        for r in sorted(res, key=key)[:top]:
            print(row(r))
        print()

    # A setting that flips nothing scores the baseline, so rank WITHIN flip-volume bands.
    print('=== best MAE MEAN per flip-volume band  (band = how many of %d entries flip) ===' % N)
    print(hdr)
    lo = 1
    for hi in (10, 25, 50, 100, 200, 400, N):
        band = [r for r in res if lo <= r[3] <= hi]
        if band:
            print('  -- %d..%d flips (%d settings)' % (lo, hi, len(band)))
            print(row(min(band, key=lambda r: r[0])))
        lo = hi + 1
    print()
    # Non-causal upper bound: flip exactly the entries a flip would have helped.
    orc = np.minimum(A['mae0'], A['mae1'])
    nb = int((A['mae1'] < A['mae0']).sum())
    print('=== ORACLE (non-causal, upper bound on ANY flip rule) ===')
    print('  flip the %d of %d entries where flipping cuts MAE  ->  mean %.3f  median %.3f  max %.3f'
          % (nb, N, orc.mean(), np.median(orc), orc.max()))
    print()
    print('%d knob settings evaluated   flips range %d -> %d of %d entries'
          % (len(res), min(r[3] for r in res), max(r[3] for r in res), N))


if __name__ == '__main__':
    main(sys.argv[1:])
