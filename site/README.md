# Landing · El Club de las Emprendedoras (waitlist 2027)

Static page, no build step. Mobile first, with a desktop layout from 900px.

```
site/
  index.html          page + copy
  assets/tokens.css   design tokens (mirror of the Figma variables)
  assets/styles.css   components + layout
  assets/app.js       waitlist form (validation, submit, success state, UTM capture)
  assets/motion.js    animation: reveals, ideas heap, letter hop, hero video (WebGL)
  assets/config.js    Apps Script /exec URL (live)
  assets/video/       club-women.mp4, stacked-alpha hero loop
  assets/brand/       logo (tomato, cream), asterisk, underline
  assets/img/         illustration, stickers, photo, og.jpg
```

## Run it locally

```bash
npx serve -l 4173 site
```

Use a real server, not `file://`, and not `python3 -m http.server` if you're testing in Safari:
the hero video needs http(s) and Range requests.

`assets/config.js` has the live endpoint, so a local submit writes a real row. With the endpoint
empty, `localhost` logs the lead to the console and shows success, and any other host shows an
error, so no signup is silently lost.

## Connect the waitlist

The form posts to a Google Apps Script that writes into the
"ClubDeLasEmprendedoras - Registration" Sheet. Setup: [`sheets/README.md`](../sheets/README.md).
Then paste the `/exec` URL into `endpoint` in `assets/config.js`.

Flow: name + email are saved first; then an optional modal asks for WhatsApp and the rest of
the questions and fills the same row.

## Before going live

- Live at https://clubemprendedoras.vercel.app (deploy notes in the root `README.md`). On a custom domain, update `og:url`, `og:image` and the canonical link.
- Confirm the claims in the copy: "Más de 500 personas", "2 de cada 3 son mujeres", "entre 4 y 6 horas a la semana".

## Figma ↔ code map

Figma file: [Club de Emprendedoras](https://www.figma.com/design/J8iryor1WNwHz7VZTsfuFt/Club-de-Emprendedoras?node-id=1-2&m=dev) · section [06 · Componentes reutilizables · v2](https://www.figma.com/design/J8iryor1WNwHz7VZTsfuFt/Club-de-Emprendedoras?node-id=47-115&m=dev) and "07 · Landing · Waitlist 2027 (mobile)".

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

## Motion

- `assets/motion.js` + the "Motion" block at the end of `assets/styles.css`: icon breathing, button light ring, letter-hop on `[data-jump]`, scroll reveals (`data-reveal` is added by JS), and the ideas heap that sorts itself.
- Everything is off under `prefers-reduced-motion: reduce`, and the hidden "before" states only exist once JS adds `html.motion`, so the page still works without JS.
- Preview locally with a server that supports HTTP Range requests (`npx serve site`); Safari won't play video from `python3 -m http.server` or from a `file://` URL. The `landing` entry in `.claude/launch.json` already does this.
- Hero loop (rebuild with `scripts/hero-video/build.sh render.mp4`): `assets/video/club-women.mp4` is a stacked-alpha H.264 (colour left, matte right, 640px per half, ping-pong so it loops seamlessly). `motion.js` composites it to transparency in a WebGL canvas once the art is on screen and at least 0.2s after load (Safari won't autoplay off-screen video); the static `club-women.webp` shows until then (and stays if WebGL or autoplay is unavailable).
