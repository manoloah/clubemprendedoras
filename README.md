# El Club de las Emprendedoras

Waitlist landing page for **El Club de las Emprendedoras**, the 2027 taller by Pame and Manu
([@emprendeconpm](https://www.instagram.com/emprendeconpm/)): *"De cero a emprendedora en 8 semanas."*
An 8-week, live, Spanish-language program where non-technical women turn an idea into a mobile
app with AI, then launch it and sell it.

The page has one job: collect name and email for the waitlist (plus optional profile answers).
Everyone on the waitlist gets a weekly newsletter on Wednesdays at 08:00 (Mexico City).

**Live:** https://www.clubdelasemprendedoras.com (also https://clubemprendedoras.vercel.app)

**Figma:** [brand system](https://www.figma.com/design/J8iryor1WNwHz7VZTsfuFt/Club-de-Emprendedoras?node-id=1-2&m=dev) · [06 · Componentes reutilizables · v2](https://www.figma.com/design/J8iryor1WNwHz7VZTsfuFt/Club-de-Emprendedoras?node-id=47-115&m=dev) (the components the CSS classes mirror)

## What's in the repo

```
site/                     the landing page (static HTML/CSS/JS, no build step)  → site/README.md
  assets/motion.js        all animation (scroll reveals, ideas heap, hero video loop)
  assets/video/           club-women.mp4, the transparent hero loop (stacked alpha)
  recetas/               Recetas de Emprendimiento e IA: the hub, each receta, recetas.json (recetas.json)  → site/recetas/README.md
sheets/                   Google Apps Script: writes sign-ups into the Sheet, syncs them to Resend  → sheets/README.md
newsletter/               weekly newsletter: newsletter.py, email template, issues, weekly routine  → newsletter/README.md
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

- Merging to `main` deploys to production at https://www.clubdelasemprendedoras.com (the bare
  domain redirects to `www`; `clubemprendedoras.vercel.app` still works). DNS is at Porkbun.
- Every other branch gets its own preview URL. Previews may ask for a Vercel login; production is public.
- `site/vercel.json` sets cache headers (images and video: 1 day) and basic security headers.
  `site/.vercelignore` keeps the developer README out of the deploy.

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
- **Recetas:** `/recetas/` lists our tutorials ("Recetas de Emprendimiento e IA"); each receta
  shows its intro and ingredients to everyone and asks newcomers for name + email (they join the
  waitlist) before the steps. Readers coming from the newsletter skip that. Details:
  `site/recetas/README.md`.
- **Newsletter:** every Tuesday at 17:00 a Claude routine takes that week's news from the news
  Sheet (Status SENT or APPROVED), the newest receta in `site/recetas/recetas.json` and
  the voice in `brand/voice.md`, drafts the issue, sends a test and schedules a Resend Broadcast
  for Wednesday 08:00. It goes from `hola@clubdelasemprendedoras.com` (replies land in the
  `info@` Porkbun mailbox) with Resend's unsubscribe link and click tracking through
  `links.clubdelasemprendedoras.com`. The Apps Script copies new sign-ups to Resend once a day
  and writes unsubscribes back into the Sheet. The routine stops instead of sending when there's
  no approved news, no receta, or more than 100 subscribers. Details: `newsletter/README.md`.

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

**PR #9 · Weekly newsletter**
- `newsletter/`: picks the news and receta, renders the email in the brand's colours, sends
  tests (`test`, and `test --broadcast` for a real one-person send) and schedules the Wednesday
  broadcast. Limit check at 100 subscribers.
- Apps Script `syncResend()`: daily sync of sign-ups to the Resend segment (first name only,
  capitalised) and of unsubscribes back to the Sheet. New deployment URL in `config.js`.
- Domain `clubdelasemprendedoras.com`: site on Vercel, sending and tracking verified in Resend,
  `hola@` forwarded to the `info@` mailbox.
- First issue (2026-10-14): welcome to the club, the week's news, the reel receta.
- A Claude scheduled task drafts and schedules each issue on Tuesdays (`newsletter/ROUTINE.md`).

**PR (next) · Recetas**
- `/recetas/` hub and the first receta, "Así hicimos el reel de Pame sin editar ni un segundo",
  with the brand's components and motion, a "Copiar" prompt button and a signup gate.
- Tutorials renamed to recetas across the newsletter (`newsletter.py receta`, `recetas.json`).
  Newsletter links to the site carry UTMs that skip the gate.

## Next

- Test on a real iPhone (the live site passes the iPhone checks in Chrome's and Safari's engines).
- The new domain is a few days old, so the first emails may land in spam: ask readers to reply
  and mark it "not spam". Consider turning off open tracking in Resend.
- Archive the old Apps Script deployment ("Registration from site") once this PR is live.
- Confirm the claims in the copy: "Más de 500 personas", "2 de cada 3 son mujeres", "entre 4 y 6 horas a la semana".
