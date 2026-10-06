# Waitlist → Google Sheets

```
site/ form ──POST JSON──▶ Apps Script /exec URL ──▶ "ClubDeLasEmprendedoras - Registration"
```

Two steps, one row per email:
1. **Sign-up** (hero and final forms): name, email, WhatsApp, plus `utm_*` / referrer.
2. **Profile modal** (optional, opens right after): the rest of the sheet's questions.
   It fills the same row.

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
these at the end the first time they're used: **Tu nombre, Actualizado, Origen, utm_source,
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
