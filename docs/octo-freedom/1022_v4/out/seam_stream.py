"""THE LIVE EVENT STREAM, IN A BROWSER. Joe 1026: *"I'd like to see the events live and as a stream
in a browser window, with the reversal events added to help understand the data flow. I need limited
data: ts, pxs, line, action, conditions (eg wob, etc)"*.

READ-ONLY. It opens claude-639244ab's running harness output and never writes to it:

    docs/octo-freedom/1026_live_seam/out/bars.jsonl    every 5 s bar: ts, utc, ohlcv, read A, read B
    docs/octo-freedom/1026_live_seam/out/events.jsonl  one line per firing
    docs/octo-freedom/1026_live_seam/out/meta.json     the run's own header

It lives in 1022_v4/out and not in their folder so a crash here cannot touch the perishable run.

FIVE COLUMNS, his: ts, pxs, line, action, conditions. Nothing else.

TWO ROW SOURCES.

    the harness's events     read straight from events.jsonl, one row each
    the emerging reversals   NOT in events.jsonl - he asked for them, so they are derived here from
                             the read-A series in bars.jsonl using the BANKED detector,
                             v4_fast.revs -> lift_off(line, side, LIFT_PTS, gap_for(tf), LIFT_TOL,
                             LIFT_WOB). No new reversal mech is written.

pxs IS THE PRODUCER, NOT A FORK: jig.px_smooth(ts, close, evt=volume>0, length=2, frac=12), which
is optimus9_system's own pxsmooth_dema_len 2 on the 5 s grid, with the filler-invisible event mask.

THE RAW BAR AND THE STAMP ARE BOTH SHOWN AND NEVER MERGED. v4_fast: *"the raw bar is the anchor and
the identity of the reversal"*; K.lift_stamp(b) = b + LIFT_WOB - 1 is when it becomes knowable.

A SLOW LINE CANNOT REVERSE EARLY, and that is not a bug: lift_off reads 6 samples spanning
(LIFT_PTS - 1) x gap_for(tf) bars, so ws12 needs 170 bars = 14 m 10 s of tape before its first
verdict exists. The header prints the span per line.

usage: seam_stream.py [port]   then open http://127.0.0.1:<port>
"""
import io
import json
import os
import sys
import datetime as dt
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import numpy as np

sys.path.insert(0, '/home/joe/thecodes')
sys.path.insert(0, '/home/joe/thecodes/docs/octo-freedom/1022_v4')
os.environ.setdefault('LG_TAPE_END', '2026-10-05')
_e = sys.stderr; sys.stderr = io.StringIO()
import v4_knobs as K
import v4_fast as F
from optimus9.analysis.jig import px_smooth
sys.stderr = _e

OUT = '/home/joe/thecodes/docs/octo-freedom/1026_live_seam/out'


def _run_dir():
    """The NEWEST run directory under out/, or out/ itself. -> a path.

    The harness moved to one directory per run (`run_YYYYmmdd_HHMMSS`) after its third start, and it
    has restarted three times already, so the path is resolved on EVERY poll rather than bound at
    import. A restart is then picked up without touching this server.
    """
    try:
        ds = sorted(d for d in os.listdir(OUT)
                    if d.startswith('run_') and os.path.isdir(os.path.join(OUT, d)))
    except OSError:
        ds = []
    for d in reversed(ds):                            # newest first, but only if it has bars yet
        p = os.path.join(OUT, d)
        if os.path.exists(os.path.join(p, 'bars.jsonl')):
            return p
    return OUT


def _paths():
    r = _run_dir()
    return (os.path.join(r, 'bars.jsonl'), os.path.join(r, 'events.jsonl'),
            os.path.join(r, 'meta.json'), os.path.join(r, 'seed.npz'), r)
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8787

_BAR = {}
EV_NAME = {1: 'ws1b oob -> ib', 2: 'baton', 3: 'Mage -> oob', 4: 'r -> oob'}
SIDE = {1: 'HIGH', -1: 'LOW'}
_STATE = {'bars': 0, 'events': 0, 'rows': [], 'revs': {}, 'pxs': {}, 'late': [],
          'seed': None, 'seed_mtime': None}


def _seed(SEED):
    """The harness's own seed arrays, so the detector is WARM. -> {'ts', 'px', <line>: array}.

    WITHOUT THIS the lift-off detector sees only the live bars, and ws12 needs
    (LIFT_PTS - 1) x gap_for(12) = 170 bars = 14 m 10 s of tape before its first verdict exists.
    The seed is 74,880 bars of the same 21 lines the harness is computing, written by the harness at
    start, so prepending it gives every rung a verdict from the first live bar.

    ONLY THE DETECTOR USES IT. No reversal whose raw bar lands inside the seed is ever emitted -
    the stream is the live window, not four days of history.
    """
    if not os.path.exists(SEED):
        return None
    mt = os.path.getmtime(SEED)
    if _STATE['seed'] is None or _STATE['seed_mtime'] != mt:
        z = np.load(SEED, allow_pickle=True)
        _STATE['seed'] = {k: np.asarray(z[k], float) for k in z.files}
        _STATE['seed']['ts'] = np.asarray(z['ts'], np.int64)
        _STATE['seed_mtime'] = mt
    return _STATE['seed']


def _tf_role(name):
    """'ws12Mage' -> (12, 'Mage'). 'ws1b' -> (1, 'b')."""
    d = ''.join(c for c in name[2:] if c.isdigit())
    return int(d), name[2 + len(d):]


def _reload():
    """Read whatever is new in both files and extend the row list. -> the row count."""
    BARS, EVENTS, META, SEED, RDIR = _paths()
    if RDIR != _STATE.get('run_dir'):                 # a restart: nothing derived survives it
        _STATE.update({'run_dir': RDIR, 'bars': 0, 'events': 0, 'rows': [], 'revs': {},
                       'pxs': {}, 'late': [], 'seed': None, 'seed_mtime': None})
    if not os.path.exists(BARS):
        return len(_STATE['rows'])
    bars = [json.loads(l) for l in io.open(BARS) if l.strip()]
    evs = ([json.loads(l) for l in io.open(EVENTS) if l.strip()]
           if os.path.exists(EVENTS) else [])
    grew = len(bars) != _STATE['bars']
    _STATE['bars'], _STATE['events'] = len(bars), len(evs)
    if not bars:
        return len(_STATE['rows'])

    if grew:
        #   pxs over every bar received so far, through the producer. Recomputed only on growth.
        ts = np.asarray([b['ts'] for b in bars], np.int64)
        px = np.asarray([b['ohlcv'][3] for b in bars], float)
        vol = np.asarray([b['ohlcv'][4] for b in bars], float)
        sd = _seed(SEED)
        if sd is not None:                            # the DEMA is warmed on the seed's own px
            ts_f = np.concatenate([sd['ts'], ts])
            px_f = np.concatenate([sd['px'], px])
            ev_f = np.concatenate([np.ones(len(sd['ts']), bool), vol > 0])
        else:
            ts_f, px_f, ev_f = ts, px, (vol > 0)
        try:
            ps = px_smooth(ts_f, px_f, evt=ev_f, length=2, frac=12)
        except Exception as ex:                       # a short series can fail the DEMA warmup
            ps = np.full(len(px_f), np.nan); _STATE['late'] = ['pxs unavailable: %s' % ex]
        _STATE['pxs'] = {int(t): (None if not np.isfinite(v) else float(v))
                         for t, v in zip(ts_f[-len(ts):], ps[-len(ts):])}

    global _BAR
    _BAR = {int(b['ts']): b for b in bars}
    rows = []
    #   1. THE HARNESS'S OWN EVENTS
    for e in evs:
        ln = e.get('lines') or []
        nm = ' -> '.join(ln)
        ev = int(e.get('ev', 0))
        #   'baton' ALONE IS TOO GENERIC - Joe 1026. The row now names the pair, the pass rule that
        #   made the bar a pass bar, and whether a receiver existed, so two firings on one line can
        #   be told apart without reading the bars.
        if ev == 2:
            recv = ln[1] if len(ln) == 2 else 'none'
            act = 'baton %s -> %s (%s)' % (ln[0] if ln else '?', recv,
                                           e.get('why') or e.get('kind') or '?')
        else:
            act = EV_NAME.get(ev, 'ev %s' % e.get('ev'))
        a, b = e.get('a') or {}, e.get('b') or {}
        bs, ba = e.get('b_src') or {}, e.get('b_age') or {}
        cond = ['read %s' % e.get('read'), SIDE.get(int(e.get('side', 0)), '?')]
        for k in ln:
            if k in a and a[k] is not None:
                cond.append('A %s %.2f' % (k, a[k]))
            if k in b and b[k] is not None:
                cond.append('B %s %.2f from %s, age %ss' % (k, b[k], bs.get(k, '?'), ba.get(k, '?')))
        cond.append('oob %.0f/%.0f, fence %.0f/%.0f'
                    % (K.OOB_LO, K.OOB_HI, 100.0 - K.RMOM_FNC, K.RMOM_FNC))
        #   #2: the candidate scan the harness already records, and both reversals, raw and stamp
        for r in (e.get('rungs') or []):
            cond.append('%s %.2f fence:%s tow:%s'
                        % (r.get('line'), r.get('value'),
                           'y' if r.get('ex_fence') else 'n', 'y' if r.get('towards') else 'n'))
        for tag, key in (('rev hand', 'rev_hand'), ('rev recv', 'rev_recv')):
            rv = e.get(key)
            if rv:
                cond.append('%s raw %s, stamp %s' % (tag, rv.get('raw_utc'), rv.get('stamp_utc')))
        #   HIS 1026 ASK: at the ws1b oob->ib event, the r values of ws1..ws12. The harness records
        #   only ws1b on this event, so the ladder is taken from the bar's own stored reads, on the
        #   read that fired - nothing is recomputed here.
        if ev == 1:
            br = _BAR.get(int(e.get('ts', 0)))
            if br:
                sr = (br.get('b') if e.get('read') == 'B' else br.get('a')) or {}
                lad = ['ws%dr %.2f' % (t, sr['ws%dr' % t])
                       for t in range(1, 13) if sr.get('ws%dr' % t) is not None]
                if lad:
                    cond.append('r ladder on read %s: %s' % (e.get('read'), ', '.join(lad)))
        #   THE LINE'S OWN VALUE, on the read that fired this row - not the other read's. For a
        #   baton it is the HANDING line; the receiver's value stays in the conditions.
        src = b if e.get('read') == 'B' else a
        val = src.get(ln[0]) if ln else None
        rows.append({'ts': e.get('utc'), 'tsms': int(e.get('ts', 0)),
                     'pxs': _STATE['pxs'].get(int(e.get('ts', 0))),
                     'line': nm, 'val': val, 'action': act, 'cond': ' | '.join(cond),
                     'kind': 'event'})

    #   2. THE EMERGING REVERSALS, from the banked detector over the read-A series
    names = sorted(bars[-1].get('a', {}).keys())
    utc = {int(b['ts']): b['utc'] for b in bars}
    tsl = [int(b['ts']) for b in bars]
    sd = _seed(SEED)
    off = len(sd['ts']) if sd is not None else 0      # where the LIVE window starts in the series
    if grew:
        F._REV.clear(); F._RUN.clear()                # the cache is keyed per array; do not leak
        for nm in names:
            tf, role = _tf_role(nm)
            if role != 'r':                           # the detector is the r-line lift-off
                continue
            live = np.asarray([(b.get('a') or {}).get(nm, np.nan) for b in bars], float)
            ser = np.concatenate([sd[nm], live]) if (sd is not None and nm in sd) else live
            span = (int(K.LIFT_PTS) - 1) * K.gap_for(tf)
            if len(ser) <= span:
                continue
            base = off if (sd is not None and nm in sd) else 0
            for side in (+1, -1):
                for raw in F.revs(ser, tf, side):
                    if int(raw) < base:               # a seed-window reversal is history, not news
                        continue
                    rb = int(raw) - base
                    _STATE['revs'][(nm, side, rb)] = (float(ser[int(raw)])
                                                      if np.isfinite(ser[int(raw)]) else None)
            #   the emit list is rebuilt below from the full set, so order stays by timestamp
    for (nm, side, raw), rval in sorted(_STATE['revs'].items(), key=lambda z: z[0][2]):
        tf, _r = _tf_role(nm)
        if raw >= len(tsl):
            continue
        st = K.lift_stamp(raw)
        rows.append({'ts': utc.get(tsl[raw]), 'tsms': tsl[raw],
                     'pxs': _STATE['pxs'].get(tsl[raw]),
                     'line': nm, 'val': rval, 'action': 'reversal lift-off %s' % SIDE[side],
                     'cond': ('LIFT_PTS %d samples, LIFT_TOL %.1f r-points, LIFT_WOB %d bars'
                              ' | gap %d bars | raw %s | stamp %s'
                              % (K.LIFT_PTS, K.LIFT_TOL, K.LIFT_WOB, K.gap_for(tf),
                                 utc.get(tsl[raw]),
                                 utc.get(tsl[st]) if st < len(tsl) else 'not yet')),
                     'kind': 'rev'})

    rows.sort(key=lambda r: (r['tsms'], r['kind']))
    for i, r in enumerate(rows, 1):
        r['n'] = i
    _STATE['rows'] = rows
    return len(rows)


def _header():
    _b, _e2, META, _s, RDIR = _paths()
    m = json.load(io.open(META)) if os.path.exists(META) else {}
    spans = ', '.join('ws%d %d bars' % (t, (int(K.LIFT_PTS) - 1) * K.gap_for(t))
                      for t in (1, 4, 8, 12))
    return {'symbol': m.get('symbol'), 'seed_to': m.get('seed_to'), 'hours': m.get('hours'),
            'bars': _STATE['bars'], 'events': _STATE['events'], 'rows': len(_STATE['rows']),
            'newest': _STATE['rows'][-1]['ts'] if _STATE['rows'] else None,
            'lift_span': spans, 'notes': _STATE['late'], 'run': os.path.basename(RDIR),
            'now': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}


PAGE = """<!doctype html><html><head><meta charset="utf-8">
<title>Live seam events</title><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{--bg:#0d0f12;--fg:#e8e6e3;--dim:#8b9199;--line:#22262c;--ev:#7fd1ff;--rev:#ffc866}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:12px/1.45 ui-monospace,Menlo,Consolas,monospace}
header{position:sticky;top:0;background:#12151a;border-bottom:1px solid var(--line);padding:8px 16px;z-index:2}
h1{font-size:13px;margin:0 0 4px;font-weight:600;letter-spacing:.02em}
.meta{color:var(--dim);font-size:11px}
.meta b{color:var(--fg);font-weight:600}
main{padding:0 16px 48px}
table{width:100%;border-collapse:collapse}
th{text-align:left;color:var(--dim);font-weight:600;border-bottom:1px solid var(--line);padding:6px 8px;position:sticky;top:52px;background:#12151a;white-space:nowrap}
td{padding:4px 8px;border-bottom:1px solid #16191e;vertical-align:top}
td.ts{white-space:nowrap;color:var(--fg)}
td.pxs{white-space:nowrap;text-align:right;color:var(--dim)}
td.line{white-space:nowrap}
td.val{white-space:nowrap;text-align:right}
td.act{white-space:nowrap}
td.cond{color:var(--dim);word-break:break-word}
tr.event td.act{color:var(--ev)}
tr.rev td.act{color:var(--rev)}
button{background:#1b1f26;color:var(--fg);border:1px solid var(--line);border-radius:4px;padding:3px 10px;font:inherit;cursor:pointer;margin-left:8px}
@media (max-width:640px){th{top:76px}td.cond{font-size:11px}}
</style></head><body>
<header>
<h1>Live seam events &mdash; ts, pxs, line, action, conditions</h1>
<div class="meta" id="m">connecting&hellip;</div>
</header>
<main><table><thead><tr>
<th>ts</th><th>pxs</th><th>line</th><th>value</th><th>action</th><th>conditions</th>
</tr></thead><tbody id="b"></tbody></table></main>
<script>
let have=0, follow=true;
const b=document.getElementById('b'), m=document.getElementById('m');
function cell(t,c){const d=document.createElement('td');d.className=c;d.textContent=t;return d}
async function tick(){
  try{
    const r=await fetch('/rows?after='+have); const j=await r.json();
    for(const row of j.rows){
      const tr=document.createElement('tr'); tr.className=row.kind;
      tr.appendChild(cell(row.ts||'-','ts'));
      tr.appendChild(cell(row.pxs==null?'-':row.pxs.toFixed(6),'pxs'));
      tr.appendChild(cell(row.line||'-','line'));
      tr.appendChild(cell(row.val==null?'-':row.val.toFixed(2),'val'));
      tr.appendChild(cell(row.action||'-','act'));
      tr.appendChild(cell(row.cond||'-','cond'));
      b.appendChild(tr); have=row.n;
    }
    const h=j.header;
    m.innerHTML='<b>'+(h.symbol||'?')+'</b> &middot; seeded to '+(h.seed_to||'?')+
      ' &middot; '+(h.hours||'?')+' h &middot; bars <b>'+h.bars+'</b>'+
      ' &middot; harness events <b>'+h.events+'</b> &middot; stream rows <b>'+h.rows+'</b>'+
      ' &middot; run '+(h.run||'-')+' &middot; newest '+(h.newest||'-')+' &middot; now '+h.now+
      '<br>lift-off span before a first verdict: '+h.lift_span+
      (h.notes&&h.notes.length?' &middot; '+h.notes.join('; '):'');
    if(follow&&j.rows.length) window.scrollTo(0,document.body.scrollHeight);
  }catch(e){ m.textContent='stream error: '+e; }
}
const f=document.createElement('button'); f.textContent='following';
f.onclick=()=>{follow=!follow; f.textContent=follow?'following':'paused'};
document.querySelector('header').appendChild(f);
tick(); setInterval(tick,2000);
</script></body></html>"""


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        if self.path.startswith('/rows'):
            try:
                after = int(self.path.split('after=')[1].split('&')[0])
            except Exception:
                after = 0
            try:
                _reload()
                body = json.dumps({'header': _header(),
                                   'rows': [r for r in _STATE['rows'] if r['n'] > after]})
            except Exception as ex:
                body = json.dumps({'header': {'notes': ['reload failed: %r' % ex], 'bars': 0,
                                              'events': 0, 'rows': 0, 'now': ''}, 'rows': []})
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body.encode())
            return
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(PAGE.encode())))
        self.end_headers()
        self.wfile.write(PAGE.encode())


if __name__ == '__main__':
    io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'seam_stream.pid'), 'w').write(str(os.getpid()))
    print('seam_stream reading %s' % _run_dir())
    print('open http://127.0.0.1:%d' % PORT)
    ThreadingHTTPServer(('127.0.0.1', PORT), H).serve_forever()
