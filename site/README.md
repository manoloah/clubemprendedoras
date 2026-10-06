# Landing · El Club de las Emprendedoras (waitlist 2027)

Static page, no build step. Mobile first, with a desktop layout from 900px.

```
site/
  index.html          page + copy
  assets/tokens.css   design tokens (mirror of the Figma variables)
  assets/styles.css   components + layout
  assets/app.js       waitlist form (validation, submit, success state, UTM capture)
  assets/config.js    Apps Script /exec URL  ← fill before publishing
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

The form posts to a Google Apps Script that writes into the
"ClubDeLasEmprendedoras - Registration" Sheet. Setup: [`sheets/README.md`](../sheets/README.md).
Then paste the `/exec` URL into `endpoint` in `assets/config.js`.

Flow: name + email + WhatsApp are saved first; then an optional modal asks the rest of the
questions and fills the same row.

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
