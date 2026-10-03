# Landing · El Club de las Emprendedoras (waitlist 2027)

Static page, no build step. Mobile first, with a desktop layout from 900px.

```
site/
  index.html          page + copy
  assets/tokens.css   design tokens (mirror of the Figma variables)
  assets/styles.css   components + layout
  assets/app.js       waitlist form (validation, submit, success state, UTM capture)
  assets/config.js    waitlist backend settings  ← fill before publishing
  assets/brand/       logo (tomato, cream), asterisk, underline
  assets/img/         illustration, stickers, photo, og.jpg
```

## Run it locally

```bash
python3 -m http.server 4173 --directory site
```

On `localhost` the form succeeds without a backend and logs the lead to the console.
On any other host it shows an error until `assets/config.js` is filled in, so no signup is silently lost.

## Connect the waitlist

1. Create (or pick) a Supabase project and run `supabase/migrations/001_waitlist.sql`.
2. Paste the project URL and the publishable/anon key into `assets/config.js`.
3. The form calls the `join_waitlist()` function, never the table. Signups land in
   `public.waitlist` with name, email and any `utm_*` / referrer. Duplicate emails are
   ignored and get the exact same response, so nobody can probe who signed up.
   A global throttle (60 signups/minute) stops scripted floods.
4. For stronger bot protection later, put Cloudflare Turnstile in front via a
   Supabase Edge Function and verify the token before calling `join_waitlist()`.

Prefer Zapier, Make or another tool? Put its webhook URL in `endpoint` instead.

## Before going live

- Set `og:image` in `index.html` to the absolute URL once the domain exists.
- Check the claims marked in the hand-off notes (260+ students, 4–6 h a week).

## Figma ↔ code map

Figma file: Club de Emprendedoras · section "06 · Componentes reutilizables · v2" and "07 · Landing · Waitlist 2027 (mobile)".

| Figma component | Code |
|---|---|
| Club/Nav | `.nav` |
| Club/Button | `.btn`, `.btn--sm`, `.btn--block` |
| Club/Input | `.field` |
| Club/Waitlist Form | `.waitlist` + `[data-waitlist]` |
| Club/Kicker | `.kicker--tomato / --navy / --cream` |
| Club/Sticker | `.sticker--pink / --olive / --tomato / --lilac / --butter` |
| Club/Note | `.note--butter / --pink / --lilac` |
| Club/Card/Week | `.card-week--*` |
| Club/Card/ForYou | `.for-you__item--*` |
| Club/FAQ Item | `.faq__item` (`<details>`) |
| Club/Phone | `.phone` |
| Club/Footer | `.footer` |
| Club/Logo | `assets/brand/logo-*.webp` |
