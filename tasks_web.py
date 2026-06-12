"""
tasks_web — tiny stdlib web service that renders the Optimus9 task list.

Reads the harness task store (/home/joe/.claude/tasks/<session>/*.json), scoped to THIS
project's sessions. Shows two blocks:
  • Active  — the current session's open tasks, in execution order (dependency then id)
  • Done    — every completed task across the project's sessions, newest close first
Auto-refreshing HTML. Run:  python3 tasks_web.py [port]   →  http://localhost:8765
"""
import sys, os, json, html, glob, datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

TASKS_ROOT = '/home/joe/.claude/tasks'
PROJECT = '/home/joe/.claude/projects/-home-joe-optimus9-docs-handover'
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
BADGE = {'completed': ('#2ea043', '✓ done'), 'in_progress': ('#bb8009', '▶ in progress'),
         'pending': ('#6e7681', '○ pending')}


def project_task_dirs():
    sids = [os.path.basename(j)[:-6] for j in glob.glob(f'{PROJECT}/*.jsonl')]
    return [f'{TASKS_ROOT}/{s}' for s in sids if os.path.isdir(f'{TASKS_ROOT}/{s}')]


def load():
    dirs = project_task_dirs()
    latest = max(dirs, key=os.path.getmtime) if dirs else None
    active, done = [], []
    for d in dirs:
        for f in glob.glob(f'{d}/*.json'):
            try:
                t = json.load(open(f)); t['_mtime'] = os.path.getmtime(f)
            except Exception:
                continue
            if t.get('status') == 'completed':
                done.append(t)
            elif d == latest:
                active.append(t)
    done.sort(key=lambda t: t['_mtime'], reverse=True)
    return planned_order(active), done


def planned_order(tasks):
    ids = {t['id'] for t in tasks}
    indeg = {t['id']: len([b for b in t.get('blockedBy', []) if b in ids]) for t in tasks}
    by_id = {t['id']: t for t in tasks}
    key = lambda i: int(i) if str(i).isdigit() else i
    ready = sorted([i for i in indeg if indeg[i] == 0], key=key)
    out = []
    while ready:
        i = ready.pop(0); out.append(i)
        for t in tasks:
            if i in t.get('blockedBy', []):
                indeg[t['id']] -= 1
                if indeg[t['id']] == 0:
                    ready.append(t['id']); ready.sort(key=key)
    for t in tasks:
        if t['id'] not in out:
            out.append(t['id'])
    return [by_id[i] for i in out]


def task_row(t, rank, show_close=False):
    color, label = BADGE.get(t.get('status', 'pending'), ('#6e7681', t.get('status', '?')))
    muted = ' class="muted"' if t.get('status') == 'completed' else ''
    blockers = t.get('blockedBy') or []
    bl = f'<div class="bl">blocked by: {", ".join(html.escape(str(b)) for b in blockers)}</div>' if blockers else ''
    closed = (f'<div class="closed">closed {datetime.datetime.fromtimestamp(t["_mtime"]):%b %d · %H:%M}</div>'
              if show_close else '')
    return f'''<tr{muted}>
      <td class="rank">{rank}</td>
      <td class="id">#{html.escape(str(t.get("id","")))}</td>
      <td><div class="name">{html.escape(t.get("subject",""))}</div>
          <div class="det">{html.escape(t.get("description",""))}</div>{bl}{closed}</td>
      <td><span class="badge" style="background:{color}">{html.escape(label)}</span></td>
    </tr>'''


def render():
    active, done = load()
    arows = '\n'.join(task_row(t, i) for i, t in enumerate(active, 1)) or \
        '<tr><td colspan="4" class="empty">no active tasks</td></tr>'
    drows = '\n'.join(task_row(t, i, show_close=True) for i, t in enumerate(done, 1))
    done_block = f'''<h2>Completed · {len(done)} <span class="dim">(newest first)</span></h2>
      <table>{drows}</table>''' if done else ''
    return f'''<!doctype html><html><head><meta charset="utf-8">
<meta http-equiv="refresh" content="5"><title>Optimus9 — tasks</title>
<style>
  body{{font:16px/1.6 -apple-system,Segoe UI,Roboto,sans-serif;background:#0d1117;color:#f0f6fc;margin:0;padding:26px}}
  h1{{font-size:21px;margin:0 0 2px;color:#fff}} h2{{font-size:16px;margin:30px 0 6px;color:#f0f6fc}}
  .sub,.dim{{color:#8b949e;font-size:13px}} .sub{{margin-bottom:16px}}
  table{{border-collapse:collapse;width:100%;max-width:1040px}}
  td{{border-bottom:1px solid #21262d;padding:13px 10px;vertical-align:top}}
  tr.muted{{opacity:.62}}
  .rank{{color:#8b949e;width:34px;text-align:right;font-variant-numeric:tabular-nums}}
  .id{{color:#8b949e;width:48px;font-size:14px}}
  .name{{font-weight:600;font-size:16px;color:#fff}}
  .det{{color:#c9d1d9;font-size:15px;margin-top:4px;max-width:720px}}
  .bl{{color:#e3b341;font-size:13px;margin-top:5px}}
  .closed{{color:#8b949e;font-size:13px;margin-top:5px}}
  .badge{{color:#fff;border-radius:999px;padding:4px 11px;font-size:13px;white-space:nowrap}}
  .empty{{color:#8b949e;text-align:center;padding:26px}}
</style></head><body>
<h1>Optimus9 — task list</h1>
<div class="sub">{len(active)} active · {len(done)} done · auto-refresh 5s</div>
<table>{arows}</table>
{done_block}
</body></html>'''


class H(BaseHTTPRequestHandler):
    def do_GET(self):
        out = render().encode()
        self.send_response(200); self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(out))); self.end_headers()
        self.wfile.write(out)

    def log_message(self, *a):
        pass


if __name__ == '__main__':
    print(f'tasks_web → http://localhost:{PORT}  (Ctrl-C to stop)')
    HTTPServer(('127.0.0.1', PORT), H).serve_forever()
