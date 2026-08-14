"""build_ws_fin_pine — the walk as a TradingView overlay.

Joe 0814: "red and green to show the g30_markers, and blue/yellow LABELS that land on the same bar
as the creation of a tagged group, and the label text will tell me when the handoff happens. add
any label notes you think are useful. keep the label tall and skinny".

  RED / GREEN   bar colour on every g30_marker signal. red = SHORT, green = LONG.
  BLUE / YELLOW label on every signal that created a tagged group, i.e. every BLOCKED signal.
                blue = SHORT, yellow = LONG — the same pair ws_strat_momo_landed.pine uses for
                side, so the colours mean the same thing across both charts.

The label carries BOTH handover rules, because they are the live A/B: 'first' is task 8, the race,
first past the post with the 22-27 restriction. 'median' is task 9, one watched line, the median of
the tagged group re-derived every bar.

Reads ws_fin_9of12 and ws_fin_tagshrink. Writes ws_fin_walk.pine at the repo root.
"""
import sys
import datetime as dt
from datetime import timezone

from optimus9.config import get_db_config
from optimus9 import DatabaseManager

OUT = 'ws_fin_walk.pine'
# THE WALK TO DRAW, by its full identity. Anything left out here silently unions several walks —
# ws_fin_9of12 now holds six of them.
WIN_FROM  = '2026-08-04 00:00:00'
G30_LEVEL = 'g30_marker'
WSF_N     = 9               # votes needed, of 12
HANDICAP  = 0               # WSF_HANDICAP, points off the boundary for the six gcws b/m/Mage lines
LINE_HCAP = 'ws1b:1'        # WSF_LINE_HANDICAP, per line. ws1b votes at 84 / 16
LINE_XWOB = 'ws1Mage:1,ws1b:1'   # WSF_LINE_XWOB, bars ws1Mage / ws1b hold before voting
HI, LO    = 85, 15          # the fence
STALL_N   = 6               # lattice samples with no new extreme
BUCKET_MS = 60000           # TF1 pane. The 5 s signal bar is floored to its minute.


def u(ms):
    return dt.datetime.fromtimestamp(int(ms) / 1000, tz=timezone.utc).strftime('%H:%M:%S')


def main():
    db = DatabaseManager(**get_db_config()); db.connect()
    q = ("SELECT wsf_ms,wsf_utc,wsf_side,wsf_domtf,wsf_domtf_tfs,wsf_ho_utc,wsf_ho_min,"
         "wsf_ho_tf,wsf_ho_how,wsf_ho_pool,wsf_win_from,wsf_win_to "
         "FROM ws_fin_9of12 WHERE wsf_win_from=%s AND wsf_g30_level=%s AND wsf_n=%s "
         "AND wsf_handicap=%s AND wsf_line_hcap=%s AND wsf_line_xwob=%s AND wsf_hi=%s "
         "AND wsf_lo=%s AND wsf_stall_n=%s AND wsf_ho_rule=%s ORDER BY wsf_ms")
    ident = (WIN_FROM, G30_LEVEL, WSF_N, HANDICAP, LINE_HCAP, LINE_XWOB, HI, LO, STALL_N)
    F = {r['wsf_ms']: r for r in db.execute(q, ident + ('first',), fetch=True)}
    M = {r['wsf_ms']: r for r in db.execute(q, ident + ('median',), fetch=True)}
    if not F or not M:
        print('both walks must exist. run build_ws_fin.py at each HANDOVER_RULE first.')
        return 1
    LV = {}
    for r in db.execute("SELECT wfs_signal,wfs_tf FROM ws_fin_tagshrink WHERE wfs_ho_rule='median' "
                        "AND wfs_stall_n=%s AND wfs_signal >= %s", (STALL_N, WIN_FROM), fetch=True):
        LV.setdefault(r['wfs_signal'], set()).add(int(r['wfs_tf']))
    a = list(F.values())[0]; win = (a['wsf_win_from'], a['wsf_win_to'])
    db.disconnect()

    hi_ms, lo_ms, labels = [], [], []
    for ms, x in F.items():
        b = (int(ms) // BUCKET_MS) * BUCKET_MS
        # side +1 = 9+ of 12 lines OOB-HIGH = SHORT -> hi_ms -> RED.  side -1 -> lo_ms -> GREEN.
        # BUG FIXED 0814: this line had the two arrays the wrong way round, so the chart painted
        # SHORT green and LONG red while the header and the toggles said the opposite.
        (hi_ms if x['wsf_side'] > 0 else lo_ms).append(b)
        if x['wsf_domtf'] != 'BLOCKED':
            continue
        y = M[ms]
        # Joe 0814: "less lines, wider x1.7, delete the group data, keep the TF that created the
        # handoff". One row per rule: the bar, the line that created it, which test, the wait.
        def row(tag, r):
            if not r['wsf_ho_utc']:
                return f'{tag} never fires'
            return (f"{tag} {r['wsf_ho_utc'][11:]} ws{r['wsf_ho_tf']}r "
                    f"{r['wsf_ho_how']} +{r['wsf_ho_min']:.0f}m")
        txt = '\n'.join([f"{x['wsf_utc'][11:]}  {'SHORT' if x['wsf_side'] > 0 else 'LONG'}",
                         row('first ', x), row('median', y)])
        labels.append((b, x['wsf_side'], txt))

    # 105 signals land on 104 chart minutes: 10:22:35 and 10:22:55 share one. Both are SHORT and
    # both are FREE, so nothing is lost — but a future window could collide across sides, and the
    # red/green paint has one colour per bar. Report it rather than let it pass silently.
    n_sig = len(F)
    hi_ms = sorted(set(hi_ms)); lo_ms = sorted(set(lo_ms))
    clash = sorted(set(hi_ms) & set(lo_ms))
    if clash:
        print(f'  WARNING {len(clash)} chart minutes hold BOTH sides: '
              + ', '.join(u(b) for b in clash))
    if len(hi_ms) + len(lo_ms) - len(clash) != n_sig:
        print(f'  {n_sig} signals -> {len(hi_ms) + len(lo_ms) - len(clash)} painted minutes '
              f'({n_sig - len(hi_ms) - len(lo_ms) + len(clash)} share a minute with another '
              f'signal of the same side)')
    # a minute can hold more than one 5 s signal. Merge their labels so nothing is dropped.
    merged = {}
    for b, sd, txt in labels:
        merged.setdefault(b, []).append((sd, txt))
    lb = sorted((b, v[0][0], '\n- - -\n'.join(t for _, t in v)) for b, v in merged.items())

    L = []
    L.append('//@version=5')
    L.append('// ws_fin_walk  —  the g30_marker signals and the domTF handover, 08-04')
    L.append('//')
    L.append(f"//   RED     bar   side SHORT, 9+ of 12 lines OOB-HIGH     {len(hi_ms)} bars")
    L.append(f"//   GREEN   bar   side LONG,  9+ of 12 lines OOB-LOW      {len(lo_ms)} bars")
    L.append(f"//   BLUE    label a tagged group was created, side SHORT")
    L.append(f"//   YELLOW  label a tagged group was created, side LONG   {len(lb)} labels total")
    L.append('//')
    L.append('//   a label lands on the bar the group was created — the signal bar of a BLOCKED')
    L.append('//   signal. A FREE signal has no group and gets no label.')
    L.append('//')
    L.append('//   label lines, top to bottom')
    L.append('//     the signal time and its side')
    L.append('//     first   task 8. the race, first past the post, 22-27 restriction live')
    L.append('//     median  task 9. the median of the group, re-derived every bar, whole group')
    L.append('//     each rule reads  the handover bar / the line that created it /')
    L.append('//                      cross or stall / minutes waited since the signal')
    L.append('//')
    L.append(f'//   KNOBS   STALL_N {STALL_N}   HANDOVER_XWOB 4   CURL_RECENCY_TF_BARS 2')
    L.append(f'//           DOMTF 13-27   DOMTF_HTF_BAND 22-27   {WSF_N} of 12 lines   '
             f'hi {HI} / lo {LO}   WSF_HANDICAP {HANDICAP}')
    L.append(f'//           WSF_LINE_HANDICAP {LINE_HCAP}      WSF_LINE_XWOB {LINE_XWOB}')
    L.append(f'//   window  {win[0]} -> {win[1]}      pxs grid 5s      BUCKET_MS {BUCKET_MS}')
    L.append('//   source  ws_fin_9of12 / ws_fin_tagshrink, wsf_g30_level=g30_marker')
    L.append('')
    L.append('indicator("ws_fin_walk — g30_markers + domTF handover", overlay = true, '
             'max_labels_count = 500)')
    L.append('show_hi = input.bool(true, "g30_marker SHORT (red)")')
    L.append('show_lo = input.bool(true, "g30_marker LONG (green)")')
    L.append('show_lb = input.bool(true, "tagged group labels (blue/yellow)")')
    L.append('lb_size = input.string("small", "label size", options = ["tiny","small","normal"])')
    L.append('')
    L.append(f'f_hi() =>\n    array.from({", ".join(str(v) for v in hi_ms)})')
    L.append(f'f_lo() =>\n    array.from({", ".join(str(v) for v in lo_ms)})')
    L.append('g30_hi = f_hi()')
    L.append('g30_lo = f_lo()')
    L.append('')
    L.append(f'f_lb_t() =>\n    array.from({", ".join(str(b) for b, _, _ in lb)})')
    L.append(f'f_lb_s() =>\n    array.from({", ".join(str(int(s)) for _, s, _ in lb)})')
    L.append('f_lb_x() =>')
    L.append('    array.from(' + ', '.join(
        '"' + t.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n') + '"'
        for _, _, t in lb) + ')')
    L.append('lb_t = f_lb_t()')
    L.append('lb_s = f_lb_s()')
    L.append('lb_x = f_lb_x()')
    L.append('')
    L.append('bg = color(na)')
    L.append('if show_hi and array.binary_search(g30_hi, time) >= 0')
    L.append('    bg := color.new(color.red, 0)')
    L.append('if show_lo and array.binary_search(g30_lo, time) >= 0')
    L.append('    bg := color.new(color.green, 0)')
    L.append('bgcolor(bg)')
    L.append('')
    L.append('sz = lb_size == "tiny" ? size.tiny : lb_size == "normal" ? size.normal : size.small')
    L.append('i = array.binary_search(lb_t, time)')
    L.append('if show_lb and i >= 0')
    L.append('    sd = array.get(lb_s, i)')
    L.append('    label.new(bar_index, high, array.get(lb_x, i),')
    L.append('       style = label.style_label_down, textalign = text.align_left, size = sz,')
    L.append('       color = color.new(sd > 0 ? color.blue : color.yellow, 15),')
    L.append('       textcolor = sd > 0 ? color.white : color.black)')
    open(OUT, 'w').write('\n'.join(L) + '\n')
    print(f'{OUT}: {len(hi_ms)} red bars, {len(lo_ms)} green bars, {len(lb)} labels')
    return 0


if __name__ == '__main__':
    sys.exit(main())
