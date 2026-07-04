"""
lp_cascade_emit.py (Joe 0704) — modular pine for the lp-cascade (v2), built for a 5s chart. Built on the
cf15 4-bgcolor scheme + a new symbols module. Two modules (toggled by input), fixed ORDER:

  ① trades  — 4-bgcolor trade OUTCOME (cf15 scheme): WON(mfe>=WON_T & mae<=MAE_L) green/red long/short ·
              RISKY(mae>MAE_L, priority) yellow/blue long/short.  Off finisher_v2(gcs5M) + lr_walk.
  ② events  — SYMBOLS over the cascade events (plotchar, uncapped): arm ▲/▼ · gate a/b/c · s15a ● · s30a ■ ·
              gcs5 entry ★ · stale ✕.  + a KEY table (top-right).

Trades placed WITHOUT bias (spec step 5). Trigger line = gcs5M (data). Window default = week starting 06-16.
Symbols/bgcolor match on exact 5s bar time (binary_search over sorted arrays) — load on a 5s chart.
  python3 lp_cascade_emit.py
"""
import sys; sys.path.insert(0, '/home/joe/thecodes')
import datetime as dtm; from datetime import timezone
import bias_machine as bm
from optimus9.analysis.lr import lr_config, lr_walk
from optimus9.analysis import lr_v2 as L
from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from sweep_eval import BASE_BIAS

WON_T, MAE_L, TRIG = 0.7, 0.5, 'gcs5M'
def ms(s): return int(dtm.datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp() * 1000)
def d5(t): return dtm.datetime.fromtimestamp(t / 1000, timezone.utc).strftime('%m-%d')
R0, R1 = ms('2026-06-16 00:00'), ms('2026-06-23 00:00')   # week starting 06-16

db = DatabaseManager(**get_db_config()); db.connect(); ls = bm.LineStore(db); cfg = bm.BiasConfig(**BASE_BIAS); lr = lr_config(db)
SPEC = {'s2m': (6, 0.56, 'close'), 's2M': (37, 0.72, 'hlcc4'), 's3m': (6, 0.56, 'close'), 's3M': (37, 0.72, 'ohlc4'),
        's4m': (6, 0.56, 'close'), 's4M': (37, 0.72, 'ohlc4'), 's5m': (8, 0.40, 'ohlc4'), 's5M': (37, 0.83, 'ohlc4'),
        's7m': (10, 0.77, 'ohlc4'), 's7M': (37, 0.83, 'ohlc4'), 's15m': (7, 0.74, 'hlcc4'), 's15M': (37, 0.83, 'ohlc4'),
        's30m': (10, 0.60, 'hlc3'), 's30M': (37, 0.83, 'ohlc4')}   # m-lines len 6 (s5m=8, protects the arm timing)
ovr = {ln: (ls.resolve(ln)[0], ('bb', a, b, c), 'emerging') for ln, (a, b, c) in SPEC.items()}
ovr['s2M'] = (60, ('bb', 37, 0.72, 'hlcc4'), 'emerging')   # s15r/s30r/gcs5M from the DB (correct configs)
# ── in-use line configs → pine remarks (Joe 0704: store the config in the script) ──
def _cfgline(ln):
    (tf, c, vm) = ovr[ln] if ln in ovr else (ls.resolve(ln) + (ls.value_mode(ln),))
    desc = ('bb %s·%s·%s' % (c[1], c[2], c[3])) if c[0] == 'bb' else ('k %s·%s·%s·%s' % (c[3], c[1], c[2], c[4]))
    return '// %-6s tf=%-5ss %-18s vm=%s' % (ln, tf, desc, vm)
CFG_LINES = ['s2m', 's2M', 's3m', 's3M', 's4m', 's4M', 's5m', 's5M', 's7m', 's7M',
             's15m', 's15M', 's15r', 's30m', 's30M', 's30r', 'gcs5M']
CFG_REMARKS = '\n'.join(_cfgline(ln) for ln in CFG_LINES)
FIN_REMARK = ('// finisher_v2: trig=%s mage_wob=%d s30M_oob=%d s15r_lb=%d s30r_lb=%d fin_lb=%d fin_fwd=%d '
              '· exit=lr_exit_v2(s7,predict=F)+strand_rescue · stop=%.2f%%' % (
                  TRIG, lr.fin_mage_wob, lr.fin_s30M_oob, lr.s15r_lb, lr.s30r_lb, lr.fin_lb, lr.fin_fwd, lr.sl))
W = bm.BiasWindow(db, R1, lookback=168, warmup=80, cfg=cfg, lean=True, line_overrides=ovr); W._line = W._line_emerging
ts = W.ts

# ── run the cascade, capturing every event bar ─────────────────────────────────────────────────────
setups = L.v2_arm(W, lr); sig = L.gate_signals(W, lr); opens = L.gate_open(W, lr, setups, sig)
q15h, q15l = L.s_qualify(W, lr, 's15m', 's15M', 's15r', lr.s15r_lb)
q30h, q30l = L.s_qualify(W, lr, 's30m', 's30M', 's30r', lr.s30r_lb)
revT = L._mage_rev(W.line(TRIG), lr.fin_mage_wob)
ev = {'armH': [], 'armL': [], 'gA': [], 'gB': [], 'gC': [], 's15a': [], 's30a': [], 'enL': [], 'enS': [], 'stale': []}
seen = set(); entries = []
for (i, es, bd, ok, reason, cap) in opens:
    (ev['armH'] if bd == -1 else ev['armL']).append(ts[i])         # bd -1 short ⇐ armed off a HI breach
    ev['g' + reason.upper()].append(ts[ok])
    qA, qB = (q15h, q30h) if es == 1 else (q15l, q30l)
    w0, w1 = max(0, ok - lr.fin_lb), min(cap, ok + lr.fin_fwd)
    j15 = next((k for k in range(w0, w1) if qA[k]), None); j30 = next((k for k in range(w0, w1) if qB[k]), None)
    if j15 is None or j30 is None:
        ev['stale'].append(ts[ok]); continue
    ev['s15a'].append(ts[j15]); ev['s30a'].append(ts[j30])
    tk = next((k for k in range(max(j15, j30), cap) if revT[k] == bd), None)
    if tk is None:
        ev['stale'].append(ts[ok]); continue
    if tk in seen:
        continue
    seen.add(tk); (ev['enL'] if bd == 1 else ev['enS']).append(ts[tk]); entries.append((int(ts[tk]), es, bd, tk))

# ── trade outcomes (4-bgcolor, cf15 scheme) ────────────────────────────────────────────────────────
tpairs, n_won, n_risky = [], 0, 0
for (tms, _dt, es, bd, mae, mfe, *_r) in lr_walk(W, entries, lr):
    if not (R0 <= tms < R1):
        continue
    if mae > MAE_L:
        c = 2 if bd == 1 else 3; n_risky += 1
    elif mfe >= WON_T:
        c = 0 if bd == 1 else 1; n_won += 1
    else:
        continue
    tpairs.append((int(tms), c))
tpairs.sort(); tct = [t for t, _ in tpairs]; tci = [c for _, c in tpairs]

def win(a): return sorted({int(t) for t in a if R0 <= t < R1})          # sorted+dedup (binary_search needs sorted)
E = {k: win(v) for k, v in ev.items()}
print('range %s→%s · trig=%s · trades %d (WON %d / RISKY %d) · arms %d · gates %d · entries %d · stale %d' % (
    d5(R0), d5(R1), TRIG, len(tct), n_won, n_risky, len(E['armH']) + len(E['armL']),
    len(E['gA']) + len(E['gB']) + len(E['gC']), len(E['enL']) + len(E['enS']), len(E['stale'])))

# ── emit (plotchar-based, no 500-label cap; binary_search exact-match on 5s time) ────────────────────
arr = lambda v: ('array.from(' + ', '.join(map(str, v)) + ')') if v else 'array.new_int(0)'
def pc(nm, ch, loc, col, sz='tiny', ttl=''):
    c = col if col.startswith('#') else 'color.' + col
    return ('plotchar(showEvents and array.binary_search(%s, time) >= 0, char="%s", location=location.%s, '
            'color=%s, size=size.%s, title="%s")' % (nm, ch, loc, c, sz, ttl))
ARRS = [('tct', tct), ('tci', tci), ('armL', E['armL']), ('armH', E['armH']),
        ('gA', E['gA']), ('gB', E['gB']), ('gC', E['gC']), ('s15', E['s15a']), ('s30', E['s30a']),
        ('enL', E['enL']), ('enS', E['enS']), ('stl', E['stale'])]
def emit_arr(nm, vals):
    """Wrap an array in a function (TV main-body op-limit fix). Chunk >400 into concat'd sub-functions."""
    if len(vals) <= 400:
        return 'f_%s() =>\n    %s' % (nm, arr(vals)), '%s = f_%s()' % (nm, nm)
    chunks = [vals[i:i + 400] for i in range(0, len(vals), 400)]
    d = '\n'.join('f_%s_%d() =>\n    %s' % (nm, i, arr(c)) for i, c in enumerate(chunks))
    d += '\nf_%s() =>\n    a = f_%s_0()\n' % (nm, nm)
    d += ''.join('    array.concat(a, f_%s_%d())\n' % (nm, i) for i in range(1, len(chunks)))
    d += '    a'
    return d, '%s = f_%s()' % (nm, nm)
_pairs = [emit_arr(nm, v) for nm, v in ARRS]
ARR_DEFS = '\n'.join(p[0] for p in _pairs); ARR_CALLS = '\n'.join(p[1] for p in _pairs)
body = f'''//@version=5
indicator("lp-cascade v2 ({d5(R0)}→{d5(R1)}) trig {TRIG}  ▲▼arm · abc gate · ●s15a ■s30a · ★entry · ✕stale", overlay = true)
showTrades = input.bool(true, "① trades (bgcolor)")
showEvents = input.bool(true, "② cascade events (symbols)")
showKey    = input.bool(true, "key table")
// ── in-use line configs (emerging/causal; overrides — DB alignment pending) ──
{CFG_REMARKS}
{FIN_REMARK}
// ── data arrays (wrapped in functions — TV main-body op-limit) ──
{ARR_DEFS}
{ARR_CALLS}
// ── MODULE 1: trades (4-bgcolor outcome) ──
bg = color(na)
if showTrades
    idx = array.binary_search(tct, time)
    if idx >= 0
        ci = array.get(tci, idx)
        bg := ci == 0 ? color.new(color.green, 0) : ci == 1 ? color.new(color.red, 0) : ci == 2 ? color.new(color.yellow, 0) : color.new(color.blue, 0)
bgcolor(bg)
// ── MODULE 2: cascade events (plotchar — uncapped) ──
{pc('armL', '▲', 'belowbar', 'lime', ttl='arm long')}
{pc('armH', '▼', 'abovebar', 'orange', ttl='arm short')}
{pc('gA', 'a', 'top', 'fuchsia', ttl='gate a')}
{pc('gB', 'b', 'top', 'fuchsia', ttl='gate b')}
{pc('gC', 'c', 'top', 'fuchsia', ttl='gate c')}
{pc('s15', '●', 'abovebar', 'aqua', ttl='s15a')}
{pc('s30', '■', 'abovebar', '#72bcf9', ttl='s30a')}
{pc('enL', '★', 'belowbar', 'yellow', 'small', 'entry long')}
{pc('enS', '★', 'abovebar', 'yellow', 'small', 'entry short')}
{pc('stl', '✕', 'bottom', 'gray', ttl='stale')}
// ── KEY table (top-right) ──
if showKey and barstate.islast
    var table k = table.new(position.top_right, 1, 10, border_width = 1)
    table.cell(k, 0, 0, "lp-cascade key", text_color = color.white, bgcolor = color.new(color.black, 0), text_size = size.small)
    rows = array.from("▲ arm long", "▼ arm short", "a/b/c gate open", "● s15a qualify", "■ s30a qualify", "★ entry ({TRIG})", "✕ stale / no-trade", "bg WON grn/red long/short", "bg RISKY ylw/blu long/short")
    cols = array.from(color.lime, color.orange, color.fuchsia, color.aqua, #72bcf9, color.yellow, color.gray, color.green, color.yellow)
    for i = 0 to 8
        table.cell(k, 0, i + 1, array.get(rows, i), text_color = array.get(cols, i), text_size = size.normal, text_halign = text.align_left)
'''
path = '/home/joe/thecodes/lp_cascade.pine'
open(path, 'w').write(body)
print('→ ' + path)
db.disconnect()
