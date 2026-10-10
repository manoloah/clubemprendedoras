# Rutina semanal del newsletter

Instructions for the Claude routine that runs **every Tuesday at 17:00 (CDMX)** in this repo.
It drafts the Wednesday issue and schedules it for **Wednesday 08:00 CDMX**, which leaves
Pame and Manu the evening to read the test email and cancel if needed.

Run every command from the repo root with `.venv/bin/python`. Never print or commit secrets.

1. **Sync the repo.** `git checkout main && git pull`. Work on a branch
   `newsletter/<YYYY-MM-DD>` (the Wednesday date).
2. **Noticias.** `newsletter/newsletter.py news`. It returns the newest row of the news Sheet
   with Status SENT (already sent by WhatsApp) or APPROVED, dated in the last 10 days, using
   "Manu's improved version" when it exists. If it exits 1, there's nothing approved this
   week: stop, and report "No hay noticias aprobadas esta semana".
3. **Tutorial.** `newsletter/newsletter.py tutorial`. It returns the newest tutorial in the
   site's `tutoriales.json` that hasn't gone out yet. If it exits 1, draft anyway with the
   `[[TUTORIAL_TITULO]]`, `[[TUTORIAL_RESUMEN]]`, `[[TUTORIAL_URL]]` markers, **don't
   schedule**, and report "Falta el tutorial de la semana".
4. **Draft** `newsletter/issues/<YYYY-MM-DD>.md`. If that file already exists (written by hand),
   don't rewrite it: only fill the `[[TUTORIAL_*]]` markers and `tutorial_url`. Otherwise copy the structure of the most recent
   issue in that folder (front matter: `subject`, `preheader`, `news_date`, `tutorial_url`):
   - Read `brand/voice.md` first and follow it: Mexican Spanish, *tú*, written to women,
     warm and direct, no tech jargon (explain it or drop it), no hype, at most one "¡".
   - Open with `Hola, {{{contact.first_name|emprendedora}}}:` and one or two lines that
     connect to the week. Add a short welcome for new members ("Si acabas de llegar,
     bienvenida al club…"); the full welcome only went in the first issue.
   - **Las noticias de la semana:** rewrite the Sheet's news simply, 3–4 items, one or
     two sentences each, each with its link in `[texto](url)` form. Keep every fact and link
     from the Sheet; don't add news or claims that aren't there.
   - **Tu tutorial de la semana:** title, the summary from `tutoriales.json`, and a
     `[Ver el tutorial →](url){boton}` button.
   - Close with a question they can answer by replying, "Tu idea lleva mucho tiempo
     esperando." and the signature "Pame y Manu / @emprendeconpm".
   - Subject: short, curious, no clickbait, under 60 characters.
   - Run the `humanizer` skill on the text.
5. **Check.** `newsletter/newsletter.py build <issue>`, then open `newsletter/build/<issue>.html`
   at 393px wide and look at it.
6. **Test email.** `newsletter/newsletter.py test <issue>`.
7. **Schedule.** `newsletter/newsletter.py schedule <issue>`. If it exits 3, there are more
   subscribers than `NEWSLETTER_DAILY_LIMIT` (100): **don't** pass `--allow-over-limit`; report
   it so Pame and Manu can check the Resend plan.
8. **Commit** the issue and `newsletter/sent.json`, push, and open a PR against `main`.
9. **Report** in 3–5 lines: subject, news date used, tutorial, number of recipients, broadcast
   id and send time, and how to cancel (`newsletter/newsletter.py cancel <id>`).
