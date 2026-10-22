# Rutina de resultados del newsletter (newsletter_analytics)

Instructions for the Claude routine that runs **every Monday at 09:00 (CDMX)** in this repo. It
checks how last Wednesday's newsletter (and the one before) did, builds the dashboard, and posts it
in Slack `#emprendeconpm`. Run every command from the repo root with `.venv/bin/python`. Never print
or commit secrets, and never paste subscribers' emails anywhere (Slack, PR, final message).

1. **Sync.** `git checkout main && git pull`, then a branch `newsletter/stats-<YYYY-MM-DD>`.
2. **Run it.** `newsletter/newsletter_analytics.py run --slack`. In one go it:
   - takes every broadcast in `sent.json` scheduled in the last 14 days that Resend reports as sent
     (split sends count each part);
   - writes the logs into `newsletter/analytics/` (**gitignored, local only**): `recipients.csv` (one
     row per email per send: sent, delivered, opened, clicked, bounced, spam, unsubscribed,
     suppressed, which links), `broadcasts.csv` (totals and rates per send), `history.csv`
     (a snapshot per run, to see numbers grow after the send);
   - ranks the most engaged readers (1 point per send opened + 3 per send clicked) in `readers.csv`
     and the dashboard's top 10 (emails masked on the dashboard, full in the local CSV);
   - rebuilds `dashboard.html` and `dashboard.png` (no emails in them);
   - posts the PNG with a summary in `#emprendeconpm` (tags Manu);
   - refreshes each of those broadcasts' `stats` in `newsletter/sent.json`.

   Exit 4 = no `SLACK_BOT_TOKEN`: run without `--slack`, post `newsletter/analytics/dashboard.png`
   with the Slack connector (start with `<@U0AGV3HNYRE>`) and the summary below.
3. **Show the dashboard in the routine.** Publish `newsletter/analytics/dashboard.html` as an
   Artifact (same URL each week: update it, don't create a new one) so it can be opened from the
   routine's run.
4. **Read the numbers** and add one or two lines in your final message (and in Slack if something
   stands out): opens or clicks falling versus the previous issue, any spam complaint, bounces,
   unsubscribes above 1%. Opens are inflated by Apple Mail/Gmail privacy features; trust clicks more.
   If the latest issue is still "en curso" (parts left to send), say so: its numbers aren't final.
5. **Commit** only `newsletter/sent.json` (the dashboard code is already in the repo), push, open a
   PR against `main`. If `sent.json` didn't change, skip the PR.

Other commands: `newsletter_analytics.py dashboard` rebuilds the page from the saved CSVs without
calling Resend; `run --days 28` looks further back; `run --no-sent-json` leaves `sent.json` alone.
