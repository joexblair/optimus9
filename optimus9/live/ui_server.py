"""UiServer — o9-live's bespoke view (SRP: read o9's own tables + market data → serve; write operator control).

Streams (poll ~1.5s): price chart (klines + trade markers) · order book (own feed, full-height column) ·
open positions (live unrealised PnL + exit) · status strip · trade history. Controls write o9_control
(sizing mode/max/split · flatten · halt/resume) — the running loop reads it next bar. Reads o9's OWN tables.
"""
from __future__ import annotations

import datetime as dtm
import os
import time
import urllib.request

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from optimus9.config import get_db_config
from optimus9 import DatabaseManager
from optimus9.live.feed import OrderBookFeed
from optimus9.live.control import O9Control
from optimus9.live.health import HealthStore

FAKEAPI = os.environ.get("O9_FAKEAPI_URL", "http://127.0.0.1:8098")
START_EQUITY = float(os.environ.get("O9_START_EQUITY", "500"))
DD_REF = float(os.environ.get("O9_DD_REF", "21.8"))
SYMBOL = os.environ.get("O9_SYMBOL", "FARTCOINUSDT")
UI_BOOK: dict = {}
app = FastAPI(title="o9-live")


@app.on_event("startup")
def _feed():
    OrderBookFeed(SYMBOL, lambda s, b: UI_BOOK.__setitem__(s, b)).start()


def _db(name="o9_live"):
    cfg = get_db_config(); cfg["database"] = name
    d = DatabaseManager(**cfg); d.connect()
    return d


def _closed(o9):
    return o9.execute("SELECT side, entry_px, exit_px, gross, net, opened_ms, closed_ms FROM o9_ledger "
                      "WHERE status='closed' ORDER BY closed_ms", fetch=True)


def _price(dev):
    k = dev.execute("SELECT kc_timestamp t, kc_close c FROM kline_collection ORDER BY kc_timestamp DESC LIMIT 1", fetch=True)
    return (float(k[0]["c"]), int(k[0]["t"])) if k else (0.0, None)


def _tape_health(dev, bars=240, frozen_win=12):
    """Live tape integrity from kline_collection (not stored — the real live-fail modes, computed each poll):
    gaps = missing 5s prints · frozen = last frozen_win bars collapse to one close (dead-conn dojis) ·
    synthetic = ruler-line bars (high==low, wiggle=0 patch gap-fills). All grounded in past incidents."""
    ks = dev.execute("SELECT kc_timestamp t, kc_high h, kc_low l, kc_close c, kc_volume v FROM kline_collection "
                     "WHERE kc_tp_pk=(SELECT tp_pk FROM trading_pairs WHERE tp_symbol_bybit=%s) "
                     "ORDER BY kc_timestamp DESC LIMIT %s", (SYMBOL, bars), fetch=True)
    if not ks:
        return {"gaps": None, "frozen": None, "synthetic": None, "bars": 0}
    ks = list(reversed(ks))
    ts = [int(k["t"]) for k in ks]
    missing = sum(max(0, round((ts[i] - ts[i - 1]) / 5000.0) - 1) for i in range(1, len(ts)))
    tail = ks[-frozen_win:]
    frozen = len({round(float(k["c"]), 10) for k in tail}) <= 1 and len(tail) >= frozen_win
    synthetic = sum(1 for k in tail if float(k["h"]) == float(k["l"]))     # ruler bars (no range)
    return {"gaps": int(missing), "frozen": bool(frozen), "synthetic": int(synthetic), "bars": len(ks)}


@app.get("/api/history")
def history(limit: int = 100):
    o9 = _db(); rows = _closed(o9); o9.disconnect()
    bal, out = START_EQUITY, []
    for r in rows:
        net = float(r["net"]); bal += net
        out.append({"oms": int(r["opened_ms"]), "ms": int(r["closed_ms"]), "dir": r["side"], "gross": round(float(r["gross"] or net), 2),
                    "net": round(net, 2), "entry": float(r["entry_px"]), "exit": float(r["exit_px"] or 0),
                    "bal": round(bal, 2)})
    return {"trades": out[-limit:][::-1]}


@app.get("/api/positions")
def positions():
    o9 = _db(); dev = _db("pk_optimizer")
    rows = o9.execute("SELECT led_id, side, qty, entry_px, opened_ms, reason FROM o9_ledger "
                      "WHERE status='open' ORDER BY opened_ms", fetch=True)
    price, _ = _price(dev); o9.disconnect(); dev.disconnect()
    out = []
    for r in rows:
        d = 1 if r["side"] == "Buy" else -1
        qty, entry = float(r["qty"]), float(r["entry_px"])
        out.append({"id": r["led_id"], "side": r["side"], "qty": qty, "entry": entry, "mark": price,
                    "unreal": round(d * (price - entry) * qty, 2),
                    "unreal_pct": round(d * (price - entry) / entry * 100, 3) if entry else 0,
                    "opened": int(r["opened_ms"]), "reason": r["reason"]})
    return {"positions": out, "price": price}


@app.get("/api/state")
def state():
    o9 = _db(); dev = _db("pk_optimizer")
    acct = o9.execute("SELECT equity FROM o9_account WHERE acct_id=1", fetch=True)
    rows = _closed(o9)
    pos = o9.execute("SELECT side, SUM(qty) q FROM o9_ledger WHERE status='open' GROUP BY side", fetch=True)
    ctl = O9Control(o9).read()
    hlth = HealthStore(o9).read()
    price, tms = _price(dev); tape = _tape_health(dev); o9.disconnect(); dev.disconnect()
    equity = float(acct[0]["equity"]) if acct else START_EQUITY
    tape_age = round((int(time.time() * 1000) - tms - 5000) / 1000.0, 1) if tms else None
    bal, peak, wins = START_EQUITY, START_EQUITY, 0
    day0 = int(dtm.datetime.now(dtm.timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000)
    day_pnl = 0.0
    for r in rows:
        net = float(r["net"]); bal += net; peak = max(peak, bal); wins += net > 0
        if int(r["closed_ms"]) >= day0:
            day_pnl += net
    dd = round((peak - equity) / peak * 100, 1) if peak > 0 else 0.0
    open_pos = {"side": pos[0]["side"], "size": float(pos[0]["q"])} if pos else None
    hb_age = round((int(time.time() * 1000) - int(hlth["updated_ms"])) / 1000.0, 1) if hlth["updated_ms"] else None
    return {"equity": round(equity, 2), "start": START_EQUITY, "net": round(equity - START_EQUITY, 2),
            "day_pnl": round(day_pnl, 2), "exposure": round(open_pos["size"] * price if open_pos else 0, 0),
            "exposure_x": round(open_pos["size"] * price / equity, 2) if open_pos and equity else 0,
            "dd": dd, "dd_ref": DD_REF, "trades": len(rows), "win": round(wins / len(rows) * 100, 1) if rows else 0.0,
            "price": price, "tape_age": tape_age, "book_ok": bool(UI_BOOK.get(SYMBOL)),
            "cascade": {"label": hlth["phase_label"], "tone": hlth["phase_tone"], "arm": hlth["arm"],
                        "gate": hlth["gate"], "gate_reason": hlth["gate_reason"], "exit": hlth["exit_line"]},
            "feed": {"tape_age": tape_age, "gaps": tape["gaps"], "frozen": tape["frozen"],
                     "synthetic": tape["synthetic"], "book_ok": bool(UI_BOOK.get(SYMBOL)),
                     "loop_ms": hlth["loop_ms"], "rtt_ms": hlth["rtt_ms"], "clock_skew_ms": hlth["clock_skew_ms"],
                     "pubtrade_age_ms": hlth["pubtrade_age_ms"], "order_rejects": hlth["order_rejects"],
                     "ws_reconnects": hlth["ws_reconnects"], "db_reconnects": hlth["db_reconnects"],
                     "hb_age": hb_age},
            "sizing": {"mode": ctl["mode"], "max_order": ctl["max_order"], "split": ctl["split"]},
            "halted": bool(ctl["halted"])}


@app.get("/api/chart")
def chart(bars: int = 150):
    dev = _db("pk_optimizer"); o9 = _db()
    ks = dev.execute("SELECT kc_timestamp t, kc_close c FROM kline_collection WHERE kc_tp_pk="
                     "(SELECT tp_pk FROM trading_pairs WHERE tp_symbol_bybit=%s) "
                     "ORDER BY kc_timestamp DESC LIMIT %s", (SYMBOL, bars), fetch=True)
    trs = o9.execute("SELECT side, qty, entry_px, exit_px, net, reason, opened_ms, closed_ms "
                     "FROM o9_ledger ORDER BY led_id", fetch=True)
    dev.disconnect(); o9.disconnect()
    mk = []
    for t in trs:                                                    # markers carry tooltip fields (hover)
        mk.append({"t": int(t["opened_ms"]), "px": float(t["entry_px"]), "kind": "entry",
                   "side": t["side"], "qty": float(t["qty"]), "reason": t["reason"] or ""})
        if t["closed_ms"]:
            mk.append({"t": int(t["closed_ms"]), "px": float(t["exit_px"] or 0), "kind": "exit",
                       "side": t["side"], "net": round(float(t["net"] or 0), 2), "reason": t["reason"] or ""})
    return {"series": [[int(k["t"]), float(k["c"])] for k in reversed(ks)], "markers": mk}


@app.get("/api/book")
def book(levels: int = 14):
    b = UI_BOOK.get(SYMBOL)
    if not b or not b["bids"] or not b["asks"]:
        return {"bids": [], "asks": [], "spread_bps": None, "mid": None, "slip": None, "max": None}
    bid, ask = float(b["bids"][0][0]), float(b["asks"][0][0]); mid = (bid + ask) / 2.0
    o9 = _db(); mx = O9Control(o9).read()["max_order"]; o9.disconnect()
    rem, cost, filled = float(mx), 0.0, 0.0
    for p, s in b["bids"]:
        take = min(rem, float(s)); cost += take * float(p); filled += take; rem -= take
        if rem <= 0:
            break
    slip = round((mid - cost / filled) / mid * 10000, 1) if filled else None
    return {"bids": b["bids"][:levels], "asks": b["asks"][:levels],
            "spread_bps": round((ask - bid) / mid * 10000, 1), "mid": mid, "slip": slip, "max": mx}


# ── operator control (UI writes → loop reads next bar) ──
@app.post("/api/sizing")
def set_sizing(mode: str = None, max: int = None, split: int = None):
    o9 = _db(); O9Control(o9).set_sizing(mode, max, split); o9.disconnect(); return {"ok": True}


@app.post("/api/flatten")
def flatten():
    o9 = _db(); O9Control(o9).request_flatten(halt=True); o9.disconnect(); return {"ok": True}


@app.post("/api/exit")
def exit_position():
    o9 = _db(); O9Control(o9).request_flatten(halt=False); o9.disconnect(); return {"ok": True}


@app.post("/api/resume")
def resume():
    o9 = _db(); O9Control(o9).resume(); o9.disconnect(); return {"ok": True}


@app.post("/api/reset")
def reset_account():
    """Reset the paper account. Clears o9's OWN store (ledger + decisions), restores equity to start,
    tells the fakeAPI to clear its mock exchange (fx_*), and HALTS the loop (operator resumes when ready).
    Durable by design: everything is MySQL rows — this is the deliberate wipe, nothing resets on restart."""
    o9 = _db(); now = int(time.time() * 1000)
    for t in ("o9_ledger", "o9_decision"):                          # o9's own trade/decision record
        o9.execute("TRUNCATE TABLE %s" % t)
    o9.execute("INSERT INTO o9_account (acct_id, equity, realized_total, trade_count, updated_ms) "
               "VALUES (1,%s,0,0,%s) ON DUPLICATE KEY UPDATE equity=%s, realized_total=0, trade_count=0, "
               "updated_ms=%s", (START_EQUITY, now, START_EQUITY, now))
    O9Control(o9).halt()                                            # stop trading on the fresh account
    o9.disconnect()
    fakeapi_ok = False
    try:                                                            # fakeAPI owns fx_* → it resets its own
        req = urllib.request.Request(FAKEAPI + "/dev/reset", method="POST")
        with urllib.request.urlopen(req, timeout=5) as r:
            fakeapi_ok = (r.status == 200)
    except Exception:
        fakeapi_ok = False
    return {"ok": True, "equity": START_EQUITY, "fakeapi_reset": fakeapi_ok, "halted": True}


@app.get("/", response_class=HTMLResponse)
def index():
    return _PAGE


_PAGE = r"""<!doctype html><html><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>o9-live</title><style>
:root{--bg:#0A0C12;--panel:#111623;--raise:#1A2233;--line:#2A3346;--ink:#EEF2F9;--dim:#AEB7CC;--faint:#7C8699;--accent:#2FD6BE;
--long:#33D17A;--short:#FF5D5D;--warn:#F5A623;--mono:ui-monospace,'JetBrains Mono',Menlo,Consolas,monospace}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:13px system-ui,-apple-system,'Segoe UI',sans-serif;
background-image:radial-gradient(1100px 520px at 82% -10%,rgba(47,214,190,.07),transparent 60%)}
.num{font-family:var(--mono);font-variant-numeric:tabular-nums}.pos{color:var(--long)}.neg{color:var(--short)}
.lbl{font-size:10px;letter-spacing:.13em;text-transform:uppercase;color:var(--dim)}
.wrap{height:100vh;max-width:1260px;margin:0 auto;padding:8px;display:flex;flex-direction:column;gap:8px}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:8px}
.sliver{display:flex;align-items:center;gap:12px;padding:9px 13px}
.brand{font-family:var(--mono);font-weight:600;font-size:15px}.brand b{color:var(--accent)}
.dot{width:8px;height:8px;border-radius:50%;background:var(--accent);animation:p 2s infinite}
@keyframes p{0%{box-shadow:0 0 0 0 rgba(47,214,190,.5)}70%{box-shadow:0 0 0 8px rgba(47,214,190,0)}100%{box-shadow:0 0 0 0 rgba(47,214,190,0)}}
.env{font-family:var(--mono);font-size:10.5px;letter-spacing:.1em;padding:3px 9px;border-radius:5px;background:rgba(245,166,35,.14);color:var(--warn);border:1px solid rgba(245,166,35,.4)}
.px{font-family:var(--mono);font-size:15px;font-weight:600}.sizing{display:flex;align-items:center;gap:9px;margin-left:6px}
.seg{display:flex;background:var(--bg);border:1px solid var(--line);border-radius:6px;padding:2px}.seg span{font-size:11.5px;color:var(--dim);padding:5px 11px;border-radius:4px;cursor:pointer}.seg span.on{background:var(--accent);color:#04120f;font-weight:600}
.chip2{font-family:var(--mono);font-size:11.5px;color:var(--dim);border:1px solid var(--line);border-radius:5px;padding:4px 9px}.chip2 b{color:var(--ink)}
.szin{width:56px;background:var(--bg);border:1px solid var(--line);color:var(--ink);font-family:var(--mono);font-size:11.5px;padding:2px 5px;border-radius:4px;text-align:right}.szin:focus{outline:1px solid var(--accent)}
.spacer{flex:1}.kill{font:700 12px system-ui;letter-spacing:.05em;color:#fff;background:linear-gradient(180deg,#ff6b5f,#e33b30);border:1px solid #ff8a80;border-radius:6px;padding:7px 15px;cursor:pointer}
.kill.resume{background:linear-gradient(180deg,#3fe08a,#1fb56a);border-color:#7ff0b5;color:#04120f}
.bktog{display:none;font:600 11px system-ui;color:var(--accent);background:var(--bg);border:1px solid var(--line);border-radius:5px;padding:6px 10px;cursor:pointer}
.reset{font:600 11px system-ui;color:var(--warn);background:var(--bg);border:1px solid var(--line);border-radius:6px;padding:7px 12px;margin-right:6px;cursor:pointer}.reset:hover{border-color:var(--warn)}
.status{display:flex;align-items:stretch;overflow-x:auto}
.stat{display:flex;flex-direction:column;gap:3px;padding:9px 14px;border-right:1px solid var(--line);justify-content:center;white-space:nowrap}.stat .v{font-family:var(--mono);font-size:15px;font-weight:600}
.feed{display:flex;gap:14px;flex-wrap:nowrap;overflow-x:auto;flex:1}.feed i{font-style:normal;display:flex;align-items:center;gap:5px;font-family:var(--mono);font-size:12px;color:var(--dim);white-space:nowrap}
.feedbar{display:flex;align-items:center;gap:12px;padding:5px 12px}.feedbar .lbl{flex:none}
.fdot{width:6px;height:6px;border-radius:50%;background:var(--long)}.fdot.warn{background:var(--warn)}.fdot.bad{background:var(--short)}
.casc{margin-left:auto;border-right:0;align-items:flex-end}.chip{font-family:var(--mono);font-size:11.5px;padding:4px 10px;border-radius:5px;background:rgba(47,214,190,.14);color:var(--accent);border:1px solid rgba(47,214,190,.34)}
.chip.wait{background:rgba(245,166,35,.14);color:var(--warn);border-color:rgba(245,166,35,.34)}
.chip.idle{background:rgba(124,134,153,.12);color:var(--dim);border-color:var(--line)}
.ddbar{width:130px;height:5px;border-radius:3px;background:var(--bg);overflow:hidden;margin-top:3px}.ddbar i{display:block;height:100%;background:linear-gradient(90deg,var(--long),var(--warn))}
.body{flex:1;display:flex;gap:8px;min-height:0}
.main{flex:1;display:flex;flex-direction:column;gap:8px;min-height:0}
.chart{height:24%;min-height:120px;position:relative;padding:10px}canvas{position:absolute;inset:10px;width:calc(100% - 20px);height:calc(100% - 20px)}
.chleg{position:absolute;left:14px;bottom:8px;display:flex;gap:14px;font-size:10.5px;color:var(--dim);z-index:2}
.mtip{position:absolute;z-index:6;pointer-events:none;opacity:0;transform:translateY(3px);transition:opacity .12s,transform .12s;background:rgba(18,23,36,.97);border:1px solid var(--line);border-radius:6px;padding:7px 10px;font-family:var(--mono);font-size:11px;line-height:1.55;white-space:nowrap;box-shadow:0 8px 26px rgba(0,0,0,.45)}
.mtip.show{opacity:1;transform:translateY(0)}
.mtip .hd{font-family:system-ui;font-weight:600;font-size:9.5px;letter-spacing:.1em;text-transform:uppercase;margin-bottom:3px}
.mtip .k{color:var(--faint)}
.posw{flex:1;display:flex;flex-direction:column;min-height:90px}.hist{height:30%;min-height:120px;display:flex;flex-direction:column}
.ph{display:flex;gap:10px;align-items:center;padding:9px 14px;border-bottom:1px solid var(--line)}.ph h2{margin:0;font-size:13px}.ph .c{font-family:var(--mono);font-size:11.5px;color:var(--dim)}
.scroll{overflow:auto;flex:1}table{width:100%;min-width:560px;border-collapse:collapse;font-family:var(--mono);font-size:12px}
th{position:sticky;top:0;background:var(--panel);font:600 10.5px system-ui;letter-spacing:.1em;text-transform:uppercase;color:var(--dim);text-align:right;padding:8px 14px;border-bottom:1px solid var(--line)}th.l{text-align:left}
td{padding:8px 14px;text-align:right;border-bottom:1px solid rgba(42,51,70,.5);white-space:nowrap}td.l{text-align:left}tr:hover{background:rgba(47,214,190,.05)}
.side{font-weight:600;font-size:11px;padding:2px 7px;border-radius:4px}.side.s{color:var(--short);background:rgba(255,93,93,.12)}.side.b{color:var(--long);background:rgba(51,209,122,.12)}
.exit{font:600 11px system-ui;color:var(--ink);background:var(--raise);border:1px solid var(--line);border-radius:5px;padding:4px 11px;cursor:pointer}.exit:hover{border-color:var(--short);color:var(--short)}
.empty{padding:20px;text-align:center;color:var(--dim);font-family:var(--mono);font-size:12px}
.book{width:225px;display:flex;flex-direction:column}.book h3{margin:0;padding:8px 12px;font-size:11px;color:var(--dim);border-bottom:1px solid var(--line);display:flex;justify-content:space-between}
.ladder{flex:1;overflow:hidden;font-family:var(--mono);font-size:11px}.lvl{position:relative;display:flex;justify-content:space-between;padding:2.5px 12px;z-index:1}
.lvl .depth{position:absolute;top:0;bottom:0;right:0;z-index:-1;opacity:.16}.lvl.ask .depth{background:var(--short)}.lvl.bid .depth{background:var(--long)}.lvl.ask .p{color:var(--short)}.lvl.bid .p{color:var(--long)}.lvl .s{color:var(--dim)}
.spread{display:flex;justify-content:space-between;padding:6px 12px;border-block:1px solid var(--line);font-family:var(--mono);font-size:11px;color:var(--dim);background:var(--bg)}
.slip{padding:8px 12px;font-size:11px;color:var(--dim);border-top:1px solid var(--line);display:flex;justify-content:space-between}.slip b{font-family:var(--mono);color:var(--ink)}
@media(max-width:820px){.sizing{display:none}.bktog{display:inline-block}
 .book{position:fixed;right:0;top:0;height:100vh;transform:translateX(100%);transition:transform .25s;z-index:30;box-shadow:-16px 0 40px rgba(0,0,0,.4)}.book.open{transform:none}}
</style></head><body><div class=wrap>
<header class="sliver panel"><span class=dot></span><span class=brand>o9<b>&middot;</b>live</span><span class=env>FAKE-API &middot; realtime</span>
 <span class="px num" id=px>&mdash;</span>
 <div class=sizing><span class=lbl>size</span><div class=seg id=seg><span data-m=smallest>Smallest</span><span data-m=fixed>Fixed</span><span data-m=dynamic5x>Dynamic 5&times;</span></div>
  <span class=chip2>max <input class=szin id=maxo inputmode=numeric></span><span class=chip2>split <input class=szin id=split inputmode=numeric></span></div>
 <div class=spacer></div><button class=bktog id=bktog>Order book</button><button class=reset id=reset title="Reset the paper account on fakeAPI">Reset</button><button class=kill id=kill>&#9632; FLATTEN &amp; HALT</button></header>
<div class="status panel">
 <div class=stat><span class=lbl>equity</span><span class="v num" id=eq>&mdash;</span></div>
 <div class=stat><span class=lbl>day pnl</span><span class="v num" id=day>&mdash;</span></div>
 <div class=stat><span class=lbl>exposure</span><span class="v num" id=exp>&mdash;</span></div>
 <div class=stat><span class=lbl>live drawdown vs backtest</span><span class=num id=dd style=font-size:12px>&mdash;</span><span class=ddbar><i id=ddb style=width:0></i></span></div>
 <div class="stat casc"><span class=lbl>cascade state</span><span class=chip id=casc>&mdash;</span></div></div>
<div class=body>
 <div class=main>
  <div class="chart panel"><canvas id=cv></canvas><div class=mtip id=mtip></div><div class=chleg><span style=color:var(--short)>&#9660; entry</span><span style=color:var(--long)>&#9650; exit</span><span style=color:var(--accent)>&mdash; price</span></div></div>
  <div class="feedbar panel"><span class=lbl>feed health</span><div class=feed id=feed></div></div>
  <div class="posw panel"><div class=ph><h2>Open positions</h2><span class=c id=pc>&mdash;</span></div>
   <div class=scroll><table><thead><tr><th class=l>Side</th><th>Size</th><th>Entry</th><th>Mark</th><th>Unreal $</th><th>Unreal %</th><th>Start</th><th></th></tr></thead><tbody id=pb></tbody></table>
   <div class=empty id=pe>flat &mdash; no open positions</div></div></div>
  <div class="hist panel"><div class=ph><h2>Trade history</h2><span class=c id=hc>&mdash;</span></div>
   <div class=scroll><table><thead><tr><th class=l>Opened</th><th class=l>Closed</th><th>Dir</th><th>Gross</th><th>Net</th><th>Entry</th><th>Exit</th><th>Balance</th></tr></thead><tbody id=tb></tbody></table>
   <div class=empty id=he>waiting for the first realtime signal&hellip;</div></div></div>
 </div>
 <div class="book panel" id=book><h3><span>Order book</span><span id=spr>&mdash;</span></h3><div class=ladder id=asks></div>
  <div class=spread><span>mid <b id=bmid style=color:var(--ink)>&mdash;</b></span><span id=bok></span></div><div class=ladder id=bids></div>
  <div class=slip><span id=slipl>walk &mdash;</span><b id=slipv>&mdash;</b></div></div>
</div></div><script>
function money(v){return (v<0?'-$':'+$')+Math.abs(v).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g,',')}
function commas(v){return Math.round(v).toLocaleString()}
function hhmm(ms){return new Date(ms).toISOString().slice(5,19).replace('T',' ')}
function fdot(a){return a==null?'bad':a>12?'bad':a>6?'warn':''}
function hi(v,w,b){return v==null?'bad':v>=b?'bad':v>=w?'warn':''}   // higher = worse (rtt/loop)
function fitem(cls,txt){return '<i><span class="fdot '+cls+'"></span>'+txt+'</i>'}
function buildFeed(f){
 var kl=f.frozen?'bad':(f.gaps>2?'bad':(f.synthetic>0||f.gaps>0)?'warn':'');
 var klt='kline '+(f.frozen?'FROZEN':((f.gaps==null?'—':f.gaps)+'g/'+(f.synthetic==null?'—':f.synthetic)+'r'));
 var sk=f.clock_skew_ms==null?'bad':(Math.abs(f.clock_skew_ms)>=100?'bad':Math.abs(f.clock_skew_ms)>=30?'warn':'');
 var pt=f.pubtrade_age_ms==null?'bad':fdot(f.pubtrade_age_ms/1000);
 return [fitem(fdot(f.tape_age),'tape '+(f.tape_age==null?'—':f.tape_age+'s')),
  fitem(kl,klt),
  fitem(f.book_ok?'':'bad','book '+(f.book_ok?'live':'—')),
  fitem(pt,'pubTrade '+(f.pubtrade_age_ms==null?'—':(f.pubtrade_age_ms/1000).toFixed(1)+'s')),
  fitem(sk,'skew '+(f.clock_skew_ms==null?'—':(f.clock_skew_ms>0?'+':'')+f.clock_skew_ms+'ms')),
  fitem(hi(f.rtt_ms,150,400),'RTT '+(f.rtt_ms==null?'—':f.rtt_ms+'ms')),
  fitem(hi(f.loop_ms,300,600),'loop '+(f.loop_ms==null?'—':f.loop_ms+'ms')),
  fitem(f.order_rejects?'bad':'','rej '+(f.order_rejects==null?'—':f.order_rejects)),
  fitem(f.ws_reconnects?'warn':'','ws '+(f.ws_reconnects==null?'—':f.ws_reconnects)),
  fitem(f.db_reconnects?'warn':'','db '+(f.db_reconnects==null?'—':f.db_reconnects)),
  fitem(f.hb_age==null?'bad':(f.hb_age>15?'bad':f.hb_age>7?'warn':''),'hb '+(f.hb_age==null?'—':f.hb_age+'s'))].join('');}
function post(u){return fetch(u,{method:'POST'})}
var CH={series:[],markers:[]},HOV=null;
function drawChart(){var cv=document.getElementById('cv'),ctx=cv.getContext('2d'),w=cv.width=cv.clientWidth,h=cv.height=cv.clientHeight;
 var s=CH.series;if(s.length<2)return;var ys=s.map(p=>p[1]),lo=Math.min.apply(0,ys),hi=Math.max.apply(0,ys),pad=(hi-lo)*.12||1e-4;lo-=pad;hi+=pad;
 var t0=s[0][0],t1=s[s.length-1][0],X=t=>(t-t0)/(t1-t0||1)*w,Y=v=>h-(v-lo)/(hi-lo)*h;
 ctx.strokeStyle='rgba(42,51,70,.5)';for(var g=1;g<4;g++){ctx.beginPath();ctx.moveTo(0,h*g/4);ctx.lineTo(w,h*g/4);ctx.stroke()}
 var gr=ctx.createLinearGradient(0,0,0,h);gr.addColorStop(0,'rgba(47,214,190,.2)');gr.addColorStop(1,'rgba(47,214,190,0)');
 ctx.beginPath();ctx.moveTo(X(s[0][0]),Y(s[0][1]));s.forEach(p=>ctx.lineTo(X(p[0]),Y(p[1])));ctx.lineTo(w,h);ctx.lineTo(0,h);ctx.fillStyle=gr;ctx.fill();
 ctx.beginPath();ctx.moveTo(X(s[0][0]),Y(s[0][1]));s.forEach(p=>ctx.lineTo(X(p[0]),Y(p[1])));ctx.strokeStyle='#2FD6BE';ctx.lineWidth=1.6;ctx.stroke();
 var lp=s[s.length-1];ctx.beginPath();ctx.arc(X(lp[0]),Y(lp[1]),3,0,7);ctx.fillStyle='#2FD6BE';ctx.fill();
 CH.markers.forEach(function(m){if(m.t<t0)return;var x=X(m.t),y=Y(m.px),up=m.kind=='exit';m._x=x;m._y=up?y+13:y-13;ctx.beginPath();
  if(up){ctx.moveTo(x,y+9);ctx.lineTo(x-5,y+17);ctx.lineTo(x+5,y+17)}else{ctx.moveTo(x,y-9);ctx.lineTo(x-5,y-17);ctx.lineTo(x+5,y-17)}
  ctx.closePath();ctx.fillStyle=up?'#33D17A':'#FF5D5D';ctx.fill();
  if(m===HOV){ctx.beginPath();ctx.arc(x,m._y,11,0,7);ctx.strokeStyle=up?'#33D17A':'#FF5D5D';ctx.globalAlpha=.7;ctx.lineWidth=1.4;ctx.stroke();ctx.globalAlpha=1}})}
function tipRows(m){var tm=hhmm(m.t).slice(6);
 if(m.kind=='entry')return[['time',tm],['side',m.side],['size',commas(m.qty)],['fill',m.px.toFixed(5)]];
 return[['time',tm],['fill',m.px.toFixed(5)],['net',money(m.net)],['reason',m.reason||'—']];}
function findMark(px,py){var best=null,bd=18;CH.markers.forEach(function(m){if(m._x==null)return;var d=Math.hypot(px-m._x,py-m._y);if(d<bd){bd=d;best=m}});return best;}
function showTip(m){HOV=m;drawChart();var mt=document.getElementById('mtip');
 if(!m){mt.classList.remove('show');return;}
 var cl=m.kind=='exit'?'#33D17A':'#FF5D5D';
 mt.innerHTML="<div class=hd style='color:"+cl+"'>"+(m.kind=='exit'?'Exit':'Entry')+"</div>"+tipRows(m).map(function(r){
   var v=r[1],c='';if(/^\+\$/.test(v))c=" style='color:#33D17A'";else if(/^-\$/.test(v))c=" style='color:#FF5D5D'";
   return "<span class=k>"+r[0]+"</span>&nbsp;&nbsp;<span"+c+">"+v+"</span>";}).join('<br>');
 mt.classList.add('show');
 var cv=document.getElementById('cv'),cw=cv.clientWidth,ch=cv.clientHeight,tw=mt.offsetWidth,th=mt.offsetHeight;
 mt.style.left=(cv.offsetLeft+Math.min(Math.max(0,m._x+14),cw-tw))+'px';
 mt.style.top=(cv.offsetTop+Math.min(Math.max(0,m._y-th-8),ch-th))+'px';}
function tick(){
 fetch('/api/chart').then(r=>r.json()).then(c=>{CH=c;if(HOV)HOV=CH.markers.filter(function(m){return m.t==HOV.t&&m.kind==HOV.kind})[0]||null;showTip(HOV);});
 fetch('/api/book').then(r=>r.json()).then(function(b){
  document.getElementById('spr').textContent=b.spread_bps!=null?b.spread_bps+'bps':'—';
  document.getElementById('bmid').textContent=b.mid?b.mid.toFixed(5):'—';
  document.getElementById('bok').innerHTML=b.mid?'<span style=color:#33D17A>live</span>':'<span style=color:#FF5D5D>no feed</span>';
  var all=b.bids.concat(b.asks),mx=Math.max.apply(0,all.map(l=>+l[1]))||1;
  function rows(a,cls){return a.map(l=>'<div class="lvl '+cls+'"><span class=depth style=width:'+(+l[1]/mx*100)+'%></span><span class=p>'+(+l[0]).toFixed(5)+'</span><span class=s>'+Math.round(+l[1]/1000)+'k</span></div>').join('')}
  document.getElementById('asks').innerHTML=rows(b.asks.slice().reverse(),'ask');document.getElementById('bids').innerHTML=rows(b.bids,'bid');
  document.getElementById('slipl').textContent='walk '+(b.max?commas(b.max):'—')+' sell';document.getElementById('slipv').textContent=b.slip!=null?b.slip+'bps':'—';});
 fetch('/api/positions').then(r=>r.json()).then(function(p){var ps=p.positions;
  document.getElementById('pc').textContent=ps.length?(ps.length+' open'):'flat';
  document.getElementById('pe').style.display=ps.length?'none':'block';
  document.getElementById('pb').innerHTML=ps.map(function(t){var sd=t.side=='Sell'?'s':'b',nm=t.side=='Sell'?'SHORT':'LONG',cl=t.unreal>=0?'pos':'neg';
   return '<tr><td class=l><span class="side '+sd+'">'+nm+'</span></td><td>'+commas(t.qty)+'</td><td>'+t.entry.toFixed(5)+'</td><td>'+t.mark.toFixed(5)+'</td><td class="'+cl+'">'+money(t.unreal)+'</td><td class="'+cl+'">'+t.unreal_pct.toFixed(2)+'%</td><td>'+new Date(t.opened).toISOString().slice(11,19)+'</td><td><button class=exit onclick="doExit()">Exit</button></td></tr>'}).join('');});
 Promise.all([fetch('/api/state').then(r=>r.json()),fetch('/api/history').then(r=>r.json())]).then(function(x){
  var s=x[0],h=x[1].trades;
  document.getElementById('px').textContent=s.price?s.price.toFixed(5):'—';
  var e=document.getElementById('eq');e.textContent='$'+commas(s.equity);e.className='v num pos';
  var d=document.getElementById('day');d.textContent=money(s.day_pnl);d.className='v num '+(s.day_pnl>=0?'pos':'neg');
  document.getElementById('exp').textContent=s.exposure?('$'+commas(s.exposure)+' · '+s.exposure_x+'×'):'flat';
  document.getElementById('dd').innerHTML=s.dd+'% <span style=color:#7C8699>/ '+s.dd_ref+'%</span>';document.getElementById('ddb').style.width=Math.min(100,s.dd/s.dd_ref*100)+'%';
  var cc=document.getElementById('casc'),stale=(s.feed.hb_age==null||s.feed.hb_age>15);
  cc.textContent=stale?'— no heartbeat':s.cascade.label;cc.className='chip '+(stale?'idle':s.cascade.tone);
  var mo=document.getElementById('maxo');if(document.activeElement!==mo)mo.value=s.sizing.max_order;
  var sp=document.getElementById('split');if(document.activeElement!==sp)sp.value=s.sizing.split;
  document.querySelectorAll('#seg span').forEach(el=>el.className=(el.dataset.m===s.sizing.mode?'on':''));
  document.getElementById('feed').innerHTML=buildFeed(s.feed);
  var k=document.getElementById('kill');if(s.halted){k.className='kill resume';k.textContent='▶ RESUME';}else{k.className='kill';k.innerHTML='&#9632; FLATTEN &amp; HALT';}
  document.getElementById('hc').textContent=s.trades+' closed · '+s.win+'% win · start $'+s.start;
  document.getElementById('he').style.display=h.length?'none':'block';
  document.getElementById('tb').innerHTML=h.map(function(t){var cl=t.net>=0?'pos':'neg',sd=t.dir=='Sell'?'s':'b',nm=t.dir=='Sell'?'SHORT':'LONG';
   return '<tr><td class=l>'+hhmm(t.oms)+'</td><td class=l>'+hhmm(t.ms)+'</td><td class=l><span class="side '+sd+'">'+nm+'</span></td><td class="'+(t.gross>=0?'pos':'neg')+'">'+money(t.gross)+'</td><td class="'+cl+'">'+money(t.net)+'</td><td>'+t.entry.toFixed(5)+'</td><td>'+t.exit.toFixed(5)+'</td><td>$'+commas(t.bal)+'</td></tr>'}).join('');
 })}
window.doExit=function(){if(confirm('Close the open position?'))post('/api/exit').then(tick)};
document.getElementById('kill').onclick=function(){if(this.classList.contains('resume')){post('/api/resume').then(tick)}else if(confirm('FLATTEN & HALT — close everything and stop trading?')){post('/api/flatten').then(tick)}};
document.getElementById('reset').onclick=function(){if(confirm('Reset the paper account?\n\nClears ALL trades & positions on fakeAPI, restores starting equity, and HALTS the loop (press Resume when ready).'))post('/api/reset').then(tick)};
document.querySelectorAll('#seg span').forEach(el=>el.onclick=function(){post('/api/sizing?mode='+el.dataset.m).then(tick)});
function szpost(k,v){if(v!==''&&!isNaN(v)&&Number(v)>0)post('/api/sizing?'+k+'='+encodeURIComponent(v)).then(tick)}
document.getElementById('maxo').addEventListener('change',function(){szpost('max',this.value)});
document.getElementById('split').addEventListener('change',function(){szpost('split',this.value)});
document.getElementById('bktog').onclick=function(){document.getElementById('book').classList.toggle('open')};
(function(){var cv=document.getElementById('cv');
 cv.addEventListener('mousemove',function(e){var r=cv.getBoundingClientRect();var m=findMark(e.clientX-r.left,e.clientY-r.top);cv.style.cursor=m?'pointer':'default';showTip(m);});
 cv.addEventListener('mouseleave',function(){showTip(null);});
 cv.addEventListener('touchstart',function(e){var t=e.touches[0],r=cv.getBoundingClientRect();var m=findMark(t.clientX-r.left,t.clientY-r.top);if(m){e.preventDefault();showTip(m);}else showTip(null);},{passive:false});})();
tick();setInterval(tick,1500);
</script></body></html>"""
