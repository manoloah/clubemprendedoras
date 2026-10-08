# El Club de las Emprendedoras

Waitlist landing page for **El Club de las Emprendedoras**, the 2027 taller by Pame and Manu
([@emprendeconpm](https://www.instagram.com/emprendeconpm/)): *"De cero a emprendedora en 8 semanas."*
An 8-week, live, Spanish-language program where non-technical women turn an idea into a mobile
app with AI, then launch it and sell it.

The page has one job: collect name and email for the waitlist (plus optional profile answers).

**Live:** https://clubemprendedoras.vercel.app

**Figma:** [brand system](https://www.figma.com/design/J8iryor1WNwHz7VZTsfuFt/Club-de-Emprendedoras?node-id=1-2&m=dev) · [06 · Componentes reutilizables · v2](https://www.figma.com/design/J8iryor1WNwHz7VZTsfuFt/Club-de-Emprendedoras?node-id=47-115&m=dev) (the components the CSS classes mirror)

## What's in the repo

```
site/                     the landing page (static HTML/CSS/JS, no build step)  → site/README.md
  assets/motion.js        all animation (scroll reveals, ideas heap, hero video loop)
  assets/video/           club-women.mp4, the transparent hero loop (stacked alpha)
sheets/                   Google Apps Script that writes sign-ups into the Sheet  → sheets/README.md
scripts/
  rank-hero.mjs           ranks hero headline options for our ICP (TypeSafe / Jev)
  hero-video/             rebuilds the hero loop from a source MP4
brand/                    self-contained, copy-paste brand system: tokens, components, motion (JS + hero video), logos,
                          illustrations, photos, voice docs and a living guide  → brand/README.md
scripts/sync-brand.sh      keeps brand/ in step with site/ (--check to verify)
.claude/launch.json       local preview server config
CLAUDE.md                 working notes for Claude Code sessions
```

## Run it locally

```bash
npx serve -l 4173 site
```

Then open http://localhost:4173. Serve it over http: don't open `index.html` by double-click,
or the animated hero falls back to the static image. Safari also won't play the video from
`python3 -m http.server`, because that server doesn't support Range requests.

> The waitlist endpoint in `site/assets/config.js` is the live one, so a form submitted
> locally writes a real row to the Sheet.

## Deploy

Hosted on Vercel (project `clubemprendedoras`), linked to this GitHub repo with `site/` as the
project root. No build step: Vercel serves `site/` as-is.

- Merging to `main` deploys to production at https://clubemprendedoras.vercel.app.
- Every other branch gets its own preview URL. Previews may ask for a Vercel login; production is public.
- `site/vercel.json` sets cache headers (images and video: 1 day) and basic security headers.
  `site/.vercelignore` keeps the developer README out of the deploy.
- If the site moves to a custom domain, update `og:url`, `og:image` and the canonical link in
  `site/index.html`.

## How it works

- **Page:** mobile first, desktop layout from 900px. Design tokens and component classes
  mirror the Figma file (map in `site/README.md`).
- **Waitlist:** step 1 (name + email, plus UTM/referrer) posts to a Google Apps Script web app,
  which writes into the "ClubDeLasEmprendedoras - Registration" Sheet. Step 2 is an optional
  modal (WhatsApp, profile, what's stopping her) that fills the same row. Setup and security
  notes: `sheets/README.md`.
- **Motion:** icons breathe, buttons have a light running around their outline, the highlighted
  words hop, sections drop into place on scroll, and the app ideas start as a heap and sort
  themselves. All of it switches off with the OS "reduce motion" setting, and the page works
  without JavaScript.
- **Hero video:** the illustration comes alive about 0.2s after it's on screen. It's one 1.7 MB
  H.264 file with the colour on the left half and the transparency mask on the right, turned
  into real transparency in a small WebGL canvas, so it looks the same in every browser.
  To regenerate it from a new render: `brand/scripts/hero-video/build.sh path/to/render.mp4`.

## History

**PR #1 · Landing page and waitlist** (merged)
- Static landing built from the Figma design: hero with form, 2027 band, the 8 weeks with phone
  mockups, app ideas, "Este club es para ti si…", Pame and Manu, "No es otro curso", FAQ, final CTA.
- Waitlist connected to Google Sheets through Apps Script, with a two-step sign-up (WhatsApp moved
  to step 2). The earlier Supabase approach was dropped.
- Program moved to an 8-week taller; hero became "De cero a emprendedora en 8 semanas" with the
  phrase underlined; sharper app ideas; Pame and Manu photos with a float animation.
- `scripts/rank-hero.mjs` to score hero copy options against the ICP.

**PR #2 · Motion** (merged)
- Breathing icons, button light ring, hopping highlight, scroll reveals, self-sorting ideas.
- Transparent hero video loop (stacked alpha + WebGL), plus the pipeline that builds it.
- Mobile fixes: the hero headline scales to fit any phone, nothing can widen the page, and the
  underline renders in Safari.
- Local preview switched to a server Safari can play video from.

**PR #3 · Vercel deploy**
- Vercel project linked to the repo; production at https://clubemprendedoras.vercel.app.
- Absolute `og:image`/`og:url` and a canonical link, so link previews on Instagram and WhatsApp show the image.

## Next

- Test on a real iPhone (the live site passes the iPhone checks in Chrome's and Safari's engines).
- Custom domain, if wanted (then update the URLs in `site/index.html`).
- Confirm the claims in the copy: "Más de 500 personas", "2 de cada 3 son mujeres", "entre 4 y 6 horas a la semana".
