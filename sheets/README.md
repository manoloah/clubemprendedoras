# Waitlist → Google Sheets

```
site/ form ──POST JSON──▶ Apps Script /exec URL ──▶ "ClubDeLasEmprendedoras - Registration"
```

Two steps, one row per email:
1. **Sign-up** (hero and final forms): name and email, plus `utm_*` / referrer.
2. **Profile modal** (optional, opens right after): WhatsApp and the rest of the sheet's
   questions. It fills the same row.

This folder isn't deployed with the site. It's the script you paste into the Sheet.

## One-time setup (≈5 min)

1. Open the Sheet → **Extensiones → Apps Script**. Delete the sample code, paste all of
   [`Code.gs`](./Code.gs) and save.
2. **Implementar → Nueva implementación** → type **Aplicación web**:
   - Ejecutar como: **Yo**
   - Quién tiene acceso: **Cualquier usuario** (visitors aren't signed in to Google; they
     can only send a sign-up, never read the Sheet).
   - Authorize. On "app not verified": **Configuración avanzada → Ir a… (no seguro)**.
3. Copy the URL ending in `/exec`. Opening it should show
   `{"ok":true,"service":"club-emprendedoras-waitlist"}`.
4. Paste it into `endpoint` in `site/assets/config.js` and deploy the site.

To update the script later: **Implementar → Administrar implementaciones → ✏️ → Versión:
Nueva versión**. That keeps the same `/exec` URL.

## Columns

The script writes into your existing headers (matched ignoring case/extra spaces) and adds
these at the end the first time they're used: **Actualizado, Origen, utm_source,
utm_medium, utm_campaign, utm_content, referrer**. To rename a column, edit the right side of
`COLUMNS` in `Code.gs` and redeploy.

Don't rename headers in the Sheet without updating `COLUMNS`, or the script will add a new column.

## Security

- The `/exec` URL is public (it's in the page source), like a Google Form link. It can only
  add a row or fill empty cells of an existing one. It never returns data.
- A repeat email never overwrites existing answers, so knowing someone's email doesn't let
  you change their info.
- Unknown fields are dropped, values are capped at 1,000 characters, and anything starting
  with `= + - @` is stored as text so it can't run as a formula.
- A hidden honeypot field drops simple bots; at most 30 saves per minute site-wide.
- Next step if spam shows up: Cloudflare Turnstile, verified in `doPost` with a secret in
  Script Properties.

## Newsletter sync (Resend)

`syncResend()` copies every sign-up into the Resend segment the weekly newsletter goes to, and
mirrors unsubscribes back into a **Desuscrita del newsletter** column (Resend owns that flag;
the sync never re-subscribes anyone). The process is described in `newsletter/README.md`.

1. **Configuración del proyecto ⚙️ → Propiedades de la secuencia de comandos**:
   - `RESEND_API_KEY`: a **Full access** key (a "Sending access" key can't manage contacts).
   - `RESEND_SEGMENT_ID`: from `python newsletter/newsletter.py setup --create`.
2. Paste the new `Code.gs`, save, choose `syncResend` in the toolbar and **Ejecutar** once
   (authorize the external request). Check the log says `added N`.
3. Choose `installNewsletterTrigger` and **Ejecutar**. From then on it syncs every hour.
4. Redeploy the web app (new version, same `/exec` URL) so `doPost` ignores the new column.
