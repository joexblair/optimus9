"""
emit_champion_recon — MODULAR recon emitter. Build the shared data (ctx) once, then compose a
list of toggleable MODULES into one Pine. A recon variation = a different module list.

Modules (each = a self-contained Pine layer):
  walk              s30r bls walk band (1 ylw · 2 org · 3 lime)            [bgcolor]
  labels            s30r:N state-transition labels (HEAVY — 500-label cap) [label]
  exits             raw exit1/2/3 fires (HEAVY)                            [plotshape]
  pk_raw            raw 5s PKs, ungated (HEAVY)                            [plotshape]
  bias_reset_wp     bny30 bias RESET, WITH bny30p — navy bg               [bgcolor]
  bias_reset_wop    bny30 bias RESET, WITHOUT p / M-only — sky-blue bg     [bgcolor]
  cbls3_aligned     big blue ◆ on every bias-ALIGNED c_bls:3 onset         [plotshape]
  pk_aligned        bias-aligned PKs (pk==bias) as green ▲ / red ▼         [plotshape]
  table             champion line table (top-right)

cbls3_aligned + pk_aligned follow ONE in-chart toggle (alignWithP) that flips both between the
with-p and without-p bias — hone in by watching the diamonds + arrows move.

The 48h recon keeps the lean modules (no label cap, small arrays); labels/exits/pk_raw are
available but off the 48h list (heavy + capped).

Run:  python3 emit_champion_recon.py --hours 48           # the full 48h module recon
      python3 emit_champion_recon.py --hours 12 --all     # +labels/exits/pk_raw (heavy)
"""
import sys, json
import numpy as np
from datetime import datetime, timezone
sys.path.insert(0, '/home/joe/thecodes')
import logging
for nm in ('BybitKlineClient', 'BLDetect', 'KlineLoader', 'DatabaseManager'):
    logging.getLogger(nm).setLevel('ERROR')
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.analysis.bl_detect import BLDetect, GCA5M_RAW
from optimus9.orchestration.gate_signal_sweep import pine_aligned_signals, bny30_latched_bias
from bl_dialin import BREACH, SUPPORT_IC, WIN_FILE
from logger import get_logger

CHAMP_K = {'k_len': 5, 'rsi_len': 6, 'stc_len': 6, 'src': 'hl2'}
CHAMP_SUP = {'bb_len': 10, 'bb_mult': 0.40, 'src': 'hlc3'}
CHAMP_MASK, CHAMP_LB = 5, 5
LEAN = ['walk', 'cbls3_aligned', 'pk_aligned', 's30m_entry', 'bias_reset_wp', 'bias_reset_wop', 'table']
HEAVY = ['labels', 'exits', 'pk_raw']
log = get_logger('ChampRecon')
Q = chr(34)


def arr(xs):
    return f"array.from({','.join(str(x) for x in xs)})" if xs else "array.new<int>(0)"


def sarr(xs):
    return f"array.from({','.join(Q + str(x) + Q for x in xs)})" if xs else "array.new<string>(0)"


# ─────────────────────────────── shared data ───────────────────────────────
def build_ctx(det, db, end):
    base, ts, win_start, _, _ = det._setup(end)
    s30r = [f for f in det._families if f['name'] == BREACH][0]
    sup0 = det._cfg_dict(SUPPORT_IC)
    fam = {**s30r, 'k': {**s30r['k'], **CHAMP_K}, 'exit_support': {**sup0, **CHAMP_SUP}, 'exit_mask': CHAMP_MASK}
    fr = det._run_family(fam, base, ts); r = fr[3]; s30m = np.asarray(fr[4], float)   # [4]=exit_support (s30m)
    state = np.asarray(r['state']).astype(int); bdir = np.asarray(r['breach_dir']).astype(int)
    e1 = np.asarray(r['exit1']).astype(bool); e2 = np.asarray(r['exit2']).astype(bool); e3 = np.asarray(r['exit3']).astype(bool)
    ai, ad = pine_aligned_signals(base, db, GCA5M_RAW, gate=False)
    pk = np.zeros(len(ts), np.int8); pk[ai] = ad
    thr = int(det._cfg['blc_bny30_bias_reset_threshold'])
    bias_wp, reset_wp = bny30_latched_bias(base, thr, use_k=True, return_resets=True)     # WITH bny30p
    bias_wo, reset_wo = bny30_latched_bias(base, thr, use_k=False, return_resets=True)     # M-only

    M = ts >= win_start
    tsm = ts[M].astype('int64'); st = state[M]; bd = bdir[M]
    e1m, e2m, e3m = e1[M], e2[M], e3[M]; pkm = pk[M]; N = len(tsm)
    bwp = bias_wp[M]; bwo = bias_wo[M]; rwp = reset_wp[M]; rwo = reset_wo[M]; s30m_m = s30m[M]

    trans = [i for i in range(1, N) if st[i] != st[i - 1]]
    g3 = [i for i in trans if st[i] == 3]                               # c_bls:3 onsets (solo c_bls = s30r:3)

    def aligned_g3(bias):                                               # diamond where trade-side (−bd) == bias
        return [int(tsm[i]) for i in g3 if bd[i] != 0 and bias[i] != 0 and -bd[i] == bias[i]]

    def aligned_pk(bias, d):                                            # bias-aligned PKs of direction d
        return [int(tsm[i]) for i in range(N) if pkm[i] == d and bias[i] == d]

    LB = 16                                                            # match bl_review LOOKBACK
    def entries_thrown(bm):                                            # C-confirmed s30m entries + thrown-out, per bias
        ent, thr = [], []
        for gi in g3:
            td = int(bm[gi])
            if td == 0:
                continue
            lo2, hi2 = max(0, gi - LB), min(N, gi + LB + 1)
            if not any(pkm[j] != 0 and pkm[j] == td for j in range(lo2, hi2)):    # needs a bias-aligned PK candidate
                continue
            ej = None                                                  # C: 2 consecutive bias-aligned s30m bars off an OOB peak/trough
            for j in range(gi + 2, hi2):
                a, b, cc = s30m_m[j - 2], s30m_m[j - 1], s30m_m[j]
                if a != a or b != b or cc != cc:
                    continue
                if (td == -1 and a > 85 and cc < b < a) or (td == 1 and a < 15 and cc > b > a):
                    ej = j; break
            (ent if ej is not None else thr).append(int(tsm[ej if ej is not None else gi]))
        return ent, thr
    ent_wp, thr_wp = entries_thrown(bwp); ent_wo, thr_wo = entries_thrown(bwo)

    return dict(
        base=base, span=(f"{datetime.fromtimestamp(tsm[0]/1000, tz=timezone.utc):%m-%d %H:%M}–"
                         f"{datetime.fromtimestamp(tsm[-1]/1000, tz=timezone.utc):%m-%d %H:%M} UTC"),
        daytag=f"{datetime.fromtimestamp(tsm[-1]/1000, tz=timezone.utc):%m%d}", N=N, thr=thr,
        fam=fam, sup0=sup0, det=det, db=db, st0=int(st[0]),
        stt=[int(tsm[i]) for i in trans], stv=[int(st[i]) for i in trans],
        ltt=[int(tsm[i]) for i in trans],
        lls=[f"s30r:{int(st[i])}{('↓' if bd[i] < 0 else ('↑' if bd[i] > 0 else '')) if st[i] == 1 else ''}" for i in trans],
        e1t=[int(tsm[i]) for i in range(N) if e1m[i]], e2t=[int(tsm[i]) for i in range(N) if e2m[i]],
        e3t=[int(tsm[i]) for i in range(N) if e3m[i]],
        pu=[int(tsm[i]) for i in range(N) if pkm[i] == 1], pdn=[int(tsm[i]) for i in range(N) if pkm[i] == -1],
        rwp_t=[int(tsm[i]) for i in range(N) if rwp[i]], rwo_t=[int(tsm[i]) for i in range(N) if rwo[i]],
        dia_wp=aligned_g3(bwp), dia_wo=aligned_g3(bwo),
        pkal_wp_l=aligned_pk(bwp, 1), pkal_wp_s=aligned_pk(bwp, -1),
        pkal_wo_l=aligned_pk(bwo, 1), pkal_wo_s=aligned_pk(bwo, -1),
        ent_wp=ent_wp, thr_wp=thr_wp, ent_wo=ent_wo, thr_wo=thr_wo,
        n_g3=len(g3))


# ─────────────────────────────── modules ───────────────────────────────
# each module → dict(inp=<input lines>, decl=<array decls>, render=<plot lines>)
def mod_walk(c):
    return dict(inp='showWalk = input.bool(true, "bls walk band (1 ylw · 2 org · 3 lime)")',
                decl=f"var int[] stt = {arr(c['stt'])}\nvar int[] stv = {arr(c['stv'])}",
                render="bgcolor(showWalk and cur==1 ? color.new(color.yellow,82) : showWalk and cur==2 ? "
                       "color.new(color.orange,80) : showWalk and cur==3 ? color.new(color.lime,82) : na, title=\"bls walk\")")


def mod_labels(c):
    return dict(inp='showLbl  = input.bool(false, "s30r:N labels (heavy · 500 cap)")',
                decl=f"var int[] ltt = {arr(c['ltt'])}\nvar string[] lls = {sarr(c['lls'])}",
                render="if showLbl and array.includes(ltt, ms)\n"
                       "    label.new(bar_index, high, array.get(lls, array.indexof(ltt, ms)), "
                       "color=color.new(color.gray,30), textcolor=color.white, style=label.style_label_down, size=size.small)")


def mod_exits(c):
    return dict(inp='showExit = input.bool(false, "raw exit1/2/3 (heavy)")',
                decl=f"var int[] e1 = {arr(c['e1t'])}\nvar int[] e2 = {arr(c['e2t'])}\nvar int[] e3 = {arr(c['e3t'])}",
                render="plotshape(showExit and array.includes(e1, ms), style=shape.xcross,  location=location.abovebar, color=color.aqua,    size=size.tiny, title=\"exit1\")\n"
                       "plotshape(showExit and array.includes(e2, ms), style=shape.xcross,  location=location.abovebar, color=color.fuchsia, size=size.tiny, title=\"exit2\")\n"
                       "plotshape(showExit and array.includes(e3, ms), style=shape.diamond, location=location.abovebar, color=color.white,   size=size.tiny, title=\"exit3\")")


def mod_pk_raw(c):
    return dict(inp='showPkRaw= input.bool(false, "raw 5s PKs, ungated (heavy)")',
                decl=f"var int[] puR = {arr(c['pu'])}\nvar int[] pdR = {arr(c['pdn'])}",
                render="plotshape(showPkRaw and array.includes(puR, ms), style=shape.triangleup,   location=location.belowbar, color=color.new(color.green,60), size=size.tiny, title=\"pk raw long\")\n"
                       "plotshape(showPkRaw and array.includes(pdR, ms), style=shape.triangledown, location=location.abovebar, color=color.new(color.red,60),   size=size.tiny, title=\"pk raw short\")")


def mod_bias_reset_wp(c):
    return dict(inp='showRstWP = input.bool(true, "bias reset WITH-p (navy)")',
                decl=f"var int[] rstWP = {arr(c['rwp_t'])}",
                render="bgcolor(showRstWP and array.includes(rstWP, ms) ? color.new(color.navy, 15) : na, title=\"bias reset WITH-p\")")


def mod_bias_reset_wop(c):
    return dict(inp='showRstWO = input.bool(true, "bias reset WITHOUT-p / M-only (sky)")',
                decl=f"var int[] rstWO = {arr(c['rwo_t'])}",
                render="bgcolor(showRstWO and array.includes(rstWO, ms) ? color.new(color.rgb(135,206,235), 15) : na, title=\"bias reset M-only\")")


def mod_cbls3_aligned(c):
    return dict(inp='showDia = input.bool(true, "◆ bias-aligned c_bls:3")',
                decl=f"var int[] diaWP = {arr(c['dia_wp'])}\nvar int[] diaWO = {arr(c['dia_wo'])}",
                render="plotshape(showDia and array.includes(alignWithP ? diaWP : diaWO, ms), style=shape.diamond, "
                       "location=location.belowbar, color=color.new(color.blue,0), size=size.normal, title=\"bias-aligned c_bls:3\")")


def mod_pk_aligned(c):
    return dict(inp='showPkAl = input.bool(true, "bias-aligned PKs (grn ▲ / red ▼)")',
                decl=f"var int[] pkLwp = {arr(c['pkal_wp_l'])}\nvar int[] pkSwp = {arr(c['pkal_wp_s'])}\nvar int[] pkLwo = {arr(c['pkal_wo_l'])}\nvar int[] pkSwo = {arr(c['pkal_wo_s'])}",
                render="plotshape(showPkAl and array.includes(alignWithP ? pkLwp : pkLwo, ms), style=shape.triangleup,   location=location.belowbar, color=color.new(color.green,0), size=size.small, title=\"pk aligned long\")\n"
                       "plotshape(showPkAl and array.includes(alignWithP ? pkSwp : pkSwo, ms), style=shape.triangledown, location=location.abovebar, color=color.new(color.red,0),   size=size.small, title=\"pk aligned short\")")


def mod_s30m_entry(c):
    return dict(inp='showEntry= input.bool(true, "s30m entries (yellow ●) + thrown-out (grey ✕)")',
                decl=f"var int[] entWP = {arr(c['ent_wp'])}\nvar int[] entWO = {arr(c['ent_wo'])}\n"
                     f"var int[] thrWP = {arr(c['thr_wp'])}\nvar int[] thrWO = {arr(c['thr_wo'])}",
                render="plotshape(showEntry and array.includes(alignWithP ? entWP : entWO, ms), style=shape.circle,  location=location.belowbar, color=color.new(color.yellow,0), size=size.small, title=\"s30m entry (C-confirmed)\")\n"
                       "plotshape(showEntry and array.includes(alignWithP ? thrWP : thrWO, ms), style=shape.xcross,  location=location.abovebar, color=color.new(color.gray,30),   size=size.tiny,  title=\"thrown out (no s30m turn)\")")


def mod_table(c):
    blr = c['db'].execute('''SELECT bl_pk_ic_pk, bl_support_ic_pk, bl_exit3_support_ic_pk
                             FROM bl_lines WHERE bl_line_name=%s AND bl_role='breach' AND bl_is_active=1''',
                          (BREACH,), fetch=True)[0]
    names = {r['bl_ic_pk']: r['bl_line_name'] for r in c['db'].execute('SELECT bl_ic_pk, bl_line_name FROM bl_lines', fetch=True)}
    det = c['det']; fam = c['fam']

    def fmt(x):
        return (f"K len{x['k_len']} rsi{x['rsi_len']} stc{x['stc_len']} src={x['src']} {x['tf_seconds']}s"
                if x.get('kind') == 'k' else f"BB len{x['bb_len']} mult{x['bb_mult']} src={x['src']} {x['tf_seconds']}s")
    rows = [('breach (K)', BREACH, fam['k'])]
    if blr['bl_pk_ic_pk']:
        rows.append(('pk line (exit4)', names.get(blr['bl_pk_ic_pk'], '?'), det._cfg_dict(blr['bl_pk_ic_pk'])))
    if blr['bl_support_ic_pk']:
        rows.append(('support', names.get(blr['bl_support_ic_pk'], '?'), fam['exit_support']))
    if blr['bl_exit3_support_ic_pk']:
        rows.append(('exit3 support', names.get(blr['bl_exit3_support_ic_pk'], '?'), det._cfg_dict(blr['bl_exit3_support_ic_pk'])))
    nrow = len(rows) + 2
    tc = ['    table.cell(t,0,0,"champion line",text_color=color.white,bgcolor=color.new(color.gray,10),text_size=size.small)',
          '    table.cell(t,1,0,"name",text_color=color.white,bgcolor=color.new(color.gray,10),text_size=size.small)',
          '    table.cell(t,2,0,"apply on TV  (OOB 85/15)",text_color=color.white,bgcolor=color.new(color.gray,10),text_size=size.small)']
    for i, (role, nm, cc) in enumerate(rows):
        tc.append(f'    table.cell(t,0,{i+1},"{role}",text_color=color.silver,text_size=size.small)')
        tc.append(f'    table.cell(t,1,{i+1},"{nm}",text_color=color.yellow,text_size=size.small)')
        tc.append(f'    table.cell(t,2,{i+1},"{fmt(cc)}",text_color=color.aqua,text_size=size.small)')
    tc.append(f'    table.cell(t,0,{len(rows)+1},"exit_mask",text_color=color.silver,text_size=size.small)')
    tc.append(f'    table.cell(t,2,{len(rows)+1},"{CHAMP_MASK} = exit1+exit3 · lookback ±{CHAMP_LB}",text_color=color.aqua,text_size=size.small)')
    return dict(inp='showCfg  = input.bool(true, "champion table (top-right)")',
                decl=f'var table t = table.new(position.top_right, 3, {nrow}, border_width=1, frame_color=color.gray, frame_width=1)',
                render="if showCfg and barstate.islast\n" + '\n'.join(tc))


MODULES = {'walk': mod_walk, 'labels': mod_labels, 'exits': mod_exits, 'pk_raw': mod_pk_raw,
           'bias_reset_wp': mod_bias_reset_wp, 'bias_reset_wop': mod_bias_reset_wop,
           'cbls3_aligned': mod_cbls3_aligned, 'pk_aligned': mod_pk_aligned,
           's30m_entry': mod_s30m_entry, 'table': mod_table}


def emit(ctx, modules):
    parts = [MODULES[k](ctx) for k in modules]
    inputs = '\n'.join(p['inp'] for p in parts)
    align = ('alignWithP = input.bool(false, "align ◆+arrows+entries to WITH-p bias (else M-only)")\n'
             if any(m in modules for m in ('cbls3_aligned', 'pk_aligned', 's30m_entry')) else '')
    # Pine caps the MAIN BODY length → move each big array literal into a function (its body is
    # NOT main-body), leaving only a short `var x = arr_x()` assignment in the main body.
    import re
    funcs, assigns = [], []
    for p in parts:
        for line in p['decl'].split('\n'):
            m = re.match(r'(var (?:int|string)\[\]) (\w+) = (.+)$', line)
            if m:
                typ, name, expr = m.groups()
                funcs.append(f'arr_{name}() => {expr}')
                assigns.append(f'{typ} {name} = arr_{name}()')
            else:
                assigns.append(line)                                    # non-array decls (e.g. table.new)
    funcs_s = '\n'.join(funcs); assigns_s = '\n'.join(assigns)
    carry = ('var int cur = ' + str(ctx['st0']) + '\nvar int si = 0\nwhile si < array.size(stt)\n'
             '    if array.get(stt, si) > ms\n        break\n    cur := array.get(stv, si)\n    si += 1\n'
             if 'walk' in modules else '')
    renders = '\n'.join(p['render'] for p in parts)
    pine = f'''//@version=5
// champion recon (modular) — {', '.join(modules)}   |   {ctx['span']}  ({ctx['N']} bars)
indicator("champion recon {ctx['daytag']}", overlay=true, max_labels_count=500)
{align}{inputs}
{funcs_s}
ms = int(time)
{assigns_s}
{carry}{renders}
'''
    fn = f"/home/joe/thecodes/champion_recon_{ctx['daytag']}.pine"
    open(fn, 'w').write(pine)
    log.info(f"{fn}: {ctx['span']} · modules={modules} · c_bls:3 onsets {ctx['n_g3']} · "
             f"resets wp/wo {len(ctx['rwp_t'])}/{len(ctx['rwo_t'])} · diamonds wp/wo {len(ctx['dia_wp'])}/{len(ctx['dia_wo'])}")
    return dict(fn=fn, bytes=len(pine), maxarr=max(len(ctx[k]) for k in ('stt', 'dia_wp', 'dia_wo', 'pkal_wo_l', 'pkal_wo_s', 'rwo_t')))


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    hrs = int(sys.argv[sys.argv.index('--hours') + 1]) if '--hours' in sys.argv else 48
    modules = LEAN + (HEAVY if '--all' in sys.argv else [])
    modules = [m for m in MODULES if m in modules]                     # canonical order
    dmax = int(db.execute('SELECT MAX(kc_timestamp) m FROM kline_collection WHERE kc_tp_pk=1', fetch=True)[0]['m'])
    det = BLDetect(db, lookback_hours=hrs, warmup_hours=12)
    print(f'champion recon · last {hrs}h · modules={modules}', flush=True)
    ctx = build_ctx(det, db, dmax)
    r = emit(ctx, modules)
    print(f"  {ctx['span']} · {ctx['N']} bars · script {r['bytes']/1024:.0f} KB · largest array {r['maxarr']} elems", flush=True)
    print(f"  c_bls:3 onsets {ctx['n_g3']} · aligned ◆ wp/wo {len(ctx['dia_wp'])}/{len(ctx['dia_wo'])} · "
          f"resets wp/wo {len(ctx['rwp_t'])}/{len(ctx['rwo_t'])}", flush=True)
    db.disconnect()


if __name__ == '__main__':
    main()
