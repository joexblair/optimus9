"""THE r-pred WEB UI. Joe 1109: *"I want to access this -1/+1 r-pred data in a dhtml webUI"*.

HIS SPEC, 1109:
    the rows      *"the data will be anchored on closed-prev ws1 bars"* - one row per ws1 bar
    the cells     *"the r-pred data will be emerging based"* - predict_breach on EMERGING r, m and Mage
    the box       15 columns: the ws1 time, then one per wsf line, *"wsf = gcws15 to ws12"*. -1 and +1
                  are coloured, the headers are fixed, the rows update as the mouse wheel scrolls
    the cache     *"an ever-evolving cache of the rpred data, so that a) we don't bog the ui down with too
                  much data at once, and 2) so that the data is available immediately"*
    the calendar  *"click on any day, and scroll from the beginning of the day that I click on"*

HIS ANSWERS, 1109:
    the row time  the ws1 bar's OPEN - the 00:12 row is the bar 00:12:00 .. 00:12:55
    the cell      the emerging value at the 5 s bar where closed-prev first shows that ws1 bar, 00:13:00
                  for the 00:12 row
    the colours   -1 red, +1 green
    the days      the fixed tape

HIS 1109 ADDITION, two columns on the right:
    *"col1: the sum of the r-pred decisions from ws13 to ws20"* / *"col2: the same for ws21 to ws30"*, read
    the same way as every other cell. *"for these 2 columns only, the coloring is red for <0, green for >0
    and orange for 0"*.

A MISSING INPUT READS 0. predict_breach returns 0 when r, m or Mage is NaN - every line's warm-up at the
tape's start (ws30 runs to 2026-07-03 06:28:00) and 3 rows where m is NaN mid-tape. That is the producer's
own output, shown as it comes. HIS 1109 ANSWER: keep 0 - no mark, and the sums count them as 0.

THE SIDE RADIO IS NOT BUILT. He asked for it only *"if the side is required"*; predict_breach returns
+1 (high) and -1 (low) in one read, so both print at once.

THE CACHE, two halves:
    the server    computes the whole matrix once at start, ~2 s, and holds it in memory - no disk cache,
                  so a line rebuild can never be served stale. 136,079 rows x 14 lines, int8.
    the browser   fetches BLOCK rows at a time, prefetches AHEAD blocks in the scroll direction (and
                  one behind), and drops the least recently used blocks past KEEP. Only the rows on
                  screen are in the page. A calendar day prefetches its blocks when the pointer is over it.

THE LAST ws1 BAR ON THE TAPE HAS NO ROW: its print bar, the 5 s bar after it, is past the tape's end.

HIS 1109 TOWARDS/AWAY, baked in: *"the output of towards/away will be baked into the r-pred webUI. for each row,
for each field, print TO or AW below the number, in a bold font."* and *"use a slighty lower font (eg the same size
as the weekdays above the calenders) for the summary ws13 and ws21 fields, print this "TO:x  AW:x"*. The states
come from ../../1109_towards_away/towards_away.py, read at the SAME print bar as the r-pred cell above them. Only
ws4..ws30 carry a state (his answer 10A), so gcws15, gcws30 and ws1..ws3 print no TO/AW. A row before the first
pseudo trade opens has no target-side, so it prints none either.

HIS 1109 ROUNDS 2 AND 3: TO/AW at 10 px like the sum labels; the time cell 20% red for a LOW target-side and 20% green
for HIGH; *"append `(inf)` or `(exf)` to the `TO` and `AW` labels (example "TO(exf)") to denote if a line is infence
or exfence"* - ex-20/80 on the target-side by the banked reader the towards/away mech uses. The build notes are
section 7 of docs/octo-freedom/1109_towards_away.md.

usage: rpred_ui.py [port]   then open http://127.0.0.1:<port>
"""
import io
import json
import os
import sys
import time

import numpy as np

V4 = '/home/joe/thecodes/docs/octo-freedom/1022_v4'
sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, V4)
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
os.chdir(V4)                                    # the tape is cwd-sensitive - every run prints its bar count
_e = sys.stderr; sys.stderr = io.StringIO()
try:
    import v4_rcfg_sweep as RS
    import v4_live_lines as LL
    import ln
    from optimus9.compute.breaching_line import predict_breach, HI, LO, FENCE_HI, FENCE_LO
    sys.path.insert(0, os.path.join(os.path.dirname(V4), '1109_towards_away'))
    import towards_away as TA
finally:
    sys.stderr = _e
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8788
LINES = ['gcws15', 'gcws30'] + ['ws%d' % t for t in range(1, 13)]      # HIS 1109 wsf
SUMS = [('ws13-ws20 sum', range(13, 21)), ('ws21-ws30 sum', range(21, 31))]   # HIS 1109 two right columns
CONTROL_FLAGGED = 257295        # 1109 measurement: the 14 wsf columns' cells at -1 or +1, whole tape
STRIDE = len(LINES) + len(SUMS) + len(LINES) + 2 * len(SUMS) + 1   # bytes per row: r-pred, the TO/AW codes, the
#   TO/AW counts, then the pseudo trade's target-side at the row's read bar: -1 LOW, +1 HIGH, 0 no trade


def build():
    """-> (row open ms [n], [n, 14 + 2] int8: r-pred per wsf line, then the two sums). Row i is the ws1
    bar opening at t0 + 60 s * i."""
    ts = np.asarray(ln.ts, np.int64)
    assert (np.diff(ts) == 5000).all(), 'the 5 s grid has a gap - a row would not be one ws1 bar'
    E = RS.load((RS.K0, RS.R0, RS.S0))           # fdm2's emerging r lines, ws1..ws30

    def rpred(name):
        if name.startswith('gc'):                # ln.line multiplies the digits by 60, so the sub-minute lines
            r, m, M = (np.asarray(LL.sub_line(name + s), float) for s in ('r', 'm', 'Mage'))
        else:
            r = np.asarray(E[int(name[2:])], float)
            #   CONTROL: fdm2's r is the stored ws r line, exactly
            assert np.array_equal(r, np.asarray(ln.line(name + 'r'), float), equal_nan=True), name
            m, M = np.asarray(ln.line(name + 'm'), float), np.asarray(ln.line(name + 'Mage'), float)
        return predict_breach(r, m, M)

    first = np.flatnonzero((ts % 60000) == 0)    # each ws1 bar's first 5 s bar
    first = first[first + 12 < ln.N]             # its print bar, 12 five-second bars on, must be on the tape
    assert (np.diff(ts[first]) == 60000).all(), 'a ws1 bar is missing - row i would not be t0 + 60 s * i'
    prt = first + 12                             # HIS ANSWER: the cell is the value where closed-prev shows it
    assert (ts[prt] - ts[first] == 60000).all()
    cols = [rpred(name)[prt] for name in LINES]
    for _, tfs in SUMS:                          # the same read, summed: -8..+8 and -10..+10, fits int8
        cols.append(np.sum([rpred('ws%d' % t)[prt].astype(int) for t in tfs], 0))
    #   TOWARDS/AWAY at the same print bar: 0 no state, 1 TO, 2 AW, and +2 when the line is ex-20/80 on the
    #   target-side there - 3 TO(exf), 4 AW(exf). Then per sum column the TO count and the AW count over its
    #   lines, both -1 where no pseudo trade is open (no target-side, so nothing to count)
    LN, piv, trades, ST, det = TA.build()
    print('towards/away: %d ws2Mage pivots, %d pseudo trades, first opens %s'
          % (len(piv), len(trades), ln.U(trades[0][0])))
    side = np.zeros(ln.N, np.int8)
    for o, c, s in trades:
        side[o:c] = s
    live = side != 0
    sp = side[prt]
    for name in LINES:
        t = int(name[2:]) if name.startswith('ws') else 0
        if t not in ST:
            cols.append(np.zeros(len(prt), np.int8))
            continue
        #   HIS 1109 *"append `(inf)` or `(exf)`"*: ex-20/80 on the target-side by the banked reader - the
        #   one the towards/away mech's own ex-fence test uses (closed-prev, or the emerging 60 s extreme)
        exf = np.where(sp > 0, TA.exf_mask(LN, t, +1)[prt], TA.exf_mask(LN, t, -1)[prt]) & (sp != 0)
        st = ST[t][prt].astype(np.int8)
        cols.append(np.where((st != TA.NONE) & exf, st + 2, st))
    for _, tfs in SUMS:
        for code in (TA.TO, TA.AW):
            n = np.sum([(ST[t][prt] == code).astype(int) for t in tfs], 0)
            cols.append(np.where(live[prt], n, -1))
    cols.append(side[prt])                       # HIS 1109: the time cell's 20% colour, red LOW, green HIGH
    return ts[first], np.ascontiguousarray(np.stack(cols, 1).astype(np.int8)), ln.U(trades[0][0])


T0 = time.time()
OPEN, RP, TA_FIRST = build()
assert RP.shape[1] == STRIDE
DAYS = []
for i, ms in enumerate(OPEN):
    d = time.strftime('%Y-%m-%d', time.gmtime(int(ms) // 1000))
    if not DAYS or DAYS[-1][0] != d:
        DAYS.append([d, i])
FLAGGED = int((RP[:, :len(LINES)] != 0).sum())
TAC = RP[:, len(LINES) + len(SUMS):2 * len(LINES) + len(SUMS)]
U = lambda ms: time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(ms) // 1000))
META = json.dumps({
    'lines': LINES, 'sums': [s for s, _ in SUMS], 'stride': STRIDE, 'rows': int(len(OPEN)), 't0': int(OPEN[0]), 'step': 60000,
    'days': DAYS,
    'legend': [
        ['a row', 'one ws1 bar, timed at its open (UTC)'],
        ['a cell', 'emerging r-pred at the 5 s bar where closed-prev first shows that ws1 bar: the row time + 60 s'],
        ['-1 red', 'a low breach predicted: %g < r <= %g, the lower of m and Mage at or below %g, and its '
                   'overshoot past %g bigger than r\'s distance to %g' % (LO, FENCE_LO, LO, LO, LO)],
        ['+1 green', 'a high breach predicted: %g <= r < %g, the higher of m and Mage at or above %g, and its '
                     'overshoot past %g bigger than r\'s distance to %g' % (FENCE_HI, HI, HI, HI, HI)],
        ['0', 'neither'],
        ['the 2 sums', 'the same r-pred read added up over ws13..ws20 (-8 to +8) and ws21..ws30 (-10 to +10). '
                       'Red below 0, green above 0, orange at 0'],
        ['(inf) / (exf)', 'after TO or AW: the r line is in-fence or ex-20/80 on the target-side at that bar, by '
                          'the banked ex-20/80 reader the towards/away mech itself uses - closed-prev, or the '
                          'emerging extreme of the 60 s to that bar'],
        ['TO / AW', 'under each number: the new towards/away state of that r line, TO towards, AW away, at the '
                    'same 5 s bar as the r-pred cell. The target-side comes from the pseudo trade open at that bar: '
                    'the ws2Mage pivots, the last of each same-side run'],
        ['the time cell colour', 'the pseudo trade\'s target-side at the row\'s read bar, 20% opaque: red LOW, '
                                 'green HIGH. A trade opens on the first row of a new colour, and every line reads TO '
                                 'there'],
        ['TO:x  AW:x', 'under each sum: how many of its lines read TO and how many AW. A line with no r value counts '
                       'in neither'],
        ['no TO / AW', 'gcws15, gcws30 and ws1..ws3 are not in the towards/away lines (ws4..ws30). Rows before the '
                       'first pseudo trade opens, %s, have no target-side' % TA_FIRST],
        ['a missing input', 'r-pred reads 0 when r, m or Mage has no value: each line\'s warm-up at the tape\'s '
                            'start, to 2026-07-03 06:28:00 on ws30, and 3 rows where m has none'],
        ['the rows', '%s .. %s, %d ws1 bars. The tape\'s last ws1 bar has no 5 s bar after it, so no row'
                     % (U(OPEN[0]), U(OPEN[-1]), len(OPEN))],
    ]})


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, body, kind):
        self.send_response(200)
        self.send_header('Content-Type', kind)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.startswith('/meta'):
            return self._send(META.encode(), 'application/json')
        if self.path.startswith('/rows'):
            q = dict(kv.split('=') for kv in self.path.split('?', 1)[1].split('&'))
            a = max(0, int(q['start'])); b = min(len(RP), a + max(0, int(q['count'])))
            return self._send(RP[a:b].tobytes(), 'application/octet-stream')    # STRIDE bytes per row
        return self._send(PAGE.encode(), 'text/html; charset=utf-8')


PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>r-pred wsf</title>
<style>
:root{--bg:#ffffff;--fg:#1d1d1f;--mut:#6e6e73;--line:#dcdce0;--hd:#f1f1f4;--zebra:#fafafb;--red:#d93025;--grn:#1e8e3e;
  --on:#ffffff;--sel:#1a73e8;--dis:#c4c4c8;--org:#d9650b;
  --redA:color-mix(in srgb,var(--red) 20%,transparent);--grnA:color-mix(in srgb,var(--grn) 20%,transparent)}
@media (prefers-color-scheme: dark){:root{--bg:#141416;--fg:#e8e8ea;--mut:#9a9aa0;--line:#2e2e33;--hd:#1e1e22;
  --zebra:#18181b;--red:#e5483b;--grn:#2ea44f;--on:#ffffff;--sel:#8ab4f8;--dis:#4a4a50;--org:#e8710a}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:13px/1.4 system-ui,-apple-system,Segoe UI,sans-serif}
.wrap{max-width:1420px;margin:0 auto;padding:12px 16px 24px}
h1{font-size:15px;margin:0 0 8px;font-weight:600}
.cal{display:flex;gap:18px;flex-wrap:wrap;margin-bottom:10px}
.mon{min-width:200px}
.mon b{display:block;font-size:12px;margin-bottom:3px}
.grid{display:grid;grid-template-columns:repeat(7,26px);gap:2px}
.grid span{font-size:10px;color:var(--mut);text-align:center}
.grid button{height:22px;border:1px solid var(--line);background:var(--bg);color:var(--fg);border-radius:4px;
  font:11px system-ui,sans-serif;cursor:pointer;padding:0}
.grid button:hover{border-color:var(--sel)}
.grid button:disabled{color:var(--dis);border-color:transparent;cursor:default}
.grid button.on{background:var(--sel);border-color:var(--sel);color:var(--bg);font-weight:600}
.status{display:flex;gap:18px;color:var(--mut);font-size:12px;margin:4px 0 6px;font-variant-numeric:tabular-nums}
.box{height:68vh;min-height:320px;border:1px solid var(--line);border-radius:6px;overflow:auto;position:relative;overflow-anchor:none}
.inner{min-width:1200px}
.hd,.row{display:grid;grid-template-columns:150px repeat(14,minmax(54px,1fr)) repeat(2,minmax(104px,1.4fr));height:24px;align-items:center}
.row{height:38px}
.hd{position:sticky;top:0;z-index:2;background:var(--hd);border-bottom:1px solid var(--line);font-weight:600}
.hd div{text-align:center;font-size:12px}
.hd div:first-child,.row .t{text-align:left;padding-left:8px}
.body{position:relative}
.row{position:absolute;left:0;right:0;top:0;font-variant-numeric:tabular-nums;border-bottom:1px solid var(--line)}
.row.z{background:var(--zebra)}
.row div{text-align:center;height:37px;display:flex;flex-direction:column;justify-content:center;line-height:16px}
.row .t{display:block;line-height:37px}
.row div b{font-weight:700;font-size:10px}
.row div b.s{white-space:pre}
.row .t.lo{background:var(--redA)}
.row .t.hi{background:var(--grnA)}
.row .t{color:var(--fg);white-space:nowrap}
.row .m{background:var(--red);color:var(--on);font-weight:600}
.row .p{background:var(--grn);color:var(--on);font-weight:600}
.row .w{color:var(--dis)}
.row .zr{color:var(--mut)}
.row .o{background:var(--org);color:var(--on);font-weight:600}
.hd .sx,.row .sx{border-left:2px solid var(--mut)}
table.leg{border-collapse:collapse;margin-top:12px;font-size:12px}
table.leg td{border:1px solid var(--line);padding:3px 8px;vertical-align:top}
table.leg td:first-child{white-space:nowrap;font-weight:600}
</style></head><body><div class="wrap">
<h1>r-pred, wsf gcws15 to ws12 plus the ws13-ws20 and ws21-ws30 sums, emerging, on closed-prev ws1 bars, with towards/away</h1>
<div class="cal" id="cal"></div>
<div class="status"><span id="top">top row: -</span><span id="held">cache: -</span><span id="err"></span></div>
<div class="box" id="box"><div class="inner"><div class="hd" id="hd"></div><div class="body" id="body"></div></div></div>
<table class="leg" id="leg"></table>
</div><script>
const RH = 38;          // row height, px - two lines: the number, then TO / AW
const BLOCK = 720;      // rows per fetch: 12 h of ws1 bars
const AHEAD = 3;        // blocks prefetched in the scroll direction
const KEEP = 60;        // blocks held before the least recently used is dropped
let meta, NL, NC, NS;
const cache = new Map(), pending = new Set();
const box = document.getElementById('box'), body = document.getElementById('body');
const pool = [];
let lastTop = 0, dir = 1, raf = 0, dayOn = '';

const fmt = ms => new Date(ms).toISOString().slice(0, 19).replace('T', ' ');

function fetchBlock(b) {
  if (b < 0 || b * BLOCK >= meta.rows || cache.has(b) || pending.has(b)) return;
  pending.add(b);
  fetch('rows?start=' + (b * BLOCK) + '&count=' + BLOCK)
    .then(r => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.arrayBuffer(); })
    .then(buf => { pending.delete(b); cache.set(b, new Int8Array(buf)); evict(); schedule(); })
    .catch(e => { pending.delete(b); document.getElementById('err').textContent = 'fetch failed: ' + e.message; });
}
function getBlock(b) {
  const a = cache.get(b);
  if (a) { cache.delete(b); cache.set(b, a); }   // most recently used goes to the back
  return a;
}
function evict() {
  while (cache.size > KEEP) cache.delete(cache.keys().next().value);
  document.getElementById('held').textContent = 'cache: ' + cache.size + ' blocks, ' +
    (cache.size * BLOCK).toLocaleString() + ' rows held of ' + meta.rows.toLocaleString();
}
function prefetch(first, n) {
  const b0 = Math.floor(first / BLOCK), b1 = Math.floor((first + n) / BLOCK);
  for (let b = b0; b <= b1; b++) fetchBlock(b);
  for (let k = 1; k <= AHEAD; k++) fetchBlock(dir > 0 ? b1 + k : b0 - k);
  fetchBlock(dir > 0 ? b0 - 1 : b1 + 1);
}
function ensurePool(n) {
  while (pool.length < n) {
    const el = document.createElement('div'); el.className = 'row';
    const cells = [];
    for (let c = 0; c <= NC; c++) {
      const d = document.createElement('div'); d.className = c ? '' : 't'; el.appendChild(d);
      if (c) { d.n = document.createElement('span'); d.ta = document.createElement('b'); d.append(d.n, d.ta); if (c > NL) d.ta.className = 's'; }
      cells.push(d);
    }
    body.appendChild(el); pool.push({el, cells, i: -1, ok: false});
  }
}
function draw() {
  raf = 0;
  const top = box.scrollTop;
  dir = top >= lastTop ? 1 : -1; lastTop = top;
  const first = Math.max(0, Math.floor(top / RH));
  const n = Math.ceil(box.clientHeight / RH) + 2;
  ensurePool(n);
  prefetch(first, n);
  for (let k = 0; k < pool.length; k++) {
    const p = pool[k], i = first + k;
    if (k >= n || i >= meta.rows) { p.el.style.display = 'none'; p.i = -1; continue; }
    p.el.style.display = '';
    if (p.i === i && p.ok) continue;
    p.el.style.transform = 'translateY(' + (i * RH) + 'px)';
    p.el.className = 'row' + (i % 2 ? ' z' : '');
    p.cells[0].textContent = fmt(meta.t0 + i * meta.step);
    const blk = getBlock(Math.floor(i / BLOCK)), o = (i % BLOCK) * NS;
    const sd = blk ? blk[o + NS - 1] : 0;   // HIS 1109: the trade's target-side, 20% red LOW / green HIGH
    p.cells[0].className = 't' + (sd < 0 ? ' lo' : sd > 0 ? ' hi' : '');
    for (let c = 0; c < NC; c++) {
      const d = p.cells[c + 1], sx = c === NL ? ' sx' : '';
      if (!blk) { d.n.textContent = '·'; d.ta.textContent = ''; d.className = 'w' + sx; continue; }
      const v = blk[o + c];
      if (c < NL) {                     // a wsf line: -1 red, +1 green, 0 plain
        d.n.textContent = v === -1 ? '-1' : v === 1 ? '+1' : '0';
        d.className = v === -1 ? 'm' : v === 1 ? 'p' : 'zr';
        const s = blk[o + NC + c];      // HIS 1109: TO or AW below the number, bold
        d.ta.textContent = ['', 'TO(inf)', 'AW(inf)', 'TO(exf)', 'AW(exf)'][s] || '';   // HIS 1109 (inf) / (exf)
      } else {                          // a sum, HIS 1109: red below 0, green above 0, orange at 0
        d.n.textContent = v > 0 ? '+' + v : String(v);
        d.className = (v < 0 ? 'm' : v > 0 ? 'p' : 'o') + sx;
        const k = o + NC + NL + 2 * (c - NL), to = blk[k], aw = blk[k + 1];
        d.ta.textContent = to < 0 ? '' : 'TO:' + to + '  AW:' + aw;   // HIS "TO:x  AW:x", the weekday size
      }
    }
    p.i = i; p.ok = !!blk;
  }
  const t = meta.t0 + first * meta.step;
  document.getElementById('top').textContent = 'top row: ' + fmt(t);
  markDay(fmt(t).slice(0, 10));
}
function schedule() { if (!raf) raf = requestAnimationFrame(draw); }

function markDay(d) {
  if (d === dayOn) return;
  const old = document.querySelector('.grid button.on'); if (old) old.classList.remove('on');
  const b = document.querySelector('.grid button[data-d="' + d + '"]'); if (b) b.classList.add('on');
  dayOn = d;
}
function buildCal() {
  const rowOf = new Map(meta.days);
  const months = [...new Set(meta.days.map(d => d[0].slice(0, 7)))];
  const cal = document.getElementById('cal');
  for (const ym of months) {
    const [y, m] = ym.split('-').map(Number);
    const mon = document.createElement('div'); mon.className = 'mon';
    mon.innerHTML = '<b>' + new Date(Date.UTC(y, m - 1, 1)).toLocaleString('en', {month: 'long', timeZone: 'UTC'}) + ' ' + y + ' (UTC)</b>';
    const g = document.createElement('div'); g.className = 'grid';
    for (const w of ['Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa', 'Su']) { const s = document.createElement('span'); s.textContent = w; g.appendChild(s); }
    const lead = (new Date(Date.UTC(y, m - 1, 1)).getUTCDay() + 6) % 7;
    for (let k = 0; k < lead; k++) g.appendChild(document.createElement('span'));
    const nd = new Date(Date.UTC(y, m, 0)).getUTCDate();
    for (let d = 1; d <= nd; d++) {
      const key = ym + '-' + String(d).padStart(2, '0');
      const b = document.createElement('button'); b.textContent = d; b.dataset.d = key;
      if (!rowOf.has(key)) b.disabled = true;
      else {
        const r = rowOf.get(key);
        b.title = key + ' from ' + fmt(meta.t0 + r * meta.step);
        b.onmouseenter = () => { const b0 = Math.floor(r / BLOCK); fetchBlock(b0); fetchBlock(b0 + 1); fetchBlock(b0 + 2); };
        b.onclick = () => { dir = 1; box.scrollTop = r * RH; lastTop = box.scrollTop; draw(); };
      }
      g.appendChild(b);
    }
    mon.appendChild(g); cal.appendChild(mon);
  }
}
async function init() {
  meta = await (await fetch('meta')).json();
  NL = meta.lines.length; NC = NL + meta.sums.length; NS = meta.stride;
  const hd = document.getElementById('hd');
  for (const h of ['ws1 time (UTC)'].concat(meta.lines, meta.sums)) { const d = document.createElement('div'); d.textContent = h; hd.appendChild(d); }
  hd.children[NL + 1].className = 'sx';
  body.style.height = (meta.rows * RH) + 'px';
  const leg = document.getElementById('leg');
  for (const [k, v] of meta.legend) { const tr = leg.insertRow(); tr.insertCell().textContent = k; tr.insertCell().textContent = v; }
  buildCal();
  box.addEventListener('scroll', schedule, {passive: true});
  window.addEventListener('resize', schedule);
  evict();
  schedule();
}
init().catch(e => { document.getElementById('err').textContent = 'load failed: ' + e.message; });
</script></body></html>
"""


if __name__ == '__main__':
    print('bars %d, %s .. %s' % (ln.N, ln.U(0), ln.U(ln.N - 1)))
    print('rows %d, %s .. %s, built in %.1f s' % (len(OPEN), U(OPEN[0]), U(OPEN[-1]), time.time() - T0))
    print('CONTROL flagged cells %d, 1109 measurement %d: %s'
          % (FLAGGED, CONTROL_FLAGGED, 'MATCH' if FLAGGED == CONTROL_FLAGGED else 'DIFFERS'))
    for k, (label, _) in enumerate(SUMS):
        v = RP[:, len(LINES) + k].astype(int)
        print('%s: below 0 %d, at 0 %d, above 0 %d, min %d, max %d'
              % (label, (v < 0).sum(), (v == 0).sum(), (v > 0).sum(), v.min(), v.max()))
    print('towards/away cells: TO(inf) %d, AW(inf) %d, TO(exf) %d, AW(exf) %d, none %d'
          % tuple((TAC == k).sum() for k in (1, 2, 3, 4, 0)))
    print('towards/away knobs (banked): ' + ' '.join('%s=%s' % (k, v) for k, v, _, _ in TA.KNOBS))
    print('open http://127.0.0.1:%d' % PORT)
    sys.stdout.flush()
    ThreadingHTTPServer(('127.0.0.1', PORT), H).serve_forever()
