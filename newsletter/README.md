# Newsletter semanal · Miércoles de IA

Every **Wednesday at 08:00 (CDMX)** the waitlist gets an email with that week's AI and
entrepreneurship news, a tutorial from the site, and news about the taller. It goes out as a
**Resend Broadcast**, so the unsubscribe link, the `List-Unsubscribe` header and the
unsubscribe tracking are all Resend's.

```
Sheet de registros ──(Apps Script syncResend, diario)──► Resend · segmento "Club · Newsletter"
                                      ▲                               │
              "Desuscrita del newsletter" ◄── unsubscribes ───────────┤
                                                                      ▼
Sheet de noticias (SENT/APPROVED) ─┐                           Broadcast miércoles 8:00
site/tutoriales/tutoriales.json ───┼─► rutina del martes 17:00 ─► newsletter/issues/<fecha>.md
brand/voice.md ────────────────────┘     (ROUTINE.md)              + correo de prueba
```

## Weekly flow

| When | Who | What |
|---|---|---|
| Mon | Pame/Manu | News in the [news Sheet](https://docs.google.com/spreadsheets/d/1TB4WNIQhHSeBrLXEUQ5gi-CJRdBDxaXErudeUspcIyg/edit), Status `SENT` (went out on WhatsApp) or `APPROVED`. |
| Mon–Tue | Manu | Tutorial published on the site and added to `site/tutoriales/tutoriales.json`. |
| Tue 17:00 | Routine | Drafts the issue in our voice, sends a test, schedules it for Wed 08:00 ([ROUTINE.md](ROUTINE.md)). |
| Tue evening | Pame/Manu | Read the test email. To stop it: `newsletter.py cancel <id>` or cancel it in Resend. |
| Wed 08:00 | Resend | Sends to every subscribed contact. |

The routine stops and says why when there's no approved news, when the tutorial is missing
(it drafts but doesn't schedule), or when there are more subscribers than the daily limit.

## Commands

```bash
python3 -m venv .venv && .venv/bin/pip install -r newsletter/requirements.txt   # once
.venv/bin/python newsletter/newsletter.py news          # this week's approved news
.venv/bin/python newsletter/newsletter.py tutorial      # newest tutorial not sent yet
.venv/bin/python newsletter/newsletter.py audience      # subscribed / unsubscribed counts
.venv/bin/python newsletter/newsletter.py build newsletter/issues/2026-10-14.md
.venv/bin/python newsletter/newsletter.py test newsletter/issues/2026-10-14.md
.venv/bin/python newsletter/newsletter.py schedule newsletter/issues/2026-10-14.md [--dry-run]
.venv/bin/python newsletter/newsletter.py cancel <broadcast_id>
```

`schedule` refuses if the issue still has `[[MARCADORES]]`, and exits with code 3 (plus a macOS
notification) when subscribers > `NEWSLETTER_DAILY_LIMIT`. The free Resend plan allows 100
transactional emails a day (test emails count) and marketing broadcasts to up to 1,000
contacts. Check your plan's real limits at resend.com/settings/usage before raising it.

## Issue format

Markdown with a front matter block. Supported: paragraphs, `## títulos`, `- listas`,
`1. listas`, `> nota rosa`, `**negritas**`, `[links](https://…)`, `---`, and one button per
line: `[Ver el tutorial →](https://…){boton}`. Personalization: `{{{contact.first_name|emprendedora}}}`.

## Setup (once)

1. **Resend API key with Full access** (Settings → API Keys). The current `RESEND_API_KEY`
   is *Sending access* only, which can't read contacts or create broadcasts. Put it in `.env`
   (gitignored) and in the Apps Script properties.
2. **Verify the sending domain** `clubdelasemprendedoras.com` in Resend → Domains (DNS
   records for SPF/DKIM). `onboarding@resend.dev` can only send to the account owner.
3. `.venv/bin/python newsletter/newsletter.py setup --create` → copy `RESEND_SEGMENT_ID` to
   `.env` and to the Apps Script properties.
4. Apps Script sync: see "Newsletter sync (Resend)" in [sheets/README.md](../sheets/README.md).
5. Fill the rest of `.env`:

```
RESEND_API_KEY=re_...            # Full access
RESEND_SEGMENT_ID=...
NEWSLETTER_FROM=Pame y Manu <hola@clubdelasemprendedoras.com>
NEWSLETTER_REPLY_TO=info@clubdelasemprendedoras.com
NEWSLETTER_TEST_TO=info@clubdelasemprendedoras.com
NEWSLETTER_DAILY_LIMIT=100
```
