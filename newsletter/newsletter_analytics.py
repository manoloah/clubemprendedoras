#!/usr/bin/env python3
"""Newsletter analytics: how every newsletter did, as CSV logs + a dashboard.

    python newsletter/newsletter_analytics.py run [--days N] [--slack] [--no-sent-json]
    python newsletter/newsletter_analytics.py dashboard          # rebuild the dashboard from the saved CSVs

`run` asks Resend for every broadcast it reports as sent whose name is "Newsletter <issue>[ · parte N]"
(the name `newsletter.py schedule` gives; "Prueba …" test sends are left out), so a send counts even
when its sent.json entry lives on a branch that isn't merged yet. All sends by default; --days N keeps
the last N days. Each issue (2026-10-14 and 2026-10-14-b are two) is one row, its parts added together.
It writes into newsletter/analytics/ (gitignored, it holds subscribers' emails):

    readers.csv      ranking of the most engaged readers (1 point per send opened, 3 per send clicked)
    recipients.csv   one row per email per broadcast: sent, delivered, opened (+count), clicked
                     (+count, links), bounced, complained (spam), unsubscribed, suppressed
    broadcasts.csv   one row per broadcast with totals and rates
    history.csv      one row per broadcast per run, so you can see how numbers grow after the send
    dashboard.html   self-contained dashboard (no emails in it); dashboard.png is its screenshot

With --slack the PNG is posted in #emprendeconpm with a short summary. By default it also
refreshes the `stats` block of those broadcasts in sent.json (the same shape `newsletter.py stats`
writes), which is the only committed output. Needs RESEND_API_KEY (and SLACK_BOT_TOKEN for --slack)
in .env.
"""
import argparse
import csv
import html
import json
import math
import re
import subprocess
import sys
import time as time_module
from collections import OrderedDict
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import newsletter as nl  # noqa: E402  (reuses env, Resend client, Slack helpers)

OUT = nl.HERE / "analytics"
EVENTS = ("sent", "delivered", "opened", "clicked", "bounced", "complained", "unsubscribed", "suppressed")
RECIPIENT_COLS = ["issue", "part", "broadcast_id", "email", "sent", "delivered", "opened", "open_count",
                  "clicked", "click_count", "clicked_links", "bounced", "complained", "unsubscribed", "suppressed"]
BROADCAST_COLS = ["issue", "part", "parts_total", "broadcast_id", "subject", "sent_at", "recipients", *EVENTS,
                  "delivery_rate", "open_rate", "click_rate", "click_to_open", "bounce_rate", "spam_rate",
                  "unsub_rate", "as_of"]


# ---------- Resend ----------

def call(fn, *args):
    """Resend allows ~2 requests/second: retry a few times when it says slow down."""
    for attempt in range(5):
        try:
            return fn(*args)
        except Exception as e:  # SDK raises its own error types
            msg = str(e).lower()
            if not any(k in msg for k in ("rate", "429", "request failed")) or attempt == 4:
                raise
            time_module.sleep(1.5 * (attempt + 1))


def recipients_of(resend, bid, kind):
    rows, after = [], None
    while True:
        params = {"type": kind, "limit": 100, **({"after": after} if after else {})}
        page = call(resend.Broadcasts.recipients, bid, params)
        data = page.get("data", [])
        rows += data
        time_module.sleep(0.6)
        if not page.get("has_more") or not data:
            return rows
        after = data[-1]["id"]


def pct(n, d):
    return round(100 * n / d, 1) if d else 0.0


def fetch(resend, entry):
    """All per-recipient events + totals for one sent.json entry."""
    bid = entry["broadcast_id"]
    people = OrderedDict()
    for kind in EVENTS:
        for r in recipients_of(resend, bid, kind):
            p = people.setdefault(r["email"], {"email": r["email"]})
            p[kind] = True
            if kind == "opened":
                p["open_count"] = r.get("count", 1)
            if kind == "clicked":
                p["click_count"] = r.get("count", 1)
                p["_links"] = [(l["url"].split("?")[0], l["clicks"]) for l in r.get("clicked_links", [])]
                p["clicked_links"] = " | ".join(
                    f'{l["url"].split("?")[0]} x{l["clicks"]}' for l in r.get("clicked_links", []))
    try:
        links = call(resend.Broadcasts.clicked_links, bid, {}).get("data", [])
    except Exception:
        links = []
    links = [{"url": l["url"].split("?")[0], "clicks": l["clicks"], "unique": l["unique_clicks"]} for l in links]
    totals = {k: sum(1 for p in people.values() if p.get(k)) for k in EVENTS}
    return list(people.values()), totals, links


def all_broadcasts(resend):
    rows, after = [], None
    while True:
        page = call(resend.Broadcasts.list, {"limit": 100, **({"after": after} if after else {})})
        data = page.get("data", [])
        rows += data
        if not page.get("has_more") or not data:
            return rows
        after = data[-1]["id"]
        time_module.sleep(0.6)


NAME = re.compile(r"^Newsletter (\S+?)(?: · parte (\d+))?$")


def pick_broadcasts(resend, days):
    """Every newsletter broadcast Resend says went out (in the last `days` days, if given), oldest first.

    Resend is the source of truth for what was sent; sent.json adds what it knows (recipients,
    parts_total). A send missing from this branch's sent.json still counts, with an entry made
    from its name."""
    log = {e["broadcast_id"]: e for e in nl.sent_log()}
    since = datetime.now(nl.TZ) - timedelta(days=days) if days else None
    chosen, broadcasts = [], all_broadcasts(resend)
    # Parts still waiting to go out (scheduled or sending; drafts are canceled leftovers), so an
    # issue missing from sent.json is still shown as "en curso" until its last part is sent.
    parts = {}
    for b in broadcasts:
        m = NAME.match(b.get("name") or "")
        if m and (b.get("status") or "").lower() != "draft":
            parts[m.group(1)] = max(parts.get(m.group(1), 1), int(m.group(2) or 1))
    for b in broadcasts:
        m = NAME.match(b.get("name") or "")
        if (b.get("status") or "").lower() != "sent" or not m:
            continue
        sent_at = datetime.fromisoformat(b["sent_at"].replace(" ", "T"))
        if since and sent_at < since:
            continue
        e = log.get(b["id"]) or {"issue": m.group(1) + ".md", "broadcast_id": b["id"], "scheduled_at": b["sent_at"],
                                 **({"part": int(m.group(2)), "parts_total": parts[m.group(1)]} if m.group(2) else {})}
        chosen.append((e, call(resend.Broadcasts.get, b["id"])))
        time_module.sleep(0.6)
    return sorted(chosen, key=lambda c: c[1].get("sent_at") or "")


# ---------- CSV ----------

def write_csv(path, cols, rows):
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def broadcast_row(entry, b, t, as_of):
    d = t["delivered"]
    return {
        "issue": entry["issue"].removesuffix(".md"), "part": entry.get("part", 1),
        "parts_total": entry.get("parts_total", entry.get("part", 1)), "broadcast_id": entry["broadcast_id"], "subject": b.get("subject", ""),
        "sent_at": b.get("sent_at") or entry["scheduled_at"], "recipients": entry.get("recipients", t["sent"]),
        **t, "delivery_rate": pct(d, t["sent"]), "open_rate": pct(t["opened"], d),
        "click_rate": pct(t["clicked"], d), "click_to_open": pct(t["clicked"], t["opened"]),
        "bounce_rate": pct(t["bounced"], t["sent"]), "spam_rate": pct(t["complained"], d),
        "unsub_rate": pct(t["unsubscribed"], d), "as_of": as_of,
    }


def read_csv(path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


# ---------- dashboard ----------

DAYS = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]
MONTHS = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


def day_label(d):
    return f"{DAYS[d.weekday()]} {d.day} {MONTHS[d.month - 1]}"


def when_label(iso):
    d = datetime.fromisoformat(iso.replace(" ", "T")).astimezone(nl.TZ)
    return f"{day_label(d)} {d.year}, {d.strftime('%I:%M').lstrip('0')} {'am' if d.hour < 12 else 'pm'}"


def fmt(v):
    """12.0 -> '12%', 14.13 -> '14.1%'."""
    return f"{v:g}%"


def plural(n, one, many):
    return f"{n} {one if n == 1 else many}"


def group_issues(rows):
    """One row per issue (2026-10-14 and 2026-10-14-b are different emails): its parts are added
    together and it's dated by its first part. Newest first."""
    issues = OrderedDict()
    for r in sorted(rows, key=lambda r: r["sent_at"]):
        key = r["issue"]
        g = issues.setdefault(key, {"issue": key, "subjects": [], "sent_at": r["sent_at"], "sends": 0,
                                    "parts_total": 1, **{k: 0 for k in EVENTS}})
        if r["subject"] not in g["subjects"]:
            g["subjects"].append(r["subject"])
        g["sends"] += 1
        g["parts_total"] = max(g["parts_total"], int(r.get("parts_total") or 1))
        for k in EVENTS:
            g[k] += int(r[k])
    out = []
    for g in issues.values():
        d = g["delivered"]
        g["subject"] = " · ".join(g["subjects"])
        g["pending"] = g["sends"] < g["parts_total"]
        g.update(open_rate=pct(g["opened"], d), click_rate=pct(g["clicked"], d), delivery_rate=pct(g["delivered"], g["sent"]),
                 click_to_open=pct(g["clicked"], g["opened"]), bounce_rate=pct(g["bounced"], g["sent"]),
                 spam_rate=pct(g["complained"], d), unsub_rate=pct(g["unsubscribed"], d))
        out.append(g)
    return out[::-1]


def edition_label(g):
    """The day its first part went out, in CDMX (the issue name is only the planned Wednesday)."""
    return day_label(datetime.fromisoformat(g["sent_at"].replace(" ", "T")).astimezone(nl.TZ))


def window_label(days):
    return f"últimos {days} días" if days else "todos los envíos"


def engaged_readers(people):
    """Ranks readers by engagement over the window: 1 point per send opened, 3 per send clicked."""
    agg = {}
    for r in people:
        a = agg.setdefault(r["email"], {"email": r["email"], "received": 0, "opened": 0, "clicked": 0, "clicks": 0, "opens": 0})
        if r["delivered"] == "True":
            a["received"] += 1
        a["opened"] += r["opened"] == "True"
        a["clicked"] += r["clicked"] == "True"
        a["clicks"] += int(r["click_count"] or 0)
        a["opens"] += int(r["open_count"] or 0)
    for a in agg.values():
        a["score"] = a["opened"] + 3 * a["clicked"]
    ranked = sorted(agg.values(), key=lambda a: (-a["score"], -a["clicks"], -a["opens"], a["email"]))
    return [dict(a, rank=i + 1) for i, a in enumerate(ranked) if a["score"] > 0]


def mask(email):
    name, _, dom = email.partition("@")
    return f"{name[:2]}***@{dom}"


def tile(label, value, sub="", tone=""):
    return (f'<div class="tile {tone}"><div class="tl">{html.escape(label)}</div>'
            f'<div class="tv">{value}</div><div class="ts">{sub}</div></div>')


def delta(cur, prev):
    if prev is None:
        return ""
    d = round(cur - prev, 1)
    if d == 0:
        return '<span class="flat">= igual que la anterior</span>'
    cls, arrow = ("up", "▲") if d > 0 else ("down", "▼")
    return f'<span class="{cls}">{arrow} {abs(d):g} pts vs. anterior</span>'


TABLE_ISSUES = 4    # rows in the comparison table
CHART_ISSUES = 12   # points in each trend chart; the charts keep their size, older issues drop off


def nice_ceiling(v):
    """Rounds an axis maximum up to 1, 1.5, 2, 2.5, 3, 4, 5, 6, 8 or 10 times a power of ten."""
    if v <= 0:
        return 1
    mag = 10 ** math.floor(math.log10(v))
    return next(m * mag for m in (1, 1.5, 2, 2.5, 3, 4, 5, 6, 8, 10) if m * mag >= v)


def trend(issues, key, title, color, unit="%"):
    """A fixed-size line chart of one metric over the last CHART_ISSUES issues (oldest left). The
    dashed line is the average of the issues shown; the latest point is labelled. Hovering a point
    shows its edition (SVG <title>)."""
    pts = issues[:CHART_ISSUES][::-1]
    W, H, L, R, T, B = 320, 170, 34, 46, 14, 26
    vals = [g[key] for g in pts]
    top = nice_ceiling(max(vals) * 1.1)
    x = (lambda i: L + (W - L - R) / 2) if len(pts) == 1 else (lambda i: L + i * (W - L - R) / (len(pts) - 1))
    y = lambda v: T + (H - T - B) * (1 - v / top)
    show = (lambda v: fmt(v)) if unit == "%" else (lambda v: f"{v:g}")
    grid = "".join(f'<line x1="{L}" x2="{W - R}" y1="{y(t):.1f}" y2="{y(t):.1f}" class="gl"/>'
                   f'<text x="{L - 6}" y="{y(t) + 4:.1f}" class="ax" text-anchor="end">{show(round(t, 1))}</text>'
                   for t in (0, top / 2, top))
    avg = sum(vals) / len(vals)
    path = " ".join(f"{'M' if i == 0 else 'L'}{x(i):.1f},{y(v):.1f}" for i, v in enumerate(vals))
    dots = "".join(f'<circle cx="{x(i):.1f}" cy="{y(g[key]):.1f}" r="{5 if i == len(pts) - 1 else 3.5}" fill="{color}" class="dot">'
                   f'<title>{edition_label(g)} · {show(g[key])}{" (en curso)" if g["pending"] else ""}\n{html.escape(g["subject"])}</title></circle>'
                   for i, g in enumerate(pts))
    last = pts[-1]
    xl = [f'<text x="{x(0):.1f}" y="{H - 6}" class="ax" text-anchor="{"middle" if len(pts) == 1 else "start"}">{edition_label(pts[0])}</text>']
    if len(pts) > 1:
        xl.append(f'<text x="{x(len(pts) - 1):.1f}" y="{H - 6}" class="ax" text-anchor="end">{edition_label(last)}</text>')
    svg = (f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="{html.escape(title)}: últimas {len(pts)} ediciones">{grid}'
           f'<line x1="{L}" x2="{W - R}" y1="{y(avg):.1f}" y2="{y(avg):.1f}" class="avg"/>'
           f'<text x="{W - R + 6}" y="{y(avg) + 4:.1f}" class="ax">prom.</text>'
           f'<path d="{path}" fill="none" stroke="{color}" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>'
           f'{dots}{"".join(xl)}</svg>')
    prev = pts[-2][key] if len(pts) > 1 else None
    change = "" if prev is None else delta(last[key], prev) if unit == "%" else (
        f'<span class="{"up" if last[key] > prev else "down" if last[key] < prev else "flat"}">'
        f'{"▲" if last[key] >= prev else "▼"} {abs(last[key] - prev):g} vs. anterior</span>')
    return (f'<figure class="trend"><figcaption><span class="tl">{html.escape(title)}</span>'
            f'<b>{show(last[key])}</b><span class="ts">{change}</span></figcaption>{svg}'
            f'<div class="tavg">Promedio: {show(round(avg, 1))}</div></figure>')


def dashboard_html(broadcasts, links, as_of, days, readers=()):
    issues = group_issues(broadcasts)
    if not issues:
        body = '<section class="card"><p>No hubo envíos en este periodo.</p></section>'
    else:
        latest = issues[0]
        prev = issues[1] if len(issues) > 1 else None
        pending = '<span class="chip">en curso · faltan partes por enviar</span>' if latest["pending"] else ""
        tiles = "".join([
            tile("Entregados", f'{latest["delivered"]}<small> de {latest["sent"]}</small>', fmt(latest["delivery_rate"]) + " de los enviados"),
            tile("Aperturas", fmt(latest["open_rate"]), f'{plural(latest["opened"], "correo abierto", "correos abiertos")}<br>{delta(latest["open_rate"], prev and prev["open_rate"])}'),
            tile("Clics", fmt(latest["click_rate"]), f'{plural(latest["clicked"], "correo con clic", "correos con clic")} · {fmt(latest["click_to_open"])} de quienes abrieron<br>{delta(latest["click_rate"], prev and prev["click_rate"])}'),
            tile("Rebotes", latest["bounced"], fmt(latest["bounce_rate"]) + " de los enviados"),
            tile("Spam", latest["complained"], f'{fmt(latest["spam_rate"])} · suprimidos: {latest["suppressed"]}', "bad" if latest["complained"] else ""),
            tile("Bajas", latest["unsubscribed"], fmt(latest["unsub_rate"]) + " de los entregados", "bad" if latest["unsub_rate"] > 1 else ""),
        ])
        rows = "".join(
            f'<tr><td class="l"><b>{edition_label(g)}</b>{"<span class=chip>en curso</span>" if g["pending"] else ""}'
            f'<div class="subj">{html.escape(g["subject"])}</div></td>'
            f'<td>{g["sent"]}</td><td>{g["delivered"]}</td>'
            f'<td class="n">{g["opened"]} <small>{fmt(g["open_rate"])}</small></td>'
            f'<td class="n">{g["clicked"]} <small>{fmt(g["click_rate"])}</small></td>'
            f'<td>{g["bounced"]}</td><td>{g["complained"]}</td><td>{g["unsubscribed"]}</td></tr>' for g in issues[:TABLE_ISSUES])
        shown = min(len(issues), CHART_ISSUES)
        trends = "".join([
            trend(issues, "open_rate", "Aperturas", "#7B5FD6"),
            trend(issues, "click_rate", "Clics", "var(--tomato)"),
            trend(issues, "click_to_open", "Clic de quienes abrieron", "var(--green)"),
            trend(issues, "delivered", "Entregados", "var(--navy)", unit=""),
        ])
        top = "".join(
            f'<tr><td class="rk">{r["rank"]}</td><td class="l">{html.escape(mask(r["email"]))}</td>'
            f'<td>{r["received"]}</td><td>{r["opened"]}</td><td>{r["clicked"]}</td><td>{r["clicks"]}</td>'
            f'<td><span class="pts">{r["score"]}</span></td></tr>' for r in list(readers)[:10]
        ) or '<tr><td class="l" colspan="7">Todavía no hay aperturas</td></tr>'
        link_rows = "".join(f'<tr><td class="l link">{html.escape(l["url"].replace("https://", "").replace("www.", "").rstrip("/"))}</td>'
                            f'<td>{l["clicks"]}</td><td>{l["unique"]}</td></tr>' for l in links[:10]
                            ) or '<tr><td class="l" colspan="3">Sin clics todavía</td></tr>'
        body = f"""
<section class="card"><div class="eyebrow">Última edición {pending}</div>
<h2>{edition_label(latest)} · {html.escape(latest["subject"])}</h2><div class="tiles">{tiles}</div></section>
<section class="card"><h2>Últimas {min(len(issues), TABLE_ISSUES)} ediciones</h2>
<div class="scroll"><table><tr><th class="l">Edición</th><th>Enviados</th><th>Entregados</th><th>Abiertos</th><th>Con clic</th><th>Rebotes</th><th>Spam</th><th>Bajas</th></tr>{rows}</table></div></section>
<section class="card"><h2>Tendencia · {"1 edición" if shown == 1 else f"últimas {shown} ediciones"}</h2>
<p class="sub">Cada punto es una edición, de la más antigua a la más reciente. La línea punteada es el promedio. Pasa el cursor por un punto para ver cuál es.</p>
<div class="trends">{trends}</div></section>
<section class="card"><h2>Lectoras más activas</h2>
<p class="sub">1 punto por envío abierto y 3 por cada envío con clic. Top 10 de {len(readers)} lectoras con actividad (correos parcialmente ocultos).</p>
<div class="scroll"><table><tr><th class="rk">#</th><th class="l">Correo</th><th>Recibidos</th><th>Abiertos</th><th>Con clic</th><th>Clics</th><th>Puntos</th></tr>{top}</table></div></section>
<section class="card"><h2>Links más clicados</h2>
<p class="sub">Top 10 de {len(links)} links, en todos los envíos.</p>
<div class="scroll"><table><tr><th class="l">Link</th><th>Clics</th><th>Personas</th></tr>{link_rows}</table></div></section>"""
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Newsletter · resultados</title><style>
:root{{--navy:#17254A;--cream:#FFF8EC;--tomato:#F02717;--lilac:#B9A6F0;--pink:#FBC9D8;--line:#17254A1F;--green:#2E7D4F}}
*{{box-sizing:border-box}}body{{margin:0;padding:28px 20px 36px;background:var(--cream);color:var(--navy);font:15px/1.45 'DM Sans',Helvetica,Arial,sans-serif;font-variant-numeric:tabular-nums}}
main{{max-width:960px;margin:0 auto}}header{{margin-bottom:18px}}h1{{font:700 28px Georgia,serif;margin:0 0 2px}}h1 b{{color:var(--tomato)}}
.meta{{margin:0;opacity:.7;font-size:13px}}
.card{{background:#fff;border:1.5px solid var(--navy);border-radius:18px;padding:20px 22px;margin-bottom:16px}}
h2{{font:700 19px Georgia,serif;margin:0 0 14px}}h3{{font-size:13px;margin:0 0 8px;text-transform:uppercase;letter-spacing:.04em;opacity:.7}}
.eyebrow{{font-size:12px;text-transform:uppercase;letter-spacing:.06em;opacity:.7;margin-bottom:4px}}.eyebrow .chip{{opacity:1}}
.chip{{display:inline-block;margin-left:8px;padding:1px 8px;border-radius:99px;background:var(--pink);font-size:11px;text-transform:none;letter-spacing:0;font-weight:600;white-space:nowrap}}
.sub{{margin:-6px 0 12px;font-size:13px;opacity:.7}}
.tiles{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}}@media(max-width:640px){{.tiles{{grid-template-columns:1fr 1fr}}}}
.tile{{background:var(--cream);border-radius:14px;padding:14px 16px}}.tl{{font-size:12px;text-transform:uppercase;letter-spacing:.05em;opacity:.7}}
.tv{{font:700 34px/1.15 Georgia,serif}}.tv small{{font:400 14px 'DM Sans',sans-serif;opacity:.6}}.ts{{font-size:12px;opacity:.8;min-height:34px}}
.tile.bad .tv{{color:var(--tomato)}}.up{{color:var(--green);font-weight:600}}.down{{color:var(--tomato);font-weight:600}}.flat{{opacity:.7}}
table{{width:100%;border-collapse:collapse;font-size:13px}}th{{font-size:11px;text-transform:uppercase;letter-spacing:.05em;opacity:.65;font-weight:600;border-bottom:1.5px solid var(--navy)}}
th,td{{padding:9px 8px;text-align:right;white-space:nowrap}}td{{border-bottom:1px solid var(--line)}}tr:last-child td{{border-bottom:0}}
.l{{text-align:left!important;white-space:normal;overflow-wrap:anywhere}}.n small{{opacity:.6}}.subj{{font-size:12px;opacity:.7;font-weight:400;max-width:320px}}
.rk{{width:34px;text-align:center!important}}td.rk{{font-weight:700}}.pts{{display:inline-block;min-width:28px;padding:1px 8px;border-radius:99px;background:var(--pink);font-weight:700;text-align:center}}
.link{{font-size:12px}}.scroll{{overflow-x:auto;-webkit-overflow-scrolling:touch}}.scroll td.l:first-child{{min-width:170px}}
.trends{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}@media(max-width:640px){{.trends{{grid-template-columns:1fr}}}}
.trend{{margin:0;background:var(--cream);border-radius:14px;padding:14px 14px 10px}}
.trend figcaption{{display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 10px;margin-bottom:4px}}.trend figcaption .tl{{flex-basis:100%}}
.trend figcaption b{{font:700 26px/1.1 Georgia,serif}}.trend .ts{{min-height:0}}
.trend svg{{display:block;width:100%;height:auto;overflow:visible}}.trend .gl{{stroke:var(--line);stroke-width:1}}
.trend .avg{{stroke:var(--navy);stroke-opacity:.45;stroke-width:1;stroke-dasharray:3 3}}
.trend .ax{{font-size:10px;fill:var(--navy);fill-opacity:.65}}.trend .dot{{stroke:var(--cream);stroke-width:2}}.trend .dot:hover{{r:7}}
.tavg{{font-size:12px;opacity:.7;margin-top:2px}}
.note{{font-size:12px;opacity:.6;margin:20px 4px 0}}
</style></head><body><main>
<header><h1>El Club de las <b>Emprendedoras</b> · newsletter</h1>
<p class="meta">Resultados · {window_label(days)} · actualizado {html.escape(as_of)} (CDMX)</p></header>{body}
<p class="note">Las aperturas se cuentan con una imagen invisible: Apple Mail y Gmail a veces abren el correo por la persona, así que la tasa real es algo menor. Los clics son más confiables. El detalle por correo y por envío está en <code>newsletter/analytics/</code> (solo local).</p>
</main></body></html>"""


def render_png(html_path, height=2700):
    png = html_path.with_suffix(".png")
    chrome = nl.env("CHROME_PATH", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    subprocess.run([chrome, "--headless", "--disable-gpu", "--hide-scrollbars", f"--window-size=1000,{height}",
                    f"--screenshot={png}", html_path.as_uri()], check=True, capture_output=True, timeout=120)
    return png


def aggregate_links(people):
    """Clicks and distinct people per URL across every send: one person clicking the same link in two issues counts once."""
    agg = {}
    for p in people:
        for url, n in p.get("_links", []):
            a = agg.setdefault(url, {"url": url, "clicks": 0, "emails": set()})
            a["clicks"] += n
            a["emails"].add(p["email"])
    rows = [{"url": a["url"], "clicks": a["clicks"], "unique": len(a["emails"])} for a in agg.values()]
    return sorted(rows, key=lambda l: -l["clicks"])


def build_dashboard(days):
    broadcasts = read_csv(OUT / "broadcasts.csv")
    links = json.loads((OUT / "links.json").read_text()) if (OUT / "links.json").exists() else []
    as_of = max((b["as_of"] for b in broadcasts), default=datetime.now(nl.TZ).isoformat(timespec="minutes"))
    readers = engaged_readers(read_csv(OUT / "recipients.csv"))
    write_csv(OUT / "readers.csv", ["rank", "email", "score", "received", "opened", "clicked", "clicks", "opens"], readers)
    page = OUT / "dashboard.html"
    page.write_text(dashboard_html(broadcasts, links, when_label(as_of), days, readers), encoding="utf-8")
    return page, group_issues(broadcasts)


def slack_summary(issues):
    if not issues:
        return "📊 *Newsletter:* todavía no hay envíos."
    g = issues[0]
    wip = " (en curso: faltan partes por enviar)" if g["pending"] else ""
    line = (f"📊 *Resultados del newsletter {edition_label(g)}*{wip} — _{g['subject']}_\n"
            f"• Entregados: *{g['delivered']}/{g['sent']}* ({g['delivery_rate']}%)\n"
            f"• Aperturas: *{g['open_rate']}%* ({g['opened']}) · Clics: *{g['click_rate']}%* ({g['clicked']})\n"
            f"• Rebotes: {g['bounced']} · Spam: {g['complained']} · Bajas: {g['unsubscribed']}")
    if len(issues) > 1:
        p = issues[1]
        line += (f"\n• Vs. {edition_label(p)}: aperturas {p['open_rate']}% → {g['open_rate']}%, "
                 f"clics {p['click_rate']}% → {g['click_rate']}%")
    if g["complained"]:
        line += "\n⚠️ Hubo quejas de spam: revisen el asunto y el contenido."
    return line + "\n_Los números siguen subiendo unos días después del envío; el dashboard se actualiza cada semana._"


# ---------- commands ----------

def cmd_run(a):
    OUT.mkdir(exist_ok=True)
    resend = nl.resend_client()
    as_of = datetime.now(nl.TZ).isoformat(timespec="minutes")
    chosen = pick_broadcasts(resend, a.days)
    all_people, b_rows, all_links = [], [], []
    log = nl.sent_log()
    for entry, b in chosen:
        people, totals, links = fetch(resend, entry)
        label = entry["issue"].removesuffix(".md")
        for p in people:
            all_people.append({**p, "issue": label, "part": entry.get("part", 1), "broadcast_id": entry["broadcast_id"]})
        b_rows.append(broadcast_row(entry, b, totals, as_of))
        all_links.append(links)
        if not a.no_sent_json:
            for e in log:
                if e["broadcast_id"] == entry["broadcast_id"]:
                    e["stats"] = {k: totals[k] for k in EVENTS if k != "suppressed"} | {"links": links, "as_of": as_of}
        r = b_rows[-1]
        print(f"{label} parte {r['part']}: {r['delivered']}/{r['sent']} entregados · {r['opened']} abiertos ({r['open_rate']}%) · "
              f"{r['clicked']} con clic ({r['click_rate']}%) · {r['bounced']} rebotes · {r['complained']} spam · {r['unsubscribed']} bajas")
    write_csv(OUT / "recipients.csv", RECIPIENT_COLS, all_people)
    write_csv(OUT / "broadcasts.csv", BROADCAST_COLS, b_rows)
    hist = OUT / "history.csv"
    new = not hist.exists()
    with hist.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, BROADCAST_COLS, extrasaction="ignore")
        if new:
            w.writeheader()
        w.writerows(b_rows)
    (OUT / "links.json").write_text(json.dumps(aggregate_links(all_people), ensure_ascii=False, indent=1))
    if not a.no_sent_json:
        nl.SENT_LOG.write_text(json.dumps(log, ensure_ascii=False, indent=2) + "\n")
    page, issues = build_dashboard(a.days)
    png = render_png(page)
    print(f"Dashboard: {page}\nImagen: {png}\nCSV: {OUT}/recipients.csv, broadcasts.csv, history.csv")
    if a.slack:
        nl.slack_upload(png, "Resultados del newsletter", slack_summary(issues))
        print(f"Publicado en Slack ({nl.SLACK_CHANNEL}).")


def cmd_dashboard(a):
    page, _ = build_dashboard(a.days)
    print(f"Dashboard: {page}\nImagen: {render_png(page)}")


def main():
    nl.load_env()
    nl.SLACK_CHANNEL = nl.env("SLACK_CHANNEL", nl.SLACK_CHANNEL)
    nl.SLACK_MENTION = nl.env("SLACK_MENTION", nl.SLACK_MENTION)
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("run")
    p.add_argument("--days", type=int, default=0, help="solo los últimos N días (0 = todos los envíos)")
    p.add_argument("--slack", action="store_true", help="publica el dashboard (PNG) en SLACK_CHANNEL")
    p.add_argument("--no-sent-json", action="store_true", help="no actualiza stats en sent.json")
    p.set_defaults(fn=cmd_run)
    p = sub.add_parser("dashboard")
    p.add_argument("--days", type=int, default=0)
    p.set_defaults(fn=cmd_dashboard)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
