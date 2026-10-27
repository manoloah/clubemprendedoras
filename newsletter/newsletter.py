#!/usr/bin/env python3
"""
Newsletter semanal del Club de las Emprendedoras (Resend Broadcasts).

    python newsletter/newsletter.py check                # ¿hay noticias y receta nuevas? (exit 2 si falta algo)
    python newsletter/newsletter.py news                 # noticias aprobadas de esta semana
    python newsletter/newsletter.py receta               # receta nueva en el sitio
    python newsletter/newsletter.py audience             # suscritas / desuscritas (+ aviso del límite)
    python newsletter/newsletter.py build   ISSUE.md     # genera newsletter/build/ISSUE.html
    python newsletter/newsletter.py test    ISSUE.md     # manda una prueba a NEWSLETTER_TEST_TO
    python newsletter/newsletter.py pdf     ISSUE.md [--slack MSG] # build/ISSUE.pdf (y lo sube a Slack)
    python newsletter/newsletter.py slack   "MSG"        # publica en #emprendeconpm y etiqueta a Manu
    python newsletter/newsletter.py schedule ISSUE.md    # programa el broadcast (miércoles 8:00 CDMX)
    python newsletter/newsletter.py stats  [BROADCAST_ID] # guarda las métricas en sent.json
    python newsletter/newsletter.py cancel  BROADCAST_ID # cancela uno programado
    python newsletter/newsletter.py setup                # crea el segmento en Resend (una vez)

Config en .env / .env.local (ver newsletter/README.md). The whole process,
including the weekly routine, is documented in newsletter/README.md.
"""
import argparse
import csv
import html
import io
import json
import os
import re
import subprocess
import sys
import time as time_module
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
HERE = ROOT / "newsletter"
BUILD = HERE / "build"
SENT_LOG = HERE / "sent.json"
TEMPLATE = HERE / "template.html"
LOCAL_RECETAS = ROOT / "site" / "recetas" / "recetas.json"

TZ = ZoneInfo("America/Mexico_City")
SEND_TIME = time(8, 0)
NEWS_SHEET_CSV = (
    "https://docs.google.com/spreadsheets/d/"
    "1TB4WNIQhHSeBrLXEUQ5gi-CJRdBDxaXErudeUspcIyg/export?format=csv"
)
NEWS_WINDOW_DAYS = 10  # a row counts as "this week's" if dated within this many days
OK_STATUS = re.compile(r"^\s*(SENT|ENVIADA|ENVIADO|APPROV|APROB)", re.I)
PLACEHOLDER = re.compile(r"\[\[[A-Z_]+\]\]")
EXIT_OVER_LIMIT = 3
EXIT_MISSING = 2
EXIT_NO_SLACK = 4
# Overridable in .env (read in main(), after load_env): #emprendeconpm, tagging Manu.
SLACK_CHANNEL = "C0C0Z3LPQ80"
SLACK_MENTION = "<@U0AGV3HNYRE>"


# ---------- config ----------

def load_env():
    for name in (".env", ".env.local"):
        p = ROOT / name
        if not p.exists():
            continue
        for line in p.read_text().splitlines():
            m = re.match(r"\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$", line)
            if m and m.group(1) not in os.environ:
                value = re.sub(r"\s*#.*$", "", m.group(2))  # drop inline "# comments"
                os.environ[m.group(1)] = value.strip().strip('"').strip("'")


def env(name, default=None, required=False):
    v = os.environ.get(name, default)
    if required and not v:
        sys.exit(f"Falta {name} en .env (ver newsletter/README.md).")
    return v


def resend_client():
    import resend  # pip install -r newsletter/requirements.txt

    resend.api_key = env("RESEND_API_KEY", required=True)
    return resend


def notify(title, message):
    """Prints and, on macOS, shows a notification so the routine can't fail silently."""
    print(f"\n*** {title}: {message}\n")
    if sys.platform == "darwin":
        script = f"display notification {json.dumps(message)} with title {json.dumps(title)}"
        subprocess.run(["osascript", "-e", script], check=False, capture_output=True)


# ---------- news ----------

def parse_day(s):
    s = (s or "").strip()
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        return date(int(m[1]), int(m[2]), int(m[3]))
    m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)  # Sheets' M/D/YYYY
    if m:
        return date(int(m[3]), int(m[1]), int(m[2]))
    return None


def fetch_news(today):
    sent_days = {e.get("news_date") for e in sent_log()}
    with urllib.request.urlopen(NEWS_SHEET_CSV, timeout=30) as r:
        rows = list(csv.DictReader(io.StringIO(r.read().decode("utf-8"))))
    picks = []
    for row in rows:
        day = parse_day(row.get("Día"))
        status = row.get("Status", "")
        if not day or not OK_STATUS.match(status):
            continue
        if not (today - timedelta(days=NEWS_WINDOW_DAYS) < day <= today):
            continue
        if day.isoformat() in sent_days:  # already went out in an earlier issue
            continue
        text = (row.get("Manu's improved version") or "").strip() or (row.get("Noticia") or "").strip()
        text = "\n".join(l for l in text.splitlines() if not l.strip().upper().startswith("APPROVE AI NEWS"))
        picks.append({"date": day.isoformat(), "status": status.strip(), "text": text.strip()})
    picks.sort(key=lambda p: p["date"])
    return picks[-1] if picks else None


# ---------- recetas ----------

def sent_log():
    return json.loads(SENT_LOG.read_text()) if SENT_LOG.exists() else []


def reconcile_sent_log():
    """Drops broadcasts that were canceled in the Resend dashboard (not via `cancel`), so their
    news and receta count as unused again. Only checks the last 3 weeks, to keep API calls low."""
    log = sent_log()
    if not log or not os.environ.get("RESEND_API_KEY"):
        return
    resend = resend_client()
    cutoff = datetime.now(TZ) - timedelta(days=21)
    keep = []
    for e in log:
        if datetime.fromisoformat(e["scheduled_at"]) >= cutoff:
            status = (resend.Broadcasts.get(e["broadcast_id"]).get("status") or "").lower()
            if status in ("canceled", "cancelled", "draft"):
                print(f"{e['issue']}: el broadcast se canceló en Resend, se quita de sent.json.")
                continue
        keep.append(e)
    if len(keep) != len(log):
        SENT_LOG.write_text(json.dumps(keep, ensure_ascii=False, indent=2) + "\n")


def fetch_recetas():
    site = env("SITE_URL", "https://www.clubdelasemprendedoras.com").rstrip("/")
    try:
        with urllib.request.urlopen(f"{site}/recetas/recetas.json", timeout=20) as r:
            data, source = json.load(r), "site"
    except (urllib.error.URLError, json.JSONDecodeError):
        data, source = json.loads(LOCAL_RECETAS.read_text()), "local"
    items = data.get("recetas", [])
    for t in items:
        if t.get("url", "").startswith("/"):
            t["url"] = site + t["url"]
    return items, source


def new_receta():
    # Compare paths, not full URLs: SITE_URL may point at another host (e.g. vercel.app).
    path = lambda u: urllib.parse.urlsplit(u or "").path.rstrip("/")
    used = {path(e.get("receta_url")) for e in sent_log()}
    items, source = fetch_recetas()
    fresh = [t for t in items if t.get("url") and path(t["url"]) not in used]
    # A receta merged early waits for its own Wednesday instead of jumping the queue.
    upcoming = next_send_at().date().isoformat()
    fresh = [t for t in fresh if t.get("fecha", "") <= upcoming]
    fresh.sort(key=lambda t: t.get("fecha", ""))
    return (fresh[-1] if fresh else None), source


# ---------- audience ----------

def segment_contacts(resend, seg):
    contacts, after = [], None
    while True:
        params = {"limit": 100, **({"after": after} if after else {})}
        page = resend.Contacts.list(segment_id=seg, params=params)
        contacts += page["data"]
        if not page.get("has_more") or not page["data"]:
            return contacts
        after = page["data"][-1]["id"]


def audience():
    resend = resend_client()
    contacts = segment_contacts(resend, env("RESEND_SEGMENT_ID", required=True))
    active = [c for c in contacts if not c.get("unsubscribed")]
    return active, len(contacts) - len(active)


def check_limit(n, allow):
    limit = int(env("NEWSLETTER_DAILY_LIMIT", "100"))
    if n <= limit:
        return
    notify(
        "Newsletter: límite de envío",
        f"Hay {n} suscritas y el límite configurado es {limit} correos al día.",
    )
    if not allow:
        print(
            "No se programó nada. Revisa tu plan en resend.com/settings/usage y, si alcanza,\n"
            "sube NEWSLETTER_DAILY_LIMIT en .env o vuelve a correr con --allow-over-limit."
        )
        sys.exit(EXIT_OVER_LIMIT)


# ---------- rendering ----------

def read_issue(path):
    raw = Path(path).read_text()
    m = re.match(r"---\n(.*?)\n---\n(.*)", raw, re.S)
    if not m:
        sys.exit(f"{path}: falta el encabezado --- subject/preheader ---")
    meta = {}
    for line in m[1].splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, m[2]


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    s = re.sub(
        r"\[([^\]]+)\]\((https?://[^)\s]+|\[\[[A-Z_]+\]\])\)",
        r'<a href="\2" style="color:#B72E21;font-weight:600;">\1</a>',
        s,
    )
    return s


P = 'style="margin:0 0 16px;font-size:17px;line-height:1.6;color:#17254A;"'
LI = 'style="margin:0 0 12px;font-size:17px;line-height:1.6;color:#17254A;"'
H2 = ('style="margin:32px 0 12px;font-family:Georgia,\'Times New Roman\',serif;font-size:24px;'
      'line-height:1.25;color:#17254A;font-weight:700;"')


def md_to_html(md):
    out = []
    for block in re.split(r"\n\s*\n", md.strip()):
        lines = block.strip().splitlines()
        first = lines[0]
        button = re.fullmatch(r"\[(.+?)\]\((\S+?)\)\{boton\}", block.strip())
        if button:
            out.append(
                '<table role="presentation" cellpadding="0" cellspacing="0" style="margin:8px 0 24px;"><tr>'
                '<td style="background:#F02717;border-radius:999px;">'
                f'<a href="{button[2]}" style="display:inline-block;padding:14px 26px;font-size:17px;'
                f'font-weight:700;color:#FFFFFF;text-decoration:none;">{html.escape(button[1])}</a>'
                "</td></tr></table>"
            )
        elif first.startswith("## "):
            out.append(f"<h2 {H2}>{inline(first[3:])}</h2>")
            if lines[1:]:
                out.append(f"<p {P}>{'<br>'.join(inline(l) for l in lines[1:])}</p>")
        elif first.strip() == "---":
            out.append('<hr style="border:0;border-top:2px dashed #FBC0D7;margin:32px 0;">')
        elif all(re.match(r"\d+\.\s", l) for l in lines):
            items = "".join(f"<li {LI}>{inline(re.sub(r'^\d+\.\s', '', l))}</li>" for l in lines)
            out.append(f'<ol style="margin:0 0 16px;padding-left:22px;">{items}</ol>')
        elif all(l.startswith("- ") for l in lines):
            items = "".join(f"<li {LI}>{inline(l[2:])}</li>" for l in lines)
            out.append(f'<ul style="margin:0 0 16px;padding-left:22px;">{items}</ul>')
        elif first.startswith("> "):
            text = "<br>".join(inline(l.lstrip("> ")) for l in lines)
            out.append(
                '<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin:8px 0 24px;">'
                '<tr><td style="background:#FBC0D7;border-radius:16px;padding:18px 20px;font-size:17px;'
                f'line-height:1.55;color:#17254A;">{text}</td></tr></table>'
            )
        else:
            out.append(f"<p {P}>{'<br>'.join(inline(l) for l in lines)}</p>")
    return "\n".join(out)


def add_utm(page, campaign):
    """Tags links to our own site. utm_source=newsletter is also what opens a receta
    without the signup gate (see site/assets/recetas.js)."""
    def tag(m):
        url = m[1]
        if "utm_source=" in url:
            return m[0]
        base, _, frag = url.partition("#")
        sep = "&amp;" if "?" in base else "?"
        base += f"{sep}utm_source=newsletter&amp;utm_medium=email&amp;utm_campaign={campaign}"
        return f'href="{base}{"#" + frag if frag else ""}"'
    return re.sub(r'href="(https://(?:www\.)?clubdelasemprendedoras\.com[^"]*)"', tag, page)


def build(path):
    meta, body = read_issue(path)
    page = TEMPLATE.read_text()
    page = page.replace("{{SUBJECT}}", html.escape(meta.get("subject", "")))
    page = page.replace("{{PREHEADER}}", html.escape(meta.get("preheader", "")))
    page = page.replace("{{BODY}}", md_to_html(body))
    page = add_utm(page, Path(path).stem)
    BUILD.mkdir(exist_ok=True)
    out = BUILD / (Path(path).stem + ".html")
    out.write_text(page)
    return meta, page, out


def for_test(page):
    """A one-off test email has no contact, so fill the broadcast-only variables by hand."""
    page = re.sub(r"\{\{\{contact\.\w+\|([^}]*)\}\}\}", r"\1", page)
    return page.replace("{{{RESEND_UNSUBSCRIBE_URL}}}", "#")


def next_send_at(now=None):
    now = now or datetime.now(TZ)
    days = (2 - now.weekday()) % 7  # Wednesday = 2
    when = datetime.combine(now.date() + timedelta(days=days), SEND_TIME, TZ)
    if when <= now + timedelta(minutes=15):
        when += timedelta(days=7)
    return when


# ---------- commands ----------

def cmd_check(a):
    reconcile_sent_log()
    """Is everything ready for Wednesday? Exit 0 if so, EXIT_MISSING if not (prints JSON)."""
    today = date.fromisoformat(a.date) if a.date else datetime.now(TZ).date()
    news = fetch_news(today)
    receta, _ = new_receta()
    missing = []
    if not news:
        missing.append("noticias")
    if not receta:
        missing.append("receta")
    print(json.dumps({
        "para_el_miercoles": next_send_at().date().isoformat(),
        "noticias": {"ok": bool(news), "fecha": news and news["date"], "status": news and news["status"]},
        "receta": {"ok": bool(receta), "titulo": receta and receta.get("titulo"), "url": receta and receta.get("url")},
        "falta": missing,
    }, ensure_ascii=False, indent=2))
    if missing:
        sys.exit(EXIT_MISSING)


def cmd_news(a):
    reconcile_sent_log()
    today = date.fromisoformat(a.date) if a.date else datetime.now(TZ).date()
    pick = fetch_news(today)
    if not pick:
        notify("Newsletter", f"No hay noticias nuevas (SENT/APPROVED, sin enviar) en los últimos {NEWS_WINDOW_DAYS} días.")
        sys.exit(1)
    print(json.dumps(pick, ensure_ascii=False, indent=2))


def cmd_receta(a):
    reconcile_sent_log()
    t, source = new_receta()
    if not t:
        notify("Newsletter", "Todavía no hay una receta nueva en el sitio (recetas.json).")
        sys.exit(1)
    print(json.dumps({**t, "source": source}, ensure_ascii=False, indent=2))


def cmd_audience(a):
    active, unsub = audience()
    print(f"Suscritas: {len(active)} · Desuscritas: {unsub}")
    check_limit(len(active), allow=True)


def cmd_build(a):
    meta, _, out = build(a.issue)
    print(f"Listo: {out}\nAsunto: {meta.get('subject')}")


def cmd_test(a):
    meta, page, out = build(a.issue)
    resend = resend_client()
    to = a.to or env("NEWSLETTER_TEST_TO", required=True)
    if a.broadcast:
        return broadcast_test(resend, meta, page, to)
    r = resend.Emails.send({
        "from": env("NEWSLETTER_FROM", required=True),
        "to": to,
        "reply_to": env("NEWSLETTER_REPLY_TO") or None,
        "subject": "[PRUEBA] " + meta.get("subject", ""),
        "html": for_test(page),
    })
    print(f"Prueba enviada a {to} (id {r['id']}). Cuenta para el límite diario de transaccionales.")


def render_pdf(issue):
    """newsletter/build/ISSUE.pdf, printed by headless Chrome from the test version of the email."""
    meta, page, out = build(issue)
    preview = out.with_suffix(".preview.html")
    preview.write_text(for_test(page))
    pdf = out.with_suffix(".pdf")
    chrome = env("CHROME_PATH", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    subprocess.run([chrome, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={pdf}", preview.as_uri()],
                   check=True, capture_output=True, timeout=120)
    return meta, pdf


def slack_api(method, token, data=None, form=None):
    if form is not None:
        body, ctype = urllib.parse.urlencode(form).encode(), "application/x-www-form-urlencoded"
    else:
        body, ctype = json.dumps(data).encode(), "application/json; charset=utf-8"
    req = urllib.request.Request(f"https://slack.com/api/{method}", data=body,
                                 headers={"Authorization": f"Bearer {token}", "Content-Type": ctype})
    with urllib.request.urlopen(req, timeout=60) as r:
        res = json.load(r)
    if not res.get("ok"):
        sys.exit(f"Slack {method}: {res.get('error')}")
    return res


def slack_token():
    token = env("SLACK_BOT_TOKEN")
    if not token:
        print("Falta SLACK_BOT_TOKEN en .env: no se publicó en Slack.")
        sys.exit(EXIT_NO_SLACK)
    return token


def with_mention(text):
    """Tags SLACK_MENTION so the post notifies Manu (a bot's mention pings; a self-mention doesn't)."""
    return f"{SLACK_MENTION} {text}" if SLACK_MENTION and SLACK_MENTION not in text else text


def slack_post(text):
    slack_api("chat.postMessage", slack_token(), {"channel": SLACK_CHANNEL, "text": with_mention(text)})


def slack_upload(path, title, comment):
    """Posts `comment` in SLACK_CHANNEL with the file attached (needs a bot token with files:write)."""
    token = slack_token()
    data = path.read_bytes()
    up = slack_api("files.getUploadURLExternal", token, form={"filename": path.name, "length": len(data)})
    for attempt in range(3):  # Slack's upload host sometimes answers 5xx; it works on a retry
        try:
            req = urllib.request.Request(up["upload_url"], data=data,
                                         headers={"Content-Type": "application/octet-stream"})
            with urllib.request.urlopen(req, timeout=120):
                break
        except urllib.error.HTTPError as e:
            if e.code < 500 or attempt == 2:
                raise
            time_module.sleep(5)
    slack_api("files.completeUploadExternal", token, {
        "files": [{"id": up["file_id"], "title": title}],
        "channel_id": SLACK_CHANNEL,
        "initial_comment": with_mention(comment),
    })


def cmd_pdf(a):
    meta, pdf = render_pdf(a.issue)
    print(f"PDF: {pdf}")
    if a.slack:
        slack_upload(pdf, meta.get("subject", pdf.stem), a.slack)
        print(f"Publicado en Slack con el PDF ({SLACK_CHANNEL}).")


def cmd_slack(a):
    slack_post(a.message)
    print(f"Publicado en Slack ({SLACK_CHANNEL}).")


def broadcast_test(resend, meta, page, to):
    """Real broadcast to a throwaway one-person segment: checks the name and unsubscribe link."""
    free_part_segments(resend)
    seg = resend.Segments.create({"name": f"Prueba {datetime.now(TZ):%Y-%m-%d %H:%M}"})["id"]
    try:
        try:
            resend.Contacts.create({"email": to, "segments": [{"id": seg}]})
        except Exception:  # already a contact: just add it to the test segment
            resend.Contacts.Segments.add({"email": to, "segment_id": seg})
        r = resend.Broadcasts.create({
            "segment_id": seg,
            "from": env("NEWSLETTER_FROM", required=True),
            "subject": meta.get("subject", ""),  # real subject: this test is about the inbox placement
            "html": page,
            "name": "Prueba " + meta.get("subject", ""),
            "send": True,
        })
        for _ in range(36):  # wait until Resend has sent it before removing the segment
            time_module.sleep(5)
            if resend.Broadcasts.get(r["id"]).get("status") == "sent":
                break
        print(f"Broadcast de prueba enviado a {to} (id {r['id']}).")
        print("Ojo: si das clic en 'Ya no quiero recibir estos correos', te desuscribe de verdad.")
    finally:
        resend.Segments.remove(seg)


# ---------- sending in parts (Resend free plan: 100 emails a day, 3 segments) ----------
#
# Above the daily limit an issue goes out in parts, one per day, 08:00 CDMX: part 1 on
# Wednesday, part 2 on Thursday... Each part is a segment with the next `size` active
# contacts in sign-up order (created_at, id). sent.json keeps each part's `cutoff`, the
# last contact it took, so no emails are stored. People who sign up mid-week land in the
# last part. With 3 segments (the main one + 2 parts) only two parts can be scheduled at a
# time: `continue` (a daily task) deletes sent parts' segments and schedules the next one.

MAX_SEGMENTS = int(os.environ.get("RESEND_MAX_SEGMENTS", "3"))


def order_key(c):
    return [c.get("created_at", ""), c["id"]]


def issue_parts(issue):
    return [e for e in sent_log() if e.get("issue") == issue]


def free_part_segments(resend):
    """Deletes the segments of parts that have already been sent."""
    log, changed = sent_log(), False
    for e in log:
        if e.get("segment_id") and not e.get("segment_freed"):
            if (resend.Broadcasts.get(e["broadcast_id"]).get("status") or "").lower() == "sent":
                try:
                    resend.Segments.remove(e["segment_id"])
                except Exception:  # already gone
                    pass
                e["segment_freed"], changed = True, True
    if changed:
        SENT_LOG.write_text(json.dumps(log, ensure_ascii=False, indent=2) + "\n")


def pending_for(issue, active):
    parts = issue_parts(issue)
    if any("cutoff" not in e for e in parts):
        sys.exit(f"{issue} ya se envió (newsletter/sent.json). Crea un issue nuevo.")
    cutoff = max((e["cutoff"] for e in parts), default=None)
    return sorted((c for c in active if cutoff is None or order_key(c) > cutoff), key=order_key)


def schedule_part(resend, issue, meta, page, active, size, when, parts_total, dry_run=False, offset=0):
    """Schedules the next part of `issue` at `when`. Returns False if no segment is free."""
    pending = pending_for(issue, active)
    if not pending:
        print(f"Todas las suscritas ya tienen {issue}.")
        return False
    part = len(issue_parts(issue)) + 1 + offset  # offset: parts a dry run "scheduled" before
    last = part >= parts_total
    # The last part also takes mid-week sign-ups, up to the daily limit.
    batch = pending[:int(env("NEWSLETTER_DAILY_LIMIT", "100")) if last else size]
    if dry_run:
        print(f"[dry-run] Parte {part}/{parts_total}: {len(batch)} el {when:%A %d %b %H:%M} CDMX.")
        return True
    free_part_segments(resend)
    name = f"Newsletter {Path(issue).stem} · parte {part}"
    segments = resend.Segments.list()["data"]
    seg = next((x["id"] for x in segments if x["name"] == name), None)  # left by a canceled run
    if seg:
        for c in segment_contacts(resend, seg):
            resend.Contacts.Segments.remove({"email": c["email"], "segment_id": seg})
            time_module.sleep(0.6)
    elif len(segments) >= MAX_SEGMENTS:
        print(f"Parte {part}/{parts_total}: no hay segmento libre (máximo {MAX_SEGMENTS}); "
              "la programa `newsletter.py continue` cuando salga la parte anterior.")
        return False
    else:
        seg = resend.Segments.create({"name": name})["id"]
    for c in batch:
        resend.Contacts.Segments.add({"email": c["email"], "segment_id": seg})
        time_module.sleep(0.6)  # Resend allows ~2 requests per second
    broadcast(resend, issue, meta, page, seg, when, len(batch),
              {"part": part, "parts_total": parts_total, "segment_id": seg, "cutoff": order_key(batch[-1])})
    return True


def broadcast(resend, issue, meta, page, segment, when, recipients, extra=None):
    params = {
        "segment_id": segment,
        "from": env("NEWSLETTER_FROM", required=True),
        "subject": meta["subject"],
        "html": page,
        "name": f"Newsletter {Path(issue).stem}" + (f" · parte {extra['part']}" if extra else ""),
        "send": True,
        "scheduled_at": when.isoformat(),
    }
    if env("NEWSLETTER_REPLY_TO"):
        params["reply_to"] = env("NEWSLETTER_REPLY_TO")
    r = resend.Broadcasts.create(params)
    log = sent_log()
    log.append({
        "issue": issue,
        "broadcast_id": r["id"],
        "scheduled_at": when.isoformat(),
        "recipients": recipients,
        "news_date": meta.get("news_date", ""),
        "receta_url": meta.get("receta_url", ""),
        **(extra or {}),
    })
    SENT_LOG.write_text(json.dumps(log, ensure_ascii=False, indent=2) + "\n")
    label = f"Parte {extra['part']}/{extra['parts_total']}: " if extra else ""
    print(f"{label}{recipients} destinatarias, programado {r['id']} para {when:%A %d %b %H:%M} CDMX.")
    print("Para cancelarlo: python newsletter/newsletter.py cancel " + r["id"])


def cmd_schedule(a):
    reconcile_sent_log()
    issue = Path(a.issue).name
    meta, page, out = build(a.issue)
    missing = sorted(set(PLACEHOLDER.findall(page)))
    if missing and not a.force:
        sys.exit(f"El correo todavía tiene marcadores sin llenar: {', '.join(missing)}")
    if not meta.get("subject"):
        sys.exit("Falta el subject en el encabezado del issue.")

    active, unsub = audience()
    print(f"Destinatarias: {len(active)} suscritas ({unsub} desuscritas se omiten).")
    when = datetime.fromisoformat(a.at).replace(tzinfo=TZ) if a.at else next_send_at()
    resend = resend_client()
    limit = int(env("NEWSLETTER_DAILY_LIMIT", "100"))

    if a.split and len(active) > limit and not issue_parts(issue):
        total = -(-len(active) // a.split)  # ceil
        print(f"Pasa del límite de {limit} al día: va en {total} partes de hasta {a.split}, un día cada una.")
        for i in range(total):
            if not schedule_part(resend, issue, meta, page, active, a.split, when + timedelta(days=i), total,
                                 a.dry_run, offset=i if a.dry_run else 0):
                break
        return
    if a.split and issue_parts(issue):
        sys.exit(f"{issue} ya tiene partes programadas: las que faltan las programa `newsletter.py continue`.")
    if issue_parts(issue):
        sys.exit(f"{issue} ya se envió (newsletter/sent.json). Crea un issue nuevo.")
    check_limit(len(active), a.allow_over_limit)
    if a.dry_run:
        print(f"[dry-run] Se programaría para {when:%A %d %b %H:%M} CDMX. HTML: {out}")
        return
    broadcast(resend, issue, meta, page, env("RESEND_SEGMENT_ID", required=True), when, len(active))


def cmd_continue(a):
    """Daily: schedules the next part of any issue that's still going out in parts."""
    reconcile_sent_log()
    resend, now = resend_client(), datetime.now(TZ)
    issues = {e["issue"]: e for e in sent_log() if e.get("parts_total")}
    did = False
    for issue in issues:
        parts = issue_parts(issue)
        total = parts[0]["parts_total"]
        if len(parts) >= total:
            continue
        last = max(datetime.fromisoformat(e["scheduled_at"]) for e in parts)
        when = max(last + timedelta(days=1), now + timedelta(minutes=10))  # 24h+ after the last part
        path = HERE / "issues" / issue
        meta, page, _ = build(path)
        active, _ = audience()
        did |= schedule_part(resend, issue, meta, page, active, parts[0]["recipients"], when, total)
    if not did:
        print("Nada que programar.")


def cmd_stats(a):
    """Pulls each sent broadcast's numbers from Resend and saves them in sent.json."""
    resend = resend_client()
    log = sent_log()
    for e in log:
        if a.broadcast_id and e.get("broadcast_id") != a.broadcast_id:
            continue
        bid = e["broadcast_id"]

        def count(kind):
            total, after = 0, None
            while True:
                params = {"type": kind, "limit": 100, **({"after": after} if after else {})}
                page = resend.Broadcasts.recipients(bid, params)
                rows = page.get("data", [])
                total += len(rows)
                if not page.get("has_more") or not rows:
                    return total
                after = rows[-1]["id"]

        stats = {k: count(k) for k in ("sent", "delivered", "opened", "clicked", "bounced", "complained", "unsubscribed")}
        try:
            links = resend.Broadcasts.clicked_links(bid, {}).get("data", [])
            stats["links"] = [{"url": l["url"].split("?")[0], "clicks": l["clicks"], "unique": l["unique_clicks"]} for l in links]
        except Exception:  # older SDKs / plans without click data
            pass
        stats["as_of"] = datetime.now(TZ).isoformat(timespec="minutes")
        e["stats"] = stats
        d = max(stats["delivered"], 1)
        print(f"{e['issue']}: {stats['delivered']}/{stats['sent']} entregados · "
              f"{stats['opened']} abiertos ({stats['opened'] * 100 // d}%) · "
              f"{stats['clicked']} con clic ({stats['clicked'] * 100 // d}%) · "
              f"{stats['bounced']} rebotes · {stats['unsubscribed']} bajas · {stats['complained']} spam")
    SENT_LOG.write_text(json.dumps(log, ensure_ascii=False, indent=2) + "\n")


def cmd_cancel(a):
    resend = resend_client()
    resend.Broadcasts.cancel(a.broadcast_id)
    log = [e for e in sent_log() if e.get("broadcast_id") != a.broadcast_id]
    SENT_LOG.write_text(json.dumps(log, ensure_ascii=False, indent=2) + "\n")
    print(f"Cancelado: {a.broadcast_id} (y quitado de sent.json)")


def cmd_setup(a):
    resend = resend_client()
    for s in resend.Segments.list().get("data", []):
        print(f"Segmento existente: {s['name']} → {s['id']}")
    if a.create:
        r = resend.Segments.create({"name": "Club · Newsletter"})
        print(f"Creado: RESEND_SEGMENT_ID={r['id']}  (cópialo a .env y a las Script Properties)")


def main():
    global SLACK_CHANNEL, SLACK_MENTION
    load_env()
    SLACK_CHANNEL = env("SLACK_CHANNEL", SLACK_CHANNEL)
    SLACK_MENTION = env("SLACK_MENTION", SLACK_MENTION)
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("check"); p.add_argument("--date"); p.set_defaults(fn=cmd_check)
    p = sub.add_parser("news"); p.add_argument("--date"); p.set_defaults(fn=cmd_news)
    sub.add_parser("receta").set_defaults(fn=cmd_receta)
    sub.add_parser("audience").set_defaults(fn=cmd_audience)
    p = sub.add_parser("build"); p.add_argument("issue"); p.set_defaults(fn=cmd_build)
    p = sub.add_parser("test"); p.add_argument("issue"); p.add_argument("--to")
    p.add_argument("--broadcast", action="store_true", help="envío real (nombre y desuscripción funcionan)")
    p.set_defaults(fn=cmd_test)
    p = sub.add_parser("pdf"); p.add_argument("issue")
    p.add_argument("--slack", metavar="MENSAJE", help="publica MENSAJE en SLACK_CHANNEL con el PDF adjunto")
    p.set_defaults(fn=cmd_pdf)
    p = sub.add_parser("slack"); p.add_argument("message"); p.set_defaults(fn=cmd_slack)
    p = sub.add_parser("schedule")
    p.add_argument("issue")
    p.add_argument("--at", help="YYYY-MM-DDTHH:MM en hora de CDMX (default: próximo miércoles 8:00)")
    p.add_argument("--allow-over-limit", action="store_true")
    p.add_argument("--force", action="store_true", help="programar aunque queden marcadores [[...]]")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--split", type=int, metavar="N",
                   help="si pasa del límite diario: partes de N, una por día (el resto con `continue`)")
    p.set_defaults(fn=cmd_schedule)
    sub.add_parser("continue").set_defaults(fn=cmd_continue)
    p = sub.add_parser("stats"); p.add_argument("broadcast_id", nargs="?"); p.set_defaults(fn=cmd_stats)
    p = sub.add_parser("cancel"); p.add_argument("broadcast_id"); p.set_defaults(fn=cmd_cancel)
    p = sub.add_parser("setup"); p.add_argument("--create", action="store_true"); p.set_defaults(fn=cmd_setup)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
