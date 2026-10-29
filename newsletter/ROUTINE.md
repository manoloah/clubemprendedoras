# Rutina semanal del newsletter

Instructions for the Claude routine that runs **every Tuesday at 17:00 (CDMX)** in this repo.
It drafts the Wednesday issue and schedules it for **Wednesday 08:00 CDMX**, which leaves
Pame and Manu the evening to read the test email and cancel if needed.

Run every command from the repo root with `.venv/bin/python`. Never print or commit secrets.
A separate reminder runs **every Monday at 12:00 (CDMX)**: it only runs `newsletter.py check`
and, if something is missing, posts a heads-up in Slack `#emprendeconpm` so there's time to add it.

1. **Sync the repo.** `git checkout main && git pull`. Work on a branch
   `newsletter/<YYYY-MM-DD>` (the Wednesday date).
2. **Check that everything is ready.** `newsletter/newsletter.py check`. It looks for:
   - **news:** the newest row of the news Sheet dated in the last 10 days and **not used in an
     earlier issue** (`sent.json`). It doesn't need to be approved: a row with Status SENT (already
     sent by WhatsApp) or APPROVED wins over a newer one without it, and an unapproved pick comes
     back with `"aprobada": false`, which means you review and improve it in step 3. Rows marked
     REJECTED/RECHAZADA are skipped;
   - **receta:** the newest receta in the site's `recetas.json` that hasn't gone out yet.

   If it exits 2, something is missing. **Stop here: don't draft, test or schedule anything**
   (we never send an incomplete newsletter). Post in Slack `#emprendeconpm` (channel `C0C0Z3LPQ80`)
   with `newsletter/newsletter.py slack "<message>"` (the bot tags Manu so he gets notified; if it
   exits 4, use the Slack connector and start the message with `<@U0AGV3HNYRE>`), then report the
   same in your final message:

   > ⚠️ *Newsletter del miércoles {fecha}: no se armó.* Falta:
   > • *Noticias:* no hay ninguna fila de los últimos 10 días en el Sheet → https://docs.google.com/spreadsheets/d/1TB4WNIQhHSeBrLXEUQ5gi-CJRdBDxaXErudeUspcIyg/edit
   > • *Receta nueva:* publícala en el sitio y agrégala a `site/recetas/recetas.json` (guía: `site/recetas/README.md`)
   > Cuando esté, avísenle a Claude o corran la rutina con "Run now" para que salga a las 8:00.

   Only list the items that are actually missing. If it exits 0, note the news date and the
   receta and continue.
3. **Get the content.** `newsletter/newsletter.py news` (the news text, using "Manu's improved
   version" when it exists) and `newsletter/newsletter.py receta` (title, summary, URL).

   **If the news isn't approved (`"approved": false`), you are the editor; don't stop and wait for approval.**
   The agent that writes the Sheet's news is uneven, so curate them to the standard of the last
   three issues in `newsletter/issues/` (read them first: that's the bar for picks, length and tone):
   - **Check every item.** Open each link (WebFetch) and confirm the facts in the text are on that
     page, it's from the last ~2 weeks (a standout older item is fine if the text says so) and it's
     a primary source (the company's own announcement, docs or a solid outlet). Fix wrong facts
     and replace weak links with the primary source; drop items you can't confirm.
   - **Curate.** Keep what matters to a non-technical woman starting a business: tools she can use
     (images, video, design, selling, writing, organizing), big moves by the AI companies she hears
     about (OpenAI, Anthropic, Google, Meta, Canva…), and at most one "chisme"/fun item. Drop
     developer-only news, funding rounds without a takeaway, and anything hype-y.
   - **Research to fill gaps.** If fewer than 3 good items are left, search the web (WebSearch) for
     news from the last 7 days that fit the list above and add them, up to 4 items in total, each
     with its primary-source link. Never add a claim you didn't read on the linked page.
   - Then write them as step 4 says, and **save and approve the row** with the Google Sheets
     connector (find it by its `Día` date): first write the curated items into its
     `Manu's improved version` cell (plain text, one item per line with its link, the way the
     Sheet has them), which is what `newsletter.py news` reads, and only then set `Status` to
     `APPROVED`. Never approve without saving the curated text: if the issue gets canceled and the
     row is reused, the original, unchecked text would go out as approved. Best effort: if the
     connector isn't there or the write fails, leave the row unapproved (a later run reviews it
     again), note it in the Slack post and carry on.
   - In the Slack post of step 7, add one line saying you edited the news: what you kept, dropped
     and added, with the links.
4. **Draft** `newsletter/issues/<YYYY-MM-DD>.md`. If that issue is already in `newsletter/sent.json`, it went out
   early: name the new one `<YYYY-MM-DD>-b.md`. If the file exists and wasn't sent (written by hand),
   don't rewrite it: only fill any `[[RECETA_*]]` markers and `receta_url`. Otherwise copy the structure of the most recent
   issue in that folder (front matter: `subject`, `preheader`, `news_date`, `receta_url`):
   - Read `brand/voice.md` first and follow it: Mexican Spanish, *tú*, written to women,
     warm and direct, no tech jargon (explain it or drop it), no hype, at most one "¡".
   - Open with `Hola, {{{contact.first_name|emprendedora}}}:` and one or two lines that
     connect to the week. Add a short welcome for new members ("Si acabas de llegar,
     bienvenida al club. Cuando podemos, te mandamos…"; we no longer promise a weekly send, so
     don't say "cada miércoles"); the full welcome only went in the first issue.
   - **Las noticias de la semana:** rewrite the Sheet's news simply, 3–4 items, one or
     two sentences each, each with its link in `[texto](url)` form. For an approved row, keep
     every fact and link from the Sheet and don't add news or claims that aren't there; for an
     unapproved one, use the items you curated in step 3.
   - **Tu receta de la semana:** title, the summary from `recetas.json`, and a
     `[Ver la receta →](url){boton}` button.
   - Close with a question they can answer by replying, "Tu idea lleva mucho tiempo
     esperando." and the signature "Pame y Manu / @emprendeconpm".
   - Subject: short, curious, no clickbait, under 60 characters.
   - Run the `humanizer` skill on the text.
5. **Check.** `newsletter/newsletter.py build <issue>`, then open `newsletter/build/<issue>.html`
   at 393px wide and look at it.
6. **Test email** to **manolo7_11@hotmail.com** (also `NEWSLETTER_TEST_TO` in `.env`):
   `newsletter/newsletter.py test <issue> --to manolo7_11@hotmail.com`. Never to anyone else.
7. **Tell Slack, always, right after the test.** Post in `#emprendeconpm` (`C0C0Z3LPQ80`) that the test
   was sent to manolo7_11@hotmail.com:
   subject, news date, receta, number of subscribers (`newsletter/newsletter.py audience`), when
   it goes out and how to cancel. That gives Pame and Manu time for final fixes.
   Post it with the email attached as a PDF:
   `newsletter/newsletter.py pdf <issue> --slack "<the message, Slack mrkdwn>"`. If that exits 4
   (no `SLACK_BOT_TOKEN`), post the same message with the Slack connector and add that the PDF
   is in `newsletter/build/<issue>.pdf`.
8. **Schedule at least 2 hours after the test.** `newsletter/newsletter.py schedule <issue> --split 100`
   (the default, Wednesday 08:00, is well past that). Up to 100 subscribers it goes out in one
   send. Above that it goes in parts of 100, one per day at 08:00: Wednesday, Thursday, Friday…
   Resend's free plan allows 3 segments, so only two parts can be scheduled at a time. The task
   `club-newsletter-partes` runs `newsletter.py continue` Thursday to Saturday at 07:00 and
   schedules the next part once the previous one has gone out. **Never** pass
   `--allow-over-limit`. Past 300 subscribers it's time to pay for Resend: raise
   `NEWSLETTER_DAILY_LIMIT` and `RESEND_MAX_SEGMENTS` in `.env`.
9. **Commit** the issue and `newsletter/sent.json`, push, and open a PR against `main`.
10. **Report** in 3–5 lines: subject, news date used, receta, number of recipients, broadcast
   id and send time, and how to cancel (`newsletter/newsletter.py cancel <id>`).
