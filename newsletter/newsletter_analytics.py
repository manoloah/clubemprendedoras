#!/usr/bin/env python3
"""Newsletter analytics: how the last weeks' broadcasts did, as CSV logs + a dashboard.

    python newsletter/newsletter_analytics.py run [--days 14] [--slack] [--no-sent-json]
    python newsletter/newsletter_analytics.py dashboard          # rebuild the dashboard from the saved CSVs

`run` pulls every broadcast from sent.json scheduled in the last N days (default 14) that Resend
reports as sent, and writes into newsletter/analytics/ (gitignored, it holds subscribers' emails):

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
            if "rate" not in str(e).lower() and "429" not in str(e) or attempt == 4:
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
                p["clicked_links"] = " | ".join(
                    f'{l["url"].split("?")[0]} x{l["clicks"]}' for l in r.get("clicked_links", []))
    try:
        links = call(resend.Broadcasts.clicked_links, bid, {}).get("data", [])
    except Exception:
        links = []
    links = [{"url": l["url"].split("?")[0], "clicks": l["clicks"], "unique": l["unique_clicks"]} for l in links]
    totals = {k: sum(1 for p in people.values() if p.get(k)) for k in EVENTS}
    return list(people.values()), totals, links


def pick_broadcasts(resend, days):
    """sent.json entries scheduled in the last `days` days that Resend says went out."""
    now = datetime.now(nl.TZ)
    chosen = []
    for e in nl.sent_log():
        when = datetime.fromisoformat(e["scheduled_at"])
        if when > now or when < now - timedelta(days=days):
            continue
        b = call(resend.Broadcasts.get, e["broadcast_id"])
        if (b.get("status") or "").lower() != "sent":
            continue
        chosen.append((e, b))
        time_module.sleep(0.6)
    return chosen


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

def group_issues(rows):
    """Combines the parts of one issue (split sends) into one row, newest issue first."""
    issues = OrderedDict()
    for r in sorted(rows, key=lambda r: r["sent_at"]):
        g = issues.setdefault(r["issue"], {"issue": r["issue"], "subject": r["subject"], "sent_at": r["sent_at"],
                                           "parts": 0, "parts_total": 1, **{k: 0 for k in EVENTS}})
        g["parts"] += 1
        g["parts_total"] = max(g["parts_total"], int(r.get("parts_total") or 1))
        for k in EVENTS:
            g[k] += int(r[k])
    out = []
    for g in issues.values():
        d = g["delivered"]
        g.update(open_rate=pct(g["opened"], d), click_rate=pct(g["clicked"], d), delivery_rate=pct(g["delivered"], g["sent"]),
                 click_to_open=pct(g["clicked"], g["opened"]), bounce_rate=pct(g["bounced"], g["sent"]),
                 spam_rate=pct(g["complained"], d), unsub_rate=pct(g["unsubscribed"], d))
        out.append(g)
    return out[::-1]


def tile(label, value, sub="", color="var(--navy)"):
    return (f'<div class="tile"><div class="tl">{html.escape(label)}</div>'
            f'<div class="tv" style="color:{color}">{value}</div><div class="ts">{html.escape(sub)}</div></div>')


def delta(cur, prev):
    if prev is None:
        return ""
    d = round(cur - prev, 1)
    if d == 0:
        return "igual que la anterior"
    return f'{"+" if d > 0 else ""}{d} pts vs. la anterior'


def bars(issues, key, color):
    rows = []
    for g in issues[::-1]:
        v = g[key]
        rows.append(f'<div class="bar"><span class="bl">{html.escape(g["issue"])}</span>'
                    f'<span class="bt"><i style="width:{min(v, 100)}%;background:{color}"></i></span>'
                    f'<span class="bv">{v}%</span></div>')
    return "".join(rows)


def dashboard_html(broadcasts, links, as_of, days):
    issues = group_issues(broadcasts)
    if not issues:
        body = "<p>No hubo envíos en este periodo.</p>"
        latest = None
    else:
        latest = issues[0]
        pending = (f' <small>(en curso: {latest["parts"]} de {latest["parts_total"]} partes enviadas)</small>'
                   if latest["parts"] < latest["parts_total"] else "")
        prev = issues[1] if len(issues) > 1 else None
        spam_color = "var(--red)" if latest["complained"] else "var(--navy)"
        tiles = "".join([
            tile("Entregados", f'{latest["delivered"]}<small>/{latest["sent"]}</small>', f'{latest["delivery_rate"]}% de los enviados'),
            tile("Aperturas", f'{latest["open_rate"]}%', f'{latest["opened"]} personas · ' + delta(latest["open_rate"], prev and prev["open_rate"])),
            tile("Clics", f'{latest["click_rate"]}%', f'{latest["clicked"]} personas · ' + delta(latest["click_rate"], prev and prev["click_rate"])),
            tile("Clic entre quienes abrieron", f'{latest["click_to_open"]}%'),
            tile("Rebotes", latest["bounced"], f'{latest["bounce_rate"]}% de los enviados'),
            tile("Spam", latest["complained"], f'{latest["spam_rate"]}% · suprimidos: {latest["suppressed"]}', spam_color),
            tile("Bajas", latest["unsubscribed"], f'{latest["unsub_rate"]}%'),
        ])
        def row(g):
            return (f'<tr><td>{html.escape(g["issue"])}</td><td class="l">{html.escape(g["subject"])}</td><td>{g["sent"]}</td>'
                    f'<td>{g["delivered"]}</td><td>{g["opened"]} · {g["open_rate"]}%</td><td>{g["clicked"]} · {g["click_rate"]}%</td>'
                    f'<td>{g["bounced"]}</td><td>{g["complained"]}</td><td>{g["unsubscribed"]}</td></tr>')
        parts = "".join(
            f'<tr><td>{html.escape(b["issue"])} · parte {b["part"]}</td><td class="l">{html.escape(b["sent_at"][:16])} UTC</td>'
            f'<td>{b["sent"]}</td><td>{b["delivered"]}</td><td>{b["opened"]} · {b["open_rate"]}%</td><td>{b["clicked"]} · {b["click_rate"]}%</td>'
            f'<td>{b["bounced"]}</td><td>{b["complained"]}</td><td>{b["unsubscribed"]}</td></tr>'
            for b in sorted(broadcasts, key=lambda b: b["sent_at"], reverse=True))
        head = ('<tr><th>Envío</th><th class="l">Asunto</th><th>Enviados</th><th>Entregados</th>'
                '<th>Abiertos</th><th>Clics</th><th>Rebotes</th><th>Spam</th><th>Bajas</th></tr>')
        headp = head.replace("Asunto", "Hora")
        link_rows = "".join(f'<tr><td class="l">{html.escape(l["url"])}</td><td>{l["clicks"]}</td><td>{l["unique"]}</td></tr>'
                            for l in links) or '<tr><td class="l" colspan="3">Sin clics todavía</td></tr>'
        body = f"""
<h2>Última edición · {html.escape(latest["issue"])}{pending}</h2><p class="sub">{html.escape(latest["subject"])}</p>
<div class="tiles">{tiles}</div>
<h2>Últimas {days} días, por edición</h2>
<table>{head}{"".join(row(g) for g in issues)}</table>
<div class="cols"><div><h3>Aperturas</h3>{bars(issues, "open_rate", "var(--lilac)")}</div>
<div><h3>Clics</h3>{bars(issues, "click_rate", "var(--tomato)")}</div></div>
<h2>Cada envío</h2><table>{headp}{parts}</table>
<h2>Links más clicados</h2><table><tr><th class="l">Link</th><th>Clics</th><th>Personas</th></tr>{link_rows}</table>"""
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Newsletter · resultados</title><style>
:root{{--navy:#17254A;--cream:#FFF8EC;--tomato:#F02717;--red:#C4170C;--lilac:#B9A6F0;--pink:#FBC9D8;--line:#17254A22}}
*{{box-sizing:border-box}}body{{margin:0;padding:24px 16px;background:var(--cream);color:var(--navy);font:15px/1.4 'DM Sans',Helvetica,Arial,sans-serif}}
main{{max-width:880px;margin:0 auto}}h1{{font:700 28px Georgia,serif;margin:0 0 4px}}h1 b{{color:var(--tomato)}}
h2{{font:700 19px Georgia,serif;margin:28px 0 8px}}h3{{font-size:14px;margin:0 0 6px}}.sub,.meta{{margin:0 0 12px;opacity:.75}}
.tiles{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}}
.tile{{background:#fff;border:1.5px solid var(--navy);border-radius:14px;padding:12px}}.tl{{font-size:12px;opacity:.7}}
.tv{{font:700 30px Georgia,serif}}.tv small{{font-size:15px;opacity:.6}}.ts{{font-size:12px;opacity:.7}}
table{{width:100%;border-collapse:collapse;background:#fff;border-radius:12px;overflow:hidden;font-size:13px}}
th,td{{padding:7px 8px;border-bottom:1px solid var(--line);text-align:right}}th{{background:var(--pink)}}.l{{text-align:left;overflow-wrap:anywhere}}
.cols{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:16px}}@media(max-width:600px){{.cols{{grid-template-columns:1fr}}}}
.bar{{display:flex;align-items:center;gap:8px;margin:4px 0;font-size:12px}}.bl{{width:110px}}.bt{{flex:1;height:14px;background:#fff;border:1px solid var(--line);border-radius:7px;overflow:hidden}}
.bt i{{display:block;height:100%}}.bv{{width:44px;text-align:right}}.note{{font-size:12px;opacity:.65;margin-top:24px}}
</style></head><body><main>
<h1>El Club de las <b>Emprendedoras</b> · newsletter</h1>
<p class="meta">Resultados de los últimos {days} días · actualizado {html.escape(as_of)} (CDMX)</p>{body}
<p class="note">Las aperturas se cuentan con una imagen invisible: Apple Mail y Gmail a veces abren el correo por la persona, así que la tasa real es algo menor. Los clics son más confiables. El detalle por correo está en <code>newsletter/analytics/recipients.csv</code> (solo local).</p>
</main></body></html>"""


def render_png(html_path):
    png = html_path.with_suffix(".png")
    chrome = nl.env("CHROME_PATH", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    subprocess.run([chrome, "--headless", "--disable-gpu", "--hide-scrollbars", "--window-size=920,1500",
                    f"--screenshot={png}", html_path.as_uri()], check=True, capture_output=True, timeout=120)
    return png


def aggregate_links(per_broadcast_links):
    agg = {}
    for links in per_broadcast_links:
        for l in links:
            a = agg.setdefault(l["url"], {"url": l["url"], "clicks": 0, "unique": 0})
            a["clicks"] += l["clicks"]
            a["unique"] += l["unique"]
    return sorted(agg.values(), key=lambda l: -l["clicks"])


def build_dashboard(days):
    broadcasts = read_csv(OUT / "broadcasts.csv")
    links = json.loads((OUT / "links.json").read_text()) if (OUT / "links.json").exists() else []
    as_of = max((b["as_of"] for b in broadcasts), default=datetime.now(nl.TZ).isoformat(timespec="minutes"))
    page = OUT / "dashboard.html"
    page.write_text(dashboard_html(broadcasts, links, as_of[:16].replace("T", " "), days), encoding="utf-8")
    return page, group_issues(broadcasts)


def slack_summary(issues):
    if not issues:
        return "📊 *Newsletter:* no hubo envíos en las últimas 2 semanas."
    g = issues[0]
    wip = f" (en curso: {g['parts']} de {g['parts_total']} partes enviadas)" if g["parts"] < g["parts_total"] else ""
    line = (f"📊 *Resultados del newsletter {g['issue']}*{wip} — _{g['subject']}_\n"
            f"• Entregados: *{g['delivered']}/{g['sent']}* ({g['delivery_rate']}%)\n"
            f"• Aperturas: *{g['open_rate']}%* ({g['opened']}) · Clics: *{g['click_rate']}%* ({g['clicked']})\n"
            f"• Rebotes: {g['bounced']} · Spam: {g['complained']} · Bajas: {g['unsubscribed']}")
    if len(issues) > 1:
        p = issues[1]
        line += (f"\n• Vs. {p['issue']}: aperturas {p['open_rate']}% → {g['open_rate']}%, "
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
    (OUT / "links.json").write_text(json.dumps(aggregate_links(all_links), ensure_ascii=False, indent=1))
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
    p.add_argument("--days", type=int, default=14)
    p.add_argument("--slack", action="store_true", help="publica el dashboard (PNG) en SLACK_CHANNEL")
    p.add_argument("--no-sent-json", action="store_true", help="no actualiza stats en sent.json")
    p.set_defaults(fn=cmd_run)
    p = sub.add_parser("dashboard")
    p.add_argument("--days", type=int, default=14)
    p.set_defaults(fn=cmd_dashboard)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
