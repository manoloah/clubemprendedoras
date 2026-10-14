# Rutina semanal del newsletter

Instructions for the Claude routine that runs **every Tuesday at 17:00 (CDMX)** in this repo.
It drafts the Wednesday issue and schedules it for **Wednesday 08:00 CDMX**, which leaves
Pame and Manu the evening to read the test email and cancel if needed.

Run every command from the repo root with `.venv/bin/python`. Never print or commit secrets.
A separate reminder runs **every Monday at 12:00 (CDMX)**: it only runs `newsletter.py check`
and, if something is missing, posts a heads-up in Slack `#general` so there's time to add it.

1. **Sync the repo.** `git checkout main && git pull`. Work on a branch
   `newsletter/<YYYY-MM-DD>` (the Wednesday date).
2. **Check that everything is ready.** `newsletter/newsletter.py check`. It looks for:
   - **news:** the newest row of the news Sheet with Status SENT (already sent by WhatsApp) or
     APPROVED, dated in the last 10 days and **not used in an earlier issue** (`sent.json`);
   - **receta:** the newest receta in the site's `recetas.json` that hasn't gone out yet.

   If it exits 2, something is missing. **Stop here: don't draft, test or schedule anything**
   (we never send an incomplete newsletter). Post in Slack `#general` (channel `C0BKT6BE42E`)
   with the Slack connector, then report the same in your final message:

   > ⚠️ *Newsletter del miércoles {fecha}: no se armó.* Falta:
   > • *Noticias aprobadas:* agrega las de esta semana en el Sheet con Status APPROVED o SENT → https://docs.google.com/spreadsheets/d/1TB4WNIQhHSeBrLXEUQ5gi-CJRdBDxaXErudeUspcIyg/edit
   > • *Receta nueva:* publícala en el sitio y agrégala a `site/recetas/recetas.json` (guía: `site/recetas/README.md`)
   > Cuando esté, avísenle a Claude o corran la rutina con "Run now" para que salga a las 8:00.

   Only list the items that are actually missing. If it exits 0, note the news date and the
   receta and continue.
3. **Get the content.** `newsletter/newsletter.py news` (the news text, using "Manu's improved
   version" when it exists) and `newsletter/newsletter.py receta` (title, summary, URL).
4. **Draft** `newsletter/issues/<YYYY-MM-DD>.md`. If that issue is already in `newsletter/sent.json`, it went out
   early: name the new one `<YYYY-MM-DD>-b.md`. If the file exists and wasn't sent (written by hand),
   don't rewrite it: only fill any `[[RECETA_*]]` markers and `receta_url`. Otherwise copy the structure of the most recent
   issue in that folder (front matter: `subject`, `preheader`, `news_date`, `receta_url`):
   - Read `brand/voice.md` first and follow it: Mexican Spanish, *tú*, written to women,
     warm and direct, no tech jargon (explain it or drop it), no hype, at most one "¡".
   - Open with `Hola, {{{contact.first_name|emprendedora}}}:` and one or two lines that
     connect to the week. Add a short welcome for new members ("Si acabas de llegar,
     bienvenida al club…"); the full welcome only went in the first issue.
   - **Las noticias de la semana:** rewrite the Sheet's news simply, 3–4 items, one or
     two sentences each, each with its link in `[texto](url)` form. Keep every fact and link
     from the Sheet; don't add news or claims that aren't there.
   - **Tu receta de la semana:** title, the summary from `recetas.json`, and a
     `[Ver la receta →](url){boton}` button.
   - Close with a question they can answer by replying, "Tu idea lleva mucho tiempo
     esperando." and the signature "Pame y Manu / @emprendeconpm".
   - Subject: short, curious, no clickbait, under 60 characters.
   - Run the `humanizer` skill on the text.
5. **Check.** `newsletter/newsletter.py build <issue>`, then open `newsletter/build/<issue>.html`
   at 393px wide and look at it.
6. **Test email.** `newsletter/newsletter.py test <issue>`.
7. **Tell Slack.** Post in `#general` (`C0BKT6BE42E`) that the test is in `NEWSLETTER_TEST_TO`:
   subject, news date, receta, number of subscribers (`newsletter/newsletter.py audience`), when
   it goes out and how to cancel. That gives Pame and Manu time for final fixes.
8. **Schedule at least 2 hours after the test.** `newsletter/newsletter.py schedule <issue>` (the
   default, Wednesday 08:00, is already well past that; with `--at`, leave 2 hours or more). If
   there are more subscribers than `NEWSLETTER_DAILY_LIMIT` (100), it exits 3: **don't** pass
   `--allow-over-limit`. Split instead: `--batch 99` sends to at most 99 who haven't received the
   issue (the test email counts toward the 100), and running the same command again with an `--at`
   at least 24 hours later sends to the rest. Resend's plan allows 3 segments: the main one plus
   one per part. Part segments of earlier issues are deleted automatically once sent.
9. **Commit** the issue and `newsletter/sent.json`, push, and open a PR against `main`.
10. **Report** in 3–5 lines: subject, news date used, receta, number of recipients, broadcast
   id and send time, and how to cancel (`newsletter/newsletter.py cancel <id>`).
